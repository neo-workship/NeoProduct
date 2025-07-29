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
    enterprise_archive_content()

def enterprise_archive_content():
    """企业档案主内容"""
    
    with ui.splitter(value=10).classes('w-full h-full') as splitter:
        with splitter.before:
            with ui.tabs().props('vertical') as tabs:
                ai_query = ui.tab('智能问数', icon='tips_and_updates')
                data_operator = ui.tab('数据操作', icon='precision_manufacturing')
                data_sync = ui.tab('数据更新', icon='sync')
                setting = ui.tab('配置数据', icon='build_circle')
        
        with splitter.after:
            with ui.tab_panels(tabs, value=ai_query).props('vertical').classes('w-full h-full'):    
                with ui.tab_panel(ai_query).classes('w-full'):
                    chat_page()
                with ui.tab_panel(data_operator).classes('w-full'):
                    ohter_page()
                with ui.tab_panel(data_sync).classes('w-full'):
                    chat_page()
                with ui.tab_panel(setting).classes('w-full'):
                    ohter_page()

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
    with ui.row():
        ui.select(options=continents, with_input=True,label='comma-separated',
            on_change=lambda e: ui.notify(e.value)).props('dense  input-style="height: 20px; line-height: 20px"')
        ui.select(options=continents, with_input=True,label='comma-separated',
            on_change=lambda e: ui.notify(e.value)).props('dense outlined input-style="height: 20px; line-height: 20px"')
        ui.select(options=continents, with_input=True,label='comma-separated',
            on_change=lambda e: ui.notify(e.value)).props('dense outlined input-style="height: 20px; line-height: 20px"')
        ui.select(options=continents, with_input=True,label='comma-separated',
            on_change=lambda e: ui.notify(e.value)).props('dense outlined input-style="height: 20px; line-height: 20px"')
    
        # ui.select(options=continents, with_input=True,
        #     on_change=lambda e: ui.notify(e.value)).props('outlined')

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
            border-right: 1px solid #e5e7eb;
            background-color: #f9fafb;
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
    with ui.row().classes('w-full h-full').style('overflow: hidden; height: calc(100vh - 20px); margin: 0; padding: 0;'):
        
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

                    # **关键改动：删除欢迎消息**
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
                    ui.run_javascript('window.scrollToBottom()')

                    # 机器人消息
                    with messages:
                        with ui.chat_message(
                            name='Bot',
                            avatar='/static/robot.svg'
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
                    .props('autofocus outlined dense rounded rows=3')
                    .classes('flex-grow')
                    .on('send-message', handle_message)  # 监听自定义的send-message事件
                )
                ui.button(icon='send', on_click=handle_message).props('round')

if __name__ in {"__main__", "__mp_main__"}:
    ui.run(
        title='弹性布局页面',
        host='0.0.0.0',
        port=8086,
        reload=True,
        prod_js=False,
        show=True
    )