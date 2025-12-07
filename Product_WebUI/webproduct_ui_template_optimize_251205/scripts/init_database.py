#!/usr/bin/env python3
"""
独立的数据库初始化脚本 - SQLModel 版本
使用方法:python scripts/init_database.py [--test-data] [--reset] [--verbose] [--scenario SCENARIO]

核心改进:
- 使用 SQLModel 的 Session 和 select()
- 移除 SQLAlchemy 的 joinedload
- 简化查询逻辑
- 支持多场景初始化
"""
import os
import sys
import logging
import argparse
from pathlib import Path
from contextlib import contextmanager
from typing import Dict, List

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


# ===========================
# 场景配置定义
# ===========================

class ScenarioConfig:
    """场景配置基类"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.roles: List[Dict] = []
        self.permissions: List[Dict] = []
        self.role_permissions: Dict[str, List[str]] = {}
    
    def get_roles(self) -> List[Dict]:
        """获取场景角色配置"""
        return self.roles
    
    def get_permissions(self) -> List[Dict]:
        """获取场景权限配置"""
        return self.permissions
    
    def get_role_permissions(self) -> Dict[str, List[str]]:
        """获取角色权限映射"""
        return self.role_permissions


class DefaultScenario(ScenarioConfig):
    """默认场景 - 通用Web应用"""
    
    def __init__(self):
        super().__init__('default', '默认场景 - 通用Web应用,适合一般的业务系统')
        
        # 定义角色
        self.roles = [
            {
                'name': 'admin',
                'display_name': '系统管理员',
                'description': '系统管理员,拥有所有权限',
                'is_system': True
            },
            {
                'name': 'user',
                'display_name': '普通用户',
                'description': '普通注册用户,基本权限',
                'is_system': True
            },
            {
                'name': 'editor',
                'display_name': '编辑者',
                'description': '可以创建和编辑内容',
                'is_system': False
            },
            {
                'name': 'viewer',
                'display_name': '查看者',
                'description': '只能查看内容',
                'is_system': False
            },
        ]
        
        # 定义权限
        self.permissions = [
            # 系统权限
            {'name': 'system.manage', 'display_name': '系统管理', 'category': 'system', 'description': '管理系统设置'},
            {'name': 'user.manage', 'display_name': '用户管理', 'category': 'system', 'description': '管理用户账户'},
            {'name': 'role.manage', 'display_name': '角色管理', 'category': 'system', 'description': '管理角色和权限'},
            
            # 内容权限
            {'name': 'content.create', 'display_name': '创建内容', 'category': 'content', 'description': '创建新内容'},
            {'name': 'content.edit', 'display_name': '编辑内容', 'category': 'content', 'description': '编辑现有内容'},
            {'name': 'content.delete', 'display_name': '删除内容', 'category': 'content', 'description': '删除内容'},
            {'name': 'content.view', 'display_name': '查看内容', 'category': 'content', 'description': '查看内容'},
            
            # 个人资料权限
            {'name': 'profile.view', 'display_name': '查看个人资料', 'category': 'profile', 'description': '查看个人资料信息'},
            {'name': 'profile.edit', 'display_name': '编辑个人资料', 'category': 'profile', 'description': '编辑个人资料信息'},
            {'name': 'password.change', 'display_name': '修改密码', 'category': 'profile', 'description': '修改登录密码'},
        ]
        
        # 角色权限映射
        self.role_permissions = {
            'admin': ['*'],  # 所有权限
            'user': ['content.view', 'profile.view', 'profile.edit', 'password.change'],
            'editor': ['content.create', 'content.edit', 'content.view', 'profile.view', 'profile.edit', 'password.change'],
            'viewer': ['content.view', 'profile.view', 'password.change'],
        }


class CMSScenario(ScenarioConfig):
    """CMS场景 - 内容管理系统"""
    
    def __init__(self):
        super().__init__('cms', 'CMS场景 - 内容管理系统,适合博客、新闻、文档等内容发布平台')
        
        # 定义角色
        self.roles = [
            {
                'name': 'admin',
                'display_name': '超级管理员',
                'description': '拥有所有权限的超级管理员',
                'is_system': True
            },
            {
                'name': 'editor_chief',
                'display_name': '主编',
                'description': '负责内容审核和发布',
                'is_system': False
            },
            {
                'name': 'author',
                'display_name': '作者',
                'description': '撰写和编辑文章',
                'is_system': False
            },
            {
                'name': 'contributor',
                'display_name': '投稿者',
                'description': '提交文章草稿,需要审核',
                'is_system': False
            },
            {
                'name': 'reader',
                'display_name': '读者',
                'description': '浏览已发布的内容',
                'is_system': False
            },
        ]
        
        # 定义权限
        self.permissions = [
            # 系统管理
            {'name': 'system.manage', 'display_name': '系统管理', 'category': 'system', 'description': '管理系统设置'},
            {'name': 'user.manage', 'display_name': '用户管理', 'category': 'system', 'description': '管理用户账户'},
            {'name': 'role.manage', 'display_name': '角色管理', 'category': 'system', 'description': '管理角色权限'},
            
            # 文章管理
            {'name': 'article.create', 'display_name': '创建文章', 'category': 'article', 'description': '创建新文章'},
            {'name': 'article.edit', 'display_name': '编辑文章', 'category': 'article', 'description': '编辑文章内容'},
            {'name': 'article.edit_all', 'display_name': '编辑所有文章', 'category': 'article', 'description': '编辑任何人的文章'},
            {'name': 'article.delete', 'display_name': '删除文章', 'category': 'article', 'description': '删除文章'},
            {'name': 'article.delete_all', 'display_name': '删除所有文章', 'category': 'article', 'description': '删除任何人的文章'},
            {'name': 'article.publish', 'display_name': '发布文章', 'category': 'article', 'description': '发布文章到前台'},
            {'name': 'article.view_draft', 'display_name': '查看草稿', 'category': 'article', 'description': '查看未发布的草稿'},
            {'name': 'article.view', 'display_name': '查看文章', 'category': 'article', 'description': '查看已发布文章'},
            
            # 评论管理
            {'name': 'comment.create', 'display_name': '发表评论', 'category': 'comment', 'description': '对文章发表评论'},
            {'name': 'comment.moderate', 'display_name': '审核评论', 'category': 'comment', 'description': '审核和管理评论'},
            {'name': 'comment.delete', 'display_name': '删除评论', 'category': 'comment', 'description': '删除不当评论'},
            
            # 分类标签
            {'name': 'category.manage', 'display_name': '管理分类', 'category': 'taxonomy', 'description': '管理文章分类'},
            {'name': 'tag.manage', 'display_name': '管理标签', 'category': 'taxonomy', 'description': '管理文章标签'},
            
            # 媒体库
            {'name': 'media.upload', 'display_name': '上传媒体', 'category': 'media', 'description': '上传图片、视频等'},
            {'name': 'media.manage', 'display_name': '管理媒体', 'category': 'media', 'description': '管理媒体库'},
            
            # 个人资料
            {'name': 'profile.view', 'display_name': '查看资料', 'category': 'profile', 'description': '查看个人资料'},
            {'name': 'profile.edit', 'display_name': '编辑资料', 'category': 'profile', 'description': '编辑个人资料'},
        ]
        
        # 角色权限映射
        self.role_permissions = {
            'admin': ['*'],
            'editor_chief': [
                'article.create', 'article.edit', 'article.edit_all', 
                'article.delete', 'article.delete_all', 'article.publish',
                'article.view_draft', 'article.view',
                'comment.create', 'comment.moderate', 'comment.delete',
                'category.manage', 'tag.manage',
                'media.upload', 'media.manage',
                'profile.view', 'profile.edit'
            ],
            'author': [
                'article.create', 'article.edit', 'article.view_draft', 'article.view',
                'comment.create', 'comment.moderate',
                'media.upload',
                'profile.view', 'profile.edit'
            ],
            'contributor': [
                'article.create', 'article.edit', 'article.view',
                'comment.create',
                'media.upload',
                'profile.view', 'profile.edit'
            ],
            'reader': [
                'article.view', 'comment.create',
                'profile.view', 'profile.edit'
            ],
        }


class ERPScenario(ScenarioConfig):
    """ERP场景 - 企业资源计划系统"""
    
    def __init__(self):
        super().__init__('erp', 'ERP场景 - 企业资源计划系统,适合企业内部管理、财务、采购等业务')
        
        # 定义角色
        self.roles = [
            {
                'name': 'admin',
                'display_name': '系统管理员',
                'description': '系统管理员,拥有所有权限',
                'is_system': True
            },
            {
                'name': 'ceo',
                'display_name': 'CEO',
                'description': '公司最高管理者,查看所有数据',
                'is_system': False
            },
            {
                'name': 'finance_manager',
                'display_name': '财务经理',
                'description': '管理公司财务和账目',
                'is_system': False
            },
            {
                'name': 'purchase_manager',
                'display_name': '采购经理',
                'description': '管理采购订单和供应商',
                'is_system': False
            },
            {
                'name': 'sales_manager',
                'display_name': '销售经理',
                'description': '管理销售订单和客户',
                'is_system': False
            },
            {
                'name': 'warehouse_manager',
                'display_name': '仓库管理员',
                'description': '管理库存和出入库',
                'is_system': False
            },
            {
                'name': 'employee',
                'display_name': '普通员工',
                'description': '普通员工,基础权限',
                'is_system': False
            },
        ]
        
        # 定义权限
        self.permissions = [
            # 系统管理
            {'name': 'system.manage', 'display_name': '系统管理', 'category': 'system', 'description': '系统设置和配置'},
            {'name': 'user.manage', 'display_name': '用户管理', 'category': 'system', 'description': '管理用户账户'},
            {'name': 'role.manage', 'display_name': '角色管理', 'category': 'system', 'description': '管理角色权限'},
            
            # 财务管理
            {'name': 'finance.view', 'display_name': '查看财务', 'category': 'finance', 'description': '查看财务报表'},
            {'name': 'finance.manage', 'display_name': '管理财务', 'category': 'finance', 'description': '管理财务数据'},
            {'name': 'invoice.create', 'display_name': '创建发票', 'category': 'finance', 'description': '创建销售发票'},
            {'name': 'invoice.approve', 'display_name': '审批发票', 'category': 'finance', 'description': '审批发票'},
            {'name': 'payment.manage', 'display_name': '管理付款', 'category': 'finance', 'description': '处理付款事务'},
            
            # 采购管理
            {'name': 'purchase.view', 'display_name': '查看采购', 'category': 'purchase', 'description': '查看采购订单'},
            {'name': 'purchase.create', 'display_name': '创建采购', 'category': 'purchase', 'description': '创建采购订单'},
            {'name': 'purchase.approve', 'display_name': '审批采购', 'category': 'purchase', 'description': '审批采购订单'},
            {'name': 'supplier.manage', 'display_name': '管理供应商', 'category': 'purchase', 'description': '管理供应商信息'},
            
            # 销售管理
            {'name': 'sales.view', 'display_name': '查看销售', 'category': 'sales', 'description': '查看销售订单'},
            {'name': 'sales.create', 'display_name': '创建销售', 'category': 'sales', 'description': '创建销售订单'},
            {'name': 'sales.approve', 'display_name': '审批销售', 'category': 'sales', 'description': '审批销售订单'},
            {'name': 'customer.manage', 'display_name': '管理客户', 'category': 'sales', 'description': '管理客户信息'},
            
            # 库存管理
            {'name': 'inventory.view', 'display_name': '查看库存', 'category': 'inventory', 'description': '查看库存状态'},
            {'name': 'inventory.manage', 'display_name': '管理库存', 'category': 'inventory', 'description': '管理库存数据'},
            {'name': 'warehouse.in', 'display_name': '入库操作', 'category': 'inventory', 'description': '商品入库'},
            {'name': 'warehouse.out', 'display_name': '出库操作', 'category': 'inventory', 'description': '商品出库'},
            
            # 报表权限
            {'name': 'report.view', 'display_name': '查看报表', 'category': 'report', 'description': '查看各类报表'},
            {'name': 'report.export', 'display_name': '导出报表', 'category': 'report', 'description': '导出报表数据'},
            
            # 个人资料
            {'name': 'profile.view', 'display_name': '查看资料', 'category': 'profile', 'description': '查看个人资料'},
            {'name': 'profile.edit', 'display_name': '编辑资料', 'category': 'profile', 'description': '编辑个人资料'},
        ]
        
        # 角色权限映射
        self.role_permissions = {
            'admin': ['*'],
            'ceo': [
                'finance.view', 'purchase.view', 'purchase.approve',
                'sales.view', 'sales.approve', 'inventory.view',
                'report.view', 'report.export',
                'profile.view', 'profile.edit'
            ],
            'finance_manager': [
                'finance.view', 'finance.manage',
                'invoice.create', 'invoice.approve', 'payment.manage',
                'report.view', 'report.export',
                'profile.view', 'profile.edit'
            ],
            'purchase_manager': [
                'purchase.view', 'purchase.create', 'purchase.approve',
                'supplier.manage', 'inventory.view',
                'report.view',
                'profile.view', 'profile.edit'
            ],
            'sales_manager': [
                'sales.view', 'sales.create', 'sales.approve',
                'customer.manage', 'invoice.create',
                'report.view',
                'profile.view', 'profile.edit'
            ],
            'warehouse_manager': [
                'inventory.view', 'inventory.manage',
                'warehouse.in', 'warehouse.out',
                'report.view',
                'profile.view', 'profile.edit'
            ],
            'employee': [
                'profile.view', 'profile.edit'
            ],
        }


# 场景注册表
SCENARIOS = {
    'default': DefaultScenario(),
    'cms': CMSScenario(),
    'erp': ERPScenario(),
}


# ===========================
# 数据库初始化类
# ===========================

class DatabaseInitializer:
    """
    数据库初始化器 - SQLModel 版本
    
    核心改进:
    - 使用 SQLModel 的 create_engine
    - 使用 Session 而非 sessionmaker
    - 使用 select() 查询而非 query()
    - 支持多场景初始化
    """
    
    def __init__(self, logger, scenario='default'):
        self.logger = logger
        self.engine = None
        self.scenario = SCENARIOS.get(scenario, SCENARIOS['default'])
        self.logger.info(f"🎯 使用场景: {self.scenario.name} - {self.scenario.description}")
    
    def create_engine_and_session(self):
        """创建数据库引擎 - SQLModel 版本"""
        try:
            from sqlmodel import create_engine
            from sqlalchemy import event
            from auth.config import auth_config
            
            # 使用 SQLModel 的 create_engine
            self.engine = create_engine(
                auth_config.database_url,
                pool_pre_ping=True,
                echo=False
            )
            
            # 为 SQLite 启用外键约束
            if auth_config.database_type == 'sqlite':
                @event.listens_for(self.engine, "connect")
                def set_sqlite_pragma(dbapi_connection, connection_record):
                    cursor = dbapi_connection.cursor()
                    cursor.execute("PRAGMA foreign_keys=ON")
                    cursor.close()
            
            self.logger.info(f"✅ 数据库引擎创建成功: {auth_config.database_type}")
            self.logger.info(f"📍 数据库位置: {auth_config.database_url}")
            
        except Exception as e:
            self.logger.error(f"❌ 数据库引擎创建失败: {e}")
            raise
    
    @contextmanager
    def get_db_session(self):
        """
        获取数据库会话 - SQLModel 版本
        使用 Session 而不是 sessionmaker
        """
        from sqlmodel import Session
        
        session = Session(self.engine)
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            self.logger.error(f"❌ 数据库操作失败: {e}")
            raise
        finally:
            session.close()
    
    def import_all_models(self):
        """
        导入所有模型以注册到 SQLModel.metadata
        """
        try:
            from auth.models import (
                User, Role, Permission, LoginLog,
                UserRoleLink, RolePermissionLink, UserPermissionLink
            )
            
            models = {
                'User': User,
                'Role': Role,
                'Permission': Permission,
                'LoginLog': LoginLog,
                'UserRoleLink': UserRoleLink,
                'RolePermissionLink': RolePermissionLink,
                'UserPermissionLink': UserPermissionLink,
            }
            
            self.logger.info(f"✅ 成功导入 {len(models)} 个模型")
            return models
            
        except Exception as e:
            self.logger.error(f"❌ 模型导入失败: {e}")
            raise
    
    def create_all_tables(self):
        """
        创建所有数据库表 - SQLModel 版本
        """
        try:
            from sqlmodel import SQLModel
            
            self.logger.info("创建数据库表...")
            
            # 导入模型
            models = self.import_all_models()
            
            # 创建所有表
            SQLModel.metadata.create_all(bind=self.engine)
            
            self.logger.info("✅ 数据库表创建完成")
            return models
            
        except Exception as e:
            self.logger.error(f"❌ 表创建失败: {e}")
            raise
    
    def init_default_roles_and_permissions(self, models):
        """
        初始化默认角色和权限 - 支持多场景
        """
        try:
            with self.get_db_session() as session:
                from sqlmodel import select
                Role = models['Role']
                Permission = models['Permission']
                
                # 检查是否已初始化
                existing_role = session.exec(select(Role)).first()
                if existing_role is not None:
                    self.logger.info("角色和权限已存在,跳过初始化")
                    return
                
                # 创建角色
                self.logger.info(f"创建 {self.scenario.name} 场景的角色...")
                for role_data in self.scenario.get_roles():
                    role = Role(**role_data)
                    session.add(role)
                
                # 创建权限
                self.logger.info(f"创建 {self.scenario.name} 场景的权限...")
                for perm_data in self.scenario.get_permissions():
                    permission = Permission(**perm_data)
                    session.add(permission)
                
                session.commit()
                self.logger.info(f"✅ {self.scenario.name} 场景的角色和权限初始化完成")
                
        except Exception as e:
            self.logger.error(f"❌ 角色和权限初始化失败: {e}")
            raise
    
    def init_role_permissions(self, models):
        """
        初始化角色权限关系 - 支持多场景
        """
        try:
            with self.get_db_session() as session:
                from sqlmodel import select
                Role = models['Role']
                Permission = models['Permission']
                
                # 获取所有角色和权限
                all_roles = session.exec(select(Role)).all()
                all_permissions = session.exec(select(Permission)).all()
                
                # 创建权限字典方便查找
                permission_dict = {perm.name: perm for perm in all_permissions}
                
                self.logger.info(f"分配 {self.scenario.name} 场景的角色权限...")
                
                # 为每个角色分配权限
                for role in all_roles:
                    # 清除现有权限
                    role.permissions.clear()
                    
                    # 获取该角色应有的权限
                    role_perms = self.scenario.get_role_permissions().get(role.name, [])
                    
                    if '*' in role_perms:
                        # 分配所有权限
                        role.permissions.extend(all_permissions)
                        self.logger.info(f"  - {role.display_name}: 所有权限 ({len(all_permissions)}个)")
                    else:
                        # 分配指定权限
                        assigned = 0
                        for perm_name in role_perms:
                            if perm_name in permission_dict:
                                role.permissions.append(permission_dict[perm_name])
                                assigned += 1
                        self.logger.info(f"  - {role.display_name}: {assigned}个权限")
                
                session.commit()
                self.logger.info(f"✅ {self.scenario.name} 场景的角色权限分配完成")
                
        except Exception as e:
            self.logger.error(f"❌ 角色权限分配失败: {e}")
            raise
    
    def init_test_users(self, models, create_test_data=False):
        """
        初始化测试用户 - SQLModel 版本
        """
        if not create_test_data:
            return
        
        try:
            with self.get_db_session() as session:
                from sqlmodel import select
                User = models['User']
                Role = models['Role']
                
                # 检查是否已有用户
                existing_user = session.exec(select(User)).first()
                if existing_user is not None:
                    self.logger.info("测试用户已存在,跳过创建")
                    return
                
                self.logger.info("创建测试用户...")
                
                # 获取角色
                roles = session.exec(select(Role)).all()
                role_dict = {role.name: role for role in roles}
                
                # 创建管理员用户
                admin_user = User(
                    username='admin',
                    email='admin@example.com',
                    full_name='系统管理员',
                    is_superuser=True,
                    is_active=True
                )
                admin_user.set_password('admin123')
                if 'admin' in role_dict:
                    admin_user.roles.append(role_dict['admin'])
                session.add(admin_user)
                
                # 根据场景创建不同的测试用户
                if self.scenario.name == 'default':
                    # 普通用户
                    user = User(username='user', email='user@example.com', full_name='普通用户')
                    user.set_password('user123')
                    if 'user' in role_dict:
                        user.roles.append(role_dict['user'])
                    session.add(user)
                    
                    # 编辑者
                    editor = User(username='editor', email='editor@example.com', full_name='编辑者')
                    editor.set_password('editor123')
                    if 'editor' in role_dict:
                        editor.roles.append(role_dict['editor'])
                    session.add(editor)
                    
                    # 查看者
                    viewer = User(username='viewer', email='viewer@example.com', full_name='查看者')
                    viewer.set_password('viewer123')
                    if 'viewer' in role_dict:
                        viewer.roles.append(role_dict['viewer'])
                    session.add(viewer)
                
                elif self.scenario.name == 'cms':
                    # 主编
                    chief = User(username='chief', email='chief@example.com', full_name='主编')
                    chief.set_password('chief123')
                    if 'editor_chief' in role_dict:
                        chief.roles.append(role_dict['editor_chief'])
                    session.add(chief)
                    
                    # 作者
                    author = User(username='author', email='author@example.com', full_name='作者')
                    author.set_password('author123')
                    if 'author' in role_dict:
                        author.roles.append(role_dict['author'])
                    session.add(author)
                    
                    # 投稿者
                    contributor = User(username='contributor', email='contributor@example.com', full_name='投稿者')
                    contributor.set_password('contributor123')
                    if 'contributor' in role_dict:
                        contributor.roles.append(role_dict['contributor'])
                    session.add(contributor)
                
                elif self.scenario.name == 'erp':
                    # CEO
                    ceo = User(username='ceo', email='ceo@example.com', full_name='CEO')
                    ceo.set_password('ceo123')
                    if 'ceo' in role_dict:
                        ceo.roles.append(role_dict['ceo'])
                    session.add(ceo)
                    
                    # 财务经理
                    finance = User(username='finance', email='finance@example.com', full_name='财务经理')
                    finance.set_password('finance123')
                    if 'finance_manager' in role_dict:
                        finance.roles.append(role_dict['finance_manager'])
                    session.add(finance)
                    
                    # 采购经理
                    purchase = User(username='purchase', email='purchase@example.com', full_name='采购经理')
                    purchase.set_password('purchase123')
                    if 'purchase_manager' in role_dict:
                        purchase.roles.append(role_dict['purchase_manager'])
                    session.add(purchase)
                
                session.commit()
                self.logger.info(f"✅ {self.scenario.name} 场景的测试用户创建完成")
                
        except Exception as e:
            self.logger.error(f"❌ 测试用户创建失败: {e}")
            raise
    
    def run_full_initialization(self, create_test_data=False, reset_if_exists=False):
        """
        执行完整的数据库初始化流程
        """
        try:
            # 1. 创建引擎
            self.create_engine_and_session()
            
            # 2. 重置数据库(如果需要)
            if reset_if_exists:
                self.logger.warning("⚠️  重置现有数据库...")
                from sqlmodel import SQLModel
                SQLModel.metadata.drop_all(bind=self.engine)
                self.logger.info("✅ 数据库已重置")
            
            # 3. 创建所有表并导入模型
            models = self.create_all_tables()
            
            # 4. 初始化默认角色和权限
            self.init_default_roles_and_permissions(models)
            
            # 5. 初始化角色权限关系
            self.init_role_permissions(models)
            
            # 6. 创建测试用户(如果需要)
            if create_test_data:
                self.init_test_users(models, create_test_data=True)
            
            self.logger.info("🎉 数据库初始化完成!")
            
        except Exception as e:
            self.logger.error(f"❌ 数据库初始化失败: {e}")
            raise


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='数据库初始化脚本 - SQLModel 版本 (支持多场景)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
场景说明:
  default - 默认场景,适合通用Web应用
  cms     - 内容管理系统场景,适合博客、新闻等
  erp     - 企业资源计划场景,适合企业管理系统

使用示例:
  python scripts/init_database.py --scenario default --test-data
  python scripts/init_database.py --scenario cms --reset --test-data
  python scripts/init_database.py --scenario erp --verbose
        """
    )
    
    parser.add_argument('--test-data', action='store_true', help='创建测试用户数据')
    parser.add_argument('--reset', action='store_true', help='重置现有数据库')
    parser.add_argument('--verbose', action='store_true', help='详细输出')
    parser.add_argument(
        '--scenario', 
        type=str, 
        default='default', 
        choices=['default', 'cms', 'erp'],
        help='选择初始化场景 (默认: default)'
    )
    
    args = parser.parse_args()
    
    # 设置日志
    logger = setup_logging(args.verbose)
    
    logger.info("=" * 60)
    logger.info("数据库初始化脚本 - SQLModel 版本")
    logger.info("=" * 60)
    
    # 初始化数据库
    initializer = DatabaseInitializer(logger, scenario=args.scenario)
    
    try:
        initializer.run_full_initialization(
            create_test_data=args.test_data,
            reset_if_exists=args.reset
        )
        
        print("\n" + "=" * 60)
        print("✅ 数据库初始化成功!")
        print("=" * 60)
        print(f"\n🎯 场景: {initializer.scenario.name}")
        print(f"📝 描述: {initializer.scenario.description}")
        
        if args.test_data:
            print("\n🔐 测试账户已创建:")
            print("   管理员: admin / admin123")
            
            if args.scenario == 'default':
                print("   普通用户: user / user123")
                print("   编辑者: editor / editor123")
                print("   查看者: viewer / viewer123")
            elif args.scenario == 'cms':
                print("   主编: chief / chief123")
                print("   作者: author / author123")
                print("   投稿者: contributor / contributor123")
            elif args.scenario == 'erp':
                print("   CEO: ceo / ceo123")
                print("   财务经理: finance / finance123")
                print("   采购经理: purchase / purchase123")
            
            print("\n💡 提示: 使用这些账户登录测试系统")
        
    except Exception as e:
        print("\n" + "=" * 60)
        print(f"❌ 数据库初始化失败: {e}")
        print("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    main()