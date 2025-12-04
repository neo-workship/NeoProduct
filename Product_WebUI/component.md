# component

- **component\__init__.py** *(包初始化文件)*
```python
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
```

- **component\layout_config.py**
```python
from typing import Optional, Callable
from .static_resources import static_manager

class LayoutConfig:
    """布局配置类"""
    def __init__(self):
        self.app_title = 'NeoUI模板'
        self.app_icon = static_manager.get_logo_path('robot.svg')
        self.header_bg = 'bg-[#3874c8] dark:bg-gray-900'
        self.drawer_bg = 'bg-[#ebf1fa] dark:bg-gray-800'
        self.drawer_width = 'w-64'
        self.menu_title = '菜单栏'
        # 新增：自定义CSS文件路径
        self.custom_css = static_manager.get_css_path('custom.css')
        # 新增：favicon路径
        self.favicon = static_manager.get_image_path('logo', 'favicon.ico')

class MenuItem:
    """菜单项类"""
    def __init__(self, key: str, label: str, icon: str, route: Optional[str] = None, separator_after: bool = False, custom_icon_path: Optional[str] = None):
        self.key = key
        self.label = label
        self.icon = icon
        self.route = route  # 路由标识（用于SPA内部切换）
        self.separator_after = separator_after
        # 新增：自定义图标路径（如果提供则使用自定义图标而非Material Icons）
        self.custom_icon_path = custom_icon_path

class HeaderConfigItem:
    """头部配置项类"""
    def __init__(self, key: str, label: Optional[str] = None, icon: Optional[str] = None, route: Optional[str] = None, on_click: Optional[Callable] = None, custom_icon_path: Optional[str] = None):
        self.key = key
        self.label = label
        self.icon = icon
        self.route = route
        self.on_click = on_click
        # 新增：自定义图标路径
        self.custom_icon_path = custom_icon_path
```

- **component\layout_manager.py**
```python
from nicegui import ui, app
from typing import List, Dict, Callable, Optional
from .layout_config import LayoutConfig, MenuItem, HeaderConfigItem
from common.log_handler import (
    # 日志记录函数
    log_trace, log_debug, log_info, log_success, 
    log_warning, log_error, log_critical,
    # 安全执行
    safe, db_safe,
    # 装饰器
    safe_protect, catch,
    # Logger 实例
    get_logger
)
logger = get_logger(__file__)

class LayoutManager:
    """布局管理器 - 完整的路由状态管理"""
    def __init__(self, config: LayoutConfig):
        self.config = config
        self.menu_items: List[MenuItem] = []
        self.header_config_items: List[HeaderConfigItem] = []
        self.selected_menu_item_row = {'element': None, 'key': None}
        self.content_container = None
        self.left_drawer = None
        self.dark_mode = None
        self.route_handlers: Dict[str, Callable] = {}
        self.current_route = None
        self.menu_rows: Dict[str, any] = {}
        
        # 主题切换
        self._theme_key = 'theme' 
        initial_theme = app.storage.user.get(self._theme_key, False)
        app.storage.user[self._theme_key] = initial_theme   # 确保键存在
        # 新增：所有可能的路由映射
        self.all_routes: Dict[str, str] = {}  # route -> label 的映射

    def add_menu_item(self, key: str, label: str, icon: str, route: Optional[str] = None, separator_after: bool = False):
        """添加菜单项"""
        self.menu_items.append(MenuItem(key, label, icon, route, separator_after))
        # 注册路由映射
        if route:
            self.all_routes[route] = label

    def add_header_config_item(self, key: str, label: Optional[str] = None, icon: Optional[str] = None, route: Optional[str] = None, on_click: Optional[Callable] = None):
        """添加头部配置项"""
        self.header_config_items.append(HeaderConfigItem(key, label, icon, route, on_click))
        # 注册路由映射
        if route:
            self.all_routes[route] = label or key

    def set_route_handler(self, route: str, handler: Callable):
        """设置路由处理器"""
        self.route_handlers[route] = handler        
        # 如果路由映射中没有这个路由，添加一个默认标签
        if route not in self.all_routes:
            self.all_routes[route] = route.replace('_', ' ').title()

    def register_system_routes(self):
        """注册系统路由（设置菜单、用户菜单等）"""
        system_routes = {
            # 设置菜单路由
            'user_management': '用户管理',
            'role_management': '角色管理', 
            'permission_management': '权限管理',
            # ✅ 新增: 配置管理路由
            'llm_config_management': '大模型配置',
            'prompt_config_management': '提示词配置',  # ✅ 新增
            # 用户菜单路由（排除logout）
            'user_profile': '个人资料',
            'change_password': '修改密码',
            # 注意：不包含 'logout'，因为注销是一次性操作，不应该被恢复
            # 其他系统路由
            'no_permission': '权限不足',
            'login': '登录',
            'register': '注册'
        }
        
        for route, label in system_routes.items():
            self.all_routes[route] = label
            
        logger.debug(f"🔧 已注册系统路由: {list(system_routes.keys())}")
        logger.debug(f"🔧 注册的全部路由：{self.all_routes}")
        logger.debug(f"⚠️ 注意：logout 路由未注册到持久化路由中（一次性操作）")

    def select_menu_item(self, key: str, row_element=None, update_storage: bool = True):
        """选择菜单项"""
        if self.selected_menu_item_row['key'] == key:
            return

        # 清除之前的选中状态
        if self.selected_menu_item_row['element'] is not None:
            self.selected_menu_item_row['element'].classes(remove='bg-blue-200 dark:bg-blue-700')

        # 设置新的选中状态
        target_row = row_element or self.menu_rows.get(key)
        if target_row:
            target_row.classes(add='bg-blue-200 dark:bg-blue-700')
            self.selected_menu_item_row['element'] = target_row
        
        self.selected_menu_item_row['key'] = key

        menu_item = next((item for item in self.menu_items if item.key == key), None)
        if not menu_item:
            return

        ui.notify(f'切换到{menu_item.label}')

        if menu_item.route:
            self.navigate_to_route(menu_item.route, menu_item.label, update_storage)
        else:
            if self.content_container:
                self.content_container.clear()
                with self.content_container:
                    ui.label(f'{menu_item.label}内容').classes('text-2xl font-bold text-gray-800 dark:text-gray-200')

    def clear_menu_selection(self):
        """清除菜单选中状态（用于非菜单路由）"""
        if self.selected_menu_item_row['element'] is not None:
            self.selected_menu_item_row['element'].classes(remove='bg-blue-200 dark:bg-blue-700')
            self.selected_menu_item_row['element'] = None
            self.selected_menu_item_row['key'] = None

    def navigate_to_route(self, route: str, label: str, update_storage: bool = True):
        """导航到指定路由"""
        if self.current_route == route:
            return
        
        self.current_route = route
        # 如果不是菜单路由，清除菜单选中状态
        is_menu_route = any(item.route == route for item in self.menu_items)
        if not is_menu_route:
            self.clear_menu_selection()
        
        # 保存当前路由到存储（排除一次性操作路由）
        if update_storage and self._should_persist_route(route):
            try:
                app.storage.user['current_route'] = route
                logger.debug(f"💾 保存路由状态: {route}")
            except Exception as e:
                logger.debug(f"⚠️ 保存路由状态失败: {e}")
        elif not self._should_persist_route(route):
            logger.debug(f"🚫 跳过路由持久化: {route} (一次性操作)")
        
        if self.content_container:
            self.content_container.clear()

        if route in self.route_handlers:
            with self.content_container:
                try:
                    self.route_handlers[route]()
                except Exception as e:
                    logger.debug(f"❌ 路由处理器执行失败 {route}: {e}")
                    ui.label(f'页面加载失败: {str(e)}').classes('text-red-500 text-xl')
        else:
            logger.debug(f"❌ 未找到路由处理器: {route}")
            with self.content_container:
                ui.label(f'页面未找到: {label}').classes('text-2xl font-bold text-red-600')
                ui.label(f'路由 "{route}" 没有对应的处理器').classes('text-gray-600 dark:text-gray-400 mt-4')

    def _should_persist_route(self, route: str) -> bool:
        """判断路由是否应该持久化"""
        # 一次性操作路由，不应该被持久化
        non_persistent_routes = {
            'logout',      # 注销操作
            'login',       # 登录页面
            'register',    # 注册页面
        }
        return route not in non_persistent_routes

    def clear_route_storage(self):
        """清除路由存储（用于注销等场景）"""
        try:
            if 'current_route' in app.storage.user:
                del app.storage.user['current_route']
                logger.debug("🗑️ 已清除路由存储")
        except Exception as e:
            logger.debug(f"⚠️ 清除路由存储失败: {e}")

    def restore_route_from_storage(self):
        """从存储恢复路由状态 - 支持所有类型的路由"""
        try:
            # 从存储获取保存的路由
            saved_route = app.storage.user.get('current_route')
            
            # 如果没有保存的路由
            if not saved_route:
                # 如果有菜单项，选择第一个
                if self.menu_items:
                    first_item = self.menu_items[0]
                    self.select_menu_item(first_item.key, update_storage=True)
                else:
                    # 如果没有菜单项，不做任何操作
                    logger.debug("🔄 没有保存的路由，且未定义菜单项，保持空白状态")
                return
            
            # 检查路由是否在已知路由中
            if saved_route in self.all_routes:
                route_label = self.all_routes[saved_route]
                logger.debug(f"✅ 找到路由映射: {saved_route} -> {route_label}")
                
                # 检查是否是菜单项路由
                menu_item = next((item for item in self.menu_items if item.route == saved_route), None)
                if menu_item:
                    # 恢复菜单选中状态
                    self.select_menu_item(menu_item.key, update_storage=False)
                else:
                    # 直接导航到路由（不更新存储避免循环）
                    self.navigate_to_route(saved_route, route_label, update_storage=False)
                return
            
            # 兜底检查：是否在路由处理器中注册
            if saved_route in self.route_handlers:
                label = saved_route.replace('_', ' ').title()
                self.navigate_to_route(saved_route, label, update_storage=False)
                return
            
            # 如果都没找到，且有菜单项，选择第一个菜单项
            logger.debug(f"⚠️ 未找到保存的路由 {saved_route}，使用默认路由")
            if self.menu_items:
                first_item = self.menu_items[0]
                self.select_menu_item(first_item.key, update_storage=True)
            else:
                logger.debug("⚠️ 没有可用的菜单项，保持空白状态")
                
        except Exception as e:
            logger.debug(f"⚠️ 恢复路由状态失败: {e}")
            if self.menu_items:
                first_item = self.menu_items[0]
                self.select_menu_item(first_item.key, update_storage=True)
            else:
                logger.debug("⚠️ 没有可用的菜单项，保持空白状态")

    def handle_header_config_item_click(self, item: HeaderConfigItem):
        """处理头部配置项点击事件"""
        ui.notify(f'点击了头部配置项: {item.label or item.key}')
        if item.on_click:
            item.on_click()
        
        if item.route:
            self.navigate_to_route(item.route, item.label or item.key)

    def handle_settings_menu_item_click(self, route: str, label: str):
        """处理设置菜单项点击事件"""        
        from auth.auth_manager import auth_manager

        if not auth_manager.is_authenticated():
            ui.notify('请先登录', type='warning')
            self.navigate_to_route('login', '登录')
            return

        if not auth_manager.has_role('admin') and not auth_manager.current_user.is_superuser:
            ui.notify('您没有管理员权限，无法访问此功能', type='error')
            self.navigate_to_route('no_permission', '权限不足')
            return

        ui.notify(f'访问管理功能: {label}')
        self.navigate_to_route(route, label)

    def handle_user_menu_item_click(self, route: str, label: str):
        """处理用户菜单项点击事件"""
        ui.notify(f'点击了用户菜单项: {label}')
        
        # 特殊处理注销：清除路由存储
        if route == 'logout':
            logger.debug("🚪 执行用户注销，清除路由存储")
            self.clear_route_storage()
        
        self.navigate_to_route(route, label)

    def create_header(self):
        """创建头部"""
        with ui.header(elevated=True).classes(f'items-center justify-between px-4 {self.config.header_bg}'):
            with ui.row().classes('items-center gap-4'):
                ui.button(
                    on_click=lambda: self.left_drawer.toggle(),
                    icon='menu'
                ).props('flat color=white').classes('mr-2')

                with ui.avatar().classes('w-15 h-15'):
                    ui.image(self.config.app_icon).classes('w-full h-full object-contain')
                ui.label(self.config.app_title).classes('ml-4 text-xl font-medium text-white dark:text-white')

            with ui.row().classes('items-center gap-2'):
                # 头部配置项
                for item in self.header_config_items:
                    if item.icon and item.label:
                        ui.button(item.label, icon=item.icon, on_click=lambda current_item=item: self.handle_header_config_item_click(current_item)).props('flat color=white').classes('mr-2')
                    elif item.icon:
                        ui.button(icon=item.icon, on_click=lambda current_item=item: self.handle_header_config_item_click(current_item)).props('flat color=white round').classes('w-10 h-10')
                    elif item.label:
                        ui.button(item.label, on_click=lambda current_item=item: self.handle_header_config_item_click(current_item)).props('flat color=white').classes('mr-2')
                if self.header_config_items:
                    # ui.separator().props('vertical').classes('h-10')
                    ui.label("|")

                # 主题切换
                # self.dark_mode = ui.dark_mode()
                # ui.switch('主题切换').bind_value(self.dark_mode)
                self.dark_mode = ui.dark_mode(value=app.storage.user[self._theme_key])
                ui.switch('主题切换') \
                    .bind_value(self.dark_mode) \
                    .on_value_change(lambda e: app.storage.user.update({self._theme_key: e.value})) \
                    .classes('mx-2')

                # 设置菜单
                with ui.button(icon='settings').props('flat color=white round').classes('w-10 h-10'):
                    with ui.menu() as settings_menu:
                        ui.menu_item('用户管理', lambda: self.handle_settings_menu_item_click('user_management', '用户管理'))
                        ui.menu_item('角色管理', lambda: self.handle_settings_menu_item_click('role_management', '角色管理'))
                        ui.menu_item('权限管理', lambda: self.handle_settings_menu_item_click('permission_management', '权限管理'))
                        # ✅ 新增: 配置管理菜单项
                        ui.separator()  # 分隔线
                        ui.menu_item('大模型配置', lambda: self.handle_settings_menu_item_click('llm_config_management', '大模型配置'))
                        ui.menu_item('提示词配置', lambda: self.handle_settings_menu_item_click('prompt_config_management', '提示词配置'))  # ✅ 新增

                # 用户菜单
                with ui.button(icon='account_circle').props('flat color=white round').classes('w-10 h-10'):
                    with ui.menu() as user_menu:
                        ui.menu_item('个人资料', lambda: self.handle_user_menu_item_click('user_profile', '个人资料'))
                        ui.menu_item('修改密码', lambda: self.handle_user_menu_item_click('change_password', '修改密码'))
                        ui.separator()
                        ui.menu_item('注销', lambda: self.handle_user_menu_item_click('logout', '注销'))

    def create_left_drawer(self):
        """创建左侧抽屉"""
        with ui.left_drawer(fixed=False).props('bordered').classes(f'{self.config.drawer_width} {self.config.drawer_bg}') as left_drawer:
            self.left_drawer = left_drawer

            ui.label(self.config.menu_title).classes('w-full text-lg font-semibold text-gray-800 dark:text-gray-200 p-4 border-b border-gray-200 dark:border-gray-700')

            with ui.column().classes('w-full p-2 gap-1'):
                # 只有当有菜单项时才创建菜单
                if self.menu_items:
                    for menu_item in self.menu_items:
                        with ui.row().classes('w-full cursor-pointer rounded-lg hover:bg-blue-100 dark:hover:bg-blue-800 transition-colors duration-200 p-3') as menu_row:
                            ui.icon(menu_item.icon).classes('text-blue-600 mr-3 text-lg font-bold')
                            ui.label(menu_item.label).classes('text-gray-800 dark:text-gray-200 flex-1 text-lg font-bold')

                            menu_row.on('click', lambda key=menu_item.key, row=menu_row: self.select_menu_item(key, row))
                            # 保存菜单行引用
                            self.menu_rows[menu_item.key] = menu_row

                        if menu_item.separator_after:
                            ui.separator().classes('dark:bg-gray-700')
                else:
                    # 如果没有菜单项，显示提示信息
                    with ui.column().classes('w-full items-center py-8'):
                        ui.icon('menu_open').classes('text-6xl text-gray-400 mb-4')
                        ui.label('暂无菜单项').classes('text-lg font-medium text-gray-500 dark:text-gray-400')
                        ui.label('请通过头部导航或其他方式访问功能').classes('text-sm text-gray-400 dark:text-gray-500 text-center')

                # 注册系统路由并恢复路由状态
                def init_routes():
                    self.register_system_routes()
                    self.restore_route_from_storage()
                
                ui.timer(0.3, init_routes, once=True)

    def create_content_area(self):
        """创建内容区域"""
        with ui.column().classes('w-full') as content_container:
            self.content_container = content_container
```

