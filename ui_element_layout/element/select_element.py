from nicegui import ui, run

@ui.page('/')
def main():
    # with ui.avatar():
    with ui.row():
        ui.image('Loading.gif').classes('w-10')
        ui.label("加载中...")
    


if __name__ in {"__main__", "__mp_main__"}:
    ui.run(title="NiceGUI 全局数据演示", 
            port=8280,
            reload=True,
            prod_js=False,
            show=True)