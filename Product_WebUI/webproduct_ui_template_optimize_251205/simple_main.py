"""
简单布局主应用入口 - 只包含顶部导航栏的布局
"""
from nicegui import ui, app
import secrets
from config.env_config import env_config  # 导入环境变量配置
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
                {'key': 'auth_page', 'label': 'AuthTest', 'icon': 'security', 'route': 'auth_test','separator_after': True},

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

    storage_secret = env_config.get('APP_STORAGE_SECRET')
    if not storage_secret:
        storage_secret = secrets.token_urlsafe(32)
    ui.run(
        title=env_config.get('APP_TITLE', 'NeoUI布局模板'),
        port=env_config.get_int('APP_PORT', 8080),
        show=env_config.get_bool('APP_SHOW', True),
        reload=env_config.get_bool('APP_RELOAD', True),   # 设置为True，控制台中会输出两次
        favicon=env_config.get('APP_FAVICON', '🚀'),
        dark=env_config.get_bool('APP_DARK', False),
        prod_js=env_config.get_bool('APP_PROD_JS', False),
        storage_secret=secrets.token_urlsafe(32)
    )