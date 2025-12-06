from nicegui import ui
from ..auth_manager import auth_manager
from ..decorators import require_login
from ..utils import get_avatar_url, format_datetime
from component.static_resources import static_manager
from component.spa_layout import navigate_to

# 导入异常处理模块
# from common.exception_handler import log_info, log_error, safe, safe_protect
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
@safe_protect(name="个人资料页面", error_msg="个人资料页面加载失败，请稍后重试")
def profile_page_content():
    """用户资料页面内容 - 4个卡片水平排列，完全适配暗黑模式"""
    user = auth_manager.current_user
    if not user:
        ui.notify('请先登录', type='warning')
        return

    log_info("个人资料页面开始加载")

    # 页面标题
    with ui.column().classes('w-full mb-6'):
        ui.label('个人资料').classes('text-4xl font-bold text-indigo-800 dark:text-indigo-200 mb-2')
        ui.label('管理您的个人信息和账户设置').classes('text-lg text-gray-600 dark:text-gray-400')

    # 用户统计卡片区域 (These top 4 cards are already using flex-1 and look fine)
    with ui.row().classes('w-full gap-6 mb-8'):
        with ui.card().classes('flex-1 p-6 bg-gradient-to-br from-purple-500 to-purple-600 text-white shadow-lg'):
            with ui.row().classes('items-center justify-between w-full'):
                with ui.column().classes('gap-1'):
                    ui.label('用户ID').classes('text-sm opacity-90 font-medium')
                    ui.label(str(user.id)).classes('text-3xl font-bold')
                ui.icon('person').classes('text-4xl opacity-80')

        with ui.card().classes('flex-1 p-6 bg-gradient-to-br from-green-500 to-green-600 text-white shadow-lg'):
            with ui.row().classes('items-center justify-between w-full'):
                with ui.column().classes('gap-1'):
                    ui.label('登录次数').classes('text-sm opacity-90 font-medium')
                    ui.label(str(user.login_count)).classes('text-3xl font-bold')
                ui.icon('login').classes('text-4xl opacity-80')

        with ui.card().classes('flex-1 p-6 bg-gradient-to-br from-blue-500 to-blue-600 text-white shadow-lg'):
            with ui.row().classes('items-center justify-between w-full'):
                with ui.column().classes('gap-1'):
                    ui.label('账户状态').classes('text-sm opacity-90 font-medium')
                    ui.label('正常' if user.is_active else '禁用').classes('text-3xl font-bold')
                ui.icon('check_circle' if user.is_active else 'block').classes('text-4xl opacity-80')

        with ui.card().classes('flex-1 p-6 bg-gradient-to-br from-orange-500 to-orange-600 text-white shadow-lg'):
            with ui.row().classes('items-center justify-between w-full'):
                with ui.column().classes('gap-1'):
                    ui.label('角色数量').classes('text-sm opacity-90 font-medium')
                    ui.label(str(len(user.roles))).classes('text-3xl font-bold')
                ui.icon('security').classes('text-4xl opacity-80')

    # Changed classes: added 'flex-wrap items-stretch' to the row
    with ui.row().classes('w-full gap-4 flex-wrap items-stretch'):
        # 1. 基本信息卡片
        # Changed classes: added 'min-w-80' to allow wrapping and prevent excessive shrinking
        with ui.column().classes('flex-1 min-w-80'):
            create_user_info_card(user)
        
        # 2. 编辑个人信息卡片
        with ui.column().classes('flex-1 min-w-80'):
            create_profile_edit_card(user)
        
        # 3. 角色与权限卡片
        with ui.column().classes('flex-1 min-w-80'):
            create_roles_permissions_card(user)
        
        # 4. 安全设置卡片
        with ui.column().classes('flex-1 min-w-80'):
            create_security_settings_card(user)

    log_info("个人资料页面加载完成")

