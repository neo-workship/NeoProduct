"""
数据模型定义 - SQLModel 版本
使用 SQLModel 替换 SQLAlchemy，消除 DetachedInstanceError 问题
"""
from sqlmodel import SQLModel, Field, Relationship, Column, String, Text
from typing import Optional, List, Set
from datetime import datetime
import hashlib
import secrets

# ===========================
# 关联表定义
# ===========================

class UserRoleLink(SQLModel, table=True):
    """用户-角色关联表"""
    __tablename__ = "user_roles"
    
    user_id: Optional[int] = Field(
        default=None, 
        foreign_key="users.id", 
        primary_key=True,
        ondelete="CASCADE"
    )
    role_id: Optional[int] = Field(
        default=None, 
        foreign_key="roles.id", 
        primary_key=True,
        ondelete="CASCADE"
    )


class RolePermissionLink(SQLModel, table=True):
    """角色-权限关联表"""
    __tablename__ = "role_permissions"
    
    role_id: Optional[int] = Field(
        default=None, 
        foreign_key="roles.id", 
        primary_key=True,
        ondelete="CASCADE"
    )
    permission_id: Optional[int] = Field(
        default=None, 
        foreign_key="permissions.id", 
        primary_key=True,
        ondelete="CASCADE"
    )


class UserPermissionLink(SQLModel, table=True):
    """用户-权限关联表（直接权限分配）"""
    __tablename__ = "user_permissions"
    
    user_id: Optional[int] = Field(
        default=None, 
        foreign_key="users.id", 
        primary_key=True,
        ondelete="CASCADE"
    )
    permission_id: Optional[int] = Field(
        default=None, 
        foreign_key="permissions.id", 
        primary_key=True,
        ondelete="CASCADE"
    )


# ===========================
# 主要模型定义
# ===========================

class User(SQLModel, table=True):
    """用户模型 - SQLModel 版本
    
    优势：
    1. 自动支持 Pydantic 验证
    2. 自动序列化为 dict/JSON
    3. 不会产生 DetachedInstanceError
    4. 类型提示完善
    """
    __tablename__ = "users"
    
    # 主键
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    
    # 基本信息
    username: str = Field(
        max_length=50, 
        unique=True, 
        index=True,
        description="用户名，唯一标识"
    )
    email: str = Field(
        max_length=100, 
        unique=True, 
        index=True,
        description="电子邮箱"
    )
    password_hash: str = Field(max_length=255, description="密码哈希值")
    full_name: Optional[str] = Field(default=None, max_length=100, description="全名")
    phone: Optional[str] = Field(default=None, max_length=20, description="手机号")
    avatar: Optional[str] = Field(default=None, max_length=255, description="头像URL")
    bio: Optional[str] = Field(default=None, sa_column=Column(Text), description="个人简介")
    
    # 状态信息
    is_active: bool = Field(default=True, description="账户是否激活")
    is_verified: bool = Field(default=False, description="邮箱是否验证")
    is_superuser: bool = Field(default=False, description="是否超级管理员")
    
    # 登录信息
    last_login: Optional[datetime] = Field(default=None, description="最后登录时间")
    login_count: int = Field(default=0, description="登录次数")
    failed_login_count: int = Field(default=0, description="失败登录次数")
    locked_until: Optional[datetime] = Field(default=None, description="账户锁定至")
    
    # Token 管理
    session_token: Optional[str] = Field(default=None, max_length=255, description="会话令牌")
    remember_token: Optional[str] = Field(default=None, max_length=255, description="记住我令牌")
    # reset_token: Optional[str] = Field(default=None, max_length=255, description="密码重置令牌")
    # reset_token_expires: Optional[datetime] = Field(default=None, description="重置令牌过期时间")
    
    # 时间戳
    created_at: Optional[datetime] = Field(
        default_factory=datetime.now,
        description="创建时间"
    )
    updated_at: Optional[datetime] = Field(
        default_factory=datetime.now,
        description="更新时间"
    )
    
    # 关系定义（延迟导入避免循环依赖）
    roles: List["Role"] = Relationship(
        back_populates="users",
        link_model=UserRoleLink
    )
    permissions: List["Permission"] = Relationship(
        back_populates="users",
        link_model=UserPermissionLink
    )
    login_logs: List["LoginLog"] = Relationship(back_populates="user")
    
    # ===========================
    # 业务方法
    # ===========================
    
    def set_password(self, password: str):
        """设置密码（哈希存储）"""
        salt = secrets.token_hex(16)
        self.password_hash = hashlib.sha256(f"{password}{salt}".encode()).hexdigest() + f":{salt}"
    
    def check_password(self, password: str) -> bool:
        """验证密码"""
        try:
            stored_hash, salt = self.password_hash.split(':')
            test_hash = hashlib.sha256(f"{password}{salt}".encode()).hexdigest()
            return stored_hash == test_hash
        except:
            return False
    
    def has_role(self, role_name: str) -> bool:
        """检查是否有指定角色"""
        if self.is_superuser:
            return True
        try:
            return any(role.name == role_name for role in self.roles)
        except:
            return False
    
    def has_permission(self, permission_name: str) -> bool:
        """检查是否有指定权限（包括角色权限和直接权限）"""
        if self.is_superuser:
            return True
        
        try:
            # 检查用户直接分配的权限
            if any(perm.name == permission_name for perm in self.permissions):
                return True
            
            # 检查角色权限
            for role in self.roles:
                if hasattr(role, 'permissions') and any(
                    perm.name == permission_name for perm in role.permissions
                ):
                    return True
        except:
            return False
        
        return False
    
    def get_all_permissions(self) -> Set[str]:
        """获取用户的所有权限（角色权限 + 直接权限）"""
        if self.is_superuser:
            # 超级管理员拥有所有权限
            return {'*'}
        
        permissions = set()
        
        try:
            # 用户直接分配的权限
            permissions.update(perm.name for perm in self.permissions)
            
            # 角色权限
            for role in self.roles:
                if hasattr(role, 'permissions'):
                    permissions.update(perm.name for perm in role.permissions)
        except:
            pass
        
        return permissions
    
    def is_locked(self) -> bool:
        """检查用户是否被锁定"""
        return self.locked_until is not None and self.locked_until > datetime.now()
    
    # ===========================
    # Pydantic Config
    # ===========================
    
    class Config:
        """Pydantic 配置"""
        json_schema_extra = {
            "example": {
                "username": "admin",
                "email": "admin@example.com",
                "full_name": "Administrator",
                "is_active": True,
                "is_superuser": True
            }
        }


