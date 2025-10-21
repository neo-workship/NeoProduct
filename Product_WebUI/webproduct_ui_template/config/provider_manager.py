"""
Provider 管理器
管理可用的模型提供商配置
"""
from typing import List, Dict, Any
from dataclasses import dataclass


@dataclass
class ProviderInfo:
    """Provider 信息数据类"""
    key: str                    # Provider 标识 (例如: deepseek)
    display_name: str           # 显示名称 (例如: DeepSeek)
    description: str            # 描述
    default_base_url: str       # 默认 API 地址
    icon: str                   # 图标名称
    enabled: bool = True        # 是否启用

class ProviderManager:
    """Provider 管理器 - 管理可用的模型提供商"""
    
    # 预定义的 Provider 列表
    BUILTIN_PROVIDERS = [
        ProviderInfo(
            key='deepseek',
            display_name='DeepSeek',
            description='DeepSeek AI 大模型服务 - 提供高性价比的推理和对话能力',
            default_base_url='https://api.deepseek.com',
            icon='smart_toy'
        ),
        ProviderInfo(
            key='alibaba',
            display_name='阿里云',
            description='阿里云通义千问大模型 - 企业级AI服务',
            default_base_url='https://dashscope.aliyuncs.com/api/v1',
            icon='cloud'
        ),
        ProviderInfo(
            key='moonshot',
            display_name='月之暗面',
            description='月之暗面 Kimi 大模型 - 超长上下文对话',
            default_base_url='https://api.moonshot.cn/v1',
            icon='nightlight'
        ),
        ProviderInfo(
            key='ollama',
            display_name='Ollama',
            description='本地部署的开源模型 - 支持 Llama, Mistral 等',
            default_base_url='http://localhost:11434',
            icon='computer'
        ),
        ProviderInfo(
            key='openai',
            display_name='OpenAI',
            description='OpenAI GPT 系列模型 - 业界领先的大语言模型',
            default_base_url='https://api.openai.com/v1',
            icon='auto_awesome'
        ),
        ProviderInfo(
            key='doubao',
            display_name='豆包',
            description='豆包 系列模型 - 安全可靠的AI助手',
            default_base_url='https://ark.cn-beijing.volces.com/api/v3',
            icon='psychology'
        ),
        ProviderInfo(
            key='zhipu',
            display_name='智谱AI',
            description='智谱 GLM 系列模型 - 国产大模型',
            default_base_url='https://open.bigmodel.cn/api/paas/v4/',
            icon='lightbulb'
        ),
        ProviderInfo(
            key='baidu',
            display_name='百度',
            description='百度文心一言大模型',
            default_base_url='https://aip.baidubce.com',
            icon='search'
        ),
    ]
    
    def __init__(self):
        """初始化 Provider 管理器"""
        self.custom_providers: List[ProviderInfo] = []
    
    def get_all_providers(self) -> List[ProviderInfo]:
        """
        获取所有可用的 Provider (内置 + 自定义)
        
        Returns:
            List[ProviderInfo]: Provider 信息列表
        """
        return self.BUILTIN_PROVIDERS + self.custom_providers
    
    def get_provider_keys(self) -> List[str]:
        """
        获取所有 Provider 的 key 列表
        
        Returns:
            List[str]: Provider key 列表
        """
        return [p.key for p in self.get_all_providers()]
    
    def get_provider_options_for_select(self) -> List[Dict[str, str]]:
        """
        获取用于 ui.select 的 Provider 选项列表
        
        Returns:
            List[Dict]: [{'label': '显示名称', 'value': 'key'}, ...]
        """
        return [
            {
                'label': f"{p.display_name} ({p.key})",
                'value': p.key
            }
            for p in self.get_all_providers()
            if p.enabled
        ]
    
    def get_provider_info(self, provider_key: str) -> ProviderInfo | None:
        """
        根据 key 获取 Provider 信息
        
        Args:
            provider_key: Provider 标识
            
        Returns:
            ProviderInfo: Provider 信息,如果不存在返回 None
        """
        for provider in self.get_all_providers():
            if provider.key == provider_key:
                return provider
        return None
    
    def add_custom_provider(self, provider_info: ProviderInfo) -> bool:
        """
        添加自定义 Provider
        
        Args:
            provider_info: Provider 信息
            
        Returns:
            bool: 是否添加成功
        """
        # 检查是否已存在
        if provider_info.key in self.get_provider_keys():
            return False
        
        self.custom_providers.append(provider_info)
        return True
    
    def get_provider_display_name(self, provider_key: str) -> str:
        """
        获取 Provider 的显示名称
        
        Args:
            provider_key: Provider 标识
            
        Returns:
            str: 显示名称
        """
        info = self.get_provider_info(provider_key)
        return info.display_name if info else provider_key

# 全局 Provider 管理器实例
_provider_manager = None

def get_provider_manager() -> ProviderManager:
    """
    获取全局 Provider 管理器实例 (单例模式)
    
    Returns:
        ProviderManager: Provider 管理器实例
    """
    global _provider_manager
    if _provider_manager is None:
        _provider_manager = ProviderManager()
    return _provider_manager