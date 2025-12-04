from nicegui import ui, app
from typing import List, Dict, Callable, Optional
from .layout_config import LayoutConfig, MenuItem, HeaderConfigItem

class SimpleLayoutManager:
    """简单布局管理器 - 只包含顶部导航栏的布局"""
    
    def __init__(self, config: LayoutConfig):
        self.config = config
        self.nav_items: List[MenuItem] = []  # 顶部导航项（原菜单项）
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
        print(f"🔗 注册路由处理器: {route}")
        
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
            
        print(f"🔧 已注册系统路由: {list(system_routes.keys())}")
        print(f"⚠️  注意：logout 路由未注册到持久化路由中（一次性操作）")

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
        
        print(f"🧭 导航到路由: {route} ({label})")
        self.current_route = route
        
        # 如果不是导航路由，清除导航选中状态
        is_nav_route = any(item.route == route for item in self.nav_items)
        if not is_nav_route:
            self.clear_nav_selection()
        
        # 保存当前路由到存储（排除一次性操作路由）
        if update_storage and self._should_persist_route(route):
            try:
                app.storage.user['current_route'] = route
                print(f"💾 保存路由状态: {route}")
            except Exception as e:
                print(f"⚠️ 保存路由状态失败: {e}")
        elif not self._should_persist_route(route):
            print(f"🚫 跳过路由持久化: {route} (一次性操作)")
        
        if self.content_container:
            self.content_container.clear()

        if route in self.route_handlers:
            print(f"✅ 执行路由处理器: {route}")
            with self.content_container:
                try:
                    self.route_handlers[route]()
                except Exception as e:
                    print(f"❌ 路由处理器执行失败 {route}: {e}")
                    ui.label(f'页面加载失败: {str(e)}').classes('text-red-500 text-xl')
        else:
            print(f"❌ 未找到路由处理器: {route}")
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
                print("🗑️ 已清除路由存储")
        except Exception as e:
            print(f"⚠️ 清除路由存储失败: {e}")

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
                    print("🔄 没有保存的路由，且未定义导航项，保持空白状态")
                return
            
            print(f"🔄 恢复保存的路由: {saved_route}")
            # print(f"📋 可用路由映射: {list(self.all_routes.keys())}")
            
            # 检查路由是否在已知路由中
            if saved_route in self.all_routes:
                route_label = self.all_routes[saved_route]
                print(f"✅ 找到路由映射: {saved_route} -> {route_label}")
                
                # 检查是否是导航项路由
                nav_item = next((item for item in self.nav_items if item.route == saved_route), None)
                if nav_item:
                    print(f"✅ 这是导航路由，恢复导航选中状态")
                    # 恢复导航选中状态
                    self.select_nav_item(nav_item.key, update_storage=False)
                else:
                    print(f"✅ 这是非导航路由，直接导航")
                    # 直接导航到路由（不更新存储避免循环）
                    self.navigate_to_route(saved_route, route_label, update_storage=False)
                return
            
            # 兜底检查：是否在路由处理器中注册
            if saved_route in self.route_handlers:
                print(f"✅ 在路由处理器中找到路由: {saved_route}")
                label = saved_route.replace('_', ' ').title()
                self.navigate_to_route(saved_route, label, update_storage=False)
                return
            
            # 如果都没找到，且有导航项，选择第一个导航项
            print(f"⚠️ 未找到保存的路由 {saved_route}，使用默认路由")
            if self.nav_items:
                first_item = self.nav_items[0]
                self.select_nav_item(first_item.key, update_storage=True)
            else:
                print("⚠️ 没有可用的导航项，保持空白状态")
                
        except Exception as e:
            print(f"⚠️ 恢复路由状态失败: {e}")
            if self.nav_items:
                first_item = self.nav_items[0]
                self.select_nav_item(first_item.key, update_storage=True)
            else:
                print("⚠️ 没有可用的导航项，保持空白状态")

    def handle_header_config_item_click(self, item: HeaderConfigItem):
        """处理头部配置项点击事件"""
        ui.notify(f'点击了头部配置项: {item.label or item.key}')
        
        if item.on_click:
            item.on_click()
        
        if item.route:
            self.navigate_to_route(item.route, item.label or item.key)

    def handle_settings_menu_item_click(self, route: str, label: str):
        """处理设置菜单项点击事件"""
        print(f"⚙️ 点击设置菜单项: {label} -> {route}")
        
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
        print(f"👤 点击用户菜单项: {label} -> {route}")
        ui.notify(f'点击了用户菜单项: {label}')
        
        # 特殊处理注销：清除路由存储
        if route == 'logout':
            print("🚪 执行用户注销，清除路由存储")
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
                # 分隔符 (可以放在主导航项之前，如果需要的话)
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
                
                if self.header_config_items:
                    ui.separator().props('vertical').classes('h-8')

                # 主题切换
                # self.dark_mode = ui.dark_mode()
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