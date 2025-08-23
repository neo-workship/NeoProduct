# services/mongodb_service/main.py
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional,List,Tuple
import json5
import sys
import os
import re
import json
import time
from datetime import datetime, date
from decimal import Decimal
from bson import ObjectId
from contextlib import asynccontextmanager # 导入 asynccontextmanager

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from services.mongodb_service.config import get_connection_string, get_config
from services.mongodb_service.mongodb_manager import MongoDBManager
from services.mongodb_service.flat_enterprise_archive_generator_v2 import generate_doc
from services.mongodb_service.hierarchy_data import hierarchy_data
from mongo_exception_handler import log_info, log_error, safe
from schemas import *

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
            pic_url = f"http://get_pic_{request.enterprise_code}_{request.full_path_code.rsplit('.', 1)[-1]}/pic"
        update_fields[f"fields.{target_field_index}.value_pic_url"] = pic_url
        updated_field_names.append("value_pic_url")
        
        doc_url = request.dict_fields.value_doc_url
        if doc_url is None:
            doc_url = f"http://get_doc_{request.enterprise_code}_{request.full_path_code.rsplit('.', 1)[-1]}/doc"
        update_fields[f"fields.{target_field_index}.value_doc_url"] = doc_url
        updated_field_names.append("value_doc_url")
        
        video_url = request.dict_fields.value_video_url
        if video_url is None:
            video_url = f"http://get_video_{request.enterprise_code}_{request.full_path_code.rsplit('.', 1)[-1]}/video"
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

@app.post("/api/v1/enterprises/search",
          response_model=EnterpriseSearchResponse,
          summary="企业模糊搜索")
async def search_enterprises(
    request: EnterpriseSearchRequest,
    manager: MongoDBManager = Depends(get_mongodb_manager)
) -> EnterpriseSearchResponse:
    """
    根据企业代码或企业名称进行模糊搜索
    
    - **enterprise_text**: 搜索关键词，支持企业代码和企业名称的模糊匹配
    - **limit**: 返回结果数量限制，默认10条，最大100条
    
    该API会在MongoDB集合中搜索enterprise_code和enterprise_name字段，
    使用正则表达式进行模糊匹配，返回匹配的企业列表。
    """
    try:
        log_info(f"开始企业模糊搜索", 
                 extra_data=f'{{"search_text": "{request.enterprise_text}", "limit": {request.limit}}}')
        
        # 使用MongoDBManager的专用搜索方法
        documents, total_count = await manager.search_enterprises_by_text(
            search_text=request.enterprise_text,
            limit=request.limit
        )
        
        # 构建结果列表
        enterprises = []
        for doc in documents:
            enterprises.append(EnterpriseSearchItem(
                enterprise_code=doc.get("enterprise_code", doc.get("_id", "")),
                enterprise_name=doc.get("enterprise_name", "")
            ))
        
        log_info(f"企业搜索完成", 
                 extra_data=f'{{"search_text": "{request.enterprise_text}", "found_count": {len(enterprises)}, "total_count": {total_count}}}')
        
        return EnterpriseSearchResponse(
            success=True,
            message=f"找到 {len(enterprises)} 条匹配记录（共 {total_count} 条）",
            total_count=total_count,
            enterprises=enterprises
        )
            
    except Exception as e:
        log_error("企业搜索异常", exception=e,
                 extra_data=f'{{"search_text": "{request.enterprise_text}"}}')
        
        raise HTTPException(
            status_code=500,
            detail=f"搜索失败: {str(e)}"
        ).append(EnterpriseSearchItem(
                enterprise_code=doc.get("enterprise_code", doc.get("_id", "")),
                enterprise_name=doc.get("enterprise_name", "")
            ))
        
        log_info(f"企业搜索完成", 
                 extra_data=f'{{"search_text": "{request.enterprise_text}", "found_count": {len(enterprises)}, "total_count": {total_count}}}')
        
        return EnterpriseSearchResponse(
            success=True,
            message=f"找到 {len(enterprises)} 条匹配记录（共 {total_count} 条）",
            total_count=total_count,
            enterprises=enterprises
        )
            
    except Exception as e:
        log_error("企业搜索异常", exception=e,
                 extra_data=f'{{"search_text": "{request.enterprise_text}"}}')
        
        raise HTTPException(
            status_code=500,
            detail=f"搜索失败: {str(e)}"
        )

@app.post("/api/v1/enterprises/query_fields",
          response_model=QueryFieldsResponse,
          summary="查询企业字段数据")
