from pydantic import BaseModel, Field
from typing import Dict, Any, Optional,List


# --------------------------创建档案模型--------------------------
class CreateDocumentRequest(BaseModel):
    """创建文档请求模型"""
    enterprise_code: str = Field(..., description="企业代码", max_length=100)
    enterprise_name: str = Field(..., description="企业名称", max_length=200)

class CreateDocumentResponse(BaseModel):
    """创建文档响应模型"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="响应消息")
    document_id: Optional[str] = Field(None, description="文档ID(enterprise_code)")
    documents_count: Optional[int] = Field(None, description="创建的文档数量")

# --------------------------字段更新模型--------------------------
class FieldUpdateDict(BaseModel):
    """字段更新字典模型"""
    value: str = Field(..., description="字段值，不能为空")
    value_pic_url: Optional[str] = Field(None, description="图片URL")
    value_doc_url: Optional[str] = Field(None, description="文档URL") 
    value_video_url: Optional[str] = Field(None, description="视频URL")

class UpdateFieldRequest(BaseModel):
    """更新字段请求模型"""
    enterprise_code: str = Field(..., description="企业代码", max_length=100)
    full_path_code: str = Field(..., description="字段完整路径编码")
    dict_fields: FieldUpdateDict = Field(..., description="要更新的字段值字典")
    
    class Config:
        json_schema_extra = {
            "example": {
                "enterprise_code": "TEST001",
                "full_path_code": "L1_001.L2_001.L3_001.FIELD_001",
                "dict_fields": {
                    "value": "测试值",
                    "value_pic_url": "http://get_pic_TEST001_L1_001.L2_001.L3_001.FIELD_001/pic",
                    "value_doc_url": "http://get_pic_TEST001_L1_001.L2_001.L3_001.FIELD_001/doc",
                    "value_video_url": "http://get_pic_TEST001_L1_001.L2_001.L3_001.FIELD_001/video"
                }
            }
        }

class UpdateFieldResponse(BaseModel):
    """更新字段响应模型"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="响应消息")
    enterprise_code: Optional[str] = Field(None, description="企业代码")
    full_path_code: Optional[str] = Field(None, description="字段路径")
    updated_fields: Optional[List[str]] = Field(None, description="已更新的字段列表")

# --------------------------搜索模型--------------------------
class EnterpriseSearchRequest(BaseModel):
    """企业搜索请求模型"""
    enterprise_text: str = Field(..., description="企业搜索文本", min_length=1, max_length=200)
    limit: Optional[int] = Field(10, description="返回结果数量限制", ge=1, le=100)
    
    class Config:
        json_schema_extra = {
            "example": {
                "enterprise_text": "科技有限公司",
                "limit": 10
            }
        }

class EnterpriseSearchItem(BaseModel):
    """企业搜索结果项模型"""
    enterprise_code: str = Field(..., description="企业代码")
    enterprise_name: str = Field(..., description="企业名称")

class EnterpriseSearchResponse(BaseModel):
    """企业搜索响应模型"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="响应消息")
    total_count: int = Field(..., description="匹配的总数量")
    enterprises: List[EnterpriseSearchItem] = Field(..., description="企业列表")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "搜索完成",
                "total_count": 15,
                "enterprises": [
                    {
                        "enterprise_code": "TECH001",
                        "enterprise_name": "北京科技有限公司"
                    },
                    {
                        "enterprise_code": "TECH002", 
                        "enterprise_name": "上海科技发展有限公司"
                    }
                ]
            }
        }

# --------------------------企业详情--------------------------
class QueryFieldsRequest(BaseModel):
    """查询字段请求模型"""
    enterprise_code: str = Field(..., description="企业代码", max_length=100)
    path_code_param: str = Field(..., description="层级路径代码")
    fields_param: Optional[List[str]] = Field(None, description="字段代码列表，为空时查询路径下所有字段")
    
    class Config:
        json_schema_extra = {
            "example": {
                "enterprise_code": "TEST001",
                "path_code_param": "L1_001.L2_001.L3_001",
                "fields_param": ["FIELD_001", "FIELD_002"]
            }
        }

class FieldDataModel(BaseModel):
    """字段数据模型"""
    field_code: Optional[str] = Field(None, description="字段代码")
    field_name: Optional[str] = Field(None, description="字段名称")
    full_path_code: Optional[str] = Field(None, description="完整路径代码")
    full_path_name: Optional[str] = Field(None, description="完整路径名称")
    path_code: Optional[str] = Field(None, description="路径代码")
    value: Optional[str] = Field(None, description="字段值")
    value_pic_url: Optional[str] = Field(None, description="图片URL")
    value_doc_url: Optional[str] = Field(None, description="文档URL")
    value_video_url: Optional[str] = Field(None, description="视频URL")
    data_url: Optional[str] = Field(None, description="数据来源URL")
    encoding: Optional[str] = Field(None, description="编码格式")
    format: Optional[str] = Field(None, description="数据格式")
    license: Optional[str] = Field(None, description="许可证信息")
    rights: Optional[str] = Field(None, description="权限信息")
    update_frequency: Optional[str] = Field(None, description="更新频率")
    value_dict: Optional[str] = Field(None, description="值字典")

class QueryFieldsResponse(BaseModel):
    """查询字段响应模型"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="响应消息")
    enterprise_code: Optional[str] = Field(None, description="企业代码")
    path_code: Optional[str] = Field(None, description="路径代码")
    total_count: Optional[int] = Field(None, description="匹配的字段总数")
    fields: Optional[List[FieldDataModel]] = Field(None, description="字段数据列表")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "字段查询成功",
                "enterprise_code": "TEST001",
                "path_code": "L1_001.L2_001.L3_001",
                "total_count": 2,
                "fields": [
                    {
                        "field_code": "FIELD_001",
                        "field_name": "企业名称",
                        "full_path_code": "L1_001.L2_001.L3_001.FIELD_001",
                        "full_path_name": "基本信息.企业概况.基础资料.企业名称",
                        "value": "测试企业",
                        "value_pic_url": "",
                        "value_doc_url": "",
                        "value_video_url": "",
                        "data_url": "http://example.com/data",
                        "encoding": "UTF-8",
                        "format": "text/plain",
                        "license": "企业数据使用许可",
                        "rights": "企业内部使用",
                        "update_frequency": "月度更新",
                        "value_dict": "{'值1','值2','值3'}"
                    }
                ]
            }
        }