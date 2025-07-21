# database_models/business_models/openai_models.py
from sqlalchemy import Column, String, Integer, Text, Boolean, JSON, Enum, ForeignKey
from sqlalchemy.orm import relationship, declared_attr
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
    
    # 内部关系（不依赖外部模型）
    requests = relationship("OpenAIRequest", back_populates="config", cascade="all, delete-orphan")
    
    def get_user_info(self):
        """获取创建者的详细信息"""
        return self.get_creator_info()  # 使用基类方法
    
    def get_request_count(self):
        """获取请求数量"""
        return len(self.requests) if self.requests else 0
    
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
    
    # 内部关系
    config = relationship("OpenAIConfig", back_populates="requests")
    
    def get_user_info(self):
        """获取请求用户信息"""
        if not self.user_id:
            return None
            
        try:
            from auth.database import get_db
            from auth.models import User
            
            with get_db() as db:
                user = db.query(User).filter(User.id == self.user_id).first()
                if user:
                    return {
                        'id': user.id,
                        'username': user.username,
                        'full_name': user.full_name
                    }
        except Exception:
            pass
        return None
    
    def __repr__(self):
        return f"<OpenAIRequest(user_id={self.user_id}, status='{self.status}')>"

# 可选：如果需要在OpenAI模块中访问用户关系，可以定义扩展方法
class OpenAIUserMixin:
    """OpenAI模块的用户关系混入（可选使用）"""
    
    @declared_attr
    def user(cls):
        """可选的用户关系"""
        return relationship("User", lazy="select")

# 示例：如果某个特定模型需要用户关系，可以这样继承
# class OpenAIRequestWithUser(OpenAIRequest, OpenAIUserMixin):
#     pass