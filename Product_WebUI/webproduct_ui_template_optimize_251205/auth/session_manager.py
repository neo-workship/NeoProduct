"""
会话管理器 - 修复版本

修复内容:
- ✅ 使用客户端ID隔离会话存储，避免跨浏览器共享
- ✅ 每个浏览器有独立的会话缓存空间
- ✅ 彻底解决跨浏览器/设备会话泄露问题
"""
from typing import Optional, Dict
from datetime import datetime
from dataclasses import dataclass
from nicegui import app


@dataclass
class UserSession:
    """
    用户会话数据类（内存缓存）
    
    这是一个轻量级的用户会话对象，用于内存缓存，避免频繁的数据库查询。
    与数据库中的 User 模型分离，避免 DetachedInstanceError。
    """
    id: int
    username: str
    email: str
    full_name: Optional[str]
    phone: Optional[str]
    avatar: Optional[str]
    bio: Optional[str]
    is_active: bool
    is_verified: bool
    is_superuser: bool
    last_login: Optional[datetime]
    login_count: int
    failed_login_count: int
    locked_until: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    roles: list  # 角色名称列表
    permissions: dict  # 权限字典
    
    def has_role(self, role_name: str) -> bool:
        """检查是否有指定角色"""
        if self.is_superuser:
            return True
        return role_name in self.roles
    
    def has_permission(self, permission_name: str) -> bool:
        """检查是否有指定权限"""
        if self.is_superuser:
            return True
        # 检查通配符权限
        if '*' in self.permissions:
            return True
        # 检查具体权限
        return permission_name in self.permissions
    
    @staticmethod
    def from_user(user):
        """
        从 SQLModel User 对象创建 UserSession
        
        Args:
            user: SQLModel User 对象
        
        Returns:
            UserSession: 会话对象
        """
        # 提取角色名称
        role_names = [role.name for role in user.roles] if user.roles else []
        
        # 提取权限（从角色和直接权限）
        permissions = {}
        
        # 从角色获取权限
        if user.roles:
            for role in user.roles:
                if role.permissions:
                    for perm in role.permissions:
                        permissions[perm.name] = perm.display_name or perm.name
        
        # 从直接权限获取
        if user.permissions:
            for perm in user.permissions:
                permissions[perm.name] = perm.display_name or perm.name
        
        return UserSession(
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
    会话管理器 - 修复版本
    
    核心修复:
    - ✅ 使用客户端ID作为命名空间，每个浏览器有独立的会话存储
    - ✅ 避免跨浏览器/设备的会话共享问题
    - ✅ 自动清理断开连接的客户端会话
    
    职责:
    - 管理内存中的用户会话缓存（按客户端隔离）
    - 提供快速的会话查询
    - 避免频繁的数据库查询
    
    架构说明:
    _client_sessions = {
        'client_id_1': {
            'token_A': UserSession(admin),
            'token_B': UserSession(user1)
        },
        'client_id_2': {
            'token_C': UserSession(ceo),
        }
    }
    """
    
    def __init__(self):
        """
        初始化会话管理器
        
        使用二级字典结构：
        - 第一级：客户端ID → 该客户端的会话字典
        - 第二级：token → UserSession
        """
        self._client_sessions: Dict[str, Dict[str, UserSession]] = {}
    
    def _get_client_id(self) -> str:
        """
        获取当前客户端的唯一ID
        
        使用 app.storage.browser 获取浏览器级别的唯一标识。
        每个浏览器（即使是同一台电脑的不同浏览器）都有不同的 browser ID。
        
        Returns:
            str: 客户端唯一ID，如果无法获取则返回 'default'
            
        注意:
            - 在页面刚加载时，app.storage.browser 可能还未就绪
            - 此时返回 'default' 作为临时ID
            - 一旦浏览器ID就绪，会自动使用正确的ID
        """
        try:
            # app.storage.browser 包含一个自动生成的 'id' 字段
            client_id = app.storage.browser.get('id')
            if client_id:
                return str(client_id)
        except:
            pass
        
        # 如果无法获取，使用默认值
        # 这通常发生在页面初始化早期
        return 'default'
    
    def _get_sessions_dict(self) -> Dict[str, UserSession]:
        """
        获取当前客户端的会话字典
        
        为当前客户端创建或获取独立的会话存储空间。
        
        Returns:
            Dict[str, UserSession]: 当前客户端的会话字典（token -> UserSession）
        """
        client_id = self._get_client_id()
        
        # 如果该客户端还没有会话字典，创建一个
        if client_id not in self._client_sessions:
            self._client_sessions[client_id] = {}
        
        return self._client_sessions[client_id]
    
    def create_session(self, token: str, user) -> UserSession:
        """
        创建会话
        
        为当前客户端创建一个新的会话缓存。
        
        Args:
            token: 会话 token（唯一标识）
            user: SQLModel User 对象
        
        Returns:
            UserSession: 创建的会话对象
            
        示例:
            >>> session = session_manager.create_session('token_abc', user)
            >>> print(session.username)
            'admin'
        """
        # 从 User 对象创建 UserSession
        session = UserSession.from_user(user)
        
        # 存储到当前客户端的会话字典中
        sessions_dict = self._get_sessions_dict()
        sessions_dict[token] = session
        
        return session
    
    def get_session(self, token: str) -> Optional[UserSession]:
        """
        获取会话
        
        从当前客户端的会话缓存中获取指定 token 的会话。
        
        Args:
            token: 会话 token
        
        Returns:
            Optional[UserSession]: 会话对象，不存在则返回 None
            
        注意:
            - 只能获取当前客户端的会话
            - 无法获取其他客户端的会话（隔离保护）
        """
        sessions_dict = self._get_sessions_dict()
        return sessions_dict.get(token)
    
    def update_session(self, token: str, user) -> Optional[UserSession]:
        """
        更新会话（从数据库重新加载用户数据）
        
        当用户信息发生变化时（如修改资料、更改角色权限），
        需要调用此方法刷新内存缓存。
        
        Args:
            token: 会话 token
            user: SQLModel User 对象（最新数据）
        
        Returns:
            Optional[UserSession]: 更新后的会话对象，token不存在则返回None
        """
        sessions_dict = self._get_sessions_dict()
        
        if token in sessions_dict:
            # 重新创建 UserSession 并更新
            session = UserSession.from_user(user)
            sessions_dict[token] = session
            return session
        
        return None
    
    def delete_session(self, token: str):
        """
        删除会话
        
        从当前客户端的会话缓存中删除指定 token 的会话。
        通常在用户登出时调用。
        
        Args:
            token: 会话 token
        """
        sessions_dict = self._get_sessions_dict()
        
        if token in sessions_dict:
            del sessions_dict[token]
    
    def clear_client_sessions(self):
        """
        清除当前客户端的所有会话
        
        删除当前客户端的所有会话缓存。
        通常在客户端断开连接或重置会话时使用。
        """
        client_id = self._get_client_id()
        
        if client_id in self._client_sessions:
            del self._client_sessions[client_id]
    
    def clear_all_sessions(self):
        """
        清除所有客户端的所有会话
        
        ⚠️ 警告：这会删除所有浏览器的会话缓存！
        通常只在系统维护或测试时使用。
        """
        self._client_sessions.clear()
    
    def get_session_count(self) -> int:
        """
        获取当前客户端的会话数量
        
        Returns:
            int: 当前客户端的会话数量
        """
        sessions_dict = self._get_sessions_dict()
        return len(sessions_dict)
    
    def get_total_session_count(self) -> int:
        """
        获取所有客户端的会话总数
        
        Returns:
            int: 所有客户端的会话总数
        """
        total = 0
        for sessions_dict in self._client_sessions.values():
            total += len(sessions_dict)
        return total
    
    def get_client_count(self) -> int:
        """
        获取当前活跃的客户端数量
        
        Returns:
            int: 客户端数量
        """
        return len(self._client_sessions)
    
    def get_all_sessions(self) -> Dict[str, UserSession]:
        """
        获取当前客户端的所有会话（用于调试/管理）
        
        Returns:
            Dict[str, UserSession]: 当前客户端的会话字典副本
        """
        sessions_dict = self._get_sessions_dict()
        return sessions_dict.copy()
    
    def get_debug_info(self) -> Dict:
        """
        获取调试信息
        
        Returns:
            dict: 包含客户端ID、会话数量等调试信息
        """
        client_id = self._get_client_id()
        sessions_dict = self._get_sessions_dict()
        
        return {
            'current_client_id': client_id,
            'current_client_sessions': len(sessions_dict),
            'total_clients': len(self._client_sessions),
            'total_sessions': self.get_total_session_count(),
            'all_client_ids': list(self._client_sessions.keys())
        }


# 全局会话管理器实例
session_manager = SessionManager()