"""
注册页面
"""
from nicegui import ui
from ..auth_manager import auth_manager
from ..config import auth_config
from ..decorators import public_route
from ..utils import validate_email, validate_username
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
@safe_protect(name="注册页面内容", error_msg="注册页面内容加载失败")
def register_page_content():
    """注册页面内容"""
    # 检查是否允许注册
    if not auth_config.allow_registration:
        ui.notify('注册功能已关闭', type='warning')
        ui.navigate.to('/workbench')
        return
    
    # 检查是否已登录
    if auth_manager.is_authenticated():
        ui.notify('您已经登录了', type='info')
        ui.navigate.to('/workbench')
        return
    
    with ui.column().classes('absolute-center items-center'):
        with ui.card().classes('w-96 shadow-lg'):
            ui.label('用户注册').classes('text-2xl font-bold text-center w-full mb-4')
            
            # 注册表单
            username_input = ui.input(
                '用户名',
                placeholder='3-50个字符，字母数字下划线'
            ).classes('w-full').props('clearable')
            
            email_input = ui.input(
                '邮箱',
                placeholder='请输入有效的邮箱地址'
            ).classes('w-full mt-4').props('clearable')
            
            password_input = ui.input(
                '密码',
                placeholder=f'至少{auth_config.password_min_length}个字符',
                password=True,
                password_toggle_button=True
            ).classes('w-full mt-4').props('clearable')
            
            confirm_password_input = ui.input(
                '确认密码',
                placeholder='请再次输入密码',
                password=True,
                password_toggle_button=True
            ).classes('w-full mt-4').props('clearable')
            
            # 可选信息
            with ui.expansion('填写更多信息（可选）', icon='person').classes('w-full mt-4'):
                full_name_input = ui.input('姓名', placeholder='您的真实姓名').classes('w-full')
                phone_input = ui.input('电话', placeholder='手机号码').classes('w-full mt-2')
            
            # 用户协议
            agreement_checkbox = ui.checkbox('我已阅读并同意').classes('mt-4')
            ui.link('《用户服务协议》', '#').classes('text-blue-500 hover:underline ml-1').on(
                'click',
                lambda: ui.notify('用户协议内容即将添加', type='info')
            )
            
            # 注册按钮
            async def handle_register():
                # 获取输入值
                username = username_input.value.strip()
                email = email_input.value.strip()
                password = password_input.value
                confirm_password = confirm_password_input.value
                
                # 基本验证
                if not all([username, email, password, confirm_password]):
                    ui.notify('请填写所有必填项', type='warning')
                    return
                
                # 验证用户名
                username_result = validate_username(username)
                if not username_result['valid']:
                    ui.notify(username_result['message'], type='warning')
                    return
                
                # 验证邮箱
                if not validate_email(email):
                    ui.notify('邮箱格式不正确', type='warning')
                    return
                
                # 验证密码
                if password != confirm_password:
                    ui.notify('两次输入的密码不一致', type='warning')
                    return
                
                # 验证用户协议
                if not agreement_checkbox.value:
                    ui.notify('请同意用户服务协议', type='warning')
                    return
                
                # 显示加载状态
                register_button.disable()
                register_button.props('loading')
                
                # 执行注册
                result = auth_manager.register(
                    username=username,
                    email=email,
                    password=password,
                    full_name=full_name_input.value if 'full_name_input' in locals() else '',
                    phone=phone_input.value if 'phone_input' in locals() else ''
                )
                
                # 恢复按钮状态
                register_button.enable()
                register_button.props(remove='loading')
                
                if result['success']:
                    ui.notify('注册成功！即将跳转到登录页面...', type='positive')
                    # 延迟跳转
                    ui.timer(2.0, lambda: ui.navigate.to(auth_config.login_route), once=True)
                else:
                    ui.notify(result['message'], type='negative')
            
            register_button = ui.button(
                '立即注册',
                on_click=handle_register
            ).classes('w-full mt-6').props('color=primary size=lg')
            
            # 分隔线
            with ui.row().classes('w-full mt-6 items-center'):
                ui.separator().classes('flex-1')
                ui.label('已有账号？').classes('px-2 text-gray-500')
                ui.separator().classes('flex-1')
            
            # 返回登录
            ui.link(
                '返回登录',
                auth_config.login_route
            ).classes('w-full text-center text-blue-500 hover:underline mt-4')