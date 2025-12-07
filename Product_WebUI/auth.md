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
数据库连接和管理模块 - SQLModel 版本
使用 SQLModel 的 Session 替换 SQLAlchemy，大幅简化代码
"""
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy import event
from contextlib import contextmanager
from typing import Generator
from .config import auth_config

# 配置日志
from common.log_handler import (
    log_info, 
    log_error, 
    log_warning,
    log_debug,
    log_success,
    get_logger
)

# 获取绑定模块名称的logger
logger = get_logger(__file__)

# ===========================
# 全局变量
# ===========================
engine = None


# ===========================
# 数据库初始化
# ===========================

def init_database():
    """
    初始化数据库连接（不再负责建表）
    
    优势：
    1. 代码量减少 70%
    2. 不需要 SessionLocal 和 scoped_session
    3. SQLModel 的 Session 更简洁
    """
    global engine
    
    try:
        # 创建数据库引擎
        engine = create_engine(
            auth_config.database_url,
            pool_pre_ping=True,  # 自动检测连接是否有效
            echo=False,  # 生产环境设为 False
            # SQLModel 推荐的配置
            connect_args=(
                {"check_same_thread": False} 
                if auth_config.database_type == 'sqlite' 
                else {}
            )
        )
        
        # 为 SQLite 启用外键约束
        if auth_config.database_type == 'sqlite':
            @event.listens_for(engine, "connect")
            def set_sqlite_pragma(dbapi_connection, connection_record):
                cursor = dbapi_connection.cursor()
                cursor.execute("PRAGMA foreign_keys=ON")
                cursor.close()
        
        log_success(f"✅ 数据库连接初始化成功 - 类型: {auth_config.database_type}")
        
    except Exception as e:
        log_error(f"❌ 数据库连接初始化失败, 类型 {auth_config.database_type}: {e}")
        raise


# ===========================
# Session 管理 - SQLModel 简化版
# ===========================

def get_session() -> Session:
    """
    获取数据库 Session（简化版）
    
    SQLModel 优势：
    1. 不需要 SessionLocal
    2. Session 自动管理
    3. 代码量减少 80%
    
    使用示例：
        with get_session() as session:
            user = session.exec(select(User).where(User.id == 1)).first()
    """
    if engine is None:
        init_database()
    
    return Session(engine)


@contextmanager
def get_db() -> Generator[Session, None, None]:
    """
    获取数据库会话的上下文管理器（向后兼容）
    
    优势：
    1. 自动提交/回滚
    2. 自动关闭连接
    3. 异常安全
    
    使用示例：
        with get_db() as session:
            user = session.exec(select(User).where(User.id == 1)).first()
            session.add(user)
            # 自动 commit
    """
    session = get_session()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        log_error(f"❌ 数据库操作失败: {e}")
        raise
    finally:
        session.close()


# ===========================
# 数据库工具函数
# ===========================

def close_database():
    """
    关闭数据库连接
    
    注意：SQLModel 的 engine.dispose() 会关闭所有连接池
    """
    global engine
    
    if engine:
        engine.dispose()
        log_info("🔒 数据库连接已关闭")


def check_connection() -> bool:
    """
    检查数据库连接状态
    
    Returns:
        bool: 连接是否正常
    """
    try:
        with get_db() as session:
            # SQLModel 使用 exec 执行原生 SQL
            session.exec("SELECT 1")
        return True
    except Exception as e:
        log_error(f"❌ 数据库连接检查失败: {e}")
        return False


def get_engine():
    """
    获取数据库引擎（供其他模块使用）
    
    Returns:
        Engine: SQLModel/SQLAlchemy 引擎实例
    """
    if engine is None:
        init_database()
    return engine


# ===========================
# 数据库表创建（仅用于开发/测试）
# ===========================

def create_all_tables():
    """
    创建所有数据库表（开发/测试环境使用）
    
    警告：生产环境请使用 scripts/init_database.py
    """
    try:
        if engine is None:
            init_database()
        
        # 导入所有模型以注册到 SQLModel.metadata
        from .models import (
            User, Role, Permission, LoginLog,
            UserRoleLink, RolePermissionLink, UserPermissionLink
        )
        
        # 创建所有表
        SQLModel.metadata.create_all(engine)
        log_success("✅ 数据库表创建成功")
        
    except Exception as e:
        log_error(f"❌ 数据库表创建失败: {e}")
        raise


# ===========================
# 向后兼容函数
# ===========================

def reset_database():
    """
    重置数据库（已废弃，请使用 scripts/init_database.py --reset）
    """
    log_warning(
        "⚠️ reset_database() 已废弃，"
        "请使用 'python scripts/init_database.py --reset'"
    )
    import subprocess
    import sys
    
    try:
        result = subprocess.run([
            sys.executable, 
            'scripts/init_database.py', 
            '--reset', 
            '--test-data'
        ], check=True, capture_output=True, text=True)
        log_info("✅ 数据库重置完成")
        return True
    except subprocess.CalledProcessError as e:
        log_error(f"❌ 数据库重置失败: {e}")
        return False


def quick_init_for_testing():
    """
    快速初始化（仅用于测试环境）
    
    功能：
    1. 初始化数据库连接
    2. 创建所有表
    3. 初始化默认数据
    """
    try:
        # 初始化连接
        init_database()
        
        # 创建表
        create_all_tables()
        
        # 调用统一初始化脚本
        from scripts.init_database import DatabaseInitializer
        
        initializer = DatabaseInitializer()
        initializer.engine = engine
        
        # 导入模型并初始化数据
        initializer.import_all_models()
        initializer.init_auth_default_data()
        initializer.init_default_permissions()
        initializer.init_role_permissions()
        
        log_success("✅ 快速初始化完成（测试环境）")
        return True
        
    except Exception as e:
        log_error(f"❌ 快速初始化失败: {e}")
        return False


# ===========================
# 导出接口
# ===========================

__all__ = [
    # 核心函数
    'init_database',
    'get_session',
    'get_db',
    'get_engine',
    
    # 工具函数
    'close_database',
    'check_connection',
    'create_all_tables',
    
    # 向后兼容
    'reset_database',
    'quick_init_for_testing',
    
    # 全局变量
    'engine',
]
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

- **auth\models.py**
```python
"""
数据模型定义 - SQLModel 版本
使用 SQLModel 替换 SQLAlchemy，消除 DetachedInstanceError 问题
"""
from sqlmodel import SQLModel, Field, Relationship, Column, String, Text
from typing import Optional, List, Set
from datetime import datetime
import hashlib
import secrets

# ===========================
# 关联表定义
# ===========================

class UserRoleLink(SQLModel, table=True):
    """用户-角色关联表"""
    __tablename__ = "user_roles"
    
    user_id: Optional[int] = Field(
        default=None, 
        foreign_key="users.id", 
        primary_key=True,
        ondelete="CASCADE"
    )
    role_id: Optional[int] = Field(
        default=None, 
        foreign_key="roles.id", 
        primary_key=True,
        ondelete="CASCADE"
    )


class RolePermissionLink(SQLModel, table=True):
    """角色-权限关联表"""
    __tablename__ = "role_permissions"
    
    role_id: Optional[int] = Field(
        default=None, 
        foreign_key="roles.id", 
        primary_key=True,
        ondelete="CASCADE"
    )
    permission_id: Optional[int] = Field(
        default=None, 
        foreign_key="permissions.id", 
        primary_key=True,
        ondelete="CASCADE"
    )


class UserPermissionLink(SQLModel, table=True):
    """用户-权限关联表（直接权限分配）"""
    __tablename__ = "user_permissions"
    
    user_id: Optional[int] = Field(
        default=None, 
        foreign_key="users.id", 
        primary_key=True,
        ondelete="CASCADE"
    )
    permission_id: Optional[int] = Field(
        default=None, 
        foreign_key="permissions.id", 
        primary_key=True,
        ondelete="CASCADE"
    )


# ===========================
# 主要模型定义
# ===========================

class User(SQLModel, table=True):
    """用户模型 - SQLModel 版本
    
    优势：
    1. 自动支持 Pydantic 验证
    2. 自动序列化为 dict/JSON
    3. 不会产生 DetachedInstanceError
    4. 类型提示完善
    """
    __tablename__ = "users"
    
    # 主键
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    
    # 基本信息
    username: str = Field(
        max_length=50, 
        unique=True, 
        index=True,
        description="用户名，唯一标识"
    )
    email: str = Field(
        max_length=100, 
        unique=True, 
        index=True,
        description="电子邮箱"
    )
    password_hash: str = Field(max_length=255, description="密码哈希值")
    full_name: Optional[str] = Field(default=None, max_length=100, description="全名")
    phone: Optional[str] = Field(default=None, max_length=20, description="手机号")
    avatar: Optional[str] = Field(default=None, max_length=255, description="头像URL")
    bio: Optional[str] = Field(default=None, sa_column=Column(Text), description="个人简介")
    
    # 状态信息
    is_active: bool = Field(default=True, description="账户是否激活")
    is_verified: bool = Field(default=False, description="邮箱是否验证")
    is_superuser: bool = Field(default=False, description="是否超级管理员")
    
    # 登录信息
    last_login: Optional[datetime] = Field(default=None, description="最后登录时间")
    login_count: int = Field(default=0, description="登录次数")
    failed_login_count: int = Field(default=0, description="失败登录次数")
    locked_until: Optional[datetime] = Field(default=None, description="账户锁定至")
    
    # Token 管理
    session_token: Optional[str] = Field(default=None, max_length=255, description="会话令牌")
    remember_token: Optional[str] = Field(default=None, max_length=255, description="记住我令牌")
    # reset_token: Optional[str] = Field(default=None, max_length=255, description="密码重置令牌")
    # reset_token_expires: Optional[datetime] = Field(default=None, description="重置令牌过期时间")
    
    # 时间戳
    created_at: Optional[datetime] = Field(
        default_factory=datetime.now,
        description="创建时间"
    )
    updated_at: Optional[datetime] = Field(
        default_factory=datetime.now,
        description="更新时间"
    )
    
    # 关系定义（延迟导入避免循环依赖）
    roles: List["Role"] = Relationship(
        back_populates="users",
        link_model=UserRoleLink
    )
    permissions: List["Permission"] = Relationship(
        back_populates="users",
        link_model=UserPermissionLink
    )
    login_logs: List["LoginLog"] = Relationship(back_populates="user")
    
    # ===========================
    # 业务方法
    # ===========================
    
    def set_password(self, password: str):
        """设置密码（哈希存储）"""
        salt = secrets.token_hex(16)
        self.password_hash = hashlib.sha256(f"{password}{salt}".encode()).hexdigest() + f":{salt}"
    
    def check_password(self, password: str) -> bool:
        """验证密码"""
        try:
            stored_hash, salt = self.password_hash.split(':')
            test_hash = hashlib.sha256(f"{password}{salt}".encode()).hexdigest()
            return stored_hash == test_hash
        except:
            return False
    
    def has_role(self, role_name: str) -> bool:
        """检查是否有指定角色"""
        if self.is_superuser:
            return True
        try:
            return any(role.name == role_name for role in self.roles)
        except:
            return False
    
    def has_permission(self, permission_name: str) -> bool:
        """检查是否有指定权限（包括角色权限和直接权限）"""
        if self.is_superuser:
            return True
        
        try:
            # 检查用户直接分配的权限
            if any(perm.name == permission_name for perm in self.permissions):
                return True
            
            # 检查角色权限
            for role in self.roles:
                if hasattr(role, 'permissions') and any(
                    perm.name == permission_name for perm in role.permissions
                ):
                    return True
        except:
            return False
        
        return False
    
    def get_all_permissions(self) -> Set[str]:
        """获取用户的所有权限（角色权限 + 直接权限）"""
        if self.is_superuser:
            # 超级管理员拥有所有权限
            return {'*'}
        
        permissions = set()
        
        try:
            # 用户直接分配的权限
            permissions.update(perm.name for perm in self.permissions)
            
            # 角色权限
            for role in self.roles:
                if hasattr(role, 'permissions'):
                    permissions.update(perm.name for perm in role.permissions)
        except:
            pass
        
        return permissions
    
    def is_locked(self) -> bool:
        """检查用户是否被锁定"""
        return self.locked_until is not None and self.locked_until > datetime.now()
    
    # ===========================
    # Pydantic Config
    # ===========================
    
    class Config:
        """Pydantic 配置"""
        json_schema_extra = {
            "example": {
                "username": "admin",
                "email": "admin@example.com",
                "full_name": "Administrator",
                "is_active": True,
                "is_superuser": True
            }
        }


class Role(SQLModel, table=True):
    """角色模型 - SQLModel 版本"""
    __tablename__ = "roles"
    
    # 主键
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    
    # 基本信息
    name: str = Field(
        max_length=50, 
        unique=True, 
        index=True,
        description="角色名称（英文标识）"
    )
    display_name: Optional[str] = Field(default=None, max_length=100, description="显示名称（中文）")
    description: Optional[str] = Field(default=None, sa_column=Column(Text), description="角色描述")
    
    # 状态
    is_active: bool = Field(default=True, description="是否启用")
    is_system: bool = Field(default=False, description="是否系统角色（不可删除）")
    
    # 时间戳
    created_at: Optional[datetime] = Field(
        default_factory=datetime.now,
        description="创建时间"
    )
    updated_at: Optional[datetime] = Field(
        default_factory=datetime.now,
        description="更新时间"
    )
    
    # 关系定义
    users: List["User"] = Relationship(
        back_populates="roles",
        link_model=UserRoleLink
    )
    permissions: List["Permission"] = Relationship(
        back_populates="roles",
        link_model=RolePermissionLink
    )
    
    # ===========================
    # Pydantic Config
    # ===========================
    
    class Config:
        """Pydantic 配置"""
        json_schema_extra = {
            "example": {
                "name": "admin",
                "display_name": "系统管理员",
                "description": "拥有系统最高权限",
                "is_active": True,
                "is_system": True
            }
        }


class Permission(SQLModel, table=True):
    """权限模型 - SQLModel 版本"""
    __tablename__ = "permissions"
    
    # 主键
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    
    # 基本信息
    name: str = Field(
        max_length=100, 
        unique=True, 
        index=True,
        description="权限名称（英文标识）"
    )
    display_name: Optional[str] = Field(default=None, max_length=100, description="显示名称（中文）")
    category: Optional[str] = Field(default=None, max_length=50, description="权限分类")
    description: Optional[str] = Field(default=None, sa_column=Column(Text), description="权限描述")
    
    # 时间戳
    created_at: Optional[datetime] = Field(
        default_factory=datetime.now,
        description="创建时间"
    )
    updated_at: Optional[datetime] = Field(
        default_factory=datetime.now,
        description="更新时间"
    )
    
    # 关系定义
    roles: List["Role"] = Relationship(
        back_populates="permissions",
        link_model=RolePermissionLink
    )
    users: List["User"] = Relationship(
        back_populates="permissions",
        link_model=UserPermissionLink
    )
    
    # ===========================
    # Pydantic Config
    # ===========================
    
    class Config:
        """Pydantic 配置"""
        json_schema_extra = {
            "example": {
                "name": "user.create",
                "display_name": "创建用户",
                "category": "user",
                "description": "允许创建新用户账户"
            }
        }


class LoginLog(SQLModel, table=True):
    """登录日志模型 - SQLModel 版本"""
    __tablename__ = "login_logs"
    
    # 主键
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    
    # 关联用户
    user_id: Optional[int] = Field(default=None, foreign_key="users.id", ondelete="CASCADE")
    
    # 登录信息
    ip_address: Optional[str] = Field(default=None, max_length=45, description="IP地址")
    user_agent: Optional[str] = Field(default=None, max_length=255, description="User-Agent")
    login_type: Optional[str] = Field(
        default="normal", 
        max_length=20,
        description="登录类型: normal, remember_me, oauth"
    )
    is_success: bool = Field(default=True, description="是否登录成功")
    failure_reason: Optional[str] = Field(default=None, max_length=100, description="失败原因")
    
    # 时间戳
    created_at: Optional[datetime] = Field(
        default_factory=datetime.now,
        description="登录时间"
    )
    
    # 关系定义
    user: Optional["User"] = Relationship(back_populates="login_logs")
    
    # ===========================
    # Pydantic Config
    # ===========================
    
    class Config:
        """Pydantic 配置"""
        json_schema_extra = {
            "example": {
                "user_id": 1,
                "ip_address": "192.168.1.100",
                "login_type": "normal",
                "is_success": True
            }
        }


# ===========================
# 模型更新钩子
# ===========================

def update_timestamp(model: SQLModel):
    """更新时间戳的辅助函数"""
    if hasattr(model, 'updated_at'):
        model.updated_at = datetime.now()


# ===========================
# 导出所有模型
# ===========================

__all__ = [
    'User',
    'Role',
    'Permission',
    'LoginLog',
    'UserRoleLink',
    'RolePermissionLink',
    'UserPermissionLink',
    'update_timestamp'
]
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
会话管理器 - SQLModel 版本
移除对 detached_helper 的依赖,直接使用 SQLModel User 对象
"""
from typing import Optional, Dict, Set
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class UserSession:
    """
    用户会话数据类
    
    核心改进 (SQLModel 版本):
    - 直接从 User 模型创建,无需 Detached 转换
    - 保持轻量级内存缓存
    - 与 SQLModel User 模型完全兼容
    """
    id: int
    username: str
    email: str
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
    
    # 关联数据 (存储为字符串列表/集合)
    roles: list = field(default_factory=list)          # 角色名称列表
    permissions: Set[str] = field(default_factory=set)  # 权限名称集合 (包括角色权限和直接权限)
    
    def has_role(self, role_name: str) -> bool:
        """检查是否有指定角色"""
        return role_name in self.roles
    
    def has_permission(self, permission_name: str) -> bool:
        """检查是否有指定权限"""
        return self.is_superuser or permission_name in self.permissions
    
    def is_locked(self) -> bool:
        """检查用户是否被锁定"""
        return self.locked_until is not None and self.locked_until > datetime.now()
    
    @classmethod
    def from_user(cls, user) -> 'UserSession':
        """
        从 SQLModel User 对象创建会话对象
        
        核心改进:
        - 直接访问 user.roles 和 user.permissions (SQLModel 自动处理关系)
        - 不需要 joinedload
        - 不会产生 DetachedInstanceError
        """
        # 提取角色名称
        role_names = []
        try:
            # SQLModel: user.roles 返回 List[Role] 对象
            role_names = [role.name for role in user.roles]
        except Exception as e:
            # 如果关系未加载,返回空列表
            pass
        
        # 提取权限 (包括角色权限和直接权限)
        permissions = set()
        if user.is_superuser:
            permissions.add('*')  # 超级管理员拥有所有权限
        else:
            try:
                # 1. 用户直接分配的权限
                if hasattr(user, 'permissions') and user.permissions:
                    permissions.update(perm.name for perm in user.permissions)
                
                # 2. 角色权限
                if hasattr(user, 'roles') and user.roles:
                    for role in user.roles:
                        if hasattr(role, 'permissions') and role.permissions:
                            permissions.update(perm.name for perm in role.permissions)
            except Exception as e:
                # 如果关系未加载,保持空集合
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
            failed_login_count=user.failed_login_count,
            locked_until=user.locked_until,
            created_at=user.created_at,
            updated_at=user.updated_at,
            roles=role_names,
            permissions=permissions
        )


