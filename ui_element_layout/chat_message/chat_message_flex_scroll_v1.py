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
        /* 确保滚动区域样式正确 */
        .scroll-container {
            scroll-behavior: smooth;
        }
    </style>
    ''')
        
    # 使用flex布局，确保输入框能正确定位到底部
    with ui.column().classes('w-full h-full flex flex-col relative').style('overflow: hidden; height: calc(100vh - 20px); margin: 0; padding: 0;'):
        
        # 消息展示区域 - 占据剩余空间，可滚动，底部留出空间给输入框
        with ui.column().classes('flex-grow overflow-y-auto p-4 w-full rounded scroll-container').style('min-height: 0; margin-bottom: 80px;') as scroll_area:
            messages = ui.column().classes('w-full')
            
            # 欢迎消息容器
            with ui.column().classes('flex-grow flex items-center justify-center w-full') as welcome_message_container:
                ui.icon('chat', size='6rem').classes('text-blue-600')
                ui.label('欢迎,使用一企一档智能问数!!!').classes('text-xl text-blue-600')
                
        # 输入区域 - 固定在底部，距离底部10px
        with ui.row().classes('w-full items-center gap-2 p-3 rounded shadow-lg').style('position: absolute; bottom: 10px; left: 10px; right: 10px; z-index: 1000; margin: 0 auto; max-width: calc(100% - 20px);'):    
            # 提前声明可变对象，供内部嵌套函数读写
            input_ref = {'widget': None}

            async def scroll_to_bottom():
                """改进的滚动到底部函数"""
                try:
                    # 增加等待时间，确保DOM完全更新
                    await asyncio.sleep(0.1)
                    
                    # 多种方法尝试滚动，提高成功率
                    ui.run_javascript(f'''
                        // 方法1: 通过ID直接找到滚动容器
                        const scrollContainer = document.querySelector('[data-testid="{scroll_area.id}"]');
                        if (scrollContainer) {{
                            // 强制滚动到底部
                            scrollContainer.scrollTop = scrollContainer.scrollHeight;
                            
                            // 备用平滑滚动
                            setTimeout(() => {{
                                scrollContainer.scrollTo({{
                                    top: scrollContainer.scrollHeight,
                                    behavior: 'smooth'
                                }});
                            }}, 50);
                        }}
                        
                        // 方法2: 通过类名查找滚动容器
                        const scrollByClass = document.querySelector('.scroll-container');
                        if (scrollByClass) {{
                            scrollByClass.scrollTop = scrollByClass.scrollHeight;
                        }}
                        
                        // 方法3: 查找所有可能的滚动容器
                        const scrollables = document.querySelectorAll('[style*="overflow-y: auto"], .overflow-y-auto');
                        scrollables.forEach(el => {{
                            if (el.scrollHeight > el.clientHeight) {{
                                el.scrollTop = el.scrollHeight;
                            }}
                        }});
                    ''')
                    
                    # 再次延迟确保滚动生效
                    await asyncio.sleep(0.05)
                    
                except Exception as e:
                    print(f"滚动出错: {e}")

            async def force_scroll_to_bottom():
                """强制滚动到底部，多次尝试"""
                for i in range(3):  # 尝试3次
                    await scroll_to_bottom()
                    await asyncio.sleep(0.1)

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
                await force_scroll_to_bottom()

                # 机器人消息
                with messages:
                    with ui.chat_message(
                        name='Bot',
                        avatar='/static/robot.svg'
                    ).classes('w-full'):
                        # 1. 先放一个不可见的 label，用来做打字机动画
                        stream_label = ui.label('').classes('whitespace-pre-wrap')

                        full = f"这是对 '{user_message}' 的回复"  # 示例回复
                        typed = ''
                        for i, ch in enumerate(full):
                            typed += ch
                            stream_label.text = typed
                            # 打字过程中定期滚动
                            if i % 5 == 0:  # 每5个字符滚动一次
                                await scroll_to_bottom()
                            await asyncio.sleep(0.03)

                        # 2. 动画完成后，用真正的 Markdown 覆盖
                        stream_label.delete()
                        ui.markdown(typed, extras=['tables', 'mermaid', 'fenced-code-blocks'])

                # 添加第一条机器人消息后滚动
                await force_scroll_to_bottom()

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
                await force_scroll_to_bottom()

            def handle_keydown(e):
                """处理键盘事件，区分Enter和Shift+Enter"""
                # 如果按下Shift+Enter，允许换行（不做任何处理）
                if e.args.get('shiftKey', False):
                    return
                
                # 如果只按Enter，发送消息并阻止默认行为
                if e.args.get('key') == 'Enter':
                    # 使用 ui.timer 来异步调用 handle_message
                    ui.timer(0.01, handle_message, once=True)
                    return True # 阻止默认的换行行为

            # 输入框和发送按钮
            input_ref['widget'] = (
                ui.textarea(placeholder='输入你的消息...')
                .props('autofocus outlined dense rounded rows=2')
                .classes('flex-grow')
                .on('keydown', handle_keydown)
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