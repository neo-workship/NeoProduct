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
        .sidebar {
            border-right: 1px solid #e5e7eb;
            background-color: #f9fafb;
        }
        .sidebar-divider {
            height: 1px;
            background-color: #e5e7eb;
            margin: 10px 0;
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
                    const scrollArea = document.querySelector('.overflow-y-auto');
                    if (scrollArea) {
                        scrollArea.scrollTop = scrollArea.scrollHeight;
                    }
                }, 50); // 稍微延迟确保DOM更新完成
            };
        });
    </script>
    ''')
    
    # 使用水平布局：侧边栏 + 主聊天区域
    with ui.element('div').style(
        'display:flex;'
        'height:calc(100vh - 20px);'
        'width:100%;overflow:hidden;margin:0;padding:0;'
    ):
        
        # 左侧边栏
        with ui.element('div').classes('sidebar').style(
            'width:280px;'
            'min-width:280px;'
            'height:100%;'
            'overflow-y:auto;'
            'padding:16px;'
        ):
            with ui.row().classes('w-full p-4 border-b'):
                ui.icon('menu', size='md').classes('text-gray-600')
                ui.label('功能菜单').classes('text-lg font-semibold ml-2')
            # 添加按钮
            ui.button('添加按钮', icon='add').classes('w-full mb-4').props('color=primary')
            
            # 设置expansion组件
            with ui.expansion('设置expansion组件', icon='settings').classes('w-full mb-4'):
                ui.select(
                    ['选项1', '选项2', '选项3', '选项4'], 
                    label='配置选择',
                    value='选项1'
                ).classes('w-full')
            
            # 数据expansion组件
            with ui.expansion('数据expansion组件', icon='data_usage').classes('w-full mb-4'):
                ui.select(
                    ['数据源A', '数据源B', '数据源C'], 
                    label='数据源',
                    value='数据源A'
                ).classes('w-full mb-2')
                
                ui.select(
                    ['表1', '表2', '表3', '表4'], 
                    label='数据表',
                    value='表1'
                ).classes('w-full mb-2')
                
                ui.select(
                    ['字段1', '字段2', '字段3'], 
                    label='字段选择',
                    value='字段1'
                ).classes('w-full mb-2')
                
                ui.select(
                    ['升序', '降序'], 
                    label='排序方式',
                    value='升序'
                ).classes('w-full')
            
            # 分隔线
            ui.separator().classes('my-4')
            
            # 历史聊天List
            ui.label('历史聊天List').classes('text-lg font-semibold mb-3')
            
            # 历史聊天记录
            chat_history = [
                "今天天气如何？",
                "帮我分析数据",
                "什么是机器学习？",
                "如何优化代码？",
                "项目进度报告"
            ]
            
            with ui.list().classes('w-full') as history_container:
                for i, chat in enumerate(chat_history):
                    with ui.item(on_click=lambda: ui.notify('Selected contact 1')).classes('chat-history-item'):
                        with ui.item_section():
                            ui.item_label(f"{chat[:25]}..." if len(chat) > 25 else chat)
                            ui.item_label(f"2024-01-{i+1:02d}").props('caption')
        
        
        # 主聊天区域 - 保持原有布局
        with ui.element('div').style(
            'display:grid;grid-template-rows:1fr auto;'
            'flex:1;'
            'height:100%;'
            'overflow:hidden;margin:0;padding:0;'
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
                                processed_message = "\n".join([line for line in user_message.splitlines() if line.strip()])
                                ui.markdown(processed_message, extras=['tables', 'mermaid', 'fenced-code-blocks'])
                        ui.run_javascript('window.scrollToBottom()')
                        
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
                                processed_message = "\n".join([line for line in typed.splitlines() if line.strip()])
                                ui.markdown(processed_message, extras=['tables', 'mermaid', 'fenced-code-blocks'])

                        ui.run_javascript('window.scrollToBottom()')
                        
                        # 第二条机器人消息
                        with messages:
                            with ui.chat_message(
                                name='Bot',
                                text_html=True,
                                avatar='https://robohash.org/ui'
                            ).classes('w-full'):
                                processed_message = "\n".join([line for line in user_message.splitlines() if line.strip()])
                                ui.markdown(
                                    f"Echo: {processed_message}",
                                    extras=['tables', 'mermaid', 'fenced-code-blocks']
                                )

                        # 滚动到底部 - 每次添加消息后都滚动
                        await asyncio.sleep(0.1)
                        
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
        title='Chat Demo',
        host='0.0.0.0',
        port=8081,
        reload=True,
        show=True
    )