class SessionManager:
    """
    会话管理器
    
    职责:
    - 管理内存中的用户会话缓存
    - 提供快速的会话查询
    - 避免频繁的数据库查询
    """
    
    def __init__(self):
        self._sessions: Dict[str, UserSession] = {}
    
    def create_session(self, token: str, user) -> UserSession:
        """
        创建会话
        
        Args:
            token: 会话 token
            user: SQLModel User 对象
        
        Returns:
            UserSession: 会话对象
        """
        session = UserSession.from_user(user)
        self._sessions[token] = session
        return session
    
    def get_session(self, token: str) -> Optional[UserSession]:
        """
        获取会话
        
        Args:
            token: 会话 token
        
        Returns:
            Optional[UserSession]: 会话对象,不存在则返回 None
        """
        return self._sessions.get(token)
    
    def update_session(self, token: str, user) -> Optional[UserSession]:
        """
        更新会话 (从数据库重新加载用户数据)
        
        Args:
            token: 会话 token
            user: SQLModel User 对象
        
        Returns:
            Optional[UserSession]: 更新后的会话对象
        """
        if token in self._sessions:
            session = UserSession.from_user(user)
            self._sessions[token] = session
            return session
        return None
    
    def delete_session(self, token: str):
        """
        删除会话
        
        Args:
            token: 会话 token
        """
        if token in self._sessions:
            del self._sessions[token]
    
    def clear_all_sessions(self):
        """清除所有会话"""
        self._sessions.clear()
    
    def get_session_count(self) -> int:
        """获取当前会话数量"""
        return len(self._sessions)
    
    def get_all_sessions(self) -> Dict[str, UserSession]:
        """获取所有会话 (用于调试/管理)"""
        return self._sessions.copy()


