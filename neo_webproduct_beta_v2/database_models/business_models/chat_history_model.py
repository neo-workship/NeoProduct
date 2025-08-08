# database_models/business_models/chat_history_model.py
"""
聊天历史模型 - 存储用户聊天记录
"""
from sqlalchemy import Column, String, Text, Integer, JSON, Boolean, DateTime, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from typing import List, Optional, Dict, Any
from datetime import datetime
from ..shared_base import BusinessBaseModel

class ChatHistory(BusinessBaseModel):
    """聊天历史表"""
    __tablename__ = 'chat_histories'
    
    # 基础字段
    title = Column(String(200), nullable=False, comment='聊天标题')
    model_name = Column(String(100), nullable=True, comment='使用的AI模型')
    messages = Column(JSON, nullable=False, comment='聊天消息列表')
    
    # 新增字段 - 统计和缓存信息
    message_count = Column(Integer, default=0, comment='消息总数')
    last_message_at = Column(DateTime, nullable=True, comment='最后一条消息时间')
    
    # 软删除支持
    is_deleted = Column(Boolean, default=False, comment='是否已删除')
    deleted_at = Column(DateTime, nullable=True, comment='删除时间')
    deleted_by = Column(Integer, nullable=True, comment='删除人ID')
    
    # 创建复合索引
    __table_args__ = (
        # 用户聊天记录按时间排序的复合索引
        Index('idx_user_created_time', 'created_by', 'created_at'),
        # 用户有效记录查询索引
        Index('idx_user_active_records', 'created_by', 'is_deleted', 'is_active'),
        # 最后消息时间索引（用于最近活动排序）
        Index('idx_last_message_time', 'last_message_at'),
    )
    
    def __repr__(self):
        return f"<ChatHistory(id={self.id}, title='{self.title}', user_id={self.created_by}, messages={self.message_count})>"
    
    # === 实例方法 ===
    
    def update_message_stats(self):
        """更新消息统计信息"""
        if self.messages:
            self.message_count = len(self.messages)
            # 找到最后一条消息的时间
            last_timestamp = None
            for msg in reversed(self.messages):
                timestamp_str = msg.get('timestamp')
                if timestamp_str:
                    try:
                        last_timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                        break
                    except (ValueError, AttributeError):
                        continue
            
            self.last_message_at = last_timestamp or self.updated_at
        else:
            self.message_count = 0
            self.last_message_at = self.updated_at
    
    def soft_delete(self, deleted_by_user_id: int):
        """软删除聊天记录"""
        self.is_deleted = True
        self.deleted_at = func.now()
        self.deleted_by = deleted_by_user_id
        self.is_active = False
    
    def restore(self):
        """恢复已删除的聊天记录"""
        self.is_deleted = False
        self.deleted_at = None
        self.deleted_by = None
        self.is_active = True
    
    def get_message_preview(self, max_length: int = 50) -> str:
        """获取消息预览（第一条用户消息）"""
        if not self.messages:
            return "空对话"
        
        for msg in self.messages:
            if msg.get('role') == 'user':
                content = msg.get('content', '')
                if len(content) <= max_length:
                    return content
                return content[:max_length] + '...'
        
        return "无用户消息"
    
    def get_duration_info(self) -> Dict[str, Any]:
        """获取对话时长信息"""
        if not self.messages or len(self.messages) < 2:
            return {'duration_minutes': 0, 'message_count': self.message_count}
        
        first_timestamp = None
        last_timestamp = None
        
        for msg in self.messages:
            timestamp_str = msg.get('timestamp')
            if timestamp_str:
                try:
                    timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                    if first_timestamp is None:
                        first_timestamp = timestamp
                    last_timestamp = timestamp
                except (ValueError, AttributeError):
                    continue
        
        if first_timestamp and last_timestamp:
            duration = last_timestamp - first_timestamp
            duration_minutes = duration.total_seconds() / 60
        else:
            duration_minutes = 0
        
        return {
            'duration_minutes': round(duration_minutes, 1),
            'message_count': self.message_count,
            'first_message': first_timestamp,
            'last_message': last_timestamp
        }
    
    # === 类方法 ===
    
    @classmethod
    def get_user_recent_chats(cls, db_session, user_id: int, limit: int = 20, include_deleted: bool = False) -> List['ChatHistory']:
        """获取用户最近的聊天记录"""
        query = db_session.query(cls).filter(cls.created_by == user_id)
        
        if not include_deleted:
            query = query.filter(cls.is_deleted == False, cls.is_active == True)
        
        return query.order_by(cls.created_at.desc()).limit(limit).all()
    
    @classmethod
    def get_user_active_chat_count(cls, db_session, user_id: int) -> int:
        """获取用户有效聊天记录数量"""
        return db_session.query(cls).filter(
            cls.created_by == user_id,
            cls.is_deleted == False,
            cls.is_active == True
        ).count()
    
    @classmethod
    def search_user_chats_by_title(cls, db_session, user_id: int, keyword: str, limit: int = 10) -> List['ChatHistory']:
        """按标题搜索用户的聊天记录"""
        return db_session.query(cls).filter(
            cls.created_by == user_id,
            cls.is_deleted == False,
            cls.is_active == True,
            cls.title.ilike(f'%{keyword}%')
        ).order_by(cls.created_at.desc()).limit(limit).all()
    
    @classmethod
    def get_user_chats_by_model(cls, db_session, user_id: int, model_name: str) -> List['ChatHistory']:
        """获取用户使用特定模型的聊天记录"""
        return db_session.query(cls).filter(
            cls.created_by == user_id,
            cls.model_name == model_name,
            cls.is_deleted == False,
            cls.is_active == True
        ).order_by(cls.created_at.desc()).all()
    
    @classmethod
    def get_user_chat_stats(cls, db_session, user_id: int) -> Dict[str, Any]:
        """获取用户聊天统计信息"""
        from sqlalchemy import func as sql_func
        
        # 基础统计
        total_chats = db_session.query(cls).filter(
            cls.created_by == user_id,
            cls.is_deleted == False
        ).count()
        
        total_messages = db_session.query(sql_func.sum(cls.message_count)).filter(
            cls.created_by == user_id,
            cls.is_deleted == False
        ).scalar() or 0
        
        # 最近活动
        recent_chat = db_session.query(cls).filter(
            cls.created_by == user_id,
            cls.is_deleted == False
        ).order_by(cls.last_message_at.desc()).first()
        
        # 常用模型统计
        model_stats = db_session.query(
            cls.model_name,
            sql_func.count(cls.id).label('count')
        ).filter(
            cls.created_by == user_id,
            cls.is_deleted == False,
            cls.model_name.isnot(None)
        ).group_by(cls.model_name).order_by(sql_func.count(cls.id).desc()).all()
        
        return {
            'total_chats': total_chats,
            'total_messages': total_messages,
            'last_activity': recent_chat.last_message_at if recent_chat else None,
            'favorite_models': [{'model': stat[0], 'count': stat[1]} for stat in model_stats[:5]]
        }
    
    @classmethod
    def cleanup_old_deleted_chats(cls, db_session, days_old: int = 30) -> int:
        """清理指定天数前的已删除聊天记录"""
        from sqlalchemy import and_
        from datetime import timedelta
        
        cutoff_date = datetime.now() - timedelta(days=days_old)
        
        # 物理删除很久之前的软删除记录
        deleted_count = db_session.query(cls).filter(
            and_(
                cls.is_deleted == True,
                cls.deleted_at < cutoff_date
            )
        ).delete()
        
        return deleted_count