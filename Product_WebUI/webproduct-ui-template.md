# webproduct_ui_template

- **webproduct_ui_template\multilayer_main.py**
```python
"""
多层布局主应用入口 - 演示多层折叠菜单布局
基于 multilayer_spa_layout 构建UI的启动脚本
"""
import sys
import os
from pathlib import Path
from nicegui import ui, app
import secrets
# 导入环境变量配置
from config.env_config import env_config

# 导入多层布局组件
from component import (
    with_multilayer_spa_layout, 
    LayoutConfig, 
    MultilayerMenuItem,
    static_manager
)

# 导入页面处理器
from menu_pages import get_menu_page_handlers
from header_pages import get_header_page_handlers

# 导入认证模块
from auth import (
    auth_manager,
    require_login,
    require_role,
    login_page_content,
    register_page_content,
    get_auth_page_handlers
)

def create_menu_structure() -> list[MultilayerMenuItem]:
    """
    创建多层菜单结构,这里展示了2-3层的菜单结构
    """
    menu_items = [
        # 首页 - 单独的顶层菜单(无子菜单)
        MultilayerMenuItem(
            key='home',
            label='首页',
            icon='home',
            route='home',
            separator_after=True  # 后面显示分隔线
        ),
        
        # 企业档案管理 - 第一个分组
        MultilayerMenuItem(
            key='enterprise',
            label='企业档案管理',
            icon='business',
            expanded=True,  # 默认展开
            children=[
                MultilayerMenuItem(
                    key='chat',
                    label='AI对话',
                    icon='chat',
                    route='chat_page'
                ),
                MultilayerMenuItem(
                    key='doc',
                    label='日志测试',
                    icon='description',
                    route='other_page'  # 暂时复用other_page
                ),
                
            ]
        ),
        
        
        # 系统管理 - 第2个分组(演示更多子项)
        MultilayerMenuItem(
            key='system',
            label='权限测试',
            icon='admin_panel_settings',
            children=[
                MultilayerMenuItem(
                    key='auth_test',
                    label='认证系统测试',
                    icon='security',
                    route='auth_test',
                    separator_after=True
                ),
                MultilayerMenuItem(
                    key='default_auth',
                    label='用户管理',
                    icon='security',
                    route='default_auth'
                ),
                MultilayerMenuItem(
                    key='erp_auth_page',
                    label='erp',
                    icon='security',
                    route='erp_auth_page'
                ),
            ]
        ),
    ]
    
    return menu_items

def create_protected_handlers():
    """为需要认证的页面添加装饰器"""
    menu_handlers = get_menu_page_handlers()
    header_handlers = get_header_page_handlers()
    system_handlers = get_auth_page_handlers()
    
    return {**menu_handlers, **header_handlers, **system_handlers}

if __name__ in {"__main__", "__mp_main__"}:
    
    print("=" * 70)
    print("🚀 启动多层布局应用")
    
    # 获取受保护的页面处理器
    protected_handlers = create_protected_handlers()
    
    # 创建自定义配置
    config = LayoutConfig()
    
    # 登录页面
    @ui.page('/login')
    def login_page():
        login_page_content()
    
    # 注册页面
    @ui.page('/register')
    def register_page():
        register_page_content()
    
    # 主工作台页面 - 使用多层布局
    @ui.page('/workbench')
    def main_page():
        # 检查用户认证状态
        user = auth_manager.check_session()
        if not user:
            ui.navigate.to('/login')
            return        
        # 创建多层菜单结构
        menu_items = create_menu_structure()
        
        # 创建带认证的多层SPA布局
        @with_multilayer_spa_layout(
            config=config,
            menu_items=menu_items,
            header_config_items=[
                {'key': 'search', 'label': '搜索', 'icon': 'search', 'route': 'search'},
                {'key': 'messages', 'label': '消息', 'icon': 'mail', 'route': 'messages'},
                {'key': 'contact', 'label': '联系我们', 'icon': 'contact_support', 'route': 'contact'},
            ],
            route_handlers=protected_handlers
        )
        def spa_content():
            pass
        
        return spa_content()
    
    # 直接跳转到工作台
    @ui.page('/')
    def index():
        ui.navigate.to('/workbench')

    print("\n" + "=" * 70)
    print("✨ 多层布局特性:")
    print("  - 🎯 支持多层级折叠菜单(无限层级)")
    print("  - 📂 自动展开/收起父节点")
    print("  - 🔖 面包屑导航自动生成")
    print("  - 💾 刷新页面保持状态(路由+展开状态)")
    print("  - 🎨 高亮选中的叶子节点")
    print("  - 🔐 集成完整的认证和权限管理")
    print("=" * 70 + "\n")
    
    storage_secret = env_config.get('APP_STORAGE_SECRET')
    if not storage_secret:
        storage_secret = secrets.token_urlsafe(32)
    # 启动应用
    ui.run(
        title=env_config.get('APP_TITLE', 'NeoUI多层布局模板'),
        port=env_config.get_int('APP_PORT', 8080),
        show=env_config.get_bool('APP_SHOW', True),
        reload=env_config.get_bool('APP_RELOAD', True),
        favicon=env_config.get('APP_FAVICON', '🚀'),
        dark=env_config.get_bool('APP_DARK', False),
        prod_js=env_config.get_bool('APP_PROD_JS', False),
        storage_secret=secrets.token_urlsafe(32)
    )
```

## webproduct_ui_template\auth

- **webproduct_ui_template\auth\__init__.py** *(包初始化文件)*
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

- **webproduct_ui_template\auth\auth_manager.py**
```python
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
```

- **webproduct_ui_template\auth\config.py**
```python
"""
认证配置模块 - 使用环境变量版本

从 .env 文件加载所有配置，支持灵活的配置管理。
"""
import os
from pathlib import Path
from typing import Optional

# 导入环境变量配置加载器
try:
    from config.env_config import env_config
except ImportError:
    # 如果导入失败，使用简单的环境变量读取
    print("⚠️  无法导入 config.env_config，将直接使用 os.environ")
    
    class SimpleEnvConfig:
        def get(self, key, default=None):
            return os.environ.get(key, default)
        
        def get_int(self, key, default=0):
            try:
                return int(os.environ.get(key, default))
            except:
                return default
        
        def get_bool(self, key, default=False):
            value = os.environ.get(key, '').lower()
            if value in ('true', 'yes', '1', 'on'):
                return True
            elif value in ('false', 'no', '0', 'off'):
                return False
            return default
    
    env_config = SimpleEnvConfig()


class AuthConfig:
    """
    认证配置类 - 使用环境变量版本
    
    所有配置都从 .env 文件加载，支持：
    - 数据库配置
    - 会话管理
    - 密码策略
    - 登录安全
    - 功能开关
    - 路由配置
    """
    
    def __init__(self):
        """
        初始化认证配置
        
        从 .env 文件加载所有配置项，并提供合理的默认值。
        """
        # ==================== 数据库配置 ====================
        self.database_type = env_config.get('AUTH_DATABASE_TYPE', 'sqlite')
        self.database_url = self._get_database_url()
        
        # ==================== 会话配置 ====================
        self.session_secret_key = env_config.get('AUTH_SESSION_SECRET_KEY','8CAs6NgrsLAaB0Aw-w6lSv--ISwffsDK2cDDKN1r_bQ')
        
        # 会话超时时间（秒，默认24小时）
        self.session_timeout = env_config.get_int('AUTH_SESSION_TIMEOUT',3600 * 24)
        
        # "记住我"持续时间（秒，默认30天）
        self.remember_me_duration = env_config.get_int('AUTH_REMEMBER_ME_DURATION',3600 * 24 * 30)
        
        # ==================== 密码策略配置 ====================
        self.password_min_length = env_config.get_int('AUTH_PASSWORD_MIN_LENGTH',6)
        
        self.password_max_length = env_config.get_int('AUTH_PASSWORD_MAX_LENGTH',128)
        
        self.password_require_uppercase = env_config.get_bool('AUTH_PASSWORD_REQUIRE_UPPERCASE',False)
        
        self.password_require_lowercase = env_config.get_bool('AUTH_PASSWORD_REQUIRE_LOWERCASE',False)
        
        self.password_require_digit = env_config.get_bool('AUTH_PASSWORD_REQUIRE_DIGIT',False)
        
        self.password_require_special = env_config.get_bool('AUTH_PASSWORD_REQUIRE_SPECIAL',False)
        
        # ==================== 登录安全配置 ====================
        # 最大登录失败次数
        self.max_login_attempts = env_config.get_int('AUTH_MAX_LOGIN_ATTEMPTS',5)
        
        # 账户锁定持续时间（分钟）
        self.login_lock_duration = env_config.get_int('AUTH_LOGIN_LOCK_DURATION',30)
        
        # 是否启用验证码
        self.enable_captcha = env_config.get_bool('AUTH_ENABLE_CAPTCHA',False)
        
        # ==================== 功能开关 ====================
        # 是否允许用户注册
        self.allow_registration = env_config.get_bool('AUTH_ALLOW_REGISTRATION',True)
        
        # 是否允许"记住我"
        self.allow_remember_me = env_config.get_bool('AUTH_ALLOW_REMEMBER_ME',True)
        
        # 是否启用邮箱验证
        self.enable_email_verification = env_config.get_bool('AUTH_ENABLE_EMAIL_VERIFICATION', False)
        
        # 是否启用双因素认证
        self.enable_two_factor = env_config.get_bool('AUTH_ENABLE_TWO_FACTOR',False)
        
        # ==================== 路由配置 ====================
        self.login_route = env_config.get('AUTH_LOGIN_ROUTE','/login')
        
        self.register_route = env_config.get('AUTH_REGISTER_ROUTE','/register')
        
        self.logout_route = env_config.get('AUTH_LOGOUT_ROUTE','/logout')
        
        self.default_redirect = env_config.get('AUTH_DEFAULT_REDIRECT','/workbench')
    
    def _get_database_url(self) -> str:
        """
        根据数据库类型构建连接URL
        
        Returns:
            str: 数据库连接URL
        """
        db_type = self.database_type.lower()
        
        if db_type == 'sqlite':
            # SQLite 数据库路径
            sqlite_path = env_config.get(
                'AUTH_SQLITE_PATH',
                'data/neoapp.db'
            )
            
            # 确保数据目录存在
            db_path = Path(sqlite_path)
            db_path.parent.mkdir(parents=True, exist_ok=True)
            
            return f'sqlite:///{sqlite_path}'
        
        elif db_type == 'mysql':
            # MySQL 连接配置
            host = env_config.get('AUTH_MYSQL_HOST', 'localhost')
            port = env_config.get_int('AUTH_MYSQL_PORT', 3306)
            user = env_config.get('AUTH_MYSQL_USER', 'root')
            password = env_config.get('AUTH_MYSQL_PASSWORD', '')
            database = env_config.get('AUTH_MYSQL_DATABASE', 'neoapp')
            
            return f'mysql+pymysql://{user}:{password}@{host}:{port}/{database}'
        
        elif db_type == 'postgresql':
            # PostgreSQL 连接配置
            host = env_config.get('AUTH_POSTGRES_HOST', 'localhost')
            port = env_config.get_int('AUTH_POSTGRES_PORT', 5432)
            user = env_config.get('AUTH_POSTGRES_USER', 'postgres')
            password = env_config.get('AUTH_POSTGRES_PASSWORD', '')
            database = env_config.get('AUTH_POSTGRES_DATABASE', 'neoapp')
            
            return f'postgresql://{user}:{password}@{host}:{port}/{database}'
        
        else:
            # 默认使用 SQLite
            print(f"⚠️  未知的数据库类型: {db_type}，使用默认 SQLite")
            return 'sqlite:///data/neoapp.db'
    
# 全局配置实例
auth_config = AuthConfig()
```

- **webproduct_ui_template\auth\database.py**
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

- **webproduct_ui_template\auth\decorators.py**
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

- **webproduct_ui_template\auth\models.py**
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

- **webproduct_ui_template\auth\navigation.py**
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

- **webproduct_ui_template\auth\session_manager.py**
```python
"""
会话管理器 - 修复版本

修复内容:
- ✅ 使用客户端ID隔离会话存储，避免跨浏览器共享
- ✅ 每个浏览器有独立的会话缓存空间
- ✅ 彻底解决跨浏览器/设备会话泄露问题
"""
from typing import Optional, Dict
from datetime import datetime
from dataclasses import dataclass
from nicegui import app


@dataclass
class UserSession:
    """
    用户会话数据类（内存缓存）
    
    这是一个轻量级的用户会话对象，用于内存缓存，避免频繁的数据库查询。
    与数据库中的 User 模型分离，避免 DetachedInstanceError。
    """
    id: int
    username: str
    email: str
    full_name: Optional[str]
    phone: Optional[str]
    avatar: Optional[str]
    bio: Optional[str]
    is_active: bool
    is_verified: bool
    is_superuser: bool
    last_login: Optional[datetime]
    login_count: int
    failed_login_count: int
    locked_until: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    roles: list  # 角色名称列表
    permissions: dict  # 权限字典
    
    def has_role(self, role_name: str) -> bool:
        """检查是否有指定角色"""
        if self.is_superuser:
            return True
        return role_name in self.roles
    
    def has_permission(self, permission_name: str) -> bool:
        """检查是否有指定权限"""
        if self.is_superuser:
            return True
        # 检查通配符权限
        if '*' in self.permissions:
            return True
        # 检查具体权限
        return permission_name in self.permissions
    
    @staticmethod
    def from_user(user):
        """
        从 SQLModel User 对象创建 UserSession
        
        Args:
            user: SQLModel User 对象
        
        Returns:
            UserSession: 会话对象
        """
        # 提取角色名称
        role_names = [role.name for role in user.roles] if user.roles else []
        
        # 提取权限（从角色和直接权限）
        permissions = {}
        
        # 从角色获取权限
        if user.roles:
            for role in user.roles:
                if role.permissions:
                    for perm in role.permissions:
                        permissions[perm.name] = perm.display_name or perm.name
        
        # 从直接权限获取
        if user.permissions:
            for perm in user.permissions:
                permissions[perm.name] = perm.display_name or perm.name
        
        return UserSession(
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
    会话管理器 - 修复版本
    
    核心修复:
    - ✅ 使用客户端ID作为命名空间，每个浏览器有独立的会话存储
    - ✅ 避免跨浏览器/设备的会话共享问题
    - ✅ 自动清理断开连接的客户端会话
    
    职责:
    - 管理内存中的用户会话缓存（按客户端隔离）
    - 提供快速的会话查询
    - 避免频繁的数据库查询
    
    架构说明:
    _client_sessions = {
        'client_id_1': {
            'token_A': UserSession(admin),
            'token_B': UserSession(user1)
        },
        'client_id_2': {
            'token_C': UserSession(ceo),
        }
    }
    """
    
    def __init__(self):
        """
        初始化会话管理器
        
        使用二级字典结构：
        - 第一级：客户端ID → 该客户端的会话字典
        - 第二级：token → UserSession
        """
        self._client_sessions: Dict[str, Dict[str, UserSession]] = {}
    
    def _get_client_id(self) -> str:
        """
        获取当前客户端的唯一ID
        
        使用 app.storage.browser 获取浏览器级别的唯一标识。
        每个浏览器（即使是同一台电脑的不同浏览器）都有不同的 browser ID。
        
        Returns:
            str: 客户端唯一ID，如果无法获取则返回 'default'
            
        注意:
            - 在页面刚加载时，app.storage.browser 可能还未就绪
            - 此时返回 'default' 作为临时ID
            - 一旦浏览器ID就绪，会自动使用正确的ID
        """
        try:
            # app.storage.browser 包含一个自动生成的 'id' 字段
            client_id = app.storage.browser.get('id')
            if client_id:
                return str(client_id)
        except:
            pass
        
        # 如果无法获取，使用默认值
        # 这通常发生在页面初始化早期
        return 'default'
    
    def _get_sessions_dict(self) -> Dict[str, UserSession]:
        """
        获取当前客户端的会话字典
        
        为当前客户端创建或获取独立的会话存储空间。
        
        Returns:
            Dict[str, UserSession]: 当前客户端的会话字典（token -> UserSession）
        """
        client_id = self._get_client_id()
        
        # 如果该客户端还没有会话字典，创建一个
        if client_id not in self._client_sessions:
            self._client_sessions[client_id] = {}
        
        return self._client_sessions[client_id]
    
    def create_session(self, token: str, user) -> UserSession:
        """
        创建会话
        
        为当前客户端创建一个新的会话缓存。
        
        Args:
            token: 会话 token（唯一标识）
            user: SQLModel User 对象
        
        Returns:
            UserSession: 创建的会话对象
            
        示例:
            >>> session = session_manager.create_session('token_abc', user)
            >>> print(session.username)
            'admin'
        """
        # 从 User 对象创建 UserSession
        session = UserSession.from_user(user)
        
        # 存储到当前客户端的会话字典中
        sessions_dict = self._get_sessions_dict()
        sessions_dict[token] = session
        
        return session
    
    def get_session(self, token: str) -> Optional[UserSession]:
        """
        获取会话
        
        从当前客户端的会话缓存中获取指定 token 的会话。
        
        Args:
            token: 会话 token
        
        Returns:
            Optional[UserSession]: 会话对象，不存在则返回 None
            
        注意:
            - 只能获取当前客户端的会话
            - 无法获取其他客户端的会话（隔离保护）
        """
        sessions_dict = self._get_sessions_dict()
        return sessions_dict.get(token)
    
    def update_session(self, token: str, user) -> Optional[UserSession]:
        """
        更新会话（从数据库重新加载用户数据）
        
        当用户信息发生变化时（如修改资料、更改角色权限），
        需要调用此方法刷新内存缓存。
        
        Args:
            token: 会话 token
            user: SQLModel User 对象（最新数据）
        
        Returns:
            Optional[UserSession]: 更新后的会话对象，token不存在则返回None
        """
        sessions_dict = self._get_sessions_dict()
        
        if token in sessions_dict:
            # 重新创建 UserSession 并更新
            session = UserSession.from_user(user)
            sessions_dict[token] = session
            return session
        
        return None
    
    def delete_session(self, token: str):
        """
        删除会话
        
        从当前客户端的会话缓存中删除指定 token 的会话。
        通常在用户登出时调用。
        
        Args:
            token: 会话 token
        """
        sessions_dict = self._get_sessions_dict()
        
        if token in sessions_dict:
            del sessions_dict[token]
    
    def clear_client_sessions(self):
        """
        清除当前客户端的所有会话
        
        删除当前客户端的所有会话缓存。
        通常在客户端断开连接或重置会话时使用。
        """
        client_id = self._get_client_id()
        
        if client_id in self._client_sessions:
            del self._client_sessions[client_id]
    
    def clear_all_sessions(self):
        """
        清除所有客户端的所有会话
        
        ⚠️ 警告：这会删除所有浏览器的会话缓存！
        通常只在系统维护或测试时使用。
        """
        self._client_sessions.clear()
    
    def get_session_count(self) -> int:
        """
        获取当前客户端的会话数量
        
        Returns:
            int: 当前客户端的会话数量
        """
        sessions_dict = self._get_sessions_dict()
        return len(sessions_dict)
    
    def get_total_session_count(self) -> int:
        """
        获取所有客户端的会话总数
        
        Returns:
            int: 所有客户端的会话总数
        """
        total = 0
        for sessions_dict in self._client_sessions.values():
            total += len(sessions_dict)
        return total
    
    def get_client_count(self) -> int:
        """
        获取当前活跃的客户端数量
        
        Returns:
            int: 客户端数量
        """
        return len(self._client_sessions)
    
    def get_all_sessions(self) -> Dict[str, UserSession]:
        """
        获取当前客户端的所有会话（用于调试/管理）
        
        Returns:
            Dict[str, UserSession]: 当前客户端的会话字典副本
        """
        sessions_dict = self._get_sessions_dict()
        return sessions_dict.copy()
    
    def get_debug_info(self) -> Dict:
        """
        获取调试信息
        
        Returns:
            dict: 包含客户端ID、会话数量等调试信息
        """
        client_id = self._get_client_id()
        sessions_dict = self._get_sessions_dict()
        
        return {
            'current_client_id': client_id,
            'current_client_sessions': len(sessions_dict),
            'total_clients': len(self._client_sessions),
            'total_sessions': self.get_total_session_count(),
            'all_client_ids': list(self._client_sessions.keys())
        }


# 全局会话管理器实例
session_manager = SessionManager()
```

- **webproduct_ui_template\auth\utils.py**
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

### webproduct_ui_template\auth\pages

- **webproduct_ui_template\auth\pages\__init__.py** *(包初始化文件)*
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

- **webproduct_ui_template\auth\pages\change_password_page.py**
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

- **webproduct_ui_template\auth\pages\llm_config_management_page.py**
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

- **webproduct_ui_template\auth\pages\login_page.py**
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
                ui.label('编辑者：editor / editor123').classes('text-gray-600')
                ui.label('查看者：viewer / viewer123').classes('text-gray-600')



```

- **webproduct_ui_template\auth\pages\logout_page.py**
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

- **webproduct_ui_template\auth\pages\permission_management_page.py**
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

- **webproduct_ui_template\auth\pages\profile_page.py**
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

- **webproduct_ui_template\auth\pages\prompt_config_management_page.py**
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

- **webproduct_ui_template\auth\pages\register_page.py**
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

- **webproduct_ui_template\auth\pages\role_management_page.py**
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

- **webproduct_ui_template\auth\pages\user_management_page.py**
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

## webproduct_ui_template\common

- **webproduct_ui_template\common\__init__.py** *(包初始化文件)*
```python
"""
通用公共功能包
"""
```

- **webproduct_ui_template\common\log_handler.py**
```python
"""
增强的异常处理和日志模块 - 基于 Loguru 的混合架构(优化版 v2.2 - 修复调用栈问题)
保留现有 API,增强底层实现,按日期文件夹组织日志
文件路径: webproduct_ui_template/common/log_handler.py

关键修复(v2.2):
1. 修复 module/function/line_number 总是显示 log_handler.py 的问题
2. 使用 logger.opt(depth=N) 正确追踪调用栈
3. 改进用户上下文获取逻辑,减少 anonymous 出现

特性:
1. 完全兼容现有 API (log_info, log_error, safe, db_safe, safe_protect)
2. 使用 Loguru 作为底层引擎,性能提升 20-30%
3. 支持 7 种日志级别 (TRACE, DEBUG, INFO, SUCCESS, WARNING, ERROR, CRITICAL)
4. 智能日志轮转 (按天/自动压缩)
5. 异步日志写入,不阻塞主线程
6. 保留 CSV 格式兼容(用于查询工具)
7. 自动捕获用户上下文
8. 集成 NiceGUI UI 通知
9. 按日期文件夹组织: logs/2025-10-23/{app.log, error.log, app_logs.csv}
"""
import csv
import json
import asyncio
import threading
import functools
import inspect
import sys
from typing import Callable, Any, Optional, Dict, List
from datetime import datetime, timedelta
from pathlib import Path
from contextlib import contextmanager
from loguru import logger
from nicegui import ui

# =============================================================================
# 配置和初始化
# =============================================================================

class LoguruExceptionHandler:
    """基于 Loguru 的增强异常处理器 - 单例模式(线程安全)"""
    
    _instance = None
    _lock = threading.Lock()
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        # 配置参数
        self.log_base_dir = Path('logs')  # 日志根目录
        self.log_base_dir.mkdir(exist_ok=True)
        self.max_log_days = 30  # 普通日志保留30天
        self.error_log_days = 90  # 错误日志保留90天
        self.csv_enabled = True  # CSV 兼容模式
        
        # 当前日志目录(每天一个文件夹)
        self.current_log_dir = self._get_today_log_dir()
        
        # 初始化 Loguru
        self._setup_loguru()
        
        # CSV 支持(兼容现有查询工具)
        if self.csv_enabled:
            self._setup_csv_logging()
        
        # 启动定时清理任务
        self._start_cleanup_task()
        
        LoguruExceptionHandler._initialized = True
    
    def _get_today_log_dir(self) -> Path:
        """获取今天的日志目录"""
        today = datetime.now().strftime('%Y-%m-%d')
        log_dir = self.log_base_dir / today
        log_dir.mkdir(parents=True, exist_ok=True)
        return log_dir
    
    def _check_and_update_log_dir(self):
        """检查日期是否变化,如果跨天则更新日志目录"""
        today_log_dir = self._get_today_log_dir()
        
        if today_log_dir != self.current_log_dir:
            self.current_log_dir = today_log_dir
            
            # 重新配置 Loguru
            logger.remove()
            self._setup_loguru()
            if self.csv_enabled:
                self._setup_csv_logging()
    
    def _setup_loguru(self):
        """配置 Loguru 日志系统 - 按日期文件夹组织"""
        # 移除默认处理器
        logger.remove()
        
        # 1️⃣ 控制台输出 - 开发环境(彩色格式化)
        logger.add(
            sys.stderr,
            format=(
                "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
                "<level>{level: <8}</level> | "
                "<cyan>{extra[user_id]}</cyan>@<cyan>{extra[username]}</cyan> | "
                "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
                "<level>{message}</level>"
            ),
            level="DEBUG",   # ✅ 控制台输出 DEBUG,不写入日志文件
            colorize=True,
            backtrace=True,
            diagnose=True,
            enqueue=False  # 控制台同步输出,方便调试
        )
        
        # 2️⃣ 普通日志文件 - 存储在当天日期文件夹下
        logger.add(
            self.current_log_dir / "app.log",
            rotation="500 MB",
            retention=f"{self.max_log_days} days",
            compression="zip",
            encoding="utf-8",
            format=(
                "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
                "{level: <8} | "
                "{extra[user_id]}@{extra[username]} | "
                "{name}:{function}:{line} | "
                "{message}"
            ),
            level="INFO",
            enqueue=True,
            backtrace=True,
            diagnose=True
        )
        
        # 3️⃣ 错误日志文件 - 存储在当天日期文件夹下
        logger.add(
            self.current_log_dir / "error.log",
            rotation="100 MB",
            retention=f"{self.error_log_days} days",
            compression="zip",
            encoding="utf-8",
            format=(
                "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
                "{level: <8} | "
                "{extra[user_id]}@{extra[username]} | "
                "{name}:{function}:{line} | "
                "{message}\n"
                "{exception}"
            ),
            level="ERROR",
            enqueue=True,
            backtrace=True,
            diagnose=True
        )
        
        # 配置默认上下文
        logger.configure(
            extra={"user_id": None, "username": "system"}
        )
    
    def _setup_csv_logging(self):
        """设置 CSV 格式日志(兼容现有查询工具) - 存储在当天日期文件夹下"""
        def csv_sink(message):
            """CSV 格式 sink - 线程安全"""
            try:
                # 检查是否跨天
                self._check_and_update_log_dir()
                
                record = message.record
                csv_file = self.current_log_dir / "app_logs.csv"
                
                # 初始化 CSV 文件(如果不存在)
                file_exists = csv_file.exists()
                
                if not file_exists:
                    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                        writer = csv.writer(f)
                        writer.writerow([
                            'timestamp', 'level', 'user_id', 'username',
                            'module', 'function', 'line_number', 'message',
                            'exception_type', 'stack_trace', 'extra_data'
                        ])
                
                # 写入日志记录
                with open(csv_file, 'a', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    
                    # 处理异常信息
                    exception_type = ''
                    stack_trace = ''
                    if record['exception']:
                        exception_type = record['exception'].type.__name__
                        # 格式化堆栈信息(移除过长的堆栈)
                        stack_lines = str(record['exception']).split('\n')
                        stack_trace = '\n'.join(stack_lines[:20])
                    
                    writer.writerow([
                        record['time'].strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
                        record['level'].name,
                        record['extra'].get('user_id', ''),
                        record['extra'].get('username', ''),
                        record['name'],
                        record['function'],
                        record['line'],
                        record['message'],
                        exception_type,
                        stack_trace,
                        json.dumps(record['extra'].get('extra_data', {}), ensure_ascii=False)
                    ])
            except Exception as e:
                # 备用日志记录(避免日志系统本身出错)
                print(f"CSV 日志写入失败: {e}")
        
        # 添加 CSV sink
        logger.add(
            csv_sink,
            level="INFO",
            enqueue=True  # 异步写入
        )
    
    def _start_cleanup_task(self):
        """启动定时清理任务(清理过期的日志文件夹)"""
        def cleanup_worker():
            """后台清理线程"""
            while True:
                try:
                    # 每天凌晨2点执行清理
                    now = datetime.now()
                    next_run = now.replace(hour=2, minute=0, second=0, microsecond=0)
                    if next_run <= now:
                        next_run += timedelta(days=1)
                    
                    sleep_seconds = (next_run - now).total_seconds()
                    threading.Event().wait(sleep_seconds)
                    
                    # 执行清理
                    self._cleanup_old_log_folders()
                    
                except Exception as e:
                    logger.error(f"日志清理任务异常: {e}")
                    # 出错后等待1小时再重试
                    threading.Event().wait(3600)
        
        # 启动后台线程
        cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True, name="LogCleanup")
        cleanup_thread.start()
        logger.info("🧹 日志清理后台任务已启动")
    
    def _cleanup_old_log_folders(self):
        """清理过期的日志文件夹"""
        try:
            cutoff_date = datetime.now() - timedelta(days=self.max_log_days)
            deleted_count = 0
            
            # 遍历所有日期文件夹
            for log_folder in self.log_base_dir.iterdir():
                if not log_folder.is_dir():
                    continue
                
                try:
                    # 解析文件夹名(格式: YYYY-MM-DD)
                    folder_date = datetime.strptime(log_folder.name, '%Y-%m-%d')
                    
                    # 检查是否过期
                    if folder_date < cutoff_date:
                        # 删除整个文件夹
                        import shutil
                        shutil.rmtree(log_folder)
                        deleted_count += 1
                        logger.info(f"🗑️ 已删除过期日志文件夹: {log_folder.name}")
                
                except (ValueError, OSError) as e:
                    logger.warning(f"跳过无效的日志文件夹: {log_folder.name} - {e}")
                    continue
            
            if deleted_count > 0:
                logger.success(f"✅ 日志清理完成,共删除 {deleted_count} 个过期文件夹")
            else:
                logger.warning("✅ 日志清理完成,无过期文件夹")
        
        except Exception as e:
            logger.error(f"清理日志文件夹失败: {e}")
    
    def _get_user_context(self) -> Dict[str, Any]:
        """
        获取当前用户上下文 - 改进版
        
        修复说明:
        - 增加了更详细的调试信息
        - 区分不同的未登录状态: guest(未登录) vs anonymous(获取失败)
        """
        try:
            from auth.auth_manager import auth_manager
            user = auth_manager.current_user
            
            if user:
                return {
                    'user_id': user.id,
                    'username': user.username
                }
            else:
                # 未登录状态,返回 guest
                return {'user_id': None, 'username': 'system'}
                
        except ImportError:
            # auth 模块未加载
            return {'user_id': None, 'username': 'system'}
        except Exception as e:
            # 其他异常,记录错误原因
            logger.warning(f"⚠️ 获取用户上下文失败: {e}")
            return {'user_id': None, 'username': 'anonymous'}
    
    def _bind_context(self, extra_data: Optional[Dict] = None, depth: int = 0):
        """
        绑定用户上下文到日志 - 修复版
        
        关键修复:
        使用 opt(depth=depth) 让 Loguru 正确追踪调用栈位置
        
        Args:
            extra_data: 额外数据
            depth: 调用栈深度
                   - 0: 当前函数 (_bind_context)
                   - 1: 调用者 (如 log_info)
                   - 2: 调用者的调用者 (全局函数 -> 类方法)
        
        Returns:
            绑定了上下文的 logger 实例
        """
        context = self._get_user_context()
        if extra_data:
            context['extra_data'] = extra_data
        
        # 🔧 关键修复: 使用 opt(depth=depth) 正确追踪调用栈
        return logger.opt(depth=depth).bind(**context)
    
    # =========================================================================
    # 核心日志方法 - 修复版 (depth=1)
    # =========================================================================
    
    def log_trace(self, message: str, extra_data: Optional[str] = None):
        """记录追踪日志 (最详细)"""
        extra = json.loads(extra_data) if extra_data else {}
        # depth=1: 跳过当前函数,记录调用者位置
        self._bind_context(extra, depth=1).trace(message)
    
    def log_debug(self, message: str, extra_data: Optional[str] = None):
        """记录调试日志"""
        extra = json.loads(extra_data) if extra_data else {}
        self._bind_context(extra, depth=1).debug(message)
    
    def log_info(self, message: str, extra_data: Optional[str] = None):
        """记录信息日志 (兼容现有 API)"""
        extra = json.loads(extra_data) if extra_data else {}
        self._bind_context(extra, depth=1).info(message)
    
    def log_success(self, message: str, extra_data: Optional[str] = None):
        """记录成功日志"""
        extra = json.loads(extra_data) if extra_data else {}
        self._bind_context(extra, depth=1).success(message)
    
    def log_warning(self, message: str, extra_data: Optional[str] = None):
        """记录警告日志"""
        extra = json.loads(extra_data) if extra_data else {}
        self._bind_context(extra, depth=1).warning(message)
    
    def log_error(self, message: str, exception: Optional[Exception] = None, 
                  extra_data: Optional[str] = None):
        """记录错误日志 (兼容现有 API)"""
        extra = json.loads(extra_data) if extra_data else {}
        log_func = self._bind_context(extra, depth=1)
        
        if exception:
            log_func.opt(exception=exception).error(message)
        else:
            log_func.error(message)
    
    def log_critical(self, message: str, exception: Optional[Exception] = None,
                     extra_data: Optional[str] = None):
        """记录严重错误日志"""
        extra = json.loads(extra_data) if extra_data else {}
        log_func = self._bind_context(extra, depth=1)
        
        if exception:
            log_func.opt(exception=exception).critical(message)
        else:
            log_func.critical(message)
    
    # =========================================================================
    # 安全执行方法 - 兼容现有 API
    # =========================================================================
    
    def safe(self, func: Callable, *args, return_value: Any = None,
             show_error: bool = True, error_msg: str = None, **kwargs) -> Any:
        """万能安全执行函数 (兼容现有 API)"""
        try:
            self.log_info(f"    │   ├──safe开始安全执行函数: {func.__name__}")
            result = func(*args, **kwargs)
            self.log_info(f"    │   ├──safe安全函数执行成功: {func.__name__}")
            return result
            
        except Exception as e:
            error_message = error_msg or f"函数 {func.__name__} 执行失败: {str(e)}"
            self.log_error(error_message, exception=e)
            
            if show_error:
                try:
                    ui.notify(error_message, type='negative', timeout=5000)
                except Exception:
                    print(f"错误提示显示失败: {error_message}")
            
            return return_value
    
    @contextmanager
    def db_safe(self, operation_name: str = "数据库操作"):
        """数据库操作安全上下文管理器 (兼容现有 API)"""
        from auth.database import get_db
        
        try:
            with get_db() as db:
                yield db
                
        except Exception as e:
            self.log_error(f"数据库操作失败: {operation_name}", exception=e)
            try:
                ui.notify(f"数据库操作失败: {operation_name}", type='negative')
            except:
                pass
            raise
    
    def safe_protect(self, name: str = None, error_msg: str = None, 
                     return_on_error: Any = None):
        """页面/函数保护装饰器 (兼容现有 API)"""
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                func_name = name or func.__name__
                
                try:
                    self.log_info(f"├──开始页面保护执行：{func_name} ")
                    result = func(*args, **kwargs)
                    self.log_info(f"├──完成页面保护执行: {func_name} ")
                    return result
                
                except Exception as e:
                    error_message = error_msg or f"页面 {func_name} 加载失败"
                    self.log_error(f"{func_name}执行失败", exception=e)
                    
                    try:
                        with ui.row().classes('fit items-center justify-center'):
                            # 显示友好的错误页面
                            # 移除 'w-full' 和 'min-h-96'，让内容区域根据内部元素大小自适应
                            with ui.column().classes('p-6 text-center'): # 只需要 text-center 来对 column 内部的文本和行元素进行水平居中
                                ui.icon('error_outline', size='4rem').classes('text-red-500 mb-4')
                                ui.label(f'{func_name} 执行失败').classes('text-2xl font-bold text-red-600 mb-2')
                                ui.label(error_message).classes('text-gray-600 mb-4')

                                # 按钮行，需要让它在 column 中保持居中
                                # 'mx-auto' 是使块级元素（如 ui.row）水平居中的 Tailwind 类
                                with ui.row().classes('gap-2 mt-6 mx-auto'):
                                    ui.button('刷新页面', icon='refresh',
                                                on_click=lambda: ui.navigate.reload()).classes('bg-blue-500 text-white')
                                    ui.button('返回首页', icon='home',
                                                on_click=lambda: ui.navigate.to('/workbench')).classes('bg-gray-500 text-white')
                        
                    except Exception:
                        print(f"错误页面显示失败: {error_message}")
                    
                    return return_on_error
            
            return wrapper
        return decorator
    
    # =========================================================================
    # Loguru 特色功能 - 新增方法
    # =========================================================================
    
    def catch(self, func: Callable = None, *, message: str = None, 
              show_ui_error: bool = True):
        """Loguru 异常捕获装饰器"""
        def decorator(f: Callable) -> Callable:
            @functools.wraps(f)
            @logger.catch(message=message or f"Error in {f.__name__}")
            def wrapper(*args, **kwargs):
                try:
                    return f(*args, **kwargs)
                except Exception as e:
                    if show_ui_error:
                        try:
                            ui.notify(f"{f.__name__} 执行失败", type='negative')
                        except:
                            pass
                    raise
            return wrapper
        
        # 支持 @catch 和 @catch() 两种用法
        if func is None:
            return decorator
        else:
            return decorator(func)
    
    def get_logger(self, name: str = None):
        """
        获取绑定用户上下文的 logger 实例
        使用方法:
            log = handler.get_logger("my_module")
            log.info("This is a message")
        """
        context = self._get_user_context()
        bound_logger = logger.bind(**context)
        
        if name:
            bound_logger = bound_logger.bind(module_name=name)
        
        return bound_logger

