"""
企业档案主页面
整合4个tab的入口文件
"""
from auth import auth_manager
from auth.decorators import require_permission
from nicegui import ui
from common.exception_handler import safe_protect

from .ai_query_tab import create_ai_query_content_grid
from .data_operator_tab import create_data_operator_content_grid
from .data_sync_tab import create_data_sync_content_grid
from .setting_tab import create_setting_content_grid

@safe_protect(name="一企一档", error_msg="一企一档页面加载失败")
def enterprise_archive_content():
    """企业档案主内容"""
    user = auth_manager.current_user
    
    with ui.splitter(value=10).classes('w-full h-full') as splitter:
        with splitter.before:
            with ui.tabs().props('vertical') as tabs:
                ai_query = ui.tab('智能问数', icon='tips_and_updates')
                data_operator = ui.tab('数据操作', icon='precision_manufacturing')
                data_sync = ui.tab('数据更新', icon='sync')
                setting = ui.tab('配置数据', icon='build_circle')
        
        with splitter.after:
            with ui.tab_panels(tabs, value=ai_query).props('vertical').classes('w-full h-full'):    
                with ui.tab_panel(ai_query).classes('w-full'):
                    create_ai_query_content_grid()
                with ui.tab_panel(data_operator).classes('w-full'):
                    create_data_operator_content_grid()
                with ui.tab_panel(data_sync).classes('w-full'):
                    create_data_sync_content_grid()
                with ui.tab_panel(setting).classes('w-full'):
                    create_setting_content_grid()