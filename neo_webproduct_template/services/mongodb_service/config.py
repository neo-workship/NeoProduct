from typing import Dict, Any, Optional, List
from enum import Enum
import yaml
import os
from pathlib import Path

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

class ConfigLoader:
    """配置加载器"""
    
    def __init__(self, config_file_path: Optional[str] = None):
        """
        初始化配置加载器
        
        Args:
            config_file_path: YAML配置文件路径，如果为None则使用默认路径
        """
        if config_file_path is None:
            # 默认配置文件路径：项目根目录的 config/mongo_config.yaml
            current_dir = Path(__file__).parent
            project_root = current_dir.parent.parent  # 向上两级到项目根目录
            self.config_file_path = project_root / "config" / "yaml" / "mongo_config.yaml"
        else:
            self.config_file_path = Path(config_file_path)
        
        self._yaml_config = None
        self._load_config()
    
    def _load_config(self) -> None:
        """从YAML文件加载配置"""
        try:
            if not self.config_file_path.exists():
                raise FileNotFoundError(f"MongoDB配置文件不存在: {self.config_file_path}")
            
            with open(self.config_file_path, 'r', encoding='utf-8') as file:
                self._yaml_config = yaml.safe_load(file)
            
            if not self._yaml_config or 'environments' not in self._yaml_config:
                raise ValueError("无效的配置文件格式，缺少 'environments' 节点")
                
        except FileNotFoundError as e:
            print(f"警告: {e}")
            print("将使用默认的硬编码配置")
            self._yaml_config = None
        except yaml.YAMLError as e:
            print(f"YAML配置文件解析错误: {e}")
            print("将使用默认的硬编码配置")
            self._yaml_config = None
        except Exception as e:
            print(f"加载配置文件时发生错误: {e}")
            print("将使用默认的硬编码配置")
            self._yaml_config = None
    
    def get_environment_config(self, env: str) -> Dict[str, Any]:
        """
        获取指定环境的配置
        
        Args:
            env: 环境名称
            
        Returns:
            Dict[str, Any]: 环境配置字典
        """
        if self._yaml_config and 'environments' in self._yaml_config:
            env_config = self._yaml_config['environments'].get(env)
            if env_config:
                return env_config
        
        # 如果YAML配置不可用，返回硬编码的备用配置
        return self._get_fallback_config(env)
    
    def get_default_environment(self) -> str:
        """获取默认环境名称"""
        if self._yaml_config and 'default_environment' in self._yaml_config:
            return self._yaml_config['default_environment']
        return "local"
    
    def list_environments(self) -> List[str]:
        """列出所有可用的环境"""
        if self._yaml_config and 'environments' in self._yaml_config:
            return list(self._yaml_config['environments'].keys())
        return ["dev", "test", "prod", "atlas", "local", "x509"]
    
    def _get_fallback_config(self, env: str) -> Dict[str, Any]:
        """获取硬编码的备用配置"""
        fallback_configs = {
            "dev": {
                "name": "开发环境",
                "host": "localhost",
                "port": 27017,
                "database_name": "dev_db",
                "collection_name": "users",
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
            },
            "test": {
                "name": "测试环境",
                "host": "test-mongodb.example.com",
                "port": 27017,
                "database_name": "test_db",
                "collection_name": "test_data",
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
            },
            "prod": {
                "name": "生产环境",
                "host": "prod-mongodb.example.com",
                "port": 27017,
                "database_name": "prod_db",
                "collection_name": "orders",
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
            },
            "atlas": {
                "name": "MongoDB Atlas",
                "host": "cluster0.xxxxx.mongodb.net",
                "port": 27017,
                "database_name": "atlas_db",
                "collection_name": "app_data",
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
            },
            "local": {
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
            },
            "x509": {
                "name": "X.509认证",
                "host": "secure-mongodb.example.com",
                "port": 27017,
                "database_name": "secure_db",
                "collection_name": "secure_data",
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
        }
        
        return fallback_configs.get(env, fallback_configs["local"])

# ==================== 全局配置加载器实例 ====================
_config_loader = ConfigLoader()

# ==================== 配置映射 ====================
def _create_configs() -> Dict[str, MongoDBConfig]:
    """动态创建配置映射"""
    configs = {}
    for env in _config_loader.list_environments():
        config_dict = _config_loader.get_environment_config(env)
        configs[env] = MongoDBConfig(config_dict)
    return configs

CONFIGS = _create_configs()

# 默认配置
DEFAULT_CONFIG = CONFIGS.get(_config_loader.get_default_environment(), CONFIGS.get("local"))

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

def reload_config(config_file_path: Optional[str] = None) -> None:
    """重新加载配置文件"""
    global _config_loader, CONFIGS, DEFAULT_CONFIG
    _config_loader = ConfigLoader(config_file_path)
    CONFIGS = _create_configs()
    DEFAULT_CONFIG = CONFIGS.get(_config_loader.get_default_environment(), CONFIGS.get("local"))

def get_config_file_path() -> Path:
    """获取当前使用的配置文件路径"""
    return _config_loader.config_file_path

def is_yaml_config_available() -> bool:
    """检查YAML配置文件是否可用"""
    return _config_loader._yaml_config is not None