from nicegui import ui

@ui.page("/")
def main():

    with ui.column():
        check_think_expansion = ui.expansion(
            '💭 AI思考过程', 
            icon='psychology'
        ).classes('w-full mb-2')
        with check_think_expansion:
            check_think_label = ui.label('check think').classes('whitespace-pre-wrap text-sm text-gray-600 bg-gray-50 p-2 rounded')
        check_reply_label = ui.label('check reply').classes('whitespace-pre-wrap')
        check_reply_label.set_visibility(False)

    ui.separator()

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