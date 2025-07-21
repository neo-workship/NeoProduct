# database_models/business_utils.py
"""
业务模型工具类 - 提供跨模块的辅助功能
避免直接在业务模型中硬编码对 auth 模块的依赖
"""
from typing import Optional, Dict, Any, List
from contextlib import contextmanager

class UserInfoHelper:
    """用户信息辅助工具"""
    
    @staticmethod
    def get_user_info(user_id: int) -> Optional[Dict[str, Any]]:
        """获取用户基本信息"""
        if not user_id:
            return None
            
        try:
            from auth.database import get_db
            from auth.models import User
            
            with get_db() as db:
                user = db.query(User).filter(User.id == user_id).first()
                if user:
                    return {
                        'id': user.id,
                        'username': user.username,
                        'full_name': user.full_name,
                        'email': user.email,
                        'is_active': user.is_active
                    }
        except Exception:
            pass
        return None
    
    @staticmethod
    def get_users_info(user_ids: List[int]) -> Dict[int, Dict[str, Any]]:
        """批量获取用户信息"""
        if not user_ids:
            return {}
            
        try:
            from auth.database import get_db
            from auth.models import User
            
            with get_db() as db:
                users = db.query(User).filter(User.id.in_(user_ids)).all()
                return {
                    user.id: {
                        'id': user.id,
                        'username': user.username,
                        'full_name': user.full_name,
                        'email': user.email,
                        'is_active': user.is_active
                    }
                    for user in users
                }
        except Exception:
            pass
        return {}

class AuditHelper:
    """审计辅助工具"""
    
    @staticmethod
    def set_audit_fields(obj, user_id: int, is_update: bool = False):
        """设置审计字段"""
        if hasattr(obj, 'created_by') and not is_update:
            obj.created_by = user_id
        if hasattr(obj, 'updated_by'):
            obj.updated_by = user_id
    
    @staticmethod
    def get_audit_info(obj) -> Dict[str, Any]:
        """获取审计信息"""
        result = {}
        
        if hasattr(obj, 'created_by') and obj.created_by:
            result['creator'] = UserInfoHelper.get_user_info(obj.created_by)
        
        if hasattr(obj, 'updated_by') and obj.updated_by:
            result['updater'] = UserInfoHelper.get_user_info(obj.updated_by)
            
        if hasattr(obj, 'created_at'):
            result['created_at'] = obj.created_at
            
        if hasattr(obj, 'updated_at'):
            result['updated_at'] = obj.updated_at
            
        return result

class BusinessQueryHelper:
    """业务查询辅助工具"""
    
    @staticmethod
    @contextmanager
    def get_business_db():
        """获取业务数据库会话"""
        from auth.database import get_db
        with get_db() as db:
            yield db
    
    @staticmethod
    def get_user_business_records(user_id: int, model_class, **filters):
        """获取用户的业务记录"""
        try:
            with BusinessQueryHelper.get_business_db() as db:
                query = db.query(model_class).filter(model_class.created_by == user_id)
                
                # 应用额外过滤条件
                for field, value in filters.items():
                    if hasattr(model_class, field):
                        query = query.filter(getattr(model_class, field) == value)
                
                return query.all()
        except Exception:
            return []
    
    @staticmethod
    def get_active_records(model_class, **filters):
        """获取活跃记录"""
        try:
            with BusinessQueryHelper.get_business_db() as db:
                query = db.query(model_class).filter(model_class.is_active == True)
                
                # 应用额外过滤条件
                for field, value in filters.items():
                    if hasattr(model_class, field):
                        query = query.filter(getattr(model_class, field) == value)
                
                return query.all()
        except Exception:
            return []

class RelationshipHelper:
    """关系辅助工具 - 处理跨模块关系"""
    
    @staticmethod
    def get_related_records(obj, relationship_name: str, related_model_class):
        """获取关联记录"""
        try:
            if hasattr(obj, relationship_name):
                return getattr(obj, relationship_name)
            
            # 如果直接关系不存在，尝试通过外键查询
            foreign_key_field = f"{obj.__class__.__name__.lower()}_id"
            if hasattr(related_model_class, foreign_key_field):
                with BusinessQueryHelper.get_business_db() as db:
                    return db.query(related_model_class).filter(
                        getattr(related_model_class, foreign_key_field) == obj.id
                    ).all()
        except Exception:
            pass
        return []

# 为业务模型提供的便捷装饰器
def with_user_info(func):
    """装饰器：为方法添加用户信息获取功能"""
    def wrapper(self, *args, **kwargs):
        result = func(self, *args, **kwargs)
        if isinstance(result, dict) and hasattr(self, 'created_by'):
            result['user_info'] = UserInfoHelper.get_user_info(self.created_by)
        return result
    return wrapper

def with_audit_info(func):
    """装饰器：为方法添加审计信息"""
    def wrapper(self, *args, **kwargs):
        result = func(self, *args, **kwargs)
        if isinstance(result, dict):
            result['audit_info'] = AuditHelper.get_audit_info(self)
        return result
    return wrapper