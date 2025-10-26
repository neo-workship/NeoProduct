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
    
    # ==================== 其他组件 ====================
    # 聊天组件
    'ChatComponent',
    
    # 静态资源
    'StaticResourceManager',
    'static_manager'
]


# 版本信息
__version__ = '2.0.0'  # 新增多层布局,升级到2.0

# 布局类型常量
LAYOUT_TYPE_SPA = 'spa'                    # 复杂布局(左侧菜单栏)
LAYOUT_TYPE_SIMPLE = 'simple'              # 简单布局(顶部导航栏)
LAYOUT_TYPE_MULTILAYER = 'multilayer'      # 多层布局(折叠菜单)

# 使用说明
USAGE_GUIDE = """
==================== 布局组件使用指南 ====================

📌 三种布局模式:

1️⃣ SPA布局 (spa_layout) - 左侧固定菜单栏
   适用场景: 传统后台管理系统,菜单项较少(5-10个)
   
   from component import with_spa_layout, LayoutConfig
   
   @with_spa_layout(
       config=LayoutConfig(),
       menu_items=[...],
       route_handlers={...}
   )
   def main_page():
       pass

2️⃣ 简单布局 (simple_spa_layout) - 顶部导航栏
   适用场景: 简洁的门户网站,菜单项很少(3-5个)
   
   from component import with_simple_spa_layout
   
   @with_simple_spa_layout(
       nav_items=[...],
       route_handlers={...}
   )
   def main_page():
       pass

3️⃣ 多层布局 (multilayer_spa_layout) - 折叠菜单 ⭐新增
   适用场景: 功能复杂的系统,需要分类管理大量菜单(10+个)
   
   from component import (
       with_multilayer_spa_layout, 
       MultilayerMenuItem
   )
   
   menu_items = [
       MultilayerMenuItem(
           key='group1',
           label='功能分组1',
           icon='folder',
           children=[
               MultilayerMenuItem(
                   key='page1',
                   label='页面1',
                   icon='article',
                   route='page1'
               ),
           ]
       ),
   ]
   
   @with_multilayer_spa_layout(
       menu_items=menu_items,
       route_handlers={...}
   )
   def main_page():
       pass

==================== 快速开始 ====================

1. 查看演示: 运行 multilayer_main.py
2. 参考文档: 查看各模块的 __doc__ 字符串
3. 示例代码: component/multilayer_menu_config.py 中的 create_demo_menu_config()

========================================================
"""

def print_usage_guide():
    """打印使用指南"""
    print(USAGE_GUIDE)

# 如果直接运行此模块,显示使用指南
if __name__ == '__main__':
    print_usage_guide()