from nicegui import ui

@ui.page("/")
def main():
    columns = [
        {'name': 'name', 'label': 'Name', 'field': 'name', 'required': True, 'align': 'left'},
        {'name': 'age', 'label': 'Age', 'field': 'age', 'sortable': True},
    ]
    rows = [
        {'name': 'Alice', 'age': 18},
        {'name': 'Bob', 'age': 21},
        {'name': 'Carol'},
    ]
    rows1 = [(1,2,3),(4,5,6)]
    ui.table(rows=rows1, row_key='name').classes('w-full')


if __name__ in {"__main__", "__mp_main__"}:
    ui.run(
        title='弹性布局页面',
        host='0.0.0.0',
        port=8082,
        reload=True,
        show=True
    )