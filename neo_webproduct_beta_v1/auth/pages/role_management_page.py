"""
角色管理页面 - 优化布局，支持用户管理
"""
from nicegui import ui
from ..decorators import require_role
from ..auth_manager import auth_manager
from ..detached_helper import (
    detached_manager,
    get_roles_safe,
    get_role_safe,
    get_users_safe,
    update_role_safe,
    delete_role_safe,
    create_role_safe,
    DetachedRole,
    DetachedUser
)
from ..models import Role, User
from ..database import get_db

# 导入异常处理模块
from common.exception_handler import log_info, log_error, safe, db_safe, safe_protect

@require_role('admin')
@safe_protect(name="角色管理页面", error_msg="角色管理页面加载失败，请稍后重试")
def role_management_page_content():
    """角色管理页面内容 - 仅管理员可访问"""
    log_info("角色管理页面开始加载")
    
    # 页面标题
    with ui.column().classes('w-full mb-6'):
        ui.label('角色管理').classes('text-4xl font-bold text-purple-800 dark:text-purple-200 mb-2')
        ui.label('管理系统角色和权限分配，支持用户关联管理').classes('text-lg text-gray-600 dark:text-gray-400')

    # 角色统计卡片
    def load_role_statistics():
        """加载角色统计数据"""
        log_info("开始加载角色统计数据")
        role_stats = detached_manager.get_role_statistics()
        user_stats = detached_manager.get_user_statistics()
        
        return {
            **role_stats,
            'total_users': user_stats['total_users']
        }

    # 安全执行统计数据加载
    stats = safe(
        load_role_statistics,
        return_value={'total_roles': 0, 'active_roles': 0, 'system_roles': 0, 'total_users': 0},
        error_msg="角色统计数据加载失败"
    )

    # 统计卡片区域
    with ui.row().classes('w-full gap-6 mb-8'):
        with ui.card().classes('flex-1 p-6 bg-gradient-to-br from-purple-500 to-purple-600 text-white shadow-lg'):
            with ui.row().classes('items-center justify-between w-full'):
                with ui.column().classes('gap-1'):
                    ui.label('总角色数').classes('text-sm opacity-90 font-medium')
                    ui.label(str(stats['total_roles'])).classes('text-3xl font-bold')
                ui.icon('group').classes('text-4xl opacity-80')

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
                ui.icon('admin_panel_settings').classes('text-4xl opacity-80')

        with ui.card().classes('flex-1 p-6 bg-gradient-to-br from-orange-500 to-orange-600 text-white shadow-lg'):
            with ui.row().classes('items-center justify-between w-full'):
                with ui.column().classes('gap-1'):
                    ui.label('用户总数').classes('text-sm opacity-90 font-medium')
                    ui.label(str(stats['total_users'])).classes('text-3xl font-bold')
                ui.icon('people').classes('text-4xl opacity-80')

    

    # 角色列表容器 - 使用 flex 布局，减少间距
    with ui.column().classes('w-full'):
        ui.label('角色列表').classes('text-xl font-bold text-gray-800 dark:text-gray-200 mb-3')
        # 操作按钮区域 - 调小按钮尺寸
        with ui.row().classes('w-full gap-2 mb-4'):
            ui.button('创建新角色', icon='add', 
                    on_click=lambda: safe(add_role_dialog)).classes('bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 text-sm font-medium shadow-md')
            ui.button('角色模板', icon='content_copy', 
                    on_click=lambda: safe(role_template_dialog)).classes('bg-green-600 hover:bg-green-700 text-white px-4 py-2 text-sm font-medium shadow-md')
            ui.button('批量操作', icon='checklist', 
                    on_click=lambda: ui.notify('批量操作功能开发中...', type='info')).classes('bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 text-sm font-medium shadow-md')
            ui.button('导出数据', icon='download', 
                    on_click=lambda: safe(export_roles)).classes('bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 text-sm font-medium shadow-md')
        
        # 定义搜索处理函数 - 在使用前定义
        def handle_search():
            """处理搜索事件"""
            safe(load_roles)  # 立即搜索，不延迟
        
        def handle_input_search():
            """处理输入时的搜索事件 - 带延迟"""
            ui.timer(0.5, lambda: safe(load_roles), once=True)  # 延迟搜索，避免过于频繁
        
        def reset_search():
            """重置搜索"""
            search_input.value = ''
            safe(load_roles)

        # 搜索区域 - 在函数定义之后创建
        with ui.row().classes('w-full gap-2 mb-4 items-end'):
            search_input = ui.input(
                '搜索角色', 
                placeholder='输入角色名称进行模糊查找...',
                value=''
            ).classes('flex-1').props('outlined clearable')
            search_input.props('prepend-icon=search')
            
            ui.button('搜索', icon='search', 
                     on_click=handle_search).classes('bg-blue-600 hover:bg-blue-700 text-white px-4 py-2')
            ui.button('重置', icon='refresh', 
                     on_click=reset_search).classes('bg-gray-500 hover:bg-gray-600 text-white px-4 py-2')
        
        search_input.on('input', handle_input_search)  # 实时输入搜索（延迟）
        search_input.on('keydown.enter', handle_search)  # 回车键立即搜索
        roles_container = ui.column().classes('w-full gap-3')

    @safe_protect(name="角色列表加载", error_msg="角色列表加载失败")
    def load_roles():
        """加载角色数据 - 使用安全的分离数据"""
        log_info("开始加载角色列表数据")
        roles_container.clear()

        # 使用安全的数据获取方法
        all_roles = get_roles_safe()
        log_info(f"成功获取{len(all_roles)}个角色数据")
        
        # 获取搜索条件
        search_term = search_input.value.lower().strip() if search_input.value else ''
        
        # 过滤角色数据
        if search_term:
            filtered_roles = [
                role for role in all_roles 
                if (search_term in role.name.lower() or 
                    search_term in (role.display_name or '').lower() or
                    search_term in (role.description or '').lower())
            ]
            log_info(f"搜索 '{search_term}' 找到 {len(filtered_roles)} 个匹配角色")
        else:
            filtered_roles = all_roles

        with roles_container:
            if not filtered_roles:
                with ui.card().classes('w-full p-8 text-center bg-gray-50 dark:bg-gray-700'):
                    if search_term:
                        ui.icon('search_off').classes('text-6xl text-gray-400 mb-4')
                        ui.label(f'未找到匹配 "{search_term}" 的角色').classes('text-xl font-medium text-gray-500 dark:text-gray-400')
                        ui.label('请尝试其他关键词或清空搜索条件').classes('text-gray-400 dark:text-gray-500')
                        ui.button('清空搜索', icon='clear', 
                                 on_click=lambda: setattr(search_input, 'value', '')).classes('mt-4 bg-blue-500 text-white')
                    else:
                        ui.icon('group_off').classes('text-6xl text-gray-400 mb-4')
                        ui.label('暂无角色数据').classes('text-xl font-medium text-gray-500 dark:text-gray-400')
                        ui.label('点击"创建新角色"按钮添加第一个角色').classes('text-gray-400 dark:text-gray-500')
                return

            # 创建角色卡片网格 - 每行2个
            for i in range(0, len(filtered_roles), 2):
                with ui.row().classes('w-full gap-3'):
                    # 第一个角色卡片
                    with ui.column().classes('flex-1'):
                        create_role_card(filtered_roles[i])
                    
                    # 第二个角色卡片（如果存在）
                    if i + 1 < len(filtered_roles):
                        with ui.column().classes('flex-1'):
                            create_role_card(filtered_roles[i + 1])
                    else:
                        # 如果是奇数个角色，添加占位符保持布局
                        ui.column().classes('flex-1')

    def create_role_card(role_data: DetachedRole):
        """创建单个角色卡片"""
        # 确定角色颜色主题
        if role_data.name == 'admin':
            card_theme = 'border-l-4 border-red-500 bg-red-50 dark:bg-red-900/10'
            badge_theme = 'bg-red-100 text-red-800 dark:bg-red-800 dark:text-red-200'
            icon_theme = 'text-red-600 dark:text-red-400'
        elif role_data.name == 'user':
            card_theme = 'border-l-4 border-green-500 bg-green-50 dark:bg-green-900/10'
            badge_theme = 'bg-green-100 text-green-800 dark:bg-green-800 dark:text-green-200'
            icon_theme = 'text-green-600 dark:text-green-400'
        else:
            card_theme = 'border-l-4 border-blue-500 bg-blue-50 dark:bg-blue-900/10'
            badge_theme = 'bg-blue-100 text-blue-800 dark:bg-blue-800 dark:text-blue-200'
            icon_theme = 'text-blue-600 dark:text-blue-400'

        with ui.card().classes(f'w-full {card_theme} shadow-md hover:shadow-lg transition-shadow duration-300'):
            with ui.row().classes('w-full p-4 gap-4'):
                # 左侧：角色基本信息（约占 35%）- 更紧凑
                with ui.column().classes('flex-none w-72 gap-2'):
                    # 角色头部信息 - 减少间距
                    with ui.row().classes('items-center gap-3 mb-2'):
                        ui.icon('security').classes(f'text-3xl {icon_theme}')
                        with ui.column().classes('gap-0'):
                            ui.label(role_data.display_name or role_data.name).classes('text-xl font-bold text-gray-800 dark:text-gray-200')
                            ui.label(f'角色代码: {role_data.name}').classes('text-xs text-gray-500 dark:text-gray-400')

                    # 角色标签 - 使用更小的标签
                    with ui.row().classes('gap-1 flex-wrap mb-2'):
                        if role_data.is_system:
                            ui.chip('系统角色', icon='lock').classes('bg-orange-100 text-orange-800 dark:bg-orange-800 dark:text-orange-200 text-xs py-1 px-2')
                        else:
                            ui.chip('自定义', icon='edit').classes(f'{badge_theme} text-xs py-1 px-2')
                        
                        if role_data.is_active:
                            ui.chip('已启用', icon='check_circle').classes('bg-green-100 text-green-800 dark:bg-green-800 dark:text-green-200 text-xs py-1 px-2')
                        else:
                            ui.chip('已禁用', icon='block').classes('bg-red-100 text-red-800 dark:bg-red-800 dark:text-red-200 text-xs py-1 px-2')

                    # 角色描述 - 缩小高度
                    ui.label('描述:').classes('text-xs font-medium text-gray-600 dark:text-gray-400')
                    ui.label(role_data.description or '暂无描述').classes('text-sm text-gray-700 dark:text-gray-300 leading-tight min-h-[1.5rem] line-clamp-2')

                    # 统计信息 - 更紧凑
                    with ui.row().classes('gap-2 mt-2'):
                        with ui.card().classes('flex-1 p-2 bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600'):
                            ui.label('用户数').classes('text-xs text-gray-500 dark:text-gray-400')
                            ui.label(str(role_data.user_count)).classes('text-lg font-bold text-blue-600 dark:text-blue-400')
                        
                        with ui.card().classes('flex-1 p-2 bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600'):
                            ui.label('权限数').classes('text-xs text-gray-500 dark:text-gray-400')
                            ui.label(str(len(role_data.permissions))).classes('text-lg font-bold text-green-600 dark:text-green-400')

                # 右侧：用户管理区域（约占 65%）- 优化高度
                with ui.column().classes('flex-1 gap-2'):
                    # 用户列表标题和操作按钮 - 减少间距
                    with ui.row().classes('items-center justify-between w-full mb-2'):
                        ui.label(f'关联用户 ({role_data.user_count})').classes('text-lg font-bold text-gray-800 dark:text-gray-200')
                        with ui.row().classes('gap-1'):
                            ui.button('添加用户', icon='person_add',
                                     on_click=lambda r=role_data: safe(lambda: add_users_to_role_dialog(r))).classes('bg-green-600 hover:bg-green-700 text-white px-3 py-1 text-xs')
                            ui.button('批量移除', icon='person_remove',
                                     on_click=lambda r=role_data: safe(lambda: batch_remove_users_dialog(r))).classes('bg-red-600 hover:bg-red-700 text-white px-3 py-1 text-xs')

                    # 用户列表区域 - 减少高度和内边距
                    with ui.card().classes('w-full p-3 bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 min-h-[120px] max-h-[160px] overflow-auto'):
                        if role_data.users:
                            with ui.column().classes('w-full gap-1'):
                                for username in role_data.users:
                                    with ui.row().classes('items-center justify-between w-full p-2 bg-gray-50 dark:bg-gray-600 rounded hover:bg-gray-100 dark:hover:bg-gray-500 transition-colors'):
                                        with ui.row().classes('items-center gap-2'):
                                            ui.icon('person').classes('text-blue-500 text-lg')
                                            ui.label(username).classes('text-sm text-gray-800 dark:text-gray-200 font-medium')
                                        
                                        if not role_data.is_system:  # 只有非系统角色才能移除用户
                                            ui.button(icon='close',
                                                     on_click=lambda u=username, r=role_data: safe(lambda: remove_user_from_role(u, r))).props('flat round color=red').classes('w-6 h-6')
                        else:
                            with ui.column().classes('w-full items-center justify-center py-4'):
                                ui.icon('people_outline').classes('text-3xl text-gray-400 mb-1')
                                ui.label('无关联用户').classes('text-sm text-gray-500 dark:text-gray-400')
                                ui.label('点击"添加用户"分配用户').classes('text-xs text-gray-400 dark:text-gray-500')

                    # 角色操作按钮 - 使用更小的按钮
                    with ui.row().classes('gap-1 w-full mt-2'):
                        ui.button('查看', icon='visibility',
                                 on_click=lambda r=role_data: safe(lambda: view_role_dialog(r))).classes('flex-1 bg-blue-600 hover:bg-blue-700 text-white py-1 text-xs')
                        
                        if not role_data.is_system:
                            ui.button('编辑', icon='edit',
                                     on_click=lambda r=role_data: safe(lambda: edit_role_dialog(r))).classes('flex-1 bg-green-600 hover:bg-green-700 text-white py-1 text-xs')
                            ui.button('删除', icon='delete',
                                     on_click=lambda r=role_data: safe(lambda: delete_role_dialog(r))).classes('flex-1 bg-red-600 hover:bg-red-700 text-white py-1 text-xs')
                        else:
                            ui.button('系统角色', icon='lock',
                                     on_click=lambda: ui.notify('系统角色不可编辑', type='info')).classes('flex-1 bg-gray-400 text-white py-1 text-xs').disable()

    @safe_protect(name="添加用户到角色")
    def add_users_to_role_dialog(role_data: DetachedRole):
        """添加用户到角色对话框"""
        log_info(f"打开添加用户到角色对话框: {role_data.name}")
        
        with ui.dialog() as dialog, ui.card().classes('w-[600px] max-h-[80vh]'):
            dialog.open()
            
            # 对话框标题
            with ui.row().classes('w-full items-center justify-between p-4 bg-gradient-to-r from-green-500 to-green-600 text-white rounded-t-lg -m-6 mb-6'):
                ui.label(f'为角色 "{role_data.display_name or role_data.name}" 添加用户').classes('text-xl font-bold')
                ui.button(icon='close', on_click=dialog.close).props('flat round color=white').classes('ml-auto')

            # 获取所有用户，排除已有该角色的用户
            all_users = get_users_safe()
            available_users = [user for user in all_users if role_data.name not in user.roles]
            
            if not available_users:
                with ui.column().classes('w-full items-center py-8'):
                    ui.icon('people_outline').classes('text-6xl text-gray-400 mb-4')
                    ui.label('没有可添加的用户').classes('text-xl font-medium text-gray-500')
                    ui.label('所有用户都已拥有此角色，或系统中暂无其他用户').classes('text-gray-400')
                return

            # 用户选择列表
            selected_users = set()
            user_list_container = ui.column().classes('w-full gap-2 max-h-96 overflow-auto border border-gray-200 dark:border-gray-600 rounded-lg p-4')

            def update_user_list():
                """更新用户列表"""
                user_list_container.clear()
                search_term = search_input.value.lower() if search_input.value else ''
                
                filtered_users = [
                    user for user in available_users 
                    if search_term in user.username.lower() or search_term in user.email.lower()
                ]

                with user_list_container:
                    if not filtered_users:
                        with ui.column().classes('w-full items-center py-4'):
                            ui.icon('search_off').classes('text-4xl text-gray-400 mb-2')
                            ui.label('未找到匹配的用户').classes('text-gray-500')
                        return

                    for user in filtered_users:
                        with ui.row().classes('items-center gap-3 p-3 bg-gray-50 dark:bg-gray-700 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors'):
                            checkbox = ui.checkbox(
                                on_change=lambda e, u=user: selected_users.add(u.id) if e.value else selected_users.discard(u.id)
                            ).classes('mr-2')
                            
                            ui.icon('person').classes('text-blue-500 text-xl')
                            with ui.column().classes('flex-1 gap-1'):
                                ui.label(user.username).classes('font-medium text-gray-800 dark:text-gray-200')
                                ui.label(user.email).classes('text-sm text-gray-500 dark:text-gray-400')
                                if user.full_name:
                                    ui.label(user.full_name).classes('text-sm text-gray-600 dark:text-gray-300')
                            
                            # 显示用户当前角色
                            if user.roles:
                                with ui.row().classes('gap-1 flex-wrap'):
                                    for role_name in user.roles[:2]:  # 只显示前2个角色
                                        ui.chip(role_name, color='blue').classes('text-xs')
                                    if len(user.roles) > 2:
                                        ui.chip(f'+{len(user.roles) - 2}', color='gray').classes('text-xs')

            # 定义搜索处理函数 - 在使用前定义
            def handle_user_search():
                """处理用户搜索事件"""
                update_user_list()  # 立即搜索
            
            def handle_user_input_search():
                """处理用户输入搜索事件 - 带延迟"""
                ui.timer(0.5, update_user_list, once=True)  # 延迟搜索
            
            def reset_user_search():
                """重置用户搜索"""
                search_input.value = ''
                update_user_list()

            # 搜索区域 - 在函数定义之后创建
            with ui.row().classes('w-full gap-2 mb-4 items-end'):
                search_input = ui.input('搜索用户', placeholder='输入用户名或邮箱搜索').classes('flex-1')
                ui.button('搜索', icon='search',
                         on_click=handle_user_search).classes('bg-blue-600 hover:bg-blue-700 text-white px-3 py-1')
                ui.button('重置', icon='refresh',
                         on_click=reset_user_search).classes('bg-gray-500 hover:bg-gray-600 text-white px-3 py-1')
            
            # 绑定用户搜索事件 - 在所有组件创建完成后绑定
            search_input.on('input', handle_user_input_search)  # 实时输入搜索（延迟）
            search_input.on('keydown.enter', handle_user_search)  # 回车键立即搜索
            # search_input.on('blur', handle_user_search)  # 失去焦点时搜索
            
            # 初始加载用户列表
            update_user_list()

            def confirm_add_users():
                """确认添加用户"""
                if not selected_users:
                    ui.notify('请至少选择一个用户', type='warning')
                    return

                log_info(f"开始为角色 {role_data.name} 添加用户: {list(selected_users)}")
                
                try:
                    with db_safe("添加用户到角色") as db:
                        role = db.query(Role).filter(Role.id == role_data.id).first()
                        if not role:
                            ui.notify('角色不存在', type='error')
                            return

                        added_count = 0
                        for user_id in selected_users:
                            user = db.query(User).filter(User.id == user_id).first()
                            if user and role not in user.roles:
                                user.roles.append(role)
                                added_count += 1

                        db.commit()
                        
                        if added_count > 0:
                            log_info(f"成功为角色 {role_data.name} 添加了 {added_count} 个用户")
                            ui.notify(f'成功添加 {added_count} 个用户到角色 {role_data.name}', type='positive')
                            dialog.close()
                            safe(load_roles)  # 重新加载角色列表
                        else:
                            ui.notify('没有用户被添加', type='info')

                except Exception as e:
                    log_error(f"添加用户到角色失败: {role_data.name}", exception=e)
                    ui.notify('添加用户失败，请稍后重试', type='negative')

            # 操作按钮
            with ui.row().classes('w-full justify-end gap-3 mt-6'):
                ui.button('取消', on_click=dialog.close).classes('px-6 py-2 bg-gray-500 hover:bg-gray-600 text-white')
                ui.button('确认添加', on_click=lambda: safe(confirm_add_users)).classes('px-6 py-2 bg-green-600 hover:bg-green-700 text-white')

    @safe_protect(name="批量移除用户")
    def batch_remove_users_dialog(role_data: DetachedRole):
        """批量移除用户对话框"""
        log_info(f"打开批量移除用户对话框: {role_data.name}")
        
        if not role_data.users:
            ui.notify('此角色暂无用户可移除', type='info')
            return

        if role_data.is_system:
            ui.notify('系统角色不允许移除用户', type='warning')
            return

        with ui.dialog() as dialog, ui.card().classes('w-[500px]'):
            dialog.open()
            
            # 对话框标题
            with ui.row().classes('w-full items-center justify-between p-4 bg-gradient-to-r from-red-500 to-red-600 text-white rounded-t-lg -m-6 mb-6'):
                ui.label(f'从角色 "{role_data.display_name or role_data.name}" 批量移除用户').classes('text-xl font-bold')
                ui.button(icon='close', on_click=dialog.close).props('flat round color=white').classes('ml-auto')

            ui.label('选择要移除的用户：').classes('text-lg font-medium mb-4')
            
            # 用户选择列表
            selected_users = set()
            with ui.column().classes('w-full gap-2 max-h-80 overflow-auto'):
                for username in role_data.users:
                    with ui.row().classes('items-center gap-3 p-3 bg-red-50 dark:bg-red-900/20 rounded-lg'):
                        checkbox = ui.checkbox(
                            on_change=lambda e, u=username: selected_users.add(u) if e.value else selected_users.discard(u)
                        ).classes('mr-2')
                        
                        ui.icon('person').classes('text-red-500 text-xl')
                        ui.label(username).classes('font-medium text-gray-800 dark:text-gray-200')

            def confirm_remove_users():
                """确认移除用户"""
                if not selected_users:
                    ui.notify('请至少选择一个用户', type='warning')
                    return

                log_info(f"开始从角色 {role_data.name} 移除用户: {list(selected_users)}")
                
                try:
                    with db_safe("从角色移除用户") as db:
                        role = db.query(Role).filter(Role.id == role_data.id).first()
                        if not role:
                            ui.notify('角色不存在', type='error')
                            return

                        removed_count = 0
                        for username in selected_users:
                            user = db.query(User).filter(User.username == username).first()
                            if user and role in user.roles:
                                user.roles.remove(role)
                                removed_count += 1

                        db.commit()
                        
                        if removed_count > 0:
                            log_info(f"成功从角色 {role_data.name} 移除了 {removed_count} 个用户")
                            ui.notify(f'成功从角色 {role_data.name} 移除 {removed_count} 个用户', type='positive')
                            dialog.close()
                            safe(load_roles)  # 重新加载角色列表
                        else:
                            ui.notify('没有用户被移除', type='info')

                except Exception as e:
                    log_error(f"从角色移除用户失败: {role_data.name}", exception=e)
                    ui.notify('移除用户失败，请稍后重试', type='negative')

            # 操作按钮
            with ui.row().classes('w-full justify-end gap-3 mt-6'):
                ui.button('取消', on_click=dialog.close).classes('px-6 py-2 bg-gray-500 hover:bg-gray-600 text-white')
                ui.button('确认移除', on_click=lambda: safe(confirm_remove_users)).classes('px-6 py-2 bg-red-600 hover:bg-red-700 text-white')

    @safe_protect(name="移除单个用户")
    def remove_user_from_role(username: str, role_data: DetachedRole):
        """从角色中移除单个用户"""
        log_info(f"移除用户 {username} 从角色 {role_data.name}")
        
        if role_data.is_system:
            ui.notify('系统角色不允许移除用户', type='warning')
            return

        try:
            with db_safe("移除用户角色") as db:
                role = db.query(Role).filter(Role.id == role_data.id).first()
                user = db.query(User).filter(User.username == username).first()
                
                if not role or not user:
                    ui.notify('角色或用户不存在', type='error')
                    return

                if role in user.roles:
                    user.roles.remove(role)
                    db.commit()
                    
                    log_info(f"成功移除用户 {username} 从角色 {role_data.name}")
                    ui.notify(f'已将用户 {username} 从角色 {role_data.name} 中移除', type='positive')
                    safe(load_roles)  # 重新加载角色列表
                else:
                    ui.notify('用户不在此角色中', type='info')

        except Exception as e:
            log_error(f"移除用户角色失败: {username} - {role_data.name}", exception=e)
            ui.notify('移除失败，请稍后重试', type='negative')

    # 其他对话框函数保持原有逻辑...
    @safe_protect(name="查看角色详情")
    def view_role_dialog(role_data: DetachedRole):
        """查看角色详情对话框"""
        log_info(f"查看角色详情: {role_data.name}")
        
        with ui.dialog() as dialog, ui.card().classes('w-[700px] max-h-[80vh] overflow-auto'):
            dialog.open()
            
            # 标题区域
            with ui.row().classes('w-full items-center justify-between p-4 bg-gradient-to-r from-purple-500 to-purple-600 text-white rounded-t-lg -m-6 mb-6'):
                ui.label(f'角色详情: {role_data.display_name or role_data.name}').classes('text-xl font-bold')
                ui.button(icon='close', on_click=dialog.close).props('flat round color=white').classes('ml-auto')

            # 基本信息
            with ui.card().classes('w-full mb-4 bg-gray-50 dark:bg-gray-700'):
                ui.label('基本信息').classes('font-bold mb-3 text-gray-800 dark:text-gray-200')
                
                info_items = [
                    ('角色名称', role_data.name),
                    ('显示名称', role_data.display_name or "无"),
                    ('描述', role_data.description or "无"),
                    ('状态', "活跃" if role_data.is_active else "禁用"),
                    ('类型', "系统角色" if role_data.is_system else "自定义角色"),
                    ('创建时间', role_data.created_at.strftime('%Y-%m-%d %H:%M:%S') if role_data.created_at else '未知'),
                    ('更新时间', role_data.updated_at.strftime('%Y-%m-%d %H:%M:%S') if role_data.updated_at else '未知')
                ]
                
                for label, value in info_items:
                    with ui.row().classes('items-center gap-4 py-1'):
                        ui.label(f'{label}:').classes('text-sm font-medium text-gray-600 dark:text-gray-400 w-20')
                        ui.label(str(value)).classes('text-sm text-gray-800 dark:text-gray-200')

            # 用户列表
            if role_data.users:
                with ui.card().classes('w-full mb-4 bg-blue-50 dark:bg-blue-900/20'):
                    ui.label(f'拥有此角色的用户 ({len(role_data.users)})').classes('font-bold mb-3 text-blue-800 dark:text-blue-200')
                    
                    with ui.column().classes('gap-2 max-h-40 overflow-auto'):
                        for username in role_data.users:
                            with ui.row().classes('items-center gap-3 p-2 bg-white dark:bg-gray-700 rounded-lg shadow-sm'):
                                ui.icon('person').classes('text-blue-500')
                                ui.label(username).classes('text-sm font-medium')
            else:
                with ui.card().classes('w-full mb-4 bg-gray-50 dark:bg-gray-700'):
                    ui.label('暂无用户拥有此角色').classes('text-gray-500 dark:text-gray-400 text-center py-4')

            # 权限列表
            if role_data.permissions:
                with ui.card().classes('w-full mb-4 bg-green-50 dark:bg-green-900/20'):
                    ui.label(f'角色权限 ({len(role_data.permissions)})').classes('font-bold mb-3 text-green-800 dark:text-green-200')
                    
                    with ui.row().classes('gap-2 flex-wrap max-h-32 overflow-auto'):
                        for perm in role_data.permissions:
                            ui.chip(perm, icon='security').classes('bg-green-100 text-green-800 dark:bg-green-800 dark:text-green-200 text-sm')
            else:
                with ui.card().classes('w-full mb-4 bg-gray-50 dark:bg-gray-700'):
                    ui.label('暂无分配权限').classes('text-gray-500 dark:text-gray-400 text-center py-4')

    @safe_protect(name="编辑角色对话框")
    def edit_role_dialog(role_data: DetachedRole):
        """编辑角色对话框 - 使用安全更新方法"""
        log_info(f"编辑角色: {role_data.name}")
        
        if role_data.is_system:
            ui.notify('系统角色不允许编辑', type='warning')
            return

        with ui.dialog() as dialog, ui.card().classes('w-96'):
            dialog.open()
            ui.label(f'编辑角色: {role_data.name}').classes('text-lg font-semibold')

            # 表单字段
            name_input = ui.input('角色名称', value=role_data.name).classes('w-full')
            display_name_input = ui.input('显示名称', value=role_data.display_name or '').classes('w-full')
            description_input = ui.textarea('描述', value=role_data.description or '').classes('w-full')
            is_active_switch = ui.switch('启用角色', value=role_data.is_active).classes('mt-4')

            def save_role():
                """保存角色修改 - 使用安全更新方法"""
                log_info(f"开始保存角色修改: {role_data.name}")
                
                if not name_input.value.strip():
                    ui.notify('角色名称不能为空', type='warning')
                    return

                # 准备更新数据
                update_data = {
                    'name': name_input.value.strip(),
                    'display_name': display_name_input.value.strip() or None,
                    'description': description_input.value.strip() or None,
                    'is_active': is_active_switch.value
                }

                # 使用安全的更新方法
                success = update_role_safe(role_data.id, **update_data)
                
                if success:
                    log_info(f"角色修改成功: {update_data['name']}")
                    ui.notify('角色信息已更新', type='positive')
                    dialog.close()
                    safe(load_roles)
                else:
                    log_error(f"保存角色修改失败: {role_data.name}")
                    ui.notify('保存失败，角色名称可能已存在', type='negative')

            with ui.row().classes('w-full justify-end gap-2 mt-6'):
                ui.button('取消', on_click=dialog.close).classes('bg-gray-500 text-white')
                ui.button('保存', on_click=lambda: safe(save_role)).classes('bg-blue-500 text-white')

    @safe_protect(name="添加角色对话框")
    def add_role_dialog():
        """添加角色对话框 - 使用安全创建方法"""
        log_info("打开添加角色对话框")
        
        with ui.dialog() as dialog, ui.card().classes('w-96'):
            dialog.open()
            ui.label('创建新角色').classes('text-lg font-semibold')

            # 表单字段
            name_input = ui.input('角色名称', placeholder='如: editor').classes('w-full')
            display_name_input = ui.input('显示名称', placeholder='如: 编辑员').classes('w-full')
            description_input = ui.textarea('描述', placeholder='角色功能描述').classes('w-full')
            is_active_switch = ui.switch('启用角色', value=True).classes('mt-4')

            def save_new_role():
                """保存新角色 - 使用安全创建方法"""
                log_info("开始创建新角色")
                
                if not name_input.value.strip():
                    ui.notify('角色名称不能为空', type='warning')
                    return

                # 使用安全的创建方法
                role_id = create_role_safe(
                    name=name_input.value.strip(),
                    display_name=display_name_input.value.strip() or None,
                    description=description_input.value.strip() or None,
                    is_active=is_active_switch.value
                )
                
                if role_id:
                    log_info(f"新角色创建成功: {name_input.value} (ID: {role_id})")
                    ui.notify(f'角色 {display_name_input.value or name_input.value} 创建成功', type='positive')
                    dialog.close()
                    safe(load_roles)
                else:
                    log_error(f"创建角色失败: {name_input.value}")
                    ui.notify('角色创建失败，名称可能已存在', type='negative')

            with ui.row().classes('w-full justify-end gap-2 mt-6'):
                ui.button('取消', on_click=dialog.close).classes('bg-gray-500 text-white')
                ui.button('创建角色', on_click=lambda: safe(save_new_role)).classes('bg-blue-500 text-white')

    @safe_protect(name="删除角色对话框")
    def delete_role_dialog(role_data: DetachedRole):
        """删除角色对话框 - 使用安全删除方法"""
        log_info(f"打开删除角色对话框: {role_data.name}")
        
        if role_data.is_system:
            ui.notify('系统角色不允许删除', type='warning')
            return

        if role_data.user_count > 0:
            ui.notify(f'角色 {role_data.name} 仍有 {role_data.user_count} 个用户，请先移除用户后再删除', type='warning')
            return

        with ui.dialog() as dialog, ui.card().classes('w-96'):
            dialog.open()
            ui.label('确认删除角色').classes('text-lg font-semibold text-red-600')
            ui.label(f'您确定要删除角色 "{role_data.display_name or role_data.name}" 吗？').classes('mt-2')
            ui.label('此操作不可撤销！').classes('text-red-500 mt-2 font-medium')

            def confirm_delete():
                """确认删除 - 使用安全删除方法"""
                log_info(f"开始删除角色: {role_data.name}")
                
                # 使用安全的删除方法
                success = delete_role_safe(role_data.id)
                
                if success:
                    log_info(f"角色删除成功: {role_data.name}")
                    ui.notify(f'角色 {role_data.name} 已删除', type='positive')
                    dialog.close()
                    safe(load_roles)
                else:
                    log_error(f"删除角色失败: {role_data.name}")
                    ui.notify('删除失败，角色可能仍有用户使用', type='negative')

            with ui.row().classes('w-full justify-end gap-2 mt-6'):
                ui.button('取消', on_click=dialog.close).classes('bg-gray-500 text-white')
                ui.button('确认删除', on_click=lambda: safe(confirm_delete)).classes('bg-red-500 text-white')

    def role_template_dialog():
        """角色模板对话框"""
        log_info("打开角色模板对话框")
        
        with ui.dialog() as dialog, ui.card().classes('w-[500px]'):
            dialog.open()
            ui.label('角色模板').classes('text-lg font-semibold')
            ui.label('选择预定义的角色模板快速创建角色').classes('text-gray-600 mt-2')

            templates = [
                {
                    'name': 'editor',
                    'display_name': '编辑员',
                    'description': '可以编辑和管理内容，但无法管理用户',
                    'icon': 'edit'
                },
                {
                    'name': 'viewer',
                    'display_name': '观察员',
                    'description': '只能查看内容，无法进行任何修改操作',
                    'icon': 'visibility'
                },
                {
                    'name': 'moderator',
                    'display_name': '审核员',
                    'description': '可以审核和管理用户内容，维护社区秩序',
                    'icon': 'gavel'
                },
                {
                    'name': 'analyst',
                    'display_name': '分析师',
                    'description': '可以查看和分析数据报告，生成业务洞察',
                    'icon': 'analytics'
                }
            ]

            for template in templates:
                with ui.card().classes('w-full p-4 mb-3 cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700'):
                    with ui.row().classes('items-center gap-4'):
                        ui.icon(template['icon']).classes('text-3xl text-blue-500')
                        with ui.column().classes('flex-1'):
                            ui.label(template['display_name']).classes('font-bold')
                            ui.label(template['description']).classes('text-sm text-gray-600 dark:text-gray-400')
                        ui.button('使用模板', 
                                 on_click=lambda t=template: create_from_template(dialog, t)).classes('bg-blue-500 text-white')

            ui.button('关闭', on_click=dialog.close).classes('w-full mt-4 bg-gray-500 text-white')

    def create_from_template(parent_dialog, template):
        """从模板创建角色 - 使用安全创建方法"""
        parent_dialog.close()
        log_info(f"从模板创建角色: {template['name']}")
        
        # 使用安全的创建方法
        role_id = create_role_safe(
            name=template['name'],
            display_name=template['display_name'],
            description=template['description'],
            is_active=True
        )
        
        if role_id:
            log_info(f"从模板创建角色成功: {template['name']} (ID: {role_id})")
            ui.notify(f'角色 {template["display_name"]} 创建成功', type='positive')
            safe(load_roles)
        else:
            log_error(f"从模板创建角色失败: {template['name']}")
            ui.notify(f'角色 {template["name"]} 已存在或创建失败', type='negative')

    def export_roles():
        """导出角色功能"""
        log_info("开始导出角色数据")
        
        # 获取所有角色数据
        roles = get_roles_safe()
        
        if not roles:
            ui.notify('暂无角色数据可导出', type='warning')
            return
        
        # 这里可以实现实际的导出逻辑
        # 例如生成CSV、Excel或JSON文件
        export_data = []
        for role in roles:
            export_data.append({
                'ID': role.id,
                '角色名称': role.name,
                '显示名称': role.display_name or '',
                '描述': role.description or '',
                '状态': '活跃' if role.is_active else '禁用',
                '类型': '系统角色' if role.is_system else '自定义角色',
                '用户数量': role.user_count,
                '权限数量': len(role.permissions),
                '创建时间': role.created_at.strftime('%Y-%m-%d %H:%M:%S') if role.created_at else ''
            })
        
        log_info(f"导出角色数据: {len(export_data)} 条记录")
        ui.notify(f'角色数据导出功能开发中... (共{len(export_data)}条记录)', type='info')

    # 初始加载
    safe(load_roles, error_msg="初始化角色列表失败")

    log_info("角色管理页面加载完成")