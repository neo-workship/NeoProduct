"""
数据库连接和管理模块
使用SQLAlchemy ORM，支持多种数据库
    create_engine (创建数据库连接引擎), 
    event (监听数据库事件), 
    declarative_base (ORM 模型基类), 
    sessionmaker (会话工厂), 
    scoped_session (线程安全的会话管理)
contextlib.contextmanager 用于创建上下文管理器，简化 try...finally 结构
config.auth_config: 导入之前解析的认证配置，获取数据库连接信息和其他默认数据
"""
from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from contextlib import contextmanager
from .config import auth_config
import logging

# 配置日志
logger = logging.getLogger(__name__)

# 创建基类
Base = declarative_base()

# 全局变量
engine = None
SessionLocal = None

def init_database():
    """初始化数据库"""
    global engine, SessionLocal
    
    try:
        # 创建数据库引擎
        engine = create_engine(
            auth_config.database_url,
            pool_pre_ping=True,
            echo=False  # 生产环境设为False
        )
        
        # 为SQLite启用外键约束
        if auth_config.database_type == 'sqlite':
            @event.listens_for(engine, "connect")
            def set_sqlite_pragma(dbapi_connection, connection_record):
                cursor = dbapi_connection.cursor()
                cursor.execute("PRAGMA foreign_keys=ON")
                cursor.close()
        
        # 创建会话工厂
        SessionLocal = scoped_session(
            sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=engine
            )
        )
        
        # 导入所有模型（确保表被创建）
        from . import models
        
        # 创建所有表
        Base.metadata.create_all(bind=engine)
        
        # 初始化默认数据
        _init_default_data()
        # 初始化默认权限
        init_default_permissions()
        # 如果需要重新初始化角色权限关系，取消下面的注释
        init_role_permissions()
        
        logger.info(f"数据库初始化成功: {auth_config.database_type}")
        
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        raise

def get_session():
    """获取数据库会话"""
    if SessionLocal is None:
        init_database()
    return SessionLocal()

@contextmanager
def get_db():
    """获取数据库会话的上下文管理器"""
    session = get_session()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"数据库操作失败: {e}")
        raise
    finally:
        session.close()

def _init_default_data():
    """初始化默认数据"""
    from .models import Role, Permission
    
    with get_db() as db:
        # 检查是否已初始化
        if db.query(Role).first() is not None:
            return
        
        # 创建默认角色
        for role_data in auth_config.default_roles:
            role = Role(
                name=role_data['name'],
                display_name=role_data['display_name'],
                description=role_data['description']
            )
            db.add(role)
        
        # 创建默认权限（预留）
        for perm_data in auth_config.default_permissions:
            permission = Permission(
                name=perm_data['name'],
                display_name=perm_data['display_name'],
                category=perm_data['category']
            )
            db.add(permission)
        
        db.commit()
        logger.info("默认数据初始化完成")

def reset_database():
    """重置数据库（仅用于开发/测试）"""
    global engine
    
    if engine is None:
        init_database()
    
    # 删除所有表
    Base.metadata.drop_all(bind=engine)
    
    # 重新创建所有表
    Base.metadata.create_all(bind=engine)
    
    # 重新初始化默认数据
    _init_default_data()
    
    logger.info("数据库已重置")

def close_database():
    """关闭数据库连接"""
    global SessionLocal
    
    if SessionLocal:
        SessionLocal.remove()
        SessionLocal = None
    
    logger.info("数据库连接已关闭")


