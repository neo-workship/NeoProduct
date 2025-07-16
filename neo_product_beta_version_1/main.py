"""
主应用入口 - 集成认证功能
"""
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
    get_auth_page_handlers,
    init_database
)

# 初始化测试数据
def init_test_data():
    """创建测试用户（仅在开发环境使用）"""
    from auth.database import get_db
    from auth.models import User, Role
    
    with get_db() as db:
        # 检查是否已有用户
        if db.query(User).count() > 0:
            return
        
        # 获取角色
        admin_role = db.query(Role).filter(Role.name == 'admin').first()
        user_role = db.query(Role).filter(Role.name == 'user').first()
        
        # 创建管理员
        admin = User(
            username='admin',
            email='admin@example.com',
            full_name='系统管理员',
            is_active=True,
            is_verified=True,
            is_superuser=True
        )
        admin.set_password('admin123')
        if admin_role:
            admin.roles.append(admin_role)
        
        # 创建普通用户
        user = User(
            username='user',
            email='user@example.com',
            full_name='测试用户',
            is_active=True,
            is_verified=True
        )
        user.set_password('user123')
        if user_role:
            user.roles.append(user_role)
        
        db.add(admin)
        db.add(user)
        db.commit()
       
        print("✅ 测试数据初始化完成")

# 创建受保护的页面处理器
def create_protected_handlers():
    """为需要认证的页面添加装饰器"""
    menu_handlers = get_menu_page_handlers()
    header_handlers = get_header_page_handlers()
    system_handlers = get_auth_page_handlers()
    
    return {**menu_handlers, **header_handlers,**system_handlers}

if __name__ in {"__main__", "__mp_main__"}:
    # 初始化数据库和测试数据
    init_database()
    init_test_data()

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
                {'key': 'home', 'label': '首页', 'icon': 'home', 'route': 'home'},
                {'key': 'dashboard', 'label': '看板', 'icon': 'dashboard', 'route': 'dashboard', 'separator_after': True},
                {'key': 'data', 'label': '智能审计', 'icon': 'policy', 'route': 'data'},
                {'key': 'analysis', 'label': '智能问数', 'icon': 'question_answer', 'route': 'analysis'},
                {'key': 'mcp', 'label': 'MCP服务', 'icon': 'api', 'route': 'mcp', 'separator_after': True},
                {'key': 'about', 'label': '关于', 'icon': 'info', 'route': 'about'}
            ],
            header_config_items=[
                {'key': 'search', 'icon': 'search', 'label': '查询', 'route': 'search_page'},
                {'key': 'messages', 'icon': 'mail', 'label': '消息', 'route': 'messages_page'},
                {'key': 'contact', 'label': '联系我们', 'icon': 'support', 'route': 'contact_page'},
            ],
            route_handlers=protected_handlers
        )
        def spa_layout():
            pass

        spa_layout()

    # 启动应用
    print("🌐 启动应用服务器...")
    print("📝 测试账号：")
    print("   管理员 - 用户名: admin, 密码: admin123")
    print("   普通用户 - 用户名: user, 密码: user123")
    print("🔄 支持页面刷新保持路由状态（基于存储）")

    @app.on_startup
    def redirect_to_workbench():
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