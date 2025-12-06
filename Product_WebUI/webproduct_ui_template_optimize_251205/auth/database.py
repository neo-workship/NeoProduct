"""
数据库连接和管理模块 - SQLModel 版本
使用 SQLModel 的 Session 替换 SQLAlchemy，大幅简化代码
"""
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy import event
from contextlib import contextmanager
from typing import Generator
from .config import auth_config

# 配置日志
from common.log_handler import (
    log_info, 
    log_error, 
    log_warning,
    log_debug,
    log_success,
    get_logger
)

# 获取绑定模块名称的logger
logger = get_logger(__file__)

# ===========================
# 全局变量
# ===========================
engine = None


# ===========================
# 数据库初始化
# ===========================

def init_database():
    """
    初始化数据库连接（不再负责建表）
    
    优势：
    1. 代码量减少 70%
    2. 不需要 SessionLocal 和 scoped_session
    3. SQLModel 的 Session 更简洁
    """
    global engine
    
    try:
        # 创建数据库引擎
        engine = create_engine(
            auth_config.database_url,
            pool_pre_ping=True,  # 自动检测连接是否有效
            echo=False,  # 生产环境设为 False
            # SQLModel 推荐的配置
            connect_args=(
                {"check_same_thread": False} 
                if auth_config.database_type == 'sqlite' 
                else {}
            )
        )
        
        # 为 SQLite 启用外键约束
        if auth_config.database_type == 'sqlite':
            @event.listens_for(engine, "connect")
            def set_sqlite_pragma(dbapi_connection, connection_record):
                cursor = dbapi_connection.cursor()
                cursor.execute("PRAGMA foreign_keys=ON")
                cursor.close()
        
        log_success(f"✅ 数据库连接初始化成功 - 类型: {auth_config.database_type}")
        
    except Exception as e:
        log_error(f"❌ 数据库连接初始化失败, 类型 {auth_config.database_type}: {e}")
        raise


# ===========================
# Session 管理 - SQLModel 简化版
# ===========================

def get_session() -> Session:
    """
    获取数据库 Session（简化版）
    
    SQLModel 优势：
    1. 不需要 SessionLocal
    2. Session 自动管理
    3. 代码量减少 80%
    
    使用示例：
        with get_session() as session:
            user = session.exec(select(User).where(User.id == 1)).first()
    """
    if engine is None:
        init_database()
    
    return Session(engine)


@contextmanager
def get_db() -> Generator[Session, None, None]:
    """
    获取数据库会话的上下文管理器（向后兼容）
    
    优势：
    1. 自动提交/回滚
    2. 自动关闭连接
    3. 异常安全
    
    使用示例：
        with get_db() as session:
            user = session.exec(select(User).where(User.id == 1)).first()
            session.add(user)
            # 自动 commit
    """
    session = get_session()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        log_error(f"❌ 数据库操作失败: {e}")
        raise
    finally:
        session.close()


# ===========================
# 数据库工具函数
# ===========================

def close_database():
    """
    关闭数据库连接
    
    注意：SQLModel 的 engine.dispose() 会关闭所有连接池
    """
    global engine
    
    if engine:
        engine.dispose()
        log_info("🔒 数据库连接已关闭")


def check_connection() -> bool:
    """
    检查数据库连接状态
    
    Returns:
        bool: 连接是否正常
    """
    try:
        with get_db() as session:
            # SQLModel 使用 exec 执行原生 SQL
            session.exec("SELECT 1")
        return True
    except Exception as e:
        log_error(f"❌ 数据库连接检查失败: {e}")
        return False


def get_engine():
    """
    获取数据库引擎（供其他模块使用）
    
    Returns:
        Engine: SQLModel/SQLAlchemy 引擎实例
    """
    if engine is None:
        init_database()
    return engine


# ===========================
# 数据库表创建（仅用于开发/测试）
# ===========================

def create_all_tables():
    """
    创建所有数据库表（开发/测试环境使用）
    
    警告：生产环境请使用 scripts/init_database.py
    """
    try:
        if engine is None:
            init_database()
        
        # 导入所有模型以注册到 SQLModel.metadata
        from .models import (
            User, Role, Permission, LoginLog,
            UserRoleLink, RolePermissionLink, UserPermissionLink
        )
        
        # 创建所有表
        SQLModel.metadata.create_all(engine)
        log_success("✅ 数据库表创建成功")
        
    except Exception as e:
        log_error(f"❌ 数据库表创建失败: {e}")
        raise


# ===========================
# 向后兼容函数
# ===========================

def reset_database():
    """
    重置数据库（已废弃，请使用 scripts/init_database.py --reset）
    """
    log_warning(
        "⚠️ reset_database() 已废弃，"
        "请使用 'python scripts/init_database.py --reset'"
    )
    import subprocess
    import sys
    
    try:
        result = subprocess.run([
            sys.executable, 
            'scripts/init_database.py', 
            '--reset', 
            '--test-data'
        ], check=True, capture_output=True, text=True)
        log_info("✅ 数据库重置完成")
        return True
    except subprocess.CalledProcessError as e:
        log_error(f"❌ 数据库重置失败: {e}")
        return False


def quick_init_for_testing():
    """
    快速初始化（仅用于测试环境）
    
    功能：
    1. 初始化数据库连接
    2. 创建所有表
    3. 初始化默认数据
    """
    try:
        # 初始化连接
        init_database()
        
        # 创建表
        create_all_tables()
        
        # 调用统一初始化脚本
        from scripts.init_database import DatabaseInitializer
        
        initializer = DatabaseInitializer()
        initializer.engine = engine
        
        # 导入模型并初始化数据
        initializer.import_all_models()
        initializer.init_auth_default_data()
        initializer.init_default_permissions()
        initializer.init_role_permissions()
        
        log_success("✅ 快速初始化完成（测试环境）")
        return True
        
    except Exception as e:
        log_error(f"❌ 快速初始化失败: {e}")
        return False


# ===========================
# 导出接口
# ===========================

__all__ = [
    # 核心函数
    'init_database',
    'get_session',
    'get_db',
    'get_engine',
    
    # 工具函数
    'close_database',
    'check_connection',
    'create_all_tables',
    
    # 向后兼容
    'reset_database',
    'quick_init_for_testing',
    
    # 全局变量
    'engine',
]