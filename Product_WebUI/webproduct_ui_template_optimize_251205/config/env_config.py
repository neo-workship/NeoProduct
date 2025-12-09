"""
环境变量配置加载器

统一管理从 .env 文件加载环境变量，并提供类型转换和默认值处理。

使用方法:
    from config.env_config import env_config
    
    # 获取字符串配置
    app_title = env_config.get('APP_TITLE', 'Default Title')
    
    # 获取整数配置
    app_port = env_config.get_int('APP_PORT', 8080)
    
    # 获取布尔配置
    app_show = env_config.get_bool('APP_SHOW', True)
    
    # 获取列表配置
    allowed_hosts = env_config.get_list('ALLOWED_HOSTS', ['localhost'])
"""
import os
from pathlib import Path
from typing import Any, Optional, List, Dict
import secrets


class EnvConfig:
    """环境变量配置管理器"""
    
    def __init__(self, env_file: str = '.env'):
        """
        初始化环境变量配置
        
        Args:
            env_file: .env 文件路径（相对于项目根目录）
        """
        self.env_file = env_file
        self.config: Dict[str, str] = {}
        self._load_env_file()
    
    def _get_project_root(self) -> Path:
        """
        获取项目根目录
        
        Returns:
            Path: 项目根目录路径
        """
        # 从当前文件向上查找，直到找到包含 .env 或 requirements.txt 的目录
        current = Path(__file__).resolve().parent
        
        # 向上最多查找5层
        for _ in range(5):
            if (current / '.env').exists() or (current / '.env.example').exists():
                return current
            if (current / 'requirements.txt').exists():
                return current
            if current.parent == current:  # 到达根目录
                break
            current = current.parent
        
        # 如果没找到，返回当前文件的父目录的父目录（假设结构是 project/config/env_config.py）
        return Path(__file__).resolve().parent.parent
    
    def _load_env_file(self):
        """从 .env 文件加载环境变量"""
        project_root = self._get_project_root()
        env_path = project_root / self.env_file
        
        # 如果 .env 不存在，尝试加载 .env.example
        if not env_path.exists():
            env_example_path = project_root / '.env.example'
            if env_example_path.exists():
                print(f"⚠️  .env 文件不存在，使用 .env.example 的默认配置")
                print(f"   建议执行: cp .env.example .env")
                env_path = env_example_path
        
        if not env_path.exists():
            print(f"⚠️  未找到环境变量配置文件: {env_path}")
            print(f"   将使用代码中的默认值")
            return
        
        # 读取并解析 .env 文件
        try:
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    
                    # 跳过空行和注释
                    if not line or line.startswith('#'):
                        continue
                    
                    # 解析 KEY=VALUE 格式
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        
                        # 移除值两端的引号
                        if value.startswith('"') and value.endswith('"'):
                            value = value[1:-1]
                        elif value.startswith("'") and value.endswith("'"):
                            value = value[1:-1]
                        
                        self.config[key] = value
            
            print(f"✅ 已加载环境变量配置: {env_path}")
            print(f"   共加载 {len(self.config)} 个配置项")
        
        except Exception as e:
            print(f"❌ 加载环境变量配置失败: {e}")
    
    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """
        获取字符串配置
        
        优先级: 系统环境变量 > .env 文件 > 默认值
        
        Args:
            key: 配置键名
            default: 默认值
        
        Returns:
            配置值或默认值
        """
        # 1. 优先从系统环境变量获取
        value = os.environ.get(key)
        if value is not None:
            return value
        
        # 2. 从 .env 文件获取
        value = self.config.get(key)
        if value is not None and value != '':
            return value
        
        # 3. 返回默认值
        return default
    
    def get_int(self, key: str, default: int = 0) -> int:
        """
        获取整数配置
        
        Args:
            key: 配置键名
            default: 默认值
        
        Returns:
            整数配置值
        """
        value = self.get(key)
        if value is None:
            return default
        
        try:
            return int(value)
        except ValueError:
            print(f"⚠️  配置 {key}='{value}' 无法转换为整数，使用默认值: {default}")
            return default
    
    def get_float(self, key: str, default: float = 0.0) -> float:
        """
        获取浮点数配置
        
        Args:
            key: 配置键名
            default: 默认值
        
        Returns:
            浮点数配置值
        """
        value = self.get(key)
        if value is None:
            return default
        
        try:
            return float(value)
        except ValueError:
            print(f"⚠️  配置 {key}='{value}' 无法转换为浮点数，使用默认值: {default}")
            return default
    
    def get_bool(self, key: str, default: bool = False) -> bool:
        """
        获取布尔配置
        
        支持的真值: true, yes, 1, on (不区分大小写)
        支持的假值: false, no, 0, off (不区分大小写)
        
        Args:
            key: 配置键名
            default: 默认值
        
        Returns:
            布尔配置值
        """
        value = self.get(key)
        if value is None:
            return default
        
        value_lower = value.lower()
        if value_lower in ('true', 'yes', '1', 'on'):
            return True
        elif value_lower in ('false', 'no', '0', 'off'):
            return False
        else:
            print(f"⚠️  配置 {key}='{value}' 无法转换为布尔值，使用默认值: {default}")
            return default
    
    def get_list(self, key: str, default: Optional[List[str]] = None, 
                 separator: str = ',') -> List[str]:
        """
        获取列表配置
        
        Args:
            key: 配置键名
            default: 默认值
            separator: 分隔符，默认为逗号
        
        Returns:
            列表配置值
        
        示例:
            ALLOWED_HOSTS=localhost,127.0.0.1,example.com
            => ['localhost', '127.0.0.1', 'example.com']
        """
        if default is None:
            default = []
        
        value = self.get(key)
        if value is None:
            return default
        
        # 分割并去除空白
        items = [item.strip() for item in value.split(separator)]
        # 过滤空字符串
        return [item for item in items if item]
    
    def get_dict(self, key: str, default: Optional[Dict[str, str]] = None,
                 item_separator: str = ',', kv_separator: str = ':') -> Dict[str, str]:
        """
        获取字典配置
        
        Args:
            key: 配置键名
            default: 默认值
            item_separator: 项分隔符，默认为逗号
            kv_separator: 键值分隔符，默认为冒号
        
        Returns:
            字典配置值
        
        示例:
            DATABASE_OPTIONS=host:localhost,port:3306,charset:utf8
            => {'host': 'localhost', 'port': '3306', 'charset': 'utf8'}
        """
        if default is None:
            default = {}
        
        value = self.get(key)
        if value is None:
            return default
        
        result = {}
        items = value.split(item_separator)
        
        for item in items:
            item = item.strip()
            if not item:
                continue
            
            if kv_separator in item:
                k, v = item.split(kv_separator, 1)
                result[k.strip()] = v.strip()
        
        return result
    
    def require(self, key: str) -> str:
        """
        获取必需的配置，如果不存在则抛出异常
        
        Args:
            key: 配置键名
        
        Returns:
            配置值
        
        Raises:
            ValueError: 如果配置不存在
        """
        value = self.get(key)
        if value is None:
            raise ValueError(f"必需的环境变量 {key} 未设置")
        return value
    
    def set(self, key: str, value: str):
        """
        设置配置值（仅在内存中，不会写入文件）
        
        Args:
            key: 配置键名
            value: 配置值
        """
        self.config[key] = value
    
    def has(self, key: str) -> bool:
        """
        检查配置是否存在
        
        Args:
            key: 配置键名
        
        Returns:
            是否存在
        """
        return key in os.environ or key in self.config
    
    def all(self) -> Dict[str, str]:
        """
        获取所有配置
        
        Returns:
            所有配置的字典
        """
        # 合并系统环境变量和 .env 配置
        result = self.config.copy()
        result.update(os.environ)
        return result
    
    def get_or_generate_secret(self, key: str, length: int = 32) -> str:
        """
        获取密钥配置，如果不存在则生成一个随机密钥
        
        Args:
            key: 配置键名
            length: 随机密钥长度（字节数）
        
        Returns:
            密钥字符串
        
        注意:
            生成的密钥不会被保存到 .env 文件，每次重启都会生成新的。
            建议在生产环境中设置固定的密钥。
        """
        value = self.get(key)
        if value:
            return value
        
        # 生成随机密钥
        secret = secrets.token_urlsafe(length)
        print(f"⚠️  {key} 未设置，已生成随机密钥（重启后会改变）")
        print(f"   建议在 .env 文件中设置: {key}={secret}")
        return secret

