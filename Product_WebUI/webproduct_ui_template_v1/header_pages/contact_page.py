from nicegui import ui

def contact_page_content():
    """联系我们页面内容"""
    ui.label('联系我们').classes('text-3xl font-bold text-emerald-800 dark:text-emerald-200')
    ui.label('如有任何问题或建议，请随时联系我们。').classes('text-gray-600 dark:text-gray-400 mt-4')
    
    with ui.card().classes('w-full mt-4'):
        ui.label('联系方式').classes('text-lg font-semibold')
        ui.label('📧 邮箱: support@example.com').classes('mt-2')
        ui.label('📞 电话: +86 400-123-4567').classes('mt-2')
        ui.label('💬 在线客服: 工作日 9:00-18:00').classes('mt-2')
        
    with ui.card().classes('w-full mt-4'):
        ui.label('意见反馈').classes('text-lg font-semibold')
        ui.textarea('请输入您的意见或建议', placeholder='我们很重视您的反馈...').classes('w-full mt-2')
        ui.button('提交反馈', icon='send').classes('mt-2')