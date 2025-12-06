"""
会话管理器 - SQLModel 版本
移除对 detached_helper 的依赖,直接使用 SQLModel User 对象
"""
from typing import Optional, Dict, Set
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class UserSession:
    """
    用户会话数据类
    
    核心改进 (SQLModel 版本):
    - 直接从 User 模型创建,无需 Detached 转换
    - 保持轻量级内存缓存
    - 与 SQLModel User 模型完全兼容
    """
    id: int
    username: str
    email: str
    full_name: Optional[str] = None
    phone: Optional[str] = None
    avatar: Optional[str] = None
    bio: Optional[str] = None
    
    # 状态信息
    is_active: bool = True
    is_verified: bool = False
    is_superuser: bool = False
    
    # 登录信息
    last_login: Optional[datetime] = None
    login_count: int = 0
    failed_login_count: int = 0
    locked_until: Optional[datetime] = None
    
    # 时间戳
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    # 关联数据 (存储为字符串列表/集合)
    roles: list = field(default_factory=list)          # 角色名称列表
    permissions: Set[str] = field(default_factory=set)  # 权限名称集合 (包括角色权限和直接权限)
    
    def has_role(self, role_name: str) -> bool:
        """检查是否有指定角色"""
        return role_name in self.roles
    
    def has_permission(self, permission_name: str) -> bool:
        """检查是否有指定权限"""
        return self.is_superuser or permission_name in self.permissions
    
    def is_locked(self) -> bool:
        """检查用户是否被锁定"""
        return self.locked_until is not None and self.locked_until > datetime.now()
    
    @classmethod
    def from_user(cls, user) -> 'UserSession':
        """
        从 SQLModel User 对象创建会话对象
        
        核心改进:
        - 直接访问 user.roles 和 user.permissions (SQLModel 自动处理关系)
        - 不需要 joinedload
        - 不会产生 DetachedInstanceError
        """
        # 提取角色名称
        role_names = []
        try:
            # SQLModel: user.roles 返回 List[Role] 对象
            role_names = [role.name for role in user.roles]
        except Exception as e:
            # 如果关系未加载,返回空列表
            pass
        
        # 提取权限 (包括角色权限和直接权限)
        permissions = set()
        if user.is_superuser:
            permissions.add('*')  # 超级管理员拥有所有权限
        else:
            try:
                # 1. 用户直接分配的权限
                if hasattr(user, 'permissions') and user.permissions:
                    permissions.update(perm.name for perm in user.permissions)
                
                # 2. 角色权限
                if hasattr(user, 'roles') and user.roles:
                    for role in user.roles:
                        if hasattr(role, 'permissions') and role.permissions:
                            permissions.update(perm.name for perm in role.permissions)
            except Exception as e:
                # 如果关系未加载,保持空集合
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
            failed_login_count=user.failed_login_count,
            locked_until=user.locked_until,
            created_at=user.created_at,
            updated_at=user.updated_at,
            roles=role_names,
            permissions=permissions
        )


class SessionManager:
    """
    会话管理器
    
    职责:
    - 管理内存中的用户会话缓存
    - 提供快速的会话查询
    - 避免频繁的数据库查询
    """
    
    def __init__(self):
        self._sessions: Dict[str, UserSession] = {}
    
    def create_session(self, token: str, user) -> UserSession:
        """
        创建会话
        
        Args:
            token: 会话 token
            user: SQLModel User 对象
        
        Returns:
            UserSession: 会话对象
        """
        session = UserSession.from_user(user)
        self._sessions[token] = session
        return session
    
    def get_session(self, token: str) -> Optional[UserSession]:
        """
        获取会话
        
        Args:
            token: 会话 token
        
        Returns:
            Optional[UserSession]: 会话对象,不存在则返回 None
        """
        return self._sessions.get(token)
    
    def update_session(self, token: str, user) -> Optional[UserSession]:
        """
        更新会话 (从数据库重新加载用户数据)
        
        Args:
            token: 会话 token
            user: SQLModel User 对象
        
        Returns:
            Optional[UserSession]: 更新后的会话对象
        """
        if token in self._sessions:
            session = UserSession.from_user(user)
            self._sessions[token] = session
            return session
        return None
    
    def delete_session(self, token: str):
        """
        删除会话
        
        Args:
            token: 会话 token
        """
        if token in self._sessions:
            del self._sessions[token]
    
    def clear_all_sessions(self):
        """清除所有会话"""
        self._sessions.clear()
    
    def get_session_count(self) -> int:
        """获取当前会话数量"""
        return len(self._sessions)
    
    def get_all_sessions(self) -> Dict[str, UserSession]:
        """获取所有会话 (用于调试/管理)"""
        return self._sessions.copy()


# 全局会话管理器实例
session_manager = SessionManager()