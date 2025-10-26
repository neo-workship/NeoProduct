"""
登录页面
"""
from nicegui import ui
from ..auth_manager import auth_manager
from ..config import auth_config
from ..decorators import public_route
from common.log_handler import (
    # 日志记录函数
    log_trace, log_debug, log_info, log_success, 
    log_warning, log_error, log_critical,
    # 安全执行
    safe, db_safe,
    # 装饰器
    safe_protect, catch,
    # Logger 实例
    get_logger
)
logger = get_logger(__file__)

@public_route
@safe_protect(name="登录页面", error_msg="登录页面发生错误", return_on_error=None)
def login_page_content():
    """登录页面内容"""
    # 检查是否已登录
    if auth_manager.is_authenticated():
        ui.notify('您已经登录了', type='info')
        ui.navigate.to('/workbench')
        return
    
    with ui.column().classes('absolute-center items-center'):
        with ui.card().classes('w-96 shadow-lg'):
            ui.label('用户登录').classes('text-2xl font-bold text-center w-full mb-4')
            
            # 登录表单
            username_input = ui.input(
                '用户名/邮箱',
                placeholder='请输入用户名或邮箱'
            ).classes('w-full').props('clearable')
            
            password_input = ui.input(
                '密码',
                placeholder='请输入密码',
                password=True,
                password_toggle_button=True
            ).classes('w-full mt-4').props('clearable')
            
            # 记住我选项
            remember_checkbox = ui.checkbox(
                '记住我',
                value=False
            ).classes('mt-4') if auth_config.allow_remember_me else None
            
            # 登录按钮
            async def handle_login():
                username = username_input.value.strip()
                password = password_input.value
                
                if not username or not password:
                    ui.notify('请输入用户名和密码', type='warning')
                    return
                
                # 显示加载状态
                login_button.disable()
                login_button.props('loading')
                
                # 执行登录
                result = auth_manager.login(
                    username, 
                    password,
                    remember_checkbox.value if remember_checkbox else False
                )
                
                # 恢复按钮状态
                login_button.enable()
                login_button.props(remove='loading')
                
                if result['success']:
                    ui.notify(f'欢迎回来，{result["user"].username}！', type='positive')
                    # 重定向到首页或之前的页面
                    ui.navigate.to('/workbench')
                else:
                    ui.notify(result['message'], type='negative')
            
            login_button = ui.button(
                '登录',
                on_click=handle_login
            ).classes('w-full mt-6').props('color=primary size=lg')
            
            # 快捷登录（Enter键）
            username_input.on('keydown.enter', handle_login)
            password_input.on('keydown.enter', handle_login)
            
            # 分隔线
            with ui.row().classes('w-full mt-6 items-center'):
                ui.separator().classes('flex-1')
                ui.label('或').classes('px-2 text-gray-500')
                ui.separator().classes('flex-1')
            
            # 其他选项
            with ui.row().classes('w-full justify-between mt-4'):
                if auth_config.allow_registration:
                    ui.link('注册新账号', auth_config.register_route).classes('text-blue-500 hover:underline')
                else:
                    ui.label('')  # 占位
                
                ui.link('忘记密码？', '#').classes('text-gray-500 hover:underline').on(
                    'click',
                    lambda: ui.notify('密码重置功能即将推出', type='info')
                )
            
            # 测试账号提示（开发环境）
            with ui.expansion('查看测试账号', icon='info').classes('w-full mt-4 text-sm'):
                ui.label('管理员：admin / admin123').classes('text-gray-600')
                ui.label('普通用户：user / user123').classes('text-gray-600')


