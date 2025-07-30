"""
聊天组件 - 类似Vue组件，可复用的聊天UI
"""
import asyncio
from nicegui import ui, app
from typing import Optional
from component import static_manager
import os
    
def chat_page():
    # 添加全局样式，保持原有样式并添加scroll_area优化
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
    ''')
    
    # 主容器 - 使用水平布局
    with ui.row().classes('w-full h-full').style('overflow: hidden; height: calc(100vh - 120px); margin: 0; padding: 0;'):   
        # 侧边栏 - 固定宽度
        with ui.column().classes('sidebar h-full').style('width: 280px; min-width: 280px;'):
            # 侧边栏标题
            with ui.row().classes('w-full p-4 border-b'):
                ui.icon('menu', size='md').classes('text-gray-600')
                ui.label('功能菜单').classes('text-lg font-semibold ml-2')
            
            # 侧边栏内容 - 完全按照原有结构
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
            
            # 核心改进：使用 ui.scroll_area 替代原来的 ui.column + overflow-y-auto
            with ui.scroll_area().classes('flex-grow p-4 w-full rounded ').style(
                'margin-bottom: 80px;'  # 为输入框留出空间
            ) as scroll_area:
                messages = ui.column().classes('w-full')
                
                # 欢迎消息容器
                with ui.column().classes('flex-grow flex items-center justify-center w-full') as welcome_message_container:
                    ui.icon('chat', size='6rem').classes('text-blue-600')
                    ui.label('欢迎,使用一企一档智能问数!!!').classes('text-xl text-blue-600')
                    
            # 输入区域 - 固定在底部，距离底部10px
            with ui.row().classes('w-full items-center gap-2 p-3 rounded ').style(
                'position: absolute; bottom: 10px; left: 10px; right: 10px; z-index: 1000; '
                'margin: 0 auto; max-width: calc(100% - 20px);'
            ):    
                # 提前声明可变对象，供内部嵌套函数读写
                input_ref = {'widget': None}

                async def scroll_to_bottom_smooth():
                    """平滑滚动到底部，使用更可靠的方法"""
                    try:
                        # 方法1: 使用 scroll_area 的内置方法，设置 percent > 1 确保滚动到底部
                        scroll_area.scroll_to(percent=1.1)
                        # 添加小延迟确保滚动完成
                        await asyncio.sleep(0.05)
                    except Exception as e:
                        print(f"滚动出错: {e}")

                async def handle_message(event=None):
                    user_message = input_ref['widget'].value.strip()
                    if not user_message:
                        return
                    input_ref['widget'].set_value('')

                    # 删除欢迎消息
                    if welcome_message_container:
                        welcome_message_container.clear()

                    # 用户消息
                    with messages:
                        with ui.chat_message(
                            name='您',
                            avatar='/static/robot.svg',
                            sent=True
                        ).classes('w-full'):
                            ui.label(user_message).classes('whitespace-pre-wrap break-words')

                    # 添加用户消息后立即滚动到底部
                    await scroll_to_bottom_smooth()

                    # 机器人消息
                    with messages:
                        with ui.chat_message(
                            name='AI',
                            avatar='/static/robot.svg'
                        ).classes('w-full'):
                            # 先放一个不可见的 label，用来做打字机动画
                            stream_label = ui.label('').classes('whitespace-pre-wrap')

                            full = f"我收到了您的消息：{user_message}。这是一个智能回复示例。"  # 示例回复
                            typed = ''
                            for ch in full:
                                typed += ch
                                stream_label.text = typed
                                # 打字过程中也滚动到底部
                                await scroll_to_bottom_smooth()
                                await asyncio.sleep(0.03)

                            # 完成回复后最终滚动
                            await scroll_to_bottom_smooth()

                # 输入框和发送按钮
                input_ref['widget'] = ui.textarea(
                    placeholder='请输入您的消息...(Enter发送，Shift+Enter换行)',
                    on_change=None
                ).classes('flex-grow').style(
                    'min-height: 44px; max-height: 120px; resize: none;'
                ).props('outlined dense rounded rows=3')

                # 监听自定义发送消息事件
                input_ref['widget'].on('send-message', handle_message)
                
                send_button = ui.button(
                    icon='send',
                    on_click=handle_message
                ).props('round dense ').classes('ml-2')

    # 添加键盘事件处理的 JavaScript
    ui.add_head_html('''
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
        });
    </script>
    ''')