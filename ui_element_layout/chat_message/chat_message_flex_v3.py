import asyncio
from nicegui import ui, app
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
static_files_dir = os.path.join(current_dir, 'static_assets')
app.add_static_files('/static', static_files_dir)

@ui.page('/')
def chat_page():
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
        /* Potentially add specific overrides for Quasar/NiceGUI chat message components */
        /* These are examples, you'll need to inspect your HTML to find the exact classes */
        .q-message-container .q-message-text {
            padding-bottom: 0px !important; /* Adjust if the text content itself has extra padding */
        }
        .q-chat-message__text { /* Or whatever the class for the text bubble content is */
            margin-bottom: 0 !important;
            padding-bottom: 0 !important;
        }
    </style>
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            document.addEventListener('keydown', function(e) {
                if (e.target.tagName === 'TEXTAREA') {
                    if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        e.target.dispatchEvent(new CustomEvent('send-message'));
                    }
                }
            });
            
            window.scrollToBottom = function() {
                setTimeout(function() {
                    const scrollArea = document.querySelector('.overflow-y-auto');
                    if (scrollArea) {
                        scrollArea.scrollTop = scrollArea.scrollHeight;
                    }
                }, 50);
            };
        });
    </script>
    ''')
        
    with ui.column().classes('w-full h-full flex flex-col relative').style('overflow: hidden; height: calc(100vh - 20px); margin: 0; padding: 0;'):
        
        # Message display area - flexible height, scrollable, with padding at the bottom for the input
        # Adjusted padding-bottom instead of margin-bottom
        with ui.column().classes('flex-grow overflow-y-auto p-4 w-full rounded ').style('scroll-behavior: smooth; min-height: 0; padding-bottom: 100px;') as scroll_area: # Adjust padding-bottom as needed
            messages = ui.column().classes('w-full')
            
            with ui.column().classes('flex-grow flex items-center justify-center w-full') as welcome_message_container:
                ui.icon('chat', size='6rem').classes('text-blue-600')
                ui.label('欢迎,使用一企一档智能问数!!!').classes('text-xl text-blue-600')
                
        # Input area - fixed at the bottom
        # Ensure its height is factored into the scroll area's padding-bottom
        with ui.row().classes('w-full items-center gap-2 p-3 rounded shadow-lg').style('position: absolute; bottom: 10px; left: 10px; right: 10px; z-index: 1000; margin: 0 auto; max-width: calc(100% - 20px);'):     
            input_ref = {'widget': None}

            async def handle_message(event=None):
                user_message = input_ref['widget'].value.strip()
                if not user_message:
                    return
                input_ref['widget'].set_value('')

                if welcome_message_container:
                    welcome_message_container.clear()

                with messages:
                    with ui.chat_message(
                        name='您',
                        avatar='/static/robot.svg',
                        sent=True
                    ).classes('w-full'): # Add .style('margin-bottom: 0;') if needed here
                        ui.markdown(user_message, extras=['fenced-code-blocks']).classes('whitespace-pre-wrap break-words') # Add .style('margin-bottom: 0;') if needed here
                ui.run_javascript('window.scrollToBottom()')

                with messages:
                    with ui.chat_message(
                        name='Bot',
                        avatar='/static/robot.svg'
                    ).classes('w-full'): # Add .style('margin-bottom: 0;') if needed here
                        stream_label = ui.label('').classes('whitespace-pre-wrap')

                        full = f"{user_message}"
                        typed = ''
                        for ch in full:
                            typed += ch
                            stream_label.text = typed
                            ui.run_javascript('window.scrollToBottom()')
                            await asyncio.sleep(0.03)

                        stream_label.delete()
                        ui.markdown(typed, extras=['tables', 'mermaid', 'fenced-code-blocks']).classes('whitespace-pre-wrap break-words') # Add .style('margin-bottom: 0;') if needed here

                ui.run_javascript('window.scrollToBottom()')

                with messages:
                    with ui.chat_message(
                        name='Bot',
                        text_html=True,
                        avatar='/static/robot.svg'
                    ).classes('w-full'): # Add .style('margin-bottom: 0;') if needed here
                        ui.markdown(
                            f"Echo: {user_message}",
                            extras=['tables', 'mermaid', 'fenced-code-blocks']
                        ).classes('whitespace-pre-wrap break-words') # Add .style('margin-bottom: 0;') if needed here
                ui.run_javascript('window.scrollToBottom()')

            input_ref['widget'] = (
                ui.textarea(placeholder='输入你的消息... (Enter发送，Shift+Enter换行)')
                .props('autofocus outlined dense rounded rows=3')
                .classes('flex-grow')
                .on('send-message', handle_message)
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