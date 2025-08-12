from nicegui import ui
from datetime import datetime
@ui.page('/')
def main():
    ui.markdown('''
        # Example
        ## Example
        ### Example
        #### Example
        ##### Example
    ''')

    from sqlalchemy.sql import func
    ui.label(datetime.now())
    ui.label(datetime.now().strftime('%Y-%m-%d %H:%M'))

if __name__ in {"__main__", "__mp_main__"}:
    ui.run(
        title='可下载表格',
        host='0.0.0.0',
        port=8082,
        reload=True,
        show=True
    )