- **component\multilayer_layout_manager.py**
```python
"""
多层布局管理器
实现多层级折叠菜单的UI渲染和交互逻辑
✨ 优化版本: 改善了菜单项间距,使其更加美观舒适
"""
from nicegui import ui, app
from typing import List, Dict, Callable, Optional, Set
from .layout_config import LayoutConfig, HeaderConfigItem
from .multilayer_menu_config import MultilayerMenuItem, MultilayerMenuConfig
from common.log_handler import (
    # 日志记录函数
    log_trace, log_debug, log_info, log_success, log_warning, log_error, log_critical,
    # 安全执行
    safe, db_safe,
    # 装饰器
    safe_protect, catch,
    # Logger 实例
    get_logger
)
logger = get_logger(__file__)

class MultilayerLayoutManager:
    """多层布局管理器 - 支持折叠菜单的完整布局管理"""
    
    def __init__(self, config: LayoutConfig):
        self.config = config
        self.menu_config = MultilayerMenuConfig()
        self.header_config_items: List[HeaderConfigItem] = []
        
        # UI组件引用
        self.content_container = None
        self.left_drawer = None
        self.dark_mode = None
        
        # 路由和状态管理
        self.route_handlers: Dict[str, Callable] = {}
        self.current_route = None
        self.current_label = None
        
        # 展开状态管理
        self.expanded_keys: Set[str] = set()          # 当前展开的父节点keys
        self.selected_leaf_key: Optional[str] = None  # 当前选中的叶子节点key
        
        # UI元素引用映射
        self.expansion_refs: Dict[str, any] = {}  # key -> ui.expansion对象
        self.leaf_refs: Dict[str, any] = {}       # key -> 叶子节点ui.row对象
        
        # 存储键
        self._route_key = 'multilayer_current_route'
        self._label_key = 'multilayer_current_label'
        self._expanded_keys_key = 'multilayer_expanded_keys'
        self._theme_key = 'theme'
        
        # 初始化主题
        initial_theme = app.storage.user.get(self._theme_key, False)
        app.storage.user[self._theme_key] = initial_theme
        
        # 所有可能的路由映射
        self.all_routes: Dict[str, str] = {}
    
    def add_menu_item(self, item: MultilayerMenuItem):
        """添加顶层菜单项"""
        self.menu_config.add_menu_item(item)
        self._update_route_mappings()
    
    def _update_route_mappings(self):
        """更新路由映射"""
        self.all_routes.update(self.menu_config.get_all_routes())
    
    def add_header_config_item(self, key: str, label: Optional[str] = None, 
                              icon: Optional[str] = None, route: Optional[str] = None, 
                              on_click: Optional[Callable] = None):
        """添加头部配置项"""
        self.header_config_items.append(
            HeaderConfigItem(key=key, label=label, icon=icon, route=route, on_click=on_click)
        )
    
    def set_route_handler(self, route: str, handler: Callable):
        """设置路由处理器"""
        self.route_handlers[route] = handler
    
    def _add_drawer_scrollbar_styles(self):
        """添加抽屉滚动条样式"""
        ui.add_head_html('''
            <style>
            /* 多层布局抽屉滚动条样式 - 参考chat_component的滚动条设置 */
            .multilayer-drawer {
                overflow-y: auto;
                overflow-x: hidden;   /* ✨ 关键修复1: 禁用水平滚动 */
                border-right: 1px solid #e5e7eb;
            }
            
            /* 菜单内容区域滚动条 */
            .multilayer-menu-content {
                overflow-y: auto;
                overflow-x: hidden;  /* ✨ 关键修复2: 禁用水平滚动 */
                max-height: calc(100vh - 100px);
                border-right: 1px solid #e5e7eb;
            }
                         
            /* Webkit浏览器(Chrome, Safari, Edge)滚动条样式 */
            .multilayer-drawer::-webkit-scrollbar,
            .multilayer-menu-content::-webkit-scrollbar {
                width: 1px;
            }
            
            .multilayer-drawer::-webkit-scrollbar-track,
            .multilayer-menu-content::-webkit-scrollbar-track {
                background: transparent;
            }
            
            .multilayer-drawer::-webkit-scrollbar-thumb,
            .multilayer-menu-content::-webkit-scrollbar-thumb {
                background-color: #d1d5db;
                border-radius: 1px;
            }
            
            .multilayer-drawer::-webkit-scrollbar-thumb:hover,
            .multilayer-menu-content::-webkit-scrollbar-thumb:hover {
                background-color: #9ca3af;
            }
            
            /* Firefox滚动条样式 */
            .multilayer-drawer,
            .multilayer-menu-content {
                scrollbar-width: thin;
                scrollbar-color: #d1d5db transparent;
            }
            
            /* 暗色主题滚动条 */
            .dark .multilayer-drawer::-webkit-scrollbar-thumb,
            .dark .multilayer-menu-content::-webkit-scrollbar-thumb {
                background-color: #4b5563;
            }
            
            .dark .multilayer-drawer::-webkit-scrollbar-thumb:hover,
            .dark .multilayer-menu-content::-webkit-scrollbar-thumb:hover {
                background-color: #6b7280;
            }
            
            .dark .multilayer-drawer,
            .dark .multilayer-menu-content {
                scrollbar-color: #4b5563 transparent;
            }
            </style>
        ''')
    
    def create_header(self):
        """创建头部"""
        with ui.header(elevated=True).classes(f'items-center justify-between px-4 {self.config.header_bg}'):
            with ui.row().classes('items-center gap-4'):
                # 菜单按钮
                ui.button(
                    on_click=lambda: self.left_drawer.toggle(),
                    icon='menu'
                ).props('flat color=white').classes('mr-2')
                
                # Logo和标题
                with ui.avatar().classes('cursor-pointer'):
                    ui.image(self.config.app_icon).classes('w-10 h-10')
                
                ui.label(self.config.app_title).classes('text-xl font-bold text-white')
            
            with ui.row().classes('items-center gap-2'):
                # 头部配置项
                for current_item in self.header_config_items:
                    ui.button(
                        icon=current_item.icon,
                        on_click=lambda item=current_item: self.handle_header_config_item_click(item)
                    ).props('flat color=white').classes('mr-2')
                
                if self.header_config_items:
                    # ui.separator().props('vertical').classes('h-8')
                    ui.label("|")
                
                # 主题切换
                self.dark_mode = ui.dark_mode(value=app.storage.user[self._theme_key])
                ui.switch('主题切换') \
                    .bind_value(self.dark_mode) \
                    .on_value_change(lambda e: app.storage.user.update({self._theme_key: e.value})) \
                    .classes('mx-2')
                
                # 设置菜单
                with ui.button(icon='settings').props('flat color=white round').classes('w-10 h-10'):
                    with ui.menu():
                        ui.menu_item('用户管理', lambda: self.handle_settings_menu_item_click('user_management', '用户管理'))
                        ui.menu_item('角色管理', lambda: self.handle_settings_menu_item_click('role_management', '角色管理'))
                        ui.menu_item('权限管理', lambda: self.handle_settings_menu_item_click('permission_management', '权限管理'))
                        ui.separator()
                        ui.menu_item('大模型配置', lambda: self.handle_settings_menu_item_click('llm_config_management', '大模型配置'))
                        ui.menu_item('提示词配置', lambda: self.handle_settings_menu_item_click('prompt_config_management', '提示词配置'))
                
                # 用户菜单
                with ui.button(icon='account_circle').props('flat color=white round').classes('w-10 h-10'):
                    with ui.menu():
                        ui.menu_item('个人资料', lambda: self.handle_user_menu_item_click('user_profile', '个人资料'))
                        ui.menu_item('修改密码', lambda: self.handle_user_menu_item_click('change_password', '修改密码'))
                        ui.separator()
                        ui.menu_item('注销', lambda: self.handle_user_menu_item_click('logout', '注销'))
    
    def create_left_drawer(self):
        """创建左侧抽屉(多层菜单)
        
        ✨ 优化说明:
        1. 将菜单内容区域的 gap 从 gap-1 改为 gap-3,增加菜单项之间的间距
        2. 在 expansion 组件上添加 my-2 类,为展开面板增加垂直外边距
        3. 在叶子节点 row 上添加 my-1 类,为每个菜单项增加轻微的垂直外边距
        4. 调整了整体的 padding,使菜单显示更加舒适
        """
        # 添加自定义滚动条样式
        self._add_drawer_scrollbar_styles()
        
        with ui.left_drawer(fixed=False).props('bordered').classes(
            f'{self.config.drawer_width} {self.config.drawer_bg}'
        ) as left_drawer:
            self.left_drawer = left_drawer
            
            # 菜单标题
            ui.label(self.config.menu_title).classes(
                'w-full text-lg font-semibold text-gray-800 dark:text-gray-200 p-4 '
                'border-b border-gray-200 dark:border-gray-700'
            )
            
            # ✨ 优化点1: 将 gap-1 改为 gap-3,增加菜单项之间的间距
            # ✨ 优化点2: 调整 padding 为 p-3,使整体更舒适
            with ui.column().classes('w-full p-3 gap-2 multilayer-menu-content'):
                if self.menu_config.menu_items:
                    for item in self.menu_config.menu_items:
                        self._render_menu_item(item)
                        
                        if item.separator_after:
                            # ✨ 优化点6: 分隔符使用 -my-1.5,抵消部分 gap-3 的间距
                            # 解释: gap-3(12px) + separator自身 + (-my-1.5 即 -6px) ≈ 合理的分隔间距
                            ui.separator().classes('dark:bg-gray-700 -my-1.5')
                else:
                    # 无菜单项提示
                    with ui.column().classes('w-full items-center py-8'):
                        ui.icon('menu_open').classes('text-6xl text-gray-400 mb-4')
                        ui.label('暂无菜单项').classes('text-lg font-medium text-gray-500 dark:text-gray-400')
    
    def _render_menu_item(self, item: MultilayerMenuItem, level: int = 0):
        """递归渲染菜单项
        
        ✨ 优化说明:
        1. 为 expansion 组件添加 my-2 类,增加垂直外边距
        2. 为叶子节点的 row 添加 my-1 类,增加轻微的垂直外边距
        3. 适当调整 padding,使菜单项内容更加舒适
        """
        indent_class = f'ml-{level * 4}' if level > 0 else ''
        
        if item.is_parent:
            # ✨ 优化点3: 为父节点添加 my-2 类,增加垂直外边距
            # 父节点:使用expansion
            with ui.expansion(
                text=item.label,
                icon=item.icon,
                value=item.expanded or (item.key in self.expanded_keys)
            ).classes(f'w-full {indent_class} my-2').props('dense') as expansion:
                # 保存expansion引用
                self.expansion_refs[item.key] = expansion
                
                # 监听展开/收起事件
                expansion.on_value_change(
                    lambda e, key=item.key: self._handle_expansion_change(key, e.value)
                )
                
                # 递归渲染子节点
                for child in item.children:
                    self._render_menu_item(child, level + 1)
        
        else:
            # ✨ 优化点4: 为叶子节点添加 my-1 类,增加轻微的垂直外边距
            # ✨ 优化点5: 将 padding 从 p-3 调整为 py-3 px-4,使内容更加舒适
            # 叶子节点:可点击的行
            with ui.row().classes(
                f'w-full cursor-pointer rounded-lg hover:bg-blue-100 dark:hover:bg-blue-800 '
                f'transition-colors duration-200 py-3 px-4 items-center {indent_class} my-1'
            ) as leaf_row:
                ui.icon(item.icon).classes('text-blue-600 dark:text-blue-400 mr-3 text-lg')
                ui.label(item.label).classes('text-gray-800 dark:text-gray-200 flex-1')
                
                # 保存叶子节点引用
                self.leaf_refs[item.key] = leaf_row
                
                # 绑定点击事件
                leaf_row.on('click', lambda key=item.key: self.select_leaf_item(key))
    
    def _handle_expansion_change(self, key: str, value: bool):
        """处理展开/收起事件"""
        if value:
            self.expand_parent(key, update_storage=True)
        else:
            self.collapse_parent(key, update_storage=True)
    
    def create_content_area(self):
        """创建内容区域"""
        with ui.column().classes('w-full') as content_container:
            self.content_container = content_container
    
    def navigate_to_route(self, route: str, label: str, update_storage: bool = True):
        """导航到指定路由"""
        # print(f"🚀 导航到路由: {route} ({label})")
        
        self.current_route = route
        self.current_label = label
        
        if update_storage:
            app.storage.user[self._route_key] = route
            app.storage.user[self._label_key] = label
        
        # 清空内容区域
        if self.content_container:
            self.content_container.clear()
        
        # 渲染新内容
        with self.content_container:
            # 查找菜单项以显示面包屑
            menu_item = self.menu_config.find_by_route(route)
            if menu_item:
                self._render_breadcrumb(menu_item)
            
            # 执行路由处理器
            if route in self.route_handlers:
                self.route_handlers[route]()
            else:
                # 默认显示
                with ui.column().classes('w-full items-center justify-center py-16'):
                    ui.icon('info').classes('text-6xl text-blue-500 mb-4')
                    ui.label(f'当前页面: {label}').classes('text-2xl font-bold text-gray-800 dark:text-gray-200')
                    ui.label(f'路由: {route}').classes('text-gray-600 dark:text-gray-400 mt-2')
    
    def _render_breadcrumb(self, item: MultilayerMenuItem):
        """渲染面包屑导航"""
        breadcrumb = []
        current_key = item.key
        
        while current_key:
            current_item = self.menu_config.find_by_key(current_key)
            if current_item:
                breadcrumb.insert(0, current_item.label)
                current_key = current_item.parent_key
            else:
                break
        
        if breadcrumb:
            with ui.row().classes('items-center gap-2 mb-4 text-gray-600 dark:text-gray-400'):
                ui.icon('home').classes('text-lg')
                for i, label in enumerate(breadcrumb):
                    if i > 0:
                        ui.icon('chevron_right').classes('text-sm')
                    ui.label(label).classes('text-sm')
    
    def select_leaf_item(self, key: str, update_storage: bool = True):
        """选中叶子节点"""
        item = self.menu_config.find_by_key(key)
        if not item or not item.is_leaf:
            log_warning(f"⚠️ 节点 {key} 不是有效的叶子节点")
            return        
        # 清除之前的选中状态
        if self.selected_leaf_key and self.selected_leaf_key in self.leaf_refs:
            old_row = self.leaf_refs[self.selected_leaf_key]
            old_row.classes(remove='bg-blue-200 dark:bg-blue-700')
        # 设置新的选中状态
        if key in self.leaf_refs:
            new_row = self.leaf_refs[key]
            new_row.classes(add='bg-blue-200 dark:bg-blue-700')
        
        self.selected_leaf_key = key
        
        # 确保父节点展开
        parent_chain = self.menu_config.get_parent_chain_keys(key)
        for parent_key in parent_chain:
            if parent_key not in self.expanded_keys:
                self.expand_parent(parent_key, update_storage=False)
        
        # 导航到对应路由
        if item.route:
            self.navigate_to_route(item.route, item.label, update_storage=update_storage)
    
    def expand_parent(self, key: str, update_storage: bool = True):
        """展开父节点"""
        if key in self.expanded_keys:
            return
        self.expanded_keys.add(key)
        if key in self.expansion_refs:
            expansion = self.expansion_refs[key]
            expansion.open()
        if update_storage:
            self._save_expanded_state()
    
    def collapse_parent(self, key: str, update_storage: bool = True):
        """收起父节点"""
        if key not in self.expanded_keys:
            return
        self.expanded_keys.remove(key)
        if key in self.expansion_refs:
            expansion = self.expansion_refs[key]
            expansion.close()
        if update_storage:
            self._save_expanded_state()
            
    def _save_expanded_state(self):
        """保存展开状态到存储"""
        app.storage.user[self._expanded_keys_key] = list(self.expanded_keys)
    
    def _load_expanded_state(self):
        """从存储加载展开状态"""
        stored_keys = app.storage.user.get(self._expanded_keys_key, [])
        self.expanded_keys = set(stored_keys)
    
    def handle_header_config_item_click(self, item: HeaderConfigItem):
        """处理头部配置项点击"""
        if item.on_click:
            item.on_click()
        elif item.route:
            self.navigate_to_route(item.route, item.label or item.key)
    
    def handle_settings_menu_item_click(self, route: str, label: str):
        """处理设置菜单项点击"""
        self.navigate_to_route(route, label)
    
    def handle_user_menu_item_click(self, route: str, label: str):
        """处理用户菜单项点击"""
        if route == 'logout':
            logger.debug("🚪 执行用户注销，清除路由存储")
            self.clear_route_storage()
        self.navigate_to_route(route, label)
    
    def clear_route_storage(self):
        """清除路由存储"""
        if self._route_key in app.storage.user:
            del app.storage.user[self._route_key]
        if self._label_key in app.storage.user:
            del app.storage.user[self._label_key]
        if self._expanded_keys_key in app.storage.user:
            del app.storage.user[self._expanded_keys_key]
    
    def restore_route_from_storage(self):
        """从存储恢复路由"""
        stored_route = app.storage.user.get(self._route_key)
        stored_label = app.storage.user.get(self._label_key)
        
        # 加载展开状态
        self._load_expanded_state()
        
        if stored_route and stored_route in self.all_routes:            
            # 查找对应的菜单项
            menu_item = self.menu_config.find_by_route(stored_route)
            if menu_item and menu_item.is_leaf:
                self.select_leaf_item(menu_item.key, update_storage=False)
            else:
                self.navigate_to_route(stored_route, stored_label, update_storage=False)
        else:
            # 默认路由
            if self.menu_config.menu_items:
                first_leaf = self.menu_config.get_first_leaf()
                if first_leaf:
                    self.select_leaf_item(first_leaf.key)
    
    def register_system_routes(self):
        """注册系统路由"""
        system_routes = {
            # 设置菜单路由
            'user_management': '用户管理',
            'role_management': '角色管理', 
            'permission_management': '权限管理',
            # ✅ 新增: 配置管理路由
            'llm_config_management': '大模型配置',
            'prompt_config_management': '提示词配置',  # ✅ 新增
            # 用户菜单路由（排除logout）
            'user_profile': '个人资料',
            'change_password': '修改密码',
            # 其他系统路由
            'no_permission': '权限不足',
            'login': '登录',
            'register': '注册'
        }
        
        for route, label in system_routes.items():
            if route not in self.all_routes:
                self.all_routes[route] = label
        logger.debug(f"🔧 已注册系统路由: {list(system_routes.keys())}")
        logger.debug(f"🔧 注册的全部路由：{self.all_routes}")
        logger.debug(f"⚠️ 注意：logout 路由未注册到持久化路由中（一次性操作）")
    
    def initialize_layout(self):
        """初始化布局"""
        def init_routes():
            self.register_system_routes()
            self.restore_route_from_storage()
        
        ui.timer(0.3, init_routes, once=True)
```

