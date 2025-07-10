from nicegui import ui
from typing import List, Dict, Callable, Optional
from .layout_config import LayoutConfig, MenuItem, HeaderConfigItem

class LayoutManager:
    """布局管理器"""
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

    def add_menu_item(self, key: str, label: str, icon: str, route: Optional[str] = None, separator_after: bool = False):
        """添加菜单项"""
        self.menu_items.append(MenuItem(key, label, icon, route, separator_after))

    def add_header_config_item(self, key: str, label: Optional[str] = None, icon: Optional[str] = None, route: Optional[str] = None, on_click: Optional[Callable] = None):
        """添加头部配置项"""
        self.header_config_items.append(HeaderConfigItem(key, label, icon, route, on_click))

    def set_route_handler(self, route: str, handler: Callable):
        """设置路由处理器"""
        self.route_handlers[route] = handler

    def select_menu_item(self, key: str, row_element):
        """选择菜单项"""
        if self.selected_menu_item_row['key'] == key:
            return

        if self.selected_menu_item_row['element'] is not None:
            self.selected_menu_item_row['element'].classes(remove='bg-blue-200 dark:bg-blue-700')

        row_element.classes(add='bg-blue-200 dark:bg-blue-700')
        self.selected_menu_item_row['element'] = row_element
        self.selected_menu_item_row['key'] = key

        menu_item = next((item for item in self.menu_items if item.key == key), None)
        if not menu_item:
            return

        ui.notify(f'切换到{menu_item.label}')

        if menu_item.route:
            self.navigate_to_route(menu_item.route, menu_item.label)
        else:
            if self.content_container:
                self.content_container.clear()
                with self.content_container:
                    ui.label(f'{menu_item.label}内容').classes('text-2xl font-bold text-gray-800 dark:text-gray-200')

    def handle_header_config_item_click(self, item: HeaderConfigItem):
        """处理新增的头部配置项点击事件"""
        ui.notify(f'点击了头部配置项: {item.label or item.key}')
        if item.on_click:
            item.on_click()
        if item.route:
            self.navigate_to_route(item.route, item.label or item.key)

    def handle_settings_click(self):
        """设置按钮的点击处理函数"""
        ui.notify('点击了设置')
        self.navigate_to_route('settings_page', '设置')

    def handle_user_profile_click(self):
        """用户中心按钮的点击处理函数"""
        ui.notify('点击了用户中心')
        self.navigate_to_route('user_profile_page', '用户中心')

    def navigate_to_route(self, route: str, label: str):
        """导航到指定路由"""
        if self.current_route == route:
            return
        self.current_route = route
        if self.content_container:
            self.content_container.clear()

        if route in self.route_handlers:
            with self.content_container:
                self.route_handlers[route]()
        else:
            with self.content_container:
                ui.label(f'{label}内容').classes('text-2xl font-bold text-gray-800 dark:text-gray-200')
                ui.label(f'这是{label}页面的内容区域').classes('text-gray-600 dark:text-gray-400 mt-4')

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
                
                # 主题设置、设置和用户中心按钮
                self.dark_mode = ui.dark_mode()
                ui.switch('主题切换').bind_value(self.dark_mode)
                ui.button(
                    icon='settings',
                    on_click=self.handle_settings_click
                ).props('flat color=white round').classes('w-10 h-10')
                ui.button(
                    icon='account_circle',
                    on_click=self.handle_user_profile_click
                ).props('flat color=white round').classes('w-10 h-10')

    def create_left_drawer(self):
        """创建左侧抽屉"""
        with ui.left_drawer(fixed=False).props('bordered').classes(f'{self.config.drawer_width} {self.config.drawer_bg}') as left_drawer:
            self.left_drawer = left_drawer

            ui.label(self.config.menu_title).classes('w-full text-lg font-semibold text-gray-800 dark:text-gray-200 p-4 border-b border-gray-200 dark:border-gray-700')

            with ui.column().classes('w-full p-2 gap-1'):
                menu_rows = {}

                for menu_item in self.menu_items:
                    with ui.row().classes('w-full cursor-pointer rounded-lg hover:bg-blue-100 dark:hover:bg-blue-800 transition-colors duration-200 p-3') as menu_row:
                        ui.icon(menu_item.icon).classes('text-blue-600 mr-3 text-lg font-bold')
                        ui.label(menu_item.label).classes('text-gray-800 dark:text-gray-200 font-medium flex-1 text-lg font-bold')

                        menu_row.on('click', lambda key=menu_item.key, row=menu_row: self.select_menu_item(key, row))
                        menu_rows[menu_item.key] = menu_row

                    if menu_item.separator_after:
                        ui.separator().classes('dark:bg-gray-700')

                if self.menu_items:
                    first_item = self.menu_items[0]
                    ui.timer(0.1, lambda: self.select_menu_item(first_item.key, menu_rows[first_item.key]), once=True)

    def create_content_area(self):
        """创建内容区域"""
        with ui.column().classes('flex-1 p-6') as content_container:
            self.content_container = content_container
            ui.label('欢迎使用MCP集成服务平台').classes('text-3xl font-bold text-gray-800 dark:text-gray-200')
            ui.label('请从左侧菜单选择功能').classes('text-gray-600 dark:text-gray-400 mt-4 text-lg')