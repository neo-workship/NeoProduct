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