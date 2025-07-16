from nicegui import ui

def data_page_content():
    """数据连接页面内容"""
    ui.label('数据连接').classes('text-3xl font-bold text-orange-800 dark:text-orange-200')
    ui.label('配置您的数据源连接。').classes('text-gray-600 dark:text-gray-400 mt-4')
    ui.input('数据库连接字符串').classes('w-full mt-2')
    ui.button('测试连接').classes('mt-4')