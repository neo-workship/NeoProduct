"""
认证管理器 - SQLModel 版本
移除对 detached_helper 和 joinedload 的依赖,直接使用 SQLModel 查询
"""
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from nicegui import app, ui
from sqlmodel import Session, select

# 导入模型和数据库
from .models import User, Role, LoginLog
from .database import get_db
from .config import auth_config
from .utils import validate_password, validate_email
from .session_manager import session_manager, UserSession
from .navigation import navigate_to, redirect_to_login
import secrets

# 导入日志处理
from common.log_handler import (
    log_info, log_error, log_warning, log_debug, 
    log_success, log_trace, get_logger, safe, db_safe
)

logger = get_logger(__file__)


class AuthManager:
    """
    认证管理器 - SQLModel 版本
    
    核心改进:
    - 移除所有 joinedload 调用
    - 使用 SQLModel 的 session.get() 和 select() 查询
    - SQLModel 自动处理关系加载,不会产生 DetachedInstanceError
    - 简化了查询逻辑,提升性能
    """
    
    def __init__(self):
        self.current_user: Optional[UserSession] = None
        self._session_key = 'auth_session_token'
        self._remember_key = 'auth_remember_token'
    
    def register(self, username: str, email: str, password: str, **kwargs) -> Dict[str, Any]:
        """
        用户注册 - SQLModel 版本
        
        改进:
        - 直接使用 session.exec(select(...))
        - 不需要 joinedload
        """
        # 验证输入
        if not username or len(username) < 3:
            log_warning(f"注册失败: 用户名过短 ({username})")
            return {'success': False, 'message': '用户名至少3个字符'}
        
        if not validate_email(email):
            log_warning(f"注册失败: 邮箱格式不正确 ({email})")
            return {'success': False, 'message': '邮箱格式不正确'}
        
        if not password or len(password) < 6:
            log_warning("注册失败: 密码过短")
            return {'success': False, 'message': '密码至少6个字符'}
        
        # 检查用户是否已存在
        with get_db() as session:
            # SQLModel 查询: 简单直接
            existing = session.exec(
                select(User).where(
                    (User.username == username) | (User.email == email)
                )
            ).first()
            
            if existing:
                log_warning(f"注册失败: 用户名或邮箱已存在 ({username}/{email})")
                return {'success': False, 'message': '用户名或邮箱已存在'}
            
            # 创建新用户
            new_user = User(
                username=username,
                email=email,
                full_name=kwargs.get('full_name'),
                phone=kwargs.get('phone'),
                is_active=True,
                is_verified=False
            )
            new_user.set_password(password)
            
            session.add(new_user)
            session.commit()  # 显式 commit,确保 ID 生成
            session.refresh(new_user)  # 刷新获取 ID
            
            log_success(f"用户注册成功: {username} (ID: {new_user.id})")
            return {
                'success': True, 
                'message': '注册成功', 
                'user_id': new_user.id
            }
    
    def login(self, username: str, password: str, remember_me: bool = False) -> Dict[str, Any]:
        """
        用户登录 - SQLModel 版本
        
        改进:
        - 使用 session.exec(select(...)) 查询
        - 不需要 joinedload
        - SQLModel 自动处理关系
        """
        if not username or not password:
            log_warning("登录失败: 用户名或密码为空")
            return {'success': False, 'message': '请输入用户名和密码'}
        
        with get_db() as session:
            # SQLModel 查询: 简单明了
            user = session.exec(
                select(User).where(
                    (User.username == username) | (User.email == username)
                )
            ).first()
            
            if not user:
                log_warning(f"登录失败: 用户不存在 ({username})")
                return {'success': False, 'message': '用户名或密码错误'}
            
            # 检查用户是否被锁定
            if user.is_locked():
                remaining = (user.locked_until - datetime.now()).seconds // 60
                log_warning(f"登录失败: 账户已锁定 ({username}, 剩余 {remaining} 分钟)")
                return {
                    'success': False, 
                    'message': f'账户已锁定,请 {remaining} 分钟后重试'
                }
            
            # 验证密码
            if not user.check_password(password):
                user.failed_login_count += 1
                
                # 连续失败达到阈值,锁定账户
                if user.failed_login_count >= auth_config.max_login_attempts:
                    user.locked_until = datetime.now() + timedelta(
                        minutes=auth_config.login_lock_duration
                    )
                    log_warning(f"账户已锁定: {username} (失败次数: {user.failed_login_count})")
                
                session.commit()
                log_warning(f"登录失败: 密码错误 ({username}, 失败次数: {user.failed_login_count})")
                return {'success': False, 'message': '用户名或密码错误'}
            
            # 检查账户状态
            if not user.is_active:
                log_warning(f"登录失败: 账户未激活 ({username})")
                return {'success': False, 'message': '账户未激活,请联系管理员'}
            
            # 登录成功 - 更新用户信息
            user.last_login = datetime.now()
            user.login_count += 1
            user.failed_login_count = 0
            user.locked_until = None
            
            # 生成会话 token
            session_token = secrets.token_urlsafe(32)
            user.session_token = session_token
            
            # 如果勾选"记住我"
            if remember_me and auth_config.allow_remember_me:
                remember_token = secrets.token_urlsafe(32)
                user.remember_token = remember_token
                app.storage.user[self._remember_key] = remember_token
            
            session.commit()
            
            # 保存到浏览器
            app.storage.user[self._session_key] = session_token
            
            # 创建内存会话
            user_session = session_manager.create_session(session_token, user)
            self.current_user = user_session
            
            # 记录登录日志
            self._create_login_log(
                user_id=user.id,
                is_success=True,
                ip_address=self._get_client_ip(),
                user_agent=self._get_user_agent()
            )
            
            log_success(f"用户登录成功: {username}")
            return {
                'success': True, 
                'message': '登录成功', 
                'user': user_session
            }
    
    def logout(self):
        """
        用户登出 - SQLModel 版本
        """
        if not self.current_user:
            return
        
        session_token = app.storage.user.get(self._session_key)
        
        # 清除数据库中的 token
        if session_token:
            with get_db() as session:
                user = session.exec(
                    select(User).where(User.session_token == session_token)
                ).first()
                
                if user:
                    user.session_token = None
                    user.remember_token = None
                    log_info(f"用户登出: {user.username}")
        
        # 清除浏览器存储
        app.storage.user.pop(self._session_key, None)
        app.storage.user.pop(self._remember_key, None)
        
        # 清除内存会话
        if session_token:
            session_manager.delete_session(session_token)
        
        self.current_user = None
    
    def check_session(self) -> Optional[UserSession]:
        """
        检查会话有效性 - SQLModel 版本
        
        改进:
        - 使用 session.exec(select(...)) 查询
        - 不需要 joinedload
        - SQLModel 自动处理关系加载
        """
        # 1. 检查当前内存会话
        if self.current_user:
            return self.current_user
        
        # 2. 检查浏览器 session token
        session_token = app.storage.user.get(self._session_key)
        if not session_token:
            log_debug("未找到 session_token")
            return None
        
        # 3. 检查内存缓存
        user_session = session_manager.get_session(session_token)
        if user_session:
            log_debug(f"内存缓存命中: {user_session.username}")
            self.current_user = user_session
            return user_session
        
        # 4. 从数据库验证 token 有效性
        try:
            with get_db() as session:
                # SQLModel 查询: 简单直接
                user = session.exec(
                    select(User).where(
                        User.session_token == session_token,
                        User.is_active == True
                    )
                ).first()
                
                if user:
                    # 重新创建内存会话
                    user_session = session_manager.create_session(session_token, user)
                    self.current_user = user_session
                    log_debug(f"数据库验证成功: {user.username}")
                    return user_session
                else:
                    log_debug("数据库验证失败: token 已失效或用户不存在")
                    # token 无效,清除浏览器存储
                    app.storage.user.pop(self._session_key, None)
                    app.storage.user.pop(self._remember_key, None)
                    self.current_user = None
                    
        except Exception as e:
            log_error(f"数据库查询出错: {e}")
            self.current_user = None
            return None
        
        # 5. 检查 remember_me token (如果主 token 失效)
        remember_token = app.storage.user.get(self._remember_key)
        if remember_token and auth_config.allow_remember_me:
            log_debug("检查 remember_me token")
            try:
                with get_db() as session:
                    user = session.exec(
                        select(User).where(
                            User.remember_token == remember_token,
                            User.is_active == True
                        )
                    ).first()
                    
                    if user:
                        # 使用 remember token 重新登录
                        new_session_token = secrets.token_urlsafe(32)
                        user.session_token = new_session_token
                        session.commit()
                        
                        # 保存新的 session token
                        app.storage.user[self._session_key] = new_session_token
                        
                        # 创建内存会话
                        user_session = session_manager.create_session(new_session_token, user)
                        self.current_user = user_session
                        
                        log_success(f"Remember me 验证成功: {user.username}")
                        return user_session
                        
            except Exception as e:
                log_error(f"Remember token 验证出错: {e}")
        
        return None
    
    def update_profile(self, **update_data) -> Dict[str, Any]:
        """
        更新用户资料 - SQLModel 版本
        """
        if not self.current_user:
            return {'success': False, 'message': '请先登录'}
        
        with get_db() as session:
            user = session.get(User, self.current_user.id)
            
            if not user:
                return {'success': False, 'message': '用户不存在'}
            
            # 更新基本字段
            allowed_fields = ['full_name', 'phone', 'avatar', 'bio']
            for field in allowed_fields:
                if field in update_data:
                    setattr(user, field, update_data[field])
            
            session.commit()
            
            # 刷新内存会话
            session_token = app.storage.user.get(self._session_key)
            if session_token:
                session.refresh(user)  # 刷新对象以加载关系
                self.current_user = session_manager.update_session(session_token, user)
            
            log_info(f"用户资料更新成功: {user.username}")
            return {'success': True, 'message': '资料更新成功', 'user': self.current_user}
    
    def change_password(self, old_password: str, new_password: str) -> Dict[str, Any]:
        """
        修改密码 - SQLModel 版本
        """
        if not self.current_user:
            return {'success': False, 'message': '请先登录'}
        
        if not new_password or len(new_password) < 6:
            return {'success': False, 'message': '新密码至少6个字符'}
        
        with get_db() as session:
            user = session.get(User, self.current_user.id)
            
            if not user:
                return {'success': False, 'message': '用户不存在'}
            
            # 验证旧密码
            if not user.check_password(old_password):
                log_warning(f"修改密码失败: 旧密码错误 ({user.username})")
                return {'success': False, 'message': '旧密码错误'}
            
            # 设置新密码
            user.set_password(new_password)
            session.commit()
            
            log_success(f"密码修改成功: {user.username}")
            return {'success': True, 'message': '密码修改成功'}
    
    def get_user_by_id(self, user_id: int) -> Optional[UserSession]:
        """
        通过 ID 获取用户 - SQLModel 版本
        """
        # 如果是当前用户,直接返回缓存
        if self.current_user and self.current_user.id == user_id:
            return self.current_user
        
        with get_db() as session:
            user = session.get(User, user_id)
            
            if user:
                return UserSession.from_user(user)
        
        return None
    
    def get_user_by_username(self, username: str) -> Optional[UserSession]:
        """
        通过用户名获取用户 - SQLModel 版本
        """
        with get_db() as session:
            user = session.exec(
                select(User).where(User.username == username)
            ).first()
            
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
    
    def _create_login_log(self, user_id: int, is_success: bool, 
                         ip_address: str, user_agent: str, 
                         failure_reason: str = None):
        """创建登录日志"""
        try:
            with get_db() as session:
                log_entry = LoginLog(
                    user_id=user_id,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    is_success=is_success,
                    failure_reason=failure_reason,
                    login_type='normal'
                )
                session.add(log_entry)
        except Exception as e:
            log_error(f"创建登录日志失败: {e}")
    
    def _get_client_ip(self) -> str:
        """获取客户端 IP"""
        # TODO: 从请求中获取真实 IP
        return '127.0.0.1'
    
    def _get_user_agent(self) -> str:
        """获取用户代理"""
        # TODO: 从请求中获取 User-Agent
        return 'Unknown'


# 全局认证管理器实例
auth_manager = AuthManager()