async def query_enterprise_fields(
    request: QueryFieldsRequest,
    manager: MongoDBManager = Depends(get_mongodb_manager)
) -> QueryFieldsResponse:
    """
    根据企业代码和路径代码查询字段数据
    
    - **enterprise_code**: 企业代码，用于定位企业文档
    - **path_code_param**: 层级路径代码，用于匹配fields数组中的path_code字段
    - **fields_param**: 字段代码列表（可选）
        - 如果为空，返回指定路径下的所有字段
        - 如果不为空，只返回指定field_code的字段
    
    返回的字段包括：full_path_name、value、value_pic_url、value_doc_url、
    value_video_url、data_url、encoding、format、license、rights、
    update_frequency、value_dict等信息。
    """
    try:
        log_info(f"开始查询企业字段数据", 
                extra_data=f'{{"enterprise_code": "{request.enterprise_code}", "path_code": "{request.path_code_param}", "fields_param": {request.fields_param}}}')
        
        # 1. 检查企业是否存在
        enterprise_doc = await manager.find_document_by_id(request.enterprise_code)
        if not enterprise_doc:
            log_error(f"企业文档未找到", 
                    extra_data=f'{{"enterprise_code": "{request.enterprise_code}"}}')
            return QueryFieldsResponse(
                success=False,
                message=f"企业代码 {request.enterprise_code} 对应的文档未找到",
                enterprise_code=request.enterprise_code,
                path_code=request.path_code_param,
                total_count=0,
                fields=[]
            )
        
        # 2. 查询字段数据
        field_results, total_count = await manager.query_fields_by_path_and_codes(
            enterprise_code=request.enterprise_code,
            path_code=request.path_code_param,
            field_codes=request.fields_param
        )
        
        # 3. 转换为响应模型
        field_models = []
        for field_data in field_results:
            field_model = FieldDataModel(
                field_code=field_data.get("field_code"),
                field_name=field_data.get("field_name"),
                full_path_code=field_data.get("full_path_code"),
                full_path_name=field_data.get("full_path_name"),
                path_code=field_data.get("path_code"),
                value=field_data.get("value"),
                value_pic_url=field_data.get("value_pic_url"),
                value_doc_url=field_data.get("value_doc_url"),
                value_video_url=field_data.get("value_video_url"),
                data_url=field_data.get("data_url"),
                encoding=field_data.get("encoding"),
                format=field_data.get("format"),
                license=field_data.get("license"),
                rights=field_data.get("rights"),
                update_frequency=field_data.get("update_frequency"),
                value_dict=field_data.get("value_dict")
            )
            field_models.append(field_model)
        
        # 4. 构建响应
        if total_count > 0:
            log_info(f"字段查询成功", 
                    extra_data=f'{{"enterprise_code": "{request.enterprise_code}", "path_code": "{request.path_code_param}", "total_count": {total_count}}}')
            
            return QueryFieldsResponse(
                success=True,
                message=f"字段查询成功，共找到 {total_count} 个字段",
                enterprise_code=request.enterprise_code,
                path_code=request.path_code_param,
                total_count=total_count,
                fields=field_models
            )
        else:
            log_info(f"未找到匹配的字段", 
                    extra_data=f'{{"enterprise_code": "{request.enterprise_code}", "path_code": "{request.path_code_param}", "fields_param": {request.fields_param}}}')
            
            return QueryFieldsResponse(
                success=True,
                message="查询完成，但未找到匹配的字段",
                enterprise_code=request.enterprise_code,
                path_code=request.path_code_param,
                total_count=0,
                fields=[]
            )
            
    except Exception as e:
        log_error("查询企业字段异常", exception=e, 
                extra_data=f'{{"enterprise_code": "{request.enterprise_code}", "path_code": "{request.path_code_param}"}}')
        
        raise HTTPException(
            status_code=500,
            detail=f"查询字段失败: {str(e)}"
        )

@app.post("/api/v1/enterprises/edit_field_value",
          response_model=EditFieldValueResponse,
          summary="批量编辑字段值")
async def edit_field_value(
    request: EditFieldValueRequest,
    manager: MongoDBManager = Depends(get_mongodb_manager)
) -> EditFieldValueResponse:
    """
    批量编辑企业档案中指定路径下的字段值
    
    - **enterprise_code**: 企业代码，用于定位企业文档
    - **path_code_param**: 层级路径代码，用于匹配字段
    - **dict_fields**: 字段更新字典列表，每个字典包含要更新的字段信息
    
    该API会通过enterprise_code查询文档，然后用path_code_param匹配fields数组中的path_code字段，
    最后使用dict_fields中的key-value对更新匹配字段的值。
    """
    try:
        log_info(f"开始批量编辑字段值", 
                extra_data=f'{{"enterprise_code": "{request.enterprise_code}", "path_code_param": "{request.path_code_param}", "fields_count": {len(request.dict_fields)}}}')
        
        # 1. 检查参数
        if not request.dict_fields:
            return EditFieldValueResponse(
                success=False,
                message="dict_fields 不能为空"
            )
        
        # 2. 查找企业文档
        enterprise_doc = await manager.find_document_by_id(request.enterprise_code)
        if not enterprise_doc:
            log_error(f"企业文档未找到", 
                    extra_data=f'{{"enterprise_code": "{request.enterprise_code}"}}')
            return EditFieldValueResponse(
                success=False,
                message=f"企业代码 {request.enterprise_code} 对应的文档未找到"
            )
        
        # 3. 在fields数组中查找匹配path_code的字段
        fields_array = enterprise_doc.get("fields", [])
        matched_fields_indices = []
        
        for index, field in enumerate(fields_array):
            if field.get("path_code") == request.path_code_param:
                matched_fields_indices.append((index, field))
        
        if not matched_fields_indices:
            log_error(f"未找到匹配的字段", 
                    extra_data=f'{{"enterprise_code": "{request.enterprise_code}", "path_code_param": "{request.path_code_param}"}}')
            return EditFieldValueResponse(
                success=False,
                message=f"路径代码 {request.path_code_param} 未匹配到任何字段"
            )
        
        # 4. 准备批量更新数据
        update_fields = {}
        updated_field_codes = []
        total_processed = 0
        updated_count = 0
        
        # 将dict_fields转换为以field_code为key的字典，便于查找
        field_updates_map = {}
        for field_dict in request.dict_fields:
            if "field_code" in field_dict:
                field_updates_map[field_dict["field_code"]] = field_dict
        
        # 遍历匹配的字段，应用更新
        for field_index, field in matched_fields_indices:
            field_code = field.get("field_code")
            total_processed += 1
            
            # 检查是否有针对该字段的更新
            if field_code in field_updates_map:
                field_update = field_updates_map[field_code]
                field_updated = False
                
                # 遍历更新字典中的所有字段
                for update_key, update_value in field_update.items():
                    # 跳过field_code，因为它只是用于匹配的
                    if update_key == "field_code":
                        continue
                    
                    # 检查字段是否存在于FieldDataModel中
                    if update_key in FieldDataModel.__fields__:
                        update_fields[f"fields.{field_index}.{update_key}"] = update_value
                        field_updated = True
                
                # 如果有字段被更新，记录并更新时间戳
                if field_updated:
                    update_fields[f"fields.{field_index}.update_time"] = manager.get_current_timestamp()
                    updated_field_codes.append(field_code)
                    updated_count += 1
        
        # 5. 执行数据库更新操作
        if update_fields:
            success = await manager.update_document(request.enterprise_code, update_fields)
            
            if success:
                log_info(f"字段批量更新成功", 
                        extra_data=f'{{"enterprise_code": "{request.enterprise_code}", "path_code_param": "{request.path_code_param}", "updated_count": {updated_count}, "updated_fields": {updated_field_codes}}}')
                
                return EditFieldValueResponse(
                    success=True,
                    message="字段批量更新成功",
                    enterprise_code=request.enterprise_code,
                    path_code=request.path_code_param,
                    total_processed=total_processed,
                    updated_count=updated_count,
                    updated_fields=updated_field_codes
                )
            else:
                log_error(f"数据库更新失败", 
                        extra_data=f'{{"enterprise_code": "{request.enterprise_code}", "path_code_param": "{request.path_code_param}"}}')
                
                return EditFieldValueResponse(
                    success=False,
                    message="数据库更新操作失败",
                    enterprise_code=request.enterprise_code,
                    path_code=request.path_code_param,
                    total_processed=total_processed,
                    updated_count=0
                )
        else:
            log_info(f"没有找到需要更新的字段", 
                    extra_data=f'{{"enterprise_code": "{request.enterprise_code}", "path_code_param": "{request.path_code_param}"}}')
            
            return EditFieldValueResponse(
                success=True,
                message="没有找到需要更新的字段",
                enterprise_code=request.enterprise_code,
                path_code=request.path_code_param,
                total_processed=total_processed,
                updated_count=0,
                updated_fields=[]
            )
            
    except Exception as e:
        log_error("批量编辑字段值异常", exception=e, 
                extra_data=f'{{"enterprise_code": "{request.enterprise_code}", "path_code_param": "{request.path_code_param}"}}')
        
        raise HTTPException(
            status_code=500,
            detail=f"批量编辑字段值失败: {str(e)}"
        )

