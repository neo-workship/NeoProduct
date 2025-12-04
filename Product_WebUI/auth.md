# auth

- **auth\__init__.py** *(包初始化文件)*
```python
"""
认证和权限管理包
提供用户认证、会话管理和权限控制功能
"""
from .auth_manager import AuthManager, auth_manager
from .session_manager import SessionManager, session_manager, UserSession
from .decorators import require_login, require_role, require_permission
from .models import User, Role, Permission
from .database import init_database
from .config import AuthConfig, auth_config
from .navigation import navigate_to, redirect_to_login, redirect_to_home
from .pages import (
    login_page_content,
    logout_page_content,
    register_page_content,
    profile_page_content,
    change_password_page_content,
    permission_management_page_content,
    role_management_page_content,
    user_management_page_content,
    get_auth_page_handlers
)

# 初始化数据库
init_database()

__all__ = [
    'AuthManager',
    'auth_manager',
    'SessionManager',
    'session_manager',
    'UserSession',
    'require_login',
    'require_role',
    'require_permission',
    'User',
    'Role',
    'Permission',
    'AuthConfig',
    'auth_config',
    'navigate_to',
    'redirect_to_login',
    'redirect_to_home',
    'login_page_content',
    'logout_page_content',
    'register_page_content',
    'profile_page_content',
    'change_password_page_content',
    'permission_management_page_content',
    'role_management_page_content',
    'user_management_page_content',
    'get_auth_page_handlers',
    'init_database'
]
```

- **auth\auth_manager.py**
```python
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
    get_logger,
    safe, 
    db_safe,
)

# 获取绑定模块名称的logger
logger = get_logger(__file__)

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
        
        try:
            # with get_db() as db:
            with db_safe(f"用户注册: {username}") as db:
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
        except Exception as e:
            # db_safe 已经记录了错误,这里只需要返回失败信息
            return {'success': False, 'message': '注册失败,请稍后重试'}
    
    def login(self, username: str, password: str, remember_me: bool = False) -> Dict[str, Any]:
        """用户登录"""
        try:
        # with get_db() as db:
            with db_safe(f"用户登录: {username}") as db:
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
        except Exception as e:
            # db_safe 已经记录了错误
            return {'success': False, 'message': '登录失败,请稍后重试'}
            
    def logout(self):
        """用户登出 - 增强版"""
        session_token = app.storage.user.get(self._session_key)
        if self.current_user:
            # with get_db() as db:
            with db_safe(f"用户登出: {self.current_user.username}") as db:
                user = db.query(User).filter(User.id == self.current_user.id).first()
                if user:
                    user.session_token = None
                    user.remember_token = None
                    db.commit()
            log_success(f"用户登出: {self.current_user.username}")

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
            log_debug("❌ 浏览器无 session_token")
            if self.current_user:
                log_debug(f"⚠️ 发现服务器状态残留，清除用户: {self.current_user.username}")
                self.current_user = None
            return None
        
        # 3. 浏览器有 token，检查内存缓存
        # log_info("✅ 浏览器有 session_token，开始验证...")
        user_session = session_manager.get_session(session_token)
        if user_session:
            log_debug(f"🎯 内存缓存命中: {user_session.username}")
            self.current_user = user_session
            return user_session
        
        # 4. 内存缓存没有，从数据库验证 token 有效性
        try:
            # with get_db() as db:
            with db_safe(f"检查当前Session Token") as db:
                from sqlalchemy.orm import joinedload
                user = db.query(User).options(
                    joinedload(User.roles).joinedload(Role.permissions),
                    joinedload(User.permissions)
                ).filter(
                    User.session_token == session_token,
                    User.is_active == True
                ).first()
                
                if user:
                    # 重新创建内存会话
                    user_session = session_manager.create_session(session_token, user)
                    self.current_user = user_session
                    return user_session
                else:
                    log_debug("❌ 数据库验证失败，token 已失效或用户不存在")                 
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
            log_debug(f"🔍 检查记住我 token: {remember_token[:12] + '...'}")
            try:
                # with get_db() as db:
                with db_safe(f"检查当前remember_me token") as db:
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
                        
                        log_debug(f"🔄 通过记住我重新建立会话: {user_session.username}")
                        return user_session
                    else:
                        log_error("❌ 记住我 token 验证失败")
                        app.storage.user.pop(self._remember_key, None)
                        
            except Exception as e:
                log_error(f"❌ 记住我验证出错: {e}")
        
        # 6. 所有验证都失败
        log_error("❌ 所有验证都失败，用户未登录")
        self.current_user = None
        return None

    def change_password(self, user_id: int, old_password: str, new_password: str) -> Dict[str, Any]:
        """修改密码"""
        # with get_db() as db:
        with db_safe(f"修改密码") as db:
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
        # with get_db() as db:
        with db_safe(f"重置密码") as db:
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
        # with get_db() as db:
        with db_safe(f"新用户资料") as db:
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
        
        # with get_db() as db:
        with db_safe(f"通过ID获取用户") as db:
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
        # with get_db() as db:
        with db_safe(f"通过用户名获取用户") as db:
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
```

- **auth\config.py**
```python
"""
认证配置模块
"""
import os
from pathlib import Path
from typing import Optional

class AuthConfig:
    """认证配置类"""
    
    def __init__(self):
        """
        这是类的构造函数，在创建 AuthConfig 类的实例时会自动调用。它初始化了所有认证相关的配置属性，并为其设置了默认值。
        """
        # 数据库配置
        self.database_type = 'sqlite'  # 默认使用SQLite，可切换为mysql、postgresql等
        self.database_url = self._get_database_url()
        
        # 会话配置
        self.session_secret_key = os.environ.get('SESSION_SECRET_KEY', 'your-secret-key-here')
        self.session_timeout = 3600 * 24  # 24小时
        self.remember_me_duration = 3600 * 24 * 30  # 30天
        
        # 密码配置
        self.password_min_length = 6
        self.password_require_uppercase = False
        self.password_require_lowercase = False
        self.password_require_numbers = False
        self.password_require_special = False
        
        # 注册配置
        self.allow_registration = True
        self.require_email_verification = False
        self.default_user_role = 'user'  # 默认角色
        
        # 登录配置
        self.max_login_attempts = 5
        self.lockout_duration = 1800  # 30分钟
        self.allow_remember_me = True
        
        # 路由配置
        self.login_route = '/login'
        self.logout_route = '/logout'
        self.register_route = '/register'
        self.unauthorized_redirect = '/login'
        
        # 默认角色配置（预留给权限管理包使用）
        self.default_roles = [
            {'name': 'admin', 'display_name': '管理员', 'description': '系统管理员，拥有所有权限'},
            {'name': 'editor', 'display_name': '编辑', 'description': '可以编辑内容'},
            {'name': 'viewer', 'display_name': '查看', 'description': '只能查看内容'},
            {'name': 'user', 'display_name': '普通用户', 'description': '普通注册用户'}
        ]
        
        # 默认权限配置（预留给权限管理包使用）
        self.default_permissions = [
            # 系统权限
            {'name': 'system.manage', 'display_name': '系统管理', 'category': '系统'},
            {'name': 'user.manage', 'display_name': '用户管理', 'category': '系统'},
            {'name': 'role.manage', 'display_name': '角色管理', 'category': '系统'},
            
            # 内容权限
            {'name': 'content.create', 'display_name': '创建内容', 'category': '内容'},
            {'name': 'content.edit', 'display_name': '编辑内容', 'category': '内容'},
            {'name': 'content.delete', 'display_name': '删除内容', 'category': '内容'},
            {'name': 'content.view', 'display_name': '查看内容', 'category': '内容'},
        ]
        
        # 页面权限映射（预留给权限管理包使用）
        self.page_permissions = {
            # menu_pages
            'dashboard': ['content.view'],
            'data': ['content.view', 'content.edit'],
            'analysis': ['content.view'],
            'mcp': ['system.manage'],
            
            # header_pages
            'settings_page': ['user.manage'],
            'user_profile_page': [],  # 所有登录用户都可访问
        }
    
    def _get_database_url(self) -> str:
        """获取数据库URL
        一个私有方法（以下划线开头），用于根据 self.database_type 属性生成数据库连接字符串。
        """
        if self.database_type == 'sqlite':
            db_path = Path('data') / 'auth.db'
            db_path.parent.mkdir(exist_ok=True)
            return f'sqlite:///{db_path}'
        elif self.database_type == 'mysql':
            # 示例：mysql://user:password@localhost/dbname
            return os.environ.get('DATABASE_URL', 'mysql://root:12345678@localhost:3309/auth_db')
        elif self.database_type == 'postgresql':
            # 示例：postgresql://user:password@localhost/dbname
            return os.environ.get('DATABASE_URL', 'postgresql://neo:12345678@172.22.160.1/auth_db')
        else:
            raise ValueError(f"Unsupported database type: {self.database_type}")
    
    def set_database_type(self, db_type: str):
        """设置数据库类型
        允许在程序运行时动态修改数据库类型。
        """
        if db_type not in ['sqlite', 'mysql', 'postgresql']:
            raise ValueError(f"Unsupported database type: {db_type}")
        self.database_type = db_type
        self.database_url = self._get_database_url()

# 全局配置实例
# 创建了一个AuthConfig的全局实例 auth_config。在项目的其他地方，可以直接导入 auth_config 来访问和使用这些配置，而无需每次都创建一个新的 AuthConfig 对象
auth_config = AuthConfig()
```

- **auth\database.py**
```python
"""
数据库连接和管理模块（重构版）
专注于数据库连接和会话管理，建表功能已迁移到 scripts/init_database.py
"""
from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from contextlib import contextmanager
from .config import auth_config

# 配置日志
# import logging
# logger = logging.getLogger(__name__)
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
logger = get_logger(__file__)

# 创建基类
Base = declarative_base()
# 全局变量
engine = None
SessionLocal = None

def init_database():
    """初始化数据库连接（不再负责建表）"""
    global engine, SessionLocal
    
    try:
        # 创建数据库引擎
        engine = create_engine(
            auth_config.database_url,
            pool_pre_ping=True,
            echo=False  # 生产环境设为False
        )
        
        # 为SQLite启用外键约束
        if auth_config.database_type == 'sqlite':
            @event.listens_for(engine, "connect")
            def set_sqlite_pragma(dbapi_connection, connection_record):
                cursor = dbapi_connection.cursor()
                cursor.execute("PRAGMA foreign_keys=ON")
                cursor.close()
        
        # 创建会话工厂
        SessionLocal = scoped_session(
            sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=engine
            )
        )
        
    except Exception as e:
        log_error(f"数据库连接初始化失败,类型{auth_config.database_type}: {e}")
        raise

def get_session():
    """获取数据库会话"""
    if SessionLocal is None:
        init_database()
    return SessionLocal()

@contextmanager
def get_db():
    """获取数据库会话的上下文管理器"""
    session = get_session()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        log_error(f"数据库操作失败: {e}")
        raise
    finally:
        session.close()

def close_database():
    """关闭数据库连接"""
    global SessionLocal
    
    if SessionLocal:
        SessionLocal.remove()
        log_info("数据库连接已关闭")

def check_connection():
    """检查数据库连接状态"""
    try:
        with get_db() as db:
            db.execute("SELECT 1")
        return True
    except Exception as e:
        log_error(f"数据库连接检查失败: {e}")
        return False

def get_engine():
    """获取数据库引擎（供其他模块使用）"""
    if engine is None:
        init_database()
    return engine

# 兼容性函数（向后兼容旧代码）
def reset_database():
    """重置数据库（已废弃，请使用 scripts/init_database.py --reset）"""
    log_warning("reset_database() 已废弃，请使用 'python scripts/init_database.py --reset'")
    import subprocess
    import sys
    
    try:
        result = subprocess.run([
            sys.executable, 
            'scripts/init_database.py', 
            '--reset', 
            '--test-data'
        ], check=True, capture_output=True, text=True)
        log_info("数据库重置完成")
        return True
    except subprocess.CalledProcessError as e:
        log_error(f"数据库重置失败: {e}")
        return False

# 保留一些重要的初始化函数供快速初始化使用
def quick_init_for_testing():
    """快速初始化（仅用于测试环境）"""
    try:
        init_database()
        
        # 调用统一初始化脚本
        from scripts.init_database import DatabaseInitializer
        
        initializer = DatabaseInitializer()
        initializer.engine = engine
        initializer.SessionLocal = SessionLocal
        
        # 导入模型并创建表
        initializer.import_all_models()
        initializer.create_all_tables()
        
        # 初始化基础数据
        initializer.init_auth_default_data()
        initializer.init_default_permissions()
        initializer.init_role_permissions()
        
        log_success("快速初始化完成")
        return True
        
    except Exception as e:
        log_error(f"快速初始化失败: {e}")
        return False
```

- **auth\decorators.py**
```python
"""
装饰器模块
提供登录验证、角色验证、权限验证等装饰器
"""
from functools import wraps
from nicegui import ui
from .auth_manager import auth_manager
from .config import auth_config

# import logging
# logger = logging.getLogger(__name__)
from common.log_handler import (
    log_info, 
    log_error, 
    log_warning,
    log_debug,
    log_success,
    log_trace,
    get_logger
)

def require_login(redirect_to_login: bool = True):
    """
    要求用户登录的装饰器
    Args:
        redirect_to_login: 未登录时是否重定向到登录页
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 检查会话
            user = auth_manager.check_session()
            
            if not user:
                log_warning(f"未认证用户尝试访问受保护资源: {func.__name__}")
                
                if redirect_to_login:
                    ui.notify('请先登录', type='warning')
                    ui.navigate.to(auth_config.login_route)
                else:
                    ui.notify('需要登录才能访问此功能', type='error')
                return
            
            # 更新current_user确保是最新的
            auth_manager.current_user = user
            return func(*args, **kwargs)
        return wrapper
    return decorator

def require_role(*roles):
    """
    要求用户具有指定角色的装饰器
    Args:
        *roles: 允许的角色列表
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 首先检查登录
            user = auth_manager.check_session()
            if not user:
                ui.notify('请先登录', type='warning')
                ui.navigate.to(auth_config.login_route)
                return
            
            # 超级管理员跳过角色检查
            if user.is_superuser:
                return func(*args, **kwargs)
            
            # 检查角色
            # user_roles = [role.name for role in user.roles]
            # if not any(role in user_roles for role in roles):
            #     log_warning(f"用户 {user.username} 尝试访问需要角色 {roles} 的资源")
            #     ui.notify(f'您没有权限访问此功能，需要以下角色之一：{", ".join(roles)}', type='error')
            #     return
            #------------------------------------------------------
            # ✅ 修复：user.roles 已经是字符串列表，不需要提取 .name
            # 检查角色
            user_roles = user.roles  # 直接使用，因为 DetachedUser.roles 就是 List[str]
            if not any(role in user_roles for role in roles):
                log_warning(f"用户 {user.username} 尝试访问需要角色 {roles} 的资源")
                ui.notify(f'您没有权限访问此功能，需要以下角色之一：{", ".join(roles)}', type='error')

                from component import universal_navigate_to
                try:
                    universal_navigate_to('no_permission', '权限不足')
                except RuntimeError:
                    # 如果布局管理器未初始化,直接渲染权限不足页面
                    from .pages import no_permission_page_content
                    no_permission_page_content()
                return
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

def require_permission(*permissions):
    """
    要求用户具有指定权限的装饰器
    
    Args:
        *permissions: 需要的权限列表
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 首先检查登录
            user = auth_manager.check_session()
            if not user:
                ui.notify('请先登录', type='warning')
                ui.open(auth_config.login_route)
                return
            
            # 检查权限
            missing_permissions = []
            for permission in permissions:
                if not auth_manager.has_permission(permission):
                    missing_permissions.append(permission)
            
            if missing_permissions:
                log_warning(f"用户 {user.username} 缺少权限: {missing_permissions}")
                ui.notify(f'您缺少以下权限：{", ".join(missing_permissions)}', type='error')
                from component import universal_navigate_to
                try:
                    universal_navigate_to('no_permission', '权限不足')
                except RuntimeError:
                    from .pages import no_permission_page_content
                    no_permission_page_content()
                return
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

def public_route(func):
    """
    标记公开路由（不需要认证）的装饰器
    主要用于文档和代码可读性
    """
    func._public_route = True
    return func

def admin_only(func):
    """
    仅管理员可访问的装饰器
    """
    return require_role('admin')(func)

def authenticated_only(func):
    """
    仅需要登录即可访问的装饰器（简化版）
    """
    return require_login(redirect_to_login=True)(func)

# 页面级装饰器
def protect_page(roles=None, permissions=None, redirect_to_login=True):
    """
    保护整个页面的装饰器
    
    Args:
        roles: 允许的角色列表
        permissions: 需要的权限列表
        redirect_to_login: 未登录时是否重定向
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 检查登录
            user = auth_manager.check_session()
            if not user:
                if redirect_to_login:
                    ui.notify('请先登录', type='warning')
                    ui.navigate.to(auth_config.login_route)
                else:
                    ui.notify('需要登录才能访问此页面', type='error')
                return
            
            # 检查角色
            if roles and not user.is_superuser:
                user_roles = [role.name for role in user.roles]
                if not any(role in user_roles for role in roles):
                    ui.notify(f'您没有权限访问此页面', type='error')
                    return
            
            # 检查权限
            if permissions:
                missing = [p for p in permissions if not auth_manager.has_permission(p)]
                if missing:
                    ui.notify(f'您缺少访问此页面的权限', type='error')
                    return
            
            return func(*args, **kwargs)
        return wrapper
    return decorator
```

