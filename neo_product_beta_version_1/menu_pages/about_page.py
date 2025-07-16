from nicegui import ui

def about_page_content():
    """关于页面内容"""
    ui.label('关于我们').classes('text-3xl font-bold text-gray-800 dark:text-gray-200')
    ui.label('这是一个由NiceGUI构建的SPA示例。').classes('text-gray-600 dark:text-gray-400 mt-4')
    ui.link('访问NiceGUI官网', 'https://nicegui.io').classes('text-blue-500 hover:underline mt-2')