- **component\multilayer_menu_config.py**
```python
"""
多层菜单配置模块
定义多层级菜单的数据结构和配置类
"""
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field

@dataclass
class MultilayerMenuItem:
    """多层菜单项数据类"""
    key: str                                    # 唯一标识符
    label: str                                  # 显示标签
    icon: str = 'folder'                        # 图标名称(Material Icons)
    route: Optional[str] = None                 # 路由标识(叶子节点必须有)
    children: List['MultilayerMenuItem'] = field(default_factory=list)  # 子菜单列表
    expanded: bool = False                      # 默认是否展开
    separator_after: bool = False               # 之后是否显示分隔线
    custom_icon_path: Optional[str] = None      # 自定义图标路径
    parent_key: Optional[str] = None            # 父节点key(自动设置)
    level: int = 0                              # 层级深度(自动计算)
    
    def __post_init__(self):
        """初始化后自动设置子节点的父节点引用和层级"""
        self._update_children_metadata()
    
    def _update_children_metadata(self):
        """更新子节点的元数据(父节点key和层级)"""
        for child in self.children:
            child.parent_key = self.key
            child.level = self.level + 1
            child._update_children_metadata()
    
    @property
    def is_parent(self) -> bool:
        """是否是父节点(有子节点)"""
        return len(self.children) > 0
    
    @property
    def is_leaf(self) -> bool:
        """是否是叶子节点(有路由且无子节点)"""
        return self.route is not None and len(self.children) == 0
    
    @property
    def is_root(self) -> bool:
        """是否是根节点(没有父节点)"""
        return self.parent_key is None
    
    def add_child(self, child: 'MultilayerMenuItem') -> 'MultilayerMenuItem':
        """添加子节点"""
        child.parent_key = self.key
        child.level = self.level + 1
        self.children.append(child)
        child._update_children_metadata()
        return self
    
    def find_by_key(self, key: str) -> Optional['MultilayerMenuItem']:
        """递归查找指定key的节点"""
        if self.key == key:
            return self
        
        for child in self.children:
            result = child.find_by_key(key)
            if result:
                return result
        
        return None
    
    def find_by_route(self, route: str) -> Optional['MultilayerMenuItem']:
        """递归查找指定路由的叶子节点"""
        if self.route == route:
            return self
        
        for child in self.children:
            result = child.find_by_route(route)
            if result:
                return result
        
        return None
    
    def get_parent_chain(self) -> List[str]:
        """获取从根节点到当前节点的父节点key链"""
        chain = []
        current = self
        while current.parent_key:
            chain.insert(0, current.parent_key)
            # 需要从根节点查找父节点
            current = None  # 简化处理,实际使用中由manager维护
            break
        return chain
    
    def get_all_routes(self) -> List[str]:
        """递归获取所有叶子节点的路由"""
        routes = []
        if self.is_leaf:
            routes.append(self.route)
        
        for child in self.children:
            routes.extend(child.get_all_routes())
        
        return routes
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式(用于调试和序列化)"""
        return {
            'key': self.key,
            'label': self.label,
            'icon': self.icon,
            'route': self.route,
            'expanded': self.expanded,
            'level': self.level,
            'is_parent': self.is_parent,
            'is_leaf': self.is_leaf,
            'children': [child.to_dict() for child in self.children]
        }

class MultilayerMenuConfig:
    """多层菜单配置管理类"""
    
    def __init__(self):
        self.menu_items: List[MultilayerMenuItem] = []
        self._route_map: Dict[str, MultilayerMenuItem] = {}  # 路由->节点映射
        self._key_map: Dict[str, MultilayerMenuItem] = {}    # key->节点映射
    
    def add_menu_item(self, item: MultilayerMenuItem):
        """添加顶层菜单项"""
        self.menu_items.append(item)
        self._rebuild_maps()
    
    def _rebuild_maps(self):
        """重建路由和key映射表"""
        self._route_map.clear()
        self._key_map.clear()
        
        for item in self.menu_items:
            self._build_maps_recursive(item)
    
    def _build_maps_recursive(self, item: MultilayerMenuItem):
        """递归构建映射表"""
        # 添加 key映射
        self._key_map[item.key] = item
        
        # 添加路由映射(只针对叶子节点)
        if item.is_leaf:
            self._route_map[item.route] = item
        
        # 递归处理子节点
        for child in item.children:
            self._build_maps_recursive(child)
    
    def find_by_route(self, route: str) -> Optional[MultilayerMenuItem]:
        """通过路由查找节点"""
        return self._route_map.get(route)
    
    def find_by_key(self, key: str) -> Optional[MultilayerMenuItem]:
        """通过key查找节点"""
        return self._key_map.get(key)
    
    def get_parent_chain_keys(self, key: str) -> List[str]:
        """获取指定节点的所有父节点key链"""
        item = self.find_by_key(key)
        if not item:
            return []
        
        chain = []
        current_key = item.parent_key
        
        while current_key:
            chain.insert(0, current_key)
            parent_item = self.find_by_key(current_key)
            if parent_item:
                current_key = parent_item.parent_key
            else:
                break
        
        return chain
    
    def get_all_routes(self) -> Dict[str, str]:
        """获取所有路由映射 {route: label}"""
        routes = {}
        for route, item in self._route_map.items():
            routes[route] = item.label
        return routes
    
    # ✨ 新增方法: 获取第一个叶子节点
    def get_first_leaf(self) -> Optional[MultilayerMenuItem]:
        """
        递归查找并返回第一个叶子节点
        
        Returns:
            第一个叶子节点,如果没有则返回 None
        """
        for item in self.menu_items:
            result = self._find_first_leaf_recursive(item)
            if result:
                return result
        return None
    
    def _find_first_leaf_recursive(self, item: MultilayerMenuItem) -> Optional[MultilayerMenuItem]:
        """
        递归辅助方法:在给定节点的子树中查找第一个叶子节点
        
        Args:
            item: 当前检查的节点
            
        Returns:
            第一个找到的叶子节点,如果没有则返回 None
        """
        # 如果当前节点是叶子节点,直接返回
        if item.is_leaf:
            return item
        
        # 否则递归查找子节点中的第一个叶子节点
        for child in item.children:
            result = self._find_first_leaf_recursive(child)
            if result:
                return result
        
        return None
    
    def validate(self) -> List[str]:
        """验证配置的有效性,返回错误信息列表"""
        errors = []
        
        # 检查key唯一性
        keys = set()
        for item in self.menu_items:
            self._validate_keys_recursive(item, keys, errors)
        
        # 检查叶子节点必须有路由
        for key, item in self._key_map.items():
            if item.is_leaf and not item.route:
                errors.append(f"叶子节点 '{item.label}' (key={key}) 缺少路由配置")
        
        return errors
    
    def _validate_keys_recursive(self, item: MultilayerMenuItem, keys: set, errors: List[str]):
        """递归验证key唯一性"""
        if item.key in keys:
            errors.append(f"重复的key: {item.key}")
        keys.add(item.key)
        
        for child in item.children:
            self._validate_keys_recursive(child, keys, errors)

# 辅助函数:快速创建菜单项
def create_menu_item(key: str, 
                     label: str, 
                     icon: str = 'folder',
                     route: Optional[str] = None,
                     children: Optional[List[MultilayerMenuItem]] = None,
                     **kwargs) -> MultilayerMenuItem:
    """快速创建菜单项的辅助函数"""
    return MultilayerMenuItem(
        key=key,
        label=label,
        icon=icon,
        route=route,
        children=children or [],
        **kwargs
    )


# 示例配置
def create_demo_menu_config() -> MultilayerMenuConfig:
    """创建演示用的菜单配置"""
    config = MultilayerMenuConfig()
    
    # 企业档案管理
    enterprise_menu = MultilayerMenuItem(
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
    )
    
    # 系统管理
    system_menu = MultilayerMenuItem(
        key='system',
        label='系统管理',
        icon='admin_panel_settings',
        children=[
            MultilayerMenuItem(
                key='users',
                label='用户管理',
                icon='group',
                route='user_management'
            ),
            MultilayerMenuItem(
                key='roles',
                label='角色管理',
                icon='badge',
                route='role_management'
            ),
        ]
    )
    
    config.add_menu_item(enterprise_menu)
    config.add_menu_item(system_menu)
    
    return config

if __name__ == '__main__':
    # 测试代码
    print("🧪 测试多层菜单配置模块\n")
    
    config = create_demo_menu_config()
    
    print("✅ 菜单结构:")
    for item in config.menu_items:
        print(f"\n📁 {item.label} (key={item.key})")
        for child in item.children:
            print(f"  ├─ {child.label} (key={child.key}, route={child.route})")
    
    print("\n✅ 所有路由映射:")
    for route, label in config.get_all_routes().items():
        print(f"  {route} -> {label}")
    
    print("\n✅ 查找测试:")
    chat_item = config.find_by_route('chat_page')
    if chat_item:
        print(f"  找到路由 'chat_page': {chat_item.label}")
        parent_chain = config.get_parent_chain_keys(chat_item.key)
        print(f"  父节点链: {parent_chain}")
    
    print("\n✅ 验证配置:")
    errors = config.validate()
    if errors:
        print(f"  ❌ 发现 {len(errors)} 个错误:")
        for error in errors:
            print(f"    - {error}")
    else:
        print("  ✅ 配置验证通过!")
```

- **component\multilayer_spa_layout.py**
```python
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
```

- **component\simple_layout_manager.py**
```python
from nicegui import ui, app
from typing import List, Dict, Callable, Optional
from .layout_config import LayoutConfig, MenuItem, HeaderConfigItem
from common.log_handler import (
    log_info, 
    log_error, 
    log_warning,
    log_debug,
    log_success,
    log_trace,
    get_logger
)
logger = get_logger(__file__)

class SimpleLayoutManager:
    """简单布局管理器 - 只包含顶部导航栏的布局"""
    
    def __init__(self, config: LayoutConfig):
        self.config = config
        self.nav_items: List[MenuItem] = []  # 顶部导航项
        self.header_config_items: List[HeaderConfigItem] = []
        self.selected_nav_item = {'key': None}  # 当前选中的导航项
        self.content_container = None
        self.dark_mode = None
        self.route_handlers: Dict[str, Callable] = {}
        self.current_route = None
        self.nav_buttons: Dict[str, any] = {}  # 导航按钮引用
        # 主题切换
        self._theme_key = 'theme' 
        initial_theme = app.storage.user.get(self._theme_key, False)
        app.storage.user[self._theme_key] = initial_theme   # 确保键存在
        # 路由映射
        self.all_routes: Dict[str, str] = {}  # route -> label 的映射

    def add_nav_item(self, key: str, label: str, icon: str, route: Optional[str] = None):
        """添加顶部导航项"""
        self.nav_items.append(MenuItem(key, label, icon, route, False))
        # 注册路由映射
        if route:
            self.all_routes[route] = label

    def add_header_config_item(self, key: str, label: Optional[str] = None, icon: Optional[str] = None, route: Optional[str] = None, on_click: Optional[Callable] = None):
        """添加头部配置项"""
        self.header_config_items.append(HeaderConfigItem(key, label, icon, route, on_click))
        # 注册路由映射
        if route:
            self.all_routes[route] = label or key

    def set_route_handler(self, route: str, handler: Callable):
        """设置路由处理器"""
        self.route_handlers[route] = handler
        
        # 如果路由映射中没有这个路由，添加一个默认标签
        if route not in self.all_routes:
            self.all_routes[route] = route.replace('_', ' ').title()

    def register_system_routes(self):
        """注册系统路由（设置菜单、用户菜单等）"""
        system_routes = {
            # 设置菜单路由
            'user_management': '用户管理',
            'role_management': '角色管理', 
            'permission_management': '权限管理',
            # ✅ 新增: 配置管理路由
            'llm_config_management': '大模型配置',
            'prompt_config_management': '提示词配置',  # ✅ 新增

            # 用户菜单路由（排除logout）
            'user_profile': '个人资料',
            'change_password': '修改密码',
            
            # 其他系统路由
            'no_permission': '权限不足',
            'login': '登录',
            'register': '注册'
        }
        
        for route, label in system_routes.items():
            self.all_routes[route] = label
            
        logger.debug(f"🔧 已注册系统路由: {list(system_routes.keys())}")
        logger.debug(f"🔧 注册的全部路由：{self.all_routes}")
        logger.debug(f"⚠️  注意：logout 路由未注册到持久化路由中（一次性操作）")

    def select_nav_item(self, key: str, button_element=None, update_storage: bool = True):
        """选择导航项"""
        if self.selected_nav_item['key'] == key:
            return

        # 清除之前的选中状态
        for btn_key, btn in self.nav_buttons.items():
            if btn_key == key:
                btn.props('color=primary')  # 选中状态
            else:
                btn.props('color=white')  # 未选中状态
        
        self.selected_nav_item['key'] = key

        nav_item = next((item for item in self.nav_items if item.key == key), None)
        if not nav_item:
            return

        ui.notify(f'切换到{nav_item.label}')

        if nav_item.route:
            self.navigate_to_route(nav_item.route, nav_item.label, update_storage)
        else:
            if self.content_container:
                self.content_container.clear()
                with self.content_container:
                    ui.label(f'{nav_item.label}内容').classes('text-2xl font-bold text-gray-800 dark:text-gray-200')

    def clear_nav_selection(self):
        """清除导航选中状态（用于非导航路由）"""
        for btn in self.nav_buttons.values():
            btn.props('color=white')
        self.selected_nav_item['key'] = None

    def navigate_to_route(self, route: str, label: str, update_storage: bool = True):
        """导航到指定路由"""
        if self.current_route == route:
            return
        
        self.current_route = route
        
        # 如果不是导航路由，清除导航选中状态
        is_nav_route = any(item.route == route for item in self.nav_items)
        if not is_nav_route:
            self.clear_nav_selection()
        
        # 保存当前路由到存储（排除一次性操作路由）
        if update_storage and self._should_persist_route(route):
            try:
                app.storage.user['current_route'] = route
            except Exception as e:
                logger.error(f"⚠️ 保存路由状态失败: {e}")
        elif not self._should_persist_route(route):
            logger.debug(f"🚫 跳过路由持久化: {route} (一次性操作)")
        
        if self.content_container:
            self.content_container.clear()

        if route in self.route_handlers:
            with self.content_container:
                try:
                    self.route_handlers[route]()
                except Exception as e:
                    logger.error(f"❌ 路由处理器执行失败 {route}: {e}")
                    ui.label(f'页面加载失败: {str(e)}').classes('text-red-500 text-xl')
        else:
            logger.error(f"❌ 未找到路由处理器: {route}")
            with self.content_container:
                ui.label(f'页面未找到: {label}').classes('text-2xl font-bold text-red-600')
                ui.label(f'路由 "{route}" 没有对应的处理器').classes('text-gray-600 dark:text-gray-400 mt-4')

    def _should_persist_route(self, route: str) -> bool:
        """判断路由是否应该持久化"""
        # 一次性操作路由，不应该被持久化
        non_persistent_routes = {
            'logout',      # 注销操作
            'login',       # 登录页面
            'register',    # 注册页面
        }
        return route not in non_persistent_routes

    def clear_route_storage(self):
        """清除路由存储（用于注销等场景）"""
        try:
            if 'current_route' in app.storage.user:
                del app.storage.user['current_route']
                logger.debug("🗑️ 已清除路由存储")
        except Exception as e:
            logger.warning(f"⚠️ 清除路由存储失败: {e}")

    def restore_route_from_storage(self):
        """从存储恢复路由状态"""
        try:
            # 从存储获取保存的路由
            saved_route = app.storage.user.get('current_route')
            
            # 如果没有保存的路由
            if not saved_route:
                # 如果有导航项，选择第一个
                if self.nav_items:
                    first_item = self.nav_items[0]
                    self.select_nav_item(first_item.key, update_storage=True)
                else:
                    # 如果没有导航项，不做任何操作
                    logger.warning("🔄 没有保存的路由，且未定义导航项，保持空白状态")
                return
            
            logger.debug(f"🔄 恢复保存的路由: {saved_route}")
            
            # 检查路由是否在已知路由中
            if saved_route in self.all_routes:
                route_label = self.all_routes[saved_route]
                logger.debug(f"✅ 找到路由映射: {saved_route} -> {route_label}")
                
                # 检查是否是导航项路由
                nav_item = next((item for item in self.nav_items if item.route == saved_route), None)
                if nav_item:
                    # 恢复导航选中状态
                    self.select_nav_item(nav_item.key, update_storage=False)
                else:
                    logger.debug(f"✅ 这是非导航路由，直接导航")
                    # 直接导航到路由（不更新存储避免循环）
                    self.navigate_to_route(saved_route, route_label, update_storage=False)
                return
            
            # 兜底检查：是否在路由处理器中注册
            if saved_route in self.route_handlers:
                logger.debug(f"✅ 在路由处理器中找到路由: {saved_route}")
                label = saved_route.replace('_', ' ').title()
                self.navigate_to_route(saved_route, label, update_storage=False)
                return
            
            # 如果都没找到，且有导航项，选择第一个导航项
            logger.debug(f"⚠️ 未找到保存的路由 {saved_route}，使用默认路由")
            if self.nav_items:
                first_item = self.nav_items[0]
                self.select_nav_item(first_item.key, update_storage=True)
            else:
                logger.debug("⚠️ 没有可用的导航项，保持空白状态")
                
        except Exception as e:
            logger.debug(f"⚠️ 恢复路由状态失败: {e}")
            if self.nav_items:
                first_item = self.nav_items[0]
                self.select_nav_item(first_item.key, update_storage=True)
            else:
                logger.debug("⚠️ 没有可用的导航项，保持空白状态")

    def handle_header_config_item_click(self, item: HeaderConfigItem):
        """处理头部配置项点击事件"""
        ui.notify(f'点击了头部配置项: {item.label or item.key}')
        
        if item.on_click:
            item.on_click()
        
        if item.route:
            self.navigate_to_route(item.route, item.label or item.key)

    def handle_settings_menu_item_click(self, route: str, label: str):
        """处理设置菜单项点击事件"""        
        from auth.auth_manager import auth_manager

        if not auth_manager.is_authenticated():
            ui.notify('请先登录', type='warning')
            self.navigate_to_route('login', '登录')
            return

        if not auth_manager.has_role('admin') and not auth_manager.current_user.is_superuser:
            ui.notify('您没有管理员权限，无法访问此功能', type='error')
            self.navigate_to_route('no_permission', '权限不足')
            return

        ui.notify(f'访问管理功能: {label}')
        self.navigate_to_route(route, label)

    def handle_user_menu_item_click(self, route: str, label: str):
        """处理用户菜单项点击事件"""
        ui.notify(f'点击了用户菜单项: {label}')
        
        # 特殊处理注销：清除路由存储
        if route == 'logout':
            logger.debug("🚪 执行用户注销，清除路由存储")
            self.clear_route_storage()
        
        self.navigate_to_route(route, label)

    def create_header(self):
        """创建头部导航栏"""
        with ui.header(elevated=True).classes(f'items-center justify-between px-2 {self.config.header_bg}'):
            # 左侧：Logo
            with ui.row().classes('items-center gap-2'):
                # Logo区域
                with ui.avatar():
                    ui.image(self.config.app_icon).classes('w-12 h-12')
                ui.label(self.config.app_title).classes('text-xl font-medium text-white dark:text-white')

            # 右侧区域：主导航项 + 头部配置项 + 主题切换 + 设置菜单 + 用户菜单
            # 将所有这些元素放在一个单独的 ui.row 中，它们会作为一个整体靠右对齐
            with ui.row().classes('items-center gap-2'): # 使用 gap-2 可以在内部元素之间增加一些间距
                # ui.separator().props('vertical').classes('h-8 mx-4') # 如果希望主导航项和logo之间有分隔符，可以保留，但根据图片，可能不需要
                # 主导航项
                for nav_item in self.nav_items:
                    nav_btn = ui.button(
                        nav_item.label, 
                        icon=nav_item.icon,
                        on_click=lambda key=nav_item.key: self.select_nav_item(key)
                    ).props('flat color=white').classes('mx-1')
                    # 保存按钮引用用于状态控制
                    self.nav_buttons[nav_item.key] = nav_btn
                
                # 主导航项和右侧配置项之间的分隔符 (根据图片，这里可能需要一个分隔符)
                if self.nav_items and (self.header_config_items or self.dark_mode or True): # 假设后面的元素总是存在
                    # ui.separator().props('vertical').classes('h-8 mx-4') # 在主导航项和右侧功能区之间添加分隔符
                    ui.label("|")

                # 头部配置项
                for item in self.header_config_items:
                    if item.icon and item.label:
                        ui.button(item.label, icon=item.icon, on_click=lambda current_item=item: self.handle_header_config_item_click(current_item)).props('flat color=white').classes('mr-2')
                    elif item.icon:
                        ui.button(icon=item.icon, on_click=lambda current_item=item: self.handle_header_config_item_click(current_item)).props('flat color=white round').classes('w-10 h-10')
                    elif item.label:
                        ui.button(item.label, on_click=lambda current_item=item: self.handle_header_config_item_click(current_item)).props('flat color=white').classes('mr-2')

                # 主题切换
                # ui.switch('主题切换').bind_value(self.dark_mode).classes('mx-2')
                self.dark_mode = ui.dark_mode(value=app.storage.user[self._theme_key])
                ui.switch('主题切换') \
                    .bind_value(self.dark_mode) \
                    .on_value_change(lambda e: app.storage.user.update({self._theme_key: e.value})) \
                    .classes('mx-2')

                # 设置菜单
                with ui.button(icon='settings').props('flat color=white round').classes('w-10 h-10'):
                    with ui.menu() as settings_menu:
                        ui.menu_item('用户管理', lambda: self.handle_settings_menu_item_click('user_management', '用户管理'))
                        ui.menu_item('角色管理', lambda: self.handle_settings_menu_item_click('role_management', '角色管理'))
                        ui.menu_item('权限管理', lambda: self.handle_settings_menu_item_click('permission_management', '权限管理'))
                        # ✅ 新增: 配置管理菜单项
                        ui.separator()  # 分隔线
                        ui.menu_item('大模型配置', lambda: self.handle_settings_menu_item_click('llm_config_management', '大模型配置'))
                        ui.menu_item('提示词配置', lambda: self.handle_settings_menu_item_click('prompt_config_management', '提示词配置'))  # ✅ 新增

                # 用户菜单
                with ui.button(icon='account_circle').props('flat color=white round').classes('w-10 h-10'):
                    with ui.menu() as user_menu:
                        ui.menu_item('个人资料', lambda: self.handle_user_menu_item_click('user_profile', '个人资料'))
                        ui.menu_item('修改密码', lambda: self.handle_user_menu_item_click('change_password', '修改密码'))
                        ui.separator()
                        ui.menu_item('注销', lambda: self.handle_user_menu_item_click('logout', '注销'))

    def create_content_area(self):
        """创建内容区域"""
        with ui.column().classes('flex-1 w-full') as content_container:
            self.content_container = content_container

    def initialize_layout(self):
        """初始化布局（延迟执行路由恢复）"""
        def init_routes():
            self.register_system_routes()
            self.restore_route_from_storage()
        
        ui.timer(0.3, init_routes, once=True)
```

- **component\simple_spa_layout.py**
```python
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
```