- **auth\detached_helper.py**
```python
"""
分离数据帮助器 - 解决SQLAlchemy DetachedInstanceError问题的通用工具
增强版本：增加对用户-权限直接关联的支持
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

# 设置日志
# import logging
# logger = logging.getLogger(__name__)
from common.log_handler import (
    log_info, 
    log_error, 
    log_warning,
    log_debug,
    log_success,
    log_trace,
    get_logger,
    safe, 
    db_safe,
)
# 获取绑定模块名称的logger
logger = get_logger(__file__)

@dataclass
class DetachedUser:
    """分离的用户数据类 - 不依赖SQLAlchemy会话"""
    id: int
    username: str
    email: str
    password_hash: str = ""
    full_name: Optional[str] = None
    phone: Optional[str] = None
    avatar: Optional[str] = None
    bio: Optional[str] = None
    
    # 状态信息
    is_active: bool = True
    is_verified: bool = False
    is_superuser: bool = False
    
    # 登录信息
    last_login: Optional[datetime] = None
    login_count: int = 0
    failed_login_count: int = 0
    locked_until: Optional[datetime] = None
    
    # 时间戳
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    # 关联数据
    roles: List[str] = field(default_factory=list)          # 角色名称列表
    permissions: List[str] = field(default_factory=list)    # 权限名称列表（包括角色权限和直接权限）
    direct_permissions: List[str] = field(default_factory=list)  # 直接分配的权限名称列表
    role_permissions: List[str] = field(default_factory=list)  # 通过角色获得的权限名称列表

    def has_role(self, role_name: str) -> bool:
        """检查是否有指定角色"""
        return role_name in self.roles

    def has_permission(self, permission_name: str) -> bool:
        """检查是否有指定权限（包括角色权限和直接权限）"""
        return self.is_superuser or permission_name in self.permissions

    def has_direct_permission(self, permission_name: str) -> bool:
        """检查是否有直接分配的权限"""
        return permission_name in self.direct_permissions

    def has_role_permission(self, permission_name: str) -> bool:
        """检查是否通过角色拥有权限"""
        return permission_name in self.role_permissions

    def is_locked(self) -> bool:
        """检查用户是否被锁定"""
        return self.locked_until is not None and self.locked_until > datetime.now()

    @classmethod
    def from_user(cls, user) -> 'DetachedUser':
        """从User模型创建分离的用户对象"""
        try:
            from .models import User, Role, Permission
            
            # 提取角色信息
            roles = []
            role_permissions = []
            if hasattr(user, 'roles') and user.roles:
                roles = [role.name for role in user.roles]
                # 收集角色的所有权限
                for role in user.roles:
                    if hasattr(role, 'permissions') and role.permissions:
                        role_permissions.extend([perm.name for perm in role.permissions])

            # 提取直接权限
            direct_permissions = []
            if hasattr(user, 'permissions') and user.permissions:
                direct_permissions = [perm.name for perm in user.permissions]

            # 合并所有权限（去重）
            all_permissions = list(set(role_permissions + direct_permissions))

            return cls(
                id=user.id,
                username=user.username,
                email=user.email,
                password_hash=getattr(user, 'password_hash', ''),
                full_name=user.full_name,
                phone=user.phone,
                avatar=user.avatar,
                bio=user.bio,
                is_active=user.is_active,
                is_verified=user.is_verified,
                is_superuser=user.is_superuser,
                last_login=user.last_login,
                login_count=user.login_count,
                failed_login_count=user.failed_login_count,
                locked_until=user.locked_until,
                created_at=user.created_at,
                updated_at=user.updated_at,
                roles=roles,
                permissions=all_permissions,
                direct_permissions=direct_permissions,
                role_permissions=list(set(role_permissions))
            )
        except Exception as e:
            # logger.error(f"创建DetachedUser失败: {e}")
            log_error(f"创建DetachedUser失败: {e}")
            return cls(
                id=user.id,
                username=user.username,
                email=user.email,
                is_active=getattr(user, 'is_active', True),
                is_superuser=getattr(user, 'is_superuser', False)
            )

@dataclass
class DetachedRole:
    """分离的角色数据类"""
    id: int
    name: str
    display_name: Optional[str] = None
    description: Optional[str] = None
    is_active: bool = True
    is_system: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # 权限和用户信息
    permissions: List[str] = field(default_factory=list)
    user_count: int = 0
    users: List[str] = field(default_factory=list)  # 用户名列表

    @classmethod
    def from_role(cls, role) -> 'DetachedRole':
        """从Role模型创建分离的角色对象"""
        try:
            # 提取权限信息
            permissions = []
            if hasattr(role, 'permissions') and role.permissions:
                permissions = [perm.name for perm in role.permissions]

            # 提取用户信息
            users = []
            user_count = 0
            if hasattr(role, 'users') and role.users:
                users = [user.username for user in role.users]
                user_count = len(role.users)

            return cls(
                id=role.id,
                name=role.name,
                display_name=role.display_name,
                description=role.description,
                is_active=role.is_active,
                is_system=role.is_system,
                created_at=role.created_at,
                updated_at=role.updated_at,
                permissions=permissions,
                user_count=user_count,
                users=users
            )
        except Exception as e:
            log_error(f"创建DetachedRole失败: {e}")
            return cls(
                id=role.id,
                name=role.name,
                display_name=getattr(role, 'display_name', None),
                is_active=getattr(role, 'is_active', True),
                is_system=getattr(role, 'is_system', False)
            )

@dataclass
class DetachedPermission:
    """分离的权限数据类"""
    id: int
    name: str
    display_name: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # 关联信息
    roles: List[str] = field(default_factory=list)  # 关联的角色名称列表
    roles_count: int = 0  # 关联的角色数量
    users_count: int = 0  # 间接关联的用户数量（通过角色）
    direct_users: List[str] = field(default_factory=list)  # 直接关联的用户名称列表
    direct_users_count: int = 0  # 直接关联的用户数量

    @classmethod
    def from_permission(cls, permission) -> 'DetachedPermission':
        """从Permission模型创建分离的权限对象"""
        try:
            # 提取角色信息
            roles = []
            users_count = 0
            if hasattr(permission, 'roles') and permission.roles:
                roles = [role.name for role in permission.roles]
                # 计算间接关联的用户数量（通过角色）
                users_set = set()
                for role in permission.roles:
                    if hasattr(role, 'users') and role.users:
                        users_set.update(user.id for user in role.users)
                users_count = len(users_set)

            # 提取直接关联的用户信息
            direct_users = []
            direct_users_count = 0
            if hasattr(permission, 'users') and permission.users:
                direct_users = [user.username for user in permission.users]
                direct_users_count = len(permission.users)

            return cls(
                id=permission.id,
                name=permission.name,
                display_name=permission.display_name,
                category=permission.category,
                description=permission.description,
                created_at=permission.created_at,
                updated_at=permission.updated_at,
                roles=roles,
                roles_count=len(roles),
                users_count=users_count,
                direct_users=direct_users,
                direct_users_count=direct_users_count
            )
        except Exception as e:
            log_error(f"创建DetachedPermission失败: {e}")
            return cls(
                id=permission.id,
                name=permission.name,
                display_name=getattr(permission, 'display_name', None),
                category=getattr(permission, 'category', None),
                description=getattr(permission, 'description', None)
            )


class DetachedDataManager:
    """分离数据管理器 - 处理SQLAlchemy会话依赖问题，增强用户权限关联支持"""

    @staticmethod
    def get_user_safe(user_id: int) -> Optional[DetachedUser]:
        """安全获取用户数据（不会产生DetachedInstanceError）"""
        try:
            from .database import get_db
            from sqlalchemy.orm import joinedload

            # with get_db() as db:
            with db_safe("安全获取用户数据") as db:
                user = db.query(User).options(
                    joinedload(User.roles).joinedload(Role.permissions),
                    joinedload(User.permissions)  # 加载直接权限
                ).filter(User.id == user_id).first()

                if user:
                    return DetachedUser.from_user(user)
                return None

        except Exception as e:
            log_error(f"获取用户数据失败 (ID: {user_id}): {e}")
            return None

    @staticmethod
    def get_users_safe(search_term: str = None, limit: int = None) -> List[DetachedUser]:
        """安全获取用户列表"""
        try:
            from .database import get_db
            from sqlalchemy.orm import joinedload

            # with get_db() as db:
            with db_safe("安全获取用户列表") as db:
                query = db.query(User).options(
                    joinedload(User.roles).joinedload(Role.permissions),
                    joinedload(User.permissions)  # 加载直接权限
                )

                # 搜索过滤
                if search_term:
                    query = query.filter(
                        (User.username.contains(search_term)) |
                        (User.email.contains(search_term)) |
                        (User.full_name.contains(search_term))
                    )

                # 限制数量
                if limit:
                    query = query.limit(limit)

                users = query.all()
                return [DetachedUser.from_user(user) for user in users]

        except Exception as e:
            log_error(f"获取用户列表失败: {e}")
            return []

    @staticmethod
    def get_permission_safe(permission_id: int) -> Optional[DetachedPermission]:
        """安全获取权限数据"""
        try:
            from .database import get_db
            from sqlalchemy.orm import joinedload

            # with get_db() as db:
            with db_safe("安全获取权限数据") as db:
                permission = db.query(Permission).options(
                    joinedload(Permission.roles).joinedload(Role.users),
                    joinedload(Permission.users)  # 加载直接关联的用户
                ).filter(Permission.id == permission_id).first()

                if permission:
                    return DetachedPermission.from_permission(permission)
                return None

        except Exception as e:
            log_error(f"获取权限数据失败 (ID: {permission_id}): {e}")
            return None

    @staticmethod
    def get_permissions_safe(search_term: str = None, category: str = None, limit: int = None) -> List[DetachedPermission]:
        """安全获取权限列表"""
        try:
            from .database import get_db
            from sqlalchemy.orm import joinedload

            # with get_db() as db:
            with db_safe("安全获取权限列表") as db:
                query = db.query(Permission).options(
                    joinedload(Permission.roles).joinedload(Role.users),
                    joinedload(Permission.users)  # 加载直接关联的用户
                )

                # 搜索过滤
                if search_term:
                    query = query.filter(
                        (Permission.name.contains(search_term)) |
                        (Permission.display_name.contains(search_term)) |
                        (Permission.description.contains(search_term))
                    )

                # 分类过滤
                if category:
                    query = query.filter(Permission.category == category)

                # 限制数量
                if limit:
                    query = query.limit(limit)

                permissions = query.all()
                return [DetachedPermission.from_permission(perm) for perm in permissions]

        except Exception as e:
            log_error(f"获取权限列表失败: {e}")
            return []

    @staticmethod
    def get_role_safe(role_id: int) -> Optional[DetachedRole]:
        """安全获取角色数据"""
        try:
            from .database import get_db
            from sqlalchemy.orm import joinedload

            # with get_db() as db:
            with db_safe("安全获取角色数据") as db:
                role = db.query(Role).options(
                    joinedload(Role.permissions),
                    joinedload(Role.users)
                ).filter(Role.id == role_id).first()

                if role:
                    return DetachedRole.from_role(role)
                return None

        except Exception as e:
            log_error(f"获取角色数据失败 (ID: {role_id}): {e}")
            return None

    @staticmethod
    def get_roles_safe() -> List[DetachedRole]:
        """安全获取角色列表"""
        try:
            from .database import get_db
            from sqlalchemy.orm import joinedload

            # with get_db() as db:
            with db_safe("安全获取角色列表") as db:
                roles = db.query(Role).options(
                    joinedload(Role.permissions),
                    joinedload(Role.users)
                ).all()

                return [DetachedRole.from_role(role) for role in roles]

        except Exception as e:
            log_error(f"获取角色列表失败: {e}")
            return []

    @staticmethod
    def update_user_safe(user_id: int, **update_data) -> bool:
        """安全更新用户数据"""
        try:
            from .database import get_db

            # with get_db() as db:
            with db_safe("安全更新用户数据") as db:
                user = db.query(User).filter(User.id == user_id).first()
                if not user:
                    return False

                # 更新基本字段
                basic_fields = ['username', 'email', 'full_name', 'phone', 'avatar', 'bio', 
                               'is_active', 'is_verified', 'is_superuser']
                for field in basic_fields:
                    if field in update_data:
                        setattr(user, field, update_data[field])
                        log_info(f"更新用户字段 {field}: {update_data[field]}")

                db.commit()
                log_info(f"用户更新成功: {user.username}")
                return True

        except Exception as e:
            log_error(f"更新用户失败 (ID: {user_id}): {e}")
            return False

    @staticmethod
    def delete_user_safe(user_id: int) -> bool:
        """安全删除用户"""
        try:
            from .database import get_db

            # with get_db() as db:
            with db_safe("安全删除用户") as db:
                user = db.query(User).filter(User.id == user_id).first()
                if not user:
                    return False

                username = user.username
                db.delete(user)
                db.commit()
                log_warning(f"用户删除成功: {username}")
                return True

        except Exception as e:
            log_error(f"删除用户失败 (ID: {user_id}): {e}")
            return False

    @staticmethod
    def lock_user_safe(user_id: int, lock_duration_minutes: int = 30) -> bool:
        """安全锁定用户"""
        try:
            from .database import get_db

            # with get_db() as db:
            with db_safe("安全锁定用户") as db:
                user = db.query(User).filter(User.id == user_id).first()
                if not user:
                    return False

                user.locked_until = datetime.now() + timedelta(minutes=lock_duration_minutes)
                db.commit()
                log_info(f"用户锁定成功: {user.username}, 锁定到: {user.locked_until}")
                return True

        except Exception as e:
            log_info(f"锁定用户失败 (ID: {user_id}): {e}")
            return False

    @staticmethod
    def unlock_user_safe(user_id: int) -> bool:
        """安全解锁用户"""
        try:
            from .database import get_db

            # with get_db() as db:
            with db_safe("安全解锁用户") as db:
                user = db.query(User).filter(User.id == user_id).first()
                if not user:
                    return False

                user.locked_until = None
                user.failed_login_count = 0  # 重置失败登录次数
                db.commit()
                log_info(f"用户解锁成功: {user.username}")
                return True

        except Exception as e:
            log_error(f"解锁用户失败 (ID: {user_id}): {e}")
            return False

    @staticmethod
    def batch_unlock_users_safe() -> int:
        """批量解锁所有已锁定的用户"""
        try:
            from .database import get_db

            # with get_db() as db:
            with db_safe("批量解锁所有已锁定的用户") as db:
                locked_users = db.query(User).filter(User.locked_until.isnot(None)).all()
                count = len(locked_users)

                for user in locked_users:
                    user.locked_until = None
                    user.failed_login_count = 0

                db.commit()
                log_info(f"批量解锁用户成功，解锁数量: {count}")
                return count

        except Exception as e:
            log_error(f"批量解锁用户失败: {e}")
            return 0

    @staticmethod
    def create_role_safe(name: str, display_name: str = None, description: str = None, is_active: bool = True) -> Optional[int]:
        """安全创建角色"""
        try:
            from .database import get_db

            # with get_db() as db:
            with db_safe("安全创建角色") as db:
                # 检查角色名称是否已存在
                existing = db.query(Role).filter(Role.name == name).first()
                if existing:
                    log_warning(f"角色名称已存在: {name}")
                    return None

                role = Role(
                    name=name,
                    display_name=display_name,
                    description=description,
                    is_active=is_active
                )
                
                db.add(role)
                db.commit()
                
                log_info(f"角色创建成功: {name}")
                return role.id

        except Exception as e:
            log_error(f"创建角色失败: {e}")
            return None

    @staticmethod
    def update_role_safe(role_id: int, **update_data) -> bool:
        """安全更新角色数据"""
        try:
            from .database import get_db
            # with get_db() as db:
            with db_safe("安全创建角色") as db:
                role = db.query(Role).filter(Role.id == role_id).first()
                if not role:
                    return False

                # 更新基本字段
                basic_fields = ['display_name', 'description', 'is_active', 'is_system']
                for field in basic_fields:
                    if field in update_data:
                        setattr(role, field, update_data[field])
                        log_info(f"更新角色字段 {field}: {update_data[field]}")

                db.commit()
                log_success(f"角色更新成功: {role.name}")
                return True

        except Exception as e:
            log_error(f"更新角色失败 (ID: {role_id}): {e}")
            return False

    @staticmethod
    def delete_role_safe(role_id: int) -> bool:
        """安全删除角色"""
        try:
            from .database import get_db

            # with get_db() as db:
            with db_safe("安全删除角色") as db:
                role = db.query(Role).filter(Role.id == role_id).first()
                if not role:
                    return False

                # 检查是否有用户关联
                if hasattr(role, 'users') and role.users:
                    log_warning(f"无法删除角色，存在用户关联: {role.name}")
                    return False

                role_name = role.name
                db.delete(role)
                db.commit()
                log_success(f"角色删除成功: {role_name}")
                return True

        except Exception as e:
            log_error(f"删除角色失败 (ID: {role_id}): {e}")
            return False

    @staticmethod
    def create_permission_safe(name: str, display_name: str = None, category: str = None, description: str = None) -> Optional[int]:
        """安全创建权限"""
        try:
            from .database import get_db

            # with get_db() as db:
            with db_safe("安全创建权限") as db:
                # 检查权限名称是否已存在
                existing = db.query(Permission).filter(Permission.name == name).first()
                if existing:
                    log_warning(f"权限名称已存在: {name}")
                    return None

                permission = Permission(
                    name=name,
                    display_name=display_name,
                    category=category,
                    description=description
                )
                
                db.add(permission)
                db.commit()
                
                log_success(f"权限创建成功: {name}")
                return permission.id

        except Exception as e:
            log_error(f"创建权限失败: {e}")
            return None

    @staticmethod
    def update_permission_safe(permission_id: int, **update_data) -> bool:
        """安全更新权限数据"""
        try:
            from .database import get_db

            # with get_db() as db:
            with db_safe("安全更新权限数据") as db:
                permission = db.query(Permission).filter(Permission.id == permission_id).first()
                if not permission:
                    return False

                # 更新基本字段
                basic_fields = ['display_name', 'category', 'description']
                for field in basic_fields:
                    if field in update_data:
                        setattr(permission, field, update_data[field])
                        log_info(f"更新权限字段 {field}: {update_data[field]}")

                db.commit()
                log_success(f"权限更新成功: {permission.name}")
                return True

        except Exception as e:
            log_error(f"更新权限失败 (ID: {permission_id}): {e}")
            return False

    @staticmethod
    def delete_permission_safe(permission_id: int) -> bool:
        """安全删除权限"""
        try:
            from .database import get_db

            # with get_db() as db:
            with db_safe("安全删除权限") as db:
                permission = db.query(Permission).filter(Permission.id == permission_id).first()
                if not permission:
                    return False

                # 检查是否有角色关联
                has_role_associations = hasattr(permission, 'roles') and permission.roles
                has_user_associations = hasattr(permission, 'users') and permission.users
                
                if has_role_associations or has_user_associations:
                    log_warning(f"无法删除权限，存在关联关系: {permission.name}")
                    return False

                permission_name = permission.name
                db.delete(permission)
                db.commit()
                log_success(f"权限删除成功: {permission_name}")
                return True

        except Exception as e:
            log_error(f"删除权限失败 (ID: {permission_id}): {e}")
            return False

    # 新增：用户权限直接关联管理
    @staticmethod
    def add_permission_to_user_safe(user_id: int, permission_id: int) -> bool:
        """安全为用户添加直接权限"""
        try:
            from .database import get_db

            # with get_db() as db:
            with db_safe("安全为用户添加直接权限") as db:
                user = db.query(User).filter(User.id == user_id).first()
                permission = db.query(Permission).filter(Permission.id == permission_id).first()
                
                if not user or not permission:
                    return False

                if permission not in user.permissions:
                    user.permissions.append(permission)
                    db.commit()
                    log_info(f"为用户 {user.username} 添加权限 {permission.name}")
                    return True
                else:
                    log_info(f"用户 {user.username} 已拥有权限 {permission.name}")
                    return True

        except Exception as e:
            log_error(f"为用户添加权限失败 (用户ID: {user_id}, 权限ID: {permission_id}): {e}")
            return False

    @staticmethod
    def remove_permission_from_user_safe(user_id: int, permission_id: int) -> bool:
        """安全从用户移除直接权限"""
        try:
            from .database import get_db

            # with get_db() as db:
            with db_safe("安全从用户移除直接权限") as db:
                user = db.query(User).filter(User.id == user_id).first()
                permission = db.query(Permission).filter(Permission.id == permission_id).first()
                
                if not user or not permission:
                    return False

                if permission in user.permissions:
                    user.permissions.remove(permission)
                    db.commit()
                    log_info(f"从用户 {user.username} 移除权限 {permission.name}")
                    return True
                else:
                    log_info(f"用户 {user.username} 没有权限 {permission.name}")
                    return True

        except Exception as e:
            log_error(f"从用户移除权限失败 (用户ID: {user_id}, 权限ID: {permission_id}): {e}")
            return False

    @staticmethod
    def get_user_direct_permissions_safe(user_id: int) -> List[str]:
        """安全获取用户直接权限列表"""
        try:
            from .database import get_db
            from sqlalchemy.orm import joinedload

            # with get_db() as db:
            with db_safe("安全获取用户直接权限列表") as db:
                user = db.query(User).options(
                    joinedload(User.permissions)
                ).filter(User.id == user_id).first()

                if user and hasattr(user, 'permissions') and user.permissions:
                    return [perm.name for perm in user.permissions]
                return []

        except Exception as e:
            log_error(f"获取用户直接权限失败 (用户ID: {user_id}): {e}")
            return []

    @staticmethod
    def get_permission_direct_users_safe(permission_id: int) -> List[Dict[str, Any]]:
        """安全获取权限直接关联的用户列表"""
        try:
            from .database import get_db
            from sqlalchemy.orm import joinedload

            # with get_db() as db:
            with db_safe("安全获取权限直接关联的用户列表") as db:
                permission = db.query(Permission).options(
                    joinedload(Permission.users)
                ).filter(Permission.id == permission_id).first()

                if permission and hasattr(permission, 'users') and permission.users:
                    return [
                        {
                            'id': user.id,
                            'username': user.username,
                            'full_name': user.full_name,
                            'email': user.email,
                            'is_active': user.is_active
                        }
                        for user in permission.users
                    ]
                return []

        except Exception as e:
            log_error(f"获取权限直接关联用户失败 (权限ID: {permission_id}): {e}")
            return []

    @staticmethod
    def get_user_statistics() -> Dict[str, int]:
        """获取用户统计数据"""
        try:
            from .database import get_db
            
            # with get_db() as db:
            with db_safe("获取用户统计数据") as db:
                total_users = db.query(User).count()
                active_users = db.query(User).filter(User.is_active == True).count()
                verified_users = db.query(User).filter(User.is_verified == True).count()
                
                # 统计管理员用户（通过角色）
                admin_users = db.query(User).join(User.roles).filter(Role.name == 'admin').count()
                
                # 统计当前锁定的用户
                current_time = datetime.now()
                locked_users = db.query(User).filter(
                    User.locked_until != None,
                    User.locked_until > current_time
                ).count()
                
                superusers = db.query(User).filter(User.is_superuser == True).count()
                
                return {
                    'total_users': total_users,
                    'active_users': active_users,
                    'inactive_users': total_users - active_users,
                    'verified_users': verified_users,  # 保持兼容性
                    'admin_users': admin_users,        # 保持兼容性
                    'locked_users': locked_users,
                    'superusers': superusers
                }
                
        except Exception as e:
            log_error(f"获取用户统计失败: {e}")
            return {
                'total_users': 0,
                'active_users': 0,
                'inactive_users': 0,
                'verified_users': 0,
                'admin_users': 0,
                'locked_users': 0,
                'superusers': 0
            }

    @staticmethod
    def get_role_statistics() -> Dict[str, int]:
        """获取角色统计数据"""
        try:
            from .database import get_db
            
            # with get_db() as db:
            with db_safe(f"获取角色统计数据") as db:
                total_roles = db.query(Role).count()
                active_roles = db.query(Role).filter(Role.is_active == True).count()
                system_roles = db.query(Role).filter(Role.is_system == True).count()
                
                return {
                    'total_roles': total_roles,
                    'active_roles': active_roles,
                    'inactive_roles': total_roles - active_roles,
                    'system_roles': system_roles,
                    'custom_roles': total_roles - system_roles
                }
                
        except Exception as e:
            log_error(f"获取角色统计失败: {e}")
            return {
                'total_roles': 0,
                'active_roles': 0,
                'inactive_roles': 0,
                'system_roles': 0,
                'custom_roles': 0
            }

    @staticmethod
    def get_permission_statistics() -> Dict[str, int]:
        """获取权限统计数据"""
        try:
            from .database import get_db
            
            # with get_db() as db:
            with db_safe(f"获取权限统计数据") as db:
                total_permissions = db.query(Permission).count()
                system_permissions = db.query(Permission).filter(Permission.category == '系统').count()
                content_permissions = db.query(Permission).filter(Permission.category == '内容').count()
                
                return {
                    'total_permissions': total_permissions,
                    'system_permissions': system_permissions,
                    'content_permissions': content_permissions,
                    'other_permissions': total_permissions - system_permissions - content_permissions
                }
                
        except Exception as e:
            log_error(f"获取权限统计失败: {e}")
            return {
                'total_permissions': 0,
                'system_permissions': 0,
                'content_permissions': 0,
                'other_permissions': 0
            }

# 需要导入模型类
try:
    from .models import User, Role, Permission
except ImportError:
    log_error("无法导入模型类，某些功能可能不可用")

# 全局实例
detached_manager = DetachedDataManager()

# 便捷函数
def get_user_safe(user_id: int) -> Optional[DetachedUser]:
    """便捷函数：安全获取用户"""
    return detached_manager.get_user_safe(user_id)

def get_users_safe(search_term: str = None, limit: int = None) -> List[DetachedUser]:
    """便捷函数：安全获取用户列表"""
    return detached_manager.get_users_safe(search_term, limit)

def get_role_safe(role_id: int) -> Optional[DetachedRole]:
    """便捷函数：安全获取角色"""
    return detached_manager.get_role_safe(role_id)

def get_roles_safe() -> List[DetachedRole]:
    """便捷函数：安全获取角色列表"""
    return detached_manager.get_roles_safe()

def update_user_safe(user_id: int, **update_data) -> bool:
    """便捷函数：安全更新用户"""
    return detached_manager.update_user_safe(user_id, **update_data)

def update_role_safe(role_id: int, **update_data) -> bool:
    """便捷函数：安全更新角色"""
    return detached_manager.update_role_safe(role_id, **update_data)

def delete_user_safe(user_id: int) -> bool:
    """便捷函数：安全删除用户"""
    return detached_manager.delete_user_safe(user_id)

def delete_role_safe(role_id: int) -> bool:
    """便捷函数：安全删除角色"""
    return detached_manager.delete_role_safe(role_id)

def create_role_safe(name: str, display_name: str = None, description: str = None, is_active: bool = True) -> Optional[int]:
    """便捷函数：安全创建角色"""
    return detached_manager.create_role_safe(name, display_name, description, is_active)

def lock_user_safe(user_id: int, lock_duration_minutes: int = 30) -> bool:
    """便捷函数：安全锁定用户"""
    return detached_manager.lock_user_safe(user_id, lock_duration_minutes)

def unlock_user_safe(user_id: int) -> bool:
    """便捷函数：安全解锁用户"""
    return detached_manager.unlock_user_safe(user_id)

def batch_unlock_users_safe() -> int:
    """便捷函数：批量解锁用户"""
    return detached_manager.batch_unlock_users_safe()

def get_permission_safe(permission_id: int) -> Optional[DetachedPermission]:
    """便捷函数：安全获取权限"""
    return detached_manager.get_permission_safe(permission_id)

def get_permissions_safe(search_term: str = None, category: str = None, limit: int = None) -> List[DetachedPermission]:
    """便捷函数：安全获取权限列表"""
    return detached_manager.get_permissions_safe(search_term, category, limit)

def create_permission_safe(name: str, display_name: str = None, category: str = None, description: str = None) -> Optional[int]:
    """便捷函数：安全创建权限"""
    return detached_manager.create_permission_safe(name, display_name, category, description)

def update_permission_safe(permission_id: int, **update_data) -> bool:
    """便捷函数：安全更新权限"""
    return detached_manager.update_permission_safe(permission_id, **update_data)

def delete_permission_safe(permission_id: int) -> bool:
    """便捷函数：安全删除权限"""
    return detached_manager.delete_permission_safe(permission_id)

# 新增：用户权限直接关联便捷函数
def add_permission_to_user_safe(user_id: int, permission_id: int) -> bool:
    """便捷函数：安全为用户添加直接权限"""
    return detached_manager.add_permission_to_user_safe(user_id, permission_id)

def remove_permission_from_user_safe(user_id: int, permission_id: int) -> bool:
    """便捷函数：安全从用户移除直接权限"""
    return detached_manager.remove_permission_from_user_safe(user_id, permission_id)

def get_user_direct_permissions_safe(user_id: int) -> List[str]:
    """便捷函数：安全获取用户直接权限列表"""
    return detached_manager.get_user_direct_permissions_safe(user_id)

def get_permission_direct_users_safe(permission_id: int) -> List[Dict[str, Any]]:
    """便捷函数：安全获取权限直接关联的用户列表"""
    return detached_manager.get_permission_direct_users_safe(permission_id)
```

- **auth\models.py**
```python
"""
数据模型定义
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Table, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from .database import Base
import hashlib
import secrets

# 用户-角色关联表
user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id', ondelete='CASCADE')),
    Column('role_id', Integer, ForeignKey('roles.id', ondelete='CASCADE'))
)

# 角色-权限关联表（预留给权限管理包使用）
role_permissions = Table(
    'role_permissions',
    Base.metadata,
    Column('role_id', Integer, ForeignKey('roles.id', ondelete='CASCADE')),
    Column('permission_id', Integer, ForeignKey('permissions.id', ondelete='CASCADE'))
)

# 用户-权限关联表（用于特殊权限分配，预留）
user_permissions = Table(
    'user_permissions',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id', ondelete='CASCADE')),
    Column('permission_id', Integer, ForeignKey('permissions.id', ondelete='CASCADE'))
)

class User(Base):
    """用户模型"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    
    # 用户信息
    full_name = Column(String(100))
    phone = Column(String(20))
    avatar = Column(String(255))  # 头像URL
    bio = Column(Text)  # 个人简介
    
    # 状态信息
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)  # 邮箱验证状态
    is_superuser = Column(Boolean, default=False)  # 超级管理员
    
    # 登录信息
    last_login = Column(DateTime)
    login_count = Column(Integer, default=0)
    failed_login_count = Column(Integer, default=0)
    locked_until = Column(DateTime)  # 账户锁定时间
    
    # 会话信息
    session_token = Column(String(255), unique=True)
    remember_token = Column(String(255), unique=True)
    
    # 时间戳
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # 关系
    roles = relationship('Role', secondary=user_roles, back_populates='users')
    permissions = relationship('Permission', secondary=user_permissions, back_populates='users')
    login_logs = relationship('LoginLog', back_populates='user', cascade='all, delete-orphan')
    
    def set_password(self, password: str):
        """设置密码"""
        self.password_hash = self._hash_password(password)
    
    def check_password(self, password: str) -> bool:
        """验证密码"""
        return self.password_hash == self._hash_password(password)
    
    def _hash_password(self, password: str) -> str:
        """密码哈希（简单示例，生产环境建议使用bcrypt）"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def generate_session_token(self) -> str:
        """生成会话令牌"""
        self.session_token = secrets.token_urlsafe(32)
        return self.session_token
    
    def generate_remember_token(self) -> str:
        """生成记住我令牌"""
        self.remember_token = secrets.token_urlsafe(32)
        return self.remember_token
    
    def has_role(self, role_name: str) -> bool:
        """检查是否有指定角色"""
        try:
            return any(role.name == role_name for role in self.roles)
        except:
            # 如果roles未加载，返回False
            return False
    
    def has_permission(self, permission_name: str) -> bool:
        """检查是否有指定权限（预留接口）"""
        # 超级管理员拥有所有权限
        if self.is_superuser:
            return True
        
        try:
            # 检查用户直接分配的权限
            if any(perm.name == permission_name for perm in self.permissions):
                return True
            
            # 检查角色权限
            for role in self.roles:
                if hasattr(role, 'permissions') and any(perm.name == permission_name for perm in role.permissions):
                    return True
        except:
            # 如果关联数据未加载，返回False
            return False
        
        return False
    
    def get_permissions(self) -> set:
        """获取用户的所有权限（预留接口）"""
        if self.is_superuser:
            # 超级管理员返回所有权限
            from .database import get_db
            with get_db() as session:
                all_perms = session.query(Permission).all()
                return {perm.name for perm in all_perms}
        
        permissions = set()
        
        try:
            # 用户直接分配的权限
            permissions.update(perm.name for perm in self.permissions)
            
            # 角色权限
            for role in self.roles:
                if hasattr(role, 'permissions'):
                    permissions.update(perm.name for perm in role.permissions)
        except:
            # 如果关联数据未加载，返回空集合
            pass
        
        return permissions
    
    def __repr__(self):
        return f"<User(username='{self.username}', email='{self.email}')>"

class Role(Base):
    """角色模型"""
    __tablename__ = 'roles'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    display_name = Column(String(100))
    description = Column(Text)
    
    # 状态
    is_active = Column(Boolean, default=True)
    is_system = Column(Boolean, default=False)  # 系统角色不可删除
    
    # 时间戳
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # 关系
    users = relationship('User', secondary=user_roles, back_populates='roles')
    permissions = relationship('Permission', secondary=role_permissions, back_populates='roles')
    
    def __repr__(self):
        return f"<Role(name='{self.name}', display_name='{self.display_name}')>"

class Permission(Base):
    """权限模型（预留给权限管理包使用）"""
    __tablename__ = 'permissions'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    display_name = Column(String(100))
    category = Column(String(50))  # 权限分类
    description = Column(Text)
    
    # 时间戳
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # 关系
    roles = relationship('Role', secondary=role_permissions, back_populates='permissions')
    users = relationship('User', secondary=user_permissions, back_populates='permissions')
    
    def __repr__(self):
        return f"<Permission(name='{self.name}', category='{self.category}')>"

class LoginLog(Base):
    """登录日志模型"""
    __tablename__ = 'login_logs'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    
    # 登录信息
    ip_address = Column(String(45))
    user_agent = Column(String(255))
    login_type = Column(String(20))  # normal, remember_me, oauth
    is_success = Column(Boolean)
    failure_reason = Column(String(100))
    
    # 时间戳
    created_at = Column(DateTime, server_default=func.now())
    
    # 关系
    user = relationship('User', back_populates='login_logs')
    
    def __repr__(self):
        return f"<LoginLog(user_id={self.user_id}, is_success={self.is_success})>"
```

- **auth\navigation.py**
```python
"""
导航工具模块
"""
from nicegui import ui

def navigate_to(path: str):
    """导航到指定路径"""
    ui.navigate.to(path)

def redirect_to_login():
    """重定向到登录页"""
    from .config import auth_config
    ui.navigate.to(auth_config.login_route)

def redirect_to_home():
    """重定向到首页"""
    ui.navigate.to('/workbench')
```

- **auth\session_manager.py**
```python
"""
会话管理器 - 处理用户会话和缓存
"""
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class UserSession:
    """用户会话数据类"""
    id: int
    username: str
    email: str
    full_name: Optional[str] = None
    phone: Optional[str] = None
    avatar: Optional[str] = None
    bio: Optional[str] = None
    is_active: bool = True
    is_verified: bool = False
    is_superuser: bool = False
    last_login: Optional[datetime] = None
    login_count: int = 0
    created_at: Optional[datetime] = None
    roles: list = field(default_factory=list)
    permissions: set = field(default_factory=set)
    
    def has_role(self, role_name: str) -> bool:
        """检查是否有指定角色"""
        return role_name in self.roles
    
    def has_permission(self, permission_name: str) -> bool:
        """检查是否有指定权限"""
        return self.is_superuser or permission_name in self.permissions
    
    @classmethod
    def from_user(cls, user) -> 'UserSession':
        """从User模型创建会话对象"""
        # 提取角色名称
        role_names = []
        try:
            role_names = [role.name for role in user.roles]
        except:
            pass
        
        # 提取权限
        permissions = set()
        if user.is_superuser:
            permissions.add('*')  # 超级管理员拥有所有权限
        else:
            try:
                # 用户直接权限
                permissions.update(perm.name for perm in user.permissions)
                # 角色权限
                for role in user.roles:
                    if hasattr(role, 'permissions'):
                        permissions.update(perm.name for perm in role.permissions)
            except:
                pass
        
        return cls(
            id=user.id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            phone=user.phone,
            avatar=user.avatar,
            bio=user.bio,
            is_active=user.is_active,
            is_verified=user.is_verified,
            is_superuser=user.is_superuser,
            last_login=user.last_login,
            login_count=user.login_count,
            created_at=user.created_at,
            roles=role_names,
            permissions=permissions
        )

class SessionManager:
    """会话管理器"""
    
    def __init__(self):
        self._sessions: Dict[str, UserSession] = {}
    
    def create_session(self, token: str, user) -> UserSession:
        """创建会话"""
        session = UserSession.from_user(user)
        self._sessions[token] = session
        return session
    
    def get_session(self, token: str) -> Optional[UserSession]:
        """获取会话"""
        return self._sessions.get(token)
    
    def delete_session(self, token: str):
        """删除会话"""
        if token in self._sessions:
            del self._sessions[token]
    
    def clear_all_sessions(self):
        """清除所有会话"""
        self._sessions.clear()

# 全局会话管理器
session_manager = SessionManager()
```

- **auth\utils.py**
```python
"""
工具函数模块
"""
import re
from typing import Dict, Any
from .config import auth_config

def validate_email(email: str) -> bool:
    """验证邮箱格式"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password: str) -> Dict[str, Any]:
    """验证密码强度"""
    if len(password) < auth_config.password_min_length:
        return {
            'valid': False, 
            'message': f'密码长度至少需要{auth_config.password_min_length}个字符'
        }
    
    if auth_config.password_require_uppercase and not any(c.isupper() for c in password):
        return {
            'valid': False,
            'message': '密码需要包含至少一个大写字母'
        }
    
    if auth_config.password_require_lowercase and not any(c.islower() for c in password):
        return {
            'valid': False,
            'message': '密码需要包含至少一个小写字母'
        }
    
    if auth_config.password_require_numbers and not any(c.isdigit() for c in password):
        return {
            'valid': False,
            'message': '密码需要包含至少一个数字'
        }
    
    if auth_config.password_require_special:
        special_chars = r'!@#$%^&*()_+-=[]{}|;:,.<>?'
        if not any(c in special_chars for c in password):
            return {
                'valid': False,
                'message': '密码需要包含至少一个特殊字符'
            }
    
    return {'valid': True, 'message': '密码强度符合要求'}

def validate_username(username: str) -> Dict[str, Any]:
    """验证用户名"""
    if len(username) < 3:
        return {
            'valid': False,
            'message': '用户名长度至少需要3个字符'
        }
    
    if len(username) > 50:
        return {
            'valid': False,
            'message': '用户名长度不能超过50个字符'
        }
    
    # 只允许字母、数字、下划线和连字符
    pattern = r'^[a-zA-Z0-9_-]+$'
    if not re.match(pattern, username):
        return {
            'valid': False,
            'message': '用户名只能包含字母、数字、下划线和连字符'
        }
    
    return {'valid': True, 'message': '用户名格式正确'}

def format_datetime(dt) -> str:
    """格式化日期时间"""
    if not dt:
        return ''
    return dt.strftime('%Y-%m-%d %H:%M:%S')

def mask_email(email: str) -> str:
    """遮罩邮箱地址"""
    if not email or '@' not in email:
        return email
    
    username, domain = email.split('@')
    if len(username) <= 3:
        masked_username = username[0] + '*' * (len(username) - 1)
    else:
        masked_username = username[:2] + '*' * (len(username) - 4) + username[-2:]
    
    return f"{masked_username}@{domain}"

def get_avatar_url(user) -> str:
    """获取用户头像URL"""
    if user.avatar:
        return user.avatar
    
    # 使用默认头像或生成Gravatar
    from component.static_resources import static_manager
    return static_manager.get_avatar_path('default_avatar.png')

def sanitize_input(text: str) -> str:
    """清理用户输入"""
    if not text:
        return ''
    
    # 移除首尾空白
    text = text.strip()
    
    # 移除潜在的危险字符
    dangerous_chars = ['<', '>', '&', '"', "'", '\0']
    for char in dangerous_chars:
        text = text.replace(char, '')
    
    return text
```

## auth\pages

- **auth\pages\__init__.py** *(包初始化文件)*
```python
"""
认证相关页面
"""
from .login_page import login_page_content
from .logout_page import logout_page_content
from .register_page import register_page_content
from .profile_page import profile_page_content
from .change_password_page import change_password_page_content

from .permission_management_page import permission_management_page_content
from .role_management_page import role_management_page_content
from .user_management_page import user_management_page_content

# ✅ 新增: 导入大模型配置管理页面
from .llm_config_management_page import llm_config_management_page_content
from .prompt_config_management_page import prompt_config_management_page_content  # ✅ 新增

def no_permission_page_content():
    """权限不足页面"""
    from nicegui import ui
    with ui.column().classes('fit items-center justify-center'):
        ui.label('权限不足').classes('text-3xl font-bold text-red-600 dark:text-red-400')
        ui.label('您没有访问此功能的权限').classes('text-gray-600 dark:text-gray-400 mt-4')
        
        with ui.card().classes('w-full  mt-6 p-6 items-center justify-center'):
            ui.icon('block').classes('text-6xl text-red-500 mb-4')
            ui.label('访问被拒绝').classes('text-xl font-semibold text-red-600')
            ui.label('您需要管理员权限才能访问此功能').classes('text-gray-600 mt-2')
            
            with ui.row().classes('gap-2 mt-6 justify-center'):
                # 选择不同的layout这里要做响应的切换
                # simple_spa_layout->simple_navigate_to / spa_layout->navigate_to
                def go_home():
                    from component import universal_navigate_to
                    try:
                        universal_navigate_to('home', '首页')
                    except RuntimeError as e:
                        ui.notify('导航失败: 布局未初始化', type='warning')
                
                ui.button('返回首页', icon='home', on_click=go_home).classes('bg-blue-500 text-white')
                ui.button('联系管理员', icon='contact_support', 
                        on_click=lambda: ui.notify('请联系系统管理员申请权限', type='info')).classes('bg-gray-500 text-white')

def get_auth_page_handlers():
    """获取所有认证页面处理函数"""
    return {
        'login': login_page_content,
        'logout': logout_page_content,
        'register': register_page_content,
        'user_profile': profile_page_content,
        'change_password': change_password_page_content,
        'permission_management': permission_management_page_content,
        'role_management': role_management_page_content,
        'user_management': user_management_page_content,
        'no_permission': no_permission_page_content,
        # ✅ 新增: 大模型配置管理页面路由
        'llm_config_management': llm_config_management_page_content,
        'prompt_config_management': prompt_config_management_page_content,  # ✅ 新增
    }

__all__ = [
    'login_page_content',
    'logout_page_content',
    'register_page_content', 
    'profile_page_content',
    'change_password_page_content',
    'permission_management_page_content',
    'role_management_page_content',
    'user_management_page_content',
    'no_permission_page_content',
    # ✅ 新增导出
    'llm_config_management_page_content',
    'prompt_config_management_page_content',  # ✅ 新增导出
    'get_auth_page_handlers'
]
```

