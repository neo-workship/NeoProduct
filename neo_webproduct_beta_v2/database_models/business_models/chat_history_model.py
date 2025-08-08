# database_models/business_models/chat_history_model.py
"""
聊天历史模型 - 存储用户聊天记录
"""
from sqlalchemy import Column, String, Text, Integer, JSON
from ..shared_base import BusinessBaseModel

class ChatHistory(BusinessBaseModel):
    """聊天历史表"""
    __tablename__ = 'chat_histories'
    
    # 聊天标题
    title = Column(String(200), nullable=False, comment='聊天标题')
    
    # 使用的模型
    model_name = Column(String(100), nullable=True, comment='使用的AI模型')
    
    # 聊天消息内容(JSON格式存储)
    messages = Column(JSON, nullable=False, comment='聊天消息列表')
    
    # 关联用户ID (来自继承的 created_by 字段)
    # created_by 字段已在 BusinessBaseModel 中定义，无需重复
    
    def __repr__(self):
        return f"<ChatHistory(id={self.id}, title='{self.title}', user_id={self.created_by})>"