from nicegui import ui

def two_page_content():
    """智能问数页面内容"""
    ui.label('智能问数').classes('text-3xl font-bold text-blue-800 dark:text-blue-200')
    ui.label('使用自然语言查询您的数据。').classes('text-gray-600 dark:text-gray-400 mt-4')
    ui.input('请输入您的问题', placeholder='例如：上个月销售额是多少？').classes('w-full mt-2')
    ui.button('开始分析').classes('mt-4')