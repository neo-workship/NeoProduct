"""
认证和权限管理包
提供用户认证、会话管理和权限控制功能
"""
from .auth_manager import AuthManager, auth_manager
from .session_manager import SessionManager, session_manager, UserSession
from .decorators import require_login, require_role, require_permission
from .models import User, Role, Permission
from .database import init_database
from .config import AuthConfig, auth_config
from .navigation import navigate_to, redirect_to_login, redirect_to_home
from .pages import (
    login_page_content,
    logout_page_content,
    register_page_content,
    profile_page_content,
    change_password_page_content,
    permission_management_page_content,
    role_management_page_content,
    user_management_page_content,
    get_auth_page_handlers
)

# 初始化数据库
init_database()

__all__ = [
    'AuthManager',
    'auth_manager',
    'SessionManager',
    'session_manager',
    'UserSession',
    'require_login',
    'require_role',
    'require_permission',
    'User',
    'Role',
    'Permission',
    'AuthConfig',
    'auth_config',
    'navigate_to',
    'redirect_to_login',
    'redirect_to_home',
    'login_page_content',
    'logout_page_content',
    'register_page_content',
    'profile_page_content',
    'change_password_page_content',
    'permission_management_page_content',
    'role_management_page_content',
    'user_management_page_content',
    'get_auth_page_handlers',
    'init_database'
]