from typing import Dict, Any, Optional, List
from enum import Enum

class AuthType(str, Enum):
    """认证类型枚举"""
    NONE = "none"
    PASSWORD = "password"
    X509 = "x509"
    SCRAM_SHA_1 = "SCRAM-SHA-1"
    SCRAM_SHA_256 = "SCRAM-SHA-256"

class SSLMode(str, Enum):
    """SSL 模式枚举"""
    DISABLED = "disabled"
    PREFERRED = "preferred"
    REQUIRED = "required"

class MongoDBConfig:
    """MongoDB 配置类"""
    def __init__(self, config_dict: Dict[str, Any]):
        self.config = config_dict
    def get_connection_string(self) -> str:
        """生成 MongoDB 连接字符串"""
        config = self.config
        # 基础连接信息
        if config["auth_type"] == AuthType.NONE:
            connection_string = f"mongodb://{config['host']}:{config['port']}/{config['database_name']}"
        else:
            username = config.get("username", "")
            password = config.get("password", "")
            connection_string = f"mongodb://{username}:{password}@{config['host']}:{config['port']}/{config['database_name']}" 
        # 添加查询参数
        params = []
        
        if config.get("auth_database") and config["auth_type"] != AuthType.NONE:
            params.append(f"authSource={config['auth_database']}")
        if config.get("replica_set"):
            params.append(f"replicaSet={config['replica_set']}")
        if config.get("read_preference", "primary") != "primary":
            params.append(f"readPreference={config['read_preference']}")
        if config.get("ssl_mode") == SSLMode.REQUIRED:
            params.append("ssl=true")
        elif config.get("ssl_mode") == SSLMode.PREFERRED:
            params.append("ssl=preferred")
        if params:
            connection_string += "?" + "&".join(params)
        return connection_string
    
    def get_collection_name(self) -> Optional[str]:
        """获取默认集合名称"""
        return self.config.get("collection_name")
# ==================== 预定义配置 ====================
# 开发环境配置
DEV_CONFIG = {
    "name": "开发环境",
    "host": "localhost",
    "port": 27017,
    "database_name": "dev_db",
    "collection_name": "users",  # 默认操作的集合
    "auth_type": AuthType.PASSWORD,
    "username": "dev_user",
    "password": "dev_password",
    "auth_database": "admin",
    "ssl_mode": SSLMode.DISABLED,
    "ssl_verify_cert": False,
    "replica_set": None,
    "read_preference": "primary",
    "connect_timeout_ms": 30000,
    "socket_timeout_ms": 30000,
    "server_selection_timeout_ms": 30000,
    "max_pool_size": 10,
    "min_pool_size": 1,
    "max_idle_time_ms": 60000,
    "description": "开发环境 MongoDB 配置",
    "is_active": True,
    "tags": ["dev", "local"]
}

# 测试环境配置
TEST_CONFIG = {
    "name": "测试环境",
    "host": "test-mongodb.example.com",
    "port": 27017,
    "database_name": "test_db",
    "collection_name": "test_data",  # 测试环境默认集合
    "auth_type": AuthType.SCRAM_SHA_256,
    "username": "test_user",
    "password": "test_password_123",
    "auth_database": "admin",
    "ssl_mode": SSLMode.PREFERRED,
    "ssl_verify_cert": True,
    "replica_set": "test-rs",
    "read_preference": "secondary",
    "connect_timeout_ms": 30000,
    "socket_timeout_ms": 30000,
    "server_selection_timeout_ms": 30000,
    "max_pool_size": 20,
    "min_pool_size": 2,
    "max_idle_time_ms": 60000,
    "description": "测试环境 MongoDB 配置",
    "is_active": True,
    "tags": ["test", "replica"]
}

# 生产环境配置
PROD_CONFIG = {
    "name": "生产环境",
    "host": "prod-mongodb.example.com",
    "port": 27017,
    "database_name": "prod_db",
    "collection_name": "orders",  # 生产环境默认操作订单集合
    "auth_type": AuthType.SCRAM_SHA_256,
    "username": "prod_user",
    "password": "prod_super_secure_password_456",
    "auth_database": "admin",
    "ssl_mode": SSLMode.REQUIRED,
    "ssl_cert_file": "/path/to/client.pem",
    "ssl_key_file": "/path/to/client-key.pem",
    "ssl_ca_file": "/path/to/ca.pem",
    "ssl_verify_cert": True,
    "replica_set": "prod-rs",
    "read_preference": "secondaryPreferred",
    "connect_timeout_ms": 30000,
    "socket_timeout_ms": 30000,
    "server_selection_timeout_ms": 30000,
    "max_pool_size": 50,
    "min_pool_size": 5,
    "max_idle_time_ms": 60000,
    "description": "生产环境 MongoDB 配置",
    "is_active": True,
    "tags": ["prod", "ssl", "replica"]
}

