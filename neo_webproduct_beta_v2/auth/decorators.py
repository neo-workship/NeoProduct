"""
装饰器模块
提供登录验证、角色验证、权限验证等装饰器
"""
from functools import wraps
from nicegui import ui
from .auth_manager import auth_manager
from .config import auth_config
import logging

logger = logging.getLogger(__name__)

def require_login(redirect_to_login: bool = True):
    """
    要求用户登录的装饰器
    
    Args:
        redirect_to_login: 未登录时是否重定向到登录页
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 检查会话
            user = auth_manager.check_session()
            
            if not user:
                logger.warning(f"未认证用户尝试访问受保护资源: {func.__name__}")
                
                if redirect_to_login:
                    ui.notify('请先登录', type='warning')
                    ui.navigate.to(auth_config.login_route)
                else:
                    ui.notify('需要登录才能访问此功能', type='error')
                return
            
            # 更新current_user确保是最新的
            auth_manager.current_user = user
            return func(*args, **kwargs)
        return wrapper
    return decorator

def require_role(*roles):
    """
    要求用户具有指定角色的装饰器
    
    Args:
        *roles: 允许的角色列表
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 首先检查登录
            user = auth_manager.check_session()
            if not user:
                ui.notify('请先登录', type='warning')
                ui.navigate.to(auth_config.login_route)
                return
            
            # 超级管理员跳过角色检查
            if user.is_superuser:
                return func(*args, **kwargs)
            
            # 检查角色
            user_roles = [role.name for role in user.roles]
            if not any(role in user_roles for role in roles):
                logger.warning(f"用户 {user.username} 尝试访问需要角色 {roles} 的资源")
                ui.notify(f'您没有权限访问此功能，需要以下角色之一：{", ".join(roles)}', type='error')
                return
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

def require_permission(*permissions):
    """
    要求用户具有指定权限的装饰器
    
    Args:
        *permissions: 需要的权限列表
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 首先检查登录
            user = auth_manager.check_session()
            if not user:
                ui.notify('请先登录', type='warning')
                ui.open(auth_config.login_route)
                return
            
            # 检查权限
            missing_permissions = []
            for permission in permissions:
                if not auth_manager.has_permission(permission):
                    missing_permissions.append(permission)
            
            if missing_permissions:
                logger.warning(f"用户 {user.username} 缺少权限: {missing_permissions}")
                ui.notify(f'您缺少以下权限：{", ".join(missing_permissions)}', type='error')
                return
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

def public_route(func):
    """
    标记公开路由（不需要认证）的装饰器
    主要用于文档和代码可读性
    """
    func._public_route = True
    return func

def admin_only(func):
    """
    仅管理员可访问的装饰器
    """
    return require_role('admin')(func)

def authenticated_only(func):
    """
    仅需要登录即可访问的装饰器（简化版）
    """
    return require_login(redirect_to_login=True)(func)

# 页面级装饰器
def protect_page(roles=None, permissions=None, redirect_to_login=True):
    """
    保护整个页面的装饰器
    
    Args:
        roles: 允许的角色列表
        permissions: 需要的权限列表
        redirect_to_login: 未登录时是否重定向
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 检查登录
            user = auth_manager.check_session()
            if not user:
                if redirect_to_login:
                    ui.notify('请先登录', type='warning')
                    ui.navigate.to(auth_config.login_route)
                else:
                    ui.notify('需要登录才能访问此页面', type='error')
                return
            
            # 检查角色
            if roles and not user.is_superuser:
                user_roles = [role.name for role in user.roles]
                if not any(role in user_roles for role in roles):
                    ui.notify(f'您没有权限访问此页面', type='error')
                    return
            
            # 检查权限
            if permissions:
                missing = [p for p in permissions if not auth_manager.has_permission(p)]
                if missing:
                    ui.notify(f'您缺少访问此页面的权限', type='error')
                    return
            
            return func(*args, **kwargs)
        return wrapper
    return decorator