- **component\spa_layout.py**
```python
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

            # 只有用户传递了菜单项才添加，否则为空
            if menu_items is not None:
                for item in menu_items:
                    layout_manager.add_menu_item(item['key'], item['label'], item['icon'], item.get('route'), item.get('separator_after', False))

            if header_config_items is not None:
                for item in header_config_items:
                    layout_manager.add_header_config_item(item['key'], item.get('label'), item.get('icon'), item.get('route'), item.get('on_click'))

            if route_handlers:
                for route, handler in route_handlers.items():
                    layout_manager.set_route_handler(route, handler)

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
    """导航到指定路由"""
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
                # 如果都没找到，使用路由名作为标签
                label = route.replace('_', ' ').title()
    
    # 导航并保存状态
    layout_manager.navigate_to_route(route, label, update_storage=True)
    
    # 同步更新菜单选中状态
    for menu_item in layout_manager.menu_items:
        if menu_item.route == route:
            layout_manager.select_menu_item(menu_item.key, update_storage=False)
            break


def create_spa_layout(config: Optional[LayoutConfig] = None,
                      menu_items: Optional[List[Dict[str, Any]]] = None,
                      header_config_items: Optional[List[Dict[str, Any]]] = None,
                      route_handlers: Optional[Dict[str, Callable]] = None) -> LayoutManager:
    global current_layout_manager
    layout_config = config or LayoutConfig()
    layout_manager = LayoutManager(layout_config)
    current_layout_manager = layout_manager

    # 只有用户传递了菜单项才添加，否则为空
    if menu_items is not None:
        for item in menu_items:
            layout_manager.add_menu_item(item['key'], item['label'], item['icon'], item.get('route'), item.get('separator_after', False))

    if header_config_items is not None:
        for item in header_config_items:
            layout_manager.add_header_config_item(item['key'], item.get('label'), item.get('icon'), item.get('route'), item.get('on_click'))

    if route_handlers:
        for route, handler in route_handlers.items():
            layout_manager.set_route_handler(route, handler)

    layout_manager.create_header()
    layout_manager.create_left_drawer()
    layout_manager.create_content_area()

    return layout_manager
```

- **component\static_resources.py**
```python
# 解决方案1: 更新static_resources.py，添加CSS加载功能

from nicegui import ui, app
import os
from pathlib import Path
from typing import Optional

class StaticResourceManager:
    """静态资源管理器"""
    
    def __init__(self, static_dir: str = "static"):
        self.static_dir = Path(static_dir)
        self.base_url = "/static"  # 静态文件的URL前缀
        self._ensure_directories()
        self._setup_static_routes()
    
    def _ensure_directories(self):
        """确保静态资源目录存在"""
        directories = [
            self.static_dir / "images" / "logo",
            self.static_dir / "images" / "avatars", 
            self.static_dir / "images" / "icons" / "menu-icons",
            self.static_dir / "images" / "icons" / "header-icons",
            self.static_dir / "css" / "themes",
            self.static_dir / "js" / "components",
            self.static_dir / "fonts" / "custom-fonts"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def _setup_static_routes(self):
        """设置静态文件路由"""
        if self.static_dir.exists():
            # 注册静态文件路由
            app.add_static_files(self.base_url, str(self.static_dir))
    
    def load_css_files(self):
        """加载所有CSS文件到页面"""
        css_files = [
            "css/custom.css",
            "css/themes/light.css", 
            "css/themes/dark.css"
        ]
        
        for css_file in css_files:
            css_path = self.static_dir / css_file
            if css_path.exists():
                # 方法1: 通过URL引用
                css_url = f"{self.base_url}/{css_file}"
                ui.add_head_html(f'<link rel="stylesheet" type="text/css" href="{css_url}">')
                print(f"✅ 已加载CSS: {css_url}")
            else:
                print(f"⚠️  CSS文件不存在: {css_path}")
    
    def load_inline_css(self, css_file: str):
        """将CSS内容内联到页面"""
        css_path = self.static_dir / css_file
        if css_path.exists():
            try:
                with open(css_path, 'r', encoding='utf-8') as f:
                    css_content = f.read()
                ui.add_head_html(f'<style type="text/css">{css_content}</style>')
                print(f"✅ 已内联加载CSS: {css_file}")
                return True
            except Exception as e:
                print(f"❌ 加载CSS失败 {css_file}: {e}")
                return False
        else:
            print(f"⚠️  CSS文件不存在: {css_path}")
            return False
    
    def get_css_url(self, filename: str) -> str:
        """获取CSS文件的URL"""
        return f"{self.base_url}/css/{filename}"
    
    def get_image_path(self, category: str, filename: str) -> str:
        """获取图片路径"""
        return f"{self.base_url}/images/{category}/{filename}"
    
    def get_logo_path(self, filename: str = "robot.svg") -> str:
        """获取Logo路径"""
        return self.get_image_path("logo", filename)
    
    def get_avatar_path(self, filename: str = "default_avatar.png") -> str:
        """获取头像路径"""
        return self.get_image_path("avatars", filename)
    
    def get_icon_path(self, category: str, filename: str) -> str:
        """获取图标路径"""
        return f"{self.base_url}/images/icons/{category}/{filename}"
    
    def get_css_path(self, filename: str) -> str:
        """获取CSS文件路径"""
        return f"{self.base_url}/css/{filename}"
    
    def get_theme_css_path(self, theme: str) -> str:
        """获取主题CSS路径"""
        return f"{self.base_url}/css/themes/{theme}.css"
    
    def get_js_path(self, filename: str) -> str:
        """获取JavaScript文件路径"""
        return f"{self.base_url}/js/{filename}"
    
    def get_font_path(self, filename: str) -> str:
        """获取字体文件路径"""
        return f"{self.base_url}/fonts/custom-fonts/{filename}"
    
    def file_exists(self, file_path: str) -> bool:
        """检查文件是否存在"""
        # 如果是URL路径，转换为本地路径检查
        if file_path.startswith(self.base_url):
            relative_path = file_path.replace(self.base_url + "/", "")
            local_path = self.static_dir / relative_path
        else:
            local_path = Path(file_path)
        return local_path.exists()
    
    def get_fallback_path(self, primary_path: str, fallback_path: str) -> str:
        """获取备用路径（如果主路径不存在）"""
        return primary_path if self.file_exists(primary_path) else fallback_path

# 全局静态资源管理器实例
static_manager = StaticResourceManager()
```

## component\chat

- **component\chat\__init__.py** *(包初始化文件)*
```python
"""
聊天组件包 - 可复用的聊天UI组件
从 menu_pages/enterprise_archive/chat_component 迁移而来

提供完整的聊天功能,包括:
- 聊天数据状态管理
- 聊天区域UI管理
- 侧边栏UI管理
- LLM模型配置
- Markdown内容解析
"""

from .chat_data_state import ChatDataState, SelectedValues, CurrentState, CurrentPromptConfig
from .chat_area_manager import ChatAreaManager
from .chat_sidebar_manager import ChatSidebarManager
from .chat_component import ChatComponent
from .config import (
    get_model_options_for_select,
    get_model_config,
    get_default_model,
    reload_llm_config,
    get_model_config_info,
    get_prompt_options_for_select,
    get_system_prompt,
    get_examples,
    get_default_prompt,
    reload_prompt_config,
    get_prompt_config_info
)
from .markdown_ui_parser import MarkdownUIParser

__all__ = [
    # 数据状态
    'ChatDataState',
    'SelectedValues',
    'CurrentState',
    'CurrentPromptConfig',
    
    # 管理器
    'ChatAreaManager',
    'ChatSidebarManager',
    
    # 主组件
    'ChatComponent',
    
    # 配置函数
    'get_model_options_for_select',
    'get_model_config',
    'get_default_model',
    'reload_llm_config',
    'get_model_config_info',
    'get_prompt_options_for_select',
    'get_system_prompt',
    'get_examples',
    'get_default_prompt',
    'reload_prompt_config',
    'get_prompt_config_info',
    
    # 工具类
    'MarkdownUIParser',
]
```

- **component\chat\chat_area_manager.py**
```python
"""
ChatAreaManager - 聊天内容显示区域
负责渲染展示聊天内容的UI和相关业务逻辑
"""
from abc import ABC, abstractmethod
import asyncio
from datetime import datetime
from nicegui import ui
from typing import Optional, List, Dict, Any
from component import static_manager
from .chat_data_state import ChatDataState
from .markdown_ui_parser import MarkdownUIParser

class ThinkContentParser:
    """思考内容解析器 - 专门处理<think>标签"""
    
    def __init__(self):
        self.is_in_think = False
        self.think_start_pos = -1
        self.think_content = ""
    
    def parse_chunk(self, full_content: str) -> Dict[str, Any]:
        """解析内容块,返回处理结果"""
        result = {
            'has_think': False,
            'think_content': '',
            'display_content': full_content,
            'think_complete': False,
            'think_updated': False
        }
    
        # 检测思考开始
        if '<think>' in full_content and not self.is_in_think:
            self.is_in_think = True
            self.think_start_pos = full_content.find('<think>')
            result['has_think'] = True
        
        # 检测思考结束
        if '</think>' in full_content and self.is_in_think:
            think_end_pos = full_content.find('</think>') + 8
            self.think_content = full_content[self.think_start_pos + 7:think_end_pos - 8]
            result['display_content'] = full_content[:self.think_start_pos] + full_content[think_end_pos:]
            result['think_content'] = self.think_content.strip()
            result['think_complete'] = True
            self.is_in_think = False
        elif self.is_in_think:
            # 正在思考中
            if self.think_start_pos >= 0:
                current_think = full_content[self.think_start_pos + 7:]
                result['display_content'] = full_content[:self.think_start_pos]
                result['think_content'] = current_think.strip()
                result['think_updated'] = True
        
        result['has_think'] = self.think_start_pos >= 0
        return result

class MessagePreprocessor:
    """消息预处理器"""
    
    def __init__(self, chat_data_state):
        self.chat_data_state = chat_data_state
    
    def enhance_user_message(self, user_message: str) -> str:
        """增强用户消息 - 使用 textarea 输入的提示数据"""
        try:
            # 检查是否启用了提示数据
            if not self.chat_data_state.switch:
                return user_message
            
            # 获取 textarea 中的原始输入
            raw_input = self.chat_data_state.selected_values.raw_input
            
            if not raw_input or not raw_input.strip():
                ui.notify("未输入提示数据", type="warning")
                return user_message
            
            # 直接将 textarea 内容附加到用户消息后面
            append_text = f"\n\n{raw_input.strip()}"
            
            return f"{user_message}{append_text}"
    
        except Exception as e:
            ui.notify(f"[ERROR] 增强用户消息时发生异常: {e}", type="negative")
            return user_message

class AIClientManager:
    """AI客户端管理器"""
    
    def __init__(self, chat_data_state):
        self.chat_data_state = chat_data_state
    
    async def get_client(self):
        """获取AI客户端"""
        from common.safe_openai_client_pool import get_openai_client
        
        selected_model = self.chat_data_state.current_model_config['selected_model']
        model_config = self.chat_data_state.current_model_config['config']
        
        client = await get_openai_client(selected_model, model_config)
        if not client:
            raise Exception(f"无法连接到模型 {selected_model}")
        
        return client, model_config
    
    def prepare_messages(self, user_msg_dict: Dict) -> List[Dict[str, str]]:
        """准备发送给AI的消息列表"""
        # 默认情况下,使用最近的5条聊天记录
        recent_messages = self.chat_data_state.current_chat_messages[-5:]
        
        if (self.chat_data_state.current_state.prompt_select_widget and 
            self.chat_data_state.current_prompt_config.system_prompt):
            system_message = {
                "role": "system", 
                "content": self.chat_data_state.current_prompt_config.system_prompt
            }
            recent_messages = [system_message] + recent_messages
        
        return recent_messages

class ContentDisplayStrategy(ABC):
    """内容展示策略抽象基类"""
    def __init__(self, ui_components):
        self.ui_components = ui_components
        self.think_parser = ThinkContentParser()
        self.structure_created = False
        self.reply_created = False
        self.think_expansion = None
        self.think_label = None
        self.reply_label = None
        self.chat_content_container = None
    
    @abstractmethod
    def create_ui_structure(self, has_think: bool):
        """创建UI结构"""
        pass
    
    @abstractmethod
    def update_content(self, parse_result: Dict[str, Any]) -> bool:
        """更新内容显示,返回是否需要滚动"""
        pass
    
    def process_stream_chunk(self, full_content: str) -> bool:
        """处理流式数据块 - 模板方法"""
        parse_result = self.think_parser.parse_chunk(full_content)
        
        # 创建UI结构(如果需要)
        if not self.structure_created:
            self.create_ui_structure(parse_result['has_think'])
            self.structure_created = True
        
        # 更新内容
        need_scroll = self.update_content(parse_result)
        return need_scroll
    
    async def finalize_content(self, final_content: str):
        """完成内容显示"""
        final_result = self.think_parser.parse_chunk(final_content)
        
        if final_result['think_complete'] and self.think_label:
            self.think_label.set_text(final_result['think_content'])
        
        if self.reply_label and final_result['display_content'].strip():
            self.reply_label.set_content(final_result['display_content'].strip())
            # 调用markdown优化显示
            if hasattr(self.ui_components, 'markdown_parser'):
                await self.ui_components.markdown_parser.optimize_content_display(
                    self.reply_label, final_result['display_content'], self.chat_content_container
                )

class DefaultDisplayStrategy(ContentDisplayStrategy):
    """默认展示策略"""
    
    def create_ui_structure(self, has_think: bool):
        """创建默认UI结构"""
        self.ui_components.waiting_ai_message_container.clear()
        with self.ui_components.waiting_ai_message_container:
            with ui.column().classes('w-full') as self.chat_content_container:
                if has_think:
                    self.think_expansion = ui.expansion(
                        '💭 AI思考过程...(可点击打开查看)', 
                        icon='psychology'
                    ).classes('w-full mb-2')
                    with self.think_expansion:
                        self.think_label = ui.label('').classes(
                            'whitespace-pre-wrap bg-[#81c784] border-0 shadow-none rounded-none'
                        )
                else:
                    self.reply_label = ui.markdown('').classes('w-full')
                    self.reply_created = True
    
    def update_content(self, parse_result: Dict[str, Any]) -> bool:
        """更新默认展示内容"""
        if parse_result['think_updated'] and self.think_label:
            self.think_label.set_text(parse_result['think_content'])
        
        if parse_result['think_complete']:
            # 思考完成,创建回复组件
            if self.chat_content_container and not self.reply_created:
                with self.chat_content_container:
                    self.reply_label = ui.markdown('').classes('w-full')
                self.reply_created = True
            
            if self.think_label:
                self.think_label.set_text(parse_result['think_content'])
        
        # 更新显示内容
        if self.reply_label and parse_result['display_content'].strip():
            with self.chat_content_container:
                self.reply_label.set_content(parse_result['display_content'].strip())
        
        return True  # 需要滚动

class StreamResponseProcessor:
    """流式响应处理器"""
    
    def __init__(self, chat_area_manager):
        self.chat_area_manager = chat_area_manager
        self.display_strategy = None
    
    def get_display_strategy(self) -> ContentDisplayStrategy:
        """获取展示策略 - 只使用默认策略"""
        return DefaultDisplayStrategy(self.chat_area_manager)
    
    async def process_stream_response(self, stream_response) -> str:
        """处理流式响应"""
        self.display_strategy = self.get_display_strategy()
        assistant_reply = ""
        
        for chunk in stream_response:
            if chunk.choices[0].delta.content:
                chunk_content = chunk.choices[0].delta.content
                assistant_reply += chunk_content
                
                # 使用策略处理内容
                need_scroll = self.display_strategy.process_stream_chunk(assistant_reply)
                
                if need_scroll:
                    await self.chat_area_manager.scroll_to_bottom_smooth()
                    await asyncio.sleep(0.05)
        
        # 完成内容显示
        await self.display_strategy.finalize_content(assistant_reply)
        return assistant_reply

class MessageProcessor:
    """消息处理门面类"""
    
    def __init__(self, chat_area_manager):
        self.chat_area_manager = chat_area_manager
        self.preprocessor = MessagePreprocessor(chat_area_manager.chat_data_state)
        self.ai_client_manager = AIClientManager(chat_area_manager.chat_data_state)
        self.stream_processor = StreamResponseProcessor(chat_area_manager)
    
    async def process_user_message(self, user_message: str) -> str:
        """处理用户消息并返回AI回复"""
        # 1. 预处理用户消息
        enhanced_message = self.preprocessor.enhance_user_message(user_message)
        
        # 2. 保存用户消息到历史
        user_msg_dict = {
            'role': 'user',
            'content': enhanced_message,
            'timestamp': datetime.now().isoformat()
        }
        
        self.chat_area_manager.chat_data_state.current_chat_messages.append(user_msg_dict)
        
        # 3. 渲染用户消息
        await self.chat_area_manager.render_single_message(user_msg_dict)
        await self.chat_area_manager.scroll_to_bottom_smooth()
        
        # 4. 启动等待效果
        await self.chat_area_manager.start_waiting_effect("正在处理")
        
        try:
            # 5. 获取AI客户端
            client, model_config = await self.ai_client_manager.get_client()
            
            # 6. 准备消息列表
            messages = self.ai_client_manager.prepare_messages(user_msg_dict)
            
            # 7. 调用AI API
            actual_model_name = model_config.get('model_name', 
                self.chat_area_manager.chat_data_state.current_model_config['selected_model']
            ) if model_config else self.chat_area_manager.chat_data_state.current_model_config['selected_model']
            
            stream_response = await asyncio.to_thread(
                client.chat.completions.create,
                model=actual_model_name,
                messages=messages,
                max_tokens=2000,
                temperature=0.7,
                stream=True
            )
            
            # 8. 停止等待效果并处理流式响应
            await self.chat_area_manager.stop_waiting_effect()
            assistant_reply = await self.stream_processor.process_stream_response(stream_response)
            
            return assistant_reply
            
        except Exception as e:
            # 错误处理
            error_message = f"抱歉,调用AI服务时出现错误:{str(e)[:300]}..."
            ui.notify('AI服务调用失败,请稍后重试', type='negative')
            
            await self.chat_area_manager.stop_waiting_effect()
            if self.chat_area_manager.waiting_message_label:
                self.chat_area_manager.waiting_message_label.set_text(error_message)
                self.chat_area_manager.waiting_message_label.classes(remove='text-gray-500 italic')
            
            return error_message

# 更新后的 ChatAreaManager 类
class ChatAreaManager:
    """主聊天区域管理器 - 负责聊天内容展示和用户交互"""  
    def __init__(self, chat_data_state):
        """初始化聊天区域管理器"""
        self.chat_data_state = chat_data_state
        self.markdown_parser = MarkdownUIParser()
        # UI组件引用
        self.scroll_area = None
        self.chat_messages_container = None
        self.welcome_message_container = None
        self.input_ref = {'widget': None}
        self.send_button_ref = {'widget': None}
        self.clear_button_ref = {'widget': None}
        # 其他UI引用
        self.switch = None
        self.hierarchy_selector = None
        # 新增类属性:AI回复相关组件
        self.reply_label = None
        self.chat_content_container = None
        # 等待效果
        self.waiting_message_label = None
        self.waiting_animation_task = None
        self.waiting_ai_message_container = None
        # 聊天头像
        self.user_avatar = static_manager.get_fallback_path(
            static_manager.get_logo_path('user.svg'),
            static_manager.get_logo_path('ProfileHeader.gif'),
        )
        self.robot_avatar = static_manager.get_fallback_path(
            static_manager.get_logo_path('robot_txt.svg'),
            static_manager.get_logo_path('Live chatbot.gif'),
        )
        
        # 初始化消息处理器
        self.message_processor = MessageProcessor(self)

    #region 等待效果相关方法
    async def start_waiting_effect(self, message="正在处理"):
        """启动等待效果"""
        # 添加等待效果的机器人消息容器
        with self.chat_messages_container:
            self.waiting_ai_message_container = ui.chat_message(
                avatar=self.robot_avatar
            ).classes('w-full')
            
            with self.waiting_ai_message_container:
                self.waiting_message_label = ui.label(message).classes('whitespace-pre-wrap text-gray-500 italic')

        await self.scroll_to_bottom_smooth()

        # 启动等待动画
        animation_active = [True]  # 使用列表以支持闭包内修改
        
        async def animate_waiting():
            dots_count = 0
            while animation_active[0] and self.waiting_message_label:
                dots_count = (dots_count % 3) + 1
                waiting_dots = "." * dots_count
                self.waiting_message_label.set_text(f"{message}{waiting_dots}")
                await asyncio.sleep(0.5)
        
        self.waiting_animation_task = asyncio.create_task(animate_waiting())
        
        # 存储动画状态的引用
        self.waiting_animation_active = animation_active

    async def stop_waiting_effect(self):
        """停止等待效果"""
        if hasattr(self, 'waiting_animation_active'):
            self.waiting_animation_active[0] = False
        
        if self.waiting_animation_task:
            self.waiting_animation_task.cancel()
            try:
                await self.waiting_animation_task
            except asyncio.CancelledError:
                pass

    async def cleanup_waiting_effect(self):
        """清理等待效果的UI组件"""
        if self.waiting_ai_message_container:
            self.waiting_ai_message_container.clear()
            self.waiting_ai_message_container = None
        self.waiting_message_label = None
    #endregion

    #region 消息渲染相关方法
    async def render_single_message(self, message: Dict[str, Any], container=None):
        """渲染单条消息"""
        target_container = container if container is not None else self.chat_messages_container
        
        with target_container:
            if message['role'] == 'user':
                with ui.chat_message(
                    avatar=self.user_avatar,
                    sent=True
                ).classes('w-full'):
                    ui.label(message['content']).classes('whitespace-pre-wrap break-words')
            
            elif message['role'] == 'assistant':
                with ui.chat_message(
                    avatar=self.robot_avatar
                ).classes('w-full'):
                    # 创建临时的chat_content_container用于单条消息渲染
                    with ui.column().classes('w-full') as self.chat_content_container:
                        # 检查消息内容是否包含think标签
                        content = message['content']
                        if '<think>' in content and '</think>' in content:
                            # 包含think内容,需要特殊处理
                            import re
                            # 提取think内容
                            think_match = re.search(r'<think>(.*?)</think>', content, re.DOTALL)
                            if think_match:
                                think_content = think_match.group(1).strip()
                                # 移除think标签,获取显示内容
                                display_content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL).strip()
                                
                                # 创建think展开面板
                                with ui.expansion(
                                    '💭 AI思考过程...(可点击打开查看)', 
                                    icon='psychology'
                                ).classes('w-full mb-2'):
                                    ui.label(think_content).classes(
                                        'whitespace-pre-wrap bg-[#81c784] border-0 shadow-none rounded-none'
                                    )
                                
                                # 显示实际回复内容
                                if display_content:
                                    temp_reply_label = ui.markdown(display_content).classes('w-full')
                                    await self.markdown_parser.optimize_content_display(
                                        temp_reply_label, 
                                        display_content, 
                                        self.chat_content_container
                                    )
                        else:
                            # 不包含think内容,直接显示
                            temp_reply_label = ui.markdown(content).classes('w-full')
                            await self.markdown_parser.optimize_content_display(
                                temp_reply_label, 
                                content, 
                                self.chat_content_container
                            )

    def restore_welcome_message(self):
        """恢复欢迎消息"""
        self.chat_messages_container.clear()
        if self.welcome_message_container:
            self.welcome_message_container.clear()
            with self.welcome_message_container:
                with ui.card().classes('w-full max-w-3xl mx-auto shadow-lg'):
                    with ui.column().classes('p-6 text-center'):
                        ui.icon('waving_hand', size='3xl').classes('text-blue-500 mb-4 text-3xl')
                        ui.label('欢迎使用智能问答助手').classes('text-2xl font-bold mb-2')
                        ui.label('请输入您的问题,我将为您提供帮助').classes('text-lg text-gray-600 mb-4')
                        
                        with ui.row().classes('justify-center gap-4'):
                            ui.chip('问答', icon='quiz').classes('text-blue-600 text-lg')
                            ui.chip('制表', icon='table_view').classes('text-yellow-600 text-lg')
                            ui.chip('绘图', icon='dirty_lens').classes('text-purple-600 text-lg')
                            ui.chip('分析', icon='analytics').classes('text-orange-600 text-lg')
    #endregion

    #region 滚动相关方法
    async def scroll_to_bottom_smooth(self):
        """平滑滚动到底部"""
        if self.scroll_area:
            await asyncio.sleep(0.05)
            self.scroll_area.scroll_to(percent=1)
    #endregion

    #region 消息处理相关方法
    def handle_keydown(self, e):
        """处理键盘事件 - 使用NiceGUI原生方法"""
        # 检查输入框是否已禁用,如果禁用则不处理按键事件
        if not self.input_ref['widget'].enabled:
            return
            
        # 获取事件详细信息
        key = e.args.get('key', '')
        shift_key = e.args.get('shiftKey', False)
        
        if key == 'Enter':
            if shift_key:
                # Shift+Enter: 允许换行,不做任何处理
                pass
            else:
                # 单独的Enter: 发送消息
                # 阻止默认的换行行为
                ui.run_javascript('event.preventDefault();')
                # 异步调用消息处理函数
                ui.timer(0.01, lambda: self.handle_message(), once=True)

    async def handle_message(self):
        """处理发送消息"""
        user_message = self.input_ref['widget'].value.strip()
        if not user_message:
            ui.notify('请输入消息内容', type='warning')
            return
        
        # 清空输入框
        self.input_ref['widget'].set_value('')
        
        # 禁用输入控件
        self.input_ref['widget'].set_enabled(False)
        self.send_button_ref['widget'].set_enabled(False)
        
        try:
            # 清除欢迎消息
            if self.welcome_message_container:
                self.welcome_message_container.clear()
            # 使用消息处理器处理用户消息
            assistant_reply = await self.message_processor.process_user_message(user_message)
            # 记录AI回复到聊天历史
            self.chat_data_state.current_chat_messages.append({
                'role': 'assistant', 
                'content': assistant_reply,
                'timestamp': datetime.now().isoformat(),
                'model': self.chat_data_state.current_state.selected_model
            })
            # 完成回复后最终滚动
            await self.scroll_to_bottom_smooth()
        finally:
            # 恢复输入控件
            await self.stop_waiting_effect()
            self.input_ref['widget'].set_enabled(True)
            self.send_button_ref['widget'].set_enabled(True)
            self.input_ref['widget'].run_method('focus')

    async def clear_chat_content(self):
        """清空聊天内容"""
        try:
            # 清空聊天消息容器
            self.chat_messages_container.clear()
            # 清空聊天数据状态中的消息
            self.chat_data_state.current_chat_messages.clear()
            # 恢复欢迎消息
            self.restore_welcome_message()
            # 显示成功提示
            ui.notify('聊天内容已清空', type='positive')
        except Exception as e:
            ui.notify(f'清空聊天失败: {str(e)}', type='negative')
    #endregion

    #region think内容处理方法
    def has_think_content(self, messages):
        """检测消息列表是否包含think内容"""
        for msg in messages:
            if msg.get('role') == 'assistant' and '<think>' in msg.get('content', ''):
                return True
        return False

    def remove_think_content(self, messages):
        """从消息列表中移除think标签及内容"""
        import re
        cleaned_messages = []
        
        for msg in messages:
            cleaned_msg = msg.copy()
            if msg.get('role') == 'assistant':
                content = msg.get('content', '')
                if '<think>' in content and '</think>' in content:
                    # 移除think标签及其内容
                    cleaned_content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL)
                    cleaned_msg['content'] = cleaned_content.strip()
            
            cleaned_messages.append(cleaned_msg)
        
        return cleaned_messages
    #endregion

    #region 历史记录相关逻辑
    async def render_chat_history(self, chat_id):
        """渲染聊天历史内容"""
        try:
            self.chat_messages_container.clear()
            self.welcome_message_container.clear()
            await self.start_waiting_effect("正在加载聊天记录")

            from database_models.business_models.chat_history_model import ChatHistory
            from auth.database import get_db 
            with get_db() as db:
                chat = db.query(ChatHistory).filter(
                    ChatHistory.id == chat_id,
                    ChatHistory.is_deleted == False
                ).first()
                
                if not chat:
                    ui.notify('聊天记录不存在', type='negative')
                    return
                # 在会话关闭前获取消息数据
                prompt_name = chat.prompt_name
                model_name = chat.model_name
                messages = chat.messages.copy() if chat.messages else []
                chat_title = chat.title
                
            # 清空当前聊天消息并加载历史消息
            self.chat_data_state.current_chat_messages.clear()
            self.chat_data_state.current_chat_messages.extend(messages)
            await self.stop_waiting_effect()
            await self.cleanup_waiting_effect()

            # 恢复历史聊天,侧边栏设置
            self.chat_data_state.current_state.model_select_widget.set_value(model_name)
            self.chat_data_state.current_state.prompt_select_widget.set_value(prompt_name)

            # 清空聊天界面
            self.chat_messages_container.clear()
            # 使用异步任务来渲染消息
            async def render_messages_async():
                for msg in messages:
                    await self.render_single_message(msg)

            # 创建异步任务来处理消息渲染
            ui.timer(0.01, lambda: asyncio.create_task(render_messages_async()), once=True)
            # 滚动到底部
            ui.timer(0.1, lambda: self.scroll_area.scroll_to(percent=1), once=True)
            ui.notify(f'已加载聊天: {chat_title}', type='positive') 
 
        except Exception as e:
            await self.stop_waiting_effect()
            await self.cleanup_waiting_effect()
            self.restore_welcome_message()
            ui.notify('加载聊天失败', type='negative')    
    #endregion

    def render_ui(self):
        """渲染主聊天区域UI"""
        # 主聊天区域 - 占据剩余空间
        with ui.column().classes('flex-grow h-full').style('position: relative; overflow: hidden;'):
            # 聊天消息区域 - 使用 scroll_area 提供更好的滚动体验
            self.scroll_area = ui.scroll_area().classes('w-full').style('height: calc(100% - 80px); padding-bottom: 20px;')

            with self.scroll_area:
                self.chat_messages_container = ui.column().classes('w-full gap-2')  
                # 欢迎消息(可能会被删除)
                self.welcome_message_container = ui.column().classes('w-full')
                with self.welcome_message_container:
                    self.restore_welcome_message()
            # 输入区域 - 固定在底部,距离底部10px
            with ui.row().classes('w-full items-center gap-2 rounded ').style(
                'position: absolute; bottom: 10px; left: 10px; right: 10px; z-index: 1000; '
                'margin: 0 auto; max-width: calc(100% - 20px);'
            ):    
                # 创建textarea并绑定事件
                self.input_ref['widget'] = ui.textarea(
                    placeholder='请输入您的消息...(Enter发送,Shift+Enter换行)'
                ).classes('flex-grow').style(
                    'min-height: 44px; max-height: 120px; resize: none;'
                ).props('outlined dense rounded rows=3').tooltip('输入聊天内容')

                # 使用.on()方法监听keydown事件
                self.input_ref['widget'].on('keydown', self.handle_keydown)
                
                self.send_button_ref['widget'] = ui.button(
                    icon='send',
                    on_click=self.handle_message
                ).props('round dense ').classes('ml-2').tooltip('发送聊天内容')

                # 清空聊天按钮
                self.clear_button_ref['widget'] = ui.button(
                    icon='cleaning_services',
                    on_click=self.clear_chat_content
                ).props('round dense').classes('ml-2').tooltip('清空聊天内容')
```

