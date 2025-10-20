"""
SafeOpenAIClientPool - 线程安全的OpenAI客户端连接池

文件路径: \common\safe_openai_client_pool.py

专为NiceGUI应用设计的OpenAI客户端管理器，提供线程安全的客户端创建、缓存和管理功能。

特性：
- 异步锁保证并发安全，避免重复创建客户端
- 智能缓存机制，按模型配置缓存客户端实例
- 自动内存管理，支持LRU缓存清理
- 完善的错误处理和用户友好的提示
- 详细的统计信息和性能监控
- 配置更新时自动刷新客户端
- 支持配置函数和配置字典两种传参方式

设计原则：
1. 线程安全：使用asyncio.Lock()防止并发创建
2. 内存高效：限制缓存大小，自动清理旧客户端
3. 用户友好：提供清晰的错误信息和状态提示
4. 可观测性：详细的日志和统计信息
5. 容错性：优雅处理各种异常情况
6. 兼容性：支持多种配置传递方式
"""

import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, Optional, Set, Any, Union, Callable
from openai import OpenAI


class SafeOpenAIClientPool:
    """
    线程安全的OpenAI客户端连接池
    
    使用场景：
    - NiceGUI应用的聊天功能
    - 多用户并发访问OpenAI API
    - 动态模型切换
    - 配置热更新
    """
    
    def __init__(self, max_clients: int = 20, client_ttl_hours: int = 24):
        """
        初始化客户端池
        
        Args:
            max_clients: 最大缓存的客户端数量，防止内存泄漏
            client_ttl_hours: 客户端生存时间（小时），超时自动清理
        """
        # 客户端缓存
        self._clients: Dict[str, OpenAI] = {}
        self._client_configs: Dict[str, Dict] = {}  # 缓存配置信息，用于验证
        self._creation_times: Dict[str, datetime] = {}  # 记录创建时间
        self._access_times: Dict[str, datetime] = {}  # 记录最后访问时间
        self._access_counts: Dict[str, int] = {}  # 记录访问次数
        
        # 并发控制
        self._lock = asyncio.Lock()  # 异步锁，确保线程安全
        self._creating: Set[str] = set()  # 正在创建的客户端标记
        
        # 配置参数
        self._max_clients = max_clients
        self._client_ttl = timedelta(hours=client_ttl_hours)
        
        # 统计信息
        self._total_requests = 0
        self._cache_hits = 0
        self._cache_misses = 0
        self._creation_count = 0
        self._cleanup_count = 0
        
        print(f"🔧 SafeOpenAIClientPool 已初始化")
        print(f"   最大缓存: {max_clients} 个客户端")
        print(f"   客户端TTL: {client_ttl_hours} 小时")
    
    async def get_client(self, model_key: str, config_getter_func=None) -> Optional[OpenAI]:
        """
        获取指定模型的OpenAI客户端实例
        
        Args:
            model_key: 模型键名 (如 'deepseek-chat', 'moonshot-v1-8k')
            config_getter_func: 配置获取方式，支持：
                              - 函数：function(model_key) -> dict
                              - 字典：直接使用该配置
                              - None：尝试自动导入配置函数
            
        Returns:
            OpenAI客户端实例，失败时返回None
        """
        self._total_requests += 1
        start_time = time.time()
        
        try:
            # 清理过期的客户端
            await self._cleanup_expired_clients()
            
            # 快速路径：缓存命中且有效
            if await self._is_client_valid(model_key):
                self._cache_hits += 1
                self._access_counts[model_key] = self._access_counts.get(model_key, 0) + 1
                self._access_times[model_key] = datetime.now()
                
                elapsed_ms = (time.time() - start_time) * 1000
                print(f"⚡ 缓存命中: {model_key} ({elapsed_ms:.1f}ms)")
                return self._clients[model_key]
            
            # 慢速路径：需要创建新客户端
            self._cache_misses += 1
            return await self._create_client_safe(model_key, config_getter_func, start_time)
            
        except Exception as e:
            elapsed_ms = (time.time() - start_time) * 1000
            error_msg = f"获取OpenAI客户端失败 ({model_key}): {str(e)}"
            print(f"❌ {error_msg} ({elapsed_ms:.1f}ms)")
            return None
    
    async def _is_client_valid(self, model_key: str) -> bool:
        """
        检查缓存的客户端是否仍然有效
        
        Args:
            model_key: 模型键名
            
        Returns:
            客户端是否有效
        """
        if model_key not in self._clients:
            return False
        
        # 检查是否过期
        creation_time = self._creation_times.get(model_key)
        if creation_time and datetime.now() - creation_time > self._client_ttl:
            print(f"⏰ 客户端已过期: {model_key}")
            await self._remove_client(model_key)
            return False
        
        # 简单的有效性检查
        try:
            client = self._clients[model_key]
            return hasattr(client, 'api_key') and hasattr(client, 'base_url')
        except Exception:
            return False
    
    async def _create_client_safe(self, model_key: str, config_getter_func, start_time: float) -> Optional[OpenAI]:
        """
        线程安全的客户端创建方法
        
        Args:
            model_key: 模型键名
            config_getter_func: 配置获取方式
            start_time: 开始时间（用于性能统计）
            
        Returns:
            创建的OpenAI客户端实例
        """
        # 检查是否正在创建，避免重复创建
        if model_key in self._creating:
            print(f"⏳ 等待客户端创建完成: {model_key}")
            
            # 等待其他协程完成创建（最多等待10秒）
            wait_start = time.time()
            while model_key in self._creating and (time.time() - wait_start) < 10:
                await asyncio.sleep(0.01)
            
            # 检查是否创建成功
            if model_key in self._clients:
                elapsed_ms = (time.time() - start_time) * 1000
                print(f"✅ 等待完成，获取客户端: {model_key} ({elapsed_ms:.1f}ms)")
                return self._clients[model_key]
            else:
                print(f"⚠️ 等待客户端创建超时或失败: {model_key}")
                return None
        
        # 获取异步锁，确保只有一个协程创建客户端
        async with self._lock:
            # 双重检查锁定模式
            if model_key in self._clients:
                elapsed_ms = (time.time() - start_time) * 1000
                print(f"🔄 锁内缓存命中: {model_key} ({elapsed_ms:.1f}ms)")
                return self._clients[model_key]
            
            # 标记为正在创建
            self._creating.add(model_key)
            
            try:
                return await self._create_client_internal(model_key, config_getter_func, start_time)
            finally:
                # 无论成功失败，都要清除创建标记
                self._creating.discard(model_key)
    
    async def _create_client_internal(self, model_key: str, config_getter_func, start_time: float) -> Optional[OpenAI]:
        """
        内部客户端创建方法
        
        Args:
            model_key: 模型键名
            config_getter_func: 配置获取方式
            start_time: 开始时间
            
        Returns:
            创建的OpenAI客户端实例
        """
        print(f"🔨 开始创建OpenAI客户端: {model_key}")
        
        try:
            # 获取模型配置
            config = await self._get_model_config(model_key, config_getter_func)
            if not config:
                raise ValueError(f"无法获取模型配置: {model_key}")
            
            # 验证必要的配置项
            api_key = config.get('api_key', '').strip()
            base_url = config.get('base_url', '').strip()
            
            if not api_key:
                raise ValueError(f"模型 {model_key} 缺少有效的 API Key")
            
            if not base_url:
                raise ValueError(f"模型 {model_key} 缺少有效的 Base URL")
            
            # 检查缓存是否已满，如需要则清理
            await self._check_and_cleanup_cache()
            
            # 创建OpenAI客户端实例
            client = OpenAI(
                api_key=api_key,
                base_url=base_url,
                timeout=config.get('timeout', 60),
                max_retries=config.get('max_retries', 3)
            )
            
            # 缓存客户端和相关信息
            current_time = datetime.now()
            self._clients[model_key] = client
            self._client_configs[model_key] = config.copy()
            self._creation_times[model_key] = current_time
            self._access_times[model_key] = current_time
            self._access_counts[model_key] = 1
            self._creation_count += 1
            
            elapsed_ms = (time.time() - start_time) * 1000
            model_name = config.get('name', model_key)
            
            print(f"✅ 客户端创建成功: {model_name} ({elapsed_ms:.1f}ms)")
            print(f"   API Key: {api_key[:12]}...")
            print(f"   Base URL: {base_url}")
            
            return client
            
        except Exception as e:
            error_msg = f"创建OpenAI客户端失败 ({model_key}): {str(e)}"
            print(f"❌ {error_msg}")
            raise
    
    async def _get_model_config(self, model_key: str, config_getter_func) -> Optional[Dict]:
        """
        获取模型配置信息（支持函数和字典两种方式）
        
        Args:
            model_key: 模型键名
            config_getter_func: 外部提供的配置获取方式
            
        Returns:
            模型配置字典
        """
        if config_getter_func:
            if callable(config_getter_func):
                # 使用外部提供的配置获取函数
                try:
                    config = config_getter_func(model_key)
                    if isinstance(config, dict):
                        return config
                    else:
                        print(f"⚠️ 配置获取函数返回了非字典类型: {type(config)}")
                        return None
                except Exception as e:
                    print(f"⚠️ 调用配置获取函数失败: {str(e)}")
                    return None
            elif isinstance(config_getter_func, dict):
                # 直接使用配置字典
                return config_getter_func
            else:
                print(f"⚠️ 不支持的config_getter_func类型: {type(config_getter_func)}")
                return None
        
        # 尝试自动导入配置获取函数
        try:
            # 假设配置函数在某个已知模块中
            # 这里需要根据实际项目结构调整导入路径
            from menu_pages.enterprise_archive.chat_component.config import get_model_config
            return get_model_config(model_key)
        except ImportError:
            print(f"⚠️ 无法自动导入配置获取函数，请提供 config_getter_func 参数")
            return None
    
    async def _check_and_cleanup_cache(self):
        """
        检查缓存大小并在需要时清理最少使用的客户端
        """
        if len(self._clients) >= self._max_clients:
            print(f"🧹 缓存已满 ({len(self._clients)}/{self._max_clients})，开始清理...")
            
            # 找到最少使用的客户端（LRU策略）
            if self._access_times:
                # 按最后访问时间排序，移除最久未使用的
                oldest_model = min(self._access_times.items(), key=lambda x: x[1])[0]
                await self._remove_client(oldest_model)
                self._cleanup_count += 1
                print(f"🗑️ 已清理最久未使用的客户端: {oldest_model}")
    
    async def _cleanup_expired_clients(self):
        """
        清理过期的客户端
        """
        current_time = datetime.now()
        expired_clients = []
        
        for model_key, creation_time in self._creation_times.items():
            if current_time - creation_time > self._client_ttl:
                expired_clients.append(model_key)
        
        for model_key in expired_clients:
            await self._remove_client(model_key)
            self._cleanup_count += 1
            print(f"⏰ 已清理过期客户端: {model_key}")
    
    async def _remove_client(self, model_key: str):
        """
        移除指定的客户端及其相关信息
        
        Args:
            model_key: 要移除的模型键名
        """
        self._clients.pop(model_key, None)
        self._client_configs.pop(model_key, None)
        self._creation_times.pop(model_key, None)
        self._access_times.pop(model_key, None)
        self._access_counts.pop(model_key, None)
    
    async def update_client(self, model_key: str, config_getter_func=None) -> Optional[OpenAI]:
        """
        更新指定模型的客户端（配置变更时使用）
        
        Args:
            model_key: 模型键名
            config_getter_func: 配置获取方式
            
        Returns:
            更新后的客户端实例
        """
        print(f"🔄 更新客户端: {model_key}")
        
        # 移除旧客户端
        await self._remove_client(model_key)
        
        # 创建新客户端
        return await self.get_client(model_key, config_getter_func)
    
    async def clear_cache(self) -> int:
        """
        清空所有缓存的客户端
        
        Returns:
            清理的客户端数量
        """
        async with self._lock:
            cleared_count = len(self._clients)
            
            self._clients.clear()
            self._client_configs.clear()
            self._creation_times.clear()
            self._access_times.clear()
            self._access_counts.clear()
            
            self._cleanup_count += cleared_count
            
            print(f"🧹 已清空所有客户端缓存，共清理 {cleared_count} 个客户端")
            return cleared_count
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取客户端池的统计信息
        
        Returns:
            包含各种统计信息的字典
        """
        cache_hit_rate = (self._cache_hits / self._total_requests * 100) if self._total_requests > 0 else 0.0
        
        return {
            # 基本状态
            'cached_clients': len(self._clients),
            'creating_clients': len(self._creating),
            'max_clients': self._max_clients,
            'models': list(self._clients.keys()),
            
            # 性能统计
            'total_requests': self._total_requests,
            'cache_hits': self._cache_hits,
            'cache_misses': self._cache_misses,
            'cache_hit_rate': f"{cache_hit_rate:.1f}%",
            'creation_count': self._creation_count,
            'cleanup_count': self._cleanup_count,
            
            # 详细信息
            'access_counts': self._access_counts.copy(),
            'creation_times': {
                k: v.strftime('%H:%M:%S') for k, v in self._creation_times.items()
            },
            'access_times': {
                k: v.strftime('%H:%M:%S') for k, v in self._access_times.items()
            }
        }
    
    def print_stats(self):
        """
        打印详细的统计信息到控制台
        """
        stats = self.get_stats()
        
        print(f"\n📊 SafeOpenAIClientPool 统计信息")
        print(f"{'=' * 50}")
        print(f"缓存状态: {stats['cached_clients']}/{stats['max_clients']} 个客户端")
        print(f"正在创建: {stats['creating_clients']} 个")
        print(f"总请求数: {stats['total_requests']}")
        print(f"缓存命中率: {stats['cache_hit_rate']}")
        print(f"创建次数: {stats['creation_count']}")
        print(f"清理次数: {stats['cleanup_count']}")
        
        if stats['models']:
            print(f"\n📱 已缓存的模型:")
            for model in stats['models']:
                access_count = stats['access_counts'].get(model, 0)
                creation_time = stats['creation_times'].get(model, 'Unknown')
                access_time = stats['access_times'].get(model, 'Unknown')
                print(f"  • {model}")
                print(f"    访问次数: {access_count}")
                print(f"    创建时间: {creation_time}")
                print(f"    最后访问: {access_time}")
        else:
            print(f"\n暂无缓存的客户端")
        
        print()
    
    def __repr__(self):
        """返回客户端池的字符串表示"""
        return f"<SafeOpenAIClientPool(clients={len(self._clients)}/{self._max_clients}, hit_rate={self.get_stats()['cache_hit_rate']})>"


# ==================== 全局单例实例 ====================

# 全局客户端池实例（延迟初始化）
_global_client_pool: Optional[SafeOpenAIClientPool] = None

def get_openai_client_pool(max_clients: int = 20, client_ttl_hours: int = 24) -> SafeOpenAIClientPool:
    """
    获取全局OpenAI客户端池实例（单例模式）
    
    Args:
        max_clients: 最大缓存客户端数量（仅在首次调用时生效）
        client_ttl_hours: 客户端生存时间小时数（仅在首次调用时生效）
        
    Returns:
        全局客户端池实例
    """
    global _global_client_pool
    if _global_client_pool is None:
        _global_client_pool = SafeOpenAIClientPool(max_clients, client_ttl_hours)
    return _global_client_pool


# ==================== 便捷函数 ====================

async def get_openai_client(model_key: str, config_getter_func=None) -> Optional[OpenAI]:
    """
    便捷函数：获取OpenAI客户端（重构版本）
    
    Args:
        model_key: 模型键名
        config_getter_func: 配置获取方式，支持：
                          - 函数：function(model_key) -> dict
                          - 字典：直接使用该配置
                          - None：尝试自动导入配置函数
        
    Returns:
        OpenAI客户端实例
    """
    pool = get_openai_client_pool()
    
    # 重构：支持函数和字典两种方式
    if config_getter_func is None:
        # 保持原有逻辑：尝试自动导入
        return await pool.get_client(model_key, None)
    elif callable(config_getter_func):
        # 原有逻辑：传递函数
        return await pool.get_client(model_key, config_getter_func)
    elif isinstance(config_getter_func, dict):
        # 新增逻辑：直接传递配置字典
        def dict_config_getter(key: str) -> dict:
            return config_getter_func
        return await pool.get_client(model_key, dict_config_getter)
    else:
        # 其他类型，转换为字典处理
        print(f"⚠️ 未知的配置类型: {type(config_getter_func)}, 尝试作为字典处理")
        def fallback_config_getter(key: str) -> dict:
            return config_getter_func if isinstance(config_getter_func, dict) else {}
        return await pool.get_client(model_key, fallback_config_getter)

async def clear_openai_cache() -> int:
    """
    便捷函数：清空OpenAI客户端缓存
    
    Returns:
        清理的客户端数量
    """
    pool = get_openai_client_pool()
    return await pool.clear_cache()

def print_openai_stats():
    """
    便捷函数：打印OpenAI客户端池统计信息
    """
    pool = get_openai_client_pool()
    pool.print_stats()


# ==================== 使用示例 ====================

async def example_usage():
    """
    使用示例（展示重构后的多种使用方式）
    """
    print("🚀 SafeOpenAIClientPool 重构版本使用示例")
    print("=" * 60)
    
    # 方式1：使用配置获取函数（原有方式）
    def mock_get_model_config(model_key: str):
        configs = {
            'deepseek-chat': {
                'name': 'DeepSeek Chat',
                'api_key': 'sk-deepseek-test-key',
                'base_url': 'https://api.deepseek.com/v1',
                'timeout': 60
            },
            'moonshot-v1-8k': {
                'name': 'Moonshot 8K',
                'api_key': 'sk-moonshot-test-key',
                'base_url': 'https://api.moonshot.cn/v1',
                'timeout': 60
            }
        }
        return configs.get(model_key)
    
    print("\n📋 方式1：使用配置获取函数")
    client1 = await get_openai_client('deepseek-chat', mock_get_model_config)
    if client1:
        print("✅ 成功获取客户端（配置函数方式）")
    
    # 方式2：直接传递配置字典（新增方式）
    config_dict = {
        'name': 'Claude Chat',
        'api_key': 'sk-claude-test-key',
        'base_url': 'https://api.anthropic.com/v1',
        'timeout': 60
    }
    
    print("\n📋 方式2：直接传递配置字典")
    client2 = await get_openai_client('claude-3-sonnet', config_dict)
    if client2:
        print("✅ 成功获取客户端（配置字典方式）")
    
    # 方式3：自动导入配置函数（保持兼容）
    print("\n📋 方式3：自动导入配置函数")
    client3 = await get_openai_client('gpt-4', None)
    if client3:
        print("✅ 成功获取客户端（自动导入方式）")
    else:
        print("⚠️ 自动导入失败（这是正常的，因为示例环境中没有配置模块）")
    
    # 打印统计信息
    print_openai_stats()
    
    # 测试缓存命中
    print(f"\n🔄 测试缓存命中...")
    start_time = time.time()
    cached_client = await get_openai_client('deepseek-chat', mock_get_model_config)
    elapsed_ms = (time.time() - start_time) * 1000
    print(f"缓存命中耗时: {elapsed_ms:.1f}ms")
    
    # 清理缓存
    print(f"\n🧹 清理缓存...")
    cleared_count = await clear_openai_cache()
    print(f"已清理 {cleared_count} 个客户端")
    
    print_openai_stats()

if __name__ == "__main__":
    # 运行示例
    import asyncio
    asyncio.run(example_usage())