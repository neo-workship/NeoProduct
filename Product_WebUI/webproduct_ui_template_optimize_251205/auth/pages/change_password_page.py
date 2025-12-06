from nicegui import ui
from ..auth_manager import auth_manager
from ..decorators import require_login
from ..utils import validate_password
import re
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

@require_login()
@safe_protect(name="修改密码页面", error_msg="修改密码页面发生错误", return_on_error=None)
def change_password_page_content():
    """修改密码页面内容"""
    user = auth_manager.current_user
    if not user:
        ui.notify('请先登录', type='warning')
        return

    # Page Title and Subtitle
    with ui.column().classes('w-full items-center md:items-start p-4 md:p-2'):
        ui.label('修改密码').classes('text-4xl font-extrabold text-orange-700 dark:text-orange-300 mb-2')
        ui.label('为了账户安全，请定期修改您的密码').classes('text-lg text-gray-600 dark:text-gray-400')

    with ui.row().classes('w-full justify-center p-4 md:p-2'):
        with ui.card().classes('w-full p-4 mb-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-700'): # Use w-full directly here

            with ui.grid().classes('w-full grid-cols-1 md:grid-cols-4 gap-10'):
                # Left side: Password change form (3/4 width on medium+)
                with ui.column().classes('col-span-1 md:col-span-3 '): # Occupies 3 out of 4 columns
                    ui.label('修改密码表单').classes('text-2xl font-bold mb-2 text-gray-800 dark:text-gray-200 border-b pb-4 border-gray-200 dark:border-gray-700')

                    # Password input form
                    current_password = ui.input(
                        '当前密码',
                        password=True,
                        placeholder='请输入当前密码'
                    ).classes('w-full mb-2').props('outlined clearable')

                    new_password = ui.input(
                        '新密码',
                        password=True,
                        placeholder='请输入新密码'
                    ).classes('w-full mb-2').props('outlined clearable')

                    confirm_password = ui.input(
                        '确认新密码',
                        password=True,
                        placeholder='请再次输入新密码'
                    ).classes('w-full mb-2').props('outlined clearable')

                    # Password strength indicator
                    with ui.column().classes('w-full items-start mb-4'):
                        ui.label('密码强度').classes('text-base font-semibold text-gray-700 dark:text-gray-300 mb-2')
                        with ui.row().classes('w-full items-center gap-3'):
                            strength_progress = ui.linear_progress(value=0).classes('flex-1 h-3 rounded-full').props('rounded color=primary')
                            strength_label = ui.label('无').classes('text-sm font-medium text-gray-600 dark:text-gray-400 min-w-[50px]')

                    def check_password_strength(password):
                        """检查密码强度"""
                        if not password:
                            return 0, '无', 'text-gray-600 dark:text-gray-400'

                        score = 0
                        # Length check
                        if len(password) >= 8:
                            score += 1
                        if len(password) >= 12:
                            score += 1

                        # Character type check
                        if re.search(r'[a-z]', password):
                            score += 1
                        if re.search(r'[A-Z]', password):
                            score += 1
                        if re.search(r'\d', password):
                            score += 1
                        if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
                            score += 1

                        # Strength determination
                        if score <= 2:
                            return score / 6, '弱', 'text-red-600 dark:text-red-400'
                        elif score <= 4:
                            return score / 6, '中等', 'text-orange-600 dark:text-orange-400'
                        elif score <= 5:
                            return score / 6, '强', 'text-green-600 dark:text-green-400'
                        else:
                            return 1.0, '很强', 'text-green-700 dark:text-green-300'

                    def update_password_strength():
                        """更新密码强度显示"""
                        password = new_password.value
                        strength, text, label_color = check_password_strength(password)
                        strength_progress.set_value(strength)
                        
                        # Set progress bar color based on strength
                        if strength == 0:
                            strength_progress.props('color=grey')
                        elif strength <= 0.33:
                            strength_progress.props('color=red')
                        elif strength <= 0.66:
                            strength_progress.props('color=orange')
                        else:
                            strength_progress.props('color=green')
                        
                        strength_label.text = text
                        strength_label.classes(replace=f'text-sm font-medium {label_color} min-w-[50px]')

                    # Bind password strength check
                    new_password.on('input', update_password_strength)

                    def handle_password_change():
                        """处理密码修改"""
                        # Get input values
                        current_pwd = current_password.value
                        new_pwd = new_password.value
                        confirm_pwd = confirm_password.value

                        # Basic validation
                        if not current_pwd:
                            ui.notify('请输入当前密码', type='warning', position='top')
                            current_password.run_method('focus')
                            return

                        if not new_pwd:
                            ui.notify('请输入新密码', type='warning', position='top')
                            new_password.run_method('focus')
                            return

                        if not confirm_pwd:
                            ui.notify('请确认新密码', type='warning', position='top')
                            confirm_password.run_method('focus')
                            return

                        if new_pwd != confirm_pwd:
                            ui.notify('两次输入的密码不一致', type='warning', position='top')
                            confirm_password.run_method('focus')
                            confirm_password.run_method('select')
                            return

                        if current_pwd == new_pwd:
                            ui.notify('新密码不能与当前密码相同', type='warning', position='top')
                            new_password.run_method('focus')
                            new_password.run_method('select')
                            return

                        # Validate new password strength with backend logic
                        password_result = validate_password(new_pwd)
                        if not password_result['valid']:
                            ui.notify(password_result['message'], type='warning', position='top')
                            new_password.run_method('focus')
                            new_password.run_method('select')
                            return

                        # Check password strength visually (can be combined with backend validation)
                        strength, text, _ = check_password_strength(new_pwd)
                        if strength < 0.5:  # Strength too weak
                            ui.notify('密码强度太弱，请选择更强的密码', type='warning', position='top')
                            new_password.run_method('focus')
                            new_password.run_method('select')
                            return

                        # Show loading state
                        change_button.disable()
                        change_button.props('loading')

                        try:
                            # Call authentication manager to change password
                            result = auth_manager.change_password(
                                user_id=user.id,
                                old_password=current_pwd,
                                new_password=new_pwd
                            )

                            if result['success']:
                                ui.notify('密码修改成功！即将跳转到登录页面...', type='positive', position='top')
                                # Clear form
                                current_password.value = ''
                                new_password.value = ''
                                confirm_password.value = ''
                                update_password_strength() # Reset strength indicator

                                # Manually perform logout to clear current session
                                auth_manager.logout()

                                # Redirect to login page after a delay
                                ui.timer(1.5, lambda: ui.navigate.to('/login'), once=True)
                            else:
                                ui.notify(result['message'], type='negative', position='top')
                                if '原密码错误' in result['message']:
                                    current_password.run_method('focus')
                                    current_password.run_method('select')

                        except Exception as e:
                            ui.notify(f'密码修改失败: {str(e)}', type='negative', position='top')

                        finally:
                            # Restore button state
                            change_button.enable()
                            change_button.props(remove='loading')

                    # Change password button
                    change_button = ui.button(
                        '修改密码',
                        icon='save',
                        on_click=handle_password_change
                    ).classes('w-full mt-6 bg-indigo-600 hover:bg-indigo-700 dark:bg-indigo-700 dark:hover:bg-indigo-800 text-white py-3 text-lg font-semibold rounded-lg shadow-md transition-colors duration-200')

                    # Support Enter key submission
                    current_password.on('keydown.enter', handle_password_change)
                    new_password.on('keydown.enter', handle_password_change)
                    confirm_password.on('keydown.enter', handle_password_change)

                # Right side: Password requirements (1/4 width on medium+)
                with ui.column().classes('col-span-1'): # Occupies 1 out of 4 columns
                    with ui.card().classes('w-full p-6 shadow-lg rounded-lg bg-gray-50 dark:bg-gray-700 h-full'): # h-full to make it fill vertical space
                        ui.label('密码要求').classes('text-2xl font-bold mb-6 text-gray-800 dark:text-gray-200 border-b pb-4 border-gray-200 dark:border-gray-600')

                        requirements = [
                            '至少8个字符',
                            '包含大写字母 (A-Z)',
                            '包含小写字母 (a-z)',
                            '包含数字 (0-9)',
                            '包含特殊字符 (!@#$%^&*)',
                        ]

                        for req in requirements:
                            with ui.row().classes('items-center gap-3 mt-3'):
                                ui.icon('check_circle').classes('text-green-600 dark:text-green-400 text-xl flex-shrink-0')
                                ui.label(req).classes('text-base text-gray-700 dark:text-gray-300 leading-relaxed')

                    # The "安全提示" and "账户安全状态" blocks are completely removed.