class Role(SQLModel, table=True):
    """角色模型 - SQLModel 版本"""
    __tablename__ = "roles"
    
    # 主键
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    
    # 基本信息
    name: str = Field(
        max_length=50, 
        unique=True, 
        index=True,
        description="角色名称（英文标识）"
    )
    display_name: Optional[str] = Field(default=None, max_length=100, description="显示名称（中文）")
    description: Optional[str] = Field(default=None, sa_column=Column(Text), description="角色描述")
    
    # 状态
    is_active: bool = Field(default=True, description="是否启用")
    is_system: bool = Field(default=False, description="是否系统角色（不可删除）")
    
    # 时间戳
    created_at: Optional[datetime] = Field(
        default_factory=datetime.now,
        description="创建时间"
    )
    updated_at: Optional[datetime] = Field(
        default_factory=datetime.now,
        description="更新时间"
    )
    
    # 关系定义
    users: List["User"] = Relationship(
        back_populates="roles",
        link_model=UserRoleLink
    )
    permissions: List["Permission"] = Relationship(
        back_populates="roles",
        link_model=RolePermissionLink
    )
    
    # ===========================
    # Pydantic Config
    # ===========================
    
    class Config:
        """Pydantic 配置"""
        json_schema_extra = {
            "example": {
                "name": "admin",
                "display_name": "系统管理员",
                "description": "拥有系统最高权限",
                "is_active": True,
                "is_system": True
            }
        }


class Permission(SQLModel, table=True):
    """权限模型 - SQLModel 版本"""
    __tablename__ = "permissions"
    
    # 主键
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    
    # 基本信息
    name: str = Field(
        max_length=100, 
        unique=True, 
        index=True,
        description="权限名称（英文标识）"
    )
    display_name: Optional[str] = Field(default=None, max_length=100, description="显示名称（中文）")
    category: Optional[str] = Field(default=None, max_length=50, description="权限分类")
    description: Optional[str] = Field(default=None, sa_column=Column(Text), description="权限描述")
    
    # 时间戳
    created_at: Optional[datetime] = Field(
        default_factory=datetime.now,
        description="创建时间"
    )
    updated_at: Optional[datetime] = Field(
        default_factory=datetime.now,
        description="更新时间"
    )
    
    # 关系定义
    roles: List["Role"] = Relationship(
        back_populates="permissions",
        link_model=RolePermissionLink
    )
    users: List["User"] = Relationship(
        back_populates="permissions",
        link_model=UserPermissionLink
    )
    
    # ===========================
    # Pydantic Config
    # ===========================
    
    class Config:
        """Pydantic 配置"""
        json_schema_extra = {
            "example": {
                "name": "user.create",
                "display_name": "创建用户",
                "category": "user",
                "description": "允许创建新用户账户"
            }
        }


class LoginLog(SQLModel, table=True):
    """登录日志模型 - SQLModel 版本"""
    __tablename__ = "login_logs"
    
    # 主键
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    
    # 关联用户
    user_id: Optional[int] = Field(default=None, foreign_key="users.id", ondelete="CASCADE")
    
    # 登录信息
    ip_address: Optional[str] = Field(default=None, max_length=45, description="IP地址")
    user_agent: Optional[str] = Field(default=None, max_length=255, description="User-Agent")
    login_type: Optional[str] = Field(
        default="normal", 
        max_length=20,
        description="登录类型: normal, remember_me, oauth"
    )
    is_success: bool = Field(default=True, description="是否登录成功")
    failure_reason: Optional[str] = Field(default=None, max_length=100, description="失败原因")
    
    # 时间戳
    created_at: Optional[datetime] = Field(
        default_factory=datetime.now,
        description="登录时间"
    )
    
    # 关系定义
    user: Optional["User"] = Relationship(back_populates="login_logs")
    
    # ===========================
    # Pydantic Config
    # ===========================
    
    class Config:
        """Pydantic 配置"""
        json_schema_extra = {
            "example": {
                "user_id": 1,
                "ip_address": "192.168.1.100",
                "login_type": "normal",
                "is_success": True
            }
        }


# ===========================
# 模型更新钩子
# ===========================

def update_timestamp(model: SQLModel):
    """更新时间戳的辅助函数"""
    if hasattr(model, 'updated_at'):
        model.updated_at = datetime.now()


# ===========================
# 导出所有模型
# ===========================

__all__ = [
    'User',
    'Role',
    'Permission',
    'LoginLog',
    'UserRoleLink',
    'RolePermissionLink',
    'UserPermissionLink',
    'update_timestamp'
]