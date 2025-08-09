from nicegui import ui
import io


@ui.page("/")
def main():
    table_data = [
        {'name': 'Alice', 'age': 30, 'city': 'New York'},
        {'name': 'Bob', 'age': 24, 'city': 'London'},
        {'name': 'Charlie', 'age': 35, 'city': 'Paris'},
    ]

    # Create the ui.table
    table = ui.table(columns=[
        {'name': 'name', 'label': 'Name', 'field': 'name'},
        {'name': 'age', 'label': 'Age', 'field': 'age'},
        {'name': 'city', 'label': 'City', 'field': 'city'},
    ], rows=table_data)

    # Function to generate CSV content
    def generate_csv():
        output = io.StringIO()
        # Write header
        output.write("Name,Age,City\n")
        # Write data rows
        for row in table_data:
            output.write(f"{row['name']},{row['age']},{row['city']}\n")
        return output.getvalue().encode('utf-8')

    # Button to trigger download
    ui.button('Download CSV', on_click=lambda: ui.download(generate_csv(), 'table_data.csv'))

    with ui.chat_message(
                    name='AI',
                ).classes('w-full'):
        # 创建思考区域
        think_expansion = ui.expansion(
            '💭 AI思考过程', 
            icon='psychology'
        ).classes('w-full mb-2')
        with think_expansion:
            think_label = ui.label('think').classes('whitespace-pre-wrap text-sm text-gray-600 bg-gray-50 p-2 rounded')
        
        # 创建回复区域，但暂时设为空且不可见
        reply_label = ui.label('reply').classes('whitespace-pre-wrap')
        reply_label.set_visibility(False)
    

if __name__ in {"__main__", "__mp_main__"}:
    ui.run(
        title='可下载表格',
        host='0.0.0.0',
        port=8082,
        reload=True,
        show=True
    )