def init_default_permissions():
    """初始化默认权限数据"""
    from .models import Permission, Role
    from .database import get_db
    
    default_permissions = [
        # 系统管理权限
        {'name': 'system.manage', 'display_name': '系统管理', 'category': '系统', 'description': '系统设置和配置管理'},
        {'name': 'user.manage', 'display_name': '用户管理', 'category': '系统', 'description': '用户账户的增删改查'},
        {'name': 'role.manage', 'display_name': '角色管理', 'category': '系统', 'description': '角色的创建和权限分配'},
        {'name': 'permission.manage', 'display_name': '权限管理', 'category': '系统', 'description': '权限的创建和管理'},
        {'name': 'log.view', 'display_name': '日志查看', 'category': '系统', 'description': '系统日志和操作记录查看'},
        
        # 内容管理权限
        {'name': 'content.view', 'display_name': '查看内容', 'category': '内容', 'description': '查看系统中的内容和数据'},
        {'name': 'content.create', 'display_name': '创建内容', 'category': '内容', 'description': '创建新的内容和数据'},
        {'name': 'content.edit', 'display_name': '编辑内容', 'category': '内容', 'description': '编辑和修改现有内容'},
        {'name': 'content.delete', 'display_name': '删除内容', 'category': '内容', 'description': '删除内容和数据'},
        {'name': 'content.publish', 'display_name': '发布内容', 'category': '内容', 'description': '发布和上线内容'},
        
        # 数据分析权限
        {'name': 'analytics.view', 'display_name': '查看分析', 'category': '分析', 'description': '查看数据分析和报表'},
        {'name': 'analytics.export', 'display_name': '导出数据', 'category': '分析', 'description': '导出分析数据和报表'},
        {'name': 'dashboard.view', 'display_name': '查看仪表板', 'category': '分析', 'description': '访问数据仪表板'},
        
        # 业务权限
        {'name': 'project.view', 'display_name': '查看项目', 'category': '业务', 'description': '查看项目信息'},
        {'name': 'project.manage', 'display_name': '管理项目', 'category': '业务', 'description': '创建和管理项目'},
        {'name': 'task.view', 'display_name': '查看任务', 'category': '业务', 'description': '查看任务列表'},
        {'name': 'task.manage', 'display_name': '管理任务', 'category': '业务', 'description': '创建和管理任务'},
        
        # 个人权限
        {'name': 'profile.view', 'display_name': '查看个人资料', 'category': '个人', 'description': '查看自己的个人资料'},
        {'name': 'profile.edit', 'display_name': '编辑个人资料', 'category': '个人', 'description': '修改自己的个人资料'},
        {'name': 'password.change', 'display_name': '修改密码', 'category': '个人', 'description': '修改自己的登录密码'},
    ]
    
    try:
        with get_db() as db:
            # 检查是否已经初始化过权限
            existing_count = db.query(Permission).count()
            if existing_count > 0:
                print(f"✅ 权限已存在 {existing_count} 条，跳过初始化")
                return
            
            # 创建默认权限
            created_permissions = []
            for perm_data in default_permissions:
                permission = Permission(
                    name=perm_data['name'],
                    display_name=perm_data['display_name'],
                    category=perm_data['category'],
                    description=perm_data['description']
                )
                db.add(permission)
                created_permissions.append(permission)
            
            db.commit()
            print(f"✅ 创建默认权限 {len(created_permissions)} 条")
            
            # 为管理员角色分配所有权限
            admin_role = db.query(Role).filter(Role.name == 'admin').first()
            if admin_role:
                admin_role.permissions.extend(created_permissions)
                db.commit()
                print(f"✅ 为管理员角色分配了 {len(created_permissions)} 个权限")
            
            # 为普通用户角色分配基础权限
            user_role = db.query(Role).filter(Role.name == 'user').first()
            if user_role:
                basic_permissions = [
                    'content.view', 'profile.view', 'profile.edit', 'password.change',
                    'dashboard.view', 'project.view', 'task.view'
                ]
                user_perms = [p for p in created_permissions if p.name in basic_permissions]
                user_role.permissions.extend(user_perms)
                db.commit()
                print(f"✅ 为普通用户角色分配了 {len(user_perms)} 个基础权限")
                
    except Exception as e:
        print(f"❌ 初始化默认权限失败: {e}")


def init_role_permissions():
    """初始化角色权限关系（如果角色和权限都已存在）"""
    from .models import Permission, Role
    from .database import get_db
    
    # 定义角色权限映射
    role_permission_mapping = {
        'admin': [
            # 管理员拥有所有权限
            'system.manage', 'user.manage', 'role.manage', 'permission.manage', 'log.view',
            'content.view', 'content.create', 'content.edit', 'content.delete', 'content.publish',
            'analytics.view', 'analytics.export', 'dashboard.view',
            'project.view', 'project.manage', 'task.view', 'task.manage',
            'profile.view', 'profile.edit', 'password.change'
        ],
        'editor': [
            # 编辑者权限
            'content.view', 'content.create', 'content.edit', 'content.publish',
            'analytics.view', 'dashboard.view',
            'project.view', 'project.manage', 'task.view', 'task.manage',
            'profile.view', 'profile.edit', 'password.change'
        ],
        'viewer': [
            # 查看者权限
            'content.view', 'analytics.view', 'dashboard.view',
            'project.view', 'task.view',
            'profile.view', 'profile.edit', 'password.change'
        ],
        'user': [
            # 普通用户权限
            'content.view', 'dashboard.view',
            'project.view', 'task.view',
            'profile.view', 'profile.edit', 'password.change'
        ]
    }
    
    try:
        with get_db() as db:
            for role_name, permission_names in role_permission_mapping.items():
                role = db.query(Role).filter(Role.name == role_name).first()
                if not role:
                    continue
                
                # 清除现有权限关联
                role.permissions.clear()
                
                # 添加新的权限关联
                permissions = db.query(Permission).filter(Permission.name.in_(permission_names)).all()
                role.permissions.extend(permissions)
                
                print(f"✅ 为角色 '{role_name}' 分配了 {len(permissions)} 个权限")
            
            db.commit()
            print("✅ 角色权限关系初始化完成")
            
    except Exception as e:
        print(f"❌ 初始化角色权限关系失败: {e}")
