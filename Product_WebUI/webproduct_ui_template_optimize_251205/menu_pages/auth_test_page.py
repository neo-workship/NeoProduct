"""
认证系统测试页面
全面测试用户管理、角色管理、权限管理的功能和效果
使用与其他管理页面一致的 session 管理方式
"""
from nicegui import ui
from auth import auth_manager, require_login
from auth.database import get_db
from auth.models import User, Role, Permission
from sqlmodel import select
from common.log_handler import (
    log_info, log_success, log_warning, log_error,
    safe_protect, get_logger
)

logger = get_logger(__name__)


@safe_protect(name="认证系统测试页面", error_msg="认证系统测试页面加载失败")
@require_login(redirect_to_login=True)
def auth_test_page_content():
    """
    认证系统测试页面内容
    
    功能模块:
    1. 当前用户信息展示
    2. 权限检查测试
    3. 角色管理测试
    4. 用户权限分配测试
    5. 数据库数据查看
    
    采用与 user_management_page.py 一致的 session 管理方式
    """
    
    ui.label('🔐 认证系统全面测试').classes('text-3xl font-bold text-indigo-700 mb-6')
    
    # 获取当前用户 - 直接使用 auth_manager
    current_user = auth_manager.check_session()
    if not current_user:
        ui.label('❌ 无法获取当前用户信息').classes('text-red-600')
        return
    
    # ===========================
    # 第一部分: 当前用户信息
    # ===========================
    with ui.card().classes('w-full mb-6'):
        ui.label('👤 当前登录用户信息').classes('text-2xl font-bold mb-4')
        
        # 从数据库加载完整用户数据 - 使用标准模式
        def load_current_user_info():
            """加载当前用户完整信息"""
            try:
                with get_db() as session:
                    # 重新从数据库加载用户以获取关系数据
                    # UserSession.id 对应 User.id
                    user = session.exec(
                        select(User).where(User.id == current_user.id)
                    ).first()
                    
                    if not user:
                        return None
                    
                    # 刷新关系数据
                    session.refresh(user)
                    
                    return {
                        'username': user.username,
                        'full_name': user.full_name,
                        'email': user.email,
                        'is_superuser': user.is_superuser,
                        'is_active': user.is_active,
                        'roles': [
                            {'name': role.name, 'display_name': role.display_name}
                            for role in (user.roles if hasattr(user, 'roles') else [])
                        ],
                        'permissions': list(user.get_all_permissions())
                    }
            except Exception as e:
                log_error(f"加载用户信息失败: {e}")
                return None
        
        user_info = load_current_user_info()
        
        if user_info:
            with ui.row().classes('w-full gap-4'):
                with ui.column().classes('flex-1'):
                    ui.label(f'用户名: {user_info["username"]}').classes('text-lg')
                    ui.label(f'全名: {user_info["full_name"] or "未设置"}').classes('text-lg')
                    ui.label(f'邮箱: {user_info["email"] or "未设置"}').classes('text-lg')
                    ui.label(f'超级管理员: {"是" if user_info["is_superuser"] else "否"}').classes('text-lg')
                    ui.label(f'账户状态: {"激活" if user_info["is_active"] else "未激活"}').classes('text-lg')
                
                with ui.column().classes('flex-1'):
                    ui.label('📋 当前角色:').classes('text-lg font-semibold')
                    if user_info['roles']:
                        for role in user_info['roles']:
                            ui.label(f'  • {role["display_name"]} ({role["name"]})').classes('text-sm text-blue-600')
                    else:
                        ui.label('  无角色').classes('text-sm text-gray-500')
                    
                    ui.label('🔑 拥有权限数量:').classes('text-lg font-semibold mt-2')
                    if '*' in user_info['permissions']:
                        ui.label('  全部权限 (超级管理员)').classes('text-sm text-green-600')
                    else:
                        ui.label(f'  {len(user_info["permissions"])} 个权限').classes('text-sm text-blue-600')
        else:
            ui.label('加载用户信息失败').classes('text-red-600')
    
    # ===========================
    # 第二部分: 权限检查测试
    # ===========================
    with ui.card().classes('w-full mb-6'):
        ui.label('🧪 权限检查测试').classes('text-2xl font-bold mb-4')
        
        # 测试权限列表
        test_permissions = [
            ('system.manage', '系统管理'),
            ('user.manage', '用户管理'),
            ('role.manage', '角色管理'),
            ('content.create', '创建内容'),
            ('content.edit', '编辑内容'),
            ('content.delete', '删除内容'),
            ('content.view', '查看内容'),
            ('profile.view', '查看个人资料'),
            ('profile.edit', '编辑个人资料'),
        ]
        
        ui.label('检测当前用户是否拥有以下权限:').classes('text-sm text-gray-600 mb-2')
        
        with ui.grid(columns=3).classes('w-full gap-2'):
            for perm_name, perm_display in test_permissions:
                has_perm = auth_manager.has_permission(perm_name)
                
                with ui.card().classes('p-3'):
                    ui.label(perm_display).classes('font-semibold text-sm')
                    ui.label(perm_name).classes('text-xs text-gray-500')
                    
                    if has_perm:
                        ui.label('✅ 有权限').classes('text-green-600 text-sm font-bold mt-2')
                    else:
                        ui.label('❌ 无权限').classes('text-red-600 text-sm font-bold mt-2')
    
    # ===========================
    # 第三部分: 数据库数据查看
    # ===========================
    with ui.card().classes('w-full mb-6'):
        ui.label('📊 数据库数据查看').classes('text-2xl font-bold mb-4')
        
        # 数据展示容器
        data_display = ui.column().classes('w-full')
        
        with ui.row().classes('gap-2 mb-4'):
            def show_all_users():
                """显示所有用户 - 使用标准 session 模式"""
                data_display.clear()
                with data_display:
                    ui.label('👥 所有用户列表').classes('text-xl font-bold mb-3')
                    
                    try:
                        with get_db() as session:
                            users = session.exec(select(User)).all()
                            
                            if not users:
                                ui.label('暂无用户数据').classes('text-gray-500')
                                return
                            
                            # 在 session 内处理所有关系数据
                            rows = []
                            for user in users:
                                session.refresh(user)  # 确保关系数据已加载
                                roles_str = ', '.join([r.display_name for r in user.roles]) if hasattr(user, 'roles') and user.roles else '无'
                                rows.append({
                                    'id': user.id,
                                    'username': user.username,
                                    'full_name': user.full_name or '-',
                                    'email': user.email or '-',
                                    'is_superuser': '是' if user.is_superuser else '否',
                                    'is_active': '是' if user.is_active else '否',
                                    'roles': roles_str,
                                })
                            
                            # 创建表格数据
                            columns = [
                                {'name': 'id', 'label': 'ID', 'field': 'id', 'align': 'left'},
                                {'name': 'username', 'label': '用户名', 'field': 'username', 'align': 'left'},
                                {'name': 'full_name', 'label': '全名', 'field': 'full_name', 'align': 'left'},
                                {'name': 'email', 'label': '邮箱', 'field': 'email', 'align': 'left'},
                                {'name': 'is_superuser', 'label': '超管', 'field': 'is_superuser', 'align': 'center'},
                                {'name': 'is_active', 'label': '激活', 'field': 'is_active', 'align': 'center'},
                                {'name': 'roles', 'label': '角色', 'field': 'roles', 'align': 'left'},
                            ]
                            
                            ui.table(columns=columns, rows=rows, row_key='id').classes('w-full')
                            ui.label(f'共 {len(users)} 个用户').classes('text-sm text-gray-500 mt-2')
                    
                    except Exception as e:
                        log_error(f"查询用户失败: {e}")
                        ui.label(f'查询失败: {str(e)}').classes('text-red-600')
            
            def show_all_roles():
                """显示所有角色 - 使用标准 session 模式"""
                data_display.clear()
                with data_display:
                    ui.label('🎭 所有角色列表').classes('text-xl font-bold mb-3')
                    
                    try:
                        with get_db() as session:
                            roles = session.exec(select(Role)).all()
                            
                            if not roles:
                                ui.label('暂无角色数据').classes('text-gray-500')
                                return
                            
                            # 在 session 内处理所有数据
                            rows = []
                            for role in roles:
                                session.refresh(role)  # 刷新关系数据
                                perm_count = len(role.permissions) if hasattr(role, 'permissions') else 0
                                
                                rows.append({
                                    'id': role.id,
                                    'name': role.name,
                                    'display_name': role.display_name or '-',
                                    'description': role.description or '-',
                                    'is_system': '是' if role.is_system else '否',
                                    'perm_count': perm_count,
                                })
                            
                            columns = [
                                {'name': 'id', 'label': 'ID', 'field': 'id', 'align': 'left'},
                                {'name': 'name', 'label': '角色名', 'field': 'name', 'align': 'left'},
                                {'name': 'display_name', 'label': '显示名', 'field': 'display_name', 'align': 'left'},
                                {'name': 'description', 'label': '描述', 'field': 'description', 'align': 'left'},
                                {'name': 'is_system', 'label': '系统角色', 'field': 'is_system', 'align': 'center'},
                                {'name': 'perm_count', 'label': '权限数', 'field': 'perm_count', 'align': 'center'},
                            ]
                            
                            ui.table(columns=columns, rows=rows, row_key='id').classes('w-full')
                            ui.label(f'共 {len(roles)} 个角色').classes('text-sm text-gray-500 mt-2')
                    
                    except Exception as e:
                        log_error(f"查询角色失败: {e}")
                        ui.label(f'查询失败: {str(e)}').classes('text-red-600')
            
            def show_all_permissions():
                """显示所有权限 - 使用标准 session 模式"""
                data_display.clear()
                with data_display:
                    ui.label('🔑 所有权限列表').classes('text-xl font-bold mb-3')
                    
                    try:
                        with get_db() as session:
                            permissions = session.exec(select(Permission)).all()
                            
                            if not permissions:
                                ui.label('暂无权限数据').classes('text-gray-500')
                                return
                            
                            # 在 session 内处理数据
                            rows = []
                            for perm in permissions:
                                rows.append({
                                    'id': perm.id,
                                    'name': perm.name,
                                    'display_name': perm.display_name or '-',
                                    'category': perm.category or '-',
                                    'description': perm.description or '-',
                                })
                            
                            columns = [
                                {'name': 'id', 'label': 'ID', 'field': 'id', 'align': 'left'},
                                {'name': 'name', 'label': '权限名', 'field': 'name', 'align': 'left'},
                                {'name': 'display_name', 'label': '显示名', 'field': 'display_name', 'align': 'left'},
                                {'name': 'category', 'label': '分类', 'field': 'category', 'align': 'left'},
                                {'name': 'description', 'label': '描述', 'field': 'description', 'align': 'left'},
                            ]
                            
                            ui.table(columns=columns, rows=rows, row_key='id').classes('w-full')
                            ui.label(f'共 {len(permissions)} 个权限').classes('text-sm text-gray-500 mt-2')
                    
                    except Exception as e:
                        log_error(f"查询权限失败: {e}")
                        ui.label(f'查询失败: {str(e)}').classes('text-red-600')
            
            ui.button('查看所有用户', on_click=show_all_users, icon='group').classes('bg-blue-500')
            ui.button('查看所有角色', on_click=show_all_roles, icon='badge').classes('bg-green-500')
            ui.button('查看所有权限', on_click=show_all_permissions, icon='lock').classes('bg-purple-500')
    
    # ===========================
    # 第四部分: 角色-权限关系测试
    # ===========================
    with ui.card().classes('w-full mb-6'):
        ui.label('🔗 角色-权限关系测试').classes('text-2xl font-bold mb-4')
        
        relationship_display = ui.column().classes('w-full')
        
        def show_role_permissions():
            """显示每个角色的权限详情 - 使用标准 session 模式"""
            relationship_display.clear()
            with relationship_display:
                try:
                    with get_db() as session:
                        roles = session.exec(select(Role)).all()
                        
                        if not roles:
                            ui.label('暂无角色数据').classes('text-gray-500')
                            return
                        
                        for role in roles:
                            # 在 session 内刷新关系数据
                            session.refresh(role)
                            
                            with ui.expansion(role.display_name or role.name, icon='badge').classes('w-full mb-2'):
                                with ui.column().classes('p-4'):
                                    ui.label(f'角色标识: {role.name}').classes('text-sm')
                                    ui.label(f'角色描述: {role.description or "无"}').classes('text-sm')
                                    ui.label(f'系统角色: {"是" if role.is_system else "否"}').classes('text-sm')
                                    
                                    ui.separator()
                                    
                                    ui.label('拥有的权限:').classes('font-semibold mt-2')
                                    if hasattr(role, 'permissions') and role.permissions:
                                        # 按分类组织权限
                                        perms_by_category = {}
                                        for perm in role.permissions:
                                            category = perm.category or '其他'
                                            if category not in perms_by_category:
                                                perms_by_category[category] = []
                                            perms_by_category[category].append(perm)
                                        
                                        for category, perms in perms_by_category.items():
                                            ui.label(f'  📁 {category}:').classes('text-sm font-semibold mt-2')
                                            for perm in perms:
                                                ui.label(f'    • {perm.display_name} ({perm.name})').classes('text-xs text-blue-600')
                                    else:
                                        ui.label('  无权限').classes('text-sm text-gray-500')
                
                except Exception as e:
                    log_error(f"查询角色权限关系失败: {e}")
                    ui.label(f'查询失败: {str(e)}').classes('text-red-600')
        
        ui.button('查看角色-权限关系', on_click=show_role_permissions, icon='account_tree').classes('bg-indigo-500')
    
    # ===========================
    # 第五部分: 权限测试工具
    # ===========================
    with ui.card().classes('w-full mb-6'):
        ui.label('🛠️ 权限测试工具').classes('text-2xl font-bold mb-4')
        
        ui.label('输入权限标识,测试当前用户是否拥有该权限:').classes('text-sm text-gray-600 mb-2')
        
        test_result = ui.column().classes('w-full mt-4')
        
        with ui.row().classes('w-full gap-2 items-end'):
            perm_input = ui.input(
                label='权限标识',
                placeholder='例如: user.manage',
                value='user.manage'
            ).classes('flex-1')
            
            def test_permission():
                """测试权限"""
                perm_name = perm_input.value.strip()
                if not perm_name:
                    ui.notify('请输入权限标识', type='warning')
                    return
                
                test_result.clear()
                with test_result:
                    has_perm = auth_manager.has_permission(perm_name)
                    
                    with ui.card().classes('w-full p-4'):
                        ui.label(f'测试权限: {perm_name}').classes('text-lg font-bold')
                        
                        if has_perm:
                            ui.label('✅ 当前用户拥有此权限').classes('text-green-600 text-xl font-bold mt-2')
                            ui.notify(f'权限检查通过: {perm_name}', type='positive')
                        else:
                            ui.label('❌ 当前用户没有此权限').classes('text-red-600 text-xl font-bold mt-2')
                            ui.notify(f'权限检查失败: {perm_name}', type='negative')
                        
                        # 显示用户拥有的所有权限
                        ui.separator()
                        ui.label('当前用户拥有的所有权限:').classes('text-sm font-semibold mt-2')
                        
                        # 从数据库重新加载获取最新权限
                        try:
                            with get_db() as session:
                                user = session.exec(
                                    select(User).where(User.id == current_user.id)
                                ).first()
                                
                                if user:
                                    session.refresh(user)
                                    all_perms = user.get_all_permissions()
                                    
                                    if '*' in all_perms:
                                        ui.label('  🌟 全部权限 (超级管理员)').classes('text-sm text-green-600')
                                    else:
                                        for perm in sorted(all_perms):
                                            ui.label(f'  • {perm}').classes('text-xs text-gray-600')
                                else:
                                    ui.label('  无法加载权限数据').classes('text-sm text-red-500')
                        except Exception as e:
                            log_error(f"加载权限失败: {e}")
                            ui.label('  加载权限失败').classes('text-sm text-red-500')
            
            ui.button('测试权限', on_click=test_permission, icon='check_circle').classes('bg-blue-500')
    
    # ===========================
    # 第六部分: 使用说明
    # ===========================
    with ui.card().classes('w-full'):
        ui.label('📖 使用说明').classes('text-2xl font-bold mb-4')
        
        with ui.column().classes('gap-2'):
            ui.label('1️⃣ 当前用户信息').classes('font-semibold')
            ui.label('   展示当前登录用户的基本信息、角色和权限统计').classes('text-sm text-gray-600')
            
            ui.label('2️⃣ 权限检查测试').classes('font-semibold mt-3')
            ui.label('   快速检查当前用户是否拥有常用权限').classes('text-sm text-gray-600')
            
            ui.label('3️⃣ 数据库数据查看').classes('font-semibold mt-3')
            ui.label('   查看系统中所有的用户、角色、权限数据').classes('text-sm text-gray-600')
            
            ui.label('4️⃣ 角色-权限关系').classes('font-semibold mt-3')
            ui.label('   查看每个角色分配了哪些权限').classes('text-sm text-gray-600')
            
            ui.label('5️⃣ 权限测试工具').classes('font-semibold mt-3')
            ui.label('   输入任意权限标识,测试当前用户是否拥有').classes('text-sm text-gray-600')
            
            ui.separator().classes('my-3')
            
            ui.label('💡 提示:').classes('font-semibold text-blue-600')
            ui.label('   • 使用不同角色的账户登录,可以看到不同的权限效果').classes('text-sm')
            ui.label('   • 超级管理员拥有所有权限').classes('text-sm')
            ui.label('   • 可以在用户管理页面修改用户角色,然后重新登录查看效果').classes('text-sm')
            ui.label('   • 本页面采用与其他管理页面一致的 session 管理方式').classes('text-sm text-green-600')


# 导出
__all__ = ['auth_test_page_content']