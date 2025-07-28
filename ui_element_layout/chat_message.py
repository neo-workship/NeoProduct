import asyncio
from nicegui import ui,app
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
static_files_dir = os.path.join(current_dir, 'static_assets')
app.add_static_files('/static', static_files_dir)

@ui.page('/')
def chat_page():
    # ui.add_head_html('''
    #     <style>
    #     /* === 用户消息（sent） === */
    #     /* 气泡整体背景 */
    #     .q-message-sent .q-message-container {
    #         background-color: #1976d2 !important; 
    #     }
    #     /* 文字块背景（去掉 Quasar 自带的白色） */
    #     .q-message-sent .q-message-text,
    #     .q-message-sent .q-message-text-content {
    #         background: transparent !important;
    #         color: #ffffff;
    #     }

    #     /* === Bot 消息（received） === */
    #     .q-message-received .q-message-container {
    #         background-color: #e0e0e0 !important;   /* 灰色 */
    #     }
    #     .q-message-received .q-message-text,
    #     .q-message-received .q-message-text-content {
    #         background: transparent !important;
    #         color: #000000;
    #     }
    #     </style>
    # ''')
    
    # 聊天消息区域 - 可滚动，占据剩余空间，底部留出输入框空间
    messages = ui.column().classes('flex-grow overflow-y-auto p-4 w-full mb-20').style('scroll-behavior: smooth;')

    # 欢迎消息容器
    # 初始时，我们会在这里放置欢迎信息
    welcome_message_container = ui.column().classes('absolute-center items-center')
    with welcome_message_container:
        ui.icon('chat', size='6rem').classes('text-gray-400')
        ui.label('Welcome! Start chatting by typing a message below.').classes('text-xl text-gray-600')

    # 提前声明可变对象，供内部嵌套函数读写
    input_ref = {'widget': None}

    async def handle_message():
        user_message = input_ref['widget'].value#.strip()
        if not user_message:
            return
        input_ref['widget'].set_value('')

        # **关键改动：删除欢迎消息**
        # 在发送第一条消息时，删除欢迎消息容器中的所有元素
        if welcome_message_container:
            welcome_message_container.clear()
            # 也可以选择删除整个容器，但清除内容更灵活
            # welcome_message_container.delete()

        # 用户消息 - 限制宽度并居中
        with messages:
            with ui.row().classes('w-full justify-center'):
                with ui.chat_message(
                                name='You',
                                avatar='/static/robot.svg',
                                sent=True).classes('max-w-3xl w-full'):

                    ui.markdown(user_message, extras=['tables','mermaid','fenced-code-blocks'])#.classes('text-lg')

        # 机器人消息 - 限制宽度并居中
        with messages:
            with ui.row().classes('w-full justify-center'):
                with ui.chat_message(name='Bot',
                                          avatar='https://robohash.org/ui').classes('max-w-3xl w-full'):

                    # 1. 先放一个不可见的 label，用来做打字机动画
                    stream_label = ui.label('').classes('whitespace-pre-wrap')

                    full = f"{user_message}" # 示例回复，实际应用中会是LLM的回复
                    typed = ''
                    for ch in full:
                        typed += ch
                        stream_label.text = typed
                        await asyncio.sleep(0.03)

                    # 2. 动画完成后，用真正的 Markdown 覆盖
                    stream_label.delete()                       # 移除 label
                    ui.markdown(typed, extras=['tables', 'mermaid','fenced-code-blocks'])

        # 第二条机器人消息 (可选，根据您的需求决定是否保留)
        with messages:
            with ui.row().classes('w-full justify-center'):
                with ui.chat_message(
                                name='Bot',
                                text_html=True,
                                avatar='https://robohash.org/ui').classes('max-w-3xl w-full'):
                    ui.markdown(f"Echo: {user_message}", extras=['tables','mermaid','fenced-code-blocks'])


    # 底部输入区 - 固定在底部，居中，限制宽度
    with ui.footer().classes('bg-white border-t'):
        with ui.row().classes('w-full justify-center p-4'):
            with ui.row().classes('max-w-4xl w-full items-center gap-2'):
                input_ref['widget'] = (
                    ui.textarea(placeholder='Type your message here...')
                    .props('autofocus outlined dense')
                    .classes('flex-grow')
                    .on('keydown.enter', handle_message)
                )
                ui.button(icon='send', on_click=handle_message).props('round')

if __name__ in {"__main__", "__mp_main__"}:
    ui.run(
        title='Chat Demo',
        host='0.0.0.0',
        port=8081,
        reload=True,
        show=True
    )