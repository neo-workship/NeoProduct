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
        # 添加key映射
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
    
    # 个人档案管理
    personal_menu = MultilayerMenuItem(
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
            MultilayerMenuItem(
                key='settings',
                label='设置',
                icon='settings',
                route='settings_page'
            ),
        ],
        separator_after=True
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
    config.add_menu_item(personal_menu)
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