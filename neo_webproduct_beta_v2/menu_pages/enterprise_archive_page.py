# menu_pages/enterprise_archive_page.py 
from auth import auth_manager
from auth.decorators import require_permission
from nicegui import ui
# 导入异常处理模块
from common.exception_handler import log_info, log_error, safe, db_safe, safe_protect

@safe_protect(name="一企一档", error_msg="一企一档页面加载失败")
def enterprise_archive_content():
    user = auth_manager.current_user
    # ui.label(f'欢迎，{user.username}, 权限为：{user.permissions}')
    with ui.splitter(value=40).classes('w-full') as splitter:
        with splitter.before:
            with ui.tabs().props('vertical').classes('w-full') as tabs:
                ai_query = ui.tab('智能问数', icon='tips_and_updates')
                data_operator = ui.tab('数据操作', icon='precision_manufacturing')
                data_sync = ui.tab('数据更新', icon='sync_alt')
                setting = ui.tab('配置数据', icon='build_circle')
        with splitter.after:
            with ui.tab_panels(tabs, value=ai_query).props('vertical').classes('w-full'):
                with ui.tab_panel(ai_query):
                    ui.label('Content of 智能问数')
                with ui.tab_panel(data_operator):
                    ui.label('Content of 数据操作')
                with ui.tab_panel(data_sync):
                    ui.label('Content of 数据同步')
                with ui.tab_panel(setting):
                    ui.label('Content of 配置数据')