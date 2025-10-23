"""
数据库连接和管理模块（重构版）
专注于数据库连接和会话管理，建表功能已迁移到 scripts/init_database.py
"""
from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from contextlib import contextmanager
from .config import auth_config

# 配置日志
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

# 创建基类
Base = declarative_base()

# 全局变量
engine = None
SessionLocal = None

def init_database():
    """初始化数据库连接（不再负责建表）"""
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
        
        log_success(f"数据库连接初始化成功: {auth_config.database_type}")
        
    except Exception as e:
        log_error(f"数据库连接初始化失败: {e}")
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
        log_error(f"数据库操作失败: {e}")
        raise
    finally:
        session.close()

def close_database():
    """关闭数据库连接"""
    global SessionLocal
    
    if SessionLocal:
        SessionLocal.remove()
        log_info("数据库连接已关闭")

def check_connection():
    """检查数据库连接状态"""
    try:
        with get_db() as db:
            db.execute("SELECT 1")
        return True
    except Exception as e:
        log_error(f"数据库连接检查失败: {e}")
        return False

def get_engine():
    """获取数据库引擎（供其他模块使用）"""
    if engine is None:
        init_database()
    return engine

# 兼容性函数（向后兼容旧代码）
def reset_database():
    """重置数据库（已废弃，请使用 scripts/init_database.py --reset）"""
    log_warning("reset_database() 已废弃，请使用 'python scripts/init_database.py --reset'")
    import subprocess
    import sys
    
    try:
        result = subprocess.run([
            sys.executable, 
            'scripts/init_database.py', 
            '--reset', 
            '--test-data'
        ], check=True, capture_output=True, text=True)
        log_info("数据库重置完成")
        return True
    except subprocess.CalledProcessError as e:
        log_error(f"数据库重置失败: {e}")
        return False

# 保留一些重要的初始化函数供快速初始化使用
def quick_init_for_testing():
    """快速初始化（仅用于测试环境）"""
    try:
        init_database()
        
        # 调用统一初始化脚本
        from scripts.init_database import DatabaseInitializer
        
        initializer = DatabaseInitializer()
        initializer.engine = engine
        initializer.SessionLocal = SessionLocal
        
        # 导入模型并创建表
        initializer.import_all_models()
        initializer.create_all_tables()
        
        # 初始化基础数据
        initializer.init_auth_default_data()
        initializer.init_default_permissions()
        initializer.init_role_permissions()
        
        log_success("快速初始化完成")
        return True
        
    except Exception as e:
        log_error(f"快速初始化失败: {e}")
        return False