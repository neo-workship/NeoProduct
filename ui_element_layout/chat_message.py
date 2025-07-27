# from nicegui import ui
# import asyncio

# @ui.page('/')
# def chat_page():
#     messages = ui.column().classes("w-full")

#     async def handle_message():
#         user_message = message_input.value
#         if not user_message:
#             return

#         message_input.set_value('')

#         # Display the user's message on the RIGHT side, with avatar also on the right
#         # Removing 'avatar_position' as it's not a valid argument.
#         with messages:
#             ui.chat_message(user_message, name='You', avatar='https://robohash.org/ui', sent=False).classes("w-full items-end") # <-- Removed avatar_position

#         # Simulate streaming the response back on the LEFT side (default)
#         with messages:
#             bot_message = ui.chat_message(name='Bot', avatar='https://robohash.org/ui')
#             with bot_message:
#                 response_label = ui.label('')

#             full_response = f"You just said: {user_message}"
#             for i in range(len(full_response)):
#                 response_label.text = full_response[:i+1]
#                 await asyncio.sleep(0.05) # Simulate typing delay

#     # The input field for the user to type messages
#     message_input = ui.textarea(placeholder='Type your message here...') \
#         .props('autofocus') \
#         .classes('w-full') \
#         .on('keydown.enter', handle_message).classes("w-full h-10")

# ui.run()

import asyncio
from nicegui import ui

@ui.page('/')
def chat_page():
    messages = ui.column().classes('w-full flex-grow overflow-y-auto p-4')

    # 提前声明可变对象，供内部嵌套函数读写
    input_ref = {'widget': None}

    async def handle_message():
        user_message = input_ref['widget'].value.strip()
        if not user_message:
            return
        input_ref['widget'].set_value('')

        # 用户消息
        with messages:
            with ui.chat_message(
                            name='You',
                            avatar='https://robohash.org/ui',
                            sent=True).classes('w-full items-end'):
            
                ui.markdown(user_message , extras=['tables','mermaid','fenced-code-blocks']).classes('w-full items-end text-lg')

        # 机器人消息
        with messages:
            with ui.chat_message(name='Bot',
                                      avatar='https://robohash.org/ui'):
                
              
               # 1. 先放一个不可见的 label，用来做打字机动画
                stream_label = ui.label('').classes('whitespace-pre-wrap')

                full = f"{user_message}"
                typed = ''
                for ch in full:
                    typed += ch
                    stream_label.text = typed
                    await asyncio.sleep(0.03)

                # 2. 动画完成后，用真正的 Markdown 覆盖
                stream_label.delete()                       # 移除 label
                ui.markdown(typed, extras=['tables', 'mermaid','fenced-code-blocks'])
        
        with messages:
            with ui.chat_message(
                            name='Bot',
                            text_html=True,
                            avatar='https://robohash.org/ui'):
                ui.markdown(f"{user_message}", extras=['tables','mermaid','fenced-code-blocks']).classes('w-full items-start')

    # 底部输入区
    with ui.footer().classes('bg-white'), ui.row().classes('w-full items-center p-2 gap-2'):
        input_ref['widget'] = (
            ui.textarea(placeholder='Type your message here...')
            .props('autofocus outlined dense')
            .classes('flex-grow')
            .on('keydown.enter', handle_message)   # 现在 handle_message 已定义
        )
        ui.button(icon='send', on_click=handle_message)

ui.run(title='Chat Demo', reload=False, dark=False)