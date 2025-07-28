from nicegui import ui,app
import asyncio
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
static_files_dir = os.path.join(current_dir, 'static_assets')
app.add_static_files('/static', static_files_dir)

@ui.page('/')
def page_layout():
   
    with ui.header(elevated=True).style('background-color: #3874c8').classes('items-center justify-between'):
        ui.label('HEADER')
    with ui.left_drawer(top_corner=True, bottom_corner=True).style('background-color: #d7e3f4'):
        ui.label('LEFT DRAWER')
    # with ui.footer().style('background-color: #3874c8'):
    #     ui.label('FOOTER')
    ohter_page()
    ui.separator()
    chat_page_grid()

def ohter_page():
    continents = [
    'Asia',
    'Africa',
    'Antarctica',
    'Europe',
    'Oceania',
    'North America',
    'South America',
    ]
    with ui.column():
        ui.select(options=continents, with_input=True,
            on_change=lambda e: ui.notify(e.value)).classes('w-40')

def chat_page_grid():
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
    
    # 使用网格布局，明确定义行高
    with ui.element('div').style(
        'display:grid;grid-template-rows:1fr auto;'
        'height:calc(100vh - 150px);'   # 64px ≈ header 高度，可按实际改动, header、left_drawer 都占高度，导致 100vh 被它们挤掉一部分，于是 grid 的 100vh 被撑破，
        'width:100%;overflow:hidden;margin:0;padding:0;'
    ):
        
        # 消息展示区域 - 第一行，占据剩余空间
        with ui.column().classes('overflow-y-auto p-4 w-full rounded').style('scroll-behavior: smooth; min-height: 0;') as scroll_area:
            messages = ui.column().classes('w-full')
            
            # 欢迎消息容器
            welcome_message_container = ui.column().classes('flex items-center justify-center w-full').style('min-height:0; flex:1 1 0')
            with welcome_message_container:
                ui.icon('chat', size='6rem').classes('text-blue-600')
                ui.label('欢迎,使用一企一档智能问数!!!').classes('text-xl text-blue-600')

        # 输入区域 - 第二行，固定高度，距离底部10px
        with ui.element('div').style('padding: 10px;'):
            with ui.row().classes('w-full items-center gap-2 p-3 rounded shadow-lg'):
                # 提前声明可变对象，供内部嵌套函数读写
                input_ref = {'widget': None}

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
                                await asyncio.sleep(0.03)

                            # 2. 动画完成后，用真正的 Markdown 覆盖
                            stream_label.delete()
                            ui.markdown(typed, extras=['tables', 'mermaid', 'fenced-code-blocks'])
           
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

                    # 滚动到底部 - 每次添加消息后都滚动
                    await asyncio.sleep(0.1)

                # 输入框和发送按钮
                input_ref['widget'] = (
                    ui.textarea(placeholder='输入你的消息...')
                    .props('autofocus outlined dense rounded rows=2')
                    .classes('flex-grow bg-white')
                    .on('keydown.enter', handle_message)
                )
                ui.button(icon='send', on_click=handle_message).props('round')

if __name__ in {"__main__", "__mp_main__"}:
    ui.run(
        title='弹性布局页面',
        host='0.0.0.0',
        port=8086,
        reload=True,
        show=True
    )