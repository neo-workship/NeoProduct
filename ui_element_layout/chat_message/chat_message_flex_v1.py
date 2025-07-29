import asyncio
from nicegui import ui, app
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
static_files_dir = os.path.join(current_dir, 'static_assets')
app.add_static_files('/static', static_files_dir)

@ui.page('/')
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
    with ui.column().classes('w-full h-full flex flex-col relative').style('overflow: hidden; height: calc(100vh - 20px); margin: 0; padding: 0;'):
        
        # 消息展示区域 - 占据剩余空间，可滚动，底部留出空间给输入框
        with ui.column().classes('flex-grow overflow-y-auto p-4 w-full rounded ').style('scroll-behavior: smooth; min-height: 0; margin-bottom: 80px;') as scroll_area:
            messages = ui.column().classes('w-full')
            
            # 欢迎消息容器
            with ui.column().classes('flex-grow flex items-center justify-center w-full') as welcome_message_container:
                ui.icon('chat', size='6rem').classes('text-blue-600')
                ui.label('欢迎,使用一企一档智能问数!!!').classes('text-xl text-blue-600')
                
        # 输入区域 - 固定在底部，距离底部10px
        with ui.row().classes('w-full items-center gap-2 p-3 rounded  shadow-lg').style('position: absolute; bottom: 10px; left: 10px; right: 10px; z-index: 1000; margin: 0 auto; max-width: calc(100% - 20px);'):    
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
                        avatar='/static/robot.svg',
                        sent=True
                    ).classes('w-full'):
                        ui.markdown(user_message, extras=['tables', 'mermaid', 'fenced-code-blocks'])

                # 添加用户消息后立即滚动
                await scroll_to_bottom()

                # 机器人消息
                with messages:
                    with ui.chat_message(
                        name='Bot',
                        avatar='/static/robot.svg'
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
                        avatar='/static/robot.svg'
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

if __name__ in {"__main__", "__mp_main__"}:
    ui.run(
        title='Chat Demo',
        host='0.0.0.0',
        port=8081,
        reload=True,
        show=True
    )