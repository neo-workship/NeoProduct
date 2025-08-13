"""
聊天组件事件驱动架构 - 第一阶段：基础设施
"""
from typing import Dict, Any, Callable, List
from dataclasses import dataclass
from enum import Enum
import asyncio
from datetime import datetime


class ChatEventType(Enum):
    """聊天事件类型枚举"""
    # 侧边栏事件
    MODEL_CHANGED = "model_changed"
    PROMPT_CHANGED = "prompt_changed"
    NEW_CHAT_REQUESTED = "new_chat_requested"
    CHAT_HISTORY_SELECTED = "chat_history_selected"
    CONFIG_REFRESHED = "config_refreshed"
    
    # 主聊天区事件
    MESSAGE_SENT = "message_sent"
    MESSAGE_RECEIVED = "message_received"
    TYPING_STARTED = "typing_started"
    TYPING_STOPPED = "typing_stopped"
    CHAT_CLEARED = "chat_cleared"
    
    # 共享事件
    ERROR_OCCURRED = "error_occurred"
    UI_UPDATE_REQUESTED = "ui_update_requested"


@dataclass
class ChatEvent:
    """聊天事件数据类"""
    event_type: ChatEventType
    data: Dict[str, Any]
    timestamp: datetime
    source: str  # 事件源标识 (sidebar/chat_area)
    
    @classmethod
    def create(cls, event_type: ChatEventType, data: Dict[str, Any] = None, source: str = "unknown"):
        """创建事件的便捷方法"""
        return cls(
            event_type=event_type,
            data=data or {},
            timestamp=datetime.now(),
            source=source
        )


class ChatEventBus:
    """聊天事件总线 - 事件驱动通信核心"""
    
    def __init__(self):
        # 事件监听器存储 {event_type: [callback_functions]}
        self._listeners: Dict[ChatEventType, List[Callable]] = {}
        # 事件历史记录 (可选，用于调试)
        self._event_history: List[ChatEvent] = []
        # 最大历史记录数量
        self._max_history = 100
    
    def subscribe(self, event_type: ChatEventType, callback: Callable[[ChatEvent], None]):
        """订阅事件"""
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        self._listeners[event_type].append(callback)
        print(f"[EventBus] 订阅事件: {event_type.value}")
    
    def unsubscribe(self, event_type: ChatEventType, callback: Callable[[ChatEvent], None]):
        """取消订阅事件"""
        if event_type in self._listeners and callback in self._listeners[event_type]:
            self._listeners[event_type].remove(callback)
            print(f"[EventBus] 取消订阅事件: {event_type.value}")
    
    def publish(self, event: ChatEvent):
        """发布事件"""
        print(f"[EventBus] 发布事件: {event.event_type.value} from {event.source}")
        
        # 记录事件历史
        self._add_to_history(event)
        
        # 通知所有监听器
        if event.event_type in self._listeners:
            for callback in self._listeners[event.event_type]:
                try:
                    # 异步处理事件
                    if asyncio.iscoroutinefunction(callback):
                        asyncio.create_task(callback(event))
                    else:
                        callback(event)
                except Exception as e:
                    print(f"[EventBus] 事件处理异常: {e}")
                    # 发布错误事件
                    error_event = ChatEvent.create(
                        ChatEventType.ERROR_OCCURRED,
                        {"error": str(e), "original_event": event.event_type.value},
                        "event_bus"
                    )
                    self._add_to_history(error_event)
    
    def publish_simple(self, event_type: ChatEventType, data: Dict[str, Any] = None, source: str = "unknown"):
        """发布事件的简便方法"""
        event = ChatEvent.create(event_type, data, source)
        self.publish(event)
    
    def _add_to_history(self, event: ChatEvent):
        """添加事件到历史记录"""
        self._event_history.append(event)
        # 保持历史记录在限制范围内
        if len(self._event_history) > self._max_history:
            self._event_history = self._event_history[-self._max_history:]
    
    def get_event_history(self, event_type: ChatEventType = None, limit: int = 20) -> List[ChatEvent]:
        """获取事件历史记录"""
        if event_type:
            filtered_events = [e for e in self._event_history if e.event_type == event_type]
            return filtered_events[-limit:] if filtered_events else []
        return self._event_history[-limit:]
    
    def clear_history(self):
        """清空事件历史"""
        self._event_history.clear()
        print("[EventBus] 事件历史已清空")


