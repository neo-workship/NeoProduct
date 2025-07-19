"""
权限管理页面 - 卡片模式布局，与用户管理和角色管理页面保持一致
增加了用户-权限直接关联管理功能
"""
from nicegui import ui
from ..decorators import require_role
from ..auth_manager import auth_manager
from ..detached_helper import (
    detached_manager,
    get_permissions_safe,
    get_permission_safe,
    get_roles_safe,
    get_users_safe,
    update_permission_safe,
    delete_permission_safe,
    create_permission_safe,
    get_permission_direct_users_safe,  # 新增导入
    DetachedPermission,
    DetachedRole,
    DetachedUser
)
from ..models import Permission, Role, User
from ..database import get_db
from datetime import datetime

# 导入异常处理模块
from common.exception_handler import log_info, log_error, safe, db_safe, safe_protect

@require_role('admin')
@safe_protect(name="权限管理页面", error_msg="权限管理页面加载失败，请稍后重试")
def permission_management_page_content():
    """权限管理页面内容 - 仅管理员可访问"""
    log_info("权限管理页面开始加载")
    
    # 页面标题
    with ui.column().classes('w-full mb-6'):
        ui.label('权限管理').classes('text-4xl font-bold text-green-800 dark:text-green-200 mb-2')
        ui.label('管理系统权限和资源访问控制，支持角色和用户关联管理').classes('text-lg text-gray-600 dark:text-gray-400')

    # 权限统计卡片
    def load_permission_statistics():
        """加载权限统计数据"""
        log_info("开始加载权限统计数据")
        permission_stats = detached_manager.get_permission_statistics()
        role_stats = detached_manager.get_role_statistics()
        user_stats = detached_manager.get_user_statistics()
        
        return {
            **permission_stats,
            'total_roles': role_stats['total_roles'],
            'total_users': user_stats['total_users']
        }

    # 安全执行统计数据加载
    stats = safe(
        load_permission_statistics,
        return_value={'total_permissions': 0, 'system_permissions': 0, 'content_permissions': 0, 'total_roles': 0, 'total_users': 0},
        error_msg="权限统计数据加载失败"
    )

    # 统计卡片区域
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
                    ui.label('关联角色').classes('text-sm opacity-90 font-medium')
                    ui.label(str(stats['total_roles'])).classes('text-3xl font-bold')
                ui.icon('group').classes('text-4xl opacity-80')

    # 搜索和筛选区域
    with ui.card().classes('w-full mb-6 p-6 bg-white dark:bg-gray-800 shadow-lg'):
        with ui.row().classes('w-full items-end gap-4'):
            search_input = ui.input('搜索权限', placeholder='权限名称、标识或描述').classes('flex-1')
            category_filter = ui.select(
                options=['全部', '系统', '内容', '分析', '业务', '个人', '其他'],
                label='权限分类',
                value='全部'
            ).classes('w-48')
            
            with ui.row().classes('gap-2'):
                ui.button('搜索', icon='search', on_click=lambda: handle_search()).classes('bg-blue-600 text-white px-4 py-2')
                ui.button('重置', icon='refresh', on_click=lambda: reset_search()).classes('bg-gray-500 text-white px-4 py-2')
                ui.button('添加权限', icon='add', on_click=lambda: add_permission_dialog()).classes('bg-green-600 text-white px-4 py-2')

    # 权限列表容器
    permissions_container = ui.column().classes('w-full gap-4')

    def update_permissions_display():
        """更新权限显示"""
        log_info("开始更新权限显示")
        
        search_term = search_input.value.strip() if search_input.value else None
        category = category_filter.value if category_filter.value != '全部' else None
        
        permissions = safe(
            lambda: get_permissions_safe(search_term=search_term, category=category),
            return_value=[],
            error_msg="权限列表加载失败"
        )
        
        permissions_container.clear()
        load_permissions()
        
        with permissions_container:
            if not permissions:
                search_term = search_input.value.strip() if search_input.value else None
                with ui.card().classes('w-full p-8 text-center bg-gray-50 dark:bg-gray-700'):
                    if search_term:
                        ui.icon('search_off').classes('text-6xl text-gray-400 mb-4')
                        ui.label('未找到匹配的权限').classes('text-lg text-gray-600 dark:text-gray-400 mb-2')
                        ui.label(f'搜索关键词: "{search_term}"').classes('text-sm text-gray-500 dark:text-gray-500')
                    else:
                        ui.icon('security').classes('text-6xl text-gray-400 mb-4')
                        ui.label('暂无权限数据').classes('text-lg text-gray-600 dark:text-gray-400')
                return

            # 权限卡片列表
            for permission_data in permissions:
                create_permission_card(permission_data)

    def create_permission_card(permission_data: DetachedPermission):
        """创建权限卡片"""
        # 确定角色颜色主题
        if permission_data.name == 'system.manage':
            card_theme = 'border-l-4 border-red-500 bg-red-50 dark:bg-red-900/10'
            badge_theme = 'bg-red-100 text-red-800 dark:bg-red-800 dark:text-red-200'
            icon_theme = 'text-red-600 dark:text-red-400'
        elif permission_data.name == 'user':
            card_theme = 'border-l-4 border-green-500 bg-green-50 dark:bg-green-900/10'
            badge_theme = 'bg-green-100 text-green-800 dark:bg-green-800 dark:text-green-200'
            icon_theme = 'text-green-600 dark:text-green-400'
        else:
            card_theme = 'border-l-4 border-blue-500 bg-blue-50 dark:bg-blue-900/10'
            badge_theme = 'bg-blue-100 text-blue-800 dark:bg-blue-800 dark:text-blue-200'
            icon_theme = 'text-blue-600 dark:text-blue-400'
            
        with ui.card().classes(f'w-full {card_theme} shadow-md hover:shadow-lg transition-shadow duration-300'):
            with ui.row().classes('w-full p-4 gap-4'):
                # 左侧：权限基本信息（约占 40%）
                with ui.column().classes('flex-none w-72 gap-2'):
                    # 权限标题和分类
                    with ui.row().classes('items-center gap-3 mb-2'):
                        ui.label(permission_data.display_name or permission_data.name).classes('text-xl font-bold text-gray-800 dark:text-gray-200')
                        
                        # 分类标签
                        category_color = {
                            '系统': 'bg-red-100 text-red-800 dark:bg-red-800 dark:text-red-200',
                            '内容': 'bg-purple-100 text-purple-800 dark:bg-purple-800 dark:text-purple-200',
                            '分析': 'bg-blue-100 text-blue-800 dark:bg-blue-800 dark:text-blue-200',
                            '业务': 'bg-green-100 text-green-800 dark:bg-green-800 dark:text-green-200',
                            '个人': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-800 dark:text-yellow-200'
                        }.get(permission_data.category, 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200')
                        
                        ui.chip(permission_data.category or '其他', icon='label').classes(f'{category_color} text-xs py-1 px-2')

                    # 权限标识符
                    ui.label(f'权限标识: {permission_data.name}').classes('text-sm font-mono bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded text-gray-700 dark:text-gray-300')

                    # 使用状态
                    with ui.row().classes('items-center gap-2 mt-2'):
                        if permission_data.roles_count > 0:
                            if permission_data.roles_count > 1:
                                ui.chip(f'{permission_data.roles_count}个角色', icon='group').classes('bg-green-100 text-green-800 dark:bg-green-800 dark:text-green-200 text-xs py-1 px-2')
                            else:
                                ui.chip('1个角色', icon='person').classes('bg-orange-100 text-orange-800 dark:bg-orange-800 dark:text-orange-200 text-xs py-1 px-2')
                        else:
                            ui.chip('未使用', icon='warning').classes('bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200 text-xs py-1 px-2').tooltip('此权限未被任何角色使用')

                    # 权限描述
                    if permission_data.description:
                        ui.label('描述:').classes('text-xs font-medium text-gray-600 dark:text-gray-400')
                        ui.label(permission_data.description).classes('text-sm text-gray-700 dark:text-gray-300')
                    else:
                        ui.label('暂无描述').classes('text-sm text-gray-500 dark:text-gray-400 italic')

                    # 统计信息
                    with ui.row().classes('gap-2 mt-2'):
                        with ui.card().classes('flex-1 p-2 bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600'):
                            ui.label('权限ID').classes('text-xs text-gray-500 dark:text-gray-400')
                            ui.label(str(permission_data.id)).classes('text-lg font-bold text-blue-600 dark:text-blue-400')
                        
                        with ui.card().classes('flex-1 p-2 bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600'):
                            ui.label('关联角色').classes('text-xs text-gray-500 dark:text-gray-400')
                            ui.label(str(permission_data.roles_count)).classes('text-lg font-bold text-green-600 dark:text-green-400')

                # 右侧：关联管理区域（约占 60%）
                with ui.column().classes('flex-1 gap-2'):
                    # 关联角色区域 - 修改后的版本
                    with ui.column().classes('gap-2'):
                        with ui.row().classes('items-center justify-between w-full'):
                            ui.label(f'关联角色 ({permission_data.roles_count})').classes('text-lg font-bold text-gray-800 dark:text-gray-200')

                        # 角色操作按钮区域 - 只保留添加和删除按钮
                        with ui.card().classes(f'w-full {card_theme} shadow-md hover:shadow-lg transition-shadow duration-300'):
                            with ui.row().classes('gap-2 p-4 justify-center'):
                                ui.button('添加角色', icon='add', 
                                         on_click=lambda: add_roles_to_permission(permission_data)).classes('bg-blue-600 text-white px-4 py-2')
                                ui.button('删除角色', icon='remove', 
                                         on_click=lambda: remove_roles_from_permission(permission_data)).classes('bg-red-600 text-white px-4 py-2')

                    # 关联用户区域 - 修改后的版本
                    with ui.column().classes('gap-2'):
                        # 获取权限直接关联的用户
                        permission_users = safe(
                            lambda: get_permission_direct_users_safe(permission_data.id),
                            return_value=[],
                            error_msg="获取权限关联用户失败"
                        )
                        
                        with ui.row().classes('items-center justify-between w-full'):
                            ui.label(f'关联用户 ({len(permission_users)})').classes('text-lg font-bold text-gray-800 dark:text-gray-200')

                        # 用户操作按钮区域 - 只保留添加和删除按钮
                        with ui.card().classes(f'w-full {card_theme} shadow-md hover:shadow-lg transition-shadow duration-300'):
                            with ui.row().classes('gap-2 p-4 justify-center'):
                                ui.button('添加用户', icon='person_add', 
                                         on_click=lambda: add_users_to_permission(permission_data)).classes('bg-indigo-600 text-white px-4 py-2')
                                ui.button('删除用户', icon='person_remove', 
                                         on_click=lambda: remove_users_from_permission(permission_data)).classes('bg-orange-600 text-white px-4 py-2')

                    # 操作按钮区域
                    with ui.row().classes('gap-2 mt-4 justify-end'):
                        ui.button('编辑权限', icon='edit', 
                                 on_click=lambda: edit_permission_dialog(permission_data)).classes('bg-yellow-600 hover:bg-yellow-700 text-white px-3 py-1')
                        ui.button('删除权限', icon='delete', 
                                 on_click=lambda: delete_permission_confirm(permission_data)).classes('bg-red-600 hover:bg-red-700 text-white px-3 py-1')

    # 处理函数
    def handle_search():
        """处理搜索"""
        log_info(f"权限搜索: {search_input.value}, 分类: {category_filter.value}")
        update_permissions_display()

    def reset_search():
        """重置搜索"""
        search_input.value = ''
        category_filter.value = '全部'
        update_permissions_display()

    search_input.on('keyup.enter', handle_search)

    # 权限CRUD操作
    def add_permission_dialog():
        """添加权限对话框"""
        with ui.dialog() as dialog, ui.card().classes('w-96 p-6'):
            ui.label('添加新权限').classes('text-xl font-bold text-green-600 mb-4')

            name_input = ui.input('权限标识', placeholder='例如: content.create').classes('w-full mb-3')
            display_name_input = ui.input('显示名称', placeholder='例如: 创建内容').classes('w-full mb-3')
            category_select = ui.select(
                options=['系统', '内容', '分析', '业务', '个人', '其他'],
                label='权限分类',
                value='其他'
            ).classes('w-full mb-3')
            description_input = ui.textarea('权限描述', placeholder='详细描述该权限的作用').classes('w-full mb-4')

            with ui.row().classes('w-full gap-2 mt-6 justify-end'):
                ui.button('取消', on_click=dialog.close).classes('bg-gray-500 text-white px-4 py-2')
                ui.button('创建权限', on_click=lambda: create_new_permission()).classes('bg-green-600 text-white px-4 py-2')

            def create_new_permission():
                """创建新权限"""
                if not name_input.value:
                    ui.notify('请输入权限标识', type='warning')
                    return

                log_info(f"开始创建权限: {name_input.value}")
                
                permission_id = safe(
                    lambda: create_permission_safe(
                        name=name_input.value,
                        display_name=display_name_input.value or None,
                        category=category_select.value,
                        description=description_input.value or None
                    ),
                    return_value=None,
                    error_msg="权限创建失败"
                )

                if permission_id:
                    ui.notify('权限创建成功', type='positive')
                    dialog.close()
                    update_permissions_display()
                else:
                    ui.notify('权限创建失败，可能权限标识已存在', type='error')

        dialog.open()

    def edit_permission_dialog(permission_data: DetachedPermission):
        """编辑权限对话框"""
        with ui.dialog() as dialog, ui.card().classes('w-96 p-6'):
            ui.label('编辑权限').classes('text-xl font-bold text-yellow-600 mb-4')

            name_input = ui.input('权限标识', value=permission_data.name).classes('w-full mb-3')
            name_input.enabled = False  # 权限标识不可修改
            
            display_name_input = ui.input('显示名称', value=permission_data.display_name or '').classes('w-full mb-3')
            category_select = ui.select(
                options=['系统', '内容', '分析', '业务', '个人', '其他'],
                label='权限分类',
                value=permission_data.category or '其他'
            ).classes('w-full mb-3')
            description_input = ui.textarea('权限描述', value=permission_data.description or '').classes('w-full mb-4')

            with ui.row().classes('w-full gap-2 mt-6 justify-end'):
                ui.button('取消', on_click=dialog.close).classes('bg-gray-500 text-white px-4 py-2')
                ui.button('保存修改', on_click=lambda: save_permission_changes()).classes('bg-yellow-600 text-white px-4 py-2')

            def save_permission_changes():
                """保存权限修改"""
                log_info(f"开始更新权限: {permission_data.name}")
                
                success = safe(
                    lambda: update_permission_safe(
                        permission_data.id,
                        display_name=display_name_input.value or None,
                        category=category_select.value,
                        description=description_input.value or None
                    ),
                    return_value=False,
                    error_msg="权限更新失败"
                )

                if success:
                    ui.notify('权限更新成功', type='positive')
                    dialog.close()
                    update_permissions_display()
                else:
                    ui.notify('权限更新失败', type='error')

        dialog.open()

    def delete_permission_confirm(permission_data: DetachedPermission):
        """确认删除权限"""
        with ui.dialog() as dialog, ui.card().classes('w-96 p-6'):
            ui.label('确认删除权限').classes('text-xl font-bold text-red-600 mb-4')
            ui.label(f'权限: {permission_data.display_name or permission_data.name}').classes('text-gray-700 mb-2')
            ui.label(f'标识: {permission_data.name}').classes('text-gray-700 mb-2')
            
            if permission_data.roles_count > 0:
                ui.label(f'⚠️ 该权限已关联 {permission_data.roles_count} 个角色，删除后将移除所有关联').classes('text-orange-600 font-medium mt-4')
            
            ui.label('此操作不可撤销，确定要删除吗？').classes('text-red-600 font-medium mt-4')

            with ui.row().classes('w-full gap-2 mt-6 justify-end'):
                ui.button('取消', on_click=dialog.close).classes('bg-gray-500 text-white px-4 py-2')
                ui.button('确认删除', on_click=lambda: execute_delete_permission()).classes('bg-red-600 text-white px-4 py-2')

            def execute_delete_permission():
                """执行删除权限"""
                log_info(f"开始删除权限: {permission_data.name}")
                
                success = safe(
                    lambda: delete_permission_safe(permission_data.id),
                    return_value=False,
                    error_msg="权限删除失败"
                )

                if success:
                    ui.notify('权限删除成功', type='positive')
                    dialog.close()
                    update_permissions_display()
                else:
                    ui.notify('权限删除失败，可能存在关联关系', type='error')

        dialog.open()

    # 角色关联管理 - 添加角色对话框
    def add_roles_to_permission(permission_data: DetachedPermission):
        """为权限添加角色关联"""
        with ui.dialog() as dialog, ui.card().classes('w-lg p-6'):
            ui.label('为权限添加角色').classes('text-xl font-bold text-blue-600 mb-4')
            ui.label(f'权限: {permission_data.display_name or permission_data.name}').classes('text-gray-700 mb-4')

            # 角色选择区域
            selected_roles = set()
            role_search_input = ui.input('搜索角色', placeholder='输入角色名称搜索').classes('w-full mb-4')
            
            with ui.column().classes('w-full max-h-60 overflow-y-auto border border-gray-200 dark:border-gray-600 rounded p-3') as role_list_container:
                pass  # 角色列表将在这里动态生成

            def update_role_list():
                """更新角色列表"""
                search_term = role_search_input.value.strip() if role_search_input.value else None
                
                all_roles = safe(
                    lambda: get_roles_safe(),
                    return_value=[],
                    error_msg="获取角色列表失败"
                )
                
                # 过滤掉已经关联的角色
                available_roles = [role for role in all_roles if role.name not in permission_data.roles]
                
                # 搜索过滤
                if search_term:
                    available_roles = [role for role in available_roles 
                                     if search_term.lower() in role.name.lower() or 
                                        (role.display_name and search_term.lower() in role.display_name.lower())]
                
                role_list_container.clear()
                with role_list_container:
                    if not available_roles:
                        ui.label('没有可添加的角色').classes('text-gray-500 text-center py-4')
                        return
                    
                    for role in available_roles:
                        def create_role_checkbox(r):
                            def on_role_check(checked):
                                if checked:
                                    selected_roles.add(r.id)
                                else:
                                    selected_roles.discard(r.id)
                            
                            with ui.row().classes('items-center gap-3 p-2 hover:bg-gray-50 dark:hover:bg-gray-700 rounded'):
                                ui.checkbox(on_change=on_role_check).classes('flex-none')
                                ui.icon('badge').classes('text-blue-500')
                                with ui.column().classes('gap-1'):
                                    ui.label(r.display_name or r.name).classes('font-medium')
                                    ui.label(f'角色标识: {r.name}').classes('text-sm text-gray-500')
                        
                        create_role_checkbox(role)

            role_search_input.on('input', lambda: update_role_list())

            with ui.row().classes('w-full gap-2 mt-6 justify-end'):
                ui.button('取消', on_click=dialog.close).classes('bg-gray-500 text-white px-4 py-2')
                ui.button('确认添加', on_click=lambda: confirm_update_roles()).classes('bg-blue-600 text-white px-4 py-2')

            def confirm_update_roles():
                """确认更新角色关联"""
                if not selected_roles:
                    ui.notify('请至少选择一个角色', type='warning')
                    return

                log_info(f"开始为权限 {permission_data.name} 添加角色关联: {list(selected_roles)}")
                
                success = safe(
                    lambda: add_permission_to_roles(permission_data.id, list(selected_roles)),
                    return_value=False,
                    error_msg="权限角色关联失败"
                )

                if success:
                    ui.notify('权限角色关联成功', type='positive')
                    dialog.close()
                    update_permissions_display()
                else:
                    ui.notify('权限角色关联失败', type='error')

            # 初始化角色列表
            update_role_list()

        dialog.open()

    # 角色关联管理 - 删除角色对话框（新增）
    def remove_roles_from_permission(permission_data: DetachedPermission):
        """从权限中删除角色关联"""
        with ui.dialog() as dialog, ui.card().classes('w-lg p-6'):
            ui.label('删除权限的角色关联').classes('text-xl font-bold text-red-600 mb-4')
            ui.label(f'权限: {permission_data.display_name or permission_data.name}').classes('text-gray-700 mb-4')

            if not permission_data.roles:
                ui.label('该权限暂无关联角色').classes('text-gray-500 text-center py-4')
                with ui.row().classes('w-full gap-2 mt-6 justify-end'):
                    ui.button('关闭', on_click=dialog.close).classes('bg-gray-500 text-white px-4 py-2')
                dialog.open()
                return

            # 角色选择区域
            selected_roles_to_remove = set()
            role_search_input = ui.input('搜索角色', placeholder='输入角色名称搜索').classes('w-full mb-4')
            
            with ui.column().classes('w-full max-h-60 overflow-y-auto border border-gray-200 dark:border-gray-600 rounded p-3') as role_list_container:
                pass  # 角色列表将在这里动态生成

            def update_role_removal_list():
                """更新可删除的角色列表"""
                search_term = role_search_input.value.strip() if role_search_input.value else None
                
                # 获取已关联的角色
                associated_roles = permission_data.roles
                
                # 搜索过滤
                if search_term:
                    filtered_roles = [role_name for role_name in associated_roles 
                                     if search_term.lower() in role_name.lower()]
                else:
                    filtered_roles = associated_roles
                
                role_list_container.clear()
                with role_list_container:
                    if not filtered_roles:
                        ui.label('没有匹配的角色').classes('text-gray-500 text-center py-4')
                        return
                    
                    for role_name in filtered_roles:
                        def create_role_removal_checkbox(rn):
                            def on_role_check(checked):
                                if checked:
                                    selected_roles_to_remove.add(rn)
                                else:
                                    selected_roles_to_remove.discard(rn)
                            
                            with ui.row().classes('items-center gap-3 p-2 hover:bg-gray-50 dark:hover:bg-gray-700 rounded'):
                                ui.checkbox(on_change=on_role_check).classes('flex-none')
                                ui.icon('badge').classes('text-red-500')
                                ui.label(rn).classes('font-medium')
                        
                        create_role_removal_checkbox(role_name)

            role_search_input.on('input', lambda: update_role_removal_list())

            with ui.row().classes('w-full gap-2 mt-6 justify-end'):
                ui.button('取消', on_click=dialog.close).classes('bg-gray-500 text-white px-4 py-2')
                ui.button('确认删除', on_click=lambda: confirm_remove_roles()).classes('bg-red-600 text-white px-4 py-2')

            def confirm_remove_roles():
                """确认删除角色关联"""
                if not selected_roles_to_remove:
                    ui.notify('请至少选择一个角色', type='warning')
                    return

                log_info(f"开始从权限 {permission_data.name} 删除角色关联: {list(selected_roles_to_remove)}")
                
                success_count = 0
                for role_name in selected_roles_to_remove:
                    success = safe(
                        lambda rn=role_name: remove_permission_from_role(permission_data.id, rn),
                        return_value=False,
                        error_msg=f"删除角色 {role_name} 关联失败"
                    )
                    if success:
                        success_count += 1

                if success_count > 0:
                    ui.notify(f'成功删除 {success_count} 个角色关联', type='positive')
                    dialog.close()
                    update_permissions_display()
                else:
                    ui.notify('删除角色关联失败', type='error')

            # 初始化角色列表
            update_role_removal_list()

        dialog.open()

    # 用户关联管理 - 添加用户对话框
    def add_users_to_permission(permission_data: DetachedPermission):
        """为权限添加用户关联"""
        with ui.dialog() as dialog, ui.card().classes('w-lg p-6'):
            ui.label('为权限添加用户').classes('text-xl font-bold text-indigo-600 mb-4')
            ui.label(f'权限: {permission_data.display_name or permission_data.name}').classes('text-gray-700 mb-4')

            # 用户选择区域
            selected_users = set()
            user_search_input = ui.input('搜索用户', placeholder='输入用户名或邮箱搜索').classes('w-full mb-4')
            
            with ui.column().classes('w-full max-h-60 overflow-y-auto border border-gray-200 dark:border-gray-600 rounded p-3') as user_list_container:
                pass  # 用户列表将在这里动态生成

            def update_user_list():
                """更新用户列表"""
                search_term = user_search_input.value.strip() if user_search_input.value else None
                
                all_users = safe(
                    lambda: get_users_safe(search_term=search_term, limit=100),
                    return_value=[],
                    error_msg="获取用户列表失败"
                )
                
                # 获取已关联的用户ID
                permission_users = safe(
                    lambda: get_permission_direct_users_safe(permission_data.id),
                    return_value=[],
                    error_msg="获取权限关联用户失败"
                )
                existing_user_ids = {user['id'] for user in permission_users}
                
                # 过滤掉已经关联的用户
                available_users = [user for user in all_users if user.id not in existing_user_ids]
                
                user_list_container.clear()
                with user_list_container:
                    if not available_users:
                        ui.label('没有可添加的用户').classes('text-gray-500 text-center py-4')
                        return
                    
                    for user in available_users:
                        def create_user_checkbox(u):
                            def on_user_check(checked):
                                if checked:
                                    selected_users.add(u.id)
                                else:
                                    selected_users.discard(u.id)
                            
                            with ui.row().classes('items-center gap-3 p-2 hover:bg-gray-50 dark:hover:bg-gray-700 rounded'):
                                ui.checkbox(on_change=on_user_check).classes('flex-none')
                                ui.icon('person').classes('text-indigo-500')
                                with ui.column().classes('gap-1'):
                                    ui.label(u.full_name or u.username).classes('font-medium')
                                    ui.label(f'用户名: {u.username} | 邮箱: {u.email}').classes('text-sm text-gray-500')
                        
                        create_user_checkbox(user)

            user_search_input.on('input', lambda: update_user_list())

            with ui.row().classes('w-full gap-2 mt-6 justify-end'):
                ui.button('取消', on_click=dialog.close).classes('bg-gray-500 text-white px-4 py-2')
                ui.button('确认添加', on_click=lambda: confirm_update_users()).classes('bg-indigo-600 text-white px-4 py-2')

            def confirm_update_users():
                """确认更新用户关联"""
                if not selected_users:
                    ui.notify('请至少选择一个用户', type='warning')
                    return

                log_info(f"开始为权限 {permission_data.name} 添加用户关联: {list(selected_users)}")
                
                success = safe(
                    lambda: add_permission_to_users(permission_data.id, list(selected_users)),
                    return_value=False,
                    error_msg="权限用户关联失败"
                )

                if success:
                    ui.notify('权限用户关联成功', type='positive')
                    dialog.close()
                    update_permissions_display()
                else:
                    ui.notify('权限用户关联失败', type='error')

            # 初始化用户列表
            update_user_list()

        dialog.open()

    # 用户关联管理 - 删除用户对话框（新增）
    def remove_users_from_permission(permission_data: DetachedPermission):
        """从权限中删除用户关联"""
        with ui.dialog() as dialog, ui.card().classes('w-lg p-6'):
            ui.label('删除权限的用户关联').classes('text-xl font-bold text-orange-600 mb-4')
            ui.label(f'权限: {permission_data.display_name or permission_data.name}').classes('text-gray-700 mb-4')

            # 获取已关联的用户
            permission_users = safe(
                lambda: get_permission_direct_users_safe(permission_data.id),
                return_value=[],
                error_msg="获取权限关联用户失败"
            )

            if not permission_users:
                ui.label('该权限暂无关联用户').classes('text-gray-500 text-center py-4')
                with ui.row().classes('w-full gap-2 mt-6 justify-end'):
                    ui.button('关闭', on_click=dialog.close).classes('bg-gray-500 text-white px-4 py-2')
                dialog.open()
                return

            # 用户选择区域
            selected_users_to_remove = set()
            user_search_input = ui.input('搜索用户', placeholder='输入用户名或邮箱搜索').classes('w-full mb-4')
            
            with ui.column().classes('w-full max-h-60 overflow-y-auto border border-gray-200 dark:border-gray-600 rounded p-3') as user_list_container:
                pass  # 用户列表将在这里动态生成

            def update_user_removal_list():
                """更新可删除的用户列表"""
                search_term = user_search_input.value.strip() if user_search_input.value else None
                
                # 搜索过滤
                if search_term:
                    filtered_users = [user for user in permission_users 
                                     if search_term.lower() in user['username'].lower() or 
                                        search_term.lower() in (user.get('full_name', '') or '').lower()]
                else:
                    filtered_users = permission_users
                
                user_list_container.clear()
                with user_list_container:
                    if not filtered_users:
                        ui.label('没有匹配的用户').classes('text-gray-500 text-center py-4')
                        return
                    
                    for user_data in filtered_users:
                        def create_user_removal_checkbox(ud):
                            def on_user_check(checked):
                                if checked:
                                    selected_users_to_remove.add(ud['id'])
                                else:
                                    selected_users_to_remove.discard(ud['id'])
                            
                            with ui.row().classes('items-center gap-3 p-2 hover:bg-gray-50 dark:hover:bg-gray-700 rounded'):
                                ui.checkbox(on_change=on_user_check).classes('flex-none')
                                ui.icon('person').classes('text-orange-500')
                                with ui.column().classes('gap-1'):
                                    ui.label(ud.get('full_name') or ud['username']).classes('font-medium')
                                    ui.label(f"用户名: {ud['username']}").classes('text-sm text-gray-500')
                        
                        create_user_removal_checkbox(user_data)

            user_search_input.on('input', lambda: update_user_removal_list())

            with ui.row().classes('w-full gap-2 mt-6 justify-end'):
                ui.button('取消', on_click=dialog.close).classes('bg-gray-500 text-white px-4 py-2')
                ui.button('确认删除', on_click=lambda: confirm_remove_users()).classes('bg-orange-600 text-white px-4 py-2')

            def confirm_remove_users():
                """确认删除用户关联"""
                if not selected_users_to_remove:
                    ui.notify('请至少选择一个用户', type='warning')
                    return

                log_info(f"开始从权限 {permission_data.name} 删除用户关联: {list(selected_users_to_remove)}")
                
                success_count = 0
                for user_id in selected_users_to_remove:
                    success = safe(
                        lambda uid=user_id: remove_permission_from_user(permission_data.id, uid),
                        return_value=False,
                        error_msg=f"删除用户 {user_id} 关联失败"
                    )
                    if success:
                        success_count += 1

                if success_count > 0:
                    ui.notify(f'成功删除 {success_count} 个用户关联', type='positive')
                    dialog.close()
                    update_permissions_display()
                else:
                    ui.notify('删除用户关联失败', type='error')

            # 初始化用户列表
            update_user_removal_list()

        dialog.open()

    # 辅助函数：权限-角色关联操作
    def add_permission_to_roles(permission_id: int, role_ids: list) -> bool:
        """将权限添加到指定角色"""
        try:
            with db_safe("添加权限到角色") as db:
                permission = db.query(Permission).filter(Permission.id == permission_id).first()
                if not permission:
                    return False

                roles = db.query(Role).filter(Role.id.in_(role_ids)).all()
                for role in roles:
                    if permission not in role.permissions:
                        role.permissions.append(permission)

                return True

        except Exception as e:
            log_error(f"添加权限到角色失败: {e}")
            return False

    def remove_permission_from_role(permission_id: int, role_name: str) -> bool:
        """从指定角色中移除权限"""
        try:
            with db_safe("移除权限角色关联") as db:
                permission = db.query(Permission).filter(Permission.id == permission_id).first()
                if not permission:
                    return False

                role = db.query(Role).filter(Role.name == role_name).first()
                if not role:
                    return False

                if permission in role.permissions:
                    role.permissions.remove(permission)

                return True

        except Exception as e:
            log_error(f"移除权限角色关联失败: {e}")
            return False

    # 辅助函数：权限-用户关联操作（新增功能）
    def add_permission_to_users(permission_id: int, user_ids: list) -> bool:
        """将权限直接添加到指定用户 - 使用 detached_helper 中的函数"""
        try:
            success_count = 0
            for user_id in user_ids:
                # 使用 detached_helper 中的函数
                from ..detached_helper import add_permission_to_user_safe
                if add_permission_to_user_safe(user_id, permission_id):
                    success_count += 1
            
            return success_count > 0

        except Exception as e:
            log_error(f"添加权限到用户失败: {e}")
            return False

    def remove_permission_from_user(permission_id: int, user_id: int) -> bool:
        """从指定用户中移除权限 - 使用 detached_helper 中的函数"""
        try:
            from ..detached_helper import remove_permission_from_user_safe
            return remove_permission_from_user_safe(user_id, permission_id)

        except Exception as e:
            log_error(f"移除用户权限关联失败: {e}")
            return False

    # 初始化函数
    def load_permissions():
        """加载权限数据"""
        # 在这里可以添加任何初始化逻辑
        pass

    # 初始加载权限显示
    update_permissions_display()

    log_info("权限管理页面加载完成")