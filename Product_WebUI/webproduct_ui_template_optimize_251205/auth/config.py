"""
认证配置模块 - 使用环境变量版本

从 .env 文件加载所有配置，支持灵活的配置管理。
"""
import os
from pathlib import Path
from typing import Optional

# 导入环境变量配置加载器
try:
    from config.env_config import env_config
except ImportError:
    # 如果导入失败，使用简单的环境变量读取
    print("⚠️  无法导入 config.env_config，将直接使用 os.environ")
    
    class SimpleEnvConfig:
        def get(self, key, default=None):
            return os.environ.get(key, default)
        
        def get_int(self, key, default=0):
            try:
                return int(os.environ.get(key, default))
            except:
                return default
        
        def get_bool(self, key, default=False):
            value = os.environ.get(key, '').lower()
            if value in ('true', 'yes', '1', 'on'):
                return True
            elif value in ('false', 'no', '0', 'off'):
                return False
            return default
    
    env_config = SimpleEnvConfig()


class AuthConfig:
    """
    认证配置类 - 使用环境变量版本
    
    所有配置都从 .env 文件加载，支持：
    - 数据库配置
    - 会话管理
    - 密码策略
    - 登录安全
    - 功能开关
    - 路由配置
    """
    
    def __init__(self):
        """
        初始化认证配置
        
        从 .env 文件加载所有配置项，并提供合理的默认值。
        """
        # ==================== 数据库配置 ====================
        self.database_type = env_config.get('AUTH_DATABASE_TYPE', 'sqlite')
        self.database_url = self._get_database_url()
        
        # ==================== 会话配置 ====================
        self.session_secret_key = env_config.get('AUTH_SESSION_SECRET_KEY','8CAs6NgrsLAaB0Aw-w6lSv--ISwffsDK2cDDKN1r_bQ')
        
        # 会话超时时间（秒，默认24小时）
        self.session_timeout = env_config.get_int('AUTH_SESSION_TIMEOUT',3600 * 24)
        
        # "记住我"持续时间（秒，默认30天）
        self.remember_me_duration = env_config.get_int('AUTH_REMEMBER_ME_DURATION',3600 * 24 * 30)
        
        # ==================== 密码策略配置 ====================
        self.password_min_length = env_config.get_int('AUTH_PASSWORD_MIN_LENGTH',6)
        
        self.password_max_length = env_config.get_int('AUTH_PASSWORD_MAX_LENGTH',128)
        
        self.password_require_uppercase = env_config.get_bool('AUTH_PASSWORD_REQUIRE_UPPERCASE',False)
        
        self.password_require_lowercase = env_config.get_bool('AUTH_PASSWORD_REQUIRE_LOWERCASE',False)
        
        self.password_require_digit = env_config.get_bool('AUTH_PASSWORD_REQUIRE_DIGIT',False)
        
        self.password_require_special = env_config.get_bool('AUTH_PASSWORD_REQUIRE_SPECIAL',False)
        
        # ==================== 登录安全配置 ====================
        # 最大登录失败次数
        self.max_login_attempts = env_config.get_int('AUTH_MAX_LOGIN_ATTEMPTS',5)
        
        # 账户锁定持续时间（分钟）
        self.login_lock_duration = env_config.get_int('AUTH_LOGIN_LOCK_DURATION',30)
        
        # 是否启用验证码
        self.enable_captcha = env_config.get_bool('AUTH_ENABLE_CAPTCHA',False)
        
        # ==================== 功能开关 ====================
        # 是否允许用户注册
        self.allow_registration = env_config.get_bool('AUTH_ALLOW_REGISTRATION',True)
        
        # 是否允许"记住我"
        self.allow_remember_me = env_config.get_bool('AUTH_ALLOW_REMEMBER_ME',True)
        
        # 是否启用邮箱验证
        self.enable_email_verification = env_config.get_bool('AUTH_ENABLE_EMAIL_VERIFICATION', False)
        
        # 是否启用双因素认证
        self.enable_two_factor = env_config.get_bool('AUTH_ENABLE_TWO_FACTOR',False)
        
        # ==================== 路由配置 ====================
        self.login_route = env_config.get('AUTH_LOGIN_ROUTE','/login')
        
        self.register_route = env_config.get('AUTH_REGISTER_ROUTE','/register')
        
        self.logout_route = env_config.get('AUTH_LOGOUT_ROUTE','/logout')
        
        self.default_redirect = env_config.get('AUTH_DEFAULT_REDIRECT','/workbench')
    
    def _get_database_url(self) -> str:
        """
        根据数据库类型构建连接URL
        
        Returns:
            str: 数据库连接URL
        """
        db_type = self.database_type.lower()
        
        if db_type == 'sqlite':
            # SQLite 数据库路径
            sqlite_path = env_config.get(
                'AUTH_SQLITE_PATH',
                'data/neoapp.db'
            )
            
            # 确保数据目录存在
            db_path = Path(sqlite_path)
            db_path.parent.mkdir(parents=True, exist_ok=True)
            
            return f'sqlite:///{sqlite_path}'
        
        elif db_type == 'mysql':
            # MySQL 连接配置
            host = env_config.get('AUTH_MYSQL_HOST', 'localhost')
            port = env_config.get_int('AUTH_MYSQL_PORT', 3306)
            user = env_config.get('AUTH_MYSQL_USER', 'root')
            password = env_config.get('AUTH_MYSQL_PASSWORD', '')
            database = env_config.get('AUTH_MYSQL_DATABASE', 'neoapp')
            
            return f'mysql+pymysql://{user}:{password}@{host}:{port}/{database}'
        
        elif db_type == 'postgresql':
            # PostgreSQL 连接配置
            host = env_config.get('AUTH_POSTGRES_HOST', 'localhost')
            port = env_config.get_int('AUTH_POSTGRES_PORT', 5432)
            user = env_config.get('AUTH_POSTGRES_USER', 'postgres')
            password = env_config.get('AUTH_POSTGRES_PASSWORD', '')
            database = env_config.get('AUTH_POSTGRES_DATABASE', 'neoapp')
            
            return f'postgresql://{user}:{password}@{host}:{port}/{database}'
        
        else:
            # 默认使用 SQLite
            print(f"⚠️  未知的数据库类型: {db_type}，使用默认 SQLite")
            return 'sqlite:///data/neoapp.db'
    
# 全局配置实例
auth_config = AuthConfig()