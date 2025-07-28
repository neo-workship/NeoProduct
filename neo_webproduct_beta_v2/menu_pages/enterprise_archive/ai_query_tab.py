"""
智能问数Tab逻辑
"""
from nicegui import ui
from .hierarchy_selector_component import HierarchySelector

from .chat_component import ChatComponent

def create_ai_query_content_grid():
    """创建智能问数内容网格"""
    with ui.column().classes('w-full gap-4 p-4'):
        # 第一部分：层级选择器
        # 使用层级选择器组件
        hierarchy_selector = HierarchySelector()
        hierarchy_selector.render()
        # 第二部分：聊天组件
        # 使用聊天组件
        chat_component = ChatComponent()
        chat_component.render(height="600px")