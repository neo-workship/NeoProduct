from nicegui import ui, app
from component import with_spa_layout, LayoutConfig, static_manager
from menu_pages import get_menu_page_handlers
from header_pages import get_header_page_handlers

if __name__ in {"__main__", "__mp_main__"}:
    # 获取所有页面处理函数
    menu_handlers = get_menu_page_handlers()
    header_handlers = get_header_page_handlers()
    # 合并所有路由处理器
    all_route_handlers = {**menu_handlers, **header_handlers}
    # 创建自定义配置
    config = LayoutConfig()
    @ui.page('/')
    @with_spa_layout(
        config=config,
        menu_items=[
            {'key': 'home', 'label': '首页', 'icon': 'home', 'route': 'home'},
            {'key': 'dashboard', 'label': '看板', 'icon': 'dashboard', 'route': 'dashboard', 'separator_after': True},
            {'key': 'data', 'label': '连接数据', 'icon': 'electrical_services', 'route': 'data'},
            {'key': 'analysis', 'label': '智能问数', 'icon': 'question_answer', 'route': 'analysis'},
            {'key': 'mcp', 'label': 'mcp服务', 'icon': 'api', 'route': 'mcp', 'separator_after': True},
            {'key': 'about', 'label': '关于', 'icon': 'info', 'route': 'about'}
        ],
        header_config_items=[
            {'key': 'search', 'icon': 'search', 'label': '查询', 'route': 'search_page'},
            {'key': 'messages', 'icon': 'mail', 'label': '消息', 'route': 'messages_page'},
            {'key': 'notifications', 'icon': 'notifications', 'label': '提醒', 'route': 'notifications_page'},
            {'key': 'contact', 'label': '联系我们', 'icon': 'support', 'route': 'contact_page'}
        ],
        route_handlers=all_route_handlers
    )
    def main_page():
        """主页面入口函数"""
        pass

    # 启动应用
    print("🌐 启动应用服务器...")
    ui.run(
        title=config.app_title, 
        port=8080, 
        show=True,
        reload=True,
        favicon='🚀',
        dark=False
    )