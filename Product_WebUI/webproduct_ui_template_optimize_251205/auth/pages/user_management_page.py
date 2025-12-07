"""
用户管理页面 - 完整功能版本
包含分页、编辑、角色管理、锁定、重置密码、删除等完整功能
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
@safe_protect(name="用户管理页面", error_msg="用户管理页面加载失败,请稍后重试")
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
        """加载用户列表 - SQLModel 版本,带分页"""
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
                    {'name': 'id', 'label': 'ID', 'field': 'id', 'align': 'left', 'sortable': True},
                    {'name': 'username', 'label': '用户名', 'field': 'username', 'align': 'left', 'sortable': True},
                    {'name': 'email', 'label': '邮箱', 'field': 'email', 'align': 'left'},
                    {'name': 'full_name', 'label': '姓名', 'field': 'full_name', 'align': 'left'},
                    {'name': 'roles', 'label': '角色', 'field': 'roles', 'align': 'left'},
                    {'name': 'status', 'label': '状态', 'field': 'status', 'align': 'center'},
                    {'name': 'created_at', 'label': '创建时间', 'field': 'created_at', 'align': 'left', 'sortable': True},
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
                        'created_at': format_datetime(user.created_at)[:10] if user.created_at else '-',
                        'is_superuser': user.is_superuser,
                        'is_locked': user.is_locked(),
                        'is_active': user.is_active,
                    })
                
                # ✅ 渲染带分页的表格
                table = ui.table(
                    columns=columns,
                    rows=rows,
                    row_key='id',
                    pagination={'rowsPerPage': 5, 'sortBy': 'id', 'descending': True},
                    column_defaults={
                        'align': 'left',
                        'headerClasses': 'uppercase text-primary text-base font-bold',
                        'classes': 'text-base'
                    }
                ).classes('w-full')
                
                # ✅ 添加状态列的插槽(使用徽章显示)
                table.add_slot('body-cell-status', '''
                    <q-td key="status" :props="props">
                        <q-badge :color="props.row.status_color">
                            {{ props.row.status }}
                        </q-badge>
                    </q-td>
                ''')
                
                # ✅ 添加操作列的插槽
                table.add_slot('body-cell-actions', '''
                    <q-td key="actions" :props="props">
                        <q-btn flat dense round icon="edit" color="blue" size="sm"
                               @click="$parent.$emit('edit', props.row)">
                            <q-tooltip>编辑</q-tooltip>
                        </q-btn>
                        <q-btn flat dense round icon="manage_accounts" color="purple" size="sm"
                               @click="$parent.$emit('roles', props.row)">
                            <q-tooltip>管理角色</q-tooltip>
                        </q-btn>
                        <q-btn v-if="props.row.is_locked" flat dense round icon="lock_open" color="green" size="sm"
                               @click="$parent.$emit('unlock', props.row)">
                            <q-tooltip>解锁</q-tooltip>
                        </q-btn>
                        <q-btn v-else flat dense round icon="lock" color="orange" size="sm"
                               @click="$parent.$emit('lock', props.row)">
                            <q-tooltip>锁定</q-tooltip>
                        </q-btn>
                        <q-btn flat dense round icon="vpn_key" color="indigo" size="sm"
                               @click="$parent.$emit('reset_password', props.row)">
                            <q-tooltip>重置密码</q-tooltip>
                        </q-btn>
                        <q-btn v-if="!props.row.is_superuser" flat dense round icon="delete" color="red" size="sm"
                               @click="$parent.$emit('delete', props.row)">
                            <q-tooltip>删除</q-tooltip>
                        </q-btn>
                    </q-td>
                ''')
                
                # ✅ 绑定操作事件
                table.on('edit', lambda e: safe(lambda: edit_user_dialog(e.args)))
                table.on('roles', lambda e: safe(lambda: manage_user_roles_dialog(e.args)))
                table.on('unlock', lambda e: safe(lambda: unlock_user(e.args['id'])))
                table.on('lock', lambda e: safe(lambda: lock_user_dialog(e.args)))
                table.on('reset_password', lambda e: safe(lambda: reset_password_dialog(e.args)))
                table.on('delete', lambda e: safe(lambda: delete_user_dialog(e.args)))

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
                placeholder='字母数字下划线,3-50字符'
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
                label='姓名(可选)'
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
                    
                    log_success(f"用户创建成功: {username}")
                    ui.notify(f'用户 {username} 创建成功', type='positive')
                    dialog.close()
                    safe(load_users)
            
            with ui.row().classes('w-full justify-end gap-2 mt-6'):
                ui.button('取消', on_click=dialog.close).classes('bg-gray-500 text-white')
                ui.button('创建', on_click=lambda: safe(submit_create)).classes('bg-blue-500 text-white')
        
        dialog.open()

    # ===========================
    # 编辑用户对话框
    # ===========================
    
    @safe_protect(name="编辑用户对话框")
    def edit_user_dialog(row_data):
        """编辑用户对话框 - SQLModel 版本"""
        with ui.dialog() as dialog, ui.card().classes('w-96 p-6'):
            ui.label(f'编辑用户: {row_data["username"]}').classes('text-xl font-bold mb-4')
            
            # 加载用户数据
            with get_db() as session:
                user = session.get(User, row_data['id'])
                if not user:
                    ui.notify('用户不存在', type='negative')
                    return
                
                email_input = ui.input(
                    label='邮箱',
                    value=user.email
                ).classes('w-full')
                
                full_name_input = ui.input(
                    label='姓名',
                    value=user.full_name or ''
                ).classes('w-full')
                
                phone_input = ui.input(
                    label='电话',
                    value=user.phone or ''
                ).classes('w-full')
                
                is_active_checkbox = ui.checkbox(
                    '启用账户',
                    value=user.is_active
                ).classes('mb-2')
                
                is_verified_checkbox = ui.checkbox(
                    '邮箱已验证',
                    value=user.is_verified
                ).classes('mb-2')
                
                if user.is_superuser:
                    ui.label('⚠️ 超级管理员,部分字段不可修改').classes('text-sm text-orange-500 mt-2')
            
            def submit_edit():
                """提交编辑 - SQLModel 版本"""
                with get_db() as session:
                    user = session.get(User, row_data['id'])
                    if user:
                        # 验证邮箱
                        if not validate_email(email_input.value):
                            ui.notify('邮箱格式不正确', type='negative')
                            return
                        
                        # 检查邮箱是否被其他用户使用
                        existing = session.exec(
                            select(User).where(
                                (User.email == email_input.value) & 
                                (User.id != user.id)
                            )
                        ).first()
                        
                        if existing:
                            ui.notify('邮箱已被其他用户使用', type='negative')
                            return
                        
                        user.email = email_input.value.strip()
                        user.full_name = full_name_input.value.strip() or None
                        user.phone = phone_input.value.strip() or None
                        user.is_verified = is_verified_checkbox.value
                        
                        # 超级管理员不能被禁用
                        if not user.is_superuser:
                            user.is_active = is_active_checkbox.value
                        
                        log_info(f"用户更新成功: {user.username}")
                        ui.notify(f'用户 {user.username} 更新成功', type='positive')
                        dialog.close()
                        safe(load_users)
            
            with ui.row().classes('w-full justify-end gap-2 mt-6'):
                ui.button('取消', on_click=dialog.close).classes('bg-gray-500 text-white')
                ui.button('保存', on_click=lambda: safe(submit_edit)).classes('bg-blue-500 text-white')
        
        dialog.open()

    # ===========================
    # 管理用户角色对话框
    # ===========================
    
    @safe_protect(name="管理用户角色对话框")
    def manage_user_roles_dialog(row_data):
        """管理用户角色对话框 - SQLModel 版本"""
        with ui.dialog() as dialog, ui.card().classes('w-[500px] p-6'):
            ui.label(f'管理角色: {row_data["username"]}').classes('text-xl font-bold mb-4')
            
            with get_db() as session:
                user = session.get(User, row_data['id'])
                if not user:
                    ui.notify('用户不存在', type='negative')
                    return
                
                # 获取所有角色
                all_roles = session.exec(select(Role)).all()
                
                # 当前用户的角色 ID 集合
                current_role_ids = {r.id for r in user.roles}
                
                # 存储选中的角色
                selected_roles = set(current_role_ids)
                
                # 渲染角色选择器
                ui.label(f'当前已关联 {len(current_role_ids)} 个角色').classes('text-sm text-gray-600 mb-4')
                
                with ui.scroll_area().classes('w-full h-96'):
                    for role in all_roles:
                        is_checked = role.id in current_role_ids
                        
                        def on_change(checked, role_id=role.id):
                            if checked:
                                selected_roles.add(role_id)
                            else:
                                selected_roles.discard(role_id)
                        
                        with ui.card().classes('w-full p-3 mb-2'):
                            with ui.row().classes('w-full items-center justify-between'):
                                with ui.row().classes('items-center gap-3'):
                                    ui.checkbox(
                                        value=is_checked,
                                        on_change=lambda e, rid=role.id: on_change(e.value, rid)
                                    )
                                    
                                    with ui.column().classes('gap-1'):
                                        ui.label(role.display_name or role.name).classes('font-bold')
                                        ui.label(f"@{role.name}").classes('text-xs text-gray-500')
                                
                                # 角色标签
                                if role.is_system:
                                    ui.badge('系统').props('color=blue')
                                elif not role.is_active:
                                    ui.badge('禁用').props('color=orange')
                
                def submit_roles():
                    """提交角色更改 - SQLModel 版本"""
                    with get_db() as session:
                        user = session.get(User, row_data['id'])
                        if user:
                            # 清空现有角色
                            user.roles.clear()
                            
                            # 添加新角色
                            for role_id in selected_roles:
                                role = session.get(Role, role_id)
                                if role:
                                    user.roles.append(role)
                            
                            log_success(f"用户角色更新成功: {user.username}, 角色数: {len(selected_roles)}")
                            ui.notify(f'用户 {user.username} 角色已更新', type='positive')
                            dialog.close()
                            safe(load_users)
                
                with ui.row().classes('w-full justify-end gap-2 mt-6'):
                    ui.button('取消', on_click=dialog.close).classes('bg-gray-500 text-white')
                    ui.button('保存', on_click=lambda: safe(submit_roles)).classes('bg-purple-500 text-white')
        
        dialog.open()

    # ===========================
    # 解锁用户
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

    # ===========================
    # 锁定用户对话框
    # ===========================
    
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

    # ===========================
    # 重置密码对话框
    # ===========================
    
    @safe_protect(name="重置密码对话框")
    def reset_password_dialog(row_data):
        """重置密码对话框"""
        with ui.dialog() as dialog, ui.card().classes('w-96 p-6'):
            ui.label(f'重置密码: {row_data["username"]}').classes('text-xl font-bold mb-4')
            
            # 密码生成选项
            with ui.row().classes('w-full gap-2 mb-4'):
                ui.label('密码长度:').classes('text-sm')
                password_length = ui.number(
                    value=12,
                    min=6,
                    max=32
                ).classes('w-24')
            
            # 生成的密码显示
            new_password_input = ui.input(
                label='新密码',
                placeholder='点击生成随机密码',
                password=False
            ).classes('w-full')
            
            def generate_password():
                """生成随机密码"""
                length = int(password_length.value)
                # 包含大小写字母、数字和特殊字符
                chars = string.ascii_letters + string.digits + '!@#$%^&*'
                password = ''.join(secrets.choice(chars) for _ in range(length))
                new_password_input.value = password
                ui.notify('密码已生成', type='info')
            
            ui.button(
                '生成随机密码',
                icon='refresh',
                on_click=generate_password
            ).classes('bg-indigo-500 text-white mb-4')
            
            # 自动生成一个初始密码
            generate_password()
            
            ui.label('⚠️ 请务必保存此密码,重置后无法找回').classes('text-sm text-orange-500')
            
            def submit_reset():
                """提交密码重置"""
                new_password = new_password_input.value
                
                if not new_password or len(new_password) < 6:
                    ui.notify('密码至少6个字符', type='negative')
                    return
                
                with get_db() as session:
                    user = session.get(User, row_data['id'])
                    if user:
                        user.set_password(new_password)
                        
                        # 清除锁定状态
                        user.locked_until = None
                        user.failed_login_count = 0
                        
                        log_warning(f"用户密码已重置: {user.username}")
                        ui.notify(f'用户 {user.username} 密码已重置', type='positive')
                        
                        # 显示密码提示
                        ui.notify(f'新密码: {new_password}', type='info', timeout=10000)
                        
                        dialog.close()
                        safe(load_users)
            
            with ui.row().classes('w-full justify-end gap-2 mt-6'):
                ui.button('取消', on_click=dialog.close).classes('bg-gray-500 text-white')
                ui.button('确认重置', on_click=lambda: safe(submit_reset)).classes('bg-indigo-500 text-white')
        
        dialog.open()

    # ===========================
    # 删除用户对话框
    # ===========================
    
    @safe_protect(name="删除用户对话框")
    def delete_user_dialog(row_data):
        """删除用户对话框"""
        with ui.dialog() as dialog, ui.card().classes('w-96 p-6'):
            ui.label(f'删除用户: {row_data["username"]}').classes('text-xl font-bold text-red-600 mb-4')
            ui.label('此操作不可撤销!').classes('text-red-500 mb-4')
            
            # 二次确认
            confirm_input = ui.input(
                label=f'请输入用户名 "{row_data["username"]}" 以确认删除',
                placeholder=row_data["username"]
            ).classes('w-full')
            
            def submit_delete():
                """提交删除"""
                if confirm_input.value != row_data["username"]:
                    ui.notify('用户名不匹配,删除取消', type='negative')
                    return
                
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