from nicegui import ui, run


selected_values = {
    'first': None,
    'field': [],
}

@ui.page('/')
def main():
    names = ['Alice', 'Bob', 'Carol']
    ui.select(names, multiple=True, value=names[:2], label='comma-separated',on_change=lambda e: ui.notify(e.value) ) \
        .classes('w-64')
    ui.select(names, multiple=True, value=names[:2], label='with chips',on_change=lambda e: ui.notify(e.value) ) \
        .classes('w-64').props('use-chips')

if __name__ in {"__main__", "__mp_main__"}:
    ui.run(title="NiceGUI 全局数据演示", 
            port=8280,
            reload=True,
            prod_js=False,
            show=True)