- **component\chat\chat_component.py**
````python
"""
ChatComponent - 聊天组件统一入口
提供简洁的API供外部调用,封装所有内部实现细节
"""

from nicegui import ui
from typing import Optional
from .chat_data_state import ChatDataState
from .chat_area_manager import ChatAreaManager
from .chat_sidebar_manager import ChatSidebarManager


class ChatComponent:
    """
    聊天组件主类 - 统一入口
    
    使用示例:
```python
    from component.chat import ChatComponent
    
    # 基础使用
    chat = ChatComponent()
    chat.render()
    
    # 自定义配置
    chat = ChatComponent(
        sidebar_visible=True,
        default_model='deepseek-chat',
        default_prompt='一企一档专家',
        is_record_history=True
    )
    chat.render()
```
    """
    
    def __init__(
        self,
        sidebar_visible: bool = True,
        default_model: Optional[str] = None,
        default_prompt: Optional[str] = None,
        is_record_history: bool = True
    ):
        """
        初始化聊天组件
        
        Args:
            sidebar_visible: 侧边栏是否可见,默认为True
            default_model: 指定的默认LLM模型,默认为None(使用配置文件中的默认值)
            default_prompt: 指定的默认提示词模板,默认为None(使用配置文件中的默认值)
            is_record_history: 是否记录聊天历史到数据库,默认为True
        """
        self.sidebar_visible = sidebar_visible
        self.default_model = default_model
        self.default_prompt = default_prompt
        self.is_record_history = is_record_history
        
        # 初始化数据状态
        self.chat_data_state = ChatDataState()
        
        # 初始化管理器(延迟到render时创建,因为需要UI上下文)
        self.chat_area_manager: Optional[ChatAreaManager] = None
        self.chat_sidebar_manager: Optional[ChatSidebarManager] = None
        
    def render(self):
        """
        渲染聊天组件UI
        必须在NiceGUI的UI上下文中调用
        """
        # 添加聊天组件专用样式
        self._add_chat_styles()
        
        # 创建管理器实例
        self.chat_area_manager = ChatAreaManager(self.chat_data_state)
        self.chat_sidebar_manager = ChatSidebarManager(
            chat_data_state=self.chat_data_state,
            chat_area_manager=self.chat_area_manager,
            sidebar_visible=self.sidebar_visible,
            default_model=self.default_model,
            default_prompt=self.default_prompt,
            is_record_history=self.is_record_history
        )
        
        # 渲染UI结构
        with ui.row().classes('w-full h-full chat-archive-container').style(
            'height: calc(100vh - 120px); margin: 0; padding: 0;'
        ):
            # 侧边栏
            self.chat_sidebar_manager.render_ui()
            # 主聊天区域
            self.chat_area_manager.render_ui()
    
    def _add_chat_styles(self):
        """添加聊天组件专用CSS样式"""
        ui.add_head_html('''
            <style>
            /* 聊天组件专用样式 - 只影响聊天组件内部,不影响全局 */
            .chat-archive-container {
                height: calc(100vh - 145px) !important;
                margin: 0 !important;
                padding: 0 !important;
                overflow-y: auto !important;
            }        
            .chat-archive-sidebar {
                border-right: 1px solid #e5e7eb;
                overflow-y: auto;
            }
            .chat-archive-sidebar::-webkit-scrollbar {
                width: 2px;
            }
            .chat-archive-sidebar::-webkit-scrollbar-track {
                background: transparent;
            }
            .chat-archive-sidebar::-webkit-scrollbar-thumb {
                background-color: #d1d5db;
                border-radius: 3px;
            }
            .chat-archive-sidebar::-webkit-scrollbar-thumb:hover {
                background-color: #9ca3af;
            }
            /* 优化 scroll_area 内容区域的样式 */
            .q-scrollarea__content {
                min-height: 100%;
            }
            .chathistorylist-hide-scrollbar {
                overflow-y: auto;
                scrollbar-width: none;
                -ms-overflow-style: none;
            }
            .chathistorylist-scrollbar::-webkit-scrollbar {
                display: none;
            }
            </style>
        ''')
    
    def get_chat_data_state(self) -> ChatDataState:
        """获取聊天数据状态对象"""
        return self.chat_data_state
    
    def get_chat_area_manager(self) -> Optional[ChatAreaManager]:
        """获取聊天区域管理器"""
        return self.chat_area_manager
    
    def get_chat_sidebar_manager(self) -> Optional[ChatSidebarManager]:
        """获取侧边栏管理器"""
        return self.chat_sidebar_manager
````

- **component\chat\chat_data_state.py**
```python
"""
聊天数据状态管理
定义聊天组件使用的所有数据结构
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Union

@dataclass
class SelectedValues:
    """数据输入值数据结构 - 通过 textarea JSON 输入"""
    # 层级数据
    # l1: Optional[str] = None
    # l2: Optional[str] = None
    # l3: Optional[str] = None
    # field: Union[List[str], str, None] = None
    # field_name: Union[List[str], str, None] = None
    
    # # 扩展字段
    # data_url: Optional[str] = None
    # full_path_code: Optional[str] = None
    # full_path_name: Optional[str] = None
    
    # textarea 输入相关
    raw_input: Optional[str] = None  # textarea原始输入内容

@dataclass
class CurrentState:
    """当前状态数据结构"""
    model_options: List[str] = field(default_factory=list)
    default_model: str = 'deepseek-chat'
    selected_model: str = 'deepseek-chat'
    model_select_widget: Optional[Any] = None
    prompt_select_widget: Optional[Any] = None

@dataclass
class CurrentPromptConfig:
    """当前提示词配置数据结构"""
    selected_prompt: Optional[str] = None
    system_prompt: str = ''
    examples: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ChatDataState:
    """聊天数据状态主类"""
    # 模型相关
    model_options: List[str] = field(default_factory=list)
    default_model: str = 'deepseek-chat'
    current_model_config: Dict[str, Any] = field(default_factory=dict)
    
    # 当前状态
    current_state: CurrentState = field(default_factory=CurrentState)
    
    # 记录当前聊天中的消息
    current_chat_messages: List[Dict] = field(default_factory=list)
    
    # 提示词初始化
    prompt_options: List[str] = field(default_factory=list)
    default_prompt: Optional[str] = None
    current_prompt_config: CurrentPromptConfig = field(default_factory=CurrentPromptConfig)
    
    # 数据输入开关和值
    switch: bool = False
    selected_values: SelectedValues = field(default_factory=SelectedValues)

    # 当前聊天id
    current_chat_id: Optional[int] = None
```

