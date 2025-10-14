# database_models/business_models/mongodb_models.py
from sqlalchemy import Column, String, Integer, Text, Boolean, JSON, Enum, ForeignKey
from sqlalchemy.orm import relationship
from ..shared_base import BusinessBaseModel
import enum

class MongoDBAuthType(enum.Enum):
    """MongoDB认证类型枚举"""
    NONE = "none"  # 无认证
    PASSWORD = "password"  # 用户名密码认证
    X509 = "x509"  # X.509证书认证
    SCRAM_SHA_1 = "SCRAM-SHA-1"  # SCRAM-SHA-1认证
    SCRAM_SHA_256 = "SCRAM-SHA-256"  # SCRAM-SHA-256认证

class MongoDBSSLMode(enum.Enum):
    """MongoDB SSL连接模式枚举"""
    DISABLED = "disabled"  # 禁用SSL
    PREFERRED = "preferred"  # 优先使用SSL
    REQUIRED = "required"  # 必须使用SSL

class MongoDBConfig(BusinessBaseModel):
    """MongoDB连接配置模型"""
    __tablename__ = 'mongodb_configs'
    
    # === 基础配置信息 ===
    name = Column(String(100), nullable=False, index=True, comment="配置名称")
    
    # === 连接信息 ===
    host = Column(String(255), nullable=False, default="localhost", comment="主机地址")
    port = Column(Integer, nullable=False, default=27017, comment="端口号")
    database_name = Column(String(100), nullable=False, comment="数据库名称")
    
    # === 认证信息 ===
    auth_type = Column(Enum(MongoDBAuthType), default=MongoDBAuthType.PASSWORD, comment="认证类型")
    username = Column(String(100), nullable=True, comment="用户名")
    password = Column(String(255), nullable=True, comment="密码(加密存储)")
    auth_database = Column(String(100), nullable=True, default="admin", comment="认证数据库")
    
    # === SSL/TLS配置 ===
    ssl_mode = Column(Enum(MongoDBSSLMode), default=MongoDBSSLMode.DISABLED, comment="SSL模式")
    ssl_cert_file = Column(String(500), nullable=True, comment="SSL证书文件路径")
    ssl_key_file = Column(String(500), nullable=True, comment="SSL私钥文件路径")
    ssl_ca_file = Column(String(500), nullable=True, comment="SSL CA证书文件路径")
    
    # === 连接池配置 ===
    max_pool_size = Column(Integer, default=100, comment="最大连接池大小")
    min_pool_size = Column(Integer, default=0, comment="最小连接池大小")
    max_idle_time_ms = Column(Integer, default=30000, comment="最大空闲时间(毫秒)")
    connect_timeout_ms = Column(Integer, default=20000, comment="连接超时时间(毫秒)")
    socket_timeout_ms = Column(Integer, default=20000, comment="Socket超时时间(毫秒)")
    server_selection_timeout_ms = Column(Integer, default=30000, comment="服务器选择超时时间(毫秒)")
    
    # === 高级配置 ===
    replica_set = Column(String(100), nullable=True, comment="副本集名称")
    read_preference = Column(String(50), default="primary", comment="读偏好设置")
    write_concern = Column(JSON, nullable=True, comment="写关注设置")
    read_concern = Column(String(50), nullable=True, comment="读关注级别")
    
    # === 权限控制 ===
    is_public = Column(Boolean, default=False, comment="是否公开可用")
    allowed_roles = Column(JSON, default=list, comment="允许的角色列表")
    
    # === 使用统计 ===
    total_connections = Column(Integer, default=0, comment="总连接数")
    last_connected_at = Column(String(30), nullable=True, comment="最后连接时间")
    connection_status = Column(String(20), default='unknown', comment="连接状态")
    
    # === 扩展配置 ===
    additional_options = Column(JSON, nullable=True, comment="附加连接选项")
    tags = Column(JSON, default=list, comment="标签列表，用于分类")
    
    def get_connection_string(self, include_password=False):
        """
        生成MongoDB连接字符串
        
        Args:
            include_password (bool): 是否包含密码
            
        Returns:
            str: MongoDB连接字符串
        """
        # 基础URI
        if self.auth_type == MongoDBAuthType.NONE:
            uri = f"mongodb://{self.host}:{self.port}/{self.database_name}"
        else:
            if include_password and self.username and self.password:
                uri = f"mongodb://{self.username}:{self.password}@{self.host}:{self.port}/{self.database_name}"
            elif self.username:
                uri = f"mongodb://{self.username}@{self.host}:{self.port}/{self.database_name}"
            else:
                uri = f"mongodb://{self.host}:{self.port}/{self.database_name}"
        
        # 添加参数
        params = []
        
        if self.auth_database and self.auth_type != MongoDBAuthType.NONE:
            params.append(f"authSource={self.auth_database}")
            
        if self.auth_type != MongoDBAuthType.NONE and self.auth_type != MongoDBAuthType.PASSWORD:
            params.append(f"authMechanism={self.auth_type.value}")
            
        if self.ssl_mode != MongoDBSSLMode.DISABLED:
            params.append(f"ssl=true")
            if self.ssl_mode == MongoDBSSLMode.REQUIRED:
                params.append("ssl_cert_reqs=CERT_REQUIRED")
                
        if self.replica_set:
            params.append(f"replicaSet={self.replica_set}")
            
        if self.read_preference != "primary":
            params.append(f"readPreference={self.read_preference}")
            
        # 连接超时设置
        params.append(f"connectTimeoutMS={self.connect_timeout_ms}")
        params.append(f"socketTimeoutMS={self.socket_timeout_ms}")
        params.append(f"serverSelectionTimeoutMS={self.server_selection_timeout_ms}")
        params.append(f"maxPoolSize={self.max_pool_size}")
        params.append(f"minPoolSize={self.min_pool_size}")
        params.append(f"maxIdleTimeMS={self.max_idle_time_ms}")
        
        if params:
            uri += "?" + "&".join(params)
            
        return uri
    
    def get_safe_connection_info(self):
        """获取安全的连接信息（不包含密码）"""
        return {
            'name': self.name,
            'host': self.host,
            'port': self.port,
            'database_name': self.database_name,
            'auth_type': self.auth_type.value,
            'username': self.username,
            'auth_database': self.auth_database,
            'ssl_mode': self.ssl_mode.value,
            'replica_set': self.replica_set,
            'connection_string': self.get_connection_string(include_password=False)
        }
    
    def test_connection(self):
        """
        测试数据库连接
        
        Returns:
            dict: 连接测试结果
        """
        try:
            from pymongo import MongoClient
            from datetime import datetime
            
            # 创建连接字符串
            connection_string = self.get_connection_string(include_password=True)
            
            # 尝试连接
            client = MongoClient(connection_string, serverSelectionTimeoutMS=5000)
            
            # 测试连接
            db = client[self.database_name]
            server_info = client.server_info()
            
            # 更新连接状态
            self.connection_status = 'success'
            self.last_connected_at = datetime.now().isoformat()
            self.total_connections += 1
            
            client.close()
            
            return {
                'success': True,
                'message': '连接成功',
                'server_version': server_info.get('version'),
                'connection_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.connection_status = 'failed'
            return {
                'success': False,
                'message': f'连接失败: {str(e)}',
                'error_type': type(e).__name__
            }
    
    def get_creator_info(self):
        """获取创建者信息"""
        return super().get_creator_info()
    
    def get_connection_count(self):
        """获取连接统计"""
        return {
            'total_connections': self.total_connections,
            'last_connected': self.last_connected_at,
            'status': self.connection_status
        }
    
    def update_connection_stats(self):
        """更新连接统计"""
        from datetime import datetime
        self.total_connections += 1
        self.last_connected_at = datetime.now().isoformat()
    
    def to_dict_extended(self, include_sensitive=False):
        """
        扩展的字典转换，包含额外信息
        
        Args:
            include_sensitive (bool): 是否包含敏感信息（如密码）
            
        Returns:
            dict: 扩展的字典数据
        """
        base_dict = self.to_dict(include_audit_info=True)
        
        # 移除敏感信息（除非明确要求包含）
        if not include_sensitive and 'password' in base_dict:
            base_dict['password'] = '***隐藏***'
            
        # 添加扩展信息
        base_dict.update({
            'connection_info': self.get_safe_connection_info(),
            'connection_stats': self.get_connection_count(),
            'is_ssl_enabled': self.ssl_mode != MongoDBSSLMode.DISABLED,
            'has_auth': self.auth_type != MongoDBAuthType.NONE,
            'has_replica_set': bool(self.replica_set)
        })
        
        return base_dict
    
    def __repr__(self):
        return f"<MongoDBConfig(name='{self.name}', host='{self.host}:{self.port}', db='{self.database_name}')>"

# 可选：MongoDB连接会话记录表（如果需要记录连接历史）
class MongoDBConnectionLog(BusinessBaseModel):
    """MongoDB连接日志记录（可选）"""
    __tablename__ = 'mongodb_connection_logs'
    
    config_id = Column(Integer, ForeignKey('mongodb_configs.id'), nullable=False, comment="配置ID")
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, comment="用户ID")
    
    # 连接信息
    connection_time = Column(String(30), nullable=False, comment="连接时间")
    operation_type = Column(String(50), nullable=False, comment="操作类型")
    operation_result = Column(String(20), default='success', comment="操作结果")
    error_message = Column(Text, nullable=True, comment="错误信息")
    
    # 性能信息
    response_time_ms = Column(Integer, nullable=True, comment="响应时间(毫秒)")
    documents_affected = Column(Integer, default=0, comment="影响的文档数")
    
    # 元数据
    client_info = Column(JSON, nullable=True, comment="客户端信息")
    query_info = Column(JSON, nullable=True, comment="查询信息")
    
    # 关系
    config = relationship("MongoDBConfig", backref="connection_logs")
    
    def __repr__(self):
        return f"<MongoDBConnectionLog(config_id={self.config_id}, operation='{self.operation_type}', result='{self.operation_result}')>"