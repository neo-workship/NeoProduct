"""
工具函数模块
"""
import re
from typing import Dict, Any
from .config import auth_config

def validate_email(email: str) -> bool:
    """验证邮箱格式"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password: str) -> Dict[str, Any]:
    """验证密码强度"""
    if len(password) < auth_config.password_min_length:
        return {
            'valid': False, 
            'message': f'密码长度至少需要{auth_config.password_min_length}个字符'
        }
    
    if auth_config.password_require_uppercase and not any(c.isupper() for c in password):
        return {
            'valid': False,
            'message': '密码需要包含至少一个大写字母'
        }
    
    if auth_config.password_require_lowercase and not any(c.islower() for c in password):
        return {
            'valid': False,
            'message': '密码需要包含至少一个小写字母'
        }
    
    if auth_config.password_require_numbers and not any(c.isdigit() for c in password):
        return {
            'valid': False,
            'message': '密码需要包含至少一个数字'
        }
    
    if auth_config.password_require_special:
        special_chars = r'!@#$%^&*()_+-=[]{}|;:,.<>?'
        if not any(c in special_chars for c in password):
            return {
                'valid': False,
                'message': '密码需要包含至少一个特殊字符'
            }
    
    return {'valid': True, 'message': '密码强度符合要求'}

def validate_username(username: str) -> Dict[str, Any]:
    """验证用户名"""
    if len(username) < 3:
        return {
            'valid': False,
            'message': '用户名长度至少需要3个字符'
        }
    
    if len(username) > 50:
        return {
            'valid': False,
            'message': '用户名长度不能超过50个字符'
        }
    
    # 只允许字母、数字、下划线和连字符
    pattern = r'^[a-zA-Z0-9_-]+$'
    if not re.match(pattern, username):
        return {
            'valid': False,
            'message': '用户名只能包含字母、数字、下划线和连字符'
        }
    
    return {'valid': True, 'message': '用户名格式正确'}

def format_datetime(dt) -> str:
    """格式化日期时间"""
    if not dt:
        return ''
    return dt.strftime('%Y-%m-%d %H:%M:%S')

def mask_email(email: str) -> str:
    """遮罩邮箱地址"""
    if not email or '@' not in email:
        return email
    
    username, domain = email.split('@')
    if len(username) <= 3:
        masked_username = username[0] + '*' * (len(username) - 1)
    else:
        masked_username = username[:2] + '*' * (len(username) - 4) + username[-2:]
    
    return f"{masked_username}@{domain}"

def get_avatar_url(user) -> str:
    """获取用户头像URL"""
    if user.avatar:
        return user.avatar
    
    # 使用默认头像或生成Gravatar
    from component.static_resources import static_manager
    return static_manager.get_avatar_path('default_avatar.png')

def sanitize_input(text: str) -> str:
    """清理用户输入"""
    if not text:
        return ''
    
    # 移除首尾空白
    text = text.strip()
    
    # 移除潜在的危险字符
    dangerous_chars = ['<', '>', '&', '"', "'", '\0']
    for char in dangerous_chars:
        text = text.replace(char, '')
    
    return text