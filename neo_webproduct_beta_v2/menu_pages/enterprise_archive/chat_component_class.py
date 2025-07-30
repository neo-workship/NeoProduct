"""
聊天组件 - 类似Vue组件，可复用的聊天UI
重构为组件类，封装优化但保持原有功能和布局不变
"""
import asyncio
from nicegui import ui, app
from typing import Optional, Dict, Any, Callable, List
from component import static_manager
import os
from .hierarchy_selector_component import HierarchySelector


class ChatComponent:
    """聊天组件类 - 封装聊天界面的所有功能"""
    
    def __init__(self, 
                 title: str = "功能菜单",
                 models: List[str] = None,
                 default_model: str = "deepseek-chat",
                 enable_prompt_assist: bool = True,
                 history_count: int = 5,
                 welcome_message: str = None,
                 on_message_send: Optional[Callable] = None):
        """
        初始化聊天组件
        
        Args:
            title: 侧边栏标题
            models: 可选择的模型列表
            default_model: 默认选择的模型
            enable_prompt_assist: 是否启用提示辅助
            history_count: 历史对话显示数量
            welcome_message: 自定义欢迎消息
            on_message_send: 消息发送时的回调函数
        """
        # 配置参数
        self.title = title
        self.models = models or ["deepseek-chat", "moonshot-v1-8k", "Qwen32B"]
        self.default_model = default_model
        self.enable_prompt_assist = enable_prompt_assist
        self.history_count = history_count
        self.welcome_message = welcome_message
        self.on_message_send = on_message_send
        
        # UI元素引用
        self.ui_refs = {
            'input': {'widget': None},
            'send_button': {'widget': None},
            'scroll_area': None,
            'messages': None,
            'welcome_container': None,
            'model_select': None,
            'prompt_switch': None
        }
        
        # 组件状态
        self.state = {
            'selected_model': default_model,
            'prompt_assist_enabled': False,
            'message_history': [],
            'is_sending': False
        }
        
        # 样式配置
        self.styles = self._get_default_styles()
    
    def _get_default_styles(self) -> str:
        """获取默认样式"""
        return '''
        <style>
            html, body {
                overflow: hidden !important;
                height: 100vh !important;
                margin: 0 !important;
                padding: 0 !important;
            }
            .nicegui-content {
                height: 100vh !important;
                overflow: hidden !important;
            }
            .sidebar {
                border-right: 1px solid #e5e7eb;
                overflow-y: auto;
            }
            .sidebar::-webkit-scrollbar {
                width: 6px;
            }
            .sidebar::-webkit-scrollbar-track {
                background: transparent;
            }
            .sidebar::-webkit-scrollbar-thumb {
                background-color: #d1d5db;
                border-radius: 3px;
            }
            .sidebar::-webkit-scrollbar-thumb:hover {
                background-color: #9ca3af;
            }
            .chat-history-item {
                cursor: pointer;
                transition: background-color 0.2s;
            }
            .chat-history-item:hover {
                background-color: #e5e7eb;
            }
            .expansion-panel {
                margin-bottom: 8px;
            }
            /* 优化 scroll_area 内容区域的样式 */
            .q-scrollarea__content {
                min-height: 100%;
            }
        </style>
        '''
    
    def render(self):
        """渲染聊天组件 - 对应原有的chat_page函数"""
        # 添加样式
        ui.add_head_html(self.styles)
        
        # 主容器 - 使用水平布局
        with ui.row().classes('w-full h-full').style(
            'overflow: hidden; height: calc(100vh - 120px); margin: 0; padding: 0;'
        ):
            self._create_sidebar()
            self._create_chat_area()
    
    def _create_sidebar(self):
        """创建侧边栏"""
        with ui.column().classes('sidebar h-full').style('width: 280px; min-width: 280px;'):
            self._create_sidebar_header()
            self._create_sidebar_content()
    
    def _create_sidebar_header(self):
        """创建侧边栏标题"""
        with ui.row().classes('w-full p-4 border-b'):
            ui.icon('menu', size='md').classes('text-gray-600')
            ui.label(self.title).classes('text-lg font-semibold ml-2')
    
    def _create_sidebar_content(self):
        """创建侧边栏内容"""
        with ui.column().classes('w-full p-3'):
            self._create_add_button()
            self._create_model_selection()
            self._create_prompt_assistance()
            self._create_history_panel()
    
    def _create_add_button(self):
        """创建添加按钮"""
        ui.button(
            '添加按钮', 
            icon='add',
            on_click=self._on_add_click
        ).classes('w-full mb-3').props('outlined')
    
    def _create_model_selection(self):
        """创建模型选择组件"""
        with ui.expansion('选择模型', icon='settings').classes('expansion-panel w-full'):
            with ui.column().classes('p-2'):
                self.ui_refs['model_select'] = ui.select(
                    options=self.models,
                    value=self.default_model,
                    with_input=True,
                    on_change=self._on_model_change
                ).props('autofocus outlined dense')
    
    def _create_prompt_assistance(self):
        """创建提示辅助组件"""
        if not self.enable_prompt_assist:
            return
            
        with ui.expansion('提示辅助', icon='tips_and_updates').classes('expansion-panel w-full'):
            with ui.column().classes('p-2'):
                self.ui_refs['prompt_switch'] = ui.switch(
                    '启用',
                    on_change=self._on_prompt_assist_change
                )
                
                # 创建4个选择器（保持原有结构）
                for i in range(4):
                    ui.select(
                        options=[],
                        with_input=True,
                        on_change=lambda e: ui.notify(e.value)
                    ).props('autofocus outlined dense')
    
    def _create_history_panel(self):
        """创建历史消息面板"""
        with ui.expansion('历史消息', icon='history').classes('expansion-panel w-full'):
            with ui.column().classes('p-2'):
                for i in range(self.history_count):
                    ui.label(f'历史对话 {i+1}').classes(
                        'chat-history-item p-2 rounded cursor-pointer'
                    ).on('click', lambda i=i: self._on_history_click(i))
    
    def _create_chat_area(self):
        """创建主聊天区域"""
        with ui.column().classes('flex-grow h-full').style(
            'position: relative; overflow: hidden;'
        ):
            self._create_message_area()
            self._create_input_area()
    
    def _create_message_area(self):
        """创建消息显示区域"""
        self.ui_refs['scroll_area'] = ui.scroll_area().classes('w-full').style(
            'height: calc(100% - 80px); padding-bottom: 20px;'
        )
        
        with self.ui_refs['scroll_area']:
            self.ui_refs['messages'] = ui.column().classes('w-full p-4 gap-4')
            self._create_welcome_message()
    
    def _create_welcome_message(self):
        """创建欢迎消息"""
        self.ui_refs['welcome_container'] = ui.column().classes('w-full')
        
        with self.ui_refs['welcome_container']:
            with ui.card().classes('w-full max-w-3xl mx-auto shadow-lg'):
                with ui.column().classes('p-6 text-center'):
                    ui.icon('tips_and_updates', size='3xl').classes('text-blue-500 mb-4 text-3xl')
                    
                    welcome_text = self.welcome_message or '欢迎使用一企一档智能助手'
                    ui.label(welcome_text).classes('text-2xl font-bold mb-2')
                    ui.label('请输入您的问题，我将为您提供帮助').classes('text-lg text-gray-600 mb-4')
                    
                    with ui.row().classes('justify-center gap-4'):
                        ui.chip('问答', icon='help_outline').classes('text-blue-600 text-lg')
                        ui.chip('翻译', icon='translate').classes('text-yellow-600 text-lg')
                        ui.chip('写作', icon='edit').classes('text-purple-600 text-lg')
                        ui.chip('分析', icon='analytics').classes('text-orange-600 text-lg')
    
    def _create_input_area(self):
        """创建输入区域"""
        with ui.row().classes('w-full items-center gap-2 p-3 rounded').style(
            'position: absolute; bottom: 10px; left: 10px; right: 10px; z-index: 1000; '
            'margin: 0 auto; max-width: calc(100% - 20px);'
        ):
            self._create_input_field()
            self._create_send_button()
    
    def _create_input_field(self):
        """创建输入框"""
        self.ui_refs['input']['widget'] = ui.textarea(
            placeholder='请输入您的消息...(Enter发送，Shift+Enter换行)'
        ).classes('flex-grow').style(
            'min-height: 44px; max-height: 120px; resize: none;'
        ).props('outlined dense rounded rows=3')
        
        # 绑定键盘事件
        self.ui_refs['input']['widget'].on('keydown', self._handle_keydown)
    
    def _create_send_button(self):
        """创建发送按钮"""
        self.ui_refs['send_button']['widget'] = ui.button(
            icon='send',
            on_click=self._handle_message
        ).props('round dense').classes('ml-2')
    
    async def _scroll_to_bottom_smooth(self):
        """平滑滚动到底部"""
        try:
            self.ui_refs['scroll_area'].scroll_to(percent=1.1)
            await asyncio.sleep(0.05)
        except Exception as e:
            print(f"滚动出错: {e}")
    
    def _handle_keydown(self, e):
        """处理键盘事件"""
        if self.state['is_sending']:
            return
            
        key = e.args.get('key', '')
        shift_key = e.args.get('shiftKey', False)
        
        if key == 'Enter':
            if shift_key:
                # Shift+Enter: 允许换行
                pass
            else:
                # Enter: 发送消息
                ui.run_javascript('event.preventDefault();')
                ui.timer(0.01, lambda: self._handle_message(), once=True)
    
    async def _handle_message(self, event=None):
        """处理消息发送"""
        if self.state['is_sending']:
            return
            
        user_message = self.ui_refs['input']['widget'].value.strip()
        if not user_message:
            return
        
        # 设置发送状态
        self._set_sending_state(True)
        
        try:
            await self._process_message(user_message)
        finally:
            self._set_sending_state(False)
    
    def _set_sending_state(self, is_sending: bool):
        """设置发送状态"""
        self.state['is_sending'] = is_sending
        self.ui_refs['input']['widget'].set_enabled(not is_sending)
        self.ui_refs['send_button']['widget'].set_enabled(not is_sending)
        
        if not is_sending:
            # 清空输入框并重新聚焦
            self.ui_refs['input']['widget'].set_value('')
            self.ui_refs['input']['widget'].run_method('focus')
    
    async def _process_message(self, user_message: str):
        """处理用户消息"""
        # 删除欢迎消息
        if self.ui_refs['welcome_container']:
            self.ui_refs['welcome_container'].clear()
        
        # 添加用户消息
        await self._add_user_message(user_message)
        
        # 调用外部处理函数或默认处理
        if self.on_message_send:
            response = await self.on_message_send(user_message, self.state['selected_model'])
        else:
            response = await self._default_message_handler(user_message)
        
        # 添加AI回复
        await self._add_ai_message(response)
    
    async def _add_user_message(self, message: str):
        """添加用户消息"""
        with self.ui_refs['messages']:
            user_avatar = static_manager.get_fallback_path(
                static_manager.get_logo_path('user.svg'),
                'https://robohash.org/user'
            )
            with ui.chat_message(
                name='您',
                avatar=user_avatar,
                sent=True
            ).classes('w-full'):
                ui.label(message).classes('whitespace-pre-wrap break-words')
        
        await self._scroll_to_bottom_smooth()
    
    async def _add_ai_message(self, message: str):
        """添加AI消息（带打字机效果）"""
        with self.ui_refs['messages']:
            robot_avatar = static_manager.get_fallback_path(
                static_manager.get_logo_path('robot_txt.svg'),
                'https://robohash.org/ui'
            )
            with ui.chat_message(
                name='AI',
                avatar=robot_avatar
            ).classes('w-full'):
                stream_label = ui.label('').classes('whitespace-pre-wrap')
                
                # 打字机效果
                typed = ''
                for ch in message:
                    typed += ch
                    stream_label.text = typed
                    await self._scroll_to_bottom_smooth()
                    await asyncio.sleep(0.03)
                
                await self._scroll_to_bottom_smooth()
    
    async def _default_message_handler(self, user_message: str) -> str:
        """默认消息处理器"""
        return (f"我收到了您的消息：{user_message}。这是一个智能回复示例，"
                f"包含更多内容来演示打字机效果。让我们看看这个功能如何工作...")
    
    # 事件回调方法
    def _on_add_click(self):
        """添加按钮点击事件"""
        ui.notify('添加按钮被点击')
    
    def _on_model_change(self, e):
        """模型选择变化事件"""
        self.state['selected_model'] = e.value
        ui.notify(f'已切换到模型: {e.value}')
    
    def _on_prompt_assist_change(self, e):
        """提示辅助开关变化事件"""
        self.state['prompt_assist_enabled'] = e.value
        ui.notify(f'提示辅助已{"启用" if e.value else "禁用"}')
    
    def _on_history_click(self, index: int):
        """历史对话点击事件"""
        ui.notify(f'加载历史对话 {index + 1}')
    
    # 公共API方法
    def add_message(self, message: str, is_user: bool = True):
        """添加消息到聊天记录"""
        if is_user:
            ui.timer(0.01, lambda: self._add_user_message(message), once=True)
        else:
            ui.timer(0.01, lambda: self._add_ai_message(message), once=True)
    
    def clear_messages(self):
        """清除所有消息"""
        if self.ui_refs['messages']:
            self.ui_refs['messages'].clear()
        self._create_welcome_message()
    
    def set_model(self, model: str):
        """设置当前模型"""
        if model in self.models and self.ui_refs['model_select']:
            self.ui_refs['model_select'].set_value(model)
            self.state['selected_model'] = model
    
    def get_current_model(self) -> str:
        """获取当前选择的模型"""
        return self.state['selected_model']
    
    def set_enabled(self, enabled: bool):
        """启用/禁用聊天组件"""
        if self.ui_refs['input']['widget']:
            self.ui_refs['input']['widget'].set_enabled(enabled)
        if self.ui_refs['send_button']['widget']:
            self.ui_refs['send_button']['widget'].set_enabled(enabled)


# 保持原有接口兼容性
def chat_page():
    """原有的chat_page函数，保持向后兼容"""
    chat_component = ChatComponent()
    chat_component.render()
    return chat_component


# 导出组件类和原有函数
__all__ = ['ChatComponent', 'chat_page']