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