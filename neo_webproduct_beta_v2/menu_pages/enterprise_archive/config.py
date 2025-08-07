"""
LLM模型配置管理器
读取YAML配置文件，为chat_component提供模型选择数据
"""
import yaml
import os
from pathlib import Path
from typing import Dict, List, Any, Optional


class LLMModelConfigManager:
    """LLM模型配置管理器"""
    
    def __init__(self, config_file_path: Optional[str] = None):
        """
        初始化配置管理器
        
        Args:
            config_file_path: YAML配置文件路径，如果为None则使用默认路径
        """
        if config_file_path is None:
            # 默认配置文件路径：项目根目录的 config/yaml/llm_model_config.yaml
            current_dir = Path(__file__).parent
            project_root = current_dir.parent.parent  # 向上两级到项目根目录
            self.config_file_path = project_root / "config" / "yaml" / "llm_model_config.yaml"
        else:
            self.config_file_path = Path(config_file_path)
        
        self._yaml_config = None
        self._model_options = []
        self._load_config()
    
    def _load_config(self) -> None:
        """从YAML文件加载配置"""
        try:
            if not self.config_file_path.exists():
                raise FileNotFoundError(f"LLM模型配置文件不存在: {self.config_file_path}")
            
            with open(self.config_file_path, 'r', encoding='utf-8') as file:
                self._yaml_config = yaml.safe_load(file)
            
            if not self._yaml_config:
                raise ValueError("配置文件为空或格式无效")
            
            # 解析配置并生成模型选项
            self._parse_model_config()
                
        except FileNotFoundError as e:
            print(f"警告: {e}")
            print("将使用默认的硬编码配置")
            self._use_fallback_config()
        except yaml.YAMLError as e:
            print(f"YAML配置文件解析错误: {e}")
            print("将使用默认的硬编码配置")
            self._use_fallback_config()
        except Exception as e:
            print(f"加载配置文件时发生错误: {e}")
            print("将使用默认的硬编码配置")
            self._use_fallback_config()
    
    def _parse_model_config(self) -> None:
        """解析YAML配置，生成模型选项列表"""
        self._model_options = []
        
        # 遍历所有提供商的配置
        for provider_key, provider_config in self._yaml_config.items():
            # 跳过非模型配置节点
            if provider_key in ['defaults', 'metadata']:
                continue
            
            if isinstance(provider_config, dict):
                # 遍历该提供商下的所有模型
                for model_key, model_config in provider_config.items():
                    if isinstance(model_config, dict):
                        # 检查模型是否启用
                        if model_config.get('enabled', True):
                            # 使用model_key作为value，name作为显示标签
                            display_name = model_config.get('name', model_key)
                            description = model_config.get('description', '')
                            
                            # 创建选项字典，key为模型标识符，包含完整配置信息
                            option = {
                                'key': model_key,
                                'label': display_name,
                                'value': model_key,  # ui.select的value
                                'config': model_config,  # 完整的模型配置
                                'provider': provider_key,
                                'description': description
                            }
                            
                            self._model_options.append(option)
    
    def _use_fallback_config(self) -> None:
        """使用回退的硬编码配置"""
        fallback_models = [
            {
                'key': 'deepseek-chat',
                'label': 'DeepSeek Chat',
                'value': 'deepseek-chat',
                'provider': 'deepseek',
                'description': 'DeepSeek Chat 中文优化对话模型',
                'config': {
                    'name': 'DeepSeek Chat',
                    'provider': 'deepseek',
                    'model_name': 'deepseek-chat',
                    'enabled': True,
                    'description': 'DeepSeek Chat 中文优化对话模型'
                }
            },
            {
                'key': 'moonshot-v1-8k',
                'label': 'moonshot-v1-8k',
                'value': 'moonshot-v1-8k',
                'provider': 'moonshot',
                'description': '月之暗面通用大模型',
                'config': {
                    'name': 'moonshot-v1-8k',
                    'provider': 'moonshot',
                    'model_name': 'moonshot-v1-8k',
                    'enabled': True,
                    'description': '月之暗面通用大模型'
                }
            },
            {
                'key': 'qwen-plus',
                'label': '通义千问Plus',
                'value': 'qwen-plus',
                'provider': 'alibaba',
                'description': '阿里通义千问 Plus 中文对话模型',
                'config': {
                    'name': '通义千问Plus',
                    'provider': 'alibaba',
                    'model_name': 'qwen-plus-2025-07-28',
                    'enabled': True,
                    'description': '阿里通义千问 Plus 中文对话模型'
                }
            }
        ]
        
        self._model_options = fallback_models
    
    def get_model_options(self) -> List[Dict[str, Any]]:
        """
        获取模型选项列表，供ui.select使用
        
        Returns:
            List[Dict]: 包含模型选项的字典列表
                每个字典包含: key, label, value, config, provider, description
        """
        return self._model_options.copy()
    
    def get_model_options_for_select(self, include_disabled: bool = False) -> List[str]:
        """
        获取用于ui.select的options列表（仅包含key）
        
        Args:
            include_disabled: 是否包含禁用的模型，默认为False
        
        Returns:
            List[str]: 模型key列表，用作ui.select的options
        """
        if include_disabled:
            return [option['key'] for option in self._model_options]
        else:
            return [option['key'] for option in self._model_options 
                    if option['config'].get('enabled', True)]
    
    def get_model_config(self, model_key: str) -> Optional[Dict[str, Any]]:
        """
        根据模型key获取完整的模型配置
        
        Args:
            model_key: 模型标识符
            
        Returns:
            Dict[str, Any]: 模型的完整配置信息，如果未找到则返回None
        """
        for option in self._model_options:
            if option['key'] == model_key:
                return option['config']
        return None
    
    def get_enabled_models(self) -> List[Dict[str, Any]]:
        """
        获取所有启用的模型
        
        Returns:
            List[Dict]: 启用的模型列表
        """
        return [option for option in self._model_options 
                if option['config'].get('enabled', True)]
    
    def get_models_by_provider(self, provider: str) -> List[Dict[str, Any]]:
        """
        根据提供商获取模型列表
        
        Args:
            provider: 提供商名称
            
        Returns:
            List[Dict]: 指定提供商的模型列表
        """
        return [option for option in self._model_options 
                if option['provider'] == provider]
    
    def get_default_model(self) -> Optional[str]:
        """
        获取默认模型key（第一个启用的模型）
        
        Returns:
            str: 默认模型key，如果没有启用的模型则返回None
        """
        enabled_models = self.get_enabled_models()
        if enabled_models:
            return enabled_models[0]['key']
        return None
    
    def reload_config(self) -> bool:
        """
        重新加载配置文件
        
        Returns:
            bool: 重新加载是否成功
        """
        try:
            old_model_count = len(self._model_options)
            
            # 重新加载配置
            self._yaml_config = None
            self._model_options = []
            self._load_config()
            
            new_model_count = len(self._model_options)
            
            print(f"配置重新加载完成: {old_model_count} -> {new_model_count} 个模型")
            return True
            
        except Exception as e:
            print(f"配置重新加载失败: {e}")
            return False
    
    def get_config_info(self) -> Dict[str, Any]:
        """
        获取配置文件信息
        
        Returns:
            Dict: 配置文件信息
        """
        return {
            'config_file_path': str(self.config_file_path),
            'file_exists': self.config_file_path.exists(),
            'total_models': len(self._model_options),
            'enabled_models': len(self.get_enabled_models()),
            'providers': list(set(option['provider'] for option in self._model_options)),
            'last_modified': self.config_file_path.stat().st_mtime if self.config_file_path.exists() else None
        }


