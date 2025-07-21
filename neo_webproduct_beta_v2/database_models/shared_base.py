# database_models/shared_base.py
from sqlalchemy import Column, Integer, DateTime, String, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from auth.database import Base

class TimestampMixin:
    """时间戳混入类"""
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class AuditMixin:
    """审计混入类 - 记录操作用户"""
    created_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    updated_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    
    # 关系定义（使用字符串避免循环导入）
    creator = relationship("User", foreign_keys=[created_by], back_populates=None)
    updater = relationship("User", foreign_keys=[updated_by], back_populates=None)

class BusinessBaseModel(Base, TimestampMixin, AuditMixin):
    """业务模型基类"""
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)
    is_active = Column(Boolean, default=True)
    description = Column(String(500), nullable=True)
    
    def to_dict(self):
        """转换为字典，便于JSON序列化"""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}