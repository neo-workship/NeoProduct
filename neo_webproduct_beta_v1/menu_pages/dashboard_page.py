from nicegui import ui

def dashboard_content():
    """看板页面内容"""
    ui.label('数据看板').classes('text-3xl font-bold text-purple-800 dark:text-purple-200')
    ui.label('在这里查看关键指标和图表。').classes('text-gray-600 dark:text-gray-400 mt-4')
    ui.button('刷新数据', on_click=lambda: ui.notify('数据已刷新')).classes('mt-4')