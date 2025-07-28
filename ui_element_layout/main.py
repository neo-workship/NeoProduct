from nicegui import ui
from ui_element_layout.chat_message.ai_query import create_ai_query_content
from data_operator import create_data_operator_content
from data_sync import create_data_sync_content
from setting import create_setting_content
from grid_layout import create_grid_layout_content

@ui.page('/')
def enterprise_archive_content():  
    with ui.row().classes('w-full'):
        with ui.tabs().classes('flex') as tabs:
            ai_query = ui.tab('智能问数', icon='tips_and_updates')
            data_operator = ui.tab('数据操作', icon='precision_manufacturing')
            data_sync = ui.tab('数据更新', icon='sync_alt')
            setting = ui.tab('配置数据', icon='build_circle')
            grid_layout = ui.tab("Grid布局",icon="grid_4x4")
        with ui.tab_panels(tabs, value=ai_query).classes('w-full'):
            with ui.tab_panel(ai_query).classes('w-full'):
                create_ai_query_content()
            with ui.tab_panel(data_operator).classes('w-full'):
                create_data_operator_content()
            with ui.tab_panel(data_sync).classes('w-full'):
                create_data_sync_content()
            with ui.tab_panel(setting).classes('w-full'):
                create_setting_content()
            with ui.tab_panel(grid_layout).classes('w-full'):
                create_grid_layout_content()

if __name__ in {"__main__", "__mp_main__"}:
    ui.run(
        title='弹性布局页面',
        host='0.0.0.0',
        port=8081,
        reload=True,
        show=True
    )