@app.delete("/api/v1/documents/batch", 
            response_model=DeleteManyDocumentsResponse, 
            summary="批量删除MongoDB文档")
async def delete_many_documents(
    request: DeleteManyDocumentsRequest,
    manager: MongoDBManager = Depends(get_mongodb_manager)
) -> DeleteManyDocumentsResponse:
    """
    批量删除企业档案MongoDB文档
    
    - **filter_query**: 删除条件查询字典，支持MongoDB查询语法
    - **confirm_delete**: 确认删除标志，必须设置为true才能执行删除操作
    
    该API使用deleteMany方法批量删除符合条件的文档。
    为了防止误操作，必须设置confirm_delete为true。
    
    常用查询条件示例：
    - 按企业代码删除: {"enterprise_code": "COMPANY001"}
    - 按多个企业代码删除: {"enterprise_code": {"$in": ["COMPANY001", "COMPANY002"]}}
    - 按时间范围删除: {"created_at": {"$lt": "2024-01-01T00:00:00"}}
    - 按字段值删除: {"enterprise_name": {"$regex": "测试", "$options": "i"}}
    """
    try:
        log_info(f"开始批量删除文档", 
                 extra_data=f'{{"filter_query": {request.filter_query}, "confirm_delete": {request.confirm_delete}}}')
        
        # 安全检查：必须确认删除
        if not request.confirm_delete:
            log_error("未确认删除操作")
            return DeleteManyDocumentsResponse(
                success=False,
                message="为防止误操作，请设置 confirm_delete 为 true",
                deleted_count=0,
                filter_query=request.filter_query
            )
        
        # 安全检查：防止删除所有文档
        if not request.filter_query or request.filter_query == {}:
            log_error("删除条件为空，拒绝执行")
            return DeleteManyDocumentsResponse(
                success=False,
                message="删除条件不能为空，以防止误删除所有文档",
                deleted_count=0,
                filter_query=request.filter_query
            )
        
        # 调用MongoDB管理器的批量删除方法
        delete_result = await manager.delete_many_documents(request.filter_query)
        
        # 构建响应
        response = DeleteManyDocumentsResponse(
            success=delete_result["success"],
            message=delete_result["message"],
            deleted_count=delete_result["deleted_count"],
            filter_query=request.filter_query if delete_result["success"] else None
        )
        
        if delete_result["success"]:
            log_info(f"批量删除文档完成", 
                    extra_data=f'{{"deleted_count": {delete_result["deleted_count"]}, "filter_query": {request.filter_query}}}')
        else:
            log_error(f"批量删除文档失败", 
                     extra_data=f'{{"message": "{delete_result["message"]}", "filter_query": {request.filter_query}}}')
        
        return response
        
    except Exception as e:
        log_error("批量删除文档API异常", exception=e, 
                 extra_data=f'{{"filter_query": {request.filter_query}}}')
        
        raise HTTPException(
            status_code=500,
            detail=f"批量删除文档失败: {str(e)}"
        )

# ==================== 执行原生MongoDB查询命令 ====================
@app.post("/api/v1/enterprises/execute_mongo_cmd",
          response_model=ExecuteMongoQueryResponse,
          summary="执行原始MongoDB查询语句")
