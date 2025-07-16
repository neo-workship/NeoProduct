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