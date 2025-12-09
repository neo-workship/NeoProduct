"""
认证管理器 - SQLModel 版本
修复：移除全局共享的 current_user 实例属性，改为只读属性
彻底解决跨浏览器/设备会话共享的安全问题
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
    
    核心改进（BUG 修复）:
    - ❌ 移除了 self.current_user 实例属性（这是全局共享状态的根源）
    - ✅ 改为 @property current_user，每次都从当前浏览器会话验证
    - ✅ 完全依赖 app.storage.user + SessionManager 的双层缓存机制
    - ✅ 彻底解决跨浏览器/设备会话共享问题
    
    架构说明:
    - app.storage.user: 基于 cookie 的浏览器级存储（每个浏览器独立）
    - SessionManager: 内存缓存层（token -> UserSession 映射）
    - 数据库: 持久化存储层（token 验证和用户数据）
    """
    
    def __init__(self):
        """
        初始化认证管理器
        
        注意：不再存储 self.current_user，避免全局共享状态
        """
        self._session_key = 'auth_session_token'
        self._remember_key = 'auth_remember_token'
    
    @property
    def current_user(self) -> Optional[UserSession]:
        """
        获取当前登录用户（只读属性）
        
        ⚠️ 重要：每次访问都会调用 check_session() 重新验证
        这确保了每个浏览器/设备都获取自己的会话，不会共享
        
        Returns:
            Optional[UserSession]: 当前用户会话，未登录返回 None
        """
        return self.check_session()
    
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
        - ✅ 不再设置 self.current_user（已移除）
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
            # ✅ 不再设置 self.current_user（已改为只读属性）
            
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
        
        改进:
        - ✅ 不再需要检查或清除 self.current_user（已移除）
        """
        # 获取当前会话 token（用于日志记录）
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
        
        # ✅ 不再需要设置 self.current_user = None（已移除）
    
    def check_session(self) -> Optional[UserSession]:
        """
        检查会话有效性 - SQLModel 版本
        
        核心修复:
        - ✅ 移除了 "if self.current_user: return self.current_user" 的逻辑
        - ✅ 永远从 app.storage.user 开始验证（确保浏览器隔离）
        - ✅ 使用 SessionManager 内存缓存提升性能（按客户端隔离）
        - ✅ 数据库作为最终验证层
        - ✅ 移除日志输出，避免与日志系统的用户上下文获取产生无限递归
        - ✅ 添加防御性检查，处理页面初始化早期的情况
        
        流程:
        1. 从 app.storage.user 获取当前浏览器的 session_token
        2. 检查 SessionManager 内存缓存（已按客户端隔离）
        3. 如果缓存未命中，从数据库验证
        4. 尝试 remember_me token（如果主 token 失效）
        
        Returns:
            Optional[UserSession]: 用户会话对象，未登录返回 None
        """
        # ✅ 修复：永远从 app.storage.user 开始（不再检查 self.current_user）
        # 1. 检查浏览器 session token
        try:
            session_token = app.storage.user.get(self._session_key)
        except:
            # 防御性检查：在页面初始化早期，app.storage.user 可能还未就绪
            return None
        
        if not session_token:
            return None
        
        # 2. 检查内存缓存（SessionManager）
        user_session = session_manager.get_session(session_token)
        if user_session:
            # ✅ 移除日志，避免递归（日志系统会调用 current_user）
            return user_session
        
        # 3. 从数据库验证 token 有效性
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
                    # ✅ 只在数据库验证成功时记录（这是关键操作）
                    log_info(f"会话恢复: {user.username}")
                    return user_session
                else:
                    # token 无效,清除浏览器存储
                    app.storage.user.pop(self._session_key, None)
                    app.storage.user.pop(self._remember_key, None)
                    
        except Exception as e:
            log_error(f"数据库查询出错: {e}")
            return None
        
        # 4. 检查 remember_me token (如果主 token 失效)
        remember_token = app.storage.user.get(self._remember_key)
        if remember_token and auth_config.allow_remember_me:
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
                        
                        log_success(f"Remember me 验证成功: {user.username}")
                        return user_session
                        
            except Exception as e:
                log_error(f"Remember token 验证出错: {e}")
        
        return None
    
    def update_profile(self, **update_data) -> Dict[str, Any]:
        """
        更新用户资料 - SQLModel 版本
        
        改进:
        - ✅ 使用 self.current_user（现在是只读属性，自动验证）
        - ✅ 更新后刷新 SessionManager 缓存
        """
        # 使用只读属性（自动调用 check_session）
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
                session_manager.update_session(session_token, user)
            
            log_info(f"用户资料更新成功: {user.username}")
            return {'success': True, 'message': '资料更新成功', 'user': self.current_user}
    
    def change_password(self, old_password: str, new_password: str) -> Dict[str, Any]:
        """
        修改密码 - SQLModel 版本
        
        改进:
        - ✅ 使用 self.current_user（现在是只读属性，自动验证）
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
        
        改进:
        - ✅ 使用 self.current_user（现在是只读属性，自动验证）
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
        """
        检查是否已认证
        
        改进:
        - ✅ 使用 self.current_user（现在是只读属性，自动验证）
        """
        return self.current_user is not None
    
    def has_role(self, role_name: str) -> bool:
        """
        检查当前用户是否有指定角色
        
        改进:
        - ✅ 使用 self.current_user（现在是只读属性，自动验证）
        """
        if not self.current_user:
            return False
        return self.current_user.has_role(role_name)
    
    def has_permission(self, permission_name: str) -> bool:
        """
        检查当前用户是否有指定权限
        
        改进:
        - ✅ 使用 self.current_user（现在是只读属性，自动验证）
        """
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