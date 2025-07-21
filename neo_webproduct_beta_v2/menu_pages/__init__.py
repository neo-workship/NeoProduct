from .home_page import home_content
from .dashboard_page import dashboard_content
from .smart_audit_page import smart_audit_content
from .person_archive_page import person_archive_content
from .enterprise_archive_page import enterprise_archive_content
from .about_page import about_page_content
from .smart_index_page import smart_index_content

# 导出所有菜单页面处理函数
def get_menu_page_handlers():
    """获取所有菜单页面处理函数"""
    return {
        'home': home_content,
        'dashboard': dashboard_content,
        'smart_audit': smart_audit_content,
        'smart_index':smart_index_content,
        'person_archive': person_archive_content,
        'enterprise_archive': enterprise_archive_content,
        'about': about_page_content
    }

__all__ = [
    'home_content',
    'dashboard_content',
    'smart_audit_content',
    'smart_index_content',
    'person_archive_content',
    'enterprise_archive_content',
    'about_page_content',
    'get_menu_page_handlers'
]