@safe_protect(name="创建用户基本信息卡片", error_msg="创建用户基本信息卡片页面加载失败")
def create_user_info_card(user):
    """创建用户基本信息卡片 - 完全适配暗黑模式"""
    # 确定用户状态主题
    if user.is_superuser:
        card_theme = 'border-l-4 border-purple-500'
        icon_theme = 'text-purple-600 dark:text-purple-400'
    elif 'admin' in user.roles:
        card_theme = 'border-l-4 border-red-500'
        icon_theme = 'text-red-600 dark:text-red-400'
    else:
        card_theme = 'border-l-4 border-blue-500'
        icon_theme = 'text-blue-600 dark:text-blue-400'

    with ui.card().classes(f'w-full p-4 mb-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-700 {card_theme}'):
        with ui.column().classes('w-full p-4 gap-3 h-full'):
            # 标题
            ui.label('基本信息').classes('text-lg font-bold text-gray-800 dark:text-white border-b pb-2 border-gray-200 dark:border-gray-600 mb-3')
            
            # 头像区域
            with ui.column().classes('items-center gap-2 mb-4'):
                with ui.avatar().classes('w-16 h-16 bg-gradient-to-br from-blue-400 to-purple-500'):
                    avatar_url = get_avatar_url(user)
                    ui.image(avatar_url).classes('w-14 h-14 rounded-full border-2 border-white dark:border-gray-600')
                
                ui.button(
                    '更换头像',
                    icon='photo_camera',
                    on_click=lambda: ui.notify('头像上传功能即将推出', type='info')
                ).classes('bg-blue-600 hover:bg-blue-700 text-white px-2 py-1 text-xs rounded-md').props('size=sm')

            # 用户基本信息
            with ui.column().classes('gap-2 flex-1'):
                # 用户名
                with ui.row().classes('items-center gap-2'):
                    ui.icon('person').classes(f'text-lg {icon_theme}')
                    with ui.column().classes('gap-0'):
                        ui.label(user.username).classes('text-lg font-bold text-gray-800 dark:text-white')
                        ui.label(f'ID: {user.id}').classes('text-xs text-gray-500 dark:text-gray-400')

                # 邮箱
                with ui.row().classes('w-full items-center gap-2'):
                    ui.icon('email').classes('text-lg text-gray-600 dark:text-gray-400')
                    ui.label(user.email).classes('text-sm text-gray-700 dark:text-gray-300 truncate')

                # 姓名（如果有）
                if user.full_name:
                    with ui.row().classes('items-center gap-2'):
                        ui.icon('badge').classes('text-lg text-gray-600 dark:text-gray-400')
                        ui.label(user.full_name).classes('text-sm text-gray-700 dark:text-gray-300')

            # 用户标签
            with ui.column().classes('gap-2 mt-3'):
                if user.is_superuser:
                    ui.chip('超级管理员', icon='admin_panel_settings').classes('bg-purple-100 text-purple-800 dark:bg-purple-800 dark:text-purple-200 text-xs')
                
                with ui.row().classes('gap-1 flex-wrap'):
                    if user.is_active:
                        ui.chip('正常', icon='check_circle').classes('bg-green-100 text-green-800 dark:bg-green-800 dark:text-green-200 text-xs')
                    else:
                        ui.chip('禁用', icon='block').classes('bg-red-100 text-red-800 dark:bg-red-800 dark:text-red-200 text-xs')

                    if user.is_verified:
                        ui.chip('已验证', icon='verified').classes('bg-blue-100 text-blue-800 dark:bg-blue-800 dark:text-blue-200 text-xs')
                    else:
                        ui.chip('未验证', icon='warning').classes('bg-orange-100 text-orange-800 dark:bg-orange-800 dark:text-orange-200 text-xs')

            # 时间信息
            with ui.column().classes('gap-2 mt-auto'):
                with ui.row().classes('items-center gap-2 p-2 bg-gray-50 dark:bg-gray-700 rounded text-xs'):
                    ui.icon('calendar_today').classes('text-sm text-blue-600 dark:text-blue-400')
                    with ui.column().classes('gap-0'):
                        ui.label('注册').classes('text-xs text-gray-600 dark:text-gray-400')
                        ui.label(format_datetime(user.created_at)[:10] if user.created_at else '未知').classes('text-xs font-medium text-gray-800 dark:text-white')

                with ui.row().classes('items-center gap-2 p-2 bg-gray-50 dark:bg-gray-700 rounded text-xs'):
                    ui.icon('access_time').classes('text-sm text-green-600 dark:text-green-400')
                    with ui.column().classes('gap-0'):
                        ui.label('最后登录').classes('text-xs text-gray-600 dark:text-gray-400')
                        ui.label(format_datetime(user.last_login)[:10] if user.last_login else '从未登录').classes('text-xs font-medium text-gray-800 dark:text-white')

