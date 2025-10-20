from nicegui import ui

def home_content():
    """首页内容"""
    ui.label('欢迎回到首页!').classes('text-3xl font-bold text-green-800 dark:text-green-200')
    ui.label('这是您个性化的仪表板。').classes('text-gray-600 dark:text-gray-400 mt-4')