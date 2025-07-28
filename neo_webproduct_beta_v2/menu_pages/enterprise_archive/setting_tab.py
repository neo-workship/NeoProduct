"""
配置数据Tab逻辑
"""
from nicegui import ui

def create_setting_content_grid():
    """创建配置数据内容网格"""
    with ui.grid(columns=1).classes('w-full gap-4'):
        ui.label('配置数据功能').classes('text-h6')
        ui.label('此功能正在开发中...').classes('text-body1 text-grey-6')