"""
用户管理页面 - SQLModel 版本
移除 detached_helper 依赖，直接使用 SQLModel 查询
"""
from nicegui import ui
from sqlmodel import Session, select, func
from datetime import datetime, timedelta
import secrets
import string

# 导入模型和数据库
from ..models import User, Role
from ..database import get_db
from ..decorators import require_role
from ..auth_manager import auth_manager
from ..utils import format_datetime, validate_email, validate_username

# 导入日志处理
from common.log_handler import (
    log_trace, log_debug, log_info, log_success, 
    log_warning, log_error, log_critical,
    safe, db_safe, safe_protect, catch, get_logger
)

logger = get_logger(__file__)


@require_role('admin')
@safe_protect(name="用户管理页面", error_msg="用户管理页面加载失败，请稍后重试")
def user_management_page_content():
    """用户管理页面内容 - 仅管理员可访问"""
    
    # 页面标题
    with ui.column().classes('w-full mb-6'):
        ui.label('用户管理').classes('text-4xl font-bold text-blue-800 dark:text-blue-200 mb-2')
        ui.label('管理系统用户账户、角色分配和权限控制').classes('text-lg text-gray-600 dark:text-gray-400')

    # ===========================
    # 统计数据加载
    # ===========================
    
    def load_user_statistics():
        """加载用户统计数据 - SQLModel 版本"""
        with get_db() as session:
            total_users = session.exec(
                select(func.count()).select_from(User)
            ).one()
            
            active_users = session.exec(
                select(func.count()).select_from(User).where(User.is_active == True)
            ).one()
            
            locked_users = session.exec(
                select(func.count()).select_from(User).where(
                    User.locked_until > datetime.now()
                )
            ).one()
            
            superusers = session.exec(
                select(func.count()).select_from(User).where(User.is_superuser == True)
            ).one()
            
            return {
                'total_users': total_users,
                'active_users': active_users,
                'locked_users': locked_users,
                'superusers': superusers
            }
    
    # 安全执行统计数据加载
    stats = safe(
        load_user_statistics,
        return_value={'total_users': 0, 'active_users': 0, 'locked_users': 0, 'superusers': 0},
        error_msg="用户统计数据加载失败"
    )

    # ===========================
    # 统计卡片区域
    # ===========================
    
    with ui.row().classes('w-full gap-6 mb-8'):
        with ui.card().classes('flex-1 p-6 bg-gradient-to-br from-blue-500 to-blue-600 text-white shadow-lg'):
            with ui.row().classes('items-center justify-between w-full'):
                with ui.column().classes('gap-1'):
                    ui.label('总用户数').classes('text-sm opacity-90 font-medium')
                    ui.label(str(stats['total_users'])).classes('text-3xl font-bold')
                ui.icon('group').classes('text-4xl opacity-80')

        with ui.card().classes('flex-1 p-6 bg-gradient-to-br from-green-500 to-green-600 text-white shadow-lg'):
            with ui.row().classes('items-center justify-between w-full'):
                with ui.column().classes('gap-1'):
                    ui.label('活跃用户').classes('text-sm opacity-90 font-medium')
                    ui.label(str(stats['active_users'])).classes('text-3xl font-bold')
                ui.icon('check_circle').classes('text-4xl opacity-80')

        with ui.card().classes('flex-1 p-6 bg-gradient-to-br from-red-500 to-red-600 text-white shadow-lg'):
            with ui.row().classes('items-center justify-between w-full'):
                with ui.column().classes('gap-1'):
                    ui.label('锁定用户').classes('text-sm opacity-90 font-medium')
                    ui.label(str(stats['locked_users'])).classes('text-3xl font-bold')
                ui.icon('lock').classes('text-4xl opacity-80')

        with ui.card().classes('flex-1 p-6 bg-gradient-to-br from-purple-500 to-purple-600 text-white shadow-lg'):
            with ui.row().classes('items-center justify-between w-full'):
                with ui.column().classes('gap-1'):
                    ui.label('管理员').classes('text-sm opacity-90 font-medium')
                    ui.label(str(stats['superusers'])).classes('text-3xl font-bold')
                ui.icon('admin_panel_settings').classes('text-4xl opacity-80')

    # ===========================
    # 搜索和操作区域
    # ===========================
    
    with ui.card().classes('w-full mb-6'):
        with ui.row().classes('w-full items-center gap-4 p-4'):
            search_input = ui.input(
                label='搜索用户', 
                placeholder='输入用户名、邮箱或姓名...'
            ).classes('flex-1')
            
            ui.button(
                '搜索', 
                icon='search',
                on_click=lambda: safe(load_users)
            ).classes('bg-blue-500 text-white')
            
            ui.button(
                '创建用户', 
                icon='person_add',
                on_click=lambda: safe(create_user_dialog)
            ).classes('bg-green-500 text-white')
            
            ui.button(
                '刷新', 
                icon='refresh',
                on_click=lambda: safe(load_users)
            ).classes('bg-gray-500 text-white')

    # ===========================
    # 用户列表表格
    # ===========================
    
    # 创建表格容器
    table_container = ui.column().classes('w-full')
    
    @safe_protect(name="加载用户列表")
    def load_users():
        """加载用户列表 - SQLModel 版本"""
        table_container.clear()
        
        with table_container:
            with get_db() as session:
                # 构建查询
                stmt = select(User)
                
                # 搜索过滤
                if search_input.value:
                    search_term = search_input.value.strip()
                    stmt = stmt.where(
                        (User.username.contains(search_term)) |
                        (User.email.contains(search_term)) |
                        (User.full_name.contains(search_term))
                    )
                
                # 排序
                stmt = stmt.order_by(User.created_at.desc())
                
                # 执行查询
                users = session.exec(stmt).all()
                
                log_info(f"查询到 {len(users)} 个用户")
                
                # 表格列定义
                columns = [
                    {'name': 'id', 'label': 'ID', 'field': 'id', 'align': 'left'},
                    {'name': 'username', 'label': '用户名', 'field': 'username', 'align': 'left'},
                    {'name': 'email', 'label': '邮箱', 'field': 'email', 'align': 'left'},
                    {'name': 'full_name', 'label': '姓名', 'field': 'full_name', 'align': 'left'},
                    {'name': 'roles', 'label': '角色', 'field': 'roles', 'align': 'left'},
                    {'name': 'status', 'label': '状态', 'field': 'status', 'align': 'center'},
                    {'name': 'created_at', 'label': '创建时间', 'field': 'created_at', 'align': 'left'},
                    {'name': 'actions', 'label': '操作', 'field': 'actions', 'align': 'center'},
                ]
                
                # 转换为表格数据
                rows = []
                for user in users:
                    # 获取角色名称列表
                    role_names = [role.name for role in user.roles]
                    
                    # 判断用户状态
                    if user.is_locked():
                        status = '🔒 已锁定'
                        status_color = 'red'
                    elif not user.is_active:
                        status = '❌ 已禁用'
                        status_color = 'orange'
                    else:
                        status = '✅ 正常'
                        status_color = 'green'
                    
                    rows.append({
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'full_name': user.full_name or '-',
                        'roles': ', '.join(role_names) if role_names else '无角色',
                        'status': status,
                        'status_color': status_color,
                        'created_at': format_datetime(user.created_at),
                        'is_superuser': user.is_superuser,
                        'is_locked': user.is_locked(),
                        'is_active': user.is_active,
                    })
                
                # 渲染表格
                with ui.card().classes('w-full'):
                    ui.table(
                        columns=columns,
                        rows=rows,
                        row_key='id'
                    ).classes('w-full').props('flat bordered').style('max-height: 600px')
                    
                    # 为每行添加操作按钮
                    def create_action_buttons(row_data):
                        with ui.row().classes('gap-2'):
                            ui.button(
                                '编辑', 
                                icon='edit',
                                on_click=lambda r=row_data: safe(lambda: edit_user_dialog(r))
                            ).props('size=sm flat dense').classes('text-blue-600')
                            
                            ui.button(
                                '角色', 
                                icon='manage_accounts',
                                on_click=lambda r=row_data: safe(lambda: manage_user_roles_dialog(r))
                            ).props('size=sm flat dense').classes('text-purple-600')
                            
                            if row_data['is_locked']:
                                ui.button(
                                    '解锁', 
                                    icon='lock_open',
                                    on_click=lambda r=row_data: safe(lambda: unlock_user(r['id']))
                                ).props('size=sm flat dense').classes('text-green-600')
                            else:
                                ui.button(
                                    '锁定', 
                                    icon='lock',
                                    on_click=lambda r=row_data: safe(lambda: lock_user_dialog(r))
                                ).props('size=sm flat dense').classes('text-orange-600')
                            
                            if not row_data['is_superuser']:
                                ui.button(
                                    '删除', 
                                    icon='delete',
                                    on_click=lambda r=row_data: safe(lambda: delete_user_dialog(r))
                                ).props('size=sm flat dense').classes('text-red-600')

    # ===========================
    # 创建用户对话框
    # ===========================
    
    @safe_protect(name="创建用户对话框")
    def create_user_dialog():
        """创建用户对话框 - SQLModel 版本"""
        with ui.dialog() as dialog, ui.card().classes('w-96 p-6'):
            ui.label('创建新用户').classes('text-xl font-bold mb-4')
            
            username_input = ui.input(
                label='用户名', 
                placeholder='字母数字下划线，3-50字符'
            ).classes('w-full')
            
            email_input = ui.input(
                label='邮箱', 
                placeholder='user@example.com'
            ).classes('w-full')
            
            password_input = ui.input(
                label='密码', 
                placeholder='至少6个字符',
                password=True,
                password_toggle_button=True
            ).classes('w-full')
            
            full_name_input = ui.input(
                label='姓名（可选）'
            ).classes('w-full')
            
            def submit_create():
                """提交创建 - SQLModel 版本"""
                username = username_input.value.strip()
                email = email_input.value.strip()
                password = password_input.value
                full_name = full_name_input.value.strip() or None
                
                # 验证
                if not username or len(username) < 3:
                    ui.notify('用户名至少3个字符', type='negative')
                    return
                
                if not validate_email(email):
                    ui.notify('邮箱格式不正确', type='negative')
                    return
                
                if not password or len(password) < 6:
                    ui.notify('密码至少6个字符', type='negative')
                    return
                
                # 创建用户
                with get_db() as session:
                    # 检查用户名和邮箱是否已存在
                    existing = session.exec(
                        select(User).where(
                            (User.username == username) | (User.email == email)
                        )
                    ).first()
                    
                    if existing:
                        ui.notify('用户名或邮箱已存在', type='negative')
                        return
                    
                    # 创建新用户
                    new_user = User(
                        username=username,
                        email=email,
                        full_name=full_name,
                        is_active=True
                    )
                    new_user.set_password(password)
                    
                    session.add(new_user)
                    # session.commit() 自动在 get_db() 退出时调用
                    
                    log_success(f"用户创建成功: {username}")
                    ui.notify(f'用户 {username} 创建成功', type='positive')
                    dialog.close()
                    safe(load_users)
            
            with ui.row().classes('w-full justify-end gap-2 mt-6'):
                ui.button('取消', on_click=dialog.close).classes('bg-gray-500 text-white')
                ui.button('创建', on_click=lambda: safe(submit_create)).classes('bg-blue-500 text-white')
        
        dialog.open()

    # ===========================
    # 其他辅助函数
    # ===========================
    
    @safe_protect(name="解锁用户")
    def unlock_user(user_id: int):
        """解锁用户 - SQLModel 版本"""
        with get_db() as session:
            user = session.get(User, user_id)
            if user:
                user.locked_until = None
                user.failed_login_count = 0
                log_info(f"用户解锁成功: {user.username}")
                ui.notify(f'用户 {user.username} 已解锁', type='positive')
                safe(load_users)

    @safe_protect(name="锁定用户对话框")
    def lock_user_dialog(row_data):
        """锁定用户对话框"""
        with ui.dialog() as dialog, ui.card().classes('w-96 p-6'):
            ui.label(f'锁定用户: {row_data["username"]}').classes('text-xl font-bold mb-4')
            
            duration_select = ui.select(
                label='锁定时长',
                options={30: '30分钟', 60: '1小时', 1440: '24小时', 10080: '7天'},
                value=30
            ).classes('w-full')
            
            def submit_lock():
                minutes = duration_select.value
                with get_db() as session:
                    user = session.get(User, row_data['id'])
                    if user:
                        user.locked_until = datetime.now() + timedelta(minutes=minutes)
                        log_warning(f"用户已锁定: {user.username}, 时长: {minutes}分钟")
                        ui.notify(f'用户 {user.username} 已锁定 {minutes} 分钟', type='warning')
                        dialog.close()
                        safe(load_users)
            
            with ui.row().classes('w-full justify-end gap-2 mt-6'):
                ui.button('取消', on_click=dialog.close).classes('bg-gray-500 text-white')
                ui.button('确认锁定', on_click=lambda: safe(submit_lock)).classes('bg-orange-500 text-white')
        
        dialog.open()

    @safe_protect(name="删除用户对话框")
    def delete_user_dialog(row_data):
        """删除用户对话框"""
        with ui.dialog() as dialog, ui.card().classes('w-96 p-6'):
            ui.label(f'删除用户: {row_data["username"]}').classes('text-xl font-bold text-red-600 mb-4')
            ui.label('此操作不可撤销！').classes('text-red-500 mb-4')
            
            def submit_delete():
                with get_db() as session:
                    user = session.get(User, row_data['id'])
                    if user:
                        username = user.username
                        session.delete(user)
                        log_warning(f"用户已删除: {username}")
                        ui.notify(f'用户 {username} 已删除', type='warning')
                        dialog.close()
                        safe(load_users)
            
            with ui.row().classes('w-full justify-end gap-2 mt-6'):
                ui.button('取消', on_click=dialog.close).classes('bg-gray-500 text-white')
                ui.button('确认删除', on_click=lambda: safe(submit_delete)).classes('bg-red-500 text-white')
        
        dialog.open()

    # 初始加载
    safe(load_users)
    log_success("===用户管理页面加载完成===")