# Atlas 云数据库配置
ATLAS_CONFIG = {
    "name": "MongoDB Atlas",
    "host": "cluster0.xxxxx.mongodb.net",
    "port": 27017,
    "database_name": "atlas_db",
    "collection_name": "app_data",  # Atlas 默认集合
    "auth_type": AuthType.SCRAM_SHA_1,
    "username": "atlas_user",
    "password": "atlas_password_789",
    "auth_database": "admin",
    "ssl_mode": SSLMode.REQUIRED,
    "ssl_verify_cert": True,
    "replica_set": "atlas-cluster0-shard-0",
    "read_preference": "primary",
    "connect_timeout_ms": 30000,
    "socket_timeout_ms": 30000,
    "server_selection_timeout_ms": 30000,
    "max_pool_size": 30,
    "min_pool_size": 3,
    "max_idle_time_ms": 60000,
    "description": "MongoDB Atlas 云数据库配置",
    "is_active": True,
    "tags": ["atlas", "cloud", "ssl"]
}

# 无认证本地配置
LOCAL_NO_AUTH_CONFIG = {
    "name": "本地无认证",
    "host": "localhost",
    "port": 27017,
    "database_name": "数字政府",
    "collection_name": "一企一档",
    "auth_type": AuthType.NONE,
    "username": None,
    "password": None,
    "auth_database": None,
    "ssl_mode": SSLMode.DISABLED,
    "ssl_verify_cert": False,
    "replica_set": None,
    "read_preference": "primary",
    "connect_timeout_ms": 30000,
    "socket_timeout_ms": 30000,
    "server_selection_timeout_ms": 30000,
    "max_pool_size": 50,
    "min_pool_size": 20,
    "max_idle_time_ms": 60000,
    "description": "本地开发用无认证配置",
    "is_active": True,
    "tags": ["local", "no-auth"]
}

# X.509 证书认证配置
X509_CONFIG = {
    "name": "X.509认证",
    "host": "secure-mongodb.example.com",
    "port": 27017,
    "database_name": "secure_db",
    "collection_name": "secure_data",  # 安全数据集合
    "auth_type": AuthType.X509,
    "username": "C=US,ST=NY,L=NYC,O=Example,OU=IT,CN=client",
    "password": None,
    "auth_database": "$external",
    "ssl_mode": SSLMode.REQUIRED,
    "ssl_cert_file": "/path/to/client.pem",
    "ssl_key_file": "/path/to/client-key.pem",
    "ssl_ca_file": "/path/to/ca.pem",
    "ssl_verify_cert": True,
    "replica_set": "secure-rs",
    "read_preference": "primary",
    "connect_timeout_ms": 30000,
    "socket_timeout_ms": 30000,
    "server_selection_timeout_ms": 30000,
    "max_pool_size": 20,
    "min_pool_size": 2,
    "max_idle_time_ms": 60000,
    "description": "使用 X.509 证书认证的安全配置",
    "is_active": True,
    "tags": ["x509", "secure", "ssl"]
}
# ==================== 配置映射 ====================
CONFIGS = {
    "dev": MongoDBConfig(DEV_CONFIG),
    "test": MongoDBConfig(TEST_CONFIG),
    "prod": MongoDBConfig(PROD_CONFIG),
    "atlas": MongoDBConfig(ATLAS_CONFIG),
    "local": MongoDBConfig(LOCAL_NO_AUTH_CONFIG),
    "x509": MongoDBConfig(X509_CONFIG),
}
# 默认配置
DEFAULT_CONFIG = CONFIGS["local"]
# ==================== 便捷函数 ====================
def get_connection_string(env: str = "local") -> str:
    """获取指定环境的连接字符串"""
    return get_config(env).get_connection_string()
def get_config(env: str = "local") -> MongoDBConfig:
    """获取指定环境的配置"""
    return CONFIGS.get(env, DEFAULT_CONFIG)
def list_configs() -> List[str]:
    """列出所有可用的配置"""
    return list(CONFIGS.keys())
def add_config(name: str, config_dict: Dict[str, Any]) -> None:
    """添加新的配置"""
    CONFIGS[name] = MongoDBConfig(config_dict)