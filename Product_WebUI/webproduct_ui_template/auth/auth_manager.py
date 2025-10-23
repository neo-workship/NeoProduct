"""
认证管理器
处理用户认证、会话管理等核心功能
"""
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from nicegui import app, ui
from .models import User, Role, LoginLog, Permission
from .database import get_db
from .config import auth_config
from .utils import validate_password, validate_email
from .session_manager import session_manager, UserSession
from .navigation import navigate_to, redirect_to_login
import secrets
from common.log_handler import (
    log_info, 
    log_error, 
    log_warning,
    log_debug,
    log_success,
    log_trace,
    get_logger
)

# 获取绑定模块名称的logger
logger = get_logger(__name__)

class AuthManager:
    """认证管理器"""
    
    def __init__(self):
        self.current_user: Optional[UserSession] = None
        self._session_key = 'auth_session_token'
        self._remember_key = 'auth_remember_token'
    
    def register(self, username: str, email: str, password: str, **kwargs) -> Dict[str, Any]:
        """用户注册"""
        # 验证输入
        if not username or len(username) < 3:
            log_warning(f"注册失败: 用户名不符合要求: {username}") 
            return {'success': False, 'message': '用户名至少需要3个字符'}
        
        if not validate_email(email):
            log_warning(f"注册失败: 邮箱格式不正确: {email}")
            return {'success': False, 'message': '邮箱格式不正确'}
        
        password_result = validate_password(password)
        if not password_result['valid']:
            log_warning(f"注册失败: 密码强度不足: {username}")
            return {'success': False, 'message': password_result['message']}
        
        with get_db() as db:
            # 检查用户名是否存在
            if db.query(User).filter(User.username == username).first():
                log_warning(f"注册失败: 用户名已存在: {username}")
                return {'success': False, 'message': '用户名已存在'}
            
            # 检查邮箱是否存在
            if db.query(User).filter(User.email == email).first():
                log_warning(f"注册失败: 邮箱已被注册: {email}")
                return {'success': False, 'message': '邮箱已被注册'}
            
            # 创建新用户
            user = User(
                username=username,
                email=email,
                full_name=kwargs.get('full_name', ''),
                phone=kwargs.get('phone', ''),
                is_active=True,
                is_verified=not auth_config.require_email_verification
            )
            user.set_password(password)
            
            # 分配默认角色
            default_role = db.query(Role).filter(Role.name == auth_config.default_user_role).first()
            if default_role:
                user.roles.append(default_role)
            
            db.add(user)
            db.commit()
            log_success(f"新用户注册成功: {username}")
            return {'success': True, 'message': '注册成功', 'user': user}
    
    def login(self, username: str, password: str, remember_me: bool = False) -> Dict[str, Any]:
        """用户登录"""
        with get_db() as db:
            from sqlalchemy.orm import joinedload
            # 查找用户（支持用户名或邮箱登录）
            user = db.query(User).options(
                joinedload(User.roles).joinedload(Role.permissions),
                joinedload(User.permissions)
            ).filter(
                (User.username == username) | (User.email == username)
            ).first()
            
            if not user:
                log_warning(f"登录失败: 用户名或密码错误: {username}")
                return {'success': False, 'message': '用户名或密码错误'}
            
            # 检查账户是否被锁定
            if user.locked_until and user.locked_until > datetime.now():
                remaining = int((user.locked_until - datetime.now()).total_seconds() / 60)
                log_warning(f"登录失败: 账户被锁定: {user.username}, 剩余时间: {remaining}分钟") # <-- **【修改】**
                return {'success': False, 'message': f'账户已被锁定，请在{remaining}分钟后重试'}
            
            # 验证密码
            if not user.check_password(password):
                # 记录失败次数
                user.failed_login_count += 1
                
                # 检查是否需要锁定账户
                if user.failed_login_count >= auth_config.max_login_attempts:
                    user.locked_until = datetime.now() + timedelta(seconds=auth_config.lockout_duration)
                    db.commit()
                    return {'success': False, 'message': f'登录失败次数过多，账户已被锁定'}
                
                db.commit()
                return {'success': False, 'message': '用户名或密码错误'}
            
            # 检查账户是否激活
            if not user.is_active:
                return {'success': False, 'message': '账户已被禁用'}
            
            # 登录成功
            user.failed_login_count = 0
            user.locked_until = None
            user.last_login = datetime.now()
            user.login_count += 1
            
            # 生成会话令牌
            session_token = user.generate_session_token()
            
            # 设置会话
            app.storage.user[self._session_key] = session_token
            
            # 处理记住我
            if remember_me and auth_config.allow_remember_me:
                remember_token = user.generate_remember_token()
                app.storage.user[self._remember_key] = remember_token
            
            # 记录登录日志
            log = LoginLog(
                user_id=user.id,
                ip_address=self._get_client_ip(),
                user_agent=self._get_user_agent(),
                login_type='normal',
                is_success=True
            )
            db.add(log)
            
            db.commit()
            
            # 创建会话
            user_session = session_manager.create_session(session_token, user)
            self.current_user = user_session
    
            log_success(f"用户登录成功: {user.username}")
            return {'success': True, 'message': '登录成功', 'user': user_session}
            
    def logout(self):
        """用户登出 - 增强版"""
        session_token = app.storage.user.get(self._session_key)

        if self.current_user:
            with get_db() as db:
                user = db.query(User).filter(User.id == self.current_user.id).first()
                if user:
                    user.session_token = None
                    user.remember_token = None
                    db.commit()
            log_info(f"用户登出: {self.current_user.username}")

        # 清除会话缓存
        if session_token:
            session_manager.delete_session(session_token)

        # 清除所有用户存储数据
        try:
            app.storage.user.clear()  # 清除所有用户存储数据，包括路由
            log_success("🗑️ 已清除所有用户存储数据")
        except Exception as e:
            log_error(f"⚠️ 清除用户存储失败: {e}")
            # 逐个清除关键数据
            for key in [self._session_key, self._remember_key, 'current_route']:
                try:
                    app.storage.user.pop(key, None)
                except:
                    pass
        
        self.current_user = None
    
    def check_session(self) -> Optional[UserSession]:
        """
        检查会话状态 - 完整版本
        解决多浏览器状态不一致问题
        """
        import time
        current_time = time.strftime("%H:%M:%S")
        log_debug(f"🔍 {current_time} 当前服务器内存用户: {self.current_user.username if self.current_user else 'None'}") # <-- **【修改: 从 print 替换为 log_debug】**        
        # 1. 获取浏览器存储的 session_token
        session_token = app.storage.user.get(self._session_key) 
        # 2. 如果浏览器没有 token，清除可能的服务器状态残留
        if not session_token:
            log_warning("❌ 浏览器无 session_token")
            if self.current_user:
                log_warning(f"⚠️ 发现服务器状态残留，清除用户: {self.current_user.username}")
                self.current_user = None
            return None
        
        # 3. 浏览器有 token，检查内存缓存
        # log_info("✅ 浏览器有 session_token，开始验证...")
        user_session = session_manager.get_session(session_token)
        if user_session:
            log_info(f"🎯 内存缓存命中: {user_session.username}")
            self.current_user = user_session
            return user_session
        
        # 4. 内存缓存没有，从数据库验证 token 有效性
        try:
            with get_db() as db:
                from sqlalchemy.orm import joinedload
                user = db.query(User).options(
                    joinedload(User.roles).joinedload(Role.permissions),
                    joinedload(User.permissions)
                ).filter(
                    User.session_token == session_token,
                    User.is_active == True
                ).first()
                
                if user:
                    log_success(f"✅ 数据库验证成功: {user.username}")
                    # 重新创建内存会话
                    user_session = session_manager.create_session(session_token, user)
                    self.current_user = user_session
                    return user_session
                else:
                    log_warning("❌ 数据库验证失败，token 已失效或用户不存在")                 
                    # token 无效，清除浏览器存储
                    app.storage.user.pop(self._session_key, None)
                    app.storage.user.pop(self._remember_key, None)
                    self.current_user = None
                    
        except Exception as e:
            log_error(f"❌ 数据库查询出错: {e}")
            self.current_user = None
            return None
        
        # 5. 检查 remember_me token（如果主 token 失效）
        remember_token = app.storage.user.get(self._remember_key)
        if remember_token and auth_config.allow_remember_me:
            log_info(f"🔍 检查记住我 token: {remember_token[:12] + '...'}")
            try:
                with get_db() as db:
                    from sqlalchemy.orm import joinedload
                    user = db.query(User).options(
                        joinedload(User.roles).joinedload(Role.permissions),
                        joinedload(User.permissions)
                    ).filter(
                        User.remember_token == remember_token,
                        User.is_active == True
                    ).first()
                    
                    if user:
                        log_success(f"✅ 记住我验证成功: {user.username}")
                        
                        # 生成新的 session token
                        new_session_token = user.generate_session_token()
                        app.storage.user[self._session_key] = new_session_token
                        db.commit()
                        
                        # 创建新会话
                        user_session = session_manager.create_session(new_session_token, user)
                        self.current_user = user_session
                        
                        log_info(f"🔄 通过记住我重新建立会话: {user_session.username}")
                        return user_session
                    else:
                        log_info("❌ 记住我 token 验证失败")
                        app.storage.user.pop(self._remember_key, None)
                        
            except Exception as e:
                log_error(f"❌ 记住我验证出错: {e}")
        
        # 6. 所有验证都失败
        log_error("❌ 所有验证都失败，用户未登录")
        self.current_user = None
        return None

    def change_password(self, user_id: int, old_password: str, new_password: str) -> Dict[str, Any]:
        """修改密码"""
        with get_db() as db:
            user = db.query(User).filter(User.id == user_id).first()
            
            if not user:
                logger.warning(f"密码修改失败: 用户不存在: user_id={user_id}")
                return {'success': False, 'message': '用户不存在'}
            
            # 验证旧密码
            if not user.check_password(old_password):
                logger.warning(f"密码修改失败: 原密码错误: {user.username}")
                return {'success': False, 'message': '原密码错误'}
            
            # 验证新密码
            password_result = validate_password(new_password)
            if not password_result['valid']:
                logger.warning(f"密码修改失败: 新密码强度不足: {user.username}")
                return {'success': False, 'message': password_result['message']}
            
            # 设置新密码
            user.set_password(new_password)
            
            # 清除所有会话（安全考虑）
            user.session_token = None
            user.remember_token = None
            
            db.commit()
            
            log_success(f"用户修改密码成功: {user.username}")
            return {'success': True, 'message': '密码修改成功，请重新登录'}
    
    def reset_password(self, email: str) -> Dict[str, Any]:
        """重置密码（发送重置链接）"""
        with get_db() as db:
            user = db.query(User).filter(User.email == email).first()
            
            if not user:
                # 为了安全，即使用户不存在也返回成功
                return {'success': True, 'message': '如果该邮箱已注册，您将收到密码重置邮件'}
            
            # TODO: 实现密码重置令牌生成和邮件发送
            # reset_token = secrets.token_urlsafe(32)
            # send_reset_email(user.email, reset_token)
            
            log_info(f"密码重置请求: {user.email}")
            return {'success': True, 'message': '如果该邮箱已注册，您将收到密码重置邮件'}
    
    def update_profile(self, user_id: int, **kwargs) -> Dict[str, Any]:
        """更新用户资料"""
        with get_db() as db:
            user = db.query(User).filter(User.id == user_id).first()
            
            if not user:
                return {'success': False, 'message': '用户不存在'}
            
            # 更新允许修改的字段
            allowed_fields = ['full_name', 'phone', 'avatar', 'bio']
            for field in allowed_fields:
                if field in kwargs:
                    setattr(user, field, kwargs[field])
            
            # 如果要修改邮箱，需要额外验证
            if 'email' in kwargs and kwargs['email'] != user.email:
                if not validate_email(kwargs['email']):
                    return {'success': False, 'message': '邮箱格式不正确'}
                
                # 检查邮箱是否已被使用
                existing = db.query(User).filter(
                    User.email == kwargs['email'],
                    User.id != user_id
                ).first()
                
                if existing:
                    return {'success': False, 'message': '该邮箱已被使用'}
                
                user.email = kwargs['email']
                user.is_verified = False  # 需要重新验证
            
            db.commit()
            
            # 更新会话缓存
            session_token = app.storage.user.get(self._session_key)
            if session_token and self.current_user and self.current_user.id == user_id:
                # 重新加载用户数据到会话
                from sqlalchemy.orm import joinedload
                user = db.query(User).options(
                    joinedload(User.roles).joinedload(Role.permissions),
                    joinedload(User.permissions)
                ).filter(User.id == user_id).first()
                
                if user:
                    user_session = session_manager.create_session(session_token, user)
                    self.current_user = user_session
            
            log_success(f"用户资料更新成功: {user.username}")
            return {'success': True, 'message': '资料更新成功', 'user': self.current_user}
    
    def get_user_by_id(self, user_id: int) -> Optional[UserSession]:
        """通过ID获取用户"""
        # 如果是当前用户，直接返回缓存
        if self.current_user and self.current_user.id == user_id:
            return self.current_user
        
        with get_db() as db:
            from sqlalchemy.orm import joinedload
            user = db.query(User).options(
                joinedload(User.roles).joinedload(Role.permissions),
                joinedload(User.permissions)
            ).filter(User.id == user_id).first()
            
            if user:
                return UserSession.from_user(user)
        return None
    
    def get_user_by_username(self, username: str) -> Optional[UserSession]:
        """通过用户名获取用户"""
        with get_db() as db:
            from sqlalchemy.orm import joinedload
            user = db.query(User).options(
                joinedload(User.roles).joinedload(Role.permissions),
                joinedload(User.permissions)
            ).filter(User.username == username).first()
            
            if user:
                return UserSession.from_user(user)
        return None
    
    def is_authenticated(self) -> bool:
        """检查是否已认证"""
        return self.current_user is not None
    
    def has_role(self, role_name: str) -> bool:
        """检查当前用户是否有指定角色"""
        if not self.current_user:
            return False
        return self.current_user.has_role(role_name)
    
    def has_permission(self, permission_name: str) -> bool:
        """检查当前用户是否有指定权限"""
        if not self.current_user:
            return False
        return self.current_user.has_permission(permission_name)
    
    def _get_client_ip(self) -> str:
        """获取客户端IP"""
        # TODO: 从请求中获取真实IP
        return '127.0.0.1'
    
    def _get_user_agent(self) -> str:
        """获取用户代理"""
        # TODO: 从请求中获取User-Agent
        return 'Unknown'

# 全局认证管理器实例
auth_manager = AuthManager()