- **component\chat\chat_sidebar_manager.py**
```python
"""
ChatSidebarManager - 聊天侧边栏管理器
负责管理侧边栏的UI和相关业务逻辑
"""
from datetime import datetime
from nicegui import ui
from typing import Optional
from .chat_data_state import ChatDataState

from .config import (
    get_model_options_for_select, 
    get_model_config, 
    get_default_model,
    reload_llm_config,
    get_model_config_info,
    get_prompt_options_for_select,
    get_system_prompt,
    get_examples,
    get_default_prompt,
    reload_prompt_config
)

class ChatSidebarManager:
    """聊天侧边栏管理器"""
    
    def __init__(
        self, 
        chat_data_state: ChatDataState, 
        chat_area_manager,
        sidebar_visible: bool = True, 
        default_model: Optional[str] = None, 
        default_prompt: Optional[str] = None,
        is_record_history: bool = True
    ):
        """
        初始化侧边栏管理器
        
        Args:
            chat_data_state: 聊天数据状态对象
            chat_area_manager: 聊天区域管理器实例
            sidebar_visible: 侧边栏是否可见,默认为True
            default_model: 指定的默认模型,默认为None
            default_prompt: 指定的默认提示词,默认为None
            is_record_history: 是否记录聊天历史,默认为True
        """
        self.chat_data_state = chat_data_state
        self.chat_area_manager = chat_area_manager
        
        # UI组件引用
        self.history_list_container = None
        self.switch = None
        self.data_input_textarea = None  # textarea输入框
        self.validation_status_label = None  # 验证状态标签
        
        # 存储侧边栏可见性配置
        self.sidebar_visible = sidebar_visible
        self.is_record_history = is_record_history

        # 初始化数据
        self._initialize_data(default_model, default_prompt)
    
    def _initialize_data(self, default_model_param: Optional[str] = None, default_prompt_param: Optional[str] = None):
        """初始化数据状态"""
        # 初始化模型相关数据
        self.chat_data_state.model_options = get_model_options_for_select()
        
        if default_model_param and default_model_param in self.chat_data_state.model_options:
            self.chat_data_state.default_model = default_model_param
        else:
            self.chat_data_state.default_model = get_default_model() or 'deepseek-chat'
            if default_model_param:
                ui.notify(f"指定的模型 '{default_model_param}' 不存在，使用默认模型", type='warning')

        self.chat_data_state.current_model_config = {
            'selected_model': self.chat_data_state.default_model, 
            'config': get_model_config(self.chat_data_state.default_model)
        }
        
        # 初始化当前状态
        self.chat_data_state.current_state.model_options = self.chat_data_state.model_options
        self.chat_data_state.current_state.default_model = self.chat_data_state.default_model
        self.chat_data_state.current_state.selected_model = self.chat_data_state.default_model
        
        # 初始化提示词数据
        self.chat_data_state.prompt_options = get_prompt_options_for_select()
        
        if default_prompt_param and default_prompt_param in self.chat_data_state.prompt_options:
            self.chat_data_state.default_prompt = default_prompt_param
        else:
            self.chat_data_state.default_prompt = get_default_prompt() or (
                self.chat_data_state.prompt_options[0] if self.chat_data_state.prompt_options else None
            )
            if default_prompt_param:
                ui.notify(f"指定的提示词 '{default_prompt_param}' 不存在，使用默认提示词", type='warning')

        self.chat_data_state.current_prompt_config.selected_prompt = self.chat_data_state.default_prompt
        self.chat_data_state.current_prompt_config.system_prompt = (
            get_system_prompt(self.chat_data_state.default_prompt) 
            if self.chat_data_state.default_prompt else ''
        )
        self.chat_data_state.current_prompt_config.examples = (
            get_examples(self.chat_data_state.default_prompt) 
            if self.chat_data_state.default_prompt else {}
        )
        self.chat_data_state.current_chat_id = None

    # region 模型选择相关处理逻辑
    def on_model_change(self, e):
        """模型选择变化事件处理"""
        selected_model = e.value
        
        # 更新当前状态
        self.chat_data_state.current_state.selected_model = selected_model
        self.chat_data_state.current_model_config['selected_model'] = selected_model
        self.chat_data_state.current_model_config['config'] = get_model_config(selected_model)
        
        # 显示选择信息
        ui.notify(f'已切换到模型: {selected_model}')
    
    def on_refresh_model_config(self):
        """刷新模型配置"""
        try:
            ui.notify('正在刷新模型配置...', type='info')
            success = reload_llm_config()
            
            if success:
                # 重新获取配置
                new_options = get_model_options_for_select()
                new_default = get_default_model() or 'deepseek-chat'
                
                # 更新数据状态
                self.chat_data_state.model_options = new_options
                self.chat_data_state.default_model = new_default
                self.chat_data_state.current_state.model_options = new_options
                self.chat_data_state.current_state.default_model = new_default
                
                # 更新UI组件
                if self.chat_data_state.current_state.model_select_widget:
                    current_selection = self.chat_data_state.current_state.selected_model
                    if current_selection not in new_options:
                        current_selection = new_default
                    
                    self.chat_data_state.current_state.model_select_widget.set_options(new_options)
                    self.chat_data_state.current_state.model_select_widget.set_value(current_selection)
                    self.chat_data_state.current_state.selected_model = current_selection
                    
                    # 同步更新 current_model_config
                    self.chat_data_state.current_model_config['selected_model'] = current_selection
                    self.chat_data_state.current_model_config['config'] = get_model_config(current_selection)
                
                # 显示刷新结果
                config_info = get_model_config_info()
                ui.notify(
                    f'配置刷新成功！共加载 {config_info["total_models"]} 个模型，'
                    f'其中 {config_info["enabled_models"]} 个已启用',
                    type='positive'
                )
            else:
                ui.notify('配置刷新失败，请检查配置文件', type='negative')
                
        except Exception as e:
            ui.notify(f'刷新配置时出错: {str(e)}', type='negative')
    
    def on_prompt_change(self, e):
        """提示词选择变化事件处理"""
        selected_prompt_key = e.value
        
        # 获取系统提示词内容和示例
        system_prompt = get_system_prompt(selected_prompt_key)
        examples = get_examples(selected_prompt_key)
        
        # 更新当前提示词配置
        self.chat_data_state.current_prompt_config.selected_prompt = selected_prompt_key
        self.chat_data_state.current_prompt_config.system_prompt = system_prompt or ''
        self.chat_data_state.current_prompt_config.examples = examples or {}
        
        # 显示选择信息
        ui.notify(f'已切换到提示词: {selected_prompt_key}')
    
    def on_refresh_prompt_config(self):
        """刷新提示词配置"""
        try:
            ui.notify('正在刷新提示词配置...', type='info')
            success = reload_prompt_config()
            
            if success:
                # 重新获取配置
                prompt_options = get_prompt_options_for_select()
                new_default = get_default_prompt() or (prompt_options[0] if prompt_options else None)
                
                # 更新数据状态
                self.chat_data_state.prompt_options = prompt_options
                self.chat_data_state.default_prompt = new_default
                
                # 更新UI组件
                if self.chat_data_state.current_state.prompt_select_widget:
                    current_selection = self.chat_data_state.current_prompt_config.selected_prompt
                    if current_selection not in prompt_options:
                        current_selection = new_default
                    
                    self.chat_data_state.current_state.prompt_select_widget.set_options(prompt_options)
                    self.chat_data_state.current_state.prompt_select_widget.set_value(current_selection)
                    
                    self.chat_data_state.current_prompt_config.selected_prompt = current_selection
                    self.chat_data_state.current_prompt_config.system_prompt = (
                        get_system_prompt(current_selection) if current_selection else ''
                    )
                    self.chat_data_state.current_prompt_config.examples = (
                        get_examples(current_selection) if current_selection else {}
                    )
                
                ui.notify(f'提示词配置刷新成功，共加载 {len(prompt_options)} 个模板', type='positive')
            else:
                ui.notify('提示词配置刷新失败', type='negative')
                
        except Exception as e:
            ui.notify(f'刷新提示词配置时发生错误: {str(e)}', type='negative')
    # endregion 模型选择相关逻辑
    
    # region textarea 数据输入相关逻辑
    def _render_textarea_input(self):
        """
        渲染textarea输入框 - 极简版
        """
        # textarea输入框 - 直接双向绑定到 selected_values.raw_input
        self.data_input_textarea = ui.textarea(
            placeholder='请输入提示数据...\n\n支持多行输入，无格式限制',
            value=''
        ).classes('w-full').props('outlined dense').style(
            'min-height: 120px; '
            'font-size: 14px; '
            'line-height: 1.6;'
        ).bind_value(self.chat_data_state.selected_values, 'raw_input')
        
        # 使用说明
        with ui.row().classes('w-full mt-1 items-center'):
            ui.icon('info', size='sm').classes('text-blue-500')
            ui.label('启用开关后，此处内容将附加到您的对话消息中').classes('text-xs text-gray-600')
    # endregion textarea 数据输入相关逻辑
    
    #region 新建会话相关逻辑
    async def on_create_new_chat(self):
        """新建聊天会话"""
        try:
            # 🔥 新增：先判断是否已有聊天记录，执行插入或更新操作
            if self.chat_data_state.current_chat_messages:
                # 检查当前是否为加载的历史对话（通过检查 current_chat_messages 是否与某个历史记录匹配）
                existing_chat_id = self.get_current_loaded_chat_id()
                
                if existing_chat_id:
                    # 更新现有聊天记录
                    update_success = self.update_existing_chat_to_database(existing_chat_id)
                    if update_success:
                        ui.notify('对话已更新', type='positive')
                    else:
                        ui.notify('更新对话失败', type='negative')
                        return
                else:
                    # 插入新的聊天记录
                    save_success = self.save_chat_to_database()
                    if save_success:
                        ui.notify('对话已保存', type='positive')
                    else:
                        ui.notify('保存对话失败', type='negative')
                        return
                
                # 清空当前聊天记录
                self.chat_data_state.current_chat_messages.clear()
                # 恢复欢迎消息
                self.chat_area_manager.restore_welcome_message()
                # 新增：自动刷新聊天历史列表
                self.refresh_chat_history_list()
                # 重置当前加载的聊天ID
                self.reset_current_loaded_chat_id()     
            else:
                self.chat_area_manager.restore_welcome_message()
                ui.notify('界面已重置', type='info')
                
        except Exception as e:
            ui.notify(f'创建新对话失败: {str(e)}', type='negative')
    
    def get_current_loaded_chat_id(self):
        """获取当前加载的聊天记录ID"""
        return self.chat_data_state.current_chat_id

    def set_current_loaded_chat_id(self, chat_id):
        """设置当前加载的聊天记录ID"""
        self.chat_data_state.current_chat_id = chat_id

    def reset_current_loaded_chat_id(self):
        """重置当前加载的聊天记录ID"""
        self.chat_data_state.current_chat_id = None

    def update_existing_chat_to_database(self, chat_id):
        """更新现有的聊天记录到数据库"""
        if chat_id is None:
            return True
        try:
            from auth import auth_manager
            from database_models.business_models.chat_history_model import ChatHistory
            from auth.database import get_db
            
            current_user = auth_manager.current_user
            if not current_user:
                ui.notify('用户未登录，无法更新聊天记录', type='warning')
                return False
            
            if not self.chat_data_state.current_chat_messages:
                ui.notify('没有聊天记录需要更新', type='info')
                return False
            
            with get_db() as db:
                chat_history = db.query(ChatHistory).filter(
                    ChatHistory.id == chat_id,
                    ChatHistory.created_by == current_user.id,
                    ChatHistory.is_deleted == False
                ).first()
                
                if not chat_history:
                    ui.notify('聊天记录不存在或无权限', type='negative')
                    return False
                
                # 更新聊天记录
                chat_history.messages = self.chat_data_state.current_chat_messages.copy()
                chat_history.model_name = self.chat_data_state.current_state.selected_model
                
                # 使用模型的内置方法更新统计信息
                chat_history.update_message_stats()
                chat_history.updated_at = datetime.now()
                
                db.commit()
                return True
                
        except Exception as e:
            ui.notify(f'更新聊天记录失败: {str(e)}', type='negative')
            return False

    def save_chat_to_database(self):
        """保存新的聊天记录到数据库"""
        try:
            from auth import auth_manager
            from database_models.business_models.chat_history_model import ChatHistory
            from database_models.business_utils import AuditHelper
            from auth.database import get_db
            
            current_user = auth_manager.current_user
            if not current_user:
                ui.notify('用户未登录，无法保存聊天记录', type='warning')
                return False
            
            if not self.chat_data_state.current_chat_messages:
                ui.notify('没有聊天记录需要保存', type='info')
                return False
            
            # 生成聊天标题（使用第一条用户消息的前20个字符）
            title = "新对话"
            for msg in self.chat_data_state.current_chat_messages:
                if msg.get('role') == 'user':
                    content = msg.get('content', '')
                    title = content[:20] + ('...' if len(content) > 20 else '')
                    break
            
            # 处理think内容：检测是否有think内容，有则移除
            messages_to_save = self.chat_data_state.current_chat_messages.copy()
            if self.chat_area_manager.has_think_content(messages_to_save):
                messages_to_save = self.chat_area_manager.remove_think_content(messages_to_save)
            
            with get_db() as db:
                chat_history = ChatHistory(
                    title=title,
                    model_name=self.chat_data_state.current_state.selected_model,
                    prompt_name = self.chat_data_state.current_prompt_config.selected_prompt,
                    messages=messages_to_save
                )
                
                # 使用模型的内置方法更新统计信息
                chat_history.update_message_stats()
                
                # 设置审计字段
                AuditHelper.set_audit_fields(chat_history, current_user.id)
                
                db.add(chat_history)
                db.commit()
                
                return True
                
        except Exception as e:
            ui.notify(f'保存聊天记录失败: {str(e)}', type='negative')
            return False
    #endregion 新建会话相关逻辑
    
    #region 历史记录相关逻辑
    def load_chat_histories(self):
        """从数据库加载聊天历史列表"""
        try:
            from auth import auth_manager
            from database_models.business_models.chat_history_model import ChatHistory
            from auth.database import get_db
            
            current_user = auth_manager.current_user
            if not current_user:
                return []
            
            with get_db() as db:
                chat_histories = ChatHistory.get_user_recent_chats(
                    db_session=db, 
                    user_id=current_user.id, 
                    limit=20
                )
                
                # 转换为UI需要的数据结构
                history_list = []
                for chat in chat_histories:
                    preview = chat.get_message_preview(30)
                    duration_info = chat.get_duration_info()
                    
                    history_list.append({
                        'id': chat.id,
                        'title': chat.title,
                        'preview': preview,
                        'created_at': chat.created_at.strftime('%Y-%m-%d %H:%M'),
                        'updated_at': chat.updated_at.strftime('%Y-%m-%d %H:%M'),
                        'last_message_at': chat.last_message_at.strftime('%Y-%m-%d %H:%M') if chat.last_message_at else None,
                        'message_count': chat.message_count,
                        'model_name': chat.model_name,
                        'duration_minutes': duration_info['duration_minutes'],
                        'chat_object': chat
                    })
                return history_list        
        except Exception as e:
            ui.notify('加载聊天历史失败', type='negative')
            return []
        
    async def on_load_chat_history(self, chat_id):
        """加载指定的聊天历史到当前对话中"""
        # 设置当前加载的聊天ID，用于后续更新判断
        self.set_current_loaded_chat_id(chat_id)
        # 调用聊天区域管理器渲染聊天历史
        await self.chat_area_manager.render_chat_history(chat_id)
    
    def on_edit_chat_history(self, chat_id):
        """编辑聊天历史记录"""
        def save_title():
            try:
                from auth import auth_manager
                from database_models.business_models.chat_history_model import ChatHistory
                from auth.database import get_db
                
                current_user = auth_manager.current_user
                if not current_user:
                    ui.notify('用户未登录', type='warning')
                    return
                
                new_title = title_input.value.strip()
                if not new_title:
                    ui.notify('标题不能为空', type='warning')
                    return
                
                with get_db() as db:
                    chat_history = db.query(ChatHistory).filter(
                        ChatHistory.id == chat_id,
                        ChatHistory.created_by == current_user.id,
                        ChatHistory.is_deleted == False
                    ).first()
                    
                    if chat_history:
                        chat_history.title = new_title
                        chat_history.updated_at = datetime.now()
                        db.commit()
                        
                        # 刷新历史记录列表
                        self.refresh_chat_history_list()
                        ui.notify('标题修改成功', type='positive')
                        dialog.close()
                    else:
                        ui.notify('聊天记录不存在', type='negative')
                        
            except Exception as e:
                ui.notify(f'修改失败: {str(e)}', type='negative')
        
        # 获取当前标题
        try:
            from auth import auth_manager
            from database_models.business_models.chat_history_model import ChatHistory
            from auth.database import get_db
            
            current_user = auth_manager.current_user
            if not current_user:
                ui.notify('用户未登录', type='warning')
                return
            
            with get_db() as db:
                chat_history = db.query(ChatHistory).filter(
                    ChatHistory.id == chat_id,
                    ChatHistory.created_by == current_user.id,
                    ChatHistory.is_deleted == False
                ).first()
                
                if not chat_history:
                    ui.notify('聊天记录不存在', type='negative')
                    return
                
                current_title = chat_history.title
        except Exception as e:
            ui.notify('获取聊天记录失败', type='negative')
            return
        
        # 显示编辑对话框
        with ui.dialog() as dialog:
            with ui.card().classes('w-96'):
                with ui.column().classes('w-full gap-4'):
                    ui.label('编辑聊天标题').classes('text-lg font-medium')
                    title_input = ui.input('聊天标题', value=current_title).classes('w-full')
                    
                    with ui.row().classes('w-full justify-end gap-2'):
                        ui.button('取消', on_click=dialog.close).props('flat')
                        ui.button('保存', on_click=save_title).props('color=primary')
        
        dialog.open()
    
    def on_delete_chat_history(self, chat_id):
        """删除聊天历史记录"""
        def confirm_delete():
            try:
                from auth import auth_manager
                from database_models.business_models.chat_history_model import ChatHistory
                from auth.database import get_db
                
                current_user = auth_manager.current_user
                if not current_user:
                    ui.notify('用户未登录，无法删除聊天记录', type='warning')
                    return
                
                with get_db() as db:
                    chat_history = db.query(ChatHistory).filter(
                        ChatHistory.id == chat_id,
                        ChatHistory.created_by == current_user.id,
                        ChatHistory.is_deleted == False
                    ).first()
                    
                    if not chat_history:
                        ui.notify('聊天记录不存在或无权限删除', type='negative')
                        return
                    
                    chat_title = chat_history.title
                    
                    # 软删除操作
                    chat_history.is_deleted = True
                    chat_history.deleted_at = datetime.now()
                    chat_history.deleted_by = current_user.id
                    chat_history.is_active = False
                    
                    db.commit()
                    
                    # 如果删除的是当前加载的聊天，需要重置界面
                    current_loaded_id = self.get_current_loaded_chat_id()
                    if current_loaded_id == chat_id:
                        self.chat_data_state.current_chat_messages.clear()
                        self.chat_area_manager.restore_welcome_message()
                        self.reset_current_loaded_chat_id()
                        
                    # 刷新聊天历史列表
                    self.refresh_chat_history_list()
                    
                    ui.notify(f'已删除聊天: {chat_title}', type='positive')
                    
            except Exception as e:
                ui.notify(f'删除聊天失败: {str(e)}', type='negative')
        
        # 显示确认对话框
        with ui.dialog() as dialog:
            with ui.card().classes('w-80'):
                with ui.column().classes('w-full'):
                    ui.icon('warning', size='lg').classes('text-orange-500 mx-auto')
                    ui.label('确认删除聊天记录？').classes('text-lg font-medium text-center')
                    ui.label('删除后可以在回收站中恢复').classes('text-sm text-gray-600 text-center')
                    
                    with ui.row().classes('w-full justify-end gap-2'):
                        ui.button('取消', on_click=dialog.close).props('flat')
                        ui.button('删除', on_click=lambda: [confirm_delete(), dialog.close()]).props('color=negative')
        
        dialog.open()
    
    def create_chat_history_list(self):
        """创建聊天历史列表组件"""
        chat_histories = self.load_chat_histories()
        
        if not chat_histories:
            with ui.column().classes('w-full text-center'):
                ui.icon('chat_bubble_outline', size='lg').classes('text-gray-400 mb-2')
                ui.label('暂无聊天记录').classes('text-gray-500 text-sm')
            return
        
        with ui.list().classes('w-full').props('dense separator'):
            for history in chat_histories:
                with ui.item(on_click=lambda chat_id=history['id']: self.on_load_chat_history(chat_id)).classes('cursor-pointer'):
                    with ui.item_section():
                        ui.item_label(history['title']).classes('font-medium')
                        info_text = f"{history['updated_at']} • {history['message_count']}条消息"
                        if history['duration_minutes'] > 0:
                            info_text += f" • {history['duration_minutes']}分钟"
                        if history['model_name']:
                            info_text += f" • {history['model_name']}"
                        ui.item_label(info_text).props('caption').classes('text-xs')
                    
                    with ui.item_section().props('side'):
                        with ui.row().classes('gap-1'):
                            ui.button(
                                icon='edit'
                            ).on('click.stop', lambda chat_id=history['id']: self.on_edit_chat_history(chat_id)).props('dense flat round size="sm"').classes('text-blue-600').tooltip('编辑')
                            
                            ui.button(
                                icon='delete'
                            ).on('click.stop', lambda chat_id=history['id']: self.on_delete_chat_history(chat_id)).props('dense flat round size="sm"').classes('text-red-600').tooltip('删除')
        
    def refresh_chat_history_list(self):
        """刷新聊天历史列表"""
        try:
            if self.history_list_container:
                self.history_list_container.clear()
                with self.history_list_container:
                    self.create_chat_history_list()
                ui.notify('聊天历史已刷新', type='positive')
        except Exception as e:
            ui.notify('刷新失败', type='negative')
    #endregion 历史记录相关逻辑
    
    def render_ui(self):
        """渲染侧边栏UI"""
        visibility_style = 'display: none;' if not self.sidebar_visible else ''
        with ui.column().classes('chat-archive-sidebar h-full').style(
            f'width: 280px; min-width: 280px; {visibility_style}'
        ):
            # 侧边栏标题
            with ui.row().classes('w-full'):
                ui.icon('menu', size='md').classes('text-gray-600')
                ui.label('功能菜单').classes('text-lg font-semibold')
            
            # 侧边栏内容
            with ui.column().classes('w-full items-center'):
                # 新建对话按钮
                ui.button(
                    '新建对话', 
                    icon='add', 
                    on_click=self.on_create_new_chat
                ).classes('w-64').props('outlined rounded').tooltip('创建新聊天/保存当前聊天')
                        
                # 选择模型expansion组件
                with ui.expansion('选择模型', icon='view_in_ar').classes('w-full').tooltip('选择大语言模型'):
                    with ui.column().classes('w-full'):
                        # 配置管理按钮行
                        with ui.row().classes('w-full'):
                            ui.button(
                                '刷新配置', 
                                icon='refresh',
                                on_click=self.on_refresh_model_config
                            ).classes('text-xs').props('dense flat color="primary"').style('min-width: 80px;')
                        
                        # 模型选择下拉框
                        self.chat_data_state.current_state.model_select_widget = ui.select(
                            options=self.chat_data_state.current_state.model_options,
                            value=self.chat_data_state.current_state.default_model,
                            with_input=True,
                            on_change=self.on_model_change
                        ).classes('w-full').props('autofocus dense')

                # 上下文模板expansion组件
                with ui.expansion('上下文模板', icon='pattern').classes('w-full').tooltip('选择上下文模型'):
                    with ui.column().classes('w-full'):
                        # 配置管理按钮行
                        with ui.row().classes('w-full'):
                            ui.button(
                                '刷新配置', 
                                icon='refresh',
                                on_click=self.on_refresh_prompt_config
                            ).classes('text-xs').props('dense flat color="primary"').style('min-width: 80px;')
                        
                        # 提示词选择下拉框
                        self.chat_data_state.current_state.prompt_select_widget = ui.select(
                            options=self.chat_data_state.prompt_options, 
                            value=self.chat_data_state.default_prompt, 
                            with_input=True,
                            on_change=self.on_prompt_change
                        ).classes('w-full').props('autofocus dense')

                # 🔥 提示数据 - 只使用textarea
                with ui.expansion('提示数据', icon='tips_and_updates').classes('w-full').tooltip('输入提示数据'):
                    with ui.column().classes('w-full chathistorylist-hide-scrollbar').style('flex-grow: 1;'):
                        self.switch = ui.switch('启用', value=False).bind_value(self.chat_data_state, 'switch')
                        
                        # 渲染textarea输入
                        self._render_textarea_input()
                    
                # 聊天历史expansion组件
                with ui.expansion('历史消息', icon='history').classes('w-full').tooltip('操作历史聊天内容'):
                    with ui.column().classes('w-full'):
                        # 添加刷新按钮
                        with ui.row().classes('w-full'):
                            ui.button(
                                '刷新历史', 
                                icon='refresh',
                                on_click=self.refresh_chat_history_list
                            ).classes('text-xs').props('dense flat color="primary"').style('min-width: 80px;')
                        
                        # 聊天历史列表容器
                        self.history_list_container = ui.column().classes('w-full h-96 chathistorylist-hide-scrollbar')
                        with self.history_list_container:
                            self.create_chat_history_list()
```

