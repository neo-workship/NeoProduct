# menu_pages/enterprise_archive_page.py 
from auth import auth_manager
from auth.decorators import require_permission
from nicegui import app,ui
from common.exception_handler import log_info, log_error, safe, db_safe, safe_protect

@safe_protect(name="一企一档", error_msg="一企一档页面加载失败")
def enterprise_archive_content():
    user = auth_manager.current_user
    with ui.row().classes('w-full'):    
        # 第一行：标签头部区域
        with ui.tabs().classes('flex justify-start') as tabs:
            ai_query = ui.tab('智能问数', icon='tips_and_updates')
            data_operator = ui.tab('数据操作', icon='precision_manufacturing')
            data_sync = ui.tab('数据更新', icon='sync')
            setting = ui.tab('配置数据', icon='build_circle')
            
        # 第二行：分隔线
        ui.separator().classes('w-full')
        
        # 第三行：内容区域
        with ui.tab_panels(tabs, value=ai_query).classes('w-full'):
            with ui.tab_panel(ai_query).classes('w-full'):
                create_ai_query_content_grid()
            with ui.tab_panel(data_operator).classes('w-full'):
                create_data_operator_content_grid()
            with ui.tab_panel(data_sync).classes('w-full'):
                create_data_sync_content_grid()
            with ui.tab_panel(setting).classes('w-full'):
                create_setting_content_grid()

def create_ai_query_content_grid():
    pass

def create_data_operator_content_grid():
    pass

def create_data_sync_content_grid():
    pass
        
def create_setting_content_grid():
    pass
