from nicegui import ui, app
from .chat_data_state import ChatDataState
from .chat_area_manager import ChatAreaManager
from .chat_sidebar_manager import ChatSidebarManager

def chat_page():
    ui.add_head_html('''
        <style>
        /* 聊天组件专用样式 - 只影响聊天组件内部，不影响全局 */
        .chat-archive-container {
            /*overflow: hidden !important;*/
            height: calc(100vh - 145px) !important;
            margin: 0 !important;
            padding: 0 !important;
            overflow-y: auto !important;
        }        
        .chat-archive-sidebar {
            border-right: 1px solid #e5e7eb;
            overflow-y: auto;
        }
        .chat-archive-sidebar::-webkit-scrollbar {
            width: 2px;
        }
        .chat-archive-sidebar::-webkit-scrollbar-track {
            background: transparent;
        }
        .chat-archive-sidebar::-webkit-scrollbar-thumb {
            background-color: #d1d5db;
            border-radius: 3px;
        }
        .chat-archive-sidebar::-webkit-scrollbar-thumb:hover {
            background-color: #9ca3af;
        }
        /* 优化 scroll_area 内容区域的样式 */
        .q-scrollarea__content {
            min-height: 100%;
        }
        .chathistorylist-hide-scrollbar {
            overflow-y: auto;
            scrollbar-width: none;
            -ms-overflow-style: none;
        }
        .chathistorylist-scrollbar::-webkit-scrollbar {
            display: none;
        }
        </style>
    ''')
    
    # 1. 数据状态初始化
    chat_data_state = ChatDataState()
    
    # 2. 创建管理器实例
    chat_area_manager = ChatAreaManager(chat_data_state)
    chat_sidebar_manager = ChatSidebarManager(chat_data_state, chat_area_manager)
    
    # 3. 渲染UI结构
    with ui.row().classes('w-full h-full chat-archive-container').style('height: calc(100vh - 120px); margin: 0; padding: 0;'):
        # 侧边栏
        chat_sidebar_manager.render_ui()
        # 主聊天区域  
        chat_area_manager.render_ui()