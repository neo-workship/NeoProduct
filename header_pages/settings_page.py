from nicegui import ui

def settings_page_content():
    """系统设置页面内容"""
    ui.label('系统设置').classes('text-3xl font-bold text-teal-800 dark:text-teal-200')
    ui.label('这是您的系统设置页面。').classes('text-gray-600 dark:text-gray-400 mt-4')
    
    with ui.card().classes('w-full mt-4'):
        ui.label('基本设置').classes('text-lg font-semibold')
        ui.checkbox('启用通知', value=True).classes('mt-4')
        ui.input('默认语言', value='中文').classes('mt-2')
        ui.select(['简体中文', '繁體中文', 'English'], value='简体中文', label='界面语言').classes('mt-2')
        
    with ui.card().classes('w-full mt-4'):
        ui.label('高级设置').classes('text-lg font-semibold')
        ui.checkbox('开启调试模式', value=False).classes('mt-4')
        ui.checkbox('自动备份数据', value=True).classes('mt-2')
        ui.number('会话超时时间 (分钟)', value=30, min=5, max=120).classes('mt-2')
        
    ui.button('保存设置', icon='save').classes('mt-4')