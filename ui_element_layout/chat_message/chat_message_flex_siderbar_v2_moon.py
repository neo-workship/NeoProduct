import asyncio
from nicegui import ui, app
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
static_files_dir = os.path.join(current_dir, 'static_assets')
app.add_static_files('/static', static_files_dir)

@ui.page('/')
def chat_page():
    # 仅保留必要的全局样式，去掉 scrollToBottom 的 JS
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
            background-color: #f9fafb;
            overflow-y: auto;
        }
        .sidebar::-webkit-scrollbar { width: 6px; }
        .sidebar::-webkit-scrollbar-track { background: transparent; }
        .sidebar::-webkit-scrollbar-thumb { background-color: #d1d5db; border-radius: 3px; }
        .sidebar::-webkit-scrollbar-thumb:hover { background-color: #9ca3af; }
        .chat-history-item { cursor: pointer; transition: background-color 0.2s; }
        .chat-history-item:hover { background-color: #e5e7eb; }
        .expansion-panel { margin-bottom: 8px; }
    </style>
    <script>
        document.addEventListener('DOMContentLoaded', function () {
            // 监听所有 textarea 的 Enter 发送
            document.addEventListener('keydown', function (e) {
                if (e.target.tagName === 'TEXTAREA') {
                    if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        e.target.dispatchEvent(new CustomEvent('send-message'));
                    }
                }
            });
        });
    </script>
    ''')

    # 主容器
    with ui.row().classes('w-full h-full').style('overflow: hidden; height: calc(100vh - 20px); margin: 0; padding: 0;'):
        # 侧边栏
        with ui.column().classes('sidebar h-full').style('width: 280px; min-width: 280px;'):
            with ui.row().classes('w-full p-4 border-b'):
                ui.icon('menu', size='md').classes('text-gray-600')
                ui.label('功能菜单').classes('text-lg font-semibold ml-2')

            with ui.column().classes('w-full p-3'):
                ui.button('添加按钮', icon='add').classes('w-full mb-3').props('outlined')

                with ui.expansion('选择模型', icon='settings').classes('expansion-panel w-full'):
                    with ui.column().classes('p-2'):
                        models = ["deepseek-chat", "moonshot-v1-8k", "Qwen32B"]
                        ui.select(options=models, value='deepseek-chat', with_input=True,
                                  on_change=lambda e: ui.notify(e.value)).props('autofocus outlined dense')

                with ui.expansion('提示辅助数据', icon='settings').classes('expansion-panel w-full'):
                    with ui.column().classes('p-2'):
                        ui.switch('启用')
                        for _ in range(4):
                            ui.select(options=[], with_input=True,
                                      on_change=lambda e: ui.notify(e.value)).props('autofocus outlined dense')

                ui.separator().classes('my-4')
                ui.label('历史聊天').classes('font-semibold mb-3')

                chat_history = [
                    '今天的天气如何？',
                    '帮我写一个Python函数',
                    '什么是机器学习？',
                    '推荐一些好看的电影',
                    '如何学习编程？',
                ]
                with ui.list().classes('w-full'):
                    for i, chat in enumerate(chat_history):
                        with ui.item(on_click=lambda: ui.notify('Selected contact')).classes('chat-history-item'):
                            with ui.item_section():
                                ui.item_label(f"{chat[:25]}..." if len(chat) > 25 else chat)
                                ui.item_label(f"2024-01-{i+1:02d}").props('caption')

        # 聊天区域
        with ui.column().classes('flex-grow h-full flex flex-col relative').style('overflow: hidden; min-width: 0;'):
            # 用 ui.scroll_area 替换原来的手动滚动 column
            with ui.scroll_area().classes('flex-grow p-4').style('padding: 16px 16px 80px 16px') as scroll_area:
                messages = ui.column().classes('w-full')
                # 欢迎信息
                with ui.column().classes('flex-grow flex items-center justify-center w-full') as welcome_message_container:
                    ui.icon('chat', size='6rem').classes('text-blue-600')
                    ui.label('欢迎,使用一企一档智能问数!!!').classes('text-xl text-blue-600')

            # 固定在底部的输入框
            with ui.row().classes('w-full items-center gap-2 p-3 rounded shadow-lg').style(
                'position: absolute; bottom: 10px; left: 10px; right: 10px; z-index: 1000; margin: 0 auto; max-width: calc(100% - 20px);'
            ):
                input_ref = {'widget': None}

                async def handle_message(event=None):
                    user_message = input_ref['widget'].value.strip()
                    if not user_message:
                        return
                    input_ref['widget'].set_value('')

                    # 隐藏欢迎信息
                    if welcome_message_container:
                        welcome_message_container.clear()

                    # 用户消息
                    with messages:
                        with ui.chat_message(name='您', avatar='/static/robot.svg', sent=True).classes('w-full'):
                            ui.label(user_message).classes('whitespace-pre-wrap break-words')

                    scroll_area.scroll_to(percent=100, duration=0.2)  # 滚动到底部

                    # 机器人消息
                    with messages:
                        with ui.chat_message(name='Bot', avatar='/static/robot.svg').classes('w-full'):
                            stream_label = ui.label('').classes('whitespace-pre-wrap')
                            full = f"我收到了您的消息：{user_message}。这是一个智能回复示例。"
                            typed = ''
                            for ch in full:
                                typed += ch
                                stream_label.text = typed
                                scroll_area.scroll_to(percent=100, duration=0.1)
                                await asyncio.sleep(0.03)
                            stream_label.delete()
                            ui.markdown(typed, extras=['tables', 'mermaid', 'fenced-code-blocks']).classes(
                                'whitespace-pre-wrap break-words'
                            )

                    scroll_area.scroll_to(percent=100, duration=0.2)

                input_ref['widget'] = (
                    ui.textarea(placeholder='输入你的消息... (Enter发送，Shift+Enter换行)')
                    .props('autofocus outlined dense rounded rows=3')
                    .classes('flex-grow')
                    .on('send-message', handle_message)
                )
                ui.button(icon='send', on_click=handle_message).props('round')

if __name__ in {"__main__", "__mp_main__"}:
    ui.run(
        title='Chat Demo with Sidebar',
        host='0.0.0.0',
        port=8082,
        reload=True,
        show=True
    )