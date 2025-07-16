from .home_page import home_page_content
from .dashboard_page import dashboard_page_content
from .data_page import data_page_content
from .analysis_page import analysis_page_content
from .mcp_page import mcp_page_content
from .about_page import about_page_content

# 导出所有菜单页面处理函数
def get_menu_page_handlers():
    """获取所有菜单页面处理函数"""
    return {
        'home': home_page_content,
        'dashboard': dashboard_page_content,
        'data': data_page_content,
        'analysis': analysis_page_content,
        'mcp': mcp_page_content,
        'about': about_page_content
    }

__all__ = [
    'home_page_content',
    'dashboard_page_content',
    'data_page_content',
    'analysis_page_content',
    'mcp_page_content',
    'about_page_content',
    'get_menu_page_handlers'
]