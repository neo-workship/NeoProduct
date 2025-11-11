from nicegui import ui

@ui.page("/")
def main():
    with ui.row():
        e1 = ui.spinner(size='lg')
        e2 = ui.spinner('audio', size='lg', color='green')
        e3 = ui.spinner('dots', size='lg', color='red')

        e1.visible = False


if __name__ in {"__main__", "__mp_main__"}:
    ui.run(
        title='弹性布局页面',
        host='0.0.0.0',
        port=8081,
        reload=True,
        show=True
    )