# 全局会话管理器实例
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
权限管理页面 - 优化版本
在每个分类的 ui.expansion 中使用 ui.table 展示权限
包含3个操作列: 权限操作、角色操作、用户操作
"""
from nicegui import ui
from sqlmodel import Session, select, func
from datetime import datetime

# 导入模型和数据库
from ..models import Permission, Role, User
from ..database import get_db
from ..decorators import require_role
from ..auth_manager import auth_manager

# 导入日志处理
from common.log_handler import (
    log_trace, log_debug, log_info, log_success, 
    log_warning, log_error, log_critical,
    safe, db_safe, safe_protect, catch, get_logger
)

logger = get_logger(__file__)


@require_role('admin')
@safe_protect(name="权限管理页面", error_msg="权限管理页面加载失败,请稍后重试")
def permission_management_page_content():
    """权限管理页面内容 - 仅管理员可访问"""
    
    # 页面标题
    with ui.column().classes('w-full mb-6'):
        ui.label('权限管理').classes('text-4xl font-bold text-green-800 dark:text-green-200 mb-2')
        ui.label('管理系统权限和资源访问控制,支持角色和用户关联管理').classes('text-lg text-gray-600 dark:text-gray-400')

    # ===========================
    # 统计数据加载
    # ===========================
    
    def load_permission_statistics():
        """加载权限统计数据 - SQLModel 版本"""
        with get_db() as session:
            total_permissions = session.exec(
                select(func.count()).select_from(Permission)
            ).one()
            
            system_permissions = session.exec(
                select(func.count()).select_from(Permission).where(
                    Permission.category == 'system'
                )
            ).one()
            
            content_permissions = session.exec(
                select(func.count()).select_from(Permission).where(
                    Permission.category == 'content'
                )
            ).one()
            
            total_roles = session.exec(
                select(func.count()).select_from(Role)
            ).one()
            
            total_users = session.exec(
                select(func.count()).select_from(User)
            ).one()
            
            return {
                'total_permissions': total_permissions,
                'system_permissions': system_permissions,
                'content_permissions': content_permissions,
                'other_permissions': total_permissions - system_permissions - content_permissions,
                'total_roles': total_roles,
                'total_users': total_users
            }
    
    # 安全执行统计数据加载
    stats = safe(
        load_permission_statistics,
        return_value={
            'total_permissions': 0, 'system_permissions': 0, 
            'content_permissions': 0, 'other_permissions': 0,
            'total_roles': 0, 'total_users': 0
        },
        error_msg="权限统计数据加载失败"
    )

    # ===========================
    # 统计卡片区域
    # ===========================
    
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
                    ui.label('其他权限').classes('text-sm opacity-90 font-medium')
                    ui.label(str(stats['other_permissions'])).classes('text-3xl font-bold')
                ui.icon('more_horiz').classes('text-4xl opacity-80')

    # ===========================
    # 搜索和操作区域
    # ===========================
    
    with ui.card().classes('w-full mb-6'):
        with ui.row().classes('w-full items-center gap-4 p-4'):
            search_input = ui.input(
                label='搜索权限', 
                placeholder='输入权限名称或描述...'
            ).classes('flex-1')
            
            category_select = ui.select(
                label='分类筛选',
                options={
                    'all': '全部',
                    'system': '系统权限',
                    'user': '用户权限',
                    'content': '内容权限',
                    'other': '其他'
                },
                value='all'
            ).classes('w-48')
            
            ui.button(
                '搜索', 
                icon='search',
                on_click=lambda: safe(load_permissions)
            ).classes('bg-green-500 text-white')
            
            ui.button(
                '创建权限', 
                icon='add_box',
                on_click=lambda: safe(create_permission_dialog)
            ).classes('bg-blue-500 text-white')
            
            ui.button(
                '刷新', 
                icon='refresh',
                on_click=lambda: safe(load_permissions)
            ).classes('bg-gray-500 text-white')

    # ===========================
    # 权限列表 - 按分类展示
    # ===========================
    
    # 创建列表容器
    list_container = ui.column().classes('w-full')
    
    @safe_protect(name="加载权限列表")
    def load_permissions():
        """加载权限列表 - SQLModel 版本,按分类展示"""
        list_container.clear()
        
        with list_container:
            with get_db() as session:
                # 构建查询
                stmt = select(Permission)
                
                # 搜索过滤
                if search_input.value:
                    search_term = search_input.value.strip()
                    stmt = stmt.where(
                        (Permission.name.contains(search_term)) |
                        (Permission.display_name.contains(search_term)) |
                        (Permission.description.contains(search_term))
                    )
                
                # 分类过滤
                if category_select.value != 'all':
                    if category_select.value == 'other':
                        stmt = stmt.where(
                            (Permission.category == None) | 
                            (~Permission.category.in_(['system', 'user', 'content']))
                        )
                    else:
                        stmt = stmt.where(Permission.category == category_select.value)
                
                # 排序
                stmt = stmt.order_by(Permission.category, Permission.name)
                
                # 执行查询
                permissions = session.exec(stmt).all()
                
                log_info(f"查询到 {len(permissions)} 个权限")
                
                if not permissions:
                    with ui.card().classes('w-full p-8 text-center'):
                        ui.icon('inbox', size='64px').classes('text-gray-400 mb-4')
                        ui.label('暂无权限数据').classes('text-xl text-gray-500')
                    return
                
                # 按分类组织权限
                permissions_by_category = {}
                for perm in permissions:
                    category = perm.category or '其他'
                    if category not in permissions_by_category:
                        permissions_by_category[category] = []
                    permissions_by_category[category].append(perm)
                
                # ✅ 为每个分类创建 expansion,内部使用 table 展示
                for category, perms in sorted(permissions_by_category.items()):
                    with ui.expansion(
                        f"{category.upper()} ({len(perms)})", 
                        icon='folder_open'
                    ).classes('w-full mb-4').props('default-opened'):
                        # ✅ 为每个分类创建独立的表格
                        create_category_table(category, perms)

    def create_category_table(category: str, perms: list):
        """为分类创建表格"""
        # 表格列定义
        columns = [
            {'name': 'name', 'label': '权限名称', 'field': 'name', 'align': 'left', 'sortable': True},
            {'name': 'display_name', 'label': '显示名称', 'field': 'display_name', 'align': 'left'},
            {'name': 'description', 'label': '描述', 'field': 'description', 'align': 'left'},
            {'name': 'roles', 'label': '角色数', 'field': 'roles', 'align': 'center', 'sortable': True},
            {'name': 'users', 'label': '用户数', 'field': 'users', 'align': 'center', 'sortable': True},
            {'name': 'perm_actions', 'label': '权限操作', 'field': 'perm_actions', 'align': 'center'},
            {'name': 'role_actions', 'label': '角色操作', 'field': 'role_actions', 'align': 'center'},
            {'name': 'user_actions', 'label': '用户操作', 'field': 'user_actions', 'align': 'center'},
        ]
        
        # 转换为表格数据
        rows = []
        for perm in perms:
            rows.append({
                'id': perm.id,
                'name': perm.name,
                'display_name': perm.display_name or '-',
                'description': perm.description or '-',
                'roles': len(perm.roles),
                'users': len(perm.users),
            })
        
        # ✅ 创建表格
        table = ui.table(
            columns=columns,
            rows=rows,
            row_key='id',
            pagination={'rowsPerPage': 10, 'sortBy': 'name'},
            column_defaults={
                        'align': 'left',
                        'headerClasses': 'uppercase text-primary text-base font-bold',
                        'classes': 'text-base'
            }
        ).classes('w-full')
        
        # ✅ 添加权限操作列的插槽
        table.add_slot('body-cell-perm_actions', '''
            <q-td key="perm_actions" :props="props">
                <q-btn flat dense round icon="edit" color="blue" size="sm"
                       @click="$parent.$emit('edit_perm', props.row)">
                    <q-tooltip>编辑权限</q-tooltip>
                </q-btn>
                <q-btn flat dense round icon="delete" color="red" size="sm"
                       @click="$parent.$emit('delete_perm', props.row)">
                    <q-tooltip>删除权限</q-tooltip>
                </q-btn>
            </q-td>
        ''')
        
        # ✅ 添加角色操作列的插槽
        table.add_slot('body-cell-role_actions', '''
            <q-td key="role_actions" :props="props">
                <q-btn flat dense round icon="add_circle" color="purple" size="sm"
                       @click="$parent.$emit('add_role', props.row)">
                    <q-tooltip>添加角色 ({{ props.row.roles }})</q-tooltip>
                </q-btn>
                <q-btn flat dense round icon="remove_circle" color="orange" size="sm"
                       @click="$parent.$emit('remove_role', props.row)">
                    <q-tooltip>删除角色</q-tooltip>
                </q-btn>
            </q-td>
        ''')
        
        # ✅ 添加用户操作列的插槽
        table.add_slot('body-cell-user_actions', '''
            <q-td key="user_actions" :props="props">
                <q-btn flat dense round icon="person_add" color="green" size="sm"
                       @click="$parent.$emit('add_user', props.row)">
                    <q-tooltip>添加用户 ({{ props.row.users }})</q-tooltip>
                </q-btn>
                <q-btn flat dense round icon="person_remove" color="red" size="sm"
                       @click="$parent.$emit('remove_user', props.row)">
                    <q-tooltip>删除用户</q-tooltip>
                </q-btn>
            </q-td>
        ''')
        
        # ✅ 绑定操作事件
        table.on('edit_perm', lambda e: safe(lambda: edit_permission_dialog(e.args)))
        table.on('delete_perm', lambda e: safe(lambda: delete_permission_dialog(e.args)))
        table.on('add_role', lambda e: safe(lambda: manage_permission_roles_dialog(e.args)))
        table.on('remove_role', lambda e: safe(lambda: manage_permission_roles_dialog(e.args)))
        table.on('add_user', lambda e: safe(lambda: manage_permission_users_dialog(e.args)))
        table.on('remove_user', lambda e: safe(lambda: manage_permission_users_dialog(e.args)))

    # ===========================
    # 创建权限对话框
    # ===========================
    
    @safe_protect(name="创建权限对话框")
    def create_permission_dialog():
        """创建权限对话框 - SQLModel 版本"""
        with ui.dialog() as dialog, ui.card().classes('w-96 p-6'):
            ui.label('创建新权限').classes('text-xl font-bold mb-4')
            
            name_input = ui.input(
                label='权限名称', 
                placeholder='如: user.create'
            ).classes('w-full')
            
            display_name_input = ui.input(
                label='显示名称', 
                placeholder='如: 创建用户'
            ).classes('w-full')
            
            category_input = ui.select(
                label='权限分类',
                options=['system', 'user', 'content', 'other'],
                value='other'
            ).classes('w-full')
            
            description_input = ui.textarea(
                label='权限描述',
                placeholder='描述此权限的作用和使用场景...'
            ).classes('w-full')
            
            def submit_create():
                """提交创建 - SQLModel 版本"""
                name = name_input.value.strip()
                display_name = display_name_input.value.strip()
                category = category_input.value
                description = description_input.value.strip() or None
                
                # 验证
                if not name or len(name) < 3:
                    ui.notify('权限名称至少3个字符', type='negative')
                    return
                
                if not display_name:
                    ui.notify('请输入显示名称', type='negative')
                    return
                
                # 创建权限
                with get_db() as session:
                    # 检查权限名是否已存在
                    existing = session.exec(
                        select(Permission).where(Permission.name == name)
                    ).first()
                    
                    if existing:
                        ui.notify('权限名称已存在', type='negative')
                        return
                    
                    # 创建新权限
                    new_permission = Permission(
                        name=name,
                        display_name=display_name,
                        category=category if category != 'other' else None,
                        description=description
                    )
                    
                    session.add(new_permission)
                    
                    log_success(f"权限创建成功: {name}")
                    ui.notify(f'权限 {display_name} 创建成功', type='positive')
                    dialog.close()
                    safe(load_permissions)
            
            with ui.row().classes('w-full justify-end gap-2 mt-6'):
                ui.button('取消', on_click=dialog.close).classes('bg-gray-500 text-white')
                ui.button('创建', on_click=lambda: safe(submit_create)).classes('bg-green-500 text-white')
        
        dialog.open()

    # ===========================
    # 编辑权限对话框
    # ===========================
    
    @safe_protect(name="编辑权限对话框")
    def edit_permission_dialog(row_data):
        """编辑权限对话框 - SQLModel 版本"""
        with ui.dialog() as dialog, ui.card().classes('w-96 p-6'):
            ui.label(f'编辑权限: {row_data["display_name"]}').classes('text-xl font-bold mb-4')
            
            # 加载权限数据
            with get_db() as session:
                perm = session.get(Permission, row_data['id'])
                if not perm:
                    ui.notify('权限不存在', type='negative')
                    return
                
                display_name_input = ui.input(
                    label='显示名称',
                    value=perm.display_name or ''
                ).classes('w-full')
                
                category_input = ui.select(
                    label='权限分类',
                    options=['system', 'user', 'content', 'other'],
                    value=perm.category or 'other'
                ).classes('w-full')
                
                description_input = ui.textarea(
                    label='权限描述',
                    value=perm.description or ''
                ).classes('w-full')
                
                ui.label('⚠️ 权限名称不可修改').classes('text-sm text-orange-500 mt-2')
            
            def submit_edit():
                """提交编辑 - SQLModel 版本"""
                with get_db() as session:
                    permission = session.get(Permission, row_data['id'])
                    if permission:
                        permission.display_name = display_name_input.value.strip()
                        permission.category = category_input.value if category_input.value != 'other' else None
                        permission.description = description_input.value.strip() or None
                        
                        log_info(f"权限更新成功: {permission.name}")
                        ui.notify(f'权限 {permission.display_name} 更新成功', type='positive')
                        dialog.close()
                        safe(load_permissions)
            
            with ui.row().classes('w-full justify-end gap-2 mt-6'):
                ui.button('取消', on_click=dialog.close).classes('bg-gray-500 text-white')
                ui.button('保存', on_click=lambda: safe(submit_edit)).classes('bg-blue-500 text-white')
        
        dialog.open()

    # ===========================
    # 管理权限-角色关联对话框
    # ===========================
    
    @safe_protect(name="管理权限角色对话框")
    def manage_permission_roles_dialog(row_data):
        """管理权限-角色关联对话框 - SQLModel 版本"""
        with ui.dialog() as dialog, ui.card().classes('w-[600px] p-6'):
            ui.label(f'管理角色: {row_data["display_name"]}').classes('text-xl font-bold mb-4')
            
            with get_db() as session:
                permission = session.get(Permission, row_data['id'])
                if not permission:
                    ui.notify('权限不存在', type='negative')
                    return
                
                # 获取所有角色
                all_roles = session.exec(select(Role)).all()
                
                # 当前权限的角色 ID 集合
                current_role_ids = {r.id for r in permission.roles}
                
                # 存储选中的角色
                selected_roles = set(current_role_ids)
                
                # 渲染角色选择器
                ui.label(f'当前已关联 {len(current_role_ids)} 个角色').classes('text-sm text-gray-600 mb-4')
                
                with ui.scroll_area().classes('w-full h-96'):
                    for role in all_roles:
                        is_checked = role.id in current_role_ids
                        
                        def on_change(checked, role_id=role.id):
                            if checked:
                                selected_roles.add(role_id)
                            else:
                                selected_roles.discard(role_id)
                        
                        with ui.card().classes('w-full p-3 mb-2'):
                            with ui.row().classes('w-full items-center justify-between'):
                                with ui.row().classes('items-center gap-3'):
                                    ui.checkbox(
                                        value=is_checked,
                                        on_change=lambda e, rid=role.id: on_change(e.value, rid)
                                    )
                                    
                                    with ui.column().classes('gap-1'):
                                        ui.label(role.display_name or role.name).classes('font-bold')
                                        ui.label(f"@{role.name}").classes('text-xs text-gray-500')
                                
                                # 角色标签
                                if role.is_system:
                                    ui.badge('系统').props('color=blue')
                                elif not role.is_active:
                                    ui.badge('禁用').props('color=orange')
                
                def submit_roles():
                    """提交角色更改 - SQLModel 版本"""
                    with get_db() as session:
                        permission = session.get(Permission, row_data['id'])
                        if permission:
                            # 清空现有角色
                            permission.roles.clear()
                            
                            # 添加新角色
                            for role_id in selected_roles:
                                role = session.get(Role, role_id)
                                if role:
                                    permission.roles.append(role)
                            
                            log_success(f"权限角色更新成功: {permission.name}, 角色数: {len(selected_roles)}")
                            ui.notify(f'权限 {permission.display_name} 角色已更新', type='positive')
                            dialog.close()
                            safe(load_permissions)
                
                with ui.row().classes('w-full justify-end gap-2 mt-6'):
                    ui.button('取消', on_click=dialog.close).classes('bg-gray-500 text-white')
                    ui.button('保存', on_click=lambda: safe(submit_roles)).classes('bg-purple-500 text-white')
        
        dialog.open()

    # ===========================
    # 管理权限-用户关联对话框
    # ===========================
    
    @safe_protect(name="管理权限用户对话框")
    def manage_permission_users_dialog(row_data):
        """管理权限-用户直接关联对话框 - SQLModel 版本"""
        with ui.dialog() as dialog, ui.card().classes('w-[600px] p-6'):
            ui.label(f'管理直接用户: {row_data["display_name"]}').classes('text-xl font-bold mb-4')
            ui.label('为用户直接分配权限(不通过角色)').classes('text-sm text-gray-600 mb-4')
            
            with get_db() as session:
                permission = session.get(Permission, row_data['id'])
                if not permission:
                    ui.notify('权限不存在', type='negative')
                    return
                
                # 获取所有用户
                all_users = session.exec(select(User)).all()
                
                # 当前权限的直接用户 ID 集合
                current_user_ids = {u.id for u in permission.users}
                
                # 存储选中的用户
                selected_users = set(current_user_ids)
                
                # 渲染用户选择器
                ui.label(f'当前已直接关联 {len(current_user_ids)} 个用户').classes('text-sm text-gray-600 mb-4')
                
                with ui.scroll_area().classes('w-full h-96'):
                    for user in all_users:
                        is_checked = user.id in current_user_ids
                        
                        def on_change(checked, user_id=user.id):
                            if checked:
                                selected_users.add(user_id)
                            else:
                                selected_users.discard(user_id)
                        
                        with ui.card().classes('w-full p-3 mb-2'):
                            with ui.row().classes('w-full items-center justify-between'):
                                with ui.row().classes('items-center gap-3'):
                                    ui.checkbox(
                                        value=is_checked,
                                        on_change=lambda e, uid=user.id: on_change(e.value, uid)
                                    )
                                    
                                    with ui.column().classes('gap-1'):
                                        ui.label(user.username).classes('font-bold')
                                        ui.label(user.email).classes('text-xs text-gray-500')
                                
                                # 用户状态
                                if user.is_superuser:
                                    ui.badge('超管').props('color=red')
                                elif not user.is_active:
                                    ui.badge('禁用').props('color=orange')
                                else:
                                    ui.badge('正常').props('color=green')
                
                def submit_users():
                    """提交用户更改 - SQLModel 版本"""
                    with get_db() as session:
                        permission = session.get(Permission, row_data['id'])
                        if permission:
                            # 清空现有直接用户
                            permission.users.clear()
                            
                            # 添加新用户
                            for user_id in selected_users:
                                user = session.get(User, user_id)
                                if user:
                                    permission.users.append(user)
                            
                            log_success(f"权限直接用户更新成功: {permission.name}, 用户数: {len(selected_users)}")
                            ui.notify(f'权限 {permission.display_name} 直接用户已更新', type='positive')
                            dialog.close()
                            safe(load_permissions)
                
                with ui.row().classes('w-full justify-end gap-2 mt-6'):
                    ui.button('取消', on_click=dialog.close).classes('bg-gray-500 text-white')
                    ui.button('保存', on_click=lambda: safe(submit_users)).classes('bg-green-500 text-white')
        
        dialog.open()

    # ===========================
    # 删除权限对话框
    # ===========================
    
    @safe_protect(name="删除权限对话框")
    def delete_permission_dialog(row_data):
        """删除权限对话框 - SQLModel 版本"""
        with ui.dialog() as dialog, ui.card().classes('w-96 p-6'):
            ui.label(f'删除权限: {row_data["display_name"]}').classes('text-xl font-bold text-red-600 mb-4')
            ui.label('此操作将移除所有角色和用户的该权限关联,且不可撤销。').classes('text-sm text-red-500 mt-2')
            
            # 二次确认
            confirm_input = ui.input(
                label=f'请输入权限名 "{row_data["name"]}" 以确认删除',
                placeholder=row_data["name"]
            ).classes('w-full mt-4')
            
            def submit_delete():
                """提交删除 - SQLModel 版本"""
                if confirm_input.value != row_data["name"]:
                    ui.notify('权限名不匹配,删除取消', type='negative')
                    return
                
                with get_db() as session:
                    permission = session.get(Permission, row_data['id'])
                    if permission:
                        perm_name = permission.display_name or permission.name
                        session.delete(permission)
                        
                        log_warning(f"权限已删除: {permission.name}")
                        ui.notify(f'权限 {perm_name} 已删除', type='warning')
                        dialog.close()
                        safe(load_permissions)
            
            with ui.row().classes('w-full justify-end gap-2 mt-6'):
                ui.button('取消', on_click=dialog.close).classes('bg-gray-500 text-white')
                ui.button('确认删除', on_click=lambda: safe(submit_delete)).classes('bg-red-500 text-white')
        
        dialog.open()

    # 初始加载
    safe(load_permissions)
    log_success("===权限管理页面加载完成===")
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
角色管理页面 - 优化版本
使用 ui.table 展示角色,包含完整的操作和用户关联管理功能
"""
from nicegui import ui
from sqlmodel import Session, select, func
from datetime import datetime
import io
import csv