- **auth\pages\change_password_page.py**
```python
from nicegui import ui
from ..auth_manager import auth_manager
from ..decorators import require_login
from ..utils import validate_password
import re
from common.log_handler import (
    # 日志记录函数
    log_trace, log_debug, log_info, log_success, 
    log_warning, log_error, log_critical,
    # 安全执行
    safe, db_safe,
    # 装饰器
    safe_protect, catch,
    # Logger 实例
    get_logger
)
logger = get_logger(__file__)

@require_login()
@safe_protect(name="修改密码页面", error_msg="修改密码页面发生错误", return_on_error=None)
def change_password_page_content():
    """修改密码页面内容"""
    user = auth_manager.current_user
    if not user:
        ui.notify('请先登录', type='warning')
        return

    # Page Title and Subtitle
    with ui.column().classes('w-full items-center md:items-start p-4 md:p-2'):
        ui.label('修改密码').classes('text-4xl font-extrabold text-orange-700 dark:text-orange-300 mb-2')
        ui.label('为了账户安全，请定期修改您的密码').classes('text-lg text-gray-600 dark:text-gray-400')

    with ui.row().classes('w-full justify-center p-4 md:p-2'):
        with ui.card().classes('w-full p-4 mb-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-700'): # Use w-full directly here

            with ui.grid().classes('w-full grid-cols-1 md:grid-cols-4 gap-10'):
                # Left side: Password change form (3/4 width on medium+)
                with ui.column().classes('col-span-1 md:col-span-3 '): # Occupies 3 out of 4 columns
                    ui.label('修改密码表单').classes('text-2xl font-bold mb-2 text-gray-800 dark:text-gray-200 border-b pb-4 border-gray-200 dark:border-gray-700')

                    # Password input form
                    current_password = ui.input(
                        '当前密码',
                        password=True,
                        placeholder='请输入当前密码'
                    ).classes('w-full mb-2').props('outlined clearable')

                    new_password = ui.input(
                        '新密码',
                        password=True,
                        placeholder='请输入新密码'
                    ).classes('w-full mb-2').props('outlined clearable')

                    confirm_password = ui.input(
                        '确认新密码',
                        password=True,
                        placeholder='请再次输入新密码'
                    ).classes('w-full mb-2').props('outlined clearable')

                    # Password strength indicator
                    with ui.column().classes('w-full items-start mb-4'):
                        ui.label('密码强度').classes('text-base font-semibold text-gray-700 dark:text-gray-300 mb-2')
                        with ui.row().classes('w-full items-center gap-3'):
                            strength_progress = ui.linear_progress(value=0).classes('flex-1 h-3 rounded-full').props('rounded color=primary')
                            strength_label = ui.label('无').classes('text-sm font-medium text-gray-600 dark:text-gray-400 min-w-[50px]')

                    def check_password_strength(password):
                        """检查密码强度"""
                        if not password:
                            return 0, '无', 'text-gray-600 dark:text-gray-400'

                        score = 0
                        # Length check
                        if len(password) >= 8:
                            score += 1
                        if len(password) >= 12:
                            score += 1

                        # Character type check
                        if re.search(r'[a-z]', password):
                            score += 1
                        if re.search(r'[A-Z]', password):
                            score += 1
                        if re.search(r'\d', password):
                            score += 1
                        if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
                            score += 1

                        # Strength determination
                        if score <= 2:
                            return score / 6, '弱', 'text-red-600 dark:text-red-400'
                        elif score <= 4:
                            return score / 6, '中等', 'text-orange-600 dark:text-orange-400'
                        elif score <= 5:
                            return score / 6, '强', 'text-green-600 dark:text-green-400'
                        else:
                            return 1.0, '很强', 'text-green-700 dark:text-green-300'

                    def update_password_strength():
                        """更新密码强度显示"""
                        password = new_password.value
                        strength, text, label_color = check_password_strength(password)
                        strength_progress.set_value(strength)
                        
                        # Set progress bar color based on strength
                        if strength == 0:
                            strength_progress.props('color=grey')
                        elif strength <= 0.33:
                            strength_progress.props('color=red')
                        elif strength <= 0.66:
                            strength_progress.props('color=orange')
                        else:
                            strength_progress.props('color=green')
                        
                        strength_label.text = text
                        strength_label.classes(replace=f'text-sm font-medium {label_color} min-w-[50px]')

                    # Bind password strength check
                    new_password.on('input', update_password_strength)

                    def handle_password_change():
                        """处理密码修改"""
                        # Get input values
                        current_pwd = current_password.value
                        new_pwd = new_password.value
                        confirm_pwd = confirm_password.value

                        # Basic validation
                        if not current_pwd:
                            ui.notify('请输入当前密码', type='warning', position='top')
                            current_password.run_method('focus')
                            return

                        if not new_pwd:
                            ui.notify('请输入新密码', type='warning', position='top')
                            new_password.run_method('focus')
                            return

                        if not confirm_pwd:
                            ui.notify('请确认新密码', type='warning', position='top')
                            confirm_password.run_method('focus')
                            return

                        if new_pwd != confirm_pwd:
                            ui.notify('两次输入的密码不一致', type='warning', position='top')
                            confirm_password.run_method('focus')
                            confirm_password.run_method('select')
                            return

                        if current_pwd == new_pwd:
                            ui.notify('新密码不能与当前密码相同', type='warning', position='top')
                            new_password.run_method('focus')
                            new_password.run_method('select')
                            return

                        # Validate new password strength with backend logic
                        password_result = validate_password(new_pwd)
                        if not password_result['valid']:
                            ui.notify(password_result['message'], type='warning', position='top')
                            new_password.run_method('focus')
                            new_password.run_method('select')
                            return

                        # Check password strength visually (can be combined with backend validation)
                        strength, text, _ = check_password_strength(new_pwd)
                        if strength < 0.5:  # Strength too weak
                            ui.notify('密码强度太弱，请选择更强的密码', type='warning', position='top')
                            new_password.run_method('focus')
                            new_password.run_method('select')
                            return

                        # Show loading state
                        change_button.disable()
                        change_button.props('loading')

                        try:
                            # Call authentication manager to change password
                            result = auth_manager.change_password(
                                user_id=user.id,
                                old_password=current_pwd,
                                new_password=new_pwd
                            )

                            if result['success']:
                                ui.notify('密码修改成功！即将跳转到登录页面...', type='positive', position='top')
                                # Clear form
                                current_password.value = ''
                                new_password.value = ''
                                confirm_password.value = ''
                                update_password_strength() # Reset strength indicator

                                # Manually perform logout to clear current session
                                auth_manager.logout()

                                # Redirect to login page after a delay
                                ui.timer(1.5, lambda: ui.navigate.to('/login'), once=True)
                            else:
                                ui.notify(result['message'], type='negative', position='top')
                                if '原密码错误' in result['message']:
                                    current_password.run_method('focus')
                                    current_password.run_method('select')

                        except Exception as e:
                            ui.notify(f'密码修改失败: {str(e)}', type='negative', position='top')

                        finally:
                            # Restore button state
                            change_button.enable()
                            change_button.props(remove='loading')

                    # Change password button
                    change_button = ui.button(
                        '修改密码',
                        icon='save',
                        on_click=handle_password_change
                    ).classes('w-full mt-6 bg-indigo-600 hover:bg-indigo-700 dark:bg-indigo-700 dark:hover:bg-indigo-800 text-white py-3 text-lg font-semibold rounded-lg shadow-md transition-colors duration-200')

                    # Support Enter key submission
                    current_password.on('keydown.enter', handle_password_change)
                    new_password.on('keydown.enter', handle_password_change)
                    confirm_password.on('keydown.enter', handle_password_change)

                # Right side: Password requirements (1/4 width on medium+)
                with ui.column().classes('col-span-1'): # Occupies 1 out of 4 columns
                    with ui.card().classes('w-full p-6 shadow-lg rounded-lg bg-gray-50 dark:bg-gray-700 h-full'): # h-full to make it fill vertical space
                        ui.label('密码要求').classes('text-2xl font-bold mb-6 text-gray-800 dark:text-gray-200 border-b pb-4 border-gray-200 dark:border-gray-600')

                        requirements = [
                            '至少8个字符',
                            '包含大写字母 (A-Z)',
                            '包含小写字母 (a-z)',
                            '包含数字 (0-9)',
                            '包含特殊字符 (!@#$%^&*)',
                        ]

                        for req in requirements:
                            with ui.row().classes('items-center gap-3 mt-3'):
                                ui.icon('check_circle').classes('text-green-600 dark:text-green-400 text-xl flex-shrink-0')
                                ui.label(req).classes('text-base text-gray-700 dark:text-gray-300 leading-relaxed')

                    # The "安全提示" and "账户安全状态" blocks are completely removed.
```

- **auth\pages\llm_config_management_page.py**
```python
"""
大模型配置管理页面 - 优化版
管理 config/yaml/llm_model_config.yaml 中的模型配置
提供新建、修改、删除功能

优化内容:
1. 添加 model_name 字段配置 (API实际使用的模型名称)
2. 在 "显示名称 (name)" 旁边添加 "模型名称 (model_name)" 输入框
3. 更新保存逻辑,包含 model_name 字段
"""
from nicegui import ui
from ..decorators import require_role
from typing import Optional, Dict, Any
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from config.yaml_config_manager import LLMConfigFileManager
from config.provider_manager import get_provider_manager, ProviderInfo
from component.chat.config import get_llm_config_manager
from common.log_handler import (
    # 日志记录函数
    log_trace, log_debug, log_info, log_success, 
    log_warning, log_error, log_critical,
    # 安全执行
    safe, db_safe,
    # 装饰器
    safe_protect, catch,
    # Logger 实例
    get_logger
)
logger = get_logger(__file__)

class LLMConfigManagementPage:
    """大模型配置管理页面类"""
    
    def __init__(self):
        self.file_manager = LLMConfigFileManager()
        self.provider_manager = get_provider_manager()
        self.table = None
        self.models_data = []

    def render(self):
        """渲染页面"""

        ui.add_head_html('''
            <style>
            .llm_edit_dialog-hide-scrollbar {
                overflow-y: auto;
                scrollbar-width: none;
                -ms-overflow-style: none;
            }
            .llm_edit_dialog-hide-scrollbar::-webkit-scrollbar {
                display: none;
            }
            </style>
        ''')
        
        # 页面标题
        with ui.row().classes('w-full items-center justify-between mb-6'):
            with ui.column():
                ui.label('大模型配置管理').classes('text-3xl font-bold text-blue-800 dark:text-blue-200')
                ui.label('管理系统中的大模型API配置').classes('text-sm text-gray-600 dark:text-gray-400')
            
            with ui.row().classes('gap-2'):
                ui.button('Provider 列表', icon='list', 
                         on_click=self.show_provider_list_dialog).props('flat')
                ui.button('刷新列表', icon='refresh', 
                         on_click=self.refresh_table).classes('bg-gray-500 text-white')
                ui.button('新增配置', icon='add', 
                         on_click=self.show_add_dialog).classes('bg-blue-500 text-white')
        
        # 配置列表表格
        self.create_table()
    
    def create_table(self):
        """创建配置列表表格"""
        # 加载数据
        self.load_models_data()
        
        # 表格列定义
        columns = [
            {
                'name': 'provider', 
                'label': '提供商', 
                'field': 'provider', 
                'align': 'left',
                'sortable': True
            },
            {
                'name': 'model_key', 
                'label': '配置唯一标识', 
                'field': 'model_key', 
                'align': 'left',
                'sortable': True
            },
            # {
            #     'name': 'name', 
            #     'label': '显示名称', 
            #     'field': 'name', 
            #     'align': 'left'
            # },
            {
                'name': 'model_name', 
                'label': '模型名称', 
                'field': 'model_name', 
                'align': 'left'
            },
            {
                'name': 'base_url', 
                'label': 'API地址', 
                'field': 'base_url', 
                'align': 'left'
            },
            {
                'name': 'enabled', 
                'label': '状态', 
                'field': 'enabled', 
                'align': 'center',
                'sortable': True
            },
            {
                'name': 'actions', 
                'label': '操作', 
                'field': 'actions', 
                'align': 'center'
            }
        ]
        
        # 创建表格
        self.table = ui.table(
            columns=columns,
            rows=self.models_data,
            row_key='model_key',
            pagination={'rowsPerPage': 10, 'sortBy': 'provider'},
            column_defaults={
                    'align': 'left',
                    'headerClasses': 'uppercase text-primary text-base font-bold',
                    'classes': 'text-base'
            }
        ).classes('w-full')
        
        # 添加操作按钮列的插槽
        self.table.add_slot('body-cell-enabled', '''
            <q-td key="enabled" :props="props">
                <q-badge :color="props.row.enabled ? 'green' : 'red'">
                    {{ props.row.enabled ? '已启用' : '已禁用' }}
                </q-badge>
            </q-td>
        ''')
        
        self.table.add_slot('body-cell-actions', '''
            <q-td key="actions" :props="props">
                <q-btn flat dense icon="edit" color="blue" 
                       @click="$parent.$emit('edit', props.row)" />
                <q-btn flat dense icon="delete" color="red" 
                       @click="$parent.$emit('delete', props.row)" />
            </q-td>
        ''')
        
        # 绑定操作事件
        self.table.on('edit', lambda e: self.show_edit_dialog(e.args))
        self.table.on('delete', lambda e: self.show_delete_confirm(e.args))
    
    def load_models_data(self):
        """从配置文件加载模型数据"""
        self.models_data = []
        
        providers_config = self.file_manager.get_provider_configs()
        
        for provider_key, models in providers_config.items():
            provider_display = self.provider_manager.get_provider_display_name(provider_key)
            
            for model_key, config in models.items():
                if isinstance(config, dict):
                    self.models_data.append({
                        'provider_key': provider_key,  # 原始 key
                        'provider': provider_display,   # 显示名称
                        'model_key': model_key,
                        'name': config.get('name', model_key),
                        'model_name': config.get('model_name', model_key),  # ✅ 添加 model_name
                        'base_url': config.get('base_url', ''),
                        'enabled': config.get('enabled', True),
                        '_raw_config': config  # 保存完整配置用于编辑
                    })
    
    def refresh_table(self):
        """刷新表格数据"""
        self.load_models_data()
        if self.table:
            self.table.update()
        ui.notify('配置列表已刷新', type='positive')
    
    def show_provider_list_dialog(self):
        """显示 Provider 列表对话框"""
        with ui.dialog() as dialog, ui.card().classes('w-full max-w-3xl'):
            ui.label('可用的模型提供商').classes('text-xl font-bold mb-4')
            
            providers = self.provider_manager.get_all_providers()
            
            # 使用卡片展示 Provider
            with ui.grid(columns=2).classes('w-full gap-4 llm_edit_dialog-hide-scrollbar'):
                for provider in providers:
                    with ui.card().classes('w-full'):
                        with ui.card_section():
                            with ui.row().classes('items-center gap-2'):
                                ui.icon(provider.icon).classes('text-2xl text-blue-500')
                                ui.label(provider.display_name).classes('text-lg font-bold')
                                ui.badge(provider.key).classes('ml-2')
                        
                        with ui.card_section():
                            ui.label(provider.description).classes('text-sm text-gray-600')
                        
                        with ui.card_section():
                            ui.label(f'默认地址: {provider.default_base_url}').classes('text-xs text-gray-500')
                        
                        with ui.card_actions().classes('justify-end'):
                            # 显示该 Provider 下的模型数量
                            models_count = len([
                                m for m in self.models_data 
                                if m['provider'] == provider.key
                            ])
                            ui.label(f'{models_count} 个模型').classes('text-sm text-gray-500')
            
            with ui.row().classes('w-full justify-end mt-4'):
                ui.button('关闭', on_click=dialog.close).props('flat')
        
        dialog.open()
    
    def show_add_dialog(self):
        """显示新增配置对话框"""
        # 获取所有 provider 选项
        provider_options = {
            p.key: p.display_name 
            for p in self.provider_manager.get_all_providers()
        }
        
        with ui.dialog() as dialog, ui.card().classes('w-full max-w-2xl'):
            ui.label('新增模型配置').classes('text-xl font-bold mb-4')
            
            # 表单字段
            with ui.column().classes('w-full gap-4 llm_edit_dialog-hide-scrollbar'):
                # 基本信息
                ui.label('基本信息').classes('text-lg font-semibold text-blue-600')
                with ui.grid(columns=2).classes('w-full gap-4'):
                    provider_select = ui.select(
                        options=provider_options,
                        label='选择 Provider *',
                        with_input=True
                    ).classes('w-full')
                    
                    model_key_input = ui.input(
                        label='配置唯一标识*',
                        placeholder='说明：可以是任意的唯一字符串'
                    ).classes('w-full')
                
                # ✅ 优化: 将 name 和 model_name 放在一起
                with ui.grid(columns=2).classes('w-full gap-4'):
                    model_name_input = ui.input(
                        label='显示名称 *',
                        placeholder='说明: 任何有意义名称，便于用户检索区分'
                    ).classes('w-full')
                    
                    # ✅ 新增: model_name 字段
                    model_name_api_input = ui.input(
                        label='模型名称 *',
                        placeholder='大模型名称，如：deepseek-chat'
                    ).classes('w-full')
                
                # API配置
                ui.separator()
                ui.label('API配置').classes('text-lg font-semibold text-blue-600')
                
                base_url_input = ui.input(
                    label='API地址 *',
                    placeholder='如：https://api.example.com/v1'
                ).classes('w-full')
                
                api_key_input = ui.input(
                    label='API Key *',
                    placeholder='sk-...',
                    password=True,
                    password_toggle_button=True
                ).classes('w-full')
                
                # 高级配置
                ui.separator()
                ui.label('高级配置').classes('text-lg font-semibold text-blue-600')
                
                with ui.grid(columns=3).classes('w-full gap-4'):
                    timeout_input = ui.number(
                        label='超时时间(秒)',
                        value=60,
                        min=10,
                        max=300
                    ).classes('w-full')
                    
                    max_retries_input = ui.number(
                        label='最大重试次数',
                        value=3,
                        min=0,
                        max=10
                    ).classes('w-full')
                    
                    stream_switch = ui.switch(
                        '支持流式输出',
                        value=True
                    ).classes('w-full')
                
                enabled_switch = ui.switch(
                    '启用此配置',
                    value=True
                ).classes('w-full')
                
                description_input = ui.textarea(
                    label='描述',
                    placeholder='简要描述该模型配置...'
                ).classes('w-full').props('rows=2')
            
            # 按钮
            with ui.row().classes('w-full justify-end gap-2 mt-4'):
                ui.button('取消', on_click=dialog.close).props('flat')
                ui.button(
                    '保存',
                    icon='save',
                    on_click=lambda: self.save_new_config(
                        dialog,
                        provider_select.value,
                        model_key_input.value,
                        model_name_input.value,
                        model_name_api_input.value,  # ✅ 新增参数
                        base_url_input.value,
                        api_key_input.value,
                        timeout_input.value,
                        max_retries_input.value,
                        stream_switch.value,
                        enabled_switch.value,
                        description_input.value
                    )
                ).classes('bg-blue-500 text-white')
        
        dialog.open()
    
    def save_new_config(self, dialog, provider, model_key, name, model_name_api,
                        base_url, api_key, timeout, max_retries, stream, enabled, description):
        """保存新配置"""
        # 验证必填字段
        if not all([provider, model_key, name, model_name_api, base_url, api_key]):
            ui.notify('请填写所有必填字段', type='negative')
            return
        
        # 构建配置对象
        config = {
            'name': name,
            'provider': provider,
            'model_name': model_name_api,  # ✅ 添加 model_name 字段
            'base_url': base_url,
            'api_key': api_key,
            'timeout': int(timeout),
            'max_retries': int(max_retries),
            'stream': stream,
            'enabled': enabled,
            'description': description,
        }
        
        # 保存到文件
        success = self.file_manager.add_model_config(provider, model_key, config)
        
        if success:
            ui.notify(f'成功添加模型配置: {name}', type='positive')
            
            # 重新加载配置管理器
            get_llm_config_manager().reload_config()
            
            dialog.close()
            
            # 刷新页面
            ui.navigate.reload()
        else:
            ui.notify('保存失败,可能配置已存在', type='negative')
    
    def show_edit_dialog(self, row_data):
        """显示编辑配置对话框"""
        provider = row_data['provider_key']  # 使用原始 key
        model_key = row_data['model_key']
        config = row_data['_raw_config']
        
        with ui.dialog() as dialog, ui.card().classes('w-full max-w-2xl'):
            ui.label(f'编辑配置: {row_data["name"]}').classes('text-xl font-bold mb-4')
            
            # 表单字段(预填充)
            with ui.column().classes('w-full gap-4 llm_edit_dialog-hide-scrollbar'):
                # 基本信息
                ui.label('基本信息').classes('text-lg font-semibold text-blue-600')
                
                with ui.grid(columns=2).classes('w-full gap-4'):
                    # 显示 Provider 和 model_key (不可编辑)
                    provider_display = self.provider_manager.get_provider_display_name(provider)
                    with ui.column().classes('w-full'):
                        ui.label('提供商').classes('text-sm text-gray-600')
                        ui.label(f'{provider_display} ({provider})').classes('text-base font-semibold')
                    
                    with ui.column().classes('w-full'):
                        ui.label('配置唯一标识').classes('text-sm text-gray-600')
                        ui.label(model_key).classes('text-base font-semibold')
                
                # ✅ 优化: 将 name 和 model_name 放在一起
                with ui.grid(columns=2).classes('w-full gap-4'):
                    model_name_input = ui.input(
                        label='显示名称 *',
                        value=config.get('name', '')
                    ).classes('w-full')
                    
                    # ✅ 新增: model_name 字段
                    model_name_api_input = ui.input(
                        label='模型名称 *',
                        value=config.get('model_name', model_key)  # 如果没有则使用 model_key
                    ).classes('w-full')
                
                # API配置
                ui.separator()
                ui.label('API配置').classes('text-lg font-semibold text-blue-600')
                
                base_url_input = ui.input(
                    label='API地址 *',
                    value=config.get('base_url', '')
                ).classes('w-full')
                
                api_key_input = ui.input(
                    label='API Key *',
                    value=config.get('api_key', ''),
                    password=True,
                    password_toggle_button=True
                ).classes('w-full')
                
                # 高级配置
                ui.separator()
                ui.label('高级配置').classes('text-lg font-semibold text-blue-600')
                
                with ui.grid(columns=3).classes('w-full gap-4'):
                    timeout_input = ui.number(
                        label='超时时间(秒)',
                        value=config.get('timeout', 60),
                        min=10,
                        max=300
                    ).classes('w-full')
                    
                    max_retries_input = ui.number(
                        label='最大重试次数',
                        value=config.get('max_retries', 3),
                        min=0,
                        max=10
                    ).classes('w-full')
                    
                    stream_switch = ui.switch(
                        '支持流式输出',
                        value=config.get('stream', True)
                    ).classes('w-full')
                
                enabled_switch = ui.switch(
                    '启用此配置',
                    value=config.get('enabled', True)
                ).classes('w-full')
                
                description_input = ui.textarea(
                    label='描述',
                    value=config.get('description', '')
                ).classes('w-full').props('rows=2')
            
            # 按钮
            with ui.row().classes('w-full justify-end gap-2 mt-4'):
                ui.button('取消', on_click=dialog.close).props('flat')
                ui.button(
                    '保存修改',
                    icon='save',
                    on_click=lambda: self.save_edit_config(
                        dialog,
                        provider,
                        model_key,
                        model_name_input.value,
                        model_name_api_input.value,  # ✅ 新增参数
                        base_url_input.value,
                        api_key_input.value,
                        timeout_input.value,
                        max_retries_input.value,
                        stream_switch.value,
                        enabled_switch.value,
                        description_input.value
                    )
                ).classes('bg-blue-500 text-white')
        
        dialog.open()
    
    def save_edit_config(self, dialog, provider, model_key, name, model_name_api,
                        base_url, api_key, timeout, max_retries, stream, enabled, description):
        """保存编辑后的配置"""
        # 验证必填字段
        if not all([name, model_name_api, base_url, api_key]):
            ui.notify('请填写所有必填字段', type='negative')
            return
        
        # 构建配置对象
        config = {
            'name': name,
            'provider': provider,
            'model_name': model_name_api,  # ✅ 添加 model_name 字段
            'base_url': base_url,
            'api_key': api_key,
            'timeout': int(timeout),
            'max_retries': int(max_retries),
            'stream': stream,
            'enabled': enabled,
            'description': description,
        }
        
        # 更新文件
        success = self.file_manager.update_model_config(provider, model_key, config)
        
        if success:
            ui.notify(f'成功更新模型配置: {name}', type='positive')
            
            # 重新加载配置管理器
            get_llm_config_manager().reload_config()
            
            dialog.close()
            
            # 刷新页面
            ui.navigate.reload()
        else:
            ui.notify('更新失败', type='negative')
    
    def show_delete_confirm(self, row_data):
        """显示删除确认对话框"""
        provider = row_data['provider_key']  # 使用原始 key
        model_key = row_data['model_key']
        name = row_data['name']
        
        with ui.dialog() as dialog, ui.card():
            with ui.column().classes('items-center gap-4 p-4'):
                ui.icon('warning', size='64px').classes('text-orange-500')
                ui.label('确认删除').classes('text-xl font-bold')
                ui.label(f'确定要删除模型配置 "{name}" 吗?').classes('text-gray-600')
                ui.label('此操作不可恢复!').classes('text-sm text-red-500')
                
                with ui.row().classes('gap-2 mt-4'):
                    ui.button('取消', on_click=dialog.close).props('flat')
                    ui.button(
                        '确认删除',
                        icon='delete',
                        on_click=lambda: self.delete_config(dialog, provider, model_key, name)
                    ).classes('bg-red-500 text-white')
        
        dialog.open()
    
    def delete_config(self, dialog, provider, model_key, name):
        """删除配置"""
        success = self.file_manager.delete_model_config(provider, model_key)
        
        if success:
            ui.notify(f'成功删除模型配置: {name}', type='positive')
            
            # 重新加载配置管理器
            get_llm_config_manager().reload_config()
            
            dialog.close()
            
            # 刷新页面
            ui.navigate.reload()
        else:
            ui.notify('删除失败', type='negative')

@require_role('admin')
@safe_protect(name=f"大模型配置管理页面/{__name__}", error_msg=f"大模型配置管理页面加载失败")
def llm_config_management_page_content():
    """大模型配置管理页面入口函数"""
    page = LLMConfigManagementPage()
    page.render()
```

- **auth\pages\login_page.py**
```python
"""
登录页面
"""
from nicegui import ui
from ..auth_manager import auth_manager
from ..config import auth_config
from ..decorators import public_route
from common.log_handler import (
    # 日志记录函数
    log_trace, log_debug, log_info, log_success, 
    log_warning, log_error, log_critical,
    # 安全执行
    safe, db_safe,
    # 装饰器
    safe_protect, catch,
    # Logger 实例
    get_logger
)
logger = get_logger(__file__)

@public_route
@safe_protect(name="登录页面", error_msg="登录页面发生错误", return_on_error=None)
def login_page_content():
    """登录页面内容"""
    # 检查是否已登录
    if auth_manager.is_authenticated():
        ui.notify('您已经登录了', type='info')
        ui.navigate.to('/workbench')
        return
    
    with ui.column().classes('absolute-center items-center'):
        with ui.card().classes('w-96 shadow-lg'):
            ui.label('用户登录').classes('text-2xl font-bold text-center w-full mb-4')
            
            # 登录表单
            username_input = ui.input(
                '用户名/邮箱',
                placeholder='请输入用户名或邮箱'
            ).classes('w-full').props('clearable')
            
            password_input = ui.input(
                '密码',
                placeholder='请输入密码',
                password=True,
                password_toggle_button=True
            ).classes('w-full mt-4').props('clearable')
            
            # 记住我选项
            remember_checkbox = ui.checkbox(
                '记住我',
                value=False
            ).classes('mt-4') if auth_config.allow_remember_me else None
            
            # 登录按钮
            async def handle_login():
                username = username_input.value.strip()
                password = password_input.value
                
                if not username or not password:
                    ui.notify('请输入用户名和密码', type='warning')
                    return
                
                # 显示加载状态
                login_button.disable()
                login_button.props('loading')
                
                # 执行登录
                result = auth_manager.login(
                    username, 
                    password,
                    remember_checkbox.value if remember_checkbox else False
                )
                
                # 恢复按钮状态
                login_button.enable()
                login_button.props(remove='loading')
                
                if result['success']:
                    ui.notify(f'欢迎回来，{result["user"].username}！', type='positive')
                    # 重定向到首页或之前的页面
                    ui.navigate.to('/workbench')
                else:
                    ui.notify(result['message'], type='negative')
            
            login_button = ui.button(
                '登录',
                on_click=handle_login
            ).classes('w-full mt-6').props('color=primary size=lg')
            
            # 快捷登录（Enter键）
            username_input.on('keydown.enter', handle_login)
            password_input.on('keydown.enter', handle_login)
            
            # 分隔线
            with ui.row().classes('w-full mt-6 items-center'):
                ui.separator().classes('flex-1')
                ui.label('或').classes('px-2 text-gray-500')
                ui.separator().classes('flex-1')
            
            # 其他选项
            with ui.row().classes('w-full justify-between mt-4'):
                if auth_config.allow_registration:
                    ui.link('注册新账号', auth_config.register_route).classes('text-blue-500 hover:underline')
                else:
                    ui.label('')  # 占位
                
                ui.link('忘记密码？', '#').classes('text-gray-500 hover:underline').on(
                    'click',
                    lambda: ui.notify('密码重置功能即将推出', type='info')
                )
            
            # 测试账号提示（开发环境）
            with ui.expansion('查看测试账号', icon='info').classes('w-full mt-4 text-sm'):
                ui.label('管理员：admin / admin123').classes('text-gray-600')
                ui.label('普通用户：user / user123').classes('text-gray-600')



```

- **auth\pages\logout_page.py**
```python
from nicegui import ui, app
from ..auth_manager import auth_manager
from ..decorators import public_route
from common.log_handler import (
    # 日志记录函数
    log_trace, log_debug, log_info, log_success, log_warning, log_error, log_critical,
    # 安全执行
    safe, db_safe,
    # 装饰器
    safe_protect, catch,
    # Logger 实例
    get_logger
)
logger = get_logger(__file__)

@public_route
@safe_protect(name="注销页面", error_msg="注销页面发生错误", return_on_error=None)
def logout_page_content():
    """注销页面内容 - 增强版"""
    print("🚪 开始执行注销流程")
    
    # 清除路由存储
    try:
        if 'current_route' in app.storage.user:
            del app.storage.user['current_route']
            print("🗑️ 已清除路由存储")
    except Exception as e:
        print(f"⚠️ 清除路由存储失败: {e}")
    
    # 执行注销
    auth_manager.logout()
    
    # 显示注销成功信息
    ui.notify('已退出登录!', type='info')
    
    # 延迟跳转到登录页面
    ui.timer(1.0, lambda: ui.navigate.to('/login'), once=True)
    
    # 显示注销确认页面
    with ui.column().classes('absolute-center items-center'):
        with ui.card().classes('p-8 text-center'):
            ui.icon('logout', size='4rem').classes('text-blue-500 mb-4')
            ui.label('正在注销...').classes('text-xl font-medium mb-2')
            ui.label('即将跳转到登录页面').classes('text-gray-600')
            ui.spinner(size='lg').classes('mt-4')
```

