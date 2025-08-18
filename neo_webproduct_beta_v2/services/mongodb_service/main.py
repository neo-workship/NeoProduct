# services/mongodb_service/main.py
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional,List,Tuple
import sys
import os
import re
import json
import time
from typing import Union
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
    解析和执行原始MongoDB查询语句，返回分类后的数据
    
    支持的查询类型：
    - db.collection.find() - 查询文档 (明细)
    - db.collection.findOne() - 查询单个文档 (明细)
    - db.collection.aggregate() - 聚合查询 (明细)
    - db.collection.count() - 计数查询 (汇总)
    - db.collection.countDocuments() - 统计文档数量查询 (汇总)
    - db.collection.distinct() - 去重统计 (汇总)
    
    注意：
    - 查询将在配置文件指定的数据库("数字政府")和集合("一企一档")中执行
    - 查询语句中的集合名会被忽略，始终使用配置的集合
    
    Args:
        request: 包含原始查询语句的请求模型
        
    Returns:
        包含分类后数据的响应模型
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
        
        # 2.2 修复和预处理查询语句
        fixed_query = _fix_query_syntax(request.query_cmd)
        
        # 2.3 解析查询参数（集合名将被忽略，使用配置的集合）
        _, query_params = _parse_query_parameters(fixed_query, query_type)
        
        # 2.4 执行MongoDB查询（使用配置的集合）
        result_data, total_count = await _execute_mongodb_query(
            manager, query_type, query_params
        )
        print(f"_classify_query_result result_data:{result_data} ， total_count:{total_count}")

        # 2.5 根据查询类型对返回数据进行分类处理
        response_data = _classify_query_result(query_type, result_data, total_count)
        
        # 2.6 计算统计信息
        execution_time = (time.time() - start_time) * 1000
        statis = {
            "耗时": f"{round(execution_time, 2)}ms",
            "文档数": len(result_data) if result_data else total_count
        }
        
        log_info("MongoDB原生查询执行成功", 
                extra_data=f'{{"query_type": "{query_type}", "result_type": "{response_data["type"]}", "execution_time_ms": {execution_time}, "collection": "{manager.collection_name}"}}')
        
        return ExecuteMongoQueryResponse(
            success=True,
            message="查询执行成功",
            statis=statis,
            **response_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        execution_time = (time.time() - start_time) * 1000
        log_error("MongoDB原生查询执行失败", exception=e,
                 extra_data=f'{{"query_cmd": "{request.query_cmd[:200]}...", "execution_time_ms": {execution_time}, "collection": "{manager.collection_name if manager else "未知"}"}}')
        
        # 错误时也返回 ExecuteMongoQueryResponse 格式
        return ExecuteMongoQueryResponse(
            success=False,
            message=f"查询执行失败: {str(e)}",
            type="错误",
            statis={
                "耗时": f"{round(execution_time, 2)}ms",
                "文档数": 0
            },
            field_value=[],
            field_meta=None
        )
    
# 响应结果分类处理
def _classify_query_result(query_type: str, result_data: List[Dict[str, Any]], total_count: int) -> Dict[str, Any]:
    """
    根据查询类型对返回结果进行分类处理
    
    Args:
        query_type: 查询类型
        result_data: 查询结果数据
        total_count: 总数量
        
    Returns:
        分类后的数据字典
    """
    if query_type in ["count", "countDocuments", "distinct"]:  # 修改：将 countDocuments 加入汇总类型
        # 汇总类型：count、countDocuments、distinct
        if query_type in ["count", "countDocuments"]:  # 修改：count 和 countDocuments 统一处理
            field_value = total_count
        elif query_type == "distinct":
            # distinct返回的是去重后的值列表的数量
            field_value = len(result_data) if result_data else 0
            
        return {
            "type": "汇总",
            "field_value": field_value,
            "field_meta": None
        }
    
    elif query_type in ["find", "findOne", "aggregate"]:
        # 明细类型：find、findOne、aggregate
        
        # 提取字段数据值（根据文档结构提取）
        field_value_list = []
        field_meta = None
        
        for doc in result_data:
            if "fields" in doc and isinstance(doc["fields"], list):
                # 如果是企业档案文档，提取fields数组中的数据
                for field in doc["fields"]:
                    field_data = _extract_field_value(field)
                    if field_data:
                        field_value_list.append(field_data)
                        
                        # 设置元数据（取第一个字段的元数据作为代表）
                        if field_meta is None:
                            field_meta = _extract_field_meta(field)
            else:
                # 普通文档，直接提取
                field_data = _extract_field_value(doc)
                if field_data:
                    field_value_list.append(field_data)
                    
                    if field_meta is None:
                        field_meta = _extract_field_meta(doc)
        
        # 如果是findOne，只返回第一个结果
        if query_type == "findOne":
            field_value = field_value_list[0] if field_value_list else {}
        else:
            field_value = field_value_list
            
        return {
            "type": "明细", 
            "field_value": field_value,
            "field_meta": field_meta or {}
        }
    
    else:
        # 默认返回明细类型
        return {
            "type": "明细",
            "field_value": result_data,
            "field_meta": {}
        }

def _extract_field_value(field_doc: Dict[str, Any]) -> Dict[str, Any]:
    """
    从字段文档中提取字段数据值部分
    
    Args:
        field_doc: 字段文档
        
    Returns:
        字段数据值字典
    """
    field_value = {}
    
    # 提取字段数据值相关字段
    value_fields = [
        "value", "value_text", "value_pic_url", 
        "value_doc_url", "value_video_url"
    ]
    
    for field_name in value_fields:
        if field_name in field_doc:
            field_value[field_name] = field_doc[field_name]
    
    return field_value

def _extract_field_meta(field_doc: Dict[str, Any]) -> Dict[str, Any]:
    """
    从字段文档中提取元数据部分
    
    Args:
        field_doc: 字段文档
        
    Returns:
        元数据字典
    """
    field_meta = {}
    
    # 提取元数据相关字段
    meta_fields = [
        "remark", "data_url", "is_required", "data_source",
        "encoding", "format", "license", "rights", 
        "update_frequency", "value_dict"
    ]
    
    for field_name in meta_fields:
        if field_name in field_doc:
            field_meta[field_name] = field_doc[field_name]
    
    return field_meta

# 辅助函数实现
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
        return "aggregate"
    elif ".countdocuments(" in query_cmd_clean:  # 新增：countDocuments 支持
        return "countDocuments"
    elif ".count(" in query_cmd_clean:
        return "count"
    elif ".distinct(" in query_cmd_clean:
        return "distinct"
    
    return None

def _fix_query_syntax(query_cmd: str) -> str:
    """
    修复查询语句的语法问题
    
    Args:
        query_cmd: 原始查询命令
        
    Returns:
        修复后的查询命令
    """
    # 移除前后空白字符
    fixed_query = query_cmd.strip()
    
    # 括号匹配检查和修复
    open_brackets = fixed_query.count('(')
    close_brackets = fixed_query.count(')')
    if open_brackets > close_brackets:
        fixed_query += ')' * (open_brackets - close_brackets)
    
    open_braces = fixed_query.count('{')
    close_braces = fixed_query.count('}')
    if open_braces > close_braces:
        fixed_query += '}' * (open_braces - close_braces)
    
    open_squares = fixed_query.count('[')
    close_squares = fixed_query.count(']')
    if open_squares > close_squares:
        fixed_query += ']' * (open_squares - close_squares)
    
    # JSON引号修复：将单引号替换为双引号（在字符串内容中）
    fixed_query = re.sub(r"'([^']*)'", r'"\1"', fixed_query)
    
    # 字段名标准化：为未加引号的字段名添加双引号
    fixed_query = re.sub(r'([{,]\s*)([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'\1"\2":', fixed_query)
    
    # 修复缺失的逗号（简单情况）
    fixed_query = re.sub(r'}\s*{', '},{', fixed_query)
    fixed_query = re.sub(r']\s*\[', '],[', fixed_query)
    print(f"--> fixed_query:{fixed_query}")
    return fixed_query

def _parse_query_parameters(query_cmd: str, query_type: str) -> Tuple[Optional[str], Dict[str, Any]]:
    """
    解析查询参数
    
    Args:
        query_cmd: 查询命令
        query_type: 查询类型
        
    Returns:
        (集合名(始终返回None表示使用配置的默认集合), 查询参数字典)
    """
    # 重要：不再解析集合名，始终返回None表示使用配置文件中的默认集合
    # 这样可以确保使用配置文件中的 "一企一档" 集合
    collection_name = None  # 让MongoDB管理器使用配置的默认集合
    
    try:
        # 根据查询类型提取参数
        if query_type in ["find", "findOne"]:
            # 提取find/findOne的参数
            match = re.search(rf'\.{query_type}\((.*)\)', query_cmd, re.DOTALL)
            if match:
                params_str = match.group(1).strip()
                if params_str:
                    # 尝试解析JSON参数
                    try:
                        # 简单处理：如果有多个参数，取第一个作为filter
                        if ',' in params_str:
                            filter_part = params_str.split(',')[0].strip()
                        else:
                            filter_part = params_str
                        
                        filter_dict = json.loads(filter_part) if filter_part else {}
                        return collection_name, {"filter": filter_dict}
                    except json.JSONDecodeError:
                        return collection_name, {"filter": {}}
                else:
                    return collection_name, {"filter": {}}
        
        elif query_type == "aggregate":
            # 提取aggregate的pipeline参数
            match = re.search(r'\.aggregate\((.*)\)', query_cmd, re.DOTALL)
            if match:
                params_str = match.group(1).strip()
                if params_str:
                    try:
                        pipeline = json.loads(params_str)
                        return collection_name, {"pipeline": pipeline}
                    except json.JSONDecodeError:
                        return collection_name, {"pipeline": []}
                else:
                    return collection_name, {"pipeline": []}
        
        elif query_type in ["count", "countDocuments"]:  # 支持 countDocuments
            # 提取count/countDocuments的参数
            if query_type == "countDocuments":
                match = re.search(r'\.countDocuments\((.*)\)', query_cmd, re.DOTALL)
            else:
                match = re.search(r'\.count\((.*)\)', query_cmd, re.DOTALL)
                
            if match:
                params_str = match.group(1).strip()
                if params_str:
                    try:
                        filter_dict = json.loads(params_str)
                        return collection_name, {"filter": filter_dict}
                    except json.JSONDecodeError:
                        return collection_name, {"filter": {}}
                else:
                    return collection_name, {"filter": {}}
        
        elif query_type == "distinct":
            # 提取distinct的参数
            match = re.search(r'\.distinct\((.*)\)', query_cmd, re.DOTALL)
            if match:
                params_str = match.group(1).strip()
                params_list = [p.strip(' "\'') for p in params_str.split(',')]
                field_name = params_list[0] if params_list else ""
                filter_dict = {}
                if len(params_list) > 1:
                    try:
                        filter_dict = json.loads(params_list[1])
                    except json.JSONDecodeError:
                        pass
                
                return collection_name, {"field": field_name, "filter": filter_dict}
        
        return collection_name, {}
        
    except Exception as e:
        log_error("解析查询参数失败", exception=e)
        return collection_name, {}

async def _execute_mongodb_query(
    manager: MongoDBManager, 
    query_type: str, 
    query_params: Dict[str, Any]
) -> Tuple[List[Dict[str, Any]], int]:
    """
    执行MongoDB查询
    
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
            cursor = collection.find(filter_dict).limit(1000)
            result_data = await cursor.to_list(length=1000)
            
        elif query_type == "findOne":
            filter_dict = query_params.get("filter", {})
            
            # findOne只返回一个文档
            doc = await collection.find_one(filter_dict)
            result_data = [doc] if doc else []
            total_count = 1 if doc else 0
            
        elif query_type == "aggregate":
            pipeline = query_params.get("pipeline", [])
            
            # 执行聚合查询
            cursor = collection.aggregate(pipeline)
            result_data = await cursor.to_list(length=1000)
            total_count = len(result_data)
            
        elif query_type in ["count", "countDocuments"]:  # 支持 countDocuments
            filter_dict = query_params.get("filter", {})
            
            # 执行计数查询
            count_result = await collection.count_documents(filter_dict)
            result_data = [{"count": count_result}]
            total_count = 1  # 保持原逻辑：对于count查询，total_count返回1
            
        elif query_type == "distinct":
            field_name = query_params.get("field", "")
            filter_dict = query_params.get("filter", {})
            
            if not field_name:
                raise Exception("distinct查询缺少字段名")
            
            # 执行去重查询
            distinct_values = await collection.distinct(field_name, filter_dict)
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
