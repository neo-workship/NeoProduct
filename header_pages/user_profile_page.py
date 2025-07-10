from nicegui import ui
from component.static_resources import static_manager

def user_profile_page_content():
    """用户个人资料页面内容"""
    ui.label('用户个人资料').classes('text-3xl font-bold text-indigo-800 dark:text-indigo-200')
    ui.label('在这里管理您的个人信息。').classes('text-gray-600 dark:text-gray-400 mt-4')
    
    with ui.card().classes('w-full mt-4 custom-card'):
        ui.label('基本信息').classes('text-lg font-semibold')
        
        with ui.row().classes('items-center gap-4 mt-4'):
            with ui.avatar().classes('w-16 h-16'):
                # 使用静态资源管理器获取头像路径
                avatar_path = static_manager.get_avatar_path('default_avatar.png')
                if static_manager.file_exists(avatar_path):
                    ui.image(avatar_path).classes('rounded-full')
                else:
                    # 如果文件不存在，使用占位符
                    ui.image('https://via.placeholder.com/64').classes('rounded-full')
            with ui.column():
                ui.label('用户名: Alice').classes('font-medium')
                ui.label('邮箱: alice@example.com').classes('text-gray-600')
                ui.label('角色: 管理员').classes('text-blue-600')
        
        ui.input('姓名', value='Alice Zhang').classes('w-full mt-4')
        ui.input('邮箱', value='alice@example.com').classes('w-full mt-2')
        ui.input('电话', value='+86 138-0013-8000').classes('w-full mt-2')
        ui.textarea('个人简介', value='热爱数据分析的产品经理').classes('w-full mt-2')
        
    with ui.card().classes('w-full mt-4 custom-card'):
        ui.label('安全设置').classes('text-lg font-semibold')
        ui.button('修改密码', icon='lock').classes('mt-4 custom-button')
        ui.button('双因素认证', icon='security').classes('mt-2 custom-button')
        
    ui.button('保存资料', icon='save').classes('mt-4 custom-button')
    ui.button('编辑头像', icon='photo_camera').classes('mt-4 ml-2 custom-button')