- **auth\pages\permission_management_page.py**
```python
"""
权限管理页面 - 卡片模式布局，与用户管理和角色管理页面保持一致
增加了用户-权限直接关联管理功能
"""
from nicegui import ui
from ..decorators import require_role
from ..auth_manager import auth_manager
from ..detached_helper import (
    detached_manager,
    get_permissions_safe,
    get_permission_safe,
    get_roles_safe,
    get_users_safe,
    update_permission_safe,
    delete_permission_safe,
    create_permission_safe,
    get_permission_direct_users_safe,  # 新增导入
    DetachedPermission,
    DetachedRole,
    DetachedUser
)
from ..models import Permission, Role, User
from ..database import get_db
from datetime import datetime

# 导入异常处理模块
# from common.exception_handler import log_info, log_error, safe, db_safe, safe_protect
from common.log_handler import (
    # 日志记录函数
    log_trace, log_debug, log_info, log_success, 
    log_warning, log_error, log_critical,
    # 安全执行
    safe, db_safe,
    # 装饰器
    safe_protect, catch,
    # Logger 实例
    get_logger
)
logger = get_logger(__file__)

@require_role('admin')
@safe_protect(name="权限管理页面", error_msg="权限管理页面加载失败，请稍后重试")
def permission_management_page_content():
    """权限管理页面内容 - 仅管理员可访问"""    
    # 页面标题
    with ui.column().classes('w-full mb-6'):
        ui.label('权限管理').classes('text-4xl font-bold text-green-800 dark:text-green-200 mb-2')
        ui.label('管理系统权限和资源访问控制，支持角色和用户关联管理').classes('text-lg text-gray-600 dark:text-gray-400')

    # 权限统计卡片
    def load_permission_statistics():
        """加载权限统计数据"""
        permission_stats = detached_manager.get_permission_statistics()
        role_stats = detached_manager.get_role_statistics()
        user_stats = detached_manager.get_user_statistics()
        
        return {
            **permission_stats,
            'total_roles': role_stats['total_roles'],
            'total_users': user_stats['total_users']
        }

    # 安全执行统计数据加载
    stats = safe(
        load_permission_statistics,
        return_value={'total_permissions': 0, 'system_permissions': 0, 'content_permissions': 0, 'total_roles': 0, 'total_users': 0},
        error_msg="权限统计数据加载失败"
    )

    # 统计卡片区域
    with ui.row().classes('w-full gap-6 mb-8'):
        with ui.card().classes('flex-1 p-6 bg-gradient-to-br from-green-500 to-green-600 text-white shadow-lg'):
            with ui.row().classes('items-center justify-between w-full'):
                with ui.column().classes('gap-1'):
                    ui.label('总权限数').classes('text-sm opacity-90 font-medium')
                    ui.label(str(stats['total_permissions'])).classes('text-3xl font-bold')
                ui.icon('security').classes('text-4xl opacity-80')

        with ui.card().classes('flex-1 p-6 bg-gradient-to-br from-blue-500 to-blue-600 text-white shadow-lg'):
            with ui.row().classes('items-center justify-between w-full'):
                with ui.column().classes('gap-1'):
                    ui.label('系统权限').classes('text-sm opacity-90 font-medium')
                    ui.label(str(stats['system_permissions'])).classes('text-3xl font-bold')
                ui.icon('admin_panel_settings').classes('text-4xl opacity-80')

        with ui.card().classes('flex-1 p-6 bg-gradient-to-br from-purple-500 to-purple-600 text-white shadow-lg'):
            with ui.row().classes('items-center justify-between w-full'):
                with ui.column().classes('gap-1'):
                    ui.label('内容权限').classes('text-sm opacity-90 font-medium')
                    ui.label(str(stats['content_permissions'])).classes('text-3xl font-bold')
                ui.icon('folder_shared').classes('text-4xl opacity-80')

        with ui.card().classes('flex-1 p-6 bg-gradient-to-br from-orange-500 to-orange-600 text-white shadow-lg'):
            with ui.row().classes('items-center justify-between w-full'):
                with ui.column().classes('gap-1'):
                    ui.label('关联角色').classes('text-sm opacity-90 font-medium')
                    ui.label(str(stats['total_roles'])).classes('text-3xl font-bold')
                ui.icon('group').classes('text-4xl opacity-80')

    # 权限列表容器
    with ui.column().classes('w-full'):
        with ui.row().classes('w-full gap-2 mt-4'):
            ui.button('添加权限', icon='add', on_click=lambda: add_permission_dialog()).classes('bg-blue-500 text-white')
            # 测试异常按钮
            ui.button('测试异常', icon='bug_report', 
                     on_click=lambda: safe(lambda: ui.notify("test")),
                     color='red').classes('ml-4')
        # 处理函数
        def handle_search():
            """处理搜索"""
            log_info(f"权限搜索: {search_input.value}")
            load_permissions()

        def reset_search():
            """重置搜索"""
            search_input.value = ''
            load_permissions()
            
        with ui.row().classes('w-full gap-2 mb-4 items-end'):
            search_input = ui.input('搜索权限', placeholder='权限名称、标识或描述').classes('flex-1').props('outlined clearable')
            search_input.props('prepend-icon=search')
            
            ui.button('搜索', icon='search', on_click=lambda: handle_search()).classes('bg-blue-600 text-white px-4 py-2')
            ui.button('重置', icon='refresh', on_click=lambda: reset_search()).classes('bg-gray-500 text-white px-4 py-2')

        search_input.on('keyup.enter', handle_search)
    
        # 权限列表容器
        permissions_container = ui.column().classes('w-full gap-4')

    def load_permissions():
        """更新权限显示"""
        log_info("开始更新权限显示")
        
        search_term = search_input.value.strip() if search_input.value else None
        all_permissions = safe(
            lambda: get_permissions_safe(search_term=search_term),
            return_value=[],
            error_msg="权限列表加载失败"
        )
        
        permissions_container.clear()
        
        with permissions_container:
            if not all_permissions:
                search_term = search_input.value.strip() if search_input.value else None
                with ui.card().classes('w-full p-8 text-center bg-gray-50 dark:bg-gray-700'):
                    if search_term:
                        ui.icon('search_off').classes('text-6xl text-gray-400 mb-4')
                        ui.label('未找到匹配的权限').classes('text-lg text-gray-600 dark:text-gray-400 mb-2')
                        ui.label(f'搜索关键词: "{search_term}"').classes('text-sm text-gray-500 dark:text-gray-500')
                    else:
                        ui.icon('security').classes('text-6xl text-gray-400 mb-4')
                        ui.label('暂无权限数据').classes('text-lg text-gray-600 dark:text-gray-400')
                return

            MAX_DISPLAY_USERS = 2
            permissions_to_display = all_permissions[:MAX_DISPLAY_USERS]
            has_more_permissions = len(all_permissions) > MAX_DISPLAY_USERS

            with ui.card().classes('w-full p-4 mb-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-700'):
                with ui.row().classes('items-center gap-3'):
                    ui.icon('info').classes('text-blue-600 dark:text-blue-400 text-2xl')
                    with ui.column().classes('flex-1'):
                        ui.label('使用提示').classes('text-lg font-semibold text-blue-800 dark:text-blue-200')
                        if not search_term:
                            ui.label('权限列表最多显示2个权限。要查看或操作特定权限，请使用上方搜索框输入权限名称或标识搜索').classes('text-blue-700 dark:text-blue-300 text-sm leading-relaxed')
                        else:
                            if len(all_permissions) > MAX_DISPLAY_USERS:
                                ui.label(f'搜索到 {len(all_permissions)} 个权限，当前显示前 {MAX_DISPLAY_USERS} 个。请使用更精确的关键词缩小搜索范围。').classes('text-blue-700 dark:text-blue-300 text-sm leading-relaxed')
                            else:
                                ui.label(f'搜索到 {len(all_permissions)} 个匹配权限。').classes('text-blue-700 dark:text-blue-300 text-sm leading-relaxed')
            
            with ui.row().classes('w-full items-center justify-between mb-4'):
                if search_term:
                    ui.label(f'搜索结果: {len(all_permissions)} 个权限').classes('text-lg font-medium text-gray-700 dark:text-gray-300')
                else:
                    ui.label(f'权限总数: {len(all_permissions)} 个').classes('text-lg font-medium text-gray-700 dark:text-gray-300')
                if has_more_permissions:
                    ui.chip(f'显示 {len(permissions_to_display)}/{len(all_permissions)}', icon='visibility').classes('bg-orange-100 text-orange-800 dark:bg-orange-800 dark:text-orange-200')


            # 权限卡片列表
            for i in range(0, len(permissions_to_display), 2):
                with ui.row().classes('w-full gap-3'):
                    # 第一个权限卡片
                    with ui.column().classes('flex-1'):
                        create_permission_card(permissions_to_display[i])
                    # 第二个权限卡片（如果存在）
                    if i + 1 < len(permissions_to_display):
                        with ui.column().classes('flex-1'):
                            create_permission_card(permissions_to_display[i + 1])
                    else:
                        # 如果是奇数个权限，添加占位符保持布局
                        ui.column().classes('flex-1')

            # 如果有更多用户未显示，显示提示
            if has_more_permissions:
                with ui.card().classes('w-full p-4 mt-4 bg-orange-50 dark:bg-orange-900/20 border border-orange-200 dark:border-orange-700'):
                    with ui.row().classes('items-center gap-3'):
                        ui.icon('visibility_off').classes('text-orange-600 dark:text-orange-400 text-2xl')
                        with ui.column().classes('flex-1'):
                            ui.label(f'还有 {len(all_permissions) - MAX_DISPLAY_USERS} 个权限未显示').classes('text-lg font-semibold text-orange-800 dark:text-orange-200')
                            ui.label('请使用搜索功能查找特定权限，或者使用更精确的关键词缩小范围。').classes('text-orange-700 dark:text-orange-300 text-sm')


    def create_permission_card(permission_data: DetachedPermission):
        """创建权限卡片"""
        # 确定角色颜色主题
        if permission_data.name == 'system.manage':
            card_theme = 'border-l-4 border-red-500 bg-red-50 dark:bg-red-900/10'
            badge_theme = 'bg-red-100 text-red-800 dark:bg-red-800 dark:text-red-200'
            icon_theme = 'text-red-600 dark:text-red-400'
        elif permission_data.name == 'user':
            card_theme = 'border-l-4 border-green-500 bg-green-50 dark:bg-green-900/10'
            badge_theme = 'bg-green-100 text-green-800 dark:bg-green-800 dark:text-green-200'
            icon_theme = 'text-green-600 dark:text-green-400'
        else:
            card_theme = 'border-l-4 border-blue-500 bg-blue-50 dark:bg-blue-900/10'
            badge_theme = 'bg-blue-100 text-blue-800 dark:bg-blue-800 dark:text-blue-200'
            icon_theme = 'text-blue-600 dark:text-blue-400'
            
        with ui.card().classes(f'w-full {card_theme} shadow-md hover:shadow-lg transition-shadow duration-300'):
            with ui.row().classes('w-full p-4 gap-4'):
                # 左侧：权限基本信息（约占 40%）
                with ui.column().classes('flex-none w-72 gap-2'):
                    # 权限标题和分类
                    with ui.row().classes('items-center gap-3 mb-2'):
                        ui.label(permission_data.display_name or permission_data.name).classes('text-xl font-bold text-gray-800 dark:text-gray-200')
                        
                        # 分类标签
                        category_color = {
                            '系统': 'bg-red-100 text-red-800 dark:bg-red-800 dark:text-red-200',
                            '内容': 'bg-purple-100 text-purple-800 dark:bg-purple-800 dark:text-purple-200',
                            '分析': 'bg-blue-100 text-blue-800 dark:bg-blue-800 dark:text-blue-200',
                            '业务': 'bg-green-100 text-green-800 dark:bg-green-800 dark:text-green-200',
                            '个人': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-800 dark:text-yellow-200'
                        }.get(permission_data.category, 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200')
                        
                        ui.chip(permission_data.category or '其他', icon='label').classes(f'{category_color} text-xs py-1 px-2')

                    # 权限标识符
                    ui.label(f'权限标识: {permission_data.name}').classes('text-sm font-mono bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded text-gray-700 dark:text-gray-300')

                    # 使用状态
                    with ui.row().classes('items-center gap-2 mt-2'):
                        if permission_data.roles_count > 0:
                            if permission_data.roles_count > 1:
                                ui.chip(f'{permission_data.roles_count}个角色', icon='group').classes('bg-green-100 text-green-800 dark:bg-green-800 dark:text-green-200 text-xs py-1 px-2')
                            else:
                                ui.chip('1个角色', icon='person').classes('bg-orange-100 text-orange-800 dark:bg-orange-800 dark:text-orange-200 text-xs py-1 px-2')
                        else:
                            ui.chip('未使用', icon='warning').classes('bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200 text-xs py-1 px-2').tooltip('此权限未被任何角色使用')

                    # 权限描述
                    if permission_data.description:
                        ui.label('描述:').classes('text-xs font-medium text-gray-600 dark:text-gray-400')
                        ui.label(permission_data.description).classes('text-sm text-gray-700 dark:text-gray-300')
                    else:
                        ui.label('暂无描述').classes('text-sm text-gray-500 dark:text-gray-400 italic')

                    # 统计信息
                    with ui.row().classes('gap-2 mt-2'):
                        with ui.card().classes('flex-1 p-2 bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600'):
                            ui.label('权限ID').classes('text-xs text-gray-500 dark:text-gray-400')
                            ui.label(str(permission_data.id)).classes('text-lg font-bold text-blue-600 dark:text-blue-400')
                        
                        with ui.card().classes('flex-1 p-2 bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600'):
                            ui.label('关联角色').classes('text-xs text-gray-500 dark:text-gray-400')
                            ui.label(str(permission_data.roles_count)).classes('text-lg font-bold text-green-600 dark:text-green-400')

                # 右侧：关联管理区域（约占 60%）
                with ui.column().classes('flex-1 gap-2'):
                    # 关联角色区域 - 修改后的版本
                    with ui.column().classes('gap-2'):
                        with ui.row().classes('items-center justify-between w-full'):
                            ui.label(f'关联角色 ({permission_data.roles_count})').classes('text-lg font-bold text-gray-800 dark:text-gray-200')

                        # 角色操作按钮区域 - 只保留添加和删除按钮
                        # with ui.card().classes(f'w-full {card_theme} shadow-md hover:shadow-lg transition-shadow duration-300'):
                        with ui.row().classes('gap-4 w-full items-center justify-start'):
                            ui.button('添加角色', icon='add', 
                                    on_click=lambda: add_roles_to_permission(permission_data)).classes('bg-blue-600 text-white px-4 py-2')
                            ui.button('删除角色', icon='remove', 
                                    on_click=lambda: remove_roles_from_permission(permission_data)).classes('bg-red-600 text-white px-4 py-2')

                    # 关联用户区域 - 修改后的版本
                    with ui.column().classes('gap-2'):
                        # 获取权限直接关联的用户
                        permission_users = safe(
                            lambda: get_permission_direct_users_safe(permission_data.id),
                            return_value=[],
                            error_msg="获取权限关联用户失败"
                        )
                        
                        with ui.row().classes('items-center justify-between w-full'):
                            ui.label(f'关联用户 ({len(permission_users)})').classes('text-lg font-bold text-gray-800 dark:text-gray-200')

                        # 用户操作按钮区域 - 只保留添加和删除按钮
                        # with ui.card().classes(f'w-full {card_theme} shadow-md hover:shadow-lg transition-shadow duration-300'):
                        with ui.row().classes('gap-4 w-full items-center justify-start'):
                            ui.button('添加用户', icon='person_add', 
                                        on_click=lambda: add_users_to_permission(permission_data)).classes('bg-indigo-600 text-white px-4 py-2')
                            ui.button('删除用户', icon='person_remove', 
                                        on_click=lambda: remove_users_from_permission(permission_data)).classes('bg-orange-600 text-white px-4 py-2')
                            # ui.button('批量关联', icon='upload_file',
                            #             on_click=lambda: batch_associate_users_to_permission_dialog(permission_data)).classes('bg-purple-600 hover:bg-purple-700 text-white px-4 py-2')


                    # 操作按钮区域
                    with ui.row().classes('items-center justify-between w-full'):
                            ui.label(f'权限操作').classes('text-lg font-bold text-gray-800 dark:text-gray-200')
                    with ui.row().classes('gap-4 w-full items-center justify-start'):
                        ui.button('编辑权限', icon='edit', 
                                 on_click=lambda: edit_permission_dialog(permission_data)).classes('bg-yellow-600 hover:bg-yellow-700 text-white px-4 py-2')
                        ui.button('删除权限', icon='delete', 
                                 on_click=lambda: delete_permission_confirm(permission_data)).classes('bg-red-600 hover:bg-red-700 text-white px-4 py-2')

    # 权限CRUD操作
    @safe_protect(name="批量关联用户到权限")
    def batch_associate_users_to_permission_dialog(permission_data: DetachedPermission):
        """批量关联用户到权限对话框 - 通过上传文件"""
        log_info(f"打开批量关联用户到权限对话框: {permission_data.name}")
        
        with ui.dialog() as dialog, ui.card().classes('w-[700px] max-h-[80vh]'):
            dialog.open()
            
            # 对话框标题
            with ui.row().classes('w-full items-center justify-between p-4 bg-gradient-to-r from-purple-500 to-purple-600 text-white rounded-t-lg -m-6 mb-6'):
                ui.label(f'批量关联用户到权限 "{permission_data.display_name or permission_data.name}"').classes('text-xl font-bold')
                ui.button(icon='close', on_click=dialog.close).props('flat round color=white').classes('ml-auto')

            # 说明信息
            with ui.card().classes('w-full mb-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-700'):
                ui.label('操作说明').classes('font-bold mb-2 text-blue-800 dark:text-blue-200')
                ui.label('1. 上传包含用户信息的文本文件（支持 .txt 和 .csv 格式）').classes('text-sm text-blue-700 dark:text-blue-300')
                ui.label('2. 文件每行包含一个用户名或注册邮箱').classes('text-sm text-blue-700 dark:text-blue-300')
                ui.label('3. 系统将自动识别用户并建立权限关联').classes('text-sm text-blue-700 dark:text-blue-300')
                ui.label('4. 如果用户已关联该权限，将会跳过').classes('text-sm text-blue-700 dark:text-blue-300')
                ui.label('5. 无法识别的用户名/邮箱将在结果中显示').classes('text-sm text-blue-700 dark:text-blue-300')

            # 文件上传示例
            with ui.expansion('查看文件格式示例', icon='help').classes('w-full mb-4'):
                with ui.column().classes('gap-2'):
                    ui.label('TXT 文件示例:').classes('font-bold text-gray-700 dark:text-gray-300')
                    ui.code('''admin
    user1
    test@example.com
    manager
    developer@company.com''').classes('text-sm bg-gray-100 dark:bg-gray-800 p-2 rounded')
                    
                    ui.label('CSV 文件示例:').classes('font-bold text-gray-700 dark:text-gray-300 mt-4')
                    ui.code('''username
    admin
    user1
    test@example.com
    manager''').classes('text-sm bg-gray-100 dark:bg-gray-800 p-2 rounded')

            # 文件上传区域
            uploaded_file_content = None
            upload_status = ui.label('请选择用户列表文件').classes('text-gray-600 dark:text-gray-400')
            
            def handle_file_upload(e):
                """处理文件上传"""
                nonlocal uploaded_file_content
                
                if not e.content:
                    upload_status.text = '文件上传失败：文件为空'
                    upload_status.classes('text-red-600')
                    return
                
                # 检查文件类型
                filename = e.name.lower()
                if not (filename.endswith('.txt') or filename.endswith('.csv')):
                    upload_status.text = '文件格式不支持：仅支持 .txt 和 .csv 文件'
                    upload_status.classes('text-red-600')
                    return
                
                try:
                    # 解码文件内容
                    uploaded_file_content = e.content.read().decode('utf-8')
                    upload_status.text = f'文件上传成功: {e.name} ({len(uploaded_file_content.splitlines())} 行)'
                    upload_status.classes('text-green-600')
                    log_info(f"文件上传成功: {e.name}, 内容长度: {len(uploaded_file_content)}")
                    
                except Exception as ex:
                    log_error(f"文件上传处理失败: {e.name}", exception=ex)
                    upload_status.text = f'文件处理失败: {str(ex)}'
                    upload_status.classes('text-red-600')
                    uploaded_file_content = None

            ui.upload(
                label='选择用户列表文件',
                on_upload=handle_file_upload,
                max_file_size=1024*1024  # 1MB 限制
            ).classes('w-full').props('accept=".txt,.csv"')

            def process_batch_association():
                """处理批量关联"""
                if not uploaded_file_content:
                    ui.notify('请先上传用户列表文件', type='warning')
                    return

                try:
                    # 解析用户列表
                    users_list = []
                    lines = uploaded_file_content.strip().split('\n')
                    
                    for i, line in enumerate(lines):
                        line = line.strip()
                        # 跳过空行和CSV标题行
                        if not line or (i == 0 and line.lower() in ['username', 'user', 'email', '用户名', '邮箱']):
                            continue
                        # 移除可能的逗号分隔符（支持CSV格式）
                        if ',' in line:
                            line = line.split(',')[0].strip()
                        if line:
                            users_list.append(line)

                    if not users_list:
                        ui.notify('文件中没有发现有效的用户信息', type='warning')
                        return

                    log_info(f"开始批量关联用户到权限 {permission_data.name}: {len(users_list)} 个用户")

                    # 执行批量关联
                    success_count = 0
                    skip_count = 0
                    error_users = []

                    with db_safe(f"批量关联用户到权限 {permission_data.name}") as db:
                        permission = db.query(Permission).filter(Permission.id == permission_data.id).first()
                        if not permission:
                            ui.notify('权限不存在', type='error')
                            return

                        for user_identifier in users_list:
                            try:
                                # 尝试按用户名查找
                                user = db.query(User).filter(User.username == user_identifier).first()
                                
                                # 如果按用户名找不到，尝试按邮箱查找
                                if not user and '@' in user_identifier:
                                    user = db.query(User).filter(User.email == user_identifier).first()
                                
                                if not user:
                                    error_users.append(user_identifier)
                                    continue
                                
                                # 检查是否已经有直接权限关联
                                if permission in user.permissions:
                                    skip_count += 1
                                    log_info(f"用户 {user.username} 已拥有权限 {permission_data.name}，跳过")
                                    continue
                                
                                # 添加权限关联
                                user.permissions.append(permission)
                                success_count += 1
                                log_info(f"成功为用户 {user.username} 添加权限 {permission_data.name}")
                                
                            except Exception as e:
                                log_error(f"处理用户 {user_identifier} 时出错", exception=e)
                                error_users.append(user_identifier)

                    # 显示结果对话框
                    result_message = f'''批量关联完成！
                    成功关联: {success_count} 个用户
                    已有权限跳过: {skip_count} 个用户
                    无法识别: {len(error_users)} 个用户'''

                    with ui.dialog() as result_dialog, ui.card().classes('w-[500px]'):
                        result_dialog.open()
                        
                        # 结果标题
                        with ui.row().classes('w-full items-center justify-between p-4 bg-gradient-to-r from-green-500 to-blue-500 text-white rounded-t-lg -m-6 mb-6'):
                            ui.label('批量关联结果').classes('text-xl font-bold')
                            ui.button(icon='close', on_click=result_dialog.close).props('flat round color=white').classes('ml-auto')

                        # 统计卡片
                        with ui.row().classes('w-full gap-2 mb-4'):
                            with ui.card().classes('flex-1 p-3 bg-green-50 dark:bg-green-900/20 text-center'):
                                ui.label('成功关联').classes('text-sm text-green-700 dark:text-green-300')
                                ui.label(str(success_count)).classes('text-2xl font-bold text-green-700 dark:text-green-300')

                            with ui.card().classes('flex-1 p-3 bg-yellow-50 dark:bg-yellow-900/20 text-center'):
                                ui.label('跳过').classes('text-sm text-yellow-700 dark:text-yellow-300')
                                ui.label(str(skip_count)).classes('text-2xl font-bold text-yellow-700 dark:text-yellow-300')

                            with ui.card().classes('flex-1 p-3 bg-red-50 dark:bg-red-900/20 text-center'):
                                ui.label('错误').classes('text-sm text-red-700 dark:text-red-300')
                                ui.label(str(len(error_users))).classes('text-2xl font-bold text-red-700 dark:text-red-300')

                        # 详细信息
                        ui.label(result_message).classes('text-sm text-gray-700 dark:text-gray-300 whitespace-pre-line mb-4')
                        
                        # 显示无法识别的用户
                        if error_users:
                            with ui.expansion('查看无法识别的用户', icon='error').classes('w-full mb-4'):
                                with ui.column().classes('gap-1 max-h-40 overflow-auto'):
                                    for user in error_users:
                                        ui.label(f'• {user}').classes('text-sm text-red-600 dark:text-red-400')

                        with ui.row().classes('w-full justify-end gap-2'):
                            ui.button('确定', on_click=result_dialog.close).classes('bg-purple-600 hover:bg-purple-700 text-white')

                    # 显示成功通知
                    if success_count > 0:
                        ui.notify(f'成功关联 {success_count} 个用户到权限 {permission_data.name}', type='positive')
                        dialog.close()
                        safe(load_permissions)  # 重新加载权限列表
                    else:
                        ui.notify('没有新用户被关联', type='info')

                    log_info(f"批量关联完成: 权限={permission_data.name}, 成功={success_count}, 跳过={skip_count}, 错误={len(error_users)}")

                except Exception as e:
                    log_error(f"批量关联用户失败: {permission_data.name}", exception=e)
                    ui.notify('批量关联失败，请稍后重试', type='negative')

            # 操作按钮
            with ui.row().classes('w-full justify-end gap-3 mt-6'):
                ui.button('取消', on_click=dialog.close).classes('px-6 py-2 bg-gray-500 hover:bg-gray-600 text-white')
                ui.button('开始关联', icon='link', on_click=lambda: safe(process_batch_association)).classes('px-6 py-2 bg-purple-600 hover:bg-purple-700 text-white')

    def add_permission_dialog():
        """添加权限对话框"""
        with ui.dialog() as dialog, ui.card().classes('w-96 p-6'):
            ui.label('添加新权限').classes('text-xl font-bold text-green-600 mb-4')

            name_input = ui.input('权限标识', placeholder='例如: content.create').classes('w-full mb-3')
            display_name_input = ui.input('显示名称', placeholder='例如: 创建内容').classes('w-full mb-3')
            category_select = ui.select(
                options=['系统', '内容', '分析', '业务', '个人', '其他'],
                label='权限分类',
                value='其他'
            ).classes('w-full mb-3')
            description_input = ui.textarea('权限描述', placeholder='详细描述该权限的作用').classes('w-full mb-4')

            with ui.row().classes('w-full gap-2 mt-6 justify-end'):
                ui.button('取消', on_click=dialog.close).classes('bg-gray-500 text-white px-4 py-2')
                ui.button('创建权限', on_click=lambda: create_new_permission()).classes('bg-green-600 text-white px-4 py-2')

            def create_new_permission():
                """创建新权限"""
                if not name_input.value:
                    ui.notify('请输入权限标识', type='warning')
                    return

                log_info(f"开始创建权限: {name_input.value}")
                
                permission_id = safe(
                    lambda: create_permission_safe(
                        name=name_input.value,
                        display_name=display_name_input.value or None,
                        category=category_select.value,
                        description=description_input.value or None
                    ),
                    return_value=None,
                    error_msg="权限创建失败"
                )

                if permission_id:
                    ui.notify('权限创建成功', type='positive')
                    dialog.close()
                    load_permissions()
                else:
                    ui.notify('权限创建失败，可能权限标识已存在', type='error')

        dialog.open()

    def edit_permission_dialog(permission_data: DetachedPermission):
        """编辑权限对话框"""
        with ui.dialog() as dialog, ui.card().classes('w-96 p-6'):
            ui.label('编辑权限').classes('text-xl font-bold text-yellow-600 mb-4')

            name_input = ui.input('权限标识', value=permission_data.name).classes('w-full mb-3')
            name_input.enabled = False  # 权限标识不可修改
            
            display_name_input = ui.input('显示名称', value=permission_data.display_name or '').classes('w-full mb-3')
            category_select = ui.select(
                options=['系统', '内容', '分析', '业务', '个人', '其他'],
                label='权限分类',
                value=permission_data.category or '其他'
            ).classes('w-full mb-3')
            description_input = ui.textarea('权限描述', value=permission_data.description or '').classes('w-full mb-4')

            with ui.row().classes('w-full gap-2 mt-6 justify-end'):
                ui.button('取消', on_click=dialog.close).classes('bg-gray-500 text-white px-4 py-2')
                ui.button('保存修改', on_click=lambda: save_permission_changes()).classes('bg-yellow-600 text-white px-4 py-2')

            def save_permission_changes():
                """保存权限修改"""
                log_info(f"开始更新权限: {permission_data.name}")
                
                success = safe(
                    lambda: update_permission_safe(
                        permission_data.id,
                        display_name=display_name_input.value or None,
                        category=category_select.value,
                        description=description_input.value or None
                    ),
                    return_value=False,
                    error_msg="权限更新失败"
                )

                if success:
                    ui.notify('权限更新成功', type='positive')
                    dialog.close()
                    load_permissions()
                else:
                    ui.notify('权限更新失败', type='error')

        dialog.open()

    def delete_permission_confirm(permission_data: DetachedPermission):
        """确认删除权限"""
        with ui.dialog() as dialog, ui.card().classes('w-96 p-6'):
            ui.label('确认删除权限').classes('text-xl font-bold text-red-600 mb-4')
            ui.label(f'权限: {permission_data.display_name or permission_data.name}').classes('text-gray-700 mb-2')
            ui.label(f'标识: {permission_data.name}').classes('text-gray-700 mb-2')
            
            if permission_data.roles_count > 0:
                ui.label(f'⚠️ 该权限已关联 {permission_data.roles_count} 个角色，删除后将移除所有关联').classes('text-orange-600 font-medium mt-4')
            
            ui.label('此操作不可撤销，确定要删除吗？').classes('text-red-600 font-medium mt-4')

            with ui.row().classes('w-full gap-2 mt-6 justify-end'):
                ui.button('取消', on_click=dialog.close).classes('bg-gray-500 text-white px-4 py-2')
                ui.button('确认删除', on_click=lambda: execute_delete_permission()).classes('bg-red-600 text-white px-4 py-2')

            def execute_delete_permission():
                """执行删除权限"""
                log_info(f"开始删除权限: {permission_data.name}")
                
                success = safe(
                    lambda: delete_permission_safe(permission_data.id),
                    return_value=False,
                    error_msg="权限删除失败"
                )

                if success:
                    ui.notify('权限删除成功', type='positive')
                    dialog.close()
                    load_permissions()
                else:
                    ui.notify('权限删除失败，可能存在关联关系', type='error')

        dialog.open()

    # 角色关联管理 - 添加角色对话框
    def add_roles_to_permission(permission_data: DetachedPermission):
        """为权限添加角色关联"""
        with ui.dialog() as dialog, ui.card().classes('w-lg p-6'):
            ui.label('为权限添加角色').classes('text-xl font-bold text-blue-600 mb-4')
            ui.label(f'权限: {permission_data.display_name or permission_data.name}').classes('text-gray-700 mb-4')

            # 角色选择区域
            selected_roles = set()
            role_search_input = ui.input('搜索角色', placeholder='输入角色名称搜索').classes('w-full mb-4')
            
            with ui.column().classes('w-full max-h-60 overflow-y-auto border border-gray-200 dark:border-gray-600 rounded p-3') as role_list_container:
                pass  # 角色列表将在这里动态生成

            def update_role_list():
                """更新角色列表"""
                search_term = role_search_input.value.strip() if role_search_input.value else None
                
                all_roles = safe(
                    lambda: get_roles_safe(),
                    return_value=[],
                    error_msg="获取角色列表失败"
                )
                
                # 过滤掉已经关联的角色
                available_roles = [role for role in all_roles if role.name not in permission_data.roles]
                
                # 搜索过滤
                if search_term:
                    available_roles = [role for role in available_roles 
                                     if search_term.lower() in role.name.lower() or 
                                        (role.display_name and search_term.lower() in role.display_name.lower())]
                
                role_list_container.clear()
                with role_list_container:
                    if not available_roles:
                        ui.label('没有可添加的角色').classes('text-gray-500 text-center py-4')
                        return
                    
                    for role in available_roles:
                        def create_role_checkbox(r):
                            def on_role_check(checked):
                                if checked:
                                    selected_roles.add(r.id)
                                else:
                                    selected_roles.discard(r.id)
                            
                            with ui.row().classes('items-center gap-3 p-2 hover:bg-gray-50 dark:hover:bg-gray-700 rounded'):
                                ui.checkbox(on_change=on_role_check).classes('flex-none')
                                ui.icon('badge').classes('text-blue-500')
                                with ui.column().classes('gap-1'):
                                    ui.label(r.display_name or r.name).classes('font-medium')
                                    ui.label(f'角色标识: {r.name}').classes('text-sm text-gray-500')
                        
                        create_role_checkbox(role)

            role_search_input.on('input', lambda: update_role_list())

            with ui.row().classes('w-full gap-2 mt-6 justify-end'):
                ui.button('取消', on_click=dialog.close).classes('bg-gray-500 text-white px-4 py-2')
                ui.button('确认添加', on_click=lambda: confirm_update_roles()).classes('bg-blue-600 text-white px-4 py-2')

            def confirm_update_roles():
                """确认更新角色关联"""
                if not selected_roles:
                    ui.notify('请至少选择一个角色', type='warning')
                    return

                log_info(f"开始为权限 {permission_data.name} 添加角色关联: {list(selected_roles)}")
                
                success = safe(
                    lambda: add_permission_to_roles(permission_data.id, list(selected_roles)),
                    return_value=False,
                    error_msg="权限角色关联失败"
                )

                if success:
                    ui.notify('权限角色关联成功', type='positive')
                    dialog.close()
                    load_permissions()
                else:
                    ui.notify('权限角色关联失败', type='error')

            # 初始化角色列表
            update_role_list()

        dialog.open()

    # 角色关联管理 - 删除角色对话框（新增）
    def remove_roles_from_permission(permission_data: DetachedPermission):
        """从权限中删除角色关联"""
        with ui.dialog() as dialog, ui.card().classes('w-lg p-6'):
            ui.label('删除权限的角色关联').classes('text-xl font-bold text-red-600 mb-4')
            ui.label(f'权限: {permission_data.display_name or permission_data.name}').classes('text-gray-700 mb-4')

            if not permission_data.roles:
                ui.label('该权限暂无关联角色').classes('text-gray-500 text-center py-4')
                with ui.row().classes('w-full gap-2 mt-6 justify-end'):
                    ui.button('关闭', on_click=dialog.close).classes('bg-gray-500 text-white px-4 py-2')
                dialog.open()
                return

            # 角色选择区域
            selected_roles_to_remove = set()
            role_search_input = ui.input('搜索角色', placeholder='输入角色名称搜索').classes('w-full mb-4')
            
            with ui.column().classes('w-full max-h-60 overflow-y-auto border border-gray-200 dark:border-gray-600 rounded p-3') as role_list_container:
                pass  # 角色列表将在这里动态生成

            def update_role_removal_list():
                """更新可删除的角色列表"""
                search_term = role_search_input.value.strip() if role_search_input.value else None
                
                # 获取已关联的角色
                associated_roles = permission_data.roles
                
                # 搜索过滤
                if search_term:
                    filtered_roles = [role_name for role_name in associated_roles 
                                     if search_term.lower() in role_name.lower()]
                else:
                    filtered_roles = associated_roles
                
                role_list_container.clear()
                with role_list_container:
                    if not filtered_roles:
                        ui.label('没有匹配的角色').classes('text-gray-500 text-center py-4')
                        return
                    
                    for role_name in filtered_roles:
                        def create_role_removal_checkbox(rn):
                            def on_role_check(checked):
                                if checked:
                                    selected_roles_to_remove.add(rn)
                                else:
                                    selected_roles_to_remove.discard(rn)
                            
                            with ui.row().classes('items-center gap-3 p-2 hover:bg-gray-50 dark:hover:bg-gray-700 rounded'):
                                ui.checkbox(on_change=on_role_check).classes('flex-none')
                                ui.icon('badge').classes('text-red-500')
                                ui.label(rn).classes('font-medium')
                        
                        create_role_removal_checkbox(role_name)

            role_search_input.on('input', lambda: update_role_removal_list())

            with ui.row().classes('w-full gap-2 mt-6 justify-end'):
                ui.button('取消', on_click=dialog.close).classes('bg-gray-500 text-white px-4 py-2')
                ui.button('确认删除', on_click=lambda: confirm_remove_roles()).classes('bg-red-600 text-white px-4 py-2')

            def confirm_remove_roles():
                """确认删除角色关联"""
                if not selected_roles_to_remove:
                    ui.notify('请至少选择一个角色', type='warning')
                    return

                log_info(f"开始从权限 {permission_data.name} 删除角色关联: {list(selected_roles_to_remove)}")
                
                success_count = 0
                for role_name in selected_roles_to_remove:
                    success = safe(
                        lambda rn=role_name: remove_permission_from_role(permission_data.id, rn),
                        return_value=False,
                        error_msg=f"删除角色 {role_name} 关联失败"
                    )
                    if success:
                        success_count += 1

                if success_count > 0:
                    ui.notify(f'成功删除 {success_count} 个角色关联', type='positive')
                    dialog.close()
                    load_permissions()
                else:
                    ui.notify('删除角色关联失败', type='error')

            # 初始化角色列表
            update_role_removal_list()

        dialog.open()

    # 用户关联管理 - 添加用户对话框
    def add_users_to_permission(permission_data: DetachedPermission):
        """为权限添加用户关联"""
        with ui.dialog() as dialog, ui.card().classes('w-lg p-6'):
            ui.label('为权限添加用户').classes('text-xl font-bold text-indigo-600 mb-4')
            ui.label(f'权限: {permission_data.display_name or permission_data.name}').classes('text-gray-700 mb-4')

            # 用户选择区域
            selected_users = set()
            user_search_input = ui.input('搜索用户', placeholder='输入用户名或邮箱搜索').classes('w-full mb-4')
            
            with ui.column().classes('w-full max-h-60 overflow-y-auto border border-gray-200 dark:border-gray-600 rounded p-3') as user_list_container:
                pass  # 用户列表将在这里动态生成

            def update_user_list():
                """更新用户列表"""
                search_term = user_search_input.value.strip() if user_search_input.value else None
                
                all_users = safe(
                    lambda: get_users_safe(search_term=search_term, limit=100),
                    return_value=[],
                    error_msg="获取用户列表失败"
                )
                
                # 获取已关联的用户ID
                permission_users = safe(
                    lambda: get_permission_direct_users_safe(permission_data.id),
                    return_value=[],
                    error_msg="获取权限关联用户失败"
                )
                existing_user_ids = {user['id'] for user in permission_users}
                
                # 过滤掉已经关联的用户
                available_users = [user for user in all_users if user.id not in existing_user_ids]
                
                user_list_container.clear()
                with user_list_container:
                    if not available_users:
                        ui.label('没有可添加的用户').classes('text-gray-500 text-center py-4')
                        return
                    
                    for user in available_users:
                        def create_user_checkbox(u):
                            def on_user_check(checked):
                                if checked:
                                    selected_users.add(u.id)
                                else:
                                    selected_users.discard(u.id)
                            
                            with ui.row().classes('items-center gap-3 p-2 hover:bg-gray-50 dark:hover:bg-gray-700 rounded'):
                                ui.checkbox(on_change=on_user_check).classes('flex-none')
                                ui.icon('person').classes('text-indigo-500')
                                with ui.column().classes('gap-1'):
                                    ui.label(u.full_name or u.username).classes('font-medium')
                                    ui.label(f'用户名: {u.username} | 邮箱: {u.email}').classes('text-sm text-gray-500')
                        
                        create_user_checkbox(user)

            user_search_input.on('input', lambda: update_user_list())

            with ui.row().classes('w-full gap-2 mt-6 justify-end'):
                ui.button('取消', on_click=dialog.close).classes('bg-gray-500 text-white px-4 py-2')
                ui.button('确认添加', on_click=lambda: confirm_update_users()).classes('bg-indigo-600 text-white px-4 py-2')

            def confirm_update_users():
                """确认更新用户关联"""
                if not selected_users:
                    ui.notify('请至少选择一个用户', type='warning')
                    return

                log_info(f"开始为权限 {permission_data.name} 添加用户关联: {list(selected_users)}")
                
                success = safe(
                    lambda: add_permission_to_users(permission_data.id, list(selected_users)),
                    return_value=False,
                    error_msg="权限用户关联失败"
                )

                if success:
                    ui.notify('权限用户关联成功', type='positive')
                    dialog.close()
                    load_permissions()
                else:
                    ui.notify('权限用户关联失败', type='error')

            # 初始化用户列表
            update_user_list()

        dialog.open()

    # 用户关联管理 - 删除用户对话框（新增）
    def remove_users_from_permission(permission_data: DetachedPermission):
        """从权限中删除用户关联"""
        with ui.dialog() as dialog, ui.card().classes('w-lg p-6'):
            ui.label('删除权限的用户关联').classes('text-xl font-bold text-orange-600 mb-4')
            ui.label(f'权限: {permission_data.display_name or permission_data.name}').classes('text-gray-700 mb-4')

            # 获取已关联的用户
            permission_users = safe(
                lambda: get_permission_direct_users_safe(permission_data.id),
                return_value=[],
                error_msg="获取权限关联用户失败"
            )

            if not permission_users:
                ui.label('该权限暂无关联用户').classes('text-gray-500 text-center py-4')
                with ui.row().classes('w-full gap-2 mt-6 justify-end'):
                    ui.button('关闭', on_click=dialog.close).classes('bg-gray-500 text-white px-4 py-2')
                dialog.open()
                return

            # 用户选择区域
            selected_users_to_remove = set()
            user_search_input = ui.input('搜索用户', placeholder='输入用户名或邮箱搜索').classes('w-full mb-4')
            
            with ui.column().classes('w-full max-h-60 overflow-y-auto border border-gray-200 dark:border-gray-600 rounded p-3') as user_list_container:
                pass  # 用户列表将在这里动态生成

            def update_user_removal_list():
                """更新可删除的用户列表"""
                search_term = user_search_input.value.strip() if user_search_input.value else None
                
                # 搜索过滤
                if search_term:
                    filtered_users = [user for user in permission_users 
                                     if search_term.lower() in user['username'].lower() or 
                                        search_term.lower() in (user.get('full_name', '') or '').lower()]
                else:
                    filtered_users = permission_users
                
                user_list_container.clear()
                with user_list_container:
                    if not filtered_users:
                        ui.label('没有匹配的用户').classes('text-gray-500 text-center py-4')
                        return
                    
                    for user_data in filtered_users:
                        def create_user_removal_checkbox(ud):
                            def on_user_check(checked):
                                if checked:
                                    selected_users_to_remove.add(ud['id'])
                                else:
                                    selected_users_to_remove.discard(ud['id'])
                            
                            with ui.row().classes('items-center gap-3 p-2 hover:bg-gray-50 dark:hover:bg-gray-700 rounded'):
                                ui.checkbox(on_change=on_user_check).classes('flex-none')
                                ui.icon('person').classes('text-orange-500')
                                with ui.column().classes('gap-1'):
                                    ui.label(ud.get('full_name') or ud['username']).classes('font-medium')
                                    ui.label(f"用户名: {ud['username']}").classes('text-sm text-gray-500')
                        
                        create_user_removal_checkbox(user_data)

            user_search_input.on('input', lambda: update_user_removal_list())

            with ui.row().classes('w-full gap-2 mt-6 justify-end'):
                ui.button('取消', on_click=dialog.close).classes('bg-gray-500 text-white px-4 py-2')
                ui.button('确认删除', on_click=lambda: confirm_remove_users()).classes('bg-orange-600 text-white px-4 py-2')

            def confirm_remove_users():
                """确认删除用户关联"""
                if not selected_users_to_remove:
                    ui.notify('请至少选择一个用户', type='warning')
                    return

                log_info(f"开始从权限 {permission_data.name} 删除用户关联: {list(selected_users_to_remove)}")
                
                success_count = 0
                for user_id in selected_users_to_remove:
                    success = safe(
                        lambda uid=user_id: remove_permission_from_user(permission_data.id, uid),
                        return_value=False,
                        error_msg=f"删除用户 {user_id} 关联失败"
                    )
                    if success:
                        success_count += 1

                if success_count > 0:
                    ui.notify(f'成功删除 {success_count} 个用户关联', type='positive')
                    dialog.close()
                    load_permissions()
                else:
                    ui.notify('删除用户关联失败', type='error')

            # 初始化用户列表
            update_user_removal_list()

        dialog.open()

    # 辅助函数：权限-角色关联操作
    def add_permission_to_roles(permission_id: int, role_ids: list) -> bool:
        """将权限添加到指定角色"""
        try:
            with db_safe("添加权限到角色") as db:
                permission = db.query(Permission).filter(Permission.id == permission_id).first()
                if not permission:
                    return False

                roles = db.query(Role).filter(Role.id.in_(role_ids)).all()
                for role in roles:
                    if permission not in role.permissions:
                        role.permissions.append(permission)

                return True

        except Exception as e:
            log_error(f"添加权限到角色失败: {e}")
            return False

    def remove_permission_from_role(permission_id: int, role_name: str) -> bool:
        """从指定角色中移除权限"""
        try:
            with db_safe("移除权限角色关联") as db:
                permission = db.query(Permission).filter(Permission.id == permission_id).first()
                if not permission:
                    return False

                role = db.query(Role).filter(Role.name == role_name).first()
                if not role:
                    return False

                if permission in role.permissions:
                    role.permissions.remove(permission)

                return True

        except Exception as e:
            log_error(f"移除权限角色关联失败: {e}")
            return False

    # 辅助函数：权限-用户关联操作（新增功能）
    def add_permission_to_users(permission_id: int, user_ids: list) -> bool:
        """将权限直接添加到指定用户 - 使用 detached_helper 中的函数"""
        try:
            success_count = 0
            for user_id in user_ids:
                # 使用 detached_helper 中的函数
                from ..detached_helper import add_permission_to_user_safe
                if add_permission_to_user_safe(user_id, permission_id):
                    success_count += 1
            
            return success_count > 0

        except Exception as e:
            log_error(f"添加权限到用户失败: {e}")
            return False

    def remove_permission_from_user(permission_id: int, user_id: int) -> bool:
        """从指定用户中移除权限 - 使用 detached_helper 中的函数"""
        try:
            from ..detached_helper import remove_permission_from_user_safe
            return remove_permission_from_user_safe(user_id, permission_id)

        except Exception as e:
            log_error(f"移除用户权限关联失败: {e}")
            return False

    # 初始加载权限显示
    load_permissions()

    log_info("===权限管理页面加载完成===")



```

