from nicegui import ui

def search_page_content():
    """搜索页面内容"""
    ui.label('搜索页面').classes('text-3xl font-bold text-yellow-800 dark:text-yellow-200')
    ui.label('您可以在这里进行全局搜索。').classes('text-gray-600 dark:text-gray-400 mt-4')
    ui.input('搜索关键词', placeholder='输入关键词').classes('w-full mt-2')
    ui.button('搜索').classes('mt-4')