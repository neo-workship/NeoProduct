import asyncio
import time
from datetime import datetime

# 模拟 OpenAI 同步流式迭代器
class MockStreamIterator:
    def __init__(self, chunks, delay=0.1):
        self.chunks = chunks
        self.delay = delay
        self.index = 0
    
    def __iter__(self):
        return self
    
    def __next__(self):
        if self.index >= len(self.chunks):
            raise StopIteration
        
        # 模拟网络延迟 - 这里会阻塞
        print(f"[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] Blocking for chunk {self.index}")
        time.sleep(self.delay)  # 同步阻塞
        
        chunk = self.chunks[self.index]
        self.index += 1
        print(f"[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] Returning chunk: {chunk}")
        return chunk

def create_mock_stream():
    """模拟 client.chat.completions.create(stream=True) 的返回值"""
    chunks = ["Hello", " ", "world", "!", " ", "This", " ", "is", " ", "streaming", "."]
    return MockStreamIterator(chunks, delay=0.2)

async def test_stream_with_asyncio_to_thread():
    """测试使用 asyncio.to_thread 的方式"""
    print("\n=== 测试方式1: 使用 asyncio.to_thread ===")
    
    start_time = time.time()
    
    # 模拟原代码的做法
    print(f"[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] 开始调用 asyncio.to_thread")
    stream_response = await asyncio.to_thread(create_mock_stream)
    print(f"[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] asyncio.to_thread 完成，耗时: {time.time() - start_time:.2f}s")
    
    # 开始处理流式数据
    print(f"[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] 开始处理流式数据")
    full_content = ""
    chunk_count = 0
    
    loop_start = time.time()
    for chunk in stream_response:
        chunk_count += 1
        full_content += chunk
        chunk_time = time.time()
        print(f"[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] 处理chunk {chunk_count}: '{chunk}', 当前内容: '{full_content}', 循环耗时: {chunk_time - loop_start:.2f}s")
        
        # 模拟UI更新
        await asyncio.sleep(0.01)  # 模拟UI更新的异步操作
        loop_start = chunk_time
    
    total_time = time.time() - start_time
    print(f"\n总耗时: {total_time:.2f}s")
    print(f"最终内容: '{full_content}'")

async def test_stream_direct():
    """测试直接处理的方式（作为对比）"""
    print("\n=== 测试方式2: 直接处理 ===")
    
    start_time = time.time()
    
    print(f"[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] 直接创建流式迭代器")
    stream_response = create_mock_stream()
    
    print(f"[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] 开始处理流式数据")
    full_content = ""
    chunk_count = 0
    
    loop_start = time.time()
    for chunk in stream_response:
        chunk_count += 1
        full_content += chunk
        chunk_time = time.time()
        print(f"[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] 处理chunk {chunk_count}: '{chunk}', 当前内容: '{full_content}', 循环耗时: {chunk_time - loop_start:.2f}s")
        
        # 模拟UI更新
        await asyncio.sleep(0.01)
        loop_start = chunk_time
    
    total_time = time.time() - start_time
    print(f"\n总耗时: {total_time:.2f}s")
    print(f"最终内容: '{full_content}'")

async def main():
    """同时运行两个测试来对比"""
    print("开始流式处理测试...")
    
    # 测试1: 使用 asyncio.to_thread
    await test_stream_with_asyncio_to_thread()
    
    await asyncio.sleep(1)  # 间隔
    
    # 测试2: 直接处理
    await test_stream_direct()
    
    print("\n=== 测试结论 ===")
    print("如果两种方式的时间分布相似，说明都是真流式")
    print("如果方式1在 'asyncio.to_thread 完成' 时就等了很久，说明是假流式")

if __name__ == "__main__":
    asyncio.run(main())