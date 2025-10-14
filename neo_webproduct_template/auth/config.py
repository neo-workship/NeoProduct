"""
认证配置模块
"""
import os
from pathlib import Path
from typing import Optional

class AuthConfig:
    """认证配置类"""
    
    def __init__(self):
        """
        这是类的构造函数，在创建 AuthConfig 类的实例时会自动调用。它初始化了所有认证相关的配置属性，并为其设置了默认值。
        """
        # 数据库配置
        self.database_type = 'sqlite'  # 默认使用SQLite，可切换为mysql、postgresql等
        self.database_url = self._get_database_url()
        
        # 会话配置
        self.session_secret_key = os.environ.get('SESSION_SECRET_KEY', 'your-secret-key-here')
        self.session_timeout = 3600 * 24  # 24小时
        self.remember_me_duration = 3600 * 24 * 30  # 30天
        
        # 密码配置
        self.password_min_length = 6
        self.password_require_uppercase = False
        self.password_require_lowercase = False
        self.password_require_numbers = False
        self.password_require_special = False
        
        # 注册配置
        self.allow_registration = True
        self.require_email_verification = False
        self.default_user_role = 'user'  # 默认角色
        
        # 登录配置
        self.max_login_attempts = 5
        self.lockout_duration = 1800  # 30分钟
        self.allow_remember_me = True
        
        # 路由配置
        self.login_route = '/login'
        self.logout_route = '/logout'
        self.register_route = '/register'
        self.unauthorized_redirect = '/login'
        
        # 默认角色配置（预留给权限管理包使用）
        self.default_roles = [
            {'name': 'admin', 'display_name': '管理员', 'description': '系统管理员，拥有所有权限'},
            {'name': 'editor', 'display_name': '编辑', 'description': '可以编辑内容'},
            {'name': 'viewer', 'display_name': '查看', 'description': '只能查看内容'},
            {'name': 'user', 'display_name': '普通用户', 'description': '普通注册用户'}
        ]
        
        # 默认权限配置（预留给权限管理包使用）
        self.default_permissions = [
            # 系统权限
            {'name': 'system.manage', 'display_name': '系统管理', 'category': '系统'},
            {'name': 'user.manage', 'display_name': '用户管理', 'category': '系统'},
            {'name': 'role.manage', 'display_name': '角色管理', 'category': '系统'},
            
            # 内容权限
            {'name': 'content.create', 'display_name': '创建内容', 'category': '内容'},
            {'name': 'content.edit', 'display_name': '编辑内容', 'category': '内容'},
            {'name': 'content.delete', 'display_name': '删除内容', 'category': '内容'},
            {'name': 'content.view', 'display_name': '查看内容', 'category': '内容'},
        ]
        
        # 页面权限映射（预留给权限管理包使用）
        self.page_permissions = {
            # menu_pages
            'dashboard': ['content.view'],
            'data': ['content.view', 'content.edit'],
            'analysis': ['content.view'],
            'mcp': ['system.manage'],
            
            # header_pages
            'settings_page': ['user.manage'],
            'user_profile_page': [],  # 所有登录用户都可访问
        }
    
    def _get_database_url(self) -> str:
        """获取数据库URL
        一个私有方法（以下划线开头），用于根据 self.database_type 属性生成数据库连接字符串。
        """
        if self.database_type == 'sqlite':
            db_path = Path('data') / 'auth.db'
            db_path.parent.mkdir(exist_ok=True)
            return f'sqlite:///{db_path}'
        elif self.database_type == 'mysql':
            # 示例：mysql://user:password@localhost/dbname
            return os.environ.get('DATABASE_URL', 'mysql://root:12345678@localhost:3309/auth_db')
        elif self.database_type == 'postgresql':
            # 示例：postgresql://user:password@localhost/dbname
            return os.environ.get('DATABASE_URL', 'postgresql://neo:12345678@172.22.160.1/auth_db')
        else:
            raise ValueError(f"Unsupported database type: {self.database_type}")
    
    def set_database_type(self, db_type: str):
        """设置数据库类型
        允许在程序运行时动态修改数据库类型。
        """
        if db_type not in ['sqlite', 'mysql', 'postgresql']:
            raise ValueError(f"Unsupported database type: {db_type}")
        self.database_type = db_type
        self.database_url = self._get_database_url()

# 全局配置实例
# 创建了一个AuthConfig的全局实例 auth_config。在项目的其他地方，可以直接导入 auth_config 来访问和使用这些配置，而无需每次都创建一个新的 AuthConfig 对象
auth_config = AuthConfig()