- **component\chat\config.py**
```python
"""
LLM模型配置管理器
读取YAML配置文件，为chat_component提供模型选择数据
"""
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional

# LLMModelConfigManager类读取配置文件llm_model_config.yaml
class LLMModelConfigManager:
    """LLM模型配置管理器"""
    
    def __init__(self, config_file_path: Optional[str] = None):
        """
        初始化配置管理器
        
        Args:
            config_file_path: YAML配置文件路径，如果为None则使用默认路径
        """
        if config_file_path is None:
            # 默认配置文件路径：项目根目录的 config/yaml/llm_model_config.yaml
            current_dir = Path(__file__).parent
            project_root = current_dir.parent.parent  # 向上两级到项目根目录
            self.config_file_path = project_root / "config" / "yaml" / "llm_model_config.yaml"
        else:
            self.config_file_path = Path(config_file_path)
        
        self._yaml_config = None
        self._model_options = []
        self._load_config()
    
    def _load_config(self) -> None:
        """从YAML文件加载配置"""
        try:
            if not self.config_file_path.exists():
                raise FileNotFoundError(f"LLM模型配置文件不存在: {self.config_file_path}")
            
            with open(self.config_file_path, 'r', encoding='utf-8') as file:
                self._yaml_config = yaml.safe_load(file)
            
            if not self._yaml_config:
                raise ValueError("配置文件为空或格式无效")
            
            # 解析配置并生成模型选项
            self._parse_model_config()
                
        except Exception as e:
            print(f"错误: 无法加载LLM配置文件: {e}")
            print("请确保配置文件存在且格式正确")
            self._yaml_config = None
            self._model_options = []
    
    def _parse_model_config(self) -> None:
        """解析YAML配置，生成模型选项列表"""
        self._model_options = []
        
        # 遍历所有提供商的配置
        for provider_key, provider_config in self._yaml_config.items():
            # 跳过非模型配置节点
            if provider_key in ['defaults', 'metadata']:
                continue
            
            if isinstance(provider_config, dict):
                # 遍历该提供商下的所有模型
                for model_key, model_config in provider_config.items():
                    if isinstance(model_config, dict):
                        # 检查模型是否启用
                        if model_config.get('enabled', True):
                            option = {
                                'key': model_key,
                                'label': model_config.get('name', model_key),
                                'value': model_key,
                                'config': model_config,
                                'provider': provider_key,
                                'description': model_config.get('description', '')
                            }
                            self._model_options.append(option)
    
    def get_model_options_for_select(self, include_disabled: bool = False) -> List[str]:
        """
        获取用于ui.select的模型选项
        
        Args:
            include_disabled: 是否包含禁用的模型，默认为False
        
        Returns:
            List[str]: 模型key列表
        """
        if include_disabled:
            return [option['key'] for option in self._model_options]
        return [option['key'] for option in self._model_options 
                if option['config'].get('enabled', True)]

    def get_model_config(self, model_key: str) -> Optional[Dict[str, Any]]:
        """
        根据模型key获取配置
        
        Args:
            model_key: 模型标识符
            
        Returns:
            Dict[str, Any]: 模型的完整配置信息，如果未找到则返回None
        """
        for option in self._model_options:
            if option['key'] == model_key:
                return option['config']
        return None
    
    def get_default_model(self) -> Optional[str]:
        """
        获取默认模型key（第一个启用的模型）
        
        Returns:
            str: 默认模型key，如果没有启用的模型则返回None
        """
        enabled_models = [opt for opt in self._model_options 
                         if opt['config'].get('enabled', True)]
        return enabled_models[0]['key'] if enabled_models else None
    
    def reload_config(self) -> bool:
        """
        重新加载配置文件
        
        Returns:
            bool: 重新加载是否成功
        """
        try:
            old_model_count = len(self._model_options)
            
            # 重新加载配置
            self._yaml_config = None
            self._model_options = []
            self._load_config()
            
            new_model_count = len(self._model_options)
            
            print(f"配置重新加载完成: {old_model_count} -> {new_model_count} 个模型")
            return True
            
        except Exception as e:
            print(f"配置重新加载失败: {e}")
            return False
    
    def get_config_info(self) -> Dict[str, Any]:
        """
        获取配置文件信息
        
        Returns:
            Dict: 配置文件信息
        """
        return {
            'config_file_path': str(self.config_file_path),
            'file_exists': self.config_file_path.exists(),
            'total_models': len(self._model_options),
            'enabled_models': len([opt for opt in self._model_options 
                                 if opt['config'].get('enabled', True)]),
            'providers': list(set(option['provider'] for option in self._model_options)),
            'last_modified': self.config_file_path.stat().st_mtime if self.config_file_path.exists() else None
        }

# LLMModelConfigManager 全局配置管理器实例
_config_manager = None

def get_llm_config_manager() -> LLMModelConfigManager:
    """
    获取全局LLM配置管理器实例（单例模式）
    
    Returns:
        LLMModelConfigManager: 配置管理器实例
    """
    global _config_manager
    if _config_manager is None:
        _config_manager = LLMModelConfigManager()
    return _config_manager

def get_model_options_for_select(include_disabled: bool = False) -> List[str]:
    """
    获取用于ui.select的模型选项的便捷函数
    
    Args:
        include_disabled: 是否包含禁用的模型，默认为False
    
    Returns:
        List[str]: 模型key列表
    """
    return get_llm_config_manager().get_model_options_for_select(include_disabled)

def get_model_config(model_key: str) -> Optional[Dict[str, Any]]:
    """
    根据模型key获取配置的便捷函数
    
    Args:
        model_key: 模型标识符
        
    Returns:
        Dict[str, Any]: 模型配置信息
    """
    return get_llm_config_manager().get_model_config(model_key)

def get_default_model() -> Optional[str]:
    """
    获取默认模型key的便捷函数
    
    Returns:
        str: 默认模型key
    """
    return get_llm_config_manager().get_default_model()

def reload_llm_config() -> bool:
    """
    重新加载LLM配置的便捷函数
    
    Returns:
        bool: 重新加载是否成功
    """
    return get_llm_config_manager().reload_config()

def get_model_config_info() -> Dict[str, Any]:
    """
    获取配置信息的便捷函数
    
    Returns:
        Dict: 配置文件信息
    """
    return get_llm_config_manager().get_config_info()

# SystemPromptConfigManager类读取配置文件system_prompt_config.yaml
class SystemPromptConfigManager:
    """系统提示词配置管理器"""
    def __init__(self, config_file_path: Optional[str] = None):
        """
        初始化配置管理器
        
        Args:
            config_file_path: YAML配置文件路径，如果为None则使用默认路径
        """
        if config_file_path is None:
            # 默认配置文件路径：项目根目录的 config/yaml/system_prompt_config.yaml
            current_dir = Path(__file__).parent
            project_root = current_dir.parent.parent  # 向上两级到项目根目录
            self.config_file_path = project_root / "config" / "yaml" / "system_prompt_config.yaml"
        else:
            self.config_file_path = Path(config_file_path)
        
        self._yaml_config = None
        self._prompt_options = []
        self._load_config()

    def _load_config(self) -> None:
        """从YAML文件加载配置"""
        try:
            if not self.config_file_path.exists():
                raise FileNotFoundError(f"系统提示词配置文件不存在: {self.config_file_path}")
            
            with open(self.config_file_path, 'r', encoding='utf-8') as file:
                self._yaml_config = yaml.safe_load(file)
            
            if not self._yaml_config:
                raise ValueError("配置文件为空或格式无效")
            
            # 解析配置并生成提示词选项
            self._parse_prompt_config()
                
        except Exception as e:
            print(f"错误: 无法加载系统提示词配置文件: {e}")
            print("请确保配置文件存在且格式正确")
            self._yaml_config = None
            self._prompt_options = []

    def _parse_prompt_config(self) -> None:
        """解析YAML配置，生成提示词选项列表"""
        self._prompt_options = []
        
        # 检查是否存在 prompt_templates 节点
        prompt_templates = self._yaml_config.get('prompt_templates', {})
        
        if not prompt_templates:
            print("警告: 配置文件中未找到 'prompt_templates' 节点")
            return
        
        # 遍历所有提示词模板的配置
        for template_key, template_config in prompt_templates.items():
            # 跳过非字典类型的配置节点
            if not isinstance(template_config, dict):
                continue
            
            # 提取配置信息
            enabled = template_config.get('enabled', True)
            name = template_config.get('name', template_key)
            system_prompt = template_config.get('system_prompt', '')
            examples = template_config.get('examples', {})
            
            # 构建提示词选项
            prompt_option = {
                'key': template_key,
                'name': name,
                'enabled': enabled,
                'system_prompt': system_prompt,
                'examples': examples,
                'config': template_config
            }
            self._prompt_options.append(prompt_option)
        
        # print(f"已加载 {len(self._prompt_options)} 个系统提示词模板")

    def get_prompt_options_for_select(self, include_disabled: bool = False) -> List[str]:
        """
        获取用于ui.select的提示词选项列表
        
        Args:
            include_disabled: 是否包含禁用的提示词，默认为False
        
        Returns:
            List[str]: 提示词key列表
        """
        if include_disabled:
            return [option['key'] for option in self._prompt_options]
        else:
            return [option['key'] for option in self._prompt_options 
                   if option.get('enabled', True)]

    def get_prompt_config(self, prompt_key: str) -> Optional[Dict[str, Any]]:
        """
        根据提示词key获取完整配置信息
        
        Args:
            prompt_key: 提示词标识符
            
        Returns:
            Dict[str, Any]: 提示词配置信息，如果不存在则返回None
        """
        for option in self._prompt_options:
            if option['key'] == prompt_key:
                return option
        return None

    def get_system_prompt(self, prompt_key: str) -> Optional[str]:
        """
        获取系统提示词内容
        
        Args:
            prompt_key: 提示词标识符
            
        Returns:
            str: 系统提示词内容，如果不存在则返回None
        """
        config = self.get_prompt_config(prompt_key)
        return config.get('system_prompt') if config else None

    def get_examples(self, prompt_key: str) -> Optional[Dict[str, Any]]:
        """
        获取示例内容
        
        Args:
            prompt_key: 提示词标识符
            
        Returns:
            Dict: 示例内容，如果不存在则返回None
        """
        config = self.get_prompt_config(prompt_key)
        return config.get('examples') if config else None

    def get_default_prompt(self) -> Optional[str]:
        """
        获取默认提示词key
        
        Returns:
            str: 默认提示词key，如果没有启用的提示词则返回None
        """
        enabled_prompts = [opt for opt in self._prompt_options 
                         if opt.get('enabled', True)]
        return enabled_prompts[0]['key'] if enabled_prompts else None

    def reload_config(self) -> bool:
        """
        重新加载配置文件
        
        Returns:
            bool: 重新加载是否成功
        """
        try:
            old_prompt_count = len(self._prompt_options)
            
            # 重新加载配置
            self._yaml_config = None
            self._prompt_options = []
            self._load_config()
            
            new_prompt_count = len(self._prompt_options)
            
            print(f"配置重新加载完成: {old_prompt_count} -> {new_prompt_count} 个提示词模板")
            return True
            
        except Exception as e:
            print(f"配置重新加载失败: {e}")
            return False

    def get_config_info(self) -> Dict[str, Any]:
        """
        获取配置文件信息
        
        Returns:
            Dict: 配置文件信息
        """
        return {
            'config_file_path': str(self.config_file_path),
            'file_exists': self.config_file_path.exists(),
            'total_prompts': len(self._prompt_options),
            'enabled_prompts': len([opt for opt in self._prompt_options 
                                  if opt.get('enabled', True)]),
            'last_modified': self.config_file_path.stat().st_mtime if self.config_file_path.exists() else None
        }

# SystemPromptConfigManager 全局配置管理器实例
_prompt_config_manager = None

def get_system_prompt_manager() -> SystemPromptConfigManager:
    """
    获取全局系统提示词配置管理器实例（单例模式）
    
    Returns:
        SystemPromptConfigManager: 配置管理器实例
    """
    global _prompt_config_manager
    if _prompt_config_manager is None:
        _prompt_config_manager = SystemPromptConfigManager()
    return _prompt_config_manager

def get_prompt_options_for_select(include_disabled: bool = False) -> List[str]:
    """
    获取用于ui.select的提示词选项的便捷函数
    
    Args:
        include_disabled: 是否包含禁用的提示词，默认为False
    
    Returns:
        List[str]: 提示词key列表
    """
    return get_system_prompt_manager().get_prompt_options_for_select(include_disabled)

def get_prompt_config(prompt_key: str) -> Optional[Dict[str, Any]]:
    """
    根据提示词key获取配置的便捷函数
    
    Args:
        prompt_key: 提示词标识符
        
    Returns:
        Dict[str, Any]: 提示词配置信息
    """
    return get_system_prompt_manager().get_prompt_config(prompt_key)

def get_system_prompt(prompt_key: str) -> Optional[str]:
    """
    获取系统提示词内容的便捷函数
    
    Args:
        prompt_key: 提示词标识符
        
    Returns:
        str: 系统提示词内容
    """
    return get_system_prompt_manager().get_system_prompt(prompt_key)

def get_examples(prompt_key: str) -> Optional[Dict[str, Any]]:
    """
    获取示例内容的便捷函数
    
    Args:
        prompt_key: 提示词标识符
        
    Returns:
        Dict: 示例内容
    """
    return get_system_prompt_manager().get_examples(prompt_key)

def get_default_prompt() -> Optional[str]:
    """
    获取默认提示词key的便捷函数
    
    Returns:
        str: 默认提示词key
    """
    return get_system_prompt_manager().get_default_prompt()

def reload_prompt_config() -> bool:
    """
    重新加载系统提示词配置的便捷函数
    
    Returns:
        bool: 重新加载是否成功
    """
    return get_system_prompt_manager().reload_config()

def get_prompt_config_info() -> Dict[str, Any]:
    """
    获取配置信息的便捷函数
    
    Returns:
        Dict: 配置文件信息
    """
    return get_system_prompt_manager().get_config_info()
```

- **component\chat\markdown_ui_parser.py**
````python
import re
import asyncio
from typing import Optional, List, Dict, Any
from nicegui import ui
import io
import json
import csv