# =============================================================================
# 全局单例实例
# =============================================================================

_exception_handler = None
_handler_lock = threading.Lock()

def get_exception_handler() -> LoguruExceptionHandler:
    """获取异常处理器单例(线程安全)"""
    global _exception_handler
    if _exception_handler is None:
        with _handler_lock:
            if _exception_handler is None:
                _exception_handler = LoguruExceptionHandler()
    return _exception_handler

# =============================================================================
# 对外暴露的核心函数 - 完全兼容现有 API (修复版 depth=2)
# =============================================================================

def log_trace(message: str, extra_data: Optional[str] = None):
    """记录追踪日志"""
    handler = get_exception_handler()
    extra = json.loads(extra_data) if extra_data else {}
    # 🔧 depth=2: 跳过当前函数 + _bind_context,记录真实调用者
    handler._bind_context(extra, depth=2).trace(message)

def log_debug(message: str, extra_data: Optional[str] = None):
    """记录调试日志"""
    handler = get_exception_handler()
    extra = json.loads(extra_data) if extra_data else {}
    handler._bind_context(extra, depth=2).debug(message)

def log_info(message: str, extra_data: Optional[str] = None):
    """记录信息日志 (兼容现有 API)"""
    handler = get_exception_handler()
    extra = json.loads(extra_data) if extra_data else {}
    handler._bind_context(extra, depth=2).info(message)

def log_success(message: str, extra_data: Optional[str] = None):
    """记录成功日志"""
    handler = get_exception_handler()
    extra = json.loads(extra_data) if extra_data else {}
    handler._bind_context(extra, depth=2).success(message)

def log_warning(message: str, extra_data: Optional[str] = None):
    """记录警告日志"""
    handler = get_exception_handler()
    extra = json.loads(extra_data) if extra_data else {}
    handler._bind_context(extra, depth=2).warning(message)

def log_error(message: str, exception: Optional[Exception] = None,
              extra_data: Optional[str] = None):
    """记录错误日志 (兼容现有 API)"""
    handler = get_exception_handler()
    extra = json.loads(extra_data) if extra_data else {}
    log_func = handler._bind_context(extra, depth=2)
    
    if exception:
        log_func.opt(exception=exception).error(message)
    else:
        log_func.error(message)

def log_critical(message: str, exception: Optional[Exception] = None,
                 extra_data: Optional[str] = None):
    """记录严重错误日志"""
    handler = get_exception_handler()
    extra = json.loads(extra_data) if extra_data else {}
    log_func = handler._bind_context(extra, depth=2)
    
    if exception:
        log_func.opt(exception=exception).critical(message)
    else:
        log_func.critical(message)

def safe(func: Callable, *args, return_value: Any = None,
         show_error: bool = True, error_msg: str = None, **kwargs) -> Any:
    """万能安全执行函数 (兼容现有 API)"""
    handler = get_exception_handler()
    return handler.safe(func, *args, return_value=return_value,
                       show_error=show_error, error_msg=error_msg, **kwargs)

@contextmanager
def db_safe(operation_name: str = "数据库操作"):
    """数据库操作安全上下文管理器 (兼容现有 API)"""
    handler = get_exception_handler()
    with handler.db_safe(operation_name) as db:
        yield db

def safe_protect(name: str = None, error_msg: str = None, return_on_error: Any = None):
    """页面/函数保护装饰器 (兼容现有 API)"""
    handler = get_exception_handler()
    return handler.safe_protect(name, error_msg, return_on_error)

def catch(func: Callable = None, *, message: str = None, show_ui_error: bool = True):
    """Loguru 异常捕获装饰器"""
    handler = get_exception_handler()
    return handler.catch(func, message=message, show_ui_error=show_ui_error)

def get_logger(name: str = None):
    """获取绑定用户上下文的 logger 实例"""
    handler = get_exception_handler()
    return handler.get_logger(name)

# =============================================================================
# 日志查询和管理工具函数 - 兼容现有 API (适配日期文件夹结构)
# =============================================================================

def get_log_files(days: int = 7) -> List[Dict]:
    """获取最近几天的日志文件列表 (兼容现有 API)"""
    handler = get_exception_handler()
    log_files = []
    
    for i in range(days):
        date = datetime.now() - timedelta(days=i)
        date_str = date.strftime('%Y-%m-%d')
        date_folder = handler.log_base_dir / date_str
        
        if not date_folder.exists():
            continue
        
        # CSV 格式日志文件
        csv_file = date_folder / 'app_logs.csv'
        if csv_file.exists():
            log_files.append({
                'date': date_str,
                'file_path': csv_file,
                'size': csv_file.stat().st_size,
                'type': 'csv'
            })
        
        # 普通日志文件
        log_file = date_folder / 'app.log'
        if log_file.exists():
            log_files.append({
                'date': date_str,
                'file_path': log_file,
                'size': log_file.stat().st_size,
                'type': 'log'
            })
        
        # 错误日志文件
        error_file = date_folder / 'error.log'
        if error_file.exists():
            log_files.append({
                'date': date_str,
                'file_path': error_file,
                'size': error_file.stat().st_size,
                'type': 'error'
            })
    
    return log_files

def get_today_errors(limit: int = 50) -> List[Dict]:
    """获取今天的错误日志 (兼容现有 API)"""
    handler = get_exception_handler()
    today_folder = handler.current_log_dir
    csv_file = today_folder / "app_logs.csv"
    
    if not csv_file.exists():
        return []
    
    try:
        errors = []
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['level'] in ['ERROR', 'CRITICAL']:
                    errors.append(row)
        
        return errors[-limit:] if len(errors) > limit else errors
    
    except Exception as e:
        print(f"读取错误日志失败: {e}")
        return []

def get_today_logs_by_level(level: str = "INFO", limit: int = 100) -> List[Dict]:
    """根据日志级别获取今天的日志"""
    handler = get_exception_handler()
    today_folder = handler.current_log_dir
    csv_file = today_folder / "app_logs.csv"
    
    if not csv_file.exists():
        return []
    
    try:
        logs = []
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['level'] == level.upper():
                    logs.append(row)
        
        return logs[-limit:] if len(logs) > limit else logs
    
    except Exception as e:
        print(f"读取日志失败: {e}")
        return []

def cleanup_logs(days_to_keep: int = 30):
    """手动清理旧日志文件夹 (兼容现有 API)"""
    handler = get_exception_handler()
    handler.max_log_days = days_to_keep
    handler._cleanup_old_log_folders()
    log_info(f"日志清理完成: 保留 {days_to_keep} 天")

