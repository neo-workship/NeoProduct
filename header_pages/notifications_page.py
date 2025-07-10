from nicegui import ui

def notifications_page_content():
    """通知页面内容"""
    ui.label('通知中心').classes('text-3xl font-bold text-pink-800 dark:text-pink-200')
    ui.label('管理您的系统通知和提醒设置。').classes('text-gray-600 dark:text-gray-400 mt-4')
    
    with ui.card().classes('w-full mt-4'):
        ui.label('通知设置').classes('text-lg font-semibold')
        ui.checkbox('邮件通知', value=True).classes('mt-2')
        ui.checkbox('桌面通知', value=False).classes('mt-2')
        ui.checkbox('短信通知', value=False).classes('mt-2')
        ui.button('保存设置', icon='save').classes('mt-4')