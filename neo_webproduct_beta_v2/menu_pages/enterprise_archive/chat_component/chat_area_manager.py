from abc import ABC, abstractmethod
import asyncio
import aiohttp
import re
from datetime import datetime
from nicegui import ui, app
from typing import Optional, List, Dict, Any
from component import static_manager
from .chat_data_state import ChatDataState
from .markdown_ui_parser import MarkdownUIParser

class ThinkContentParser:
    """思考内容解析器 - 专门处理<think>标签"""
    
    def __init__(self):
        self.is_in_think = False
        self.think_start_pos = -1
        self.think_content = ""
    
    def parse_chunk(self, full_content: str) -> Dict[str, Any]:
        """解析内容块，返回处理结果"""
        result = {
            'has_think': False,
            'think_content': '',
            'display_content': full_content,
            'think_complete': False,
            'think_updated': False
        }
        
        # 检测思考开始
        if '<think>' in full_content and not self.is_in_think:
            self.is_in_think = True
            self.think_start_pos = full_content.find('<think>')
            result['has_think'] = True
        
        # 检测思考结束
        if '</think>' in full_content and self.is_in_think:
            think_end_pos = full_content.find('</think>') + 8
            self.think_content = full_content[self.think_start_pos + 7:think_end_pos - 8]
            result['display_content'] = full_content[:self.think_start_pos] + full_content[think_end_pos:]
            result['think_content'] = self.think_content.strip()
            result['think_complete'] = True
            self.is_in_think = False
        elif self.is_in_think:
            # 正在思考中
            if self.think_start_pos >= 0:
                current_think = full_content[self.think_start_pos + 7:]
                result['display_content'] = full_content[:self.think_start_pos]
                result['think_content'] = current_think.strip()
                result['think_updated'] = True
        
        result['has_think'] = self.think_start_pos >= 0
        return result

class MessagePreprocessor:
    """消息预处理器"""
    
    def __init__(self, chat_data_state):
        self.chat_data_state = chat_data_state
    
    def enhance_user_message(self, user_message: str) -> str:
        """增强用户消息（原有逻辑保持不变）"""
        try:
            if not self.chat_data_state.switch:
                return user_message
                
            if not (self.chat_data_state.current_state.prompt_select_widget and 
                    self.chat_data_state.current_state.prompt_select_widget.value == "一企一档专家"):
                ui.notify("上下文模板未选择'一企一档专家'", type="warning")
                return user_message
                
            selected_values = self.chat_data_state.selected_values
            if not (selected_values and selected_values['l3']):
                ui.notify("未选择足够的层级数据（至少需要3级）", type="warning")
                return user_message
                
            append_text = ""
            if selected_values['field']:
                full_path_code = selected_values['full_path_name']
                field_value = selected_values['field_name']
                append_text = f"\n\n 满足在一个子文档中：[path_name] = {'.'.join(full_path_code.split('.')[:3])} 且 [field_name] in {field_value}"
            else:
                full_path_code = selected_values['full_path_name']
                append_text = f"\n\n[path_name] = {full_path_code}"
            
            if append_text:
                return f"{user_message}{append_text}"
                
            return user_message
    
        except Exception as e:
            ui.notify(f"[ERROR] 增强用户消息时发生异常: {e}", type="negative")
            return user_message

class AIClientManager:
    """AI客户端管理器"""
    
    def __init__(self, chat_data_state):
        self.chat_data_state = chat_data_state
    
    async def get_client(self):
        """获取AI客户端"""
        from common.safe_openai_client_pool import get_openai_client
        
        selected_model = self.chat_data_state.current_model_config['selected_model']
        model_config = self.chat_data_state.current_model_config['config']
        
        client = await get_openai_client(selected_model, model_config)
        if not client:
            raise Exception(f"无法连接到模型 {selected_model}")
        
        return client, model_config
    
    def prepare_messages(self,user_msg_dict:Dict ) -> List[Dict[str, str]]:
        """准备发送给AI的消息列表"""
        # 默认情况下，使用最近的5条聊天记录
        recent_messages = self.chat_data_state.current_chat_messages[-5:]
        
        # 如果 selected_prompt 是 '一企一档专家'，则清空历史聊天记录
        if self.chat_data_state.current_prompt_config.selected_prompt == '一企一档专家':
            recent_messages = [user_msg_dict]
        
        if (self.chat_data_state.current_state.prompt_select_widget and 
            self.chat_data_state.current_prompt_config.system_prompt):
            system_message = {
                "role": "system", 
                "content": self.chat_data_state.current_prompt_config.system_prompt
            }
            recent_messages = [system_message] + recent_messages
        
        return recent_messages

class ContentDisplayStrategy(ABC):
    """内容展示策略抽象基类"""
    def __init__(self, ui_components):
        self.ui_components = ui_components
        self.think_parser = ThinkContentParser()
        self.structure_created = False
        self.reply_created = False
        self.think_expansion = None
        self.think_label = None
        self.reply_label = None
        self.chat_content_container = None
    
    @abstractmethod
    def create_ui_structure(self, has_think: bool):
        """创建UI结构"""
        pass
    
    @abstractmethod
    def update_content(self, parse_result: Dict[str, Any]) -> bool:
        """更新内容显示，返回是否需要滚动"""
        pass
    
    def process_stream_chunk(self, full_content: str) -> bool:
        """处理流式数据块 - 模板方法"""
        parse_result = self.think_parser.parse_chunk(full_content)
        
        # 创建UI结构（如果需要）
        if not self.structure_created:
            self.create_ui_structure(parse_result['has_think'])
            self.structure_created = True
        
        # 更新内容
        need_scroll = self.update_content(parse_result)
        return need_scroll
    
    async def finalize_content(self, final_content: str):
        """完成内容显示"""
        final_result = self.think_parser.parse_chunk(final_content)
        
        if final_result['think_complete'] and self.think_label:
            self.think_label.set_text(final_result['think_content'])
        
        if self.reply_label and final_result['display_content'].strip():
            self.reply_label.set_content(final_result['display_content'].strip())
            # 调用markdown优化显示
            if hasattr(self.ui_components, 'markdown_parser'):
                await self.ui_components.markdown_parser.optimize_content_display(
                    self.reply_label, final_result['display_content'], self.chat_content_container
                )

class DefaultDisplayStrategy(ContentDisplayStrategy):
    """默认展示策略"""
    
    def create_ui_structure(self, has_think: bool):
        """创建默认UI结构"""
        self.ui_components.waiting_ai_message_container.clear()
        with self.ui_components.waiting_ai_message_container:
            with ui.column().classes('w-full') as self.chat_content_container:
                if has_think:
                    self.think_expansion = ui.expansion(
                        '💭 AI思考过程...(可点击打开查看)', 
                        icon='psychology'
                    ).classes('w-full mb-2')
                    with self.think_expansion:
                        self.think_label = ui.label('').classes(
                            'whitespace-pre-wrap bg-[#81c784] border-0 shadow-none rounded-none'
                        )
                else:
                    self.reply_label = ui.markdown('').classes('w-full')
                    self.reply_created = True
    
    def update_content(self, parse_result: Dict[str, Any]) -> bool:
        """更新默认展示内容"""
        if parse_result['think_updated'] and self.think_label:
            self.think_label.set_text(parse_result['think_content'])
        
        if parse_result['think_complete']:
            # 思考完成，创建回复组件
            if self.chat_content_container and not self.reply_created:
                with self.chat_content_container:
                    self.reply_label = ui.markdown('').classes('w-full')
                self.reply_created = True
            
            if self.think_label:
                self.think_label.set_text(parse_result['think_content'])
        
        # 更新显示内容
        if self.reply_label and parse_result['display_content'].strip():
            with self.chat_content_container:
                self.reply_label.set_content(parse_result['display_content'].strip())
        
        return True  # 需要滚动