@safe_protect(name="创建个人信息编辑卡片", error_msg="创建个人信息编辑卡片页面加载失败")
def create_profile_edit_card(user):
    """创建个人信息编辑卡片 - 完全适配暗黑模式"""
    with ui.card().classes('w-full p-4 mb-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-700'):
        with ui.column().classes('w-full p-4 gap-3 h-full'):
            ui.label('编辑个人信息').classes('text-lg font-bold text-gray-800 dark:text-white border-b pb-2 border-gray-200 dark:border-gray-600 mb-3')

            # 表单字段
            full_name_input = ui.input(
                '姓名',
                value=user.full_name or '',
                placeholder='请输入您的姓名'
            ).classes('w-full').props('outlined clearable')

            phone_input = ui.input(
                '电话',
                value=user.phone or '',
                placeholder='请输入您的电话'
            ).classes('w-full mt-2').props('outlined clearable')

            email_input = ui.input(
                '邮箱地址',
                value=user.email,
                placeholder='请输入您的邮箱'
            ).classes('w-full mt-2').props('outlined clearable')

            bio_input = ui.textarea(
                '个人简介',
                value=user.bio or '',
                placeholder='介绍一下自己...'
            ).classes('w-full mt-2 flex-1').props('outlined clearable')

            def save_profile():
                """保存个人资料"""
                log_info(f"开始保存用户资料: {user.username}")
                
                result = auth_manager.update_profile(
                    user.id,
                    full_name=full_name_input.value,
                    phone=phone_input.value,
                    email=email_input.value,
                    bio=bio_input.value
                )

                if result['success']:
                    log_info(f"用户资料保存成功: {user.username}")
                    ui.notify('个人资料更新成功', type='positive', position='top')
                    ui.timer(1.0, lambda: ui.navigate.reload(), once=True)
                else:
                    log_error(f"保存用户资料失败: {user.username}")
                    ui.notify(result['message'], type='negative', position='top')

            # 保存按钮 - 固定在底部
            ui.button(
                '保存修改',
                icon='save',
                on_click=lambda: safe(save_profile)
            ).classes('mt-auto bg-green-600 hover:bg-green-700 text-white w-full py-2 font-semibold rounded-lg transition-colors duration-200')

@safe_protect(name="创建角色权限卡片", error_msg="创建角色权限卡片页面加载失败")
def create_roles_permissions_card(user):
    """创建角色权限卡片 - 完全适配暗黑模式"""
    with ui.card().classes('w-full p-4 mb-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-700'):
        with ui.column().classes('w-full p-4 gap-3 h-full'):
            ui.label('角色与权限').classes('text-lg font-bold text-gray-800 dark:text-white border-b pb-2 border-gray-200 dark:border-gray-600 mb-3')

            # 当前角色显示
            ui.label('当前角色').classes('text-sm font-medium text-gray-700 dark:text-gray-300 mb-2')
            if user.roles:
                with ui.column().classes('gap-1 mb-4'):
                    for role in user.roles:
                        role_color = 'red' if role == 'admin' else 'blue' if role == 'user' else 'green'
                        ui.chip(role, icon='security').classes(f'bg-{role_color}-100 text-{role_color}-800 dark:bg-{role_color}-800 dark:text-{role_color}-200 text-xs font-medium')
            else:
                with ui.card().classes('w-full p-3 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600'):
                    with ui.column().classes('w-full items-center py-1'):
                        ui.icon('security_update_warning').classes('text-2xl text-gray-400 mb-1')
                        ui.label('暂无角色').classes('text-xs text-gray-500 dark:text-gray-400')

            # 权限说明
            ui.separator().classes('my-3 border-gray-200 dark:border-gray-600')
            ui.label('权限说明').classes('text-sm font-medium text-gray-700 dark:text-gray-300 mb-2')
            
            # 权限列表 - 紧凑显示
            with ui.column().classes('gap-2 flex-1 overflow-auto'):
                permission_items = [
                    ('管理员', '系统完整管理权限', 'admin_panel_settings'),
                    ('普通用户', '基本功能使用权限', 'person'),
                    ('数据访问', '查看和分析数据', 'analytics'),
                    ('内容编辑', '创建编辑内容', 'edit')
                ]

                for title, desc, icon in permission_items:
                    with ui.row().classes('items-start gap-2 p-2 bg-gray-50 dark:bg-gray-700 rounded'):
                        ui.icon(icon).classes('text-sm text-blue-600 dark:text-blue-400 mt-0.5')
                        with ui.column().classes('flex-1 gap-0'):
                            ui.label(title).classes('text-xs font-medium text-gray-800 dark:text-white')
                            ui.label(desc).classes('text-xs text-gray-600 dark:text-gray-400 leading-tight')

