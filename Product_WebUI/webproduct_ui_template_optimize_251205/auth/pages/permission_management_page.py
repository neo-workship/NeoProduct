"""
权限管理页面 - SQLModel 版本
移除 detached_helper 依赖，直接使用 SQLModel 查询
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
@safe_protect(name="权限管理页面", error_msg="权限管理页面加载失败，请稍后重试")
def permission_management_page_content():
    """权限管理页面内容 - 仅管理员可访问"""
    
    # 页面标题
    with ui.column().classes('w-full mb-6'):
        ui.label('权限管理').classes('text-4xl font-bold text-green-800 dark:text-green-200 mb-2')
        ui.label('管理系统权限和资源访问控制，支持角色和用户关联管理').classes('text-lg text-gray-600 dark:text-gray-400')

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
    # 权限列表
    # ===========================
    
    # 创建列表容器
    list_container = ui.column().classes('w-full')
    
    @safe_protect(name="加载权限列表")
    def load_permissions():
        """加载权限列表 - SQLModel 版本"""
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
                
                # 渲染分类卡片
                for category, perms in sorted(permissions_by_category.items()):
                    with ui.expansion(
                        f"{category.upper()} ({len(perms)})", 
                        icon='folder_open'
                    ).classes('w-full mb-4').props('default-opened'):
                        with ui.grid(columns=2).classes('w-full gap-4 p-4'):
                            for perm in perms:
                                render_permission_card(perm)

    def render_permission_card(perm: Permission):
        """渲染单个权限卡片"""
        with ui.card().classes('p-4 hover:shadow-xl transition-shadow'):
            # 权限头部
            with ui.row().classes('w-full items-start justify-between mb-3'):
                with ui.column().classes('gap-1 flex-1'):
                    ui.label(perm.display_name or perm.name).classes('text-lg font-bold text-green-700')
                    ui.label(f"@{perm.name}").classes('text-xs text-gray-500 font-mono')
                
                # 分类标签
                category_colors = {
                    'system': 'blue',
                    'user': 'purple',
                    'content': 'orange',
                }
                color = category_colors.get(perm.category, 'gray')
                ui.badge(perm.category or '其他').props(f'color={color}')
            
            # 描述
            if perm.description:
                ui.label(perm.description).classes('text-sm text-gray-600 mb-3 line-clamp-2')
            
            # 统计信息
            with ui.row().classes('w-full gap-4 mb-3'):
                with ui.column().classes('flex-1 items-center'):
                    ui.icon('group_work').classes('text-xl text-purple-500')
                    ui.label(str(len(perm.roles))).classes('text-lg font-bold')
                    ui.label('角色').classes('text-xs text-gray-500')
                
                with ui.column().classes('flex-1 items-center'):
                    ui.icon('person').classes('text-xl text-blue-500')
                    # 计算直接关联的用户数
                    direct_user_count = len(perm.users)
                    ui.label(str(direct_user_count)).classes('text-lg font-bold')
                    ui.label('直接用户').classes('text-xs text-gray-500')
            
            # 操作按钮
            with ui.row().classes('w-full gap-2'):
                ui.button(
                    '编辑', 
                    icon='edit',
                    on_click=lambda p=perm: safe(lambda: edit_permission_dialog(p))
                ).props('size=sm flat').classes('flex-1 text-blue-600')
                
                ui.button(
                    '角色', 
                    icon='groups',
                    on_click=lambda p=perm: safe(lambda: manage_permission_roles_dialog(p))
                ).props('size=sm flat').classes('flex-1 text-purple-600')
                
                ui.button(
                    '用户', 
                    icon='person_add',
                    on_click=lambda p=perm: safe(lambda: manage_permission_users_dialog(p))
                ).props('size=sm flat').classes('flex-1 text-green-600')
                
                ui.button(
                    '删除', 
                    icon='delete',
                    on_click=lambda p=perm: safe(lambda: delete_permission_dialog(p))
                ).props('size=sm flat').classes('flex-1 text-red-600')

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
    def edit_permission_dialog(perm: Permission):
        """编辑权限对话框 - SQLModel 版本"""
        with ui.dialog() as dialog, ui.card().classes('w-96 p-6'):
            ui.label(f'编辑权限: {perm.display_name or perm.name}').classes('text-xl font-bold mb-4')
            
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
                    permission = session.get(Permission, perm.id)
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
    def manage_permission_roles_dialog(perm: Permission):
        """管理权限-角色关联对话框 - SQLModel 版本"""
        with ui.dialog() as dialog, ui.card().classes('w-[600px] p-6'):
            ui.label(f'管理角色: {perm.display_name or perm.name}').classes('text-xl font-bold mb-4')
            
            with get_db() as session:
                permission = session.get(Permission, perm.id)
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
                        permission = session.get(Permission, perm.id)
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
    def manage_permission_users_dialog(perm: Permission):
        """管理权限-用户直接关联对话框 - SQLModel 版本"""
        with ui.dialog() as dialog, ui.card().classes('w-[600px] p-6'):
            ui.label(f'管理直接用户: {perm.display_name or perm.name}').classes('text-xl font-bold mb-4')
            ui.label('为用户直接分配权限（不通过角色）').classes('text-sm text-gray-600 mb-4')
            
            with get_db() as session:
                permission = session.get(Permission, perm.id)
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
                        permission = session.get(Permission, perm.id)
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
    def delete_permission_dialog(perm: Permission):
        """删除权限对话框 - SQLModel 版本"""
        with ui.dialog() as dialog, ui.card().classes('w-96 p-6'):
            ui.label(f'删除权限: {perm.display_name or perm.name}').classes('text-xl font-bold text-red-600 mb-4')
            ui.label('此操作将移除所有角色和用户的该权限关联，且不可撤销。').classes('text-sm text-red-500 mt-2')
            
            def submit_delete():
                """提交删除 - SQLModel 版本"""
                with get_db() as session:
                    permission = session.get(Permission, perm.id)
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