from nicegui import ui, app
from .chat_data_state import ChatDataState,chat_component_styles
from .chat_area_manager import ChatAreaManager
from .chat_sidebar_manager import ChatSidebarManager

def chat_page():

    ui.add_head_html('''
        <style>
        /* 聊天组件专用样式 - 跨多个管理器使用 */
        .chat-archive-container {
            height: calc(100vh - 145px) !important;
            margin: 0 !important;
            padding: 0 !important;
            overflow-y: auto !important;
        }
        
        .chat-archive-sidebar {
            border-right: 1px solid #e5e7eb;
            overflow-y: auto;
        }
        
        .chathistorylist-hide-scrollbar {
            overflow-y: auto;
            scrollbar-width: none;
            -ms-overflow-style: none;
        }
        /* ... 其他样式 */
        </style>
    ''')
    
    # 1. 数据状态初始化
    chat_data_state = ChatDataState()
    
    # 2. 统一应用样式（保持在最外层）
    # ui.add_head_html(chat_component_styles)
    
    # 3. 创建管理器实例
    chat_area_manager = ChatAreaManager(chat_data_state)
    chat_sidebar_manager = ChatSidebarManager(chat_data_state, chat_area_manager)
    
    # 4. 渲染UI结构
    with ui.row().classes('w-full h-full chat-archive-container').style('height: calc(100vh - 120px); margin: 0; padding: 0;'):
        # 侧边栏
        chat_sidebar_manager.render_ui()
        # 主聊天区域  
        chat_area_manager.render_ui()