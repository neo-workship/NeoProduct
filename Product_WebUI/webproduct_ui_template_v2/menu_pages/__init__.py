from .home_page import home_content
from .two_page import two_page_content
from .one_page import one_page_content


# 导出所有菜单页面处理函数
def get_menu_page_handlers():
    """获取所有菜单页面处理函数"""
    return {
        'home': home_content,
        'two_page': two_page_content,
        'one_page': one_page_content
    }

__all__ = [
    'home_content',
    'two_page_content',
    'one_page_content',
    'get_menu_page_handlers'
]