# 导入模型和数据库
from ..models import Role, User, Permission
from ..database import get_db
from ..decorators import require_role
from ..auth_manager import auth_manager

# 导入日志处理
from common.log_handler import (
    log_trace, log_debug, log_info, log_success, 
    log_warning, log_error, log_critical,
    safe, db_safe, safe_protect, catch, get_logger
)

logger = get_logger(__file__)


@require_role('admin')
@safe_protect(name="角色管理页面", error_msg="角色管理页面加载失败,请稍后重试")
def role_management_page_content():
    """角色管理页面内容 - 仅管理员可访问"""
    
    # 页面标题
    with ui.column().classes('w-full mb-6'):
        ui.label('角色管理').classes('text-4xl font-bold text-purple-800 dark:text-purple-200 mb-2')
        ui.label('管理系统角色和权限分配,支持用户关联管理').classes('text-lg text-gray-600 dark:text-gray-400')

    # ===========================
    # 统计数据加载
    # ===========================
    
    def load_role_statistics():
        """加载角色统计数据 - SQLModel 版本"""
        with get_db() as session:
            total_roles = session.exec(
                select(func.count()).select_from(Role)
            ).one()
            
            active_roles = session.exec(
                select(func.count()).select_from(Role).where(Role.is_active == True)
            ).one()
            
            system_roles = session.exec(
                select(func.count()).select_from(Role).where(Role.is_system == True)
            ).one()
            
            total_users = session.exec(
                select(func.count()).select_from(User)
            ).one()
            
            return {
                'total_roles': total_roles,
                'active_roles': active_roles,
                'system_roles': system_roles,
                'total_users': total_users
            }
    
    # 安全执行统计数据加载
    stats = safe(
        load_role_statistics,
        return_value={'total_roles': 0, 'active_roles': 0, 'system_roles': 0, 'total_users': 0},
        error_msg="角色统计数据加载失败"
    )

    # ===========================
    # 统计卡片区域
    # ===========================
    
    with ui.row().classes('w-full gap-6 mb-8'):
        with ui.card().classes('flex-1 p-6 bg-gradient-to-br from-purple-500 to-purple-600 text-white shadow-lg'):
            with ui.row().classes('items-center justify-between w-full'):
                with ui.column().classes('gap-1'):
                    ui.label('总角色数').classes('text-sm opacity-90 font-medium')
                    ui.label(str(stats['total_roles'])).classes('text-3xl font-bold')
                ui.icon('group_work').classes('text-4xl opacity-80')

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
                ui.icon('security').classes('text-4xl opacity-80')

        with ui.card().classes('flex-1 p-6 bg-gradient-to-br from-orange-500 to-orange-600 text-white shadow-lg'):
            with ui.row().classes('items-center justify-between w-full'):
                with ui.column().classes('gap-1'):
                    ui.label('总用户数').classes('text-sm opacity-90 font-medium')
                    ui.label(str(stats['total_users'])).classes('text-3xl font-bold')
                ui.icon('group').classes('text-4xl opacity-80')

    # ===========================
    # 操作区域
    # ===========================
    
    with ui.card().classes('w-full mb-6'):
        with ui.row().classes('w-full items-center gap-4 p-4'):
            # ✅ 搜索框
            search_input = ui.input(
                label='搜索角色',
                placeholder='输入角色名称或显示名称...'
            ).classes('flex-1')
            
            ui.button(
                '搜索',
                icon='search',
                on_click=lambda: safe(load_roles)
            ).classes('bg-blue-500 text-white')
            
            ui.button(
                '创建角色', 
                icon='add_circle',
                on_click=lambda: safe(create_role_dialog)
            ).classes('bg-purple-500 text-white')
            
            ui.button(
                '刷新', 
                icon='refresh',
                on_click=lambda: safe(load_roles)
            ).classes('bg-gray-500 text-white')
            
            ui.button(
                '导出角色', 
                icon='download',
                on_click=lambda: safe(export_roles)
            ).classes('bg-blue-500 text-white')

    # ===========================
    # 角色列表表格
    # ===========================
    
    # 创建表格容器
    table_container = ui.column().classes('w-full')
    
    @safe_protect(name="加载角色列表")
    def load_roles():
        """加载角色列表 - SQLModel 版本,使用 ui.table"""
        table_container.clear()
        
        with table_container:
            with get_db() as session:
                # 构建查询
                stmt = select(Role)
                
                # ✅ 搜索过滤 - 支持角色名称和显示名称
                if search_input.value:
                    search_term = search_input.value.strip()
                    stmt = stmt.where(
                        (Role.name.contains(search_term)) |
                        (Role.display_name.contains(search_term))
                    )
                
                # 排序
                stmt = stmt.order_by(Role.created_at.desc())
                
                # 执行查询
                roles = session.exec(stmt).all()
                
                log_info(f"查询到 {len(roles)} 个角色")
                
                # 表格列定义
                columns = [
                    {'name': 'id', 'label': 'ID', 'field': 'id', 'align': 'left', 'sortable': True},
                    {'name': 'name', 'label': '角色名称', 'field': 'name', 'align': 'left', 'sortable': True},
                    {'name': 'display_name', 'label': '显示名称', 'field': 'display_name', 'align': 'left'},
                    {'name': 'description', 'label': '描述', 'field': 'description', 'align': 'left'},
                    {'name': 'permissions', 'label': '权限数', 'field': 'permissions', 'align': 'center', 'sortable': True},
                    {'name': 'users', 'label': '用户数', 'field': 'users', 'align': 'center', 'sortable': True},
                    {'name': 'status', 'label': '状态', 'field': 'status', 'align': 'center'},
                    {'name': 'actions', 'label': '操作', 'field': 'actions', 'align': 'center'},
                    {'name': 'user_actions', 'label': '用户关联', 'field': 'user_actions', 'align': 'center'},
                ]
                
                # 转换为表格数据
                rows = []
                for role in roles:
                    # 计算权限和用户数量
                    permission_count = len(role.permissions)
                    user_count = len(role.users)
                    
                    # 判断角色状态
                    if role.is_system:
                        status = '🔒 系统角色'
                        status_color = 'blue'
                    elif not role.is_active:
                        status = '❌ 已禁用'
                        status_color = 'orange'
                    else:
                        status = '✅ 正常'
                        status_color = 'green'
                    
                    rows.append({
                        'id': role.id,
                        'name': role.name,
                        'display_name': role.display_name or '-',
                        'description': role.description or '-',
                        'permissions': permission_count,
                        'users': user_count,
                        'status': status,
                        'status_color': status_color,
                        'is_system': role.is_system,
                        'is_active': role.is_active,
                    })
                
                # ✅ 渲染带分页的表格
                table = ui.table(
                    columns=columns,
                    rows=rows,
                    row_key='id',
                    pagination={'rowsPerPage': 10, 'sortBy': 'id', 'descending': True},
                    column_defaults={
                        'align': 'left',
                        'headerClasses': 'uppercase text-primary text-base font-bold',
                        'classes': 'text-base'
                    }
                ).classes('w-full')
                
                # ✅ 添加状态列的插槽
                table.add_slot('body-cell-status', '''
                    <q-td key="status" :props="props">
                        <q-badge :color="props.row.status_color">
                            {{ props.row.status }}
                        </q-badge>
                    </q-td>
                ''')
                
                # ✅ 添加操作列的插槽 (查看、编辑、删除)
                table.add_slot('body-cell-actions', '''
                    <q-td key="actions" :props="props">
                        <q-btn flat dense round icon="visibility" color="blue" size="sm"
                               @click="$parent.$emit('view', props.row)">
                            <q-tooltip>查看详情</q-tooltip>
                        </q-btn>
                        <q-btn flat dense round icon="edit" color="purple" size="sm"
                               @click="$parent.$emit('edit', props.row)">
                            <q-tooltip>编辑</q-tooltip>
                        </q-btn>
                        <q-btn flat dense round icon="vpn_key" color="indigo" size="sm"
                               @click="$parent.$emit('permissions', props.row)">
                            <q-tooltip>管理权限</q-tooltip>
                        </q-btn>
                        <q-btn v-if="!props.row.is_system" flat dense round icon="delete" color="red" size="sm"
                               @click="$parent.$emit('delete', props.row)">
                            <q-tooltip>删除</q-tooltip>
                        </q-btn>
                    </q-td>
                ''')
                
                # ✅ 添加用户关联列的插槽 (添加用户、批量删除、批量管理、用户列表)
                table.add_slot('body-cell-user_actions', '''
                    <q-td key="user_actions" :props="props">
                        <q-btn flat dense round icon="person_add" color="green" size="sm"
                               @click="$parent.$emit('add_user', props.row)">
                            <q-tooltip>添加用户</q-tooltip>
                        </q-btn>
                        <q-btn flat dense round icon="people" color="blue" size="sm"
                               @click="$parent.$emit('user_list', props.row)">
                            <q-tooltip>用户列表 ({{ props.row.users }})</q-tooltip>
                        </q-btn>
                        <q-btn flat dense round icon="group_remove" color="orange" size="sm"
                               @click="$parent.$emit('batch_remove', props.row)">
                            <q-tooltip>批量移除</q-tooltip>
                        </q-btn>
                        <q-btn flat dense round icon="manage_accounts" color="purple" size="sm"
                               @click="$parent.$emit('batch_manage', props.row)">
                            <q-tooltip>批量管理</q-tooltip>
                        </q-btn>
                    </q-td>
                ''')
                
                # ✅ 绑定操作事件
                table.on('view', lambda e: safe(lambda: view_role_dialog(e.args)))
                table.on('edit', lambda e: safe(lambda: edit_role_dialog(e.args)))
                table.on('permissions', lambda e: safe(lambda: manage_role_permissions_dialog(e.args)))
                table.on('delete', lambda e: safe(lambda: delete_role_dialog(e.args)))
                
                # ✅ 绑定用户关联事件
                table.on('add_user', lambda e: safe(lambda: add_user_to_role_dialog(e.args)))
                table.on('user_list', lambda e: safe(lambda: view_role_users_dialog(e.args)))
                table.on('batch_remove', lambda e: safe(lambda: batch_remove_users_dialog(e.args)))
                table.on('batch_manage', lambda e: safe(lambda: batch_manage_users_dialog(e.args)))

    # ===========================
    # 创建角色对话框
    # ===========================
    
    @safe_protect(name="创建角色对话框")
    def create_role_dialog():
        """创建角色对话框 - SQLModel 版本"""
        with ui.dialog() as dialog, ui.card().classes('w-96 p-6'):
            ui.label('创建新角色').classes('text-xl font-bold mb-4')
            
            name_input = ui.input(
                label='角色名称', 
                placeholder='小写字母下划线,如: editor'
            ).classes('w-full')
            
            display_name_input = ui.input(
                label='显示名称', 
                placeholder='如: 编辑者'
            ).classes('w-full')
            
            description_input = ui.textarea(
                label='角色描述',
                placeholder='描述此角色的职责和权限范围...'
            ).classes('w-full')
            
            is_active_checkbox = ui.checkbox('启用角色', value=True).classes('mb-2')
            
            def submit_create():
                """提交创建 - SQLModel 版本"""
                name = name_input.value.strip()
                display_name = display_name_input.value.strip()
                description = description_input.value.strip() or None
                is_active = is_active_checkbox.value
                
                # 验证
                if not name or len(name) < 2:
                    ui.notify('角色名称至少2个字符', type='negative')
                    return
                
                if not display_name:
                    ui.notify('请输入显示名称', type='negative')
                    return
                
                # 创建角色
                with get_db() as session:
                    # 检查角色名是否已存在
                    existing = session.exec(
                        select(Role).where(Role.name == name)
                    ).first()
                    
                    if existing:
                        ui.notify('角色名称已存在', type='negative')
                        return
                    
                    # 创建新角色
                    new_role = Role(
                        name=name,
                        display_name=display_name,
                        description=description,
                        is_active=is_active,
                        is_system=False
                    )
                    
                    session.add(new_role)
                    
                    log_success(f"角色创建成功: {name}")
                    ui.notify(f'角色 {display_name} 创建成功', type='positive')
                    dialog.close()
                    safe(load_roles)
            
            with ui.row().classes('w-full justify-end gap-2 mt-6'):
                ui.button('取消', on_click=dialog.close).classes('bg-gray-500 text-white')
                ui.button('创建', on_click=lambda: safe(submit_create)).classes('bg-purple-500 text-white')
        
        dialog.open()

    # ===========================
    # 查看角色详情对话框
    # ===========================
    
    @safe_protect(name="查看角色详情对话框")
    def view_role_dialog(row_data):
        """查看角色详情对话框"""
        with ui.dialog() as dialog, ui.card().classes('w-[600px] p-6'):
            ui.label(f'角色详情: {row_data["display_name"]}').classes('text-xl font-bold mb-4')
            
            with get_db() as session:
                role = session.get(Role, row_data['id'])
                if not role:
                    ui.notify('角色不存在', type='negative')
                    return
                
                # 基本信息
                with ui.card().classes('w-full p-4 mb-4 bg-purple-50 dark:bg-purple-900/20'):
                    ui.label('基本信息').classes('text-lg font-semibold mb-2')
                    
                    with ui.grid(columns=2).classes('w-full gap-4'):
                        with ui.column():
                            ui.label('角色名称').classes('text-sm text-gray-600')
                            ui.label(role.name).classes('text-base font-semibold')
                        
                        with ui.column():
                            ui.label('显示名称').classes('text-sm text-gray-600')
                            ui.label(role.display_name or '-').classes('text-base font-semibold')
                    
                    with ui.column().classes('w-full mt-2'):
                        ui.label('描述').classes('text-sm text-gray-600')
                        ui.label(role.description or '无描述').classes('text-base')
                    
                    with ui.row().classes('w-full gap-4 mt-2'):
                        if role.is_system:
                            ui.badge('系统角色', color='blue')
                        if role.is_active:
                            ui.badge('已启用', color='green')
                        else:
                            ui.badge('已禁用', color='orange')
                
                # 统计信息
                with ui.card().classes('w-full p-4 mb-4 bg-blue-50 dark:bg-blue-900/20'):
                    ui.label('统计信息').classes('text-lg font-semibold mb-2')
                    
                    with ui.row().classes('w-full gap-6'):
                        with ui.column().classes('items-center'):
                            ui.icon('security').classes('text-3xl text-purple-500')
                            ui.label(str(len(role.permissions))).classes('text-2xl font-bold')
                            ui.label('权限数').classes('text-sm text-gray-600')
                        
                        with ui.column().classes('items-center'):
                            ui.icon('group').classes('text-3xl text-blue-500')
                            ui.label(str(len(role.users))).classes('text-2xl font-bold')
                            ui.label('用户数').classes('text-sm text-gray-600')
                
                # 权限列表
                with ui.card().classes('w-full p-4 bg-green-50 dark:bg-green-900/20'):
                    ui.label(f'权限列表 ({len(role.permissions)})').classes('text-lg font-semibold mb-2')
                    
                    if not role.permissions:
                        ui.label('暂无权限').classes('text-gray-500 text-center py-4')
                    else:
                        # 按分类组织权限
                        permissions_by_category = {}
                        for perm in role.permissions:
                            category = perm.category or '其他'
                            if category not in permissions_by_category:
                                permissions_by_category[category] = []
                            permissions_by_category[category].append(perm)
                        
                        with ui.scroll_area().classes('w-full h-48'):
                            for category, perms in sorted(permissions_by_category.items()):
                                ui.label(category).classes('text-sm font-semibold text-purple-700 mt-2')
                                for perm in perms:
                                    with ui.row().classes('items-center gap-2 ml-4'):
                                        ui.icon('check_circle', size='xs').classes('text-green-500')
                                        ui.label(perm.display_name or perm.name).classes('text-sm')
            
            with ui.row().classes('w-full justify-end gap-2 mt-4'):
                ui.button('关闭', on_click=dialog.close).classes('bg-gray-500 text-white')
                ui.button(
                    '编辑',
                    icon='edit',
                    on_click=lambda: (dialog.close(), safe(lambda: edit_role_dialog(row_data)))
                ).classes('bg-purple-500 text-white')
        
        dialog.open()

    # ===========================
    # 编辑角色对话框
    # ===========================
    
    @safe_protect(name="编辑角色对话框")
    def edit_role_dialog(row_data):
        """编辑角色对话框 - SQLModel 版本"""
        with ui.dialog() as dialog, ui.card().classes('w-96 p-6'):
            ui.label(f'编辑角色: {row_data["display_name"]}').classes('text-xl font-bold mb-4')
            
            # 加载角色数据
            with get_db() as session:
                role = session.get(Role, row_data['id'])
                if not role:
                    ui.notify('角色不存在', type='negative')
                    return
                
                display_name_input = ui.input(
                    label='显示名称',
                    value=role.display_name or ''
                ).classes('w-full')
                
                description_input = ui.textarea(
                    label='角色描述',
                    value=role.description or ''
                ).classes('w-full')
                
                is_active_checkbox = ui.checkbox('启用角色', value=role.is_active).classes('mb-2')
                
                if role.is_system:
                    ui.label('⚠️ 系统角色,部分字段不可修改').classes('text-sm text-orange-500 mt-2')
            
            def submit_edit():
                """提交编辑 - SQLModel 版本"""
                with get_db() as session:
                    role = session.get(Role, row_data['id'])
                    if role:
                        role.display_name = display_name_input.value.strip()
                        role.description = description_input.value.strip() or None
                        
                        # 系统角色不能禁用
                        if not role.is_system:
                            role.is_active = is_active_checkbox.value
                        
                        log_info(f"角色更新成功: {role.name}")
                        ui.notify(f'角色 {role.display_name} 更新成功', type='positive')
                        dialog.close()
                        safe(load_roles)
            
            with ui.row().classes('w-full justify-end gap-2 mt-6'):
                ui.button('取消', on_click=dialog.close).classes('bg-gray-500 text-white')
                ui.button('保存', on_click=lambda: safe(submit_edit)).classes('bg-blue-500 text-white')
        
        dialog.open()

    # ===========================
    # 管理角色权限对话框
    # ===========================
    
    @safe_protect(name="管理角色权限对话框")
    def manage_role_permissions_dialog(row_data):
        """管理角色权限对话框 - SQLModel 版本"""
        with ui.dialog() as dialog, ui.card().classes('w-[600px] p-6'):
            ui.label(f'管理权限: {row_data["display_name"]}').classes('text-xl font-bold mb-4')
            
            with get_db() as session:
                role = session.get(Role, row_data['id'])
                if not role:
                    ui.notify('角色不存在', type='negative')
                    return
                
                # 获取所有权限
                all_permissions = session.exec(select(Permission)).all()
                
                # 当前角色的权限 ID 集合
                current_permission_ids = {p.id for p in role.permissions}
                
                # 按分类组织权限
                permissions_by_category = {}
                for perm in all_permissions:
                    category = perm.category or '其他'
                    if category not in permissions_by_category:
                        permissions_by_category[category] = []
                    permissions_by_category[category].append(perm)
                
                # 存储选中的权限
                selected_permissions = set(current_permission_ids)
                
                # 渲染权限选择器
                ui.label(f'当前已关联 {len(current_permission_ids)} 个权限').classes('text-sm text-gray-600 mb-4')
                
                with ui.scroll_area().classes('w-full h-96'):
                    for category, perms in sorted(permissions_by_category.items()):
                        with ui.expansion(category, icon='folder').classes('w-full mb-2'):
                            for perm in perms:
                                is_checked = perm.id in current_permission_ids
                                
                                def on_change(checked, perm_id=perm.id):
                                    if checked:
                                        selected_permissions.add(perm_id)
                                    else:
                                        selected_permissions.discard(perm_id)
                                
                                with ui.row().classes('w-full items-center'):
                                    ui.checkbox(
                                        text=f"{perm.display_name or perm.name} ({perm.name})",
                                        value=is_checked,
                                        on_change=lambda e, pid=perm.id: on_change(e.value, pid)
                                    ).classes('flex-1')
                                    
                                    if perm.description:
                                        ui.icon('info').classes('text-gray-400').tooltip(perm.description)
                
                def submit_permissions():
                    """提交权限更改 - SQLModel 版本"""
                    with get_db() as session:
                        role = session.get(Role, row_data['id'])
                        if role:
                            # 清空现有权限
                            role.permissions.clear()
                            
                            # 添加新权限
                            for perm_id in selected_permissions:
                                perm = session.get(Permission, perm_id)
                                if perm:
                                    role.permissions.append(perm)
                            
                            log_success(f"角色权限更新成功: {role.name}, 权限数: {len(selected_permissions)}")
                            ui.notify(f'角色 {role.display_name} 权限已更新', type='positive')
                            dialog.close()
                            safe(load_roles)
                
                with ui.row().classes('w-full justify-end gap-2 mt-6'):
                    ui.button('取消', on_click=dialog.close).classes('bg-gray-500 text-white')
                    ui.button('保存', on_click=lambda: safe(submit_permissions)).classes('bg-purple-500 text-white')
        
        dialog.open()

    # ===========================
    # 添加用户到角色对话框
    # ===========================
    
    @safe_protect(name="添加用户到角色对话框")
    def add_user_to_role_dialog(row_data):
        """添加用户到角色对话框"""
        with ui.dialog() as dialog, ui.card().classes('w-[500px] p-6'):
            ui.label(f'添加用户: {row_data["display_name"]}').classes('text-xl font-bold mb-4')
            
            with get_db() as session:
                role = session.get(Role, row_data['id'])
                if not role:
                    ui.notify('角色不存在', type='negative')
                    return
                
                # 获取所有用户
                all_users = session.exec(select(User)).all()
                
                # 当前角色的用户 ID 集合
                current_user_ids = {u.id for u in role.users}
                
                # 可添加的用户(不在角色中的用户)
                available_users = [u for u in all_users if u.id not in current_user_ids]
                
                if not available_users:
                    ui.label('所有用户都已添加到此角色').classes('text-gray-500 text-center py-8')
                else:
                    ui.label(f'可添加 {len(available_users)} 个用户').classes('text-sm text-gray-600 mb-4')
                    
                    # 搜索框
                    search_input = ui.input(
                        label='搜索用户',
                        placeholder='输入用户名或邮箱...'
                    ).classes('w-full mb-4')
                    
                    # 存储选中的用户
                    selected_users = set()
                    
                    # 用户列表容器
                    user_list_container = ui.column().classes('w-full')
                    
                    def render_user_list():
                        """渲染用户列表"""
                        user_list_container.clear()
                        
                        # 搜索过滤
                        search_term = search_input.value.strip().lower() if search_input.value else ''
                        filtered_users = [
                            u for u in available_users
                            if not search_term or 
                            search_term in u.username.lower() or 
                            search_term in u.email.lower()
                        ]
                        
                        with user_list_container:
                            with ui.scroll_area().classes('w-full h-96'):
                                for user in filtered_users:
                                    def on_change(checked, user_id=user.id):
                                        if checked:
                                            selected_users.add(user_id)
                                        else:
                                            selected_users.discard(user_id)
                                    
                                    with ui.card().classes('w-full p-3 mb-2'):
                                        with ui.row().classes('w-full items-center justify-between'):
                                            with ui.row().classes('items-center gap-3'):
                                                ui.checkbox(
                                                    value=False,
                                                    on_change=lambda e, uid=user.id: on_change(e.value, uid)
                                                )
                                                
                                                with ui.column().classes('gap-1'):
                                                    ui.label(user.username).classes('font-bold')
                                                    ui.label(user.email).classes('text-xs text-gray-500')
                                            
                                            # 用户状态
                                            if user.is_superuser:
                                                ui.badge('超管', color='red')
                                            elif user.is_active:
                                                ui.badge('正常', color='green')
                                            else:
                                                ui.badge('禁用', color='orange')
                    
                    # 绑定搜索事件
                    search_input.on('input', render_user_list)
                    
                    # 初始渲染
                    render_user_list()
                    
                    def submit_add():
                        """提交添加用户"""
                        if not selected_users:
                            ui.notify('请至少选择一个用户', type='warning')
                            return
                        
                        with get_db() as session:
                            role = session.get(Role, row_data['id'])
                            if role:
                                # 添加新用户
                                for user_id in selected_users:
                                    user = session.get(User, user_id)
                                    if user and user not in role.users:
                                        role.users.append(user)
                                
                                log_success(f"角色添加用户成功: {role.name}, 添加数: {len(selected_users)}")
                                ui.notify(f'成功添加 {len(selected_users)} 个用户到角色 {role.display_name}', type='positive')
                                dialog.close()
                                safe(load_roles)
                    
                    with ui.row().classes('w-full justify-end gap-2 mt-6'):
                        ui.button('取消', on_click=dialog.close).classes('bg-gray-500 text-white')
                        ui.button('添加', on_click=lambda: safe(submit_add)).classes('bg-green-500 text-white')
        
        dialog.open()

    # ===========================
    # 查看角色用户列表对话框
    # ===========================
    
    @safe_protect(name="查看角色用户列表对话框")
    def view_role_users_dialog(row_data):
        """查看角色用户列表对话框 - SQLModel 版本"""
        with ui.dialog() as dialog, ui.card().classes('w-[600px] p-6'):
            ui.label(f'用户列表: {row_data["display_name"]}').classes('text-xl font-bold mb-4')
            
            with get_db() as session:
                role = session.get(Role, row_data['id'])
                if not role:
                    ui.notify('角色不存在', type='negative')
                    return
                
                users = role.users
                
                if not users:
                    ui.label('此角色暂无用户').classes('text-gray-500 text-center py-8')
                else:
                    ui.label(f'共 {len(users)} 个用户').classes('text-sm text-gray-600 mb-4')
                    
                    # 搜索框
                    search_input = ui.input(
                        label='搜索用户',
                        placeholder='输入用户名或邮箱...'
                    ).classes('w-full mb-4')
                    
                    # 用户列表容器
                    user_list_container = ui.column().classes('w-full')
                    
                    def render_user_list():
                        """渲染用户列表"""
                        user_list_container.clear()
                        
                        # 搜索过滤
                        search_term = search_input.value.strip().lower() if search_input.value else ''
                        filtered_users = [
                            u for u in users
                            if not search_term or 
                            search_term in u.username.lower() or 
                            search_term in u.email.lower()
                        ]
                        
                        with user_list_container:
                            with ui.scroll_area().classes('w-full h-96'):
                                for user in filtered_users:
                                    with ui.card().classes('w-full p-4 mb-2'):
                                        with ui.row().classes('w-full items-center justify-between'):
                                            with ui.column().classes('gap-1'):
                                                ui.label(user.username).classes('font-bold')
                                                ui.label(user.email).classes('text-sm text-gray-500')
                                            
                                            with ui.row().classes('gap-2'):
                                                # 用户状态
                                                if user.is_superuser:
                                                    ui.badge('超管', color='red')
                                                elif user.is_active:
                                                    ui.badge('正常', color='green')
                                                else:
                                                    ui.badge('禁用', color='orange')
                                                
                                                # 移除按钮
                                                ui.button(
                                                    icon='person_remove',
                                                    on_click=lambda u=user: safe(lambda: remove_user_from_role(role.id, u.id))
                                                ).props('flat dense round size=sm color=red').tooltip('从角色移除')
                    
                    # 绑定搜索事件
                    search_input.on('input', render_user_list)
                    
                    # 初始渲染
                    render_user_list()
                    
                    def remove_user_from_role(role_id, user_id):
                        """从角色移除用户"""
                        with get_db() as session:
                            role = session.get(Role, role_id)
                            user = session.get(User, user_id)
                            if role and user:
                                if user in role.users:
                                    role.users.remove(user)
                                    log_info(f"从角色移除用户: {user.username} -> {role.name}")
                                    ui.notify(f'用户 {user.username} 已从角色移除', type='positive')
                                    render_user_list()
                                    safe(load_roles)
                
                with ui.row().classes('w-full justify-end gap-2 mt-6'):
                    ui.button('关闭', on_click=dialog.close).classes('bg-gray-500 text-white')
        
        dialog.open()

    # ===========================
    # 批量移除用户对话框
    # ===========================
    
    @safe_protect(name="批量移除用户对话框")
    def batch_remove_users_dialog(row_data):
        """批量移除用户对话框"""
        with ui.dialog() as dialog, ui.card().classes('w-[500px] p-6'):
            ui.label(f'批量移除: {row_data["display_name"]}').classes('text-xl font-bold mb-4')
            
            with get_db() as session:
                role = session.get(Role, row_data['id'])
                if not role:
                    ui.notify('角色不存在', type='negative')
                    return
                
                users = role.users
                
                if not users:
                    ui.label('此角色暂无用户').classes('text-gray-500 text-center py-8')
                else:
                    ui.label(f'选择要移除的用户 (共 {len(users)} 个)').classes('text-sm text-gray-600 mb-4')
                    
                    # 存储选中的用户
                    selected_users = set()
                    
                    with ui.scroll_area().classes('w-full h-96'):
                        for user in users:
                            def on_change(checked, user_id=user.id):
                                if checked:
                                    selected_users.add(user_id)
                                else:
                                    selected_users.discard(user_id)
                            
                            with ui.card().classes('w-full p-3 mb-2'):
                                with ui.row().classes('w-full items-center justify-between'):
                                    with ui.row().classes('items-center gap-3'):
                                        ui.checkbox(
                                            value=False,
                                            on_change=lambda e, uid=user.id: on_change(e.value, uid)
                                        )
                                        
                                        with ui.column().classes('gap-1'):
                                            ui.label(user.username).classes('font-bold')
                                            ui.label(user.email).classes('text-xs text-gray-500')
                                    
                                    # 用户状态
                                    if user.is_superuser:
                                        ui.badge('超管', color='red')
                                    elif user.is_active:
                                        ui.badge('正常', color='green')
                                    else:
                                        ui.badge('禁用', color='orange')
                    
                    def submit_remove():
                        """提交批量移除"""
                        if not selected_users:
                            ui.notify('请至少选择一个用户', type='warning')
                            return
                        
                        with get_db() as session:
                            role = session.get(Role, row_data['id'])
                            if role:
                                # 移除选中的用户
                                removed_count = 0
                                for user_id in selected_users:
                                    user = session.get(User, user_id)
                                    if user and user in role.users:
                                        role.users.remove(user)
                                        removed_count += 1
                                
                                log_success(f"批量移除用户成功: {role.name}, 移除数: {removed_count}")
                                ui.notify(f'成功从角色 {role.display_name} 移除 {removed_count} 个用户', type='positive')
                                dialog.close()
                                safe(load_roles)
                    
                    with ui.row().classes('w-full justify-end gap-2 mt-6'):
                        ui.button('取消', on_click=dialog.close).classes('bg-gray-500 text-white')
                        ui.button('移除', on_click=lambda: safe(submit_remove)).classes('bg-orange-500 text-white')
        
        dialog.open()

    # ===========================
    # 批量管理用户对话框
    # ===========================
    
    @safe_protect(name="批量管理用户对话框")
    def batch_manage_users_dialog(row_data):
        """批量管理用户对话框 - 包含添加和移除"""
        with ui.dialog() as dialog, ui.card().classes('w-[700px] p-6'):
            ui.label(f'批量管理: {row_data["display_name"]}').classes('text-xl font-bold mb-4')
            
            with get_db() as session:
                role = session.get(Role, row_data['id'])
                if not role:
                    ui.notify('角色不存在', type='negative')
                    return
                
                # 获取所有用户
                all_users = session.exec(select(User)).all()
                
                # 当前角色的用户 ID 集合
                current_user_ids = {u.id for u in role.users}
                
                # 存储用户状态变化
                user_changes = {}  # {user_id: True/False} True=添加, False=移除
                
                ui.label(f'管理角色用户 (当前 {len(current_user_ids)} 个)').classes('text-sm text-gray-600 mb-4')
                
                # 搜索框
                search_input = ui.input(
                    label='搜索用户',
                    placeholder='输入用户名或邮箱...'
                ).classes('w-full mb-4')
                
                # 用户列表容器
                user_list_container = ui.column().classes('w-full')
                
                def render_user_list():
                    """渲染用户列表"""
                    user_list_container.clear()
                    
                    # 搜索过滤
                    search_term = search_input.value.strip().lower() if search_input.value else ''
                    filtered_users = [
                        u for u in all_users
                        if not search_term or 
                        search_term in u.username.lower() or 
                        search_term in u.email.lower()
                    ]
                    
                    with user_list_container:
                        with ui.scroll_area().classes('w-full h-96'):
                            for user in filtered_users:
                                # 确定初始状态
                                is_in_role = user.id in current_user_ids
                                
                                def on_change(checked, user_id=user.id, initial=is_in_role):
                                    if checked != initial:
                                        user_changes[user_id] = checked
                                    else:
                                        user_changes.pop(user_id, None)
                                
                                with ui.card().classes('w-full p-3 mb-2'):
                                    with ui.row().classes('w-full items-center justify-between'):
                                        with ui.row().classes('items-center gap-3'):
                                            ui.checkbox(
                                                value=is_in_role,
                                                on_change=lambda e, uid=user.id, init=is_in_role: on_change(e.value, uid, init)
                                            )
                                            
                                            with ui.column().classes('gap-1'):
                                                ui.label(user.username).classes('font-bold')
                                                ui.label(user.email).classes('text-xs text-gray-500')
                                        
                                        with ui.row().classes('gap-2'):
                                            # 用户状态
                                            if user.is_superuser:
                                                ui.badge('超管', color='red')
                                            elif user.is_active:
                                                ui.badge('正常', color='green')
                                            else:
                                                ui.badge('禁用', color='orange')
                                            
                                            # 当前状态
                                            if is_in_role:
                                                ui.badge('已关联', color='blue')
                
                # 绑定搜索事件
                search_input.on('input', render_user_list)
                
                # 初始渲染
                render_user_list()
                
                def submit_batch_manage():
                    """提交批量管理"""
                    if not user_changes:
                        ui.notify('没有变化', type='info')
                        dialog.close()
                        return
                    
                    with get_db() as session:
                        role = session.get(Role, row_data['id'])
                        if role:
                            added_count = 0
                            removed_count = 0
                            
                            for user_id, should_be_in_role in user_changes.items():
                                user = session.get(User, user_id)
                                if user:
                                    if should_be_in_role:
                                        # 添加用户
                                        if user not in role.users:
                                            role.users.append(user)
                                            added_count += 1
                                    else:
                                        # 移除用户
                                        if user in role.users:
                                            role.users.remove(user)
                                            removed_count += 1
                            
                            log_success(f"批量管理用户成功: {role.name}, 添加: {added_count}, 移除: {removed_count}")
                            ui.notify(f'批量管理完成 - 添加 {added_count} 个, 移除 {removed_count} 个', type='positive')
                            dialog.close()
                            safe(load_roles)
                
                with ui.row().classes('w-full justify-end gap-2 mt-6'):
                    ui.button('取消', on_click=dialog.close).classes('bg-gray-500 text-white')
                    ui.button('保存', on_click=lambda: safe(submit_batch_manage)).classes('bg-purple-500 text-white')
        
        dialog.open()

    # ===========================
    # 删除角色对话框
    # ===========================
    
    @safe_protect(name="删除角色对话框")
    def delete_role_dialog(row_data):
        """删除角色对话框 - SQLModel 版本"""
        if row_data['is_system']:
            ui.notify('系统角色不能删除', type='negative')
            return
        
        with ui.dialog() as dialog, ui.card().classes('w-96 p-6'):
            ui.label(f'删除角色: {row_data["display_name"]}').classes('text-xl font-bold text-red-600 mb-4')
            ui.label('此操作将移除所有用户的该角色关联,且不可撤销。').classes('text-sm text-red-500 mt-2')
            
            # 二次确认
            confirm_input = ui.input(
                label=f'请输入角色名 "{row_data["name"]}" 以确认删除',
                placeholder=row_data["name"]
            ).classes('w-full mt-4')
            
            def submit_delete():
                """提交删除 - SQLModel 版本"""
                if confirm_input.value != row_data["name"]:
                    ui.notify('角色名不匹配,删除取消', type='negative')
                    return
                
                with get_db() as session:
                    role = session.get(Role, row_data['id'])
                    if role:
                        role_name = role.display_name
                        session.delete(role)
                        
                        log_warning(f"角色已删除: {role.name}")
                        ui.notify(f'角色 {role_name} 已删除', type='warning')
                        dialog.close()
                        safe(load_roles)
            
            with ui.row().classes('w-full justify-end gap-2 mt-6'):
                ui.button('取消', on_click=dialog.close).classes('bg-gray-500 text-white')
                ui.button('确认删除', on_click=lambda: safe(submit_delete)).classes('bg-red-500 text-white')
        
        dialog.open()

    # ===========================
    # 导出角色功能
    # ===========================
    
    @safe_protect(name="导出角色数据")
    def export_roles():
        """导出角色数据为 CSV"""
        with get_db() as session:
            roles = session.exec(select(Role)).all()
            
            # 创建 CSV
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(['ID', '角色名', '显示名称', '描述', '状态', '系统角色', '权限数', '用户数'])
            
            for role in roles:
                writer.writerow([
                    role.id,
                    role.name,
                    role.display_name or '',
                    role.description or '',
                    '启用' if role.is_active else '禁用',
                    '是' if role.is_system else '否',
                    len(role.permissions),
                    len(role.users)
                ])
            
            ui.notify('角色数据导出功能开发中...', type='info')
            log_info(f"导出了 {len(roles)} 个角色")

    # 初始加载
    safe(load_roles)
    log_success("===角色管理页面加载完成===")