# 全局事件总线实例
chat_event_bus = ChatEventBus()


class ChatSidebarManager:
    """聊天侧边栏管理器 - 第二阶段完整实现"""
    
    def __init__(self, event_bus: ChatEventBus):
        self.event_bus = event_bus
        
        # === 模型配置相关属性 ===
        self._model_options = []
        self._selected_model = None
        self._model_config = None
        self._model_select_widget = None
        
        # === 提示词配置相关属性 ===
        self._prompt_options = []
        self._selected_prompt = None
        self._prompt_config = None
        self._prompt_select_widget = None
        
        # === 数据选择相关属性 ===
        self._data_enabled = False
        self._hierarchy_selector = None
        
        # === 聊天历史相关属性 ===
        self._chat_histories = []
        self._history_list_container = None
        
        # === UI 容器引用 ===
        self._sidebar_container = None
        
        # 设置事件监听器
        self._setup_event_listeners()
        
        print("[ChatSidebarManager] 初始化完成")
    
    def _setup_event_listeners(self):
        """设置事件监听器"""
        # 监听来自主聊天区的事件
        self.event_bus.subscribe(ChatEventType.CHAT_CLEARED, self._on_chat_cleared)
        self.event_bus.subscribe(ChatEventType.ERROR_OCCURRED, self._on_error_occurred)
    
    # === 模型配置 Getter/Setter ===
    @property
    def selected_model(self) -> str:
        return self._selected_model
    
    @selected_model.setter
    def selected_model(self, value: str):
        old_model = self._selected_model
        self._selected_model = value
        
        # 发布模型变更事件
        self.event_bus.publish_simple(
            ChatEventType.MODEL_CHANGED,
            {"old_model": old_model, "new_model": value},
            "sidebar"
        )
        
        # 更新UI组件
        if self._model_select_widget:
            self._model_select_widget.value = value
    
    @property
    def model_options(self) -> List[str]:
        return self._model_options
    
    @model_options.setter
    def model_options(self, value: List[str]):
        self._model_options = value
        if self._model_select_widget:
            self._model_select_widget.options = value
    
    # === 提示词配置 Getter/Setter ===
    @property
    def selected_prompt(self) -> str:
        return self._selected_prompt
    
    @selected_prompt.setter
    def selected_prompt(self, value: str):
        old_prompt = self._selected_prompt
        self._selected_prompt = value
        
        # 发布提示词变更事件
        self.event_bus.publish_simple(
            ChatEventType.PROMPT_CHANGED,
            {"old_prompt": old_prompt, "new_prompt": value},
            "sidebar"
        )
        
        # 更新UI组件
        if self._prompt_select_widget:
            self._prompt_select_widget.value = value
    
    @property
    def prompt_options(self) -> List[str]:
        return self._prompt_options
    
    @prompt_options.setter
    def prompt_options(self, value: List[str]):
        self._prompt_options = value
        if self._prompt_select_widget:
            self._prompt_select_widget.options = value
    
    # === 数据选择相关 ===
    @property
    def data_enabled(self) -> bool:
        return self._data_enabled
    
    @data_enabled.setter
    def data_enabled(self, value: bool):
        self._data_enabled = value
        # 可以添加数据启用/禁用的逻辑
    
    # === 聊天历史相关 ===
    @property
    def chat_histories(self) -> List[Dict]:
        return self._chat_histories
    
    @chat_histories.setter
    def chat_histories(self, value: List[Dict]):
        self._chat_histories = value
        self._refresh_history_ui()
    
    # === 核心业务方法 ===
    def initialize_config(self):
        """初始化配置 - 从现有代码迁移"""
        try:
            # 导入配置模块 (从原代码迁移)
            from .config import (
                get_model_options_for_select, 
                get_default_model,
                get_prompt_options_for_select,
                get_default_prompt
            )
            
            # 初始化模型配置
            self.model_options = get_model_options_for_select()
            self.selected_model = get_default_model() or 'deepseek-chat'
            
            # 初始化提示词配置
            self.prompt_options = get_prompt_options_for_select()
            self.selected_prompt = get_default_prompt() or (self.prompt_options[0] if self.prompt_options else None)
            
        except Exception as e:
            print(f"[ChatSidebarManager] 配置初始化失败: {e}")
    
    def refresh_model_config(self):
        """刷新模型配置"""
        try:
            from .config import reload_llm_config, get_model_options_for_select, get_default_model
            
            reload_llm_config()
            self.model_options = get_model_options_for_select()
            default_model = get_default_model()
            if default_model:
                self.selected_model = default_model
                
            # 发布配置刷新事件
            self.event_bus.publish_simple(
                ChatEventType.CONFIG_REFRESHED,
                {"type": "model", "options": self.model_options},
                "sidebar"
            )
            
        except Exception as e:
            self.event_bus.publish_simple(
                ChatEventType.ERROR_OCCURRED,
                {"error": f"模型配置刷新失败: {e}"},
                "sidebar"
            )
    
    def refresh_prompt_config(self):
        """刷新提示词配置"""
        try:
            from .config import reload_prompt_config, get_prompt_options_for_select, get_default_prompt
            
            reload_prompt_config()
            self.prompt_options = get_prompt_options_for_select()
            default_prompt = get_default_prompt()
            if default_prompt:
                self.selected_prompt = default_prompt
                
            # 发布配置刷新事件
            self.event_bus.publish_simple(
                ChatEventType.CONFIG_REFRESHED,
                {"type": "prompt", "options": self.prompt_options},
                "sidebar"
            )
            
        except Exception as e:
            self.event_bus.publish_simple(
                ChatEventType.ERROR_OCCURRED,
                {"error": f"提示词配置刷新失败: {e}"},
                "sidebar"
            )
    
    def load_chat_histories(self):
        """加载聊天历史 - 从原代码迁移逻辑"""
        try:
            from auth import auth_manager
            from database_models.business_models.chat_history_model import ChatHistory
            from auth.database import get_db
            
            current_user = auth_manager.current_user
            if not current_user:
                return
            
            with get_db() as db:
                chat_histories = ChatHistory.get_user_recent_chats(
                    db_session=db, 
                    user_id=current_user.id, 
                    limit=20
                )
                
                # 转换为UI需要的数据结构
                history_list = []
                for chat in chat_histories:
                    preview = chat.get_message_preview(30)
                    duration_info = chat.get_duration_info()
                    
                    history_list.append({
                        'id': chat.id,
                        'title': chat.title,
                        'preview': preview,
                        'created_at': chat.created_at.strftime('%Y-%m-%d %H:%M'),
                        'updated_at': chat.updated_at.strftime('%Y-%m-%d %H:%M'),
                        'last_message_at': chat.last_message_at.strftime('%Y-%m-%d %H:%M') if chat.last_message_at else None,
                        'message_count': chat.message_count,
                        'model_name': chat.model_name,
                        'duration_minutes': duration_info['duration_minutes'],
                        'chat_object': chat
                    })
                
                self.chat_histories = history_list
                
        except Exception as e:
            print(f"[ChatSidebarManager] 加载聊天历史失败: {e}")
            self.event_bus.publish_simple(
                ChatEventType.ERROR_OCCURRED,
                {"error": f"加载聊天历史失败: {e}"},
                "sidebar"
            )
    
    def delete_chat_history(self, chat_id: int):
        """删除聊天历史"""
        try:
            from database_models.business_models.chat_history_model import ChatHistory
            from auth.database import get_db
            
            with get_db() as db:
                ChatHistory.delete_chat(db, chat_id)
                
            # 重新加载历史列表
            self.load_chat_histories()
            
            self.event_bus.publish_simple(
                ChatEventType.UI_UPDATE_REQUESTED,
                {"action": "chat_deleted", "chat_id": chat_id},
                "sidebar"
            )
            
        except Exception as e:
            self.event_bus.publish_simple(
                ChatEventType.ERROR_OCCURRED,
                {"error": f"删除聊天失败: {e}"},
                "sidebar"
            )
    
    def request_new_chat(self):
        """请求新建聊天"""
        self.event_bus.publish_simple(
            ChatEventType.NEW_CHAT_REQUESTED,
            {},
            "sidebar"
        )
    
    def select_chat_history(self, chat_data: Dict):
        """选择聊天历史"""
        self.event_bus.publish_simple(
            ChatEventType.CHAT_HISTORY_SELECTED,
            {"chat": chat_data},
            "sidebar"
        )
    
    # === UI 绑定相关方法 ===
    def bind_model_select_widget(self, widget):
        """绑定模型选择组件"""
        self._model_select_widget = widget
        widget.bind_value(self, 'selected_model')
        
    def bind_prompt_select_widget(self, widget):
        """绑定提示词选择组件"""
        self._prompt_select_widget = widget
        widget.bind_value(self, 'selected_prompt')
    
    def bind_hierarchy_selector(self, selector):
        """绑定层级选择器"""
        self._hierarchy_selector = selector
    
    def bind_history_container(self, container):
        """绑定历史记录容器"""
        self._history_list_container = container
    
    def _refresh_history_ui(self):
        """刷新历史记录UI"""
        if self._history_list_container:
            # 这里可以触发UI刷新逻辑
            pass
    
    # === 事件处理方法 ===
    def _on_chat_cleared(self, event: ChatEvent):
        """处理聊天清空事件"""
        print(f"[ChatSidebarManager] 收到聊天清空事件: {event.data}")
    
    def _on_error_occurred(self, event: ChatEvent):
        """处理错误事件"""
        print(f"[ChatSidebarManager] 收到错误事件: {event.data}")
        
    # === 获取当前状态的便捷方法 ===
    def get_current_config(self) -> Dict[str, Any]:
        """获取当前完整配置"""
        return {
            "selected_model": self.selected_model,
            "model_options": self.model_options,
            "selected_prompt": self.selected_prompt,
            "prompt_options": self.prompt_options,
            "data_enabled": self.data_enabled,
            "chat_histories_count": len(self.chat_histories)
        }


