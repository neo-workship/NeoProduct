#!/usr/bin/env python3
"""
独立的数据库初始化脚本 - 复用现有ORM模型
使用方法：python scripts/init_database.py [--test-data] [--reset] [--verbose]
"""
import os
import sys
import logging
import argparse
from pathlib import Path
from contextlib import contextmanager

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def setup_logging(verbose=False):
    """设置日志"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )
    return logging.getLogger(__name__)

class DatabaseInitializer:
    """数据库初始化器 - 复用现有模型"""
    
    def __init__(self, logger):
        self.logger = logger
        self.engine = None
        self.SessionLocal = None
    
    def create_engine_and_session(self):
        """创建数据库引擎和会话"""
        try:
            from sqlalchemy import create_engine, event
            from sqlalchemy.orm import sessionmaker
            from auth.config import auth_config  # 使用项目的配置
            
            # 使用项目配置的数据库URL
            self.engine = create_engine(
                auth_config.database_url,
                pool_pre_ping=True,
                echo=False
            )
            
            # 为SQLite启用外键约束
            if auth_config.database_type == 'sqlite':
                @event.listens_for(self.engine, "connect")
                def set_sqlite_pragma(dbapi_connection, connection_record):
                    cursor = dbapi_connection.cursor()
                    cursor.execute("PRAGMA foreign_keys=ON")
                    cursor.close()
            
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
            self.logger.info(f"✅ 数据库引擎创建成功: {auth_config.database_type}")
            self.logger.info(f"📍 数据库位置: {auth_config.database_url}")
            
        except Exception as e:
            self.logger.error(f"❌ 数据库引擎创建失败: {e}")
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
            self.logger.error(f"数据库操作失败: {e}")
            raise
        finally:
            session.close()
    
    def import_all_models(self):
        """导入所有现有模型"""
        try:
            self.logger.info("开始导入现有模型...")
            
            # 导入认证模型（从auth包）
            from auth.models import User, Role, Permission, LoginLog
            # 导入关联表
            from auth.models import user_roles, role_permissions, user_permissions
            self.logger.info("✅ 认证模型导入成功")
            
            # 导入业务模型（从database_models包）
            from database_models.business_models.openai_models import OpenAIConfig, OpenAIRequest
            self.logger.info("✅ OpenAI业务模型导入成功")
            
            # 在这里添加其他业务模型的导入
            # 例如：未来添加MongoDB模型时
            # from database_models.business_models.mongodb_models import MongoDBConfig, MongoDBQuery
            # self.logger.info("✅ MongoDB业务模型导入成功")
            
            # 例如：未来添加审计模型时
            # from database_models.business_models.audit_models import AuditRecord
            # self.logger.info("✅ 审计业务模型导入成功")
            
            self.logger.info("✅ 所有模型导入完成")
            
            # 返回模型类以便后续使用
            return {
                'User': User,
                'Role': Role, 
                'Permission': Permission,
                'LoginLog': LoginLog,
                'OpenAIConfig': OpenAIConfig,
                'OpenAIRequest': OpenAIRequest,
            }
            
        except ImportError as e:
            self.logger.error(f"❌ 模型导入失败: {e}")
            raise
    
    def create_all_tables(self):
        """创建所有表"""
        try:
            # 导入模型
            models = self.import_all_models()
            
            # 获取Base类（从auth.database）
            from auth.database import Base
            
            # 创建所有表
            Base.metadata.create_all(bind=self.engine)
            self.logger.info("✅ 所有数据表创建成功")
            
            return models
            
        except Exception as e:
            self.logger.error(f"❌ 表创建失败: {e}")
            raise
    
    def init_default_roles_and_permissions(self, models):
        """初始化默认角色和权限"""
        try:
            with self.get_db_session() as db:
                Role = models['Role']
                Permission = models['Permission']
                
                # 检查是否已初始化
                if db.query(Role).first() is not None:
                    self.logger.info("角色和权限已存在，跳过初始化")
                    return
                
                # 使用auth_config中的默认角色配置
                from auth.config import auth_config
                
                # 创建默认角色
                for role_data in auth_config.default_roles:
                    role = Role(**role_data)
                    db.add(role)
                
                # 创建默认权限（使用auth_config中的配置，并添加OpenAI相关权限）
                permissions_data = list(auth_config.default_permissions)  # 复制基础权限
                
                # 添加OpenAI相关权限
                openai_permissions = [
                    {'name': 'openai.view', 'display_name': '查看OpenAI配置', 'category': 'openai'},
                    {'name': 'openai.create', 'display_name': '创建OpenAI配置', 'category': 'openai'},
                    {'name': 'openai.edit', 'display_name': '编辑OpenAI配置', 'category': 'openai'},
                    {'name': 'openai.delete', 'display_name': '删除OpenAI配置', 'category': 'openai'},
                    {'name': 'openai.use', 'display_name': '使用OpenAI对话', 'category': 'openai'},
                    {'name': 'openai.manage_api_key', 'display_name': '管理API密钥', 'category': 'openai'},
                ]
                permissions_data.extend(openai_permissions)
                
                # 添加更多业务权限
                additional_permissions = [
                    {'name': 'profile.view', 'display_name': '查看个人资料', 'category': 'profile'},
                    {'name': 'profile.edit', 'display_name': '编辑个人资料', 'category': 'profile'},
                    {'name': 'password.change', 'display_name': '修改密码', 'category': 'profile'},
                ]
                permissions_data.extend(additional_permissions)
                
                for perm_data in permissions_data:
                    permission = Permission(**perm_data)
                    db.add(permission)
                
                db.commit()
                self.logger.info("✅ 默认角色和权限初始化完成")
                
        except Exception as e:
            self.logger.error(f"❌ 默认角色和权限初始化失败: {e}")
            raise
    
    def init_role_permissions(self, models):
        """初始化角色权限关系"""
        try:
            with self.get_db_session() as db:
                Role = models['Role']
                Permission = models['Permission']
                
                # 获取角色
                admin_role = db.query(Role).filter(Role.name == 'admin').first()
                user_role = db.query(Role).filter(Role.name == 'user').first()
                editor_role = db.query(Role).filter(Role.name == 'editor').first()
                viewer_role = db.query(Role).filter(Role.name == 'viewer').first()
                
                if not all([admin_role, user_role, editor_role, viewer_role]):
                    self.logger.warning("部分角色不存在，跳过权限分配")
                    return
                
                # 清除现有权限关联
                for role in [admin_role, user_role, editor_role, viewer_role]:
                    role.permissions.clear()
                
                # 获取所有权限
                all_permissions = db.query(Permission).all()
                openai_view = db.query(Permission).filter(Permission.name == 'openai.view').first()
                openai_use = db.query(Permission).filter(Permission.name == 'openai.use').first()
                profile_perms = db.query(Permission).filter(Permission.category == 'profile').all()
                
                # 分配权限
                # 管理员：所有权限
                admin_role.permissions.extend(all_permissions)
                
                # 编辑者：OpenAI相关权限 + 个人资料
                editor_permissions = db.query(Permission).filter(
                    Permission.category.in_(['openai', 'profile'])
                ).all()
                editor_role.permissions.extend(editor_permissions)
                
                # 查看者：查看权限 + 个人资料
                viewer_permissions = [openai_view] + profile_perms
                viewer_role.permissions.extend([p for p in viewer_permissions if p])
                
                # 普通用户：基础权限
                user_permissions = [openai_view, openai_use] + profile_perms
                user_role.permissions.extend([p for p in user_permissions if p])
                
                db.commit()
                self.logger.info("✅ 角色权限关系初始化完成")
                
        except Exception as e:
            self.logger.error(f"❌ 角色权限关系初始化失败: {e}")
            raise
    
    def init_test_users(self, models, create_test_data=False):
        """初始化测试用户"""
        if not create_test_data:
            self.logger.info("跳过测试用户创建")
            return
        
        try:
            with self.get_db_session() as db:
                User = models['User']
                Role = models['Role']
                
                # 检查是否已有用户
                if db.query(User).count() > 0:
                    self.logger.info("用户已存在，跳过测试用户创建")
                    return
                
                # 获取角色
                admin_role = db.query(Role).filter(Role.name == 'admin').first()
                user_role = db.query(Role).filter(Role.name == 'user').first()
                editor_role = db.query(Role).filter(Role.name == 'editor').first()
                viewer_role = db.query(Role).filter(Role.name == 'viewer').first()
                
                # 创建测试用户
                users_data = [
                    {
                        'user_data': {
                            'username': 'admin',
                            'email': 'admin@example.com',
                            'full_name': '系统管理员',
                            'is_active': True,
                            'is_verified': True,
                            'is_superuser': True
                        },
                        'password': 'admin123',
                        'roles': [admin_role] if admin_role else []
                    },
                    {
                        'user_data': {
                            'username': 'user',
                            'email': 'user@example.com',
                            'full_name': '普通用户',
                            'is_active': True,
                            'is_verified': True
                        },
                        'password': 'user123',
                        'roles': [user_role] if user_role else []
                    },
                    {
                        'user_data': {
                            'username': 'editor',
                            'email': 'editor@example.com',
                            'full_name': '内容编辑',
                            'is_active': True,
                            'is_verified': True
                        },
                        'password': 'editor123',
                        'roles': [editor_role] if editor_role else []
                    },
                    {
                        'user_data': {
                            'username': 'viewer',
                            'email': 'viewer@example.com',
                            'full_name': '查看用户',
                            'is_active': True,
                            'is_verified': True
                        },
                        'password': 'viewer123',
                        'roles': [viewer_role] if viewer_role else []
                    }
                ]
                
                for user_info in users_data:
                    user = User(**user_info['user_data'])
                    user.set_password(user_info['password'])
                    user.roles.extend(user_info['roles'])
                    db.add(user)
                
                db.commit()
                
                self.logger.info("✅ 测试用户创建完成")
                self.logger.info("🔐 测试账户信息:")
                self.logger.info("   管理员: admin / admin123")
                self.logger.info("   普通用户: user / user123") 
                self.logger.info("   编辑者: editor / editor123")
                self.logger.info("   查看者: viewer / viewer123")
                
        except Exception as e:
            self.logger.error(f"❌ 测试用户创建失败: {e}")
            raise
    
    def init_business_default_data(self, models):
        """初始化业务默认数据"""
        try:
            self._init_openai_default_data(models)
            # 在这里添加其他业务模块的默认数据初始化
            # self._init_mongodb_default_data(models)
            # self._init_audit_default_data(models)
            
            self.logger.info("✅ 业务默认数据初始化完成")
            
        except Exception as e:
            self.logger.error(f"❌ 业务默认数据初始化失败: {e}")
            raise
    
    def _init_openai_default_data(self, models):
        """初始化OpenAI模块的默认数据"""
        try:
            with self.get_db_session() as db:
                OpenAIConfig = models['OpenAIConfig']
                
                # 检查是否已有配置
                if db.query(OpenAIConfig).first() is not None:
                    self.logger.info("OpenAI配置已存在，跳过默认数据创建")
                    return
                
                # 导入枚举类型
                from database_models.business_models.openai_models import ModelType
                
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
                
                self.logger.info("✅ OpenAI默认配置创建完成")
                
        except Exception as e:
            self.logger.error(f"❌ OpenAI默认数据初始化失败: {e}")
            raise
    
    def run_full_initialization(self, create_test_data=False, reset_if_exists=False):
        """运行完整的数据库初始化"""
        self.logger.info("🚀 开始数据库完整初始化...")
        
        try:
            # 1. 创建引擎和会话
            self.create_engine_and_session()
            
            # 2. 重置数据库（如果需要）
            if reset_if_exists:
                self.logger.warning("🔄 重置现有数据库...")
                from auth.database import Base
                Base.metadata.drop_all(bind=self.engine)
                self.logger.info("✅ 数据库已重置")
            
            # 3. 创建所有表并导入模型
            models = self.create_all_tables()
            
            # 4. 初始化默认角色和权限
            self.init_default_roles_and_permissions(models)
            
            # 5. 初始化角色权限关系
            self.init_role_permissions(models)
            
            # 6. 初始化业务默认数据
            self.init_business_default_data(models)
            
            # 7. 创建测试用户（如果需要）
            if create_test_data:
                self.init_test_users(models, create_test_data=True)
            
            self.logger.info("🎉 数据库初始化完成！")
            
        except Exception as e:
            self.logger.error(f"❌ 数据库初始化失败: {e}")
            raise

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='数据库初始化脚本')
    parser.add_argument('--test-data', action='store_true', help='创建测试用户数据')
    parser.add_argument('--reset', action='store_true', help='重置现有数据库')
    parser.add_argument('--verbose', action='store_true', help='详细输出')
    
    args = parser.parse_args()
    
    # 设置日志
    logger = setup_logging(args.verbose)
    
    # 初始化数据库
    initializer = DatabaseInitializer(logger)
    
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
            print("   编辑者: editor / editor123")
            print("   查看者: viewer / viewer123")
        
    except Exception as e:
        print(f"\n❌ 数据库初始化失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()