"""
权限管理页面 - 卡片模式布局，与用户管理和角色管理页面保持一致
"""
from nicegui import ui
from ..decorators import require_role
from ..auth_manager import auth_manager
from ..detached_helper import (
    detached_manager,
    get_permissions_safe,
    get_permission_safe,
    get_roles_safe,
    update_permission_safe,
    delete_permission_safe,
    create_permission_safe,
    DetachedPermission,
    DetachedRole
)
from ..models import Permission, Role
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
        ui.label('管理系统权限和资源访问控制，支持角色关联管理').classes('text-lg text-gray-600 dark:text-gray-400')

    # 权限统计卡片
    def load_permission_statistics():
        """加载权限统计数据"""
        log_info("开始加载权限统计数据")
        permission_stats = detached_manager.get_permission_statistics()
        role_stats = detached_manager.get_role_statistics()
        
        return {
            **permission_stats,
            'total_roles': role_stats['total_roles']
        }

    # 安全执行统计数据加载
    stats = safe(
        load_permission_statistics,
        return_value={'total_permissions': 0, 'system_permissions': 0, 'content_permissions': 0, 'total_roles': 0},
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
                    ui.label('关联角色').classes('text-sm opacity-90 font-medium')
                    ui.label(str(stats['total_roles'])).classes('text-3xl font-bold')
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
                        ui.label(f'未找到匹配 "{search_term}" 的权限').classes('text-xl font-medium text-gray-500 dark:text-gray-400')
                        ui.label('请尝试其他关键词或清空搜索条件').classes('text-gray-400 dark:text-gray-500')
                        ui.button('清空搜索', icon='clear', 
                                on_click=reset_search).classes('mt-4 bg-blue-500 text-white')
                    else:
                        ui.icon('security_off').classes('text-6xl text-gray-400 mb-4')
                        ui.label('暂无权限数据').classes('text-xl font-medium text-gray-500 dark:text-gray-400')
                        ui.label('点击"添加权限"按钮添加第一个权限').classes('text-gray-400 dark:text-gray-500')
                return

            # 显示搜索结果统计
            search_term = search_input.value.strip() if search_input.value else None
            if search_term:
                ui.label(f'搜索 "{search_term}" 找到 {len(permissions)} 个权限').classes('text-sm text-gray-600 dark:text-gray-400 mb-4')

            # 创建权限卡片网格 - 每行2个（与用户/角色页面保持一致）
            for i in range(0, len(permissions), 2):
                with ui.row().classes('w-full gap-3'):
                    # 第一个权限卡片
                    with ui.column().classes('flex-1'):
                        create_permission_card(permissions[i])
                    
                    # 第二个权限卡片（如果存在）
                    if i + 1 < len(permissions):
                        with ui.column().classes('flex-1'):
                            create_permission_card(permissions[i + 1])
                    else:
                        # 如果是奇数个权限，添加占位符保持布局
                        ui.column().classes('flex-1')

    def create_permission_card(permission_data: DetachedPermission):
        """创建单个权限卡片"""
        # 根据权限分类确定主题色
        if permission_data.category == '系统':
            card_theme = 'border-l-4 border-red-500 bg-red-50 dark:bg-red-900/10'
            badge_theme = 'bg-red-100 text-red-800 dark:bg-red-800 dark:text-red-200'
            icon_theme = 'text-red-600 dark:text-red-400'
            category_icon = 'admin_panel_settings'
        elif permission_data.category == '内容':
            card_theme = 'border-l-4 border-blue-500 bg-blue-50 dark:bg-blue-900/10'
            badge_theme = 'bg-blue-100 text-blue-800 dark:bg-blue-800 dark:text-blue-200'
            icon_theme = 'text-blue-600 dark:text-blue-400'
            category_icon = 'content_paste'
        elif permission_data.category == '分析':
            card_theme = 'border-l-4 border-purple-500 bg-purple-50 dark:bg-purple-900/10'
            badge_theme = 'bg-purple-100 text-purple-800 dark:bg-purple-800 dark:text-purple-200'
            icon_theme = 'text-purple-600 dark:text-purple-400'
            category_icon = 'analytics'
        elif permission_data.category == '业务':
            card_theme = 'border-l-4 border-green-500 bg-green-50 dark:bg-green-900/10'
            badge_theme = 'bg-green-100 text-green-800 dark:bg-green-800 dark:text-green-200'
            icon_theme = 'text-green-600 dark:text-green-400'
            category_icon = 'business'
        elif permission_data.category == '个人':
            card_theme = 'border-l-4 border-orange-500 bg-orange-50 dark:bg-orange-900/10'
            badge_theme = 'bg-orange-100 text-orange-800 dark:bg-orange-800 dark:text-orange-200'
            icon_theme = 'text-orange-600 dark:text-orange-400'
            category_icon = 'person'
        else:
            card_theme = 'border-l-4 border-gray-500 bg-gray-50 dark:bg-gray-900/10'
            badge_theme = 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200'
            icon_theme = 'text-gray-600 dark:text-gray-400'
            category_icon = 'security'

        with ui.card().classes(f'w-full {card_theme} shadow-md hover:shadow-lg transition-shadow duration-300'):
            with ui.row().classes('w-full p-4 gap-4'):
                # 左侧：权限基本信息（约占 40%）
                with ui.column().classes('flex-none w-80 gap-2'):
                    # 权限头部信息
                    with ui.row().classes('items-center gap-3 mb-2'):
                        ui.icon(category_icon).classes(f'text-3xl {icon_theme}')
                        with ui.column().classes('gap-0'):
                            ui.label(permission_data.display_name or permission_data.name).classes('text-xl font-bold text-gray-800 dark:text-gray-200')
                            ui.label(permission_data.name).classes('text-sm text-gray-500 dark:text-gray-400 font-mono')

                    # 权限分类标签
                    with ui.row().classes('gap-1 flex-wrap mb-2'):
                        ui.chip(permission_data.category or '未分类', icon='category').classes(f'{badge_theme} text-xs py-1 px-2')
                        
                        # 角色状态指示器
                        if permission_data.roles_count > 0:
                            if permission_data.roles_count >= 3:
                                ui.chip(f'{permission_data.roles_count}个角色', icon='groups').classes('bg-green-100 text-green-800 dark:bg-green-800 dark:text-green-200 text-xs py-1 px-2').tooltip('此权限被多个角色使用')
                            elif permission_data.roles_count == 2:
                                ui.chip(f'{permission_data.roles_count}个角色', icon='group').classes('bg-blue-100 text-blue-800 dark:bg-blue-800 dark:text-blue-200 text-xs py-1 px-2')
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

                # 右侧：角色和操作区域（约占 60%）
                with ui.column().classes('flex-1 gap-2'):
                    # 关联角色信息
                    with ui.row().classes('items-center justify-between w-full mb-2'):
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
                                        with ui.chip(role_name, icon='group', removable=True).classes(f'bg-{role_color}-100 text-{role_color}-800 dark:bg-{role_color}-800 dark:text-{role_color}-200 text-sm') as chip:
                                            chip.on('remove', lambda role=role_name, perm=permission_data: remove_role_from_permission(perm, role))
                                
                                # 批量操作区域
                                with ui.row().classes('w-full justify-between items-center mt-2 pt-2 border-t border-gray-200 dark:border-gray-600'):
                                    with ui.row().classes('gap-1'):
                                        ui.button('+添加', icon='add', on_click=lambda p=permission_data: quick_add_role_dialog(p)).props('flat size=md color=green').classes('text-xs')
                                        ui.button('管理', icon='settings', on_click=lambda p=permission_data: manage_permission_roles_dialog(p)).props('flat size=md color=blue').classes('text-xs')
                                    
                                    # 快速移除所有角色按钮
                                    if len(permission_data.roles) > 1:
                                        ui.button('清空', icon='clear_all', on_click=lambda p=permission_data: remove_all_roles_confirm(p)).props('flat size=md color=red').classes('text-xs').tooltip('移除所有角色关联')
                        else:
                            # 无角色状态
                            with ui.column().classes('w-full items-center justify-center py-3'):
                                ui.icon('group_off').classes('text-2xl text-gray-400 mb-1')
                                ui.label('暂无关联角色').classes('text-sm text-gray-500 dark:text-gray-400 mb-2')
                                
                                # 添加角色按钮
                                with ui.row().classes('gap-1'):
                                    ui.button('添加角色', icon='add', on_click=lambda p=permission_data: quick_add_role_dialog(p)).props('flat size=sm color=green').classes('text-xs')
                                    ui.button('批量管理', icon='settings', on_click=lambda p=permission_data: manage_permission_roles_dialog(p)).props('flat size=sm color=blue').classes('text-xs')

                    # 时间信息
                    with ui.card().classes('w-full p-3 bg-gray-50 dark:bg-gray-600 border border-gray-200 dark:border-gray-600'):
                        with ui.row().classes('items-center justify-between w-full'):
                            with ui.column().classes('gap-1'):
                                ui.label('创建时间').classes('text-xs text-gray-500 dark:text-gray-400')
                                if permission_data.created_at:
                                    ui.label(permission_data.created_at.strftime('%Y-%m-%d %H:%M')).classes('text-sm font-medium text-gray-700 dark:text-gray-300')
                                else:
                                    ui.label('未知').classes('text-sm text-gray-500')
                            
                            # 操作按钮
                            with ui.row().classes('gap-1'):
                                ui.button(icon='edit', on_click=lambda p=permission_data: edit_permission_dialog(p)).props('flat round size=sm color=blue').tooltip('编辑权限')
                                
                                # 快速操作菜单
                                with ui.button(icon='more_vert').props('flat round size=sm color=gray') as more_btn:
                                    with ui.menu() as more_menu:
                                        ui.menu_item('快速添加角色', lambda p=permission_data: quick_add_role_dialog(p))
                                        ui.menu_item('管理所有角色', lambda p=permission_data: manage_permission_roles_dialog(p))
                                        ui.separator()
                                        if permission_data.roles_count > 0:
                                            ui.menu_item('移除所有角色', lambda p=permission_data: remove_all_roles_confirm(p))
                                        if permission_data.roles_count == 0:
                                            ui.menu_item('删除权限', lambda p=permission_data: delete_permission_confirm(p))
                                
                                # 如果没有关联角色，显示删除按钮
                                if permission_data.roles_count == 0:
                                    ui.button(icon='delete', on_click=lambda p=permission_data: delete_permission_confirm(p)).props('flat round size=sm color=red').tooltip('删除权限')

    # 搜索事件处理
    def handle_search():
        update_permissions_display()

    def reset_search():
        search_input.value = ''
        category_filter.value = '全部'
        update_permissions_display()

    search_input.on('keydown.enter', handle_search)
    category_filter.on('update:model-value', handle_search)

    # 权限操作对话框
    def add_permission_dialog():
        """添加权限对话框"""
        with ui.dialog() as dialog, ui.card().classes('w-96 p-6'):
            ui.label('添加新权限').classes('text-xl font-bold mb-4')

            name_input = ui.input('权限名称', placeholder='如: user.manage').classes('w-full')
            display_name_input = ui.input('显示名称', placeholder='如: 用户管理').classes('w-full mt-3')
            category_input = ui.select(
                options=['系统', '内容', '分析', '业务', '个人', '其他'],
                label='权限分类'
            ).classes('w-full mt-3')
            description_input = ui.textarea('权限描述', placeholder='详细描述此权限的用途').classes('w-full mt-3')

            with ui.row().classes('w-full gap-2 mt-6 justify-end'):
                ui.button('取消', on_click=dialog.close).classes('bg-gray-500 text-white px-4 py-2')
                ui.button('确认添加', on_click=lambda: confirm_add_permission()).classes('bg-green-600 text-white px-4 py-2')

            def confirm_add_permission():
                name = name_input.value.strip()
                display_name = display_name_input.value.strip()
                category = category_input.value
                description = description_input.value.strip()

                if not name:
                    ui.notify('请输入权限名称', type='warning')
                    return

                log_info(f"开始创建权限: {name}")
                success = safe(
                    lambda: create_permission_safe(
                        name=name,
                        display_name=display_name or None,
                        category=category,
                        description=description or None
                    ),
                    return_value=False,
                    error_msg="权限创建失败"
                )

                if success:
                    ui.notify('权限创建成功', type='positive')
                    dialog.close()
                    update_permissions_display()
                else:
                    ui.notify('权限创建失败，请检查权限名称是否重复', type='error')

        dialog.open()

    def edit_permission_dialog(permission_data: DetachedPermission):
        """编辑权限对话框"""
        with ui.dialog() as dialog, ui.card().classes('w-96 p-6'):
            ui.label(f'编辑权限: {permission_data.name}').classes('text-xl font-bold mb-4')

            name_input = ui.input('权限名称', value=permission_data.name).classes('w-full').props('readonly')
            display_name_input = ui.input('显示名称', value=permission_data.display_name or '').classes('w-full mt-3')
            category_input = ui.select(
                options=['系统', '内容', '分析', '业务', '个人', '其他'],
                value=permission_data.category or '其他',
                label='权限分类'
            ).classes('w-full mt-3')
            description_input = ui.textarea('权限描述', value=permission_data.description or '').classes('w-full mt-3')

            with ui.row().classes('w-full gap-2 mt-6 justify-end'):
                ui.button('取消', on_click=dialog.close).classes('bg-gray-500 text-white px-4 py-2')
                ui.button('保存更改', on_click=lambda: confirm_edit_permission()).classes('bg-blue-600 text-white px-4 py-2')

            def confirm_edit_permission():
                display_name = display_name_input.value.strip()
                category = category_input.value
                description = description_input.value.strip()

                log_info(f"开始更新权限: {permission_data.name}")
                success = safe(
                    lambda: update_permission_safe(
                        permission_data.id,
                        display_name=display_name or None,
                        category=category,
                        description=description or None
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
        """删除权限确认对话框"""
        with ui.dialog() as dialog, ui.card().classes('w-80 p-6'):
            ui.label('确认删除权限').classes('text-xl font-bold text-red-600 mb-4')
            ui.label(f'权限名称: {permission_data.name}').classes('text-gray-700 mb-2')
            ui.label(f'显示名称: {permission_data.display_name or "无"}').classes('text-gray-700 mb-2')
            ui.label('此操作无法撤销！').classes('text-red-500 font-bold mt-4')

            with ui.row().classes('w-full gap-2 mt-6 justify-end'):
                ui.button('取消', on_click=dialog.close).classes('bg-gray-500 text-white px-4 py-2')
                ui.button('确认删除', on_click=lambda: confirm_delete_permission()).classes('bg-red-600 text-white px-4 py-2')

            def confirm_delete_permission():
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
                    ui.notify('权限删除失败', type='error')

        dialog.open()

    def quick_add_role_dialog(permission_data: DetachedPermission):
        """快速添加角色对话框"""
        with ui.dialog() as dialog, ui.card().classes('w-96 p-6'):
            ui.label(f'为权限 "{permission_data.display_name or permission_data.name}" 添加角色').classes('text-lg font-bold mb-4')
            
            # 获取可用角色（排除已关联的）
            available_roles = safe(
                lambda: [role for role in get_roles_safe() if role.name not in permission_data.roles],
                return_value=[],
                error_msg="获取可用角色失败"
            )
            
            if not available_roles:
                ui.label('所有角色都已关联此权限').classes('text-gray-500 text-center py-4')
                with ui.row().classes('w-full justify-center mt-4'):
                    ui.button('关闭', on_click=dialog.close).classes('bg-gray-500 text-white px-4 py-2')
                dialog.open()
                return
            
            # 角色选择器
            selected_role_ids = []
            
            ui.label('选择要添加的角色:').classes('text-sm font-medium mb-2')
            
            with ui.column().classes('w-full gap-2 max-h-48 overflow-auto'):
                for role in available_roles:
                    with ui.row().classes('w-full items-center p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded'):
                        checkbox = ui.checkbox(
                            value=False,
                            on_change=lambda checked, role_id=role.id: toggle_quick_role_selection(role_id, checked)
                        )
                        
                        with ui.column().classes('flex-1 ml-2'):
                            ui.label(role.display_name or role.name).classes('font-medium')
                            ui.label(f'角色名: {role.name}').classes('text-sm text-gray-600')
                            if role.description:
                                ui.label(role.description).classes('text-xs text-gray-500')

            def toggle_quick_role_selection(role_id: int, checked: bool):
                """切换角色选择状态"""
                if checked:
                    if role_id not in selected_role_ids:
                        selected_role_ids.append(role_id)
                else:
                    if role_id in selected_role_ids:
                        selected_role_ids.remove(role_id)

            with ui.row().classes('w-full gap-2 mt-6 justify-end'):
                ui.button('取消', on_click=dialog.close).classes('bg-gray-500 text-white px-4 py-2')
                ui.button('添加选中角色', on_click=lambda: confirm_quick_add_roles()).classes('bg-green-600 text-white px-4 py-2')

            def confirm_quick_add_roles():
                """确认快速添加角色"""
                if not selected_role_ids:
                    ui.notify('请至少选择一个角色', type='warning')
                    return

                log_info(f"快速为权限 {permission_data.name} 添加角色: {selected_role_ids}")
                
                success = safe(
                    lambda: add_permission_to_roles(permission_data.id, selected_role_ids),
                    return_value=False,
                    error_msg="快速添加角色失败"
                )

                if success:
                    ui.notify(f'成功为权限添加了 {len(selected_role_ids)} 个角色', type='positive')
                    dialog.close()
                    update_permissions_display()
                else:
                    ui.notify('添加角色失败', type='error')

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
                        role_color = 'red' if role_name == 'admin' else 'blue' if role_name == 'user' else 'green'
                        ui.chip(role_name, icon='group').classes(f'bg-{role_color}-100 text-{role_color}-800 dark:bg-{role_color}-800 dark:text-{role_color}-200 text-sm')
            
            ui.label('此操作无法撤销！').classes('text-red-500 font-bold')

            with ui.row().classes('w-full gap-2 mt-6 justify-end'):
                ui.button('取消', on_click=dialog.close).classes('bg-gray-500 text-white px-4 py-2')
                ui.button('确认移除所有', on_click=lambda: execute_remove_all_roles()).classes('bg-red-600 text-white px-4 py-2')

            def execute_remove_all_roles():
                """执行移除所有角色操作"""
                log_info(f"开始移除权限 {permission_data.name} 的所有角色关联")
                
                success_count = 0
                total_count = len(permission_data.roles)
                
                for role_name in permission_data.roles:
                    success = safe(
                        lambda rn=role_name: remove_permission_from_role(permission_data.id, rn),
                        return_value=False,
                        error_msg=f"移除角色 {role_name} 失败"
                    )
                    if success:
                        success_count += 1

                if success_count == total_count:
                    ui.notify(f'成功移除所有 {total_count} 个角色关联', type='positive')
                elif success_count > 0:
                    ui.notify(f'成功移除 {success_count}/{total_count} 个角色关联', type='warning')
                else:
                    ui.notify('移除角色关联失败', type='error')
                
                dialog.close()
                update_permissions_display()

        dialog.open()

    def manage_permission_roles_dialog(permission_data: DetachedPermission):
        """管理权限角色关联对话框"""
        with ui.dialog() as dialog, ui.card().classes('w-[800px] max-h-[600px] p-6'):
            ui.label(f'管理权限角色: {permission_data.display_name or permission_data.name}').classes('text-xl font-bold mb-4')

            # 当前关联的角色
            with ui.column().classes('w-full mb-6'):
                ui.label('当前关联角色').classes('text-lg font-semibold mb-2')
                
                if permission_data.roles:
                    with ui.row().classes('gap-2 flex-wrap'):
                        for role_name in permission_data.roles:
                            ui.chip(role_name, removable=False).classes('bg-blue-100 text-blue-800')
                else:
                    ui.label('暂无关联角色').classes('text-gray-500')

            # 可用角色列表
            ui.label('可用角色').classes('text-lg font-semibold mb-2')
            
            # 角色搜索
            role_search_input = ui.input('搜索角色', placeholder='输入角色名称搜索').classes('w-full mb-4')
            
            # 角色列表容器
            with ui.column().classes('w-full max-h-64 overflow-auto') as role_list_container:
                pass

            selected_roles = set()

            def update_role_list():
                """更新角色列表"""
                role_list_container.clear()
                search_term = role_search_input.value.strip() if role_search_input.value else None
                
                roles = safe(
                    lambda: get_roles_safe(),
                    return_value=[],
                    error_msg="角色列表加载失败"
                )

                # 过滤搜索
                if search_term:
                    roles = [r for r in roles if search_term.lower() in r.name.lower() 
                           or search_term.lower() in (r.display_name or '').lower()]

                with role_list_container:
                    for role in roles:
                        is_current = role.name in permission_data.roles
                        is_selected = role.id in selected_roles
                        
                        with ui.row().classes('w-full items-center p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded'):
                            if is_current:
                                ui.checkbox(value=True, on_change=None).props('disable')
                                ui.label('已关联').classes('text-xs text-green-600 bg-green-100 px-2 py-1 rounded')
                            else:
                                checkbox = ui.checkbox(
                                    value=is_selected,
                                    on_change=lambda checked, role_id=role.id: toggle_role_selection(role_id, checked)
                                )
                            
                            with ui.column().classes('flex-1 ml-2'):
                                ui.label(role.display_name or role.name).classes('font-medium')
                                ui.label(f'角色名: {role.name}').classes('text-sm text-gray-600')
                                if role.description:
                                    ui.label(role.description).classes('text-xs text-gray-500')

            def toggle_role_selection(role_id: int, checked: bool):
                """切换角色选择状态"""
                if checked:
                    selected_roles.add(role_id)
                else:
                    selected_roles.discard(role_id)

            def handle_role_search():
                update_role_list()

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

    # 辅助函数：添加权限到角色
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

    # 初始加载权限显示
    update_permissions_display()

    log_info("权限管理页面加载完成")