async def execute_mongo_command(
    request: ExecuteMongoQueryRequest,
    manager: MongoDBManager = Depends(get_mongodb_manager)
) -> ExecuteMongoQueryResponse:
    """
    解析和执行原始MongoDB查询语句，返回新格式的分类数据
    
    支持的查询类型：
    - db.collection.find()、db.collection.findOne()、db.collection.aggregate()、db.collection.count()、db.collection.countDocuments()、db.collection.distinct()
    
    注意：
    - 查询将在配置文件指定的数据库("数字政府")和集合("一企一档")中执行
    - 查询语句中的集合名会被忽略，始终使用配置的集合
    
    Args:
        request: 包含原始查询语句的请求模型
        
    Returns:
        包含新格式分类后数据的响应模型
    """
    start_time = time.time()
    
    try:
        log_info("开始执行MongoDB原生查询", 
                extra_data=f'{{"query_cmd": "{request.query_cmd[:200]}...", "database": "{manager.database.name if manager.database is not None else "未知"}", "collection": "{manager.collection_name}"}}')
        
        # 2.1 解析查询操作类型
        query_type = _parse_query_type(request.query_cmd)
        if not query_type:
            raise HTTPException(
                status_code=400,
                detail="不支持的查询类型，只支持 find/findOne/aggregate/count/countDocuments/distinct 操作"
            )
        
        # 2.2 解析查询参数（集合名将被忽略，使用配置的集合）
        query_params = _parse_query_parameters_with_json5(request.query_cmd, query_type)
        
        # 2.3 执行MongoDB查询（使用配置的集合）
        result_data, total_count = await _execute_mongodb_query(
            manager, query_type, query_params
        )
        
        # 2.4 根据查询类型对返回数据进行分类处理 - 使用新格式
        response_data = _classify_query_result_new_format(query_type, result_data, total_count,query_params)
        
        # 2.5 计算统计信息 - 运行耗时以ms为单位
        execution_time = (time.time() - start_time) * 1000
        
        log_info("MongoDB原生查询执行成功", 
                extra_data=f'{{"query_type": "{query_type}", "result_type": "{response_data["type"]}", "execution_time_ms": {execution_time}, "collection": "{manager.collection_name}"}}')
        
        # 2.6 直接返回新格式的响应数据
        return ExecuteMongoQueryResponse(
            type=response_data["type"],
            period=f"{round(execution_time, 2)}ms",
            messages=response_data["messages"],
            result_data=response_data["result_data"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        execution_time = (time.time() - start_time) * 1000
        log_error("MongoDB原生查询执行失败", exception=e,
                 extra_data=f'{{"query_cmd": "{request.query_cmd[:200]}...", "execution_time_ms": {execution_time}, "collection": "{manager.collection_name if manager else "未知"}"}}')
        
        # 错误时也返回新格式
        return ExecuteMongoQueryResponse(
            type="错误",
            period=f"{round(execution_time, 2)}ms",
            messages=f"查询执行失败: {str(e)}",
            result_data=[]
        )

def _parse_query_type(query_cmd: str) -> Optional[str]:
    """
    解析查询操作类型
    
    Args:
        query_cmd: 原始查询命令
        
    Returns:
        查询类型字符串或None
    """
    query_cmd_clean = query_cmd.strip().lower()
    
    if ".find(" in query_cmd_clean and ".findone(" not in query_cmd_clean:
        return "find"
    elif ".findone(" in query_cmd_clean:
        return "findOne"
    elif ".aggregate(" in query_cmd_clean:
        # 检查是否包含 $group 操作
        if "$group" in query_cmd_clean:
            return "group"
        else:
            return "aggregate"
    elif ".countdocuments(" in query_cmd_clean:
        return "countDocuments"
    elif ".count(" in query_cmd_clean:
        return "count"
    elif ".distinct(" in query_cmd_clean:
        return "distinct"
    
    return None

def _extract_method_params(query_cmd: str, method_name: str) -> str:
    """
    提取方法的参数部分
    
    Args:
        query_cmd: 查询命令
        method_name: 方法名（如 aggregate, find等）
        
    Returns:
        参数字符串
    """
    # 使用正则表达式匹配方法调用，支持嵌套括号
    pattern = rf'\.{method_name}\s*\('
    match = re.search(pattern, query_cmd, re.IGNORECASE)
    if not match:
        return ""
    
    start_pos = match.end() - 1  # 从左括号开始
    bracket_count = 0
    end_pos = start_pos
    
    # 找到匹配的右括号
    for i in range(start_pos, len(query_cmd)):
        if query_cmd[i] == '(':
            bracket_count += 1
        elif query_cmd[i] == ')':
            bracket_count -= 1
            if bracket_count == 0:
                end_pos = i
                break
    
    # 提取括号内的内容
    params_str = query_cmd[start_pos + 1:end_pos].strip()
    return params_str

def _preprocess_js_object(js_str: str) -> str:
    """
    预处理JavaScript对象字符串，使其更容易被json5解析
    
    Args:
        js_str: JavaScript对象字符串
        
    Returns:
        预处理后的字符串
    """
    if not js_str.strip():
        return js_str
    
    # 移除JavaScript特有的语法
    # 1. 移除JavaScript注释
    js_str = re.sub(r'//.*?$', '', js_str, flags=re.MULTILINE)
    js_str = re.sub(r'/\*.*?\*/', '', js_str, flags=re.DOTALL)
    
    # 2. 处理MongoDB特有的操作符（保持$符号）
    # MongoDB的字段名和操作符通常以$开头，这些是合法的
    
    # 3. 处理正则表达式字面量 /pattern/flags -> {"$regex": "pattern", "$options": "flags"}
    if '"$regex"' not in js_str and "'$regex'" not in js_str:
        js_str = re.sub(r'/([^/]+)/([gimx]*)', r'"\\1"', js_str)
    else:
        # 如果已经在$regex上下文中，只需要将正则字面量转换为字符串
        js_str = re.sub(r':\s*/([^/]+)/([gimx]*)', r': "\\1"', js_str)
    
    # 4. 处理Date对象 Date() -> {"$date": "..."}
    # 简化处理，实际应用中可能需要更复杂的日期解析
    js_str = re.sub(r'new\s+Date\s*\(\s*([^)]+)\s*\)', r'{"$date": \1}', js_str)
    js_str = re.sub(r'Date\s*\(\s*([^)]+)\s*\)', r'{"$date": \1}', js_str)
    
    # 5. 处理ObjectId ObjectId("...") -> {"$oid": "..."}
    js_str = re.sub(r'ObjectId\s*\(\s*["\']([^"\']+)["\']\s*\)', r'{"$oid": "\1"}', js_str)
    
    return js_str

def _parse_query_parameters_with_json5(query_cmd: str, query_type: str) -> Dict[str, Any]:
    """
    使用json5解析查询参数，更好地处理JavaScript语法
    
    Args:
        query_cmd: 查询命令
        query_type: 查询类型
        
    Returns:
        查询参数字典
    """
    try:
        if query_type in ["find", "findOne"]:
            params_str = _extract_method_params(query_cmd, query_type)
            if not params_str:
                return {"filter": {}}
            
            # 如果有多个参数，用逗号分割（注意处理嵌套对象中的逗号）
            filter_str = _extract_first_parameter(params_str)
            filter_str = _preprocess_js_object(filter_str)
            
            try:
                filter_dict = json5.loads(filter_str) if filter_str else {}
                return {"filter": filter_dict}
            except Exception as e:
                log_error(f"解析find/findOne参数失败: {filter_str}", exception=e)
                return {"filter": {}}
        
        elif query_type in ["aggregate", "group"]:
            params_str = _extract_method_params(query_cmd, "aggregate")
            if not params_str:
                return {"pipeline": []}
            
            # 预处理JavaScript对象语法
            params_str = _preprocess_js_object(params_str)
            
            try:
                # 尝试解析为数组
                pipeline = json5.loads(params_str)
                
                # 确保pipeline是列表类型
                if not isinstance(pipeline, list):
                    pipeline = [pipeline]
                
                # 验证pipeline中的每个阶段都是字典
                validated_pipeline = []
                for stage in pipeline:
                    if isinstance(stage, dict):
                        validated_pipeline.append(stage)
                    else:
                        log_error(f"Invalid pipeline stage (not a dict): {stage}")
                        # 尝试转换为字典
                        try:
                            if isinstance(stage, str):
                                stage_dict = json5.loads(stage)
                                if isinstance(stage_dict, dict):
                                    validated_pipeline.append(stage_dict)
                            else:
                                log_error(f"Cannot convert stage to dict: {stage}")
                        except:
                            log_error(f"Failed to parse stage: {stage}")
                
                # 如果是group类型，添加字段别名处理
                if query_type == "group":
                    validated_pipeline = _add_group_field_aliases(validated_pipeline)
                
                return {"pipeline": validated_pipeline}
                
            except Exception as e:
                log_error(f"解析aggregate参数失败: {params_str}", exception=e)
                return {"pipeline": []}
        
        elif query_type in ["count", "countDocuments"]:
            method = "countDocuments" if query_type == "countDocuments" else "count"
            params_str = _extract_method_params(query_cmd, method)
            
            if not params_str:
                return {"filter": {}}
            
            params_str = _preprocess_js_object(params_str)
            
            try:
                filter_dict = json5.loads(params_str) if params_str else {}
                return {"filter": filter_dict}
            except Exception as e:
                log_error(f"解析{method}参数失败: {params_str}", exception=e)
                return {"filter": {}}
        
        elif query_type == "distinct":
            params_str = _extract_method_params(query_cmd, "distinct")
            if not params_str:
                return {"field": "", "filter": {}}
            
            # distinct方法通常有两个参数：字段名和过滤条件
            params = _split_parameters(params_str)
            
            field_name = ""
            filter_dict = {}
            
            if len(params) >= 1:
                # 第一个参数是字段名（字符串）
                field_param = params[0].strip().strip('\'"')
                field_name = field_param
            
            if len(params) >= 2:
                # 第二个参数是过滤条件（对象）
                filter_str = _preprocess_js_object(params[1])
                try:
                    filter_dict = json5.loads(filter_str)
                except Exception as e:
                    log_error(f"解析distinct过滤条件失败: {params[1]}", exception=e)
                    filter_dict = {}

            return {"field": field_name, "filter": filter_dict}
        return {}
        
    except Exception as e:
        log_error("解析查询参数失败", exception=e)
        return {}

def _add_group_field_aliases(pipeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    为group聚合操作添加字段别名处理
    
    Args:
        pipeline: 聚合管道
        
    Returns:
        处理后的聚合管道
    """
    # 聚合操作符到中文别名的映射
    AGGREGATION_ALIASES = {
        "$sum": "求和",
        "$avg": "平均值", 
        "$min": "最小值",
        "$max": "最大值",
        "$stdDevPop": "总体标准差",
        "$stdDevSamp": "样本标准差",
        "$count": "计数"
    }
    
    processed_pipeline = []
    field_aliases = {}
    
    for stage in pipeline:
        if isinstance(stage, dict) and "$group" in stage:
            group_stage = stage.copy()
            group_spec = group_stage["$group"]
            
            # 处理group阶段中的聚合字段
            if isinstance(group_spec, dict):
                for field_name, field_expr in group_spec.items():
                    if field_name != "_id" and isinstance(field_expr, dict):
                        # 检查是否包含聚合操作符
                        for agg_op, agg_value in field_expr.items():
                            if agg_op in AGGREGATION_ALIASES:
                                # 生成中文别名
                                chinese_alias = AGGREGATION_ALIASES[agg_op]
                                field_aliases[field_name] = chinese_alias
                                
                                log_info(f"为字段 {field_name} 添加别名: {chinese_alias}")
            
            processed_pipeline.append(group_stage)
        else:
            processed_pipeline.append(stage)
    
    # 如果有别名，添加到pipeline的元数据中
    if field_aliases:
        # 可以选择将别名信息添加到某个位置，或者在后续处理中使用
        # 这里先记录日志，具体使用方式可以在后续步骤中确定
        log_info(f"Group查询字段别名映射: {field_aliases}")
    
    return processed_pipeline

def _extract_first_parameter(params_str: str) -> str:
    """
    从参数字符串中提取第一个参数（考虑嵌套括号和引号）
    
    Args:
        params_str: 参数字符串
        
    Returns:
        第一个参数的字符串
    """
    if not params_str.strip():
        return ""
    
    bracket_count = 0
    brace_count = 0
    square_count = 0
    in_string = False
    string_char = None
    escape_next = False
    
    for i, char in enumerate(params_str):
        if escape_next:
            escape_next = False
            continue
        
        if char == '\\':
            escape_next = True
            continue
        
        if not in_string:
            if char in ['"', "'"]:
                in_string = True
                string_char = char
            elif char == '(':
                bracket_count += 1
            elif char == ')':
                bracket_count -= 1
            elif char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
            elif char == '[':
                square_count += 1
            elif char == ']':
                square_count -= 1
            elif char == ',' and bracket_count == 0 and brace_count == 0 and square_count == 0:
                return params_str[:i].strip()
        else:
            if char == string_char:
                in_string = False
                string_char = None
    
    return params_str.strip()

def _split_parameters(params_str: str) -> List[str]:
    """
    智能分割参数字符串，考虑嵌套括号和引号
    
    Args:
        params_str: 参数字符串
        
    Returns:
        参数列表
    """
    if not params_str.strip():
        return []
    
    params = []
    current_param = ""
    bracket_count = 0
    brace_count = 0
    square_count = 0
    in_string = False
    string_char = None
    escape_next = False
    
    for char in params_str:
        if escape_next:
            current_param += char
            escape_next = False
            continue
        
        if char == '\\':
            current_param += char
            escape_next = True
            continue
        
        if not in_string:
            if char in ['"', "'"]:
                in_string = True
                string_char = char
                current_param += char
            elif char == '(':
                bracket_count += 1
                current_param += char
            elif char == ')':
                bracket_count -= 1
                current_param += char
            elif char == '{':
                brace_count += 1
                current_param += char
            elif char == '}':
                brace_count -= 1
                current_param += char
            elif char == '[':
                square_count += 1
                current_param += char
            elif char == ']':
                square_count -= 1
                current_param += char
            elif char == ',' and bracket_count == 0 and brace_count == 0 and square_count == 0:
                params.append(current_param.strip())
                current_param = ""
            else:
                current_param += char
        else:
            current_param += char
            if char == string_char:
                in_string = False
                string_char = None
    
    if current_param.strip():
        params.append(current_param.strip())
    
    return params

def _serialize_document(doc: Any) -> str:
    """
    安全地序列化MongoDB文档，处理datetime、ObjectId等特殊类型
    
    Args:
        doc: 要序列化的文档
        
    Returns:
        JSON字符串
    """
    def json_serializer(obj):
        """JSON序列化器，处理特殊类型"""
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, date):
            return obj.isoformat()
        elif isinstance(obj, ObjectId):
            return str(obj)
        elif isinstance(obj, Decimal):
            return float(obj)
        elif hasattr(obj, 'to_dict'):
            return obj.to_dict()
        elif hasattr(obj, '__dict__'):
            return obj.__dict__
        else:
            return str(obj)
    
    try:
        if isinstance(doc, dict):
            return json5.dumps(doc, ensure_ascii=False, default=json_serializer)
        else:
            return str(doc)
    except Exception as e:
        # 如果序列化失败，返回字符串表示
        return str(doc)

def _convert_data_meta_to_dict(data_meta):
    """
    将DataMetaFieldModel对象转换为字典
    
    Args:
        data_meta: DataMetaFieldModel对象
        
    Returns:
        字典格式的数据
    """
    if hasattr(data_meta, 'to_dict'):
        return data_meta.to_dict()
    elif hasattr(data_meta, '__dict__'):
        return data_meta.__dict__
    elif hasattr(data_meta, 'dict'):  # 如果是Pydantic模型
        return data_meta.dict()
    elif hasattr(data_meta, 'model_dump'):  # 如果是Pydantic v2模型
        return data_meta.model_dump()
    else:
        # 如果都没有，手动提取属性
        return {
            'data_source': getattr(data_meta, 'data_source', ''),
            'encoding': getattr(data_meta, 'encoding', ''),
            'format': getattr(data_meta, 'format', ''),
            'license': getattr(data_meta, 'license', ''),
            'rights': getattr(data_meta, 'rights', ''),
            'update_frequency': getattr(data_meta, 'update_frequency', ''),
            'value_dict': getattr(data_meta, 'value_dict', '')
        }

def _classify_query_result_new_format(query_type: str, 
                                      result_data: List[Dict[str, Any]], 
                                      total_count: int,
                                      query_params: Dict[str, Any]) -> Dict[str, Any]:
    """
    根据查询类型对返回结果进行分类处理 - 新格式（修复 None 值处理和单个字段文档处理）
    
    Args:
        query_type: 查询类型
        result_data: 查询结果数据
        total_count: 总数量
        query_params: 查询参数
        
    Returns:
        分类后的数据字典 - 新格式
    """
    result = None
    
    if query_type in ["count", "countDocuments", "distinct"]:
        # 汇总类型：count、countDocuments、distinct
        if result_data and len(result_data) > 0 and "count" in result_data[0]:
            count_value = result_data[0]["count"]
        else:
            count_value = total_count
            
        result = {
            "type": "汇总",
            "messages": "正常处理",
            "result_data": [count_value] if count_value is not None else [0]
        }
        
    elif query_type == "group":
        # 分组汇总类型：$group 聚合操作
        processed_group_data = []
        
        for doc in result_data:
            if doc is not None and isinstance(doc, dict):
                # 处理分组结果，应用字段别名
                processed_doc = _apply_group_field_aliases(doc, query_params)
                processed_group_data.append(processed_doc)
            elif doc is not None:
                # 如果不是字典但也不是None，直接添加
                processed_group_data.append(doc)
            # 跳过 None 值
        
        result = {
            "type": "分组",
            "messages": "正常处理", 
            "result_data": processed_group_data
        }
        
    elif query_type in ["find", "findOne", "aggregate"]:
        # 明细类型：find、findOne、aggregate
        result_list = []
        
        for doc in result_data:
            # 跳过 None 值
            if doc is None:
                continue
                
            # 判断文档类型并相应处理
            if _is_enterprise_archive_document(doc):
                # 标准企业档案文档，包含 fields 数组
                for field in doc["fields"]:
                    if field is None:
                        continue
                        
                    # 构建符合新格式的数据项
                    data_item = {
                        "data_value": {
                            "enterprise_code": doc.get("enterprise_code", ""),
                            "enterprise_name": doc.get("enterprise_name", ""),
                            "full_path_code": field.get("full_path_code", ""),
                            "full_path_name": field.get("full_path_name", ""),
                            "field_code": field.get("field_code", ""),
                            "field_name": field.get("field_name", ""),
                            "value": field.get("value", ""),
                            "value_text": field.get("value_text", ""),
                            "value_pic_url": field.get("value_pic_url", ""),
                            "value_doc_url": field.get("value_doc_url", ""),
                            "value_video_url": field.get("value_video_url", "")
                        },
                        "data_meta": DataMetaFieldModel(
                            data_source=field.get("data_source", ""),
                            encoding=field.get("encoding", ""),
                            format=field.get("format", ""),
                            license=field.get("license", ""),
                            rights=field.get("rights", ""),
                            update_frequency=field.get("update_frequency", ""),
                            value_dict=field.get("value_dict", "")
                        )
                    }
                    result_list.append(data_item)
                    
            elif _is_single_field_document(doc):
                # 单个字段文档（如 $unwind 后的结果）
                field = doc.get("fields", {})
                data_item = {
                    "data_value": {
                        "enterprise_code": doc.get("enterprise_code", ""),
                        "enterprise_name": doc.get("enterprise_name", ""),
                        "full_path_code": field.get("full_path_code", ""),
                        "full_path_name": field.get("full_path_name", ""),
                        "field_code": field.get("field_code", ""),
                        "field_name": field.get("field_name", ""),
                        "value": field.get("value", ""),
                        "value_text": field.get("value_text", ""),
                        "value_pic_url": field.get("value_pic_url", ""),
                        "value_doc_url": field.get("value_doc_url", ""),
                        "value_video_url": field.get("value_video_url", "")
                    },
                    "data_meta": DataMetaFieldModel(
                        data_source=field.get("data_source", ""),
                        encoding=field.get("encoding", ""),
                        format=field.get("format", ""),
                        license=field.get("license", ""),
                        rights=field.get("rights", ""),
                        update_frequency=field.get("update_frequency", ""),
                        value_dict=field.get("value_dict", "")
                    )
                }
                result_list.append(data_item)
            else:
                # 其他格式的文档，转换为标准格式
                data_item = {
                    "data_value": {
                        "enterprise_code": doc.get("enterprise_code", ""),
                        "enterprise_name": doc.get("enterprise_name", ""),
                        "full_path_code": doc.get("full_path_code", ""),
                        "full_path_name": doc.get("full_path_name", ""),
                        "field_code": doc.get("field_code", ""),
                        "field_name": doc.get("field_name", ""),
                        "value": _serialize_document(doc),
                        "value_text": doc.get("value_text", ""),
                        "value_pic_url": doc.get("value_pic_url", ""),
                        "value_doc_url": doc.get("value_doc_url", ""),
                        "value_video_url": doc.get("value_video_url", "")
                    },
                    "data_meta": DataMetaFieldModel(
                        data_source=doc.get("data_source", ""),
                        encoding=doc.get("encoding", ""),
                        format=doc.get("format", ""),
                        license=doc.get("license", ""),
                        rights=doc.get("rights", ""),
                        update_frequency=doc.get("update_frequency", ""),
                        value_dict=doc.get("value_dict", "")
                    )
                }
                result_list.append(data_item)
        
        result = {
            "type": "明细",
            "messages": "正常处理",
            "result_data": result_list
        }
    
    # 处理序列化和文件存储（保持原有逻辑）
    try:
        serializable_result_data = []
        for item in result["result_data"]:
            if isinstance(item, dict) and "data_meta" in item:
                serializable_item = item.copy()
                # 将DataMetaFieldModel转换为字典
                serializable_item["data_meta"] = _convert_data_meta_to_dict(item["data_meta"])
                serializable_result_data.append(serializable_item)
            else:
                serializable_result_data.append(item)
        
        storage_data = {
            "query_type": query_type,
            "query_params": query_params,
            "result": {
                "type": result["type"],
                "result": serializable_result_data,  # 使用转换后的数据
            },
            "total_count": total_count,
        }
        
        # 以query_type命名文件
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"D://mongoquery_history//{query_type}_{timestamp}.json"
        # 使用json5写入文件，支持更灵活的JSON格式
        with open(filename, 'w', encoding='utf-8') as f:
            json5.dump(storage_data, f, ensure_ascii=False, indent=2)
                    
    except Exception as e:
        # 文件存储失败不影响主要功能，可以记录日志或静默处理
        print(f"文件存储失败{e}")
        pass
    
    return result

def _is_enterprise_archive_document(doc: Dict[str, Any]) -> bool:
    """
    判断文档是否为标准企业档案文档（包含 fields 数组）
    
    Args:
        doc: 待判断的文档
        
    Returns:
        True 如果是标准企业档案文档，False 否则
    """
    return (
        isinstance(doc, dict) and
        "fields" in doc and
        isinstance(doc["fields"], list) and
        len(doc["fields"]) > 0
    )

def _is_single_field_document(doc: Dict[str, Any]) -> bool:
    """
    判断文档是否为单个字段文档（如 $unwind 后的结果）
    
    特征：
    - 包含 enterprise_code, enterprise_name
    - 包含 fields 字段，但是字典而不是数组
    - fields 字典包含字段相关属性
    
    Args:
        doc: 待判断的文档
        
    Returns:
        True 如果是单个字段文档，False 否则
    """
    return (
        isinstance(doc, dict) and
        "enterprise_code" in doc and
        "enterprise_name" in doc and
        "fields" in doc and
        isinstance(doc["fields"], dict) and
        # 检查 fields 字典是否包含字段特征属性
        any(key in doc["fields"] for key in ["field_name", "field_code", "path_name", "full_path_name"])
    )

def _apply_group_field_aliases(group_doc: Dict[str, Any], query_params: Dict[str, Any]) -> Dict[str, Any]:
    """
    为分组查询结果应用字段别名
    
    Args:
        group_doc: 分组查询返回的单个文档
        query_params: 查询参数（包含字段别名信息）
        
    Returns:
        应用别名后的文档
    """
    # 聚合操作符到中文别名的映射
    AGGREGATION_ALIASES = {
        "$sum": "求和",
        "$avg": "平均值", 
        "$min": "最小值",
        "$max": "最大值",
        "$stdDevPop": "总体标准差",
        "$stdDevSamp": "样本标准差",
        "$count": "计数"
    }
    
    if group_doc is None:
        return {}
    
    processed_doc = group_doc.copy()
    
    try:
        # 从pipeline中获取$group阶段的字段定义
        pipeline = query_params.get("pipeline", [])
        group_stage = None
        
        for stage in pipeline:
            if isinstance(stage, dict) and "$group" in stage:
                group_stage = stage["$group"]
                break
        
        if group_stage and isinstance(group_stage, dict):
            # 遍历分组文档的字段，应用别名
            for field_name, field_value in list(processed_doc.items()):
                if field_name != "_id" and field_name in group_stage:
                    # 获取该字段的聚合定义
                    field_def = group_stage[field_name]
                    if isinstance(field_def, dict):
                        # 查找聚合操作符
                        for agg_op in field_def.keys():
                            if agg_op in AGGREGATION_ALIASES:
                                # 生成中文别名
                                chinese_alias = AGGREGATION_ALIASES[agg_op]
                                # 重命名字段
                                processed_doc[chinese_alias] = field_value
                                # 删除原字段名（可选，根据需求决定）
                                # del processed_doc[field_name]
                                log_info(f"应用分组字段别名: {field_name} -> {chinese_alias}")
                                break
        
    except Exception as e:
        log_error("应用分组字段别名失败", exception=e)
        # 如果出错，返回原始文档
        return group_doc
    
    return processed_doc
    
async def _execute_mongodb_query(
    manager: MongoDBManager, 
    query_type: str, 
    query_params: Dict[str, Any]
) -> Tuple[List[Dict[str, Any]], int]:
    """
    执行MongoDB查询 - 支持group查询
    
    Args:
        manager: MongoDB管理器（已经连接到配置的数据库和集合）
        query_type: 查询类型
        query_params: 查询参数
        
    Returns:
        (查询结果数据, 总文档数)
    """
    if manager.collection is None:
        raise Exception("MongoDB集合未初始化")
    
    # 直接使用管理器中配置的集合（"一企一档"）
    collection = manager.collection
    log_info(f"使用配置的集合: {manager.collection_name}")
    
    total_count = 0
    result_data = []
    
    try:
        if query_type == "find":
            filter_dict = query_params.get("filter", {})
            
            # 获取总数
            total_count = await collection.count_documents(filter_dict)
            
            # 执行查询（限制返回数量避免内存问题）
            cursor = collection.find(filter_dict).limit(100)
            result_data = await cursor.to_list(length=100)
            
        elif query_type == "findOne":
            filter_dict = query_params.get("filter", {})
            
            # findOne只返回一个文档
            doc = await collection.find_one(filter_dict)
            result_data = [doc] if doc else []
            total_count = 1 if doc else 0
            
        elif query_type in ["aggregate", "group"]:
            pipeline = query_params.get("pipeline", [])
            
            # 验证pipeline是字典列表
            if not isinstance(pipeline, list):
                raise Exception(f"Pipeline必须是列表类型，当前类型: {type(pipeline)}")
         
            for i, stage in enumerate(pipeline):
                if not isinstance(stage, dict):
                    raise Exception(f"Pipeline阶段{i}必须是字典类型，当前类型: {type(stage)}")
            
            log_info(f"执行聚合查询，pipeline: {pipeline}")
            
            # 执行聚合查询
            cursor = collection.aggregate(pipeline)
            result_data = await cursor.to_list(length=100)
            total_count = len(result_data)
            
            # 对于group查询，记录额外信息
            if query_type == "group":
                log_info(f"Group查询完成，返回 {total_count} 个分组结果")
            
        elif query_type in ["count", "countDocuments"]:
            filter_dict = query_params.get("filter", {})
            
            # 执行计数查询
            count_result = await collection.count_documents(filter_dict)
            # 修正：确保 result_data 格式正确，包含 count 字段
            result_data = [{"count": count_result}]
            total_count = count_result  # 修正：total_count 应该是实际计数结果
            
        elif query_type == "distinct":
            field_name = query_params.get("field", "")
            filter_dict = query_params.get("filter", {})
            
            if not field_name:
                raise Exception("distinct查询缺少字段名")
            
            # 执行去重查询
            distinct_values = await collection.distinct(field_name, filter_dict)
            # 修正：确保 result_data 格式正确，包含 count 字段
            result_data = [{"count": len(distinct_values)}]
            total_count = len(distinct_values)
        
        else:
            raise Exception(f"不支持的查询类型: {query_type}")
        
        log_info(f"查询执行成功", 
                extra_data=f'{{"query_type": "{query_type}", "collection": "{manager.collection_name}", "result_count": {len(result_data)}, "total_count": {total_count}}}')
        
        return result_data, total_count
        
    except Exception as e:
        log_error("MongoDB查询执行失败", exception=e, 
                 extra_data=f'{{"query_type": "{query_type}", "query_params": {query_params}, "collection": "{manager.collection_name}"}}')
        raise
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
