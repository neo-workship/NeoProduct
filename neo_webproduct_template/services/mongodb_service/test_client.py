# services/mongodb_service/test_client.py
"""
MongoDB服务测试客户端
用于测试API接口功能
"""

import asyncio
import aiohttp
import json
from typing import Dict, Any

class MongoDBServiceClient:
    """MongoDB服务测试客户端"""
    
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        
    async def test_health(self) -> Dict[str, Any]:
        """测试健康检查接口"""
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(f"{self.base_url}/health") as response:
                    return {
                        "status_code": response.status,
                        "data": await response.json()
                    }
            except Exception as e:
                return {"error": str(e)}
    
    async def test_create_document(self, enterprise_code: str, enterprise_name: str) -> Dict[str, Any]:
        """测试创建文档接口"""
        data = {
            "enterprise_code": enterprise_code,
            "enterprise_name": enterprise_name
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    f"{self.base_url}/api/v1/documents",
                    json=data,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    return {
                        "status_code": response.status,
                        "data": await response.json()
                    }
            except Exception as e:
                return {"error": str(e)}
    
    async def test_root(self) -> Dict[str, Any]:
        """测试根路径接口"""
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(f"{self.base_url}/") as response:
                    return {
                        "status_code": response.status,
                        "data": await response.json()
                    }
            except Exception as e:
                return {"error": str(e)}

async def run_tests():
    """运行所有测试"""
    client = MongoDBServiceClient()
    
    print("=" * 60)
    print("MongoDB Service API 测试")
    print("=" * 60)
    
    # 测试1: 服务状态
    print("\n1. 测试服务状态...")
    result = await client.test_root()
    print(f"响应状态: {result.get('status_code', 'Error')}")
    print(f"响应数据: {json.dumps(result.get('data', result), indent=2, ensure_ascii=False)}")
    
    # 测试2: 健康检查
    print("\n2. 测试健康检查...")
    result = await client.test_health()
    print(f"响应状态: {result.get('status_code', 'Error')}")
    print(f"响应数据: {json.dumps(result.get('data', result), indent=2, ensure_ascii=False)}")
    
    # 测试3: 创建文档
    print("\n3. 测试创建企业档案文档...")
    test_cases = [
        {"enterprise_code": "TEST001", "enterprise_name": "测试企业有限公司"},
        {"enterprise_code": "DEMO002", "enterprise_name": "演示科技股份有限公司"},
        {"enterprise_code": "SAMPLE003", "enterprise_name": "样例建筑工程有限公司"}
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n  测试用例 {i}: {test_case['enterprise_name']}")
        result = await client.test_create_document(
            test_case["enterprise_code"], 
            test_case["enterprise_name"]
        )
        print(f"  响应状态: {result.get('status_code', 'Error')}")
        print(f"  响应数据: {json.dumps(result.get('data', result), indent=2, ensure_ascii=False)}")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == "__main__":
    print("启动MongoDB服务API测试...")
    print("请确保MongoDB服务已启动 (python main.py)")
    
    try:
        asyncio.run(run_tests())
    except KeyboardInterrupt:
        print("\n测试被用户中断")
    except Exception as e:
        print(f"\n测试过程中出现异常: {e}")
        import traceback
        traceback.print_exc()