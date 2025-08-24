from pydantic import BaseModel, Field
from typing import Dict, Any, Optional,List,Union

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

# --------------------------查询企业信息--------------------------
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

# --------------------------编辑企业信息--------------------------
class EditFieldValueRequest(BaseModel):
    """批量编辑字段值请求模型"""
    enterprise_code: str = Field(..., description="企业代码", max_length=100)
    path_code_param: str = Field(..., description="层级路径代码")
    dict_fields: List[Dict[str, Any]] = Field(..., description="字段更新字典列表")
    
    class Config:
        json_schema_extra = {
            "example": {
                "enterprise_code": "TEST001",
                "path_code_param": "L1_001.L2_001.L3_001",
                "dict_fields": [
                    {
                        "field_code": "FIELD_001",
                        "value": "更新的值1",
                        "value_pic_url": "http://example.com/pic1.jpg"
                    },
                    {
                        "field_code": "FIELD_002",
                        "value": "更新的值2",
                        "encoding": "UTF-8"
                    }
                ]
            }
        }

class EditFieldValueResponse(BaseModel):
    """批量编辑字段值响应模型"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="响应消息")
    enterprise_code: Optional[str] = Field(None, description="企业代码")
    path_code: Optional[str] = Field(None, description="路径代码")
    total_processed: Optional[int] = Field(None, description="处理的字段总数")
    updated_count: Optional[int] = Field(None, description="实际更新的字段数量")
    updated_fields: Optional[List[str]] = Field(None, description="已更新的字段代码列表")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "字段批量更新成功",
                "enterprise_code": "TEST001",
                "path_code": "L1_001.L2_001.L3_001",
                "total_processed": 2,
                "updated_count": 2,
                "updated_fields": ["FIELD_001", "FIELD_002"]
            }
        }

# --------------------------批量删除模型--------------------------
class DeleteManyDocumentsRequest(BaseModel):
    """批量删除文档请求模型"""
    filter_query: Dict[str, Any] = Field(..., description="删除条件查询字典")
    confirm_delete: bool = Field(False, description="确认删除标志，防止误操作")
    
    class Config:
        json_schema_extra = {
            "example": {
                "filter_query": {
                    "enterprise_code": {"$in": ["COMPANY001", "COMPANY002"]},
                    "created_at": {"$lt": "2024-01-01T00:00:00"}
                },
                "confirm_delete": True
            }
        }

class DeleteManyDocumentsResponse(BaseModel):
    """批量删除文档响应模型"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="响应消息")
    deleted_count: int = Field(..., description="实际删除的文档数量")
    filter_query: Optional[Dict[str, Any]] = Field(None, description="删除条件查询字典")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "成功删除 2 个文档",
                "deleted_count": 2,
                "filter_query": {
                    "enterprise_code": {"$in": ["COMPANY001", "COMPANY002"]}
                }
            }
        }

# --------------------------执行原生MongoDB查询模型--------------------------
# 保持原有的 ExecuteMongoQueryRequest 不变
class ExecuteMongoQueryRequest(BaseModel):
    """执行MongoDB原生查询请求模型"""
    query_cmd: str = Field(..., description="原始MongoDB查询语句", min_length=1)
    
    class Config:
        json_schema_extra = {
            "example": {
                "query_cmd": "db.collection.find({\"enterprise_code\": \"TEST001\"})"
            }
        }

# --------------------------分组操作结果模型--------------------------
class GroupResultSingleField(BaseModel):
    """单字段分组结果模型"""
    group_id: Union[str, int, float, None] = Field(..., alias="_id", description="分组字段值")
    
    class Config:
        # 允许额外字段（用于存储聚合结果，如 count、sum、avg 等）
        extra = "allow"
        # 允许通过别名填充字段
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "技术部",
                "count": 45,
                "总金额": 1250000,
                "平均年龄": 28.5
            }
        }

class GroupResultMultiField(BaseModel):
    """多字段分组结果模型"""
    group_id: Dict[str, Union[str, int, float, None]] = Field(..., alias="_id", description="分组字段组合")
    
    class Config:
        # 允许额外字段（用于存储聚合结果）
        extra = "allow"
        # 允许通过别名填充字段
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": {
                    "dept": "技术部",
                    "city": "北京"
                },
                "count": 20,
                "求和薪资": 800000
            }
        }

class GroupResultItem(BaseModel):
    """分组结果项 - 通用模型"""
    group_id: Union[str, int, float, None, Dict[str, Any]] = Field(..., alias="_id", description="分组标识")
    
    class Config:
        # 允许额外字段
        extra = "allow"
        # 允许通过别名填充字段
        populate_by_name = True
        json_schema_extra = {
            "examples": [
                {
                    "_id": "技术部",
                    "count": 45,
                    "求和": 1250000
                },
                {
                    "_id": {
                        "dept": "技术部", 
                        "city": "北京"
                    },
                    "count": 20,
                    "平均值": 28.5
                }
            ]
        }

# 完全重写 ExecuteMongoQueryResponse 以匹配新格式
class ExecuteMongoQueryResponse(BaseModel):
    """执行MongoDB原生查询响应模型 - 新格式（支持分组和字段策略）"""
    type: str = Field(..., description="查询类型：'汇总'、'明细' 或 '分组'")
    period: str = Field(..., description="执行时间ms")
    messages: str = Field(..., description="处理信息：如果发生异常，则为异常内容；否则值就是 正常处理")
    result_data: List[Any] = Field(..., description="结果数据列表")
    structure_type: str = Field(default="")
    field_strategy: str = Field(default="")
    
    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "type": "明细",
                    "period": "125.67ms",
                    "messages": "正常处理",
                    "result_data": [
                        {
                            "enterprise_code": "TEST001",
                            "enterprise_name": "测试企业",
                            "field_code": "FIELD_001",
                            "field_name": "企业名称",
                            "value": "测试数据"
                        }
                    ],
                    "field_strategy": "full_fields"
                },
                {
                    "type": "分组",
                    "period": "89.23ms", 
                    "messages": "正常处理",
                    "result_data": [
                        {
                            "_id": "技术部",
                            "count": 45,
                            "求和薪资": 1250000
                        },
                        {
                            "_id": "销售部", 
                            "count": 30,
                            "平均值年龄": 32.5
                        }
                    ],
                    "field_strategy": "existing_fields"
                },
                {
                    "type": "汇总",
                    "period": "45.12ms",
                    "messages": "正常处理", 
                    "result_data": [156],
                    "field_strategy": ""
                }
            ]
        }