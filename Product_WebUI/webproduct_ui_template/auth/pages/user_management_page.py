"""
用户管理页面 - 增强版：添加用户锁定状态显示和控制功能
"""
from nicegui import ui
from ..decorators import require_role
from ..auth_manager import auth_manager
from ..detached_helper import (
    detached_manager, 
    get_users_safe, 
    get_user_safe,
    get_roles_safe,
    DetachedUser
)
from ..utils import format_datetime, validate_email, validate_username
from ..models import User, Role
from ..database import get_db
import secrets
import string
from datetime import datetime, timedelta

# 导入异常处理模块
# from common.exception_handler import log_info, log_error, safe, db_safe, safe_protect
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
# 获取绑定模块名称的logger
logger = get_logger(__file__)

@require_role('admin')
@safe_protect(name="用户管理页面", error_msg="用户管理页面加载失败，请稍后重试")
def user_management_page_content():
    """用户管理页面内容 - 仅管理员可访问"""
    # 页面标题
    with ui.column().classes('w-full mb-6'):
        ui.label('用户管理').classes('text-4xl font-bold text-indigo-800 dark:text-indigo-200 mb-2')
        ui.label('管理系统中的所有用户账户').classes('text-lg text-gray-600 dark:text-gray-400')

    # 用户统计卡片 - 添加锁定用户统计
    def load_user_statistics():
        """加载用户统计数据 - 增加锁定用户统计"""
        # 获取基础统计
        base_stats = detached_manager.get_user_statistics()
        # 计算锁定用户数量
        try:
            with db_safe("统计锁定用户") as db:
                current_time = datetime.now()
                locked_users_count = db.query(User).filter(
                    User.locked_until != None,
                    User.locked_until > current_time
                ).count()  
                base_stats['locked_users'] = locked_users_count    
        except Exception as e:
            log_error("获取锁定用户统计失败", exception=e)
            base_stats['locked_users'] = 0
        return base_stats
    # 安全执行统计数据加载
    stats = safe(
        load_user_statistics,
        return_value={'total_users': 0, 'active_users': 0, 'verified_users': 0, 'admin_users': 0, 'locked_users': 0},
        error_msg="用户统计数据加载失败"
    )

    with ui.row().classes('w-full gap-6 mb-8'):
        with ui.card().classes('flex-1 p-4 bg-gradient-to-r from-blue-500 to-blue-600 text-white'):
            with ui.row().classes('items-center justify-between w-full'):
                with ui.column().classes('gap-1'):
                    ui.label('总用户数').classes('text-sm opacity-90')
                    ui.label(str(stats['total_users'])).classes('text-3xl font-bold')
                ui.icon('people').classes('text-2xl opacity-80')

        with ui.card().classes('flex-1 p-4 bg-gradient-to-r from-green-500 to-green-600 text-white'):
            with ui.row().classes('items-center justify-between w-full'):
                with ui.column().classes('gap-1'):
                    ui.label('活跃用户').classes('text-sm opacity-90')
                    ui.label(str(stats['active_users'])).classes('text-3xl font-bold')
                ui.icon('check_circle').classes('text-2xl opacity-80')

        with ui.card().classes('flex-1 p-4 bg-gradient-to-r from-orange-500 to-orange-600 text-white'):
            with ui.row().classes('items-center justify-between w-full'):
                with ui.column().classes('gap-1'):
                    ui.label('已验证用户').classes('text-sm opacity-90')
                    ui.label(str(stats['verified_users'])).classes('text-3xl font-bold')
                ui.icon('verified').classes('text-2xl opacity-80')

        # 新增：锁定用户统计卡片
        with ui.card().classes('flex-1 p-4 bg-gradient-to-r from-red-500 to-red-600 text-white'):
            with ui.row().classes('items-center justify-between w-full'):
                with ui.column().classes('gap-1'):
                    ui.label('锁定用户').classes('text-sm opacity-90')
                    ui.label(str(stats['locked_users'])).classes('text-3xl font-bold')
                ui.icon('lock').classes('text-2xl opacity-80')

        with ui.card().classes('flex-1 p-4 bg-gradient-to-r from-purple-500 to-purple-600 text-white'):
            with ui.row().classes('items-center justify-between w-full'):
                with ui.column().classes('gap-1'):
                    ui.label('管理员').classes('text-sm opacity-90')
                    ui.label(str(stats['admin_users'])).classes('text-3xl font-bold')
                ui.icon('admin_panel_settings').classes('text-2xl opacity-80')

    with ui.card().classes('w-full mt-6'):
        ui.label('用户列表').classes('text-lg font-semibold')

        # 操作按钮行
        with ui.row().classes('w-full gap-2 mt-4'):
            ui.button('添加用户', icon='add', on_click=lambda: safe(add_user_dialog)).classes('bg-blue-500 text-white')
            ui.button('导出用户', icon='download', on_click=lambda: safe(export_users)).classes('bg-green-500 text-white')
            ui.button('批量解锁', icon='lock_open', on_click=lambda: safe(batch_unlock_users)).classes('bg-orange-500 text-white')
            # 测试异常按钮
            ui.button('测试异常', icon='bug_report', 
                     on_click=lambda: safe(test_exception_function),
                     color='red').classes('ml-4')

        # 绑定搜索事件处理函数
        def handle_search():
            """处理搜索事件 - 立即执行"""
            safe(load_users)
        
        def handle_input_search():
            """处理输入搜索事件 - 延迟执行"""
            ui.timer(0.5, lambda: safe(load_users), once=True)
        
        def reset_search():
            """重置搜索"""
            search_input.value = ''
            safe(load_users)

        # 搜索区域
        with ui.row().classes('w-full gap-2 mt-4 items-end'):
            search_input = ui.input(
                '搜索用户', 
                placeholder='输入用户名或邮箱进行搜索...',
                value=''
            ).classes('flex-1').props('outlined clearable')
            search_input.props('prepend-icon=search')
            
            ui.button('搜索', icon='search', 
                     on_click=handle_search).classes('bg-blue-600 hover:bg-blue-700 text-white px-4 py-2')
            ui.button('重置', icon='refresh', 
                     on_click=reset_search).classes('bg-gray-500 hover:bg-gray-600 text-white px-4 py-2')

        # 用户表格容器
        users_container = ui.column().classes('w-full gap-3')

        def load_users():
            """加载用户数据 - 使用网格布局，最多显示2个用户，鼓励搜索"""
            users_container.clear()

            # 获取搜索条件
            search_term = search_input.value.strip() if hasattr(search_input, 'value') and search_input.value else None
            
            # 使用安全的数据获取方法，传入搜索条件
            all_users = get_users_safe(search_term=search_term)

            # 限制显示的用户数量
            MAX_DISPLAY_USERS = 2
            users_to_display = all_users[:MAX_DISPLAY_USERS]
            has_more_users = len(all_users) > MAX_DISPLAY_USERS

            with users_container:
                # 搜索提示区域
                with ui.card().classes('w-full p-4 mb-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-700'):
                    with ui.row().classes('items-center gap-3'):
                        ui.icon('info').classes('text-blue-600 dark:text-blue-400 text-2xl')
                        with ui.column().classes('flex-1'):
                            ui.label('使用提示').classes('text-lg font-semibold text-blue-800 dark:text-blue-200')
                            if not search_term:
                                ui.label('用户列表最多显示2个用户。要查看或操作特定用户，请使用上方搜索框输入用户名或邮箱进行搜索。').classes('text-blue-700 dark:text-blue-300 text-sm leading-relaxed')
                            else:
                                if len(all_users) > MAX_DISPLAY_USERS:
                                    ui.label(f'搜索到 {len(all_users)} 个用户，当前显示前 {MAX_DISPLAY_USERS} 个。请使用更精确的关键词缩小搜索范围。').classes('text-blue-700 dark:text-blue-300 text-sm leading-relaxed')
                                else:
                                    ui.label(f'搜索到 {len(all_users)} 个匹配用户。').classes('text-blue-700 dark:text-blue-300 text-sm leading-relaxed')

                # 处理无数据情况
                if not all_users:
                    with ui.card().classes('w-full p-8 text-center bg-gray-50 dark:bg-gray-700'):
                        if search_term:
                            ui.icon('search_off').classes('text-6xl text-gray-400 mb-4')
                            ui.label(f'未找到匹配 "{search_term}" 的用户').classes('text-xl font-medium text-gray-500 dark:text-gray-400')
                            ui.label('请尝试其他关键词或清空搜索条件').classes('text-gray-400 dark:text-gray-500 mt-2')
                            with ui.row().classes('gap-2 mt-4 justify-center'):
                                ui.button('清空搜索', icon='clear', 
                                        on_click=reset_search).classes('bg-blue-500 text-white')
                                ui.button('添加新用户', icon='person_add',
                                        on_click=lambda: safe(add_user_dialog)).classes('bg-green-500 text-white')
                        else:
                            ui.icon('people_off').classes('text-6xl text-gray-400 mb-4')
                            ui.label('暂无用户数据').classes('text-xl font-medium text-gray-500 dark:text-gray-400')
                            ui.label('点击"添加用户"按钮添加第一个用户').classes('text-gray-400 dark:text-gray-500 mt-2')
                            ui.button('添加新用户', icon='person_add',
                                    on_click=lambda: safe(add_user_dialog)).classes('mt-4 bg-green-500 text-white')
                    return

                # 显示统计信息
                with ui.row().classes('w-full items-center justify-between mb-4'):
                    if search_term:
                        ui.label(f'搜索结果: {len(all_users)} 个用户').classes('text-lg font-medium text-gray-700 dark:text-gray-300')
                    else:
                        ui.label(f'用户总数: {len(all_users)} 个').classes('text-lg font-medium text-gray-700 dark:text-gray-300')
                    
                    if has_more_users:
                        ui.chip(f'显示 {len(users_to_display)}/{len(all_users)}', icon='visibility').classes('bg-orange-100 text-orange-800 dark:bg-orange-800 dark:text-orange-200')

                # 创建用户卡片网格 - 每行2个
                if users_to_display:
                    for i in range(0, len(users_to_display), 2):
                        with ui.row().classes('w-full gap-3'):
                            # 第一个用户卡片
                            with ui.column().classes('flex-1'):
                                create_user_card(users_to_display[i])
                            
                            # 第二个用户卡片（如果存在）
                            if i + 1 < len(users_to_display):
                                with ui.column().classes('flex-1'):
                                    create_user_card(users_to_display[i + 1])
                            else:
                                # 如果是奇数个用户，添加占位符保持布局
                                ui.column().classes('flex-1')

                # 如果有更多用户未显示，显示提示
                if has_more_users:
                    with ui.card().classes('w-full p-4 mt-4 bg-orange-50 dark:bg-orange-900/20 border border-orange-200 dark:border-orange-700'):
                        with ui.row().classes('items-center gap-3'):
                            ui.icon('visibility_off').classes('text-orange-600 dark:text-orange-400 text-2xl')
                            with ui.column().classes('flex-1'):
                                ui.label(f'还有 {len(all_users) - MAX_DISPLAY_USERS} 个用户未显示').classes('text-lg font-semibold text-orange-800 dark:text-orange-200')
                                ui.label('请使用搜索功能查找特定用户，或者使用更精确的关键词缩小范围。').classes('text-orange-700 dark:text-orange-300 text-sm')

        def create_user_card(user_data: DetachedUser):
            """创建单个用户卡片 - 增加锁定状态显示"""
            # 检查用户是否被锁定
            is_locked = user_data.locked_until and user_data.locked_until > datetime.now()
            
            # 确定用户状态主题
            if user_data.is_superuser:
                card_theme = 'border-l-4 border-purple-500 bg-purple-50 dark:bg-purple-900/10'
                badge_theme = 'bg-purple-100 text-purple-800 dark:bg-purple-800 dark:text-purple-200'
                icon_theme = 'text-purple-600 dark:text-purple-400'
            elif is_locked:
                card_theme = 'border-l-4 border-red-600 bg-red-50 dark:bg-red-900/10'
                badge_theme = 'bg-red-100 text-red-800 dark:bg-red-800 dark:text-red-200'
                icon_theme = 'text-red-600 dark:text-red-400'
            elif 'admin' in user_data.roles:
                card_theme = 'border-l-4 border-red-500 bg-red-50 dark:bg-red-900/10'
                badge_theme = 'bg-red-100 text-red-800 dark:bg-red-800 dark:text-red-200'
                icon_theme = 'text-red-600 dark:text-red-400'
            else:
                card_theme = 'border-l-4 border-blue-500 bg-blue-50 dark:bg-blue-900/10'
                badge_theme = 'bg-blue-100 text-blue-800 dark:bg-blue-800 dark:text-blue-200'
                icon_theme = 'text-blue-600 dark:text-blue-400'

            with ui.card().classes(f'w-full {card_theme} shadow-md hover:shadow-lg transition-shadow duration-300'):
                with ui.row().classes('w-full p-4 gap-4'):
                    # 左侧：用户基本信息（约占 35%）
                    with ui.column().classes('flex-none w-72 gap-2'):
                        # 用户头部信息
                        with ui.row().classes('items-center gap-3 mb-2'):
                            # 根据锁定状态显示不同图标
                            icon_name = 'lock' if is_locked else 'person'
                            ui.icon(icon_name).classes(f'text-3xl {icon_theme}')
                            with ui.column().classes('gap-0'):
                                ui.label(user_data.username).classes('text-xl font-bold text-gray-800 dark:text-gray-200')
                                ui.label(f'ID: {user_data.id}').classes('text-xs text-gray-500 dark:text-gray-400')

                        # 用户标签 - 添加锁定状态标签
                        with ui.row().classes('gap-1 flex-wrap mb-2'):
                            if user_data.is_superuser:
                                ui.chip('超级管理员', icon='admin_panel_settings').classes('bg-purple-100 text-purple-800 dark:bg-purple-800 dark:text-purple-200 text-xs py-1 px-2')
                            
                            # 锁定状态标签 - 新增
                            if is_locked:
                                ui.chip('已锁定', icon='lock').classes('bg-red-100 text-red-800 dark:bg-red-800 dark:text-red-200 text-xs py-1 px-2')
                            
                            if user_data.is_active:
                                ui.chip('已激活', icon='check_circle').classes('bg-green-100 text-green-800 dark:bg-green-800 dark:text-green-200 text-xs py-1 px-2')
                            else:
                                ui.chip('已禁用', icon='block').classes('bg-red-100 text-red-800 dark:bg-red-800 dark:text-red-200 text-xs py-1 px-2')
                            
                            if user_data.is_verified:
                                ui.chip('已验证', icon='verified').classes('bg-blue-100 text-blue-800 dark:bg-blue-800 dark:text-blue-200 text-xs py-1 px-2')
                            else:
                                ui.chip('未验证', icon='warning').classes('bg-orange-100 text-orange-800 dark:bg-orange-800 dark:text-orange-200 text-xs py-1 px-2')

                        # 用户信息
                        ui.label('基本信息:').classes('text-xs font-medium text-gray-600 dark:text-gray-400')
                        ui.label(user_data.email).classes('text-sm text-gray-700 dark:text-gray-300 leading-tight min-h-[1.5rem] line-clamp-1')
                        if user_data.full_name:
                            ui.label(f'姓名: {user_data.full_name}').classes('text-sm text-gray-700 dark:text-gray-300 leading-tight')

                        # 锁定信息显示 - 新增
                        if is_locked:
                            ui.label('锁定信息:').classes('text-xs font-medium text-red-600 dark:text-red-400 mt-2')
                            ui.label(f'锁定至: {format_datetime(user_data.locked_until)}').classes('text-xs text-red-700 dark:text-red-300')
                            remaining_time = user_data.locked_until - datetime.now()
                            if remaining_time.total_seconds() > 0:
                                minutes = int(remaining_time.total_seconds() / 60)
                                ui.label(f'剩余: {minutes} 分钟').classes('text-xs text-red-700 dark:text-red-300')

                        # 统计信息
                        with ui.row().classes('gap-2 mt-2'):
                            with ui.card().classes('flex-1 p-2 bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600'):
                                ui.label('登录次数').classes('text-xs text-gray-500 dark:text-gray-400')
                                ui.label(str(user_data.login_count)).classes('text-lg font-bold text-blue-600 dark:text-blue-400')

                    # 右侧：角色管理区域（约占 65%）
                    with ui.column().classes('flex-1 gap-2'):
                        # 角色列表标题
                        with ui.row().classes('items-center justify-between w-full mb-2'):
                            ui.label(f'用户角色 ({len(user_data.roles)})').classes('text-lg font-bold text-gray-800 dark:text-gray-200')

                        # 角色列表区域
                        with ui.card().classes('w-full p-3 bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 min-h-[80px] max-h-[120px] overflow-auto'):
                            if user_data.roles:
                                with ui.row().classes('gap-2 flex-wrap'):
                                    for role in user_data.roles:
                                        role_color = 'red' if role == 'admin' else 'blue' if role == 'user' else 'green'
                                        ui.chip(role, icon='security').classes(f'bg-{role_color}-100 text-{role_color}-800 dark:bg-{role_color}-800 dark:text-{role_color}-200 text-sm')
                            else:
                                with ui.column().classes('w-full items-center justify-center py-2'):
                                    ui.icon('security_update_warning').classes('text-2xl text-gray-400 mb-1')
                                    ui.label('暂无角色').classes('text-sm text-gray-500 dark:text-gray-400')

                        # 最后登录信息
                        ui.label('最后登录').classes('text-sm font-medium text-gray-600 dark:text-gray-400')
                        ui.label(format_datetime(user_data.last_login) if user_data.last_login else '从未登录').classes('text-sm text-gray-700 dark:text-gray-300')

                        # 用户操作按钮
                        with ui.row().classes('gap-1 w-full mt-2'):
                            ui.button('编辑', icon='edit',
                                    on_click=lambda u=user_data: safe(lambda: edit_user_dialog(u.id))).classes('flex-1 bg-blue-600 hover:bg-blue-700 text-white py-1 text-xs')
                            
                            # 锁定/解锁按钮 - 新增
                            if is_locked:
                                ui.button('解锁', icon='lock_open',
                                        on_click=lambda u=user_data: safe(lambda: toggle_user_lock(u.id, False))).classes('flex-1 bg-orange-600 hover:bg-orange-700 text-white py-1 text-xs')
                            else:
                                ui.button('锁定', icon='lock',
                                        on_click=lambda u=user_data: safe(lambda: toggle_user_lock(u.id, True))).classes('flex-1 bg-red-600 hover:bg-red-700 text-white py-1 text-xs')
                            
                            ui.button('重置密码', icon='lock_reset',
                                    on_click=lambda u=user_data: safe(lambda: reset_password_dialog(u.id))).classes('flex-1 bg-purple-600 hover:bg-purple-700 text-white py-1 text-xs')
                            
                            # 只有当不是当前登录用户时才显示删除按钮
                            if not auth_manager.current_user or auth_manager.current_user.id != user_data.id:
                                ui.button('删除', icon='delete',
                                        on_click=lambda u=user_data: safe(lambda: delete_user_dialog(u.id))).classes('flex-1 bg-red-600 hover:bg-red-700 text-white py-1 text-xs')
                            else:
                                ui.button('当前用户', icon='person',
                                        on_click=lambda: ui.notify('这是您当前登录的账户', type='info')).classes('flex-1 bg-gray-400 text-white py-1 text-xs').disable()

        def toggle_user_lock(user_id: int, lock: bool):
            """切换用户锁定状态"""
            user_data = get_user_safe(user_id)
            if not user_data:
                ui.notify('用户不存在', type='error')
                return
            
            action = "锁定" if lock else "解锁"            
            try:
                with db_safe(f"{action}用户") as db:
                    user = db.query(User).filter(User.id == user_id).first()
                    if not user:
                        ui.notify('用户不存在', type='error')
                        return
                    
                    if lock:
                        # 锁定用户 - 设置30分钟后解锁
                        user.locked_until = datetime.now() + timedelta(minutes=30)
                        ui.notify(f'用户 {user.username} 已锁定 30 分钟', type='warning')
                        log_info(f"用户锁定成功: {user.username}, 锁定至: {user.locked_until}")
                    else:
                        # 解锁用户
                        user.locked_until = None
                        ui.notify(f'用户 {user.username} 已解锁', type='positive')
                        log_info(f"用户解锁成功: {user.username}")
                    
                    db.commit()
                    safe(load_users)  # 重新加载用户列表
                    
            except Exception as e:
                log_error(f"{action}用户失败: {user_data.username}", exception=e)
                ui.notify(f'{action}失败，请稍后重试', type='negative')

        def batch_unlock_users():
            """批量解锁所有锁定的用户"""
            log_info("开始批量解锁用户")
            
            try:
                with db_safe("批量解锁用户") as db:
                    current_time = datetime.now()
                    locked_users = db.query(User).filter(
                        User.locked_until != None,
                        User.locked_until > current_time
                    ).all()
                    
                    if not locked_users:
                        ui.notify('当前没有锁定的用户', type='info')
                        return
                    
                    count = len(locked_users)
                    for user in locked_users:
                        user.locked_until = None
                    
                    db.commit()
                    
                    log_info(f"批量解锁用户成功: {count} 个用户")
                    ui.notify(f'已解锁 {count} 个用户', type='positive')
                    safe(load_users)  # 重新加载用户列表
                    
            except Exception as e:
                log_error("批量解锁用户失败", exception=e)
                ui.notify('批量解锁失败，请稍后重试', type='negative')

        def edit_user_dialog(user_id):
            """编辑用户对话框 - 增加锁定状态控制"""
            
            with ui.dialog() as dialog, ui.card().classes('w-96'):
                dialog.open()
                ui.label('编辑用户').classes('text-lg font-semibold')

                # 安全获取用户数据
                user_data = get_user_safe(user_id)
                if not user_data:
                    ui.label('用户不存在或加载失败').classes('text-red-500')
                    log_error(f"编辑用户失败: 用户ID {user_id} 不存在或加载失败")
                    return

                # 获取可用角色
                available_roles = safe(get_roles_safe, return_value=[])

                # 检查用户是否被锁定
                is_locked = user_data.locked_until and user_data.locked_until > datetime.now()

                # 表单字段
                username_input = ui.input('用户名', value=user_data.username).classes('w-full')
                email_input = ui.input('邮箱', value=user_data.email).classes('w-full')
                full_name_input = ui.input('姓名', value=user_data.full_name or '').classes('w-full')

                # 状态开关
                is_active_switch = ui.switch('账户启用', value=user_data.is_active).classes('mt-4')
                is_verified_switch = ui.switch('邮箱验证', value=user_data.is_verified).classes('mt-2')
                
                # 新增：锁定状态控制开关
                is_locked_switch = ui.switch('锁定账户', value=is_locked).classes('mt-2')
                
                # 锁定信息显示
                if is_locked:
                    with ui.card().classes('w-full mt-2 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-700'):
                        ui.label('锁定信息').classes('text-sm font-medium text-red-600 dark:text-red-400')
                        ui.label(f'锁定至: {format_datetime(user_data.locked_until)}').classes('text-xs text-red-700 dark:text-red-300')
                        remaining_time = user_data.locked_until - datetime.now()
                        if remaining_time.total_seconds() > 0:
                            minutes = int(remaining_time.total_seconds() / 60)
                            ui.label(f'剩余时间: {minutes} 分钟').classes('text-xs text-red-700 dark:text-red-300')

                # 角色选择
                ui.label('角色权限').classes('mt-4 font-medium')
                role_checkboxes = {}
                for role in available_roles:
                    role_checkboxes[role.name] = ui.checkbox(
                        role.display_name or role.name,
                        value=role.name in user_data.roles
                    ).classes('mt-1')

                def save_user():
                    """保存用户修改 - 包含锁定状态处理"""
                    
                    # 验证输入
                    if not username_input.value.strip():
                        ui.notify('用户名不能为空', type='warning')
                        return

                    if not validate_email(email_input.value):
                        ui.notify('邮箱格式不正确', type='warning')
                        return

                    try:
                        with db_safe("更新用户信息") as db:
                            user = db.query(User).filter(User.id == user_id).first()
                            if not user:
                                ui.notify('用户不存在', type='error')
                                return
                            
                            # 更新基本信息
                            user.username = username_input.value.strip()
                            user.email = email_input.value.strip()
                            user.full_name = full_name_input.value.strip() or None
                            user.is_active = is_active_switch.value
                            user.is_verified = is_verified_switch.value
                            
                            # 处理锁定状态 - 新增逻辑
                            if is_locked_switch.value and not is_locked:
                                # 用户从未锁定变为锁定
                                user.locked_until = datetime.now() + timedelta(minutes=30)
                                log_info(f"用户 {user.username} 被设置为锁定状态，锁定至: {user.locked_until}")
                            elif not is_locked_switch.value and is_locked:
                                # 用户从锁定变为未锁定
                                user.locked_until = None
                                log_info(f"用户 {user.username} 被解除锁定状态")
                            # 如果状态没有改变，不处理 locked_until
                            
                            # 更新角色
                            user.roles.clear()
                            selected_roles = [role_name for role_name, checkbox in role_checkboxes.items() if checkbox.value]
                            if selected_roles:
                                roles = db.query(Role).filter(Role.name.in_(selected_roles)).all()
                                user.roles.extend(roles)
                            
                            db.commit()
                            
                            log_info(f"用户修改成功: {user.username}, 新角色: {selected_roles}, 锁定状态: {is_locked_switch.value}")
                            ui.notify('用户信息已更新', type='positive')
                            dialog.close()
                            safe(load_users)

                    except Exception as e:
                        log_error(f"保存用户修改失败: 用户ID {user_id}", exception=e)
                        ui.notify('保存失败，请稍后重试', type='negative')

                with ui.row().classes('w-full justify-end gap-2 mt-6'):
                    ui.button('取消', on_click=dialog.close).classes('bg-gray-500 text-white')
                    ui.button('保存', on_click=lambda: safe(save_user)).classes('bg-blue-500 text-white')

        def add_user_dialog():
            """添加用户对话框"""
            log_info("打开添加用户对话框")
            
            with ui.dialog() as dialog, ui.card().classes('w-96'):
                dialog.open()
                ui.label('添加新用户').classes('text-lg font-semibold')

                # 表单字段
                username_input = ui.input('用户名', placeholder='3-50个字符').classes('w-full')
                email_input = ui.input('邮箱', placeholder='有效的邮箱地址').classes('w-full')
                full_name_input = ui.input('姓名', placeholder='可选').classes('w-full')
                password_input = ui.input('密码', password=True, placeholder='至少6个字符').classes('w-full')

                # 角色选择
                available_roles = safe(get_roles_safe, return_value=[])
                
                ui.label('角色权限').classes('mt-4 font-medium')
                role_checkboxes = {}
                for role in available_roles:
                    role_checkboxes[role.name] = ui.checkbox(
                        role.display_name or role.name,
                        value=(role.name == 'user')  # 默认选择user角色
                    ).classes('mt-1')

                def save_new_user():
                    """保存新用户"""
                    log_info("开始创建新用户")
                    
                    # 验证输入
                    username_result = validate_username(username_input.value or '')
                    if not username_result['valid']:
                        ui.notify(username_result['message'], type='warning')
                        log_error(f"用户名验证失败: {username_result['message']}")
                        return

                    if not validate_email(email_input.value or ''):
                        ui.notify('邮箱格式不正确', type='warning')
                        log_error(f"邮箱验证失败: {email_input.value}")
                        return

                    if not password_input.value or len(password_input.value) < 6:
                        ui.notify('密码至少需要6个字符', type='warning')
                        log_error("密码长度不足")
                        return

                    try:
                        with db_safe("创建新用户") as db:
                            # 检查用户名和邮箱是否已存在
                            existing = db.query(User).filter(
                                (User.username == username_input.value) |
                                (User.email == email_input.value)
                            ).first()

                            if existing:
                                ui.notify('用户名或邮箱已存在', type='warning')
                                log_error(f"用户创建失败: 用户名或邮箱已存在 - {username_input.value}, {email_input.value}")
                                return

                            # 创建新用户
                            new_user = User(
                                username=username_input.value.strip(),
                                email=email_input.value.strip(),
                                full_name=full_name_input.value.strip() or None,
                                is_active=True,
                                is_verified=True,
                                locked_until=None  # 新用户默认不锁定
                            )
                            new_user.set_password(password_input.value)

                            # 分配角色
                            selected_roles = []
                            for role_name, checkbox in role_checkboxes.items():
                                if checkbox.value:
                                    role = db.query(Role).filter(Role.name == role_name).first()
                                    if role:
                                        new_user.roles.append(role)
                                        selected_roles.append(role_name)

                            db.add(new_user)
                            db.commit()

                            log_info(f"新用户创建成功: {new_user.username}, 角色: {selected_roles}")
                            ui.notify(f'用户 {new_user.username} 创建成功', type='positive')
                            dialog.close()
                            safe(load_users)

                    except Exception as e:
                        log_error(f"创建用户失败: {username_input.value}", exception=e)
                        ui.notify('用户创建失败，请稍后重试', type='negative')

                with ui.row().classes('w-full justify-end gap-2 mt-6'):
                    ui.button('取消', on_click=dialog.close).classes('bg-gray-500 text-white')
                    ui.button('创建用户', on_click=lambda: safe(save_new_user)).classes('bg-blue-500 text-white')

        def reset_password_dialog(user_id):
            """重置密码对话框"""
            log_info(f"打开重置密码对话框: 用户ID {user_id}")
            
            # 安全获取用户数据
            user_data = get_user_safe(user_id)
            if not user_data:
                ui.notify('用户不存在', type='error')
                log_error(f"重置密码失败: 用户ID {user_id} 不存在")
                return
            
            with ui.dialog() as dialog, ui.card().classes('w-96'):
                dialog.open()
                ui.label(f'重置用户密码: {user_data.username}').classes('text-lg font-semibold')

                # 显示生成的密码
                password_display = ui.input('新密码', password=False).classes('w-full mt-4')
                password_display.props('hint="点击下方按钮生成随机密码"')
                password_display.disable()

                def generate_password():
                    """生成随机密码"""
                    length = 12
                    characters = string.ascii_letters + string.digits + "!@#$%^&*"
                    password = ''.join(secrets.choice(characters) for _ in range(length))
                    password_display.enable()
                    password_display.value = password
                    password_display.disable()
                    ui.notify('已生成随机密码', type='info')
                    log_info(f"为用户 {user_data.username} 生成随机密码")

                ui.button('生成随机密码', icon='casino', 
                         on_click=lambda: safe(generate_password)).classes('w-full mt-2 bg-purple-500 text-white')

                def perform_reset():
                    """执行密码重置"""
                    log_info(f"开始重置用户密码: {user_data.username}")
                    
                    if not password_display.value:
                        ui.notify('请先生成密码', type='warning')
                        return

                    try:
                        with db_safe("重置用户密码") as db:
                            user = db.query(User).filter(User.id == user_id).first()
                            if not user:
                                ui.notify('用户不存在', type='error')
                                return

                            # 更新密码
                            user.set_password(password_display.value)
                            user.session_token = None
                            user.remember_token = None
                            db.commit()

                            log_info(f"用户密码重置成功: {user.username}")
                            ui.notify(f'用户 {user.username} 密码重置成功', type='positive')
                            dialog.close()

                    except Exception as e:
                        log_error(f"重置密码失败: {user_data.username}", exception=e)
                        ui.notify('密码重置失败，请稍后重试', type='negative')

                with ui.row().classes('w-full justify-end gap-2 mt-6'):
                    ui.button('取消', on_click=dialog.close).classes('bg-gray-500 text-white')
                    ui.button('重置密码', on_click=lambda: safe(perform_reset)).classes('bg-orange-500 text-white')

        def delete_user_dialog(user_id):
            """删除用户对话框"""
            log_info(f"打开删除用户对话框: 用户ID {user_id}")
            
            # 安全获取用户数据
            user_data = get_user_safe(user_id)
            if not user_data:
                ui.notify('用户不存在', type='error')
                log_error(f"删除用户失败: 用户ID {user_id} 不存在")
                return
            
            with ui.dialog() as dialog, ui.card().classes('w-96'):
                dialog.open()
                ui.label('确认删除用户').classes('text-lg font-semibold text-red-600')
                ui.label(f'您确定要删除用户 "{user_data.username}" 吗？').classes('mt-2')
                ui.label('此操作不可撤销！').classes('text-red-500 mt-2 font-medium')

                def confirm_delete():
                    """确认删除"""
                    log_info(f"开始删除用户: {user_data.username}")
                    
                    # 检查是否是当前登录用户
                    if auth_manager.current_user and auth_manager.current_user.id == user_id:
                        ui.notify('不能删除当前登录的用户', type='warning')
                        log_error(f"删除用户失败: 尝试删除当前登录用户 {user_data.username}")
                        return

                    # 使用安全的删除方法
                    success = detached_manager.delete_user_safe(user_id)
                    
                    if success:
                        log_info(f"用户删除成功: {user_data.username}")
                        ui.notify(f'用户 {user_data.username} 已删除', type='positive')
                        dialog.close()
                        safe(load_users)
                    else:
                        log_error(f"删除用户失败: {user_data.username}")
                        ui.notify('删除失败，请稍后重试', type='negative')

                with ui.row().classes('w-full justify-end gap-2 mt-6'):
                    ui.button('取消', on_click=dialog.close).classes('bg-gray-500 text-white')
                    ui.button('确认删除', on_click=lambda: safe(confirm_delete)).classes('bg-red-500 text-white')

        def export_users():
            """导出用户功能（测试）"""
            log_info("开始导出用户数据")
            ui.notify('用户导出功能开发中...', type='info')

        def test_exception_function():
            """测试异常处理功能"""
            log_info("触发测试异常")
            raise ValueError("这是一个测试异常，用于验证异常处理功能")

        # 绑定搜索事件 - 确保事件正确绑定和触发
        search_input.on('input', handle_input_search)  # 实时输入搜索（延迟）
        search_input.on('keydown.enter', handle_search)  # 回车键立即搜索

        # 初始加载
        safe(load_users, error_msg="初始化用户列表失败")

    log_success("===用户管理页面加载完成===")