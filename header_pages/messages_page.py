from nicegui import ui

def messages_page_content():
    """消息页面内容"""
    ui.label('消息中心').classes('text-3xl font-bold text-cyan-800 dark:text-cyan-200')
    ui.label('查看您的所有消息和通知。').classes('text-gray-600 dark:text-gray-400 mt-4')
    
    with ui.card().classes('w-full mt-4'):
        ui.label('新消息').classes('text-lg font-semibold')
        ui.label('您有3条未读消息').classes('text-gray-600 mt-2')
        ui.button('查看全部', icon='visibility').classes('mt-2')