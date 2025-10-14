

"""
数据操作Tab逻辑
"""
from nicegui import ui

def bi_analysis_content():
    """创建数据操作内容网格"""
    with ui.grid(columns=1).classes('w-full gap-4'):
        ui.label('数据操作功能').classes('text-h6')
        ui.label('此功能正在开发中...').classes(' text-grey-6')