def get_log_statistics(days: int = 7) -> Dict[str, Any]:
    """获取日志统计信息"""
    handler = get_exception_handler()
    stats = {
        'total_logs': 0,
        'error_count': 0,
        'warning_count': 0,
        'info_count': 0,
        'by_date': {},
        'by_level': {},
        'by_user': {}
    }
    
    for i in range(days):
        date = datetime.now() - timedelta(days=i)
        date_str = date.strftime('%Y-%m-%d')
        date_folder = handler.log_base_dir / date_str
        csv_file = date_folder / 'app_logs.csv'
        
        if csv_file.exists():
            try:
                with open(csv_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        stats['total_logs'] += 1
                        
                        level = row['level']
                        stats['by_level'][level] = stats['by_level'].get(level, 0) + 1
                        
                        if level == 'ERROR':
                            stats['error_count'] += 1
                        elif level == 'WARNING':
                            stats['warning_count'] += 1
                        elif level == 'INFO':
                            stats['info_count'] += 1
                        
                        stats['by_date'][date_str] = stats['by_date'].get(date_str, 0) + 1
                        
                        username = row.get('username', 'unknown')
                        stats['by_user'][username] = stats['by_user'].get(username, 0) + 1
            
            except Exception as e:
                print(f"读取 {csv_file} 失败: {e}")
    
    return stats

def get_log_folder_info() -> Dict[str, Any]:
    """获取日志文件夹信息"""
    handler = get_exception_handler()
    
    folder_info = {
        'base_dir': str(handler.log_base_dir),
        'current_dir': str(handler.current_log_dir),
        'folder_count': 0,
        'total_size': 0,
        'folders': []
    }
    
    try:
        for log_folder in sorted(handler.log_base_dir.iterdir(), reverse=True):
            if not log_folder.is_dir():
                continue
            
            try:
                folder_size = sum(f.stat().st_size for f in log_folder.rglob('*') if f.is_file())
                
                folder_info['folders'].append({
                    'name': log_folder.name,
                    'path': str(log_folder),
                    'size': folder_size,
                    'file_count': len(list(log_folder.iterdir()))
                })
                
                folder_info['folder_count'] += 1
                folder_info['total_size'] += folder_size
            
            except Exception as e:
                print(f"读取文件夹 {log_folder} 失败: {e}")
    
    except Exception as e:
        print(f"读取日志文件夹信息失败: {e}")
    
    return folder_info

# =============================================================================
# 使用示例和测试
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("🚀 基于 Loguru 的增强异常处理器 - 测试 (v2.2 修复版)")
    print("=" * 70)
    
    # 1. 基础日志记录
    print("\n📝 测试 1: 基础日志记录")
    log_trace("这是追踪日志")
    log_debug("这是调试日志")
    log_info("应用启动", extra_data='{"version": "2.2.0", "env": "production"}')
    log_success("初始化成功")
    log_warning("这是警告日志")
    log_error("这是错误日志")
    log_critical("这是严重错误日志")
    
    # 2. 模拟业务代码调用
    print("\n🎯 测试 2: 模拟业务代码调用(验证 module/function/line 是否正确)")
    
    def business_function():
        """模拟业务函数"""
        log_info("业务函数中的信息日志")
        log_warning("业务函数中的警告日志")
        
        try:
            raise ValueError("测试异常")
        except Exception as e:
            log_error("业务函数中出现错误", exception=e)
    
    # 调用业务函数
    business_function()
    
    # 3. 查看日志文件
    print("\n📂 测试 3: 查看日志文件")
    log_files = get_log_files(1)
    print(f"今天的日志文件: {len(log_files)} 个")
    for file in log_files:
        print(f"  - {file['date']} ({file['type']}): {file['size']} bytes")
    
    # 4. 日志统计
    print("\n📈 测试 4: 日志统计")
    stats = get_log_statistics(days=1)
    print(f"总日志数: {stats['total_logs']}")
    print(f"错误数: {stats['error_count']}")
    print(f"按级别统计: {stats['by_level']}")
    
    print("\n" + "=" * 70)
    print("✅ 测试完成! 请检查 logs/YYYY-MM-DD/app_logs.csv 文件")
    print("✅ 验证: module 应该显示 '__main__'")
    print("✅ 验证: function 应该显示 'business_function'")
    print("✅ 验证: line_number 应该显示 business_function 中的实际行号")
    print("=" * 70)
```

- **webproduct_ui_template\common\safe_openai_client_pool.py**
```python
"""
SafeOpenAIClientPool - 线程安全的OpenAI客户端连接池

文件路径: \common\safe_openai_client_pool.py

专为NiceGUI应用设计的OpenAI客户端管理器，提供线程安全的客户端创建、缓存和管理功能。

特性：
- 异步锁保证并发安全，避免重复创建客户端
- 智能缓存机制，按模型配置缓存客户端实例
- 自动内存管理，支持LRU缓存清理
- 完善的错误处理和用户友好的提示
- 详细的统计信息和性能监控
- 配置更新时自动刷新客户端
- 支持配置函数和配置字典两种传参方式

设计原则：
1. 线程安全：使用asyncio.Lock()防止并发创建
2. 内存高效：限制缓存大小，自动清理旧客户端
3. 用户友好：提供清晰的错误信息和状态提示
4. 可观测性：详细的日志和统计信息
5. 容错性：优雅处理各种异常情况
6. 兼容性：支持多种配置传递方式
"""

import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, Optional, Set, Any, Union, Callable
from openai import OpenAI


class SafeOpenAIClientPool:
    """
    线程安全的OpenAI客户端连接池
    
    使用场景：
    - NiceGUI应用的聊天功能
    - 多用户并发访问OpenAI API
    - 动态模型切换
    - 配置热更新
    """
    
    def __init__(self, max_clients: int = 20, client_ttl_hours: int = 24):
        """
        初始化客户端池
        
        Args:
            max_clients: 最大缓存的客户端数量，防止内存泄漏
            client_ttl_hours: 客户端生存时间（小时），超时自动清理
        """
        # 客户端缓存
        self._clients: Dict[str, OpenAI] = {}
        self._client_configs: Dict[str, Dict] = {}  # 缓存配置信息，用于验证
        self._creation_times: Dict[str, datetime] = {}  # 记录创建时间
        self._access_times: Dict[str, datetime] = {}  # 记录最后访问时间
        self._access_counts: Dict[str, int] = {}  # 记录访问次数
        
        # 并发控制
        self._lock = asyncio.Lock()  # 异步锁，确保线程安全
        self._creating: Set[str] = set()  # 正在创建的客户端标记
        
        # 配置参数
        self._max_clients = max_clients
        self._client_ttl = timedelta(hours=client_ttl_hours)
        
        # 统计信息
        self._total_requests = 0
        self._cache_hits = 0
        self._cache_misses = 0
        self._creation_count = 0
        self._cleanup_count = 0
        
        print(f"🔧 SafeOpenAIClientPool 已初始化")
        print(f"   最大缓存: {max_clients} 个客户端")
        print(f"   客户端TTL: {client_ttl_hours} 小时")
    
    async def get_client(self, model_key: str, config_getter_func=None) -> Optional[OpenAI]:
        """
        获取指定模型的OpenAI客户端实例
        
        Args:
            model_key: 模型键名 (如 'deepseek-chat', 'moonshot-v1-8k')
            config_getter_func: 配置获取方式，支持：
                              - 函数：function(model_key) -> dict
                              - 字典：直接使用该配置
                              - None：尝试自动导入配置函数
            
        Returns:
            OpenAI客户端实例，失败时返回None
        """
        self._total_requests += 1
        start_time = time.time()
        
        try:
            # 清理过期的客户端
            await self._cleanup_expired_clients()
            
            # 快速路径：缓存命中且有效
            if await self._is_client_valid(model_key):
                self._cache_hits += 1
                self._access_counts[model_key] = self._access_counts.get(model_key, 0) + 1
                self._access_times[model_key] = datetime.now()
                
                elapsed_ms = (time.time() - start_time) * 1000
                print(f"⚡ 缓存命中: {model_key} ({elapsed_ms:.1f}ms)")
                return self._clients[model_key]
            
            # 慢速路径：需要创建新客户端
            self._cache_misses += 1
            return await self._create_client_safe(model_key, config_getter_func, start_time)
            
        except Exception as e:
            elapsed_ms = (time.time() - start_time) * 1000
            error_msg = f"获取OpenAI客户端失败 ({model_key}): {str(e)}"
            print(f"❌ {error_msg} ({elapsed_ms:.1f}ms)")
            return None
    
    async def _is_client_valid(self, model_key: str) -> bool:
        """
        检查缓存的客户端是否仍然有效
        
        Args:
            model_key: 模型键名
            
        Returns:
            客户端是否有效
        """
        if model_key not in self._clients:
            return False
        
        # 检查是否过期
        creation_time = self._creation_times.get(model_key)
        if creation_time and datetime.now() - creation_time > self._client_ttl:
            print(f"⏰ 客户端已过期: {model_key}")
            await self._remove_client(model_key)
            return False
        
        # 简单的有效性检查
        try:
            client = self._clients[model_key]
            return hasattr(client, 'api_key') and hasattr(client, 'base_url')
        except Exception:
            return False
    
    async def _create_client_safe(self, model_key: str, config_getter_func, start_time: float) -> Optional[OpenAI]:
        """
        线程安全的客户端创建方法
        
        Args:
            model_key: 模型键名
            config_getter_func: 配置获取方式
            start_time: 开始时间（用于性能统计）
            
        Returns:
            创建的OpenAI客户端实例
        """
        # 检查是否正在创建，避免重复创建
        if model_key in self._creating:
            print(f"⏳ 等待客户端创建完成: {model_key}")
            
            # 等待其他协程完成创建（最多等待10秒）
            wait_start = time.time()
            while model_key in self._creating and (time.time() - wait_start) < 10:
                await asyncio.sleep(0.01)
            
            # 检查是否创建成功
            if model_key in self._clients:
                elapsed_ms = (time.time() - start_time) * 1000
                print(f"✅ 等待完成，获取客户端: {model_key} ({elapsed_ms:.1f}ms)")
                return self._clients[model_key]
            else:
                print(f"⚠️ 等待客户端创建超时或失败: {model_key}")
                return None
        
        # 获取异步锁，确保只有一个协程创建客户端
        async with self._lock:
            # 双重检查锁定模式
            if model_key in self._clients:
                elapsed_ms = (time.time() - start_time) * 1000
                print(f"🔄 锁内缓存命中: {model_key} ({elapsed_ms:.1f}ms)")
                return self._clients[model_key]
            
            # 标记为正在创建
            self._creating.add(model_key)
            
            try:
                return await self._create_client_internal(model_key, config_getter_func, start_time)
            finally:
                # 无论成功失败，都要清除创建标记
                self._creating.discard(model_key)
    
    async def _create_client_internal(self, model_key: str, config_getter_func, start_time: float) -> Optional[OpenAI]:
        """
        内部客户端创建方法
        
        Args:
            model_key: 模型键名
            config_getter_func: 配置获取方式
            start_time: 开始时间
            
        Returns:
            创建的OpenAI客户端实例
        """
        print(f"🔨 开始创建OpenAI客户端: {model_key}")
        
        try:
            # 获取模型配置
            config = await self._get_model_config(model_key, config_getter_func)
            if not config:
                raise ValueError(f"无法获取模型配置: {model_key}")
            
            # 验证必要的配置项
            api_key = config.get('api_key', '').strip()
            base_url = config.get('base_url', '').strip()
            
            if not api_key:
                raise ValueError(f"模型 {model_key} 缺少有效的 API Key")
            
            if not base_url:
                raise ValueError(f"模型 {model_key} 缺少有效的 Base URL")
            
            # 检查缓存是否已满，如需要则清理
            await self._check_and_cleanup_cache()
            
            # 创建OpenAI客户端实例
            client = OpenAI(
                api_key=api_key,
                base_url=base_url,
                timeout=config.get('timeout', 60),
                max_retries=config.get('max_retries', 3)
            )
            
            # 缓存客户端和相关信息
            current_time = datetime.now()
            self._clients[model_key] = client
            self._client_configs[model_key] = config.copy()
            self._creation_times[model_key] = current_time
            self._access_times[model_key] = current_time
            self._access_counts[model_key] = 1
            self._creation_count += 1
            
            elapsed_ms = (time.time() - start_time) * 1000
            model_name = config.get('name', model_key)
            
            print(f"✅ 客户端创建成功: {model_name} ({elapsed_ms:.1f}ms)")
            print(f"   API Key: {api_key[:12]}...")
            print(f"   Base URL: {base_url}")
            
            return client
            
        except Exception as e:
            error_msg = f"创建OpenAI客户端失败 ({model_key}): {str(e)}"
            print(f"❌ {error_msg}")
            raise
    
    async def _get_model_config(self, model_key: str, config_getter_func) -> Optional[Dict]:
        """
        获取模型配置信息（支持函数和字典两种方式）
        
        Args:
            model_key: 模型键名
            config_getter_func: 外部提供的配置获取方式
            
        Returns:
            模型配置字典
        """
        if config_getter_func:
            if callable(config_getter_func):
                # 使用外部提供的配置获取函数
                try:
                    config = config_getter_func(model_key)
                    if isinstance(config, dict):
                        return config
                    else:
                        print(f"⚠️ 配置获取函数返回了非字典类型: {type(config)}")
                        return None
                except Exception as e:
                    print(f"⚠️ 调用配置获取函数失败: {str(e)}")
                    return None
            elif isinstance(config_getter_func, dict):
                # 直接使用配置字典
                return config_getter_func
            else:
                print(f"⚠️ 不支持的config_getter_func类型: {type(config_getter_func)}")
                return None
        
        # 尝试自动导入配置获取函数
        try:
            # 假设配置函数在某个已知模块中
            # 这里需要根据实际项目结构调整导入路径
            from menu_pages.enterprise_archive.chat_component.config import get_model_config
            return get_model_config(model_key)
        except ImportError:
            print(f"⚠️ 无法自动导入配置获取函数，请提供 config_getter_func 参数")
            return None
    
    async def _check_and_cleanup_cache(self):
        """
        检查缓存大小并在需要时清理最少使用的客户端
        """
        if len(self._clients) >= self._max_clients:
            print(f"🧹 缓存已满 ({len(self._clients)}/{self._max_clients})，开始清理...")
            
            # 找到最少使用的客户端（LRU策略）
            if self._access_times:
                # 按最后访问时间排序，移除最久未使用的
                oldest_model = min(self._access_times.items(), key=lambda x: x[1])[0]
                await self._remove_client(oldest_model)
                self._cleanup_count += 1
                print(f"🗑️ 已清理最久未使用的客户端: {oldest_model}")
    
    async def _cleanup_expired_clients(self):
        """
        清理过期的客户端
        """
        current_time = datetime.now()
        expired_clients = []
        
        for model_key, creation_time in self._creation_times.items():
            if current_time - creation_time > self._client_ttl:
                expired_clients.append(model_key)
        
        for model_key in expired_clients:
            await self._remove_client(model_key)
            self._cleanup_count += 1
            print(f"⏰ 已清理过期客户端: {model_key}")
    
    async def _remove_client(self, model_key: str):
        """
        移除指定的客户端及其相关信息
        
        Args:
            model_key: 要移除的模型键名
        """
        self._clients.pop(model_key, None)
        self._client_configs.pop(model_key, None)
        self._creation_times.pop(model_key, None)
        self._access_times.pop(model_key, None)
        self._access_counts.pop(model_key, None)
    
    async def update_client(self, model_key: str, config_getter_func=None) -> Optional[OpenAI]:
        """
        更新指定模型的客户端（配置变更时使用）
        
        Args:
            model_key: 模型键名
            config_getter_func: 配置获取方式
            
        Returns:
            更新后的客户端实例
        """
        print(f"🔄 更新客户端: {model_key}")
        
        # 移除旧客户端
        await self._remove_client(model_key)
        
        # 创建新客户端
        return await self.get_client(model_key, config_getter_func)
    
    async def clear_cache(self) -> int:
        """
        清空所有缓存的客户端
        
        Returns:
            清理的客户端数量
        """
        async with self._lock:
            cleared_count = len(self._clients)
            
            self._clients.clear()
            self._client_configs.clear()
            self._creation_times.clear()
            self._access_times.clear()
            self._access_counts.clear()
            
            self._cleanup_count += cleared_count
            
            print(f"🧹 已清空所有客户端缓存，共清理 {cleared_count} 个客户端")
            return cleared_count
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取客户端池的统计信息
        
        Returns:
            包含各种统计信息的字典
        """
        cache_hit_rate = (self._cache_hits / self._total_requests * 100) if self._total_requests > 0 else 0.0
        
        return {
            # 基本状态
            'cached_clients': len(self._clients),
            'creating_clients': len(self._creating),
            'max_clients': self._max_clients,
            'models': list(self._clients.keys()),
            
            # 性能统计
            'total_requests': self._total_requests,
            'cache_hits': self._cache_hits,
            'cache_misses': self._cache_misses,
            'cache_hit_rate': f"{cache_hit_rate:.1f}%",
            'creation_count': self._creation_count,
            'cleanup_count': self._cleanup_count,
            
            # 详细信息
            'access_counts': self._access_counts.copy(),
            'creation_times': {
                k: v.strftime('%H:%M:%S') for k, v in self._creation_times.items()
            },
            'access_times': {
                k: v.strftime('%H:%M:%S') for k, v in self._access_times.items()
            }
        }
    
    def print_stats(self):
        """
        打印详细的统计信息到控制台
        """
        stats = self.get_stats()
        
        print(f"\n📊 SafeOpenAIClientPool 统计信息")
        print(f"{'=' * 50}")
        print(f"缓存状态: {stats['cached_clients']}/{stats['max_clients']} 个客户端")
        print(f"正在创建: {stats['creating_clients']} 个")
        print(f"总请求数: {stats['total_requests']}")
        print(f"缓存命中率: {stats['cache_hit_rate']}")
        print(f"创建次数: {stats['creation_count']}")
        print(f"清理次数: {stats['cleanup_count']}")
        
        if stats['models']:
            print(f"\n📱 已缓存的模型:")
            for model in stats['models']:
                access_count = stats['access_counts'].get(model, 0)
                creation_time = stats['creation_times'].get(model, 'Unknown')
                access_time = stats['access_times'].get(model, 'Unknown')
                print(f"  • {model}")
                print(f"    访问次数: {access_count}")
                print(f"    创建时间: {creation_time}")
                print(f"    最后访问: {access_time}")
        else:
            print(f"\n暂无缓存的客户端")
        
        print()
    
    def __repr__(self):
        """返回客户端池的字符串表示"""
        return f"<SafeOpenAIClientPool(clients={len(self._clients)}/{self._max_clients}, hit_rate={self.get_stats()['cache_hit_rate']})>"


# ==================== 全局单例实例 ====================

# 全局客户端池实例（延迟初始化）
_global_client_pool: Optional[SafeOpenAIClientPool] = None

def get_openai_client_pool(max_clients: int = 20, client_ttl_hours: int = 24) -> SafeOpenAIClientPool:
    """
    获取全局OpenAI客户端池实例（单例模式）
    
    Args:
        max_clients: 最大缓存客户端数量（仅在首次调用时生效）
        client_ttl_hours: 客户端生存时间小时数（仅在首次调用时生效）
        
    Returns:
        全局客户端池实例
    """
    global _global_client_pool
    if _global_client_pool is None:
        _global_client_pool = SafeOpenAIClientPool(max_clients, client_ttl_hours)
    return _global_client_pool


# ==================== 便捷函数 ====================

async def get_openai_client(model_key: str, config_getter_func=None) -> Optional[OpenAI]:
    """
    便捷函数：获取OpenAI客户端（重构版本）
    
    Args:
        model_key: 模型键名
        config_getter_func: 配置获取方式，支持：
                          - 函数：function(model_key) -> dict
                          - 字典：直接使用该配置
                          - None：尝试自动导入配置函数
        
    Returns:
        OpenAI客户端实例
    """
    pool = get_openai_client_pool()
    
    # 重构：支持函数和字典两种方式
    if config_getter_func is None:
        # 保持原有逻辑：尝试自动导入
        return await pool.get_client(model_key, None)
    elif callable(config_getter_func):
        # 原有逻辑：传递函数
        return await pool.get_client(model_key, config_getter_func)
    elif isinstance(config_getter_func, dict):
        # 新增逻辑：直接传递配置字典
        def dict_config_getter(key: str) -> dict:
            return config_getter_func
        return await pool.get_client(model_key, dict_config_getter)
    else:
        # 其他类型，转换为字典处理
        print(f"⚠️ 未知的配置类型: {type(config_getter_func)}, 尝试作为字典处理")
        def fallback_config_getter(key: str) -> dict:
            return config_getter_func if isinstance(config_getter_func, dict) else {}
        return await pool.get_client(model_key, fallback_config_getter)

async def clear_openai_cache() -> int:
    """
    便捷函数：清空OpenAI客户端缓存
    
    Returns:
        清理的客户端数量
    """
    pool = get_openai_client_pool()
    return await pool.clear_cache()

def print_openai_stats():
    """
    便捷函数：打印OpenAI客户端池统计信息
    """
    pool = get_openai_client_pool()
    pool.print_stats()


# ==================== 使用示例 ====================

async def example_usage():
    """
    使用示例（展示重构后的多种使用方式）
    """
    print("🚀 SafeOpenAIClientPool 重构版本使用示例")
    print("=" * 60)
    
    # 方式1：使用配置获取函数（原有方式）
    def mock_get_model_config(model_key: str):
        configs = {
            'deepseek-chat': {
                'name': 'DeepSeek Chat',
                'api_key': 'sk-deepseek-test-key',
                'base_url': 'https://api.deepseek.com/v1',
                'timeout': 60
            },
            'moonshot-v1-8k': {
                'name': 'Moonshot 8K',
                'api_key': 'sk-moonshot-test-key',
                'base_url': 'https://api.moonshot.cn/v1',
                'timeout': 60
            }
        }
        return configs.get(model_key)
    
    print("\n📋 方式1：使用配置获取函数")
    client1 = await get_openai_client('deepseek-chat', mock_get_model_config)
    if client1:
        print("✅ 成功获取客户端（配置函数方式）")
    
    # 方式2：直接传递配置字典（新增方式）
    config_dict = {
        'name': 'Claude Chat',
        'api_key': 'sk-claude-test-key',
        'base_url': 'https://api.anthropic.com/v1',
        'timeout': 60
    }
    
    print("\n📋 方式2：直接传递配置字典")
    client2 = await get_openai_client('claude-3-sonnet', config_dict)
    if client2:
        print("✅ 成功获取客户端（配置字典方式）")
    
    # 方式3：自动导入配置函数（保持兼容）
    print("\n📋 方式3：自动导入配置函数")
    client3 = await get_openai_client('gpt-4', None)
    if client3:
        print("✅ 成功获取客户端（自动导入方式）")
    else:
        print("⚠️ 自动导入失败（这是正常的，因为示例环境中没有配置模块）")
    
    # 打印统计信息
    print_openai_stats()
    
    # 测试缓存命中
    print(f"\n🔄 测试缓存命中...")
    start_time = time.time()
    cached_client = await get_openai_client('deepseek-chat', mock_get_model_config)
    elapsed_ms = (time.time() - start_time) * 1000
    print(f"缓存命中耗时: {elapsed_ms:.1f}ms")
    
    # 清理缓存
    print(f"\n🧹 清理缓存...")
    cleared_count = await clear_openai_cache()
    print(f"已清理 {cleared_count} 个客户端")
    
    print_openai_stats()

if __name__ == "__main__":
    # 运行示例
    import asyncio
    asyncio.run(example_usage())
```

## webproduct_ui_template\component

- **webproduct_ui_template\component\__init__.py** *(包初始化文件)*
```python
"""
组件包初始化文件
导出所有布局组件和工具函数
"""

# 原有的复杂布局(包含侧边栏)
from .layout_config import LayoutConfig, MenuItem, HeaderConfigItem
from .layout_manager import LayoutManager
from .spa_layout import (
    with_spa_layout,
    create_spa_layout,
    get_layout_manager,
    register_route_handler,
    navigate_to
)

# 简单布局(只有顶部导航栏)
from .simple_layout_manager import SimpleLayoutManager
from .simple_spa_layout import (
    with_simple_spa_layout,
    create_simple_spa_layout,
    get_simple_layout_manager,
    register_simple_route_handler,
    simple_navigate_to
)

# ✨ 新增: 多层布局(折叠菜单)
from .multilayer_menu_config import (
    MultilayerMenuItem,
    MultilayerMenuConfig,
    create_menu_item,
    create_demo_menu_config
)
from .multilayer_layout_manager import MultilayerLayoutManager
from .multilayer_spa_layout import (
    with_multilayer_spa_layout,
    create_multilayer_spa_layout,
    get_multilayer_layout_manager,
    register_multilayer_route_handler,
    multilayer_navigate_to,
    multilayer_expand_parent,
    multilayer_collapse_parent,
    multilayer_select_leaf,
    multilayer_clear_route_storage
)

# 静态资源管理
from .static_resources import StaticResourceManager, static_manager

# 聊天组件
from .chat import ChatComponent


# ==================== 🆕 通用导航函数 ====================
def universal_navigate_to(route: str, label: str = None):
    """
    通用导航函数,自动检测当前使用的布局类型并调用对应的导航函数
    
    支持三种布局模式:
    1. multilayer_spa_layout (多层布局)
    2. simple_spa_layout (简单布局)
    3. spa_layout (复杂布局)
    
    Args:
        route: 目标路由
        label: 路由标签(可选,如果不提供会自动查找)
        
    Raises:
        RuntimeError: 如果没有任何布局管理器被初始化
        
    Example:
        from component import universal_navigate_to
        
        # 在任何布局中都可以使用
        universal_navigate_to('home', '首页')
    """
    # 按使用频率和优先级依次尝试
    
    # 1. 尝试多层布局
    try:
        from .multilayer_spa_layout import get_multilayer_layout_manager, multilayer_navigate_to
        get_multilayer_layout_manager()  # 检查是否初始化
        multilayer_navigate_to(route, label)
        return
    except RuntimeError:
        pass
    
    # 2. 尝试简单布局
    try:
        from .simple_spa_layout import get_simple_layout_manager, simple_navigate_to
        get_simple_layout_manager()  # 检查是否初始化
        simple_navigate_to(route, label)
        return
    except RuntimeError:
        pass
    
    # 3. 尝试复杂布局(SPA)
    try:
        from .spa_layout import get_layout_manager, navigate_to
        get_layout_manager()  # 检查是否初始化
        navigate_to(route, label)
        return
    except RuntimeError:
        pass
    
    # 如果所有布局都未初始化,抛出错误
    raise RuntimeError(
        "没有可用的布局管理器。请确保使用了以下装饰器之一:\n"
        "- @with_multilayer_spa_layout\n"
        "- @with_simple_spa_layout\n"
        "- @with_spa_layout"
    )


def get_current_layout_type():
    """
    获取当前使用的布局类型
    
    Returns:
        str: 'multilayer', 'simple', 'spa' 或 None
        
    Example:
        from component import get_current_layout_type
        
        layout_type = get_current_layout_type()
        if layout_type == 'multilayer':
            print("当前使用多层布局")
    """
    try:
        from .multilayer_spa_layout import get_multilayer_layout_manager
        get_multilayer_layout_manager()
        return 'multilayer'
    except RuntimeError:
        pass
    
    try:
        from .simple_spa_layout import get_simple_layout_manager
        get_simple_layout_manager()
        return 'simple'
    except RuntimeError:
        pass
    
    try:
        from .spa_layout import get_layout_manager
        get_layout_manager()
        return 'spa'
    except RuntimeError:
        pass
    
    return None


# 导出列表
__all__ = [
    # ==================== 布局配置 ====================
    'LayoutConfig',
    'MenuItem',
    'HeaderConfigItem',

    # ==================== 复杂布局(原有) ====================
    'LayoutManager',
    'with_spa_layout',
    'create_spa_layout',
    'get_layout_manager',
    'register_route_handler',
    'navigate_to',

    # ==================== 简单布局 ====================
    'SimpleLayoutManager',
    'with_simple_spa_layout',
    'create_simple_spa_layout',
    'get_simple_layout_manager',
    'register_simple_route_handler',
    'simple_navigate_to',

    # ==================== 多层布局(新增) ====================
    # 菜单配置
    'MultilayerMenuItem',
    'MultilayerMenuConfig',
    'create_menu_item',
    'create_demo_menu_config',

    # 布局管理器
    'MultilayerLayoutManager',

    # 装饰器和创建函数
    'with_multilayer_spa_layout',
    'create_multilayer_spa_layout',
    'get_multilayer_layout_manager',

    # 路由和导航
    'register_multilayer_route_handler',
    'multilayer_navigate_to',

    # 菜单操作
    'multilayer_expand_parent',
    'multilayer_collapse_parent',
    'multilayer_select_leaf',

    # 状态管理
    'multilayer_clear_route_storage',

    # ==================== 🆕 通用工具函数 ====================
    'universal_navigate_to',
    'get_current_layout_type',

    # ==================== 其他组件 ====================
    # 聊天组件
    'ChatComponent',

    # 静态资源
    'StaticResourceManager',
    'static_manager'
]


# 版本信息
__version__ = '2.1.0'  # 新增通用导航函数,升级到2.1

# 布局类型常量
LAYOUT_TYPE_SPA = 'spa'                    # 复杂布局(左侧菜单栏)
LAYOUT_TYPE_SIMPLE = 'simple'              # 简单布局(顶部导航栏)
LAYOUT_TYPE_MULTILAYER = 'multilayer'      # 多层布局(折叠菜单)
```

- **webproduct_ui_template\component\layout_config.py**
```python
from typing import Optional, Callable
from .static_resources import static_manager
from config.env_config import env_config

class LayoutConfig:
    """布局配置类"""
    def __init__(self):
        self.app_title = env_config.get('APP_TITLE', 'NeoUI布局模板')
        self.app_icon = static_manager.get_logo_path('robot.svg')
        self.header_bg = 'bg-[#3874c8] dark:bg-gray-900'
        self.drawer_bg = 'bg-[#ebf1fa] dark:bg-gray-800'
        self.drawer_width = 'w-64'
        self.menu_title = '菜单栏'
        # 新增：自定义CSS文件路径
        self.custom_css = static_manager.get_css_path('custom.css')
        # 新增：favicon路径
        self.favicon = static_manager.get_image_path('logo', 'favicon.ico')

class MenuItem:
    """菜单项类"""
    def __init__(self, key: str, label: str, icon: str, route: Optional[str] = None, separator_after: bool = False, custom_icon_path: Optional[str] = None):
        self.key = key
        self.label = label
        self.icon = icon
        self.route = route  # 路由标识（用于SPA内部切换）
        self.separator_after = separator_after
        # 新增：自定义图标路径（如果提供则使用自定义图标而非Material Icons）
        self.custom_icon_path = custom_icon_path

class HeaderConfigItem:
    """头部配置项类"""
    def __init__(self, key: str, label: Optional[str] = None, icon: Optional[str] = None, route: Optional[str] = None, on_click: Optional[Callable] = None, custom_icon_path: Optional[str] = None):
        self.key = key
        self.label = label
        self.icon = icon
        self.route = route
        self.on_click = on_click
        # 新增：自定义图标路径
        self.custom_icon_path = custom_icon_path
```

- **webproduct_ui_template\component\layout_manager.py**
```python
from nicegui import ui, app
from typing import List, Dict, Callable, Optional
from .layout_config import LayoutConfig, MenuItem, HeaderConfigItem
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

class LayoutManager:
    """布局管理器 - 完整的路由状态管理"""
    def __init__(self, config: LayoutConfig):
        self.config = config
        self.menu_items: List[MenuItem] = []
        self.header_config_items: List[HeaderConfigItem] = []
        self.selected_menu_item_row = {'element': None, 'key': None}
        self.content_container = None
        self.left_drawer = None
        self.dark_mode = None
        self.route_handlers: Dict[str, Callable] = {}
        self.current_route = None
        self.menu_rows: Dict[str, any] = {}
        
        # 主题切换
        self._theme_key = 'theme' 
        initial_theme = app.storage.user.get(self._theme_key, False)
        app.storage.user[self._theme_key] = initial_theme   # 确保键存在
        # 新增：所有可能的路由映射
        self.all_routes: Dict[str, str] = {}  # route -> label 的映射

    def add_menu_item(self, key: str, label: str, icon: str, route: Optional[str] = None, separator_after: bool = False):
        """添加菜单项"""
        self.menu_items.append(MenuItem(key, label, icon, route, separator_after))
        # 注册路由映射
        if route:
            self.all_routes[route] = label

    def add_header_config_item(self, key: str, label: Optional[str] = None, icon: Optional[str] = None, route: Optional[str] = None, on_click: Optional[Callable] = None):
        """添加头部配置项"""
        self.header_config_items.append(HeaderConfigItem(key, label, icon, route, on_click))
        # 注册路由映射
        if route:
            self.all_routes[route] = label or key

    def set_route_handler(self, route: str, handler: Callable):
        """设置路由处理器"""
        self.route_handlers[route] = handler        
        # 如果路由映射中没有这个路由，添加一个默认标签
        if route not in self.all_routes:
            self.all_routes[route] = route.replace('_', ' ').title()

    def register_system_routes(self):
        """注册系统路由（设置菜单、用户菜单等）"""
        system_routes = {
            # 设置菜单路由
            'user_management': '用户管理',
            'role_management': '角色管理', 
            'permission_management': '权限管理',
            # ✅ 新增: 配置管理路由
            'llm_config_management': '大模型配置',
            'prompt_config_management': '提示词配置',  # ✅ 新增
            # 用户菜单路由（排除logout）
            'user_profile': '个人资料',
            'change_password': '修改密码',
            # 注意：不包含 'logout'，因为注销是一次性操作，不应该被恢复
            # 其他系统路由
            'no_permission': '权限不足',
            'login': '登录',
            'register': '注册'
        }
        
        for route, label in system_routes.items():
            self.all_routes[route] = label
            
        # logger.debug(f"🔧 已注册系统路由: {list(system_routes.keys())}")
        # logger.debug(f"🔧 注册的全部路由：{self.all_routes}")
        # logger.debug(f"⚠️ 注意：logout 路由未注册到持久化路由中（一次性操作）")

    def select_menu_item(self, key: str, row_element=None, update_storage: bool = True):
        """选择菜单项"""
        if self.selected_menu_item_row['key'] == key:
            return

        # 清除之前的选中状态
        if self.selected_menu_item_row['element'] is not None:
            self.selected_menu_item_row['element'].classes(remove='bg-blue-200 dark:bg-blue-700')

        # 设置新的选中状态
        target_row = row_element or self.menu_rows.get(key)
        if target_row:
            target_row.classes(add='bg-blue-200 dark:bg-blue-700')
            self.selected_menu_item_row['element'] = target_row
        
        self.selected_menu_item_row['key'] = key

        menu_item = next((item for item in self.menu_items if item.key == key), None)
        if not menu_item:
            return

        ui.notify(f'切换到{menu_item.label}')

        if menu_item.route:
            self.navigate_to_route(menu_item.route, menu_item.label, update_storage)
        else:
            if self.content_container:
                self.content_container.clear()
                with self.content_container:
                    ui.label(f'{menu_item.label}内容').classes('text-2xl font-bold text-gray-800 dark:text-gray-200')

    def clear_menu_selection(self):
        """清除菜单选中状态（用于非菜单路由）"""
        if self.selected_menu_item_row['element'] is not None:
            self.selected_menu_item_row['element'].classes(remove='bg-blue-200 dark:bg-blue-700')
            self.selected_menu_item_row['element'] = None
            self.selected_menu_item_row['key'] = None

    def navigate_to_route(self, route: str, label: str, update_storage: bool = True):
        """导航到指定路由"""
        if self.current_route == route:
            return
        
        self.current_route = route
        # 如果不是菜单路由，清除菜单选中状态
        is_menu_route = any(item.route == route for item in self.menu_items)
        if not is_menu_route:
            self.clear_menu_selection()
        
        # 保存当前路由到存储（排除一次性操作路由）
        if update_storage and self._should_persist_route(route):
            try:
                app.storage.user['current_route'] = route
                logger.debug(f"💾 保存路由状态: {route}")
            except Exception as e:
                logger.debug(f"⚠️ 保存路由状态失败: {e}")
        elif not self._should_persist_route(route):
            logger.debug(f"🚫 跳过路由持久化: {route} (一次性操作)")
        
        if self.content_container:
            self.content_container.clear()

        if route in self.route_handlers:
            with self.content_container:
                try:
                    self.route_handlers[route]()
                except Exception as e:
                    logger.debug(f"❌ 路由处理器执行失败 {route}: {e}")
                    ui.label(f'页面加载失败: {str(e)}').classes('text-red-500 text-xl')
        else:
            logger.debug(f"❌ 未找到路由处理器: {route}")
            with self.content_container:
                ui.label(f'页面未找到: {label}').classes('text-2xl font-bold text-red-600')
                ui.label(f'路由 "{route}" 没有对应的处理器').classes('text-gray-600 dark:text-gray-400 mt-4')

    def _should_persist_route(self, route: str) -> bool:
        """判断路由是否应该持久化"""
        # 一次性操作路由，不应该被持久化
        non_persistent_routes = {
            'logout',      # 注销操作
            'login',       # 登录页面
            'register',    # 注册页面
        }
        return route not in non_persistent_routes

    def clear_route_storage(self):
        """清除路由存储（用于注销等场景）"""
        try:
            if 'current_route' in app.storage.user:
                del app.storage.user['current_route']
                logger.debug("🗑️ 已清除路由存储")
        except Exception as e:
            logger.debug(f"⚠️ 清除路由存储失败: {e}")

    def restore_route_from_storage(self):
        """从存储恢复路由状态 - 支持所有类型的路由"""
        try:
            # 从存储获取保存的路由
            saved_route = app.storage.user.get('current_route')
            
            # 如果没有保存的路由
            if not saved_route:
                # 如果有菜单项，选择第一个
                if self.menu_items:
                    first_item = self.menu_items[0]
                    self.select_menu_item(first_item.key, update_storage=True)
                else:
                    # 如果没有菜单项，不做任何操作
                    logger.debug("🔄 没有保存的路由，且未定义菜单项，保持空白状态")
                return
            
            # 检查路由是否在已知路由中
            if saved_route in self.all_routes:
                route_label = self.all_routes[saved_route]
                logger.debug(f"✅ 找到路由映射: {saved_route} -> {route_label}")
                
                # 检查是否是菜单项路由
                menu_item = next((item for item in self.menu_items if item.route == saved_route), None)
                if menu_item:
                    # 恢复菜单选中状态
                    self.select_menu_item(menu_item.key, update_storage=False)
                else:
                    # 直接导航到路由（不更新存储避免循环）
                    self.navigate_to_route(saved_route, route_label, update_storage=False)
                return
            
            # 兜底检查：是否在路由处理器中注册
            if saved_route in self.route_handlers:
                label = saved_route.replace('_', ' ').title()
                self.navigate_to_route(saved_route, label, update_storage=False)
                return
            
            # 如果都没找到，且有菜单项，选择第一个菜单项
            logger.debug(f"⚠️ 未找到保存的路由 {saved_route}，使用默认路由")
            if self.menu_items:
                first_item = self.menu_items[0]
                self.select_menu_item(first_item.key, update_storage=True)
            else:
                logger.debug("⚠️ 没有可用的菜单项，保持空白状态")
                
        except Exception as e:
            logger.debug(f"⚠️ 恢复路由状态失败: {e}")
            if self.menu_items:
                first_item = self.menu_items[0]
                self.select_menu_item(first_item.key, update_storage=True)
            else:
                logger.debug("⚠️ 没有可用的菜单项，保持空白状态")

    def handle_header_config_item_click(self, item: HeaderConfigItem):
        """处理头部配置项点击事件"""
        ui.notify(f'点击了头部配置项: {item.label or item.key}')
        if item.on_click:
            item.on_click()
        
        if item.route:
            self.navigate_to_route(item.route, item.label or item.key)

    def handle_settings_menu_item_click(self, route: str, label: str):
        """处理设置菜单项点击事件"""        
        from auth.auth_manager import auth_manager

        if not auth_manager.is_authenticated():
            ui.notify('请先登录', type='warning')
            self.navigate_to_route('login', '登录')
            return

        if not auth_manager.has_role('admin') and not auth_manager.current_user.is_superuser:
            ui.notify('您没有管理员权限，无法访问此功能', type='error')
            self.navigate_to_route('no_permission', '权限不足')
            return

        ui.notify(f'访问管理功能: {label}')
        self.navigate_to_route(route, label)

    def handle_user_menu_item_click(self, route: str, label: str):
        """处理用户菜单项点击事件"""
        ui.notify(f'点击了用户菜单项: {label}')
        
        # 特殊处理注销：清除路由存储
        if route == 'logout':
            logger.debug("🚪 执行用户注销，清除路由存储")
            self.clear_route_storage()
        
        self.navigate_to_route(route, label)

    def create_header(self):
        """创建头部"""
        with ui.header(elevated=True).classes(f'items-center justify-between px-4 {self.config.header_bg}'):
            with ui.row().classes('items-center gap-4'):
                ui.button(
                    on_click=lambda: self.left_drawer.toggle(),
                    icon='menu'
                ).props('flat color=white').classes('mr-2')

                with ui.avatar().classes('w-15 h-15'):
                    ui.image(self.config.app_icon).classes('w-full h-full object-contain')
                ui.label(self.config.app_title).classes('ml-4 text-xl font-medium text-white dark:text-white')

            with ui.row().classes('items-center gap-2'):
                # 头部配置项
                for item in self.header_config_items:
                    if item.icon and item.label:
                        ui.button(item.label, icon=item.icon, on_click=lambda current_item=item: self.handle_header_config_item_click(current_item)).props('flat color=white').classes('mr-2')
                    elif item.icon:
                        ui.button(icon=item.icon, on_click=lambda current_item=item: self.handle_header_config_item_click(current_item)).props('flat color=white round').classes('w-10 h-10')
                    elif item.label:
                        ui.button(item.label, on_click=lambda current_item=item: self.handle_header_config_item_click(current_item)).props('flat color=white').classes('mr-2')
                if self.header_config_items:
                    # ui.separator().props('vertical').classes('h-10')
                    ui.label("|")

                # 主题切换
                # self.dark_mode = ui.dark_mode()
                # ui.switch('主题切换').bind_value(self.dark_mode)
                self.dark_mode = ui.dark_mode(value=app.storage.user[self._theme_key])
                ui.switch('主题切换') \
                    .bind_value(self.dark_mode) \
                    .on_value_change(lambda e: app.storage.user.update({self._theme_key: e.value})) \
                    .classes('mx-2')

                # 设置菜单
                with ui.button(icon='settings').props('flat color=white round').classes('w-10 h-10'):
                    with ui.menu() as settings_menu:
                        ui.menu_item('用户管理', lambda: self.handle_settings_menu_item_click('user_management', '用户管理'))
                        ui.menu_item('角色管理', lambda: self.handle_settings_menu_item_click('role_management', '角色管理'))
                        ui.menu_item('权限管理', lambda: self.handle_settings_menu_item_click('permission_management', '权限管理'))
                        # ✅ 新增: 配置管理菜单项
                        ui.separator()  # 分隔线
                        ui.menu_item('大模型配置', lambda: self.handle_settings_menu_item_click('llm_config_management', '大模型配置'))
                        ui.menu_item('提示词配置', lambda: self.handle_settings_menu_item_click('prompt_config_management', '提示词配置'))  # ✅ 新增

                # 用户菜单
                with ui.button(icon='account_circle').props('flat color=white round').classes('w-10 h-10'):
                    with ui.menu() as user_menu:
                        ui.menu_item('个人资料', lambda: self.handle_user_menu_item_click('user_profile', '个人资料'))
                        ui.menu_item('修改密码', lambda: self.handle_user_menu_item_click('change_password', '修改密码'))
                        ui.separator()
                        ui.menu_item('注销', lambda: self.handle_user_menu_item_click('logout', '注销'))

    def create_left_drawer(self):
        """创建左侧抽屉"""
        with ui.left_drawer(fixed=False).props('bordered').classes(f'{self.config.drawer_width} {self.config.drawer_bg}') as left_drawer:
            self.left_drawer = left_drawer

            ui.label(self.config.menu_title).classes('w-full text-lg font-semibold text-gray-800 dark:text-gray-200 p-4 border-b border-gray-200 dark:border-gray-700')

            with ui.column().classes('w-full p-2 gap-1'):
                # 只有当有菜单项时才创建菜单
                if self.menu_items:
                    for menu_item in self.menu_items:
                        with ui.row().classes('w-full cursor-pointer rounded-lg hover:bg-blue-100 dark:hover:bg-blue-800 transition-colors duration-200 p-3') as menu_row:
                            ui.icon(menu_item.icon).classes('text-blue-600 mr-3 text-lg font-bold')
                            ui.label(menu_item.label).classes('text-gray-800 dark:text-gray-200 flex-1 text-lg font-bold')

                            menu_row.on('click', lambda key=menu_item.key, row=menu_row: self.select_menu_item(key, row))
                            # 保存菜单行引用
                            self.menu_rows[menu_item.key] = menu_row

                        if menu_item.separator_after:
                            ui.separator().classes('dark:bg-gray-700')
                else:
                    # 如果没有菜单项，显示提示信息
                    with ui.column().classes('w-full items-center py-8'):
                        ui.icon('menu_open').classes('text-6xl text-gray-400 mb-4')
                        ui.label('暂无菜单项').classes('text-lg font-medium text-gray-500 dark:text-gray-400')
                        ui.label('请通过头部导航或其他方式访问功能').classes('text-sm text-gray-400 dark:text-gray-500 text-center')

                # 注册系统路由并恢复路由状态
                def init_routes():
                    self.register_system_routes()
                    self.restore_route_from_storage()
                
                ui.timer(0.3, init_routes, once=True)

    def create_content_area(self):
        """创建内容区域"""
        with ui.column().classes('w-full') as content_container:
            self.content_container = content_container
```

- **webproduct_ui_template\component\multilayer_layout_manager.py**
```python
"""
多层布局管理器
实现多层级折叠菜单的UI渲染和交互逻辑
✨ 优化版本: 改善了菜单项间距,使其更加美观舒适
"""
from nicegui import ui, app
from typing import List, Dict, Callable, Optional, Set
from .layout_config import LayoutConfig, HeaderConfigItem
from .multilayer_menu_config import MultilayerMenuItem, MultilayerMenuConfig
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

class MultilayerLayoutManager:
    """多层布局管理器 - 支持折叠菜单的完整布局管理"""
    
    def __init__(self, config: LayoutConfig):
        self.config = config
        self.menu_config = MultilayerMenuConfig()
        self.header_config_items: List[HeaderConfigItem] = []
        
        # UI组件引用
        self.content_container = None
        self.left_drawer = None
        self.dark_mode = None
        
        # 路由和状态管理
        self.route_handlers: Dict[str, Callable] = {}
        self.current_route = None
        self.current_label = None
        
        # 展开状态管理
        self.expanded_keys: Set[str] = set()          # 当前展开的父节点keys
        self.selected_leaf_key: Optional[str] = None  # 当前选中的叶子节点key
        
        # UI元素引用映射
        self.expansion_refs: Dict[str, any] = {}  # key -> ui.expansion对象
        self.leaf_refs: Dict[str, any] = {}       # key -> 叶子节点ui.row对象
        
        # 存储键
        self._route_key = 'multilayer_current_route'
        self._label_key = 'multilayer_current_label'
        self._expanded_keys_key = 'multilayer_expanded_keys'
        self._theme_key = 'theme'
        
        # 初始化主题
        initial_theme = app.storage.user.get(self._theme_key, False)
        app.storage.user[self._theme_key] = initial_theme
        
        # 所有可能的路由映射
        self.all_routes: Dict[str, str] = {}
    
    def add_menu_item(self, item: MultilayerMenuItem):
        """添加顶层菜单项"""
        self.menu_config.add_menu_item(item)
        self._update_route_mappings()
    
    def _update_route_mappings(self):
        """更新路由映射"""
        self.all_routes.update(self.menu_config.get_all_routes())
    
    def add_header_config_item(self, key: str, label: Optional[str] = None, 
                              icon: Optional[str] = None, route: Optional[str] = None, 
                              on_click: Optional[Callable] = None):
        """添加头部配置项"""
        self.header_config_items.append(
            HeaderConfigItem(key=key, label=label, icon=icon, route=route, on_click=on_click)
        )
    
    def set_route_handler(self, route: str, handler: Callable):
        """设置路由处理器"""
        self.route_handlers[route] = handler
    
    def _add_drawer_scrollbar_styles(self):
        """添加抽屉滚动条样式"""
        ui.add_head_html('''
            <style>
            /* 多层布局抽屉滚动条样式 - 参考chat_component的滚动条设置 */
            .multilayer-drawer {
                overflow-y: auto;
                overflow-x: hidden;   /* ✨ 关键修复1: 禁用水平滚动 */
                border-right: 1px solid #e5e7eb;
            }
            
            /* 菜单内容区域滚动条 */
            .multilayer-menu-content {
                overflow-y: auto;
                overflow-x: hidden;  /* ✨ 关键修复2: 禁用水平滚动 */
                max-height: calc(100vh - 100px);
                border-right: 1px solid #e5e7eb;
            }
                         
            /* Webkit浏览器(Chrome, Safari, Edge)滚动条样式 */
            .multilayer-drawer::-webkit-scrollbar,
            .multilayer-menu-content::-webkit-scrollbar {
                width: 1px;
            }
            
            .multilayer-drawer::-webkit-scrollbar-track,
            .multilayer-menu-content::-webkit-scrollbar-track {
                background: transparent;
            }
            
            .multilayer-drawer::-webkit-scrollbar-thumb,
            .multilayer-menu-content::-webkit-scrollbar-thumb {
                background-color: #d1d5db;
                border-radius: 1px;
            }
            
            .multilayer-drawer::-webkit-scrollbar-thumb:hover,
            .multilayer-menu-content::-webkit-scrollbar-thumb:hover {
                background-color: #9ca3af;
            }
            
            /* Firefox滚动条样式 */
            .multilayer-drawer,
            .multilayer-menu-content {
                scrollbar-width: thin;
                scrollbar-color: #d1d5db transparent;
            }
            
            /* 暗色主题滚动条 */
            .dark .multilayer-drawer::-webkit-scrollbar-thumb,
            .dark .multilayer-menu-content::-webkit-scrollbar-thumb {
                background-color: #4b5563;
            }
            
            .dark .multilayer-drawer::-webkit-scrollbar-thumb:hover,
            .dark .multilayer-menu-content::-webkit-scrollbar-thumb:hover {
                background-color: #6b7280;
            }
            
            .dark .multilayer-drawer,
            .dark .multilayer-menu-content {
                scrollbar-color: #4b5563 transparent;
            }
            </style>
        ''')
    
    def create_header(self):
        """创建头部"""
        with ui.header(elevated=True).classes(f'items-center justify-between px-4 {self.config.header_bg}'):
            with ui.row().classes('items-center gap-4'):
                # 菜单按钮
                ui.button(
                    on_click=lambda: self.left_drawer.toggle(),
                    icon='menu'
                ).props('flat color=white').classes('mr-2')
                
                # Logo和标题
                with ui.avatar().classes('cursor-pointer'):
                    ui.image(self.config.app_icon).classes('w-10 h-10')
                
                ui.label(self.config.app_title).classes('text-xl font-bold text-white')
            
            with ui.row().classes('items-center gap-2'):
                # 头部配置项
                for current_item in self.header_config_items:
                    ui.button(
                        icon=current_item.icon,
                        on_click=lambda item=current_item: self.handle_header_config_item_click(item)
                    ).props('flat color=white').classes('mr-2')
                
                if self.header_config_items:
                    # ui.separator().props('vertical').classes('h-8')
                    ui.label("|")
                
                # 主题切换
                self.dark_mode = ui.dark_mode(value=app.storage.user[self._theme_key])
                ui.switch('主题切换') \
                    .bind_value(self.dark_mode) \
                    .on_value_change(lambda e: app.storage.user.update({self._theme_key: e.value})) \
                    .classes('mx-2')
                
                # 设置菜单
                with ui.button(icon='settings').props('flat color=white round').classes('w-10 h-10'):
                    with ui.menu():
                        ui.menu_item('用户管理', lambda: self.handle_settings_menu_item_click('user_management', '用户管理'))
                        ui.menu_item('角色管理', lambda: self.handle_settings_menu_item_click('role_management', '角色管理'))
                        ui.menu_item('权限管理', lambda: self.handle_settings_menu_item_click('permission_management', '权限管理'))
                        ui.separator()
                        ui.menu_item('大模型配置', lambda: self.handle_settings_menu_item_click('llm_config_management', '大模型配置'))
                        ui.menu_item('提示词配置', lambda: self.handle_settings_menu_item_click('prompt_config_management', '提示词配置'))
                
                # 用户菜单
                with ui.button(icon='account_circle').props('flat color=white round').classes('w-10 h-10'):
                    with ui.menu():
                        ui.menu_item('个人资料', lambda: self.handle_user_menu_item_click('user_profile', '个人资料'))
                        ui.menu_item('修改密码', lambda: self.handle_user_menu_item_click('change_password', '修改密码'))
                        ui.separator()
                        ui.menu_item('注销', lambda: self.handle_user_menu_item_click('logout', '注销'))
    
    def create_left_drawer(self):
        """创建左侧抽屉(多层菜单)
        
        ✨ 优化说明:
        1. 将菜单内容区域的 gap 从 gap-1 改为 gap-3,增加菜单项之间的间距
        2. 在 expansion 组件上添加 my-2 类,为展开面板增加垂直外边距
        3. 在叶子节点 row 上添加 my-1 类,为每个菜单项增加轻微的垂直外边距
        4. 调整了整体的 padding,使菜单显示更加舒适
        """
        # 添加自定义滚动条样式
        self._add_drawer_scrollbar_styles()
        
        with ui.left_drawer(fixed=False).props('bordered').classes(
            f'{self.config.drawer_width} {self.config.drawer_bg}'
        ) as left_drawer:
            self.left_drawer = left_drawer
            
            # 菜单标题
            ui.label(self.config.menu_title).classes(
                'w-full text-lg font-semibold text-gray-800 dark:text-gray-200 p-4 '
                'border-b border-gray-200 dark:border-gray-700'
            )
            
            # ✨ 优化点1: 将 gap-1 改为 gap-3,增加菜单项之间的间距
            # ✨ 优化点2: 调整 padding 为 p-3,使整体更舒适
            with ui.column().classes('w-full p-3 gap-2 multilayer-menu-content'):
                if self.menu_config.menu_items:
                    for item in self.menu_config.menu_items:
                        self._render_menu_item(item)
                        
                        if item.separator_after:
                            # ✨ 优化点6: 分隔符使用 -my-1.5,抵消部分 gap-3 的间距
                            # 解释: gap-3(12px) + separator自身 + (-my-1.5 即 -6px) ≈ 合理的分隔间距
                            ui.separator().classes('dark:bg-gray-700 -my-1.5')
                else:
                    # 无菜单项提示
                    with ui.column().classes('w-full items-center py-8'):
                        ui.icon('menu_open').classes('text-6xl text-gray-400 mb-4')
                        ui.label('暂无菜单项').classes('text-lg font-medium text-gray-500 dark:text-gray-400')
    
    def _render_menu_item(self, item: MultilayerMenuItem, level: int = 0):
        """递归渲染菜单项
        
        ✨ 优化说明:
        1. 为 expansion 组件添加 my-2 类,增加垂直外边距
        2. 为叶子节点的 row 添加 my-1 类,增加轻微的垂直外边距
        3. 适当调整 padding,使菜单项内容更加舒适
        """
        indent_class = f'ml-{level * 4}' if level > 0 else ''
        
        if item.is_parent:
            # ✨ 优化点3: 为父节点添加 my-2 类,增加垂直外边距
            # 父节点:使用expansion
            with ui.expansion(
                text=item.label,
                icon=item.icon,
                value=item.expanded or (item.key in self.expanded_keys)
            ).classes(f'w-full {indent_class} my-2').props('dense') as expansion:
                # 保存expansion引用
                self.expansion_refs[item.key] = expansion
                
                # 监听展开/收起事件
                expansion.on_value_change(
                    lambda e, key=item.key: self._handle_expansion_change(key, e.value)
                )
                
                # 递归渲染子节点
                for child in item.children:
                    self._render_menu_item(child, level + 1)
        
        else:
            # ✨ 优化点4: 为叶子节点添加 my-1 类,增加轻微的垂直外边距
            # ✨ 优化点5: 将 padding 从 p-3 调整为 py-3 px-4,使内容更加舒适
            # 叶子节点:可点击的行
            with ui.row().classes(
                f'w-full cursor-pointer rounded-lg hover:bg-blue-100 dark:hover:bg-blue-800 '
                f'transition-colors duration-200 py-3 px-4 items-center {indent_class} my-1'
            ) as leaf_row:
                ui.icon(item.icon).classes('text-blue-600 dark:text-blue-400 mr-3 text-lg')
                ui.label(item.label).classes('text-gray-800 dark:text-gray-200 flex-1')
                
                # 保存叶子节点引用
                self.leaf_refs[item.key] = leaf_row
                
                # 绑定点击事件
                leaf_row.on('click', lambda key=item.key: self.select_leaf_item(key))
    
    def _handle_expansion_change(self, key: str, value: bool):
        """处理展开/收起事件"""
        if value:
            self.expand_parent(key, update_storage=True)
        else:
            self.collapse_parent(key, update_storage=True)
    
    def create_content_area(self):
        """创建内容区域"""
        with ui.column().classes('w-full') as content_container:
            self.content_container = content_container
    
    def navigate_to_route(self, route: str, label: str, update_storage: bool = True):
        """导航到指定路由"""
        # print(f"🚀 导航到路由: {route} ({label})")
        
        self.current_route = route
        self.current_label = label
        
        if update_storage:
            app.storage.user[self._route_key] = route
            app.storage.user[self._label_key] = label
        
        # 清空内容区域
        if self.content_container:
            self.content_container.clear()
        
        # 渲染新内容
        with self.content_container:
            # 查找菜单项以显示面包屑
            menu_item = self.menu_config.find_by_route(route)
            if menu_item:
                self._render_breadcrumb(menu_item)
            
            # 执行路由处理器
            if route in self.route_handlers:
                self.route_handlers[route]()
            else:
                # 默认显示
                with ui.column().classes('w-full items-center justify-center py-16'):
                    ui.icon('info').classes('text-6xl text-blue-500 mb-4')
                    ui.label(f'当前页面: {label}').classes('text-2xl font-bold text-gray-800 dark:text-gray-200')
                    ui.label(f'路由: {route}').classes('text-gray-600 dark:text-gray-400 mt-2')
    
    def _render_breadcrumb(self, item: MultilayerMenuItem):
        """渲染面包屑导航"""
        breadcrumb = []
        current_key = item.key
        
        while current_key:
            current_item = self.menu_config.find_by_key(current_key)
            if current_item:
                breadcrumb.insert(0, current_item.label)
                current_key = current_item.parent_key
            else:
                break
        
        if breadcrumb:
            with ui.row().classes('items-center gap-2 mb-4 text-gray-600 dark:text-gray-400'):
                ui.icon('home').classes('text-lg')
                for i, label in enumerate(breadcrumb):
                    if i > 0:
                        ui.icon('chevron_right').classes('text-sm')
                    ui.label(label).classes('text-sm')
    
    def select_leaf_item(self, key: str, update_storage: bool = True):
        """选中叶子节点"""
        item = self.menu_config.find_by_key(key)
        if not item or not item.is_leaf:
            log_warning(f"⚠️ 节点 {key} 不是有效的叶子节点")
            return        
        # 清除之前的选中状态
        if self.selected_leaf_key and self.selected_leaf_key in self.leaf_refs:
            old_row = self.leaf_refs[self.selected_leaf_key]
            old_row.classes(remove='bg-blue-200 dark:bg-blue-700')
        # 设置新的选中状态
        if key in self.leaf_refs:
            new_row = self.leaf_refs[key]
            new_row.classes(add='bg-blue-200 dark:bg-blue-700')
        
        self.selected_leaf_key = key
        
        # 确保父节点展开
        parent_chain = self.menu_config.get_parent_chain_keys(key)
        for parent_key in parent_chain:
            if parent_key not in self.expanded_keys:
                self.expand_parent(parent_key, update_storage=False)
        
        # 导航到对应路由
        if item.route:
            self.navigate_to_route(item.route, item.label, update_storage=update_storage)
    
    def expand_parent(self, key: str, update_storage: bool = True):
        """展开父节点"""
        if key in self.expanded_keys:
            return
        self.expanded_keys.add(key)
        if key in self.expansion_refs:
            expansion = self.expansion_refs[key]
            expansion.open()
        if update_storage:
            self._save_expanded_state()
    
    def collapse_parent(self, key: str, update_storage: bool = True):
        """收起父节点"""
        if key not in self.expanded_keys:
            return
        self.expanded_keys.remove(key)
        if key in self.expansion_refs:
            expansion = self.expansion_refs[key]
            expansion.close()
        if update_storage:
            self._save_expanded_state()
            
    def _save_expanded_state(self):
        """保存展开状态到存储"""
        app.storage.user[self._expanded_keys_key] = list(self.expanded_keys)
    
    def _load_expanded_state(self):
        """从存储加载展开状态"""
        stored_keys = app.storage.user.get(self._expanded_keys_key, [])
        self.expanded_keys = set(stored_keys)
    
    def handle_header_config_item_click(self, item: HeaderConfigItem):
        """处理头部配置项点击"""
        if item.on_click:
            item.on_click()
        elif item.route:
            self.navigate_to_route(item.route, item.label or item.key)
    
    def handle_settings_menu_item_click(self, route: str, label: str):
        """处理设置菜单项点击"""
        self.navigate_to_route(route, label)
    
    def handle_user_menu_item_click(self, route: str, label: str):
        """处理用户菜单项点击"""
        if route == 'logout':
            logger.debug("🚪 执行用户注销，清除路由存储")
            self.clear_route_storage()
        self.navigate_to_route(route, label)
    
    def clear_route_storage(self):
        """清除路由存储"""
        if self._route_key in app.storage.user:
            del app.storage.user[self._route_key]
        if self._label_key in app.storage.user:
            del app.storage.user[self._label_key]
        if self._expanded_keys_key in app.storage.user:
            del app.storage.user[self._expanded_keys_key]
    
    def restore_route_from_storage(self):
        """从存储恢复路由"""
        stored_route = app.storage.user.get(self._route_key)
        stored_label = app.storage.user.get(self._label_key)
        
        # 加载展开状态
        self._load_expanded_state()
        
        if stored_route and stored_route in self.all_routes:            
            # 查找对应的菜单项
            menu_item = self.menu_config.find_by_route(stored_route)
            if menu_item and menu_item.is_leaf:
                self.select_leaf_item(menu_item.key, update_storage=False)
            else:
                self.navigate_to_route(stored_route, stored_label, update_storage=False)
        else:
            # 默认路由
            if self.menu_config.menu_items:
                first_leaf = self.menu_config.get_first_leaf()
                if first_leaf:
                    self.select_leaf_item(first_leaf.key)
    
    def register_system_routes(self):
        """注册系统路由"""
        system_routes = {
            # 设置菜单路由
            'user_management': '用户管理',
            'role_management': '角色管理', 
            'permission_management': '权限管理',
            # ✅ 新增: 配置管理路由
            'llm_config_management': '大模型配置',
            'prompt_config_management': '提示词配置',  # ✅ 新增
            # 用户菜单路由（排除logout）
            'user_profile': '个人资料',
            'change_password': '修改密码',
            # 其他系统路由
            'no_permission': '权限不足',
            'login': '登录',
            'register': '注册'
        }
        
        for route, label in system_routes.items():
            if route not in self.all_routes:
                self.all_routes[route] = label
        # logger.debug(f"🔧 已注册系统路由: {list(system_routes.keys())}")
        # logger.debug(f"🔧 注册的全部路由：{self.all_routes}")
        # logger.debug(f"⚠️ 注意：logout 路由未注册到持久化路由中（一次性操作）")
    
    def initialize_layout(self):
        """初始化布局"""
        def init_routes():
            self.register_system_routes()
            self.restore_route_from_storage()
        
        ui.timer(0.3, init_routes, once=True)
```

- **webproduct_ui_template\component\multilayer_menu_config.py**
```python
"""
多层菜单配置模块
定义多层级菜单的数据结构和配置类
"""
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field

@dataclass
class MultilayerMenuItem:
    """多层菜单项数据类"""
    key: str                                    # 唯一标识符
    label: str                                  # 显示标签
    icon: str = 'folder'                        # 图标名称(Material Icons)
    route: Optional[str] = None                 # 路由标识(叶子节点必须有)
    children: List['MultilayerMenuItem'] = field(default_factory=list)  # 子菜单列表
    expanded: bool = False                      # 默认是否展开
    separator_after: bool = False               # 之后是否显示分隔线
    custom_icon_path: Optional[str] = None      # 自定义图标路径
    parent_key: Optional[str] = None            # 父节点key(自动设置)
    level: int = 0                              # 层级深度(自动计算)
    
    def __post_init__(self):
        """初始化后自动设置子节点的父节点引用和层级"""
        self._update_children_metadata()
    
    def _update_children_metadata(self):
        """更新子节点的元数据(父节点key和层级)"""
        for child in self.children:
            child.parent_key = self.key
            child.level = self.level + 1
            child._update_children_metadata()
    
    @property
    def is_parent(self) -> bool:
        """是否是父节点(有子节点)"""
        return len(self.children) > 0
    
    @property
    def is_leaf(self) -> bool:
        """是否是叶子节点(有路由且无子节点)"""
        return self.route is not None and len(self.children) == 0
    
    @property
    def is_root(self) -> bool:
        """是否是根节点(没有父节点)"""
        return self.parent_key is None
    
    def add_child(self, child: 'MultilayerMenuItem') -> 'MultilayerMenuItem':
        """添加子节点"""
        child.parent_key = self.key
        child.level = self.level + 1
        self.children.append(child)
        child._update_children_metadata()
        return self
    
    def find_by_key(self, key: str) -> Optional['MultilayerMenuItem']:
        """递归查找指定key的节点"""
        if self.key == key:
            return self
        
        for child in self.children:
            result = child.find_by_key(key)
            if result:
                return result
        
        return None
    
    def find_by_route(self, route: str) -> Optional['MultilayerMenuItem']:
        """递归查找指定路由的叶子节点"""
        if self.route == route:
            return self
        
        for child in self.children:
            result = child.find_by_route(route)
            if result:
                return result
        
        return None
    
    def get_parent_chain(self) -> List[str]:
        """获取从根节点到当前节点的父节点key链"""
        chain = []
        current = self
        while current.parent_key:
            chain.insert(0, current.parent_key)
            # 需要从根节点查找父节点
            current = None  # 简化处理,实际使用中由manager维护
            break
        return chain
    
    def get_all_routes(self) -> List[str]:
        """递归获取所有叶子节点的路由"""
        routes = []
        if self.is_leaf:
            routes.append(self.route)
        
        for child in self.children:
            routes.extend(child.get_all_routes())
        
        return routes
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式(用于调试和序列化)"""
        return {
            'key': self.key,
            'label': self.label,
            'icon': self.icon,
            'route': self.route,
            'expanded': self.expanded,
            'level': self.level,
            'is_parent': self.is_parent,
            'is_leaf': self.is_leaf,
            'children': [child.to_dict() for child in self.children]
        }

class MultilayerMenuConfig:
    """多层菜单配置管理类"""
    
    def __init__(self):
        self.menu_items: List[MultilayerMenuItem] = []
        self._route_map: Dict[str, MultilayerMenuItem] = {}  # 路由->节点映射
        self._key_map: Dict[str, MultilayerMenuItem] = {}    # key->节点映射
    
    def add_menu_item(self, item: MultilayerMenuItem):
        """添加顶层菜单项"""
        self.menu_items.append(item)
        self._rebuild_maps()
    
    def _rebuild_maps(self):
        """重建路由和key映射表"""
        self._route_map.clear()
        self._key_map.clear()
        
        for item in self.menu_items:
            self._build_maps_recursive(item)
    
    def _build_maps_recursive(self, item: MultilayerMenuItem):
        """递归构建映射表"""
        # 添加 key映射
        self._key_map[item.key] = item
        
        # 添加路由映射(只针对叶子节点)
        if item.is_leaf:
            self._route_map[item.route] = item
        
        # 递归处理子节点
        for child in item.children:
            self._build_maps_recursive(child)
    
    def find_by_route(self, route: str) -> Optional[MultilayerMenuItem]:
        """通过路由查找节点"""
        return self._route_map.get(route)
    
    def find_by_key(self, key: str) -> Optional[MultilayerMenuItem]:
        """通过key查找节点"""
        return self._key_map.get(key)
    
    def get_parent_chain_keys(self, key: str) -> List[str]:
        """获取指定节点的所有父节点key链"""
        item = self.find_by_key(key)
        if not item:
            return []
        
        chain = []
        current_key = item.parent_key
        
        while current_key:
            chain.insert(0, current_key)
            parent_item = self.find_by_key(current_key)
            if parent_item:
                current_key = parent_item.parent_key
            else:
                break
        
        return chain
    
    def get_all_routes(self) -> Dict[str, str]:
        """获取所有路由映射 {route: label}"""
        routes = {}
        for route, item in self._route_map.items():
            routes[route] = item.label
        return routes
    
    # ✨ 新增方法: 获取第一个叶子节点
    def get_first_leaf(self) -> Optional[MultilayerMenuItem]:
        """
        递归查找并返回第一个叶子节点
        
        Returns:
            第一个叶子节点,如果没有则返回 None
        """
        for item in self.menu_items:
            result = self._find_first_leaf_recursive(item)
            if result:
                return result
        return None
    
    def _find_first_leaf_recursive(self, item: MultilayerMenuItem) -> Optional[MultilayerMenuItem]:
        """
        递归辅助方法:在给定节点的子树中查找第一个叶子节点
        
        Args:
            item: 当前检查的节点
            
        Returns:
            第一个找到的叶子节点,如果没有则返回 None
        """
        # 如果当前节点是叶子节点,直接返回
        if item.is_leaf:
            return item
        
        # 否则递归查找子节点中的第一个叶子节点
        for child in item.children:
            result = self._find_first_leaf_recursive(child)
            if result:
                return result
        
        return None
    
    def validate(self) -> List[str]:
        """验证配置的有效性,返回错误信息列表"""
        errors = []
        
        # 检查key唯一性
        keys = set()
        for item in self.menu_items:
            self._validate_keys_recursive(item, keys, errors)
        
        # 检查叶子节点必须有路由
        for key, item in self._key_map.items():
            if item.is_leaf and not item.route:
                errors.append(f"叶子节点 '{item.label}' (key={key}) 缺少路由配置")
        
        return errors
    
    def _validate_keys_recursive(self, item: MultilayerMenuItem, keys: set, errors: List[str]):
        """递归验证key唯一性"""
        if item.key in keys:
            errors.append(f"重复的key: {item.key}")
        keys.add(item.key)
        
        for child in item.children:
            self._validate_keys_recursive(child, keys, errors)

# 辅助函数:快速创建菜单项
def create_menu_item(key: str, 
                     label: str, 
                     icon: str = 'folder',
                     route: Optional[str] = None,
                     children: Optional[List[MultilayerMenuItem]] = None,
                     **kwargs) -> MultilayerMenuItem:
    """快速创建菜单项的辅助函数"""
    return MultilayerMenuItem(
        key=key,
        label=label,
        icon=icon,
        route=route,
        children=children or [],
        **kwargs
    )


# 示例配置
def create_demo_menu_config() -> MultilayerMenuConfig:
    """创建演示用的菜单配置"""
    config = MultilayerMenuConfig()
    
    # 企业档案管理
    enterprise_menu = MultilayerMenuItem(
        key='enterprise',
        label='企业档案管理',
        icon='business',
        expanded=True,
        children=[
            MultilayerMenuItem(
                key='chat',
                label='AI对话',
                icon='chat',
                route='chat_page'
            ),
            MultilayerMenuItem(
                key='doc',
                label='文档管理',
                icon='description',
                route='doc_page'
            ),
        ]
    )
    
    # 系统管理
    system_menu = MultilayerMenuItem(
        key='system',
        label='系统管理',
        icon='admin_panel_settings',
        children=[
            MultilayerMenuItem(
                key='users',
                label='用户管理',
                icon='group',
                route='user_management'
            ),
            MultilayerMenuItem(
                key='roles',
                label='角色管理',
                icon='badge',
                route='role_management'
            ),
        ]
    )
    
    config.add_menu_item(enterprise_menu)
    config.add_menu_item(system_menu)
    
    return config

if __name__ == '__main__':
    # 测试代码
    print("🧪 测试多层菜单配置模块\n")
    
    config = create_demo_menu_config()
    
    print("✅ 菜单结构:")
    for item in config.menu_items:
        print(f"\n📁 {item.label} (key={item.key})")
        for child in item.children:
            print(f"  ├─ {child.label} (key={child.key}, route={child.route})")
    
    print("\n✅ 所有路由映射:")
    for route, label in config.get_all_routes().items():
        print(f"  {route} -> {label}")
    
    print("\n✅ 查找测试:")
    chat_item = config.find_by_route('chat_page')
    if chat_item:
        print(f"  找到路由 'chat_page': {chat_item.label}")
        parent_chain = config.get_parent_chain_keys(chat_item.key)
        print(f"  父节点链: {parent_chain}")
    
    print("\n✅ 验证配置:")
    errors = config.validate()
    if errors:
        print(f"  ❌ 发现 {len(errors)} 个错误:")
        for error in errors:
            print(f"    - {error}")
    else:
        print("  ✅ 配置验证通过!")
```

- **webproduct_ui_template\component\multilayer_spa_layout.py**
```python
"""
多层SPA布局装饰器和工具函数
提供类似spa_layout和simple_spa_layout的接口,但使用多层折叠菜单
"""
from nicegui import ui
from functools import wraps
from typing import List, Dict, Callable, Optional, Any
from .layout_config import LayoutConfig
from .multilayer_layout_manager import MultilayerLayoutManager
from .multilayer_menu_config import MultilayerMenuItem

# 全局布局管理器实例
current_multilayer_layout_manager: Optional[MultilayerLayoutManager] = None

def with_multilayer_spa_layout(
    config: Optional[LayoutConfig] = None,
    menu_items: Optional[List[MultilayerMenuItem]] = None,
    header_config_items: Optional[List[Dict[str, Any]]] = None,
    route_handlers: Optional[Dict[str, Callable]] = None
):
    """
    多层SPA布局装饰器
    
    使用方式:
    @with_multilayer_spa_layout(
        config=config,
        menu_items=[...],
        header_config_items=[...],
        route_handlers={...}
    )
    def main_page():
        pass
    
    Args:
        config: 布局配置对象
        menu_items: MultilayerMenuItem列表(多层菜单项)
        header_config_items: 头部配置项列表
        route_handlers: 路由处理器字典 {route: handler}
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            global current_multilayer_layout_manager
            
            # 创建布局配置
            layout_config = config or LayoutConfig()
            layout_manager = MultilayerLayoutManager(layout_config)
            current_multilayer_layout_manager = layout_manager
            
            # 添加菜单项
            if menu_items is not None:
                for item in menu_items:
                    layout_manager.add_menu_item(item)
            
            # 添加头部配置项
            if header_config_items is not None:
                for item in header_config_items:
                    layout_manager.add_header_config_item(
                        item['key'],
                        item.get('label'),
                        item.get('icon'),
                        item.get('route'),
                        item.get('on_click')
                    )
            
            # 设置路由处理器
            if route_handlers:
                for route, handler in route_handlers.items():
                    layout_manager.set_route_handler(route, handler)
            
            # 创建布局
            layout_manager.create_header()
            layout_manager.create_left_drawer()
            layout_manager.create_content_area()
            
            # 初始化路由
            layout_manager.initialize_layout()
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator

def create_multilayer_spa_layout(
    config: Optional[LayoutConfig] = None,
    menu_items: Optional[List[MultilayerMenuItem]] = None,
    header_config_items: Optional[List[Dict[str, Any]]] = None,
    route_handlers: Optional[Dict[str, Callable]] = None
) -> MultilayerLayoutManager:
    """
    创建多层SPA布局(函数式API)
    
    使用方式:
    layout_manager = create_multilayer_spa_layout(
        config=config,
        menu_items=[...],
        header_config_items=[...],
        route_handlers={...}
    )
    
    Returns:
        MultilayerLayoutManager实例
    """
    global current_multilayer_layout_manager
    
    # 创建布局配置
    layout_config = config or LayoutConfig()
    layout_manager = MultilayerLayoutManager(layout_config)
    current_multilayer_layout_manager = layout_manager
    
    # 添加菜单项
    if menu_items is not None:
        for item in menu_items:
            layout_manager.add_menu_item(item)
    
    # 添加头部配置项
    if header_config_items is not None:
        for item in header_config_items:
            layout_manager.add_header_config_item(
                item['key'],
                item.get('label'),
                item.get('icon'),
                item.get('route'),
                item.get('on_click')
            )
    
    # 设置路由处理器
    if route_handlers:
        for route, handler in route_handlers.items():
            layout_manager.set_route_handler(route, handler)
    
    # 创建布局
    layout_manager.create_header()
    layout_manager.create_left_drawer()
    layout_manager.create_content_area()
    
    # 初始化路由
    layout_manager.initialize_layout()
    
    return layout_manager


def get_multilayer_layout_manager() -> MultilayerLayoutManager:
    """
    获取当前多层布局管理器实例
    
    Returns:
        MultilayerLayoutManager实例
        
    Raises:
        RuntimeError: 如果布局管理器未初始化
    """
    global current_multilayer_layout_manager
    
    if current_multilayer_layout_manager is None:
        raise RuntimeError(
            "多层布局管理器未初始化,请确保使用了 @with_multilayer_spa_layout 装饰器"
            "或调用了 create_multilayer_spa_layout() 函数"
        )
    
    return current_multilayer_layout_manager


def register_multilayer_route_handler(route: str, handler: Callable):
    """
    注册多层布局的路由处理器
    
    Args:
        route: 路由标识
        handler: 路由处理函数
    """
    layout_manager = get_multilayer_layout_manager()
    layout_manager.set_route_handler(route, handler)


def multilayer_navigate_to(route: str, label: Optional[str] = None):
    """
    多层布局的导航函数
    
    Args:
        route: 目标路由
        label: 路由标签(可选,如果不提供会自动查找)
    """
    layout_manager = get_multilayer_layout_manager()
    
    # 如果没有提供label,尝试查找
    if label is None:
        # 首先在菜单中查找
        menu_item = layout_manager.menu_config.find_by_route(route)
        if menu_item:
            label = menu_item.label
        else:
            # 在头部配置项中查找
            header_item = next(
                (item for item in layout_manager.header_config_items if item.route == route),
                None
            )
            if header_item:
                label = header_item.label or header_item.key
            else:
                # 如果都没找到,使用路由名作为标签
                label = route.replace('_', ' ').title()
    
    # 导航并保存状态
    layout_manager.navigate_to_route(route, label, update_storage=True)
    
    # 如果是菜单项,同步更新选中状态
    menu_item = layout_manager.menu_config.find_by_route(route)
    if menu_item and menu_item.is_leaf:
        layout_manager.select_leaf_item(menu_item.key, update_storage=False)


def multilayer_expand_parent(parent_key: str):
    """
    展开指定的父节点
    
    Args:
        parent_key: 父节点的key
    """
    layout_manager = get_multilayer_layout_manager()
    layout_manager.expand_parent(parent_key, update_storage=True)


def multilayer_collapse_parent(parent_key: str):
    """
    收起指定的父节点
    
    Args:
        parent_key: 父节点的key
    """
    layout_manager = get_multilayer_layout_manager()
    layout_manager.collapse_parent(parent_key, update_storage=True)


def multilayer_select_leaf(leaf_key: str):
    """
    选中指定的叶子节点
    
    Args:
        leaf_key: 叶子节点的key
    """
    layout_manager = get_multilayer_layout_manager()
    layout_manager.select_leaf_item(leaf_key, update_storage=True)


def multilayer_clear_route_storage():
    """清除多层布局的路由存储(用于注销等场景)"""
    layout_manager = get_multilayer_layout_manager()
    layout_manager.clear_route_storage()


# 导出所有公共API
__all__ = [
    # 装饰器和创建函数
    'with_multilayer_spa_layout',
    'create_multilayer_spa_layout',
    
    # 获取管理器
    'get_multilayer_layout_manager',
    
    # 路由操作
    'register_multilayer_route_handler',
    'multilayer_navigate_to',
    
    # 菜单操作
    'multilayer_expand_parent',
    'multilayer_collapse_parent',
    'multilayer_select_leaf',
    
    # 状态管理
    'multilayer_clear_route_storage',
]


# 使用示例
if __name__ == '__main__':
    """
    示例代码展示如何使用多层布局
    """
    print("=" * 60)
    print("多层SPA布局使用示例")
    print("=" * 60)
    
    example_code = '''
    # 1. 导入必要的模块
    from component import (
        with_multilayer_spa_layout, 
        LayoutConfig,
        MultilayerMenuItem
    )

    # 2. 创建多层菜单结构
    menu_items = [
        MultilayerMenuItem(
            key='enterprise',
            label='企业档案管理',
            icon='business',
            expanded=True,
            children=[
                MultilayerMenuItem(
                    key='chat',
                    label='AI对话',
                    icon='chat',
                    route='chat_page'
                ),
                MultilayerMenuItem(
                    key='doc',
                    label='文档管理',
                    icon='description',
                    route='doc_page'
                ),
            ]
        ),
        MultilayerMenuItem(
            key='personal',
            label='个人档案管理',
            icon='people',
            children=[
                MultilayerMenuItem(
                    key='profile',
                    label='个人资料',
                    icon='person',
                    route='profile_page'
                ),
            ]
        ),
    ]

    # 3. 定义路由处理器
    def chat_page_handler():
        ui.label('AI对话页面').classes('text-2xl font-bold')
        ui.label('这是一个聊天界面...')

    def doc_page_handler():
        ui.label('文档管理页面').classes('text-2xl font-bold')
        ui.label('这里可以管理各种文档...')

    route_handlers = {
        'chat_page': chat_page_handler,
        'doc_page': doc_page_handler,
        'profile_page': lambda: ui.label('个人资料页面'),
    }

    # 4. 使用装饰器创建布局
    @ui.page('/workbench')
    def main_page():
        @with_multilayer_spa_layout(
            config=LayoutConfig(),
            menu_items=menu_items,
            header_config_items=[
                {'key': 'search', 'icon': 'search', 'route': 'search'},
                {'key': 'messages', 'icon': 'mail', 'route': 'messages'},
            ],
            route_handlers=route_handlers
        )
        def spa_content():
            pass
        
        return spa_content()

    # 5. 在页面中使用导航函数
    from component import multilayer_navigate_to

    def some_button_handler():
        multilayer_navigate_to('chat_page')  # 导航到AI对话页面
    '''
    
    print(example_code)
    print("=" * 60)
    print("✅ 更多示例请参考 multilayer_main.py")
    print("=" * 60)
```

- **webproduct_ui_template\component\simple_layout_manager.py**
```python
from nicegui import ui, app
from typing import List, Dict, Callable, Optional
from .layout_config import LayoutConfig, MenuItem, HeaderConfigItem
from common.log_handler import (
    log_info, 
    log_error, 
    log_warning,
    log_debug,
    log_success,
    log_trace,
    get_logger
)
logger = get_logger(__file__)

class SimpleLayoutManager:
    """简单布局管理器 - 只包含顶部导航栏的布局"""
    
    def __init__(self, config: LayoutConfig):
        self.config = config
        self.nav_items: List[MenuItem] = []  # 顶部导航项
        self.header_config_items: List[HeaderConfigItem] = []
        self.selected_nav_item = {'key': None}  # 当前选中的导航项
        self.content_container = None
        self.dark_mode = None
        self.route_handlers: Dict[str, Callable] = {}
        self.current_route = None
        self.nav_buttons: Dict[str, any] = {}  # 导航按钮引用
        # 主题切换
        self._theme_key = 'theme' 
        initial_theme = app.storage.user.get(self._theme_key, False)
        app.storage.user[self._theme_key] = initial_theme   # 确保键存在
        # 路由映射
        self.all_routes: Dict[str, str] = {}  # route -> label 的映射

    def add_nav_item(self, key: str, label: str, icon: str, route: Optional[str] = None):
        """添加顶部导航项"""
        self.nav_items.append(MenuItem(key, label, icon, route, False))
        # 注册路由映射
        if route:
            self.all_routes[route] = label

    def add_header_config_item(self, key: str, label: Optional[str] = None, icon: Optional[str] = None, route: Optional[str] = None, on_click: Optional[Callable] = None):
        """添加头部配置项"""
        self.header_config_items.append(HeaderConfigItem(key, label, icon, route, on_click))
        # 注册路由映射
        if route:
            self.all_routes[route] = label or key

    def set_route_handler(self, route: str, handler: Callable):
        """设置路由处理器"""
        self.route_handlers[route] = handler
        
        # 如果路由映射中没有这个路由，添加一个默认标签
        if route not in self.all_routes:
            self.all_routes[route] = route.replace('_', ' ').title()

    def register_system_routes(self):
        """注册系统路由（设置菜单、用户菜单等）"""
        system_routes = {
            # 设置菜单路由
            'user_management': '用户管理',
            'role_management': '角色管理', 
            'permission_management': '权限管理',
            # ✅ 新增: 配置管理路由
            'llm_config_management': '大模型配置',
            'prompt_config_management': '提示词配置',  # ✅ 新增

            # 用户菜单路由（排除logout）
            'user_profile': '个人资料',
            'change_password': '修改密码',
            
            # 其他系统路由
            'no_permission': '权限不足',
            'login': '登录',
            'register': '注册'
        }
        
        for route, label in system_routes.items():
            self.all_routes[route] = label
            
        # logger.debug(f"🔧 已注册系统路由: {list(system_routes.keys())}")
        # logger.debug(f"🔧 注册的全部路由：{self.all_routes}")
        # logger.debug(f"⚠️  注意：logout 路由未注册到持久化路由中（一次性操作）")

    def select_nav_item(self, key: str, button_element=None, update_storage: bool = True):
        """选择导航项"""
        if self.selected_nav_item['key'] == key:
            return

        # 清除之前的选中状态
        for btn_key, btn in self.nav_buttons.items():
            if btn_key == key:
                btn.props('color=primary')  # 选中状态
            else:
                btn.props('color=white')  # 未选中状态
        
        self.selected_nav_item['key'] = key

        nav_item = next((item for item in self.nav_items if item.key == key), None)
        if not nav_item:
            return

        ui.notify(f'切换到{nav_item.label}')

        if nav_item.route:
            self.navigate_to_route(nav_item.route, nav_item.label, update_storage)
        else:
            if self.content_container:
                self.content_container.clear()
                with self.content_container:
                    ui.label(f'{nav_item.label}内容').classes('text-2xl font-bold text-gray-800 dark:text-gray-200')

    def clear_nav_selection(self):
        """清除导航选中状态（用于非导航路由）"""
        for btn in self.nav_buttons.values():
            btn.props('color=white')
        self.selected_nav_item['key'] = None

    def navigate_to_route(self, route: str, label: str, update_storage: bool = True):
        """导航到指定路由"""
        if self.current_route == route:
            return
        
        self.current_route = route
        
        # 如果不是导航路由，清除导航选中状态
        is_nav_route = any(item.route == route for item in self.nav_items)
        if not is_nav_route:
            self.clear_nav_selection()
        
        # 保存当前路由到存储（排除一次性操作路由）
        if update_storage and self._should_persist_route(route):
            try:
                app.storage.user['current_route'] = route
            except Exception as e:
                logger.error(f"⚠️ 保存路由状态失败: {e}")
        elif not self._should_persist_route(route):
            logger.debug(f"🚫 跳过路由持久化: {route} (一次性操作)")
        
        if self.content_container:
            self.content_container.clear()

        if route in self.route_handlers:
            with self.content_container:
                try:
                    self.route_handlers[route]()
                except Exception as e:
                    logger.error(f"❌ 路由处理器执行失败 {route}: {e}")
                    ui.label(f'页面加载失败: {str(e)}').classes('text-red-500 text-xl')
        else:
            logger.error(f"❌ 未找到路由处理器: {route}")
            with self.content_container:
                ui.label(f'页面未找到: {label}').classes('text-2xl font-bold text-red-600')
                ui.label(f'路由 "{route}" 没有对应的处理器').classes('text-gray-600 dark:text-gray-400 mt-4')

    def _should_persist_route(self, route: str) -> bool:
        """判断路由是否应该持久化"""
        # 一次性操作路由，不应该被持久化
        non_persistent_routes = {
            'logout',      # 注销操作
            'login',       # 登录页面
            'register',    # 注册页面
        }
        return route not in non_persistent_routes

    def clear_route_storage(self):
        """清除路由存储（用于注销等场景）"""
        try:
            if 'current_route' in app.storage.user:
                del app.storage.user['current_route']
                logger.debug("🗑️ 已清除路由存储")
        except Exception as e:
            logger.warning(f"⚠️ 清除路由存储失败: {e}")

    def restore_route_from_storage(self):
        """从存储恢复路由状态"""
        try:
            # 从存储获取保存的路由
            saved_route = app.storage.user.get('current_route')
            
            # 如果没有保存的路由
            if not saved_route:
                # 如果有导航项，选择第一个
                if self.nav_items:
                    first_item = self.nav_items[0]
                    self.select_nav_item(first_item.key, update_storage=True)
                else:
                    # 如果没有导航项，不做任何操作
                    logger.warning("🔄 没有保存的路由，且未定义导航项，保持空白状态")
                return
            
            logger.debug(f"🔄 恢复保存的路由: {saved_route}")
            
            # 检查路由是否在已知路由中
            if saved_route in self.all_routes:
                route_label = self.all_routes[saved_route]
                logger.debug(f"✅ 找到路由映射: {saved_route} -> {route_label}")
                
                # 检查是否是导航项路由
                nav_item = next((item for item in self.nav_items if item.route == saved_route), None)
                if nav_item:
                    # 恢复导航选中状态
                    self.select_nav_item(nav_item.key, update_storage=False)
                else:
                    logger.debug(f"✅ 这是非导航路由，直接导航")
                    # 直接导航到路由（不更新存储避免循环）
                    self.navigate_to_route(saved_route, route_label, update_storage=False)
                return
            
            # 兜底检查：是否在路由处理器中注册
            if saved_route in self.route_handlers:
                logger.debug(f"✅ 在路由处理器中找到路由: {saved_route}")
                label = saved_route.replace('_', ' ').title()
                self.navigate_to_route(saved_route, label, update_storage=False)
                return
            
            # 如果都没找到，且有导航项，选择第一个导航项
            logger.debug(f"⚠️ 未找到保存的路由 {saved_route}，使用默认路由")
            if self.nav_items:
                first_item = self.nav_items[0]
                self.select_nav_item(first_item.key, update_storage=True)
            else:
                logger.debug("⚠️ 没有可用的导航项，保持空白状态")
                
        except Exception as e:
            logger.debug(f"⚠️ 恢复路由状态失败: {e}")
            if self.nav_items:
                first_item = self.nav_items[0]
                self.select_nav_item(first_item.key, update_storage=True)
            else:
                logger.debug("⚠️ 没有可用的导航项，保持空白状态")

    def handle_header_config_item_click(self, item: HeaderConfigItem):
        """处理头部配置项点击事件"""
        ui.notify(f'点击了头部配置项: {item.label or item.key}')
        
        if item.on_click:
            item.on_click()
        
        if item.route:
            self.navigate_to_route(item.route, item.label or item.key)

    def handle_settings_menu_item_click(self, route: str, label: str):
        """处理设置菜单项点击事件"""        
        from auth.auth_manager import auth_manager

        if not auth_manager.is_authenticated():
            ui.notify('请先登录', type='warning')
            self.navigate_to_route('login', '登录')
            return

        if not auth_manager.has_role('admin') and not auth_manager.current_user.is_superuser:
            ui.notify('您没有管理员权限，无法访问此功能', type='error')
            self.navigate_to_route('no_permission', '权限不足')
            return

        ui.notify(f'访问管理功能: {label}')
        self.navigate_to_route(route, label)

    def handle_user_menu_item_click(self, route: str, label: str):
        """处理用户菜单项点击事件"""
        ui.notify(f'点击了用户菜单项: {label}')
        
        # 特殊处理注销：清除路由存储
        if route == 'logout':
            logger.debug("🚪 执行用户注销，清除路由存储")
            self.clear_route_storage()
        
        self.navigate_to_route(route, label)

    def create_header(self):
        """创建头部导航栏"""
        with ui.header(elevated=True).classes(f'items-center justify-between px-2 {self.config.header_bg}'):
            # 左侧：Logo
            with ui.row().classes('items-center gap-2'):
                # Logo区域
                with ui.avatar():
                    ui.image(self.config.app_icon).classes('w-12 h-12')
                ui.label(self.config.app_title).classes('text-xl font-medium text-white dark:text-white')

            # 右侧区域：主导航项 + 头部配置项 + 主题切换 + 设置菜单 + 用户菜单
            # 将所有这些元素放在一个单独的 ui.row 中，它们会作为一个整体靠右对齐
            with ui.row().classes('items-center gap-2'): # 使用 gap-2 可以在内部元素之间增加一些间距
                # ui.separator().props('vertical').classes('h-8 mx-4') # 如果希望主导航项和logo之间有分隔符，可以保留，但根据图片，可能不需要
                # 主导航项
                for nav_item in self.nav_items:
                    nav_btn = ui.button(
                        nav_item.label, 
                        icon=nav_item.icon,
                        on_click=lambda key=nav_item.key: self.select_nav_item(key)
                    ).props('flat color=white').classes('mx-1')
                    # 保存按钮引用用于状态控制
                    self.nav_buttons[nav_item.key] = nav_btn
                
                # 主导航项和右侧配置项之间的分隔符 (根据图片，这里可能需要一个分隔符)
                if self.nav_items and (self.header_config_items or self.dark_mode or True): # 假设后面的元素总是存在
                    # ui.separator().props('vertical').classes('h-8 mx-4') # 在主导航项和右侧功能区之间添加分隔符
                    ui.label("|")

                # 头部配置项
                for item in self.header_config_items:
                    if item.icon and item.label:
                        ui.button(item.label, icon=item.icon, on_click=lambda current_item=item: self.handle_header_config_item_click(current_item)).props('flat color=white').classes('mr-2')
                    elif item.icon:
                        ui.button(icon=item.icon, on_click=lambda current_item=item: self.handle_header_config_item_click(current_item)).props('flat color=white round').classes('w-10 h-10')
                    elif item.label:
                        ui.button(item.label, on_click=lambda current_item=item: self.handle_header_config_item_click(current_item)).props('flat color=white').classes('mr-2')

                # 主题切换
                # ui.switch('主题切换').bind_value(self.dark_mode).classes('mx-2')
                self.dark_mode = ui.dark_mode(value=app.storage.user[self._theme_key])
                ui.switch('主题切换') \
                    .bind_value(self.dark_mode) \
                    .on_value_change(lambda e: app.storage.user.update({self._theme_key: e.value})) \
                    .classes('mx-2')

                # 设置菜单
                with ui.button(icon='settings').props('flat color=white round').classes('w-10 h-10'):
                    with ui.menu() as settings_menu:
                        ui.menu_item('用户管理', lambda: self.handle_settings_menu_item_click('user_management', '用户管理'))
                        ui.menu_item('角色管理', lambda: self.handle_settings_menu_item_click('role_management', '角色管理'))
                        ui.menu_item('权限管理', lambda: self.handle_settings_menu_item_click('permission_management', '权限管理'))
                        # ✅ 新增: 配置管理菜单项
                        ui.separator()  # 分隔线
                        ui.menu_item('大模型配置', lambda: self.handle_settings_menu_item_click('llm_config_management', '大模型配置'))
                        ui.menu_item('提示词配置', lambda: self.handle_settings_menu_item_click('prompt_config_management', '提示词配置'))  # ✅ 新增

                # 用户菜单
                with ui.button(icon='account_circle').props('flat color=white round').classes('w-10 h-10'):
                    with ui.menu() as user_menu:
                        ui.menu_item('个人资料', lambda: self.handle_user_menu_item_click('user_profile', '个人资料'))
                        ui.menu_item('修改密码', lambda: self.handle_user_menu_item_click('change_password', '修改密码'))
                        ui.separator()
                        ui.menu_item('注销', lambda: self.handle_user_menu_item_click('logout', '注销'))

    def create_content_area(self):
        """创建内容区域"""
        with ui.column().classes('flex-1 w-full') as content_container:
            self.content_container = content_container

    def initialize_layout(self):
        """初始化布局（延迟执行路由恢复）"""
        def init_routes():
            self.register_system_routes()
            self.restore_route_from_storage()
        
        ui.timer(0.3, init_routes, once=True)
```

- **webproduct_ui_template\component\simple_spa_layout.py**
```python
from nicegui import ui
from functools import wraps
from typing import List, Dict, Callable, Optional, Any
from .layout_config import LayoutConfig
from .simple_layout_manager import SimpleLayoutManager

current_simple_layout_manager = None

def with_simple_spa_layout(config: Optional[LayoutConfig] = None,
                          nav_items: Optional[List[Dict[str, Any]]] = None,
                          header_config_items: Optional[List[Dict[str, Any]]] = None,
                          route_handlers: Optional[Dict[str, Callable]] = None):
    """简单SPA布局装饰器 - 只包含顶部导航栏"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            global current_simple_layout_manager
            layout_config = config or LayoutConfig()
            layout_manager = SimpleLayoutManager(layout_config)
            current_simple_layout_manager = layout_manager

            # 只有用户传递了导航项才添加，否则为空
            if nav_items is not None:
                for item in nav_items:
                    layout_manager.add_nav_item(item['key'], item['label'], item['icon'], item.get('route'))

            # 添加头部配置项
            if header_config_items is not None:
                for item in header_config_items:
                    layout_manager.add_header_config_item(
                        item['key'], 
                        item.get('label'), 
                        item.get('icon'), 
                        item.get('route'), 
                        item.get('on_click')
                    )

            # 设置路由处理器
            if route_handlers:
                for route, handler in route_handlers.items():
                    layout_manager.set_route_handler(route, handler)

            # 创建布局
            layout_manager.create_header()
            layout_manager.create_content_area()
            
            # 初始化路由
            layout_manager.initialize_layout()

            return func(*args, **kwargs)
        return wrapper
    return decorator

def get_simple_layout_manager() -> SimpleLayoutManager:
    """获取简单布局管理器实例"""
    global current_simple_layout_manager
    if current_simple_layout_manager is None:
        raise RuntimeError("布局管理器未初始化，请确保使用了 @with_simple_spa_layout 装饰器")
    return current_simple_layout_manager

def register_simple_route_handler(route: str, handler: Callable):
    """注册简单布局的路由处理器"""
    layout_manager = get_simple_layout_manager()
    layout_manager.set_route_handler(route, handler)

def simple_navigate_to(route: str, label: str = None):
    """简单布局的导航函数"""
    layout_manager = get_simple_layout_manager()
    if label is None:
        # 首先检查导航项
        nav_item = next((item for item in layout_manager.nav_items if item.route == route), None)
        if nav_item:
            label = nav_item.label
        else:
            # 检查头部配置项
            header_item = next((item for item in layout_manager.header_config_items if item.route == route), None)
            if header_item:
                label = header_item.label or header_item.key
            else:
                # 如果都没找到，使用路由名作为标签
                label = route.replace('_', ' ').title()
    
    # 导航并保存状态
    layout_manager.navigate_to_route(route, label, update_storage=True)
    
    # 同步更新导航选中状态（只有在导航项中才更新选中状态）
    for nav_item in layout_manager.nav_items:
        if nav_item.route == route:
            layout_manager.select_nav_item(nav_item.key, update_storage=False)
            break

def create_simple_spa_layout(config: Optional[LayoutConfig] = None,
                            nav_items: Optional[List[Dict[str, Any]]] = None,
                            header_config_items: Optional[List[Dict[str, Any]]] = None,
                            route_handlers: Optional[Dict[str, Callable]] = None) -> SimpleLayoutManager:
    """创建简单SPA布局"""
    global current_simple_layout_manager
    layout_config = config or LayoutConfig()
    layout_manager = SimpleLayoutManager(layout_config)
    current_simple_layout_manager = layout_manager

    # 只有用户传递了导航项才添加，否则为空
    if nav_items is not None:
        for item in nav_items:
            layout_manager.add_nav_item(item['key'], item['label'], item['icon'], item.get('route'))

    # 添加头部配置项
    if header_config_items is not None:
        for item in header_config_items:
            layout_manager.add_header_config_item(
                item['key'], 
                item.get('label'), 
                item.get('icon'), 
                item.get('route'), 
                item.get('on_click')
            )

    # 设置路由处理器
    if route_handlers:
        for route, handler in route_handlers.items():
            layout_manager.set_route_handler(route, handler)

    # 创建布局
    layout_manager.create_header()
    layout_manager.create_content_area()
    
    # 初始化路由
    layout_manager.initialize_layout()

    return layout_manager
```

- **webproduct_ui_template\component\spa_layout.py**
```python
from nicegui import ui
from functools import wraps
from typing import List, Dict, Callable, Optional, Any
from .layout_config import LayoutConfig
from .layout_manager import LayoutManager

current_layout_manager = None

def with_spa_layout(config: Optional[LayoutConfig] = None,
                    menu_items: Optional[List[Dict[str, Any]]] = None,
                    header_config_items: Optional[List[Dict[str, Any]]] = None,
                    route_handlers: Optional[Dict[str, Callable]] = None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            global current_layout_manager
            layout_config = config or LayoutConfig()
            layout_manager = LayoutManager(layout_config)
            current_layout_manager = layout_manager

            # 只有用户传递了菜单项才添加，否则为空
            if menu_items is not None:
                for item in menu_items:
                    layout_manager.add_menu_item(item['key'], item['label'], item['icon'], item.get('route'), item.get('separator_after', False))

            if header_config_items is not None:
                for item in header_config_items:
                    layout_manager.add_header_config_item(item['key'], item.get('label'), item.get('icon'), item.get('route'), item.get('on_click'))

            if route_handlers:
                for route, handler in route_handlers.items():
                    layout_manager.set_route_handler(route, handler)

            layout_manager.create_header()
            layout_manager.create_left_drawer()
            layout_manager.create_content_area()

            return func(*args, **kwargs)
        return wrapper
    return decorator

def get_layout_manager() -> LayoutManager:
    global current_layout_manager
    if current_layout_manager is None:
        raise RuntimeError("布局管理器未初始化，请确保使用了 @with_spa_layout 装饰器")
    return current_layout_manager

def register_route_handler(route: str, handler: Callable):
    layout_manager = get_layout_manager()
    layout_manager.set_route_handler(route, handler)


def navigate_to(route: str, label: str = None):
    """导航到指定路由"""
    layout_manager = get_layout_manager()
    if label is None:
        menu_item = next((item for item in layout_manager.menu_items if item.route == route), None)
        if menu_item:
            label = menu_item.label
        else:
            header_item = next((item for item in layout_manager.header_config_items if item.route == route), None)
            if header_item:
                label = header_item.label or header_item.key
            else:
                # 如果都没找到，使用路由名作为标签
                label = route.replace('_', ' ').title()
    
    # 导航并保存状态
    layout_manager.navigate_to_route(route, label, update_storage=True)
    
    # 同步更新菜单选中状态
    for menu_item in layout_manager.menu_items:
        if menu_item.route == route:
            layout_manager.select_menu_item(menu_item.key, update_storage=False)
            break


def create_spa_layout(config: Optional[LayoutConfig] = None,
                      menu_items: Optional[List[Dict[str, Any]]] = None,
                      header_config_items: Optional[List[Dict[str, Any]]] = None,
                      route_handlers: Optional[Dict[str, Callable]] = None) -> LayoutManager:
    global current_layout_manager
    layout_config = config or LayoutConfig()
    layout_manager = LayoutManager(layout_config)
    current_layout_manager = layout_manager

    # 只有用户传递了菜单项才添加，否则为空
    if menu_items is not None:
        for item in menu_items:
            layout_manager.add_menu_item(item['key'], item['label'], item['icon'], item.get('route'), item.get('separator_after', False))

    if header_config_items is not None:
        for item in header_config_items:
            layout_manager.add_header_config_item(item['key'], item.get('label'), item.get('icon'), item.get('route'), item.get('on_click'))

    if route_handlers:
        for route, handler in route_handlers.items():
            layout_manager.set_route_handler(route, handler)

    layout_manager.create_header()
    layout_manager.create_left_drawer()
    layout_manager.create_content_area()

    return layout_manager
```

- **webproduct_ui_template\component\static_resources.py**
```python
# 解决方案1: 更新static_resources.py，添加CSS加载功能

from nicegui import ui, app
import os
from pathlib import Path
from typing import Optional

class StaticResourceManager:
    """静态资源管理器"""
    
    def __init__(self, static_dir: str = "static"):
        self.static_dir = Path(static_dir)
        self.base_url = "/static"  # 静态文件的URL前缀
        self._ensure_directories()
        self._setup_static_routes()
    
    def _ensure_directories(self):
        """确保静态资源目录存在"""
        directories = [
            self.static_dir / "images" / "logo",
            self.static_dir / "images" / "avatars", 
            self.static_dir / "images" / "icons" / "menu-icons",
            self.static_dir / "images" / "icons" / "header-icons",
            self.static_dir / "css" / "themes",
            self.static_dir / "js" / "components",
            self.static_dir / "fonts" / "custom-fonts"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def _setup_static_routes(self):
        """设置静态文件路由"""
        if self.static_dir.exists():
            # 注册静态文件路由
            app.add_static_files(self.base_url, str(self.static_dir))
    
    def load_css_files(self):
        """加载所有CSS文件到页面"""
        css_files = [
            "css/custom.css",
            "css/themes/light.css", 
            "css/themes/dark.css"
        ]
        
        for css_file in css_files:
            css_path = self.static_dir / css_file
            if css_path.exists():
                # 方法1: 通过URL引用
                css_url = f"{self.base_url}/{css_file}"
                ui.add_head_html(f'<link rel="stylesheet" type="text/css" href="{css_url}">')
                print(f"✅ 已加载CSS: {css_url}")
            else:
                print(f"⚠️  CSS文件不存在: {css_path}")
    
    def load_inline_css(self, css_file: str):
        """将CSS内容内联到页面"""
        css_path = self.static_dir / css_file
        if css_path.exists():
            try:
                with open(css_path, 'r', encoding='utf-8') as f:
                    css_content = f.read()
                ui.add_head_html(f'<style type="text/css">{css_content}</style>')
                print(f"✅ 已内联加载CSS: {css_file}")
                return True
            except Exception as e:
                print(f"❌ 加载CSS失败 {css_file}: {e}")
                return False
        else:
            print(f"⚠️  CSS文件不存在: {css_path}")
            return False
    
    def get_css_url(self, filename: str) -> str:
        """获取CSS文件的URL"""
        return f"{self.base_url}/css/{filename}"
    
    def get_image_path(self, category: str, filename: str) -> str:
        """获取图片路径"""
        return f"{self.base_url}/images/{category}/{filename}"
    
    def get_logo_path(self, filename: str = "robot.svg") -> str:
        """获取Logo路径"""
        return self.get_image_path("logo", filename)
    
    def get_avatar_path(self, filename: str = "default_avatar.png") -> str:
        """获取头像路径"""
        return self.get_image_path("avatars", filename)
    
    def get_icon_path(self, category: str, filename: str) -> str:
        """获取图标路径"""
        return f"{self.base_url}/images/icons/{category}/{filename}"
    
    def get_css_path(self, filename: str) -> str:
        """获取CSS文件路径"""
        return f"{self.base_url}/css/{filename}"
    
    def get_theme_css_path(self, theme: str) -> str:
        """获取主题CSS路径"""
        return f"{self.base_url}/css/themes/{theme}.css"
    
    def get_js_path(self, filename: str) -> str:
        """获取JavaScript文件路径"""
        return f"{self.base_url}/js/{filename}"
    
    def get_font_path(self, filename: str) -> str:
        """获取字体文件路径"""
        return f"{self.base_url}/fonts/custom-fonts/{filename}"
    
    def file_exists(self, file_path: str) -> bool:
        """检查文件是否存在"""
        # 如果是URL路径，转换为本地路径检查
        if file_path.startswith(self.base_url):
            relative_path = file_path.replace(self.base_url + "/", "")
            local_path = self.static_dir / relative_path
        else:
            local_path = Path(file_path)
        return local_path.exists()
    
    def get_fallback_path(self, primary_path: str, fallback_path: str) -> str:
        """获取备用路径（如果主路径不存在）"""
        return primary_path if self.file_exists(primary_path) else fallback_path

# 全局静态资源管理器实例
static_manager = StaticResourceManager()
```

### webproduct_ui_template\component\chat

- **webproduct_ui_template\component\chat\__init__.py** *(包初始化文件)*
```python
"""
聊天组件包 - 可复用的聊天UI组件
从 menu_pages/enterprise_archive/chat_component 迁移而来

提供完整的聊天功能,包括:
- 聊天数据状态管理
- 聊天区域UI管理
- 侧边栏UI管理
- LLM模型配置
- Markdown内容解析
"""

from .chat_data_state import ChatDataState, SelectedValues, CurrentState, CurrentPromptConfig
from .chat_area_manager import ChatAreaManager
from .chat_sidebar_manager import ChatSidebarManager
from .chat_component import ChatComponent
from .config import (
    get_model_options_for_select,
    get_model_config,
    get_default_model,
    reload_llm_config,
    get_model_config_info,
    get_prompt_options_for_select,
    get_system_prompt,
    get_examples,
    get_default_prompt,
    reload_prompt_config,
    get_prompt_config_info
)
from .markdown_ui_parser import MarkdownUIParser

__all__ = [
    # 数据状态
    'ChatDataState',
    'SelectedValues',
    'CurrentState',
    'CurrentPromptConfig',
    
    # 管理器
    'ChatAreaManager',
    'ChatSidebarManager',
    
    # 主组件
    'ChatComponent',
    
    # 配置函数
    'get_model_options_for_select',
    'get_model_config',
    'get_default_model',
    'reload_llm_config',
    'get_model_config_info',
    'get_prompt_options_for_select',
    'get_system_prompt',
    'get_examples',
    'get_default_prompt',
    'reload_prompt_config',
    'get_prompt_config_info',
    
    # 工具类
    'MarkdownUIParser',
]
```

- **webproduct_ui_template\component\chat\chat_area_manager.py**
```python
"""
ChatAreaManager - 聊天内容显示区域
负责渲染展示聊天内容的UI和相关业务逻辑
"""
from abc import ABC, abstractmethod
import asyncio
from datetime import datetime
from nicegui import ui
from typing import Optional, List, Dict, Any
from component import static_manager
from .chat_data_state import ChatDataState
from .markdown_ui_parser import MarkdownUIParser

class ThinkContentParser:
    """思考内容解析器 - 专门处理<think>标签"""
    
    def __init__(self):
        self.is_in_think = False
        self.think_start_pos = -1
        self.think_content = ""
    
    def parse_chunk(self, full_content: str) -> Dict[str, Any]:
        """解析内容块,返回处理结果"""
        result = {
            'has_think': False,
            'think_content': '',
            'display_content': full_content,
            'think_complete': False,
            'think_updated': False
        }
    
        # 检测思考开始
        if '<think>' in full_content and not self.is_in_think:
            self.is_in_think = True
            self.think_start_pos = full_content.find('<think>')
            result['has_think'] = True
        
        # 检测思考结束
        if '</think>' in full_content and self.is_in_think:
            think_end_pos = full_content.find('</think>') + 8
            self.think_content = full_content[self.think_start_pos + 7:think_end_pos - 8]
            result['display_content'] = full_content[:self.think_start_pos] + full_content[think_end_pos:]
            result['think_content'] = self.think_content.strip()
            result['think_complete'] = True
            self.is_in_think = False
        elif self.is_in_think:
            # 正在思考中
            if self.think_start_pos >= 0:
                current_think = full_content[self.think_start_pos + 7:]
                result['display_content'] = full_content[:self.think_start_pos]
                result['think_content'] = current_think.strip()
                result['think_updated'] = True
        
        result['has_think'] = self.think_start_pos >= 0
        return result

class MessagePreprocessor:
    """消息预处理器"""
    
    def __init__(self, chat_data_state):
        self.chat_data_state = chat_data_state
    
    def enhance_user_message(self, user_message: str) -> str:
        """增强用户消息 - 使用 textarea 输入的提示数据"""
        try:
            # 检查是否启用了提示数据
            if not self.chat_data_state.switch:
                return user_message
            
            # 获取 textarea 中的原始输入
            raw_input = self.chat_data_state.selected_values.raw_input
            
            if not raw_input or not raw_input.strip():
                ui.notify("未输入提示数据", type="warning")
                return user_message
            
            # 直接将 textarea 内容附加到用户消息后面
            append_text = f"\n\n{raw_input.strip()}"
            
            return f"{user_message}{append_text}"
    
        except Exception as e:
            ui.notify(f"[ERROR] 增强用户消息时发生异常: {e}", type="negative")
            return user_message

class AIClientManager:
    """AI客户端管理器"""
    
    def __init__(self, chat_data_state):
        self.chat_data_state = chat_data_state
    
    async def get_client(self):
        """获取AI客户端"""
        from common.safe_openai_client_pool import get_openai_client
        
        selected_model = self.chat_data_state.current_model_config['selected_model']
        model_config = self.chat_data_state.current_model_config['config']
        
        client = await get_openai_client(selected_model, model_config)
        if not client:
            raise Exception(f"无法连接到模型 {selected_model}")
        
        return client, model_config
    
    def prepare_messages(self, user_msg_dict: Dict) -> List[Dict[str, str]]:
        """准备发送给AI的消息列表"""
        # 默认情况下,使用最近的5条聊天记录
        recent_messages = self.chat_data_state.current_chat_messages[-5:]
        
        if (self.chat_data_state.current_state.prompt_select_widget and 
            self.chat_data_state.current_prompt_config.system_prompt):
            system_message = {
                "role": "system", 
                "content": self.chat_data_state.current_prompt_config.system_prompt
            }
            recent_messages = [system_message] + recent_messages
        
        return recent_messages

class ContentDisplayStrategy(ABC):
    """内容展示策略抽象基类"""
    def __init__(self, ui_components):
        self.ui_components = ui_components
        self.think_parser = ThinkContentParser()
        self.structure_created = False
        self.reply_created = False
        self.think_expansion = None
        self.think_label = None
        self.reply_label = None
        self.chat_content_container = None
    
    @abstractmethod
    def create_ui_structure(self, has_think: bool):
        """创建UI结构"""
        pass
    
    @abstractmethod
    def update_content(self, parse_result: Dict[str, Any]) -> bool:
        """更新内容显示,返回是否需要滚动"""
        pass
    
    def process_stream_chunk(self, full_content: str) -> bool:
        """处理流式数据块 - 模板方法"""
        parse_result = self.think_parser.parse_chunk(full_content)
        
        # 创建UI结构(如果需要)
        if not self.structure_created:
            self.create_ui_structure(parse_result['has_think'])
            self.structure_created = True
        
        # 更新内容
        need_scroll = self.update_content(parse_result)
        return need_scroll
    
    async def finalize_content(self, final_content: str):
        """完成内容显示"""
        final_result = self.think_parser.parse_chunk(final_content)
        
        if final_result['think_complete'] and self.think_label:
            self.think_label.set_text(final_result['think_content'])
        
        if self.reply_label and final_result['display_content'].strip():
            self.reply_label.set_content(final_result['display_content'].strip())
            # 调用markdown优化显示
            if hasattr(self.ui_components, 'markdown_parser'):
                await self.ui_components.markdown_parser.optimize_content_display(
                    self.reply_label, final_result['display_content'], self.chat_content_container
                )

class DefaultDisplayStrategy(ContentDisplayStrategy):
    """默认展示策略"""
    
    def create_ui_structure(self, has_think: bool):
        """创建默认UI结构"""
        self.ui_components.waiting_ai_message_container.clear()
        with self.ui_components.waiting_ai_message_container:
            with ui.column().classes('w-full') as self.chat_content_container:
                if has_think:
                    self.think_expansion = ui.expansion(
                        '💭 AI思考过程...(可点击打开查看)', 
                        icon='psychology'
                    ).classes('w-full mb-2')
                    with self.think_expansion:
                        self.think_label = ui.label('').classes(
                            'whitespace-pre-wrap bg-[#81c784] border-0 shadow-none rounded-none'
                        )
                else:
                    self.reply_label = ui.markdown('').classes('w-full')
                    self.reply_created = True
    
    def update_content(self, parse_result: Dict[str, Any]) -> bool:
        """更新默认展示内容"""
        if parse_result['think_updated'] and self.think_label:
            self.think_label.set_text(parse_result['think_content'])
        
        if parse_result['think_complete']:
            # 思考完成,创建回复组件
            if self.chat_content_container and not self.reply_created:
                with self.chat_content_container:
                    self.reply_label = ui.markdown('').classes('w-full')
                self.reply_created = True
            
            if self.think_label:
                self.think_label.set_text(parse_result['think_content'])
        
        # 更新显示内容
        if self.reply_label and parse_result['display_content'].strip():
            with self.chat_content_container:
                self.reply_label.set_content(parse_result['display_content'].strip())
        
        return True  # 需要滚动

class StreamResponseProcessor:
    """流式响应处理器"""
    
    def __init__(self, chat_area_manager):
        self.chat_area_manager = chat_area_manager
        self.display_strategy = None
    
    def get_display_strategy(self) -> ContentDisplayStrategy:
        """获取展示策略 - 只使用默认策略"""
        return DefaultDisplayStrategy(self.chat_area_manager)
    
    async def process_stream_response(self, stream_response) -> str:
        """处理流式响应"""
        self.display_strategy = self.get_display_strategy()
        assistant_reply = ""
        
        for chunk in stream_response:
            if chunk.choices[0].delta.content:
                chunk_content = chunk.choices[0].delta.content
                assistant_reply += chunk_content
                
                # 使用策略处理内容
                need_scroll = self.display_strategy.process_stream_chunk(assistant_reply)
                
                if need_scroll:
                    await self.chat_area_manager.scroll_to_bottom_smooth()
                    await asyncio.sleep(0.05)
        
        # 完成内容显示
        await self.display_strategy.finalize_content(assistant_reply)
        return assistant_reply

class MessageProcessor:
    """消息处理门面类"""
    
    def __init__(self, chat_area_manager):
        self.chat_area_manager = chat_area_manager
        self.preprocessor = MessagePreprocessor(chat_area_manager.chat_data_state)
        self.ai_client_manager = AIClientManager(chat_area_manager.chat_data_state)
        self.stream_processor = StreamResponseProcessor(chat_area_manager)
    
    async def process_user_message(self, user_message: str) -> str:
        """处理用户消息并返回AI回复"""
        # 1. 预处理用户消息
        enhanced_message = self.preprocessor.enhance_user_message(user_message)
        
        # 2. 保存用户消息到历史
        user_msg_dict = {
            'role': 'user',
            'content': enhanced_message,
            'timestamp': datetime.now().isoformat()
        }
        
        self.chat_area_manager.chat_data_state.current_chat_messages.append(user_msg_dict)
        
        # 3. 渲染用户消息
        await self.chat_area_manager.render_single_message(user_msg_dict)
        await self.chat_area_manager.scroll_to_bottom_smooth()
        
        # 4. 启动等待效果
        await self.chat_area_manager.start_waiting_effect("正在处理")
        
        try:
            # 5. 获取AI客户端
            client, model_config = await self.ai_client_manager.get_client()
            
            # 6. 准备消息列表
            messages = self.ai_client_manager.prepare_messages(user_msg_dict)
            
            # 7. 调用AI API
            actual_model_name = model_config.get('model_name', 
                self.chat_area_manager.chat_data_state.current_model_config['selected_model']
            ) if model_config else self.chat_area_manager.chat_data_state.current_model_config['selected_model']
            
            stream_response = await asyncio.to_thread(
                client.chat.completions.create,
                model=actual_model_name,
                messages=messages,
                max_tokens=2000,
                temperature=0.7,
                stream=True
            )
            
            # 8. 停止等待效果并处理流式响应
            await self.chat_area_manager.stop_waiting_effect()
            assistant_reply = await self.stream_processor.process_stream_response(stream_response)
            
            return assistant_reply
            
        except Exception as e:
            # 错误处理
            error_message = f"抱歉,调用AI服务时出现错误:{str(e)[:300]}..."
            ui.notify('AI服务调用失败,请稍后重试', type='negative')
            
            await self.chat_area_manager.stop_waiting_effect()
            if self.chat_area_manager.waiting_message_label:
                self.chat_area_manager.waiting_message_label.set_text(error_message)
                self.chat_area_manager.waiting_message_label.classes(remove='text-gray-500 italic')
            
            return error_message

# 更新后的 ChatAreaManager 类
class ChatAreaManager:
    """主聊天区域管理器 - 负责聊天内容展示和用户交互"""  
    def __init__(self, chat_data_state):
        """初始化聊天区域管理器"""
        self.chat_data_state = chat_data_state
        self.markdown_parser = MarkdownUIParser()
        # UI组件引用
        self.scroll_area = None
        self.chat_messages_container = None
        self.welcome_message_container = None
        self.input_ref = {'widget': None}
        self.send_button_ref = {'widget': None}
        self.clear_button_ref = {'widget': None}
        # 其他UI引用
        self.switch = None
        self.hierarchy_selector = None
        # 新增类属性:AI回复相关组件
        self.reply_label = None
        self.chat_content_container = None
        # 等待效果
        self.waiting_message_label = None
        self.waiting_animation_task = None
        self.waiting_ai_message_container = None
        # 聊天头像
        self.user_avatar = static_manager.get_fallback_path(
            static_manager.get_logo_path('user.svg'),
            static_manager.get_logo_path('ProfileHeader.gif'),
        )
        self.robot_avatar = static_manager.get_fallback_path(
            static_manager.get_logo_path('robot_txt.svg'),
            static_manager.get_logo_path('Live chatbot.gif'),
        )
        
        # 初始化消息处理器
        self.message_processor = MessageProcessor(self)

    #region 等待效果相关方法
    async def start_waiting_effect(self, message="正在处理"):
        """启动等待效果"""
        # 添加等待效果的机器人消息容器
        with self.chat_messages_container:
            self.waiting_ai_message_container = ui.chat_message(
                avatar=self.robot_avatar
            ).classes('w-full')
            
            with self.waiting_ai_message_container:
                self.waiting_message_label = ui.label(message).classes('whitespace-pre-wrap text-gray-500 italic')

        await self.scroll_to_bottom_smooth()

        # 启动等待动画
        animation_active = [True]  # 使用列表以支持闭包内修改
        
        async def animate_waiting():
            dots_count = 0
            while animation_active[0] and self.waiting_message_label:
                dots_count = (dots_count % 3) + 1
                waiting_dots = "." * dots_count
                self.waiting_message_label.set_text(f"{message}{waiting_dots}")
                await asyncio.sleep(0.5)
        
        self.waiting_animation_task = asyncio.create_task(animate_waiting())
        
        # 存储动画状态的引用
        self.waiting_animation_active = animation_active

    async def stop_waiting_effect(self):
        """停止等待效果"""
        if hasattr(self, 'waiting_animation_active'):
            self.waiting_animation_active[0] = False
        
        if self.waiting_animation_task:
            self.waiting_animation_task.cancel()
            try:
                await self.waiting_animation_task
            except asyncio.CancelledError:
                pass

    async def cleanup_waiting_effect(self):
        """清理等待效果的UI组件"""
        if self.waiting_ai_message_container:
            self.waiting_ai_message_container.clear()
            self.waiting_ai_message_container = None
        self.waiting_message_label = None
    #endregion

    #region 消息渲染相关方法
    async def render_single_message(self, message: Dict[str, Any], container=None):
        """渲染单条消息"""
        target_container = container if container is not None else self.chat_messages_container
        
        with target_container:
            if message['role'] == 'user':
                with ui.chat_message(
                    avatar=self.user_avatar,
                    sent=True
                ).classes('w-full'):
                    ui.label(message['content']).classes('whitespace-pre-wrap break-words')
            
            elif message['role'] == 'assistant':
                with ui.chat_message(
                    avatar=self.robot_avatar
                ).classes('w-full'):
                    # 创建临时的chat_content_container用于单条消息渲染
                    with ui.column().classes('w-full') as self.chat_content_container:
                        # 检查消息内容是否包含think标签
                        content = message['content']
                        if '<think>' in content and '</think>' in content:
                            # 包含think内容,需要特殊处理
                            import re
                            # 提取think内容
                            think_match = re.search(r'<think>(.*?)</think>', content, re.DOTALL)
                            if think_match:
                                think_content = think_match.group(1).strip()
                                # 移除think标签,获取显示内容
                                display_content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL).strip()
                                
                                # 创建think展开面板
                                with ui.expansion(
                                    '💭 AI思考过程...(可点击打开查看)', 
                                    icon='psychology'
                                ).classes('w-full mb-2'):
                                    ui.label(think_content).classes(
                                        'whitespace-pre-wrap bg-[#81c784] border-0 shadow-none rounded-none'
                                    )
                                
                                # 显示实际回复内容
                                if display_content:
                                    temp_reply_label = ui.markdown(display_content).classes('w-full')
                                    await self.markdown_parser.optimize_content_display(
                                        temp_reply_label, 
                                        display_content, 
                                        self.chat_content_container
                                    )
                        else:
                            # 不包含think内容,直接显示
                            temp_reply_label = ui.markdown(content).classes('w-full')
                            await self.markdown_parser.optimize_content_display(
                                temp_reply_label, 
                                content, 
                                self.chat_content_container
                            )

    def restore_welcome_message(self):
        """恢复欢迎消息"""
        self.chat_messages_container.clear()
        if self.welcome_message_container:
            self.welcome_message_container.clear()
            with self.welcome_message_container:
                with ui.card().classes('w-full max-w-3xl mx-auto shadow-lg'):
                    with ui.column().classes('p-6 text-center'):
                        ui.icon('waving_hand', size='3xl').classes('text-blue-500 mb-4 text-3xl')
                        ui.label('欢迎使用智能问答助手').classes('text-2xl font-bold mb-2')
                        ui.label('请输入您的问题,我将为您提供帮助').classes('text-lg text-gray-600 mb-4')
                        
                        with ui.row().classes('justify-center gap-4'):
                            ui.chip('问答', icon='quiz').classes('text-blue-600 text-lg')
                            ui.chip('制表', icon='table_view').classes('text-yellow-600 text-lg')
                            ui.chip('绘图', icon='dirty_lens').classes('text-purple-600 text-lg')
                            ui.chip('分析', icon='analytics').classes('text-orange-600 text-lg')
    #endregion

    #region 滚动相关方法
    async def scroll_to_bottom_smooth(self):
        """平滑滚动到底部"""
        if self.scroll_area:
            await asyncio.sleep(0.05)
            self.scroll_area.scroll_to(percent=1)
    #endregion

    #region 消息处理相关方法
    def handle_keydown(self, e):
        """处理键盘事件 - 使用NiceGUI原生方法"""
        # 检查输入框是否已禁用,如果禁用则不处理按键事件
        if not self.input_ref['widget'].enabled:
            return
            
        # 获取事件详细信息
        key = e.args.get('key', '')
        shift_key = e.args.get('shiftKey', False)
        
        if key == 'Enter':
            if shift_key:
                # Shift+Enter: 允许换行,不做任何处理
                pass
            else:
                # 单独的Enter: 发送消息
                # 阻止默认的换行行为
                ui.run_javascript('event.preventDefault();')
                # 异步调用消息处理函数
                ui.timer(0.01, lambda: self.handle_message(), once=True)

    async def handle_message(self):
        """处理发送消息"""
        user_message = self.input_ref['widget'].value.strip()
        if not user_message:
            ui.notify('请输入消息内容', type='warning')
            return
        
        # 清空输入框
        self.input_ref['widget'].set_value('')
        
        # 禁用输入控件
        self.input_ref['widget'].set_enabled(False)
        self.send_button_ref['widget'].set_enabled(False)
        
        try:
            # 清除欢迎消息
            if self.welcome_message_container:
                self.welcome_message_container.clear()
            # 使用消息处理器处理用户消息
            assistant_reply = await self.message_processor.process_user_message(user_message)
            # 记录AI回复到聊天历史
            self.chat_data_state.current_chat_messages.append({
                'role': 'assistant', 
                'content': assistant_reply,
                'timestamp': datetime.now().isoformat(),
                'model': self.chat_data_state.current_state.selected_model
            })
            # 完成回复后最终滚动
            await self.scroll_to_bottom_smooth()
        finally:
            # 恢复输入控件
            await self.stop_waiting_effect()
            self.input_ref['widget'].set_enabled(True)
            self.send_button_ref['widget'].set_enabled(True)
            self.input_ref['widget'].run_method('focus')

    async def clear_chat_content(self):
        """清空聊天内容"""
        try:
            # 清空聊天消息容器
            self.chat_messages_container.clear()
            # 清空聊天数据状态中的消息
            self.chat_data_state.current_chat_messages.clear()
            # 恢复欢迎消息
            self.restore_welcome_message()
            # 显示成功提示
            ui.notify('聊天内容已清空', type='positive')
        except Exception as e:
            ui.notify(f'清空聊天失败: {str(e)}', type='negative')
    #endregion

    #region think内容处理方法
    def has_think_content(self, messages):
        """检测消息列表是否包含think内容"""
        for msg in messages:
            if msg.get('role') == 'assistant' and '<think>' in msg.get('content', ''):
                return True
        return False

    def remove_think_content(self, messages):
        """从消息列表中移除think标签及内容"""
        import re
        cleaned_messages = []
        
        for msg in messages:
            cleaned_msg = msg.copy()
            if msg.get('role') == 'assistant':
                content = msg.get('content', '')
                if '<think>' in content and '</think>' in content:
                    # 移除think标签及其内容
                    cleaned_content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL)
                    cleaned_msg['content'] = cleaned_content.strip()
            
            cleaned_messages.append(cleaned_msg)
        
        return cleaned_messages
    #endregion

    #region 历史记录相关逻辑
    async def render_chat_history(self, chat_id):
        """渲染聊天历史内容"""
        try:
            self.chat_messages_container.clear()
            self.welcome_message_container.clear()
            await self.start_waiting_effect("正在加载聊天记录")

            from database_models.business_models.chat_history_model import ChatHistory
            from auth.database import get_db 
            with get_db() as db:
                chat = db.query(ChatHistory).filter(
                    ChatHistory.id == chat_id,
                    ChatHistory.is_deleted == False
                ).first()
                
                if not chat:
                    ui.notify('聊天记录不存在', type='negative')
                    return
                # 在会话关闭前获取消息数据
                prompt_name = chat.prompt_name
                model_name = chat.model_name
                messages = chat.messages.copy() if chat.messages else []
                chat_title = chat.title
                
            # 清空当前聊天消息并加载历史消息
            self.chat_data_state.current_chat_messages.clear()
            self.chat_data_state.current_chat_messages.extend(messages)
            await self.stop_waiting_effect()
            await self.cleanup_waiting_effect()

            # 恢复历史聊天,侧边栏设置
            self.chat_data_state.current_state.model_select_widget.set_value(model_name)
            self.chat_data_state.current_state.prompt_select_widget.set_value(prompt_name)

            # 清空聊天界面
            self.chat_messages_container.clear()
            # 使用异步任务来渲染消息
            async def render_messages_async():
                for msg in messages:
                    await self.render_single_message(msg)

            # 创建异步任务来处理消息渲染
            ui.timer(0.01, lambda: asyncio.create_task(render_messages_async()), once=True)
            # 滚动到底部
            ui.timer(0.1, lambda: self.scroll_area.scroll_to(percent=1), once=True)
            ui.notify(f'已加载聊天: {chat_title}', type='positive') 
 
        except Exception as e:
            await self.stop_waiting_effect()
            await self.cleanup_waiting_effect()
            self.restore_welcome_message()
            ui.notify('加载聊天失败', type='negative')    
    #endregion

    def render_ui(self):
        """渲染主聊天区域UI"""
        # 主聊天区域 - 占据剩余空间
        with ui.column().classes('flex-grow h-full').style('position: relative; overflow: hidden;'):
            # 聊天消息区域 - 使用 scroll_area 提供更好的滚动体验
            self.scroll_area = ui.scroll_area().classes('w-full').style('height: calc(100% - 80px); padding-bottom: 20px;')

            with self.scroll_area:
                self.chat_messages_container = ui.column().classes('w-full gap-2')  
                # 欢迎消息(可能会被删除)
                self.welcome_message_container = ui.column().classes('w-full')
                with self.welcome_message_container:
                    self.restore_welcome_message()
            # 输入区域 - 固定在底部,距离底部10px
            with ui.row().classes('w-full items-center gap-2 rounded ').style(
                'position: absolute; bottom: 10px; left: 10px; right: 10px; z-index: 1000; '
                'margin: 0 auto; max-width: calc(100% - 20px);'
            ):    
                # 创建textarea并绑定事件
                self.input_ref['widget'] = ui.textarea(
                    placeholder='请输入您的消息...(Enter发送,Shift+Enter换行)'
                ).classes('flex-grow').style(
                    'min-height: 44px; max-height: 120px; resize: none;'
                ).props('outlined dense rounded rows=3').tooltip('输入聊天内容')

                # 使用.on()方法监听keydown事件
                self.input_ref['widget'].on('keydown', self.handle_keydown)
                
                self.send_button_ref['widget'] = ui.button(
                    icon='send',
                    on_click=self.handle_message
                ).props('round dense ').classes('ml-2').tooltip('发送聊天内容')

                # 清空聊天按钮
                self.clear_button_ref['widget'] = ui.button(
                    icon='cleaning_services',
                    on_click=self.clear_chat_content
                ).props('round dense').classes('ml-2').tooltip('清空聊天内容')
```

- **webproduct_ui_template\component\chat\chat_component.py**
````python
"""
ChatComponent - 聊天组件统一入口
提供简洁的API供外部调用,封装所有内部实现细节
"""

from nicegui import ui
from typing import Optional
from .chat_data_state import ChatDataState
from .chat_area_manager import ChatAreaManager
from .chat_sidebar_manager import ChatSidebarManager


class ChatComponent:
    """
    聊天组件主类 - 统一入口
    
    使用示例:
```python
    from component.chat import ChatComponent
    
    # 基础使用
    chat = ChatComponent()
    chat.render()
    
    # 自定义配置
    chat = ChatComponent(
        sidebar_visible=True,
        default_model='deepseek-chat',
        default_prompt='一企一档专家',
        is_record_history=True
    )
    chat.render()
```
    """
    
    def __init__(
        self,
        sidebar_visible: bool = True,
        default_model: Optional[str] = None,
        default_prompt: Optional[str] = None,
        is_record_history: bool = True
    ):
        """
        初始化聊天组件
        
        Args:
            sidebar_visible: 侧边栏是否可见,默认为True
            default_model: 指定的默认LLM模型,默认为None(使用配置文件中的默认值)
            default_prompt: 指定的默认提示词模板,默认为None(使用配置文件中的默认值)
            is_record_history: 是否记录聊天历史到数据库,默认为True
        """
        self.sidebar_visible = sidebar_visible
        self.default_model = default_model
        self.default_prompt = default_prompt
        self.is_record_history = is_record_history
        
        # 初始化数据状态
        self.chat_data_state = ChatDataState()
        
        # 初始化管理器(延迟到render时创建,因为需要UI上下文)
        self.chat_area_manager: Optional[ChatAreaManager] = None
        self.chat_sidebar_manager: Optional[ChatSidebarManager] = None
        
    def render(self):
        """
        渲染聊天组件UI
        必须在NiceGUI的UI上下文中调用
        """
        # 添加聊天组件专用样式
        self._add_chat_styles()
        
        # 创建管理器实例
        self.chat_area_manager = ChatAreaManager(self.chat_data_state)
        self.chat_sidebar_manager = ChatSidebarManager(
            chat_data_state=self.chat_data_state,
            chat_area_manager=self.chat_area_manager,
            sidebar_visible=self.sidebar_visible,
            default_model=self.default_model,
            default_prompt=self.default_prompt,
            is_record_history=self.is_record_history
        )
        
        # 渲染UI结构
        with ui.row().classes('w-full h-full chat-archive-container').style(
            'height: calc(100vh - 120px); margin: 0; padding: 0;'
        ):
            # 侧边栏
            self.chat_sidebar_manager.render_ui()
            # 主聊天区域
            self.chat_area_manager.render_ui()
    
    def _add_chat_styles(self):
        """添加聊天组件专用CSS样式"""
        ui.add_head_html('''
            <style>
            /* 聊天组件专用样式 - 只影响聊天组件内部,不影响全局 */
            .chat-archive-container {
                height: calc(100vh - 145px) !important;
                margin: 0 !important;
                padding: 0 !important;
                overflow-y: auto !important;
            }        
            .chat-archive-sidebar {
                border-right: 1px solid #e5e7eb;
                overflow-y: auto;
            }
            .chat-archive-sidebar::-webkit-scrollbar {
                width: 2px;
            }
            .chat-archive-sidebar::-webkit-scrollbar-track {
                background: transparent;
            }
            .chat-archive-sidebar::-webkit-scrollbar-thumb {
                background-color: #d1d5db;
                border-radius: 3px;
            }
            .chat-archive-sidebar::-webkit-scrollbar-thumb:hover {
                background-color: #9ca3af;
            }
            /* 优化 scroll_area 内容区域的样式 */
            .q-scrollarea__content {
                min-height: 100%;
            }
            .chathistorylist-hide-scrollbar {
                overflow-y: auto;
                scrollbar-width: none;
                -ms-overflow-style: none;
            }
            .chathistorylist-scrollbar::-webkit-scrollbar {
                display: none;
            }
            </style>
        ''')
    
    def get_chat_data_state(self) -> ChatDataState:
        """获取聊天数据状态对象"""
        return self.chat_data_state
    
    def get_chat_area_manager(self) -> Optional[ChatAreaManager]:
        """获取聊天区域管理器"""
        return self.chat_area_manager
    
    def get_chat_sidebar_manager(self) -> Optional[ChatSidebarManager]:
        """获取侧边栏管理器"""
        return self.chat_sidebar_manager
````

- **webproduct_ui_template\component\chat\chat_data_state.py**
```python
"""
聊天数据状态管理
定义聊天组件使用的所有数据结构
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Union

@dataclass
class SelectedValues:
    """数据输入值数据结构 - 通过 textarea JSON 输入"""
    # 层级数据
    # l1: Optional[str] = None
    # l2: Optional[str] = None
    # l3: Optional[str] = None
    # field: Union[List[str], str, None] = None
    # field_name: Union[List[str], str, None] = None
    
    # # 扩展字段
    # data_url: Optional[str] = None
    # full_path_code: Optional[str] = None
    # full_path_name: Optional[str] = None
    
    # textarea 输入相关
    raw_input: Optional[str] = None  # textarea原始输入内容

@dataclass
class CurrentState:
    """当前状态数据结构"""
    model_options: List[str] = field(default_factory=list)
    default_model: str = 'deepseek-chat'
    selected_model: str = 'deepseek-chat'
    model_select_widget: Optional[Any] = None
    prompt_select_widget: Optional[Any] = None

@dataclass
class CurrentPromptConfig:
    """当前提示词配置数据结构"""
    selected_prompt: Optional[str] = None
    system_prompt: str = ''
    examples: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ChatDataState:
    """聊天数据状态主类"""
    # 模型相关
    model_options: List[str] = field(default_factory=list)
    default_model: str = 'deepseek-chat'
    current_model_config: Dict[str, Any] = field(default_factory=dict)
    
    # 当前状态
    current_state: CurrentState = field(default_factory=CurrentState)
    
    # 记录当前聊天中的消息
    current_chat_messages: List[Dict] = field(default_factory=list)
    
    # 提示词初始化
    prompt_options: List[str] = field(default_factory=list)
    default_prompt: Optional[str] = None
    current_prompt_config: CurrentPromptConfig = field(default_factory=CurrentPromptConfig)
    
    # 数据输入开关和值
    switch: bool = False
    selected_values: SelectedValues = field(default_factory=SelectedValues)

    # 当前聊天id
    current_chat_id: Optional[int] = None
```

- **webproduct_ui_template\component\chat\chat_sidebar_manager.py**
```python
"""
ChatSidebarManager - 聊天侧边栏管理器
负责管理侧边栏的UI和相关业务逻辑
"""
from datetime import datetime
from nicegui import ui
from typing import Optional
from .chat_data_state import ChatDataState

from .config import (
    get_model_options_for_select, 
    get_model_config, 
    get_default_model,
    reload_llm_config,
    get_model_config_info,
    get_prompt_options_for_select,
    get_system_prompt,
    get_examples,
    get_default_prompt,
    reload_prompt_config
)

class ChatSidebarManager:
    """聊天侧边栏管理器"""
    
    def __init__(
        self, 
        chat_data_state: ChatDataState, 
        chat_area_manager,
        sidebar_visible: bool = True, 
        default_model: Optional[str] = None, 
        default_prompt: Optional[str] = None,
        is_record_history: bool = True
    ):
        """
        初始化侧边栏管理器
        
        Args:
            chat_data_state: 聊天数据状态对象
            chat_area_manager: 聊天区域管理器实例
            sidebar_visible: 侧边栏是否可见,默认为True
            default_model: 指定的默认模型,默认为None
            default_prompt: 指定的默认提示词,默认为None
            is_record_history: 是否记录聊天历史,默认为True
        """
        self.chat_data_state = chat_data_state
        self.chat_area_manager = chat_area_manager
        
        # UI组件引用
        self.history_list_container = None
        self.switch = None
        self.data_input_textarea = None  # textarea输入框
        self.validation_status_label = None  # 验证状态标签
        
        # 存储侧边栏可见性配置
        self.sidebar_visible = sidebar_visible
        self.is_record_history = is_record_history

        # 初始化数据
        self._initialize_data(default_model, default_prompt)
    
    def _initialize_data(self, default_model_param: Optional[str] = None, default_prompt_param: Optional[str] = None):
        """初始化数据状态"""
        # 初始化模型相关数据
        self.chat_data_state.model_options = get_model_options_for_select()
        
        if default_model_param and default_model_param in self.chat_data_state.model_options:
            self.chat_data_state.default_model = default_model_param
        else:
            self.chat_data_state.default_model = get_default_model() or 'deepseek-chat'
            if default_model_param:
                ui.notify(f"指定的模型 '{default_model_param}' 不存在，使用默认模型", type='warning')

        self.chat_data_state.current_model_config = {
            'selected_model': self.chat_data_state.default_model, 
            'config': get_model_config(self.chat_data_state.default_model)
        }
        
        # 初始化当前状态
        self.chat_data_state.current_state.model_options = self.chat_data_state.model_options
        self.chat_data_state.current_state.default_model = self.chat_data_state.default_model
        self.chat_data_state.current_state.selected_model = self.chat_data_state.default_model
        
        # 初始化提示词数据
        self.chat_data_state.prompt_options = get_prompt_options_for_select()
        
        if default_prompt_param and default_prompt_param in self.chat_data_state.prompt_options:
            self.chat_data_state.default_prompt = default_prompt_param
        else:
            self.chat_data_state.default_prompt = get_default_prompt() or (
                self.chat_data_state.prompt_options[0] if self.chat_data_state.prompt_options else None
            )
            if default_prompt_param:
                ui.notify(f"指定的提示词 '{default_prompt_param}' 不存在，使用默认提示词", type='warning')

        self.chat_data_state.current_prompt_config.selected_prompt = self.chat_data_state.default_prompt
        self.chat_data_state.current_prompt_config.system_prompt = (
            get_system_prompt(self.chat_data_state.default_prompt) 
            if self.chat_data_state.default_prompt else ''
        )
        self.chat_data_state.current_prompt_config.examples = (
            get_examples(self.chat_data_state.default_prompt) 
            if self.chat_data_state.default_prompt else {}
        )
        self.chat_data_state.current_chat_id = None

    # region 模型选择相关处理逻辑
    def on_model_change(self, e):
        """模型选择变化事件处理"""
        selected_model = e.value
        
        # 更新当前状态
        self.chat_data_state.current_state.selected_model = selected_model
        self.chat_data_state.current_model_config['selected_model'] = selected_model
        self.chat_data_state.current_model_config['config'] = get_model_config(selected_model)
        
        # 显示选择信息
        ui.notify(f'已切换到模型: {selected_model}')
    
    def on_refresh_model_config(self):
        """刷新模型配置"""
        try:
            ui.notify('正在刷新模型配置...', type='info')
            success = reload_llm_config()
            
            if success:
                # 重新获取配置
                new_options = get_model_options_for_select()
                new_default = get_default_model() or 'deepseek-chat'
                
                # 更新数据状态
                self.chat_data_state.model_options = new_options
                self.chat_data_state.default_model = new_default
                self.chat_data_state.current_state.model_options = new_options
                self.chat_data_state.current_state.default_model = new_default
                
                # 更新UI组件
                if self.chat_data_state.current_state.model_select_widget:
                    current_selection = self.chat_data_state.current_state.selected_model
                    if current_selection not in new_options:
                        current_selection = new_default
                    
                    self.chat_data_state.current_state.model_select_widget.set_options(new_options)
                    self.chat_data_state.current_state.model_select_widget.set_value(current_selection)
                    self.chat_data_state.current_state.selected_model = current_selection
                    
                    # 同步更新 current_model_config
                    self.chat_data_state.current_model_config['selected_model'] = current_selection
                    self.chat_data_state.current_model_config['config'] = get_model_config(current_selection)
                
                # 显示刷新结果
                config_info = get_model_config_info()
                ui.notify(
                    f'配置刷新成功！共加载 {config_info["total_models"]} 个模型，'
                    f'其中 {config_info["enabled_models"]} 个已启用',
                    type='positive'
                )
            else:
                ui.notify('配置刷新失败，请检查配置文件', type='negative')
                
        except Exception as e:
            ui.notify(f'刷新配置时出错: {str(e)}', type='negative')
    
    def on_prompt_change(self, e):
        """提示词选择变化事件处理"""
        selected_prompt_key = e.value
        
        # 获取系统提示词内容和示例
        system_prompt = get_system_prompt(selected_prompt_key)
        examples = get_examples(selected_prompt_key)
        
        # 更新当前提示词配置
        self.chat_data_state.current_prompt_config.selected_prompt = selected_prompt_key
        self.chat_data_state.current_prompt_config.system_prompt = system_prompt or ''
        self.chat_data_state.current_prompt_config.examples = examples or {}
        
        # 显示选择信息
        ui.notify(f'已切换到提示词: {selected_prompt_key}')
    
    def on_refresh_prompt_config(self):
        """刷新提示词配置"""
        try:
            ui.notify('正在刷新提示词配置...', type='info')
            success = reload_prompt_config()
            
            if success:
                # 重新获取配置
                prompt_options = get_prompt_options_for_select()
                new_default = get_default_prompt() or (prompt_options[0] if prompt_options else None)
                
                # 更新数据状态
                self.chat_data_state.prompt_options = prompt_options
                self.chat_data_state.default_prompt = new_default
                
                # 更新UI组件
                if self.chat_data_state.current_state.prompt_select_widget:
                    current_selection = self.chat_data_state.current_prompt_config.selected_prompt
                    if current_selection not in prompt_options:
                        current_selection = new_default
                    
                    self.chat_data_state.current_state.prompt_select_widget.set_options(prompt_options)
                    self.chat_data_state.current_state.prompt_select_widget.set_value(current_selection)
                    
                    self.chat_data_state.current_prompt_config.selected_prompt = current_selection
                    self.chat_data_state.current_prompt_config.system_prompt = (
                        get_system_prompt(current_selection) if current_selection else ''
                    )
                    self.chat_data_state.current_prompt_config.examples = (
                        get_examples(current_selection) if current_selection else {}
                    )
                
                ui.notify(f'提示词配置刷新成功，共加载 {len(prompt_options)} 个模板', type='positive')
            else:
                ui.notify('提示词配置刷新失败', type='negative')
                
        except Exception as e:
            ui.notify(f'刷新提示词配置时发生错误: {str(e)}', type='negative')
    # endregion 模型选择相关逻辑
    
    # region textarea 数据输入相关逻辑
    def _render_textarea_input(self):
        """
        渲染textarea输入框 - 极简版
        """
        # textarea输入框 - 直接双向绑定到 selected_values.raw_input
        self.data_input_textarea = ui.textarea(
            placeholder='请输入提示数据...\n\n支持多行输入，无格式限制',
            value=''
        ).classes('w-full').props('outlined dense').style(
            'min-height: 120px; '
            'font-size: 14px; '
            'line-height: 1.6;'
        ).bind_value(self.chat_data_state.selected_values, 'raw_input')
        
        # 使用说明
        with ui.row().classes('w-full mt-1 items-center'):
            ui.icon('info', size='sm').classes('text-blue-500')
            ui.label('启用开关后，此处内容将附加到您的对话消息中').classes('text-xs text-gray-600')
    # endregion textarea 数据输入相关逻辑
    
    #region 新建会话相关逻辑
    async def on_create_new_chat(self):
        """新建聊天会话"""
        try:
            # 🔥 新增：先判断是否已有聊天记录，执行插入或更新操作
            if self.chat_data_state.current_chat_messages:
                # 检查当前是否为加载的历史对话（通过检查 current_chat_messages 是否与某个历史记录匹配）
                existing_chat_id = self.get_current_loaded_chat_id()
                
                if existing_chat_id:
                    # 更新现有聊天记录
                    update_success = self.update_existing_chat_to_database(existing_chat_id)
                    if update_success:
                        ui.notify('对话已更新', type='positive')
                    else:
                        ui.notify('更新对话失败', type='negative')
                        return
                else:
                    # 插入新的聊天记录
                    save_success = self.save_chat_to_database()
                    if save_success:
                        ui.notify('对话已保存', type='positive')
                    else:
                        ui.notify('保存对话失败', type='negative')
                        return
                
                # 清空当前聊天记录
                self.chat_data_state.current_chat_messages.clear()
                # 恢复欢迎消息
                self.chat_area_manager.restore_welcome_message()
                # 新增：自动刷新聊天历史列表
                self.refresh_chat_history_list()
                # 重置当前加载的聊天ID
                self.reset_current_loaded_chat_id()     
            else:
                self.chat_area_manager.restore_welcome_message()
                ui.notify('界面已重置', type='info')
                
        except Exception as e:
            ui.notify(f'创建新对话失败: {str(e)}', type='negative')
    
    def get_current_loaded_chat_id(self):
        """获取当前加载的聊天记录ID"""
        return self.chat_data_state.current_chat_id

    def set_current_loaded_chat_id(self, chat_id):
        """设置当前加载的聊天记录ID"""
        self.chat_data_state.current_chat_id = chat_id

    def reset_current_loaded_chat_id(self):
        """重置当前加载的聊天记录ID"""
        self.chat_data_state.current_chat_id = None

    def update_existing_chat_to_database(self, chat_id):
        """更新现有的聊天记录到数据库"""
        if chat_id is None:
            return True
        try:
            from auth import auth_manager
            from database_models.business_models.chat_history_model import ChatHistory
            from auth.database import get_db
            
            current_user = auth_manager.current_user
            if not current_user:
                ui.notify('用户未登录，无法更新聊天记录', type='warning')
                return False
            
            if not self.chat_data_state.current_chat_messages:
                ui.notify('没有聊天记录需要更新', type='info')
                return False
            
            with get_db() as db:
                chat_history = db.query(ChatHistory).filter(
                    ChatHistory.id == chat_id,
                    ChatHistory.created_by == current_user.id,
                    ChatHistory.is_deleted == False
                ).first()
                
                if not chat_history:
                    ui.notify('聊天记录不存在或无权限', type='negative')
                    return False
                
                # 更新聊天记录
                chat_history.messages = self.chat_data_state.current_chat_messages.copy()
                chat_history.model_name = self.chat_data_state.current_state.selected_model
                
                # 使用模型的内置方法更新统计信息
                chat_history.update_message_stats()
                chat_history.updated_at = datetime.now()
                
                db.commit()
                return True
                
        except Exception as e:
            ui.notify(f'更新聊天记录失败: {str(e)}', type='negative')
            return False

    def save_chat_to_database(self):
        """保存新的聊天记录到数据库"""
        try:
            from auth import auth_manager
            from database_models.business_models.chat_history_model import ChatHistory
            from database_models.business_utils import AuditHelper
            from auth.database import get_db
            
            current_user = auth_manager.current_user
            if not current_user:
                ui.notify('用户未登录，无法保存聊天记录', type='warning')
                return False
            
            if not self.chat_data_state.current_chat_messages:
                ui.notify('没有聊天记录需要保存', type='info')
                return False
            
            # 生成聊天标题（使用第一条用户消息的前20个字符）
            title = "新对话"
            for msg in self.chat_data_state.current_chat_messages:
                if msg.get('role') == 'user':
                    content = msg.get('content', '')
                    title = content[:20] + ('...' if len(content) > 20 else '')
                    break
            
            # 处理think内容：检测是否有think内容，有则移除
            messages_to_save = self.chat_data_state.current_chat_messages.copy()
            if self.chat_area_manager.has_think_content(messages_to_save):
                messages_to_save = self.chat_area_manager.remove_think_content(messages_to_save)
            
            with get_db() as db:
                chat_history = ChatHistory(
                    title=title,
                    model_name=self.chat_data_state.current_state.selected_model,
                    prompt_name = self.chat_data_state.current_prompt_config.selected_prompt,
                    messages=messages_to_save
                )
                
                # 使用模型的内置方法更新统计信息
                chat_history.update_message_stats()
                
                # 设置审计字段
                AuditHelper.set_audit_fields(chat_history, current_user.id)
                
                db.add(chat_history)
                db.commit()
                
                return True
                
        except Exception as e:
            ui.notify(f'保存聊天记录失败: {str(e)}', type='negative')
            return False
    #endregion 新建会话相关逻辑
    
    #region 历史记录相关逻辑
    def load_chat_histories(self):
        """从数据库加载聊天历史列表"""
        try:
            from auth import auth_manager
            from database_models.business_models.chat_history_model import ChatHistory
            from auth.database import get_db
            
            current_user = auth_manager.current_user
            if not current_user:
                return []
            
            with get_db() as db:
                chat_histories = ChatHistory.get_user_recent_chats(
                    db_session=db, 
                    user_id=current_user.id, 
                    limit=20
                )
                
                # 转换为UI需要的数据结构
                history_list = []
                for chat in chat_histories:
                    preview = chat.get_message_preview(30)
                    duration_info = chat.get_duration_info()
                    
                    history_list.append({
                        'id': chat.id,
                        'title': chat.title,
                        'preview': preview,
                        'created_at': chat.created_at.strftime('%Y-%m-%d %H:%M'),
                        'updated_at': chat.updated_at.strftime('%Y-%m-%d %H:%M'),
                        'last_message_at': chat.last_message_at.strftime('%Y-%m-%d %H:%M') if chat.last_message_at else None,
                        'message_count': chat.message_count,
                        'model_name': chat.model_name,
                        'duration_minutes': duration_info['duration_minutes'],
                        'chat_object': chat
                    })
                return history_list        
        except Exception as e:
            ui.notify('加载聊天历史失败', type='negative')
            return []
        
    async def on_load_chat_history(self, chat_id):
        """加载指定的聊天历史到当前对话中"""
        # 设置当前加载的聊天ID，用于后续更新判断
        self.set_current_loaded_chat_id(chat_id)
        # 调用聊天区域管理器渲染聊天历史
        await self.chat_area_manager.render_chat_history(chat_id)
    
    def on_edit_chat_history(self, chat_id):
        """编辑聊天历史记录"""
        def save_title():
            try:
                from auth import auth_manager
                from database_models.business_models.chat_history_model import ChatHistory
                from auth.database import get_db
                
                current_user = auth_manager.current_user
                if not current_user:
                    ui.notify('用户未登录', type='warning')
                    return
                
                new_title = title_input.value.strip()
                if not new_title:
                    ui.notify('标题不能为空', type='warning')
                    return
                
                with get_db() as db:
                    chat_history = db.query(ChatHistory).filter(
                        ChatHistory.id == chat_id,
                        ChatHistory.created_by == current_user.id,
                        ChatHistory.is_deleted == False
                    ).first()
                    
                    if chat_history:
                        chat_history.title = new_title
                        chat_history.updated_at = datetime.now()
                        db.commit()
                        
                        # 刷新历史记录列表
                        self.refresh_chat_history_list()
                        ui.notify('标题修改成功', type='positive')
                        dialog.close()
                    else:
                        ui.notify('聊天记录不存在', type='negative')
                        
            except Exception as e:
                ui.notify(f'修改失败: {str(e)}', type='negative')
        
        # 获取当前标题
        try:
            from auth import auth_manager
            from database_models.business_models.chat_history_model import ChatHistory
            from auth.database import get_db
            
            current_user = auth_manager.current_user
            if not current_user:
                ui.notify('用户未登录', type='warning')
                return
            
            with get_db() as db:
                chat_history = db.query(ChatHistory).filter(
                    ChatHistory.id == chat_id,
                    ChatHistory.created_by == current_user.id,
                    ChatHistory.is_deleted == False
                ).first()
                
                if not chat_history:
                    ui.notify('聊天记录不存在', type='negative')
                    return
                
                current_title = chat_history.title
        except Exception as e:
            ui.notify('获取聊天记录失败', type='negative')
            return
        
        # 显示编辑对话框
        with ui.dialog() as dialog:
            with ui.card().classes('w-96'):
                with ui.column().classes('w-full gap-4'):
                    ui.label('编辑聊天标题').classes('text-lg font-medium')
                    title_input = ui.input('聊天标题', value=current_title).classes('w-full')
                    
                    with ui.row().classes('w-full justify-end gap-2'):
                        ui.button('取消', on_click=dialog.close).props('flat')
                        ui.button('保存', on_click=save_title).props('color=primary')
        
        dialog.open()
    
    def on_delete_chat_history(self, chat_id):
        """删除聊天历史记录"""
        def confirm_delete():
            try:
                from auth import auth_manager
                from database_models.business_models.chat_history_model import ChatHistory
                from auth.database import get_db
                
                current_user = auth_manager.current_user
                if not current_user:
                    ui.notify('用户未登录，无法删除聊天记录', type='warning')
                    return
                
                with get_db() as db:
                    chat_history = db.query(ChatHistory).filter(
                        ChatHistory.id == chat_id,
                        ChatHistory.created_by == current_user.id,
                        ChatHistory.is_deleted == False
                    ).first()
                    
                    if not chat_history:
                        ui.notify('聊天记录不存在或无权限删除', type='negative')
                        return
                    
                    chat_title = chat_history.title
                    
                    # 软删除操作
                    chat_history.is_deleted = True
                    chat_history.deleted_at = datetime.now()
                    chat_history.deleted_by = current_user.id
                    chat_history.is_active = False
                    
                    db.commit()
                    
                    # 如果删除的是当前加载的聊天，需要重置界面
                    current_loaded_id = self.get_current_loaded_chat_id()
                    if current_loaded_id == chat_id:
                        self.chat_data_state.current_chat_messages.clear()
                        self.chat_area_manager.restore_welcome_message()
                        self.reset_current_loaded_chat_id()
                        
                    # 刷新聊天历史列表
                    self.refresh_chat_history_list()
                    
                    ui.notify(f'已删除聊天: {chat_title}', type='positive')
                    
            except Exception as e:
                ui.notify(f'删除聊天失败: {str(e)}', type='negative')
        
        # 显示确认对话框
        with ui.dialog() as dialog:
            with ui.card().classes('w-80'):
                with ui.column().classes('w-full'):
                    ui.icon('warning', size='lg').classes('text-orange-500 mx-auto')
                    ui.label('确认删除聊天记录？').classes('text-lg font-medium text-center')
                    ui.label('删除后可以在回收站中恢复').classes('text-sm text-gray-600 text-center')
                    
                    with ui.row().classes('w-full justify-end gap-2'):
                        ui.button('取消', on_click=dialog.close).props('flat')
                        ui.button('删除', on_click=lambda: [confirm_delete(), dialog.close()]).props('color=negative')
        
        dialog.open()
    
    def create_chat_history_list(self):
        """创建聊天历史列表组件"""
        chat_histories = self.load_chat_histories()
        
        if not chat_histories:
            with ui.column().classes('w-full text-center'):
                ui.icon('chat_bubble_outline', size='lg').classes('text-gray-400 mb-2')
                ui.label('暂无聊天记录').classes('text-gray-500 text-sm')
            return
        
        with ui.list().classes('w-full').props('dense separator'):
            for history in chat_histories:
                with ui.item(on_click=lambda chat_id=history['id']: self.on_load_chat_history(chat_id)).classes('cursor-pointer'):
                    with ui.item_section():
                        ui.item_label(history['title']).classes('font-medium')
                        info_text = f"{history['updated_at']} • {history['message_count']}条消息"
                        if history['duration_minutes'] > 0:
                            info_text += f" • {history['duration_minutes']}分钟"
                        if history['model_name']:
                            info_text += f" • {history['model_name']}"
                        ui.item_label(info_text).props('caption').classes('text-xs')
                    
                    with ui.item_section().props('side'):
                        with ui.row().classes('gap-1'):
                            ui.button(
                                icon='edit'
                            ).on('click.stop', lambda chat_id=history['id']: self.on_edit_chat_history(chat_id)).props('dense flat round size="sm"').classes('text-blue-600').tooltip('编辑')
                            
                            ui.button(
                                icon='delete'
                            ).on('click.stop', lambda chat_id=history['id']: self.on_delete_chat_history(chat_id)).props('dense flat round size="sm"').classes('text-red-600').tooltip('删除')
        
    def refresh_chat_history_list(self):
        """刷新聊天历史列表"""
        try:
            if self.history_list_container:
                self.history_list_container.clear()
                with self.history_list_container:
                    self.create_chat_history_list()
                ui.notify('聊天历史已刷新', type='positive')
        except Exception as e:
            ui.notify('刷新失败', type='negative')
    #endregion 历史记录相关逻辑
    
    def render_ui(self):
        """渲染侧边栏UI"""
        visibility_style = 'display: none;' if not self.sidebar_visible else ''
        with ui.column().classes('chat-archive-sidebar h-full').style(
            f'width: 280px; min-width: 280px; {visibility_style}'
        ):
            # 侧边栏标题
            with ui.row().classes('w-full'):
                ui.icon('menu', size='md').classes('text-gray-600')
                ui.label('功能菜单').classes('text-lg font-semibold')
            
            # 侧边栏内容
            with ui.column().classes('w-full items-center'):
                # 新建对话按钮
                ui.button(
                    '新建对话', 
                    icon='add', 
                    on_click=self.on_create_new_chat
                ).classes('w-64').props('outlined rounded').tooltip('创建新聊天/保存当前聊天')
                        
                # 选择模型expansion组件
                with ui.expansion('选择模型', icon='view_in_ar').classes('w-full').tooltip('选择大语言模型'):
                    with ui.column().classes('w-full'):
                        # 配置管理按钮行
                        with ui.row().classes('w-full'):
                            ui.button(
                                '刷新配置', 
                                icon='refresh',
                                on_click=self.on_refresh_model_config
                            ).classes('text-xs').props('dense flat color="primary"').style('min-width: 80px;')
                        
                        # 模型选择下拉框
                        self.chat_data_state.current_state.model_select_widget = ui.select(
                            options=self.chat_data_state.current_state.model_options,
                            value=self.chat_data_state.current_state.default_model,
                            with_input=True,
                            on_change=self.on_model_change
                        ).classes('w-full').props('autofocus dense')

                # 上下文模板expansion组件
                with ui.expansion('上下文模板', icon='pattern').classes('w-full').tooltip('选择上下文模型'):
                    with ui.column().classes('w-full'):
                        # 配置管理按钮行
                        with ui.row().classes('w-full'):
                            ui.button(
                                '刷新配置', 
                                icon='refresh',
                                on_click=self.on_refresh_prompt_config
                            ).classes('text-xs').props('dense flat color="primary"').style('min-width: 80px;')
                        
                        # 提示词选择下拉框
                        self.chat_data_state.current_state.prompt_select_widget = ui.select(
                            options=self.chat_data_state.prompt_options, 
                            value=self.chat_data_state.default_prompt, 
                            with_input=True,
                            on_change=self.on_prompt_change
                        ).classes('w-full').props('autofocus dense')

                # 🔥 提示数据 - 只使用textarea
                with ui.expansion('提示数据', icon='tips_and_updates').classes('w-full').tooltip('输入提示数据'):
                    with ui.column().classes('w-full chathistorylist-hide-scrollbar').style('flex-grow: 1;'):
                        self.switch = ui.switch('启用', value=False).bind_value(self.chat_data_state, 'switch')
                        
                        # 渲染textarea输入
                        self._render_textarea_input()
                    
                # 聊天历史expansion组件
                with ui.expansion('历史消息', icon='history').classes('w-full').tooltip('操作历史聊天内容'):
                    with ui.column().classes('w-full'):
                        # 添加刷新按钮
                        with ui.row().classes('w-full'):
                            ui.button(
                                '刷新历史', 
                                icon='refresh',
                                on_click=self.refresh_chat_history_list
                            ).classes('text-xs').props('dense flat color="primary"').style('min-width: 80px;')
                        
                        # 聊天历史列表容器
                        self.history_list_container = ui.column().classes('w-full h-96 chathistorylist-hide-scrollbar')
                        with self.history_list_container:
                            self.create_chat_history_list()
```

- **webproduct_ui_template\component\chat\config.py**
```python
"""
LLM模型配置管理器
读取YAML配置文件，为chat_component提供模型选择数据
"""
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional

# LLMModelConfigManager类读取配置文件llm_model_config.yaml
class LLMModelConfigManager:
    """LLM模型配置管理器"""
    
    def __init__(self, config_file_path: Optional[str] = None):
        """
        初始化配置管理器
        
        Args:
            config_file_path: YAML配置文件路径，如果为None则使用默认路径
        """
        if config_file_path is None:
            # 默认配置文件路径：项目根目录的 config/yaml/llm_model_config.yaml
            current_dir = Path(__file__).parent
            project_root = current_dir.parent.parent  # 向上两级到项目根目录
            self.config_file_path = project_root / "config" / "yaml" / "llm_model_config.yaml"
        else:
            self.config_file_path = Path(config_file_path)
        
        self._yaml_config = None
        self._model_options = []
        self._load_config()
    
    def _load_config(self) -> None:
        """从YAML文件加载配置"""
        try:
            if not self.config_file_path.exists():
                raise FileNotFoundError(f"LLM模型配置文件不存在: {self.config_file_path}")
            
            with open(self.config_file_path, 'r', encoding='utf-8') as file:
                self._yaml_config = yaml.safe_load(file)
            
            if not self._yaml_config:
                raise ValueError("配置文件为空或格式无效")
            
            # 解析配置并生成模型选项
            self._parse_model_config()
                
        except Exception as e:
            print(f"错误: 无法加载LLM配置文件: {e}")
            print("请确保配置文件存在且格式正确")
            self._yaml_config = None
            self._model_options = []
    
    def _parse_model_config(self) -> None:
        """解析YAML配置，生成模型选项列表"""
        self._model_options = []
        
        # 遍历所有提供商的配置
        for provider_key, provider_config in self._yaml_config.items():
            # 跳过非模型配置节点
            if provider_key in ['defaults', 'metadata']:
                continue
            
            if isinstance(provider_config, dict):
                # 遍历该提供商下的所有模型
                for model_key, model_config in provider_config.items():
                    if isinstance(model_config, dict):
                        # 检查模型是否启用
                        if model_config.get('enabled', True):
                            option = {
                                'key': model_key,
                                'label': model_config.get('name', model_key),
                                'value': model_key,
                                'config': model_config,
                                'provider': provider_key,
                                'description': model_config.get('description', '')
                            }
                            self._model_options.append(option)
    
    def get_model_options_for_select(self, include_disabled: bool = False) -> List[str]:
        """
        获取用于ui.select的模型选项
        
        Args:
            include_disabled: 是否包含禁用的模型，默认为False
        
        Returns:
            List[str]: 模型key列表
        """
        if include_disabled:
            return [option['key'] for option in self._model_options]
        return [option['key'] for option in self._model_options 
                if option['config'].get('enabled', True)]

    def get_model_config(self, model_key: str) -> Optional[Dict[str, Any]]:
        """
        根据模型key获取配置
        
        Args:
            model_key: 模型标识符
            
        Returns:
            Dict[str, Any]: 模型的完整配置信息，如果未找到则返回None
        """
        for option in self._model_options:
            if option['key'] == model_key:
                return option['config']
        return None
    
    def get_default_model(self) -> Optional[str]:
        """
        获取默认模型key（第一个启用的模型）
        
        Returns:
            str: 默认模型key，如果没有启用的模型则返回None
        """
        enabled_models = [opt for opt in self._model_options 
                         if opt['config'].get('enabled', True)]
        return enabled_models[0]['key'] if enabled_models else None
    
    def reload_config(self) -> bool:
        """
        重新加载配置文件
        
        Returns:
            bool: 重新加载是否成功
        """
        try:
            old_model_count = len(self._model_options)
            
            # 重新加载配置
            self._yaml_config = None
            self._model_options = []
            self._load_config()
            
            new_model_count = len(self._model_options)
            
            print(f"配置重新加载完成: {old_model_count} -> {new_model_count} 个模型")
            return True
            
        except Exception as e:
            print(f"配置重新加载失败: {e}")
            return False
    
    def get_config_info(self) -> Dict[str, Any]:
        """
        获取配置文件信息
        
        Returns:
            Dict: 配置文件信息
        """
        return {
            'config_file_path': str(self.config_file_path),
            'file_exists': self.config_file_path.exists(),
            'total_models': len(self._model_options),
            'enabled_models': len([opt for opt in self._model_options 
                                 if opt['config'].get('enabled', True)]),
            'providers': list(set(option['provider'] for option in self._model_options)),
            'last_modified': self.config_file_path.stat().st_mtime if self.config_file_path.exists() else None
        }

# LLMModelConfigManager 全局配置管理器实例
_config_manager = None

def get_llm_config_manager() -> LLMModelConfigManager:
    """
    获取全局LLM配置管理器实例（单例模式）
    
    Returns:
        LLMModelConfigManager: 配置管理器实例
    """
    global _config_manager
    if _config_manager is None:
        _config_manager = LLMModelConfigManager()
    return _config_manager

def get_model_options_for_select(include_disabled: bool = False) -> List[str]:
    """
    获取用于ui.select的模型选项的便捷函数
    
    Args:
        include_disabled: 是否包含禁用的模型，默认为False
    
    Returns:
        List[str]: 模型key列表
    """
    return get_llm_config_manager().get_model_options_for_select(include_disabled)

def get_model_config(model_key: str) -> Optional[Dict[str, Any]]:
    """
    根据模型key获取配置的便捷函数
    
    Args:
        model_key: 模型标识符
        
    Returns:
        Dict[str, Any]: 模型配置信息
    """
    return get_llm_config_manager().get_model_config(model_key)

def get_default_model() -> Optional[str]:
    """
    获取默认模型key的便捷函数
    
    Returns:
        str: 默认模型key
    """
    return get_llm_config_manager().get_default_model()

def reload_llm_config() -> bool:
    """
    重新加载LLM配置的便捷函数
    
    Returns:
        bool: 重新加载是否成功
    """
    return get_llm_config_manager().reload_config()

def get_model_config_info() -> Dict[str, Any]:
    """
    获取配置信息的便捷函数
    
    Returns:
        Dict: 配置文件信息
    """
    return get_llm_config_manager().get_config_info()

# SystemPromptConfigManager类读取配置文件system_prompt_config.yaml
class SystemPromptConfigManager:
    """系统提示词配置管理器"""
    def __init__(self, config_file_path: Optional[str] = None):
        """
        初始化配置管理器
        
        Args:
            config_file_path: YAML配置文件路径，如果为None则使用默认路径
        """
        if config_file_path is None:
            # 默认配置文件路径：项目根目录的 config/yaml/system_prompt_config.yaml
            current_dir = Path(__file__).parent
            project_root = current_dir.parent.parent  # 向上两级到项目根目录
            self.config_file_path = project_root / "config" / "yaml" / "system_prompt_config.yaml"
        else:
            self.config_file_path = Path(config_file_path)
        
        self._yaml_config = None
        self._prompt_options = []
        self._load_config()

    def _load_config(self) -> None:
        """从YAML文件加载配置"""
        try:
            if not self.config_file_path.exists():
                raise FileNotFoundError(f"系统提示词配置文件不存在: {self.config_file_path}")
            
            with open(self.config_file_path, 'r', encoding='utf-8') as file:
                self._yaml_config = yaml.safe_load(file)
            
            if not self._yaml_config:
                raise ValueError("配置文件为空或格式无效")
            
            # 解析配置并生成提示词选项
            self._parse_prompt_config()
                
        except Exception as e:
            print(f"错误: 无法加载系统提示词配置文件: {e}")
            print("请确保配置文件存在且格式正确")
            self._yaml_config = None
            self._prompt_options = []

    def _parse_prompt_config(self) -> None:
        """解析YAML配置，生成提示词选项列表"""
        self._prompt_options = []
        
        # 检查是否存在 prompt_templates 节点
        prompt_templates = self._yaml_config.get('prompt_templates', {})
        
        if not prompt_templates:
            print("警告: 配置文件中未找到 'prompt_templates' 节点")
            return
        
        # 遍历所有提示词模板的配置
        for template_key, template_config in prompt_templates.items():
            # 跳过非字典类型的配置节点
            if not isinstance(template_config, dict):
                continue
            
            # 提取配置信息
            enabled = template_config.get('enabled', True)
            name = template_config.get('name', template_key)
            system_prompt = template_config.get('system_prompt', '')
            examples = template_config.get('examples', {})
            
            # 构建提示词选项
            prompt_option = {
                'key': template_key,
                'name': name,
                'enabled': enabled,
                'system_prompt': system_prompt,
                'examples': examples,
                'config': template_config
            }
            self._prompt_options.append(prompt_option)
        
        # print(f"已加载 {len(self._prompt_options)} 个系统提示词模板")

    def get_prompt_options_for_select(self, include_disabled: bool = False) -> List[str]:
        """
        获取用于ui.select的提示词选项列表
        
        Args:
            include_disabled: 是否包含禁用的提示词，默认为False
        
        Returns:
            List[str]: 提示词key列表
        """
        if include_disabled:
            return [option['key'] for option in self._prompt_options]
        else:
            return [option['key'] for option in self._prompt_options 
                   if option.get('enabled', True)]

    def get_prompt_config(self, prompt_key: str) -> Optional[Dict[str, Any]]:
        """
        根据提示词key获取完整配置信息
        
        Args:
            prompt_key: 提示词标识符
            
        Returns:
            Dict[str, Any]: 提示词配置信息，如果不存在则返回None
        """
        for option in self._prompt_options:
            if option['key'] == prompt_key:
                return option
        return None

    def get_system_prompt(self, prompt_key: str) -> Optional[str]:
        """
        获取系统提示词内容
        
        Args:
            prompt_key: 提示词标识符
            
        Returns:
            str: 系统提示词内容，如果不存在则返回None
        """
        config = self.get_prompt_config(prompt_key)
        return config.get('system_prompt') if config else None

    def get_examples(self, prompt_key: str) -> Optional[Dict[str, Any]]:
        """
        获取示例内容
        
        Args:
            prompt_key: 提示词标识符
            
        Returns:
            Dict: 示例内容，如果不存在则返回None
        """
        config = self.get_prompt_config(prompt_key)
        return config.get('examples') if config else None

    def get_default_prompt(self) -> Optional[str]:
        """
        获取默认提示词key
        
        Returns:
            str: 默认提示词key，如果没有启用的提示词则返回None
        """
        enabled_prompts = [opt for opt in self._prompt_options 
                         if opt.get('enabled', True)]
        return enabled_prompts[0]['key'] if enabled_prompts else None

    def reload_config(self) -> bool:
        """
        重新加载配置文件
        
        Returns:
            bool: 重新加载是否成功
        """
        try:
            old_prompt_count = len(self._prompt_options)
            
            # 重新加载配置
            self._yaml_config = None
            self._prompt_options = []
            self._load_config()
            
            new_prompt_count = len(self._prompt_options)
            
            print(f"配置重新加载完成: {old_prompt_count} -> {new_prompt_count} 个提示词模板")
            return True
            
        except Exception as e:
            print(f"配置重新加载失败: {e}")
            return False

    def get_config_info(self) -> Dict[str, Any]:
        """
        获取配置文件信息
        
        Returns:
            Dict: 配置文件信息
        """
        return {
            'config_file_path': str(self.config_file_path),
            'file_exists': self.config_file_path.exists(),
            'total_prompts': len(self._prompt_options),
            'enabled_prompts': len([opt for opt in self._prompt_options 
                                  if opt.get('enabled', True)]),
            'last_modified': self.config_file_path.stat().st_mtime if self.config_file_path.exists() else None
        }

# SystemPromptConfigManager 全局配置管理器实例
_prompt_config_manager = None

def get_system_prompt_manager() -> SystemPromptConfigManager:
    """
    获取全局系统提示词配置管理器实例（单例模式）
    
    Returns:
        SystemPromptConfigManager: 配置管理器实例
    """
    global _prompt_config_manager
    if _prompt_config_manager is None:
        _prompt_config_manager = SystemPromptConfigManager()
    return _prompt_config_manager

def get_prompt_options_for_select(include_disabled: bool = False) -> List[str]:
    """
    获取用于ui.select的提示词选项的便捷函数
    
    Args:
        include_disabled: 是否包含禁用的提示词，默认为False
    
    Returns:
        List[str]: 提示词key列表
    """
    return get_system_prompt_manager().get_prompt_options_for_select(include_disabled)

def get_prompt_config(prompt_key: str) -> Optional[Dict[str, Any]]:
    """
    根据提示词key获取配置的便捷函数
    
    Args:
        prompt_key: 提示词标识符
        
    Returns:
        Dict[str, Any]: 提示词配置信息
    """
    return get_system_prompt_manager().get_prompt_config(prompt_key)

def get_system_prompt(prompt_key: str) -> Optional[str]:
    """
    获取系统提示词内容的便捷函数
    
    Args:
        prompt_key: 提示词标识符
        
    Returns:
        str: 系统提示词内容
    """
    return get_system_prompt_manager().get_system_prompt(prompt_key)

def get_examples(prompt_key: str) -> Optional[Dict[str, Any]]:
    """
    获取示例内容的便捷函数
    
    Args:
        prompt_key: 提示词标识符
        
    Returns:
        Dict: 示例内容
    """
    return get_system_prompt_manager().get_examples(prompt_key)

def get_default_prompt() -> Optional[str]:
    """
    获取默认提示词key的便捷函数
    
    Returns:
        str: 默认提示词key
    """
    return get_system_prompt_manager().get_default_prompt()

def reload_prompt_config() -> bool:
    """
    重新加载系统提示词配置的便捷函数
    
    Returns:
        bool: 重新加载是否成功
    """
    return get_system_prompt_manager().reload_config()

def get_prompt_config_info() -> Dict[str, Any]:
    """
    获取配置信息的便捷函数
    
    Returns:
        Dict: 配置文件信息
    """
    return get_system_prompt_manager().get_config_info()
```

- **webproduct_ui_template\component\chat\markdown_ui_parser.py**
````python
import re
import asyncio
from typing import Optional, List, Dict, Any
from nicegui import ui
import io
import json
import csv

class MarkdownUIParser:
    """
    Markdown 内容解析器和 UI 组件映射器
    负责将 Markdown 内容解析为结构化块，并将其映射为相应的UI组件
    """
    
    def __init__(self):
        """初始化解析器"""
        pass
    
    # ==================== 主要接口方法 ====================
    async def optimize_content_display(self, reply_label, content: str, chat_content_container=None):
        """
        优化内容显示 - 将特殊内容转换为专业UI组件 
        Args:
            reply_label: 当前的markdown组件引用
            content: 完整的AI回复内容
            chat_content_container: 聊天内容容器引用
        """
        try:
            # 1. 解析内容，检测特殊块
            parsed_blocks = self.parse_content_with_regex(content)
            
            # 2. 判断是否需要优化
            if self.has_special_content(parsed_blocks):
                # 3. 显示优化提示
                self.show_optimization_hint(reply_label)
                
                # 4. 短暂延迟，让用户看到提示
                await asyncio.sleep(0.1)
                
                # 5. 获取正确的容器
                container = chat_content_container if chat_content_container else reply_label
                
                # 6. 重新渲染混合组件
                await self.render_optimized_content(container, parsed_blocks)
            
        except Exception as e:
            ui.notify(f"内容优化失败，保持原始显示: {e}")

    def parse_content_with_regex(self, content: str) -> List[Dict[str, Any]]:
        """
        使用正则表达式解析内容为结构化块
        
        Args:
            content: 需要解析的 Markdown 内容
            
        Returns:
            List[Dict]: 解析后的内容块列表
            [{
                'type': 'table|mermaid|code|heading|math|text',
                'content': '原始内容',
                'data': '解析后的数据'(可选),
                'start_pos': 开始位置,
                'end_pos': 结束位置
            }]
        """
        blocks = []
        
        # 1. 检测表格
        table_blocks = self.extract_tables(content)
        blocks.extend(table_blocks)
        
        # 2. 检测Mermaid图表
        mermaid_blocks = self.extract_mermaid(content)
        blocks.extend(mermaid_blocks)
        
        # 3. 检测代码块
        code_blocks = self.extract_code_blocks(content)
        blocks.extend(code_blocks)
        
        # 4. 检测LaTeX公式
        math_blocks = self.extract_math(content)
        blocks.extend(math_blocks)
        
        # 5. 检测标题
        heading_blocks = self.extract_headings(content)
        blocks.extend(heading_blocks)
        
        # 6. 按位置排序
        blocks.sort(key=lambda x: x['start_pos'])
        
        # 7. 填充文本块
        text_blocks = self.fill_text_blocks(content, blocks)
        
        # 8. 合并并重新排序
        all_blocks = blocks + text_blocks
        all_blocks.sort(key=lambda x: x['start_pos'])
        
        return all_blocks
    
    # ==================== 内容提取方法 ====================
    
    def extract_tables(self, content: str) -> List[Dict[str, Any]]:
        """提取表格内容"""
        tables = []
        # 匹配markdown表格模式
        pattern = r'(\|.*\|.*\n\|[-\s\|]*\|.*\n(?:\|.*\|.*\n)*)'
        
        for match in re.finditer(pattern, content):
            table_data = self.parse_table_data(match.group(1))
            if table_data:  # 确保解析成功
                tables.append({
                    'type': 'table',
                    'content': match.group(1),
                    'data': table_data,
                    'start_pos': match.start(),
                    'end_pos': match.end()
                })
        
        return tables

    def extract_mermaid(self, content: str) -> List[Dict[str, Any]]:
        """提取Mermaid图表"""
        mermaid_blocks = []
        pattern = r'```mermaid\n(.*?)```'
        
        for match in re.finditer(pattern, content, re.DOTALL):
            mermaid_blocks.append({
                'type': 'mermaid',
                'content': match.group(1).strip(),
                'start_pos': match.start(),
                'end_pos': match.end()
            })
    
        return mermaid_blocks

    def extract_code_blocks(self, content: str) -> List[Dict[str, Any]]:
        """提取代码块（排除mermaid）"""
        code_blocks = []
        pattern = r'```(\w+)?\n(.*?)```'
        
        for match in re.finditer(pattern, content, re.DOTALL):
            language = match.group(1) or 'text'
            if language.lower() != 'mermaid':  # 排除mermaid
                code_blocks.append({
                    'type': 'code',
                    'content': match.group(2).strip(),
                    'language': language,
                    'start_pos': match.start(),
                    'end_pos': match.end()
                })
        
        return code_blocks

    def extract_math(self, content: str) -> List[Dict[str, Any]]:
        """提取LaTeX数学公式"""
        math_blocks = []
        
        # 块级公式 $$...$$
        block_pattern = r'\$\$(.*?)\$\$'
        for match in re.finditer(block_pattern, content, re.DOTALL):
            math_blocks.append({
                'type': 'math',
                'content': match.group(1).strip(),
                'display_mode': 'block',
                'start_pos': match.start(),
                'end_pos': match.end()
            })
        
        # 行内公式 $...$
        inline_pattern = r'(?<!\$)\$([^\$\n]+)\$(?!\$)'
        for match in re.finditer(inline_pattern, content):
            math_blocks.append({
                'type': 'math',
                'content': match.group(1).strip(),
                'display_mode': 'inline',
                'start_pos': match.start(),
                'end_pos': match.end()
            })
        
        return math_blocks

    def extract_headings(self, content: str) -> List[Dict[str, Any]]:
        """提取标题"""
        headings = []
        pattern = r'^(#{1,6})\s+(.+)$'
        
        for match in re.finditer(pattern, content, re.MULTILINE):
            level = len(match.group(1))
            text = match.group(2).strip()
            headings.append({
                'type': 'heading',
                'content': text,
                'level': level,
                'start_pos': match.start(),
                'end_pos': match.end()
            })
        
        return headings

    def fill_text_blocks(self, content: str, special_blocks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """填充普通文本块"""
        if not special_blocks:
            return [{
                'type': 'text',
                'content': content,
                'start_pos': 0,
                'end_pos': len(content)
            }]
        
        text_blocks = []
        last_end = 0
        
        for block in special_blocks:
            if block['start_pos'] > last_end:
                text_content = content[last_end:block['start_pos']].strip()
                if text_content:
                    text_blocks.append({
                        'type': 'text',
                        'content': text_content,
                        'start_pos': last_end,
                        'end_pos': block['start_pos']
                    })
            last_end = block['end_pos']
        
        # 添加最后的文本内容
        if last_end < len(content):
            text_content = content[last_end:].strip()
            if text_content:
                text_blocks.append({
                    'type': 'text',
                    'content': text_content,
                    'start_pos': last_end,
                    'end_pos': len(content)
                })
        
        return text_blocks
    
    # ==================== 数据解析方法 ====================
    
    def parse_table_data(self, table_text: str) -> Optional[Dict[str, Any]]:
        """解析表格数据为NiceGUI table格式"""
        try:
            lines = [line.strip() for line in table_text.strip().split('\n') if line.strip()]
            if len(lines) < 3:  # 至少需要header、separator、data
                return None
            
            # 解析表头
            headers = [cell.strip() for cell in lines[0].split('|')[1:-1]]
            if not headers:
                return None
            
            # 解析数据行（跳过分隔行）
            rows = []
            for line in lines[2:]:
                cells = [cell.strip() for cell in line.split('|')[1:-1]]
                if len(cells) == len(headers):
                    row_data = dict(zip(headers, cells))
                    rows.append(row_data)
            
            return {
                'columns': [{'name': col, 'label': col, 'field': col} for col in headers],
                'rows': rows
            }
        
        except Exception as e:
            ui.notify(f"表格解析失败: {e}")
            return None
    
    # ==================== 检测和渲染方法 ====================
    
    def has_special_content(self, blocks: List[Dict[str, Any]]) -> bool:
        """检查是否包含需要优化的特殊内容"""
        special_types = {'table', 'mermaid', 'code', 'math', 'heading'}
        return any(block['type'] in special_types for block in blocks)

    def show_optimization_hint(self, reply_label):
        """显示优化提示"""
        try:
            reply_label.set_content("🔄 正在优化内容显示...")
        except:
            pass  # 如果设置失败，忽略错误

    async def render_optimized_content(self, container, blocks: List[Dict[str, Any]]):
        """渲染优化后的混合内容"""
        container.clear()
        
        with container:
            for block in blocks:
                try:
                    if block['type'] == 'table':
                        self.create_table_component(block['data'])
                    elif block['type'] == 'mermaid':
                        self.create_mermaid_component(block['content'])
                    elif block['type'] == 'code':
                        self.create_code_component(block['content'], block['language'])
                    elif block['type'] == 'math':
                        self.create_math_component(block['content'], block['display_mode'])
                    elif block['type'] == 'heading':
                        self.create_heading_component(block['content'], block['level'])
                    elif block['type'] == 'text':
                        self.create_text_component(block['content'])
                    else:
                        # 兜底：用markdown显示
                        ui.markdown(block['content']).classes('w-full')
                except Exception as e:
                    # 错误兜底：显示为代码块
                    ui.markdown(f"```\n{block['content']}\n```").classes('w-full')
    
    # ==================== UI组件创建方法 ====================
    
    def create_table_component(self, table_data: Dict[str, Any]):
        """创建表格组件"""
        if table_data and 'columns' in table_data and 'rows' in table_data:
            
            # 创建容器来包含表格和下载按钮
            with ui.card().classes('w-full relative bg-[#81c784]'):
                # 下载按钮 - 绝对定位在右上角
                with ui.row().classes('absolute top-2 right-2 z-10'):
                    ui.button(
                        # '下载', 
                        icon='download',
                        on_click=lambda: self.download_table_data(table_data)
                    ).classes('bg-blue-500 hover:bg-blue-600 text-white').props('flat round size=sm').tooltip('下载')     
                    # 表格组件
                ui.table(
                    columns=table_data['columns'],
                    rows=table_data['rows'],
                    column_defaults={
                        'align': 'left',
                        'headerClasses': 'uppercase text-primary',
                    },
                    pagination=5
                ).classes('w-full bg-[#81c784] text-gray-800')

    def download_table_data(self,table_data: Dict[str, Any]):
        """下载表格数据为CSV文件"""
        if not table_data or 'columns' not in table_data or 'rows' not in table_data:
            ui.notify('没有可下载的数据', type='warning')
            return
        try:
            # 创建CSV内容
            output = io.StringIO()
            writer = csv.writer(output)
            
            # 写入表头
            headers = [col['label'] if isinstance(col, dict) else col for col in table_data['columns']]
            writer.writerow(headers)
            
            # 写入数据行
            for row in table_data['rows']:
                if isinstance(row, dict):
                    # 如果行是字典，按列的顺序提取值
                    row_values = []
                    for col in table_data['columns']:
                        col_name = col['name'] if isinstance(col, dict) else col
                        row_values.append(row.get(col_name, ''))
                    writer.writerow(row_values)
                else:
                    # 如果行是列表，直接写入
                    writer.writerow(row)
            # 获取CSV内容
            csv_content = output.getvalue()
            output.close()
            
            # 触发下载
            ui.download(csv_content.encode('utf-8-sig'), 'table_data.csv')
            ui.notify('文件下载成功', type='positive')
        except Exception as e:
            ui.notify(f'下载失败: {str(e)}', type='negative')

    def create_mermaid_component(self, mermaid_content: str):
        """创建Mermaid图表组件"""
        try:
            # 创建容器，使用相对定位
            with ui.row().classes('w-full relative bg-[#81c784]'):
                # 右上角全屏按钮
                with ui.row().classes('absolute top-2 right-2 z-10'):
                    ui.button(
                        icon='fullscreen', 
                        on_click=lambda: self.show_fullscreen_mermaid_enhanced(mermaid_content)
                    ).props('flat round size=sm').classes('bg-blue-500 hover:bg-blue-600 text-white').tooltip('全屏显示') 
                # Mermaid图表
                ui.mermaid(mermaid_content).classes('w-full')     
        except Exception as e:
            ui.notify(f"流程图渲染失败: {e}", type="info")
            # 错误情况下也保持相同的布局结构
            ui.code(mermaid_content, language='mermaid').classes('w-full')

    def show_fullscreen_mermaid_enhanced(self, mermaid_content: str):
        """增强版全屏显示Mermaid图表"""
        
        mermaid_id = 'neo_container'
        
        def close_dialog():
            dialog.close()

        def export_image():
            """导出Mermaid图表为PNG图片"""
            try:
                # JavaScript代码：使用多种方法导出SVG
                js_code = f"""
                async function exportMermaidImage() {{
                    try {{
                        // 查找mermaid容器
                        const mermaidContainer = document.getElementById('{mermaid_id}');
                        if (!mermaidContainer) {{
                            console.error('未找到Mermaid容器');
                            return false;
                        }}
                        
                        // 查找SVG元素
                        const svgElement = mermaidContainer.querySelector('svg');
                        if (!svgElement) {{
                            console.error('未找到SVG元素');
                            return false;
                        }}
                        
                        // 克隆SVG元素以避免修改原始元素
                        const clonedSvg = svgElement.cloneNode(true);
                        
                        // 获取SVG的实际尺寸
                        const bbox = svgElement.getBBox();
                        const width = Math.max(bbox.width, svgElement.clientWidth, 400);
                        const height = Math.max(bbox.height, svgElement.clientHeight, 300);
                        
                        // 设置克隆SVG的属性
                        clonedSvg.setAttribute('width', width);
                        clonedSvg.setAttribute('height', height);
                        clonedSvg.setAttribute('viewBox', `0 0 ${{width}} ${{height}}`);
                        clonedSvg.setAttribute('xmlns', 'http://www.w3.org/2000/svg');
                        clonedSvg.setAttribute('xmlns:xlink', 'http://www.w3.org/1999/xlink');
                        
                        // 内联样式到SVG中
                        const styleSheets = Array.from(document.styleSheets);
                        let allStyles = '';
                        
                        try {{
                            for (let sheet of styleSheets) {{
                                try {{
                                    const rules = Array.from(sheet.cssRules || sheet.rules || []);
                                    for (let rule of rules) {{
                                        if (rule.type === CSSRule.STYLE_RULE) {{
                                            allStyles += rule.cssText + '\\n';
                                        }}
                                    }}
                                }} catch (e) {{
                                    // 跳过跨域样式表
                                    console.warn('跳过样式表:', e);
                                }}
                            }}
                            
                            if (allStyles) {{
                                const styleElement = document.createElement('style');
                                styleElement.textContent = allStyles;
                                clonedSvg.insertBefore(styleElement, clonedSvg.firstChild);
                            }}
                        }} catch (e) {{
                            console.warn('样式处理失败:', e);
                        }}
                        
                        // 序列化SVG
                        const serializer = new XMLSerializer();
                        let svgString = serializer.serializeToString(clonedSvg);
                        
                        // 方法1：尝试使用html2canvas式的方法
                        try {{
                            return await exportViaCanvas(svgString, width, height);
                        }} catch (canvasError) {{
                            console.warn('Canvas方法失败，尝试直接下载SVG:', canvasError);
                            // 方法2：直接下载SVG文件
                            return exportAsSVG(svgString);
                        }}
                        
                    }} catch (error) {{
                        console.error('导出图片错误:', error);
                        return false;
                    }}
                }}
                
                async function exportViaCanvas(svgString, width, height) {{
                    return new Promise((resolve, reject) => {{
                        // 创建canvas
                        const canvas = document.createElement('canvas');
                        const ctx = canvas.getContext('2d');
                        const scale = 2; // 高分辨率
                        
                        canvas.width = width * scale;
                        canvas.height = height * scale;
                        ctx.scale(scale, scale);
                        
                        // 白色背景
                        ctx.fillStyle = 'white';
                        ctx.fillRect(0, 0, width, height);
                        
                        // 创建Data URL
                        const svgBlob = new Blob([svgString], {{ type: 'image/svg+xml;charset=utf-8' }});
                        const url = URL.createObjectURL(svgBlob);
                        
                        const img = new Image();
                        img.onload = function() {{
                            try {{
                                ctx.drawImage(img, 0, 0, width, height);
                                
                                // 使用getImageData方式避免toBlob的跨域问题
                                try {{
                                    const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
                                    const newCanvas = document.createElement('canvas');
                                    const newCtx = newCanvas.getContext('2d');
                                    newCanvas.width = canvas.width;
                                    newCanvas.height = canvas.height;
                                    newCtx.putImageData(imageData, 0, 0);
                                    
                                    newCanvas.toBlob(function(blob) {{
                                        if (blob) {{
                                            downloadBlob(blob, 'flowchart_' + new Date().getTime() + '.png');
                                            resolve(true);
                                        }} else {{
                                            reject('Blob转换失败');
                                        }}
                                    }}, 'image/png', 1.0);
                                }} catch (e) {{
                                    // 如果还是失败，使用toDataURL
                                    const dataUrl = canvas.toDataURL('image/png', 1.0);
                                    downloadDataUrl(dataUrl, 'flowchart_' + new Date().getTime() + '.png');
                                    resolve(true);
                                }}
                            }} catch (error) {{
                                reject('绘制失败: ' + error.message);
                            }} finally {{
                                URL.revokeObjectURL(url);
                            }}
                        }};
                        
                        img.onerror = function() {{
                            URL.revokeObjectURL(url);
                            reject('图像加载失败');
                        }};
                        
                        img.src = url;
                    }});
                }}
                
                function exportAsSVG(svgString) {{
                    try {{
                        const blob = new Blob([svgString], {{ type: 'image/svg+xml;charset=utf-8' }});
                        downloadBlob(blob, 'flowchart_' + new Date().getTime() + '.svg');
                        return true;
                    }} catch (error) {{
                        console.error('SVG导出失败:', error);
                        return false;
                    }}
                }}
                
                function downloadBlob(blob, filename) {{
                    const url = URL.createObjectURL(blob);
                    const link = document.createElement('a');
                    link.href = url;
                    link.download = filename;
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                    setTimeout(() => URL.revokeObjectURL(url), 100);
                }}
                
                function downloadDataUrl(dataUrl, filename) {{
                    const link = document.createElement('a');
                    link.href = dataUrl;
                    link.download = filename;
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                }}
                
                // 执行导出
                exportMermaidImage().then(result => {{
                    if (result) {{
                        console.log('图片导出成功');
                    }} else {{
                        console.error('图片导出失败');
                    }}
                }}).catch(error => {{
                    console.error('导出过程中出错:', error);
                }});
                """
                
                # 执行JavaScript代码
                ui.run_javascript(js_code)
                
                # 给用户反馈
                ui.notify('正在导出图片...', type='info')
                
            except Exception as e:
                ui.notify(f'导出失败: {str(e)}', type='negative')
                print(f"Export error: {e}")
        
        # 创建全屏对话框
        with ui.dialog().props('maximized transition-show="slide-up" transition-hide="slide-down"') as dialog:
            with ui.card().classes('w-full no-shadow bg-white'):
                # 顶部工具栏
                with ui.row().classes('w-full justify-between items-center p-1 bg-gradient-to-r from-blue-500 to-purple-600 text-white'):
                    with ui.row().classes('items-center gap-3'):
                        ui.icon('account_tree', size='md')
                        ui.label('流程图全屏显示').classes('text-xl font-bold')
                    
                    with ui.row().classes('gap-1'):
                        ui.button(
                            icon='download',
                            on_click=export_image
                        ).props('flat round').classes('text-white hover:bg-white/20').tooltip('导出图片')
                        
                        ui.button(
                            icon='close',
                            on_click=close_dialog
                        ).props('flat round').classes('text-white hover:bg-white/20').tooltip('退出全屏')
                
                # 图表容器
                with ui.scroll_area().classes('flex-1 p-6 bg-gray-50'):
                    try:
                        # 重点：为ui.mermaid组件添加一个ID
                        ui.mermaid(mermaid_content).classes('w-full min-h-96 bg-white rounded-lg shadow-sm p-4').props(f'id="{mermaid_id}"')
                    except Exception as e:
                        ui.notify(f"全屏图表渲染失败: {e}", type="warning")
                        with ui.card().classes('w-full bg-white'):
                            ui.label('图表渲染失败，显示源代码:').classes('font-semibold mb-2 text-red-600')
                            ui.code(mermaid_content, language='mermaid').classes('w-full')
        
        # 添加键盘事件监听（ESC键关闭）
        dialog.on('keydown.esc', close_dialog)
        # 打开对话框
        dialog.open()

    def create_code_component(self, code_content: str, language: str):
        """创建代码组件"""
        ui.code(code_content, language=language).classes('w-full bg-gray-200 dark:bg-zinc-600')

    def create_math_component(self, math_content: str, display_mode: str):
        """创建数学公式组件"""
        if display_mode == 'block':
            ui.markdown(f'$$\n{math_content}\n$$',extras=['latex']).classes('w-full text-center')
        else:
            ui.markdown(f'${math_content}$',extras=['latex']).classes('w-full')

    def create_heading_component(self, text: str, level: int):
        """创建标题组件"""
        # 标题级别映射：向下调整2级
        # # -> ###, ## -> ####, ### -> #####, #### -> ######
        adjusted_level = level + 2
        
        # 限制最大级别为6（markdown支持的最大级别）
        if adjusted_level > 6:
            adjusted_level = 6
        
        # 生成对应级别的markdown标题
        markdown_heading = '#' * adjusted_level + ' ' + text
        
        # 使用ui.markdown渲染，这样可以保持**加粗**等markdown格式
        ui.markdown(markdown_heading).classes('w-full')

    def create_text_component(self, text_content: str):
        """创建文本组件"""
        if text_content.strip():
            ui.markdown(text_content, extras=['tables', 'mermaid', 'latex', 'fenced-code-blocks']).classes('w-full')
    
    # ==================== 便捷方法 ====================
    
    def get_supported_content_types(self) -> List[str]:
        """获取支持的内容类型列表"""
        return ['table', 'mermaid', 'code', 'math', 'heading', 'text']
    
    def is_content_optimizable(self, content: str) -> bool:
        """快速检查内容是否可优化"""
        blocks = self.parse_content_with_regex(content)
        return self.has_special_content(blocks)
````

## webproduct_ui_template\config

- **webproduct_ui_template\config\__init__.py** *(包初始化文件 - 空)*
```python

```

- **webproduct_ui_template\config\env_config.py**
```python
"""
环境变量配置加载器

统一管理从 .env 文件加载环境变量，并提供类型转换和默认值处理。

使用方法:
    from config.env_config import env_config
    
    # 获取字符串配置
    app_title = env_config.get('APP_TITLE', 'Default Title')
    
    # 获取整数配置
    app_port = env_config.get_int('APP_PORT', 8080)
    
    # 获取布尔配置
    app_show = env_config.get_bool('APP_SHOW', True)
    
    # 获取列表配置
    allowed_hosts = env_config.get_list('ALLOWED_HOSTS', ['localhost'])
"""
import os
from pathlib import Path
from typing import Any, Optional, List, Dict
import secrets


class EnvConfig:
    """环境变量配置管理器"""
    
    def __init__(self, env_file: str = '.env'):
        """
        初始化环境变量配置
        
        Args:
            env_file: .env 文件路径（相对于项目根目录）
        """
        self.env_file = env_file
        self.config: Dict[str, str] = {}
        self._load_env_file()
    
    def _get_project_root(self) -> Path:
        """
        获取项目根目录
        
        Returns:
            Path: 项目根目录路径
        """
        # 从当前文件向上查找，直到找到包含 .env 或 requirements.txt 的目录
        current = Path(__file__).resolve().parent
        
        # 向上最多查找5层
        for _ in range(5):
            if (current / '.env').exists() or (current / '.env.example').exists():
                return current
            if (current / 'requirements.txt').exists():
                return current
            if current.parent == current:  # 到达根目录
                break
            current = current.parent
        
        # 如果没找到，返回当前文件的父目录的父目录（假设结构是 project/config/env_config.py）
        return Path(__file__).resolve().parent.parent
    
    def _load_env_file(self):
        """从 .env 文件加载环境变量"""
        project_root = self._get_project_root()
        env_path = project_root / self.env_file
        
        # 如果 .env 不存在，尝试加载 .env.example
        if not env_path.exists():
            env_example_path = project_root / '.env.example'
            if env_example_path.exists():
                print(f"⚠️  .env 文件不存在，使用 .env.example 的默认配置")
                print(f"   建议执行: cp .env.example .env")
                env_path = env_example_path
        
        if not env_path.exists():
            print(f"⚠️  未找到环境变量配置文件: {env_path}")
            print(f"   将使用代码中的默认值")
            return
        
        # 读取并解析 .env 文件
        try:
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    
                    # 跳过空行和注释
                    if not line or line.startswith('#'):
                        continue
                    
                    # 解析 KEY=VALUE 格式
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        
                        # 移除值两端的引号
                        if value.startswith('"') and value.endswith('"'):
                            value = value[1:-1]
                        elif value.startswith("'") and value.endswith("'"):
                            value = value[1:-1]
                        
                        self.config[key] = value
            
            print(f"✅ 已加载环境变量配置: {env_path}")
            print(f"   共加载 {len(self.config)} 个配置项")
        
        except Exception as e:
            print(f"❌ 加载环境变量配置失败: {e}")
    
    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """
        获取字符串配置
        
        优先级: 系统环境变量 > .env 文件 > 默认值
        
        Args:
            key: 配置键名
            default: 默认值
        
        Returns:
            配置值或默认值
        """
        # 1. 优先从系统环境变量获取
        value = os.environ.get(key)
        if value is not None:
            return value
        
        # 2. 从 .env 文件获取
        value = self.config.get(key)
        if value is not None and value != '':
            return value
        
        # 3. 返回默认值
        return default
    
    def get_int(self, key: str, default: int = 0) -> int:
        """
        获取整数配置
        
        Args:
            key: 配置键名
            default: 默认值
        
        Returns:
            整数配置值
        """
        value = self.get(key)
        if value is None:
            return default
        
        try:
            return int(value)
        except ValueError:
            print(f"⚠️  配置 {key}='{value}' 无法转换为整数，使用默认值: {default}")
            return default
    
    def get_float(self, key: str, default: float = 0.0) -> float:
        """
        获取浮点数配置
        
        Args:
            key: 配置键名
            default: 默认值
        
        Returns:
            浮点数配置值
        """
        value = self.get(key)
        if value is None:
            return default
        
        try:
            return float(value)
        except ValueError:
            print(f"⚠️  配置 {key}='{value}' 无法转换为浮点数，使用默认值: {default}")
            return default
    
    def get_bool(self, key: str, default: bool = False) -> bool:
        """
        获取布尔配置
        
        支持的真值: true, yes, 1, on (不区分大小写)
        支持的假值: false, no, 0, off (不区分大小写)
        
        Args:
            key: 配置键名
            default: 默认值
        
        Returns:
            布尔配置值
        """
        value = self.get(key)
        if value is None:
            return default
        
        value_lower = value.lower()
        if value_lower in ('true', 'yes', '1', 'on'):
            return True
        elif value_lower in ('false', 'no', '0', 'off'):
            return False
        else:
            print(f"⚠️  配置 {key}='{value}' 无法转换为布尔值，使用默认值: {default}")
            return default
    
    def get_list(self, key: str, default: Optional[List[str]] = None, 
                 separator: str = ',') -> List[str]:
        """
        获取列表配置
        
        Args:
            key: 配置键名
            default: 默认值
            separator: 分隔符，默认为逗号
        
        Returns:
            列表配置值
        
        示例:
            ALLOWED_HOSTS=localhost,127.0.0.1,example.com
            => ['localhost', '127.0.0.1', 'example.com']
        """
        if default is None:
            default = []
        
        value = self.get(key)
        if value is None:
            return default
        
        # 分割并去除空白
        items = [item.strip() for item in value.split(separator)]
        # 过滤空字符串
        return [item for item in items if item]
    
    def get_dict(self, key: str, default: Optional[Dict[str, str]] = None,
                 item_separator: str = ',', kv_separator: str = ':') -> Dict[str, str]:
        """
        获取字典配置
        
        Args:
            key: 配置键名
            default: 默认值
            item_separator: 项分隔符，默认为逗号
            kv_separator: 键值分隔符，默认为冒号
        
        Returns:
            字典配置值
        
        示例:
            DATABASE_OPTIONS=host:localhost,port:3306,charset:utf8
            => {'host': 'localhost', 'port': '3306', 'charset': 'utf8'}
        """
        if default is None:
            default = {}
        
        value = self.get(key)
        if value is None:
            return default
        
        result = {}
        items = value.split(item_separator)
        
        for item in items:
            item = item.strip()
            if not item:
                continue
            
            if kv_separator in item:
                k, v = item.split(kv_separator, 1)
                result[k.strip()] = v.strip()
        
        return result
    
    def require(self, key: str) -> str:
        """
        获取必需的配置，如果不存在则抛出异常
        
        Args:
            key: 配置键名
        
        Returns:
            配置值
        
        Raises:
            ValueError: 如果配置不存在
        """
        value = self.get(key)
        if value is None:
            raise ValueError(f"必需的环境变量 {key} 未设置")
        return value
    
    def set(self, key: str, value: str):
        """
        设置配置值（仅在内存中，不会写入文件）
        
        Args:
            key: 配置键名
            value: 配置值
        """
        self.config[key] = value
    
    def has(self, key: str) -> bool:
        """
        检查配置是否存在
        
        Args:
            key: 配置键名
        
        Returns:
            是否存在
        """
        return key in os.environ or key in self.config
    
    def all(self) -> Dict[str, str]:
        """
        获取所有配置
        
        Returns:
            所有配置的字典
        """
        # 合并系统环境变量和 .env 配置
        result = self.config.copy()
        result.update(os.environ)
        return result
    
    def get_or_generate_secret(self, key: str, length: int = 32) -> str:
        """
        获取密钥配置，如果不存在则生成一个随机密钥
        
        Args:
            key: 配置键名
            length: 随机密钥长度（字节数）
        
        Returns:
            密钥字符串
        
        注意:
            生成的密钥不会被保存到 .env 文件，每次重启都会生成新的。
            建议在生产环境中设置固定的密钥。
        """
        value = self.get(key)
        if value:
            return value
        
        # 生成随机密钥
        secret = secrets.token_urlsafe(length)
        print(f"⚠️  {key} 未设置，已生成随机密钥（重启后会改变）")
        print(f"   建议在 .env 文件中设置: {key}={secret}")
        return secret

# 全局单例
env_config = EnvConfig()


# ============================================================================
# 便捷的配置访问函数（可选）
# ============================================================================

def get_env(key: str, default: Optional[str] = None) -> Optional[str]:
    """便捷函数：获取字符串配置"""
    return env_config.get(key, default)


def get_env_int(key: str, default: int = 0) -> int:
    """便捷函数：获取整数配置"""
    return env_config.get_int(key, default)


def get_env_bool(key: str, default: bool = False) -> bool:
    """便捷函数：获取布尔配置"""
    return env_config.get_bool(key, default)


def get_env_list(key: str, default: Optional[List[str]] = None, separator: str = ',') -> List[str]:
    """便捷函数：获取列表配置"""
    return env_config.get_list(key, default, separator)


# ============================================================================
# 示例用法
# ============================================================================

if __name__ == '__main__':
    print("=" * 70)
    print("🔧 环境变量配置测试")
    print("=" * 70)
    
    # 测试各种类型的配置读取
    print("\n📝 测试配置读取:")
    print(f"APP_TITLE: {env_config.get('APP_TITLE', 'Default Title')}")
    print(f"APP_PORT: {env_config.get_int('APP_PORT', 8080)}")
    print(f"APP_SHOW: {env_config.get_bool('APP_SHOW', True)}")
    print(f"APP_RELOAD: {env_config.get_bool('APP_RELOAD', True)}")
    print(f"APP_DARK: {env_config.get_bool('APP_DARK', False)}")
    
    print("\n🔐 密钥生成测试:")
    secret = env_config.get_or_generate_secret('APP_STORAGE_SECRET', 32)
    print(f"APP_STORAGE_SECRET: {secret[:10]}... (已截断)")
    
    print("\n📊 所有配置项:")
    all_config = env_config.all()
    app_configs = {k: v for k, v in all_config.items() if k.startswith('APP_') or k.startswith('AUTH_')}
    for key in sorted(app_configs.keys())[:10]:  # 只显示前10个
        value = app_configs[key]
        # 隐藏密钥信息
        if 'SECRET' in key or 'PASSWORD' in key:
            value = '***'
        print(f"  {key}: {value}")
    
    print(f"\n✅ 配置加载完成，共 {len(app_configs)} 个应用配置项")
```

- **webproduct_ui_template\config\provider_manager.py**
```python
"""
Provider 管理器
管理可用的模型提供商配置
"""
from typing import List, Dict, Any
from dataclasses import dataclass

@dataclass
class ProviderInfo:
    """Provider 信息数据类"""
    key: str                    # Provider 标识 (例如: deepseek)
    display_name: str           # 显示名称 (例如: DeepSeek)
    description: str            # 描述
    default_base_url: str       # 默认 API 地址
    icon: str                   # 图标名称
    enabled: bool = True        # 是否启用

class ProviderManager:
    """Provider 管理器 - 管理可用的模型提供商"""
    
    # 预定义的 Provider 列表
    BUILTIN_PROVIDERS = [
        ProviderInfo(
            key='deepseek',
            display_name='DeepSeek',
            description='DeepSeek AI 大模型服务 - 提供高性价比的推理和对话能力',
            default_base_url='https://api.deepseek.com',
            icon='smart_toy'
        ),
        ProviderInfo(
            key='alibaba',
            display_name='阿里云',
            description='阿里云通义千问大模型 - 企业级AI服务',
            default_base_url='https://dashscope.aliyuncs.com/api/v1',
            icon='cloud'
        ),
        ProviderInfo(
            key='moonshot',
            display_name='月之暗面',
            description='月之暗面 Kimi 大模型 - 超长上下文对话',
            default_base_url='https://api.moonshot.cn/v1',
            icon='nightlight'
        ),
        ProviderInfo(
            key='ollama',
            display_name='Ollama',
            description='本地部署的开源模型 - 支持 Llama, Mistral 等',
            default_base_url='http://localhost:11434',
            icon='computer'
        ),
        ProviderInfo(
            key='openai',
            display_name='OpenAI',
            description='OpenAI GPT 系列模型 - 业界领先的大语言模型',
            default_base_url='https://api.openai.com/v1',
            icon='auto_awesome'
        ),
        ProviderInfo(
            key='doubao',
            display_name='豆包',
            description='豆包 系列模型 - 安全可靠的AI助手',
            default_base_url='https://ark.cn-beijing.volces.com/api/v3',
            icon='psychology'
        ),
        ProviderInfo(
            key='zhipu',
            display_name='智谱AI',
            description='智谱 GLM 系列模型 - 国产大模型',
            default_base_url='https://open.bigmodel.cn/api/paas/v4/',
            icon='lightbulb'
        ),
        ProviderInfo(
            key='baidu',
            display_name='百度',
            description='百度文心一言大模型',
            default_base_url='https://aip.baidubce.com',
            icon='search'
        ),
    ]
    
    def __init__(self):
        """初始化 Provider 管理器"""
        self.custom_providers: List[ProviderInfo] = []
    
    def get_all_providers(self) -> List[ProviderInfo]:
        """
        获取所有可用的 Provider (内置 + 自定义)
        
        Returns:
            List[ProviderInfo]: Provider 信息列表
        """
        return self.BUILTIN_PROVIDERS + self.custom_providers
    
    def get_provider_keys(self) -> List[str]:
        """
        获取所有 Provider 的 key 列表
        
        Returns:
            List[str]: Provider key 列表
        """
        return [p.key for p in self.get_all_providers()]
    
    def get_provider_options_for_select(self) -> List[Dict[str, str]]:
        """
        获取用于 ui.select 的 Provider 选项列表
        
        Returns:
            List[Dict]: [{'label': '显示名称', 'value': 'key'}, ...]
        """
        return [
            {
                'label': f"{p.display_name} ({p.key})",
                'value': p.key
            }
            for p in self.get_all_providers()
            if p.enabled
        ]
    
    def get_provider_info(self, provider_key: str) -> ProviderInfo | None:
        """
        根据 key 获取 Provider 信息
        
        Args:
            provider_key: Provider 标识
            
        Returns:
            ProviderInfo: Provider 信息,如果不存在返回 None
        """
        for provider in self.get_all_providers():
            if provider.key == provider_key:
                return provider
        return None
    
    def add_custom_provider(self, provider_info: ProviderInfo) -> bool:
        """
        添加自定义 Provider
        
        Args:
            provider_info: Provider 信息
            
        Returns:
            bool: 是否添加成功
        """
        # 检查是否已存在
        if provider_info.key in self.get_provider_keys():
            return False
        
        self.custom_providers.append(provider_info)
        return True
    
    def get_provider_display_name(self, provider_key: str) -> str:
        """
        获取 Provider 的显示名称
        
        Args:
            provider_key: Provider 标识
            
        Returns:
            str: 显示名称
        """
        info = self.get_provider_info(provider_key)
        return info.display_name if info else provider_key

# 全局 Provider 管理器实例
_provider_manager = None

def get_provider_manager() -> ProviderManager:
    """
    获取全局 Provider 管理器实例 (单例模式)
    
    Returns:
        ProviderManager: Provider 管理器实例
    """
    global _provider_manager
    if _provider_manager is None:
        _provider_manager = ProviderManager()
    return _provider_manager
```

- **webproduct_ui_template\config\yaml_config_manager.py**
```python
"""
YAML配置文件管理工具类
提供配置文件的读取、写入、备份和恢复功能
"""
import yaml
import shutil
from pathlib import Path
from typing import Dict, Any, Optional,List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class YAMLConfigManager:
    """YAML配置文件管理器 - 提供安全的读写操作"""
    
    def __init__(self, config_file_path: Path):
        """
        初始化配置管理器
        
        Args:
            config_file_path: YAML配置文件路径
        """
        self.config_file_path = Path(config_file_path)
        self.backup_dir = self.config_file_path.parent / 'backups'
        self.backup_dir.mkdir(exist_ok=True)
        
    def read_config(self) -> Optional[Dict[str, Any]]:
        """
        读取配置文件
        
        Returns:
            Dict: 配置内容字典,如果失败返回None
        """
        try:
            if not self.config_file_path.exists():
                logger.error(f"配置文件不存在: {self.config_file_path}")
                return None
            
            with open(self.config_file_path, 'r', encoding='utf-8') as file:
                config = yaml.safe_load(file)
            
            logger.info(f"成功读取配置文件: {self.config_file_path}")
            return config
            
        except Exception as e:
            logger.error(f"读取配置文件失败: {e}")
            return None
    
    def write_config(self, config: Dict[str, Any], create_backup: bool = True) -> bool:
        """
        写入配置文件
        
        Args:
            config: 配置内容字典
            create_backup: 是否创建备份
            
        Returns:
            bool: 写入是否成功
        """
        try:
            # 创建备份
            if create_backup and self.config_file_path.exists():
                self._create_backup()
            
            # 写入配置
            with open(self.config_file_path, 'w', encoding='utf-8') as file:
                yaml.dump(
                    config,
                    file,
                    allow_unicode=True,
                    default_flow_style=False,
                    sort_keys=False,
                    indent=2
                )
            
            logger.info(f"成功写入配置文件: {self.config_file_path}")
            return True
            
        except Exception as e:
            logger.error(f"写入配置文件失败: {e}")
            return False
    
    def _create_backup(self) -> Optional[Path]:
        """
        创建配置文件备份
        
        Returns:
            Path: 备份文件路径,如果失败返回None
        """
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_filename = f"{self.config_file_path.stem}_backup_{timestamp}.yaml"
            backup_path = self.backup_dir / backup_filename
            
            shutil.copy2(self.config_file_path, backup_path)
            logger.info(f"创建配置备份: {backup_path}")
            
            # 保留最近10个备份
            self._cleanup_old_backups(keep_count=10)
            
            return backup_path
            
        except Exception as e:
            logger.error(f"创建备份失败: {e}")
            return None
    
    def _cleanup_old_backups(self, keep_count: int = 10):
        """清理旧备份文件,只保留最近的N个"""
        try:
            backup_files = sorted(
                self.backup_dir.glob(f"{self.config_file_path.stem}_backup_*.yaml"),
                key=lambda p: p.stat().st_mtime,
                reverse=True
            )
            
            # 删除超出保留数量的备份
            for old_backup in backup_files[keep_count:]:
                old_backup.unlink()
                logger.info(f"删除旧备份: {old_backup}")
                
        except Exception as e:
            logger.error(f"清理旧备份失败: {e}")
    
    def restore_from_backup(self, backup_path: Path) -> bool:
        """
        从备份恢复配置
        
        Args:
            backup_path: 备份文件路径
            
        Returns:
            bool: 恢复是否成功
        """
        try:
            if not backup_path.exists():
                logger.error(f"备份文件不存在: {backup_path}")
                return False
            
            shutil.copy2(backup_path, self.config_file_path)
            logger.info(f"从备份恢复配置: {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"从备份恢复失败: {e}")
            return False
    
    def validate_config_structure(self, config: Dict[str, Any]) -> tuple[bool, str]:
        """
        验证配置文件结构
        
        Args:
            config: 配置内容字典
            
        Returns:
            tuple: (是否有效, 错误信息)
        """
        if not isinstance(config, dict):
            return False, "配置必须是字典类型"
        
        if not config:
            return False, "配置不能为空"
        
        return True, ""

class LLMConfigFileManager(YAMLConfigManager):
    """大模型配置文件管理器 - 专门处理 llm_model_config.yaml"""
    
    def __init__(self):
        """初始化大模型配置管理器"""
        # 获取配置文件路径
        current_dir = Path(__file__).parent
        config_path = current_dir / "yaml" / "llm_model_config.yaml"
        super().__init__(config_path)
    
    def get_provider_configs(self) -> Dict[str, Dict[str, Any]]:
        """
        获取所有提供商的配置
        
        Returns:
            Dict: {provider_name: {model_configs}}
        """
        config = self.read_config()
        if not config:
            return {}
        
        # 排除非提供商配置节点
        exclude_keys = ['defaults', 'metadata']
        providers = {k: v for k, v in config.items() if k not in exclude_keys}
        
        return providers
    
    def get_model_config(self, provider: str, model_key: str) -> Optional[Dict[str, Any]]:
        """
        获取指定模型的配置
        
        Args:
            provider: 提供商名称
            model_key: 模型标识
            
        Returns:
            Dict: 模型配置,如果不存在返回None
        """
        config = self.read_config()
        if not config:
            return None
        
        return config.get(provider, {}).get(model_key)
    
    def add_model_config(self, provider: str, model_key: str, model_config: Dict[str, Any]) -> bool:
        """
        添加新模型配置
        
        Args:
            provider: 提供商名称
            model_key: 模型标识
            model_config: 模型配置内容
            
        Returns:
            bool: 是否添加成功
        """
        config = self.read_config()
        if not config:
            return False
        
        # 检查是否已存在
        if provider in config and model_key in config[provider]:
            logger.warning(f"模型配置已存在: {provider}.{model_key}")
            return False
        
        # 确保提供商节点存在
        if provider not in config:
            config[provider] = {}
        
        # 添加模型配置
        config[provider][model_key] = model_config
        
        return self.write_config(config)
    
    def update_model_config(self, provider: str, model_key: str, model_config: Dict[str, Any]) -> bool:
        """
        更新模型配置
        
        Args:
            provider: 提供商名称
            model_key: 模型标识
            model_config: 新的模型配置内容
            
        Returns:
            bool: 是否更新成功
        """
        config = self.read_config()
        if not config:
            return False
        
        # 检查是否存在
        if provider not in config or model_key not in config[provider]:
            logger.warning(f"模型配置不存在: {provider}.{model_key}")
            return False
        
        # 更新配置
        config[provider][model_key] = model_config
        
        return self.write_config(config)
    
    def delete_model_config(self, provider: str, model_key: str) -> bool:
        """
        删除模型配置
        
        Args:
            provider: 提供商名称
            model_key: 模型标识
            
        Returns:
            bool: 是否删除成功
        """
        config = self.read_config()
        if not config:
            return False
        
        # 检查是否存在
        if provider not in config or model_key not in config[provider]:
            logger.warning(f"模型配置不存在: {provider}.{model_key}")
            return False
        
        # 删除配置
        del config[provider][model_key]
        
        # 如果提供商下没有模型了,也删除提供商节点
        if not config[provider]:
            del config[provider]
        
        return self.write_config(config)
    
    def get_all_models_list(self) -> list[Dict[str, Any]]:
        """
        获取所有模型的列表(扁平化结构)
        
        Returns:
            List: [{provider, model_key, config}, ...]
        """
        providers = self.get_provider_configs()
        models_list = []
        
        for provider_name, models in providers.items():
            if isinstance(models, dict):
                for model_key, model_config in models.items():
                    if isinstance(model_config, dict):
                        models_list.append({
                            'provider': provider_name,
                            'model_key': model_key,
                            'config': model_config
                        })
        
        return models_list
    
    # ✅ 新增方法
    def get_providers_from_config(self) -> List[str]:
        """
        从配置文件中获取已有的 Provider 列表
        
        Returns:
            List[str]: Provider key 列表
        """
        config = self.read_config()
        if not config:
            return []
        
        # 排除非提供商配置节点
        exclude_keys = ['defaults', 'metadata', 'providers']
        providers = [k for k in config.keys() if k not in exclude_keys]
        
        return providers
    
    # ✅ 新增方法
    def ensure_provider_exists(self, provider: str) -> bool:
        """
        确保 Provider 节点存在于配置文件中
        如果不存在则创建空节点
        
        Args:
            provider: Provider 标识
            
        Returns:
            bool: 操作是否成功
        """
        config = self.read_config()
        if not config:
            return False
        
        # 如果 Provider 不存在,创建空节点
        if provider not in config:
            config[provider] = {}
            return self.write_config(config)
        
        return True
    
class SystemPromptConfigFileManager(YAMLConfigManager):
    """系统提示词配置文件管理器 - 专门处理 system_prompt_config.yaml"""
    
    def __init__(self):
        """初始化系统提示词配置管理器"""
        # 获取配置文件路径
        current_dir = Path(__file__).parent
        config_path = current_dir / "yaml" / "system_prompt_config.yaml"
        super().__init__(config_path)
    
    def get_all_prompts(self) -> Dict[str, Dict[str, Any]]:
        """
        获取所有提示词模板配置
        
        Returns:
            Dict: {template_key: {template_config}}
        """
        config = self.read_config()
        if not config:
            return {}
        
        # 获取 prompt_templates 节点
        prompt_templates = config.get('prompt_templates', {})
        
        return prompt_templates
    
    def get_prompt_config(self, template_key: str) -> Optional[Dict[str, Any]]:
        """
        获取指定提示词模板的配置
        
        Args:
            template_key: 模板标识
            
        Returns:
            Dict: 模板配置,如果不存在返回None
        """
        prompts = self.get_all_prompts()
        return prompts.get(template_key)
    
    def add_prompt_config(self, template_key: str, prompt_config: Dict[str, Any]) -> bool:
        """
        添加新提示词模板配置
        
        Args:
            template_key: 模板标识
            prompt_config: 模板配置内容
            
        Returns:
            bool: 是否添加成功
        """
        config = self.read_config()
        if not config:
            return False
        
        # 确保 prompt_templates 节点存在
        if 'prompt_templates' not in config:
            config['prompt_templates'] = {}
        
        # 检查是否已存在
        if template_key in config['prompt_templates']:
            logger.warning(f"提示词模板已存在: {template_key}")
            return False
        
        # 添加模板配置
        config['prompt_templates'][template_key] = prompt_config
        
        return self.write_config(config)
    
    def update_prompt_config(self, template_key: str, prompt_config: Dict[str, Any]) -> bool:
        """
        更新提示词模板配置
        
        Args:
            template_key: 模板标识
            prompt_config: 新的模板配置内容
            
        Returns:
            bool: 是否更新成功
        """
        config = self.read_config()
        if not config:
            return False
        
        # 检查是否存在
        if 'prompt_templates' not in config or template_key not in config['prompt_templates']:
            logger.warning(f"提示词模板不存在: {template_key}")
            return False
        
        # 更新配置
        config['prompt_templates'][template_key] = prompt_config
        
        return self.write_config(config)
    
    def delete_prompt_config(self, template_key: str) -> bool:
        """
        删除提示词模板配置
        
        Args:
            template_key: 模板标识
            
        Returns:
            bool: 是否删除成功
        """
        config = self.read_config()
        if not config:
            return False
        
        # 检查是否存在
        if 'prompt_templates' not in config or template_key not in config['prompt_templates']:
            logger.warning(f"提示词模板不存在: {template_key}")
            return False
        
        # 删除配置
        del config['prompt_templates'][template_key]
        
        return self.write_config(config)
    
    def get_all_prompts_list(self) -> List[Dict[str, Any]]:
        """
        获取所有提示词模板的列表(扁平化结构)
        
        Returns:
            List: [{template_key, config}, ...]
        """
        prompts = self.get_all_prompts()
        prompts_list = []
        
        for template_key, template_config in prompts.items():
            if isinstance(template_config, dict):
                prompts_list.append({
                    'template_key': template_key,
                    'config': template_config
                })
        
        return prompts_list
    
    def get_categories_from_config(self) -> List[str]:
        """
        从配置文件中获取所有已使用的分类
        
        Returns:
            List[str]: 分类列表
        """
        prompts = self.get_all_prompts()
        categories = set()
        
        for template_config in prompts.values():
            if isinstance(template_config, dict):
                category = template_config.get('category', '未分类')
                categories.add(category)
        
        return sorted(list(categories))
```

### webproduct_ui_template\config\yaml

- **webproduct_ui_template\config\yaml\llm_model_config.yaml**
```yaml
alibaba:
  qwen-plus-2025-07-28:
    name: 通义千问Plus
    provider: alibaba
    model_name: qwen-plus-2025-07-28
    api_key: sk-282660fdc8cc4460943f2da2a86d3d01
    base_url: https://dashscope.aliyuncs.com/compatible-mode/v1
    max_tokens: 8192
    temperature: 0.7
    top_p: 0.8
    timeout: 60
    max_retries: 3
    stream: true
    enabled: true
    description: 阿里通义千问 Plus 中文对话模型
    tags:
    - chinese
    - general
    - multimodal
  qwen3-coder-plus:
    name: 通义千问 Coder
    provider: alibaba
    model_name: qwen3-coder-plus
    api_key: sk-282660fdc8cc4460943f2da2a86d3d01
    base_url: https://dashscope.aliyuncs.com/compatible-mode/v1
    max_tokens: 8192
    temperature: 0.7
    top_p: 0.8
    timeout: 60
    max_retries: 3
    stream: true
    enabled: true
    description: 阿里通义千问 Coder 中文对话模型
    tags:
    - chinese
    - code
深度求索:
  deepseek-chat:
    name: DeepSeek Chat
    provider: deepseek
    model_name: deepseek-chat
    api_key: sk-de5a1965cfa94ccea0eaad15d93251dc
    base_url: https://api.deepseek.com/v1
    max_tokens: 4096
    temperature: 0.7
    top_p: 1.0
    frequency_penalty: 0.0
    presence_penalty: 0.0
    timeout: 60
    max_retries: 3
    stream: true
    enabled: true
    description: DeepSeek Chat 中文优化对话模型
    tags:
    - chinese
    - chat
    - reasoning
moonshot:
  moonshot-v1-8k:
    name: moonshot-v1-8k
    provider: moonshot
    model_name: moonshot-v1-8k
    api_key: sk-5IPFajDv6yy8hWKd3DScOHea2HE10r1FTN6SMgz038ljsSTf
    base_url: https://api.moonshot.cn/v1
    max_tokens: 8192
    temperature: 0.7
    top_p: 0.7
    timeout: 60
    max_retries: 3
    stream: true
    enabled: true
    description: 月之暗面通用大模型
    tags:
    - chinese
    - general
Ollama:
  qwen3:8b:
    name: qwen3-8b
    provider: ollama
    model_name: qwen3:8b
    api_key: sk-ollamakey123
    base_url: http://localhost:11434/v1
    max_tokens: 4096
    temperature: 0.7
    top_p: 0.9
    timeout: 120
    max_retries: 3
    stream: true
    enabled: true
    description: 本地部署的 qwen3 8B 模型
    tags:
    - local
    - qwen
    - opensource
  deepseek-r1:8b:
    name: deeseek-8b
    provider: ollama
    model_name: deepseek-r1:8b
    api_key: sk-ollamakey123
    base_url: http://localhost:11434/v1
    max_tokens: 4096
    temperature: 0.7
    top_p: 0.9
    timeout: 120
    max_retries: 3
    stream: true
    enabled: true
    description: 本地部署的 deepseek 8B 模型
    tags:
    - local
    - deepseek
    - opensource
  qwen2.5:latest:
    name: qwen2.5-8b
    provider: ollama
    model_name: qwen2.5:latest
    api_key: sk-ollamakey123
    base_url: http://localhost:11434/v1
    max_tokens: 4096
    temperature: 0.7
    top_p: 0.9
    timeout: 120
    max_retries: 3
    stream: true
    enabled: true
    description: 本地部署的 deepseek 8B 模型
    tags:
    - local
    - deepseek
    - opensource
defaults:
  timeout: 60
  max_retries: 3
  stream: true
  temperature: 0.7
  top_p: 1.0
  max_tokens: 4096
  enabled: true
metadata:
  version: 1.0.0
  created_at: '2025-01-01'
  description: LLM 模型统一配置文件
  supported_providers:
  - deepseek
  - alibaba
  - moonshot
  - ollama
doubao:
  deepseek-v3-1-terminus:
    name: 豆包DeepSeek
    base_url: https://ark.cn-beijing.volces.com/api/v3
    api_key: dac7e1c4-6883-4d14-98ba-29ab70e924cf
    timeout: 60
    max_retries: 3
    stream: true
    enabled: true
    description: ''
zhipu:
  glm-4.5-flash:
    name: GLM-4.5-Flash
    provider: zhipu
    model_name: glm-4.5-flash
    base_url: https://open.bigmodel.cn/api/paas/v4/
    api_key: 8741dc327c45445d83c82aca7e636842.H1wbh0PglthU51cQ
    timeout: 60
    max_retries: 3
    stream: true
    enabled: true
    description: ''
  GLM-4.1V-Thinking-Flash:
    name: GLM-4.1V-Thinking-Flash
    base_url: https://open.bigmodel.cn/api/paas/v4/
    api_key: 8741dc327c45445d83c82aca7e636842.H1wbh0PglthU51cQ
    timeout: 60
    max_retries: 3
    stream: true
    enabled: true
    description: ''

```

- **webproduct_ui_template\config\yaml\system_prompt_config.yaml**
````yaml
metadata:
  version: 1.0.0
  description: 大模型系统提示词模板配置
  author: AI Assistant
  created_date: '2025-08-10'
  updated_date: '2025-08-10'
  schema_version: '1.0'
prompt_templates:
  默认:
    name: 默认
    description: 专门用于生成高质量、规范的Markdown文档，包括表格、Mermaid图表、LaTeX公式等。
    enabled: true
    version: '1.0'
    category: 文档编写
    system_prompt: '- 你是一个AI助手，帮助用户处理各类问题,使用有条理的markdown文本格式回答,注意标题的使用从4级开始。

      '
    examples: {}
  一企一档专家:
    name: 一企一档
    description: 基于企业档案数据结构，生成精确的MongoDB查询、聚合、更新语句
    enabled: true
    version: '1.0'
    category: 数据库操作
    system_prompt: "# MongoDB查询语句生成专家\n\n## \U0001F3AF 角色定位\n你是一位MongoDB数据库专家，专门负责为企业档案系统生成高效、准确的MongoDB操作语句。\n\
      你深度理解企业档案的层级结构和数据模型，能够快速生成符合业务需求的数据库操作语句。\n\n## \U0001F5C4️ 核心数据结构\n\n### 主要集合：一企一档\n\
      企业信息以扁平化分级结构存储，每个字段信息对应企业文档中fields数组中的一个子档案，以下是字段的文档结构信息的样例。\n\n```javascript\n\
      {\n  \"_id\": \"\",\n  \"enterprise_code\": \"\",         // 企业统一信用编码\n  \"\
      enterprise_name\": \"\",         // 企业名称\n  \"fields\": [\n    {\n      \"enterprise_code\"\
      : \"\",      // 企业统一信用编码\n      \"enterprise_name\": \"\",      // 企业名称\n\n\
      \      // === 三级分类层级 ===\n      \"l1_code\": \"L19E5FFA\",      // 一级代码\n  \
      \    \"l1_name\": \"基本信息\",       // 一级名称\n      \"l2_code\": \"L279A000\",\
      \      // 二级代码\n      \"l2_name\": \"登记信息\",       // 二级名称\n      \"l3_code\"\
      : \"L336E6A6\",      // 三级代码\n      \"l3_name\": \"企业基本信息\",   // 三级名称\n\n \
      \     // === 路径信息 ===\n      \"path_code\": \"L19E5FFA.L279A000.L336E6A6\",\
      \       // 三级结构完整代码\n      \"path_name\": \"基本信息.登记信息.企业基本信息\",     //  三级结构完整名称\n\
      \      \"full_path_code\": \"L19E5FFA.L279A000.L336E6A6.F1BDA09\",   // 字段完整代码\n\
      \      \"full_path_name\": \"基本信息.登记信息.企业基本信息.统一社会信用代码\",   // 字段完整名称\n\n  \
      \    // === 字段信息 ===\n      \"field_code\": \"F1BDA09\",          // 字段代码\n\
      \      \"field_name\": \"统一社会信用代码\",   // 字段名称\n      \"field_type\": \"\",\
      \                 // 字段类型\n\n      // === 字段数据值 ===\n      \"value\": \"\",\
      \                      // 字段值\n      \"value_text\": \"\",                 //\
      \ 文本描述值\n      \"value_pic_url\": \"\",              // 字段关联图片\n      \"value_doc_url\"\
      : \"\",              // 字段关联文档\n      \"value_video_url\": \"\",           \
      \ // 字段关联视频\n\n      // === 元数据 ===\n      \"remark\": \"\",               \
      \      // 字段说明\n      \"data_url\": \"\",                   // 字段数据源url\n  \
      \    \"is_required\": false,             // 是否必填\n      \"data_source\": \"\"\
      ,                // 数据来源\n      \"encoding\": \"\",                   // 编码格式\n\
      \      \"format\": \"\",                     // 数据格式\n      \"license\": \"\"\
      ,                    // 许可证\n      \"rights\": \"\",                     //\
      \ 使用权限\n      \"update_frequency\": \"\",           // 更新频率\n      \"value_dict\"\
      : \"\",                 // 字典值选项\n\n      // === 排序显示 ===\n      \"l1_order\"\
      : ,                     // 一级分类排序\n      \"l2_order\": ,                   \
      \  // 二级分类排序\n      \"l3_order\": ,                     // 三级分类排序\n      \"\
      field_order\": ,                  // 字段排序\n\n      // === 时间戳 ===\n      \"\
      create_time\": \"\",                // 创建时间\n      \"update_time\": \"\",  \
      \              // 更新时间\n\n      // === 状态 ===\n      \"status\": \"\"      \
      \                // 数据状态\n    },\n    ......\n  ]\n}\n```\n\n## \U0001F3AF 输出规范\n\
      1. **语法准确**: 只生成严格遵循MongoDB语法规范的执行语句，不要包含其他解释文字\n2. **性能优化**: 优先考虑查询性能和索引使用\n\
      3. **可执行性**: 确保生成的语句可以直接在MongoDB中执行\n4. **控制操作**: 使用合适的操作，尽量使用aggregate，且不要自定义字段名。\n\
      5. **重命名**: 尽量不用重命名，如果非要用重命名操作，请使用**中文**进行重命名。\n"
    examples: {}
global_settings:
  default_language: zh-CN

````

## webproduct_ui_template\header_pages

- **webproduct_ui_template\header_pages\__init__.py** *(包初始化文件)*
```python
from .search_page import search_page_content
from .messages_page import messages_page_content
from .contact_page import contact_page_content

# 导出所有头部页面处理函数
def get_header_page_handlers():
    """获取所有头部页面处理函数"""
    return {
        'search': search_page_content,
        'messages': messages_page_content,
        'contact': contact_page_content,
    }

__all__ = [
    'search_page_content',
    'messages_page_content',
    'notifications_page_content',
    'contact_page_content',
    'get_header_page_handlers'
]
```

- **webproduct_ui_template\header_pages\contact_page.py**
```python
from nicegui import ui

def contact_page_content():
    """联系我们页面内容"""
    ui.label('联系我们').classes('text-3xl font-bold text-emerald-800 dark:text-emerald-200')
    ui.label('如有任何问题或建议，请随时联系我们。').classes('text-gray-600 dark:text-gray-400 mt-4')
    
    with ui.card().classes('w-full mt-4'):
        ui.label('联系方式').classes('text-lg font-semibold')
        ui.label('📧 邮箱: support@example.com').classes('mt-2')
        ui.label('📞 电话: +86 400-123-4567').classes('mt-2')
        ui.label('💬 在线客服: 工作日 9:00-18:00').classes('mt-2')
        
    with ui.card().classes('w-full mt-4'):
        ui.label('意见反馈').classes('text-lg font-semibold')
        ui.textarea('请输入您的意见或建议', placeholder='我们很重视您的反馈...').classes('w-full mt-2')
        ui.button('提交反馈', icon='send').classes('mt-2')
```

- **webproduct_ui_template\header_pages\messages_page.py**
```python
from nicegui import ui

def messages_page_content():
    """消息页面内容"""
    ui.label('消息中心').classes('text-3xl font-bold text-cyan-800 dark:text-cyan-200')
    ui.label('查看您的所有消息和通知。').classes('text-gray-600 dark:text-gray-400 mt-4')
    
    with ui.card().classes('w-full mt-4'):
        ui.label('新消息').classes('text-lg font-semibold')
        ui.label('您有3条未读消息').classes('text-gray-600 mt-2')
        ui.button('查看全部', icon='visibility').classes('mt-2')
```

- **webproduct_ui_template\header_pages\search_page.py**
```python
from nicegui import ui

def search_page_content():
    """搜索页面内容"""
    ui.label('搜索页面').classes('text-3xl font-bold text-yellow-800 dark:text-yellow-200')
    ui.label('您可以在这里进行全局搜索。').classes('text-gray-600 dark:text-gray-400 mt-4')
    ui.input('搜索关键词', placeholder='输入关键词').classes('w-full mt-2')
    ui.button('搜索').classes('mt-4')
```

## webproduct_ui_template\menu_pages

- **webproduct_ui_template\menu_pages\__init__.py** *(包初始化文件)*
```python
from .home_page import home_content
from .other_demo_page import other_page_content
from .chat_demo_page import chat_page_content
from .auth_test_page import auth_test_page_content
from .default_auth_page import default_auth_page_content
from .erp_auth_page import erp_auth_page_content  # ✅ 新增 ERP 场景页面


# 导出所有菜单页面处理函数
def get_menu_page_handlers():
    """获取所有菜单页面处理函数"""
    return {
        'home': home_content,
        'other_page': other_page_content,
        'chat_page': chat_page_content,
        'auth_test': auth_test_page_content,
        'default_auth':default_auth_page_content,
        'erp_auth_page':erp_auth_page_content
    }

__all__ = [
    'home_content',
    'other_page_content',
    'chat_page_content',
    'get_menu_page_handlers',
    'auth_test_page_content',
    'default_auth_page_content',
    'erp_auth_page_content'
]
```

- **webproduct_ui_template\menu_pages\chat_demo_page.py**
```python
"""
企业档案页面入口
使用 component/chat 可复用聊天组件（自由文本输入）
"""
# from common.exception_handler import safe_protect
import inspect
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
logger = get_logger(__name__)
from component.chat import ChatComponent

@safe_protect(name=f"聊天框测试页面/{__name__}", error_msg=f"聊天框测试页面加载失败")
def chat_page_content():
    """
    企业档案页面内容
    功能说明:
    1. 在侧边栏的"提示数据"中可以输入任意格式的提示文本
    2. 开启"启用"开关后，输入的提示数据会自动附加到对话中
    3. 无需特定格式，支持自由文本输入
    """
    chat = ChatComponent(
        sidebar_visible=True,
        default_model=None,
        default_prompt=None,
        is_record_history=True
    )
    chat.render()


# 导出主要功能，保持原有接口不变
__all__ = ['chat_page_content']
```

- **webproduct_ui_template\menu_pages\home_page.py**
```python
from nicegui import ui
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

@safe_protect(name="首页内容", error_msg="首页内容发生错误", return_on_error=None)
def home_content():
    """首页内容"""
    ui.label('欢迎回到首页!').classes('text-3xl font-bold text-green-800 dark:text-green-200')
    ui.label('这是您个性化的仪表板。').classes('text-gray-600 dark:text-gray-400 mt-4')
```
