"""
多层布局管理器
实现多层级折叠菜单的UI渲染和交互逻辑
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
        self.header_config_items.append(HeaderConfigItem(key, label, icon, route, on_click))
        if route:
            self.all_routes[route] = label or key
    
    def set_route_handler(self, route: str, handler: Callable):
        """设置路由处理器"""
        self.route_handlers[route] = handler
        print(f"🔗 注册路由处理器: {route}")
        
        if route not in self.all_routes:
            self.all_routes[route] = route.replace('_', ' ').title()
    
    def register_system_routes(self):
        """注册系统路由"""
        system_routes = {
            'user_management': '用户管理',
            'role_management': '角色管理',
            'permission_management': '权限管理',
            'llm_config_management': '大模型配置',
            'prompt_config_management': '提示词配置',
            'user_profile': '个人资料',
            'change_password': '修改密码',
            'no_permission': '权限不足',
            'login': '登录',
            'register': '注册'
        }
        
        for route, label in system_routes.items():
            self.all_routes[route] = label
        
        print(f"🔧 已注册系统路由: {list(system_routes.keys())}")
    
    def navigate_to_route(self, route: str, label: str, update_storage: bool = True):
        """导航到指定路由"""
        print(f"🧭 导航到路由: {route} ({label})")
        
        self.current_route = route
        self.current_label = label
        
        # 保存到存储
        if update_storage:
            app.storage.user[self._route_key] = route
            app.storage.user[self._label_key] = label
            print(f"💾 已保存路由状态: {route}")
        
        # 清空内容容器
        if self.content_container:
            self.content_container.clear()
        
        # 调用路由处理器
        if route in self.route_handlers:
            with self.content_container:
                # 添加面包屑导航
                self._render_breadcrumb(route)
                
                # 渲染页面内容
                try:
                    self.route_handlers[route]()
                except Exception as e:
                    print(f"❌ 路由处理器执行错误: {e}")
                    ui.label(f'加载页面失败: {str(e)}').classes('text-red-500')
        else:
            print(f"⚠️ 未找到路由处理器: {route}")
            with self.content_container:
                ui.label(f'页面未实现: {label}').classes('text-xl font-bold text-gray-500')
    
    def _render_breadcrumb(self, route: str):
        """渲染面包屑导航"""
        item = self.menu_config.find_by_route(route)
        if not item:
            return
        
        # 构建面包屑路径
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
        print(f"💾 已保存展开状态: {self.expanded_keys}")
    
    def _restore_expanded_state(self):
        """从存储恢复展开状态"""
        saved_keys = app.storage.user.get(self._expanded_keys_key, [])
        for key in saved_keys:
            self.expand_parent(key, update_storage=False)
        print(f"📖 已恢复展开状态: {saved_keys}")
    
    def restore_route_from_storage(self):
        """从存储恢复路由状态"""
        try:
            saved_route = app.storage.user.get(self._route_key)
            saved_label = app.storage.user.get(self._label_key)
            
            print(f"📖 尝试恢复路由: {saved_route} ({saved_label})")
            
            if saved_route:
                # 查找对应的菜单项
                item = self.menu_config.find_by_route(saved_route)
                if item and item.is_leaf:
                    print(f"✅ 在菜单中找到路由: {saved_route}")
                    # 先恢复展开状态
                    self._restore_expanded_state()
                    # 再选中叶子节点(不更新存储避免循环)
                    self.select_leaf_item(item.key, update_storage=False)
                    return
                
                # 检查是否在路由处理器中注册
                if saved_route in self.route_handlers:
                    print(f"✅ 在路由处理器中找到路由: {saved_route}")
                    route_label = saved_label or self.all_routes.get(saved_route, saved_route)
                    self.navigate_to_route(saved_route, route_label, update_storage=False)
                    return
            
            # 未找到保存的路由,使用第一个叶子节点
            print(f"⚠️ 未找到保存的路由,使用默认路由")
            first_leaf = self._find_first_leaf()
            if first_leaf:
                self.select_leaf_item(first_leaf.key, update_storage=True)
            else:
                print("⚠️ 没有可用的菜单项,保持空白状态")
        
        except Exception as e:
            print(f"⚠️ 恢复路由状态失败: {e}")
            first_leaf = self._find_first_leaf()
            if first_leaf:
                self.select_leaf_item(first_leaf.key, update_storage=True)
    
    def _find_first_leaf(self) -> Optional[MultilayerMenuItem]:
        """查找第一个叶子节点"""
        for item in self.menu_config.menu_items:
            leaf = self._find_first_leaf_recursive(item)
            if leaf:
                return leaf
        return None
    
    def _find_first_leaf_recursive(self, item: MultilayerMenuItem) -> Optional[MultilayerMenuItem]:
        """递归查找第一个叶子节点"""
        if item.is_leaf:
            return item
        
        for child in item.children:
            leaf = self._find_first_leaf_recursive(child)
            if leaf:
                return leaf
        
        return None
    
    def clear_route_storage(self):
        """清除路由存储(用于注销时)"""
        if self._route_key in app.storage.user:
            del app.storage.user[self._route_key]
        if self._label_key in app.storage.user:
            del app.storage.user[self._label_key]
        if self._expanded_keys_key in app.storage.user:
            del app.storage.user[self._expanded_keys_key]
        print("🗑️ 已清除路由存储")
    
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
            ui.notify('您没有管理员权限,无法访问此功能', type='error')
            self.navigate_to_route('no_permission', '权限不足')
            return
        
        ui.notify(f'访问管理功能: {label}')
        self.navigate_to_route(route, label)
    
    def handle_user_menu_item_click(self, route: str, label: str):
        """处理用户菜单项点击事件"""
        print(f"👤 点击用户菜单项: {label} -> {route}")
        ui.notify(f'点击了用户菜单项: {label}')
        
        # 特殊处理注销:清除路由存储
        if route == 'logout':
            print("🚪 执行用户注销,清除路由存储")
            self.clear_route_storage()
        
        self.navigate_to_route(route, label)
    
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
                    ui.separator().props('vertical').classes('h-8')
                
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
        """创建左侧抽屉(多层菜单)"""
        with ui.left_drawer(fixed=False).props('bordered').classes(
            f'{self.config.drawer_width} {self.config.drawer_bg}'
        ) as left_drawer:
            self.left_drawer = left_drawer
            
            # 菜单标题
            ui.label(self.config.menu_title).classes(
                'w-full text-lg font-semibold text-gray-800 dark:text-gray-200 p-4 '
                'border-b border-gray-200 dark:border-gray-700'
            )
            
            # 菜单内容区域
            with ui.column().classes('w-full p-2 gap-1'):
                if self.menu_config.menu_items:
                    for item in self.menu_config.menu_items:
                        self._render_menu_item(item)
                        
                        if item.separator_after:
                            ui.separator().classes('dark:bg-gray-700 my-2')
                else:
                    # 无菜单项提示
                    with ui.column().classes('w-full items-center py-8'):
                        ui.icon('menu_open').classes('text-6xl text-gray-400 mb-4')
                        ui.label('暂无菜单项').classes('text-lg font-medium text-gray-500 dark:text-gray-400')
    
    def _render_menu_item(self, item: MultilayerMenuItem, level: int = 0):
        """递归渲染菜单项"""
        indent_class = f'ml-{level * 4}' if level > 0 else ''
        
        if item.is_parent:
            # 父节点:使用expansion
            with ui.expansion(
                text=item.label,
                icon=item.icon,
                value=item.expanded or (item.key in self.expanded_keys)
            ).classes(f'w-full {indent_class}').props('dense') as expansion:
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
            # 叶子节点:可点击的行
            with ui.row().classes(
                f'w-full cursor-pointer rounded-lg hover:bg-blue-100 dark:hover:bg-blue-800 '
                f'transition-colors duration-200 p-3 items-center {indent_class}'
            ) as leaf_row:
                ui.icon(item.icon).classes('text-blue-600 dark:text-blue-400 mr-3 text-lg')
                ui.label(item.label).classes('text-gray-800 dark:text-gray-200 flex-1')
                
                # 保存叶子节点引用
                self.leaf_refs[item.key] = leaf_row
                
                # 绑定点击事件
                leaf_row.on('click', lambda key=item.key: self.select_leaf_item(key))
    
    def _handle_expansion_change(self, key: str, is_open: bool):
        """处理expansion展开/收起事件"""
        if is_open:
            self.expand_parent(key, update_storage=True)
        else:
            self.collapse_parent(key, update_storage=True)
    
    def create_content_area(self):
        """创建内容区域"""
        with ui.column().classes('w-full') as content_container:
            self.content_container = content_container
    
    def initialize_layout(self):
        """初始化布局(延迟执行路由恢复)"""
        def init_routes():
            self.register_system_routes()
            self.restore_route_from_storage()
        
        ui.timer(0.3, init_routes, once=True)