# 全局配置管理器实例
_config_manager = None

def get_llm_config_manager() -> LLMModelConfigManager:
    """
    获取全局LLM配置管理器实例（单例模式）
    
    Returns:
        LLMModelConfigManager: 配置管理器实例
    """
    global _config_manager
    if _config_manager is None:
        _config_manager = LLMModelConfigManager()
    return _config_manager

def get_model_options() -> List[Dict[str, Any]]:
    """
    获取模型选项列表的便捷函数
    
    Returns:
        List[Dict]: 模型选项列表
    """
    return get_llm_config_manager().get_model_options()

def get_model_options_for_select(include_disabled: bool = False) -> List[str]:
    """
    获取用于ui.select的模型选项的便捷函数
    
    Args:
        include_disabled: 是否包含禁用的模型，默认为False
    
    Returns:
        List[str]: 模型key列表
    """
    return get_llm_config_manager().get_model_options_for_select(include_disabled)

def get_model_config(model_key: str) -> Optional[Dict[str, Any]]:
    """
    根据模型key获取配置的便捷函数
    
    Args:
        model_key: 模型标识符
        
    Returns:
        Dict[str, Any]: 模型配置信息
    """
    return get_llm_config_manager().get_model_config(model_key)

def get_default_model() -> Optional[str]:
    """
    获取默认模型key的便捷函数
    
    Returns:
        str: 默认模型key
    """
    return get_llm_config_manager().get_default_model()

