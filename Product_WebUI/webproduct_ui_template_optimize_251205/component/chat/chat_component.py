"""
ChatComponent - 聊天组件统一入口
提供简洁的API供外部调用,封装所有内部实现细节
"""

from nicegui import ui
from typing import Optional
from .chat_data_state import ChatDataState
from .chat_area_manager import ChatAreaManager
from .chat_sidebar_manager import ChatSidebarManager


class ChatComponent:
    """
    聊天组件主类 - 统一入口
    
    使用示例:
```python
    from component.chat import ChatComponent
    
    # 基础使用
    chat = ChatComponent()
    chat.render()
    
    # 自定义配置
    chat = ChatComponent(
        sidebar_visible=True,
        default_model='deepseek-chat',
        default_prompt='一企一档专家',
        is_record_history=True
    )
    chat.render()
```
    """
    
    def __init__(
        self,
        sidebar_visible: bool = True,
        default_model: Optional[str] = None,
        default_prompt: Optional[str] = None,
        is_record_history: bool = True
    ):
        """
        初始化聊天组件
        
        Args:
            sidebar_visible: 侧边栏是否可见,默认为True
            default_model: 指定的默认LLM模型,默认为None(使用配置文件中的默认值)
            default_prompt: 指定的默认提示词模板,默认为None(使用配置文件中的默认值)
            is_record_history: 是否记录聊天历史到数据库,默认为True
        """
        self.sidebar_visible = sidebar_visible
        self.default_model = default_model
        self.default_prompt = default_prompt
        self.is_record_history = is_record_history
        
        # 初始化数据状态
        self.chat_data_state = ChatDataState()
        
        # 初始化管理器(延迟到render时创建,因为需要UI上下文)
        self.chat_area_manager: Optional[ChatAreaManager] = None
        self.chat_sidebar_manager: Optional[ChatSidebarManager] = None
        
    def render(self):
        """
        渲染聊天组件UI
        必须在NiceGUI的UI上下文中调用
        """
        # 添加聊天组件专用样式
        self._add_chat_styles()
        
        # 创建管理器实例
        self.chat_area_manager = ChatAreaManager(self.chat_data_state)
        self.chat_sidebar_manager = ChatSidebarManager(
            chat_data_state=self.chat_data_state,
            chat_area_manager=self.chat_area_manager,
            sidebar_visible=self.sidebar_visible,
            default_model=self.default_model,
            default_prompt=self.default_prompt,
            is_record_history=self.is_record_history
        )
        
        # 渲染UI结构
        with ui.row().classes('w-full h-full chat-archive-container').style(
            'height: calc(100vh - 120px); margin: 0; padding: 0;'
        ):
            # 侧边栏
            self.chat_sidebar_manager.render_ui()
            # 主聊天区域
            self.chat_area_manager.render_ui()
    
    def _add_chat_styles(self):
        """添加聊天组件专用CSS样式"""
        ui.add_head_html('''
            <style>
            /* 聊天组件专用样式 - 只影响聊天组件内部,不影响全局 */
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
    
    def get_chat_data_state(self) -> ChatDataState:
        """获取聊天数据状态对象"""
        return self.chat_data_state
    
    def get_chat_area_manager(self) -> Optional[ChatAreaManager]:
        """获取聊天区域管理器"""
        return self.chat_area_manager
    
    def get_chat_sidebar_manager(self) -> Optional[ChatSidebarManager]:
        """获取侧边栏管理器"""
        return self.chat_sidebar_manager