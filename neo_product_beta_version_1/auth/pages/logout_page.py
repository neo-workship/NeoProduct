from nicegui import ui, app
from ..auth_manager import auth_manager
from ..decorators import public_route

@public_route
def logout_page_content():
    """注销页面内容 - 增强版"""
    print("🚪 开始执行注销流程")
    
    # 清除路由存储
    try:
        if 'current_route' in app.storage.user:
            del app.storage.user['current_route']
            print("🗑️ 已清除路由存储")
    except Exception as e:
        print(f"⚠️ 清除路由存储失败: {e}")
    
    # 执行注销
    auth_manager.logout()
    
    # 显示注销成功信息
    ui.notify('已退出登录!', type='info')
    
    # 延迟跳转到登录页面
    ui.timer(1.0, lambda: ui.navigate.to('/login'), once=True)
    
    # 显示注销确认页面
    with ui.column().classes('absolute-center items-center'):
        with ui.card().classes('p-8 text-center'):
            ui.icon('logout', size='4rem').classes('text-blue-500 mb-4')
            ui.label('正在注销...').classes('text-xl font-medium mb-2')
            ui.label('即将跳转到登录页面').classes('text-gray-600')
            ui.spinner(size='lg').classes('mt-4')