# 全局单例
env_config = EnvConfig()


# ============================================================================
# 便捷的配置访问函数（可选）
# ============================================================================

def get_env(key: str, default: Optional[str] = None) -> Optional[str]:
    """便捷函数：获取字符串配置"""
    return env_config.get(key, default)


def get_env_int(key: str, default: int = 0) -> int:
    """便捷函数：获取整数配置"""
    return env_config.get_int(key, default)


def get_env_bool(key: str, default: bool = False) -> bool:
    """便捷函数：获取布尔配置"""
    return env_config.get_bool(key, default)


def get_env_list(key: str, default: Optional[List[str]] = None, separator: str = ',') -> List[str]:
    """便捷函数：获取列表配置"""
    return env_config.get_list(key, default, separator)


# ============================================================================
# 示例用法
# ============================================================================

if __name__ == '__main__':
    print("=" * 70)
    print("🔧 环境变量配置测试")
    print("=" * 70)
    
    # 测试各种类型的配置读取
    print("\n📝 测试配置读取:")
    print(f"APP_TITLE: {env_config.get('APP_TITLE', 'Default Title')}")
    print(f"APP_PORT: {env_config.get_int('APP_PORT', 8080)}")
    print(f"APP_SHOW: {env_config.get_bool('APP_SHOW', True)}")
    print(f"APP_RELOAD: {env_config.get_bool('APP_RELOAD', True)}")
    print(f"APP_DARK: {env_config.get_bool('APP_DARK', False)}")
    
    print("\n🔐 密钥生成测试:")
    secret = env_config.get_or_generate_secret('APP_STORAGE_SECRET', 32)
    print(f"APP_STORAGE_SECRET: {secret[:10]}... (已截断)")
    
    print("\n📊 所有配置项:")
    all_config = env_config.all()
    app_configs = {k: v for k, v in all_config.items() if k.startswith('APP_') or k.startswith('AUTH_')}
    for key in sorted(app_configs.keys())[:10]:  # 只显示前10个
        value = app_configs[key]
        # 隐藏密钥信息
        if 'SECRET' in key or 'PASSWORD' in key:
            value = '***'
        print(f"  {key}: {value}")
    
    print(f"\n✅ 配置加载完成，共 {len(app_configs)} 个应用配置项")