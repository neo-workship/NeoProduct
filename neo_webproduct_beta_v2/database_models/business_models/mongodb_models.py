from sqlalchemy import Column, String, Integer, Text, Boolean, JSON, Enum, ForeignKey
from sqlalchemy.orm import relationship, declared_attr
from ..shared_base import BusinessBaseModel
import enum

class MongoDBConfig(BusinessBaseModel):
    """OpenAI配置模型"""
    __tablename__ = 'mongodb_configs'
    