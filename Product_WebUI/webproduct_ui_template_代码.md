# webproduct_ui_template

- **webproduct_ui_template\main.py**
```python
"""
主应用入口 - 集成统一建表功能（简化版）
"""
import sys
import os
from pathlib import Path
from nicegui import ui, app
from component import with_spa_layout, LayoutConfig, static_manager
from menu_pages import get_menu_page_handlers
from header_pages import get_header_page_handlers
from auth import (
    auth_manager, 
    require_login, 
    require_role,
    login_page_content,
    register_page_content,
    get_auth_page_handlers
)

def create_protected_handlers():
    """为需要认证的页面添加装饰器"""
    menu_handlers = get_menu_page_handlers()
    header_handlers = get_header_page_handlers()
    system_handlers = get_auth_page_handlers()
    
    return {**menu_handlers, **header_handlers, **system_handlers}

if __name__ in {"__main__", "__mp_main__"}:

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

    # 主页面
    @ui.page('/workbench')
    def main_page():
        # 检查用户认证状态
        user = auth_manager.check_session()
        if not user:
            ui.navigate.to('/login')
            return

        # 创建带认证的SPA布局
        @with_spa_layout(
            config=config,
            menu_items=[
                {'key': 'home', 'label': '首页', 'icon': 'home', 'route': 'home','separator_after': True},
                {'key': 'one_page', 'label': 'ChatDemo', 'icon': 'business', 'route': 'chat_page'},
                {'key': 'two_page', 'label': 'OtherDemo', 'icon': 'people', 'route': 'other_page','separator_after': True},
            ],
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

    ui.run(
        title=config.app_title,
        port=8080,
        show=True,
        reload=True,
        favicon='🚀',
        dark=False,
        storage_secret='your-secret-key-here'
    )
```

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

