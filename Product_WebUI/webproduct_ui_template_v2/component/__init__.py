# 原有的复杂布局（包含侧边栏）
from .layout_config import LayoutConfig, MenuItem, HeaderConfigItem
from .layout_manager import LayoutManager
from .spa_layout import with_spa_layout, create_spa_layout, get_layout_manager, register_route_handler, navigate_to
from .static_resources import StaticResourceManager, static_manager

# 新增的简单布局（只有顶部导航栏）
from .simple_layout_manager import SimpleLayoutManager
from .simple_spa_layout import (
    with_simple_spa_layout, 
    create_simple_spa_layout, 
    get_simple_layout_manager, 
    register_simple_route_handler, 
    simple_navigate_to
)

# 导出聊天组件
from .chat import ChatComponent

__all__ = [
    # 布局配置
    'LayoutConfig',
    'MenuItem',
    'HeaderConfigItem',
    
    # 复杂布局（原有）
    'LayoutManager',
    'with_spa_layout',
    'create_spa_layout',
    'get_layout_manager',
    'register_route_handler',
    'navigate_to',
    
    # 简单布局（新增）
    'SimpleLayoutManager',
    'with_simple_spa_layout',
    'create_simple_spa_layout',
    'get_simple_layout_manager',
    'register_simple_route_handler',
    'simple_navigate_to',

    # 聊天组件
    'ChatComponent',  # 新增导出
    
    # 静态资源
    'StaticResourceManager',
    'static_manager'
]