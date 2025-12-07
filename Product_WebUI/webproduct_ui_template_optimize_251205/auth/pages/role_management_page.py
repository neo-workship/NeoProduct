"""
角色管理页面 - 优化版本
使用 ui.table 展示角色,包含完整的操作和用户关联管理功能
"""
from nicegui import ui
from sqlmodel import Session, select, func
from datetime import datetime
import io
import csv

# 导入模型和数据库
from ..models import Role, User, Permission
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
@safe_protect(name="角色管理页面", error_msg="角色管理页面加载失败,请稍后重试")
def role_management_page_content():
    """角色管理页面内容 - 仅管理员可访问"""
    
    # 页面标题
    with ui.column().classes('w-full mb-6'):
        ui.label('角色管理').classes('text-4xl font-bold text-purple-800 dark:text-purple-200 mb-2')
        ui.label('管理系统角色和权限分配,支持用户关联管理').classes('text-lg text-gray-600 dark:text-gray-400')

    # ===========================
    # 统计数据加载
    # ===========================
    
    def load_role_statistics():
        """加载角色统计数据 - SQLModel 版本"""
        with get_db() as session:
            total_roles = session.exec(
                select(func.count()).select_from(Role)
            ).one()
            
            active_roles = session.exec(
                select(func.count()).select_from(Role).where(Role.is_active == True)
            ).one()
            
            system_roles = session.exec(
                select(func.count()).select_from(Role).where(Role.is_system == True)
            ).one()
            
            total_users = session.exec(
                select(func.count()).select_from(User)
            ).one()
            
            return {
                'total_roles': total_roles,
                'active_roles': active_roles,
                'system_roles': system_roles,
                'total_users': total_users
            }
    
    # 安全执行统计数据加载
    stats = safe(
        load_role_statistics,
        return_value={'total_roles': 0, 'active_roles': 0, 'system_roles': 0, 'total_users': 0},
        error_msg="角色统计数据加载失败"
    )

    # ===========================
    # 统计卡片区域
    # ===========================
    
    with ui.row().classes('w-full gap-6 mb-8'):
        with ui.card().classes('flex-1 p-6 bg-gradient-to-br from-purple-500 to-purple-600 text-white shadow-lg'):
            with ui.row().classes('items-center justify-between w-full'):
                with ui.column().classes('gap-1'):
                    ui.label('总角色数').classes('text-sm opacity-90 font-medium')
                    ui.label(str(stats['total_roles'])).classes('text-3xl font-bold')
                ui.icon('group_work').classes('text-4xl opacity-80')

        with ui.card().classes('flex-1 p-6 bg-gradient-to-br from-green-500 to-green-600 text-white shadow-lg'):
            with ui.row().classes('items-center justify-between w-full'):
                with ui.column().classes('gap-1'):
                    ui.label('活跃角色').classes('text-sm opacity-90 font-medium')
                    ui.label(str(stats['active_roles'])).classes('text-3xl font-bold')
                ui.icon('check_circle').classes('text-4xl opacity-80')

        with ui.card().classes('flex-1 p-6 bg-gradient-to-br from-blue-500 to-blue-600 text-white shadow-lg'):
            with ui.row().classes('items-center justify-between w-full'):
                with ui.column().classes('gap-1'):
                    ui.label('系统角色').classes('text-sm opacity-90 font-medium')
                    ui.label(str(stats['system_roles'])).classes('text-3xl font-bold')
                ui.icon('security').classes('text-4xl opacity-80')

        with ui.card().classes('flex-1 p-6 bg-gradient-to-br from-orange-500 to-orange-600 text-white shadow-lg'):
            with ui.row().classes('items-center justify-between w-full'):
                with ui.column().classes('gap-1'):
                    ui.label('总用户数').classes('text-sm opacity-90 font-medium')
                    ui.label(str(stats['total_users'])).classes('text-3xl font-bold')
                ui.icon('group').classes('text-4xl opacity-80')

    # ===========================
    # 操作区域
    # ===========================
    
    with ui.card().classes('w-full mb-6'):
        with ui.row().classes('w-full items-center gap-4 p-4'):
            # ✅ 搜索框
            search_input = ui.input(
                label='搜索角色',
                placeholder='输入角色名称或显示名称...'
            ).classes('flex-1')
            
            ui.button(
                '搜索',
                icon='search',
                on_click=lambda: safe(load_roles)
            ).classes('bg-blue-500 text-white')
            
            ui.button(
                '创建角色', 
                icon='add_circle',
                on_click=lambda: safe(create_role_dialog)
            ).classes('bg-purple-500 text-white')
            
            ui.button(
                '刷新', 
                icon='refresh',
                on_click=lambda: safe(load_roles)
            ).classes('bg-gray-500 text-white')
            
            ui.button(
                '导出角色', 
                icon='download',
                on_click=lambda: safe(export_roles)
            ).classes('bg-blue-500 text-white')

    # ===========================
    # 角色列表表格
    # ===========================
    
    # 创建表格容器
    table_container = ui.column().classes('w-full')
    
    @safe_protect(name="加载角色列表")
    def load_roles():
        """加载角色列表 - SQLModel 版本,使用 ui.table"""
        table_container.clear()
        
        with table_container:
            with get_db() as session:
                # 构建查询
                stmt = select(Role)
                
                # ✅ 搜索过滤 - 支持角色名称和显示名称
                if search_input.value:
                    search_term = search_input.value.strip()
                    stmt = stmt.where(
                        (Role.name.contains(search_term)) |
                        (Role.display_name.contains(search_term))
                    )
                
                # 排序
                stmt = stmt.order_by(Role.created_at.desc())
                
                # 执行查询
                roles = session.exec(stmt).all()
                
                log_info(f"查询到 {len(roles)} 个角色")
                
                # 表格列定义
                columns = [
                    {'name': 'id', 'label': 'ID', 'field': 'id', 'align': 'left', 'sortable': True},
                    {'name': 'name', 'label': '角色名称', 'field': 'name', 'align': 'left', 'sortable': True},
                    {'name': 'display_name', 'label': '显示名称', 'field': 'display_name', 'align': 'left'},
                    {'name': 'description', 'label': '描述', 'field': 'description', 'align': 'left'},
                    {'name': 'permissions', 'label': '权限数', 'field': 'permissions', 'align': 'center', 'sortable': True},
                    {'name': 'users', 'label': '用户数', 'field': 'users', 'align': 'center', 'sortable': True},
                    {'name': 'status', 'label': '状态', 'field': 'status', 'align': 'center'},
                    {'name': 'actions', 'label': '操作', 'field': 'actions', 'align': 'center'},
                    {'name': 'user_actions', 'label': '用户关联', 'field': 'user_actions', 'align': 'center'},
                ]
                
                # 转换为表格数据
                rows = []
                for role in roles:
                    # 计算权限和用户数量
                    permission_count = len(role.permissions)
                    user_count = len(role.users)
                    
                    # 判断角色状态
                    if role.is_system:
                        status = '🔒 系统角色'
                        status_color = 'blue'
                    elif not role.is_active:
                        status = '❌ 已禁用'
                        status_color = 'orange'
                    else:
                        status = '✅ 正常'
                        status_color = 'green'
                    
                    rows.append({
                        'id': role.id,
                        'name': role.name,
                        'display_name': role.display_name or '-',
                        'description': role.description or '-',
                        'permissions': permission_count,
                        'users': user_count,
                        'status': status,
                        'status_color': status_color,
                        'is_system': role.is_system,
                        'is_active': role.is_active,
                    })
                
                # ✅ 渲染带分页的表格
                table = ui.table(
                    columns=columns,
                    rows=rows,
                    row_key='id',
                    pagination={'rowsPerPage': 10, 'sortBy': 'id', 'descending': True},
                    column_defaults={
                        'align': 'left',
                        'headerClasses': 'uppercase text-primary text-base font-bold',
                        'classes': 'text-base'
                    }
                ).classes('w-full')
                
                # ✅ 添加状态列的插槽
                table.add_slot('body-cell-status', '''
                    <q-td key="status" :props="props">
                        <q-badge :color="props.row.status_color">
                            {{ props.row.status }}
                        </q-badge>
                    </q-td>
                ''')
                
                # ✅ 添加操作列的插槽 (查看、编辑、删除)
                table.add_slot('body-cell-actions', '''
                    <q-td key="actions" :props="props">
                        <q-btn flat dense round icon="visibility" color="blue" size="sm"
                               @click="$parent.$emit('view', props.row)">
                            <q-tooltip>查看详情</q-tooltip>
                        </q-btn>
                        <q-btn flat dense round icon="edit" color="purple" size="sm"
                               @click="$parent.$emit('edit', props.row)">
                            <q-tooltip>编辑</q-tooltip>
                        </q-btn>
                        <q-btn flat dense round icon="vpn_key" color="indigo" size="sm"
                               @click="$parent.$emit('permissions', props.row)">
                            <q-tooltip>管理权限</q-tooltip>
                        </q-btn>
                        <q-btn v-if="!props.row.is_system" flat dense round icon="delete" color="red" size="sm"
                               @click="$parent.$emit('delete', props.row)">
                            <q-tooltip>删除</q-tooltip>
                        </q-btn>
                    </q-td>
                ''')
                
                # ✅ 添加用户关联列的插槽 (添加用户、批量删除、批量管理、用户列表)
                table.add_slot('body-cell-user_actions', '''
                    <q-td key="user_actions" :props="props">
                        <q-btn flat dense round icon="person_add" color="green" size="sm"
                               @click="$parent.$emit('add_user', props.row)">
                            <q-tooltip>添加用户</q-tooltip>
                        </q-btn>
                        <q-btn flat dense round icon="people" color="blue" size="sm"
                               @click="$parent.$emit('user_list', props.row)">
                            <q-tooltip>用户列表 ({{ props.row.users }})</q-tooltip>
                        </q-btn>
                        <q-btn flat dense round icon="group_remove" color="orange" size="sm"
                               @click="$parent.$emit('batch_remove', props.row)">
                            <q-tooltip>批量移除</q-tooltip>
                        </q-btn>
                        <q-btn flat dense round icon="manage_accounts" color="purple" size="sm"
                               @click="$parent.$emit('batch_manage', props.row)">
                            <q-tooltip>批量管理</q-tooltip>
                        </q-btn>
                    </q-td>
                ''')
                
                # ✅ 绑定操作事件
                table.on('view', lambda e: safe(lambda: view_role_dialog(e.args)))
                table.on('edit', lambda e: safe(lambda: edit_role_dialog(e.args)))
                table.on('permissions', lambda e: safe(lambda: manage_role_permissions_dialog(e.args)))
                table.on('delete', lambda e: safe(lambda: delete_role_dialog(e.args)))
                
                # ✅ 绑定用户关联事件
                table.on('add_user', lambda e: safe(lambda: add_user_to_role_dialog(e.args)))
                table.on('user_list', lambda e: safe(lambda: view_role_users_dialog(e.args)))
                table.on('batch_remove', lambda e: safe(lambda: batch_remove_users_dialog(e.args)))
                table.on('batch_manage', lambda e: safe(lambda: batch_manage_users_dialog(e.args)))

    # ===========================
    # 创建角色对话框
    # ===========================
    
    @safe_protect(name="创建角色对话框")
    def create_role_dialog():
        """创建角色对话框 - SQLModel 版本"""
        with ui.dialog() as dialog, ui.card().classes('w-96 p-6'):
            ui.label('创建新角色').classes('text-xl font-bold mb-4')
            
            name_input = ui.input(
                label='角色名称', 
                placeholder='小写字母下划线,如: editor'
            ).classes('w-full')
            
            display_name_input = ui.input(
                label='显示名称', 
                placeholder='如: 编辑者'
            ).classes('w-full')
            
            description_input = ui.textarea(
                label='角色描述',
                placeholder='描述此角色的职责和权限范围...'
            ).classes('w-full')
            
            is_active_checkbox = ui.checkbox('启用角色', value=True).classes('mb-2')
            
            def submit_create():
                """提交创建 - SQLModel 版本"""
                name = name_input.value.strip()
                display_name = display_name_input.value.strip()
                description = description_input.value.strip() or None
                is_active = is_active_checkbox.value
                
                # 验证
                if not name or len(name) < 2:
                    ui.notify('角色名称至少2个字符', type='negative')
                    return
                
                if not display_name:
                    ui.notify('请输入显示名称', type='negative')
                    return
                
                # 创建角色
                with get_db() as session:
                    # 检查角色名是否已存在
                    existing = session.exec(
                        select(Role).where(Role.name == name)
                    ).first()
                    
                    if existing:
                        ui.notify('角色名称已存在', type='negative')
                        return
                    
                    # 创建新角色
                    new_role = Role(
                        name=name,
                        display_name=display_name,
                        description=description,
                        is_active=is_active,
                        is_system=False
                    )
                    
                    session.add(new_role)
                    
                    log_success(f"角色创建成功: {name}")
                    ui.notify(f'角色 {display_name} 创建成功', type='positive')
                    dialog.close()
                    safe(load_roles)
            
            with ui.row().classes('w-full justify-end gap-2 mt-6'):
                ui.button('取消', on_click=dialog.close).classes('bg-gray-500 text-white')
                ui.button('创建', on_click=lambda: safe(submit_create)).classes('bg-purple-500 text-white')
        
        dialog.open()

    # ===========================
    # 查看角色详情对话框
    # ===========================
    
    @safe_protect(name="查看角色详情对话框")
    def view_role_dialog(row_data):
        """查看角色详情对话框"""
        with ui.dialog() as dialog, ui.card().classes('w-[600px] p-6'):
            ui.label(f'角色详情: {row_data["display_name"]}').classes('text-xl font-bold mb-4')
            
            with get_db() as session:
                role = session.get(Role, row_data['id'])
                if not role:
                    ui.notify('角色不存在', type='negative')
                    return
                
                # 基本信息
                with ui.card().classes('w-full p-4 mb-4 bg-purple-50 dark:bg-purple-900/20'):
                    ui.label('基本信息').classes('text-lg font-semibold mb-2')
                    
                    with ui.grid(columns=2).classes('w-full gap-4'):
                        with ui.column():
                            ui.label('角色名称').classes('text-sm text-gray-600')
                            ui.label(role.name).classes('text-base font-semibold')
                        
                        with ui.column():
                            ui.label('显示名称').classes('text-sm text-gray-600')
                            ui.label(role.display_name or '-').classes('text-base font-semibold')
                    
                    with ui.column().classes('w-full mt-2'):
                        ui.label('描述').classes('text-sm text-gray-600')
                        ui.label(role.description or '无描述').classes('text-base')
                    
                    with ui.row().classes('w-full gap-4 mt-2'):
                        if role.is_system:
                            ui.badge('系统角色', color='blue')
                        if role.is_active:
                            ui.badge('已启用', color='green')
                        else:
                            ui.badge('已禁用', color='orange')
                
                # 统计信息
                with ui.card().classes('w-full p-4 mb-4 bg-blue-50 dark:bg-blue-900/20'):
                    ui.label('统计信息').classes('text-lg font-semibold mb-2')
                    
                    with ui.row().classes('w-full gap-6'):
                        with ui.column().classes('items-center'):
                            ui.icon('security').classes('text-3xl text-purple-500')
                            ui.label(str(len(role.permissions))).classes('text-2xl font-bold')
                            ui.label('权限数').classes('text-sm text-gray-600')
                        
                        with ui.column().classes('items-center'):
                            ui.icon('group').classes('text-3xl text-blue-500')
                            ui.label(str(len(role.users))).classes('text-2xl font-bold')
                            ui.label('用户数').classes('text-sm text-gray-600')
                
                # 权限列表
                with ui.card().classes('w-full p-4 bg-green-50 dark:bg-green-900/20'):
                    ui.label(f'权限列表 ({len(role.permissions)})').classes('text-lg font-semibold mb-2')
                    
                    if not role.permissions:
                        ui.label('暂无权限').classes('text-gray-500 text-center py-4')
                    else:
                        # 按分类组织权限
                        permissions_by_category = {}
                        for perm in role.permissions:
                            category = perm.category or '其他'
                            if category not in permissions_by_category:
                                permissions_by_category[category] = []
                            permissions_by_category[category].append(perm)
                        
                        with ui.scroll_area().classes('w-full h-48'):
                            for category, perms in sorted(permissions_by_category.items()):
                                ui.label(category).classes('text-sm font-semibold text-purple-700 mt-2')
                                for perm in perms:
                                    with ui.row().classes('items-center gap-2 ml-4'):
                                        ui.icon('check_circle', size='xs').classes('text-green-500')
                                        ui.label(perm.display_name or perm.name).classes('text-sm')
            
            with ui.row().classes('w-full justify-end gap-2 mt-4'):
                ui.button('关闭', on_click=dialog.close).classes('bg-gray-500 text-white')
                ui.button(
                    '编辑',
                    icon='edit',
                    on_click=lambda: (dialog.close(), safe(lambda: edit_role_dialog(row_data)))
                ).classes('bg-purple-500 text-white')
        
        dialog.open()

    # ===========================
    # 编辑角色对话框
    # ===========================
    
    @safe_protect(name="编辑角色对话框")
    def edit_role_dialog(row_data):
        """编辑角色对话框 - SQLModel 版本"""
        with ui.dialog() as dialog, ui.card().classes('w-96 p-6'):
            ui.label(f'编辑角色: {row_data["display_name"]}').classes('text-xl font-bold mb-4')
            
            # 加载角色数据
            with get_db() as session:
                role = session.get(Role, row_data['id'])
                if not role:
                    ui.notify('角色不存在', type='negative')
                    return
                
                display_name_input = ui.input(
                    label='显示名称',
                    value=role.display_name or ''
                ).classes('w-full')
                
                description_input = ui.textarea(
                    label='角色描述',
                    value=role.description or ''
                ).classes('w-full')
                
                is_active_checkbox = ui.checkbox('启用角色', value=role.is_active).classes('mb-2')
                
                if role.is_system:
                    ui.label('⚠️ 系统角色,部分字段不可修改').classes('text-sm text-orange-500 mt-2')
            
            def submit_edit():
                """提交编辑 - SQLModel 版本"""
                with get_db() as session:
                    role = session.get(Role, row_data['id'])
                    if role:
                        role.display_name = display_name_input.value.strip()
                        role.description = description_input.value.strip() or None
                        
                        # 系统角色不能禁用
                        if not role.is_system:
                            role.is_active = is_active_checkbox.value
                        
                        log_info(f"角色更新成功: {role.name}")
                        ui.notify(f'角色 {role.display_name} 更新成功', type='positive')
                        dialog.close()
                        safe(load_roles)
            
            with ui.row().classes('w-full justify-end gap-2 mt-6'):
                ui.button('取消', on_click=dialog.close).classes('bg-gray-500 text-white')
                ui.button('保存', on_click=lambda: safe(submit_edit)).classes('bg-blue-500 text-white')
        
        dialog.open()

    # ===========================
    # 管理角色权限对话框
    # ===========================
    
    @safe_protect(name="管理角色权限对话框")
    def manage_role_permissions_dialog(row_data):
        """管理角色权限对话框 - SQLModel 版本"""
        with ui.dialog() as dialog, ui.card().classes('w-[600px] p-6'):
            ui.label(f'管理权限: {row_data["display_name"]}').classes('text-xl font-bold mb-4')
            
            with get_db() as session:
                role = session.get(Role, row_data['id'])
                if not role:
                    ui.notify('角色不存在', type='negative')
                    return
                
                # 获取所有权限
                all_permissions = session.exec(select(Permission)).all()
                
                # 当前角色的权限 ID 集合
                current_permission_ids = {p.id for p in role.permissions}
                
                # 按分类组织权限
                permissions_by_category = {}
                for perm in all_permissions:
                    category = perm.category or '其他'
                    if category not in permissions_by_category:
                        permissions_by_category[category] = []
                    permissions_by_category[category].append(perm)
                
                # 存储选中的权限
                selected_permissions = set(current_permission_ids)
                
                # 渲染权限选择器
                ui.label(f'当前已关联 {len(current_permission_ids)} 个权限').classes('text-sm text-gray-600 mb-4')
                
                with ui.scroll_area().classes('w-full h-96'):
                    for category, perms in sorted(permissions_by_category.items()):
                        with ui.expansion(category, icon='folder').classes('w-full mb-2'):
                            for perm in perms:
                                is_checked = perm.id in current_permission_ids
                                
                                def on_change(checked, perm_id=perm.id):
                                    if checked:
                                        selected_permissions.add(perm_id)
                                    else:
                                        selected_permissions.discard(perm_id)
                                
                                with ui.row().classes('w-full items-center'):
                                    ui.checkbox(
                                        text=f"{perm.display_name or perm.name} ({perm.name})",
                                        value=is_checked,
                                        on_change=lambda e, pid=perm.id: on_change(e.value, pid)
                                    ).classes('flex-1')
                                    
                                    if perm.description:
                                        ui.icon('info').classes('text-gray-400').tooltip(perm.description)
                
                def submit_permissions():
                    """提交权限更改 - SQLModel 版本"""
                    with get_db() as session:
                        role = session.get(Role, row_data['id'])
                        if role:
                            # 清空现有权限
                            role.permissions.clear()
                            
                            # 添加新权限
                            for perm_id in selected_permissions:
                                perm = session.get(Permission, perm_id)
                                if perm:
                                    role.permissions.append(perm)
                            
                            log_success(f"角色权限更新成功: {role.name}, 权限数: {len(selected_permissions)}")
                            ui.notify(f'角色 {role.display_name} 权限已更新', type='positive')
                            dialog.close()
                            safe(load_roles)
                
                with ui.row().classes('w-full justify-end gap-2 mt-6'):
                    ui.button('取消', on_click=dialog.close).classes('bg-gray-500 text-white')
                    ui.button('保存', on_click=lambda: safe(submit_permissions)).classes('bg-purple-500 text-white')
        
        dialog.open()

    # ===========================
    # 添加用户到角色对话框
    # ===========================
    
    @safe_protect(name="添加用户到角色对话框")
    def add_user_to_role_dialog(row_data):
        """添加用户到角色对话框"""
        with ui.dialog() as dialog, ui.card().classes('w-[500px] p-6'):
            ui.label(f'添加用户: {row_data["display_name"]}').classes('text-xl font-bold mb-4')
            
            with get_db() as session:
                role = session.get(Role, row_data['id'])
                if not role:
                    ui.notify('角色不存在', type='negative')
                    return
                
                # 获取所有用户
                all_users = session.exec(select(User)).all()
                
                # 当前角色的用户 ID 集合
                current_user_ids = {u.id for u in role.users}
                
                # 可添加的用户(不在角色中的用户)
                available_users = [u for u in all_users if u.id not in current_user_ids]
                
                if not available_users:
                    ui.label('所有用户都已添加到此角色').classes('text-gray-500 text-center py-8')
                else:
                    ui.label(f'可添加 {len(available_users)} 个用户').classes('text-sm text-gray-600 mb-4')
                    
                    # 搜索框
                    search_input = ui.input(
                        label='搜索用户',
                        placeholder='输入用户名或邮箱...'
                    ).classes('w-full mb-4')
                    
                    # 存储选中的用户
                    selected_users = set()
                    
                    # 用户列表容器
                    user_list_container = ui.column().classes('w-full')
                    
                    def render_user_list():
                        """渲染用户列表"""
                        user_list_container.clear()
                        
                        # 搜索过滤
                        search_term = search_input.value.strip().lower() if search_input.value else ''
                        filtered_users = [
                            u for u in available_users
                            if not search_term or 
                            search_term in u.username.lower() or 
                            search_term in u.email.lower()
                        ]
                        
                        with user_list_container:
                            with ui.scroll_area().classes('w-full h-96'):
                                for user in filtered_users:
                                    def on_change(checked, user_id=user.id):
                                        if checked:
                                            selected_users.add(user_id)
                                        else:
                                            selected_users.discard(user_id)
                                    
                                    with ui.card().classes('w-full p-3 mb-2'):
                                        with ui.row().classes('w-full items-center justify-between'):
                                            with ui.row().classes('items-center gap-3'):
                                                ui.checkbox(
                                                    value=False,
                                                    on_change=lambda e, uid=user.id: on_change(e.value, uid)
                                                )
                                                
                                                with ui.column().classes('gap-1'):
                                                    ui.label(user.username).classes('font-bold')
                                                    ui.label(user.email).classes('text-xs text-gray-500')
                                            
                                            # 用户状态
                                            if user.is_superuser:
                                                ui.badge('超管', color='red')
                                            elif user.is_active:
                                                ui.badge('正常', color='green')
                                            else:
                                                ui.badge('禁用', color='orange')
                    
                    # 绑定搜索事件
                    search_input.on('input', render_user_list)
                    
                    # 初始渲染
                    render_user_list()
                    
                    def submit_add():
                        """提交添加用户"""
                        if not selected_users:
                            ui.notify('请至少选择一个用户', type='warning')
                            return
                        
                        with get_db() as session:
                            role = session.get(Role, row_data['id'])
                            if role:
                                # 添加新用户
                                for user_id in selected_users:
                                    user = session.get(User, user_id)
                                    if user and user not in role.users:
                                        role.users.append(user)
                                
                                log_success(f"角色添加用户成功: {role.name}, 添加数: {len(selected_users)}")
                                ui.notify(f'成功添加 {len(selected_users)} 个用户到角色 {role.display_name}', type='positive')
                                dialog.close()
                                safe(load_roles)
                    
                    with ui.row().classes('w-full justify-end gap-2 mt-6'):
                        ui.button('取消', on_click=dialog.close).classes('bg-gray-500 text-white')
                        ui.button('添加', on_click=lambda: safe(submit_add)).classes('bg-green-500 text-white')
        
        dialog.open()

    # ===========================
    # 查看角色用户列表对话框
    # ===========================
    
    @safe_protect(name="查看角色用户列表对话框")
    def view_role_users_dialog(row_data):
        """查看角色用户列表对话框 - SQLModel 版本"""
        with ui.dialog() as dialog, ui.card().classes('w-[600px] p-6'):
            ui.label(f'用户列表: {row_data["display_name"]}').classes('text-xl font-bold mb-4')
            
            with get_db() as session:
                role = session.get(Role, row_data['id'])
                if not role:
                    ui.notify('角色不存在', type='negative')
                    return
                
                users = role.users
                
                if not users:
                    ui.label('此角色暂无用户').classes('text-gray-500 text-center py-8')
                else:
                    ui.label(f'共 {len(users)} 个用户').classes('text-sm text-gray-600 mb-4')
                    
                    # 搜索框
                    search_input = ui.input(
                        label='搜索用户',
                        placeholder='输入用户名或邮箱...'
                    ).classes('w-full mb-4')
                    
                    # 用户列表容器
                    user_list_container = ui.column().classes('w-full')
                    
                    def render_user_list():
                        """渲染用户列表"""
                        user_list_container.clear()
                        
                        # 搜索过滤
                        search_term = search_input.value.strip().lower() if search_input.value else ''
                        filtered_users = [
                            u for u in users
                            if not search_term or 
                            search_term in u.username.lower() or 
                            search_term in u.email.lower()
                        ]
                        
                        with user_list_container:
                            with ui.scroll_area().classes('w-full h-96'):
                                for user in filtered_users:
                                    with ui.card().classes('w-full p-4 mb-2'):
                                        with ui.row().classes('w-full items-center justify-between'):
                                            with ui.column().classes('gap-1'):
                                                ui.label(user.username).classes('font-bold')
                                                ui.label(user.email).classes('text-sm text-gray-500')
                                            
                                            with ui.row().classes('gap-2'):
                                                # 用户状态
                                                if user.is_superuser:
                                                    ui.badge('超管', color='red')
                                                elif user.is_active:
                                                    ui.badge('正常', color='green')
                                                else:
                                                    ui.badge('禁用', color='orange')
                                                
                                                # 移除按钮
                                                ui.button(
                                                    icon='person_remove',
                                                    on_click=lambda u=user: safe(lambda: remove_user_from_role(role.id, u.id))
                                                ).props('flat dense round size=sm color=red').tooltip('从角色移除')
                    
                    # 绑定搜索事件
                    search_input.on('input', render_user_list)
                    
                    # 初始渲染
                    render_user_list()
                    
                    def remove_user_from_role(role_id, user_id):
                        """从角色移除用户"""
                        with get_db() as session:
                            role = session.get(Role, role_id)
                            user = session.get(User, user_id)
                            if role and user:
                                if user in role.users:
                                    role.users.remove(user)
                                    log_info(f"从角色移除用户: {user.username} -> {role.name}")
                                    ui.notify(f'用户 {user.username} 已从角色移除', type='positive')
                                    render_user_list()
                                    safe(load_roles)
                
                with ui.row().classes('w-full justify-end gap-2 mt-6'):
                    ui.button('关闭', on_click=dialog.close).classes('bg-gray-500 text-white')
        
        dialog.open()

    # ===========================
    # 批量移除用户对话框
    # ===========================
    
    @safe_protect(name="批量移除用户对话框")
    def batch_remove_users_dialog(row_data):
        """批量移除用户对话框"""
        with ui.dialog() as dialog, ui.card().classes('w-[500px] p-6'):
            ui.label(f'批量移除: {row_data["display_name"]}').classes('text-xl font-bold mb-4')
            
            with get_db() as session:
                role = session.get(Role, row_data['id'])
                if not role:
                    ui.notify('角色不存在', type='negative')
                    return
                
                users = role.users
                
                if not users:
                    ui.label('此角色暂无用户').classes('text-gray-500 text-center py-8')
                else:
                    ui.label(f'选择要移除的用户 (共 {len(users)} 个)').classes('text-sm text-gray-600 mb-4')
                    
                    # 存储选中的用户
                    selected_users = set()
                    
                    with ui.scroll_area().classes('w-full h-96'):
                        for user in users:
                            def on_change(checked, user_id=user.id):
                                if checked:
                                    selected_users.add(user_id)
                                else:
                                    selected_users.discard(user_id)
                            
                            with ui.card().classes('w-full p-3 mb-2'):
                                with ui.row().classes('w-full items-center justify-between'):
                                    with ui.row().classes('items-center gap-3'):
                                        ui.checkbox(
                                            value=False,
                                            on_change=lambda e, uid=user.id: on_change(e.value, uid)
                                        )
                                        
                                        with ui.column().classes('gap-1'):
                                            ui.label(user.username).classes('font-bold')
                                            ui.label(user.email).classes('text-xs text-gray-500')
                                    
                                    # 用户状态
                                    if user.is_superuser:
                                        ui.badge('超管', color='red')
                                    elif user.is_active:
                                        ui.badge('正常', color='green')
                                    else:
                                        ui.badge('禁用', color='orange')
                    
                    def submit_remove():
                        """提交批量移除"""
                        if not selected_users:
                            ui.notify('请至少选择一个用户', type='warning')
                            return
                        
                        with get_db() as session:
                            role = session.get(Role, row_data['id'])
                            if role:
                                # 移除选中的用户
                                removed_count = 0
                                for user_id in selected_users:
                                    user = session.get(User, user_id)
                                    if user and user in role.users:
                                        role.users.remove(user)
                                        removed_count += 1
                                
                                log_success(f"批量移除用户成功: {role.name}, 移除数: {removed_count}")
                                ui.notify(f'成功从角色 {role.display_name} 移除 {removed_count} 个用户', type='positive')
                                dialog.close()
                                safe(load_roles)
                    
                    with ui.row().classes('w-full justify-end gap-2 mt-6'):
                        ui.button('取消', on_click=dialog.close).classes('bg-gray-500 text-white')
                        ui.button('移除', on_click=lambda: safe(submit_remove)).classes('bg-orange-500 text-white')
        
        dialog.open()

    # ===========================
    # 批量管理用户对话框
    # ===========================
    
    @safe_protect(name="批量管理用户对话框")
    def batch_manage_users_dialog(row_data):
        """批量管理用户对话框 - 包含添加和移除"""
        with ui.dialog() as dialog, ui.card().classes('w-[700px] p-6'):
            ui.label(f'批量管理: {row_data["display_name"]}').classes('text-xl font-bold mb-4')
            
            with get_db() as session:
                role = session.get(Role, row_data['id'])
                if not role:
                    ui.notify('角色不存在', type='negative')
                    return
                
                # 获取所有用户
                all_users = session.exec(select(User)).all()
                
                # 当前角色的用户 ID 集合
                current_user_ids = {u.id for u in role.users}
                
                # 存储用户状态变化
                user_changes = {}  # {user_id: True/False} True=添加, False=移除
                
                ui.label(f'管理角色用户 (当前 {len(current_user_ids)} 个)').classes('text-sm text-gray-600 mb-4')
                
                # 搜索框
                search_input = ui.input(
                    label='搜索用户',
                    placeholder='输入用户名或邮箱...'
                ).classes('w-full mb-4')
                
                # 用户列表容器
                user_list_container = ui.column().classes('w-full')
                
                def render_user_list():
                    """渲染用户列表"""
                    user_list_container.clear()
                    
                    # 搜索过滤
                    search_term = search_input.value.strip().lower() if search_input.value else ''
                    filtered_users = [
                        u for u in all_users
                        if not search_term or 
                        search_term in u.username.lower() or 
                        search_term in u.email.lower()
                    ]
                    
                    with user_list_container:
                        with ui.scroll_area().classes('w-full h-96'):
                            for user in filtered_users:
                                # 确定初始状态
                                is_in_role = user.id in current_user_ids
                                
                                def on_change(checked, user_id=user.id, initial=is_in_role):
                                    if checked != initial:
                                        user_changes[user_id] = checked
                                    else:
                                        user_changes.pop(user_id, None)
                                
                                with ui.card().classes('w-full p-3 mb-2'):
                                    with ui.row().classes('w-full items-center justify-between'):
                                        with ui.row().classes('items-center gap-3'):
                                            ui.checkbox(
                                                value=is_in_role,
                                                on_change=lambda e, uid=user.id, init=is_in_role: on_change(e.value, uid, init)
                                            )
                                            
                                            with ui.column().classes('gap-1'):
                                                ui.label(user.username).classes('font-bold')
                                                ui.label(user.email).classes('text-xs text-gray-500')
                                        
                                        with ui.row().classes('gap-2'):
                                            # 用户状态
                                            if user.is_superuser:
                                                ui.badge('超管', color='red')
                                            elif user.is_active:
                                                ui.badge('正常', color='green')
                                            else:
                                                ui.badge('禁用', color='orange')
                                            
                                            # 当前状态
                                            if is_in_role:
                                                ui.badge('已关联', color='blue')
                
                # 绑定搜索事件
                search_input.on('input', render_user_list)
                
                # 初始渲染
                render_user_list()
                
                def submit_batch_manage():
                    """提交批量管理"""
                    if not user_changes:
                        ui.notify('没有变化', type='info')
                        dialog.close()
                        return
                    
                    with get_db() as session:
                        role = session.get(Role, row_data['id'])
                        if role:
                            added_count = 0
                            removed_count = 0
                            
                            for user_id, should_be_in_role in user_changes.items():
                                user = session.get(User, user_id)
                                if user:
                                    if should_be_in_role:
                                        # 添加用户
                                        if user not in role.users:
                                            role.users.append(user)
                                            added_count += 1
                                    else:
                                        # 移除用户
                                        if user in role.users:
                                            role.users.remove(user)
                                            removed_count += 1
                            
                            log_success(f"批量管理用户成功: {role.name}, 添加: {added_count}, 移除: {removed_count}")
                            ui.notify(f'批量管理完成 - 添加 {added_count} 个, 移除 {removed_count} 个', type='positive')
                            dialog.close()
                            safe(load_roles)
                
                with ui.row().classes('w-full justify-end gap-2 mt-6'):
                    ui.button('取消', on_click=dialog.close).classes('bg-gray-500 text-white')
                    ui.button('保存', on_click=lambda: safe(submit_batch_manage)).classes('bg-purple-500 text-white')
        
        dialog.open()

    # ===========================
    # 删除角色对话框
    # ===========================
    
    @safe_protect(name="删除角色对话框")
    def delete_role_dialog(row_data):
        """删除角色对话框 - SQLModel 版本"""
        if row_data['is_system']:
            ui.notify('系统角色不能删除', type='negative')
            return
        
        with ui.dialog() as dialog, ui.card().classes('w-96 p-6'):
            ui.label(f'删除角色: {row_data["display_name"]}').classes('text-xl font-bold text-red-600 mb-4')
            ui.label('此操作将移除所有用户的该角色关联,且不可撤销。').classes('text-sm text-red-500 mt-2')
            
            # 二次确认
            confirm_input = ui.input(
                label=f'请输入角色名 "{row_data["name"]}" 以确认删除',
                placeholder=row_data["name"]
            ).classes('w-full mt-4')
            
            def submit_delete():
                """提交删除 - SQLModel 版本"""
                if confirm_input.value != row_data["name"]:
                    ui.notify('角色名不匹配,删除取消', type='negative')
                    return
                
                with get_db() as session:
                    role = session.get(Role, row_data['id'])
                    if role:
                        role_name = role.display_name
                        session.delete(role)
                        
                        log_warning(f"角色已删除: {role.name}")
                        ui.notify(f'角色 {role_name} 已删除', type='warning')
                        dialog.close()
                        safe(load_roles)
            
            with ui.row().classes('w-full justify-end gap-2 mt-6'):
                ui.button('取消', on_click=dialog.close).classes('bg-gray-500 text-white')
                ui.button('确认删除', on_click=lambda: safe(submit_delete)).classes('bg-red-500 text-white')
        
        dialog.open()

    # ===========================
    # 导出角色功能
    # ===========================
    
    @safe_protect(name="导出角色数据")
    def export_roles():
        """导出角色数据为 CSV"""
        with get_db() as session:
            roles = session.exec(select(Role)).all()
            
            # 创建 CSV
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(['ID', '角色名', '显示名称', '描述', '状态', '系统角色', '权限数', '用户数'])
            
            for role in roles:
                writer.writerow([
                    role.id,
                    role.name,
                    role.display_name or '',
                    role.description or '',
                    '启用' if role.is_active else '禁用',
                    '是' if role.is_system else '否',
                    len(role.permissions),
                    len(role.users)
                ])
            
            ui.notify('角色数据导出功能开发中...', type='info')
            log_info(f"导出了 {len(roles)} 个角色")

    # 初始加载
    safe(load_roles)
    log_success("===角色管理页面加载完成===")