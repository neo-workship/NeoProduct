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

            menu_items_to_use = menu_items if menu_items is not None else [
                {'key': 'home', 'label': '首页', 'icon': 'home', 'route': 'home'},
                {'key': 'dashboard', 'label': '看板', 'icon': 'dashboard', 'route': 'dashboard', 'separator_after': True},
                {'key': 'data', 'label': '连接数据', 'icon': 'electrical_services', 'route': 'data'},
                {'key': 'analysis', 'label': '智能问数', 'icon': 'question_answer', 'route': 'analysis'},
                {'key': 'mcp', 'label': 'mcp服务', 'icon': 'api', 'route': 'mcp', 'separator_after': True},
                {'key': 'about', 'label': '关于', 'icon': 'info', 'route': 'about'}
            ]
            for item in menu_items_to_use:
                layout_manager.add_menu_item(item['key'], item['label'], item['icon'], item.get('route'), item.get('separator_after', False))

            if header_config_items is not None:
                for item in header_config_items:
                    layout_manager.add_header_config_item(item['key'], item.get('label'), item.get('icon'), item.get('route'), item.get('on_click'))

            if route_handlers:
                for route, handler in route_handlers.items():
                    layout_manager.set_route_handler(route, handler)

            # 确保默认的设置和用户中心路由处理器存在
            if 'settings_page' not in layout_manager.route_handlers:
                layout_manager.set_route_handler('settings_page', lambda: ui.label('系统设置页面 (默认)').classes('text-3xl'))
            if 'user_profile_page' not in layout_manager.route_handlers:
                layout_manager.set_route_handler('user_profile_page', lambda: ui.label('用户中心页面 (默认)').classes('text-3xl'))

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
                label = route
    layout_manager.navigate_to_route(route, label)

def create_spa_layout(config: Optional[LayoutConfig] = None,
                      menu_items: Optional[List[Dict[str, Any]]] = None,
                      header_config_items: Optional[List[Dict[str, Any]]] = None,
                      route_handlers: Optional[Dict[str, Callable]] = None) -> LayoutManager:
    global current_layout_manager
    layout_config = config or LayoutConfig()
    layout_manager = LayoutManager(layout_config)
    current_layout_manager = layout_manager

    menu_items_to_use = menu_items if menu_items is not None else [
        {'key': 'home', 'label': '首页', 'icon': 'home', 'route': 'home'},
        {'key': 'dashboard', 'label': '看板', 'icon': 'dashboard', 'route': 'dashboard', 'separator_after': True},
        {'key': 'data', 'label': '连接数据', 'icon': 'electrical_services', 'route': 'data'},
        {'key': 'analysis', 'label': '智能问数', 'icon': 'question_answer', 'route': 'analysis'},
        {'key': 'mcp', 'label': 'mcp服务', 'icon': 'api', 'route': 'mcp', 'separator_after': True},
        {'key': 'about', 'label': '关于', 'icon': 'info', 'route': 'about'}
    ]
    for item in menu_items_to_use:
        layout_manager.add_menu_item(item['key'], item['label'], item['icon'], item.get('route'), item.get('separator_after', False))

    if header_config_items is not None:
        for item in header_config_items:
            layout_manager.add_header_config_item(item['key'], item.get('label'), item.get('icon'), item.get('route'), item.get('on_click'))

    if route_handlers:
        for route, handler in route_handlers.items():
            layout_manager.set_route_handler(route, handler)

    # 确保默认的设置和用户中心路由处理器存在
    if 'settings_page' not in layout_manager.route_handlers:
        layout_manager.set_route_handler('settings_page', lambda: ui.label('系统设置页面 (默认)').classes('text-3xl'))
    if 'user_profile_page' not in layout_manager.route_handlers:
        layout_manager.set_route_handler('user_profile_page', lambda: ui.label('用户中心页面 (默认)').classes('text-3xl'))

    layout_manager.create_header()
    layout_manager.create_left_drawer()
    layout_manager.create_content_area()

    return layout_manager