@safe_protect(name="创建安全设置卡片", error_msg="创建安全设置卡片页面加载失败")
def create_security_settings_card(user):
    """创建安全设置卡片 - 完全适配暗黑模式"""
    with ui.card().classes('w-full p-4 mb-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-700'):
        with ui.column().classes('w-full p-4 gap-3 h-full'):
            ui.label('安全设置').classes('text-lg font-bold text-gray-800 dark:text-white border-b pb-2 border-gray-200 dark:border-gray-600 mb-3')

            # 修改密码
            with ui.card().classes('w-full p-3 bg-orange-50 dark:bg-orange-900/20 border border-orange-200 dark:border-orange-800 rounded'):
                with ui.row().classes('items-center gap-2 w-full'):
                    ui.icon('lock').classes('text-lg text-orange-600 dark:text-orange-400')
                    with ui.column().classes('flex-1 gap-0'):
                        ui.label('修改密码').classes('text-sm font-bold text-orange-800 dark:text-orange-200')
                        ui.label('定期修改密码保证安全').classes('text-xs text-orange-600 dark:text-orange-300')

                    def go_to_change_password():
                        navigate_to('change_password', '修改密码')

                    ui.button(
                        '修改',
                        icon='edit',
                        on_click=lambda: safe(go_to_change_password)
                    ).classes('bg-orange-600 hover:bg-orange-700 text-white px-2 py-1 text-xs rounded').props('size=md')

            # 账户注销
            with ui.card().classes('w-full p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded mt-auto'):
                with ui.row().classes('items-center gap-2 w-full'):
                    ui.icon('logout').classes('text-lg text-red-600 dark:text-red-400')
                    with ui.column().classes('flex-1 gap-0'):
                        ui.label('注销账户').classes('text-sm font-bold text-red-800 dark:text-red-200')
                        ui.label('退出当前登录状态').classes('text-xs text-red-600 dark:text-red-300')

                    def handle_logout():
                        """处理注销"""
                        with ui.dialog() as logout_dialog, ui.card().classes('p-6 rounded-lg shadow-xl bg-white dark:bg-gray-800'):
                            ui.label('确认注销').classes('text-xl font-semibold text-red-600 dark:text-red-400 mb-4')
                            ui.label('您确定要注销当前账户吗？').classes('text-gray-700 dark:text-gray-300')

                            with ui.row().classes('gap-3 mt-6 justify-end w-full'):
                                ui.button('取消', on_click=logout_dialog.close).classes('bg-gray-400 hover:bg-gray-500 text-white px-4 py-2 rounded-lg')

                                def confirm_logout():
                                    logout_dialog.close()
                                    log_info(f"用户主动注销: {user.username}")
                                    navigate_to('logout', '注销')

                                ui.button('确认注销', on_click=lambda: safe(confirm_logout)).classes('bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg')

                        logout_dialog.open()

                    ui.button(
                        '注销',
                        icon='logout',
                        on_click=lambda: safe(handle_logout)
                    ).classes('bg-red-600 hover:bg-red-700 text-white px-2 py-1 text-xs rounded').props('size=md')