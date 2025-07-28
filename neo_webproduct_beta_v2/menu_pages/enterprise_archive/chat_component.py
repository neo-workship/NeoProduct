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
                with ui.row().classes('w-full p-4 border-t bg-white').style('min-height: 80px;'):
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
    # 添加全局样式，确保页面不出现滚动条
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
    </style>
    ''')
    
    # 使用flex布局，确保输入框能正确定位到底部
    with ui.column().classes('w-full h-full flex flex-col relative').style('overflow: hidden; height: calc(100vh - 300px); margin: 0; padding: 0;'):
        
        # 消息展示区域 - 占据剩余空间，可滚动，底部留出空间给输入框
        with ui.column().classes('flex-grow overflow-y-auto p-4 w-full rounded').style('scroll-behavior: smooth; min-height: 0; margin-bottom: 80px;') as scroll_area:
            messages = ui.column().classes('w-full')
            
            # 欢迎消息容器
            with ui.column().classes('flex-grow flex items-center justify-center w-full') as welcome_message_container:
                ui.icon('chat', size='6rem').classes('text-blue-600')
                ui.label('欢迎,使用一企一档智能问数!!!').classes('text-xl text-blue-600')
                

        # 输入区域 - 固定在底部，距离底部10px
        with ui.row().classes('w-full items-center gap-2 p-3 rounded bg-white shadow-lg').style('position: absolute; bottom: 10px; left: 10px; right: 10px; z-index: 1000; margin: 0 auto; max-width: calc(100% - 20px);'):    
            # 提前声明可变对象，供内部嵌套函数读写
            input_ref = {'widget': None}

            async def scroll_to_bottom():
                """强制滚动到底部的函数"""
                try:
                    await asyncio.sleep(0.05)
                    # 使用JavaScript直接操作，最可靠的方法
                    ui.run_javascript(f'''
                        const element = document.querySelector('[data-testid="{scroll_area.id}"]');
                        if (element) {{
                            element.scrollTop = element.scrollHeight;
                            element.scrollTo({{
                                top: element.scrollHeight,
                                behavior: 'smooth'
                            }});
                        }}
                    ''')
                except Exception as e:
                    print(f"滚动出错: {e}")

            async def handle_message():
                user_message = input_ref['widget'].value
                if not user_message:
                    return
                input_ref['widget'].set_value('')

                # **关键改动：删除欢迎消息**
                if welcome_message_container:
                    welcome_message_container.clear()

                # 用户消息
                with messages:
                    with ui.chat_message(
                        name='You',
                        avatar='https://robohash.org/ui',
                        sent=True
                    ).classes('w-full'):
                        ui.markdown(user_message, extras=['tables', 'mermaid', 'fenced-code-blocks'])

                # 添加用户消息后立即滚动
                await scroll_to_bottom()

                # 机器人消息
                with messages:
                    with ui.chat_message(
                        name='Bot',
                        avatar='https://robohash.org/ui'
                    ).classes('w-full'):
                        # 1. 先放一个不可见的 label，用来做打字机动画
                        stream_label = ui.label('').classes('whitespace-pre-wrap')

                        full = f"{user_message}"  # 示例回复
                        typed = ''
                        for ch in full:
                            typed += ch
                            stream_label.text = typed
                            # 打字过程中也滚动
                            if len(typed) % 10 == 0:  # 每10个字符滚动一次
                                await scroll_to_bottom()
                            await asyncio.sleep(0.03)

                        # 2. 动画完成后，用真正的 Markdown 覆盖
                        stream_label.delete()
                        ui.markdown(typed, extras=['tables', 'mermaid', 'fenced-code-blocks'])

                # 添加第一条机器人消息后滚动
                await scroll_to_bottom()

                # 第二条机器人消息
                with messages:
                    with ui.chat_message(
                        name='Bot',
                        text_html=True,
                        avatar='https://robohash.org/ui'
                    ).classes('w-full'):
                        ui.markdown(
                            f"Echo: {user_message}",
                            extras=['tables', 'mermaid', 'fenced-code-blocks']
                        )

                # 最终滚动到底部
                await scroll_to_bottom()

            # 输入框和发送按钮
            input_ref['widget'] = (
                ui.textarea(placeholder='输入你的消息...')
                .props('autofocus outlined dense rounded rows=2')
                .classes('flex-grow')
                .on('keydown.enter', handle_message)
            )
            ui.button(icon='send', on_click=handle_message).props('round')