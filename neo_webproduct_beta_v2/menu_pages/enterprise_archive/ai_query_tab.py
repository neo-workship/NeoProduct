from nicegui import ui
from .hierarchy_selector_component import HierarchySelector
from .chat_component import chat_page,ChatComponent

def create_ai_query_content_grid():
    """占满视口高度且无滚动条的布局"""
    # chat_page()
    # 关键：父容器用 flex-col，总高度严格 100vh，禁止溢出
    # with ui.column().classes('absolute-center w-full gap-2'):
    # with ui.element('div').classes('flex flex-col h-screen overflow-hidden w-full'):
        
        # 第一部分：层级选择器（固定高度 100px，无 margin/padding）
        # with ui.element('div').classes('flex-none h-[100px] w-full'):
    # hierarchy_selector = HierarchySelector()
    # hierarchy_selector.render()

        # 第二部分：聊天组件（剩余高度，内部滚动）
        # with ui.element('div').classes('flex-1 min-h-0 w-full'):
            # chat_component = ChatComponent()
            # chat_component.render()
    chat_page()
        