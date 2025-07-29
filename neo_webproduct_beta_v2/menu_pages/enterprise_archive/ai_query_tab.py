from nicegui import ui
from .hierarchy_selector_component import HierarchySelector
from .chat_component import chat_page

def create_ai_query_content_grid():
    """占满视口高度且无滚动条的布局"""
    chat_page()
        