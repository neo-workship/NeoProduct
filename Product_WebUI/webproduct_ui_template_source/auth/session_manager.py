"""
会话管理器 - 处理用户会话和缓存
"""
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class UserSession:
    """用户会话数据类"""
    id: int
    username: str
    email: str
    full_name: Optional[str] = None
    phone: Optional[str] = None
    avatar: Optional[str] = None
    bio: Optional[str] = None
    is_active: bool = True
    is_verified: bool = False
    is_superuser: bool = False
    last_login: Optional[datetime] = None
    login_count: int = 0
    created_at: Optional[datetime] = None
    roles: list = field(default_factory=list)
    permissions: set = field(default_factory=set)
    
    def has_role(self, role_name: str) -> bool:
        """检查是否有指定角色"""
        return role_name in self.roles
    
    def has_permission(self, permission_name: str) -> bool:
        """检查是否有指定权限"""
        return self.is_superuser or permission_name in self.permissions
    
    @classmethod
    def from_user(cls, user) -> 'UserSession':
        """从User模型创建会话对象"""
        # 提取角色名称
        role_names = []
        try:
            role_names = [role.name for role in user.roles]
        except:
            pass
        
        # 提取权限
        permissions = set()
        if user.is_superuser:
            permissions.add('*')  # 超级管理员拥有所有权限
        else:
            try:
                # 用户直接权限
                permissions.update(perm.name for perm in user.permissions)
                # 角色权限
                for role in user.roles:
                    if hasattr(role, 'permissions'):
                        permissions.update(perm.name for perm in role.permissions)
            except:
                pass
        
        return cls(
            id=user.id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            phone=user.phone,
            avatar=user.avatar,
            bio=user.bio,
            is_active=user.is_active,
            is_verified=user.is_verified,
            is_superuser=user.is_superuser,
            last_login=user.last_login,
            login_count=user.login_count,
            created_at=user.created_at,
            roles=role_names,
            permissions=permissions
        )

class SessionManager:
    """会话管理器"""
    
    def __init__(self):
        self._sessions: Dict[str, UserSession] = {}
    
    def create_session(self, token: str, user) -> UserSession:
        """创建会话"""
        session = UserSession.from_user(user)
        self._sessions[token] = session
        return session
    
    def get_session(self, token: str) -> Optional[UserSession]:
        """获取会话"""
        return self._sessions.get(token)
    
    def delete_session(self, token: str):
        """删除会话"""
        if token in self._sessions:
            del self._sessions[token]
    
    def clear_all_sessions(self):
        """清除所有会话"""
        self._sessions.clear()

# 全局会话管理器
session_manager = SessionManager()