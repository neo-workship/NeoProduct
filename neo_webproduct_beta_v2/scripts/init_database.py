#!/usr/bin/env python3
"""
统一数据库初始化脚本
负责创建所有表（认证表 + 业务表）并进行数据初始化
在 scripts/init_database.py 中尝试导入 UserRole、RolePermission、UserPermission，但这些在 auth.models 中是关联表（Table），不是模型类
"""
import os
import sys
import logging
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from contextlib import contextmanager

# 导入配置
from auth.config import auth_config

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DatabaseInitializer:
    """数据库初始化器"""
    
    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        self.Base = declarative_base()
        
    def create_engine_and_session(self):
        """创建数据库引擎和会话"""
        try:
            # 创建数据库引擎
            self.engine = create_engine(
                auth_config.database_url,
                pool_pre_ping=True,
                echo=False  # 生产环境设为False
            )
            
            # 为SQLite启用外键约束
            if auth_config.database_type == 'sqlite':
                @event.listens_for(self.engine, "connect")
                def set_sqlite_pragma(dbapi_connection, connection_record):
                    cursor = dbapi_connection.cursor()
                    cursor.execute("PRAGMA foreign_keys=ON")
                    cursor.close()
            
            # 创建会话工厂
            self.SessionLocal = scoped_session(
                sessionmaker(
                    autocommit=False,
                    autoflush=False,
                    bind=self.engine
                )
            )
            
            logger.info(f"数据库引擎创建成功: {auth_config.database_type}")
            
        except Exception as e:
            logger.error(f"数据库引擎创建失败: {e}")
            raise
    
    @contextmanager
    def get_db_session(self):
        """获取数据库会话的上下文管理器"""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"数据库操作失败: {e}")
            raise
        finally:
            session.close()
    
    def import_all_models(self):
        """导入所有模型以确保表能被创建"""
        try:
            # 导入认证模型
            from auth.models import User, Role, Permission, UserRole, RolePermission, UserPermission
            logger.info("✅ 认证模型导入成功")
            
            # 导入业务模型
            from database_models.business_models.openai_models import OpenAIConfig, OpenAIRequest
            logger.info("✅ OpenAI业务模型导入成功")
            
            # 在这里添加其他业务模型的导入
            # from database_models.business_models.mongodb_models import MongoDBConfig
            # from database_models.business_models.audit_models import AuditRecord
            # logger.info("✅ 其他业务模型导入成功")
            
            logger.info("所有模型导入完成")
            
        except ImportError as e:
            logger.error(f"模型导入失败: {e}")
            raise
    
    def create_all_tables(self):
        """创建所有表"""
        try:
            # 确保所有模型都已导入
            self.import_all_models()
            
            # 获取Base类（统一使用auth.database中的Base）
            from auth.database import Base
            
            # 创建所有表
            Base.metadata.create_all(bind=self.engine)
            logger.info("✅ 所有数据表创建成功")
            
        except Exception as e:
            logger.error(f"表创建失败: {e}")
            raise
    
    def init_auth_default_data(self):
        """初始化认证相关的默认数据"""
        from auth.models import Role, Permission
        
        try:
            with self.get_db_session() as db:
                # 检查是否已初始化
                if db.query(Role).first() is not None:
                    logger.info("认证默认数据已存在，跳过初始化")
                    return
                
                # 创建默认角色
                for role_data in auth_config.default_roles:
                    role = Role(
                        name=role_data['name'],
                        display_name=role_data['display_name'],
                        description=role_data['description']
                    )
                    db.add(role)
                
                # 创建默认权限
                for perm_data in auth_config.default_permissions:
                    permission = Permission(
                        name=perm_data['name'],
                        display_name=perm_data['display_name'],
                        category=perm_data['category']
                    )
                    db.add(permission)
                
                db.commit()
                logger.info("✅ 认证默认数据初始化完成")
                
        except Exception as e:
            logger.error(f"认证默认数据初始化失败: {e}")
            raise
    
    def init_default_permissions(self):
        """初始化默认权限"""
        from auth.models import Permission
        
        try:
            with self.get_db_session() as db:
                # OpenAI相关权限
                openai_permissions = [
                    {'name': 'openai.view', 'display_name': '查看OpenAI配置', 'category': 'openai'},
                    {'name': 'openai.create', 'display_name': '创建OpenAI配置', 'category': 'openai'},
                    {'name': 'openai.edit', 'display_name': '编辑OpenAI配置', 'category': 'openai'},
                    {'name': 'openai.delete', 'display_name': '删除OpenAI配置', 'category': 'openai'},
                    {'name': 'openai.use', 'display_name': '使用OpenAI对话', 'category': 'openai'},
                    {'name': 'openai.manage_api_key', 'display_name': '管理API密钥', 'category': 'openai'},
                ]
                
                # 系统管理权限
                system_permissions = [
                    {'name': 'system.user.manage', 'display_name': '用户管理', 'category': 'system'},
                    {'name': 'system.role.manage', 'display_name': '角色管理', 'category': 'system'},
                    {'name': 'system.permission.manage', 'display_name': '权限管理', 'category': 'system'},
                ]
                
                all_permissions = openai_permissions + system_permissions
                
                for perm_data in all_permissions:
                    # 检查权限是否已存在
                    existing = db.query(Permission).filter(Permission.name == perm_data['name']).first()
                    if not existing:
                        permission = Permission(
                            name=perm_data['name'],
                            display_name=perm_data['display_name'],
                            category=perm_data['category']
                        )
                        db.add(permission)
                
                db.commit()
                logger.info("✅ 默认权限初始化完成")
                
        except Exception as e:
            logger.error(f"默认权限初始化失败: {e}")
            raise
    
    def init_role_permissions(self):
        """初始化角色权限关系"""
        from auth.models import Role, Permission, RolePermission
        
        try:
            with self.get_db_session() as db:
                # 获取角色
                admin_role = db.query(Role).filter(Role.name == 'admin').first()
                user_role = db.query(Role).filter(Role.name == 'user').first()
                
                if not admin_role or not user_role:
                    logger.warning("角色不存在，跳过权限分配")
                    return
                
                # 管理员拥有所有权限
                all_permissions = db.query(Permission).all()
                for permission in all_permissions:
                    # 检查关系是否已存在
                    existing = db.query(RolePermission).filter(
                        RolePermission.role_id == admin_role.id,
                        RolePermission.permission_id == permission.id
                    ).first()
                    
                    if not existing:
                        role_perm = RolePermission(
                            role_id=admin_role.id,
                            permission_id=permission.id
                        )
                        db.add(role_perm)
                
                # 普通用户权限
                user_permission_names = ['openai.view', 'openai.use']
                for perm_name in user_permission_names:
                    permission = db.query(Permission).filter(Permission.name == perm_name).first()
                    if permission:
                        # 检查关系是否已存在
                        existing = db.query(RolePermission).filter(
                            RolePermission.role_id == user_role.id,
                            RolePermission.permission_id == permission.id
                        ).first()
                        
                        if not existing:
                            role_perm = RolePermission(
                                role_id=user_role.id,
                                permission_id=permission.id
                            )
                            db.add(role_perm)
                
                db.commit()
                logger.info("✅ 角色权限关系初始化完成")
                
        except Exception as e:
            logger.error(f"角色权限关系初始化失败: {e}")
            raise
    
    def init_test_users(self, create_test_data=False):
        """初始化测试用户（仅开发环境）"""
        if not create_test_data:
            logger.info("跳过测试用户创建")
            return
            
        from auth.models import User, Role
        
        try:
            with self.get_db_session() as db:
                # 检查是否已有用户
                if db.query(User).count() > 0:
                    logger.info("用户已存在，跳过测试用户创建")
                    return
                
                # 获取角色
                admin_role = db.query(Role).filter(Role.name == 'admin').first()
                user_role = db.query(Role).filter(Role.name == 'user').first()
                
                # 创建管理员
                admin = User(
                    username='admin',
                    email='admin@example.com',
                    full_name='系统管理员',
                    is_active=True,
                    is_verified=True,
                    is_superuser=True
                )
                admin.set_password('admin123')
                if admin_role:
                    admin.roles.append(admin_role)
                
                # 创建普通用户
                user = User(
                    username='user',
                    email='user@example.com',
                    full_name='测试用户',
                    is_active=True,
                    is_verified=True
                )
                user.set_password('user123')
                if user_role:
                    user.roles.append(user_role)
                
                db.add(admin)
                db.add(user)
                db.commit()
                
                logger.info("✅ 测试用户创建完成")
                logger.info("管理员: admin/admin123")
                logger.info("普通用户: user/user123")
                
        except Exception as e:
            logger.error(f"测试用户创建失败: {e}")
            raise
    
    def init_business_default_data(self):
        """初始化业务表的默认数据"""
        # 这里可以添加各种业务表的默认数据初始化
        try:
            # OpenAI相关默认数据
            self._init_openai_default_data()
            
            # 在这里添加其他业务模块的默认数据初始化
            # self._init_mongodb_default_data()
            # self._init_audit_default_data()
            
            logger.info("✅ 业务默认数据初始化完成")
            
        except Exception as e:
            logger.error(f"业务默认数据初始化失败: {e}")
            raise
    
    def _init_openai_default_data(self):
        """初始化OpenAI模块的默认数据"""
        from database_models.business_models.openai_models import OpenAIConfig, ModelType
        
        try:
            with self.get_db_session() as db:
                # 检查是否已有配置
                if db.query(OpenAIConfig).first() is not None:
                    logger.info("OpenAI配置已存在，跳过默认数据创建")
                    return
                
                # 创建默认配置
                default_config = OpenAIConfig(
                    name="DeepSeek默认配置",
                    api_key="sk-example-key-replace-with-real-key",
                    base_url="https://api.deepseek.com/v1",
                    model_name=ModelType.DEEPSEEK,
                    max_tokens=1000,
                    temperature=70,
                    is_public=True,
                    description="系统默认的DeepSeek配置，请管理员更新API密钥"
                )
                
                db.add(default_config)
                db.commit()
                
                logger.info("✅ OpenAI默认配置创建完成")
                
        except Exception as e:
            logger.error(f"OpenAI默认数据初始化失败: {e}")
            raise
    
    def run_full_initialization(self, create_test_data=False, reset_if_exists=False):
        """运行完整的数据库初始化"""
        logger.info("开始数据库完整初始化...")
        
        try:
            # 1. 创建引擎和会话
            self.create_engine_and_session()
            
            # 2. 重置数据库（如果需要）
            if reset_if_exists:
                logger.warning("重置现有数据库...")
                from auth.database import Base
                Base.metadata.drop_all(bind=self.engine)
                logger.info("数据库已重置")
            
            # 3. 创建所有表
            self.create_all_tables()
            
            # 4. 初始化认证默认数据
            self.init_auth_default_data()
            
            # 5. 初始化默认权限
            self.init_default_permissions()
            
            # 6. 初始化角色权限关系
            self.init_role_permissions()
            
            # 7. 初始化业务默认数据
            self.init_business_default_data()
            
            # 8. 创建测试用户（如果需要）
            if create_test_data:
                self.init_test_users(create_test_data=True)
            
            logger.info("🎉 数据库初始化完成！")
            
        except Exception as e:
            logger.error(f"数据库初始化失败: {e}")
            raise
        finally:
            if self.SessionLocal:
                self.SessionLocal.remove()


def main():
    """主函数 - 命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='数据库初始化脚本')
    parser.add_argument('--test-data', action='store_true', help='创建测试用户数据')
    parser.add_argument('--reset', action='store_true', help='重置现有数据库')
    parser.add_argument('--verbose', action='store_true', help='详细输出')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # 初始化数据库
    initializer = DatabaseInitializer()
    
    try:
        initializer.run_full_initialization(
            create_test_data=args.test_data,
            reset_if_exists=args.reset
        )
        
        print("\n✅ 数据库初始化成功！")
        if args.test_data:
            print("🔐 测试用户已创建:")
            print("   管理员: admin / admin123")
            print("   普通用户: user / user123")
        
    except Exception as e:
        print(f"\n❌ 数据库初始化失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()