- **auth\pages\profile_page.py**
```python
from nicegui import ui
from ..auth_manager import auth_manager
from ..decorators import require_login
from ..utils import get_avatar_url, format_datetime
from component.static_resources import static_manager
from component.spa_layout import navigate_to

# 导入异常处理模块
# from common.exception_handler import log_info, log_error, safe, safe_protect
from common.log_handler import (
    # 日志记录函数
    log_trace, log_debug, log_info, log_success, 
    log_warning, log_error, log_critical,
    # 安全执行
    safe, db_safe,
    # 装饰器
    safe_protect, catch,
    # Logger 实例
    get_logger
)
logger = get_logger(__file__)

@require_login()
@safe_protect(name="个人资料页面", error_msg="个人资料页面加载失败，请稍后重试")
def profile_page_content():
    """用户资料页面内容 - 4个卡片水平排列，完全适配暗黑模式"""
    user = auth_manager.current_user
    if not user:
        ui.notify('请先登录', type='warning')
        return

    log_info("个人资料页面开始加载")

    # 页面标题
    with ui.column().classes('w-full mb-6'):
        ui.label('个人资料').classes('text-4xl font-bold text-indigo-800 dark:text-indigo-200 mb-2')
        ui.label('管理您的个人信息和账户设置').classes('text-lg text-gray-600 dark:text-gray-400')

    # 用户统计卡片区域 (These top 4 cards are already using flex-1 and look fine)
    with ui.row().classes('w-full gap-6 mb-8'):
        with ui.card().classes('flex-1 p-6 bg-gradient-to-br from-purple-500 to-purple-600 text-white shadow-lg'):
            with ui.row().classes('items-center justify-between w-full'):
                with ui.column().classes('gap-1'):
                    ui.label('用户ID').classes('text-sm opacity-90 font-medium')
                    ui.label(str(user.id)).classes('text-3xl font-bold')
                ui.icon('person').classes('text-4xl opacity-80')

        with ui.card().classes('flex-1 p-6 bg-gradient-to-br from-green-500 to-green-600 text-white shadow-lg'):
            with ui.row().classes('items-center justify-between w-full'):
                with ui.column().classes('gap-1'):
                    ui.label('登录次数').classes('text-sm opacity-90 font-medium')
                    ui.label(str(user.login_count)).classes('text-3xl font-bold')
                ui.icon('login').classes('text-4xl opacity-80')

        with ui.card().classes('flex-1 p-6 bg-gradient-to-br from-blue-500 to-blue-600 text-white shadow-lg'):
            with ui.row().classes('items-center justify-between w-full'):
                with ui.column().classes('gap-1'):
                    ui.label('账户状态').classes('text-sm opacity-90 font-medium')
                    ui.label('正常' if user.is_active else '禁用').classes('text-3xl font-bold')
                ui.icon('check_circle' if user.is_active else 'block').classes('text-4xl opacity-80')

        with ui.card().classes('flex-1 p-6 bg-gradient-to-br from-orange-500 to-orange-600 text-white shadow-lg'):
            with ui.row().classes('items-center justify-between w-full'):
                with ui.column().classes('gap-1'):
                    ui.label('角色数量').classes('text-sm opacity-90 font-medium')
                    ui.label(str(len(user.roles))).classes('text-3xl font-bold')
                ui.icon('security').classes('text-4xl opacity-80')

    # Changed classes: added 'flex-wrap items-stretch' to the row
    with ui.row().classes('w-full gap-4 flex-wrap items-stretch'):
        # 1. 基本信息卡片
        # Changed classes: added 'min-w-80' to allow wrapping and prevent excessive shrinking
        with ui.column().classes('flex-1 min-w-80'):
            create_user_info_card(user)
        
        # 2. 编辑个人信息卡片
        with ui.column().classes('flex-1 min-w-80'):
            create_profile_edit_card(user)
        
        # 3. 角色与权限卡片
        with ui.column().classes('flex-1 min-w-80'):
            create_roles_permissions_card(user)
        
        # 4. 安全设置卡片
        with ui.column().classes('flex-1 min-w-80'):
            create_security_settings_card(user)

    log_info("个人资料页面加载完成")

@safe_protect(name="创建用户基本信息卡片", error_msg="创建用户基本信息卡片页面加载失败")
def create_user_info_card(user):
    """创建用户基本信息卡片 - 完全适配暗黑模式"""
    # 确定用户状态主题
    if user.is_superuser:
        card_theme = 'border-l-4 border-purple-500'
        icon_theme = 'text-purple-600 dark:text-purple-400'
    elif 'admin' in user.roles:
        card_theme = 'border-l-4 border-red-500'
        icon_theme = 'text-red-600 dark:text-red-400'
    else:
        card_theme = 'border-l-4 border-blue-500'
        icon_theme = 'text-blue-600 dark:text-blue-400'

    with ui.card().classes(f'w-full p-4 mb-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-700 {card_theme}'):
        with ui.column().classes('w-full p-4 gap-3 h-full'):
            # 标题
            ui.label('基本信息').classes('text-lg font-bold text-gray-800 dark:text-white border-b pb-2 border-gray-200 dark:border-gray-600 mb-3')
            
            # 头像区域
            with ui.column().classes('items-center gap-2 mb-4'):
                with ui.avatar().classes('w-16 h-16 bg-gradient-to-br from-blue-400 to-purple-500'):
                    avatar_url = get_avatar_url(user)
                    ui.image(avatar_url).classes('w-14 h-14 rounded-full border-2 border-white dark:border-gray-600')
                
                ui.button(
                    '更换头像',
                    icon='photo_camera',
                    on_click=lambda: ui.notify('头像上传功能即将推出', type='info')
                ).classes('bg-blue-600 hover:bg-blue-700 text-white px-2 py-1 text-xs rounded-md').props('size=sm')

            # 用户基本信息
            with ui.column().classes('gap-2 flex-1'):
                # 用户名
                with ui.row().classes('items-center gap-2'):
                    ui.icon('person').classes(f'text-lg {icon_theme}')
                    with ui.column().classes('gap-0'):
                        ui.label(user.username).classes('text-lg font-bold text-gray-800 dark:text-white')
                        ui.label(f'ID: {user.id}').classes('text-xs text-gray-500 dark:text-gray-400')

                # 邮箱
                with ui.row().classes('w-full items-center gap-2'):
                    ui.icon('email').classes('text-lg text-gray-600 dark:text-gray-400')
                    ui.label(user.email).classes('text-sm text-gray-700 dark:text-gray-300 truncate')

                # 姓名（如果有）
                if user.full_name:
                    with ui.row().classes('items-center gap-2'):
                        ui.icon('badge').classes('text-lg text-gray-600 dark:text-gray-400')
                        ui.label(user.full_name).classes('text-sm text-gray-700 dark:text-gray-300')

            # 用户标签
            with ui.column().classes('gap-2 mt-3'):
                if user.is_superuser:
                    ui.chip('超级管理员', icon='admin_panel_settings').classes('bg-purple-100 text-purple-800 dark:bg-purple-800 dark:text-purple-200 text-xs')
                
                with ui.row().classes('gap-1 flex-wrap'):
                    if user.is_active:
                        ui.chip('正常', icon='check_circle').classes('bg-green-100 text-green-800 dark:bg-green-800 dark:text-green-200 text-xs')
                    else:
                        ui.chip('禁用', icon='block').classes('bg-red-100 text-red-800 dark:bg-red-800 dark:text-red-200 text-xs')

                    if user.is_verified:
                        ui.chip('已验证', icon='verified').classes('bg-blue-100 text-blue-800 dark:bg-blue-800 dark:text-blue-200 text-xs')
                    else:
                        ui.chip('未验证', icon='warning').classes('bg-orange-100 text-orange-800 dark:bg-orange-800 dark:text-orange-200 text-xs')

            # 时间信息
            with ui.column().classes('gap-2 mt-auto'):
                with ui.row().classes('items-center gap-2 p-2 bg-gray-50 dark:bg-gray-700 rounded text-xs'):
                    ui.icon('calendar_today').classes('text-sm text-blue-600 dark:text-blue-400')
                    with ui.column().classes('gap-0'):
                        ui.label('注册').classes('text-xs text-gray-600 dark:text-gray-400')
                        ui.label(format_datetime(user.created_at)[:10] if user.created_at else '未知').classes('text-xs font-medium text-gray-800 dark:text-white')

                with ui.row().classes('items-center gap-2 p-2 bg-gray-50 dark:bg-gray-700 rounded text-xs'):
                    ui.icon('access_time').classes('text-sm text-green-600 dark:text-green-400')
                    with ui.column().classes('gap-0'):
                        ui.label('最后登录').classes('text-xs text-gray-600 dark:text-gray-400')
                        ui.label(format_datetime(user.last_login)[:10] if user.last_login else '从未登录').classes('text-xs font-medium text-gray-800 dark:text-white')

@safe_protect(name="创建个人信息编辑卡片", error_msg="创建个人信息编辑卡片页面加载失败")
def create_profile_edit_card(user):
    """创建个人信息编辑卡片 - 完全适配暗黑模式"""
    with ui.card().classes('w-full p-4 mb-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-700'):
        with ui.column().classes('w-full p-4 gap-3 h-full'):
            ui.label('编辑个人信息').classes('text-lg font-bold text-gray-800 dark:text-white border-b pb-2 border-gray-200 dark:border-gray-600 mb-3')

            # 表单字段
            full_name_input = ui.input(
                '姓名',
                value=user.full_name or '',
                placeholder='请输入您的姓名'
            ).classes('w-full').props('outlined clearable')

            phone_input = ui.input(
                '电话',
                value=user.phone or '',
                placeholder='请输入您的电话'
            ).classes('w-full mt-2').props('outlined clearable')

            email_input = ui.input(
                '邮箱地址',
                value=user.email,
                placeholder='请输入您的邮箱'
            ).classes('w-full mt-2').props('outlined clearable')

            bio_input = ui.textarea(
                '个人简介',
                value=user.bio or '',
                placeholder='介绍一下自己...'
            ).classes('w-full mt-2 flex-1').props('outlined clearable')

            def save_profile():
                """保存个人资料"""
                log_info(f"开始保存用户资料: {user.username}")
                
                result = auth_manager.update_profile(
                    user.id,
                    full_name=full_name_input.value,
                    phone=phone_input.value,
                    email=email_input.value,
                    bio=bio_input.value
                )

                if result['success']:
                    log_info(f"用户资料保存成功: {user.username}")
                    ui.notify('个人资料更新成功', type='positive', position='top')
                    ui.timer(1.0, lambda: ui.navigate.reload(), once=True)
                else:
                    log_error(f"保存用户资料失败: {user.username}")
                    ui.notify(result['message'], type='negative', position='top')

            # 保存按钮 - 固定在底部
            ui.button(
                '保存修改',
                icon='save',
                on_click=lambda: safe(save_profile)
            ).classes('mt-auto bg-green-600 hover:bg-green-700 text-white w-full py-2 font-semibold rounded-lg transition-colors duration-200')

@safe_protect(name="创建角色权限卡片", error_msg="创建角色权限卡片页面加载失败")
def create_roles_permissions_card(user):
    """创建角色权限卡片 - 完全适配暗黑模式"""
    with ui.card().classes('w-full p-4 mb-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-700'):
        with ui.column().classes('w-full p-4 gap-3 h-full'):
            ui.label('角色与权限').classes('text-lg font-bold text-gray-800 dark:text-white border-b pb-2 border-gray-200 dark:border-gray-600 mb-3')

            # 当前角色显示
            ui.label('当前角色').classes('text-sm font-medium text-gray-700 dark:text-gray-300 mb-2')
            if user.roles:
                with ui.column().classes('gap-1 mb-4'):
                    for role in user.roles:
                        role_color = 'red' if role == 'admin' else 'blue' if role == 'user' else 'green'
                        ui.chip(role, icon='security').classes(f'bg-{role_color}-100 text-{role_color}-800 dark:bg-{role_color}-800 dark:text-{role_color}-200 text-xs font-medium')
            else:
                with ui.card().classes('w-full p-3 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600'):
                    with ui.column().classes('w-full items-center py-1'):
                        ui.icon('security_update_warning').classes('text-2xl text-gray-400 mb-1')
                        ui.label('暂无角色').classes('text-xs text-gray-500 dark:text-gray-400')

            # 权限说明
            ui.separator().classes('my-3 border-gray-200 dark:border-gray-600')
            ui.label('权限说明').classes('text-sm font-medium text-gray-700 dark:text-gray-300 mb-2')
            
            # 权限列表 - 紧凑显示
            with ui.column().classes('gap-2 flex-1 overflow-auto'):
                permission_items = [
                    ('管理员', '系统完整管理权限', 'admin_panel_settings'),
                    ('普通用户', '基本功能使用权限', 'person'),
                    ('数据访问', '查看和分析数据', 'analytics'),
                    ('内容编辑', '创建编辑内容', 'edit')
                ]

                for title, desc, icon in permission_items:
                    with ui.row().classes('items-start gap-2 p-2 bg-gray-50 dark:bg-gray-700 rounded'):
                        ui.icon(icon).classes('text-sm text-blue-600 dark:text-blue-400 mt-0.5')
                        with ui.column().classes('flex-1 gap-0'):
                            ui.label(title).classes('text-xs font-medium text-gray-800 dark:text-white')
                            ui.label(desc).classes('text-xs text-gray-600 dark:text-gray-400 leading-tight')

@safe_protect(name="创建安全设置卡片", error_msg="创建安全设置卡片页面加载失败")
def create_security_settings_card(user):
    """创建安全设置卡片 - 完全适配暗黑模式"""
    with ui.card().classes('w-full p-4 mb-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-700'):
        with ui.column().classes('w-full p-4 gap-3 h-full'):
            ui.label('安全设置').classes('text-lg font-bold text-gray-800 dark:text-white border-b pb-2 border-gray-200 dark:border-gray-600 mb-3')

            # 修改密码
            with ui.card().classes('w-full p-3 bg-orange-50 dark:bg-orange-900/20 border border-orange-200 dark:border-orange-800 rounded'):
                with ui.row().classes('items-center gap-2 w-full'):
                    ui.icon('lock').classes('text-lg text-orange-600 dark:text-orange-400')
                    with ui.column().classes('flex-1 gap-0'):
                        ui.label('修改密码').classes('text-sm font-bold text-orange-800 dark:text-orange-200')
                        ui.label('定期修改密码保证安全').classes('text-xs text-orange-600 dark:text-orange-300')

                    def go_to_change_password():
                        navigate_to('change_password', '修改密码')

                    ui.button(
                        '修改',
                        icon='edit',
                        on_click=lambda: safe(go_to_change_password)
                    ).classes('bg-orange-600 hover:bg-orange-700 text-white px-2 py-1 text-xs rounded').props('size=md')

            # 账户注销
            with ui.card().classes('w-full p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded mt-auto'):
                with ui.row().classes('items-center gap-2 w-full'):
                    ui.icon('logout').classes('text-lg text-red-600 dark:text-red-400')
                    with ui.column().classes('flex-1 gap-0'):
                        ui.label('注销账户').classes('text-sm font-bold text-red-800 dark:text-red-200')
                        ui.label('退出当前登录状态').classes('text-xs text-red-600 dark:text-red-300')

                    def handle_logout():
                        """处理注销"""
                        with ui.dialog() as logout_dialog, ui.card().classes('p-6 rounded-lg shadow-xl bg-white dark:bg-gray-800'):
                            ui.label('确认注销').classes('text-xl font-semibold text-red-600 dark:text-red-400 mb-4')
                            ui.label('您确定要注销当前账户吗？').classes('text-gray-700 dark:text-gray-300')

                            with ui.row().classes('gap-3 mt-6 justify-end w-full'):
                                ui.button('取消', on_click=logout_dialog.close).classes('bg-gray-400 hover:bg-gray-500 text-white px-4 py-2 rounded-lg')

                                def confirm_logout():
                                    logout_dialog.close()
                                    log_info(f"用户主动注销: {user.username}")
                                    navigate_to('logout', '注销')

                                ui.button('确认注销', on_click=lambda: safe(confirm_logout)).classes('bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg')

                        logout_dialog.open()

                    ui.button(
                        '注销',
                        icon='logout',
                        on_click=lambda: safe(handle_logout)
                    ).classes('bg-red-600 hover:bg-red-700 text-white px-2 py-1 text-xs rounded').props('size=md')
```

