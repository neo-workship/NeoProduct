"""
多层布局管理器
实现多层级折叠菜单的UI渲染和交互逻辑
✨ 优化版本: 改善了菜单项间距,使其更加美观舒适
"""
from nicegui import ui, app
from typing import List, Dict, Callable, Optional, Set
from .layout_config import LayoutConfig, HeaderConfigItem
from .multilayer_menu_config import MultilayerMenuItem, MultilayerMenuConfig

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
        self.expanded_keys: Set[str] = set()  # 当前展开的父节点keys
        self.selected_leaf_key: Optional[str] = None  # 当前选中的叶子节点key
        
        # UI元素引用映射
        self.expansion_refs: Dict[str, any] = {}  # key -> ui.expansion对象
        self.leaf_refs: Dict[str, any] = {}  # key -> 叶子节点ui.row对象
        
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
            with ui.column().classes('w-full p-3 gap-3 multilayer-menu-content'):
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
        print(f"🚀 导航到路由: {route} ({label})")
        
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
            print(f"⚠️ 节点 {key} 不是有效的叶子节点")
            return
        
        print(f"🎯 选中叶子节点: {item.label} (key={key})")
        
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
        
        print(f"📂 展开父节点: {key}")
    
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
        
        print(f"📁 收起父节点: {key}")
    
    def _save_expanded_state(self):
        """保存展开状态到存储"""
        app.storage.user[self._expanded_keys_key] = list(self.expanded_keys)
    
    def _load_expanded_state(self):
        """从存储加载展开状态"""
        stored_keys = app.storage.user.get(self._expanded_keys_key, [])
        self.expanded_keys = set(stored_keys)
        print(f"📚 加载展开状态: {self.expanded_keys}")
    
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
            self.clear_route_storage()
            ui.navigate.to('/login')
        else:
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
            print(f"🔄 恢复路由: {stored_route} ({stored_label})")
            
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
            'user_management': '用户管理',
            'role_management': '角色管理',
            'permission_management': '权限管理',
            'llm_config_management': '大模型配置',
            'prompt_config_management': '提示词配置',
            'user_profile': '个人资料',
            'change_password': '修改密码'
        }
        
        for route, label in system_routes.items():
            if route not in self.all_routes:
                self.all_routes[route] = label
    
    def initialize_layout(self):
        """初始化布局"""
        def init_routes():
            self.register_system_routes()
            self.restore_route_from_storage()
        
        ui.timer(0.3, init_routes, once=True)