def create_demo_menu_structure() -> list[MultilayerMenuItem]:
    """
    创建演示用的多层菜单结构
    这里展示了2-3层的菜单结构
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
                    label='文档管理',
                    icon='description',
                    route='other_page'  # 暂时复用other_page
                ),
            ]
        ),
        
        
        # 系统管理 - 第2个分组(演示更多子项)
        MultilayerMenuItem(
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
                MultilayerMenuItem(
                    key='permissions',
                    label='权限管理',
                    icon='lock',
                    route='permission_management'
                ),
            ]
        ),
        
        # 配置中心 - 第3个分组
        MultilayerMenuItem(
            key='config',
            label='配置中心',
            icon='tune',
            children=[
                MultilayerMenuItem(
                    key='llm',
                    label='大模型配置',
                    icon='psychology',
                    route='llm_config_management'
                ),
                MultilayerMenuItem(
                    key='prompt',
                    label='提示词配置',
                    icon='article',
                    route='prompt_config_management'
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
    print("🚀 启动多层布局演示应用")
    print("=" * 70)
    
    # 获取受保护的页面处理器
    protected_handlers = create_protected_handlers()
    
    # 创建自定义配置
    config = LayoutConfig()
    config.app_title = 'NeoUI多层布局'
    config.menu_title = '功能导航'
    
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
        menu_items = create_demo_menu_structure()
        
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
    print("📝 测试账号：")
    print("   管理员 - 用户名: admin, 密码: admin123")
    print("   普通用户 - 用户名: user, 密码: user123")
    print("=" * 70)
    print(f"🌐 应用启动在: http://localhost:8080")
    print("=" * 70 + "\n")
    
    # 启动应用
    ui.run(
        title=config.app_title,
        port=8080,
        show=True,
        reload=True,
        favicon='🚀',
        dark=False,
        storage_secret='your-secret-key-here'
    )
```

- **webproduct_ui_template\simple_main.py**
```python
"""
简单布局主应用入口 - 只包含顶部导航栏的布局
"""
from nicegui import ui, app
from component import with_simple_spa_layout, LayoutConfig, static_manager
from menu_pages import get_menu_page_handlers
from header_pages import get_header_page_handlers
from auth import (
    auth_manager, 
    require_login, 
    require_role,
    login_page_content,
    register_page_content,
    get_auth_page_handlers,
)

# 创建受保护的页面处理器
def create_protected_handlers():
    """为需要认证的页面添加装饰器"""
    menu_handlers = get_menu_page_handlers()
    header_handlers = get_header_page_handlers()
    system_handlers = get_auth_page_handlers()
    
    return {**menu_handlers, **header_handlers, **system_handlers}

if __name__ in {"__main__", "__mp_main__"}:
    
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

    # 主页面 - 使用简单布局
    @ui.page('/workbench')
    def simple_main_page():
        # 检查用户认证状态
        user = auth_manager.check_session()
        if not user:
            ui.navigate.to('/login')
            return

        # 创建带认证的简单SPA布局
        @with_simple_spa_layout(
            config=config,
            nav_items=[
                {'key': 'home', 'label': '首页', 'icon': 'home', 'route': 'home'},
                {'key': 'one_page', 'label': 'ChatDemo', 'icon': 'business', 'route': 'chat_page'},
                {'key': 'two_page', 'label': 'OtherDemo', 'icon': 'people', 'route': 'other_page','separator_after': True},
             
            ],
            
            route_handlers=protected_handlers
        )
        def simple_spa_layout():
            pass

        simple_spa_layout()

    # 默认重定向到简单布局页面
    @ui.page('/')
    def index():
        ui.navigate.to('/workbench')

    # 启动应用
    print("🌐 启动简单布局应用服务器...")
    print("📋 布局特点：只包含顶部导航栏，无侧边栏")
    print("🎯 访问地址：http://localhost:8080/workbench")
    print("📝 测试账号：")
    print("   管理员 - 用户名: admin, 密码: admin123")
    print("   普通用户 - 用户名: user, 密码: user123")
    print("🔄 支持页面刷新保持路由状态（基于存储）")

    ui.run(
        title=config.app_title,
        port=8080,
        show=True,
        reload=True,   # 设置为True，控制台中会输出两次
        favicon='🚀',
        dark=False,
        prod_js=False,
        storage_secret='your-secret-key-here'
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

- **webproduct_ui_template\auth\config.py**
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

- **webproduct_ui_template\auth\database.py**
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

- **webproduct_ui_template\auth\detached_helper.py**
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

- **webproduct_ui_template\auth\models.py**
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

### webproduct_ui_template\auth\migrations

- **webproduct_ui_template\auth\migrations\__init__.py** *(包初始化文件 - 空)*
```python

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
            pagination={'rowsPerPage': 10, 'sortBy': 'provider'}
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



```

- **webproduct_ui_template\auth\pages\logout_page.py**
```python
from nicegui import ui, app
from ..auth_manager import auth_manager
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

- **webproduct_ui_template\auth\pages\user_management_page.py**
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

## webproduct_ui_template\common

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
        logger.debug("🧹 日志清理后台任务已启动")
    
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
                logger.debug("✅ 日志清理完成,无过期文件夹")
        
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
            print(f"⚠️ 获取用户上下文失败: {e}")
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

class LayoutConfig:
    """布局配置类"""
    def __init__(self):
        self.app_title = 'NeoUI模板'
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
            
        logger.debug(f"🔧 已注册系统路由: {list(system_routes.keys())}")
        logger.debug(f"🔧 注册的全部路由：{self.all_routes}")
        logger.debug(f"⚠️ 注意：logout 路由未注册到持久化路由中（一次性操作）")

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
        self.expanded_keys: Set[str] = set()  # 当前展开的父节点keys
        self.selected_leaf_key: Optional[str] = None  # 当前选中的叶子节点key
        
        # UI元素引用映射
        self.expansion_refs: Dict[str, any] = {}  # key -> ui.expansion对象
        self.leaf_refs: Dict[str, any] = {}  # key -> 叶子节点ui.row对象
        
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
    
    def handle_settings_menu_item_click(self, route: str, label: str):
        """
        处理设置菜单项点击事件
        
        Args:
            route: 目标路由
            label: 菜单项标签
        """
        from auth.auth_manager import auth_manager
        
        # 第一层检查：是否已登录
        if not auth_manager.is_authenticated():
            logger.debug(f"⚠️ 未登录用户尝试访问管理功能: {label}")
            ui.notify('请先登录', type='warning')
            self.navigate_to_route('login', '登录')
            return
        
        # 第二层检查：是否有管理员权限
        if not auth_manager.has_role('admin') and not auth_manager.current_user.is_superuser:
            logger.warning(f"⚠️ 用户 {auth_manager.current_user.username} 无权限访问: {label}")
            ui.notify('您没有管理员权限，无法访问此功能', type='error')
            # ✅ 关键：导航到无权限页面，不触发目标页面的装饰器
            self.navigate_to_route('no_permission', '权限不足')
            return
        
        # 第三层：权限验证通过，导航到目标页面
        logger.info(f"✅ 用户 {auth_manager.current_user.username} 访问管理功能: {label}")
        ui.notify(f'访问管理功能: {label}')
        self.navigate_to_route(route, label)

    def handle_user_menu_item_click(self, route: str, label: str):
        """
        处理用户菜单项点击事件
        
        Args:
            route: 目标路由
            label: 菜单项标签
        """
        logger.debug(f"👤 点击了用户菜单项: {label}")
        ui.notify(f'点击了用户菜单项: {label}')
        
        # 特殊处理注销：清除路由存储
        if route == 'logout':
            logger.info("🚪 执行用户注销，清除路由存储")
            self.clear_route_storage()
        
        # 导航到目标路由
        self.navigate_to_route(route, label)

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
        self.current_route = route
        self.current_label = label

        if update_storage:
            app.storage.user[self._route_key] = route
            app.storage.user[self._label_key] = label

        # 清空内容区域
        if self.content_container:
            self.content_container.clear()
        
        # ✅ 先执行路由处理器 (在 with 上下文之外)
        if route in self.route_handlers:
            with self.content_container:
                # 查找菜单项以显示面包屑
                menu_item = self.menu_config.find_by_route(route)
                if menu_item:
                    self._render_breadcrumb(menu_item)
            
            # ✅ 关键修改:在面包屑渲染后,在 with 上下文外调用handler
            self.route_handlers[route]()
        else:
            # 默认显示 (没有handler的情况)
            with self.content_container:
                menu_item = self.menu_config.find_by_route(route)
                if menu_item:
                    self._render_breadcrumb(menu_item)
                    
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
        # print(f"🎯 选中叶子节点: {item.label} (key={key})")
        
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
            ui.navigate.to('/login')
        else:
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
            # print(f"🔄 恢复路由: {stored_route} ({stored_label})")
            
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
        
        logger.debug(f"🔧 已注册系统路由: {list(system_routes.keys())}")
        logger.debug(f"🔧 注册的全部路由：{self.all_routes}")
        logger.debug(f"⚠️ 注意：logout 路由未注册到持久化路由中（一次性操作）")
    
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
            
        logger.debug(f"🔧 已注册系统路由: {list(system_routes.keys())}")
        logger.debug(f"🔧 注册的全部路由：{self.all_routes}")
        logger.debug(f"⚠️  注意：logout 路由未注册到持久化路由中（一次性操作）")

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

## webproduct_ui_template\database_models

- **webproduct_ui_template\database_models\__init__.py** *(包初始化文件 - 空)*
```python

```

- **webproduct_ui_template\database_models\business_utils.py**
```python
# database_models/business_utils.py
"""
业务模型工具类 - 提供跨模块的辅助功能
避免直接在业务模型中硬编码对 auth 模块的依赖
"""
from typing import Optional, Dict, Any, List
from contextlib import contextmanager

class UserInfoHelper:
    """用户信息辅助工具"""
    
    @staticmethod
    def get_user_info(user_id: int) -> Optional[Dict[str, Any]]:
        """获取用户基本信息"""
        if not user_id:
            return None
            
        try:
            from auth.database import get_db
            from auth.models import User
            
            with get_db() as db:
                user = db.query(User).filter(User.id == user_id).first()
                if user:
                    return {
                        'id': user.id,
                        'username': user.username,
                        'full_name': user.full_name,
                        'email': user.email,
                        'is_active': user.is_active
                    }
        except Exception:
            pass
        return None
    
    @staticmethod
    def get_users_info(user_ids: List[int]) -> Dict[int, Dict[str, Any]]:
        """批量获取用户信息"""
        if not user_ids:
            return {}
            
        try:
            from auth.database import get_db
            from auth.models import User
            
            with get_db() as db:
                users = db.query(User).filter(User.id.in_(user_ids)).all()
                return {
                    user.id: {
                        'id': user.id,
                        'username': user.username,
                        'full_name': user.full_name,
                        'email': user.email,
                        'is_active': user.is_active
                    }
                    for user in users
                }
        except Exception:
            pass
        return {}

class AuditHelper:
    """审计辅助工具"""
    
    @staticmethod
    def set_audit_fields(obj, user_id: int, is_update: bool = False):
        """设置审计字段"""
        if hasattr(obj, 'created_by') and not is_update:
            obj.created_by = user_id
        if hasattr(obj, 'updated_by'):
            obj.updated_by = user_id
    
    @staticmethod
    def get_audit_info(obj) -> Dict[str, Any]:
        """获取审计信息"""
        result = {}
        
        if hasattr(obj, 'created_by') and obj.created_by:
            result['creator'] = UserInfoHelper.get_user_info(obj.created_by)
        
        if hasattr(obj, 'updated_by') and obj.updated_by:
            result['updater'] = UserInfoHelper.get_user_info(obj.updated_by)
            
        if hasattr(obj, 'created_at'):
            result['created_at'] = obj.created_at
            
        if hasattr(obj, 'updated_at'):
            result['updated_at'] = obj.updated_at
            
        return result

class BusinessQueryHelper:
    """业务查询辅助工具"""
    
    @staticmethod
    @contextmanager
    def get_business_db():
        """获取业务数据库会话"""
        from auth.database import get_db
        with get_db() as db:
            yield db
    
    @staticmethod
    def get_user_business_records(user_id: int, model_class, **filters):
        """获取用户的业务记录"""
        try:
            with BusinessQueryHelper.get_business_db() as db:
                query = db.query(model_class).filter(model_class.created_by == user_id)
                
                # 应用额外过滤条件
                for field, value in filters.items():
                    if hasattr(model_class, field):
                        query = query.filter(getattr(model_class, field) == value)
                
                return query.all()
        except Exception:
            return []
    
    @staticmethod
    def get_active_records(model_class, **filters):
        """获取活跃记录"""
        try:
            with BusinessQueryHelper.get_business_db() as db:
                query = db.query(model_class).filter(model_class.is_active == True)
                
                # 应用额外过滤条件
                for field, value in filters.items():
                    if hasattr(model_class, field):
                        query = query.filter(getattr(model_class, field) == value)
                
                return query.all()
        except Exception:
            return []

class RelationshipHelper:
    """关系辅助工具 - 处理跨模块关系"""
    
    @staticmethod
    def get_related_records(obj, relationship_name: str, related_model_class):
        """获取关联记录"""
        try:
            if hasattr(obj, relationship_name):
                return getattr(obj, relationship_name)
            
            # 如果直接关系不存在，尝试通过外键查询
            foreign_key_field = f"{obj.__class__.__name__.lower()}_id"
            if hasattr(related_model_class, foreign_key_field):
                with BusinessQueryHelper.get_business_db() as db:
                    return db.query(related_model_class).filter(
                        getattr(related_model_class, foreign_key_field) == obj.id
                    ).all()
        except Exception:
            pass
        return []

# 为业务模型提供的便捷装饰器
def with_user_info(func):
    """装饰器：为方法添加用户信息获取功能"""
    def wrapper(self, *args, **kwargs):
        result = func(self, *args, **kwargs)
        if isinstance(result, dict) and hasattr(self, 'created_by'):
            result['user_info'] = UserInfoHelper.get_user_info(self.created_by)
        return result
    return wrapper

def with_audit_info(func):
    """装饰器：为方法添加审计信息"""
    def wrapper(self, *args, **kwargs):
        result = func(self, *args, **kwargs)
        if isinstance(result, dict):
            result['audit_info'] = AuditHelper.get_audit_info(self)
        return result
    return wrapper
```

- **webproduct_ui_template\database_models\shared_base.py**
```python
# database_models/shared_base.py
from sqlalchemy import Column, Integer, DateTime, String, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, declared_attr
from auth.database import Base

class TimestampMixin:
    """时间戳混入类"""
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class AuditMixin:
    """审计混入类 - 记录操作用户（不强制建立关系）"""
    created_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    updated_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    
    # 不在这里定义关系，让具体的业务模型自己决定是否需要关系
    # 这样可以避免与auth模块的强耦合
    
    def get_creator_info(self):
        """获取创建者信息的辅助方法"""
        if not self.created_by:
            return None
            
        # 动态导入避免循环依赖
        try:
            from auth.database import get_db
            from auth.models import User
            
            with get_db() as db:
                creator = db.query(User).filter(User.id == self.created_by).first()
                if creator:
                    return {
                        'id': creator.id,
                        'username': creator.username,
                        'full_name': creator.full_name
                    }
        except Exception:
            pass
        return None
    
    def get_updater_info(self):
        """获取更新者信息的辅助方法"""
        if not self.updated_by:
            return None
            
        try:
            from auth.database import get_db
            from auth.models import User
            
            with get_db() as db:
                updater = db.query(User).filter(User.id == self.updated_by).first()
                if updater:
                    return {
                        'id': updater.id,
                        'username': updater.username,
                        'full_name': updater.full_name
                    }
        except Exception:
            pass
        return None

class BusinessBaseModel(Base, TimestampMixin, AuditMixin):
    """业务模型基类"""
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)
    is_active = Column(Boolean, default=True)
    description = Column(String(500), nullable=True)
    
    def to_dict(self, include_audit_info=False):
        """转换为字典，便于JSON序列化"""
        result = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        
        # 可选包含审计信息
        if include_audit_info:
            result['creator_info'] = self.get_creator_info()
            result['updater_info'] = self.get_updater_info()
            
        return result
    
    def set_creator(self, user_id):
        """设置创建者"""
        self.created_by = user_id
    
    def set_updater(self, user_id):
        """设置更新者"""
        self.updated_by = user_id
```

### webproduct_ui_template\database_models\business_models

- **webproduct_ui_template\database_models\business_models\__init__.py** *(包初始化文件 - 空)*
```python

```

- **webproduct_ui_template\database_models\business_models\chat_history_model.py**
```python
# database_models/business_models/chat_history_model.py
"""
聊天历史模型 - 存储用户聊天记录
"""
from sqlalchemy import Column, String, Text, Integer, JSON, Boolean, DateTime, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from typing import List, Optional, Dict, Any
from datetime import datetime
from ..shared_base import BusinessBaseModel

class ChatHistory(BusinessBaseModel):
    """聊天历史表"""
    __tablename__ = 'chat_histories'
    
    # 基础字段
    title = Column(String(200), nullable=False, comment='聊天标题')
    model_name = Column(String(100), nullable=True, comment='使用的AI模型')
    prompt_name = Column(String(100), nullable=True, comment='使用的提示模板')
    messages = Column(JSON, nullable=False, comment='聊天消息列表')
    
    # 新增字段 - 统计和缓存信息
    message_count = Column(Integer, default=0, comment='消息总数')
    last_message_at = Column(DateTime, nullable=True, comment='最后一条消息时间')
    
    # 软删除支持
    is_deleted = Column(Boolean, default=False, comment='是否已删除')
    deleted_at = Column(DateTime, nullable=True, comment='删除时间')
    deleted_by = Column(Integer, nullable=True, comment='删除人ID')
    
    # 创建复合索引
    __table_args__ = (
        # 用户聊天记录按时间排序的复合索引
        Index('idx_user_created_time', 'created_by', 'created_at'),
        # 用户有效记录查询索引
        Index('idx_user_active_records', 'created_by', 'is_deleted', 'is_active'),
        # 最后消息时间索引（用于最近活动排序）
        Index('idx_last_message_time', 'last_message_at'),
    )
    
    def __repr__(self):
        return f"<ChatHistory(id={self.id}, title='{self.title}', user_id={self.created_by}, messages={self.message_count})>"
    
    # === 实例方法 ===
    
    def update_message_stats(self):
        """更新消息统计信息"""
        if self.messages:
            self.message_count = len(self.messages)
            # 找到最后一条消息的时间
            last_timestamp = None
            for msg in reversed(self.messages):
                timestamp_str = msg.get('timestamp')
                if timestamp_str:
                    try:
                        last_timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                        break
                    except (ValueError, AttributeError):
                        continue
            
            self.last_message_at = last_timestamp or self.updated_at
        else:
            self.message_count = 0
            self.last_message_at = self.updated_at
    
    def soft_delete(self, deleted_by_user_id: int):
        """软删除聊天记录"""
        self.is_deleted = True
        self.deleted_at = func.now()
        self.deleted_by = deleted_by_user_id
        self.is_active = False
    
    def restore(self):
        """恢复已删除的聊天记录"""
        self.is_deleted = False
        self.deleted_at = None
        self.deleted_by = None
        self.is_active = True
    
    def get_message_preview(self, max_length: int = 50) -> str:
        """获取消息预览（第一条用户消息）"""
        if not self.messages:
            return "空对话"
        
        for msg in self.messages:
            if msg.get('role') == 'user':
                content = msg.get('content', '')
                if len(content) <= max_length:
                    return content
                return content[:max_length] + '...'
        
        return "无用户消息"
    
    def get_duration_info(self) -> Dict[str, Any]:
        """获取对话时长信息"""
        if not self.messages or len(self.messages) < 2:
            return {'duration_minutes': 0, 'message_count': self.message_count}
        
        first_timestamp = None
        last_timestamp = None
        
        for msg in self.messages:
            timestamp_str = msg.get('timestamp')
            if timestamp_str:
                try:
                    timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                    if first_timestamp is None:
                        first_timestamp = timestamp
                    last_timestamp = timestamp
                except (ValueError, AttributeError):
                    continue
        
        if first_timestamp and last_timestamp:
            duration = last_timestamp - first_timestamp
            duration_minutes = duration.total_seconds() / 60
        else:
            duration_minutes = 0
        
        return {
            'duration_minutes': round(duration_minutes, 1),
            'message_count': self.message_count,
            'first_message': first_timestamp,
            'last_message': last_timestamp
        }
    
    def update_chat_title(self, new_title: str) -> bool:
        """更新聊天标题的模型方法"""
        if not new_title or not new_title.strip():
            return False
        
        if len(new_title) > 200:
            return False
        
        self.title = new_title.strip()
        from sqlalchemy.sql import func
        self.updated_at = func.now()
        
        return True
    # === 类方法 ===
    
    @classmethod
    def get_user_recent_chats(cls, db_session, user_id: int, limit: int = 20, include_deleted: bool = False) -> List['ChatHistory']:
        """获取用户最近的聊天记录"""
        query = db_session.query(cls).filter(cls.created_by == user_id)
        
        if not include_deleted:
            query = query.filter(cls.is_deleted == False, cls.is_active == True)
        
        return query.order_by(cls.updated_at.desc()).limit(limit).all()
    
    @classmethod
    def get_user_active_chat_count(cls, db_session, user_id: int) -> int:
        """获取用户有效聊天记录数量"""
        return db_session.query(cls).filter(
            cls.created_by == user_id,
            cls.is_deleted == False,
            cls.is_active == True
        ).count()
    
    @classmethod
    def search_user_chats_by_title(cls, db_session, user_id: int, keyword: str, limit: int = 10) -> List['ChatHistory']:
        """按标题搜索用户的聊天记录"""
        return db_session.query(cls).filter(
            cls.created_by == user_id,
            cls.is_deleted == False,
            cls.is_active == True,
            cls.title.ilike(f'%{keyword}%')
        ).order_by(cls.created_at.desc()).limit(limit).all()
    
    @classmethod
    def get_user_chats_by_model(cls, db_session, user_id: int, model_name: str) -> List['ChatHistory']:
        """获取用户使用特定模型的聊天记录"""
        return db_session.query(cls).filter(
            cls.created_by == user_id,
            cls.model_name == model_name,
            cls.is_deleted == False,
            cls.is_active == True
        ).order_by(cls.created_at.desc()).all()
    
    @classmethod
    def get_user_chat_stats(cls, db_session, user_id: int) -> Dict[str, Any]:
        """获取用户聊天统计信息"""
        from sqlalchemy import func as sql_func
        
        # 基础统计
        total_chats = db_session.query(cls).filter(
            cls.created_by == user_id,
            cls.is_deleted == False
        ).count()
        
        total_messages = db_session.query(sql_func.sum(cls.message_count)).filter(
            cls.created_by == user_id,
            cls.is_deleted == False
        ).scalar() or 0
        
        # 最近活动
        recent_chat = db_session.query(cls).filter(
            cls.created_by == user_id,
            cls.is_deleted == False
        ).order_by(cls.last_message_at.desc()).first()
        
        # 常用模型统计
        model_stats = db_session.query(
            cls.model_name,
            sql_func.count(cls.id).label('count')
        ).filter(
            cls.created_by == user_id,
            cls.is_deleted == False,
            cls.model_name.isnot(None)
        ).group_by(cls.model_name).order_by(sql_func.count(cls.id).desc()).all()
        
        return {
            'total_chats': total_chats,
            'total_messages': total_messages,
            'last_activity': recent_chat.last_message_at if recent_chat else None,
            'favorite_models': [{'model': stat[0], 'count': stat[1]} for stat in model_stats[:5]]
        }
    
    @classmethod
    def cleanup_old_deleted_chats(cls, db_session, days_old: int = 30) -> int:
        """清理指定天数前的已删除聊天记录"""
        from sqlalchemy import and_
        from datetime import timedelta
        
        cutoff_date = datetime.now() - timedelta(days=days_old)
        
        # 物理删除很久之前的软删除记录
        deleted_count = db_session.query(cls).filter(
            and_(
                cls.is_deleted == True,
                cls.deleted_at < cutoff_date
            )
        ).delete()
        
        return deleted_count
```

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


# 导出所有菜单页面处理函数
def get_menu_page_handlers():
    """获取所有菜单页面处理函数"""
    return {
        'home': home_content,
        'other_page': other_page_content,
        'chat_page': chat_page_content
    }

__all__ = [
    'home_content',
    'other_page_content',
    'chat_page_content',
    'get_menu_page_handlers'
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

- **webproduct_ui_template\menu_pages\other_demo_page.py**
```python
"""
log_handler.py 功能测试页面
全面测试所有日志功能,包括装饰器、日志级别、安全执行等
"""
from nicegui import ui
from datetime import datetime

# 导入 log_handler 所有功能
from common.log_handler import (
    # 日志记录函数
    log_trace, log_debug, log_info, log_success, log_warning, log_error, log_critical,
    # 安全执行
    safe, db_safe,
    # 装饰器
    safe_protect, catch,
    # Logger 实例
    get_logger,
    # 日志查询
    get_log_files, get_today_errors, get_today_logs_by_level,
    get_log_statistics, cleanup_logs
)

def other_page_content():
    """log_handler 测试页面内容"""
    
    # 页面标题
    with ui.column().classes('w-full mb-6'):
        ui.label('日志系统测试中心').classes('text-4xl font-bold text-blue-800 dark:text-blue-200 mb-2')
        ui.label('全面测试 log_handler.py 的所有功能').classes('text-lg text-gray-600 dark:text-gray-400')
    
    # 测试结果显示容器
    result_container = ui.column().classes('w-full')
    
    # ======================== 第一部分: 日志级别测试 ========================
    with ui.card().classes('w-full p-6 mb-4'):
        ui.label('1️⃣ 日志级别测试 (7个级别)').classes('text-2xl font-bold mb-4')
        
        with ui.row().classes('w-full gap-2 flex-wrap'):
            def test_log_levels():
                """测试所有7个日志级别"""
                result_container.clear()
                with result_container:
                    ui.label('🧪 测试所有日志级别...').classes('text-lg font-semibold mb-2')
                    
                    # 测试每个级别
                    log_trace("这是 TRACE 级别日志 - 最详细的调试信息")
                    ui.label('✅ TRACE: 已记录').classes('text-gray-600')
                    
                    log_debug("这是 DEBUG 级别日志 - 开发调试信息", 
                             extra_data='{"function": "test_log_levels", "line": 45}')
                    ui.label('✅ DEBUG: 已记录 (带额外数据)').classes('text-gray-600')
                    
                    log_info("这是 INFO 级别日志 - 普通运行信息")
                    ui.label('✅ INFO: 已记录').classes('text-blue-600')
                    
                    log_success("这是 SUCCESS 级别日志 - 操作成功标记")
                    ui.label('✅ SUCCESS: 已记录').classes('text-green-600')
                    
                    log_warning("这是 WARNING 级别日志 - 需要注意的情况")
                    ui.label('✅ WARNING: 已记录').classes('text-orange-600')
                    
                    try:
                        raise ValueError("模拟的错误异常")
                    except Exception as e:
                        log_error("这是 ERROR 级别日志 - 捕获的错误", exception=e)
                        ui.label('✅ ERROR: 已记录 (带异常堆栈)').classes('text-red-600')
                    
                    try:
                        raise RuntimeError("模拟的严重错误")
                    except Exception as e:
                        log_critical("这是 CRITICAL 级别日志 - 严重错误", exception=e,
                                   extra_data='{"severity": "high", "action": "alert_admin"}')
                        ui.label('✅ CRITICAL: 已记录 (带异常和额外数据)').classes('text-red-800 font-bold')
                    
                    ui.separator()
                    ui.label('📁 查看日志文件: logs/[今天日期]/app_logs.csv').classes('text-sm text-gray-500 mt-2')
                    ui.notify('所有日志级别测试完成!', type='positive')
            
            ui.button('测试所有日志级别', on_click=test_log_levels, icon='bug_report').classes('bg-blue-500')
    
    # ======================== 第二部分: safe() 函数测试 ========================
    with ui.card().classes('w-full p-6 mb-4'):
        ui.label('2️⃣ safe() 安全执行测试').classes('text-2xl font-bold mb-4')
        
        with ui.row().classes('w-full gap-2 flex-wrap'):
            def test_safe_success():
                """测试 safe() 成功场景"""
                result_container.clear()
                with result_container:
                    ui.label('🧪 测试 safe() 成功场景...').classes('text-lg font-semibold mb-2')
                    
                    def normal_function(a, b):
                        result = a + b
                        log_info(f"计算结果: {a} + {b} = {result}")
                        return result
                    
                    result = safe(normal_function, 10, 20)
                    ui.label(f'✅ 函数正常执行: 10 + 20 = {result}').classes('text-green-600 text-lg')
                    ui.notify('Safe 执行成功!', type='positive')
            
            def test_safe_error():
                """测试 safe() 错误场景"""
                result_container.clear()
                with result_container:
                    ui.label('🧪 测试 safe() 错误场景...').classes('text-lg font-semibold mb-2')
                    
                    def error_function():
                        raise ValueError("这是一个模拟的错误")
                    
                    result = safe(
                        error_function,
                        return_value="默认返回值",
                        show_error=True,
                        error_msg="函数执行失败,已返回默认值"
                    )
                    # error_function()
                    # result = "默认值"
                    ui.label(f'✅ 错误已捕获,返回默认值: "{result}"').classes('text-orange-600 text-lg')
                    ui.label('📝 错误已记录到日志,UI已显示通知').classes('text-sm text-gray-500')
            
            def test_safe_with_kwargs():
                """测试 safe() 带关键字参数"""
                result_container.clear()
                with result_container:
                    ui.label('🧪 测试 safe() 带参数...').classes('text-lg font-semibold mb-2')
                    
                    def process_user_data(user_id, name="", email="", phone=""):
                        log_info(f"处理用户数据: ID={user_id}, Name={name}, Email={email}")
                        return {"id": user_id, "name": name, "email": email, "phone": phone}
                    
                    result = safe(
                        process_user_data,
                        123,
                        name="张三",
                        email="zhangsan@test.com",
                        phone="13800138000",
                        return_value={}
                    )
                    ui.label(f'✅ 处理结果: {result}').classes('text-green-600')
                    ui.notify('带参数的 safe 执行成功!', type='positive')
            
            ui.button('测试正常执行', on_click=test_safe_success, icon='check_circle').classes('bg-green-500')
            ui.button('测试错误捕获', on_click=test_safe_error, icon='error').classes('bg-orange-500')
            ui.button('测试带参数', on_click=test_safe_with_kwargs, icon='settings').classes('bg-purple-500')
    
    # ======================== 第三部分: 装饰器测试 ========================
    with ui.card().classes('w-full p-6 mb-4'):
        ui.label('3️⃣ 装饰器测试').classes('text-2xl font-bold mb-4')
        
        with ui.row().classes('w-full gap-2 flex-wrap'):
            def test_safe_protect_decorator():
                """测试 @safe_protect 装饰器"""
                result_container.clear()
                with result_container:
                    ui.label('🧪 测试 @safe_protect 装饰器...').classes('text-lg font-semibold mb-2')
                    
                    @safe_protect(name="测试函数", error_msg="函数执行失败,已被保护")
                    def protected_function(should_fail=False):
                        log_info("进入被保护的函数")
                        if should_fail:
                            raise RuntimeError("模拟的错误")
                        return "执行成功"
                    
                    # 测试成功场景
                    result = protected_function(should_fail=False)
                    ui.label(f'✅ 正常执行: {result}').classes('text-green-600')
                    ui.seperator()
                    # 测试失败场景
                    result = protected_function(should_fail=True)
                    ui.label(f'✅ 错误已被装饰器捕获,返回: {result}').classes('text-orange-600')
                    ui.notify('safe_protect 装饰器测试完成!', type='positive')
            
            def test_catch_decorator():
                """测试 @catch 装饰器"""
                result_container.clear()
                with result_container:
                    ui.label('🧪 测试 @catch 装饰器...').classes('text-lg font-semibold mb-2')
                    
                    @catch(message="数据处理失败", show_ui_error=True)
                    def process_data(data):
                        log_info(f"处理数据: {data}")
                        if not data:
                            raise ValueError("数据不能为空")
                        return f"处理完成: {data}"
                    
                    # 正常场景
                    try:
                        result = process_data(["数据1", "数据2"])
                        ui.label(f'✅ 正常处理: {result}').classes('text-green-600')
                    except:
                        pass
                    
                    # 错误场景
                    try:
                        result = process_data(None)
                    except Exception as e:
                        ui.label(f'✅ 异常已被捕获: {type(e).__name__}').classes('text-orange-600')
                        ui.label('📝 详细堆栈已记录到日志').classes('text-sm text-gray-500')
            
            ui.button('测试 @safe_protect', on_click=test_safe_protect_decorator, icon='shield').classes('bg-indigo-500')
            ui.button('测试 @catch', on_click=test_catch_decorator, icon='security').classes('bg-cyan-500')
    
    # ======================== 第四部分: Logger 实例测试 ========================
    with ui.card().classes('w-full p-6 mb-4'):
        ui.label('4️⃣ get_logger() 实例测试').classes('text-2xl font-bold mb-4')
        
        with ui.row().classes('w-full gap-2 flex-wrap'):
            def test_get_logger():
                """测试 get_logger 获取自定义 logger"""
                result_container.clear()
                with result_container:
                    ui.label('🧪 测试 get_logger()...').classes('text-lg font-semibold mb-2')
                    
                    # 创建自定义 logger
                    log = get_logger(__file__)
                    
                    log.info("使用自定义 logger 记录 INFO")
                    ui.label('✅ INFO: 已记录').classes('text-blue-600')
                    
                    log.success("使用自定义 logger 记录 SUCCESS")
                    ui.label('✅ SUCCESS: 已记录').classes('text-green-600')
                    
                    log.warning("使用自定义 logger 记录 WARNING")
                    ui.label('✅ WARNING: 已记录').classes('text-orange-600')
                    
                    try:
                        raise ValueError("测试错误")
                    except Exception as e:
                        log.error(f"使用自定义 logger 记录 ERROR: {e}")
                        ui.label('✅ ERROR: 已记录').classes('text-red-600')
                    
                    ui.separator()
                    ui.label('💡 自定义 logger 会自动绑定用户上下文信息').classes('text-sm text-gray-500 mt-2')
                    ui.notify('get_logger 测试完成!', type='positive')
            
            ui.button('测试自定义 Logger', on_click=test_get_logger, icon='article').classes('bg-teal-500')
    
    # ======================== 第五部分: db_safe 测试 ========================
    with ui.card().classes('w-full p-6 mb-4'):
        ui.label('5️⃣ db_safe() 数据库安全测试').classes('text-2xl font-bold mb-4')
        
        with ui.row().classes('w-full gap-2 flex-wrap'):
            def test_db_safe():
                """测试 db_safe 数据库安全上下文"""
                result_container.clear()
                with result_container:
                    ui.label('🧪 测试 db_safe()...').classes('text-lg font-semibold mb-2')
                    
                    try:
                        with db_safe("测试数据库操作") as db:
                            ui.label('✅ 进入数据库安全上下文').classes('text-blue-600')
                            # 这里可以执行数据库操作
                            # user = db.query(User).first()
                            log_info("模拟数据库查询操作")
                            ui.label('✅ 数据库操作已记录').classes('text-green-600')
                    except Exception as e:
                        ui.label(f'⚠️ 数据库操作异常: {e}').classes('text-orange-600')
                    
                    ui.separator()
                    ui.label('💡 db_safe 会自动捕获异常、记录日志、回滚事务').classes('text-sm text-gray-500 mt-2')
                    ui.notify('db_safe 测试完成!', type='positive')
            
            ui.button('测试 db_safe', on_click=test_db_safe, icon='storage').classes('bg-purple-500')
    
    # ======================== 第六部分: 日志查询测试 ========================
    with ui.card().classes('w-full p-6 mb-4'):
        ui.label('6️⃣ 日志查询功能测试').classes('text-2xl font-bold mb-4')
        
        with ui.row().classes('w-full gap-2 flex-wrap'):
            def test_get_log_files():
                """查询最近的日志文件"""
                result_container.clear()
                with result_container:
                    ui.label('📂 查询最近7天的日志文件...').classes('text-lg font-semibold mb-2')
                    
                    files = get_log_files(days=7)
                    
                    if files:
                        ui.label(f'找到 {len(files)} 个日志文件:').classes('text-blue-600 mb-2')
                        for f in files[:10]:  # 最多显示10个
                            ui.label(f"📄 {f['date']} - {f['type']} ({f['size']} bytes)").classes('text-sm')
                    else:
                        ui.label('暂无日志文件').classes('text-gray-500')
                    
                    ui.notify('日志文件查询完成!', type='info')
            
            def test_get_today_errors():
                """查询今天的错误日志"""
                result_container.clear()
                with result_container:
                    ui.label('🔍 查询今天的错误日志...').classes('text-lg font-semibold mb-2')
                    
                    errors = get_today_errors(limit=10)
                    
                    if errors:
                        ui.label(f'找到 {len(errors)} 条错误日志:').classes('text-red-600 mb-2')
                        for err in errors[:5]:  # 最多显示5条
                            ui.label(f"❌ [{err['timestamp']}] {err['message']}").classes('text-sm text-red-500')
                    else:
                        ui.label('✅ 今天暂无错误日志').classes('text-green-600')
                    
                    ui.notify('错误日志查询完成!', type='info')
            
            def test_get_log_statistics():
                """获取日志统计信息"""
                result_container.clear()
                with result_container:
                    ui.label('📊 获取日志统计信息...').classes('text-lg font-semibold mb-2')
                    
                    stats = get_log_statistics(days=7)
                    
                    ui.label(f"📈 统计周期: 最近7天").classes('text-blue-600 mb-2')
                    ui.label(f"总日志数: {stats['total_logs']}").classes('text-sm')
                    ui.label(f"错误数量: {stats['error_count']}").classes('text-sm text-red-600')
                    ui.label(f"警告数量: {stats['warning_count']}").classes('text-sm text-orange-600')
                    ui.label(f"信息数量: {stats['info_count']}").classes('text-sm text-green-600')
                    
                    if stats['by_level']:
                        ui.separator()
                        ui.label('按级别统计:').classes('text-sm font-semibold mt-2')
                        for level, count in stats['by_level'].items():
                            ui.label(f"  {level}: {count}").classes('text-xs')
                    
                    ui.notify('统计信息获取完成!', type='info')
            
            def test_get_logs_by_level():
                """按级别查询日志"""
                result_container.clear()
                with result_container:
                    ui.label('🎯 按级别查询今天的日志...').classes('text-lg font-semibold mb-2')
                    
                    # 查询 SUCCESS 级别
                    success_logs = get_today_logs_by_level(level="SUCCESS", limit=5)
                    ui.label(f'✅ SUCCESS 级别: {len(success_logs)} 条').classes('text-green-600')
                    
                    # 查询 WARNING 级别
                    warning_logs = get_today_logs_by_level(level="WARNING", limit=5)
                    ui.label(f'⚠️ WARNING 级别: {len(warning_logs)} 条').classes('text-orange-600')
                    
                    # 查询 ERROR 级别
                    error_logs = get_today_logs_by_level(level="ERROR", limit=5)
                    ui.label(f'❌ ERROR 级别: {len(error_logs)} 条').classes('text-red-600')
                    
                    ui.notify('按级别查询完成!', type='info')
            
            ui.button('查询日志文件', on_click=test_get_log_files, icon='folder').classes('bg-blue-500')
            ui.button('查询今天错误', on_click=test_get_today_errors, icon='error_outline').classes('bg-red-500')
            ui.button('日志统计', on_click=test_get_log_statistics, icon='analytics').classes('bg-green-500')
            ui.button('按级别查询', on_click=test_get_log_statistics, icon='filter_list').classes('bg-purple-500')
    
    # ======================== 第七部分: 综合场景测试 ========================
    with ui.card().classes('w-full p-6 mb-4'):
        ui.label('7️⃣ 综合场景测试').classes('text-2xl font-bold mb-4')
        
        with ui.row().classes('w-full gap-2 flex-wrap'):
            def test_comprehensive_scenario():
                """综合场景: 模拟真实业务流程"""
                result_container.clear()
                with result_container:
                    ui.label('🎬 模拟用户注册流程 (综合测试)...').classes('text-lg font-semibold mb-2')
                    
                    log_info("========== 用户注册流程开始 ==========")
                    ui.label('1️⃣ 开始用户注册流程').classes('text-blue-600')
                    
                    # 步骤1: 验证输入
                    log_debug("验证用户输入数据", extra_data='{"step": 1}')
                    ui.label('  ✓ 步骤1: 验证输入数据').classes('text-sm text-gray-600')
                    
                    # 步骤2: 检查用户名
                    username = "test_user_" + str(datetime.now().timestamp())[:10]
                    log_info(f"检查用户名可用性: {username}")
                    ui.label(f'  ✓ 步骤2: 用户名检查 ({username})').classes('text-sm text-gray-600')
                    
                    # 步骤3: 数据库操作(使用 db_safe)
                    try:
                        with db_safe("创建用户记录"):
                            log_info(f"创建用户记录: {username}")
                            ui.label('  ✓ 步骤3: 数据库操作').classes('text-sm text-gray-600')
                    except Exception as e:
                        log_error("数据库操作失败", exception=e)
                    
                    # 步骤4: 发送欢迎邮件(可能失败)
                    def send_welcome_email(email):
                        log_info(f"发送欢迎邮件到: {email}")
                        # 模拟随机失败
                        import random
                        if random.random() < 0.3:
                            raise ConnectionError("邮件服务器连接失败")
                        return True
                    
                    result = safe(
                        send_welcome_email,
                        "test@example.com",
                        return_value=False,
                        show_error=False,
                        error_msg="邮件发送失败,将稍后重试"
                    )
                    
                    if result:
                        log_success(f"用户注册成功: {username}")
                        ui.label('  ✓ 步骤4: 欢迎邮件已发送').classes('text-sm text-gray-600')
                        ui.separator()
                        ui.label('✅ 注册流程完成!').classes('text-xl text-green-600 font-bold mt-2')
                    else:
                        log_warning("邮件发送失败,但用户已创建")
                        ui.label('  ⚠️ 步骤4: 邮件发送失败(将重试)').classes('text-sm text-orange-600')
                        ui.separator()
                        ui.label('⚠️ 注册完成,但邮件待发送').classes('text-xl text-orange-600 font-bold mt-2')
                    
                    log_info("========== 用户注册流程结束 ==========")
                    ui.notify('综合场景测试完成!', type='positive')
            
            ui.button('运行综合场景', on_click=test_comprehensive_scenario, icon='rocket_launch').classes('bg-gradient-to-r from-purple-500 to-pink-500 text-lg px-6 py-3')
    
    # ======================== 底部说明 ========================
    with ui.card().classes('w-full p-6 bg-blue-50 dark:bg-blue-900/20'):
        ui.label('📋 日志文件位置').classes('text-xl font-bold mb-3')
        ui.label('日志保存在 logs/[日期]/ 目录下:').classes('text-sm mb-2')
        ui.label('  • app.log - 所有级别的日志(文本格式)').classes('text-xs text-gray-600')
        ui.label('  • error.log - 仅错误和严重错误(文本格式)').classes('text-xs text-gray-600')
        ui.label('  • app_logs.csv - CSV格式日志(便于查询分析)').classes('text-xs text-gray-600')
        
        ui.separator().classes('my-3')
        
        ui.label('💡 使用建议').classes('text-xl font-bold mb-3')
        ui.label('1. 先运行各个测试,生成日志记录').classes('text-sm')
        ui.label('2. 然后查看 logs/ 目录下的日志文件').classes('text-sm')
        ui.label('3. CSV 文件可用 Excel 或文本编辑器打开查看').classes('text-sm')
        ui.label('4. 观察不同日志级别的输出格式和内容').classes('text-sm')
```

## webproduct_ui_template\scripts

- **webproduct_ui_template\scripts\__init__.py** *(包初始化文件 - 空)*
```python

```

- **webproduct_ui_template\scripts\database_migrate.py**
```python

```

- **webproduct_ui_template\scripts\deploy.py**
```python

```

- **webproduct_ui_template\scripts\health_check.py**
```python

```

- **webproduct_ui_template\scripts\init_database.py**
```python
#!/usr/bin/env python3
"""
独立的数据库初始化脚本 - 复用现有ORM模型
使用方法：python scripts/init_database.py [--test-data] [--reset] [--verbose]
"""
import os
import sys
import logging
import argparse
from pathlib import Path
from contextlib import contextmanager

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def setup_logging(verbose=False):
    """设置日志"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )
    return logging.getLogger(__name__)