- **auth\pages\prompt_config_management_page.py**
```python
"""
系统提示词配置管理页面
管理 config/yaml/system_prompt_config.yaml 中的提示词模板
提供新建、修改、删除功能
"""
from nicegui import ui
from typing import Optional, Dict, Any, List
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from config.yaml_config_manager import SystemPromptConfigFileManager
from component.chat.config import get_system_prompt_manager
# from common.exception_handler import safe_protect
from common.log_handler import (
    # 日志记录函数
    log_trace, log_debug, log_info, log_success, 
    log_warning, log_error, log_critical,
    # 安全执行
    safe, db_safe,
    # 装饰器
    safe_protect, catch,
    # Logger 实例
    get_logger
)
logger = get_logger(__file__)

class PromptConfigManagementPage:
    """系统提示词配置管理页面类"""
    
    def __init__(self):
        self.file_manager = SystemPromptConfigFileManager()
        self.prompts_data = []
        self.categories = []
        
        # 预定义分类选项
        self.default_categories = [
            '文档编写',
            '代码助手',
            '数据分析',
            '业务助手',
            '知识问答',
            '创意写作',
            '翻译助手',
            '教育培训',
            '其他'
        ]
    
    def render(self):
        """渲染页面"""
        ui.add_head_html('''
            <style>
            .prompt_edit_dialog-hide-scrollbar {
                overflow-y: auto;
                scrollbar-width: none;
                -ms-overflow-style: none;
            }
            .prompt_edit_dialog-hide-scrollbar::-webkit-scrollbar {
                display: none;
            }
            </style>
        ''')
        
        # 页面标题
        with ui.row().classes('w-full items-center justify-between mb-6'):
            with ui.column():
                ui.label('系统提示词配置管理').classes('text-3xl font-bold text-green-800 dark:text-green-200')
                ui.label('管理系统中的AI提示词模板').classes('text-sm text-gray-600 dark:text-gray-400')
            
            with ui.row().classes('gap-2'):
                ui.button('分类统计', icon='analytics', 
                         on_click=self.show_category_stats_dialog).props('flat')
                ui.button('刷新列表', icon='refresh', 
                         on_click=self.refresh_page).classes('bg-gray-500 text-white')
                ui.button('新增提示词', icon='add', 
                         on_click=self.show_add_dialog).classes('bg-green-500 text-white')
        
        # 提示词列表 - 使用卡片网格布局
        self.create_cards_grid()
    
    def create_cards_grid(self):
        """创建提示词卡片网格"""
        # 加载数据
        self.load_prompts_data()
        
        with ui.card().classes('w-full'):
            ui.label(f'提示词模板列表 (共 {len(self.prompts_data)} 个)').classes('text-lg font-semibold mb-4')
            
            if not self.prompts_data:
                with ui.column().classes('w-full items-center py-8'):
                    ui.icon('description').classes('text-6xl text-gray-400 mb-4')
                    ui.label('暂无提示词模板').classes('text-lg text-gray-500')
                    ui.label('点击上方"新增提示词"按钮添加第一个提示词模板').classes('text-sm text-gray-400')
            else:
                # 使用网格布局展示卡片
                with ui.grid(columns=3).classes('w-full gap-4'):
                    for prompt in self.prompts_data:
                        self.create_prompt_card(prompt)
    
    def create_prompt_card(self, prompt_data: Dict[str, Any]):
        """创建单个提示词卡片"""
        template_key = prompt_data['template_key']
        config = prompt_data['config']
        
        name = config.get('name', template_key)
        category = config.get('category', '未分类')
        description = config.get('description', '无描述')
        enabled = config.get('enabled', True)
        system_prompt = config.get('system_prompt', '')
        
        with ui.card().classes('w-full hover:shadow-lg transition-shadow'):
            # 卡片头部 - 名称和分类
            with ui.card_section():
                with ui.row().classes('w-full items-center justify-between'):
                    with ui.column().classes('flex-1'):
                        ui.label(name).classes('text-lg font-bold text-green-700 dark:text-green-300')
                        with ui.row().classes('gap-2 items-center mt-1'):
                            ui.badge(category, color='primary').props('outline')
                            ui.badge(template_key).classes('text-xs')
                    
                    # 状态徽章
                    if enabled:
                        ui.badge('启用', color='positive')
                    else:
                        ui.badge('禁用', color='negative')
            
            ui.separator()
            
            # 卡片内容 - 描述
            with ui.card_section():
                # 截断描述文本
                display_desc = description[:80] + '...' if len(description) > 80 else description
                ui.label(display_desc).classes('text-sm text-gray-600 dark:text-gray-400 min-h-12')
            
            ui.separator()
            
            # 卡片底部 - 提示词长度和操作按钮
            with ui.card_section():
                with ui.row().classes('w-full items-center justify-between'):
                    # 提示词字数统计
                    prompt_length = len(system_prompt)
                    ui.label(f'提示词: {prompt_length} 字符').classes('text-xs text-gray-500')
                    
                    # 操作按钮
                    with ui.row().classes('gap-1'):
                        ui.button(icon='visibility', on_click=lambda k=template_key: self.show_preview_dialog(k)).props('flat dense round size=sm color=primary').tooltip('预览')
                        ui.button(icon='edit', on_click=lambda k=template_key: self.show_edit_dialog(k)).props('flat dense round size=sm color=primary').tooltip('编辑')
                        ui.button(icon='delete', on_click=lambda k=template_key: self.show_delete_confirm(k)).props('flat dense round size=sm color=negative').tooltip('删除')
    
    def load_prompts_data(self):
        """加载提示词数据"""
        self.prompts_data = self.file_manager.get_all_prompts_list()
        self.categories = self.file_manager.get_categories_from_config()
    
    def refresh_page(self):
        """刷新页面"""
        ui.notify('正在刷新...', type='info', position='top')
        self.load_prompts_data()
        ui.notify('刷新成功!', type='positive', position='top')
        ui.navigate.reload()
    
    def show_category_stats_dialog(self):
        """显示分类统计对话框"""
        with ui.dialog() as dialog, ui.card().classes('w-full max-w-2xl'):
            ui.label('提示词分类统计').classes('text-xl font-bold mb-4')
            
            # 统计各分类的提示词数量
            category_stats = {}
            for prompt in self.prompts_data:
                category = prompt['config'].get('category', '未分类')
                category_stats[category] = category_stats.get(category, 0) + 1
            
            # 使用表格展示
            if category_stats:
                columns = [
                    {'name': 'category', 'label': '分类', 'field': 'category', 'align': 'left'},
                    {'name': 'count', 'label': '数量', 'field': 'count', 'align': 'center'},
                    {'name': 'percentage', 'label': '占比', 'field': 'percentage', 'align': 'center'},
                ]
                
                total = len(self.prompts_data)
                rows = []
                for category, count in sorted(category_stats.items(), key=lambda x: x[1], reverse=True):
                    percentage = f"{(count / total * 100):.1f}%"
                    rows.append({
                        'category': category,
                        'count': count,
                        'percentage': percentage
                    })
                
                ui.table(columns=columns, rows=rows).classes('w-full')
            else:
                ui.label('暂无数据').classes('text-gray-500')
            
            with ui.row().classes('w-full justify-end mt-4'):
                ui.button('关闭', on_click=dialog.close).props('flat')
        
        dialog.open()
    
    def show_add_dialog(self):
        """显示新增提示词对话框"""
        with ui.dialog() as dialog, ui.card().classes('w-full max-w-4xl'):
            ui.label('新增系统提示词').classes('text-xl font-bold mb-4')
            
            # 表单字段
            with ui.column().classes('w-full gap-4 prompt_edit_dialog-hide-scrollbar'):
                # 基本信息
                ui.label('基本信息').classes('text-lg font-semibold text-green-600')
                
                with ui.grid(columns=2).classes('w-full gap-4'):
                    template_key_input = ui.input(
                        label='模板标识 (key) *',
                        placeholder='例如: qa_expert'
                    ).classes('w-full')
                    
                    template_name_input = ui.input(
                        label='显示名称 *',
                        placeholder='例如: 问答专家'
                    ).classes('w-full')
                
                # 分类选择 - 支持自定义
                with ui.row().classes('w-full gap-2'):
                    # 合并预定义分类和已有分类
                    all_categories = sorted(list(set(self.default_categories + self.categories)))
                    
                    category_select = ui.select(
                        label='分类 *',
                        options=all_categories,
                        value=all_categories[0] if all_categories else None,
                        with_input=True  # 允许输入自定义分类
                    ).classes('flex-1')
                    
                    category_select.props('use-input input-debounce=0 new-value-mode=add-unique')
                
                description_input = ui.textarea(
                    label='描述 *',
                    placeholder='简要描述该提示词的用途和特点...'
                ).classes('w-full').props('rows=3')
                
                # 提示词内容
                ui.separator()
                ui.label('提示词内容').classes('text-lg font-semibold text-green-600')
                
                with ui.column().classes('w-full'):
                    ui.label('系统提示词 (支持 Markdown 格式) *').classes('text-sm font-semibold')
                    ui.label('提示: 可以使用 Markdown 语法编写结构化的提示词').classes('text-xs text-gray-500')
                    
                    system_prompt_input = ui.textarea(
                        placeholder='# 角色定位\n你是一个...\n\n## 核心能力\n1. ...\n2. ...'
                    ).classes('w-full font-mono').props('rows=12')
                    
                    # 字符计数
                    char_count_label = ui.label('0 字符').classes('text-xs text-gray-500 text-right')
                    
                    def update_char_count():
                        count = len(system_prompt_input.value or '')
                        char_count_label.text = f'{count} 字符'
                    
                    system_prompt_input.on('update:model-value', lambda: update_char_count())
                
                # 高级配置
                ui.separator()
                ui.label('高级配置').classes('text-lg font-semibold text-green-600')
                
                with ui.row().classes('w-full gap-4'):
                    version_input = ui.input(
                        label='版本号',
                        value='1.0',
                        placeholder='1.0'
                    ).classes('w-32')
                    
                    enabled_switch = ui.switch(
                        '启用此提示词',
                        value=True
                    ).classes('flex-1')
            
            # 按钮
            with ui.row().classes('w-full justify-end gap-2 mt-4'):
                ui.button('取消', on_click=dialog.close).props('flat')
                ui.button(
                    '保存',
                    icon='save',
                    on_click=lambda: self.save_new_prompt(
                        dialog,
                        template_key_input.value,
                        template_name_input.value,
                        category_select.value,
                        description_input.value,
                        system_prompt_input.value,
                        version_input.value,
                        enabled_switch.value
                    )
                ).classes('bg-green-500 text-white')
        
        dialog.open()
    
    def save_new_prompt(self, dialog, template_key, name, category, description,
                        system_prompt, version, enabled):
        """保存新提示词"""
        # 验证必填字段
        if not all([template_key, name, category, description, system_prompt]):
            ui.notify('请填写所有必填字段', type='negative')
            return
        
        # 构建配置对象
        config = {
            'name': name,
            'description': description,
            'enabled': enabled,
            'version': version,
            'category': category,
            'system_prompt': system_prompt,
            'examples': {}  # 保留 examples 字段,可后续扩展
        }
        
        # 保存到文件
        success = self.file_manager.add_prompt_config(template_key, config)
        
        if success:
            ui.notify(f'成功添加提示词模板: {name}', type='positive')
            
            # 重新加载配置管理器
            get_system_prompt_manager().reload_config()
            
            dialog.close()
            
            # 刷新页面
            ui.navigate.reload()
        else:
            ui.notify('保存失败,可能模板标识已存在', type='negative')
    
    def show_preview_dialog(self, template_key: str):
        """显示提示词预览对话框"""
        prompt_config = self.file_manager.get_prompt_config(template_key)
        if not prompt_config:
            ui.notify('提示词模板不存在', type='negative')
            return
        
        with ui.dialog() as dialog, ui.card().classes('w-full max-w-4xl prompt_edit_dialog-hide-scrollbar'):
        # with ui.column().classes('w-full gap-4 prompt_edit_dialog-hide-scrollbar'):
            # 标题
            name = prompt_config.get('name', template_key)
            ui.label(f'预览: {name}').classes('text-xl font-bold mb-4')
            
            # 基本信息
            with ui.grid(columns=2).classes('w-full gap-4 mb-4'):
                with ui.column():
                    ui.label('模板标识').classes('text-sm text-gray-600')
                    ui.label(template_key).classes('text-base font-semibold')
                
                with ui.column():
                    ui.label('分类').classes('text-sm text-gray-600')
                    category = prompt_config.get('category', '未分类')
                    ui.badge(category, color='primary')
            
            with ui.column().classes('w-full mb-4'):
                ui.label('描述').classes('text-sm text-gray-600')
                ui.label(prompt_config.get('description', '')).classes('text-base')
            
            ui.separator()
            
            # 提示词内容 - 使用 Markdown 渲染
            ui.label('提示词内容').classes('text-lg font-semibold mt-4 mb-2')
            
            system_prompt = prompt_config.get('system_prompt', '')
            
            # with ui.card().classes('w-full bg-gray-50 dark:bg-gray-800'):
            with ui.scroll_area().classes('w-full h-96'):
                ui.markdown(system_prompt).classes('p-4')
            
            # 底部信息
            with ui.row().classes('w-full justify-between mt-4'):
                prompt_length = len(system_prompt)
                ui.label(f'字符数: {prompt_length}').classes('text-sm text-gray-500')
                
                version = prompt_config.get('version', '1.0')
                ui.label(f'版本: {version}').classes('text-sm text-gray-500')
            
            with ui.row().classes('w-full justify-end gap-2 mt-4'):
                ui.button('关闭', on_click=dialog.close).props('flat')
                ui.button(
                    '编辑',
                    icon='edit',
                    on_click=lambda:  self.show_edit_dialog(template_key)
                ).classes('bg-green-500 text-white')
        
        dialog.open()
    
    def show_edit_dialog(self, template_key: str):
        """显示编辑提示词对话框"""
        prompt_config = self.file_manager.get_prompt_config(template_key)
        if not prompt_config:
            ui.notify('提示词模板不存在', type='negative')
            return
        
        with ui.dialog() as dialog, ui.card().classes('w-full max-w-4xl'):
            ui.label(f'编辑提示词: {prompt_config.get("name", template_key)}').classes('text-xl font-bold mb-4')
            
            # 表单字段(预填充)
            with ui.column().classes('w-full gap-4 prompt_edit_dialog-hide-scrollbar'):
                # 基本信息
                ui.label('基本信息').classes('text-lg font-semibold text-green-600')
                
                with ui.grid(columns=2).classes('w-full gap-4'):
                    # 显示模板标识(不可编辑)
                    with ui.column().classes('w-full'):
                        ui.label('模板标识').classes('text-sm text-gray-600')
                        ui.label(template_key).classes('text-base font-semibold')
                    
                    template_name_input = ui.input(
                        label='显示名称 *',
                        value=prompt_config.get('name', '')
                    ).classes('w-full')
                
                # 分类选择
                with ui.row().classes('w-full gap-2'):
                    all_categories = sorted(list(set(self.default_categories + self.categories)))
                    current_category = prompt_config.get('category', '未分类')
                    
                    category_select = ui.select(
                        label='分类 *',
                        options=all_categories,
                        value=current_category,
                        with_input=True
                    ).classes('flex-1')
                    
                    category_select.props('use-input input-debounce=0 new-value-mode=add-unique')
                
                description_input = ui.textarea(
                    label='描述 *',
                    value=prompt_config.get('description', '')
                ).classes('w-full').props('rows=3')
                
                # 提示词内容
                ui.separator()
                ui.label('提示词内容').classes('text-lg font-semibold text-green-600')
                
                with ui.column().classes('w-full'):
                    ui.label('系统提示词 (支持 Markdown 格式) *').classes('text-sm font-semibold')
                    
                    system_prompt_input = ui.textarea(
                        value=prompt_config.get('system_prompt', '')
                    ).classes('w-full font-mono').props('rows=12')
                    
                    # 字符计数
                    initial_count = len(prompt_config.get('system_prompt', ''))
                    char_count_label = ui.label(f'{initial_count} 字符').classes('text-xs text-gray-500 text-right')
                    
                    def update_char_count():
                        count = len(system_prompt_input.value or '')
                        char_count_label.text = f'{count} 字符'
                    
                    system_prompt_input.on('update:model-value', lambda: update_char_count())
                
                # 高级配置
                ui.separator()
                ui.label('高级配置').classes('text-lg font-semibold text-green-600')
                
                with ui.row().classes('w-full gap-4'):
                    version_input = ui.input(
                        label='版本号',
                        value=prompt_config.get('version', '1.0')
                    ).classes('w-32')
                    
                    enabled_switch = ui.switch(
                        '启用此提示词',
                        value=prompt_config.get('enabled', True)
                    ).classes('flex-1')
            
            # 按钮
            with ui.row().classes('w-full justify-end gap-2 mt-4'):
                ui.button('取消', on_click=dialog.close).props('flat')
                ui.button(
                    '保存修改',
                    icon='save',
                    on_click=lambda: self.save_edit_prompt(
                        dialog,
                        template_key,
                        template_name_input.value,
                        category_select.value,
                        description_input.value,
                        system_prompt_input.value,
                        version_input.value,
                        enabled_switch.value
                    )
                ).classes('bg-green-500 text-white')
        
        dialog.open()
    
    def save_edit_prompt(self, dialog, template_key, name, category, description,
                        system_prompt, version, enabled):
        """保存编辑后的提示词"""
        # 验证必填字段
        if not all([name, category, description, system_prompt]):
            ui.notify('请填写所有必填字段', type='negative')
            return
        
        # 构建配置对象
        config = {
            'name': name,
            'description': description,
            'enabled': enabled,
            'version': version,
            'category': category,
            'system_prompt': system_prompt,
            'examples': {}
        }
        
        # 更新文件
        success = self.file_manager.update_prompt_config(template_key, config)
        
        if success:
            ui.notify(f'成功更新提示词模板: {name}', type='positive')
            
            # 重新加载配置管理器
            get_system_prompt_manager().reload_config()
            
            dialog.close()
            
            # 刷新页面
            ui.navigate.reload()
        else:
            ui.notify('更新失败', type='negative')
    
    def show_delete_confirm(self, template_key: str):
        """显示删除确认对话框"""
        prompt_config = self.file_manager.get_prompt_config(template_key)
        if not prompt_config:
            ui.notify('提示词模板不存在', type='negative')
            return
        
        name = prompt_config.get('name', template_key)
        
        with ui.dialog() as dialog, ui.card():
            with ui.column().classes('items-center gap-4 p-4'):
                ui.icon('warning', size='64px').classes('text-orange-500')
                ui.label('确认删除').classes('text-xl font-bold')
                ui.label(f'确定要删除提示词模板 "{name}" 吗?').classes('text-gray-600')
                ui.label('此操作不可恢复!').classes('text-sm text-red-500')
                
                with ui.row().classes('gap-2 mt-4'):
                    ui.button('取消', on_click=dialog.close).props('flat')
                    ui.button(
                        '确认删除',
                        icon='delete',
                        on_click=lambda: self.delete_prompt(dialog, template_key, name)
                    ).classes('bg-red-500 text-white')
        
        dialog.open()
    
    def delete_prompt(self, dialog, template_key: str, name: str):
        """删除提示词"""
        success = self.file_manager.delete_prompt_config(template_key)
        
        if success:
            ui.notify(f'成功删除提示词模板: {name}', type='positive')
            
            # 重新加载配置管理器
            get_system_prompt_manager().reload_config()
            
            dialog.close()
            
            # 刷新页面
            ui.navigate.reload()
        else:
            ui.notify('删除失败', type='negative')


@safe_protect(name=f"系统提示词配置管理页面/{__name__}", error_msg=f"系统提示词配置管理页面类加载失败")
def prompt_config_management_page_content():
    """系统提示词配置管理页面入口函数"""
    page = PromptConfigManagementPage()
    page.render()
```

- **auth\pages\register_page.py**
```python
"""
注册页面
"""
from nicegui import ui
from ..auth_manager import auth_manager
from ..config import auth_config
from ..decorators import public_route
from ..utils import validate_email, validate_username
from common.log_handler import (
    # 日志记录函数
    log_trace, log_debug, log_info, log_success, 
    log_warning, log_error, log_critical,
    # 安全执行
    safe, db_safe,
    # 装饰器
    safe_protect, catch,
    # Logger 实例
    get_logger
)
logger = get_logger(__file__)

@public_route
@safe_protect(name="注册页面内容", error_msg="注册页面内容加载失败")
def register_page_content():
    """注册页面内容"""
    # 检查是否允许注册
    if not auth_config.allow_registration:
        ui.notify('注册功能已关闭', type='warning')
        ui.navigate.to('/workbench')
        return
    
    # 检查是否已登录
    if auth_manager.is_authenticated():
        ui.notify('您已经登录了', type='info')
        ui.navigate.to('/workbench')
        return
    
    with ui.column().classes('absolute-center items-center'):
        with ui.card().classes('w-96 shadow-lg'):
            ui.label('用户注册').classes('text-2xl font-bold text-center w-full mb-4')
            
            # 注册表单
            username_input = ui.input(
                '用户名',
                placeholder='3-50个字符，字母数字下划线'
            ).classes('w-full').props('clearable')
            
            email_input = ui.input(
                '邮箱',
                placeholder='请输入有效的邮箱地址'
            ).classes('w-full mt-4').props('clearable')
            
            password_input = ui.input(
                '密码',
                placeholder=f'至少{auth_config.password_min_length}个字符',
                password=True,
                password_toggle_button=True
            ).classes('w-full mt-4').props('clearable')
            
            confirm_password_input = ui.input(
                '确认密码',
                placeholder='请再次输入密码',
                password=True,
                password_toggle_button=True
            ).classes('w-full mt-4').props('clearable')
            
            # 可选信息
            with ui.expansion('填写更多信息（可选）', icon='person').classes('w-full mt-4'):
                full_name_input = ui.input('姓名', placeholder='您的真实姓名').classes('w-full')
                phone_input = ui.input('电话', placeholder='手机号码').classes('w-full mt-2')
            
            # 用户协议
            agreement_checkbox = ui.checkbox('我已阅读并同意').classes('mt-4')
            ui.link('《用户服务协议》', '#').classes('text-blue-500 hover:underline ml-1').on(
                'click',
                lambda: ui.notify('用户协议内容即将添加', type='info')
            )
            
            # 注册按钮
            async def handle_register():
                # 获取输入值
                username = username_input.value.strip()
                email = email_input.value.strip()
                password = password_input.value
                confirm_password = confirm_password_input.value
                
                # 基本验证
                if not all([username, email, password, confirm_password]):
                    ui.notify('请填写所有必填项', type='warning')
                    return
                
                # 验证用户名
                username_result = validate_username(username)
                if not username_result['valid']:
                    ui.notify(username_result['message'], type='warning')
                    return
                
                # 验证邮箱
                if not validate_email(email):
                    ui.notify('邮箱格式不正确', type='warning')
                    return
                
                # 验证密码
                if password != confirm_password:
                    ui.notify('两次输入的密码不一致', type='warning')
                    return
                
                # 验证用户协议
                if not agreement_checkbox.value:
                    ui.notify('请同意用户服务协议', type='warning')
                    return
                
                # 显示加载状态
                register_button.disable()
                register_button.props('loading')
                
                # 执行注册
                result = auth_manager.register(
                    username=username,
                    email=email,
                    password=password,
                    full_name=full_name_input.value if 'full_name_input' in locals() else '',
                    phone=phone_input.value if 'phone_input' in locals() else ''
                )
                
                # 恢复按钮状态
                register_button.enable()
                register_button.props(remove='loading')
                
                if result['success']:
                    ui.notify('注册成功！即将跳转到登录页面...', type='positive')
                    # 延迟跳转
                    ui.timer(2.0, lambda: ui.navigate.to(auth_config.login_route), once=True)
                else:
                    ui.notify(result['message'], type='negative')
            
            register_button = ui.button(
                '立即注册',
                on_click=handle_register
            ).classes('w-full mt-6').props('color=primary size=lg')
            
            # 分隔线
            with ui.row().classes('w-full mt-6 items-center'):
                ui.separator().classes('flex-1')
                ui.label('已有账号？').classes('px-2 text-gray-500')
                ui.separator().classes('flex-1')
            
            # 返回登录
            ui.link(
                '返回登录',
                auth_config.login_route
            ).classes('w-full text-center text-blue-500 hover:underline mt-4')
```

