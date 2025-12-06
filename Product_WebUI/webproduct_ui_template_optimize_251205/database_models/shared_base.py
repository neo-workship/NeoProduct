# database_models/shared_base.py
from sqlalchemy import Column, Integer, DateTime, String, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, declared_attr
from auth.database import Base

class TimestampMixin:
    """时间戳混入类"""
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class AuditMixin:
    """审计混入类 - 记录操作用户（不强制建立关系）"""
    created_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    updated_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    
    # 不在这里定义关系，让具体的业务模型自己决定是否需要关系
    # 这样可以避免与auth模块的强耦合
    
    def get_creator_info(self):
        """获取创建者信息的辅助方法"""
        if not self.created_by:
            return None
            
        # 动态导入避免循环依赖
        try:
            from auth.database import get_db
            from auth.models import User
            
            with get_db() as db:
                creator = db.query(User).filter(User.id == self.created_by).first()
                if creator:
                    return {
                        'id': creator.id,
                        'username': creator.username,
                        'full_name': creator.full_name
                    }
        except Exception:
            pass
        return None
    
    def get_updater_info(self):
        """获取更新者信息的辅助方法"""
        if not self.updated_by:
            return None
            
        try:
            from auth.database import get_db
            from auth.models import User
            
            with get_db() as db:
                updater = db.query(User).filter(User.id == self.updated_by).first()
                if updater:
                    return {
                        'id': updater.id,
                        'username': updater.username,
                        'full_name': updater.full_name
                    }
        except Exception:
            pass
        return None

class BusinessBaseModel(Base, TimestampMixin, AuditMixin):
    """业务模型基类"""
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)
    is_active = Column(Boolean, default=True)
    description = Column(String(500), nullable=True)
    
    def to_dict(self, include_audit_info=False):
        """转换为字典，便于JSON序列化"""
        result = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        
        # 可选包含审计信息
        if include_audit_info:
            result['creator_info'] = self.get_creator_info()
            result['updater_info'] = self.get_updater_info()
            
        return result
    
    def set_creator(self, user_id):
        """设置创建者"""
        self.created_by = user_id
    
    def set_updater(self, user_id):
        """设置更新者"""
        self.updated_by = user_id