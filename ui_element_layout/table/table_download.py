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


    def handle_upload(e):
        # In a real application, you would save the uploaded file
        # and get a URL or path to display it.
        # For demonstration, we'll use a placeholder URL.
        ui.notify(f'Uploaded: {e.name}')
        image_display.set_source('https://picsum.photos/200/200') # Replace with actual image URL

    with ui.row():
        ui.textarea('Enter your text here').classes('w-64')
        ui.upload(on_upload=handle_upload).classes('w-64')
    image_display = ui.image('https://picsum.photos/1/1').classes('w-32 h-32') # Placeholder image

if __name__ in {"__main__", "__mp_main__"}:
    ui.run(
        title='可下载表格',
        host='0.0.0.0',
        port=8082,
        reload=True,
        show=True
    )