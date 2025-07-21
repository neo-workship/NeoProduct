# database_models/business_models/openai_models.py
from sqlalchemy import Column, String, Integer, Text, Boolean, JSON, Enum
from sqlalchemy.orm import relationship
from ..shared_base import BusinessBaseModel
import enum

class ModelType(enum.Enum):
    """模型类型枚举"""
    DEEPSEEK = "deepseek-chat"
    MOONSHOT_V1_8K = "moonshot-v1-8k"
    MOONSHOT_V1_32K = "moonshot-v1-32k"

class OpenAIConfig(BusinessBaseModel):
    """OpenAI配置模型"""
    __tablename__ = 'openai_configs'
    
    # 基础配置
    name = Column(String(100), nullable=False, index=True)
    api_key = Column(String(255), nullable=False)
    base_url = Column(String(255), default="https://api.deepseek.com/v1")
    
    # 模型配置
    model_name = Column(Enum(ModelType), default=ModelType.DEEPSEEK)
    max_tokens = Column(Integer, default=1000)
    temperature = Column(Integer, default=70)  # 存储为整数 0-100
    
    # 权限控制（与auth模型关联）
    is_public = Column(Boolean, default=False)  # 是否公开可用
    allowed_roles = Column(JSON, default=list)  # 允许的角色列表 ["admin", "editor"]
    
    # 使用统计
    total_requests = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    
    def __repr__(self):
        return f"<OpenAIConfig(name='{self.name}', model='{self.model_name.value}')>"

class OpenAIRequest(BusinessBaseModel):
    """OpenAI请求记录"""
    __tablename__ = 'openai_requests'
    
    config_id = Column(Integer, ForeignKey('openai_configs.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)  # 直接关联用户
    
    # 请求信息
    prompt = Column(Text, nullable=False)
    response = Column(Text)
    tokens_used = Column(Integer, default=0)
    cost = Column(Integer, default=0)  # 成本（以分为单位）
    
    # 状态
    status = Column(String(20), default='pending')  # pending, success, error
    error_message = Column(Text)
    
    # 关系
    config = relationship("OpenAIConfig", back_populates="requests")
    user = relationship("User", back_populates="openai_requests")
    
    def __repr__(self):
        return f"<OpenAIRequest(user_id={self.user_id}, status='{self.status}')>"

# 在OpenAIConfig中添加反向关系
OpenAIConfig.requests = relationship("OpenAIRequest", back_populates="config", cascade="all, delete-orphan")