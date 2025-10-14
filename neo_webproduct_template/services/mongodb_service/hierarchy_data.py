import json
from typing import Dict, Any, List, Optional
from pathlib import Path
from pydantic import BaseModel, Field

from flat_enterprise_archive_generator_v2 import FlatEnterpriseArchiveGenerator
from mongo_exception_handler import log_info, log_error

class HierarchyResponse(BaseModel):
    """层级结构响应模型"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="响应消息")
    data: Optional[Dict[str, Any]] = Field(default=None, description="层级结构数据")
    
class HierarchyData:
    """精简版层级结构服务类 - 专为前端级联查询设计"""
    
    def __init__(self, json_file_path: str = "./hierarchy_structure.json", 
                 excel_file_path: str = "./一企一档数据项.xlsx"):
        """
        初始化层级结构服务
        Args:
            json_file_path: JSON文件路径
            excel_file_path: Excel文件路径
        """
        self.json_file_path = json_file_path
        self.excel_file_path = excel_file_path
        self.generator = FlatEnterpriseArchiveGenerator()
    
    def _ensure_json_exists(self) -> bool:
        """
        确保JSON文件存在，如果不存在则从Excel生成
        Returns:
            bool: 文件是否存在或生成成功
        """
        json_path = Path(self.json_file_path)
        
        if not json_path.exists():
            log_info("hierarchy_structure.json文件不存在，尝试从Excel生成")
            
            excel_path = Path(self.excel_file_path)
            if not excel_path.exists():
                log_error(f"Excel文件不存在: {self.excel_file_path}")
                return False
            
            try:
                self.generator.generate_hierarchy_structure_json(
                    self.excel_file_path, 
                    self.json_file_path
                )
                log_info(f"成功生成层级结构JSON文件: {self.json_file_path}")
                return True
            except Exception as e:
                log_error("生成层级结构JSON文件失败", exception=e)
                return False
        
        return True
    
    def get_hierarchy_data(self) -> HierarchyResponse:
        """
        获取完整的层级结构数据（供前端一次性获取）
        Returns:
            HierarchyResponse: 包含完整层级数据的响应
        """
        try:
            # 确保JSON文件存在
            if not self._ensure_json_exists():
                return HierarchyResponse(
                    success=False,
                    message="无法生成或读取层级结构数据文件"
                )
            
            # 读取JSON文件
            with open(self.json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            log_info(f"成功读取层级结构文件: {self.json_file_path}")
            
            # 返回原始数据结构，供前端直接使用
            return HierarchyResponse(
                success=True,
                message="获取层级结构数据成功",
                data=data
            )
            
        except json.JSONDecodeError as e:
            log_error("JSON文件格式错误", exception=e, 
                     extra_data=f'{{"file_path": "{self.json_file_path}"}}')
            return HierarchyResponse(
                success=False,
                message="层级结构数据文件格式错误"
            )
        except Exception as e:
            log_error("读取层级结构文件失败", exception=e,
                     extra_data=f'{{"file_path": "{self.json_file_path}"}}')
            return HierarchyResponse(
                success=False,
                message=f"读取层级结构数据失败: {str(e)}"
            )

# 创建全局服务实例
hierarchy_data = HierarchyData()