from nicegui import ui

def mcp_page_content():
    """MCP服务页面内容"""
    ui.label('MCP服务管理').classes('text-3xl font-bold text-red-800 dark:text-red-200')
    ui.label('管理您的MCP集成服务。').classes('text-gray-600 dark:text-gray-400 mt-4')
    ui.button('重启服务').classes('mt-4')