```

- **auth\pages\user_management_page.py**
```python
"""
用户管理页面 - 完整功能版本
包含分页、编辑、角色管理、锁定、重置密码、删除等完整功能
"""
from nicegui import ui
from sqlmodel import Session, select, func
from datetime import datetime, timedelta
import secrets
import string

# 导入模型和数据库
from ..models import User, Role
from ..database import get_db
from ..decorators import require_role
from ..auth_manager import auth_manager
from ..utils import format_datetime, validate_email, validate_username

# 导入日志处理
from common.log_handler import (
    log_trace, log_debug, log_info, log_success, 
    log_warning, log_error, log_critical,
    safe, db_safe, safe_protect, catch, get_logger
)

logger = get_logger(__file__)


@require_role('admin')
@safe_protect(name="用户管理页面", error_msg="用户管理页面加载失败,请稍后重试")
def user_management_page_content():
    """用户管理页面内容 - 仅管理员可访问"""
    
    # 页面标题
    with ui.column().classes('w-full mb-6'):
        ui.label('用户管理').classes('text-4xl font-bold text-blue-800 dark:text-blue-200 mb-2')
        ui.label('管理系统用户账户、角色分配和权限控制').classes('text-lg text-gray-600 dark:text-gray-400')

    # ===========================
    # 统计数据加载
    # ===========================
    
    def load_user_statistics():
        """加载用户统计数据 - SQLModel 版本"""
        with get_db() as session:
            total_users = session.exec(
                select(func.count()).select_from(User)
            ).one()
            
            active_users = session.exec(
                select(func.count()).select_from(User).where(User.is_active == True)
            ).one()
            
            locked_users = session.exec(
                select(func.count()).select_from(User).where(
                    User.locked_until > datetime.now()
                )
            ).one()
            
            superusers = session.exec(
                select(func.count()).select_from(User).where(User.is_superuser == True)
            ).one()
            
            return {
                'total_users': total_users,
                'active_users': active_users,
                'locked_users': locked_users,
                'superusers': superusers
            }
    
    # 安全执行统计数据加载
    stats = safe(
        load_user_statistics,
        return_value={'total_users': 0, 'active_users': 0, 'locked_users': 0, 'superusers': 0},
        error_msg="用户统计数据加载失败"
    )

    # ===========================
    # 统计卡片区域
    # ===========================
    
    with ui.row().classes('w-full gap-6 mb-8'):
        with ui.card().classes('flex-1 p-6 bg-gradient-to-br from-blue-500 to-blue-600 text-white shadow-lg'):
            with ui.row().classes('items-center justify-between w-full'):
                with ui.column().classes('gap-1'):
                    ui.label('总用户数').classes('text-sm opacity-90 font-medium')
                    ui.label(str(stats['total_users'])).classes('text-3xl font-bold')
                ui.icon('group').classes('text-4xl opacity-80')

        with ui.card().classes('flex-1 p-6 bg-gradient-to-br from-green-500 to-green-600 text-white shadow-lg'):
            with ui.row().classes('items-center justify-between w-full'):
                with ui.column().classes('gap-1'):
                    ui.label('活跃用户').classes('text-sm opacity-90 font-medium')
                    ui.label(str(stats['active_users'])).classes('text-3xl font-bold')
                ui.icon('check_circle').classes('text-4xl opacity-80')

        with ui.card().classes('flex-1 p-6 bg-gradient-to-br from-red-500 to-red-600 text-white shadow-lg'):
            with ui.row().classes('items-center justify-between w-full'):
                with ui.column().classes('gap-1'):
                    ui.label('锁定用户').classes('text-sm opacity-90 font-medium')
                    ui.label(str(stats['locked_users'])).classes('text-3xl font-bold')
                ui.icon('lock').classes('text-4xl opacity-80')

        with ui.card().classes('flex-1 p-6 bg-gradient-to-br from-purple-500 to-purple-600 text-white shadow-lg'):
            with ui.row().classes('items-center justify-between w-full'):
                with ui.column().classes('gap-1'):
                    ui.label('管理员').classes('text-sm opacity-90 font-medium')
                    ui.label(str(stats['superusers'])).classes('text-3xl font-bold')
                ui.icon('admin_panel_settings').classes('text-4xl opacity-80')

    # ===========================
    # 搜索和操作区域
    # ===========================
    
    with ui.card().classes('w-full mb-6'):
        with ui.row().classes('w-full items-center gap-4 p-4'):
            search_input = ui.input(
                label='搜索用户', 
                placeholder='输入用户名、邮箱或姓名...'
            ).classes('flex-1')
            
            ui.button(
                '搜索', 
                icon='search',
                on_click=lambda: safe(load_users)
            ).classes('bg-blue-500 text-white')
            
            ui.button(
                '创建用户', 
                icon='person_add',
                on_click=lambda: safe(create_user_dialog)
            ).classes('bg-green-500 text-white')
            
            ui.button(
                '刷新', 
                icon='refresh',
                on_click=lambda: safe(load_users)
            ).classes('bg-gray-500 text-white')

    # ===========================
    # 用户列表表格
    # ===========================
    
    # 创建表格容器
    table_container = ui.column().classes('w-full')
    
    @safe_protect(name="加载用户列表")
    def load_users():
        """加载用户列表 - SQLModel 版本,带分页"""
        table_container.clear()
        
        with table_container:
            with get_db() as session:
                # 构建查询
                stmt = select(User)
                
                # 搜索过滤
                if search_input.value:
                    search_term = search_input.value.strip()
                    stmt = stmt.where(
                        (User.username.contains(search_term)) |
                        (User.email.contains(search_term)) |
                        (User.full_name.contains(search_term))
                    )
                
                # 排序
                stmt = stmt.order_by(User.created_at.desc())
                
                # 执行查询
                users = session.exec(stmt).all()
                
                log_info(f"查询到 {len(users)} 个用户")
                
                # 表格列定义
                columns = [
                    {'name': 'id', 'label': 'ID', 'field': 'id', 'align': 'left', 'sortable': True},
                    {'name': 'username', 'label': '用户名', 'field': 'username', 'align': 'left', 'sortable': True},
                    {'name': 'email', 'label': '邮箱', 'field': 'email', 'align': 'left'},
                    {'name': 'full_name', 'label': '姓名', 'field': 'full_name', 'align': 'left'},
                    {'name': 'roles', 'label': '角色', 'field': 'roles', 'align': 'left'},
                    {'name': 'status', 'label': '状态', 'field': 'status', 'align': 'center'},
                    {'name': 'created_at', 'label': '创建时间', 'field': 'created_at', 'align': 'left', 'sortable': True},
                    {'name': 'actions', 'label': '操作', 'field': 'actions', 'align': 'center'},
                ]
                
                # 转换为表格数据
                rows = []
                for user in users:
                    # 获取角色名称列表
                    role_names = [role.name for role in user.roles]
                    
                    # 判断用户状态
                    if user.is_locked():
                        status = '🔒 已锁定'
                        status_color = 'red'
                    elif not user.is_active:
                        status = '❌ 已禁用'
                        status_color = 'orange'
                    else:
                        status = '✅ 正常'
                        status_color = 'green'
                    
                    rows.append({
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'full_name': user.full_name or '-',
                        'roles': ', '.join(role_names) if role_names else '无角色',
                        'status': status,
                        'status_color': status_color,
                        'created_at': format_datetime(user.created_at)[:10] if user.created_at else '-',
                        'is_superuser': user.is_superuser,
                        'is_locked': user.is_locked(),
                        'is_active': user.is_active,
                    })
                
                # ✅ 渲染带分页的表格
                table = ui.table(
                    columns=columns,
                    rows=rows,
                    row_key='id',
                    pagination={'rowsPerPage': 5, 'sortBy': 'id', 'descending': True},
                    column_defaults={
                        'align': 'left',
                        'headerClasses': 'uppercase text-primary text-base font-bold',
                        'classes': 'text-base'
                    }
                ).classes('w-full')
                
                # ✅ 添加状态列的插槽(使用徽章显示)
                table.add_slot('body-cell-status', '''
                    <q-td key="status" :props="props">
                        <q-badge :color="props.row.status_color">
                            {{ props.row.status }}
                        </q-badge>
                    </q-td>
                ''')
                
                # ✅ 添加操作列的插槽
                table.add_slot('body-cell-actions', '''
                    <q-td key="actions" :props="props">
                        <q-btn flat dense round icon="edit" color="blue" size="sm"
                               @click="$parent.$emit('edit', props.row)">
                            <q-tooltip>编辑</q-tooltip>
                        </q-btn>
                        <q-btn flat dense round icon="manage_accounts" color="purple" size="sm"
                               @click="$parent.$emit('roles', props.row)">
                            <q-tooltip>管理角色</q-tooltip>
                        </q-btn>
                        <q-btn v-if="props.row.is_locked" flat dense round icon="lock_open" color="green" size="sm"
                               @click="$parent.$emit('unlock', props.row)">
                            <q-tooltip>解锁</q-tooltip>
                        </q-btn>
                        <q-btn v-else flat dense round icon="lock" color="orange" size="sm"
                               @click="$parent.$emit('lock', props.row)">
                            <q-tooltip>锁定</q-tooltip>
                        </q-btn>
                        <q-btn flat dense round icon="vpn_key" color="indigo" size="sm"
                               @click="$parent.$emit('reset_password', props.row)">
                            <q-tooltip>重置密码</q-tooltip>
                        </q-btn>
                        <q-btn v-if="!props.row.is_superuser" flat dense round icon="delete" color="red" size="sm"
                               @click="$parent.$emit('delete', props.row)">
                            <q-tooltip>删除</q-tooltip>
                        </q-btn>
                    </q-td>
                ''')
                
                # ✅ 绑定操作事件
                table.on('edit', lambda e: safe(lambda: edit_user_dialog(e.args)))
                table.on('roles', lambda e: safe(lambda: manage_user_roles_dialog(e.args)))
                table.on('unlock', lambda e: safe(lambda: unlock_user(e.args['id'])))
                table.on('lock', lambda e: safe(lambda: lock_user_dialog(e.args)))
                table.on('reset_password', lambda e: safe(lambda: reset_password_dialog(e.args)))
                table.on('delete', lambda e: safe(lambda: delete_user_dialog(e.args)))

    # ===========================
    # 创建用户对话框
    # ===========================
    
    @safe_protect(name="创建用户对话框")
    def create_user_dialog():
        """创建用户对话框 - SQLModel 版本"""
        with ui.dialog() as dialog, ui.card().classes('w-96 p-6'):
            ui.label('创建新用户').classes('text-xl font-bold mb-4')
            
            username_input = ui.input(
                label='用户名', 
                placeholder='字母数字下划线,3-50字符'
            ).classes('w-full')
            
            email_input = ui.input(
                label='邮箱', 
                placeholder='user@example.com'
            ).classes('w-full')
            
            password_input = ui.input(
                label='密码', 
                placeholder='至少6个字符',
                password=True,
                password_toggle_button=True
            ).classes('w-full')
            
            full_name_input = ui.input(
                label='姓名(可选)'
            ).classes('w-full')
            
            def submit_create():
                """提交创建 - SQLModel 版本"""
                username = username_input.value.strip()
                email = email_input.value.strip()
                password = password_input.value
                full_name = full_name_input.value.strip() or None
                
                # 验证
                if not username or len(username) < 3:
                    ui.notify('用户名至少3个字符', type='negative')
                    return
                
                if not validate_email(email):
                    ui.notify('邮箱格式不正确', type='negative')
                    return
                
                if not password or len(password) < 6:
                    ui.notify('密码至少6个字符', type='negative')
                    return
                
                # 创建用户
                with get_db() as session:
                    # 检查用户名和邮箱是否已存在
                    existing = session.exec(
                        select(User).where(
                            (User.username == username) | (User.email == email)
                        )
                    ).first()
                    
                    if existing:
                        ui.notify('用户名或邮箱已存在', type='negative')
                        return
                    
                    # 创建新用户
                    new_user = User(
                        username=username,
                        email=email,
                        full_name=full_name,
                        is_active=True
                    )
                    new_user.set_password(password)
                    
                    session.add(new_user)
                    
                    log_success(f"用户创建成功: {username}")
                    ui.notify(f'用户 {username} 创建成功', type='positive')
                    dialog.close()
                    safe(load_users)
            
            with ui.row().classes('w-full justify-end gap-2 mt-6'):
                ui.button('取消', on_click=dialog.close).classes('bg-gray-500 text-white')
                ui.button('创建', on_click=lambda: safe(submit_create)).classes('bg-blue-500 text-white')
        
        dialog.open()

    # ===========================
    # 编辑用户对话框
    # ===========================
    
    @safe_protect(name="编辑用户对话框")
    def edit_user_dialog(row_data):
        """编辑用户对话框 - SQLModel 版本"""
        with ui.dialog() as dialog, ui.card().classes('w-96 p-6'):
            ui.label(f'编辑用户: {row_data["username"]}').classes('text-xl font-bold mb-4')
            
            # 加载用户数据
            with get_db() as session:
                user = session.get(User, row_data['id'])
                if not user:
                    ui.notify('用户不存在', type='negative')
                    return
                
                email_input = ui.input(
                    label='邮箱',
                    value=user.email
                ).classes('w-full')
                
                full_name_input = ui.input(
                    label='姓名',
                    value=user.full_name or ''
                ).classes('w-full')
                
                phone_input = ui.input(
                    label='电话',
                    value=user.phone or ''
                ).classes('w-full')
                
                is_active_checkbox = ui.checkbox(
                    '启用账户',
                    value=user.is_active
                ).classes('mb-2')
                
                is_verified_checkbox = ui.checkbox(
                    '邮箱已验证',
                    value=user.is_verified
                ).classes('mb-2')
                
                if user.is_superuser:
                    ui.label('⚠️ 超级管理员,部分字段不可修改').classes('text-sm text-orange-500 mt-2')
            
            def submit_edit():
                """提交编辑 - SQLModel 版本"""
                with get_db() as session:
                    user = session.get(User, row_data['id'])
                    if user:
                        # 验证邮箱
                        if not validate_email(email_input.value):
                            ui.notify('邮箱格式不正确', type='negative')
                            return
                        
                        # 检查邮箱是否被其他用户使用
                        existing = session.exec(
                            select(User).where(
                                (User.email == email_input.value) & 
                                (User.id != user.id)
                            )
                        ).first()
                        
                        if existing:
                            ui.notify('邮箱已被其他用户使用', type='negative')
                            return
                        
                        user.email = email_input.value.strip()
                        user.full_name = full_name_input.value.strip() or None
                        user.phone = phone_input.value.strip() or None
                        user.is_verified = is_verified_checkbox.value
                        
                        # 超级管理员不能被禁用
                        if not user.is_superuser:
                            user.is_active = is_active_checkbox.value
                        
                        log_info(f"用户更新成功: {user.username}")
                        ui.notify(f'用户 {user.username} 更新成功', type='positive')
                        dialog.close()
                        safe(load_users)
            
            with ui.row().classes('w-full justify-end gap-2 mt-6'):
                ui.button('取消', on_click=dialog.close).classes('bg-gray-500 text-white')
                ui.button('保存', on_click=lambda: safe(submit_edit)).classes('bg-blue-500 text-white')
        
        dialog.open()

    # ===========================
    # 管理用户角色对话框
    # ===========================
    
    @safe_protect(name="管理用户角色对话框")
    def manage_user_roles_dialog(row_data):
        """管理用户角色对话框 - SQLModel 版本"""
        with ui.dialog() as dialog, ui.card().classes('w-[500px] p-6'):
            ui.label(f'管理角色: {row_data["username"]}').classes('text-xl font-bold mb-4')
            
            with get_db() as session:
                user = session.get(User, row_data['id'])
                if not user:
                    ui.notify('用户不存在', type='negative')
                    return
                
                # 获取所有角色
                all_roles = session.exec(select(Role)).all()
                
                # 当前用户的角色 ID 集合
                current_role_ids = {r.id for r in user.roles}
                
                # 存储选中的角色
                selected_roles = set(current_role_ids)
                
                # 渲染角色选择器
                ui.label(f'当前已关联 {len(current_role_ids)} 个角色').classes('text-sm text-gray-600 mb-4')
                
                with ui.scroll_area().classes('w-full h-96'):
                    for role in all_roles:
                        is_checked = role.id in current_role_ids
                        
                        def on_change(checked, role_id=role.id):
                            if checked:
                                selected_roles.add(role_id)
                            else:
                                selected_roles.discard(role_id)
                        
                        with ui.card().classes('w-full p-3 mb-2'):
                            with ui.row().classes('w-full items-center justify-between'):
                                with ui.row().classes('items-center gap-3'):
                                    ui.checkbox(
                                        value=is_checked,
                                        on_change=lambda e, rid=role.id: on_change(e.value, rid)
                                    )
                                    
                                    with ui.column().classes('gap-1'):
                                        ui.label(role.display_name or role.name).classes('font-bold')
                                        ui.label(f"@{role.name}").classes('text-xs text-gray-500')
                                
                                # 角色标签
                                if role.is_system:
                                    ui.badge('系统').props('color=blue')
                                elif not role.is_active:
                                    ui.badge('禁用').props('color=orange')
                
                def submit_roles():
                    """提交角色更改 - SQLModel 版本"""
                    with get_db() as session:
                        user = session.get(User, row_data['id'])
                        if user:
                            # 清空现有角色
                            user.roles.clear()
                            
                            # 添加新角色
                            for role_id in selected_roles:
                                role = session.get(Role, role_id)
                                if role:
                                    user.roles.append(role)
                            
                            log_success(f"用户角色更新成功: {user.username}, 角色数: {len(selected_roles)}")
                            ui.notify(f'用户 {user.username} 角色已更新', type='positive')
                            dialog.close()
                            safe(load_users)
                
                with ui.row().classes('w-full justify-end gap-2 mt-6'):
                    ui.button('取消', on_click=dialog.close).classes('bg-gray-500 text-white')
                    ui.button('保存', on_click=lambda: safe(submit_roles)).classes('bg-purple-500 text-white')
        
        dialog.open()

    # ===========================
    # 解锁用户
    # ===========================
    
    @safe_protect(name="解锁用户")
    def unlock_user(user_id: int):
        """解锁用户 - SQLModel 版本"""
        with get_db() as session:
            user = session.get(User, user_id)
            if user:
                user.locked_until = None
                user.failed_login_count = 0
                log_info(f"用户解锁成功: {user.username}")
                ui.notify(f'用户 {user.username} 已解锁', type='positive')
                safe(load_users)

    # ===========================
    # 锁定用户对话框
    # ===========================
    
    @safe_protect(name="锁定用户对话框")
    def lock_user_dialog(row_data):
        """锁定用户对话框"""
        with ui.dialog() as dialog, ui.card().classes('w-96 p-6'):
            ui.label(f'锁定用户: {row_data["username"]}').classes('text-xl font-bold mb-4')
            
            duration_select = ui.select(
                label='锁定时长',
                options={30: '30分钟', 60: '1小时', 1440: '24小时', 10080: '7天'},
                value=30
            ).classes('w-full')
            
            def submit_lock():
                minutes = duration_select.value
                with get_db() as session:
                    user = session.get(User, row_data['id'])
                    if user:
                        user.locked_until = datetime.now() + timedelta(minutes=minutes)
                        log_warning(f"用户已锁定: {user.username}, 时长: {minutes}分钟")
                        ui.notify(f'用户 {user.username} 已锁定 {minutes} 分钟', type='warning')
                        dialog.close()
                        safe(load_users)
            
            with ui.row().classes('w-full justify-end gap-2 mt-6'):
                ui.button('取消', on_click=dialog.close).classes('bg-gray-500 text-white')
                ui.button('确认锁定', on_click=lambda: safe(submit_lock)).classes('bg-orange-500 text-white')
        
        dialog.open()

    # ===========================
    # 重置密码对话框
    # ===========================
    
    @safe_protect(name="重置密码对话框")
    def reset_password_dialog(row_data):
        """重置密码对话框"""
        with ui.dialog() as dialog, ui.card().classes('w-96 p-6'):
            ui.label(f'重置密码: {row_data["username"]}').classes('text-xl font-bold mb-4')
            
            # 密码生成选项
            with ui.row().classes('w-full gap-2 mb-4'):
                ui.label('密码长度:').classes('text-sm')
                password_length = ui.number(
                    value=12,
                    min=6,
                    max=32
                ).classes('w-24')
            
            # 生成的密码显示
            new_password_input = ui.input(
                label='新密码',
                placeholder='点击生成随机密码',
                password=False
            ).classes('w-full')
            
            def generate_password():
                """生成随机密码"""
                length = int(password_length.value)
                # 包含大小写字母、数字和特殊字符
                chars = string.ascii_letters + string.digits + '!@#$%^&*'
                password = ''.join(secrets.choice(chars) for _ in range(length))
                new_password_input.value = password
                ui.notify('密码已生成', type='info')
            
            ui.button(
                '生成随机密码',
                icon='refresh',
                on_click=generate_password
            ).classes('bg-indigo-500 text-white mb-4')
            
            # 自动生成一个初始密码
            generate_password()
            
            ui.label('⚠️ 请务必保存此密码,重置后无法找回').classes('text-sm text-orange-500')
            
            def submit_reset():
                """提交密码重置"""
                new_password = new_password_input.value
                
                if not new_password or len(new_password) < 6:
                    ui.notify('密码至少6个字符', type='negative')
                    return
                
                with get_db() as session:
                    user = session.get(User, row_data['id'])
                    if user:
                        user.set_password(new_password)
                        
                        # 清除锁定状态
                        user.locked_until = None
                        user.failed_login_count = 0
                        
                        log_warning(f"用户密码已重置: {user.username}")
                        ui.notify(f'用户 {user.username} 密码已重置', type='positive')
                        
                        # 显示密码提示
                        ui.notify(f'新密码: {new_password}', type='info', timeout=10000)
                        
                        dialog.close()
                        safe(load_users)
            
            with ui.row().classes('w-full justify-end gap-2 mt-6'):
                ui.button('取消', on_click=dialog.close).classes('bg-gray-500 text-white')
                ui.button('确认重置', on_click=lambda: safe(submit_reset)).classes('bg-indigo-500 text-white')
        
        dialog.open()

    # ===========================
    # 删除用户对话框
    # ===========================
    
    @safe_protect(name="删除用户对话框")
    def delete_user_dialog(row_data):
        """删除用户对话框"""
        with ui.dialog() as dialog, ui.card().classes('w-96 p-6'):
            ui.label(f'删除用户: {row_data["username"]}').classes('text-xl font-bold text-red-600 mb-4')
            ui.label('此操作不可撤销!').classes('text-red-500 mb-4')
            
            # 二次确认
            confirm_input = ui.input(
                label=f'请输入用户名 "{row_data["username"]}" 以确认删除',
                placeholder=row_data["username"]
            ).classes('w-full')
            
            def submit_delete():
                """提交删除"""
                if confirm_input.value != row_data["username"]:
                    ui.notify('用户名不匹配,删除取消', type='negative')
                    return
                
                with get_db() as session:
                    user = session.get(User, row_data['id'])
                    if user:
                        username = user.username
                        session.delete(user)
                        log_warning(f"用户已删除: {username}")
                        ui.notify(f'用户 {username} 已删除', type='warning')
                        dialog.close()
                        safe(load_users)
            
            with ui.row().classes('w-full justify-end gap-2 mt-6'):
                ui.button('取消', on_click=dialog.close).classes('bg-gray-500 text-white')
                ui.button('确认删除', on_click=lambda: safe(submit_delete)).classes('bg-red-500 text-white')
        
        dialog.open()

    # 初始加载
    safe(load_users)
    log_success("===用户管理页面加载完成===")
```