class MarkdownUIParser:
    """
    Markdown 内容解析器和 UI 组件映射器
    负责将 Markdown 内容解析为结构化块，并将其映射为相应的UI组件
    """
    
    def __init__(self):
        """初始化解析器"""
        pass
    
    # ==================== 主要接口方法 ====================
    async def optimize_content_display(self, reply_label, content: str, chat_content_container=None):
        """
        优化内容显示 - 将特殊内容转换为专业UI组件 
        Args:
            reply_label: 当前的markdown组件引用
            content: 完整的AI回复内容
            chat_content_container: 聊天内容容器引用
        """
        try:
            # 1. 解析内容，检测特殊块
            parsed_blocks = self.parse_content_with_regex(content)
            
            # 2. 判断是否需要优化
            if self.has_special_content(parsed_blocks):
                # 3. 显示优化提示
                self.show_optimization_hint(reply_label)
                
                # 4. 短暂延迟，让用户看到提示
                await asyncio.sleep(0.1)
                
                # 5. 获取正确的容器
                container = chat_content_container if chat_content_container else reply_label
                
                # 6. 重新渲染混合组件
                await self.render_optimized_content(container, parsed_blocks)
            
        except Exception as e:
            ui.notify(f"内容优化失败，保持原始显示: {e}")

    def parse_content_with_regex(self, content: str) -> List[Dict[str, Any]]:
        """
        使用正则表达式解析内容为结构化块
        
        Args:
            content: 需要解析的 Markdown 内容
            
        Returns:
            List[Dict]: 解析后的内容块列表
            [{
                'type': 'table|mermaid|code|heading|math|text',
                'content': '原始内容',
                'data': '解析后的数据'(可选),
                'start_pos': 开始位置,
                'end_pos': 结束位置
            }]
        """
        blocks = []
        
        # 1. 检测表格
        table_blocks = self.extract_tables(content)
        blocks.extend(table_blocks)
        
        # 2. 检测Mermaid图表
        mermaid_blocks = self.extract_mermaid(content)
        blocks.extend(mermaid_blocks)
        
        # 3. 检测代码块
        code_blocks = self.extract_code_blocks(content)
        blocks.extend(code_blocks)
        
        # 4. 检测LaTeX公式
        math_blocks = self.extract_math(content)
        blocks.extend(math_blocks)
        
        # 5. 检测标题
        heading_blocks = self.extract_headings(content)
        blocks.extend(heading_blocks)
        
        # 6. 按位置排序
        blocks.sort(key=lambda x: x['start_pos'])
        
        # 7. 填充文本块
        text_blocks = self.fill_text_blocks(content, blocks)
        
        # 8. 合并并重新排序
        all_blocks = blocks + text_blocks
        all_blocks.sort(key=lambda x: x['start_pos'])
        
        return all_blocks
    
    # ==================== 内容提取方法 ====================
    
    def extract_tables(self, content: str) -> List[Dict[str, Any]]:
        """提取表格内容"""
        tables = []
        # 匹配markdown表格模式
        pattern = r'(\|.*\|.*\n\|[-\s\|]*\|.*\n(?:\|.*\|.*\n)*)'
        
        for match in re.finditer(pattern, content):
            table_data = self.parse_table_data(match.group(1))
            if table_data:  # 确保解析成功
                tables.append({
                    'type': 'table',
                    'content': match.group(1),
                    'data': table_data,
                    'start_pos': match.start(),
                    'end_pos': match.end()
                })
        
        return tables

    def extract_mermaid(self, content: str) -> List[Dict[str, Any]]:
        """提取Mermaid图表"""
        mermaid_blocks = []
        pattern = r'```mermaid\n(.*?)```'
        
        for match in re.finditer(pattern, content, re.DOTALL):
            mermaid_blocks.append({
                'type': 'mermaid',
                'content': match.group(1).strip(),
                'start_pos': match.start(),
                'end_pos': match.end()
            })
    
        return mermaid_blocks

    def extract_code_blocks(self, content: str) -> List[Dict[str, Any]]:
        """提取代码块（排除mermaid）"""
        code_blocks = []
        pattern = r'```(\w+)?\n(.*?)```'
        
        for match in re.finditer(pattern, content, re.DOTALL):
            language = match.group(1) or 'text'
            if language.lower() != 'mermaid':  # 排除mermaid
                code_blocks.append({
                    'type': 'code',
                    'content': match.group(2).strip(),
                    'language': language,
                    'start_pos': match.start(),
                    'end_pos': match.end()
                })
        
        return code_blocks

    def extract_math(self, content: str) -> List[Dict[str, Any]]:
        """提取LaTeX数学公式"""
        math_blocks = []
        
        # 块级公式 $$...$$
        block_pattern = r'\$\$(.*?)\$\$'
        for match in re.finditer(block_pattern, content, re.DOTALL):
            math_blocks.append({
                'type': 'math',
                'content': match.group(1).strip(),
                'display_mode': 'block',
                'start_pos': match.start(),
                'end_pos': match.end()
            })
        
        # 行内公式 $...$
        inline_pattern = r'(?<!\$)\$([^\$\n]+)\$(?!\$)'
        for match in re.finditer(inline_pattern, content):
            math_blocks.append({
                'type': 'math',
                'content': match.group(1).strip(),
                'display_mode': 'inline',
                'start_pos': match.start(),
                'end_pos': match.end()
            })
        
        return math_blocks

    def extract_headings(self, content: str) -> List[Dict[str, Any]]:
        """提取标题"""
        headings = []
        pattern = r'^(#{1,6})\s+(.+)$'
        
        for match in re.finditer(pattern, content, re.MULTILINE):
            level = len(match.group(1))
            text = match.group(2).strip()
            headings.append({
                'type': 'heading',
                'content': text,
                'level': level,
                'start_pos': match.start(),
                'end_pos': match.end()
            })
        
        return headings

    def fill_text_blocks(self, content: str, special_blocks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """填充普通文本块"""
        if not special_blocks:
            return [{
                'type': 'text',
                'content': content,
                'start_pos': 0,
                'end_pos': len(content)
            }]
        
        text_blocks = []
        last_end = 0
        
        for block in special_blocks:
            if block['start_pos'] > last_end:
                text_content = content[last_end:block['start_pos']].strip()
                if text_content:
                    text_blocks.append({
                        'type': 'text',
                        'content': text_content,
                        'start_pos': last_end,
                        'end_pos': block['start_pos']
                    })
            last_end = block['end_pos']
        
        # 添加最后的文本内容
        if last_end < len(content):
            text_content = content[last_end:].strip()
            if text_content:
                text_blocks.append({
                    'type': 'text',
                    'content': text_content,
                    'start_pos': last_end,
                    'end_pos': len(content)
                })
        
        return text_blocks
    
    # ==================== 数据解析方法 ====================
    
    def parse_table_data(self, table_text: str) -> Optional[Dict[str, Any]]:
        """解析表格数据为NiceGUI table格式"""
        try:
            lines = [line.strip() for line in table_text.strip().split('\n') if line.strip()]
            if len(lines) < 3:  # 至少需要header、separator、data
                return None
            
            # 解析表头
            headers = [cell.strip() for cell in lines[0].split('|')[1:-1]]
            if not headers:
                return None
            
            # 解析数据行（跳过分隔行）
            rows = []
            for line in lines[2:]:
                cells = [cell.strip() for cell in line.split('|')[1:-1]]
                if len(cells) == len(headers):
                    row_data = dict(zip(headers, cells))
                    rows.append(row_data)
            
            return {
                'columns': [{'name': col, 'label': col, 'field': col} for col in headers],
                'rows': rows
            }
        
        except Exception as e:
            ui.notify(f"表格解析失败: {e}")
            return None
    
    # ==================== 检测和渲染方法 ====================
    
    def has_special_content(self, blocks: List[Dict[str, Any]]) -> bool:
        """检查是否包含需要优化的特殊内容"""
        special_types = {'table', 'mermaid', 'code', 'math', 'heading'}
        return any(block['type'] in special_types for block in blocks)

    def show_optimization_hint(self, reply_label):
        """显示优化提示"""
        try:
            reply_label.set_content("🔄 正在优化内容显示...")
        except:
            pass  # 如果设置失败，忽略错误

    async def render_optimized_content(self, container, blocks: List[Dict[str, Any]]):
        """渲染优化后的混合内容"""
        container.clear()
        
        with container:
            for block in blocks:
                try:
                    if block['type'] == 'table':
                        self.create_table_component(block['data'])
                    elif block['type'] == 'mermaid':
                        self.create_mermaid_component(block['content'])
                    elif block['type'] == 'code':
                        self.create_code_component(block['content'], block['language'])
                    elif block['type'] == 'math':
                        self.create_math_component(block['content'], block['display_mode'])
                    elif block['type'] == 'heading':
                        self.create_heading_component(block['content'], block['level'])
                    elif block['type'] == 'text':
                        self.create_text_component(block['content'])
                    else:
                        # 兜底：用markdown显示
                        ui.markdown(block['content']).classes('w-full')
                except Exception as e:
                    # 错误兜底：显示为代码块
                    ui.markdown(f"```\n{block['content']}\n```").classes('w-full')
    
    # ==================== UI组件创建方法 ====================
    
    def create_table_component(self, table_data: Dict[str, Any]):
        """创建表格组件"""
        if table_data and 'columns' in table_data and 'rows' in table_data:
            
            # 创建容器来包含表格和下载按钮
            with ui.card().classes('w-full relative bg-[#81c784]'):
                # 下载按钮 - 绝对定位在右上角
                with ui.row().classes('absolute top-2 right-2 z-10'):
                    ui.button(
                        # '下载', 
                        icon='download',
                        on_click=lambda: self.download_table_data(table_data)
                    ).classes('bg-blue-500 hover:bg-blue-600 text-white').props('flat round size=sm').tooltip('下载')     
                    # 表格组件
                ui.table(
                    columns=table_data['columns'],
                    rows=table_data['rows'],
                    column_defaults={
                        'align': 'left',
                        'headerClasses': 'uppercase text-primary',
                    },
                    pagination=5
                ).classes('w-full bg-[#81c784] text-gray-800')

    def download_table_data(self,table_data: Dict[str, Any]):
        """下载表格数据为CSV文件"""
        if not table_data or 'columns' not in table_data or 'rows' not in table_data:
            ui.notify('没有可下载的数据', type='warning')
            return
        try:
            # 创建CSV内容
            output = io.StringIO()
            writer = csv.writer(output)
            
            # 写入表头
            headers = [col['label'] if isinstance(col, dict) else col for col in table_data['columns']]
            writer.writerow(headers)
            
            # 写入数据行
            for row in table_data['rows']:
                if isinstance(row, dict):
                    # 如果行是字典，按列的顺序提取值
                    row_values = []
                    for col in table_data['columns']:
                        col_name = col['name'] if isinstance(col, dict) else col
                        row_values.append(row.get(col_name, ''))
                    writer.writerow(row_values)
                else:
                    # 如果行是列表，直接写入
                    writer.writerow(row)
            # 获取CSV内容
            csv_content = output.getvalue()
            output.close()
            
            # 触发下载
            ui.download(csv_content.encode('utf-8-sig'), 'table_data.csv')
            ui.notify('文件下载成功', type='positive')
        except Exception as e:
            ui.notify(f'下载失败: {str(e)}', type='negative')

    def create_mermaid_component(self, mermaid_content: str):
        """创建Mermaid图表组件"""
        try:
            # 创建容器，使用相对定位
            with ui.row().classes('w-full relative bg-[#81c784]'):
                # 右上角全屏按钮
                with ui.row().classes('absolute top-2 right-2 z-10'):
                    ui.button(
                        icon='fullscreen', 
                        on_click=lambda: self.show_fullscreen_mermaid_enhanced(mermaid_content)
                    ).props('flat round size=sm').classes('bg-blue-500 hover:bg-blue-600 text-white').tooltip('全屏显示') 
                # Mermaid图表
                ui.mermaid(mermaid_content).classes('w-full')     
        except Exception as e:
            ui.notify(f"流程图渲染失败: {e}", type="info")
            # 错误情况下也保持相同的布局结构
            ui.code(mermaid_content, language='mermaid').classes('w-full')

    def show_fullscreen_mermaid_enhanced(self, mermaid_content: str):
        """增强版全屏显示Mermaid图表"""
        
        mermaid_id = 'neo_container'
        
        def close_dialog():
            dialog.close()

        def export_image():
            """导出Mermaid图表为PNG图片"""
            try:
                # JavaScript代码：使用多种方法导出SVG
                js_code = f"""
                async function exportMermaidImage() {{
                    try {{
                        // 查找mermaid容器
                        const mermaidContainer = document.getElementById('{mermaid_id}');
                        if (!mermaidContainer) {{
                            console.error('未找到Mermaid容器');
                            return false;
                        }}
                        
                        // 查找SVG元素
                        const svgElement = mermaidContainer.querySelector('svg');
                        if (!svgElement) {{
                            console.error('未找到SVG元素');
                            return false;
                        }}
                        
                        // 克隆SVG元素以避免修改原始元素
                        const clonedSvg = svgElement.cloneNode(true);
                        
                        // 获取SVG的实际尺寸
                        const bbox = svgElement.getBBox();
                        const width = Math.max(bbox.width, svgElement.clientWidth, 400);
                        const height = Math.max(bbox.height, svgElement.clientHeight, 300);
                        
                        // 设置克隆SVG的属性
                        clonedSvg.setAttribute('width', width);
                        clonedSvg.setAttribute('height', height);
                        clonedSvg.setAttribute('viewBox', `0 0 ${{width}} ${{height}}`);
                        clonedSvg.setAttribute('xmlns', 'http://www.w3.org/2000/svg');
                        clonedSvg.setAttribute('xmlns:xlink', 'http://www.w3.org/1999/xlink');
                        
                        // 内联样式到SVG中
                        const styleSheets = Array.from(document.styleSheets);
                        let allStyles = '';
                        
                        try {{
                            for (let sheet of styleSheets) {{
                                try {{
                                    const rules = Array.from(sheet.cssRules || sheet.rules || []);
                                    for (let rule of rules) {{
                                        if (rule.type === CSSRule.STYLE_RULE) {{
                                            allStyles += rule.cssText + '\\n';
                                        }}
                                    }}
                                }} catch (e) {{
                                    // 跳过跨域样式表
                                    console.warn('跳过样式表:', e);
                                }}
                            }}
                            
                            if (allStyles) {{
                                const styleElement = document.createElement('style');
                                styleElement.textContent = allStyles;
                                clonedSvg.insertBefore(styleElement, clonedSvg.firstChild);
                            }}
                        }} catch (e) {{
                            console.warn('样式处理失败:', e);
                        }}
                        
                        // 序列化SVG
                        const serializer = new XMLSerializer();
                        let svgString = serializer.serializeToString(clonedSvg);
                        
                        // 方法1：尝试使用html2canvas式的方法
                        try {{
                            return await exportViaCanvas(svgString, width, height);
                        }} catch (canvasError) {{
                            console.warn('Canvas方法失败，尝试直接下载SVG:', canvasError);
                            // 方法2：直接下载SVG文件
                            return exportAsSVG(svgString);
                        }}
                        
                    }} catch (error) {{
                        console.error('导出图片错误:', error);
                        return false;
                    }}
                }}
                
                async function exportViaCanvas(svgString, width, height) {{
                    return new Promise((resolve, reject) => {{
                        // 创建canvas
                        const canvas = document.createElement('canvas');
                        const ctx = canvas.getContext('2d');
                        const scale = 2; // 高分辨率
                        
                        canvas.width = width * scale;
                        canvas.height = height * scale;
                        ctx.scale(scale, scale);
                        
                        // 白色背景
                        ctx.fillStyle = 'white';
                        ctx.fillRect(0, 0, width, height);
                        
                        // 创建Data URL
                        const svgBlob = new Blob([svgString], {{ type: 'image/svg+xml;charset=utf-8' }});
                        const url = URL.createObjectURL(svgBlob);
                        
                        const img = new Image();
                        img.onload = function() {{
                            try {{
                                ctx.drawImage(img, 0, 0, width, height);
                                
                                // 使用getImageData方式避免toBlob的跨域问题
                                try {{
                                    const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
                                    const newCanvas = document.createElement('canvas');
                                    const newCtx = newCanvas.getContext('2d');
                                    newCanvas.width = canvas.width;
                                    newCanvas.height = canvas.height;
                                    newCtx.putImageData(imageData, 0, 0);
                                    
                                    newCanvas.toBlob(function(blob) {{
                                        if (blob) {{
                                            downloadBlob(blob, 'flowchart_' + new Date().getTime() + '.png');
                                            resolve(true);
                                        }} else {{
                                            reject('Blob转换失败');
                                        }}
                                    }}, 'image/png', 1.0);
                                }} catch (e) {{
                                    // 如果还是失败，使用toDataURL
                                    const dataUrl = canvas.toDataURL('image/png', 1.0);
                                    downloadDataUrl(dataUrl, 'flowchart_' + new Date().getTime() + '.png');
                                    resolve(true);
                                }}
                            }} catch (error) {{
                                reject('绘制失败: ' + error.message);
                            }} finally {{
                                URL.revokeObjectURL(url);
                            }}
                        }};
                        
                        img.onerror = function() {{
                            URL.revokeObjectURL(url);
                            reject('图像加载失败');
                        }};
                        
                        img.src = url;
                    }});
                }}
                
                function exportAsSVG(svgString) {{
                    try {{
                        const blob = new Blob([svgString], {{ type: 'image/svg+xml;charset=utf-8' }});
                        downloadBlob(blob, 'flowchart_' + new Date().getTime() + '.svg');
                        return true;
                    }} catch (error) {{
                        console.error('SVG导出失败:', error);
                        return false;
                    }}
                }}
                
                function downloadBlob(blob, filename) {{
                    const url = URL.createObjectURL(blob);
                    const link = document.createElement('a');
                    link.href = url;
                    link.download = filename;
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                    setTimeout(() => URL.revokeObjectURL(url), 100);
                }}
                
                function downloadDataUrl(dataUrl, filename) {{
                    const link = document.createElement('a');
                    link.href = dataUrl;
                    link.download = filename;
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                }}
                
                // 执行导出
                exportMermaidImage().then(result => {{
                    if (result) {{
                        console.log('图片导出成功');
                    }} else {{
                        console.error('图片导出失败');
                    }}
                }}).catch(error => {{
                    console.error('导出过程中出错:', error);
                }});
                """
                
                # 执行JavaScript代码
                ui.run_javascript(js_code)
                
                # 给用户反馈
                ui.notify('正在导出图片...', type='info')
                
            except Exception as e:
                ui.notify(f'导出失败: {str(e)}', type='negative')
                print(f"Export error: {e}")
        
        # 创建全屏对话框
        with ui.dialog().props('maximized transition-show="slide-up" transition-hide="slide-down"') as dialog:
            with ui.card().classes('w-full no-shadow bg-white'):
                # 顶部工具栏
                with ui.row().classes('w-full justify-between items-center p-1 bg-gradient-to-r from-blue-500 to-purple-600 text-white'):
                    with ui.row().classes('items-center gap-3'):
                        ui.icon('account_tree', size='md')
                        ui.label('流程图全屏显示').classes('text-xl font-bold')
                    
                    with ui.row().classes('gap-1'):
                        ui.button(
                            icon='download',
                            on_click=export_image
                        ).props('flat round').classes('text-white hover:bg-white/20').tooltip('导出图片')
                        
                        ui.button(
                            icon='close',
                            on_click=close_dialog
                        ).props('flat round').classes('text-white hover:bg-white/20').tooltip('退出全屏')
                
                # 图表容器
                with ui.scroll_area().classes('flex-1 p-6 bg-gray-50'):
                    try:
                        # 重点：为ui.mermaid组件添加一个ID
                        ui.mermaid(mermaid_content).classes('w-full min-h-96 bg-white rounded-lg shadow-sm p-4').props(f'id="{mermaid_id}"')
                    except Exception as e:
                        ui.notify(f"全屏图表渲染失败: {e}", type="warning")
                        with ui.card().classes('w-full bg-white'):
                            ui.label('图表渲染失败，显示源代码:').classes('font-semibold mb-2 text-red-600')
                            ui.code(mermaid_content, language='mermaid').classes('w-full')
        
        # 添加键盘事件监听（ESC键关闭）
        dialog.on('keydown.esc', close_dialog)
        # 打开对话框
        dialog.open()

    def create_code_component(self, code_content: str, language: str):
        """创建代码组件"""
        ui.code(code_content, language=language).classes('w-full bg-gray-200 dark:bg-zinc-600')

    def create_math_component(self, math_content: str, display_mode: str):
        """创建数学公式组件"""
        if display_mode == 'block':
            ui.markdown(f'$$\n{math_content}\n$$',extras=['latex']).classes('w-full text-center')
        else:
            ui.markdown(f'${math_content}$',extras=['latex']).classes('w-full')

    def create_heading_component(self, text: str, level: int):
        """创建标题组件"""
        # 标题级别映射：向下调整2级
        # # -> ###, ## -> ####, ### -> #####, #### -> ######
        adjusted_level = level + 2
        
        # 限制最大级别为6（markdown支持的最大级别）
        if adjusted_level > 6:
            adjusted_level = 6
        
        # 生成对应级别的markdown标题
        markdown_heading = '#' * adjusted_level + ' ' + text
        
        # 使用ui.markdown渲染，这样可以保持**加粗**等markdown格式
        ui.markdown(markdown_heading).classes('w-full')

    def create_text_component(self, text_content: str):
        """创建文本组件"""
        if text_content.strip():
            ui.markdown(text_content, extras=['tables', 'mermaid', 'latex', 'fenced-code-blocks']).classes('w-full')
    
    # ==================== 便捷方法 ====================
    
    def get_supported_content_types(self) -> List[str]:
        """获取支持的内容类型列表"""
        return ['table', 'mermaid', 'code', 'math', 'heading', 'text']
    
    def is_content_optimizable(self, content: str) -> bool:
        """快速检查内容是否可优化"""
        blocks = self.parse_content_with_regex(content)
        return self.has_special_content(blocks)
````
