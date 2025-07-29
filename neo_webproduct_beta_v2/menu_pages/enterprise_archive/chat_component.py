"""
聊天组件 - 类似Vue组件，可复用的聊天UI
"""
import asyncio
from nicegui import ui, app
from typing import Optional
from component import static_manager
import os

class ChatComponent:
    """聊天组件，类似Vue组件"""
    
    def __init__(self):
        self.messages = None
        self.welcome_message_container = None
        self.input_ref = {'widget': None}
        # self._add_chat_styles()
    
    def _add_chat_styles(self):
        """添加聊天样式"""
        ui.add_head_html('''
            <style>
            /* === 用户消息（sent） === */
            /* 气泡整体背景 */
            .q-message-sent .q-message-container {
                background-color: #1976d2 !important; 
            }
            /* 文字块背景（去掉 Quasar 自带的白色） */
            .q-message-sent .q-message-text,
            .q-message-sent .q-message-text-content {
                background: transparent !important;
                color: #ffffff;
            }

            /* === Bot 消息（received） === */
            .q-message-received .q-message-container {
                background-color: #e0e0e0 !important;   /* 灰色 */
            }
            .q-message-received .q-message-text,
            .q-message-received .q-message-text-content {
                background: transparent !important;
                color: #000000;
            }
            
            /* 聊天容器样式 */
            .chat-container {
                height: 500px;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                background: #fafafa;
            }
            </style>
        ''')
    
    def render(self, height: str = "460px"):
        """
        渲染聊天组件
        Args:
            height: 聊天容器高度，默认500px
        """
        with ui.column().classes('w-full'):
            # ui.label('智能问答').classes('text-h6 mb-2')
            
            # 聊天容器
            with ui.column().classes('w-full').style(f'height: {height}; border: 1px solid #e0e0e0; border-radius: 8px; background: #fafafa;'):
                # 聊天消息区域 - 可滚动，占据剩余空间
                self.messages = ui.column().classes('flex-grow overflow-y-auto p-4 w-full').style('scroll-behavior: smooth;')
                
                # 欢迎消息容器
                self.welcome_message_container = ui.column().classes('absolute-center items-center')
                with self.welcome_message_container:
                    ui.icon('chat', size='4rem').classes('text-gray-400')
                    ui.label('欢迎使用一企一档智能问数！').classes('text-lg text-gray-600')
                
                # 底部输入区
                with ui.row().classes('w-full p-4 border-t ').style('min-height: 80px;'):
                    with ui.row().classes('w-full items-center gap-2'):
                        self.input_ref['widget'] = (
                            ui.textarea(placeholder='请输入您的问题...')
                            .props('autofocus outlined dense')
                            .classes('flex-grow')
                            .on('keydown.enter', self._handle_message)
                        )
                        ui.button(icon='send', on_click=self._handle_message).props('round')
    
    async def _handle_message(self):
        """处理消息发送"""
        user_message = self.input_ref['widget'].value.strip()
        if not user_message:
            return
        self.input_ref['widget'].set_value('')
        
        # 删除欢迎消息
        if self.welcome_message_container:
            self.welcome_message_container.clear()
        
        # 用户消息
        await self._add_user_message(user_message)
        
        # Bot回复（这里可以集成实际的AI服务）
        await self._add_bot_message(user_message)
    
    async def _add_user_message(self, message: str):
        """添加用户消息"""
        with self.messages:
            with ui.row().classes('w-full justify-end'):
                user_avatar = static_manager.get_fallback_path(
                    static_manager.get_logo_path('user.svg'),
                    'https://robohash.org/user'
                )
                with ui.chat_message(
                    name='You',
                    avatar=user_avatar,  # 使用新的路径
                    sent=True
                ).classes('max-w-3xl w-full'):
                    ui.markdown(message, extras=['tables', 'mermaid', 'fenced-code-blocks'])
    
    async def _add_bot_message(self, user_message: str):
        """添加Bot消息（带打字机效果）"""
        with self.messages:
            robot_avatar = static_manager.get_fallback_path(
                static_manager.get_logo_path('robot_txt.svg'),
                'https://robohash.org/ui'
            )
            with ui.row().classes('w-full justify-start'):
                with ui.chat_message(
                    name='智能助手',
                    avatar=robot_avatar
                ).classes('max-w-3xl w-full'):
                    
                    # 先放一个不可见的 label，用来做打字机动画
                    stream_label = ui.label('').classes('whitespace-pre-wrap')
                    
                    # 这里应该调用实际的AI服务，现在用示例回复
                    full_response = await self._get_ai_response(user_message)
                    
                    # 打字机效果
                    typed = ''
                    for ch in full_response:
                        typed += ch
                        stream_label.text = typed
                        await asyncio.sleep(0.03)
                    
                    # 动画完成后，用真正的 Markdown 覆盖
                    stream_label.delete()
                    ui.markdown(typed, extras=['tables', 'mermaid', 'fenced-code-blocks'])
    
    async def _get_ai_response(self, user_message: str) -> str:
        """
        获取AI回复 - 这里应该集成实际的AI服务
        现在返回示例回复
        """
        # TODO: 这里应该集成实际的AI服务
        # 可以根据层级选择器的选中值来构造更精准的查询
        
        return f"您问的是：{user_message}\n\n这是一个示例回复。在实际应用中，这里会调用AI服务来生成智能回答。"
    
    def get_selected_hierarchy(self) -> dict:
        """
        获取层级选择器的选中值（如果需要与层级选择器联动）
        这个方法可以被外部调用来获取当前选中的层级信息
        """
        # 这里可以通过某种方式获取层级选择器的选中值
        # 具体实现取决于组件间如何通信
        return {
            'l1': None,
            'l2': None,
            'l3': None,
            'field': None
        }
    
