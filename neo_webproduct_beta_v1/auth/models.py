"""
数据模型定义
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Table, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from .database import Base
import hashlib
import secrets

# 用户-角色关联表
user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id', ondelete='CASCADE')),
    Column('role_id', Integer, ForeignKey('roles.id', ondelete='CASCADE'))
)

# 角色-权限关联表（预留给权限管理包使用）
role_permissions = Table(
    'role_permissions',
    Base.metadata,
    Column('role_id', Integer, ForeignKey('roles.id', ondelete='CASCADE')),
    Column('permission_id', Integer, ForeignKey('permissions.id', ondelete='CASCADE'))
)

# 用户-权限关联表（用于特殊权限分配，预留）
user_permissions = Table(
    'user_permissions',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id', ondelete='CASCADE')),
    Column('permission_id', Integer, ForeignKey('permissions.id', ondelete='CASCADE'))
)

class User(Base):
    """用户模型"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    
    # 用户信息
    full_name = Column(String(100))
    phone = Column(String(20))
    avatar = Column(String(255))  # 头像URL
    bio = Column(Text)  # 个人简介
    
    # 状态信息
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)  # 邮箱验证状态
    is_superuser = Column(Boolean, default=False)  # 超级管理员
    
    # 登录信息
    last_login = Column(DateTime)
    login_count = Column(Integer, default=0)
    failed_login_count = Column(Integer, default=0)
    locked_until = Column(DateTime)  # 账户锁定时间
    
    # 会话信息
    session_token = Column(String(255), unique=True)
    remember_token = Column(String(255), unique=True)
    
    # 时间戳
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # 关系
    roles = relationship('Role', secondary=user_roles, back_populates='users')
    permissions = relationship('Permission', secondary=user_permissions, back_populates='users')
    login_logs = relationship('LoginLog', back_populates='user', cascade='all, delete-orphan')
    
    def set_password(self, password: str):
        """设置密码"""
        self.password_hash = self._hash_password(password)
    
    def check_password(self, password: str) -> bool:
        """验证密码"""
        return self.password_hash == self._hash_password(password)
    
    def _hash_password(self, password: str) -> str:
        """密码哈希（简单示例，生产环境建议使用bcrypt）"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def generate_session_token(self) -> str:
        """生成会话令牌"""
        self.session_token = secrets.token_urlsafe(32)
        return self.session_token
    
    def generate_remember_token(self) -> str:
        """生成记住我令牌"""
        self.remember_token = secrets.token_urlsafe(32)
        return self.remember_token
    
    def has_role(self, role_name: str) -> bool:
        """检查是否有指定角色"""
        try:
            return any(role.name == role_name for role in self.roles)
        except:
            # 如果roles未加载，返回False
            return False
    
    def has_permission(self, permission_name: str) -> bool:
        """检查是否有指定权限（预留接口）"""
        # 超级管理员拥有所有权限
        if self.is_superuser:
            return True
        
        try:
            # 检查用户直接分配的权限
            if any(perm.name == permission_name for perm in self.permissions):
                return True
            
            # 检查角色权限
            for role in self.roles:
                if hasattr(role, 'permissions') and any(perm.name == permission_name for perm in role.permissions):
                    return True
        except:
            # 如果关联数据未加载，返回False
            return False
        
        return False
    
    def get_permissions(self) -> set:
        """获取用户的所有权限（预留接口）"""
        if self.is_superuser:
            # 超级管理员返回所有权限
            from .database import get_db
            with get_db() as session:
                all_perms = session.query(Permission).all()
                return {perm.name for perm in all_perms}
        
        permissions = set()
        
        try:
            # 用户直接分配的权限
            permissions.update(perm.name for perm in self.permissions)
            
            # 角色权限
            for role in self.roles:
                if hasattr(role, 'permissions'):
                    permissions.update(perm.name for perm in role.permissions)
        except:
            # 如果关联数据未加载，返回空集合
            pass
        
        return permissions
    
    def __repr__(self):
        return f"<User(username='{self.username}', email='{self.email}')>"

class Role(Base):
    """角色模型"""
    __tablename__ = 'roles'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    display_name = Column(String(100))
    description = Column(Text)
    
    # 状态
    is_active = Column(Boolean, default=True)
    is_system = Column(Boolean, default=False)  # 系统角色不可删除
    
    # 时间戳
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # 关系
    users = relationship('User', secondary=user_roles, back_populates='roles')
    permissions = relationship('Permission', secondary=role_permissions, back_populates='roles')
    
    def __repr__(self):
        return f"<Role(name='{self.name}', display_name='{self.display_name}')>"

class Permission(Base):
    """权限模型（预留给权限管理包使用）"""
    __tablename__ = 'permissions'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    display_name = Column(String(100))
    category = Column(String(50))  # 权限分类
    description = Column(Text)
    
    # 时间戳
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # 关系
    roles = relationship('Role', secondary=role_permissions, back_populates='permissions')
    users = relationship('User', secondary=user_permissions, back_populates='permissions')
    
    def __repr__(self):
        return f"<Permission(name='{self.name}', category='{self.category}')>"

class LoginLog(Base):
    """登录日志模型"""
    __tablename__ = 'login_logs'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    
    # 登录信息
    ip_address = Column(String(45))
    user_agent = Column(String(255))
    login_type = Column(String(20))  # normal, remember_me, oauth
    is_success = Column(Boolean)
    failure_reason = Column(String(100))
    
    # 时间戳
    created_at = Column(DateTime, server_default=func.now())
    
    # 关系
    user = relationship('User', back_populates='login_logs')
    
    def __repr__(self):
        return f"<LoginLog(user_id={self.user_id}, is_success={self.is_success})>"