from nicegui import ui, app
from typing import List, Dict, Callable, Optional
from .layout_config import LayoutConfig, MenuItem, HeaderConfigItem

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
            # 注意：不包含 'logout'，因为注销是一次性操作，不应该被恢复
            
            # 其他系统路由
            'no_permission': '权限不足',
            'login': '登录',
            'register': '注册'
        }
        
        for route, label in system_routes.items():
            self.all_routes[route] = label
            
        print(f"🔧 已注册系统路由: {list(system_routes.keys())}")
        print(f"⚠️  注意：logout 路由未注册到持久化路由中（一次性操作）")

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
        
        print(f"🧭 导航到路由: {route} ({label})")
        self.current_route = route
        
        # 如果不是菜单路由，清除菜单选中状态
        is_menu_route = any(item.route == route for item in self.menu_items)
        if not is_menu_route:
            self.clear_menu_selection()
        
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
                    print("🔄 没有保存的路由，且未定义菜单项，保持空白状态")
                return
            
            print(f"🔄 恢复保存的路由: {saved_route}")
            print(f"📋 可用路由映射: {list(self.all_routes.keys())}")
            
            # 检查路由是否在已知路由中
            if saved_route in self.all_routes:
                route_label = self.all_routes[saved_route]
                print(f"✅ 找到路由映射: {saved_route} -> {route_label}")
                
                # 检查是否是菜单项路由
                menu_item = next((item for item in self.menu_items if item.route == saved_route), None)
                if menu_item:
                    print(f"✅ 这是菜单路由，恢复菜单选中状态")
                    # 恢复菜单选中状态
                    self.select_menu_item(menu_item.key, update_storage=False)
                else:
                    print(f"✅ 这是非菜单路由，直接导航")
                    # 直接导航到路由（不更新存储避免循环）
                    self.navigate_to_route(saved_route, route_label, update_storage=False)
                return
            
            # 兜底检查：是否在路由处理器中注册
            if saved_route in self.route_handlers:
                print(f"✅ 在路由处理器中找到路由: {saved_route}")
                label = saved_route.replace('_', ' ').title()
                self.navigate_to_route(saved_route, label, update_storage=False)
                return
            
            # 如果都没找到，且有菜单项，选择第一个菜单项
            print(f"⚠️ 未找到保存的路由 {saved_route}，使用默认路由")
            if self.menu_items:
                first_item = self.menu_items[0]
                self.select_menu_item(first_item.key, update_storage=True)
            else:
                print("⚠️ 没有可用的菜单项，保持空白状态")
                
        except Exception as e:
            print(f"⚠️ 恢复路由状态失败: {e}")
            if self.menu_items:
                first_item = self.menu_items[0]
                self.select_menu_item(first_item.key, update_storage=True)
            else:
                print("⚠️ 没有可用的菜单项，保持空白状态")

    def handle_header_config_item_click(self, item: HeaderConfigItem):
        """处理头部配置项点击事件"""
        print(f"🖱️ 点击头部配置项: {item.label or item.key}")
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
        """创建头部"""
        with ui.header(elevated=True).classes(f'items-center justify-between px-4 {self.config.header_bg}'):
            with ui.row().classes('items-center gap-4'):
                ui.button(
                    on_click=lambda: self.left_drawer.toggle(),
                    icon='menu'
                ).props('flat color=white').classes('mr-2')

                with ui.avatar():
                    ui.image(self.config.app_icon).classes('w-15 h-15')
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
                    ui.separator().props('vertical').classes('h-10')

                # 主题切换
                self.dark_mode = ui.dark_mode()
                ui.switch('主题切换').bind_value(self.dark_mode)

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
                            ui.label(menu_item.label).classes('text-gray-800 dark:text-gray-200 font-medium flex-1 text-lg font-bold')

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
        with ui.column().classes('flex-1 p-6') as content_container:
            self.content_container = content_container