class ExpertDisplayStrategy(ContentDisplayStrategy):
    """专家模式展示策略 - 支持MongoDB查询检测和执行"""
    
    def __init__(self, chat_area_manager):
        super().__init__(chat_area_manager)
        self.query_result_label = None
        self.mongodb_api_base = "http://localhost:8001"  # MongoDB服务API地址，与项目中一致
    
    def create_ui_structure(self, has_think: bool):
        """创建专家模式UI结构"""
        self.ui_components.waiting_ai_message_container.clear()
        with self.ui_components.waiting_ai_message_container:
            with ui.column().classes('w-full') as self.chat_content_container:
                if has_think:
                    # 专家模式思考区域
                    self.think_expansion = ui.expansion(
                        '🧠 专家思考分析...(点击查看详细分析)', 
                        icon='psychology'
                    ).classes('w-full mb-2')
                    with self.think_expansion:
                        self.think_label = ui.label('').classes(
                            'whitespace-pre-wrap bg-[#81c784] border-l-4 border-blue-500 p-3'
                        )
                else:
                    self.reply_label = ui.markdown('').classes('w-full')
                    self.reply_created = True
    
    def _detect_mongodb_query(self, content: str) -> Optional[str]:
        """
        简单检测MongoDB查询语句
        返回检测到的查询语句，如果没有检测到则返回None
        """
        # 首先移除代码块标记
        cleaned_content = self._extract_from_code_blocks(content)
        
        # 扩展的MongoDB查询模式，支持更多查询格式
        patterns = [
            # 标准格式：db.collection.method()
            r'db\.\w+\.find\([^)]*\)',
            r'db\.\w+\.findOne\([^)]*\)',
            r'db\.\w+\.aggregate\([^)]*\)',
            r'db\.\w+\.count\([^)]*\)',
            r'db\.\w+\.countDocuments\([^)]*\)',  # 新增：countDocuments 模式
            r'db\.\w+\.distinct\([^)]*\)',
            
            # getCollection格式：db.getCollection('name').method()
            r'db\.getCollection\([\'"][^\'"]*[\'"]\)\.\w+\([^)]*\)',
            
            # 带链式调用的格式：db.collection.method().method()
            r'db\.\w+\.\w+\([^)]*\)\.\w+',
            r'db\.getCollection\([\'"][^\'"]*[\'"]\)\.\w+\([^)]*\)\.\w+',
            
            # 更复杂的链式调用
            r'db\.getCollection\([\'"][^\'"]*[\'"]\)\.distinct\([^)]*\)\.length',
            r'db\.\w+\.distinct\([^)]*\)\.length',
            r'db\.\w+\.countDocuments\([^)]*\)',  # 新增：直接 countDocuments 调用
            r'db\.getCollection\([\'"][^\'"]*[\'"]\)\.countDocuments\([^)]*\)',  # 新增：getCollection + countDocuments
        ]
        
        for pattern in patterns:
            match = re.search(pattern, cleaned_content, re.IGNORECASE | re.MULTILINE | re.DOTALL)
            if match:
                query = match.group(0).strip()
                # 进一步清理查询语句
                query = self._clean_query_string(query)
                return query
        
        return None
    
    def _extract_from_code_blocks(self, content: str) -> str:
        """
        从代码块中提取内容，移除 ``` 标记
        """
        # 匹配各种代码块格式
        code_block_patterns = [
            r'```javascript\s*(.*?)\s*```',
            r'```js\s*(.*?)\s*```', 
            r'```mongodb\s*(.*?)\s*```',
            r'```\s*(.*?)\s*```',  # 无语言标识的代码块
        ]
        
        for pattern in code_block_patterns:
            matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
            if matches:
                # 返回第一个匹配的代码块内容
                return matches[0].strip()
        
        # 如果没有代码块，返回原内容
        return content
    
    def _clean_query_string(self, query: str) -> str:
        """
        清理查询字符串，移除多余的空白字符
        """
        # 移除行首行尾空白
        query = query.strip()
        # 压缩多个空白字符为单个空格
        query = re.sub(r'\s+', ' ', query)
        return query
    
    async def _execute_mongodb_query(self, query_cmd: str) -> Dict[str, Any]:
        """
        调用MongoDB服务API执行查询 - 适应新格式
        """
        try:
            async with aiohttp.ClientSession() as session:
                # 构建请求数据
                request_data = {"query_cmd": query_cmd}
                
                async with session.post(
                    f"{self.mongodb_api_base}/api/v1/enterprises/execute_mongo_cmd",
                    json=request_data,
                    headers={'Content-Type': 'application/json'}
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        # 添加 success 字段以保持兼容性
                        result["success"] = (result.get("messages") == "正常处理")
                        return result
                    else:
                        error_text = await response.text()
                        # 返回与新API格式一致的错误响应
                        return {
                            "success": False,
                            "type": "错误",
                            "period": "0ms", 
                            "messages": f"API调用失败: HTTP {response.status}, response={error_text}",
                            "result_data": []
                        }
        except Exception as e:
            # 返回与新API格式一致的错误响应
            return {
                "success": False,
                "type": "错误",
                "period": "0ms",
                "messages": f"网络请求失败: {str(e)}",
                "result_data": []
            }
    
    # ------------------------ 各类数据的渲染展示 -----------------------------
    def _display_query_result(self, result: Dict[str, Any]):
        """
        显示MongoDB查询结果
        将原有的处理逻辑分解为独立的函数，提高代码可维护性
        
        Args:
            result: MongoDB查询结果字典
        """
        print(f"_display_query_result:{result},type result:{type(result)}")
        if not self.chat_content_container:
            return
        
        with self.chat_content_container:
            # 显示查询统计信息
            self._display_query_statistics(result)
            
            # 根据查询类型调用相应的显示函数
            if result.get("messages") == "正常处理":  # 查询成功
                query_type = result.get("type", "")
                result_data = result.get("result_data", [])
                structure_type = result.get("structure_type","")
                field_strategy = result.get("field_strategy","")
                print(f"---> result:{result}")
                print(f"---> query_type:{query_type} | result_structure:{structure_type} | field_strategy:{field_strategy}")
                if query_type == "汇总":
                    self._display_summary_result(result_data)
                elif query_type == "分组":
                    self._display_group_result(result_data)
                elif query_type == "明细":
                    self._display_detail_result(result_data,structure_type,field_strategy)
                else:
                    self._display_other_result(query_type, result_data)
            else:
                # 查询失败
                self._display_error_result(result)

    def _display_query_statistics(self, result: Dict[str, Any]):
        """
        显示查询统计信息
        
        Args:
            result: MongoDB查询结果字典
        """
        result_data = result.get('result_data', [])
        data_count = len(result_data) if isinstance(result_data, list) else 1
        
        stats_text = (
            f"<b>📊 查询统计:</b>\n"
            f"•<b>查询类型</b>:{result.get('type', 'N/A')} &nbsp;&nbsp;&nbsp;&nbsp; •<b>运行耗时</b>: {result.get('period', '0ms')} &nbsp;&nbsp;&nbsp;&nbsp; •<b>处理信息</b>: {result.get('messages', '未知')} &nbsp;&nbsp;&nbsp;&nbsp; •<b>数据数量</b>: {data_count}"
        )
        ui.html(stats_text).classes(
            'whitespace-pre-wrap w-full text-base bg-blue-50 border-l-4 border-blue-500 p-3 mb-2'
        )

    def _display_summary_result(self, result_data: List[Any]):
        """
        显示汇总查询结果
        
        Args:
            result_data: 汇总查询结果数据列表
        """
        if result_data and len(result_data) > 0:
            # 检查是否是简单数值
            info_text = "<b>🔢 汇总结果</b>:"
            if isinstance(result_data[0], (int, float)):
                result_text = f"{info_text}{result_data[0]}"
            else:
                result_text = f"{info_text}{str(result_data[0])}"
        else:
            result_text = f"{info_text}0"
        
        ui.html(result_text).classes(
            'w-full text-base bg-green-50 border-l-4 border-green-500 p-3 mb-2'
        )

    def _display_group_result(self, result_data: List[Dict[str, Any]]):
        """
        显示分组查询结果
        
        Args:
            result_data: 分组查询结果数据列表
        """
        if isinstance(result_data, list) and result_data:
            # 格式化显示分组数据
            display_count = min(10, len(result_data))  # 最多显示10个分组
            result_text = f"📊 分组统计结果 (显示前{display_count}组，共{len(result_data)}组):\n\n"
            
            for i, group_item in enumerate(result_data[:display_count]):
                result_text += f"📋 第 {i+1} 组:\n"
                
                if isinstance(group_item, dict):
                    # 处理分组标识 (_id)
                    group_id = group_item.get('_id', 'N/A')
                    if isinstance(group_id, dict):
                        # 多字段分组
                        result_text += f"  🔖 分组条件:\n"
                        for key, value in group_id.items():
                            result_text += f"    • {key}: {value}\n"
                    else:
                        # 单字段分组
                        result_text += f"  🔖 分组值: {group_id}\n"
                    
                    # 处理聚合统计字段
                    result_text += f"  📈 统计结果:\n"
                    for field_name, field_value in group_item.items():
                        if field_name != '_id':
                            # 格式化数值显示
                            if isinstance(field_value, (int, float)):
                                if isinstance(field_value, float):
                                    formatted_value = f"{field_value:.2f}"
                                else:
                                    formatted_value = f"{field_value:,}"
                            else:
                                formatted_value = str(field_value)
                            
                            result_text += f"    • {field_name}: {formatted_value}\n"
                else:
                    # 如果不是字典格式，直接显示
                    result_text += f"  • 内容: {str(group_item)}\n"
                
                result_text += "\n"
            
            if len(result_data) > display_count:
                result_text += f"... 还有 {len(result_data) - display_count} 个分组\n"
            
            ui.label(result_text).classes(
                'whitespace-pre-wrap bg-purple-50 border-l-4 border-purple-500 p-3 mb-2 w-full'
            )
            
            # 显示分组汇总统计
            self._display_group_summary(result_data)
            
        else:
            ui.label("📊 分组结果: 无数据").classes(
                'whitespace-pre-wrap bg-gray-50 border-l-4 border-gray-500 p-3 mb-2'
            )
    
    ### ------------------- 明细数据渲染展示 -------------------------
    def _display_detail_result(self, result_data: List[Dict[str, Any]], structure_type:str,field_strategy:str):
        """
        显示明细查询结果 - 基于field_strategy进行字段匹配展示
        根据数据条数选择不同的显示方式，同时考虑字段策略
        Args:
            result_data: 明细查询结果数据列表
            result: 完整的查询结果，包含field_strategy信息
        """
        if isinstance(result_data, list) and result_data:
            # 根据数据条数选择显示方式（完全借鉴read_archive_tab的逻辑）
            if structure_type == "single_data":
                self._display_detail_results_as_cards(result_data, structure_type,field_strategy)
            elif structure_type == "multi_data" :
                self._display_detail_results_as_table(result_data, structure_type,field_strategy)
        else:
            ui.label("🔍 明细查询结果: 无数据").classes(
                'whitespace-pre-wrap bg-gray-50 border-l-4 border-gray-500 p-3 mb-2'
        )

    def _display_detail_results_as_cards(self, result_data: List[Dict[str, Any]], structure_type: str, field_strategy: str):
        """
        用卡片方式展示明细查询结果
        根据field_strategy支持两种展示模式：
        - full_card: 按标准字段模板展示
        - flat_card: 简单循环展示所有字段
        
        Args:
            result_data: 明细查询结果数据列表
            result_structure: 结果结构类型
            field_strategy: 字段策略 ("full_card" 或 "flat_card")
        """
        if not result_data:
            ui.label("🔍 明细查询结果: 无数据").classes('whitespace-pre-wrap bg-gray-50 border-l-4 border-gray-500 p-3 mb-2')
            return
        
        
        ui.label(f'🔍 明细查询结果 (共{len(result_data)}条数据)').classes('text-base font-bold text-primary mb-3')
        
        # 根据字段策略选择不同的展示方式
        if field_strategy == "full_card":
            self._display_full_card_mode(result_data)
        else:  # flat_card 或其他情况
            self._display_flat_card_mode(result_data)

    def _display_full_card_mode(self, result_data: List[Dict[str, Any]]):
        """
        full_card模式：按标准字段模板展示（左右卡片布局）
        """
        for index, data_item in enumerate(result_data):
            with ui.row().classes('w-full gap-4 items-stretch mb-4'):
                # 左侧card展示：full_path_name、value、value_pic_url、value_doc_url、value_video_url
                with ui.card().classes('flex-1 p-4'):
                    ui.label('字段信息').classes('text-subtitle1 font-medium mb-3')
                    
                    # 字段完整名称（标题）
                    full_path_name = data_item.get('字段完整名称', data_item.get('字段名称', '未知字段'))
                    ui.label(full_path_name).classes('text-base font-bold text-primary mb-2')
                    
                    # 企业名称
                    if '企业名称' in data_item:
                        with ui.row().classes('w-full gap-2 items-center mb-2'):
                            ui.icon('business').classes('text-lg text-purple-600')
                            ui.label('企业名称:').classes('text-lg font-medium')
                            enterprise_name = data_item.get('企业名称', '暂无数据')
                            ui.label(enterprise_name).classes('text-lg text-grey-8')
                    
                    # 字段值
                    with ui.row().classes('w-full gap-2 items-center mb-2'):
                        ui.icon('data_object').classes('text-lg text-blue-600')
                        ui.label('字段值:').classes('text-lg font-medium')
                        value = data_item.get('字段值', '暂无数据') or '暂无数据'
                        ui.label(str(value)).classes('text-lg text-grey-8')
                    
                    # 字段关联图片
                    self._display_link_field('字段关联图片', data_item, 'image', 'text-green-600', '查看图片')
                    
                    # 字段关联文档
                    self._display_link_field('字段关联文档', data_item, 'description', 'text-orange-600', '查看文档')
                    
                    # 字段关联视频
                    self._display_link_field('字段关联视频', data_item, 'videocam', 'text-red-600', '查看视频')
                
                # 右侧card展示：data_url、encoding、format、license、rights、update_frequency、value_dict
                with ui.card().classes('flex-1 p-4'):
                    ui.label('数据属性').classes('text-subtitle1 font-medium mb-3')
                    
                    # 数据源url
                    self._display_link_field('数据源url', data_item, 'api', 'text-blue-500', '访问API')
                    
                    # 编码格式
                    self._display_text_field('编码格式', data_item, 'code', 'text-purple-500')
                    
                    # 数据格式
                    self._display_text_field('数据格式', data_item, 'article', 'text-teal-500')
                    
                    # 许可证
                    self._display_text_field('许可证', data_item, 'gavel', 'text-amber-500')
                    
                    # 使用权限
                    self._display_text_field('使用权限', data_item, 'security', 'text-red-500')
                    
                    # 更新频率
                    self._display_text_field('更新频率', data_item, 'update', 'text-blue-500')
                    
                    # 字典值选项
                    self._display_special_field('字典值选项', data_item, 'book', 'text-green-500')
            
            # 如果不是最后一条数据，添加分隔线
            if index < len(result_data) - 1:
                ui.separator().classes('my-4')

    def _display_flat_card_mode(self, result_data: List[Dict[str, Any]]):
        """
        flat_card模式：简单循环展示所有字段（单卡片布局）
        """
        for index, data_item in enumerate(result_data):
            with ui.card().classes('w-full p-4 mb-4'):
                ui.label(f'数据记录 {index + 1}').classes('text-subtitle1 font-medium mb-3')
                
                # 循环展示所有字段
                for key, value in data_item.items():
                    if key and value is not None:  # 跳过空键和None值
                        with ui.row().classes('w-full gap-2 items-center mb-2'):
                            # 根据字段类型选择合适的图标
                            icon_name = self._get_field_icon(key)
                            ui.icon(icon_name).classes('text-lg text-blue-600')
                            
                            # 显示字段名和值
                            ui.label(f'{key}:').classes('text-lg font-medium')
                            
                            # 处理不同类型的值
                            display_value = self._format_field_value(value)
                            
                            # 如果是URL，显示为链接
                            if self._is_url(display_value):
                                ui.link(text='查看链接', target=display_value).classes('text-lg text-blue-600')
                            else:
                                ui.label(display_value).classes('text-lg text-grey-8')
            
            # 如果不是最后一条数据，添加分隔线
            if index < len(result_data) - 1:
                ui.separator().classes('my-2')
        
        # 数据总结
        if len(result_data) > 1:
            ui.label(f'📊 数据总结: 共展示了 {len(result_data)} 条明细数据').classes(
                'text-sm text-grey-600 bg-blue-50 border-l-4 border-blue-400 p-2 mt-4'
            )

    def _display_link_field(self, field_name: str, data_item: Dict, icon: str, icon_color: str, link_text: str):
        """显示链接类型字段"""
        value = data_item.get(field_name, '')
        with ui.row().classes('w-full gap-2 items-center mb-2'):
            if value and value != '暂无数据' and self._is_url(str(value)):
                ui.icon(icon).classes(f'text-lg {icon_color}')
                ui.label(f'{field_name}:').classes('text-lg font-medium')
                ui.link(text=link_text, target=str(value)).classes('text-lg text-blue-600')
            else:
                ui.icon(icon).classes('text-lg text-grey-400')
                ui.label(f'{field_name}:').classes('text-lg font-medium')
                ui.label('暂无数据').classes('text-lg text-grey-6')

    def _display_text_field(self, field_name: str, data_item: Dict, icon: str, icon_color: str):
        """显示文本类型字段"""
        value = data_item.get(field_name, '暂无数据') or '暂无数据'
        with ui.row().classes('w-full gap-2 items-center mb-2'):
            ui.icon(icon).classes(f'text-lg {icon_color}')
            ui.label(f'{field_name}:').classes('text-lg font-medium')
            ui.label(str(value)).classes('text-lg text-grey-8')

    def _display_special_field(self, field_name: str, data_item: Dict, icon: str, icon_color: str):
        """显示特殊字段（如字典值选项，可能是字符串或链接）"""
        value = data_item.get(field_name, '')
        with ui.row().classes('w-full gap-2 items-center mb-2'):
            if value and value != '暂无数据':
                ui.icon(icon).classes(f'text-lg {icon_color}')
                ui.label(f'{field_name}:').classes('text-lg font-medium')
                # 如果是链接，显示为可点击链接
                if self._is_url(str(value)):
                    ui.link(text='查看字典', target=str(value)).classes('text-lg text-blue-600')
                else:
                    ui.label(str(value)).classes('text-lg text-grey-8')
            else:
                ui.icon(icon).classes('text-lg text-grey-400')
                ui.label(f'{field_name}:').classes('text-lg font-medium')
                ui.label('暂无数据').classes('text-lg text-grey-6')

    def _get_field_icon(self, field_name: str) -> str:
        """根据字段名返回合适的图标"""
        field_name_lower = field_name.lower()
        
        # 企业相关
        if any(keyword in field_name_lower for keyword in ['企业', '公司', 'enterprise', 'company']):
            return 'business'
        # 名称相关
        elif any(keyword in field_name_lower for keyword in ['名称', 'name']):
            return 'label'
        # 代码相关
        elif any(keyword in field_name_lower for keyword in ['代码', 'code']):
            return 'tag'
        # 值相关
        elif any(keyword in field_name_lower for keyword in ['值', 'value']):
            return 'data_object'
        # 时间相关
        elif any(keyword in field_name_lower for keyword in ['时间', 'time', '日期', 'date']):
            return 'schedule'
        # URL相关
        elif any(keyword in field_name_lower for keyword in ['url', '链接', '地址']):
            return 'link'
        # 图片相关
        elif any(keyword in field_name_lower for keyword in ['图片', '图像', 'pic', 'image']):
            return 'image'
        # 文档相关
        elif any(keyword in field_name_lower for keyword in ['文档', '文件', 'doc']):
            return 'description'
        # 视频相关
        elif any(keyword in field_name_lower for keyword in ['视频', 'video']):
            return 'videocam'
        # 默认
        else:
            return 'info'

    def _format_field_value(self, value: Any) -> str:
        """格式化字段值用于显示"""
        if value is None:
            return '暂无数据'
        elif value == '':
            return '暂无数据'
        elif isinstance(value, (dict, list)):
            return str(value)
        else:
            return str(value)

    def _is_url(self, value: str) -> bool:
        """判断字符串是否为URL"""
        if not isinstance(value, str):
            return False
        return value.startswith('http://') or value.startswith('https://')

    def _display_detail_results_as_table(self, result_data: List[Dict[str, Any]], result_structure: str, field_strategy: str):
        """
        用表格方式展示明细查询结果
        Args:
            result_data: 明细查询结果数据列表  
            result_structure: 结果结构类型
            field_strategy: 字段策略
        """
        if not result_data:
            ui.label("🔍 明细查询结果: 无数据").classes(
                'whitespace-pre-wrap bg-gray-50 border-l-4 border-gray-500 p-3 mb-2'
            )
            return
        # 如果 field_strategy == "full_table"
        if field_strategy == "full_table":
            self._display_full_table(result_data)
        else:
            # 简化表格显示
            self._display_simple_table(result_data)

    def _display_full_table(self, result_data: List[Dict[str, Any]]):
        """
        显示完整的表格
        Args:
            result_data: 查询结果数据列表
        """
        pass

    def _display_simple_table(self, result_data: List[Dict[str, Any]]):
        """
        显示简化的表格（当 field_strategy != "full_table" 时使用）
        Args:
            result_data: 查询结果数据列表
        """
        pass

    def _display_data_value_fields(self, data_value: Dict[str, Any], field_strategy: str, display_context: str = "left_card"):
        """
        根据field_strategy显示data_value字段（左侧card内容）
        
        Args:
            data_value: 数据值字典
            field_strategy: 字段策略 ("full_fields" 或 "existing_fields")
            display_context: 显示上下文标识
        """
        # full_path_name（标题）- 总是显示
        full_path_name = data_value.get('full_path_name', '未知字段')
        ui.label(full_path_name).classes('text-base font-bold text-primary mb-2')
        
        if field_strategy == "full_fields":
            # 显示完整字段集合，缺失的字段显示"暂无数据"
            self._display_full_data_value_fields(data_value)
        else:
            # 只显示实际存在的字段
            self._display_existing_data_value_fields(data_value)

    def _display_data_meta_fields(self, data_meta: Dict[str, Any], field_strategy: str, display_context: str = "right_card"):
        """
        根据field_strategy显示data_meta字段（右侧card内容）
        
        Args:
            data_meta: 元数据字典
            field_strategy: 字段策略 ("full_fields" 或 "existing_fields") 
            display_context: 显示上下文标识
        """
        if field_strategy == "full_fields":
            # 显示完整字段集合，缺失的字段显示"暂无数据"
            self._display_full_data_meta_fields(data_meta)
        else:
            # 只显示实际存在的字段
            self._display_existing_data_meta_fields(data_meta)

    def _display_full_data_value_fields(self, data_value: Dict[str, Any]):
        """显示完整的data_value字段集合（full_fields策略）"""
        # value（字段值）
        value = data_value.get('value', '暂无数据') or '暂无数据'
        with ui.row().classes('gap-2 items-center mb-2'):
            ui.icon('data_object').classes('text-lg text-blue-600')
            ui.label('字段值:').classes('text-lg font-medium')
            display_value = str(value)
            if len(display_value) > 50:
                display_value = display_value[:50] + "..."
            ui.label(display_value).classes('text-lg')
        
        # value_pic_url（字段关联图片）
        value_pic_url = data_value.get('value_pic_url', '') or ''
        with ui.row().classes('gap-2 items-center mb-2'):
            ui.icon('image').classes('text-lg text-green-600')
            ui.label('关联图片:').classes('text-lg font-medium')
            if value_pic_url:
                ui.link('查看图片', target=value_pic_url).classes('text-lg text-primary')
            else:
                ui.label('暂无数据').classes('text-lg text-grey-6')
        
        # value_doc_url（字段关联文档）
        value_doc_url = data_value.get('value_doc_url', '') or ''
        with ui.row().classes('gap-2 items-center mb-2'):
            ui.icon('description').classes('text-lg text-orange-600')
            ui.label('关联文档:').classes('text-lg font-medium')
            if value_doc_url:
                ui.link('查看文档', target=value_doc_url).classes('text-lg text-primary')
            else:
                ui.label('暂无数据').classes('text-lg text-grey-6')
        
        # value_video_url（字段关联视频）
        value_video_url = data_value.get('value_video_url', '') or ''
        with ui.row().classes('gap-2 items-center mb-2'):
            ui.icon('video_library').classes('text-lg text-red-600')
            ui.label('关联视频:').classes('text-lg font-medium')
            if value_video_url:
                ui.link('查看视频', target=value_video_url).classes('text-lg text-primary')
            else:
                ui.label('暂无数据').classes('text-lg text-grey-6')
        
        # 额外显示企业名称
        enterprise_name = data_value.get('enterprise_name', '') or ''
        with ui.row().classes('gap-2 items-center mb-2'):
            ui.icon('business').classes('text-lg text-teal-600')
            ui.label('企业名称:').classes('text-lg font-medium')
            if enterprise_name:
                ui.label(str(enterprise_name)).classes('text-lg')
            else:
                ui.label('暂无数据').classes('text-lg text-grey-6')

    def _display_existing_data_value_fields(self, data_value: Dict[str, Any]):
        """只显示实际存在的data_value字段（existing_fields策略）"""
        # value（字段值）- 如果存在且非空
        if 'value' in data_value and data_value['value'] and data_value['value'] != '暂无数据':
            value = data_value['value']
            with ui.row().classes('gap-2 items-center mb-2'):
                ui.icon('data_object').classes('text-lg text-blue-600')
                ui.label('字段值:').classes('text-lg font-medium')
                display_value = str(value)
                if len(display_value) > 50:
                    display_value = display_value[:50] + "..."
                ui.label(display_value).classes('text-lg')
        
        # value_pic_url（字段关联图片）- 如果存在且非空
        if 'value_pic_url' in data_value and data_value['value_pic_url']:
            with ui.row().classes('gap-2 items-center mb-2'):
                ui.icon('image').classes('text-lg text-green-600')
                ui.label('关联图片:').classes('text-lg font-medium')
                ui.link('查看图片', target=data_value['value_pic_url']).classes('text-lg text-primary')
        
        # value_doc_url（字段关联文档）- 如果存在且非空
        if 'value_doc_url' in data_value and data_value['value_doc_url']:
            with ui.row().classes('gap-2 items-center mb-2'):
                ui.icon('description').classes('text-lg text-orange-600')
                ui.label('关联文档:').classes('text-lg font-medium')
                ui.link('查看文档', target=data_value['value_doc_url']).classes('text-lg text-primary')
        
        # value_video_url（字段关联视频）- 如果存在且非空
        if 'value_video_url' in data_value and data_value['value_video_url']:
            with ui.row().classes('gap-2 items-center mb-2'):
                ui.icon('video_library').classes('text-lg text-red-600')
                ui.label('关联视频:').classes('text-lg font-medium')
                ui.link('查看视频', target=data_value['value_video_url']).classes('text-lg text-primary')
        
        # 企业名称 - 如果存在且非空
        if 'enterprise_name' in data_value and data_value['enterprise_name']:
            with ui.row().classes('gap-2 items-center mb-2'):
                ui.icon('business').classes('text-lg text-teal-600')
                ui.label('企业名称:').classes('text-lg font-medium')
                ui.label(str(data_value['enterprise_name'])).classes('text-lg')

    def _display_full_data_meta_fields(self, data_meta: Dict[str, Any]):
        """显示完整的data_meta字段集合（full_fields策略）"""
        # data_url（数据API）
        data_url = data_meta.get('data_url', '暂无数据') or '暂无数据'
        with ui.row().classes('gap-2 items-center mb-2'):
            ui.icon('api').classes('text-lg text-purple-600')
            ui.label('数据API:').classes('text-lg font-medium')
            ui.label('暂无数据').classes('text-lg text-grey-6')
        
        # encoding（编码方式）
        encoding = data_meta.get('encoding', 'UTF-8') or 'UTF-8'
        with ui.row().classes('gap-2 items-center mb-2'):
            ui.icon('code').classes('text-lg text-indigo-600')
            ui.label('编码方式:').classes('text-lg font-medium')
            ui.label(str(encoding)).classes('text-lg')
        
        # format（格式）
        format_val = data_meta.get('format', 'JSON') or 'JSON'
        with ui.row().classes('gap-2 items-center mb-2'):
            ui.icon('description').classes('text-lg text-cyan-600')
            ui.label('格式:').classes('text-lg font-medium')
            ui.label(str(format_val)).classes('text-lg')
        
        # license（使用许可）
        license_val = data_meta.get('license', '开放') or '开放'
        with ui.row().classes('gap-2 items-center mb-2'):
            ui.icon('license').classes('text-lg text-amber-600')
            ui.label('使用许可:').classes('text-lg font-medium')
            ui.label(str(license_val)).classes('text-lg')
        
        # rights（使用权限）
        rights = data_meta.get('rights', '公开') or '公开'
        with ui.row().classes('gap-2 items-center mb-2'):
            ui.icon('security').classes('text-lg text-pink-600')
            ui.label('使用权限:').classes('text-lg font-medium')
            ui.label(str(rights)).classes('text-lg')
        
        # update_frequency（更新频率）
        update_frequency = data_meta.get('update_frequency', '实时') or '实时'
        with ui.row().classes('gap-2 items-center mb-2'):
            ui.icon('update').classes('text-lg text-blue-500')
            ui.label('更新频率:').classes('text-lg font-medium')
            ui.label(str(update_frequency)).classes('text-lg')
        
        # value_dict（数据字典）
        value_dict = data_meta.get('value_dict', '') or ''
        with ui.row().classes('gap-2 items-center mb-2'):
            ui.icon('book').classes('text-lg text-green-500')
            ui.label('数据字典:').classes('text-lg font-medium')
            if value_dict:
                ui.label(str(value_dict)).classes('text-lg')
            else:
                ui.label('暂无数据').classes('text-lg text-grey-6')

    def _display_existing_data_meta_fields(self, data_meta: Dict[str, Any]):
        """只显示实际存在的data_meta字段（existing_fields策略）"""
        # 只显示非空且有意义的字段
        meta_fields = [
            ('data_url', 'api', 'purple-600', '数据API'),
            ('encoding', 'code', 'indigo-600', '编码方式'),
            ('format', 'description', 'cyan-600', '格式'),
            ('license', 'license', 'amber-600', '使用许可'),
            ('rights', 'security', 'pink-600', '使用权限'),
            ('update_frequency', 'update', 'blue-500', '更新频率'),
            ('value_dict', 'book', 'green-500', '数据字典'),
        ]
        
        for field_key, icon, color, label in meta_fields:
            if field_key in data_meta and data_meta[field_key] and data_meta[field_key] != '暂无数据':
                with ui.row().classes('gap-2 items-center mb-2'):
                    ui.icon(icon).classes(f'text-lg text-{color}')
                    ui.label(f'{label}:').classes('text-lg font-medium')
                    ui.label(str(data_meta[field_key])).classes('text-lg')

    def _build_table_columns_by_strategy(self, result_data: List[Dict[str, Any]], field_strategy: str) -> List[Dict[str, Any]]:
        """根据field_strategy构建表格列定义"""
        # 基础列（总是显示）
        columns = [
            {'name': 'enterprise_name', 'label': '企业名称', 'field': 'enterprise_name', 'sortable': True, 'align': 'left'},
            {'name': 'field_name', 'label': '字段名称', 'field': 'field_name', 'sortable': True, 'align': 'left'},
            {'name': 'value', 'label': '字段值', 'field': 'value', 'sortable': True, 'align': 'left'},
        ]
        
        if field_strategy == "full_fields":
            # 显示完整字段集合
            columns.extend([
                {'name': 'encoding', 'label': '编码方式', 'field': 'encoding', 'sortable': True, 'align': 'left'},
                {'name': 'format', 'label': '格式', 'field': 'format', 'sortable': True, 'align': 'left'},
                {'name': 'license', 'label': '使用许可', 'field': 'license', 'sortable': True, 'align': 'left'},
            ])
        else:
            # 根据实际数据动态添加存在的列
            existing_fields = set()
            for item in result_data:
                if isinstance(item, dict) and "data_value" in item:
                    data_value = item["data_value"]
                    for field in ['encoding', 'format', 'license', 'rights']:
                        if field in data_value and data_value[field] and data_value[field] != '暂无数据':
                            existing_fields.add(field)
            
            field_labels = {
                'encoding': '编码方式',
                'format': '格式', 
                'license': '使用许可',
                'rights': '使用权限'
            }
            
            for field in existing_fields:
                columns.append({
                    'name': field, 
                    'label': field_labels[field], 
                    'field': field, 
                    'sortable': True, 
                    'align': 'left'
                })
        
        # 添加详情列
        columns.append({'name': 'details', 'label': '详情', 'field': 'details', 'sortable': False, 'align': 'center'})
        
        return columns

    def _build_table_row_by_strategy(self, data_value: Dict[str, Any], field_strategy: str, row_id: int) -> Dict[str, Any]:
        """根据field_strategy构建表格行数据"""
        # 基础行数据
        row = {
            'id': row_id,
            'enterprise_name': data_value.get('enterprise_name', '未知企业'),
            'field_name': data_value.get('field_name', '未知字段'),
            'value': data_value.get('value', '暂无数据') or '暂无数据',
            'details': '',  # 详情列占位
        }
        
        if field_strategy == "full_fields":
            # 显示完整字段，缺失的显示默认值
            row.update({
                'encoding': data_value.get('encoding', '未指定') or '未指定',
                'format': data_value.get('format', '未指定') or '未指定',
                'license': data_value.get('license', '未指定') or '未指定',
            })
        else:
            # 只添加实际存在的字段
            for field in ['encoding', 'format', 'license', 'rights']:
                if field in data_value and data_value[field] and data_value[field] != '暂无数据':
                    row[field] = data_value[field]
        
        return row

    ### ------------------- 明细数据渲染展示 -------------------------
    def _display_other_result(self, query_type: str, result_data: List[Any]):
        """
        显示其他类型查询结果
        Args:
            query_type: 查询类型字符串
            result_data: 查询结果数据列表
        """
        ui.label(f"❓ 未知查询类型 '{query_type}': {str(result_data)}").classes(
            'whitespace-pre-wrap bg-gray-50 border-l-4 border-gray-500 p-3 mb-2'
        )

    def _display_error_result(self, result: Dict[str, Any]):
        """
        显示查询错误结果
        Args:
            result: 包含错误信息的结果字典
        """
        error_text = f"❌ 查询执行失败: {result.get('messages', '未知错误')}"
        ui.label(error_text).classes(
            'whitespace-pre-wrap bg-red-50 border-l-4 border-red-500 p-3 mb-2'
        )
    # ------------------------ 各类数据的渲染展示 -----------------------------

    def update_content(self, parse_result: Dict[str, Any]) -> bool:
        """更新专家模式展示内容"""
        # 只执行通用内容更新，不进行MongoDB查询检测
        return self.update_content_common(parse_result)
    
    def update_content_common(self, parse_result: Dict[str, Any]) -> bool:
        """通用内容更新逻辑"""
        if parse_result['think_updated'] and self.think_label:
            self.think_label.set_text(parse_result['think_content'])
        
        if parse_result['think_complete']:
            if self.chat_content_container and not self.reply_created:
                with self.chat_content_container:
                    self.reply_label = ui.markdown('').classes('w-full')
                self.reply_created = True
            
            if self.think_label:
                self.think_label.set_text(parse_result['think_content'])
        
        if self.reply_label and parse_result['display_content'].strip():
            with self.chat_content_container:
                self.reply_label.set_content(parse_result['display_content'].strip())
        
        return True  # 需要滚动
    
    async def finalize_content(self, final_content: str):
        """完成内容显示，并检测和执行MongoDB查询"""
        final_result = self.think_parser.parse_chunk(final_content)
        
        if final_result['think_complete'] and self.think_label:
            self.think_label.set_text(final_result['think_content'])
        
        if self.reply_label and final_result['display_content'].strip():
            self.reply_label.set_content(final_result['display_content'].strip())
        
        # 在内容完全处理完毕后，检测MongoDB查询并执行
        display_content = final_result.get('display_content', '')
        if display_content.strip():
            query_cmd = self._detect_mongodb_query(display_content)
            if query_cmd:
                # 异步执行查询
                try:
                    result = await self._execute_mongodb_query(query_cmd)
                    self._display_query_result(result)
                    # 执行完查询后滚动到底部
                    if hasattr(self.ui_components, 'scroll_to_bottom_smooth'):
                        await self.ui_components.scroll_to_bottom_smooth()
                except Exception as e:
                    # 查询执行失败时显示错误信息
                    error_msg = f"❌ MongoDB查询执行失败: {str(e)}"
                    if self.chat_content_container:
                        with self.chat_content_container:
                            ui.label(error_msg).classes(
                                'whitespace-pre-wrap bg-red-50 border-l-4 border-red-500 p-3 mb-2'
                            )

class StreamResponseProcessor:
    """流式响应处理器"""
    
    def __init__(self, chat_area_manager):
        self.chat_area_manager = chat_area_manager
        self.display_strategy = None
    
    def get_display_strategy(self) -> ContentDisplayStrategy:
        """根据prompt配置选择展示策略"""
        prompt_name = getattr(
            self.chat_area_manager.chat_data_state.current_prompt_config, 
            'selected_prompt', 
            'default'
        )

        if prompt_name == '一企一档专家':
            return ExpertDisplayStrategy(self.chat_area_manager)
        else:
            return DefaultDisplayStrategy(self.chat_area_manager)
    
    async def process_stream_response(self, stream_response) -> str:
        """处理流式响应"""
        self.display_strategy = self.get_display_strategy()
        assistant_reply = ""
        
        for chunk in stream_response:
            if chunk.choices[0].delta.content:
                chunk_content = chunk.choices[0].delta.content
                assistant_reply += chunk_content
                
                # 使用策略处理内容
                need_scroll = self.display_strategy.process_stream_chunk(assistant_reply)
                
                if need_scroll:
                    await self.chat_area_manager.scroll_to_bottom_smooth()
                    await asyncio.sleep(0.05)
        
        # 完成内容显示
        await self.display_strategy.finalize_content(assistant_reply)
        return assistant_reply

class MessageProcessor:
    """消息处理门面类"""
    
    def __init__(self, chat_area_manager):
        self.chat_area_manager = chat_area_manager
        self.preprocessor = MessagePreprocessor(chat_area_manager.chat_data_state)
        self.ai_client_manager = AIClientManager(chat_area_manager.chat_data_state)
        self.stream_processor = StreamResponseProcessor(chat_area_manager)
    
    async def process_user_message(self, user_message: str) -> str:
        """处理用户消息并返回AI回复"""
        # 1. 预处理用户消息
        enhanced_message = self.preprocessor.enhance_user_message(user_message)
        
        # 2. 保存用户消息到历史
        user_msg_dict = {
            'role': 'user',
            'content': enhanced_message,
            'timestamp': datetime.now().isoformat()
        }
        self.chat_area_manager.chat_data_state.current_chat_messages.append(user_msg_dict)
        
        # 3. 渲染用户消息
        await self.chat_area_manager.render_single_message(user_msg_dict)
        await self.chat_area_manager.scroll_to_bottom_smooth()
        
        # 4. 启动等待效果
        await self.chat_area_manager.start_waiting_effect("正在处理")
        
        try:
            # 5. 获取AI客户端
            client, model_config = await self.ai_client_manager.get_client()
            
            # 6. 准备消息列表
            messages = self.ai_client_manager.prepare_messages(user_msg_dict)
            
            # 7. 调用AI API
            actual_model_name = model_config.get('model_name', 
                self.chat_area_manager.chat_data_state.current_model_config['selected_model']
            ) if model_config else self.chat_area_manager.chat_data_state.current_model_config['selected_model']
            
            stream_response = await asyncio.to_thread(
                client.chat.completions.create,
                model=actual_model_name,
                messages=messages,
                max_tokens=2000,
                temperature=0.7,
                stream=True
            )
            
            # 8. 停止等待效果并处理流式响应
            await self.chat_area_manager.stop_waiting_effect()
            assistant_reply = await self.stream_processor.process_stream_response(stream_response)
            
            return assistant_reply
            
        except Exception as e:
            # 错误处理
            error_message = f"抱歉，调用AI服务时出现错误：{str(e)[:300]}..."
            ui.notify('AI服务调用失败，请稍后重试', type='negative')
            
            await self.chat_area_manager.stop_waiting_effect()
            if self.chat_area_manager.waiting_message_label:
                self.chat_area_manager.waiting_message_label.set_text(error_message)
                self.chat_area_manager.waiting_message_label.classes(remove='text-gray-500 italic')
            
            return error_message

# 更新后的 ChatAreaManager 类
class ChatAreaManager:
    """主聊天区域管理器 - 负责聊天内容展示和用户交互"""  
    def __init__(self, chat_data_state):
        """初始化聊天区域管理器"""
        self.chat_data_state = chat_data_state
        self.markdown_parser = MarkdownUIParser()
        # UI组件引用
        self.scroll_area = None
        self.chat_messages_container = None
        self.welcome_message_container = None
        self.input_ref = {'widget': None}
        self.send_button_ref = {'widget': None}
        self.clear_button_ref = {'widget': None}
        # 其他UI引用
        self.switch = None
        self.hierarchy_selector = None
        # 新增类属性：AI回复相关组件
        self.reply_label = None
        self.chat_content_container = None
        # 等待效果
        self.waiting_message_label = None
        self.waiting_animation_task = None
        self.waiting_ai_message_container = None
        # 聊天头像
        self.user_avatar = static_manager.get_fallback_path(
            static_manager.get_logo_path('user.svg'),
            static_manager.get_logo_path('ProfileHeader.gif'),
        )
        self.robot_avatar = static_manager.get_fallback_path(
            static_manager.get_logo_path('robot_txt.svg'),
            static_manager.get_logo_path('Live chatbot.gif'),
        )
        
        # 初始化消息处理器
        self.message_processor = MessageProcessor(self)

    #region 等待效果相关方法 - 保持原有代码不变
    async def start_waiting_effect(self, message="正在处理"):
        """启动等待效果"""
        # 添加等待效果的机器人消息容器
        with self.chat_messages_container:
            self.waiting_ai_message_container = ui.chat_message(
                avatar=self.robot_avatar
            ).classes('w-full')
            
            with self.waiting_ai_message_container:
                self.waiting_message_label = ui.label(message).classes('whitespace-pre-wrap text-gray-500 italic')

        await self.scroll_to_bottom_smooth()

        # 启动等待动画
        animation_active = [True]  # 使用列表以支持闭包内修改
        
        async def animate_waiting():
            dots_count = 0
            while animation_active[0] and self.waiting_message_label:
                dots_count = (dots_count % 3) + 1
                waiting_dots = "." * dots_count
                self.waiting_message_label.set_text(f'{message}{waiting_dots}')
                await asyncio.sleep(0.3)

        self.waiting_animation_task = asyncio.create_task(animate_waiting())
        # 绑定停止函数到task
        self.waiting_animation_task._stop_animation = lambda: animation_active.__setitem__(0, False)

    async def stop_waiting_effect(self):
        """停止等待效果"""
        if self.waiting_animation_task and not self.waiting_animation_task.done():
            # 停止动画循环
            if hasattr(self.waiting_animation_task, '_stop_animation'):
                self.waiting_animation_task._stop_animation()
            self.waiting_animation_task.cancel()
            
        # 清理等待相关引用（但保留ai_message_container供后续使用）
        self.waiting_message_label = None
        self.waiting_animation_task = None

    async def cleanup_waiting_effect(self):
        """完全清理等待效果相关资源"""
        self.waiting_ai_message_container = None
    #endregion

    #region 滚动和渲染方法 - 保持原有代码不变
    async def scroll_to_bottom_smooth(self):
        """平滑滚动到底部，使用更可靠的方法"""
        try:
            # 使用 scroll_area 的内置方法，设置 percent > 1 确保滚动到底部
            if self.scroll_area:
                self.scroll_area.scroll_to(percent=1.1)
                # 添加小延迟确保滚动完成
                await asyncio.sleep(0.09)
        except Exception as e:
            ui.notify(f"滚动出错: {e}")

    async def render_single_message(self, message: Dict[str, Any], container=None):
        """渲染单条消息"""
        target_container = container if container is not None else self.chat_messages_container
        
        with target_container:
            if message['role'] == 'user':
                with ui.chat_message(
                    # name='您',
                    avatar=self.user_avatar,
                    sent=True
                ).classes('w-full'):
                    ui.label(message['content']).classes('whitespace-pre-wrap break-words')
            
            elif message['role'] == 'assistant':
                with ui.chat_message(
                    # name='AI',
                    avatar=self.robot_avatar
                ).classes('w-full'):
                    # 创建临时的chat_content_container用于单条消息渲染
                    with ui.column().classes('w-full') as self.chat_content_container:
                        temp_reply_label = ui.markdown(message['content']).classes('w-full')
                        # 调用optimize_content_display进行内容优化显示
                        await self.markdown_parser.optimize_content_display(
                            temp_reply_label, 
                            message['content'], 
                            self.chat_content_container
                        )
    #endregion

    # 重构后的 handle_message 方法
    async def handle_message(self, event=None):
        """处理用户消息发送 - 重构后的精简版本"""
        user_message = self.input_ref['widget'].value.strip()
        if not user_message:
            return
            
        # 🔒 禁用输入控件
        self.input_ref['widget'].set_enabled(False)
        self.send_button_ref['widget'].set_enabled(False)
        self.input_ref['widget'].set_value('')
        
        try:
            # 删除欢迎消息
            if self.welcome_message_container:
                self.welcome_message_container.clear()
            # 使用消息处理器处理用户消息
            assistant_reply = await self.message_processor.process_user_message(user_message)
            # 🔥 记录AI回复到聊天历史
            self.chat_data_state.current_chat_messages.append({
                'role': 'assistant', 
                'content': assistant_reply,
                'timestamp': datetime.now().isoformat(),
                'model': self.chat_data_state.current_state.selected_model
            })
            # 完成回复后最终滚动
            await self.scroll_to_bottom_smooth()
        finally:
            # 🔓 恢复输入控件
            await self.stop_waiting_effect()
            self.input_ref['widget'].set_enabled(True)
            self.send_button_ref['widget'].set_enabled(True)
            self.input_ref['widget'].run_method('focus')

    def has_think_content(self, messages):
        """检测消息列表是否包含think内容"""
        for msg in messages:
            if msg.get('role') == 'assistant' and '<think>' in msg.get('content', ''):
                return True
        return False

    def remove_think_content(self, messages):
        """从消息列表中移除think标签及内容"""
        import re
        cleaned_messages = []
        
        for msg in messages:
            cleaned_msg = msg.copy()
            if msg.get('role') == 'assistant':
                content = msg.get('content', '')
                if '<think>' in content and '</think>' in content:
                    # 移除think标签及其内容
                    cleaned_content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL)
                    cleaned_msg['content'] = cleaned_content.strip()
            cleaned_messages.append(cleaned_msg)
        return cleaned_messages
    
    #region 其他原有方法 - 保持不变
    def handle_keydown(self, e):
        """处理键盘事件 - 使用NiceGUI原生方法"""
        # 检查输入框是否已禁用，如果禁用则不处理按键事件
        if not self.input_ref['widget'].enabled:
            return
            
        # 获取事件详细信息
        key = e.args.get('key', '')
        shift_key = e.args.get('shiftKey', False)
        
        if key == 'Enter':
            if shift_key:
                # Shift+Enter: 允许换行，不做任何处理
                pass
            else:
                # 单独的Enter: 发送消息
                # 阻止默认的换行行为
                ui.run_javascript('event.preventDefault();')
                # 异步调用消息处理函数
                ui.timer(0.01, lambda: self.handle_message(), once=True)
    
    def clear_chat_content(self):
        """清空当前聊天内容"""
        try:
            # 清空聊天消息容器
            self.chat_messages_container.clear()
            # 清空聊天数据状态中的消息
            self.chat_data_state.current_chat_messages.clear()
            # 恢复欢迎消息
            self.restore_welcome_message()
            # 显示成功提示
            ui.notify('聊天内容已清空', type='positive')
        except Exception as e:
            ui.notify(f'清空聊天失败: {str(e)}', type='negative')

    def restore_welcome_message(self):
        """恢复欢迎消息"""
        self.chat_messages_container.clear()
        if self.welcome_message_container:
            self.welcome_message_container.clear()
            with self.welcome_message_container:
                with ui.card().classes('w-full max-w-3xl mx-auto shadow-lg'):
                    with ui.column().classes('p-6 text-center'):
                        ui.icon('waving_hand', size='3xl').classes('text-blue-500 mb-4 text-3xl')
                        ui.label('欢迎使用一企一档智能问答助手').classes('text-2xl font-bold mb-2')
                        ui.label('请输入您的问题，我将为您提供帮助').classes('text-lg text-gray-600 mb-4')
                        
                        with ui.row().classes('justify-center gap-4'):
                            ui.chip('问答', icon='quiz').classes('text-blue-600 text-lg')
                            ui.chip('制表', icon='table_view').classes('text-yellow-600 text-lg')
                            ui.chip('绘图', icon='dirty_lens').classes('text-purple-600 text-lg')
                            ui.chip('分析', icon='analytics').classes('text-orange-600 text-lg')

    async def render_chat_history(self, chat_id):
        """渲染聊天历史内容"""
        try:
            self.chat_messages_container.clear()
            self.welcome_message_container.clear()
            await self.start_waiting_effect("正在加载聊天记录")

            from database_models.business_models.chat_history_model import ChatHistory
            from auth.database import get_db 
            with get_db() as db:
                chat = db.query(ChatHistory).filter(
                    ChatHistory.id == chat_id,
                    ChatHistory.is_deleted == False
                ).first()
                
                if not chat:
                    ui.notify('聊天记录不存在', type='negative')
                    return
                # 在会话关闭前获取消息数据
                prompt_name = chat.prompt_name
                model_name = chat.model_name
                messages = chat.messages.copy() if chat.messages else []
                chat_title = chat.title
                
            # 清空当前聊天消息并加载历史消息
            self.chat_data_state.current_chat_messages.clear()
            self.chat_data_state.current_chat_messages.extend(messages)
            await self.stop_waiting_effect()
            await self.cleanup_waiting_effect()
            # 清空聊天界面
            self.chat_messages_container.clear()
            # 使用异步任务来渲染消息
            async def render_messages_async():
                for msg in messages:
                    await self.render_single_message(msg)
            # 创建异步任务来处理消息渲染
            ui.timer(0.01, lambda: asyncio.create_task(render_messages_async()), once=True)
            # 滚动到底部
            ui.timer(0.1, lambda: self.scroll_area.scroll_to(percent=1), once=True)
            ui.notify(f'已加载聊天: {chat_title}', type='positive') 
            # -----------------------------
            self.chat_data_state.current_state.model_select_widget.set_value(model_name)
            self.chat_data_state.current_state.prompt_select_widget.set_value(prompt_name)
            self.chat_data_state.switch = (prompt_name == '一企一档专家')
        except Exception as e:
            await self.stop_waiting_effect()
            await self.cleanup_waiting_effect()
            self.restore_welcome_message()
            ui.notify('加载聊天失败', type='negative')    

    def render_ui(self):
        """渲染主聊天区域UI"""
        # 主聊天区域 - 占据剩余空间
        with ui.column().classes('flex-grow h-full').style('position: relative; overflow: hidden;'):
            # 聊天消息区域 - 使用 scroll_area 提供更好的滚动体验
            self.scroll_area = ui.scroll_area().classes('w-full').style('height: calc(100% - 80px); padding-bottom: 20px;')

            with self.scroll_area:
                self.chat_messages_container = ui.column().classes('w-full gap-2')  
                # 欢迎消息（可能会被删除）
                self.welcome_message_container = ui.column().classes('w-full')
                with self.welcome_message_container:
                    self.restore_welcome_message()
            # 输入区域 - 固定在底部，距离底部10px
            with ui.row().classes('w-full items-center gap-2 rounded ').style(
                'position: absolute; bottom: 10px; left: 10px; right: 10px; z-index: 1000; '
                'margin: 0 auto; max-width: calc(100% - 20px);'
            ):    
                # 创建textarea并绑定事件
                self.input_ref['widget'] = ui.textarea(
                    placeholder='请输入您的消息...(Enter发送，Shift+Enter换行)'
                ).classes('flex-grow').style(
                    'min-height: 44px; max-height: 120px; resize: none;'
                ).props('outlined dense rounded rows=3').tooltip('输入聊天内容')

                # 使用.on()方法监听keydown事件
                self.input_ref['widget'].on('keydown', self.handle_keydown)
                
                self.send_button_ref['widget'] = ui.button(
                    icon='send',
                    on_click=self.handle_message
                ).props('round dense ').classes('ml-2').tooltip('发送聊天内容')

                # 清空聊天按钮
                self.clear_button_ref['widget'] = ui.button(
                    icon='cleaning_services',
                    on_click=self.clear_chat_content
                ).props('round dense').classes('ml-2').tooltip('清空聊天内容')
    #endregion