class DatabaseInitializer:
    """数据库初始化器 - 复用现有模型"""
    
    def __init__(self, logger):
        self.logger = logger
        self.engine = None
        self.SessionLocal = None
    
    def create_engine_and_session(self):
        """创建数据库引擎和会话"""
        try:
            from sqlalchemy import create_engine, event
            from sqlalchemy.orm import sessionmaker
            from auth.config import auth_config  # 使用项目的配置
            
            # 使用项目配置的数据库URL
            self.engine = create_engine(
                auth_config.database_url,
                pool_pre_ping=True,
                echo=False
            )
            
            # 为SQLite启用外键约束
            if auth_config.database_type == 'sqlite':
                @event.listens_for(self.engine, "connect")
                def set_sqlite_pragma(dbapi_connection, connection_record):
                    cursor = dbapi_connection.cursor()
                    cursor.execute("PRAGMA foreign_keys=ON")
                    cursor.close()
            
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
            self.logger.info(f"✅ 数据库引擎创建成功: {auth_config.database_type}")
            self.logger.info(f"📍 数据库位置: {auth_config.database_url}")
            
        except Exception as e:
            self.logger.error(f"❌ 数据库引擎创建失败: {e}")
            raise
    
    @contextmanager
    def get_db_session(self):
        """获取数据库会话的上下文管理器"""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            self.logger.error(f"数据库操作失败: {e}")
            raise
        finally:
            session.close()
    
    def import_all_models(self):
        """导入所有现有模型"""
        try:
            self.logger.info("开始导入现有模型...")
            
            # 导入认证模型（从auth包）
            from auth.models import User, Role, Permission, LoginLog
            # 导入关联表
            from auth.models import user_roles, role_permissions, user_permissions
            self.logger.info("✅ 认证模型导入成功")
            
            # 导入业务模型（从database_models包）
            from database_models.business_models.chat_history_model import ChatHistory
            # self.logger.info("✅ 审计业务模型导入成功")
            
            self.logger.info("✅ 所有模型导入完成")
            
            # 返回模型类以便后续使用
            return {
                'User': User,
                'Role': Role, 
                'Permission': Permission,
                'LoginLog': LoginLog,
                'ChatHistory': ChatHistory
            }
            
        except ImportError as e:
            self.logger.error(f"❌ 模型导入失败: {e}")
            raise
    
    def create_all_tables(self):
        """创建所有表"""
        try:
            # 导入模型
            models = self.import_all_models()
            
            # 获取Base类（从auth.database）
            from auth.database import Base
            
            # 创建所有表
            Base.metadata.create_all(bind=self.engine)
            self.logger.info("✅ 所有数据表创建成功")
            
            return models
            
        except Exception as e:
            self.logger.error(f"❌ 表创建失败: {e}")
            raise
    
    def init_default_roles_and_permissions(self, models):
        """初始化默认角色和权限"""
        try:
            with self.get_db_session() as db:
                Role = models['Role']
                Permission = models['Permission']
                
                # 检查是否已初始化
                if db.query(Role).first() is not None:
                    self.logger.info("角色和权限已存在，跳过初始化")
                    return
                
                # 使用auth_config中的默认角色配置
                from auth.config import auth_config
                
                # 创建默认角色
                for role_data in auth_config.default_roles:
                    role = Role(**role_data)
                    db.add(role)
                
                # 创建默认权限（使用auth_config中的配置，并添加OpenAI相关权限）
                permissions_data = list(auth_config.default_permissions)  # 复制基础权限
                
                # 添加OpenAI相关权限
                openai_permissions = [
                    {'name': 'openai.view', 'display_name': '查看OpenAI配置', 'category': 'openai'},
                    {'name': 'openai.create', 'display_name': '创建OpenAI配置', 'category': 'openai'},
                    {'name': 'openai.edit', 'display_name': '编辑OpenAI配置', 'category': 'openai'},
                    {'name': 'openai.delete', 'display_name': '删除OpenAI配置', 'category': 'openai'},
                    {'name': 'openai.use', 'display_name': '使用OpenAI对话', 'category': 'openai'},
                    {'name': 'openai.manage_api_key', 'display_name': '管理API密钥', 'category': 'openai'},
                ]
                permissions_data.extend(openai_permissions)
                
                # 添加更多业务权限
                additional_permissions = [
                    {'name': 'profile.view', 'display_name': '查看个人资料', 'category': 'profile'},
                    {'name': 'profile.edit', 'display_name': '编辑个人资料', 'category': 'profile'},
                    {'name': 'password.change', 'display_name': '修改密码', 'category': 'profile'},
                ]
                permissions_data.extend(additional_permissions)
                
                for perm_data in permissions_data:
                    permission = Permission(**perm_data)
                    db.add(permission)
                
                db.commit()
                self.logger.info("✅ 默认角色和权限初始化完成")
                
        except Exception as e:
            self.logger.error(f"❌ 默认角色和权限初始化失败: {e}")
            raise
    
    def init_role_permissions(self, models):
        """初始化角色权限关系"""
        try:
            with self.get_db_session() as db:
                Role = models['Role']
                Permission = models['Permission']
                
                # 获取角色
                admin_role = db.query(Role).filter(Role.name == 'admin').first()
                user_role = db.query(Role).filter(Role.name == 'user').first()
                editor_role = db.query(Role).filter(Role.name == 'editor').first()
                viewer_role = db.query(Role).filter(Role.name == 'viewer').first()
                
                if not all([admin_role, user_role, editor_role, viewer_role]):
                    self.logger.warning("部分角色不存在，跳过权限分配")
                    return
                
                # 清除现有权限关联
                for role in [admin_role, user_role, editor_role, viewer_role]:
                    role.permissions.clear()
                
                # 获取所有权限
                all_permissions = db.query(Permission).all()
                openai_view = db.query(Permission).filter(Permission.name == 'openai.view').first()
                openai_use = db.query(Permission).filter(Permission.name == 'openai.use').first()
                profile_perms = db.query(Permission).filter(Permission.category == 'profile').all()
                
                # 分配权限
                # 管理员：所有权限
                admin_role.permissions.extend(all_permissions)
                
                # 编辑者：OpenAI相关权限 + 个人资料
                editor_permissions = db.query(Permission).filter(
                    Permission.category.in_(['openai', 'profile'])
                ).all()
                editor_role.permissions.extend(editor_permissions)
                
                # 查看者：查看权限 + 个人资料
                viewer_permissions = [openai_view] + profile_perms
                viewer_role.permissions.extend([p for p in viewer_permissions if p])
                
                # 普通用户：基础权限
                user_permissions = [openai_view, openai_use] + profile_perms
                user_role.permissions.extend([p for p in user_permissions if p])
                
                db.commit()
                self.logger.info("✅ 角色权限关系初始化完成")
                
        except Exception as e:
            self.logger.error(f"❌ 角色权限关系初始化失败: {e}")
            raise
    
    def init_test_users(self, models, create_test_data=False):
        """初始化测试用户"""
        if not create_test_data:
            self.logger.info("跳过测试用户创建")
            return
        
        try:
            with self.get_db_session() as db:
                User = models['User']
                Role = models['Role']
                
                # 检查是否已有用户
                if db.query(User).count() > 0:
                    self.logger.info("用户已存在，跳过测试用户创建")
                    return
                
                # 获取角色
                admin_role = db.query(Role).filter(Role.name == 'admin').first()
                user_role = db.query(Role).filter(Role.name == 'user').first()
                editor_role = db.query(Role).filter(Role.name == 'editor').first()
                viewer_role = db.query(Role).filter(Role.name == 'viewer').first()
                
                # 创建测试用户
                users_data = [
                    {
                        'user_data': {
                            'username': 'admin',
                            'email': 'admin@example.com',
                            'full_name': '系统管理员',
                            'is_active': True,
                            'is_verified': True,
                            'is_superuser': True
                        },
                        'password': 'admin123',
                        'roles': [admin_role] if admin_role else []
                    },
                    {
                        'user_data': {
                            'username': 'user',
                            'email': 'user@example.com',
                            'full_name': '普通用户',
                            'is_active': True,
                            'is_verified': True
                        },
                        'password': 'user123',
                        'roles': [user_role] if user_role else []
                    },
                    {
                        'user_data': {
                            'username': 'editor',
                            'email': 'editor@example.com',
                            'full_name': '内容编辑',
                            'is_active': True,
                            'is_verified': True
                        },
                        'password': 'editor123',
                        'roles': [editor_role] if editor_role else []
                    },
                    {
                        'user_data': {
                            'username': 'viewer',
                            'email': 'viewer@example.com',
                            'full_name': '查看用户',
                            'is_active': True,
                            'is_verified': True
                        },
                        'password': 'viewer123',
                        'roles': [viewer_role] if viewer_role else []
                    }
                ]
                
                for user_info in users_data:
                    user = User(**user_info['user_data'])
                    user.set_password(user_info['password'])
                    user.roles.extend(user_info['roles'])
                    db.add(user)
                
                db.commit()
                
                self.logger.info("✅ 测试用户创建完成")
                self.logger.info("🔐 测试账户信息:")
                self.logger.info("   管理员: admin / admin123")
                self.logger.info("   普通用户: user / user123") 
                self.logger.info("   编辑者: editor / editor123")
                self.logger.info("   查看者: viewer / viewer123")
                
        except Exception as e:
            self.logger.error(f"❌ 测试用户创建失败: {e}")
            raise
    
    def init_business_default_data(self, models):
        """初始化业务默认数据"""
        try:
            # self._init_openai_default_data(models)
            # 在这里添加其他业务模块的默认数据初始化
            # self._init_mongodb_default_data(models)
            # self._init_audit_default_data(models)
            
            self.logger.info("✅ 业务默认数据初始化完成")
            
        except Exception as e:
            self.logger.error(f"❌ 业务默认数据初始化失败: {e}")
            raise
    
    def _init_openai_default_data(self, models):
        """初始化OpenAI模块的默认数据"""
        try:
            with self.get_db_session() as db:
                OpenAIConfig = models['OpenAIConfig']
                
                # 检查是否已有配置
                if db.query(OpenAIConfig).first() is not None:
                    self.logger.info("OpenAI配置已存在，跳过默认数据创建")
                    return
                
                # 导入枚举类型
                from database_models.business_models.openai_models import ModelType
                
                # 创建默认配置
                default_config = OpenAIConfig(
                    name="DeepSeek默认配置",
                    api_key="sk-example-key-replace-with-real-key",
                    base_url="https://api.deepseek.com/v1",
                    model_name=ModelType.DEEPSEEK,
                    max_tokens=1000,
                    temperature=70,
                    is_public=True,
                    description="系统默认的DeepSeek配置，请管理员更新API密钥"
                )
                
                db.add(default_config)
                db.commit()
                
                self.logger.info("✅ OpenAI默认配置创建完成")
                
        except Exception as e:
            self.logger.error(f"❌ OpenAI默认数据初始化失败: {e}")
            raise
    
    def run_full_initialization(self, create_test_data=False, reset_if_exists=False):
        """运行完整的数据库初始化"""
        self.logger.info("🚀 开始数据库完整初始化...")
        
        try:
            # 1. 创建引擎和会话
            self.create_engine_and_session()
            
            # 2. 重置数据库（如果需要）
            if reset_if_exists:
                self.logger.warning("🔄 重置现有数据库...")
                from auth.database import Base
                Base.metadata.drop_all(bind=self.engine)
                self.logger.info("✅ 数据库已重置")
            
            # 3. 创建所有表并导入模型
            models = self.create_all_tables()
            
            # 4. 初始化默认角色和权限
            self.init_default_roles_and_permissions(models)
            
            # 5. 初始化角色权限关系
            self.init_role_permissions(models)
            
            # 6. 初始化业务默认数据
            self.init_business_default_data(models)
            
            # 7. 创建测试用户（如果需要）
            if create_test_data:
                self.init_test_users(models, create_test_data=True)
            
            self.logger.info("🎉 数据库初始化完成！")
            
        except Exception as e:
            self.logger.error(f"❌ 数据库初始化失败: {e}")
            raise

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='数据库初始化脚本')
    parser.add_argument('--test-data', action='store_true', help='创建测试用户数据')
    parser.add_argument('--reset', action='store_true', help='重置现有数据库')
    parser.add_argument('--verbose', action='store_true', help='详细输出')
    
    args = parser.parse_args()
    
    # 设置日志
    logger = setup_logging(args.verbose)
    
    # 初始化数据库
    initializer = DatabaseInitializer(logger)
    
    try:
        initializer.run_full_initialization(
            create_test_data=args.test_data,
            reset_if_exists=args.reset
        )
        
        print("\n✅ 数据库初始化成功！")
        if args.test_data:
            print("🔐 测试用户已创建:")
            print("   管理员: admin / admin123")
            print("   普通用户: user / user123")
            print("   编辑者: editor / editor123")
            print("   查看者: viewer / viewer123")
        
    except Exception as e:
        print(f"\n❌ 数据库初始化失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

- **webproduct_ui_template\scripts\start_services.py**
```python

```

## webproduct_ui_template\services

- **webproduct_ui_template\services\__init__.py** *(包初始化文件 - 空)*
```python

```