def reload_llm_config() -> bool:
    """
    重新加载LLM配置的便捷函数
    
    Returns:
        bool: 重新加载是否成功
    """
    return get_llm_config_manager().reload_config()

def get_config_info() -> Dict[str, Any]:
    """
    获取配置信息的便捷函数
    
    Returns:
        Dict: 配置文件信息
    """
    return get_llm_config_manager().get_config_info()


# 使用示例和测试代码
if __name__ == "__main__":
    # 测试配置管理器
    config_manager = LLMModelConfigManager()
    
    print("=== 模型选项列表（仅启用）===")
    options = config_manager.get_enabled_models()
    for option in options:
        print(f"Key: {option['key']}")
        print(f"Label: {option['label']}")
        print(f"Provider: {option['provider']}")
        print(f"Description: {option['description']}")
        print(f"Enabled: {option['config'].get('enabled', True)}")
        print("-" * 40)
    
    print("\n=== 所有模型选项列表（包含禁用）===")
    all_options = config_manager.get_model_options()
    for option in all_options:
        enabled_status = "✅ 启用" if option['config'].get('enabled', True) else "❌ 禁用"
        print(f"Key: {option['key']} - {enabled_status}")
        print(f"Label: {option['label']}")
        print(f"Provider: {option['provider']}")
        print(f"Description: {option['description']}")
        print("-" * 40)
    
    print(f"\n=== ui.select 选项（仅启用）===")
    select_options = config_manager.get_model_options_for_select(include_disabled=False)
    print(f"启用的模型: {select_options}")
    
    print(f"\n=== ui.select 选项（包含禁用）===")
    select_options_all = config_manager.get_model_options_for_select(include_disabled=True)
    print(f"所有模型: {select_options_all}")
    
    print(f"\n=== 默认模型 ===")
    default_model = config_manager.get_default_model()
    print(f"Default Model: {default_model}")
    
    if default_model:
        print(f"\n=== 获取默认模型配置 ===")
        config = config_manager.get_model_config(default_model)
        print(f"Config: {config}")
    
    print(f"\n=== 本地模型检查 ===")
    local_models = config_manager.get_models_by_provider('ollama')
    if local_models:
        print(f"找到 {len(local_models)} 个本地模型:")
        for model in local_models:
            enabled_status = "✅ 启用" if model['config'].get('enabled', True) else "❌ 禁用"
            print(f"  - {model['key']}: {model['label']} ({enabled_status})")
    else:
        print("未找到本地模型")