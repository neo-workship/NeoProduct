from auth import auth_manager
from auth.decorators import require_permission
from nicegui import ui
from common.exception_handler import log_info, log_error, safe, db_safe, safe_protect

@safe_protect(name="ai", error_msg="一企一档页面加载失败")
def llm_workflow_content():
    pass