def chat_page():
    # 添加全局样式和JavaScript，确保页面不出现滚动条并处理键盘事件
    ui.add_head_html('''
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
    </style>
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            // 监听所有textarea的keydown事件
            document.addEventListener('keydown', function(e) {
                if (e.target.tagName === 'TEXTAREA') {
                    if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault(); // 阻止默认的换行行为
                        // 触发自定义事件来发送消息
                        e.target.dispatchEvent(new CustomEvent('send-message'));
                    }
                    // 如果是Shift+Enter，不做任何处理，允许默认的换行行为
                }
            });
            
            // 自动滚动到底部的函数
            window.scrollToBottom = function() {
                setTimeout(function() {
                    const scrollArea = document.querySelector('.chat-scroll-area');
                    if (scrollArea) {
                        scrollArea.scrollTop = scrollArea.scrollHeight;
                    }
                }, 50); // 稍微延迟确保DOM更新完成
            };
        });
    </script>
    ''')
    
    # 主容器 - 使用水平布局
    with ui.row().classes('w-full h-full').style('overflow: hidden; height: calc(100vh - 120px); margin: 0; padding: 0;'):
        
        # 侧边栏 - 固定宽度
        with ui.column().classes('sidebar h-full').style('width: 280px; min-width: 280px;'):
            # 侧边栏标题
            with ui.row().classes('w-full p-4 border-b'):
                ui.icon('menu', size='md').classes('text-gray-600')
                ui.label('功能菜单').classes('text-lg font-semibold ml-2')
            
            # 侧边栏内容
            with ui.column().classes('w-full p-3'):
                # 添加按钮
                ui.button('添加按钮', icon='add').classes('w-full mb-3').props('outlined')
                
                # 设置expansion组件
                with ui.expansion('选择模型', icon='settings').classes('expansion-panel w-full'):
                    with ui.column().classes('p-2'):
                        continents = ["deepseek-chat","moonshot-v1-8k","Qwen32B"]
                        ui.select(options=continents, value='deepseek-chat', with_input=True,on_change=lambda e: ui.notify(e.value)).props('autofocus outlined dense')
                
                # 数据expansion组件
                with ui.expansion('提示辅助数据', icon='settings').classes('expansion-panel w-full'):
                    with ui.column().classes('p-2'):
                        switch = ui.switch('启用')
                        ui.select(options=[], with_input=True,on_change=lambda e: ui.notify(e.value)).props('autofocus outlined dense')
                        ui.select(options=[], with_input=True,on_change=lambda e: ui.notify(e.value)).props('autofocus outlined dense')
                        ui.select(options=[], with_input=True,on_change=lambda e: ui.notify(e.value)).props('autofocus outlined dense')
                        ui.select(options=[], with_input=True,on_change=lambda e: ui.notify(e.value)).props('autofocus outlined dense')
                
                # 历史聊天List
                ui.separator().classes('my-4')
                ui.label('历史聊天').classes('font-semibold mb-3')
                
                # 模拟历史聊天记录
                chat_history = [
                    '今天的天气如何？',
                    '帮我写一个Python函数',
                    '什么是机器学习？',
                    '推荐一些好看的电影',
                    '如何学习编程？',
                ]
                
                with ui.list().classes('w-full') as history_container:
                    for i, chat in enumerate(chat_history):
                        with ui.item(on_click=lambda: ui.notify('Selected contact 1')).classes('chat-history-item'):
                            with ui.item_section():
                                ui.item_label(f"{chat[:25]}..." if len(chat) > 25 else chat)
                                ui.item_label(f"2024-01-{i+1:02d}").props('caption')
        
        # 聊天区域 - 占据剩余空间
        with ui.column().classes('flex-grow h-full flex flex-col relative').style('overflow: hidden; min-width: 0;'):
            
            # 消息展示区域 - 占据剩余空间，可滚动，底部留出空间给输入框
            with ui.column().classes('flex-grow overflow-y-auto p-4 w-full rounded chat-scroll-area sidebar').style('scroll-behavior: smooth; min-height: 0; margin-bottom: 80px;') as scroll_area:
                messages = ui.column().classes('w-full')
                
                # 欢迎消息容器
                with ui.column().classes('flex-grow flex items-center justify-center w-full') as welcome_message_container:
                    ui.icon('chat', size='6rem').classes('text-blue-600')
                    ui.label('欢迎,使用一企一档智能问数!!!').classes('text-xl text-blue-600')
                    
            # 输入区域 - 固定在底部，距离底部10px
            with ui.row().classes('w-full items-center gap-2 p-3 rounded shadow-lg').style('position: absolute; bottom: 10px; left: 10px; right: 10px; z-index: 1000; margin: 0 auto; max-width: calc(100% - 20px);'):    
                # 提前声明可变对象，供内部嵌套函数读写
                input_ref = {'widget': None}

                async def handle_message(event=None):
                    user_message = input_ref['widget'].value.strip()
                    if not user_message:
                        return
                    input_ref['widget'].set_value('')
                    ui.notify(event)

                    # **关键改动：删除欢迎消息**
                    if welcome_message_container:
                        welcome_message_container.clear()

                    # 用户消息
                    with messages:
                        user_avatar = static_manager.get_fallback_path(
                            static_manager.get_logo_path('user.svg'),
                            'https://robohash.org/user')
                        with ui.chat_message(
                            name='您',
                            avatar=user_avatar,
                            sent=True
                        ).classes('w-full'):
                            ui.label(user_message).classes('whitespace-pre-wrap break-words')

                    # 添加用户消息后立即滚动到底部
                    ui.run_javascript('window.scrollToBottom()')

                    # 机器人消息
                    with messages:
                        robot_avatar = static_manager.get_fallback_path(
                                static_manager.get_logo_path('robot_txt.svg'),
                                'https://robohash.org/ui'
                        )
                        with ui.chat_message(
                            name='Bot',
                            avatar=robot_avatar
                        ).classes('w-full'):
                           
                            # 1. 先放一个不可见的 label，用来做打字机动画
                            stream_label = ui.label('').classes('whitespace-pre-wrap')

                            full = f"我收到了您的消息：{user_message}。这是一个智能回复示例。"  # 示例回复
                            typed = ''
                            for ch in full:
                                typed += ch
                                stream_label.text = typed
                                # 打字过程中也滚动到底部
                                ui.run_javascript('window.scrollToBottom()')
                                await asyncio.sleep(0.03)

                            # 2. 动画完成后，用真正的 Markdown 覆盖
                            stream_label.delete()
                            ui.markdown(typed, extras=['tables', 'mermaid', 'fenced-code-blocks']).classes('whitespace-pre-wrap break-words')

                    # 添加机器人消息后滚动到底部
                    ui.run_javascript('window.scrollToBottom()')

                # 输入框和发送按钮
                input_ref['widget'] = (
                    ui.textarea(placeholder='输入你的消息... (Enter发送，Shift+Enter换行)')
                    .props('autofocus outlined dense rounded rows=2')
                    .classes('flex-grow')
                    .on('send-message', handle_message)  # 监听自定义的send-message事件
                )
                ui.button(icon='send', on_click=handle_message).props('round')