"""
认证相关页面
"""
from .login_page import login_page_content
from .logout_page import logout_page_content
from .register_page import register_page_content
from .profile_page import profile_page_content
from .change_password_page import change_password_page_content

from .permission_management_page import permission_management_page_content
from .role_management_page import role_management_page_content
from .user_management_page import user_management_page_content

# ✅ 新增: 导入大模型配置管理页面
from .llm_config_management_page import llm_config_management_page_content
from .prompt_config_management_page import prompt_config_management_page_content  # ✅ 新增

def no_permission_page_content():
    """权限不足页面"""
    from nicegui import ui
    
    ui.label('权限不足').classes('text-3xl font-bold text-red-600 dark:text-red-400')
    ui.label('您没有访问此功能的权限').classes('text-gray-600 dark:text-gray-400 mt-4')
    
    with ui.card().classes('w-full  mt-6 p-6 text-center'):
        ui.icon('block').classes('text-6xl text-red-500 mb-4')
        ui.label('访问被拒绝').classes('text-xl font-semibold text-red-600')
        ui.label('您需要管理员权限才能访问此功能').classes('text-gray-600 mt-2')
        
        with ui.row().classes('gap-2 mt-6 justify-center'):
            # 选择不同的layout这里要做响应的切换
            # simple_spa_layout->simple_navigate_to / spa_layout->navigate_to
            def go_home():
                from component.simple_spa_layout import simple_navigate_to
                simple_navigate_to('home', '首页')
            
            ui.button('返回首页', icon='home', on_click=go_home).classes('bg-blue-500 text-white')
            ui.button('联系管理员', icon='contact_support', 
                     on_click=lambda: ui.notify('请联系系统管理员申请权限', type='info')).classes('bg-gray-500 text-white')


def get_auth_page_handlers():
    """获取所有认证页面处理函数"""
    return {
        'login': login_page_content,
        'logout': logout_page_content,
        'register': register_page_content,
        'user_profile': profile_page_content,
        'change_password': change_password_page_content,
        'permission_management': permission_management_page_content,
        'role_management': role_management_page_content,
        'user_management': user_management_page_content,
        'no_permission': no_permission_page_content,
        # ✅ 新增: 大模型配置管理页面路由
        'llm_config_management': llm_config_management_page_content,
        'prompt_config_management': prompt_config_management_page_content,  # ✅ 新增
    }

__all__ = [
    'login_page_content',
    'logout_page_content',
    'register_page_content', 
    'profile_page_content',
    'change_password_page_content',
    'permission_management_page_content',
    'role_management_page_content',
    'user_management_page_content',
    'no_permission_page_content',
    # ✅ 新增导出
    'llm_config_management_page_content',
    'prompt_config_management_page_content',  # ✅ 新增导出
    'get_auth_page_handlers'
]