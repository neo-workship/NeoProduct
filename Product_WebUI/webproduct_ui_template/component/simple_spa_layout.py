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