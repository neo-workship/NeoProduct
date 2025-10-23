"""
分离数据帮助器 - 解决SQLAlchemy DetachedInstanceError问题的通用工具
增强版本：增加对用户-权限直接关联的支持
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

# 设置日志
# import logging
# logger = logging.getLogger(__name__)
from common.log_handler import (
    log_info, 
    log_error, 
    log_warning,
    log_debug,
    log_success,
    log_trace,
    get_logger
)

@dataclass
class DetachedUser:
    """分离的用户数据类 - 不依赖SQLAlchemy会话"""
    id: int
    username: str
    email: str
    password_hash: str = ""
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
    
    # 关联数据
    roles: List[str] = field(default_factory=list)          # 角色名称列表
    permissions: List[str] = field(default_factory=list)    # 权限名称列表（包括角色权限和直接权限）
    direct_permissions: List[str] = field(default_factory=list)  # 直接分配的权限名称列表
    role_permissions: List[str] = field(default_factory=list)  # 通过角色获得的权限名称列表

    def has_role(self, role_name: str) -> bool:
        """检查是否有指定角色"""
        return role_name in self.roles

    def has_permission(self, permission_name: str) -> bool:
        """检查是否有指定权限（包括角色权限和直接权限）"""
        return self.is_superuser or permission_name in self.permissions

    def has_direct_permission(self, permission_name: str) -> bool:
        """检查是否有直接分配的权限"""
        return permission_name in self.direct_permissions

    def has_role_permission(self, permission_name: str) -> bool:
        """检查是否通过角色拥有权限"""
        return permission_name in self.role_permissions

    def is_locked(self) -> bool:
        """检查用户是否被锁定"""
        return self.locked_until is not None and self.locked_until > datetime.now()

    @classmethod
    def from_user(cls, user) -> 'DetachedUser':
        """从User模型创建分离的用户对象"""
        try:
            from .models import User, Role, Permission
            
            # 提取角色信息
            roles = []
            role_permissions = []
            if hasattr(user, 'roles') and user.roles:
                roles = [role.name for role in user.roles]
                # 收集角色的所有权限
                for role in user.roles:
                    if hasattr(role, 'permissions') and role.permissions:
                        role_permissions.extend([perm.name for perm in role.permissions])

            # 提取直接权限
            direct_permissions = []
            if hasattr(user, 'permissions') and user.permissions:
                direct_permissions = [perm.name for perm in user.permissions]

            # 合并所有权限（去重）
            all_permissions = list(set(role_permissions + direct_permissions))

            return cls(
                id=user.id,
                username=user.username,
                email=user.email,
                password_hash=getattr(user, 'password_hash', ''),
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
                roles=roles,
                permissions=all_permissions,
                direct_permissions=direct_permissions,
                role_permissions=list(set(role_permissions))
            )
        except Exception as e:
            # logger.error(f"创建DetachedUser失败: {e}")
            log_error(f"创建DetachedUser失败: {e}")
            return cls(
                id=user.id,
                username=user.username,
                email=user.email,
                is_active=getattr(user, 'is_active', True),
                is_superuser=getattr(user, 'is_superuser', False)
            )

@dataclass
class DetachedRole:
    """分离的角色数据类"""
    id: int
    name: str
    display_name: Optional[str] = None
    description: Optional[str] = None
    is_active: bool = True
    is_system: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # 权限和用户信息
    permissions: List[str] = field(default_factory=list)
    user_count: int = 0
    users: List[str] = field(default_factory=list)  # 用户名列表

    @classmethod
    def from_role(cls, role) -> 'DetachedRole':
        """从Role模型创建分离的角色对象"""
        try:
            # 提取权限信息
            permissions = []
            if hasattr(role, 'permissions') and role.permissions:
                permissions = [perm.name for perm in role.permissions]

            # 提取用户信息
            users = []
            user_count = 0
            if hasattr(role, 'users') and role.users:
                users = [user.username for user in role.users]
                user_count = len(role.users)

            return cls(
                id=role.id,
                name=role.name,
                display_name=role.display_name,
                description=role.description,
                is_active=role.is_active,
                is_system=role.is_system,
                created_at=role.created_at,
                updated_at=role.updated_at,
                permissions=permissions,
                user_count=user_count,
                users=users
            )
        except Exception as e:
            # logger.error(f"创建DetachedRole失败: {e}")
            log_error(f"创建DetachedRole失败: {e}")
            return cls(
                id=role.id,
                name=role.name,
                display_name=getattr(role, 'display_name', None),
                is_active=getattr(role, 'is_active', True),
                is_system=getattr(role, 'is_system', False)
            )

@dataclass
class DetachedPermission:
    """分离的权限数据类"""
    id: int
    name: str
    display_name: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # 关联信息
    roles: List[str] = field(default_factory=list)  # 关联的角色名称列表
    roles_count: int = 0  # 关联的角色数量
    users_count: int = 0  # 间接关联的用户数量（通过角色）
    direct_users: List[str] = field(default_factory=list)  # 直接关联的用户名称列表
    direct_users_count: int = 0  # 直接关联的用户数量

    @classmethod
    def from_permission(cls, permission) -> 'DetachedPermission':
        """从Permission模型创建分离的权限对象"""
        try:
            # 提取角色信息
            roles = []
            users_count = 0
            if hasattr(permission, 'roles') and permission.roles:
                roles = [role.name for role in permission.roles]
                # 计算间接关联的用户数量（通过角色）
                users_set = set()
                for role in permission.roles:
                    if hasattr(role, 'users') and role.users:
                        users_set.update(user.id for user in role.users)
                users_count = len(users_set)

            # 提取直接关联的用户信息
            direct_users = []
            direct_users_count = 0
            if hasattr(permission, 'users') and permission.users:
                direct_users = [user.username for user in permission.users]
                direct_users_count = len(permission.users)

            return cls(
                id=permission.id,
                name=permission.name,
                display_name=permission.display_name,
                category=permission.category,
                description=permission.description,
                created_at=permission.created_at,
                updated_at=permission.updated_at,
                roles=roles,
                roles_count=len(roles),
                users_count=users_count,
                direct_users=direct_users,
                direct_users_count=direct_users_count
            )
        except Exception as e:
            # logger.error(f"创建DetachedPermission失败: {e}")
            log_error(f"创建DetachedPermission失败: {e}")
            return cls(
                id=permission.id,
                name=permission.name,
                display_name=getattr(permission, 'display_name', None),
                category=getattr(permission, 'category', None),
                description=getattr(permission, 'description', None)
            )


class DetachedDataManager:
    """分离数据管理器 - 处理SQLAlchemy会话依赖问题，增强用户权限关联支持"""

    @staticmethod
    def get_user_safe(user_id: int) -> Optional[DetachedUser]:
        """安全获取用户数据（不会产生DetachedInstanceError）"""
        try:
            from .database import get_db
            from sqlalchemy.orm import joinedload

            with get_db() as db:
                user = db.query(User).options(
                    joinedload(User.roles).joinedload(Role.permissions),
                    joinedload(User.permissions)  # 加载直接权限
                ).filter(User.id == user_id).first()

                if user:
                    return DetachedUser.from_user(user)
                return None

        except Exception as e:
            log_error(f"获取用户数据失败 (ID: {user_id}): {e}")
            return None

    @staticmethod
    def get_users_safe(search_term: str = None, limit: int = None) -> List[DetachedUser]:
        """安全获取用户列表"""
        try:
            from .database import get_db
            from sqlalchemy.orm import joinedload

            with get_db() as db:
                query = db.query(User).options(
                    joinedload(User.roles).joinedload(Role.permissions),
                    joinedload(User.permissions)  # 加载直接权限
                )

                # 搜索过滤
                if search_term:
                    query = query.filter(
                        (User.username.contains(search_term)) |
                        (User.email.contains(search_term)) |
                        (User.full_name.contains(search_term))
                    )

                # 限制数量
                if limit:
                    query = query.limit(limit)

                users = query.all()
                return [DetachedUser.from_user(user) for user in users]

        except Exception as e:
            log_error(f"获取用户列表失败: {e}")
            return []

    @staticmethod
    def get_permission_safe(permission_id: int) -> Optional[DetachedPermission]:
        """安全获取权限数据"""
        try:
            from .database import get_db
            from sqlalchemy.orm import joinedload

            with get_db() as db:
                permission = db.query(Permission).options(
                    joinedload(Permission.roles).joinedload(Role.users),
                    joinedload(Permission.users)  # 加载直接关联的用户
                ).filter(Permission.id == permission_id).first()

                if permission:
                    return DetachedPermission.from_permission(permission)
                return None

        except Exception as e:
            log_error(f"获取权限数据失败 (ID: {permission_id}): {e}")
            return None

    @staticmethod
    def get_permissions_safe(search_term: str = None, category: str = None, limit: int = None) -> List[DetachedPermission]:
        """安全获取权限列表"""
        try:
            from .database import get_db
            from sqlalchemy.orm import joinedload

            with get_db() as db:
                query = db.query(Permission).options(
                    joinedload(Permission.roles).joinedload(Role.users),
                    joinedload(Permission.users)  # 加载直接关联的用户
                )

                # 搜索过滤
                if search_term:
                    query = query.filter(
                        (Permission.name.contains(search_term)) |
                        (Permission.display_name.contains(search_term)) |
                        (Permission.description.contains(search_term))
                    )

                # 分类过滤
                if category:
                    query = query.filter(Permission.category == category)

                # 限制数量
                if limit:
                    query = query.limit(limit)

                permissions = query.all()
                return [DetachedPermission.from_permission(perm) for perm in permissions]

        except Exception as e:
            log_error(f"获取权限列表失败: {e}")
            return []

    @staticmethod
    def get_role_safe(role_id: int) -> Optional[DetachedRole]:
        """安全获取角色数据"""
        try:
            from .database import get_db
            from sqlalchemy.orm import joinedload

            with get_db() as db:
                role = db.query(Role).options(
                    joinedload(Role.permissions),
                    joinedload(Role.users)
                ).filter(Role.id == role_id).first()

                if role:
                    return DetachedRole.from_role(role)
                return None

        except Exception as e:
            log_error(f"获取角色数据失败 (ID: {role_id}): {e}")
            return None

    @staticmethod
    def get_roles_safe() -> List[DetachedRole]:
        """安全获取角色列表"""
        try:
            from .database import get_db
            from sqlalchemy.orm import joinedload

            with get_db() as db:
                roles = db.query(Role).options(
                    joinedload(Role.permissions),
                    joinedload(Role.users)
                ).all()

                return [DetachedRole.from_role(role) for role in roles]

        except Exception as e:
            log_error(f"获取角色列表失败: {e}")
            return []

    @staticmethod
    def update_user_safe(user_id: int, **update_data) -> bool:
        """安全更新用户数据"""
        try:
            from .database import get_db

            with get_db() as db:
                user = db.query(User).filter(User.id == user_id).first()
                if not user:
                    return False

                # 更新基本字段
                basic_fields = ['username', 'email', 'full_name', 'phone', 'avatar', 'bio', 
                               'is_active', 'is_verified', 'is_superuser']
                for field in basic_fields:
                    if field in update_data:
                        setattr(user, field, update_data[field])
                        log_info(f"更新用户字段 {field}: {update_data[field]}")

                db.commit()
                log_info(f"用户更新成功: {user.username}")
                return True

        except Exception as e:
            log_error(f"更新用户失败 (ID: {user_id}): {e}")
            return False

    @staticmethod
    def delete_user_safe(user_id: int) -> bool:
        """安全删除用户"""
        try:
            from .database import get_db

            with get_db() as db:
                user = db.query(User).filter(User.id == user_id).first()
                if not user:
                    return False

                username = user.username
                db.delete(user)
                db.commit()
                log_warning(f"用户删除成功: {username}")
                return True

        except Exception as e:
            log_error(f"删除用户失败 (ID: {user_id}): {e}")
            return False

    @staticmethod
    def lock_user_safe(user_id: int, lock_duration_minutes: int = 30) -> bool:
        """安全锁定用户"""
        try:
            from .database import get_db

            with get_db() as db:
                user = db.query(User).filter(User.id == user_id).first()
                if not user:
                    return False

                user.locked_until = datetime.now() + timedelta(minutes=lock_duration_minutes)
                db.commit()
                log_info(f"用户锁定成功: {user.username}, 锁定到: {user.locked_until}")
                return True

        except Exception as e:
            log_info(f"锁定用户失败 (ID: {user_id}): {e}")
            return False

    @staticmethod
    def unlock_user_safe(user_id: int) -> bool:
        """安全解锁用户"""
        try:
            from .database import get_db

            with get_db() as db:
                user = db.query(User).filter(User.id == user_id).first()
                if not user:
                    return False

                user.locked_until = None
                user.failed_login_count = 0  # 重置失败登录次数
                db.commit()
                log_info(f"用户解锁成功: {user.username}")
                return True

        except Exception as e:
            log_error(f"解锁用户失败 (ID: {user_id}): {e}")
            return False

    @staticmethod
    def batch_unlock_users_safe() -> int:
        """批量解锁所有已锁定的用户"""
        try:
            from .database import get_db

            with get_db() as db:
                locked_users = db.query(User).filter(User.locked_until.isnot(None)).all()
                count = len(locked_users)

                for user in locked_users:
                    user.locked_until = None
                    user.failed_login_count = 0

                db.commit()
                log_info(f"批量解锁用户成功，解锁数量: {count}")
                return count

        except Exception as e:
            log_error(f"批量解锁用户失败: {e}")
            return 0

    @staticmethod
    def create_role_safe(name: str, display_name: str = None, description: str = None, is_active: bool = True) -> Optional[int]:
        """安全创建角色"""
        try:
            from .database import get_db

            with get_db() as db:
                # 检查角色名称是否已存在
                existing = db.query(Role).filter(Role.name == name).first()
                if existing:
                    log_warning(f"角色名称已存在: {name}")
                    return None

                role = Role(
                    name=name,
                    display_name=display_name,
                    description=description,
                    is_active=is_active
                )
                
                db.add(role)
                db.commit()
                
                log_info(f"角色创建成功: {name}")
                return role.id

        except Exception as e:
            log_error(f"创建角色失败: {e}")
            return None

    @staticmethod
    def update_role_safe(role_id: int, **update_data) -> bool:
        """安全更新角色数据"""
        try:
            from .database import get_db

            with get_db() as db:
                role = db.query(Role).filter(Role.id == role_id).first()
                if not role:
                    return False

                # 更新基本字段
                basic_fields = ['display_name', 'description', 'is_active', 'is_system']
                for field in basic_fields:
                    if field in update_data:
                        setattr(role, field, update_data[field])
                        log_info(f"更新角色字段 {field}: {update_data[field]}")

                db.commit()
                log_success(f"角色更新成功: {role.name}")
                return True

        except Exception as e:
            log_error(f"更新角色失败 (ID: {role_id}): {e}")
            return False

    @staticmethod
    def delete_role_safe(role_id: int) -> bool:
        """安全删除角色"""
        try:
            from .database import get_db

            with get_db() as db:
                role = db.query(Role).filter(Role.id == role_id).first()
                if not role:
                    return False

                # 检查是否有用户关联
                if hasattr(role, 'users') and role.users:
                    log_warning(f"无法删除角色，存在用户关联: {role.name}")
                    return False

                role_name = role.name
                db.delete(role)
                db.commit()
                log_success(f"角色删除成功: {role_name}")
                return True

        except Exception as e:
            log_error(f"删除角色失败 (ID: {role_id}): {e}")
            return False

    @staticmethod
    def create_permission_safe(name: str, display_name: str = None, category: str = None, description: str = None) -> Optional[int]:
        """安全创建权限"""
        try:
            from .database import get_db

            with get_db() as db:
                # 检查权限名称是否已存在
                existing = db.query(Permission).filter(Permission.name == name).first()
                if existing:
                    log_warning(f"权限名称已存在: {name}")
                    return None

                permission = Permission(
                    name=name,
                    display_name=display_name,
                    category=category,
                    description=description
                )
                
                db.add(permission)
                db.commit()
                
                log_success(f"权限创建成功: {name}")
                return permission.id

        except Exception as e:
            log_error(f"创建权限失败: {e}")
            return None

    @staticmethod
    def update_permission_safe(permission_id: int, **update_data) -> bool:
        """安全更新权限数据"""
        try:
            from .database import get_db

            with get_db() as db:
                permission = db.query(Permission).filter(Permission.id == permission_id).first()
                if not permission:
                    return False

                # 更新基本字段
                basic_fields = ['display_name', 'category', 'description']
                for field in basic_fields:
                    if field in update_data:
                        setattr(permission, field, update_data[field])
                        log_info(f"更新权限字段 {field}: {update_data[field]}")

                db.commit()
                log_success(f"权限更新成功: {permission.name}")
                return True

        except Exception as e:
            log_error(f"更新权限失败 (ID: {permission_id}): {e}")
            return False

    @staticmethod
    def delete_permission_safe(permission_id: int) -> bool:
        """安全删除权限"""
        try:
            from .database import get_db

            with get_db() as db:
                permission = db.query(Permission).filter(Permission.id == permission_id).first()
                if not permission:
                    return False

                # 检查是否有角色关联
                has_role_associations = hasattr(permission, 'roles') and permission.roles
                has_user_associations = hasattr(permission, 'users') and permission.users
                
                if has_role_associations or has_user_associations:
                    log_warning(f"无法删除权限，存在关联关系: {permission.name}")
                    return False

                permission_name = permission.name
                db.delete(permission)
                db.commit()
                log_success(f"权限删除成功: {permission_name}")
                return True

        except Exception as e:
            log_error(f"删除权限失败 (ID: {permission_id}): {e}")
            return False

    # 新增：用户权限直接关联管理
    @staticmethod
    def add_permission_to_user_safe(user_id: int, permission_id: int) -> bool:
        """安全为用户添加直接权限"""
        try:
            from .database import get_db

            with get_db() as db:
                user = db.query(User).filter(User.id == user_id).first()
                permission = db.query(Permission).filter(Permission.id == permission_id).first()
                
                if not user or not permission:
                    return False

                if permission not in user.permissions:
                    user.permissions.append(permission)
                    db.commit()
                    log_info(f"为用户 {user.username} 添加权限 {permission.name}")
                    return True
                else:
                    log_info(f"用户 {user.username} 已拥有权限 {permission.name}")
                    return True

        except Exception as e:
            log_error(f"为用户添加权限失败 (用户ID: {user_id}, 权限ID: {permission_id}): {e}")
            return False

    @staticmethod
    def remove_permission_from_user_safe(user_id: int, permission_id: int) -> bool:
        """安全从用户移除直接权限"""
        try:
            from .database import get_db

            with get_db() as db:
                user = db.query(User).filter(User.id == user_id).first()
                permission = db.query(Permission).filter(Permission.id == permission_id).first()
                
                if not user or not permission:
                    return False

                if permission in user.permissions:
                    user.permissions.remove(permission)
                    db.commit()
                    log_info(f"从用户 {user.username} 移除权限 {permission.name}")
                    return True
                else:
                    log_info(f"用户 {user.username} 没有权限 {permission.name}")
                    return True

        except Exception as e:
            log_error(f"从用户移除权限失败 (用户ID: {user_id}, 权限ID: {permission_id}): {e}")
            return False

    @staticmethod
    def get_user_direct_permissions_safe(user_id: int) -> List[str]:
        """安全获取用户直接权限列表"""
        try:
            from .database import get_db
            from sqlalchemy.orm import joinedload

            with get_db() as db:
                user = db.query(User).options(
                    joinedload(User.permissions)
                ).filter(User.id == user_id).first()

                if user and hasattr(user, 'permissions') and user.permissions:
                    return [perm.name for perm in user.permissions]
                return []

        except Exception as e:
            log_error(f"获取用户直接权限失败 (用户ID: {user_id}): {e}")
            return []

    @staticmethod
    def get_permission_direct_users_safe(permission_id: int) -> List[Dict[str, Any]]:
        """安全获取权限直接关联的用户列表"""
        try:
            from .database import get_db
            from sqlalchemy.orm import joinedload

            with get_db() as db:
                permission = db.query(Permission).options(
                    joinedload(Permission.users)
                ).filter(Permission.id == permission_id).first()

                if permission and hasattr(permission, 'users') and permission.users:
                    return [
                        {
                            'id': user.id,
                            'username': user.username,
                            'full_name': user.full_name,
                            'email': user.email,
                            'is_active': user.is_active
                        }
                        for user in permission.users
                    ]
                return []

        except Exception as e:
            log_error(f"获取权限直接关联用户失败 (权限ID: {permission_id}): {e}")
            return []

    @staticmethod
    def get_user_statistics() -> Dict[str, int]:
        """获取用户统计数据"""
        try:
            from .database import get_db
            
            with get_db() as db:
                total_users = db.query(User).count()
                active_users = db.query(User).filter(User.is_active == True).count()
                verified_users = db.query(User).filter(User.is_verified == True).count()
                
                # 统计管理员用户（通过角色）
                admin_users = db.query(User).join(User.roles).filter(Role.name == 'admin').count()
                
                # 统计当前锁定的用户
                current_time = datetime.now()
                locked_users = db.query(User).filter(
                    User.locked_until != None,
                    User.locked_until > current_time
                ).count()
                
                superusers = db.query(User).filter(User.is_superuser == True).count()
                
                return {
                    'total_users': total_users,
                    'active_users': active_users,
                    'inactive_users': total_users - active_users,
                    'verified_users': verified_users,  # 保持兼容性
                    'admin_users': admin_users,        # 保持兼容性
                    'locked_users': locked_users,
                    'superusers': superusers
                }
                
        except Exception as e:
            log_error(f"获取用户统计失败: {e}")
            return {
                'total_users': 0,
                'active_users': 0,
                'inactive_users': 0,
                'verified_users': 0,
                'admin_users': 0,
                'locked_users': 0,
                'superusers': 0
            }

    @staticmethod
    def get_role_statistics() -> Dict[str, int]:
        """获取角色统计数据"""
        try:
            from .database import get_db
            
            with get_db() as db:
                total_roles = db.query(Role).count()
                active_roles = db.query(Role).filter(Role.is_active == True).count()
                system_roles = db.query(Role).filter(Role.is_system == True).count()
                
                return {
                    'total_roles': total_roles,
                    'active_roles': active_roles,
                    'inactive_roles': total_roles - active_roles,
                    'system_roles': system_roles,
                    'custom_roles': total_roles - system_roles
                }
                
        except Exception as e:
            log_error(f"获取角色统计失败: {e}")
            return {
                'total_roles': 0,
                'active_roles': 0,
                'inactive_roles': 0,
                'system_roles': 0,
                'custom_roles': 0
            }

    @staticmethod
    def get_permission_statistics() -> Dict[str, int]:
        """获取权限统计数据"""
        try:
            from .database import get_db
            
            with get_db() as db:
                total_permissions = db.query(Permission).count()
                system_permissions = db.query(Permission).filter(Permission.category == '系统').count()
                content_permissions = db.query(Permission).filter(Permission.category == '内容').count()
                
                return {
                    'total_permissions': total_permissions,
                    'system_permissions': system_permissions,
                    'content_permissions': content_permissions,
                    'other_permissions': total_permissions - system_permissions - content_permissions
                }
                
        except Exception as e:
            log_error(f"获取权限统计失败: {e}")
            return {
                'total_permissions': 0,
                'system_permissions': 0,
                'content_permissions': 0,
                'other_permissions': 0
            }


# 需要导入模型类
try:
    from .models import User, Role, Permission
except ImportError:
    log_error("无法导入模型类，某些功能可能不可用")

# 全局实例
detached_manager = DetachedDataManager()

# 便捷函数
def get_user_safe(user_id: int) -> Optional[DetachedUser]:
    """便捷函数：安全获取用户"""
    return detached_manager.get_user_safe(user_id)

def get_users_safe(search_term: str = None, limit: int = None) -> List[DetachedUser]:
    """便捷函数：安全获取用户列表"""
    return detached_manager.get_users_safe(search_term, limit)

def get_role_safe(role_id: int) -> Optional[DetachedRole]:
    """便捷函数：安全获取角色"""
    return detached_manager.get_role_safe(role_id)

def get_roles_safe() -> List[DetachedRole]:
    """便捷函数：安全获取角色列表"""
    return detached_manager.get_roles_safe()

def update_user_safe(user_id: int, **update_data) -> bool:
    """便捷函数：安全更新用户"""
    return detached_manager.update_user_safe(user_id, **update_data)

def update_role_safe(role_id: int, **update_data) -> bool:
    """便捷函数：安全更新角色"""
    return detached_manager.update_role_safe(role_id, **update_data)

def delete_user_safe(user_id: int) -> bool:
    """便捷函数：安全删除用户"""
    return detached_manager.delete_user_safe(user_id)

def delete_role_safe(role_id: int) -> bool:
    """便捷函数：安全删除角色"""
    return detached_manager.delete_role_safe(role_id)

def create_role_safe(name: str, display_name: str = None, description: str = None, is_active: bool = True) -> Optional[int]:
    """便捷函数：安全创建角色"""
    return detached_manager.create_role_safe(name, display_name, description, is_active)

def lock_user_safe(user_id: int, lock_duration_minutes: int = 30) -> bool:
    """便捷函数：安全锁定用户"""
    return detached_manager.lock_user_safe(user_id, lock_duration_minutes)

def unlock_user_safe(user_id: int) -> bool:
    """便捷函数：安全解锁用户"""
    return detached_manager.unlock_user_safe(user_id)

def batch_unlock_users_safe() -> int:
    """便捷函数：批量解锁用户"""
    return detached_manager.batch_unlock_users_safe()

def get_permission_safe(permission_id: int) -> Optional[DetachedPermission]:
    """便捷函数：安全获取权限"""
    return detached_manager.get_permission_safe(permission_id)

def get_permissions_safe(search_term: str = None, category: str = None, limit: int = None) -> List[DetachedPermission]:
    """便捷函数：安全获取权限列表"""
    return detached_manager.get_permissions_safe(search_term, category, limit)

def create_permission_safe(name: str, display_name: str = None, category: str = None, description: str = None) -> Optional[int]:
    """便捷函数：安全创建权限"""
    return detached_manager.create_permission_safe(name, display_name, category, description)

def update_permission_safe(permission_id: int, **update_data) -> bool:
    """便捷函数：安全更新权限"""
    return detached_manager.update_permission_safe(permission_id, **update_data)

def delete_permission_safe(permission_id: int) -> bool:
    """便捷函数：安全删除权限"""
    return detached_manager.delete_permission_safe(permission_id)

# 新增：用户权限直接关联便捷函数
def add_permission_to_user_safe(user_id: int, permission_id: int) -> bool:
    """便捷函数：安全为用户添加直接权限"""
    return detached_manager.add_permission_to_user_safe(user_id, permission_id)

def remove_permission_from_user_safe(user_id: int, permission_id: int) -> bool:
    """便捷函数：安全从用户移除直接权限"""
    return detached_manager.remove_permission_from_user_safe(user_id, permission_id)

def get_user_direct_permissions_safe(user_id: int) -> List[str]:
    """便捷函数：安全获取用户直接权限列表"""
    return detached_manager.get_user_direct_permissions_safe(user_id)

def get_permission_direct_users_safe(permission_id: int) -> List[Dict[str, Any]]:
    """便捷函数：安全获取权限直接关联的用户列表"""
    return detached_manager.get_permission_direct_users_safe(permission_id)