- **auth\pages\role_management_page.py**
```python
"""
角色管理页面 - 增强版：添加批量关联功能
"""
from nicegui import ui
from ..decorators import require_role
from ..auth_manager import auth_manager
from ..detached_helper import (
    detached_manager,
    get_roles_safe,
    get_role_safe,
    get_users_safe,
    update_role_safe,
    delete_role_safe,
    create_role_safe,
    DetachedRole,
    DetachedUser
)
from ..models import Role, User
from ..database import get_db
import io
import csv

# 导入异常处理模块
# from common.exception_handler import log_info, log_error, safe, db_safe, safe_protect
from common.log_handler import (
    # 日志记录函数
    log_trace, log_debug, log_info, log_success, 
    log_warning, log_error, log_critical,
    # 安全执行
    safe, db_safe,
    # 装饰器
    safe_protect, catch,
    # Logger 实例
    get_logger
)
logger = get_logger(__file__)

@require_role('admin')
@safe_protect(name="角色管理页面", error_msg="角色管理页面加载失败，请稍后重试")
def role_management_page_content():
    """角色管理页面内容 - 仅管理员可访问"""    
    # 页面标题
    with ui.column().classes('w-full mb-6'):
        ui.label('角色管理').classes('text-4xl font-bold text-purple-800 dark:text-purple-200 mb-2')
        ui.label('管理系统角色和权限分配，支持用户关联管理').classes('text-lg text-gray-600 dark:text-gray-400')

    # 角色统计卡片
    def load_role_statistics():
        """加载角色统计数据"""
        role_stats = detached_manager.get_role_statistics()
        user_stats = detached_manager.get_user_statistics()
        
        return {
            **role_stats,
            'total_users': user_stats['total_users']
        }

    # 安全执行统计数据加载
    stats = safe(
        load_role_statistics,
        return_value={'total_roles': 0, 'active_roles': 0, 'system_roles': 0, 'total_users': 0},
        error_msg="角色统计数据加载失败"
    )

    # 统计卡片区域
    with ui.row().classes('w-full gap-6 mb-8'):
        with ui.card().classes('flex-1 p-6 bg-gradient-to-br from-purple-500 to-purple-600 text-white shadow-lg'):
            with ui.row().classes('items-center justify-between w-full'):
                with ui.column().classes('gap-1'):
                    ui.label('总角色数').classes('text-sm opacity-90 font-medium')
                    ui.label(str(stats['total_roles'])).classes('text-3xl font-bold')
                ui.icon('group').classes('text-4xl opacity-80')

        with ui.card().classes('flex-1 p-6 bg-gradient-to-br from-green-500 to-green-600 text-white shadow-lg'):
            with ui.row().classes('items-center justify-between w-full'):
                with ui.column().classes('gap-1'):
                    ui.label('活跃角色').classes('text-sm opacity-90 font-medium')
                    ui.label(str(stats['active_roles'])).classes('text-3xl font-bold')
                ui.icon('check_circle').classes('text-4xl opacity-80')

        with ui.card().classes('flex-1 p-6 bg-gradient-to-br from-blue-500 to-blue-600 text-white shadow-lg'):
            with ui.row().classes('items-center justify-between w-full'):
                with ui.column().classes('gap-1'):
                    ui.label('系统角色').classes('text-sm opacity-90 font-medium')
                    ui.label(str(stats['system_roles'])).classes('text-3xl font-bold')
                ui.icon('admin_panel_settings').classes('text-4xl opacity-80')

        with ui.card().classes('flex-1 p-6 bg-gradient-to-br from-orange-500 to-orange-600 text-white shadow-lg'):
            with ui.row().classes('items-center justify-between w-full'):
                with ui.column().classes('gap-1'):
                    ui.label('用户总数').classes('text-sm opacity-90 font-medium')
                    ui.label(str(stats['total_users'])).classes('text-3xl font-bold')
                ui.icon('people').classes('text-4xl opacity-80')

    # 角色列表容器
    with ui.column().classes('w-full'):
        ui.label('角色列表').classes('text-xl font-bold text-gray-800 dark:text-gray-200 mb-3')
        
        # 操作按钮区域
        with ui.row().classes('w-full gap-2 mb-4'):
            ui.button('创建新角色', icon='add', 
                    on_click=lambda: safe(add_role_dialog)).classes('bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 text-sm font-medium shadow-md')
            ui.button('角色模板', icon='content_copy', 
                    on_click=lambda: safe(role_template_dialog)).classes('bg-green-600 hover:bg-green-700 text-white px-4 py-2 text-sm font-medium shadow-md')
            ui.button('批量操作', icon='checklist', 
                    on_click=lambda: ui.notify('批量操作功能开发中...', type='info')).classes('bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 text-sm font-medium shadow-md')
            ui.button('导出数据', icon='download', 
                    on_click=lambda: safe(export_roles)).classes('bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 text-sm font-medium shadow-md')
        
        # 搜索区域
        def handle_search():
            """处理搜索事件"""
            safe(load_roles)
        
        def handle_input_search():
            """处理输入时的搜索事件 - 带延迟"""
            ui.timer(0.5, lambda: safe(load_roles), once=True)
        
        def reset_search():
            """重置搜索"""
            search_input.value = ''
            safe(load_roles)

        with ui.row().classes('w-full gap-2 mb-4 items-end'):
            search_input = ui.input(
                '搜索角色', 
                placeholder='输入角色名称进行模糊查找...',
                value=''
            ).classes('flex-1').props('outlined clearable')
            search_input.props('prepend-icon=search')
            
            ui.button('搜索', icon='search', 
                     on_click=handle_search).classes('bg-blue-600 hover:bg-blue-700 text-white px-4 py-2')
            ui.button('重置', icon='clear', 
                     on_click=reset_search).classes('bg-gray-500 hover:bg-gray-600 text-white px-4 py-2')

        # 监听搜索输入变化
        search_input.on('keyup.enter', handle_search)
        search_input.on('input', handle_input_search)

        # 角色卡片容器
        roles_container = ui.column().classes('w-full gap-4')

    def load_roles():
        """加载角色列表"""        
        # 清空现有内容
        roles_container.clear()
        # 获取搜索关键词
        search_term = search_input.value.strip() if hasattr(search_input, 'value') else ''        
        # 获取角色数据
        all_roles = get_roles_safe()
        
        # 过滤角色
        if search_term:
            filtered_roles = [
                role for role in all_roles 
                if search_term.lower() in (role.name or '').lower() 
                or search_term.lower() in (role.display_name or '').lower()
                or search_term.lower() in (role.description or '').lower()
            ]
        else:
            filtered_roles = all_roles
                
        with roles_container:
            if not filtered_roles:
                # 无数据提示
                with ui.card().classes('w-full p-8 text-center bg-gray-50 dark:bg-gray-700'):
                    if search_term:
                        ui.icon('search_off').classes('text-6xl text-gray-400 mb-4')
                        ui.label(f'未找到匹配 "{search_term}" 的角色').classes('text-xl font-medium text-gray-500 dark:text-gray-400')
                        ui.button('清空搜索', icon='clear', 
                                on_click=reset_search).classes('mt-4 bg-blue-500 text-white')
                    else:
                        ui.icon('group_off').classes('text-6xl text-gray-400 mb-4')
                        ui.label('暂无角色数据').classes('text-xl font-medium text-gray-500 dark:text-gray-400')
                        ui.button('创建新角色', icon='add',
                                on_click=lambda: safe(add_role_dialog)).classes('mt-4 bg-green-500 text-white')
                return

            # 创建角色卡片
            for i in range(0, len(filtered_roles), 2):
                with ui.row().classes('w-full gap-3'):
                    # 第一个角色卡片
                    with ui.column().classes('flex-1'):
                        create_role_card(filtered_roles[i])
                    
                    # 第二个角色卡片（如果存在）
                    if i + 1 < len(filtered_roles):
                        with ui.column().classes('flex-1'):
                            create_role_card(filtered_roles[i + 1])
                    else:
                        # 如果是奇数个角色，添加占位符保持布局
                        ui.column().classes('flex-1')

    def create_role_card(role_data: DetachedRole):
        """创建单个角色卡片"""
        # 确定角色颜色主题
        if role_data.name == 'admin':
            card_theme = 'border-l-4 border-red-500 bg-red-50 dark:bg-red-900/10'
            badge_theme = 'bg-red-100 text-red-800 dark:bg-red-800 dark:text-red-200'
            icon_theme = 'text-red-600 dark:text-red-400'
        elif role_data.name == 'user':
            card_theme = 'border-l-4 border-green-500 bg-green-50 dark:bg-green-900/10'
            badge_theme = 'bg-green-100 text-green-800 dark:bg-green-800 dark:text-green-200'
            icon_theme = 'text-green-600 dark:text-green-400'
        else:
            card_theme = 'border-l-4 border-blue-500 bg-blue-50 dark:bg-blue-900/10'
            badge_theme = 'bg-blue-100 text-blue-800 dark:bg-blue-800 dark:text-blue-200'
            icon_theme = 'text-blue-600 dark:text-blue-400'

        with ui.card().classes(f'w-full {card_theme} shadow-md hover:shadow-lg transition-shadow duration-300'):
            with ui.row().classes('w-full p-4 gap-4'):
                # 左侧：角色基本信息
                with ui.column().classes('flex-none w-72 gap-2'):
                    # 角色头部信息
                    with ui.row().classes('items-center gap-3 mb-2'):
                        ui.icon('security').classes(f'text-3xl {icon_theme}')
                        with ui.column().classes('gap-0'):
                            ui.label(role_data.display_name or role_data.name).classes('text-xl font-bold text-gray-800 dark:text-gray-200')
                            ui.label(f'角色代码: {role_data.name}').classes('text-xs text-gray-500 dark:text-gray-400')

                    # 角色标签
                    with ui.row().classes('gap-1 flex-wrap mb-2'):
                        if role_data.is_system:
                            ui.chip('系统角色', icon='lock').classes('bg-orange-100 text-orange-800 dark:bg-orange-800 dark:text-orange-200 text-xs py-1 px-2')
                        else:
                            ui.chip('自定义', icon='edit').classes(f'{badge_theme} text-xs py-1 px-2')
                        
                        if role_data.is_active:
                            ui.chip('已启用', icon='check_circle').classes('bg-green-100 text-green-800 dark:bg-green-800 dark:text-green-200 text-xs py-1 px-2')
                        else:
                            ui.chip('已禁用', icon='block').classes('bg-red-100 text-red-800 dark:bg-red-800 dark:text-red-200 text-xs py-1 px-2')

                    # 角色描述
                    ui.label('描述:').classes('text-xs font-medium text-gray-600 dark:text-gray-400')
                    ui.label(role_data.description or '暂无描述').classes('text-sm text-gray-700 dark:text-gray-300 leading-tight min-h-[1.5rem] line-clamp-2')

                    # 统计信息
                    with ui.row().classes('gap-2 mt-2'):
                        with ui.card().classes('flex-1 p-2 bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600'):
                            ui.label('用户数').classes('text-xs text-gray-500 dark:text-gray-400')
                            ui.label(str(role_data.user_count)).classes('text-lg font-bold text-blue-600 dark:text-blue-400')
                        
                        with ui.card().classes('flex-1 p-2 bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600'):
                            ui.label('权限数').classes('text-xs text-gray-500 dark:text-gray-400')
                            ui.label(str(len(role_data.permissions))).classes('text-lg font-bold text-green-600 dark:text-green-400')

                # 右侧：用户管理区域
                with ui.column().classes('flex-1 gap-2'):
                    # 用户列表标题和操作按钮 - 修改这里，添加批量关联按钮
                    with ui.row().classes('items-center justify-between w-full mt-2'):
                        ui.label(f'关联用户 ({role_data.user_count})').classes('text-lg font-bold text-gray-800 dark:text-gray-200')
                        with ui.row().classes('gap-1'):
                            ui.button('添加用户', icon='person_add',
                                     on_click=lambda r=role_data: safe(lambda: add_users_to_role_dialog(r))).classes('flex-1 bg-green-600 hover:bg-green-700 text-white px-3 py-1 text-xs')
                            ui.button('批量移除', icon='person_remove',
                                     on_click=lambda r=role_data: safe(lambda: batch_remove_users_dialog(r))).classes('flex-1  bg-red-600 hover:bg-red-700 text-white px-3 py-1 text-xs')
                            # 新增批量关联按钮
                            ui.button('批量关联', icon='upload_file',
                                     on_click=lambda r=role_data: safe(lambda: batch_associate_users_dialog(r))).classes('flex-1  bg-purple-600 hover:bg-purple-700 text-white px-3 py-1 text-xs')

                    # 用户列表区域
                    with ui.card().classes('w-full p-3 bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 min-h-[120px] max-h-[160px] overflow-auto'):
                        if role_data.users:
                            with ui.column().classes('w-full gap-1'):
                                for username in role_data.users:
                                    with ui.row().classes('items-center justify-between w-full p-2 bg-gray-50 dark:bg-gray-600 rounded hover:bg-gray-100 dark:hover:bg-gray-500 transition-colors'):
                                        with ui.row().classes('items-center gap-2'):
                                            ui.icon('person').classes('text-blue-500 text-lg')
                                            ui.label(username).classes('text-sm text-gray-800 dark:text-gray-200 font-medium')
                                        
                                        if not role_data.is_system:
                                            ui.button(icon='close',
                                                     on_click=lambda u=username, r=role_data: safe(lambda: remove_user_from_role(u, r))).props('flat round color=red').classes('w-6 h-6')
                        else:
                            with ui.column().classes('w-full items-center justify-center py-4'):
                                ui.icon('people_outline').classes('text-3xl text-gray-400 mb-1')
                                ui.label('无关联用户').classes('text-sm text-gray-500 dark:text-gray-400')
                                ui.label('点击"添加用户"分配用户').classes('text-xs text-gray-400 dark:text-gray-500')

                    # 角色操作按钮
                    with ui.row().classes('gap-1 w-full mt-2'):
                        ui.button('查看', icon='visibility',
                                 on_click=lambda r=role_data: safe(lambda: view_role_dialog(r))).classes('flex-1 bg-blue-600 hover:bg-blue-700 text-white py-1 text-xs')
                        
                        if not role_data.is_system:
                            ui.button('编辑', icon='edit',
                                     on_click=lambda r=role_data: safe(lambda: edit_role_dialog(r))).classes('flex-1 bg-green-600 hover:bg-green-700 text-white py-1 text-xs')
                            ui.button('删除', icon='delete',
                                     on_click=lambda r=role_data: safe(lambda: delete_role_dialog(r))).classes('flex-1 bg-red-600 hover:bg-red-700 text-white py-1 text-xs')
                        else:
                            ui.button('系统角色', icon='lock',
                                     on_click=lambda: ui.notify('系统角色不可编辑', type='info')).classes('flex-1 bg-gray-400 text-white py-1 text-xs').disable()

    # ==================== 新增：批量关联用户对话框 ====================
    @safe_protect(name="批量关联用户")
    def batch_associate_users_dialog(role_data: DetachedRole):
        """批量关联用户对话框 - 通过上传文件"""
        log_info(f"打开批量关联用户对话框: {role_data.name}")
        
        with ui.dialog() as dialog, ui.card().classes('w-[700px] max-h-[80vh]'):
            dialog.open()
            
            # 对话框标题
            with ui.row().classes('w-full items-center justify-between p-4 bg-gradient-to-r from-purple-500 to-purple-600 text-white rounded-t-lg -m-6 mb-6'):
                ui.label(f'批量关联用户到角色 "{role_data.display_name or role_data.name}"').classes('text-xl font-bold')
                ui.button(icon='close', on_click=dialog.close).props('flat round color=white').classes('ml-auto')

            # 说明信息
            with ui.card().classes('w-full mb-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-700'):
                ui.label('操作说明').classes('font-bold mb-2 text-blue-800 dark:text-blue-200')
                ui.label('1. 上传包含用户信息的文本文件（支持 .txt 和 .csv 格式）').classes('text-sm text-blue-700 dark:text-blue-300')
                ui.label('2. 文件每行包含一个用户名或注册邮箱').classes('text-sm text-blue-700 dark:text-blue-300')
                ui.label('3. 系统将自动识别用户并建立角色关联').classes('text-sm text-blue-700 dark:text-blue-300')
                ui.label('4. 无法识别的用户将被跳过').classes('text-sm text-blue-700 dark:text-blue-300')

            # 文件示例
            with ui.expansion('查看文件格式示例', icon='info').classes('w-full mb-4'):
                with ui.card().classes('w-full bg-gray-100 dark:bg-gray-800 p-4'):
                    ui.label('文件内容示例：').classes('font-medium mb-2')
                    ui.code('''admin
user1@example.com
editor
test.user@company.com
manager
developer@team.com''').classes('w-full text-sm')

            # 文件上传区域
            upload_result = {'file_content': None, 'filename': None}
            
            async def handle_file_upload(file):
                """处理文件上传"""
                log_info(f"开始处理上传文件: {file.name}")
                
                try:
                    # 检查文件类型
                    allowed_extensions = ['.txt', '.csv']
                    file_extension = '.' + file.name.split('.')[-1].lower()
                    
                    if file_extension not in allowed_extensions:
                        ui.notify(f'不支持的文件格式。仅支持: {", ".join(allowed_extensions)}', type='warning')
                        return
                    
                    # 读取文件内容
                    content = file.content.read()
                    
                    # 尝试不同编码解码
                    try:
                        text_content = content.decode('utf-8')
                    except UnicodeDecodeError:
                        try:
                            text_content = content.decode('gbk')
                        except UnicodeDecodeError:
                            text_content = content.decode('utf-8', errors='ignore')
                    
                    upload_result['file_content'] = text_content
                    upload_result['filename'] = file.name
                    
                    # 预览文件内容
                    lines = [line.strip() for line in text_content.splitlines() if line.strip()]
                    
                    upload_status.clear()
                    with upload_status:
                        ui.label(f'✅ 文件上传成功: {file.name}').classes('text-green-600 font-medium')
                        ui.label(f'📄 发现 {len(lines)} 行用户数据').classes('text-gray-600 text-sm')
                        
                        # 显示前几行预览
                        if lines:
                            ui.label('📋 文件内容预览（前5行）:').classes('text-gray-700 font-medium mt-2 mb-1')
                            preview_lines = lines[:5]
                            for i, line in enumerate(preview_lines, 1):
                                ui.label(f'{i}. {line}').classes('text-sm text-gray-600 ml-4')
                            
                            if len(lines) > 5:
                                ui.label(f'... 还有 {len(lines) - 5} 行').classes('text-sm text-gray-500 ml-4')
                    
                    log_info(f"文件上传处理完成: {file.name}, 共{len(lines)}行数据")
                    
                except Exception as e:
                    log_error(f"文件上传处理失败: {file.name}", exception=e)
                    upload_status.clear()
                    with upload_status:
                        ui.label('❌ 文件处理失败，请检查文件格式').classes('text-red-600 font-medium')

            with ui.card().classes('w-full p-4 border-2 border-dashed border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-700'):
                ui.label('📁 选择文件上传').classes('text-lg font-medium mb-2 text-center w-full')
                ui.upload(
                    on_upload=handle_file_upload,
                    max_file_size=1024*1024*5,  # 5MB 限制
                    multiple=False
                ).classes('w-full').props('accept=".txt,.csv"')

            # 上传状态显示区域
            upload_status = ui.column().classes('w-full mb-4')

            def process_batch_association():
                """处理批量关联"""
                if not upload_result['file_content']:
                    ui.notify('请先上传用户文件', type='warning')
                    return

                log_info(f"开始批量关联用户到角色: {role_data.name}")
                
                try:
                    # 解析用户列表
                    lines = [line.strip() for line in upload_result['file_content'].splitlines() if line.strip()]
                    
                    if not lines:
                        ui.notify('文件中没有找到有效的用户数据', type='warning')
                        return

                    # 统计变量
                    success_count = 0
                    skip_count = 0
                    error_users = []
                    
                    with db_safe(f"批量关联用户到角色 {role_data.name}") as db:
                        # 获取角色对象
                        role = db.query(Role).filter(Role.name == role_data.name).first()
                        if not role:
                            ui.notify('角色不存在', type='error')
                            return

                        for user_identifier in lines:
                            try:
                                # 尝试通过用户名或邮箱查找用户
                                user = db.query(User).filter(
                                    (User.username == user_identifier) | 
                                    (User.email == user_identifier)
                                ).first()
                                
                                if user:
                                    # 检查用户是否已经拥有该角色
                                    if role not in user.roles:
                                        user.roles.append(role)
                                        success_count += 1
                                        log_info(f"成功关联用户 {user_identifier} 到角色 {role_data.name}")
                                    else:
                                        skip_count += 1
                                        log_info(f"用户 {user_identifier} 已拥有角色 {role_data.name}，跳过")
                                else:
                                    error_users.append(user_identifier)
                                    log_error(f"未找到用户: {user_identifier}")
                                    
                            except Exception as e:
                                error_users.append(user_identifier)
                                log_error(f"处理用户 {user_identifier} 时出错", exception=e)

                    # 显示处理结果
                    total_processed = len(lines)
                    
                    result_message = f'''批量关联完成！
📊 处理结果：
✅ 成功关联: {success_count} 个用户
⏭️  已存在跳过: {skip_count} 个用户
❌ 无法识别: {len(error_users)} 个用户
📝 总计处理: {total_processed} 条记录'''

                    # 显示详细结果对话框
                    with ui.dialog() as result_dialog, ui.card().classes('w-[600px]'):
                        result_dialog.open()
                        
                        ui.label('批量关联结果').classes('text-xl font-bold mb-4 text-purple-800 dark:text-purple-200')
                        
                        # 结果统计
                        with ui.row().classes('w-full gap-4 mb-4'):
                            with ui.card().classes('flex-1 p-3 bg-green-50 dark:bg-green-900/20'):
                                ui.label('成功关联').classes('text-sm text-green-600 dark:text-green-400')
                                ui.label(str(success_count)).classes('text-2xl font-bold text-green-700 dark:text-green-300')
                            
                            with ui.card().classes('flex-1 p-3 bg-yellow-50 dark:bg-yellow-900/20'):
                                ui.label('已存在跳过').classes('text-sm text-yellow-600 dark:text-yellow-400')
                                ui.label(str(skip_count)).classes('text-2xl font-bold text-yellow-700 dark:text-yellow-300')
                            
                            with ui.card().classes('flex-1 p-3 bg-red-50 dark:bg-red-900/20'):
                                ui.label('无法识别').classes('text-sm text-red-600 dark:text-red-400')
                                ui.label(str(len(error_users))).classes('text-2xl font-bold text-red-700 dark:text-red-300')

                        # 详细信息
                        ui.label(result_message).classes('text-sm text-gray-700 dark:text-gray-300 whitespace-pre-line mb-4')
                        
                        # 显示无法识别的用户
                        if error_users:
                            with ui.expansion('查看无法识别的用户', icon='error').classes('w-full mb-4'):
                                with ui.column().classes('gap-1 max-h-40 overflow-auto'):
                                    for user in error_users:
                                        ui.label(f'• {user}').classes('text-sm text-red-600 dark:text-red-400')

                        with ui.row().classes('w-full justify-end gap-2'):
                            ui.button('确定', on_click=result_dialog.close).classes('bg-purple-600 hover:bg-purple-700 text-white')

                    # 显示成功通知
                    if success_count > 0:
                        ui.notify(f'成功关联 {success_count} 个用户到角色 {role_data.name}', type='positive')
                        dialog.close()
                        safe(load_roles)  # 重新加载角色列表
                    else:
                        ui.notify('没有新用户被关联', type='info')

                    log_info(f"批量关联完成: 角色={role_data.name}, 成功={success_count}, 跳过={skip_count}, 错误={len(error_users)}")

                except Exception as e:
                    log_error(f"批量关联用户失败: {role_data.name}", exception=e)
                    ui.notify('批量关联失败，请稍后重试', type='negative')

            # 操作按钮
            with ui.row().classes('w-full justify-end gap-3 mt-6'):
                ui.button('取消', on_click=dialog.close).classes('px-6 py-2 bg-gray-500 hover:bg-gray-600 text-white')
                ui.button('开始关联', icon='link', on_click=lambda: safe(process_batch_association)).classes('px-6 py-2 bg-purple-600 hover:bg-purple-700 text-white')

    # ==================== 现有功能保持不变 ====================
    @safe_protect(name="添加用户到角色")
    def add_users_to_role_dialog(role_data: DetachedRole):
        """添加用户到角色对话框"""
        log_info(f"打开添加用户到角色对话框: {role_data.name}")
        
        with ui.dialog() as dialog, ui.card().classes('w-[600px] max-h-[80vh]'):
            dialog.open()
            
            # 对话框标题
            with ui.row().classes('w-full items-center justify-between p-4 bg-gradient-to-r from-green-500 to-green-600 text-white rounded-t-lg -m-6 mb-6'):
                ui.label(f'为角色 "{role_data.display_name or role_data.name}" 添加用户').classes('text-xl font-bold')
                ui.button(icon='close', on_click=dialog.close).props('flat round color=white').classes('ml-auto')

            # 获取所有用户
            all_users = get_users_safe()
            available_users = [user for user in all_users if user.username not in role_data.users]

            if not available_users:
                ui.label('所有用户都已关联到此角色').classes('text-center text-gray-500 dark:text-gray-400 py-8')
                with ui.row().classes('w-full justify-center mt-4'):
                    ui.button('关闭', on_click=dialog.close).classes('bg-gray-500 text-white')
                return

            ui.label(f'选择要添加到角色的用户（可添加 {len(available_users)} 个用户）：').classes('text-lg font-medium mb-4')

            # 用户选择列表
            selected_users = set()
            
            # 搜索框
            search_input = ui.input('搜索用户', placeholder='输入用户名或邮箱进行搜索...').classes('w-full mb-4').props('outlined clearable')
            
            # 用户列表容器
            user_list_container = ui.column().classes('w-full gap-2 max-h-80 overflow-auto')

            def update_user_list():
                """更新用户列表显示"""
                search_term = search_input.value.lower().strip() if search_input.value else ''
                
                # 过滤用户
                filtered_users = [
                    user for user in available_users
                    if not search_term or 
                    search_term in user.username.lower() or 
                    search_term in (user.email or '').lower()
                ]
                
                user_list_container.clear()
                with user_list_container:
                    if not filtered_users:
                        ui.label('没有找到匹配的用户').classes('text-center text-gray-500 py-4')
                        return
                    
                    for user in filtered_users:
                        with ui.row().classes('items-center gap-3 p-3 bg-green-50 dark:bg-green-900/20 rounded-lg hover:bg-green-100 dark:hover:bg-green-900/30 transition-colors'):
                            checkbox = ui.checkbox(
                                on_change=lambda e, u=user.username: selected_users.add(u) if e.value else selected_users.discard(u)
                            ).classes('mr-2')
                            
                            ui.icon('person').classes('text-green-500 text-xl')
                            
                            with ui.column().classes('flex-1 gap-1'):
                                ui.label(user.username).classes('font-medium text-gray-800 dark:text-gray-200')
                                if user.email:
                                    ui.label(user.email).classes('text-sm text-gray-600 dark:text-gray-400')
                            
                            # 用户状态标签
                            if user.is_active:
                                ui.chip('活跃', icon='check_circle').classes('bg-green-100 text-green-800 dark:bg-green-800 dark:text-green-200 text-xs')
                            else:
                                ui.chip('禁用', icon='block').classes('bg-red-100 text-red-800 dark:bg-red-800 dark:text-red-200 text-xs')

            # 监听搜索输入
            search_input.on('input', lambda: ui.timer(0.3, update_user_list, once=True))
            
            # 初始加载用户列表
            update_user_list()

            def confirm_add_users():
                """确认添加用户"""
                if not selected_users:
                    ui.notify('请选择要添加的用户', type='warning')
                    return

                try:
                    added_count = 0
                    with db_safe(f"为角色 {role_data.name} 添加用户") as db:
                        role = db.query(Role).filter(Role.name == role_data.name).first()
                        if not role:
                            ui.notify('角色不存在', type='error')
                            return

                        for username in selected_users:
                            user = db.query(User).filter(User.username == username).first()
                            if user and role not in user.roles:
                                user.roles.append(role)
                                added_count += 1

                    if added_count > 0:
                        log_info(f"成功为角色 {role_data.name} 添加了 {added_count} 个用户")
                        ui.notify(f'成功添加 {added_count} 个用户到角色 {role_data.name}', type='positive')
                        dialog.close()
                        safe(load_roles)  # 重新加载角色列表
                    else:
                        ui.notify('没有用户被添加', type='info')

                except Exception as e:
                    log_error(f"添加用户到角色失败: {role_data.name}", exception=e)
                    ui.notify('添加用户失败，请稍后重试', type='negative')

            # 操作按钮
            with ui.row().classes('w-full justify-end gap-3 mt-6'):
                ui.button('取消', on_click=dialog.close).classes('px-6 py-2 bg-gray-500 hover:bg-gray-600 text-white')
                ui.button('确认添加', on_click=lambda: safe(confirm_add_users)).classes('px-6 py-2 bg-green-600 hover:bg-green-700 text-white')

    @safe_protect(name="批量移除用户")
    def batch_remove_users_dialog(role_data: DetachedRole):
        """批量移除用户对话框"""
        log_info(f"打开批量移除用户对话框: {role_data.name}")
        
        if not role_data.users:
            ui.notify('此角色暂无用户可移除', type='info')
            return

        if role_data.is_system:
            ui.notify('系统角色不允许移除用户', type='warning')
            return

        with ui.dialog() as dialog, ui.card().classes('w-[500px]'):
            dialog.open()
            
            # 对话框标题
            with ui.row().classes('w-full items-center justify-between p-4 bg-gradient-to-r from-red-500 to-red-600 text-white rounded-t-lg -m-6 mb-6'):
                ui.label(f'从角色 "{role_data.display_name or role_data.name}" 批量移除用户').classes('text-xl font-bold')
                ui.button(icon='close', on_click=dialog.close).props('flat round color=white').classes('ml-auto')

            ui.label('选择要移除的用户：').classes('text-lg font-medium mb-4')
            
            # 用户选择列表
            selected_users = set()
            with ui.column().classes('w-full gap-2 max-h-80 overflow-auto'):
                for username in role_data.users:
                    with ui.row().classes('items-center gap-3 p-3 bg-red-50 dark:bg-red-900/20 rounded-lg'):
                        checkbox = ui.checkbox(
                            on_change=lambda e, u=username: selected_users.add(u) if e.value else selected_users.discard(u)
                        ).classes('mr-2')
                        
                        ui.icon('person').classes('text-red-500 text-xl')
                        ui.label(username).classes('font-medium text-gray-800 dark:text-gray-200')

            def confirm_remove_users():
                """确认移除用户"""
                if not selected_users:
                    ui.notify('请选择要移除的用户', type='warning')
                    return

                try:
                    removed_count = 0
                    with db_safe(f"从角色 {role_data.name} 移除用户") as db:
                        role = db.query(Role).filter(Role.name == role_data.name).first()
                        if not role:
                            ui.notify('角色不存在', type='error')
                            return

                        for username in selected_users:
                            user = db.query(User).filter(User.username == username).first()
                            if user and role in user.roles:
                                user.roles.remove(role)
                                removed_count += 1

                    if removed_count > 0:
                        log_info(f"成功从角色 {role_data.name} 移除了 {removed_count} 个用户")
                        ui.notify(f'成功从角色 {role_data.name} 移除 {removed_count} 个用户', type='positive')
                        dialog.close()
                        safe(load_roles)  # 重新加载角色列表
                    else:
                        ui.notify('没有用户被移除', type='info')

                except Exception as e:
                    log_error(f"从角色移除用户失败: {role_data.name}", exception=e)
                    ui.notify('移除用户失败，请稍后重试', type='negative')

            # 操作按钮
            with ui.row().classes('w-full justify-end gap-3 mt-6'):
                ui.button('取消', on_click=dialog.close).classes('px-6 py-2 bg-gray-500 hover:bg-gray-600 text-white')
                ui.button('确认移除', on_click=lambda: safe(confirm_remove_users)).classes('px-6 py-2 bg-red-600 hover:bg-red-700 text-white')

    @safe_protect(name="移除单个用户")
    def remove_user_from_role(username: str, role_data: DetachedRole):
        """从角色中移除单个用户"""
        log_info(f"移除用户 {username} 从角色 {role_data.name}")
        
        try:
            with db_safe(f"移除用户 {username} 从角色 {role_data.name}") as db:
                user = db.query(User).filter(User.username == username).first()
                role = db.query(Role).filter(Role.name == role_data.name).first()
                
                if user and role and role in user.roles:
                    user.roles.remove(role)
                    log_info(f"成功移除用户 {username} 从角色 {role_data.name}")
                    ui.notify(f'用户 {username} 从角色 {role_data.name} 中移除', type='positive')
                    safe(load_roles)  # 重新加载角色列表
                else:
                    ui.notify('用户不在此角色中', type='info')

        except Exception as e:
            log_error(f"移除用户角色失败: {username} - {role_data.name}", exception=e)
            ui.notify('移除失败，请稍后重试', type='negative')

    # 其他功能函数（查看、编辑、删除角色等）保持原有逻辑
    @safe_protect(name="查看角色详情")
    def view_role_dialog(role_data: DetachedRole):
        """查看角色详情对话框"""
        log_info(f"查看角色详情: {role_data.name}")
        
        with ui.dialog() as dialog, ui.card().classes('w-[700px] max-h-[80vh] overflow-auto'):
            dialog.open()
            
            # 标题区域
            with ui.row().classes('w-full items-center justify-between p-4 bg-gradient-to-r from-purple-500 to-purple-600 text-white rounded-t-lg -m-6 mb-6'):
                ui.label(f'角色详情: {role_data.display_name or role_data.name}').classes('text-xl font-bold')
                ui.button(icon='close', on_click=dialog.close).props('flat round color=white').classes('ml-auto')

            # 基本信息
            with ui.card().classes('w-full mb-4 bg-gray-50 dark:bg-gray-700'):
                ui.label('基本信息').classes('font-bold mb-3 text-gray-800 dark:text-gray-200')
                
                info_items = [
                    ('角色名称', role_data.name),
                    ('显示名称', role_data.display_name or "无"),
                    ('描述', role_data.description or "无"),
                    ('状态', "活跃" if role_data.is_active else "禁用"),
                    ('类型', "系统角色" if role_data.is_system else "自定义角色"),
                    ('创建时间', role_data.created_at.strftime('%Y-%m-%d %H:%M:%S') if role_data.created_at else '未知'),
                    ('更新时间', role_data.updated_at.strftime('%Y-%m-%d %H:%M:%S') if role_data.updated_at else '未知')
                ]
                
                for label, value in info_items:
                    with ui.row().classes('items-center gap-4 py-1'):
                        ui.label(f'{label}:').classes('text-sm font-medium text-gray-600 dark:text-gray-400 w-20')
                        ui.label(str(value)).classes('text-sm text-gray-800 dark:text-gray-200')

            # 用户列表
            if role_data.users:
                with ui.card().classes('w-full mb-4 bg-blue-50 dark:bg-blue-900/20'):
                    ui.label(f'拥有此角色的用户 ({len(role_data.users)})').classes('font-bold mb-3 text-blue-800 dark:text-blue-200')
                    
                    with ui.column().classes('gap-2 max-h-40 overflow-auto'):
                        for username in role_data.users:
                            with ui.row().classes('items-center gap-3 p-2 bg-white dark:bg-gray-700 rounded'):
                                ui.icon('person').classes('text-blue-500')
                                ui.label(username).classes('text-gray-800 dark:text-gray-200')

            # 权限列表
            if role_data.permissions:
                with ui.card().classes('w-full bg-green-50 dark:bg-green-900/20'):
                    ui.label(f'角色权限 ({len(role_data.permissions)})').classes('font-bold mb-3 text-green-800 dark:text-green-200')
                    
                    with ui.column().classes('gap-1 max-h-40 overflow-auto'):
                        for permission in role_data.permissions:
                            with ui.row().classes('items-center gap-2 p-1'):
                                ui.icon('security').classes('text-green-500 text-sm')
                                ui.label(permission).classes('text-sm text-gray-800 dark:text-gray-200')

            with ui.row().classes('w-full justify-end gap-2 mt-6'):
                ui.button('关闭', on_click=dialog.close).classes('bg-gray-500 text-white')

    @safe_protect(name="编辑角色")
    def edit_role_dialog(role_data: DetachedRole):
        """编辑角色对话框"""
        log_info(f"编辑角色: {role_data.name}")
        
        if role_data.is_system:
            ui.notify('系统角色不允许编辑', type='warning')
            return

        with ui.dialog() as dialog, ui.card().classes('w-96'):
            dialog.open()
            ui.label(f'编辑角色: {role_data.name}').classes('text-lg font-semibold')

            # 表单字段（名称不可编辑）
            ui.label('角色名称（不可修改）').classes('text-sm text-gray-600 mt-4')
            ui.input(value=role_data.name).classes('w-full').disable()
            
            display_name_input = ui.input('显示名称', value=role_data.display_name or '').classes('w-full')
            description_input = ui.textarea('描述', value=role_data.description or '').classes('w-full')
            is_active_switch = ui.switch('启用角色', value=role_data.is_active).classes('mt-4')

            def save_role():
                """保存角色修改"""
                log_info(f"保存角色修改: {role_data.name}")
                
                update_data = {
                    'name': role_data.name,  # 保持原名称
                    'display_name': display_name_input.value.strip() or None,
                    'description': description_input.value.strip() or None,
                    'is_active': is_active_switch.value
                }
                
                success = update_role_safe(role_data.id, update_data)
                
                if success:
                    log_info(f"角色修改成功: {update_data['name']}")
                    ui.notify('角色信息已更新', type='positive')
                    dialog.close()
                    safe(load_roles)
                else:
                    log_error(f"保存角色修改失败: {role_data.name}")
                    ui.notify('保存失败，角色名称可能已存在', type='negative')

            with ui.row().classes('w-full justify-end gap-2 mt-6'):
                ui.button('取消', on_click=dialog.close).classes('bg-gray-500 text-white')
                ui.button('保存', on_click=lambda: safe(save_role)).classes('bg-blue-500 text-white')

    @safe_protect(name="添加角色对话框")
    def add_role_dialog():
        """添加角色对话框"""
        log_info("打开添加角色对话框")
        
        with ui.dialog() as dialog, ui.card().classes('w-96'):
            dialog.open()
            ui.label('创建新角色').classes('text-lg font-semibold')

            # 表单字段
            name_input = ui.input('角色名称', placeholder='如: editor').classes('w-full')
            display_name_input = ui.input('显示名称', placeholder='如: 编辑员').classes('w-full')
            description_input = ui.textarea('描述', placeholder='角色功能描述').classes('w-full')
            is_active_switch = ui.switch('启用角色', value=True).classes('mt-4')

            def save_new_role():
                """保存新角色"""
                log_info("开始创建新角色")
                
                if not name_input.value.strip():
                    ui.notify('角色名称不能为空', type='warning')
                    return

                # 使用安全的创建方法
                role_id = create_role_safe(
                    name=name_input.value.strip(),
                    display_name=display_name_input.value.strip() or None,
                    description=description_input.value.strip() or None,
                    is_active=is_active_switch.value
                )
                
                if role_id:
                    log_info(f"新角色创建成功: {name_input.value} (ID: {role_id})")
                    ui.notify(f'角色 {display_name_input.value or name_input.value} 创建成功', type='positive')
                    dialog.close()
                    safe(load_roles)
                else:
                    log_error(f"创建角色失败: {name_input.value}")
                    ui.notify('角色创建失败，名称可能已存在', type='negative')

            with ui.row().classes('w-full justify-end gap-2 mt-6'):
                ui.button('取消', on_click=dialog.close).classes('bg-gray-500 text-white')
                ui.button('创建角色', on_click=lambda: safe(save_new_role)).classes('bg-blue-500 text-white')

    @safe_protect(name="删除角色对话框")
    def delete_role_dialog(role_data: DetachedRole):
        """删除角色对话框"""
        log_info(f"删除角色确认: {role_data.name}")
        
        if role_data.is_system:
            ui.notify('系统角色不允许删除', type='warning')
            return

        with ui.dialog() as dialog, ui.card().classes('w-96'):
            dialog.open()
            ui.label('确认删除角色').classes('text-lg font-semibold text-red-600')
            
            ui.label(f'您确定要删除角色 "{role_data.display_name or role_data.name}" 吗？').classes('mt-4')
            ui.label('此操作将移除所有用户的该角色关联，且不可撤销。').classes('text-sm text-red-500 mt-2')

            def confirm_delete():
                """确认删除角色"""
                success = delete_role_safe(role_data.id)
                
                if success:
                    log_info(f"角色删除成功: {role_data.name}")
                    ui.notify(f'角色 {role_data.name} 已删除', type='positive')
                    dialog.close()
                    safe(load_roles)
                else:
                    log_error(f"删除角色失败: {role_data.name}")
                    ui.notify('删除失败，请稍后重试', type='negative')

            with ui.row().classes('w-full justify-end gap-2 mt-6'):
                ui.button('取消', on_click=dialog.close).classes('bg-gray-500 text-white')
                ui.button('确认删除', on_click=lambda: safe(confirm_delete)).classes('bg-red-500 text-white')

    # 其他辅助功能
    @safe_protect(name="角色模板对话框")
    def role_template_dialog():
        """角色模板对话框"""
        ui.notify('角色模板功能开发中...', type='info')

    @safe_protect(name="导出角色数据")
    def export_roles():
        """导出角色数据"""
        ui.notify('导出功能开发中...', type='info')

    # 初始加载角色列表
    safe(load_roles)
    log_success("===角色管理页面加载完成===")
```

