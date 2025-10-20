from .home_page import home_content
from .person_archive_page import person_archive_content
from .enterprise_archive_page import enterprise_archive_content


# 导出所有菜单页面处理函数
def get_menu_page_handlers():
    """获取所有菜单页面处理函数"""
    return {
        'home': home_content,
        'person_archive': person_archive_content,
        'enterprise_archive': enterprise_archive_content
    }

__all__ = [
    'home_content',
    'person_archive_content',
    'enterprise_archive_content',
    'get_menu_page_handlers'
]