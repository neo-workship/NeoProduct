# services/mongodb_service/mongodb_manager.py
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection
from pymongo.errors import DuplicateKeyError, ServerSelectionTimeoutError
from typing import Dict, Any, Optional, List,Tuple
from datetime import datetime
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# from common.exception_handler import log_info, log_error, safe
from mongo_exception_handler import log_info, log_error, safe

class MongoDBManager:
    """
    MongoDB异步操作管理器
    
    使用Motor库实现异步MongoDB操作，提供连接管理、文档操作等功能。
    所有操作都经过异常处理和日志记录。
    """
    
    def __init__(self, connection_string: str, collection_name: str = "default_collection"):
        """
        初始化MongoDB管理器
        
        Args:
            connection_string: MongoDB连接字符串
            collection_name: 集合名称
        """
        self.connection_string = connection_string
        self.collection_name = collection_name
        self.client: Optional[AsyncIOMotorClient] = None
        self.database: Optional[AsyncIOMotorDatabase] = None
        self.collection: Optional[AsyncIOMotorCollection] = None
        
        log_info(f"MongoDB管理器初始化", 
                extra_data=f'{{"collection": "{collection_name}"}}')
    
    async def connect(self) -> bool:
        """
        连接到MongoDB数据库
        
        Returns:
            bool: 连接是否成功
        """
        try:
            log_info("正在连接MongoDB...")
            
            # 创建异步客户端
            self.client = AsyncIOMotorClient(
                self.connection_string,
                serverSelectionTimeoutMS=30000,  # 30秒超时
                connectTimeoutMS=30000,
                socketTimeoutMS=30000,
                maxPoolSize=50,  # 最大连接池大小
                minPoolSize=1,   # 最小连接池大小
                maxIdleTimeMS=60000  # 最大空闲时间60秒
            )
            
            # 从连接字符串中提取数据库名
            # 格式: mongodb://[username:password@]host:port/database[?options]
            if "/" in self.connection_string.split("://")[1]:
                db_name = self.connection_string.split("/")[-1].split("?")[0]
            else:
                db_name = "test"  # 默认数据库
            
            self.database = self.client[db_name]
            self.collection = self.database[self.collection_name]
            
            # 测试连接
            await self.client.admin.command('ping')
            
            log_info("MongoDB连接成功", 
                    extra_data=f'{{"database": "{db_name}", "collection": "{self.collection_name}"}}')
            
            return True
            
        except ServerSelectionTimeoutError as e:
            log_error("MongoDB连接超时", exception=e)
            return False
        except Exception as e:
            log_error("MongoDB连接失败", exception=e)
            return False
    
    async def disconnect(self):
        """断开MongoDB连接"""
        try:
            if self.client:
                self.client.close()
                log_info("MongoDB连接已断开")
        except Exception as e:
            log_error("MongoDB断开连接时出错", exception=e)
    
    async def ping(self) -> bool:
        """
        测试数据库连接
        
        Returns:
            bool: 连接是否可用
        """
        try:
            if not self.client:
                return False
            
            await self.client.admin.command('ping')
            return True
        except Exception as e:
            log_error("MongoDB ping失败", exception=e)
            return False
    
    async def insert_document(self, document: Dict[str, Any]) -> Optional[str]:
        """
        插入单个文档
        
        Args:
            document: 要插入的文档
            
        Returns:
            Optional[str]: 插入成功返回文档ID，失败返回None
        """
        try:
            if not self.collection:
                log_error("MongoDB集合未初始化")
                return None
            
            # 添加时间戳
            document["created_at"] = self.get_current_timestamp()
            document["updated_at"] = self.get_current_timestamp()
            
            result = await self.collection.insert_one(document)
            
            doc_id = str(result.inserted_id)
            log_info(f"文档插入成功", extra_data=f'{{"document_id": "{doc_id}"}}')
            
            return doc_id
            
        except DuplicateKeyError as e:
            log_error("文档插入失败：主键重复", exception=e)
            return None
        except Exception as e:
            log_error("文档插入失败", exception=e)
            return None
    
    async def insert_document_with_id(self, document_id: str, document: Dict[str, Any]) -> bool:
        """
        使用指定ID插入文档
        
        Args:
            document_id: 指定的文档ID
            document: 要插入的文档
            
        Returns:
            bool: 插入是否成功
        """
        try:
            if self.collection is None:
                log_error("MongoDB集合未初始化")
                return False
            
            # 设置指定的_id
            document["_id"] = document_id
            document["created_at"] = self.get_current_timestamp()
            document["updated_at"] = self.get_current_timestamp()
            
            # 使用upsert=True，如果文档存在则更新，不存在则插入
            result = await self.collection.replace_one(
                {"_id": document_id}, 
                document, 
                upsert=True
            )
            
            if result.upserted_id is not None:
                log_info(f"文档插入成功", extra_data=f'{{"document_id": "{document_id}"}}')
            elif result.modified_count > 0:
                log_info(f"文档更新成功", extra_data=f'{{"document_id": "{document_id}"}}')
            else:
                log_info(f"文档无变化", extra_data=f'{{"document_id": "{document_id}"}}')
            
            return True
            
        except Exception as e:
            log_error("文档插入/更新失败", exception=e, 
                     extra_data=f'{{"document_id": "{document_id}"}}')
            return False
    
    async def find_document_by_id(self, document_id: str) -> Optional[Dict[str, Any]]:
        """
        根据ID查找文档
        
        Args:
            document_id: 文档ID
            
        Returns:
            Optional[Dict]: 找到的文档，未找到返回None
        """
        try:
            if self.collection is None:
                log_error("MongoDB集合未初始化")
                return None
            
            document = await self.collection.find_one({"_id": document_id})
            
            if document:
                log_info(f"文档查找成功", extra_data=f'{{"document_id": "{document_id}"}}')
                return document
            else:
                log_info(f"文档未找到", extra_data=f'{{"document_id": "{document_id}"}}')
                return None
                
        except Exception as e:
            log_error("文档查找失败", exception=e, 
                     extra_data=f'{{"document_id": "{document_id}"}}')
            return None
    
    async def find_documents(self, filter_dict: Optional[Dict[str, Any]] = None, 
                           limit: int = 100, skip: int = 0) -> List[Dict[str, Any]]:
        """
        查找多个文档
        
        Args:
            filter_dict: 查询过滤条件
            limit: 限制返回数量
            skip: 跳过数量
            
        Returns:
            List[Dict]: 文档列表
        """
        try:
            if self.collection is None:
                log_error("MongoDB集合未初始化")
                return []
            
            filter_dict = filter_dict or {}
            
            cursor = self.collection.find(filter_dict).skip(skip).limit(limit)
            documents = await cursor.to_list(length=limit)
            
            log_info(f"文档查找成功", 
                    extra_data=f'{{"count": {len(documents)}, "filter": "{str(filter_dict)}"}}')
            
            return documents
            
        except Exception as e:
            log_error("文档查找失败", exception=e, 
                     extra_data=f'{{"filter": "{str(filter_dict)}"}}')
            return []
    
    async def count_documents(self, filter_dict: Optional[Dict[str, Any]] = None) -> int:
        """
        统计文档数量
        
        Args:
            filter_dict: 查询过滤条件
            
        Returns:
            int: 文档数量
        """
        try:
            if self.collection is None:
                log_error("MongoDB集合未初始化")
                return 0
            
            filter_dict = filter_dict or {}
            count = await self.collection.count_documents(filter_dict)
            
            log_info(f"文档统计完成", 
                    extra_data=f'{{"count": {count}, "filter": "{str(filter_dict)}"}}')
            
            return count
            
        except Exception as e:
            log_error("文档统计失败", exception=e)
            return 0
    
    async def update_document(self, document_id: str, update_data: Dict[str, Any]) -> bool:
        """
        更新文档
        
        Args:
            document_id: 文档ID
            update_data: 更新数据
            
        Returns:
            bool: 更新是否成功
        """
        try:
            if self.collection is None:
                log_error("MongoDB集合未初始化")
                return False
            
            # 添加更新时间
            update_data["updated_at"] = self.get_current_timestamp()
            
            result = await self.collection.update_one(
                {"_id": document_id},
                {"$set": update_data}
            )
            
            if result.modified_count > 0:
                log_info(f"文档更新成功", extra_data=f'{{"document_id": "{document_id}"}}')
                return True
            else:
                log_info(f"文档无需更新", extra_data=f'{{"document_id": "{document_id}"}}')
                return True
                
        except Exception as e:
            log_error("文档更新失败", exception=e, 
                     extra_data=f'{{"document_id": "{document_id}"}}')
            return False
    
    async def delete_document(self, document_id: str) -> bool:
        """
        删除文档
        
        Args:
            document_id: 文档ID
            
        Returns:
            bool: 删除是否成功
        """
        try:
            if self.collection is None:
                log_error("MongoDB集合未初始化")
                return False
            
            result = await self.collection.delete_one({"_id": document_id})
            
            if result.deleted_count > 0:
                log_info(f"文档删除成功", extra_data=f'{{"document_id": "{document_id}"}}')
                return True
            else:
                log_info(f"文档不存在，无需删除", extra_data=f'{{"document_id": "{document_id}"}}')
                return False
                
        except Exception as e:
            log_error("文档删除失败", exception=e, 
                     extra_data=f'{{"document_id": "{document_id}"}}')
            return False

    async def delete_many_documents(self, filter_query: Dict[str, Any]) -> Dict[str, Any]:
        """
        批量删除多个文档
        
        Args:
            filter_query: 删除条件查询字典
            
        Returns:
            Dict[str, Any]: 删除结果信息，包含成功状态、删除数量等
        """
        try:
            if self.collection is None:
                log_error("MongoDB集合未初始化")
                return {
                    "success": False,
                    "deleted_count": 0,
                    "message": "MongoDB集合未初始化"
                }
            
            # 验证查询条件
            if not filter_query:
                log_error("删除条件不能为空")
                return {
                    "success": False,
                    "deleted_count": 0,
                    "message": "删除条件不能为空"
                }
            
            # 先查询要删除的文档数量（用于日志记录）
            count_before = await self.collection.count_documents(filter_query)
            
            if count_before == 0:
                log_info("没有找到符合条件的文档", 
                        extra_data=f'{{"filter_query": {filter_query}}}')
                return {
                    "success": True,
                    "deleted_count": 0,
                    "message": "没有找到符合条件的文档"
                }
            
            # 执行批量删除
            result = await self.collection.delete_many(filter_query)
            deleted_count = result.deleted_count
            
            if deleted_count > 0:
                log_info(f"批量删除文档成功", 
                        extra_data=f'{{"deleted_count": {deleted_count}, "filter_query": {filter_query}}}')
                return {
                    "success": True,
                    "deleted_count": deleted_count,
                    "message": f"成功删除 {deleted_count} 个文档"
                }
            else:
                log_info("没有文档被删除", 
                        extra_data=f'{{"filter_query": {filter_query}}}')
                return {
                    "success": True,
                    "deleted_count": 0,
                    "message": "没有文档被删除"
                }
                
        except Exception as e:
            log_error("批量删除文档失败", exception=e, 
                    extra_data=f'{{"filter_query": {filter_query}}}')
            return {
                "success": False,
                "deleted_count": 0,
                "message": f"批量删除失败: {str(e)}"
            } 
        
    def get_current_timestamp(self) -> str:
        """
        获取当前时间戳字符串
        
        Returns:
            str: ISO格式的时间戳
        """
        return datetime.now().isoformat()
    
    async def create_index(self, index_spec: Dict[str, Any], **kwargs) -> bool:
        """
        创建索引
        
        Args:
            index_spec: 索引规格
            **kwargs: 其他索引选项
            
        Returns:
            bool: 创建是否成功
        """
        try:
            if self.collection is None:
                log_error("MongoDB集合未初始化")
                return False
            
            index_name = await self.collection.create_index(index_spec, **kwargs)
            
            log_info(f"索引创建成功", 
                    extra_data=f'{{"index_name": "{index_name}", "spec": "{str(index_spec)}"}}')
            
            return True
            
        except Exception as e:
            log_error("索引创建失败", exception=e, 
                     extra_data=f'{{"spec": "{str(index_spec)}"}}')
            return False
    
    async def get_database_stats(self) -> Optional[Dict[str, Any]]:
        """
        获取数据库统计信息
        
        Returns:
            Optional[Dict]: 数据库统计信息
        """
        try:
            if not self.database:
                log_error("MongoDB数据库未初始化")
                return None
            
            stats = await self.database.command("dbStats")
            
            log_info("数据库统计信息获取成功")
            
            return {
                "database": stats.get("db"),
                "collections": stats.get("collections"),
                "dataSize": stats.get("dataSize"),
                "storageSize": stats.get("storageSize"),
                "indexes": stats.get("indexes"),
                "indexSize": stats.get("indexSize")
            }
            
        except Exception as e:
            log_error("获取数据库统计信息失败", exception=e)
            return None
        
    async def search_enterprises_by_text(self, search_text: str, limit: int = 10) -> Tuple[List[Dict[str, Any]], int]:
        """
        根据企业代码或企业名称进行模糊搜索
        
        Args:
            search_text: 搜索关键词
            limit: 返回结果数量限制
            
        Returns:
            Tuple[List[Dict], int]: (匹配的文档列表, 总匹配数量)
        """
        try:
            if self.collection is None:
                log_error("MongoDB集合未初始化")
                return [], 0
            
            # 构建模糊查询条件
            search_pattern = {"$regex": search_text, "$options": "i"}  # i表示忽略大小写
            
            filter_dict = {
                "$or": [
                    {"enterprise_code": search_pattern},
                    {"enterprise_name": search_pattern}
                ]
            }
            
            # 只返回需要的字段以提高性能
            projection = {
                "_id": 1,
                "enterprise_code": 1,
                "enterprise_name": 1
            }
            
            # 执行查询
            cursor = self.collection.find(filter_dict, projection).limit(limit)
            documents = await cursor.to_list(length=limit)
            
            # 获取总数
            total_count = await self.collection.count_documents(filter_dict)
            
            log_info(f"企业搜索查询完成", 
                    extra_data=f'{{"search_text": "{search_text}", "found_count": {len(documents)}, "total_count": {total_count}}}')
            
            return documents, total_count
            
        except Exception as e:
            log_error("企业搜索查询失败", exception=e,
                    extra_data=f'{{"search_text": "{search_text}"}}')
            return [], 0
        
    async def query_fields_by_path_and_codes(self, enterprise_code: str, path_code: str, field_codes: Optional[List[str]] = None) -> Tuple[List[Dict[str, Any]], int]:
        """
        根据企业代码、路径代码和字段代码列表查询字段
        
        Args:
            enterprise_code: 企业代码
            path_code: 层级路径代码
            field_codes: 字段代码列表，为空时查询路径下所有字段
            
        Returns:
            Tuple[List[Dict], int]: (匹配的字段列表, 总匹配数量)
        """
        try:
            if self.collection is None:
                log_error("MongoDB集合未初始化")
                return [], 0
            
            # 构建基础查询条件
            base_filter = {
                "_id": enterprise_code,
            }
            
            # 构建聚合管道
            pipeline = [
                # 匹配企业文档
                {"$match": base_filter},
                
                # 展开fields数组
                {"$unwind": "$fields"},
                
                # 构建字段匹配条件
                {
                    "$match": {
                        "fields.path_code": path_code
                    }
                }
            ]
            
            # 如果指定了字段代码列表，则添加字段代码过滤条件
            if field_codes and len(field_codes) > 0:
                pipeline.append({
                    "$match": {
                        "fields.field_code": {"$in": field_codes}
                    }
                })
            
            # 投影需要的字段
            pipeline.append({
                "$project": {
                    "_id": 0,
                    "full_path_name": "$fields.full_path_name",
                    "value": "$fields.value",
                    "value_pic_url": "$fields.value_pic_url",
                    "value_doc_url": "$fields.value_doc_url",
                    "value_video_url": "$fields.value_video_url",
                    "data_url": "$fields.data_url",
                    "encoding": "$fields.encoding",
                    "format": "$fields.format",
                    "license": "$fields.license",
                    "rights": "$fields.rights",
                    "update_frequency": "$fields.update_frequency",
                    "value_dict": "$fields.value_dict",
                    # 额外包含一些可能有用的字段
                    "field_code": "$fields.field_code",
                    "field_name": "$fields.field_name",
                    "full_path_code": "$fields.full_path_code",
                    "path_code": "$fields.path_code"
                }
            })
            
            # 执行聚合查询
            cursor = self.collection.aggregate(pipeline)
            results = await cursor.to_list(length=None)
            
            # 统计总数
            total_count = len(results)
            
            log_info(f"字段查询完成", 
                    extra_data=f'{{"enterprise_code": "{enterprise_code}", "path_code": "{path_code}", "field_codes": {field_codes}, "found_count": {total_count}}}')
            
            return results, total_count
            
        except Exception as e:
            log_error("字段查询失败", exception=e,
                    extra_data=f'{{"enterprise_code": "{enterprise_code}", "path_code": "{path_code}", "field_codes": {field_codes}}}')
            return [], 0
