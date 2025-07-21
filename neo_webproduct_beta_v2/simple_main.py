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
    init_database
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
    config.app_title = 'MCP智能平台 - Header版'  # 修改标题以区分布局

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
                {'key': 'enterprise_archive', 'label': '一企一档', 'icon': 'business', 'route': 'enterprise_archive'},
                {'key': 'person_archive', 'label': '一人一档', 'icon': 'person', 'route': 'person_archive','separator_after': True},
                # {'key': 'data', 'label': '智能审计', 'icon': 'policy', 'route': 'data'},
                # {'key': 'analysis', 'label': '智能问数', 'icon': 'question_answer', 'route': 'analysis'},
                # {'key': 'mcp', 'label': 'MCP服务', 'icon': 'api', 'route': 'mcp'},
                # {'key': 'about', 'label': '关于', 'icon': 'info', 'route': 'about'}
            ],
            # header_config_items=[
            #     {'key': 'search', 'icon': 'search', 'label': '查询', 'route': 'search_page'},
            #     {'key': 'messages', 'icon': 'mail', 'label': '消息', 'route': 'messages_page'},
            #     {'key': 'contact', 'label': '联系我们', 'icon': 'support', 'route': 'contact_page'},
            # ],
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
        reload=True,
        favicon='🚀',
        dark=False,
        storage_secret='your-secret-key-here'
    )