from .search_page import search_page_content
from .messages_page import messages_page_content
from .notifications_page import notifications_page_content
from .contact_page import contact_page_content
from .settings_page import settings_page_content
from .user_profile_page import user_profile_page_content

# 导出所有头部页面处理函数
def get_header_page_handlers():
    """获取所有头部页面处理函数"""
    return {
        'search_page': search_page_content,
        'messages_page': messages_page_content,
        'notifications_page': notifications_page_content,
        'contact_page': contact_page_content,
        'settings_page': settings_page_content,
        'user_profile_page': user_profile_page_content
    }

__all__ = [
    'search_page_content',
    'messages_page_content',
    'notifications_page_content',
    'contact_page_content',
    'settings_page_content',
    'user_profile_page_content',
    'get_header_page_handlers'
]