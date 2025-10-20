"""
YAML配置文件管理工具类
提供配置文件的读取、写入、备份和恢复功能
"""
import yaml
import shutil
from pathlib import Path
from typing import Dict, Any, Optional,List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class YAMLConfigManager:
    """YAML配置文件管理器 - 提供安全的读写操作"""
    
    def __init__(self, config_file_path: Path):
        """
        初始化配置管理器
        
        Args:
            config_file_path: YAML配置文件路径
        """
        self.config_file_path = Path(config_file_path)
        self.backup_dir = self.config_file_path.parent / 'backups'
        self.backup_dir.mkdir(exist_ok=True)
        
    def read_config(self) -> Optional[Dict[str, Any]]:
        """
        读取配置文件
        
        Returns:
            Dict: 配置内容字典,如果失败返回None
        """
        try:
            if not self.config_file_path.exists():
                logger.error(f"配置文件不存在: {self.config_file_path}")
                return None
            
            with open(self.config_file_path, 'r', encoding='utf-8') as file:
                config = yaml.safe_load(file)
            
            logger.info(f"成功读取配置文件: {self.config_file_path}")
            return config
            
        except Exception as e:
            logger.error(f"读取配置文件失败: {e}")
            return None
    
    def write_config(self, config: Dict[str, Any], create_backup: bool = True) -> bool:
        """
        写入配置文件
        
        Args:
            config: 配置内容字典
            create_backup: 是否创建备份
            
        Returns:
            bool: 写入是否成功
        """
        try:
            # 创建备份
            if create_backup and self.config_file_path.exists():
                self._create_backup()
            
            # 写入配置
            with open(self.config_file_path, 'w', encoding='utf-8') as file:
                yaml.dump(
                    config,
                    file,
                    allow_unicode=True,
                    default_flow_style=False,
                    sort_keys=False,
                    indent=2
                )
            
            logger.info(f"成功写入配置文件: {self.config_file_path}")
            return True
            
        except Exception as e:
            logger.error(f"写入配置文件失败: {e}")
            return False
    
    def _create_backup(self) -> Optional[Path]:
        """
        创建配置文件备份
        
        Returns:
            Path: 备份文件路径,如果失败返回None
        """
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_filename = f"{self.config_file_path.stem}_backup_{timestamp}.yaml"
            backup_path = self.backup_dir / backup_filename
            
            shutil.copy2(self.config_file_path, backup_path)
            logger.info(f"创建配置备份: {backup_path}")
            
            # 保留最近10个备份
            self._cleanup_old_backups(keep_count=10)
            
            return backup_path
            
        except Exception as e:
            logger.error(f"创建备份失败: {e}")
            return None
    
    def _cleanup_old_backups(self, keep_count: int = 10):
        """清理旧备份文件,只保留最近的N个"""
        try:
            backup_files = sorted(
                self.backup_dir.glob(f"{self.config_file_path.stem}_backup_*.yaml"),
                key=lambda p: p.stat().st_mtime,
                reverse=True
            )
            
            # 删除超出保留数量的备份
            for old_backup in backup_files[keep_count:]:
                old_backup.unlink()
                logger.info(f"删除旧备份: {old_backup}")
                
        except Exception as e:
            logger.error(f"清理旧备份失败: {e}")
    
    def restore_from_backup(self, backup_path: Path) -> bool:
        """
        从备份恢复配置
        
        Args:
            backup_path: 备份文件路径
            
        Returns:
            bool: 恢复是否成功
        """
        try:
            if not backup_path.exists():
                logger.error(f"备份文件不存在: {backup_path}")
                return False
            
            shutil.copy2(backup_path, self.config_file_path)
            logger.info(f"从备份恢复配置: {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"从备份恢复失败: {e}")
            return False
    
    def validate_config_structure(self, config: Dict[str, Any]) -> tuple[bool, str]:
        """
        验证配置文件结构
        
        Args:
            config: 配置内容字典
            
        Returns:
            tuple: (是否有效, 错误信息)
        """
        if not isinstance(config, dict):
            return False, "配置必须是字典类型"
        
        if not config:
            return False, "配置不能为空"
        
        return True, ""


class LLMConfigFileManager(YAMLConfigManager):
    """大模型配置文件管理器 - 专门处理 llm_model_config.yaml"""
    
    def __init__(self):
        """初始化大模型配置管理器"""
        # 获取配置文件路径
        current_dir = Path(__file__).parent
        config_path = current_dir / "yaml" / "llm_model_config.yaml"
        super().__init__(config_path)
    
    def get_provider_configs(self) -> Dict[str, Dict[str, Any]]:
        """
        获取所有提供商的配置
        
        Returns:
            Dict: {provider_name: {model_configs}}
        """
        config = self.read_config()
        if not config:
            return {}
        
        # 排除非提供商配置节点
        exclude_keys = ['defaults', 'metadata']
        providers = {k: v for k, v in config.items() if k not in exclude_keys}
        
        return providers
    
    def get_model_config(self, provider: str, model_key: str) -> Optional[Dict[str, Any]]:
        """
        获取指定模型的配置
        
        Args:
            provider: 提供商名称
            model_key: 模型标识
            
        Returns:
            Dict: 模型配置,如果不存在返回None
        """
        config = self.read_config()
        if not config:
            return None
        
        return config.get(provider, {}).get(model_key)
    
    def add_model_config(self, provider: str, model_key: str, model_config: Dict[str, Any]) -> bool:
        """
        添加新模型配置
        
        Args:
            provider: 提供商名称
            model_key: 模型标识
            model_config: 模型配置内容
            
        Returns:
            bool: 是否添加成功
        """
        config = self.read_config()
        if not config:
            return False
        
        # 检查是否已存在
        if provider in config and model_key in config[provider]:
            logger.warning(f"模型配置已存在: {provider}.{model_key}")
            return False
        
        # 确保提供商节点存在
        if provider not in config:
            config[provider] = {}
        
        # 添加模型配置
        config[provider][model_key] = model_config
        
        return self.write_config(config)
    
    def update_model_config(self, provider: str, model_key: str, model_config: Dict[str, Any]) -> bool:
        """
        更新模型配置
        
        Args:
            provider: 提供商名称
            model_key: 模型标识
            model_config: 新的模型配置内容
            
        Returns:
            bool: 是否更新成功
        """
        config = self.read_config()
        if not config:
            return False
        
        # 检查是否存在
        if provider not in config or model_key not in config[provider]:
            logger.warning(f"模型配置不存在: {provider}.{model_key}")
            return False
        
        # 更新配置
        config[provider][model_key] = model_config
        
        return self.write_config(config)
    
    def delete_model_config(self, provider: str, model_key: str) -> bool:
        """
        删除模型配置
        
        Args:
            provider: 提供商名称
            model_key: 模型标识
            
        Returns:
            bool: 是否删除成功
        """
        config = self.read_config()
        if not config:
            return False
        
        # 检查是否存在
        if provider not in config or model_key not in config[provider]:
            logger.warning(f"模型配置不存在: {provider}.{model_key}")
            return False
        
        # 删除配置
        del config[provider][model_key]
        
        # 如果提供商下没有模型了,也删除提供商节点
        if not config[provider]:
            del config[provider]
        
        return self.write_config(config)
    
    def get_all_models_list(self) -> list[Dict[str, Any]]:
        """
        获取所有模型的列表(扁平化结构)
        
        Returns:
            List: [{provider, model_key, config}, ...]
        """
        providers = self.get_provider_configs()
        models_list = []
        
        for provider_name, models in providers.items():
            if isinstance(models, dict):
                for model_key, model_config in models.items():
                    if isinstance(model_config, dict):
                        models_list.append({
                            'provider': provider_name,
                            'model_key': model_key,
                            'config': model_config
                        })
        
        return models_list
    
    # ✅ 新增方法
    def get_providers_from_config(self) -> List[str]:
        """
        从配置文件中获取已有的 Provider 列表
        
        Returns:
            List[str]: Provider key 列表
        """
        config = self.read_config()
        if not config:
            return []
        
        # 排除非提供商配置节点
        exclude_keys = ['defaults', 'metadata', 'providers']
        providers = [k for k in config.keys() if k not in exclude_keys]
        
        return providers
    
    # ✅ 新增方法
    def ensure_provider_exists(self, provider: str) -> bool:
        """
        确保 Provider 节点存在于配置文件中
        如果不存在则创建空节点
        
        Args:
            provider: Provider 标识
            
        Returns:
            bool: 操作是否成功
        """
        config = self.read_config()
        if not config:
            return False
        
        # 如果 Provider 不存在,创建空节点
        if provider not in config:
            config[provider] = {}
            return self.write_config(config)
        
        return True
    

class SystemPromptConfigFileManager(YAMLConfigManager):
    """系统提示词配置文件管理器 - 专门处理 system_prompt_config.yaml"""
    
    def __init__(self):
        """初始化系统提示词配置管理器"""
        # 获取配置文件路径
        current_dir = Path(__file__).parent
        config_path = current_dir / "yaml" / "system_prompt_config.yaml"
        super().__init__(config_path)
    
    def get_all_prompts(self) -> Dict[str, Dict[str, Any]]:
        """
        获取所有提示词模板配置
        
        Returns:
            Dict: {template_key: {template_config}}
        """
        config = self.read_config()
        if not config:
            return {}
        
        # 获取 prompt_templates 节点
        prompt_templates = config.get('prompt_templates', {})
        
        return prompt_templates
    
    def get_prompt_config(self, template_key: str) -> Optional[Dict[str, Any]]:
        """
        获取指定提示词模板的配置
        
        Args:
            template_key: 模板标识
            
        Returns:
            Dict: 模板配置,如果不存在返回None
        """
        prompts = self.get_all_prompts()
        return prompts.get(template_key)
    
    def add_prompt_config(self, template_key: str, prompt_config: Dict[str, Any]) -> bool:
        """
        添加新提示词模板配置
        
        Args:
            template_key: 模板标识
            prompt_config: 模板配置内容
            
        Returns:
            bool: 是否添加成功
        """
        config = self.read_config()
        if not config:
            return False
        
        # 确保 prompt_templates 节点存在
        if 'prompt_templates' not in config:
            config['prompt_templates'] = {}
        
        # 检查是否已存在
        if template_key in config['prompt_templates']:
            logger.warning(f"提示词模板已存在: {template_key}")
            return False
        
        # 添加模板配置
        config['prompt_templates'][template_key] = prompt_config
        
        return self.write_config(config)
    
    def update_prompt_config(self, template_key: str, prompt_config: Dict[str, Any]) -> bool:
        """
        更新提示词模板配置
        
        Args:
            template_key: 模板标识
            prompt_config: 新的模板配置内容
            
        Returns:
            bool: 是否更新成功
        """
        config = self.read_config()
        if not config:
            return False
        
        # 检查是否存在
        if 'prompt_templates' not in config or template_key not in config['prompt_templates']:
            logger.warning(f"提示词模板不存在: {template_key}")
            return False
        
        # 更新配置
        config['prompt_templates'][template_key] = prompt_config
        
        return self.write_config(config)
    
    def delete_prompt_config(self, template_key: str) -> bool:
        """
        删除提示词模板配置
        
        Args:
            template_key: 模板标识
            
        Returns:
            bool: 是否删除成功
        """
        config = self.read_config()
        if not config:
            return False
        
        # 检查是否存在
        if 'prompt_templates' not in config or template_key not in config['prompt_templates']:
            logger.warning(f"提示词模板不存在: {template_key}")
            return False
        
        # 删除配置
        del config['prompt_templates'][template_key]
        
        return self.write_config(config)
    
    def get_all_prompts_list(self) -> List[Dict[str, Any]]:
        """
        获取所有提示词模板的列表(扁平化结构)
        
        Returns:
            List: [{template_key, config}, ...]
        """
        prompts = self.get_all_prompts()
        prompts_list = []
        
        for template_key, template_config in prompts.items():
            if isinstance(template_config, dict):
                prompts_list.append({
                    'template_key': template_key,
                    'config': template_config
                })
        
        return prompts_list
    
    def get_categories_from_config(self) -> List[str]:
        """
        从配置文件中获取所有已使用的分类
        
        Returns:
            List[str]: 分类列表
        """
        prompts = self.get_all_prompts()
        categories = set()
        
        for template_config in prompts.values():
            if isinstance(template_config, dict):
                category = template_config.get('category', '未分类')
                categories.add(category)
        
        return sorted(list(categories))