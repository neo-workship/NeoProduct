"""
企业档案主页面
整合4个tab的入口文件
"""
from auth import auth_manager
from auth.decorators import require_permission
from nicegui import ui
from common.exception_handler import safe_protect
from component import static_manager
from .chat_component import chat_page

@safe_protect(name="一企一档", error_msg="一企一档页面加载失败")
def enterprise_archive_content():
    chat_page()