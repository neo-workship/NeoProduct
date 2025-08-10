from nicegui import ui
import time
@ui.page("/")
def main():
    with ui.chat_message(name='test').classes('w-full'):
        with ui.column().classes('w-full bg-[#81c784] border-0 shadow-none rounded-none') as content:
            ui.label('Lorem ipsum dolor sit amet, consectetur adipiscing elit, ...')
            columns = [
                {'name': 'name', 'label': 'Name', 'field': 'name', 'required': True, 'align': 'left'},
                {'name': 'age', 'label': 'Age', 'field': 'age', 'sortable': True},
            ]
            rows = [
                {'name': 'Alice', 'age': 18},
                {'name': 'Bob', 'age': 21},
                {'name': 'Carol'},
            ]
            ui.table(columns=columns, rows=rows, row_key='name').classes('w-full bg-[#81c784] border-0 shadow-none rounded-none')
            ui.button("hello").classes('border-0 shadow-none rounded-none')

    with content:
        ui.label("hello")

@ui.page("/neo")
def test():
    def show_reply():
        with content:
            reply_label = ui.label("hello")

    with ui.chat_message(name='test').classes('w-full'):
        with ui.column().classes('w-full') as content:
            think_expansion = ui.expansion(
                    '💭 AI思考过程', 
                    icon='psychology'
                ).classes('w-full mb-2')
            with think_expansion:
                think_label = ui.label('hello').classes('whitespace-pre-wrap text-sm text-gray-600 bg-gray-50 p-2 rounded')                     
        
    ui.button("check",on_click=lambda: show_reply())

if __name__ in {"__main__", "__mp_main__"}:
    ui.run(
        title='可下载表格',
        host='0.0.0.0',
        port=8082,
        reload=True,
        show=True
    )