class ChatAreaManager:
    """聊天主区域管理器 - 第三阶段实现"""
    
    def __init__(self, event_bus: ChatEventBus):
        self.event_bus = event_bus
        self._setup_event_listeners()
        
        # TODO: 第三阶段实现的属性
        # self._current_messages = []
        # self._is_typing = False
        # self._current_input = ""
        
        print("[ChatAreaManager] 初始化完成")
    
    def _setup_event_listeners(self):
        """设置事件监听器"""
        # TODO: 第三阶段实现
        pass
    
    # TODO: 第三阶段实现 Getter/Setter 方法和 UI 绑定


# === 第二阶段迁移示例 ===
def chat_page_with_sidebar_manager():
    """
    集成 ChatSidebarManager 的聊天页面示例
    这个函数展示如何在现有 chat_component.py 中集成侧边栏管理器
    """
    from nicegui import ui
    
    # 创建侧边栏管理器
    sidebar_manager = ChatSidebarManager(chat_event_bus)
    
    # 初始化配置
    sidebar_manager.initialize_config()
    
    # === 事件处理函数 (从原代码迁移) ===
    def on_model_change(e):
        """模型变更处理"""
        sidebar_manager.selected_model = e.value
    
    def on_prompt_change(e):
        """提示词变更处理"""
        sidebar_manager.selected_prompt = e.value
    
    def on_refresh_model_config():
        """刷新模型配置"""
        sidebar_manager.refresh_model_config()
        ui.notify('模型配置已刷新', type='positive')
    
    def on_refresh_prompt_config():
        """刷新提示词配置"""
        sidebar_manager.refresh_prompt_config()
        ui.notify('提示词配置已刷新', type='positive')
    
    def on_create_new_chat():
        """新建聊天"""
        sidebar_manager.request_new_chat()
    
    def delete_chat_item(chat_id):
        """删除聊天项"""
        sidebar_manager.delete_chat_history(chat_id)
        ui.notify('聊天已删除', type='positive')
    
    def select_chat_item(chat_data):
        """选择聊天项"""
        sidebar_manager.select_chat_history(chat_data)
    
    def refresh_chat_history_list():
        """刷新聊天历史列表"""
        sidebar_manager.load_chat_histories()
        ui.notify('聊天历史已刷新', type='positive')
    
    # === 原有UI布局保持不变 ===
    ui.add_head_html('''
        <style>
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
    
    # 主容器 - 保持原有布局
    with ui.row().classes('w-full h-full chat-archive-container').style('height: calc(100vh - 120px); margin: 0; padding: 0;'):   
        # 侧边栏 - 固定宽度，保持原有样式
        with ui.column().classes('chat-archive-sidebar h-full').style('width: 280px; min-width: 280px;'):
            # 侧边栏标题 - 保持原有
            with ui.row().classes('w-full'):
                ui.icon('menu', size='md').classes('text-gray-600')
                ui.label('功能菜单').classes('text-lg font-semibold')
            
            # 侧边栏内容 - 保持原有结构
            with ui.column().classes('w-full items-center'):
                # 新建对话按钮 - 使用管理器方法
                ui.button('新建对话', icon='add', on_click=on_create_new_chat).classes('w-64').props('outlined rounded')
                
                # 选择模型expansion组件 - 绑定管理器
                with ui.expansion('选择模型', icon='view_in_ar').classes('w-full'):
                    with ui.column().classes('w-full'):
                        # 配置管理按钮行
                        with ui.row().classes('w-full'):
                            ui.button(
                                '刷新配置', 
                                icon='refresh',
                                on_click=on_refresh_model_config
                            ).classes('text-xs').props('dense flat color="primary"').style('min-width: 80px;')
                        
                        # 模型选择下拉框 - 绑定到管理器
                        model_select = ui.select(
                            options=sidebar_manager.model_options,
                            value=sidebar_manager.selected_model,
                            with_input=True,
                            on_change=on_model_change
                        ).classes('w-full').props('autofocus dense')
                        
                        # 绑定到管理器
                        sidebar_manager.bind_model_select_widget(model_select)

                # 上下文模板expansion组件 - 绑定管理器
                with ui.expansion('上下文模板', icon='pattern').classes('w-full'):
                    with ui.column().classes('w-full'):
                        # 配置管理按钮行
                        with ui.row().classes('w-full'):
                            ui.button(
                                '刷新配置', 
                                icon='refresh',
                                on_click=on_refresh_prompt_config
                            ).classes('text-xs').props('dense flat color="primary"').style('min-width: 80px;')
                        
                        # 提示词选择下拉框 - 绑定到管理器
                        prompt_select = ui.select(
                            options=sidebar_manager.prompt_options, 
                            value=sidebar_manager.selected_prompt, 
                            with_input=True,
                            on_change=on_prompt_change
                        ).classes('w-full').props('autofocus dense')
                        
                        # 绑定到管理器
                        sidebar_manager.bind_prompt_select_widget(prompt_select)

                # select数据expansion组件 - 保持原有
                with ui.expansion('提示数据', icon='tips_and_updates').classes('w-full'):
                    with ui.column().classes('w-full chathistorylist-hide-scrollbar').style('flex-grow: 1; '):
                        switch = ui.switch('启用', value=False)
                        # 这里可以绑定到 sidebar_manager.data_enabled
                        from .hierarchy_selector_component import HierarchySelector
                        hierarchy_selector = HierarchySelector(multiple=True)
                        hierarchy_selector.render_column()
                        sidebar_manager.bind_hierarchy_selector(hierarchy_selector)
                       
                # 聊天历史expansion组件 - 使用管理器
                with ui.expansion('历史消息', icon='history').classes('w-full'):
                    with ui.column().classes('w-full'):
                        # 添加刷新按钮
                        with ui.row().classes('w-full'):
                            ui.button(
                                '刷新历史', 
                                icon='refresh',
                                on_click=refresh_chat_history_list
                            ).classes('text-xs').props('dense flat color="primary"').style('min-width: 80px;')
                        
                        # 聊天历史列表容器
                        history_list_container = ui.column().classes('w-full h-96 chathistorylist-hide-scrollbar')
                        sidebar_manager.bind_history_container(history_list_container)
                        
                        # 创建聊天历史列表
                        def create_chat_history_list():
                            """创建聊天历史列表 - 使用管理器数据"""
                            if not sidebar_manager.chat_histories:
                                ui.label('暂无聊天记录').classes('text-gray-500 text-center text-sm')
                                return
                            
                            for chat in sidebar_manager.chat_histories:
                                with ui.card().classes('w-full mb-1 p-2 cursor-pointer hover:bg-gray-50').style('border-left: 3px solid #3b82f6;'):
                                    with ui.row().classes('w-full items-center'):
                                        with ui.column().classes('flex-grow'):
                                            # 标题和预览
                                            ui.label(chat['title'] or '未命名对话').classes('font-medium text-sm')
                                            if chat.get('preview'):
                                                ui.label(chat['preview']).classes('text-xs text-gray-500')
                                            
                                            # 时间信息
                                            with ui.row().classes('items-center gap-2'):
                                                ui.icon('schedule', size='xs').classes('text-gray-400')
                                                ui.label(chat['updated_at']).classes('text-xs text-gray-400')
                                                
                                                if chat.get('message_count', 0) > 0:
                                                    ui.icon('chat', size='xs').classes('text-gray-400')
                                                    ui.label(f"{chat['message_count']}条").classes('text-xs text-gray-400')
                                        
                                        # 操作按钮
                                        with ui.column().classes('items-center'):
                                            ui.icon('chat', size='sm').classes('text-blue-600 cursor-pointer').tooltip('加载对话').on('click', lambda chat=chat: select_chat_item(chat))
                                            ui.icon('delete', size='sm').classes('text-red-600 cursor-pointer').tooltip('删除').on('click', lambda chat_id=chat['id']: delete_chat_item(chat_id))
                        
                        with history_list_container:
                            # 初始加载历史记录
                            sidebar_manager.load_chat_histories()
                            create_chat_history_list()
        
        # 主聊天区域占位 - 第三阶段实现
        with ui.column().classes('flex-grow h-full').style('position: relative; overflow: hidden;'):
            ui.label('主聊天区域 - 第三阶段实现').classes('text-center text-gray-500 mt-20')
    
    # 返回管理器实例，供外部使用
    return sidebar_manager


# 测试用例和使用示例
def test_event_system():
    """测试事件系统"""
    print("=== 测试聊天事件系统 ===")
    
    # 创建事件总线
    bus = ChatEventBus()
    
    # 定义测试监听器
    def on_model_changed(event: ChatEvent):
        print(f"模型变更监听器触发: {event.data}")
    
    def on_message_sent(event: ChatEvent):
        print(f"消息发送监听器触发: {event.data}")
    
    # 订阅事件
    bus.subscribe(ChatEventType.MODEL_CHANGED, on_model_changed)
    bus.subscribe(ChatEventType.MESSAGE_SENT, on_message_sent)
    
    # 发布测试事件
    bus.publish_simple(
        ChatEventType.MODEL_CHANGED,
        {"old_model": "gpt-3.5", "new_model": "gpt-4"},
        "sidebar"
    )
    
    bus.publish_simple(
        ChatEventType.MESSAGE_SENT,
        {"message": "Hello, world!", "user": "test_user"},
        "chat_area"
    )
    
    # 查看事件历史
    print(f"\n事件历史记录数量: {len(bus.get_event_history())}")
    for event in bus.get_event_history():
        print(f"  - {event.event_type.value} ({event.timestamp.strftime('%H:%M:%S')})")


if __name__ == "__main__":
    test_event_system()