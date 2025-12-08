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
                {'key': 'one_page', 'label': 'AI对话', 'icon': 'business', 'route': 'chat_page'},
                {'key': 'two_page', 'label': '日志测试', 'icon': 'people', 'route': 'other_page','separator_after': True},
                {'key': 'auth_page', 'label': 'AuthTest', 'icon': 'security', 'route': 'auth_test','separator_after': True},
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