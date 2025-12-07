"""
权限管理页面 - 优化版本
在每个分类的 ui.expansion 中使用 ui.table 展示权限
包含3个操作列: 权限操作、角色操作、用户操作
"""
from nicegui import ui
from sqlmodel import Session, select, func
from datetime import datetime

# 导入模型和数据库
from ..models import Permission, Role, User
from ..database import get_db
from ..decorators import require_role
from ..auth_manager import auth_manager

# 导入日志处理
from common.log_handler import (
    log_trace, log_debug, log_info, log_success, 
    log_warning, log_error, log_critical,
    safe, db_safe, safe_protect, catch, get_logger
)

logger = get_logger(__file__)


@require_role('admin')
@safe_protect(name="权限管理页面", error_msg="权限管理页面加载失败,请稍后重试")
def permission_management_page_content():
    """权限管理页面内容 - 仅管理员可访问"""
    
    # 页面标题
    with ui.column().classes('w-full mb-6'):
        ui.label('权限管理').classes('text-4xl font-bold text-green-800 dark:text-green-200 mb-2')
        ui.label('管理系统权限和资源访问控制,支持角色和用户关联管理').classes('text-lg text-gray-600 dark:text-gray-400')

    # ===========================
    # 统计数据加载
    # ===========================
    
    def load_permission_statistics():
        """加载权限统计数据 - SQLModel 版本"""
        with get_db() as session:
            total_permissions = session.exec(
                select(func.count()).select_from(Permission)
            ).one()
            
            system_permissions = session.exec(
                select(func.count()).select_from(Permission).where(
                    Permission.category == 'system'
                )
            ).one()
            
            content_permissions = session.exec(
                select(func.count()).select_from(Permission).where(
                    Permission.category == 'content'
                )
            ).one()
            
            total_roles = session.exec(
                select(func.count()).select_from(Role)
            ).one()
            
            total_users = session.exec(
                select(func.count()).select_from(User)
            ).one()
            
            return {
                'total_permissions': total_permissions,
                'system_permissions': system_permissions,
                'content_permissions': content_permissions,
                'other_permissions': total_permissions - system_permissions - content_permissions,
                'total_roles': total_roles,
                'total_users': total_users
            }
    
    # 安全执行统计数据加载
    stats = safe(
        load_permission_statistics,
        return_value={
            'total_permissions': 0, 'system_permissions': 0, 
            'content_permissions': 0, 'other_permissions': 0,
            'total_roles': 0, 'total_users': 0
        },
        error_msg="权限统计数据加载失败"
    )

    # ===========================
    # 统计卡片区域
    # ===========================
    
    with ui.row().classes('w-full gap-6 mb-8'):
        with ui.card().classes('flex-1 p-6 bg-gradient-to-br from-green-500 to-green-600 text-white shadow-lg'):
            with ui.row().classes('items-center justify-between w-full'):
                with ui.column().classes('gap-1'):
                    ui.label('总权限数').classes('text-sm opacity-90 font-medium')
                    ui.label(str(stats['total_permissions'])).classes('text-3xl font-bold')
                ui.icon('security').classes('text-4xl opacity-80')

        with ui.card().classes('flex-1 p-6 bg-gradient-to-br from-blue-500 to-blue-600 text-white shadow-lg'):
            with ui.row().classes('items-center justify-between w-full'):
                with ui.column().classes('gap-1'):
                    ui.label('系统权限').classes('text-sm opacity-90 font-medium')
                    ui.label(str(stats['system_permissions'])).classes('text-3xl font-bold')
                ui.icon('admin_panel_settings').classes('text-4xl opacity-80')

        with ui.card().classes('flex-1 p-6 bg-gradient-to-br from-purple-500 to-purple-600 text-white shadow-lg'):
            with ui.row().classes('items-center justify-between w-full'):
                with ui.column().classes('gap-1'):
                    ui.label('内容权限').classes('text-sm opacity-90 font-medium')
                    ui.label(str(stats['content_permissions'])).classes('text-3xl font-bold')
                ui.icon('folder_shared').classes('text-4xl opacity-80')

        with ui.card().classes('flex-1 p-6 bg-gradient-to-br from-orange-500 to-orange-600 text-white shadow-lg'):
            with ui.row().classes('items-center justify-between w-full'):
                with ui.column().classes('gap-1'):
                    ui.label('其他权限').classes('text-sm opacity-90 font-medium')
                    ui.label(str(stats['other_permissions'])).classes('text-3xl font-bold')
                ui.icon('more_horiz').classes('text-4xl opacity-80')

    # ===========================
    # 搜索和操作区域
    # ===========================
    
    with ui.card().classes('w-full mb-6'):
        with ui.row().classes('w-full items-center gap-4 p-4'):
            search_input = ui.input(
                label='搜索权限', 
                placeholder='输入权限名称或描述...'
            ).classes('flex-1')
            
            category_select = ui.select(
                label='分类筛选',
                options={
                    'all': '全部',
                    'system': '系统权限',
                    'user': '用户权限',
                    'content': '内容权限',
                    'other': '其他'
                },
                value='all'
            ).classes('w-48')
            
            ui.button(
                '搜索', 
                icon='search',
                on_click=lambda: safe(load_permissions)
            ).classes('bg-green-500 text-white')
            
            ui.button(
                '创建权限', 
                icon='add_box',
                on_click=lambda: safe(create_permission_dialog)
            ).classes('bg-blue-500 text-white')
            
            ui.button(
                '刷新', 
                icon='refresh',
                on_click=lambda: safe(load_permissions)
            ).classes('bg-gray-500 text-white')

    # ===========================
    # 权限列表 - 按分类展示
    # ===========================
    
    # 创建列表容器
    list_container = ui.column().classes('w-full')
    
    @safe_protect(name="加载权限列表")
    def load_permissions():
        """加载权限列表 - SQLModel 版本,按分类展示"""
        list_container.clear()
        
        with list_container:
            with get_db() as session:
                # 构建查询
                stmt = select(Permission)
                
                # 搜索过滤
                if search_input.value:
                    search_term = search_input.value.strip()
                    stmt = stmt.where(
                        (Permission.name.contains(search_term)) |
                        (Permission.display_name.contains(search_term)) |
                        (Permission.description.contains(search_term))
                    )
                
                # 分类过滤
                if category_select.value != 'all':
                    if category_select.value == 'other':
                        stmt = stmt.where(
                            (Permission.category == None) | 
                            (~Permission.category.in_(['system', 'user', 'content']))
                        )
                    else:
                        stmt = stmt.where(Permission.category == category_select.value)
                
                # 排序
                stmt = stmt.order_by(Permission.category, Permission.name)
                
                # 执行查询
                permissions = session.exec(stmt).all()
                
                log_info(f"查询到 {len(permissions)} 个权限")
                
                if not permissions:
                    with ui.card().classes('w-full p-8 text-center'):
                        ui.icon('inbox', size='64px').classes('text-gray-400 mb-4')
                        ui.label('暂无权限数据').classes('text-xl text-gray-500')
                    return
                
                # 按分类组织权限
                permissions_by_category = {}
                for perm in permissions:
                    category = perm.category or '其他'
                    if category not in permissions_by_category:
                        permissions_by_category[category] = []
                    permissions_by_category[category].append(perm)
                
                # ✅ 为每个分类创建 expansion,内部使用 table 展示
                for category, perms in sorted(permissions_by_category.items()):
                    with ui.expansion(
                        f"{category.upper()} ({len(perms)})", 
                        icon='folder_open'
                    ).classes('w-full mb-4').props('default-opened'):
                        # ✅ 为每个分类创建独立的表格
                        create_category_table(category, perms)

    def create_category_table(category: str, perms: list):
        """为分类创建表格"""
        # 表格列定义
        columns = [
            {'name': 'name', 'label': '权限名称', 'field': 'name', 'align': 'left', 'sortable': True},
            {'name': 'display_name', 'label': '显示名称', 'field': 'display_name', 'align': 'left'},
            {'name': 'description', 'label': '描述', 'field': 'description', 'align': 'left'},
            {'name': 'roles', 'label': '角色数', 'field': 'roles', 'align': 'center', 'sortable': True},
            {'name': 'users', 'label': '用户数', 'field': 'users', 'align': 'center', 'sortable': True},
            {'name': 'perm_actions', 'label': '权限操作', 'field': 'perm_actions', 'align': 'center'},
            {'name': 'role_actions', 'label': '角色操作', 'field': 'role_actions', 'align': 'center'},
            {'name': 'user_actions', 'label': '用户操作', 'field': 'user_actions', 'align': 'center'},
        ]
        
        # 转换为表格数据
        rows = []
        for perm in perms:
            rows.append({
                'id': perm.id,
                'name': perm.name,
                'display_name': perm.display_name or '-',
                'description': perm.description or '-',
                'roles': len(perm.roles),
                'users': len(perm.users),
            })
        
        # ✅ 创建表格
        table = ui.table(
            columns=columns,
            rows=rows,
            row_key='id',
            pagination={'rowsPerPage': 10, 'sortBy': 'name'},
            column_defaults={
                        'align': 'left',
                        'headerClasses': 'uppercase text-primary text-base font-bold',
                        'classes': 'text-base'
            }
        ).classes('w-full')
        
        # ✅ 添加权限操作列的插槽
        table.add_slot('body-cell-perm_actions', '''
            <q-td key="perm_actions" :props="props">
                <q-btn flat dense round icon="edit" color="blue" size="sm"
                       @click="$parent.$emit('edit_perm', props.row)">
                    <q-tooltip>编辑权限</q-tooltip>
                </q-btn>
                <q-btn flat dense round icon="delete" color="red" size="sm"
                       @click="$parent.$emit('delete_perm', props.row)">
                    <q-tooltip>删除权限</q-tooltip>
                </q-btn>
            </q-td>
        ''')
        
        # ✅ 添加角色操作列的插槽
        table.add_slot('body-cell-role_actions', '''
            <q-td key="role_actions" :props="props">
                <q-btn flat dense round icon="add_circle" color="purple" size="sm"
                       @click="$parent.$emit('add_role', props.row)">
                    <q-tooltip>添加角色 ({{ props.row.roles }})</q-tooltip>
                </q-btn>
                <q-btn flat dense round icon="remove_circle" color="orange" size="sm"
                       @click="$parent.$emit('remove_role', props.row)">
                    <q-tooltip>删除角色</q-tooltip>
                </q-btn>
            </q-td>
        ''')
        
        # ✅ 添加用户操作列的插槽
        table.add_slot('body-cell-user_actions', '''
            <q-td key="user_actions" :props="props">
                <q-btn flat dense round icon="person_add" color="green" size="sm"
                       @click="$parent.$emit('add_user', props.row)">
                    <q-tooltip>添加用户 ({{ props.row.users }})</q-tooltip>
                </q-btn>
                <q-btn flat dense round icon="person_remove" color="red" size="sm"
                       @click="$parent.$emit('remove_user', props.row)">
                    <q-tooltip>删除用户</q-tooltip>
                </q-btn>
            </q-td>
        ''')
        
        # ✅ 绑定操作事件
        table.on('edit_perm', lambda e: safe(lambda: edit_permission_dialog(e.args)))
        table.on('delete_perm', lambda e: safe(lambda: delete_permission_dialog(e.args)))
        table.on('add_role', lambda e: safe(lambda: manage_permission_roles_dialog(e.args)))
        table.on('remove_role', lambda e: safe(lambda: manage_permission_roles_dialog(e.args)))
        table.on('add_user', lambda e: safe(lambda: manage_permission_users_dialog(e.args)))
        table.on('remove_user', lambda e: safe(lambda: manage_permission_users_dialog(e.args)))

    # ===========================
    # 创建权限对话框
    # ===========================
    
    @safe_protect(name="创建权限对话框")
    def create_permission_dialog():
        """创建权限对话框 - SQLModel 版本"""
        with ui.dialog() as dialog, ui.card().classes('w-96 p-6'):
            ui.label('创建新权限').classes('text-xl font-bold mb-4')
            
            name_input = ui.input(
                label='权限名称', 
                placeholder='如: user.create'
            ).classes('w-full')
            
            display_name_input = ui.input(
                label='显示名称', 
                placeholder='如: 创建用户'
            ).classes('w-full')
            
            category_input = ui.select(
                label='权限分类',
                options=['system', 'user', 'content', 'other'],
                value='other'
            ).classes('w-full')
            
            description_input = ui.textarea(
                label='权限描述',
                placeholder='描述此权限的作用和使用场景...'
            ).classes('w-full')
            
            def submit_create():
                """提交创建 - SQLModel 版本"""
                name = name_input.value.strip()
                display_name = display_name_input.value.strip()
                category = category_input.value
                description = description_input.value.strip() or None
                
                # 验证
                if not name or len(name) < 3:
                    ui.notify('权限名称至少3个字符', type='negative')
                    return
                
                if not display_name:
                    ui.notify('请输入显示名称', type='negative')
                    return
                
                # 创建权限
                with get_db() as session:
                    # 检查权限名是否已存在
                    existing = session.exec(
                        select(Permission).where(Permission.name == name)
                    ).first()
                    
                    if existing:
                        ui.notify('权限名称已存在', type='negative')
                        return
                    
                    # 创建新权限
                    new_permission = Permission(
                        name=name,
                        display_name=display_name,
                        category=category if category != 'other' else None,
                        description=description
                    )
                    
                    session.add(new_permission)
                    
                    log_success(f"权限创建成功: {name}")
                    ui.notify(f'权限 {display_name} 创建成功', type='positive')
                    dialog.close()
                    safe(load_permissions)
            
            with ui.row().classes('w-full justify-end gap-2 mt-6'):
                ui.button('取消', on_click=dialog.close).classes('bg-gray-500 text-white')
                ui.button('创建', on_click=lambda: safe(submit_create)).classes('bg-green-500 text-white')
        
        dialog.open()

    # ===========================
    # 编辑权限对话框
    # ===========================
    
    @safe_protect(name="编辑权限对话框")
    def edit_permission_dialog(row_data):
        """编辑权限对话框 - SQLModel 版本"""
        with ui.dialog() as dialog, ui.card().classes('w-96 p-6'):
            ui.label(f'编辑权限: {row_data["display_name"]}').classes('text-xl font-bold mb-4')
            
            # 加载权限数据
            with get_db() as session:
                perm = session.get(Permission, row_data['id'])
                if not perm:
                    ui.notify('权限不存在', type='negative')
                    return
                
                display_name_input = ui.input(
                    label='显示名称',
                    value=perm.display_name or ''
                ).classes('w-full')
                
                category_input = ui.select(
                    label='权限分类',
                    options=['system', 'user', 'content', 'other'],
                    value=perm.category or 'other'
                ).classes('w-full')
                
                description_input = ui.textarea(
                    label='权限描述',
                    value=perm.description or ''
                ).classes('w-full')
                
                ui.label('⚠️ 权限名称不可修改').classes('text-sm text-orange-500 mt-2')
            
            def submit_edit():
                """提交编辑 - SQLModel 版本"""
                with get_db() as session:
                    permission = session.get(Permission, row_data['id'])
                    if permission:
                        permission.display_name = display_name_input.value.strip()
                        permission.category = category_input.value if category_input.value != 'other' else None
                        permission.description = description_input.value.strip() or None
                        
                        log_info(f"权限更新成功: {permission.name}")
                        ui.notify(f'权限 {permission.display_name} 更新成功', type='positive')
                        dialog.close()
                        safe(load_permissions)
            
            with ui.row().classes('w-full justify-end gap-2 mt-6'):
                ui.button('取消', on_click=dialog.close).classes('bg-gray-500 text-white')
                ui.button('保存', on_click=lambda: safe(submit_edit)).classes('bg-blue-500 text-white')
        
        dialog.open()

    # ===========================
    # 管理权限-角色关联对话框
    # ===========================
    
    @safe_protect(name="管理权限角色对话框")
    def manage_permission_roles_dialog(row_data):
        """管理权限-角色关联对话框 - SQLModel 版本"""
        with ui.dialog() as dialog, ui.card().classes('w-[600px] p-6'):
            ui.label(f'管理角色: {row_data["display_name"]}').classes('text-xl font-bold mb-4')
            
            with get_db() as session:
                permission = session.get(Permission, row_data['id'])
                if not permission:
                    ui.notify('权限不存在', type='negative')
                    return
                
                # 获取所有角色
                all_roles = session.exec(select(Role)).all()
                
                # 当前权限的角色 ID 集合
                current_role_ids = {r.id for r in permission.roles}
                
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
                        permission = session.get(Permission, row_data['id'])
                        if permission:
                            # 清空现有角色
                            permission.roles.clear()
                            
                            # 添加新角色
                            for role_id in selected_roles:
                                role = session.get(Role, role_id)
                                if role:
                                    permission.roles.append(role)
                            
                            log_success(f"权限角色更新成功: {permission.name}, 角色数: {len(selected_roles)}")
                            ui.notify(f'权限 {permission.display_name} 角色已更新', type='positive')
                            dialog.close()
                            safe(load_permissions)
                
                with ui.row().classes('w-full justify-end gap-2 mt-6'):
                    ui.button('取消', on_click=dialog.close).classes('bg-gray-500 text-white')
                    ui.button('保存', on_click=lambda: safe(submit_roles)).classes('bg-purple-500 text-white')
        
        dialog.open()

    # ===========================
    # 管理权限-用户关联对话框
    # ===========================
    
    @safe_protect(name="管理权限用户对话框")
    def manage_permission_users_dialog(row_data):
        """管理权限-用户直接关联对话框 - SQLModel 版本"""
        with ui.dialog() as dialog, ui.card().classes('w-[600px] p-6'):
            ui.label(f'管理直接用户: {row_data["display_name"]}').classes('text-xl font-bold mb-4')
            ui.label('为用户直接分配权限(不通过角色)').classes('text-sm text-gray-600 mb-4')
            
            with get_db() as session:
                permission = session.get(Permission, row_data['id'])
                if not permission:
                    ui.notify('权限不存在', type='negative')
                    return
                
                # 获取所有用户
                all_users = session.exec(select(User)).all()
                
                # 当前权限的直接用户 ID 集合
                current_user_ids = {u.id for u in permission.users}
                
                # 存储选中的用户
                selected_users = set(current_user_ids)
                
                # 渲染用户选择器
                ui.label(f'当前已直接关联 {len(current_user_ids)} 个用户').classes('text-sm text-gray-600 mb-4')
                
                with ui.scroll_area().classes('w-full h-96'):
                    for user in all_users:
                        is_checked = user.id in current_user_ids
                        
                        def on_change(checked, user_id=user.id):
                            if checked:
                                selected_users.add(user_id)
                            else:
                                selected_users.discard(user_id)
                        
                        with ui.card().classes('w-full p-3 mb-2'):
                            with ui.row().classes('w-full items-center justify-between'):
                                with ui.row().classes('items-center gap-3'):
                                    ui.checkbox(
                                        value=is_checked,
                                        on_change=lambda e, uid=user.id: on_change(e.value, uid)
                                    )
                                    
                                    with ui.column().classes('gap-1'):
                                        ui.label(user.username).classes('font-bold')
                                        ui.label(user.email).classes('text-xs text-gray-500')
                                
                                # 用户状态
                                if user.is_superuser:
                                    ui.badge('超管').props('color=red')
                                elif not user.is_active:
                                    ui.badge('禁用').props('color=orange')
                                else:
                                    ui.badge('正常').props('color=green')
                
                def submit_users():
                    """提交用户更改 - SQLModel 版本"""
                    with get_db() as session:
                        permission = session.get(Permission, row_data['id'])
                        if permission:
                            # 清空现有直接用户
                            permission.users.clear()
                            
                            # 添加新用户
                            for user_id in selected_users:
                                user = session.get(User, user_id)
                                if user:
                                    permission.users.append(user)
                            
                            log_success(f"权限直接用户更新成功: {permission.name}, 用户数: {len(selected_users)}")
                            ui.notify(f'权限 {permission.display_name} 直接用户已更新', type='positive')
                            dialog.close()
                            safe(load_permissions)
                
                with ui.row().classes('w-full justify-end gap-2 mt-6'):
                    ui.button('取消', on_click=dialog.close).classes('bg-gray-500 text-white')
                    ui.button('保存', on_click=lambda: safe(submit_users)).classes('bg-green-500 text-white')
        
        dialog.open()

    # ===========================
    # 删除权限对话框
    # ===========================
    
    @safe_protect(name="删除权限对话框")
    def delete_permission_dialog(row_data):
        """删除权限对话框 - SQLModel 版本"""
        with ui.dialog() as dialog, ui.card().classes('w-96 p-6'):
            ui.label(f'删除权限: {row_data["display_name"]}').classes('text-xl font-bold text-red-600 mb-4')
            ui.label('此操作将移除所有角色和用户的该权限关联,且不可撤销。').classes('text-sm text-red-500 mt-2')
            
            # 二次确认
            confirm_input = ui.input(
                label=f'请输入权限名 "{row_data["name"]}" 以确认删除',
                placeholder=row_data["name"]
            ).classes('w-full mt-4')
            
            def submit_delete():
                """提交删除 - SQLModel 版本"""
                if confirm_input.value != row_data["name"]:
                    ui.notify('权限名不匹配,删除取消', type='negative')
                    return
                
                with get_db() as session:
                    permission = session.get(Permission, row_data['id'])
                    if permission:
                        perm_name = permission.display_name or permission.name
                        session.delete(permission)
                        
                        log_warning(f"权限已删除: {permission.name}")
                        ui.notify(f'权限 {perm_name} 已删除', type='warning')
                        dialog.close()
                        safe(load_permissions)
            
            with ui.row().classes('w-full justify-end gap-2 mt-6'):
                ui.button('取消', on_click=dialog.close).classes('bg-gray-500 text-white')
                ui.button('确认删除', on_click=lambda: safe(submit_delete)).classes('bg-red-500 text-white')
        
        dialog.open()

    # 初始加载
    safe(load_permissions)
    log_success("===权限管理页面加载完成===")