from .home_page import home_content
from .other_demo_page import other_page_content
from .chat_demo_page import chat_page_content
from .auth_test_page import auth_test_page_content


# 导出所有菜单页面处理函数
def get_menu_page_handlers():
    """获取所有菜单页面处理函数"""
    return {
        'home': home_content,
        'other_page': other_page_content,
        'chat_page': chat_page_content,
        'auth_test': auth_test_page_content
    }

__all__ = [
    'home_content',
    'other_page_content',
    'chat_page_content',
    'get_menu_page_handlers',
    'auth_test_page_content'
]