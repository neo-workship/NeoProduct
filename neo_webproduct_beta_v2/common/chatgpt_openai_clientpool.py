import threading
from openai import OpenAI


class OpenAIClientPool:
    """线程安全的 OpenAI Client 连接池，按 (api_key, base_url) 缓存并复用"""

    def __init__(self, timeout=60, max_retries=3):
        self._clients = {}  # {(api_key, base_url): OpenAI 实例}
        self._lock = threading.Lock()
        self._timeout = timeout
        self._max_retries = max_retries

    def get_client(self, api_key, base_url="https://api.openai.com/v1"):
        """获取或创建一个 OpenAI client（线程安全）"""
        key = (api_key, base_url)
        with self._lock:
            if key not in self._clients:
                client = OpenAI(
                    api_key=api_key,
                    base_url=base_url,
                    timeout=self._timeout,
                    max_retries=self._max_retries
                )
                self._clients[key] = client
            return self._clients[key]

    def close_all(self):
        """关闭池中所有客户端（释放 httpx 会话）"""
        with self._lock:
            for client in self._clients.values():
                try:
                    client.close()  # httpx.Client 的 close
                except Exception:
                    pass
            self._clients.clear()


# ===== 使用示例 =====
if __name__ == "__main__":
    pool = OpenAIClientPool(timeout=60, max_retries=3)

    # 用户 A
    client_a = pool.get_client("KEY_A", "https://api.openai.com/v1")

    # 用户 B（不同 key）
    client_b = pool.get_client("KEY_B", "https://api.openai.com/v1")

    # 用户 C（同 key，同 base_url，会复用 client_a）
    client_c = pool.get_client("KEY_A", "https://api.openai.com/v1")

    print(client_a is client_c)  # True，说明复用成功

    # 调用 API
    resp = client_a.models.list()
    print(resp)

    # 程序退出前清理（可选）
    pool.close_all()
