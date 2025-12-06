"""
角色管理页面 - SQLModel 版本
移除 detached_helper 依赖，直接使用 SQLModel 查询
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
@safe_protect(name="角色管理页面", error_msg="角色管理页面加载失败，请稍后重试")
def role_management_page_content():
    """角色管理页面内容 - 仅管理员可访问"""
    
    # 页面标题
    with ui.column().classes('w-full mb-6'):
        ui.label('角色管理').classes('text-4xl font-bold text-purple-800 dark:text-purple-200 mb-2')
        ui.label('管理系统角色和权限分配，支持用户关联管理').classes('text-lg text-gray-600 dark:text-gray-400')

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
        """加载角色列表 - SQLModel 版本"""
        table_container.clear()
        
        with table_container:
            with get_db() as session:
                # 查询所有角色
                roles = session.exec(
                    select(Role).order_by(Role.created_at.desc())
                ).all()
                
                log_info(f"查询到 {len(roles)} 个角色")
                
                # 表格列定义
                columns = [
                    {'name': 'id', 'label': 'ID', 'field': 'id', 'align': 'left'},
                    {'name': 'name', 'label': '角色名称', 'field': 'name', 'align': 'left'},
                    {'name': 'display_name', 'label': '显示名称', 'field': 'display_name', 'align': 'left'},
                    {'name': 'description', 'label': '描述', 'field': 'description', 'align': 'left'},
                    {'name': 'permissions', 'label': '权限数', 'field': 'permissions', 'align': 'center'},
                    {'name': 'users', 'label': '用户数', 'field': 'users', 'align': 'center'},
                    {'name': 'status', 'label': '状态', 'field': 'status', 'align': 'center'},
                    {'name': 'actions', 'label': '操作', 'field': 'actions', 'align': 'center'},
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
                
                # 渲染表格
                with ui.card().classes('w-full'):
                    # 使用网格布局展示角色卡片
                    with ui.grid(columns=3).classes('w-full gap-4'):
                        for row in rows:
                            with ui.card().classes('p-4 hover:shadow-xl transition-shadow'):
                                # 角色头部
                                with ui.row().classes('w-full items-center justify-between mb-4'):
                                    with ui.column().classes('gap-1'):
                                        ui.label(row['display_name']).classes('text-xl font-bold text-purple-700')
                                        ui.label(f"@{row['name']}").classes('text-sm text-gray-500')
                                    ui.badge(row['status']).props(f'color={row["status_color"]}')
                                
                                # 描述
                                ui.label(row['description']).classes('text-sm text-gray-600 mb-4 line-clamp-2')
                                
                                # 统计信息
                                with ui.row().classes('w-full gap-4 mb-4'):
                                    with ui.column().classes('flex-1 items-center'):
                                        ui.icon('security').classes('text-2xl text-blue-500')
                                        ui.label(str(row['permissions'])).classes('text-lg font-bold')
                                        ui.label('权限').classes('text-xs text-gray-500')
                                    
                                    with ui.column().classes('flex-1 items-center'):
                                        ui.icon('group').classes('text-2xl text-green-500')
                                        ui.label(str(row['users'])).classes('text-lg font-bold')
                                        ui.label('用户').classes('text-xs text-gray-500')
                                
                                # 操作按钮
                                with ui.row().classes('w-full gap-2'):
                                    ui.button(
                                        '编辑', 
                                        icon='edit',
                                        on_click=lambda r=row: safe(lambda: edit_role_dialog(r))
                                    ).props('size=sm flat').classes('flex-1 text-blue-600')
                                    
                                    ui.button(
                                        '权限', 
                                        icon='key',
                                        on_click=lambda r=row: safe(lambda: manage_role_permissions_dialog(r))
                                    ).props('size=sm flat').classes('flex-1 text-purple-600')
                                    
                                    ui.button(
                                        '用户', 
                                        icon='people',
                                        on_click=lambda r=row: safe(lambda: view_role_users_dialog(r))
                                    ).props('size=sm flat').classes('flex-1 text-green-600')
                                    
                                    if not row['is_system']:
                                        ui.button(
                                            '删除', 
                                            icon='delete',
                                            on_click=lambda r=row: safe(lambda: delete_role_dialog(r))
                                        ).props('size=sm flat').classes('flex-1 text-red-600')

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
                placeholder='小写字母下划线，如: editor'
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
                    ui.label('⚠️ 系统角色，部分字段不可修改').classes('text-sm text-orange-500 mt-2')
            
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
    # 查看角色用户对话框
    # ===========================
    
    @safe_protect(name="查看角色用户对话框")
    def view_role_users_dialog(row_data):
        """查看角色用户对话框 - SQLModel 版本"""
        with ui.dialog() as dialog, ui.card().classes('w-[500px] p-6'):
            ui.label(f'角色用户: {row_data["display_name"]}').classes('text-xl font-bold mb-4')
            
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
                    
                    with ui.scroll_area().classes('w-full h-96'):
                        for user in users:
                            with ui.card().classes('w-full p-4 mb-2'):
                                with ui.row().classes('w-full items-center justify-between'):
                                    with ui.column().classes('gap-1'):
                                        ui.label(user.username).classes('font-bold')
                                        ui.label(user.email).classes('text-sm text-gray-500')
                                    
                                    status_icon = '✅' if user.is_active else '❌'
                                    ui.label(status_icon)
                
                with ui.row().classes('w-full justify-end gap-2 mt-6'):
                    ui.button('关闭', on_click=dialog.close).classes('bg-gray-500 text-white')
        
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
            ui.label('此操作将移除所有用户的该角色关联，且不可撤销。').classes('text-sm text-red-500 mt-2')
            
            def submit_delete():
                """提交删除 - SQLModel 版本"""
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