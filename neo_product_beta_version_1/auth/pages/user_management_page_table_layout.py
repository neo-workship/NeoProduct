"""
用户管理页面 - 修复搜索功能，解决变量作用域问题
"""
from nicegui import ui
from ..decorators import require_role
from ..auth_manager import auth_manager
from ..detached_helper import (
    detached_manager, 
    get_users_safe, 
    get_user_safe,
    get_roles_safe,
    DetachedUser
)
from ..utils import format_datetime, validate_email, validate_username
from ..models import User, Role
from ..database import get_db
import secrets
import string

# 导入异常处理模块
from common.exception_handler import log_info, log_error, safe, db_safe, safe_protect

@require_role('admin')
@safe_protect(name="用户管理页面", error_msg="用户管理页面加载失败，请稍后重试")
def user_management_page_content():
    """用户管理页面内容 - 仅管理员可访问"""
    log_info("用户管理页面开始加载")
    
    # 页面标题
    with ui.column().classes('w-full mb-6'):
        ui.label('用户管理').classes('text-4xl font-bold text-indigo-800 dark:text-indigo-200 mb-2')
        ui.label('管理系统中的所有用户账户').classes('text-lg text-gray-600 dark:text-gray-400')

    # 用户统计卡片
    def load_user_statistics():
        """加载用户统计数据"""
        log_info("开始加载用户统计数据")
        return detached_manager.get_user_statistics()

    # 安全执行统计数据加载
    stats = safe(
        load_user_statistics,
        return_value={'total_users': 0, 'active_users': 0, 'verified_users': 0, 'admin_users': 0},
        error_msg="用户统计数据加载失败"
    )

    with ui.row().classes('w-full gap-6 mb-8'):
        with ui.card().classes('flex-1 p-4 bg-gradient-to-r from-blue-500 to-blue-600 text-white'):
            with ui.row().classes('items-center justify-between w-full'):
                with ui.column().classes('gap-1'):
                    ui.label('总用户数').classes('text-sm opacity-90')
                    ui.label(str(stats['total_users'])).classes('text-3xl font-bold')
                ui.icon('people').classes('text-2xl opacity-80')

        with ui.card().classes('flex-1 p-4 bg-gradient-to-r from-green-500 to-green-600 text-white'):
            with ui.row().classes('items-center justify-between w-full'):
                with ui.column().classes('gap-1'):
                    ui.label('活跃用户').classes('text-sm opacity-90')
                    ui.label(str(stats['active_users'])).classes('text-3xl font-bold')
                ui.icon('check_circle').classes('text-2xl opacity-80')

        with ui.card().classes('flex-1 p-4 bg-gradient-to-r from-orange-500 to-orange-600 text-white'):
            with ui.row().classes('items-center justify-between w-full'):
                with ui.column().classes('gap-1'):
                    ui.label('已验证用户').classes('text-sm opacity-90')
                    ui.label(str(stats['verified_users'])).classes('text-3xl font-bold')
                ui.icon('verified').classes('text-2xl opacity-80')

        with ui.card().classes('flex-1 p-4 bg-gradient-to-r from-purple-500 to-purple-600 text-white'):
            with ui.row().classes('items-center justify-between w-full'):
                with ui.column().classes('gap-1'):
                    ui.label('管理员').classes('text-sm opacity-90')
                    ui.label(str(stats['admin_users'])).classes('text-3xl font-bold')
                ui.icon('admin_panel_settings').classes('text-2xl opacity-80')

    with ui.card().classes('w-full mt-6'):
        ui.label('用户列表').classes('text-lg font-semibold')

        # 操作按钮行
        with ui.row().classes('w-full gap-2 mt-4'):
            ui.button('添加用户', icon='add', on_click=lambda: safe(add_user_dialog)).classes('bg-blue-500 text-white')
            ui.button('导出用户', icon='download', on_click=lambda: safe(export_users)).classes('bg-green-500 text-white')
            # 测试异常按钮
            ui.button('测试异常', icon='bug_report', 
                     on_click=lambda: safe(test_exception_function),
                     color='red').classes('ml-4')

        # 绑定搜索事件处理函数 - 修复搜索功能
        def handle_search():
            """处理搜索事件 - 立即执行"""
            safe(load_users)
        
        def handle_input_search():
            """处理输入搜索事件 - 延迟执行"""
            ui.timer(0.5, lambda: safe(load_users), once=True)
        
        def reset_search():
            """重置搜索"""
            search_input.value = ''
            safe(load_users)

        # 搜索区域 - 在函数定义之后创建
        with ui.row().classes('w-full gap-2 mt-4 items-end'):
            search_input = ui.input(
                '搜索用户', 
                placeholder='输入用户名或邮箱进行搜索...',
                value=''
            ).classes('flex-1').props('outlined clearable')
            search_input.props('prepend-icon=search')
            
            ui.button('搜索', icon='search', 
                     on_click=handle_search).classes('bg-blue-600 hover:bg-blue-700 text-white px-4 py-2')
            ui.button('重置', icon='refresh', 
                     on_click=reset_search).classes('bg-gray-500 hover:bg-gray-600 text-white px-4 py-2')

        # 用户表格容器
        users_container = ui.column().classes('w-full gap-3')

        @safe_protect(name="用户列表加载", error_msg="用户列表加载失败")
        def load_users():
            """加载用户数据 - 使用安全的分离数据，支持搜索"""
            log_info("开始加载用户列表数据")
            users_container.clear()

            # 获取搜索条件 - 确保能正确获取当前搜索框的值
            search_term = search_input.value.strip() if hasattr(search_input, 'value') and search_input.value else None
            
            log_info(f"搜索条件: '{search_term}'")
            
            # 使用安全的数据获取方法，传入搜索条件
            users = get_users_safe(search_term=search_term)
            log_info(f"成功获取{len(users)}个用户数据")

            # 创建表格数据
            columns = [
                {'name': 'id', 'label': 'ID', 'field': 'id', 'sortable': True, 'align': 'center'},
                {'name': 'username', 'label': '用户名', 'field': 'username', 'sortable': True, 'align': 'left'},
                {'name': 'email', 'label': '邮箱', 'field': 'email', 'sortable': True, 'align': 'left'},
                {'name': 'full_name', 'label': '姓名', 'field': 'full_name', 'sortable': True, 'align': 'left'},
                {'name': 'roles', 'label': '角色', 'field': 'roles', 'sortable': False, 'align': 'center'},
                {'name': 'status', 'label': '状态', 'field': 'status', 'sortable': True, 'align': 'center'},
                {'name': 'last_login', 'label': '最后登录', 'field': 'last_login', 'sortable': True, 'align': 'center'},
                {'name': 'actions', 'label': '操作', 'field': 'actions', 'sortable': False, 'align': 'center'},
            ]

            rows = []
            
            with users_container:
                if not users:
                    with ui.card().classes('w-full p-8 text-center bg-gray-50 dark:bg-gray-700'):
                        if search_term:
                            ui.icon('search_off').classes('text-6xl text-gray-400 mb-4')
                            ui.label(f'未找到匹配 "{search_term}" 的用户').classes('text-xl font-medium text-gray-500 dark:text-gray-400')
                            ui.label('请尝试其他关键词或清空搜索条件').classes('text-gray-400 dark:text-gray-500')
                            ui.button('清空搜索', icon='clear', 
                                     on_click=reset_search).classes('mt-4 bg-blue-500 text-white')
                        else:
                            ui.icon('people_off').classes('text-6xl text-gray-400 mb-4')
                            ui.label('暂无用户数据').classes('text-xl font-medium text-gray-500 dark:text-gray-400')
                            ui.label('点击"添加用户"按钮添加第一个用户').classes('text-gray-400 dark:text-gray-500')
                    return

                for user in users:
                    # 角色显示
                    roles_display = ', '.join(user.roles) if user.roles else '无'

                    # 状态显示
                    if user.is_active:
                        status_display = '✅ 活跃' if user.is_verified else '⚠️ 未验证'
                    else:
                        status_display = '❌ 禁用'

                    rows.append({
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'full_name': user.full_name or '-',
                        'roles': roles_display,
                        'status': status_display,
                        'last_login': format_datetime(user.last_login) if user.last_login else '从未登录',
                        'actions': f'edit_{user.id}'
                    })

                # 显示搜索结果统计
                if search_term:
                    ui.label(f'搜索 "{search_term}" 找到 {len(users)} 个用户').classes('text-sm text-gray-600 dark:text-gray-400 mb-2')

                # 创建表格
                user_table = ui.table(columns=columns, rows=rows, row_key='id', pagination=5).classes('w-full')
                
                # 为表格添加操作列的插槽内容
                user_table.add_slot('body-cell-actions', '''
                    <q-td :props="props">
                        <div class="row gap-2 no-wrap">
                            <q-btn 
                                size="md" 
                                color="blue" 
                                icon="edit" 
                                dense 
                                @click="$parent.$emit('edit_user', props.row.id)"
                                class="text-white px-3 py-2">
                                编辑
                            </q-btn>
                            <q-btn 
                                size="md" 
                                color="orange" 
                                icon="lock_reset" 
                                dense 
                                @click="$parent.$emit('reset_password', props.row.id)"
                                class="text-white px-3 py-2">
                                重置密码
                            </q-btn>
                            <q-btn 
                                v-if="props.row.id != ''' + str(auth_manager.current_user.id if auth_manager.current_user else 0) + '''"
                                size="md" 
                                color="red" 
                                icon="delete" 
                                dense 
                                @click="$parent.$emit('delete_user', props.row.id)"
                                class="text-white px-3 py-2">
                                删除
                            </q-btn>
                        </div>
                    </q-td>
                ''')
                
                # 监听表格事件
                user_table.on('edit_user', lambda e: safe(lambda: edit_user_dialog(e.args)))
                user_table.on('reset_password', lambda e: safe(lambda: reset_password_dialog(e.args)))
                user_table.on('delete_user', lambda e: safe(lambda: delete_user_dialog(e.args)))

        @safe_protect(name="添加用户对话框")
        def add_user_dialog():
            """添加用户对话框"""
            log_info("打开添加用户对话框")
            
            with ui.dialog() as dialog, ui.card().classes('w-96'):
                dialog.open()
                ui.label('添加新用户').classes('text-lg font-semibold')

                # 表单字段
                username_input = ui.input('用户名', placeholder='3-50个字符').classes('w-full')
                email_input = ui.input('邮箱', placeholder='有效的邮箱地址').classes('w-full')
                full_name_input = ui.input('姓名', placeholder='可选').classes('w-full')
                password_input = ui.input('密码', password=True, placeholder='至少6个字符').classes('w-full')

                # 角色选择
                available_roles = safe(get_roles_safe, return_value=[])
                
                ui.label('角色权限').classes('mt-4 font-medium')
                role_checkboxes = {}
                for role in available_roles:
                    role_checkboxes[role.name] = ui.checkbox(
                        role.display_name or role.name,
                        value=(role.name == 'user')  # 默认选择user角色
                    ).classes('mt-1')

                def save_new_user():
                    """保存新用户"""
                    log_info("开始创建新用户")
                    
                    # 验证输入
                    username_result = validate_username(username_input.value or '')
                    if not username_result['valid']:
                        ui.notify(username_result['message'], type='warning')
                        log_error(f"用户名验证失败: {username_result['message']}")
                        return

                    if not validate_email(email_input.value or ''):
                        ui.notify('邮箱格式不正确', type='warning')
                        log_error(f"邮箱验证失败: {email_input.value}")
                        return

                    if not password_input.value or len(password_input.value) < 6:
                        ui.notify('密码至少需要6个字符', type='warning')
                        log_error("密码长度不足")
                        return

                    try:
                        with db_safe("创建新用户") as db:
                            # 检查用户名和邮箱是否已存在
                            existing = db.query(User).filter(
                                (User.username == username_input.value) |
                                (User.email == email_input.value)
                            ).first()

                            if existing:
                                ui.notify('用户名或邮箱已存在', type='warning')
                                log_error(f"用户创建失败: 用户名或邮箱已存在 - {username_input.value}, {email_input.value}")
                                return

                            # 创建新用户
                            new_user = User(
                                username=username_input.value.strip(),
                                email=email_input.value.strip(),
                                full_name=full_name_input.value.strip() or None,
                                is_active=True,
                                is_verified=True
                            )
                            new_user.set_password(password_input.value)

                            # 分配角色
                            selected_roles = []
                            for role_name, checkbox in role_checkboxes.items():
                                if checkbox.value:
                                    role = db.query(Role).filter(Role.name == role_name).first()
                                    if role:
                                        new_user.roles.append(role)
                                        selected_roles.append(role_name)

                            db.add(new_user)
                            db.commit()

                            log_info(f"新用户创建成功: {new_user.username}, 角色: {selected_roles}")
                            ui.notify(f'用户 {new_user.username} 创建成功', type='positive')
                            dialog.close()
                            safe(load_users)

                    except Exception as e:
                        log_error(f"创建用户失败: {username_input.value}", exception=e)
                        ui.notify('用户创建失败，请稍后重试', type='negative')

                with ui.row().classes('w-full justify-end gap-2 mt-6'):
                    ui.button('取消', on_click=dialog.close).classes('bg-gray-500 text-white')
                    ui.button('创建用户', on_click=lambda: safe(save_new_user)).classes('bg-blue-500 text-white')

        @safe_protect(name="编辑用户对话框")
        def edit_user_dialog(user_id):
            """编辑用户对话框 - 使用安全的分离数据"""
            log_info(f"打开编辑用户对话框: 用户ID {user_id}")
            
            with ui.dialog() as dialog, ui.card().classes('w-96'):
                dialog.open()
                ui.label('编辑用户').classes('text-lg font-semibold')

                # 安全获取用户数据
                user_data = get_user_safe(user_id)
                if not user_data:
                    ui.label('用户不存在或加载失败').classes('text-red-500')
                    log_error(f"编辑用户失败: 用户ID {user_id} 不存在或加载失败")
                    return

                # 获取可用角色
                available_roles = safe(get_roles_safe, return_value=[])

                # 表单字段
                username_input = ui.input('用户名', value=user_data.username).classes('w-full')
                email_input = ui.input('邮箱', value=user_data.email).classes('w-full')
                full_name_input = ui.input('姓名', value=user_data.full_name or '').classes('w-full')

                # 状态开关
                is_active_switch = ui.switch('账户启用', value=user_data.is_active).classes('mt-4')
                is_verified_switch = ui.switch('邮箱验证', value=user_data.is_verified).classes('mt-2')

                # 角色选择
                ui.label('角色权限').classes('mt-4 font-medium')
                role_checkboxes = {}
                for role in available_roles:
                    role_checkboxes[role.name] = ui.checkbox(
                        role.display_name or role.name,
                        value=role.name in user_data.roles
                    ).classes('mt-1')

                def save_user():
                    """保存用户修改 - 使用安全的更新方法"""
                    log_info(f"开始保存用户修改: 用户ID {user_id}")
                    
                    # 验证输入
                    if not username_input.value.strip():
                        ui.notify('用户名不能为空', type='warning')
                        return

                    if not validate_email(email_input.value):
                        ui.notify('邮箱格式不正确', type='warning')
                        return

                    # 准备更新数据
                    update_data = {
                        'username': username_input.value.strip(),
                        'email': email_input.value.strip(),
                        'full_name': full_name_input.value.strip() or None,
                        'is_active': is_active_switch.value,
                        'is_verified': is_verified_switch.value,
                        'roles': [role_name for role_name, checkbox in role_checkboxes.items() if checkbox.value]
                    }

                    # 使用安全的更新方法
                    success = detached_manager.update_user_safe(user_id, **update_data)
                    
                    if success:
                        log_info(f"用户修改成功: {update_data['username']}, 新角色: {update_data['roles']}")
                        ui.notify('用户信息已更新', type='positive')
                        dialog.close()
                        safe(load_users)
                    else:
                        log_error(f"保存用户修改失败: 用户ID {user_id}")
                        ui.notify('保存失败，请稍后重试', type='negative')

                with ui.row().classes('w-full justify-end gap-2 mt-6'):
                    ui.button('取消', on_click=dialog.close).classes('bg-gray-500 text-white')
                    ui.button('保存', on_click=lambda: safe(save_user)).classes('bg-blue-500 text-white')

        @safe_protect(name="重置密码对话框")
        def reset_password_dialog(user_id):
            """重置密码对话框"""
            log_info(f"打开重置密码对话框: 用户ID {user_id}")
            
            # 安全获取用户数据
            user_data = get_user_safe(user_id)
            if not user_data:
                ui.notify('用户不存在', type='error')
                log_error(f"重置密码失败: 用户ID {user_id} 不存在")
                return
            
            with ui.dialog() as dialog, ui.card().classes('w-96'):
                dialog.open()
                ui.label(f'重置用户密码: {user_data.username}').classes('text-lg font-semibold')

                # 显示生成的密码
                password_display = ui.input('新密码', password=False).classes('w-full mt-4')
                password_display.props('hint="点击下方按钮生成随机密码"')
                password_display.disable()

                def generate_password():
                    """生成随机密码"""
                    length = 12
                    characters = string.ascii_letters + string.digits + "!@#$%^&*"
                    password = ''.join(secrets.choice(characters) for _ in range(length))
                    password_display.enable()
                    password_display.value = password
                    password_display.disable()
                    ui.notify('已生成随机密码', type='info')
                    log_info(f"为用户 {user_data.username} 生成随机密码")

                ui.button('生成随机密码', icon='casino', 
                         on_click=lambda: safe(generate_password)).classes('w-full mt-2 bg-purple-500 text-white')

                def perform_reset():
                    """执行密码重置"""
                    log_info(f"开始重置用户密码: {user_data.username}")
                    
                    if not password_display.value:
                        ui.notify('请先生成密码', type='warning')
                        return

                    try:
                        with db_safe("重置用户密码") as db:
                            user = db.query(User).filter(User.id == user_id).first()
                            if not user:
                                ui.notify('用户不存在', type='error')
                                return

                            # 更新密码
                            user.set_password(password_display.value)
                            user.session_token = None
                            user.remember_token = None
                            db.commit()

                            log_info(f"用户密码重置成功: {user.username}")
                            ui.notify(f'用户 {user.username} 密码重置成功', type='positive')
                            dialog.close()

                    except Exception as e:
                        log_error(f"重置密码失败: {user_data.username}", exception=e)
                        ui.notify('密码重置失败，请稍后重试', type='negative')

                with ui.row().classes('w-full justify-end gap-2 mt-6'):
                    ui.button('取消', on_click=dialog.close).classes('bg-gray-500 text-white')
                    ui.button('重置密码', on_click=lambda: safe(perform_reset)).classes('bg-orange-500 text-white')

        @safe_protect(name="删除用户对话框")
        def delete_user_dialog(user_id):
            """删除用户对话框"""
            log_info(f"打开删除用户对话框: 用户ID {user_id}")
            
            # 安全获取用户数据
            user_data = get_user_safe(user_id)
            if not user_data:
                ui.notify('用户不存在', type='error')
                log_error(f"删除用户失败: 用户ID {user_id} 不存在")
                return
            
            with ui.dialog() as dialog, ui.card().classes('w-96'):
                dialog.open()
                ui.label('确认删除用户').classes('text-lg font-semibold text-red-600')
                ui.label(f'您确定要删除用户 "{user_data.username}" 吗？').classes('mt-2')
                ui.label('此操作不可撤销！').classes('text-red-500 mt-2 font-medium')

                def confirm_delete():
                    """确认删除"""
                    log_info(f"开始删除用户: {user_data.username}")
                    
                    # 检查是否是当前登录用户
                    if auth_manager.current_user and auth_manager.current_user.id == user_id:
                        ui.notify('不能删除当前登录的用户', type='warning')
                        log_error(f"删除用户失败: 尝试删除当前登录用户 {user_data.username}")
                        return

                    # 使用安全的删除方法
                    success = detached_manager.delete_user_safe(user_id)
                    
                    if success:
                        log_info(f"用户删除成功: {user_data.username}")
                        ui.notify(f'用户 {user_data.username} 已删除', type='positive')
                        dialog.close()
                        safe(load_users)
                    else:
                        log_error(f"删除用户失败: {user_data.username}")
                        ui.notify('删除失败，请稍后重试', type='negative')

                with ui.row().classes('w-full justify-end gap-2 mt-6'):
                    ui.button('取消', on_click=dialog.close).classes('bg-gray-500 text-white')
                    ui.button('确认删除', on_click=lambda: safe(confirm_delete)).classes('bg-red-500 text-white')

        def export_users():
            """导出用户功能（测试）"""
            log_info("开始导出用户数据")
            ui.notify('用户导出功能开发中...', type='info')

        def test_exception_function():
            """测试异常处理功能"""
            log_info("触发测试异常")
            raise ValueError("这是一个测试异常，用于验证异常处理功能")

        # 绑定搜索事件 - 确保事件正确绑定和触发
        search_input.on('input', handle_input_search)  # 实时输入搜索（延迟）
        search_input.on('keydown.enter', handle_search)  # 回车键立即搜索
        # search_input.on('blur', handle_search)  # 失去焦点时搜索
        
        # 添加调试信息
        log_info("用户搜索事件已绑定")

        # 初始加载
        safe(load_users, error_msg="初始化用户列表失败")

    log_info("用户管理页面加载完成")