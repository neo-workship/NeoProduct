from abc import ABC, abstractmethod
import asyncio
import aiohttp
import re
import json
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
                full_path_code = selected_values['full_path_code']
                field_value = selected_values['field']
                append_text = f"\n\n[数据路径] {full_path_code} \n\n [字段信息] {field_value}"
            else:
                full_path_code = selected_values['full_path_code']
                append_text = f"\n\n[数据路径] {full_path_code}"
            
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
    
    def prepare_messages(self) -> List[Dict[str, str]]:
        """准备发送给AI的消息列表"""
        recent_messages = self.chat_data_state.current_chat_messages[-20:]
        
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
        调用MongoDB服务API执行查询
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
                        return await response.json()
                    else:
                        error_text = await response.text()
                        # 返回与API一致的格式
                        return {
                            "success": False,
                            "message": f"API调用失败: HTTP {response.status}, response={error_text}",
                            "type": "错误",
                            "statis": {
                                "耗时": "0ms",
                                "文档数": 0
                            },
                            "field_value": [],
                            "field_meta": None
                        }
        except Exception as e:
            # 返回与API一致的格式
            return {
                "success": False,
                "message": f"网络请求失败: {str(e)}",
                "type": "错误",
                "statis": {
                    "耗时": "0ms",
                    "文档数": 0
                },
                "field_value": [],
                "field_meta": None
            }
    
    def _display_query_result(self, result: Dict[str, Any]):
        """
        使用ui.label展示查询结果
        """
        if not self.chat_content_container:
            return
            
        with self.chat_content_container:
            # 显示查询统计信息
            if result.get("statis"):
                stats = result["statis"]
                stats_text = (
                    f"📊 查询统计:\n"
                    f"• 查询类型: {result.get('type', 'N/A')}\n"
                    f"• 耗时: {stats.get('耗时', '0ms')}\n"
                    f"• 文档数: {stats.get('文档数', 0)}"
                )
                ui.label(stats_text).classes(
                    'whitespace-pre-wrap bg-blue-50 border-l-4 border-blue-500 p-3 mb-2'
                )
            
            # 显示查询结果数据
            if result.get("success"):
                field_value = result.get("field_value", [])
                query_type = result.get("type", "")
                
                if query_type == "汇总":
                    # 显示汇总结果
                    result_text = f"🔢 汇总结果: {field_value}"
                    ui.label(result_text).classes(
                        'whitespace-pre-wrap bg-green-50 border-l-4 border-green-500 p-3 mb-2'
                    )
                elif query_type == "明细":
                    # 显示明细结果
                    if isinstance(field_value, list) and field_value:
                        # 格式化显示前几条数据
                        display_count = min(3, len(field_value))  # 最多显示3条
                        result_text = f"🔍 查询结果 (显示前{display_count}条):\n\n"
                        
                        for i, item in enumerate(field_value[:display_count]):
                            result_text += f"📄 记录 {i+1}:\n"
                            # 格式化JSON数据
                            formatted_json = json.dumps(item, ensure_ascii=False, indent=2)
                            result_text += f"{formatted_json}\n\n"
                        
                        if len(field_value) > display_count:
                            result_text += f"... 还有 {len(field_value) - display_count} 条记录"
                        
                        self.query_result_label = ui.label(result_text).classes(
                            'whitespace-pre-wrap bg-green-50 border-l-4 border-green-500 p-3 mb-2'
                        )
                    else:
                        ui.label("📝 查询结果: 未找到匹配的数据").classes(
                            'whitespace-pre-wrap bg-yellow-50 border-l-4 border-yellow-500 p-3 mb-2'
                        )
                else:
                    # 其他类型或未知类型
                    if field_value:
                        formatted_data = json.dumps(field_value, ensure_ascii=False, indent=2)
                        result_text = f"📄 查询结果:\n{formatted_data}"
                        ui.label(result_text).classes(
                            'whitespace-pre-wrap bg-green-50 border-l-4 border-green-500 p-3 mb-2'
                        )
                    else:
                        ui.label("📝 查询结果: 未找到匹配的数据").classes(
                            'whitespace-pre-wrap bg-yellow-50 border-l-4 border-yellow-500 p-3 mb-2'
                        )
            else:
                # 显示错误信息
                error_msg = f"❌ 查询失败: {result.get('message', '未知错误')}"
                ui.label(error_msg).classes(
                    'whitespace-pre-wrap bg-red-50 border-l-4 border-red-500 p-3 mb-2'
                )
    
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
            messages = self.ai_client_manager.prepare_messages()
            
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