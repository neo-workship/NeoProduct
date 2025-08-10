"""
LLM模型配置管理器
读取YAML配置文件，为chat_component提供模型选择数据
"""
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional

# LLMModelConfigManager类读取配置文件llm_model_config.yaml
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
                
        except Exception as e:
            print(f"错误: 无法加载LLM配置文件: {e}")
            print("请确保配置文件存在且格式正确")
            self._yaml_config = None
            self._model_options = []
    
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
                            option = {
                                'key': model_key,
                                'label': model_config.get('name', model_key),
                                'value': model_key,
                                'config': model_config,
                                'provider': provider_key,
                                'description': model_config.get('description', '')
                            }
                            self._model_options.append(option)
    
    def get_model_options_for_select(self, include_disabled: bool = False) -> List[str]:
        """
        获取用于ui.select的模型选项
        
        Args:
            include_disabled: 是否包含禁用的模型，默认为False
        
        Returns:
            List[str]: 模型key列表
        """
        if include_disabled:
            return [option['key'] for option in self._model_options]
        return [option['key'] for option in self._model_options 
                if option['config'].get('enabled', True)]

    def get_model_config(self, model_key: str) -> Optional[Dict[str, Any]]:
        """
        根据模型key获取配置
        
        Args:
            model_key: 模型标识符
            
        Returns:
            Dict[str, Any]: 模型的完整配置信息，如果未找到则返回None
        """
        for option in self._model_options:
            if option['key'] == model_key:
                return option['config']
        return None
    
    def get_default_model(self) -> Optional[str]:
        """
        获取默认模型key（第一个启用的模型）
        
        Returns:
            str: 默认模型key，如果没有启用的模型则返回None
        """
        enabled_models = [opt for opt in self._model_options 
                         if opt['config'].get('enabled', True)]
        return enabled_models[0]['key'] if enabled_models else None
    
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
            'enabled_models': len([opt for opt in self._model_options 
                                 if opt['config'].get('enabled', True)]),
            'providers': list(set(option['provider'] for option in self._model_options)),
            'last_modified': self.config_file_path.stat().st_mtime if self.config_file_path.exists() else None
        }

# LLMModelConfigManager 全局配置管理器实例
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

def get_model_config_info() -> Dict[str, Any]:
    """
    获取配置信息的便捷函数
    
    Returns:
        Dict: 配置文件信息
    """
    return get_llm_config_manager().get_config_info()

# SystemPromptConfigManager类读取配置文件llm_model_config.yaml
class SystemPromptConfigManager:
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
            self.config_file_path = project_root / "config" / "yaml" / "system_prompt_config.yaml"
        else:
            self.config_file_path = Path(config_file_path)
        
        self._yaml_config = None
        self._model_options = []
        self._load_config()

    def _load_config(self) -> None:
        pass