- **auth\pages\user_management_page.py**
```python
"""
用户管理页面 - 增强版：添加用户锁定状态显示和控制功能
"""
from nicegui import ui
from ..decorators import require_role
from ..auth_manager import auth_manager
from ..detached_helper import (
    detached_manager, 
    get_users_safe, 
    get_user_safe,
    get_roles_safe,
    DetachedUser
)
from ..utils import format_datetime, validate_email, validate_username
from ..models import User, Role
from ..database import get_db
import secrets
import string
from datetime import datetime, timedelta

# 导入异常处理模块
# from common.exception_handler import log_info, log_error, safe, db_safe, safe_protect
from common.log_handler import (
    # 日志记录函数
    log_trace, log_debug, log_info, log_success, 
    log_warning, log_error, log_critical,
    # 安全执行
    safe, db_safe,
    # 装饰器
    safe_protect, catch,
    # Logger 实例
    get_logger
)
# 获取绑定模块名称的logger
logger = get_logger(__file__)

@require_role('admin')
@safe_protect(name="用户管理页面", error_msg="用户管理页面加载失败，请稍后重试")
def user_management_page_content():
    """用户管理页面内容 - 仅管理员可访问"""
    # 页面标题
    with ui.column().classes('w-full mb-6'):
        ui.label('用户管理').classes('text-4xl font-bold text-indigo-800 dark:text-indigo-200 mb-2')
        ui.label('管理系统中的所有用户账户').classes('text-lg text-gray-600 dark:text-gray-400')

    # 用户统计卡片 - 添加锁定用户统计
    def load_user_statistics():
        """加载用户统计数据 - 增加锁定用户统计"""
        # 获取基础统计
        base_stats = detached_manager.get_user_statistics()
        # 计算锁定用户数量
        try:
            with db_safe("统计锁定用户") as db:
                current_time = datetime.now()
                locked_users_count = db.query(User).filter(
                    User.locked_until != None,
                    User.locked_until > current_time
                ).count()  
                base_stats['locked_users'] = locked_users_count    
        except Exception as e:
            log_error("获取锁定用户统计失败", exception=e)
            base_stats['locked_users'] = 0
        return base_stats
    # 安全执行统计数据加载
    stats = safe(
        load_user_statistics,
        return_value={'total_users': 0, 'active_users': 0, 'verified_users': 0, 'admin_users': 0, 'locked_users': 0},
        error_msg="用户统计数据加载失败"
    )

    with ui.row().classes('w-full gap-6 mb-8'):
        with ui.card().classes('flex-1 p-4 bg-gradient-to-r from-blue-500 to-blue-600 text-white'):
            with ui.row().classes('items-center justify-between w-full'):
                with ui.column().classes('gap-1'):
                    ui.label('总用户数').classes('text-sm opacity-90')
                    ui.label(str(stats['total_users'])).classes('text-3xl font-bold')
                ui.icon('people').classes('text-2xl opacity-80')

        with ui.card().classes('flex-1 p-4 bg-gradient-to-r from-green-500 to-green-600 text-white'):
            with ui.row().classes('items-center justify-between w-full'):
                with ui.column().classes('gap-1'):
                    ui.label('活跃用户').classes('text-sm opacity-90')
                    ui.label(str(stats['active_users'])).classes('text-3xl font-bold')
                ui.icon('check_circle').classes('text-2xl opacity-80')

        with ui.card().classes('flex-1 p-4 bg-gradient-to-r from-orange-500 to-orange-600 text-white'):
            with ui.row().classes('items-center justify-between w-full'):
                with ui.column().classes('gap-1'):
                    ui.label('已验证用户').classes('text-sm opacity-90')
                    ui.label(str(stats['verified_users'])).classes('text-3xl font-bold')
                ui.icon('verified').classes('text-2xl opacity-80')

        # 新增：锁定用户统计卡片
        with ui.card().classes('flex-1 p-4 bg-gradient-to-r from-red-500 to-red-600 text-white'):
            with ui.row().classes('items-center justify-between w-full'):
                with ui.column().classes('gap-1'):
                    ui.label('锁定用户').classes('text-sm opacity-90')
                    ui.label(str(stats['locked_users'])).classes('text-3xl font-bold')
                ui.icon('lock').classes('text-2xl opacity-80')

        with ui.card().classes('flex-1 p-4 bg-gradient-to-r from-purple-500 to-purple-600 text-white'):
            with ui.row().classes('items-center justify-between w-full'):
                with ui.column().classes('gap-1'):
                    ui.label('管理员').classes('text-sm opacity-90')
                    ui.label(str(stats['admin_users'])).classes('text-3xl font-bold')
                ui.icon('admin_panel_settings').classes('text-2xl opacity-80')

    with ui.card().classes('w-full mt-6'):
        ui.label('用户列表').classes('text-lg font-semibold')

        # 操作按钮行
        with ui.row().classes('w-full gap-2 mt-4'):
            ui.button('添加用户', icon='add', on_click=lambda: safe(add_user_dialog)).classes('bg-blue-500 text-white')
            ui.button('导出用户', icon='download', on_click=lambda: safe(export_users)).classes('bg-green-500 text-white')
            ui.button('批量解锁', icon='lock_open', on_click=lambda: safe(batch_unlock_users)).classes('bg-orange-500 text-white')
            # 测试异常按钮
            ui.button('测试异常', icon='bug_report', 
                     on_click=lambda: safe(test_exception_function),
                     color='red').classes('ml-4')

        # 绑定搜索事件处理函数
        def handle_search():
            """处理搜索事件 - 立即执行"""
            safe(load_users)
        
        def handle_input_search():
            """处理输入搜索事件 - 延迟执行"""
            ui.timer(0.5, lambda: safe(load_users), once=True)
        
        def reset_search():
            """重置搜索"""
            search_input.value = ''
            safe(load_users)

        # 搜索区域
        with ui.row().classes('w-full gap-2 mt-4 items-end'):
            search_input = ui.input(
                '搜索用户', 
                placeholder='输入用户名或邮箱进行搜索...',
                value=''
            ).classes('flex-1').props('outlined clearable')
            search_input.props('prepend-icon=search')
            
            ui.button('搜索', icon='search', 
                     on_click=handle_search).classes('bg-blue-600 hover:bg-blue-700 text-white px-4 py-2')
            ui.button('重置', icon='refresh', 
                     on_click=reset_search).classes('bg-gray-500 hover:bg-gray-600 text-white px-4 py-2')

        # 用户表格容器
        users_container = ui.column().classes('w-full gap-3')

        def load_users():
            """加载用户数据 - 使用网格布局，最多显示2个用户，鼓励搜索"""
            users_container.clear()

            # 获取搜索条件
            search_term = search_input.value.strip() if hasattr(search_input, 'value') and search_input.value else None
            
            # 使用安全的数据获取方法，传入搜索条件
            all_users = get_users_safe(search_term=search_term)

            # 限制显示的用户数量
            MAX_DISPLAY_USERS = 2
            users_to_display = all_users[:MAX_DISPLAY_USERS]
            has_more_users = len(all_users) > MAX_DISPLAY_USERS

            with users_container:
                # 搜索提示区域
                with ui.card().classes('w-full p-4 mb-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-700'):
                    with ui.row().classes('items-center gap-3'):
                        ui.icon('info').classes('text-blue-600 dark:text-blue-400 text-2xl')
                        with ui.column().classes('flex-1'):
                            ui.label('使用提示').classes('text-lg font-semibold text-blue-800 dark:text-blue-200')
                            if not search_term:
                                ui.label('用户列表最多显示2个用户。要查看或操作特定用户，请使用上方搜索框输入用户名或邮箱进行搜索。').classes('text-blue-700 dark:text-blue-300 text-sm leading-relaxed')
                            else:
                                if len(all_users) > MAX_DISPLAY_USERS:
                                    ui.label(f'搜索到 {len(all_users)} 个用户，当前显示前 {MAX_DISPLAY_USERS} 个。请使用更精确的关键词缩小搜索范围。').classes('text-blue-700 dark:text-blue-300 text-sm leading-relaxed')
                                else:
                                    ui.label(f'搜索到 {len(all_users)} 个匹配用户。').classes('text-blue-700 dark:text-blue-300 text-sm leading-relaxed')

                # 处理无数据情况
                if not all_users:
                    with ui.card().classes('w-full p-8 text-center bg-gray-50 dark:bg-gray-700'):
                        if search_term:
                            ui.icon('search_off').classes('text-6xl text-gray-400 mb-4')
                            ui.label(f'未找到匹配 "{search_term}" 的用户').classes('text-xl font-medium text-gray-500 dark:text-gray-400')
                            ui.label('请尝试其他关键词或清空搜索条件').classes('text-gray-400 dark:text-gray-500 mt-2')
                            with ui.row().classes('gap-2 mt-4 justify-center'):
                                ui.button('清空搜索', icon='clear', 
                                        on_click=reset_search).classes('bg-blue-500 text-white')
                                ui.button('添加新用户', icon='person_add',
                                        on_click=lambda: safe(add_user_dialog)).classes('bg-green-500 text-white')
                        else:
                            ui.icon('people_off').classes('text-6xl text-gray-400 mb-4')
                            ui.label('暂无用户数据').classes('text-xl font-medium text-gray-500 dark:text-gray-400')
                            ui.label('点击"添加用户"按钮添加第一个用户').classes('text-gray-400 dark:text-gray-500 mt-2')
                            ui.button('添加新用户', icon='person_add',
                                    on_click=lambda: safe(add_user_dialog)).classes('mt-4 bg-green-500 text-white')
                    return

                # 显示统计信息
                with ui.row().classes('w-full items-center justify-between mb-4'):
                    if search_term:
                        ui.label(f'搜索结果: {len(all_users)} 个用户').classes('text-lg font-medium text-gray-700 dark:text-gray-300')
                    else:
                        ui.label(f'用户总数: {len(all_users)} 个').classes('text-lg font-medium text-gray-700 dark:text-gray-300')
                    
                    if has_more_users:
                        ui.chip(f'显示 {len(users_to_display)}/{len(all_users)}', icon='visibility').classes('bg-orange-100 text-orange-800 dark:bg-orange-800 dark:text-orange-200')

                # 创建用户卡片网格 - 每行2个
                if users_to_display:
                    for i in range(0, len(users_to_display), 2):
                        with ui.row().classes('w-full gap-3'):
                            # 第一个用户卡片
                            with ui.column().classes('flex-1'):
                                create_user_card(users_to_display[i])
                            
                            # 第二个用户卡片（如果存在）
                            if i + 1 < len(users_to_display):
                                with ui.column().classes('flex-1'):
                                    create_user_card(users_to_display[i + 1])
                            else:
                                # 如果是奇数个用户，添加占位符保持布局
                                ui.column().classes('flex-1')

                # 如果有更多用户未显示，显示提示
                if has_more_users:
                    with ui.card().classes('w-full p-4 mt-4 bg-orange-50 dark:bg-orange-900/20 border border-orange-200 dark:border-orange-700'):
                        with ui.row().classes('items-center gap-3'):
                            ui.icon('visibility_off').classes('text-orange-600 dark:text-orange-400 text-2xl')
                            with ui.column().classes('flex-1'):
                                ui.label(f'还有 {len(all_users) - MAX_DISPLAY_USERS} 个用户未显示').classes('text-lg font-semibold text-orange-800 dark:text-orange-200')
                                ui.label('请使用搜索功能查找特定用户，或者使用更精确的关键词缩小范围。').classes('text-orange-700 dark:text-orange-300 text-sm')

        def create_user_card(user_data: DetachedUser):
            """创建单个用户卡片 - 增加锁定状态显示"""
            # 检查用户是否被锁定
            is_locked = user_data.locked_until and user_data.locked_until > datetime.now()
            
            # 确定用户状态主题
            if user_data.is_superuser:
                card_theme = 'border-l-4 border-purple-500 bg-purple-50 dark:bg-purple-900/10'
                badge_theme = 'bg-purple-100 text-purple-800 dark:bg-purple-800 dark:text-purple-200'
                icon_theme = 'text-purple-600 dark:text-purple-400'
            elif is_locked:
                card_theme = 'border-l-4 border-red-600 bg-red-50 dark:bg-red-900/10'
                badge_theme = 'bg-red-100 text-red-800 dark:bg-red-800 dark:text-red-200'
                icon_theme = 'text-red-600 dark:text-red-400'
            elif 'admin' in user_data.roles:
                card_theme = 'border-l-4 border-red-500 bg-red-50 dark:bg-red-900/10'
                badge_theme = 'bg-red-100 text-red-800 dark:bg-red-800 dark:text-red-200'
                icon_theme = 'text-red-600 dark:text-red-400'
            else:
                card_theme = 'border-l-4 border-blue-500 bg-blue-50 dark:bg-blue-900/10'
                badge_theme = 'bg-blue-100 text-blue-800 dark:bg-blue-800 dark:text-blue-200'
                icon_theme = 'text-blue-600 dark:text-blue-400'

            with ui.card().classes(f'w-full {card_theme} shadow-md hover:shadow-lg transition-shadow duration-300'):
                with ui.row().classes('w-full p-4 gap-4'):
                    # 左侧：用户基本信息（约占 35%）
                    with ui.column().classes('flex-none w-72 gap-2'):
                        # 用户头部信息
                        with ui.row().classes('items-center gap-3 mb-2'):
                            # 根据锁定状态显示不同图标
                            icon_name = 'lock' if is_locked else 'person'
                            ui.icon(icon_name).classes(f'text-3xl {icon_theme}')
                            with ui.column().classes('gap-0'):
                                ui.label(user_data.username).classes('text-xl font-bold text-gray-800 dark:text-gray-200')
                                ui.label(f'ID: {user_data.id}').classes('text-xs text-gray-500 dark:text-gray-400')

                        # 用户标签 - 添加锁定状态标签
                        with ui.row().classes('gap-1 flex-wrap mb-2'):
                            if user_data.is_superuser:
                                ui.chip('超级管理员', icon='admin_panel_settings').classes('bg-purple-100 text-purple-800 dark:bg-purple-800 dark:text-purple-200 text-xs py-1 px-2')
                            
                            # 锁定状态标签 - 新增
                            if is_locked:
                                ui.chip('已锁定', icon='lock').classes('bg-red-100 text-red-800 dark:bg-red-800 dark:text-red-200 text-xs py-1 px-2')
                            
                            if user_data.is_active:
                                ui.chip('已激活', icon='check_circle').classes('bg-green-100 text-green-800 dark:bg-green-800 dark:text-green-200 text-xs py-1 px-2')
                            else:
                                ui.chip('已禁用', icon='block').classes('bg-red-100 text-red-800 dark:bg-red-800 dark:text-red-200 text-xs py-1 px-2')
                            
                            if user_data.is_verified:
                                ui.chip('已验证', icon='verified').classes('bg-blue-100 text-blue-800 dark:bg-blue-800 dark:text-blue-200 text-xs py-1 px-2')
                            else:
                                ui.chip('未验证', icon='warning').classes('bg-orange-100 text-orange-800 dark:bg-orange-800 dark:text-orange-200 text-xs py-1 px-2')

                        # 用户信息
                        ui.label('基本信息:').classes('text-xs font-medium text-gray-600 dark:text-gray-400')
                        ui.label(user_data.email).classes('text-sm text-gray-700 dark:text-gray-300 leading-tight min-h-[1.5rem] line-clamp-1')
                        if user_data.full_name:
                            ui.label(f'姓名: {user_data.full_name}').classes('text-sm text-gray-700 dark:text-gray-300 leading-tight')

                        # 锁定信息显示 - 新增
                        if is_locked:
                            ui.label('锁定信息:').classes('text-xs font-medium text-red-600 dark:text-red-400 mt-2')
                            ui.label(f'锁定至: {format_datetime(user_data.locked_until)}').classes('text-xs text-red-700 dark:text-red-300')
                            remaining_time = user_data.locked_until - datetime.now()
                            if remaining_time.total_seconds() > 0:
                                minutes = int(remaining_time.total_seconds() / 60)
                                ui.label(f'剩余: {minutes} 分钟').classes('text-xs text-red-700 dark:text-red-300')

                        # 统计信息
                        with ui.row().classes('gap-2 mt-2'):
                            with ui.card().classes('flex-1 p-2 bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600'):
                                ui.label('登录次数').classes('text-xs text-gray-500 dark:text-gray-400')
                                ui.label(str(user_data.login_count)).classes('text-lg font-bold text-blue-600 dark:text-blue-400')

                    # 右侧：角色管理区域（约占 65%）
                    with ui.column().classes('flex-1 gap-2'):
                        # 角色列表标题
                        with ui.row().classes('items-center justify-between w-full mb-2'):
                            ui.label(f'用户角色 ({len(user_data.roles)})').classes('text-lg font-bold text-gray-800 dark:text-gray-200')

                        # 角色列表区域
                        with ui.card().classes('w-full p-3 bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 min-h-[80px] max-h-[120px] overflow-auto'):
                            if user_data.roles:
                                with ui.row().classes('gap-2 flex-wrap'):
                                    for role in user_data.roles:
                                        role_color = 'red' if role == 'admin' else 'blue' if role == 'user' else 'green'
                                        ui.chip(role, icon='security').classes(f'bg-{role_color}-100 text-{role_color}-800 dark:bg-{role_color}-800 dark:text-{role_color}-200 text-sm')
                            else:
                                with ui.column().classes('w-full items-center justify-center py-2'):
                                    ui.icon('security_update_warning').classes('text-2xl text-gray-400 mb-1')
                                    ui.label('暂无角色').classes('text-sm text-gray-500 dark:text-gray-400')

                        # 最后登录信息
                        ui.label('最后登录').classes('text-sm font-medium text-gray-600 dark:text-gray-400')
                        ui.label(format_datetime(user_data.last_login) if user_data.last_login else '从未登录').classes('text-sm text-gray-700 dark:text-gray-300')

                        # 用户操作按钮
                        with ui.row().classes('gap-1 w-full mt-2'):
                            ui.button('编辑', icon='edit',
                                    on_click=lambda u=user_data: safe(lambda: edit_user_dialog(u.id))).classes('flex-1 bg-blue-600 hover:bg-blue-700 text-white py-1 text-xs')
                            
                            # 锁定/解锁按钮 - 新增
                            if is_locked:
                                ui.button('解锁', icon='lock_open',
                                        on_click=lambda u=user_data: safe(lambda: toggle_user_lock(u.id, False))).classes('flex-1 bg-orange-600 hover:bg-orange-700 text-white py-1 text-xs')
                            else:
                                ui.button('锁定', icon='lock',
                                        on_click=lambda u=user_data: safe(lambda: toggle_user_lock(u.id, True))).classes('flex-1 bg-red-600 hover:bg-red-700 text-white py-1 text-xs')
                            
                            ui.button('重置密码', icon='lock_reset',
                                    on_click=lambda u=user_data: safe(lambda: reset_password_dialog(u.id))).classes('flex-1 bg-purple-600 hover:bg-purple-700 text-white py-1 text-xs')
                            
                            # 只有当不是当前登录用户时才显示删除按钮
                            if not auth_manager.current_user or auth_manager.current_user.id != user_data.id:
                                ui.button('删除', icon='delete',
                                        on_click=lambda u=user_data: safe(lambda: delete_user_dialog(u.id))).classes('flex-1 bg-red-600 hover:bg-red-700 text-white py-1 text-xs')
                            else:
                                ui.button('当前用户', icon='person',
                                        on_click=lambda: ui.notify('这是您当前登录的账户', type='info')).classes('flex-1 bg-gray-400 text-white py-1 text-xs').disable()

        def toggle_user_lock(user_id: int, lock: bool):
            """切换用户锁定状态"""
            user_data = get_user_safe(user_id)
            if not user_data:
                ui.notify('用户不存在', type='error')
                return
            
            action = "锁定" if lock else "解锁"            
            try:
                with db_safe(f"{action}用户") as db:
                    user = db.query(User).filter(User.id == user_id).first()
                    if not user:
                        ui.notify('用户不存在', type='error')
                        return
                    
                    if lock:
                        # 锁定用户 - 设置30分钟后解锁
                        user.locked_until = datetime.now() + timedelta(minutes=30)
                        ui.notify(f'用户 {user.username} 已锁定 30 分钟', type='warning')
                        log_info(f"用户锁定成功: {user.username}, 锁定至: {user.locked_until}")
                    else:
                        # 解锁用户
                        user.locked_until = None
                        ui.notify(f'用户 {user.username} 已解锁', type='positive')
                        log_info(f"用户解锁成功: {user.username}")
                    
                    db.commit()
                    safe(load_users)  # 重新加载用户列表
                    
            except Exception as e:
                log_error(f"{action}用户失败: {user_data.username}", exception=e)
                ui.notify(f'{action}失败，请稍后重试', type='negative')

        def batch_unlock_users():
            """批量解锁所有锁定的用户"""
            log_info("开始批量解锁用户")
            
            try:
                with db_safe("批量解锁用户") as db:
                    current_time = datetime.now()
                    locked_users = db.query(User).filter(
                        User.locked_until != None,
                        User.locked_until > current_time
                    ).all()
                    
                    if not locked_users:
                        ui.notify('当前没有锁定的用户', type='info')
                        return
                    
                    count = len(locked_users)
                    for user in locked_users:
                        user.locked_until = None
                    
                    db.commit()
                    
                    log_info(f"批量解锁用户成功: {count} 个用户")
                    ui.notify(f'已解锁 {count} 个用户', type='positive')
                    safe(load_users)  # 重新加载用户列表
                    
            except Exception as e:
                log_error("批量解锁用户失败", exception=e)
                ui.notify('批量解锁失败，请稍后重试', type='negative')

        def edit_user_dialog(user_id):
            """编辑用户对话框 - 增加锁定状态控制"""
            
            with ui.dialog() as dialog, ui.card().classes('w-96'):
                dialog.open()
                ui.label('编辑用户').classes('text-lg font-semibold')

                # 安全获取用户数据
                user_data = get_user_safe(user_id)
                if not user_data:
                    ui.label('用户不存在或加载失败').classes('text-red-500')
                    log_error(f"编辑用户失败: 用户ID {user_id} 不存在或加载失败")
                    return

                # 获取可用角色
                available_roles = safe(get_roles_safe, return_value=[])

                # 检查用户是否被锁定
                is_locked = user_data.locked_until and user_data.locked_until > datetime.now()

                # 表单字段
                username_input = ui.input('用户名', value=user_data.username).classes('w-full')
                email_input = ui.input('邮箱', value=user_data.email).classes('w-full')
                full_name_input = ui.input('姓名', value=user_data.full_name or '').classes('w-full')

                # 状态开关
                is_active_switch = ui.switch('账户启用', value=user_data.is_active).classes('mt-4')
                is_verified_switch = ui.switch('邮箱验证', value=user_data.is_verified).classes('mt-2')
                
                # 新增：锁定状态控制开关
                is_locked_switch = ui.switch('锁定账户', value=is_locked).classes('mt-2')
                
                # 锁定信息显示
                if is_locked:
                    with ui.card().classes('w-full mt-2 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-700'):
                        ui.label('锁定信息').classes('text-sm font-medium text-red-600 dark:text-red-400')
                        ui.label(f'锁定至: {format_datetime(user_data.locked_until)}').classes('text-xs text-red-700 dark:text-red-300')
                        remaining_time = user_data.locked_until - datetime.now()
                        if remaining_time.total_seconds() > 0:
                            minutes = int(remaining_time.total_seconds() / 60)
                            ui.label(f'剩余时间: {minutes} 分钟').classes('text-xs text-red-700 dark:text-red-300')

                # 角色选择
                ui.label('角色权限').classes('mt-4 font-medium')
                role_checkboxes = {}
                for role in available_roles:
                    role_checkboxes[role.name] = ui.checkbox(
                        role.display_name or role.name,
                        value=role.name in user_data.roles
                    ).classes('mt-1')

                def save_user():
                    """保存用户修改 - 包含锁定状态处理"""
                    
                    # 验证输入
                    if not username_input.value.strip():
                        ui.notify('用户名不能为空', type='warning')
                        return

                    if not validate_email(email_input.value):
                        ui.notify('邮箱格式不正确', type='warning')
                        return

                    try:
                        with db_safe("更新用户信息") as db:
                            user = db.query(User).filter(User.id == user_id).first()
                            if not user:
                                ui.notify('用户不存在', type='error')
                                return
                            
                            # 更新基本信息
                            user.username = username_input.value.strip()
                            user.email = email_input.value.strip()
                            user.full_name = full_name_input.value.strip() or None
                            user.is_active = is_active_switch.value
                            user.is_verified = is_verified_switch.value
                            
                            # 处理锁定状态 - 新增逻辑
                            if is_locked_switch.value and not is_locked:
                                # 用户从未锁定变为锁定
                                user.locked_until = datetime.now() + timedelta(minutes=30)
                                log_info(f"用户 {user.username} 被设置为锁定状态，锁定至: {user.locked_until}")
                            elif not is_locked_switch.value and is_locked:
                                # 用户从锁定变为未锁定
                                user.locked_until = None
                                log_info(f"用户 {user.username} 被解除锁定状态")
                            # 如果状态没有改变，不处理 locked_until
                            
                            # 更新角色
                            user.roles.clear()
                            selected_roles = [role_name for role_name, checkbox in role_checkboxes.items() if checkbox.value]
                            if selected_roles:
                                roles = db.query(Role).filter(Role.name.in_(selected_roles)).all()
                                user.roles.extend(roles)
                            
                            db.commit()
                            
                            log_info(f"用户修改成功: {user.username}, 新角色: {selected_roles}, 锁定状态: {is_locked_switch.value}")
                            ui.notify('用户信息已更新', type='positive')
                            dialog.close()
                            safe(load_users)

                    except Exception as e:
                        log_error(f"保存用户修改失败: 用户ID {user_id}", exception=e)
                        ui.notify('保存失败，请稍后重试', type='negative')

                with ui.row().classes('w-full justify-end gap-2 mt-6'):
                    ui.button('取消', on_click=dialog.close).classes('bg-gray-500 text-white')
                    ui.button('保存', on_click=lambda: safe(save_user)).classes('bg-blue-500 text-white')

        def add_user_dialog():
            """添加用户对话框"""
            log_info("打开添加用户对话框")
            
            with ui.dialog() as dialog, ui.card().classes('w-96'):
                dialog.open()
                ui.label('添加新用户').classes('text-lg font-semibold')

                # 表单字段
                username_input = ui.input('用户名', placeholder='3-50个字符').classes('w-full')
                email_input = ui.input('邮箱', placeholder='有效的邮箱地址').classes('w-full')
                full_name_input = ui.input('姓名', placeholder='可选').classes('w-full')
                password_input = ui.input('密码', password=True, placeholder='至少6个字符').classes('w-full')

                # 角色选择
                available_roles = safe(get_roles_safe, return_value=[])
                
                ui.label('角色权限').classes('mt-4 font-medium')
                role_checkboxes = {}
                for role in available_roles:
                    role_checkboxes[role.name] = ui.checkbox(
                        role.display_name or role.name,
                        value=(role.name == 'user')  # 默认选择user角色
                    ).classes('mt-1')

                def save_new_user():
                    """保存新用户"""
                    log_info("开始创建新用户")
                    
                    # 验证输入
                    username_result = validate_username(username_input.value or '')
                    if not username_result['valid']:
                        ui.notify(username_result['message'], type='warning')
                        log_error(f"用户名验证失败: {username_result['message']}")
                        return

                    if not validate_email(email_input.value or ''):
                        ui.notify('邮箱格式不正确', type='warning')
                        log_error(f"邮箱验证失败: {email_input.value}")
                        return

                    if not password_input.value or len(password_input.value) < 6:
                        ui.notify('密码至少需要6个字符', type='warning')
                        log_error("密码长度不足")
                        return

                    try:
                        with db_safe("创建新用户") as db:
                            # 检查用户名和邮箱是否已存在
                            existing = db.query(User).filter(
                                (User.username == username_input.value) |
                                (User.email == email_input.value)
                            ).first()

                            if existing:
                                ui.notify('用户名或邮箱已存在', type='warning')
                                log_error(f"用户创建失败: 用户名或邮箱已存在 - {username_input.value}, {email_input.value}")
                                return

                            # 创建新用户
                            new_user = User(
                                username=username_input.value.strip(),
                                email=email_input.value.strip(),
                                full_name=full_name_input.value.strip() or None,
                                is_active=True,
                                is_verified=True,
                                locked_until=None  # 新用户默认不锁定
                            )
                            new_user.set_password(password_input.value)

                            # 分配角色
                            selected_roles = []
                            for role_name, checkbox in role_checkboxes.items():
                                if checkbox.value:
                                    role = db.query(Role).filter(Role.name == role_name).first()
                                    if role:
                                        new_user.roles.append(role)
                                        selected_roles.append(role_name)

                            db.add(new_user)
                            db.commit()

                            log_info(f"新用户创建成功: {new_user.username}, 角色: {selected_roles}")
                            ui.notify(f'用户 {new_user.username} 创建成功', type='positive')
                            dialog.close()
                            safe(load_users)

                    except Exception as e:
                        log_error(f"创建用户失败: {username_input.value}", exception=e)
                        ui.notify('用户创建失败，请稍后重试', type='negative')

                with ui.row().classes('w-full justify-end gap-2 mt-6'):
                    ui.button('取消', on_click=dialog.close).classes('bg-gray-500 text-white')
                    ui.button('创建用户', on_click=lambda: safe(save_new_user)).classes('bg-blue-500 text-white')

        def reset_password_dialog(user_id):
            """重置密码对话框"""
            log_info(f"打开重置密码对话框: 用户ID {user_id}")
            
            # 安全获取用户数据
            user_data = get_user_safe(user_id)
            if not user_data:
                ui.notify('用户不存在', type='error')
                log_error(f"重置密码失败: 用户ID {user_id} 不存在")
                return
            
            with ui.dialog() as dialog, ui.card().classes('w-96'):
                dialog.open()
                ui.label(f'重置用户密码: {user_data.username}').classes('text-lg font-semibold')

                # 显示生成的密码
                password_display = ui.input('新密码', password=False).classes('w-full mt-4')
                password_display.props('hint="点击下方按钮生成随机密码"')
                password_display.disable()

                def generate_password():
                    """生成随机密码"""
                    length = 12
                    characters = string.ascii_letters + string.digits + "!@#$%^&*"
                    password = ''.join(secrets.choice(characters) for _ in range(length))
                    password_display.enable()
                    password_display.value = password
                    password_display.disable()
                    ui.notify('已生成随机密码', type='info')
                    log_info(f"为用户 {user_data.username} 生成随机密码")

                ui.button('生成随机密码', icon='casino', 
                         on_click=lambda: safe(generate_password)).classes('w-full mt-2 bg-purple-500 text-white')

                def perform_reset():
                    """执行密码重置"""
                    log_info(f"开始重置用户密码: {user_data.username}")
                    
                    if not password_display.value:
                        ui.notify('请先生成密码', type='warning')
                        return

                    try:
                        with db_safe("重置用户密码") as db:
                            user = db.query(User).filter(User.id == user_id).first()
                            if not user:
                                ui.notify('用户不存在', type='error')
                                return

                            # 更新密码
                            user.set_password(password_display.value)
                            user.session_token = None
                            user.remember_token = None
                            db.commit()

                            log_info(f"用户密码重置成功: {user.username}")
                            ui.notify(f'用户 {user.username} 密码重置成功', type='positive')
                            dialog.close()

                    except Exception as e:
                        log_error(f"重置密码失败: {user_data.username}", exception=e)
                        ui.notify('密码重置失败，请稍后重试', type='negative')

                with ui.row().classes('w-full justify-end gap-2 mt-6'):
                    ui.button('取消', on_click=dialog.close).classes('bg-gray-500 text-white')
                    ui.button('重置密码', on_click=lambda: safe(perform_reset)).classes('bg-orange-500 text-white')

        def delete_user_dialog(user_id):
            """删除用户对话框"""
            log_info(f"打开删除用户对话框: 用户ID {user_id}")
            
            # 安全获取用户数据
            user_data = get_user_safe(user_id)
            if not user_data:
                ui.notify('用户不存在', type='error')
                log_error(f"删除用户失败: 用户ID {user_id} 不存在")
                return
            
            with ui.dialog() as dialog, ui.card().classes('w-96'):
                dialog.open()
                ui.label('确认删除用户').classes('text-lg font-semibold text-red-600')
                ui.label(f'您确定要删除用户 "{user_data.username}" 吗？').classes('mt-2')
                ui.label('此操作不可撤销！').classes('text-red-500 mt-2 font-medium')

                def confirm_delete():
                    """确认删除"""
                    log_info(f"开始删除用户: {user_data.username}")
                    
                    # 检查是否是当前登录用户
                    if auth_manager.current_user and auth_manager.current_user.id == user_id:
                        ui.notify('不能删除当前登录的用户', type='warning')
                        log_error(f"删除用户失败: 尝试删除当前登录用户 {user_data.username}")
                        return

                    # 使用安全的删除方法
                    success = detached_manager.delete_user_safe(user_id)
                    
                    if success:
                        log_info(f"用户删除成功: {user_data.username}")
                        ui.notify(f'用户 {user_data.username} 已删除', type='positive')
                        dialog.close()
                        safe(load_users)
                    else:
                        log_error(f"删除用户失败: {user_data.username}")
                        ui.notify('删除失败，请稍后重试', type='negative')

                with ui.row().classes('w-full justify-end gap-2 mt-6'):
                    ui.button('取消', on_click=dialog.close).classes('bg-gray-500 text-white')
                    ui.button('确认删除', on_click=lambda: safe(confirm_delete)).classes('bg-red-500 text-white')

        def export_users():
            """导出用户功能（测试）"""
            log_info("开始导出用户数据")
            ui.notify('用户导出功能开发中...', type='info')

        def test_exception_function():
            """测试异常处理功能"""
            log_info("触发测试异常")
            raise ValueError("这是一个测试异常，用于验证异常处理功能")

        # 绑定搜索事件 - 确保事件正确绑定和触发
        search_input.on('input', handle_input_search)  # 实时输入搜索（延迟）
        search_input.on('keydown.enter', handle_search)  # 回车键立即搜索

        # 初始加载
        safe(load_users, error_msg="初始化用户列表失败")

    log_success("===用户管理页面加载完成===")
```
