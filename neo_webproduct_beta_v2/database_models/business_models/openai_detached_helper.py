from dataclasses import dataclass
from typing import List, Optional
from database_models.business_models.openai_models import OpenAIConfig
from common.exception_handler import log_info, log_error, safe, db_safe, safe_protect

@dataclass
class DetachedOpenAIConfig:
    """分离的OpenAI配置对象"""
    id: int
    name: str
    model_name: str
    max_tokens: int
    is_public: bool
    creator_name: Optional[str] = None
    total_requests: int = 0
    
    @classmethod
    def from_config(cls, config: OpenAIConfig) -> 'DetachedOpenAIConfig':
        return cls(
            id=config.id,
            name=config.name,
            model_name=config.model_name.value,
            max_tokens=config.max_tokens,
            is_public=config.is_public,
            creator_name=config.creator.username if config.creator else None,
            total_requests=config.total_requests
        )

@safe_protect(name="获取OpenAI API配置", error_msg="获取OpenAI API配置失败")
def get_openai_configs_safe() -> List[DetachedOpenAIConfig]:
    """安全获取OpenAI配置列表"""
    try:
        with db_safe("统计锁定用户") as db:
            configs = db.query(OpenAIConfig).join(OpenAIConfig.creator).all()
            return [DetachedOpenAIConfig.from_config(config) for config in configs]
    except Exception as e:
        log_error("获取OpenAI API配置失败", exception=e)
        print("获取OpenAI API配置失败", exception=e)
        return []