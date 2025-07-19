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
                ui.icon('content_paste').classes('text-4xl opacity-80')

        with ui.card().classes('flex-1 p-6 bg-gradient-to-br from-orange-500 to-orange-600 text-white shadow-lg'):
            with ui.row().classes('items-center justify-between w-full'):
                with ui.column().classes('gap-1'):
                    ui.label('系统用户').classes('text-sm opacity-90 font-medium')
                    ui.label(str(stats['total_users'])).classes('text-3xl font-bold')
                ui.icon('group').classes('text-4xl opacity-80')

    # 搜索和操作栏
    with ui.row().classes('w-full gap-2 mb-6 items-end'):
        search_input = ui.input('搜索权限', placeholder='输入权限名称或分类搜索').classes('flex-1')
        category_filter = ui.select(
            options=['全部', '系统', '内容', '分析', '业务', '个人', '其他'],
            value='全部',
            label='权限分类'
        ).classes('w-32')
        search_btn = ui.button('搜索', icon='search', on_click=lambda: handle_search()).classes('bg-blue-600 hover:bg-blue-700 text-white px-3 py-1')
        reset_btn = ui.button('重置', icon='refresh', on_click=lambda: reset_search()).classes('bg-gray-500 hover:bg-gray-600 text-white px-3 py-1')
        add_btn = ui.button('添加权限', icon='add', on_click=lambda: add_permission_dialog()).classes('bg-green-600 hover:bg-green-700 text-white px-3 py-1')

    # 权限卡片容器
    with ui.column().classes('w-full') as permissions_container:
        pass

    # 权限操作函数
    def load_permissions():
        """加载权限列表"""
        search_term = search_input.value.strip() if search_input.value else None
        category = category_filter.value if category_filter.value != '全部' else None
        
        return safe(
            lambda: get_permissions_safe(search_term=search_term, category=category),
            return_value=[],
            error_msg="权限列表加载失败"
        )

    def update_permissions_display():
        """更新权限显示"""
        permissions_container.clear()
        permissions = load_permissions()
        
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
            with ui.row().classes('w-full gap-6'):
                # 左侧：权限基本信息（约占 40%）
                with ui.column().classes('flex-none w-2/5 gap-3'):
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
                with ui.column().classes('flex-1 gap-4'):
                    # 关联角色区域
                    with ui.column().classes('gap-2'):
                        with ui.row().classes('items-center justify-between w-full'):
                            ui.label(f'关联角色 ({permission_data.roles_count})').classes('text-lg font-bold text-gray-800 dark:text-gray-200')

                        # 角色展示区域
                        with ui.card().classes('w-full p-3 bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 min-h-[120px]'):
                            if permission_data.roles:
                                # 角色芯片区域
                                with ui.column().classes('w-full gap-2'):
                                    with ui.row().classes('gap-2 flex-wrap'):
                                        for role_name in permission_data.roles:
                                            role_color = 'red' if role_name == 'admin' else 'blue' if role_name == 'user' else 'green'
                                            # 创建可删除的角色芯片
                                            with ui.card().classes(f'px-3 py-1 bg-{role_color}-100 border border-{role_color}-300 flex-none'):
                                                with ui.row().classes('items-center gap-2 no-wrap'):
                                                    ui.icon('badge').classes(f'text-{role_color}-600 text-sm')
                                                    ui.label(role_name).classes(f'text-{role_color}-800 text-sm font-medium')
                                                    ui.button(icon='close', on_click=lambda r=role_name: remove_role_from_permission(permission_data, r)).classes(f'text-{role_color}-600 hover:text-{role_color}-800 p-0 w-4 h-4').props('flat dense round size=xs')

                                    # 角色操作按钮
                                    with ui.row().classes('gap-2 mt-3'):
                                        ui.button('添加角色', icon='add', on_click=lambda: add_roles_to_permission(permission_data)).classes('bg-blue-600 text-white px-3 py-1 text-sm')
                                        if permission_data.roles:
                                            ui.button('移除所有', icon='clear_all', on_click=lambda: remove_all_roles_confirm(permission_data)).classes('bg-orange-600 text-white px-3 py-1 text-sm')
                            else:
                                # 无角色状态
                                with ui.column().classes('w-full items-center justify-center py-6'):
                                    ui.icon('group_off').classes('text-3xl text-gray-400 mb-2')
                                    ui.label('暂无关联角色').classes('text-gray-500 dark:text-gray-400 mb-3')
                                    ui.button('添加角色', icon='add', on_click=lambda: add_roles_to_permission(permission_data)).classes('bg-blue-600 text-white px-3 py-1')

                    # 关联用户区域（新增功能）
                    with ui.column().classes('gap-2'):
                        # 获取权限直接关联的用户 - 使用 detached_helper 中的函数
                        permission_users = safe(
                            lambda: get_permission_direct_users_safe(permission_data.id),
                            return_value=[],
                            error_msg="获取权限关联用户失败"
                        )
                        
                        with ui.row().classes('items-center justify-between w-full'):
                            ui.label(f'关联用户 ({len(permission_users)})').classes('text-lg font-bold text-gray-800 dark:text-gray-200')

                        # 用户展示区域
                        with ui.card().classes('w-full p-3 bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 min-h-[120px]'):
                            if permission_users:
                                # 用户芯片区域
                                with ui.column().classes('w-full gap-2'):
                                    with ui.row().classes('gap-2 flex-wrap'):
                                        for user_data in permission_users:
                                            # 创建可删除的用户芯片
                                            with ui.card().classes('px-3 py-1 bg-indigo-100 border border-indigo-300 flex-none'):
                                                with ui.row().classes('items-center gap-2 no-wrap'):
                                                    ui.icon('person').classes('text-indigo-600 text-sm')
                                                    ui.label(user_data['username']).classes('text-indigo-800 text-sm font-medium')
                                                    ui.button(icon='close', on_click=lambda u=user_data: remove_user_from_permission(permission_data, u)).classes('text-indigo-600 hover:text-indigo-800 p-0 w-4 h-4').props('flat dense round size=xs')

                                    # 用户操作按钮
                                    with ui.row().classes('gap-2 mt-3'):
                                        ui.button('添加用户', icon='person_add', on_click=lambda: add_users_to_permission(permission_data)).classes('bg-indigo-600 text-white px-3 py-1 text-sm')
                                        if permission_users:
                                            ui.button('移除所有', icon='person_remove', on_click=lambda: remove_all_users_confirm(permission_data)).classes('bg-orange-600 text-white px-3 py-1 text-sm')
                            else:
                                # 无用户状态
                                with ui.column().classes('w-full items-center justify-center py-6'):
                                    ui.icon('person_off').classes('text-3xl text-gray-400 mb-2')
                                    ui.label('无直接关联用户').classes('text-gray-500 dark:text-gray-400 mb-3')
                                    ui.button('添加用户', icon='person_add', on_click=lambda: add_users_to_permission(permission_data)).classes('bg-indigo-600 text-white px-3 py-1')

                    # 操作按钮区域
                    with ui.row().classes('gap-2 mt-4 justify-end'):
                        ui.button('编辑权限', icon='edit', on_click=lambda: edit_permission_dialog(permission_data)).classes('bg-yellow-600 hover:bg-yellow-700 text-white px-3 py-1')
                        ui.button('删除权限', icon='delete', on_click=lambda: delete_permission_confirm(permission_data)).classes('bg-red-600 hover:bg-red-700 text-white px-3 py-1')

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

    # 角色关联管理
    def add_roles_to_permission(permission_data: DetachedPermission):
        """为权限添加角色关联"""
        with ui.dialog() as dialog, ui.card().classes('w-lg p-6'):
            ui.label('为权限添加角色').classes('text-xl font-bold text-blue-600 mb-4')
            ui.label(f'权限: {permission_data.display_name or permission_data.name}').classes('text-gray-700 mb-4')

            # 角色选择区域
            selected_roles = set()
            role_search_input = ui.input('搜索角色', placeholder='输入角色名称搜索').classes('w-full mb-4')
            
            with ui.column().classes('w-full max-h-60 overflow-y-auto border border-gray-200 dark:border-gray-600 rounded p-3') as role_list_container:
                pass

            def update_role_list():
                """更新角色列表"""
                role_list_container.clear()
                search_term = role_search_input.value.strip() if role_search_input.value else None
                
                # 获取所有角色，排除已关联的
                all_roles = safe(
                    lambda: get_roles_safe(),
                    return_value=[],
                    error_msg="角色列表加载失败"
                )
                
                available_roles = [role for role in all_roles if role.name not in permission_data.roles]
                
                if search_term:
                    available_roles = [role for role in available_roles if search_term.lower() in role.name.lower() or (role.display_name and search_term.lower() in role.display_name.lower())]

                with role_list_container:
                    if not available_roles:
                        ui.label('无可用角色' if not search_term else '未找到匹配的角色').classes('text-gray-500 text-center py-4')
                        return

                    for role in available_roles:
                        with ui.row().classes('w-full items-center gap-3 p-2 hover:bg-gray-50 dark:hover:bg-gray-700 rounded'):
                            role_checkbox = ui.checkbox(value=role.id in selected_roles, on_change=lambda e, r=role: toggle_role_selection(r, e.value))
                            ui.label(role.display_name or role.name).classes('flex-1 font-medium')
                            ui.label(f'({role.name})').classes('text-sm text-gray-500')

            def toggle_role_selection(role: DetachedRole, selected: bool):
                """切换角色选择状态"""
                if selected:
                    selected_roles.add(role.id)
                else:
                    selected_roles.discard(role.id)

            def handle_role_search():
                """处理角色搜索"""
                update_role_list()

            # 搜索输入监听
            role_search_input.on('input', lambda: ui.timer(0.5, handle_role_search, once=True))

            with ui.row().classes('w-full gap-2 mt-6 justify-end'):
                ui.button('取消', on_click=dialog.close).classes('bg-gray-500 text-white px-4 py-2')
                ui.button('保存关联', on_click=lambda: confirm_update_roles()).classes('bg-blue-600 text-white px-4 py-2')

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

    def remove_role_from_permission(permission_data: DetachedPermission, role_name: str):
        """从权限中移除角色"""
        def confirm_remove():
            with ui.dialog() as confirm_dialog, ui.card().classes('w-80 p-6'):
                ui.label('确认移除角色').classes('text-lg font-bold text-orange-600 mb-4')
                ui.label(f'权限: {permission_data.display_name or permission_data.name}').classes('text-gray-700 mb-2')
                ui.label(f'角色: {role_name}').classes('text-gray-700 mb-2')
                ui.label('确定要移除此角色的关联吗？').classes('text-orange-600 font-medium mt-4')

                with ui.row().classes('w-full gap-2 mt-6 justify-end'):
                    ui.button('取消', on_click=confirm_dialog.close).classes('bg-gray-500 text-white px-4 py-2')
                    ui.button('确认移除', on_click=lambda: execute_remove_role()).classes('bg-orange-600 text-white px-4 py-2')

                def execute_remove_role():
                    """执行移除角色操作"""
                    log_info(f"开始移除权限 {permission_data.name} 的角色关联: {role_name}")
                    
                    success = safe(
                        lambda: remove_permission_from_role(permission_data.id, role_name),
                        return_value=False,
                        error_msg="移除角色关联失败"
                    )

                    if success:
                        ui.notify(f'成功移除角色 "{role_name}" 的关联', type='positive')
                        confirm_dialog.close()
                        update_permissions_display()
                    else:
                        ui.notify('移除角色关联失败', type='error')

            confirm_dialog.open()
        
        confirm_remove()

    def remove_all_roles_confirm(permission_data: DetachedPermission):
        """确认移除所有角色关联"""
        with ui.dialog() as dialog, ui.card().classes('w-96 p-6'):
            ui.label('确认移除所有角色').classes('text-xl font-bold text-red-600 mb-4')
            ui.label(f'权限: {permission_data.display_name or permission_data.name}').classes('text-gray-700 mb-2')
            ui.label(f'将移除以下 {len(permission_data.roles)} 个角色的关联:').classes('text-gray-700 mb-2')
            
            # 显示将要移除的角色
            with ui.column().classes('w-full p-3 bg-gray-50 dark:bg-gray-600 rounded mb-4'):
                with ui.row().classes('gap-2 flex-wrap'):
                    for role_name in permission_data.roles:
                        ui.chip(role_name, icon='badge').classes('bg-red-100 text-red-800 text-sm')
            
            ui.label('此操作不可撤销，确定要移除所有角色关联吗？').classes('text-red-600 font-medium')

            with ui.row().classes('w-full gap-2 mt-6 justify-end'):
                ui.button('取消', on_click=dialog.close).classes('bg-gray-500 text-white px-4 py-2')
                ui.button('确认移除', on_click=lambda: execute_remove_all_roles()).classes('bg-red-600 text-white px-4 py-2')

            def execute_remove_all_roles():
                """执行移除所有角色操作"""
                log_info(f"开始移除权限 {permission_data.name} 的所有角色关联")
                
                success_count = 0
                for role_name in permission_data.roles:
                    success = safe(
                        lambda: remove_permission_from_role(permission_data.id, role_name),
                        return_value=False,
                        error_msg=f"移除角色 {role_name} 关联失败"
                    )
                    if success:
                        success_count += 1

                if success_count > 0:
                    ui.notify(f'成功移除 {success_count} 个角色关联', type='positive')
                    dialog.close()
                    update_permissions_display()
                else:
                    ui.notify('移除角色关联失败', type='error')

        dialog.open()

    # 用户关联管理（新增功能）
    def add_users_to_permission(permission_data: DetachedPermission):
        """为权限添加用户关联"""
        with ui.dialog() as dialog, ui.card().classes('w-lg p-6'):
            ui.label('为权限添加用户').classes('text-xl font-bold text-indigo-600 mb-4')
            ui.label(f'权限: {permission_data.display_name or permission_data.name}').classes('text-gray-700 mb-4')

            # 用户选择区域
            selected_users = set()
            user_search_input = ui.input('搜索用户', placeholder='输入用户名或邮箱搜索').classes('w-full mb-4')
            
            with ui.column().classes('w-full max-h-60 overflow-y-auto border border-gray-200 dark:border-gray-600 rounded p-3') as user_list_container:
                pass

            def update_user_list():
                """更新用户列表"""
                user_list_container.clear()
                search_term = user_search_input.value.strip() if user_search_input.value else None
                
                # 获取所有用户
                all_users = safe(
                    lambda: get_users_safe(search_term=search_term),
                    return_value=[],
                    error_msg="用户列表加载失败"
                )
                
                # 获取已直接关联的用户
                current_permission_users = safe(
                    lambda: get_permission_direct_users_safe(permission_data.id),
                    return_value=[],
                    error_msg="获取权限关联用户失败"
                )
                current_user_ids = {user['id'] for user in current_permission_users}
                
                # 排除已关联的用户
                available_users = [user for user in all_users if user.id not in current_user_ids]

                with user_list_container:
                    if not available_users:
                        ui.label('无可用用户' if not search_term else '未找到匹配的用户').classes('text-gray-500 text-center py-4')
                        return

                    for user in available_users:
                        with ui.row().classes('w-full items-center gap-3 p-2 hover:bg-gray-50 dark:hover:bg-gray-700 rounded'):
                            user_checkbox = ui.checkbox(value=user.id in selected_users, on_change=lambda e, u=user: toggle_user_selection(u, e.value))
                            
                            # 用户信息显示
                            with ui.column().classes('flex-1 gap-1'):
                                ui.label(user.full_name or user.username).classes('font-medium')
                                ui.label(f'{user.username} ({user.email})').classes('text-sm text-gray-500')
                            
                            # 用户状态
                            if not user.is_active:
                                ui.chip('已停用', icon='block').classes('bg-red-100 text-red-800 text-xs')
                            elif user.is_superuser:
                                ui.chip('超管', icon='admin_panel_settings').classes('bg-purple-100 text-purple-800 text-xs')

            def toggle_user_selection(user: DetachedUser, selected: bool):
                """切换用户选择状态"""
                if selected:
                    selected_users.add(user.id)
                else:
                    selected_users.discard(user.id)

            def handle_user_search():
                """处理用户搜索"""
                update_user_list()

            # 搜索输入监听
            user_search_input.on('input', lambda: ui.timer(0.5, handle_user_search, once=True))

            with ui.row().classes('w-full gap-2 mt-6 justify-end'):
                ui.button('取消', on_click=dialog.close).classes('bg-gray-500 text-white px-4 py-2')
                ui.button('保存关联', on_click=lambda: confirm_update_users()).classes('bg-indigo-600 text-white px-4 py-2')

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

    def remove_user_from_permission(permission_data: DetachedPermission, user_data: dict):
        """从权限中移除用户"""
        def confirm_remove():
            with ui.dialog() as confirm_dialog, ui.card().classes('w-80 p-6'):
                ui.label('确认移除用户').classes('text-lg font-bold text-orange-600 mb-4')
                ui.label(f'权限: {permission_data.display_name or permission_data.name}').classes('text-gray-700 mb-2')
                ui.label(f'用户: {user_data["username"]}').classes('text-gray-700 mb-2')
                ui.label('确定要移除此用户的权限关联吗？').classes('text-orange-600 font-medium mt-4')

                with ui.row().classes('w-full gap-2 mt-6 justify-end'):
                    ui.button('取消', on_click=confirm_dialog.close).classes('bg-gray-500 text-white px-4 py-2')
                    ui.button('确认移除', on_click=lambda: execute_remove_user()).classes('bg-orange-600 text-white px-4 py-2')

                def execute_remove_user():
                    """执行移除用户操作"""
                    log_info(f"开始移除权限 {permission_data.name} 的用户关联: {user_data['username']}")
                    
                    success = safe(
                        lambda: remove_permission_from_user(permission_data.id, user_data['id']),
                        return_value=False,
                        error_msg="移除用户权限关联失败"
                    )

                    if success:
                        ui.notify(f'成功移除用户 "{user_data["username"]}" 的权限关联', type='positive')
                        confirm_dialog.close()
                        update_permissions_display()
                    else:
                        ui.notify('移除用户权限关联失败', type='error')

            confirm_dialog.open()
        
        confirm_remove()

    def remove_all_users_confirm(permission_data: DetachedPermission):
        """确认移除所有用户关联"""
        permission_users = safe(
            lambda: get_permission_direct_users_safe(permission_data.id),
            return_value=[],
            error_msg="获取权限关联用户失败"
        )
        
        with ui.dialog() as dialog, ui.card().classes('w-96 p-6'):
            ui.label('确认移除所有用户').classes('text-xl font-bold text-red-600 mb-4')
            ui.label(f'权限: {permission_data.display_name or permission_data.name}').classes('text-gray-700 mb-2')
            ui.label(f'将移除以下 {len(permission_users)} 个用户的权限关联:').classes('text-gray-700 mb-2')
            
            # 显示将要移除的用户
            with ui.column().classes('w-full p-3 bg-gray-50 dark:bg-gray-600 rounded mb-4 max-h-32 overflow-y-auto'):
                with ui.row().classes('gap-2 flex-wrap'):
                    for user_data in permission_users:
                        ui.chip(user_data['username'], icon='person').classes('bg-red-100 text-red-800 text-sm')
            
            ui.label('此操作不可撤销，确定要移除所有用户的权限关联吗？').classes('text-red-600 font-medium')

            with ui.row().classes('w-full gap-2 mt-6 justify-end'):
                ui.button('取消', on_click=dialog.close).classes('bg-gray-500 text-white px-4 py-2')
                ui.button('确认移除', on_click=lambda: execute_remove_all_users()).classes('bg-red-600 text-white px-4 py-2')

            def execute_remove_all_users():
                """执行移除所有用户操作"""
                log_info(f"开始移除权限 {permission_data.name} 的所有用户关联")
                
                success_count = 0
                for user_data in permission_users:
                    success = safe(
                        lambda: remove_permission_from_user(permission_data.id, user_data['id']),
                        return_value=False,
                        error_msg=f"移除用户 {user_data['username']} 权限关联失败"
                    )
                    if success:
                        success_count += 1

                if success_count > 0:
                    ui.notify(f'成功移除 {success_count} 个用户的权限关联', type='positive')
                    dialog.close()
                    update_permissions_display()
                else:
                    ui.notify('移除用户权限关联失败', type='error')

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

    # 初始加载权限显示
    update_permissions_display()

    log_info("权限管理页面加载完成")