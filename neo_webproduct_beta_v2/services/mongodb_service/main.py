# services/mongodb_service/main.py
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional,List
import sys
import os
from contextlib import asynccontextmanager # 导入 asynccontextmanager

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from services.mongodb_service.config import get_connection_string, get_config
from services.mongodb_service.mongodb_manager import MongoDBManager
from services.mongodb_service.flat_enterprise_archive_generator_v2 import generate_doc
from services.mongodb_service.hierarchy_data import hierarchy_data
# from common.exception_handler import log_info, log_error, safe
from mongo_exception_handler import log_info, log_error, safe

# 全局MongoDB管理器实例
mongodb_manager: Optional[MongoDBManager] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI 应用程序的生命周期事件处理器。
    在应用程序启动时初始化 MongoDB 连接，在应用程序关闭时断开连接。
    """
    global mongodb_manager
    try:
        # 使用local配置初始化MongoDB管理器
        connection_string = get_connection_string("local")
        config = get_config("local")
        collection_name = config.get_collection_name()
        
        mongodb_manager = MongoDBManager(connection_string, collection_name)
        await mongodb_manager.connect()
        
        log_info("MongoDB 服务启动成功", extra_data=f'{{"collection": "{collection_name}"}}')
        yield # 在这里应用程序开始处理请求
    except Exception as e:
        log_error("MongoDB 服务启动失败", exception=e)
        raise
    finally:
        # 应用程序关闭时断开MongoDB连接
        if mongodb_manager:
            await mongodb_manager.disconnect()
            log_info("MongoDB 服务已关闭")

app = FastAPI(
    title="MongoDB Service API",
    description="企业档案MongoDB数据服务",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan # 将 lifespan 函数传递给 FastAPI 实例
)

def get_mongodb_manager() -> MongoDBManager:
    """依赖注入：获取MongoDB管理器实例"""
    if mongodb_manager is None:
        raise HTTPException(status_code=500, detail="MongoDB 服务未初始化")
    return mongodb_manager

# ==================== 数据模型 ====================
# 创建档案模型
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

# 字段更新模型
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

# ==================== API路由 ====================

@app.get("/", summary="服务状态")
async def root():
    """获取服务状态"""
    return {
        "service": "MongoDB Service",
        "status": "running",
        "version": "1.0.0"
    }

@app.get("/health", summary="健康检查")
async def health_check(manager: MongoDBManager = Depends(get_mongodb_manager)):
    """检查服务和数据库连接健康状态"""
    try:
        # 检查数据库连接
        is_connected = await manager.ping()
        
        return {
            "status": "healthy" if is_connected else "unhealthy",
            "database_connected": is_connected,
            "collection": manager.collection_name
        }
    except Exception as e:
        log_error("健康检查失败", exception=e)
        raise HTTPException(status_code=500, detail="健康检查失败")

@app.post("/api/v1/documents", 
          response_model=CreateDocumentResponse, 
          summary="创建MongoDB文档")
async def create_document(
    request: CreateDocumentRequest,
    manager: MongoDBManager = Depends(get_mongodb_manager)
) -> CreateDocumentResponse:
    """
    创建企业档案MongoDB文档
    
    - **enterprise_code**: 企业代码，将作为文档的_id
    - **enterprise_name**: 企业名称
    
    该API会调用flat_enterprise_archive_generator_v2.generate_doc()函数生成文档数据，
    然后将数据插入到配置的collection中。
    """
    try:
        log_info(f"开始创建企业档案文档", 
                 extra_data=f'{{"enterprise_code": "{request.enterprise_code}", "enterprise_name": "{request.enterprise_name}"}}')
        
        # 调用文档生成器生成JSON数据
        def generate_documents():
            return generate_doc()
        
        # 安全执行文档生成
        template_documents = safe(
            generate_documents,
            return_value=[],
            error_msg="文档模板生成失败"
        )
        
        if not template_documents:
            log_error("文档模板生成失败或返回空数据")
            return CreateDocumentResponse(
                success=False,
                message="文档模板生成失败，请检查Excel文件"
            )
        
        # 更新模板文档中的企业信息
        for doc in template_documents:
            doc["enterprise_code"] = request.enterprise_code
            doc["enterprise_name"] = request.enterprise_name
        
        # 插入文档到MongoDB，使用enterprise_code作为_id
        result = await manager.insert_document_with_id(
            document_id=request.enterprise_code,
            document={
                "_id": request.enterprise_code,
                "enterprise_code": request.enterprise_code,
                "enterprise_name": request.enterprise_name,
                "fields": template_documents,
                "created_at": manager.get_current_timestamp(),
                "updated_at": manager.get_current_timestamp()
            }
        )
        
        if result:
            log_info(f"企业档案文档创建成功", 
                     extra_data=f'{{"enterprise_code": "{request.enterprise_code}", "fields_count": {len(template_documents)}}}')
            
            return CreateDocumentResponse(
                success=True,
                message="文档创建成功",
                document_id=request.enterprise_code,
                documents_count=len(template_documents)
            )
        else:
            log_error(f"文档插入失败", 
                      extra_data=f'{{"enterprise_code": "{request.enterprise_code}"}}')
            
            return CreateDocumentResponse(
                success=False,
                message="文档插入数据库失败"
            )
            
    except Exception as e:
        log_error("创建企业档案文档异常", exception=e, 
                  extra_data=f'{{"enterprise_code": "{request.enterprise_code}"}}')
        
        raise HTTPException(
            status_code=500,
            detail=f"创建文档失败: {str(e)}"
        )

@app.get("/api/v1/hierarchy")
async def get_hierarchy_data():
    return hierarchy_data.get_hierarchy_data()


@app.post("/api/v1/fields/update", 
          response_model=UpdateFieldResponse,
          summary="更新字段值")
async def update_field_value(
    request: UpdateFieldRequest,
    manager: MongoDBManager = Depends(get_mongodb_manager)
) -> UpdateFieldResponse:
    """
    更新企业档案中指定字段的值
    
    - **enterprise_code**: 企业代码，用于定位企业文档
    - **full_path_code**: 字段完整路径编码，用于定位具体字段
    - **dict_fields**: 包含要更新的字段值字典
        - **value**: 字段值（必填）
        - **value_pic_url**: 图片URL（可选，默认生成）
        - **value_doc_url**: 文档URL（可选，默认生成）
        - **value_video_url**: 视频URL（可选，默认生成）
    
    该API会通过enterprise_code和full_path_code定位到具体的子文档字段，
    然后将dict_fields中的值插入或更新到对应的字段中。
    """
    # 定义不可更新的 full_path_code 列表
    EXCLUDED_FULL_PATH_CODES = {
        "L19E5FFA.L279A000.L336E6A6.F1BDA09",
    }
    # 判断 full_path_code 是否在排除列表中
    if request.full_path_code in EXCLUDED_FULL_PATH_CODES:
        log_info(f"忽略对不可更新字段的请求", 
                 extra_data=f'{{"enterprise_code": "{request.enterprise_code}", "full_path_code": "{request.full_path_code}"}}')
        return UpdateFieldResponse(
            success=True,
            message=f"字段 {request.full_path_code} 不允许被修改，请求已忽略"
        )
    try:
        log_info(f"开始更新字段值", 
                extra_data=f'{{"enterprise_code": "{request.enterprise_code}", "full_path_code": "{request.full_path_code}"}}')
        
        # 1. 查找企业文档
        enterprise_doc = await manager.find_document_by_id(request.enterprise_code)
        if not enterprise_doc:
            log_error(f"企业文档未找到", 
                    extra_data=f'{{"enterprise_code": "{request.enterprise_code}"}}')
            return UpdateFieldResponse(
                success=False,
                message=f"企业代码 {request.enterprise_code} 对应的文档未找到"
            )
        
        # 2. 在fields数组中查找匹配的子文档
        fields_array = enterprise_doc.get("fields", [])
        target_field_index = None
        target_field = None
        
        for index, field in enumerate(fields_array):
            if field.get("full_path_code") == request.full_path_code:
                target_field_index = index
                target_field = field
                break
        
        if target_field_index is None:
            log_error(f"字段未找到", 
                    extra_data=f'{{"enterprise_code": "{request.enterprise_code}", "full_path_code": "{request.full_path_code}"}}')
            return UpdateFieldResponse(
                success=False,
                message=f"路径 {request.full_path_code} 对应的字段未找到"
            )
        
        # 3. 准备更新数据 - 设置默认URL值
        update_fields = {}
        updated_field_names = []
        
        # 更新value字段（必填）
        update_fields[f"fields.{target_field_index}.value"] = request.dict_fields.value
        update_fields[f"fields.{target_field_index}.value_text"] = request.dict_fields.value  # 同时更新用于全文检索的字段
        updated_field_names.append("value")
        
        # 更新可选的URL字段，如果未提供则使用默认格式
        pic_url = request.dict_fields.value_pic_url
        if pic_url is None:
            pic_url = f"http://get_pic_{request.enterprise_code}_{request.full_path_code}/pic"
        update_fields[f"fields.{target_field_index}.value_pic_url"] = pic_url
        updated_field_names.append("value_pic_url")
        
        doc_url = request.dict_fields.value_doc_url
        if doc_url is None:
            doc_url = f"http://get_pic_{request.enterprise_code}_{request.full_path_code}/doc"
        update_fields[f"fields.{target_field_index}.value_doc_url"] = doc_url
        updated_field_names.append("value_doc_url")
        
        video_url = request.dict_fields.value_video_url
        if video_url is None:
            video_url = f"http://get_pic_{request.enterprise_code}_{request.full_path_code}/video"
        update_fields[f"fields.{target_field_index}.value_video_url"] = video_url
        updated_field_names.append("value_video_url")
        
        # 更新字段的更新时间
        update_fields[f"fields.{target_field_index}.update_time"] = manager.get_current_timestamp()
        
        # 4. 执行数据库更新操作
        success = await manager.update_document(request.enterprise_code, update_fields)
        
        if success:
            log_info(f"字段值更新成功", 
                    extra_data=f'{{"enterprise_code": "{request.enterprise_code}", "full_path_code": "{request.full_path_code}", "updated_fields": {updated_field_names}}}')
            
            return UpdateFieldResponse(
                success=True,
                message="字段值更新成功",
                enterprise_code=request.enterprise_code,
                full_path_code=request.full_path_code,
                updated_fields=updated_field_names
            )
        else:
            log_error(f"字段值更新失败", 
                    extra_data=f'{{"enterprise_code": "{request.enterprise_code}", "full_path_code": "{request.full_path_code}"}}')
            
            return UpdateFieldResponse(
                success=False,
                message="数据库更新操作失败"
            )
    except Exception as e:
        log_error("更新字段值异常", exception=e, 
                extra_data=f'{{"enterprise_code": "{request.enterprise_code}", "full_path_code": "{request.full_path_code}"}}')
        
        raise HTTPException(
            status_code=500,
            detail=f"更新字段值失败: {str(e)}"
        )

# ==================== 错误处理 ====================
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """全局异常处理器"""
    log_error("未处理的API异常", exception=exc, 
              extra_data=f'{{"path": "{request.url.path}", "method": "{request.method}"}}')
    
    return {
        "error": "内部服务器错误",
        "message": "请查看日志获取详细信息"
    }

if __name__ == "__main__":
    import uvicorn
    
    log_info("正在启动MongoDB服务...")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )
