from typing import Optional, Callable
from .static_resources import static_manager

class LayoutConfig:
    """布局配置类"""
    def __init__(self):
        self.app_title = 'MCP集成综合服务平台'
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