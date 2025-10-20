# database_models/__init__.py
"""
统一业务模型导出
提供所有业务表模型的统一访问入口
"""

# 导入共享基类
from .shared_base import BusinessBaseModel, TimestampMixin, AuditMixin

# 导入OpenAI相关模型
from .business_models.openai_models import (
    OpenAIConfig,
    OpenAIRequest, 
    ModelType
)

from .business_models.mongodb_models import (
    MongoDBConfig,
    MongoDBAuthType,
    MongoDBSSLMode,
    MongoDBConnectionLog
)

# 在这里添加其他业务模型的导入
# from .business_models.mongodb_models import MongoDBConfig, MongoDBConnection
# from .business_models.audit_models import AuditRecord, AuditAction
# from .business_models.smart_index_models import IndexConfig, IndexResult

__all__ = [
    # 基础类
    'BusinessBaseModel',
    'TimestampMixin', 
    'AuditMixin',
    
    # OpenAI模型
    'OpenAIConfig',
    'OpenAIRequest',
    'ModelType',
    
    # MongoDB模型
    'MongoDBConfig',
    'MongoDBAuthType',
    'MongoDBSSLMode',
    'MongoDBConnectionLog',
]

def get_all_business_models():
    """获取所有业务模型类列表"""
    return [
        OpenAIConfig,
        OpenAIRequest,
        # 在这里添加其他模型类
        MongoDBConfig,
        MongoDBConnectionLog,
    ]

def get_models_by_category():
    """按类别获取模型"""
    return {
        'openai': [OpenAIConfig, OpenAIRequest],
        'mongodb': [MongoDBConfig, MongoDBConnectionLog],
        # 'mongodb': [MongoDBConfig, MongoDBConnection],
        # 'audit': [AuditRecord, AuditAction],
        # 'smart_index': [IndexConfig, IndexResult],
    }