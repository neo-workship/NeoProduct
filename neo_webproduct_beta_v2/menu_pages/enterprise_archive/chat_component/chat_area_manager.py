import re
import asyncio
from datetime import datetime
from nicegui import ui, app
from typing import Optional, List, Dict, Any
from component import static_manager
from .chat_data_state import ChatDataState

class ChatAreaManager:
    """主聊天区域管理器 - 负责聊天内容展示和用户交互"""
    
    def __init__(self, chat_data_state: ChatDataState):
        """初始化聊天区域管理器
        
        Args:
            chat_data_state: 聊天数据状态对象
        """
        self.chat_data_state = chat_data_state
        
        # UI组件引用
        self.scroll_area = None
        self.messages = None
        self.welcome_message_container = None
        self.input_ref = {'widget': None}
        self.send_button_ref = {'widget': None}
        
        # 其他UI引用
        self.switch = None
        self.hierarchy_selector = None

    #region 解析markdown并映射为ui组件展示相关逻辑 
    async def optimize_content_display(self, reply_label, content: str, chat_content_container=None):
        """
        优化内容显示 - 将特殊内容转换为专业NiceGUI组件
        
        Args:
            reply_label: 当前的markdown组件引用
            content: 完整的AI回复内容
            chat_content_container: 聊天内容容器引用
        """
        try:
            # 1. 解析内容，检测特殊块
            parsed_blocks = self.parse_content_with_regex(content)
            
            # 2. 判断是否需要优化
            if self.has_special_content(parsed_blocks):
                # 3. 显示优化提示
                self.show_optimization_hint(reply_label)
                
                # 4. 短暂延迟，让用户看到提示
                await asyncio.sleep(0.1)
                
                # 5. 获取正确的容器
                container = chat_content_container if chat_content_container else reply_label
                
                # 6. 重新渲染混合组件
                await self.render_optimized_content(container, parsed_blocks)
            
        except Exception as e:
            ui.notify(f"内容优化失败，保持原始显示: {e}")

    def parse_content_with_regex(self, content: str) -> List[Dict[str, Any]]:
        """
        使用Mistune解析内容为结构化块
        
        Returns:
            List[Dict]: 解析后的内容块列表
            [{
                'type': 'table|mermaid|code|heading|math|text',
                'content': '原始内容',
                'data': '解析后的数据'(可选),
                'start_pos': 开始位置,
                'end_pos': 结束位置
            }]
        """
        blocks = []
        
        # 1. 检测表格
        table_blocks = self.extract_tables(content)
        blocks.extend(table_blocks)
        
        # 2. 检测Mermaid图表
        mermaid_blocks = self.extract_mermaid(content)
        blocks.extend(mermaid_blocks)
        
        # 3. 检测代码块
        code_blocks = self.extract_code_blocks(content)
        blocks.extend(code_blocks)
        
        # 4. 检测LaTeX公式
        math_blocks = self.extract_math(content)
        blocks.extend(math_blocks)
        
        # 5. 检测标题
        heading_blocks = self.extract_headings(content)
        blocks.extend(heading_blocks)
        
        # 6. 按位置排序
        blocks.sort(key=lambda x: x['start_pos'])
        
        # 7. 填充文本块
        text_blocks = self.fill_text_blocks(content, blocks)
        
        # 8. 合并并重新排序
        all_blocks = blocks + text_blocks
        all_blocks.sort(key=lambda x: x['start_pos'])
        
        return all_blocks

    def extract_tables(self, content: str) -> List[Dict[str, Any]]:
        """提取表格内容"""
        tables = []
        # 匹配markdown表格模式
        pattern = r'(\|.*\|.*\n\|[-\s\|]*\|.*\n(?:\|.*\|.*\n)*)'
        
        for match in re.finditer(pattern, content):
            table_data = self.parse_table_data(match.group(1))
            if table_data:  # 确保解析成功
                tables.append({
                    'type': 'table',
                    'content': match.group(1),
                    'data': table_data,
                    'start_pos': match.start(),
                    'end_pos': match.end()
                })
        
        return tables

    def extract_mermaid(self, content: str) -> List[Dict[str, Any]]:
        """提取Mermaid图表"""
        mermaid_blocks = []
        pattern = r'```mermaid\n(.*?)```'
        
        for match in re.finditer(pattern, content, re.DOTALL):
            mermaid_blocks.append({
                'type': 'mermaid',
                'content': match.group(1).strip(),
                'start_pos': match.start(),
                'end_pos': match.end()
            })
    
        return mermaid_blocks

    def extract_code_blocks(self, content: str) -> List[Dict[str, Any]]:
        """提取代码块（排除mermaid）"""
        code_blocks = []
        pattern = r'```(\w+)?\n(.*?)```'
        
        for match in re.finditer(pattern, content, re.DOTALL):
            language = match.group(1) or 'text'
            if language.lower() != 'mermaid':  # 排除mermaid
                code_blocks.append({
                    'type': 'code',
                    'content': match.group(2).strip(),
                    'language': language,
                    'start_pos': match.start(),
                    'end_pos': match.end()
                })
        
        return code_blocks

    def extract_math(self, content: str) -> List[Dict[str, Any]]:
        """提取LaTeX数学公式"""
        math_blocks = []
        
        # 块级公式 $$...$$
        block_pattern = r'\$\$(.*?)\$\$'
        for match in re.finditer(block_pattern, content, re.DOTALL):
            math_blocks.append({
                'type': 'math',
                'content': match.group(1).strip(),
                'display_mode': 'block',
                'start_pos': match.start(),
                'end_pos': match.end()
            })
        
        # 行内公式 $...$
        inline_pattern = r'(?<!\$)\$([^\$\n]+)\$(?!\$)'
        for match in re.finditer(inline_pattern, content):
            math_blocks.append({
                'type': 'math',
                'content': match.group(1).strip(),
                'display_mode': 'inline',
                'start_pos': match.start(),
                'end_pos': match.end()
            })
        
        return math_blocks

    def extract_headings(self, content: str) -> List[Dict[str, Any]]:
        """提取标题"""
        headings = []
        pattern = r'^(#{1,6})\s+(.+)$'
        
        for match in re.finditer(pattern, content, re.MULTILINE):
            level = len(match.group(1))
            text = match.group(2).strip()
            headings.append({
                'type': 'heading',
                'content': text,
                'level': level,
                'start_pos': match.start(),
                'end_pos': match.end()
            })
        
        return headings

    def fill_text_blocks(self, content: str, special_blocks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """填充普通文本块"""
        if not special_blocks:
            return [{
                'type': 'text',
                'content': content,
                'start_pos': 0,
                'end_pos': len(content)
            }]
        
        text_blocks = []
        last_end = 0
        
        for block in special_blocks:
            if block['start_pos'] > last_end:
                text_content = content[last_end:block['start_pos']].strip()
                if text_content:
                    text_blocks.append({
                        'type': 'text',
                        'content': text_content,
                        'start_pos': last_end,
                        'end_pos': block['start_pos']
                    })
            last_end = block['end_pos']
        
        # 添加最后的文本内容
        if last_end < len(content):
            text_content = content[last_end:].strip()
            if text_content:
                text_blocks.append({
                    'type': 'text',
                    'content': text_content,
                    'start_pos': last_end,
                    'end_pos': len(content)
                })
        
        return text_blocks

    def parse_table_data(self, table_text: str) -> Optional[Dict[str, Any]]:
        """解析表格数据为NiceGUI table格式"""
        try:
            lines = [line.strip() for line in table_text.strip().split('\n') if line.strip()]
            if len(lines) < 3:  # 至少需要header、separator、data
                return None
            
            # 解析表头
            headers = [cell.strip() for cell in lines[0].split('|')[1:-1]]
            if not headers:
                return None
            
            # 解析数据行（跳过分隔行）
            rows = []
            for line in lines[2:]:
                cells = [cell.strip() for cell in line.split('|')[1:-1]]
                if len(cells) == len(headers):
                    row_data = dict(zip(headers, cells))
                    rows.append(row_data)
            
            return {
                'columns': [{'name': col, 'label': col, 'field': col} for col in headers],
                'rows': rows
            }
        
        except Exception as e:
            ui.notify(f"表格解析失败: {e}")
            return None

    def has_special_content(self, blocks: List[Dict[str, Any]]) -> bool:
        """检查是否包含需要优化的特殊内容"""
        special_types = {'table', 'mermaid', 'code', 'math', 'heading','text'}
        return any(block['type'] in special_types for block in blocks)

    def show_optimization_hint(self, reply_label):
        """显示优化提示"""
        try:
            reply_label.set_content("🔄 正在优化内容显示...")
        except:
            pass  # 如果设置失败，忽略错误

    async def render_optimized_content(self, container, blocks: List[Dict[str, Any]]):
        """渲染优化后的混合内容"""
        container.clear()
        
        with container:
            for block in blocks:
                try:
                    if block['type'] == 'table':
                        self.create_table_component(block['data'])
                    elif block['type'] == 'mermaid':
                        self.create_mermaid_component(block['content'])
                    elif block['type'] == 'code':
                        self.create_code_component(block['content'], block['language'])
                    elif block['type'] == 'math':
                        self.create_math_component(block['content'], block['display_mode'])
                    elif block['type'] == 'heading':
                        self.create_heading_component(block['content'], block['level'])
                    elif block['type'] == 'text':
                        self.create_text_component(block['content'])
                except Exception as e:
                    # 如果某个组件创建失败，显示原始文本作为降级方案
                    ui.markdown(f"```\n{block['content']}\n```").classes('w-full')

    def create_table_component(self, table_data: Dict[str, Any]):
        """创建表格组件"""
        if table_data and 'columns' in table_data and 'rows' in table_data:
            ui.table(
                columns=table_data['columns'],
                rows=table_data['rows']
            ).classes('w-full max-w-full')

    def create_mermaid_component(self, mermaid_content: str):
        """创建Mermaid图表组件"""
        ui.mermaid(mermaid_content).classes('w-full')

    def create_code_component(self, code_content: str, language: str):
        """创建代码组件"""
        ui.code(code_content, language=language).classes('w-full')

    def create_math_component(self, math_content: str, display_mode: str):
        """创建数学公式组件"""
        if display_mode == 'block':
            ui.markdown(f'$$\n{math_content}\n$$').classes('w-full text-center')
        else:
            ui.markdown(f'${math_content}$').classes('w-full')

    def create_heading_component(self, text: str, level: int):
        """创建标题组件"""
        ui.markdown('#' * level + ' ' + text).classes('w-full')

    def create_text_component(self, text_content: str):
        """创建文本组件"""
        ui.markdown(text_content).classes('w-full')
    #endregion  解析markdown并映射为ui组件展示相关逻辑

    #region 用户输入提交相关处理逻辑
    async def scroll_to_bottom_smooth(self):
        """平滑滚动到底部，使用更可靠的方法"""
        try:
            # 方法1: 使用 scroll_area 的内置方法，设置 percent > 1 确保滚动到底部
            if self.scroll_area:
                self.scroll_area.scroll_to(percent=1.1)
                # 添加小延迟确保滚动完成
                await asyncio.sleep(0.09)
        except Exception as e:
            print(f"滚动出错: {e}")
            ui.notify(f"滚动出错: {e}")

    def enhance_user_message(self, user_message: str) -> str:
        """
        在用户输入中动态添加 select数据expansion组件 的内容
        
        Args:
            user_message: 用户原始输入消息
            
        Returns:
            str: 增强后的用户消息（如果不满足条件则返回原消息）
        """
        try:
            # 2. 检查 select数据expansion组件 中的 switch 是否打开
            if not self.chat_data_state.switch:
                return user_message
                
            # 3. 检查上下文模板expansion组件中的 prompt_select_widget 是否选择"一企一档专家"
            if not (self.chat_data_state.current_state.prompt_select_widget and 
                    self.chat_data_state.current_state.prompt_select_widget.value == "一企一档专家"):
                ui.notify("上下文模板未选择'一企一档专家'",type="warning")
                return user_message
                
            # 4. 检查 selected_values 至少选择3级数据
            selected_values = self.chat_data_state.selected_values
            
            if not (selected_values and selected_values.l3):
                ui.notify("未选择足够的层级数据（至少需要3级）",type="warning")
                return user_message
                
            # 5. 根据是否选择4级数据决定拼接内容
            append_text = ""
            
            if selected_values.field:  # 选择了4级数据
                # 处理字段信息进行拼接
                full_path_code = selected_values.full_path_code
                field_value = selected_values.field
                
                append_text = f"\n\n[数据路径] {full_path_code} \n\n [字段信息] {field_value}"
                
            else:  # 未选择4级，使用3级内容
                full_path_code = selected_values.full_path_code
                append_text = f"\n\n[数据路径] {full_path_code}"
            
            # 6. 拼接到用户消息
            if append_text:
                enhanced_message = f"{user_message}{append_text}"
                return enhanced_message
                
            return user_message
            
        except Exception as e:
            # 异常处理：确保即使出错也不影响正常聊天功能
            ui.notify(f"[ERROR] 增强用户消息时发生异常: {e}",type="negative")
            return user_message

    async def handle_message(self, event=None):
        """处理用户消息发送"""
        user_message = self.input_ref['widget'].value.strip()
        if not user_message:
            return
            
        # 🔒 禁用输入框和发送按钮，防止重复发送
        self.input_ref['widget'].set_enabled(False)
        self.send_button_ref['widget'].set_enabled(False)
        
        # 清空输入框
        self.input_ref['widget'].set_value('')

        # 等待效果相关变量
        waiting_message = None
        waiting_dots = ""
        assistant_reply = ""
        waiting_task = None  # 初始化变量
        
        try:
            # 删除欢迎消息
            if self.welcome_message_container:
                self.welcome_message_container.clear()

            # 🔥 记录用户消息到聊天历史
            # 动态添加提示数据
            user_message = self.enhance_user_message(user_message)
            print(f"user_message:{user_message}")
            self.chat_data_state.current_chat_messages.append({
                'role': 'user',
                'content': user_message,
                'timestamp': datetime.now().isoformat()
            })

            # 用户消息
            with self.messages:
                user_avatar = static_manager.get_fallback_path(
                    static_manager.get_logo_path('user.svg'),
                    'https://robohash.org/user'
                )
                with ui.chat_message(
                    name='您',
                    avatar=user_avatar,
                    sent=True
                ).classes('w-full'):
                    ui.label(user_message).classes('whitespace-pre-wrap break-words')

            # 添加用户消息后立即滚动到底部
            await self.scroll_to_bottom_smooth()

            # 🔥 添加等待效果的机器人消息
            with self.messages:
                robot_avatar = static_manager.get_fallback_path(
                    static_manager.get_logo_path('robot_txt.svg'),
                    'https://robohash.org/ui'
                )
                with ui.chat_message(
                    name='AI',
                    avatar=robot_avatar
                ).classes('w-full') as ai_message_container:
                    waiting_message = ui.label('正在思考...').classes('whitespace-pre-wrap text-gray-500 italic')

            await self.scroll_to_bottom_smooth()

            # 🔥 启动等待动画 - 使用标志变量控制
            animation_active = True
            
            async def animate_waiting():
                nonlocal waiting_dots, animation_active
                dots_count = 0
                while animation_active and waiting_message:
                    dots_count = (dots_count % 3) + 1
                    waiting_dots = "." * dots_count
                    waiting_message.set_text(f'正在思考{waiting_dots}')
                    await asyncio.sleep(0.3)

            waiting_task = asyncio.create_task(animate_waiting())
            
            # 🔥 调用AI API
            try:
                # 构建发送给AI的消息列表
                from common.safe_openai_client_pool import get_openai_client
                # 使用 current_model_config 获取当前选择的模型，确保状态一致性
                selected_model = self.chat_data_state.current_model_config['selected_model']
                model_config = self.chat_data_state.current_model_config['config']
                # 创建 OpenAI 客户端
                client = await get_openai_client(selected_model, model_config)
                
                if not client:
                    assistant_reply = f"抱歉，无法连接到模型 {selected_model}，请检查配置或稍后重试。"
                    ui.notify(f'模型 {selected_model} 连接失败', type='negative')
                    
                    # 停止等待动画并更新消息
                    animation_active = False
                    if waiting_task and not waiting_task.done():
                        waiting_task.cancel()
                    waiting_message.set_text(assistant_reply)
                    waiting_message.classes(remove='text-gray-500 italic')
                else:
                    # 准备对话历史（取最近20条消息）
                    recent_messages = self.chat_data_state.current_chat_messages[-20:]
                    # print(f"prompt:{current_prompt_config['system_prompt']}")
                    if self.chat_data_state.current_state.get('prompt_select_widget') \
                        and self.chat_data_state.current_prompt_config.get('system_prompt'):
                        system_message = {
                            "role": "system", 
                            "content": self.chat_data_state['system_prompt']
                        }
                        # 将系统消息插入到历史消息的最前面
                        recent_messages = [system_message] + recent_messages
                    
                    # 获取实际的模型名称
                    actual_model_name = model_config.get('model_name', selected_model) if model_config else selected_model
                    
                    # 🔥 流式调用 OpenAI API
                    stream_response = await asyncio.to_thread(
                        client.chat.completions.create,
                        model=actual_model_name,
                        messages=recent_messages,
                        max_tokens=2000,
                        temperature=0.7,
                        stream=True  # 启用流式响应
                    )

                     # ⭐ 关键修复：在开始处理流式响应时才停止等待动画
                    animation_active = False
                    if waiting_task and not waiting_task.done():
                        waiting_task.cancel()
                    
                    # 🔥 处理流式响应 - 完全重写逻辑
                    assistant_reply = ""
                    is_in_think = False
                    think_start_pos = -1

                    # 清空等待消息，准备流式显示
                    ai_message_container.clear()

                    # 初始化组件变量 - 关键：不预先创建任何组件
                    think_expansion = None
                    think_label = None
                    reply_label = None
                    chat_content_container = None

                    # 用于跟踪是否已经创建了基础结构
                    structure_created = False
                    reply_created = False
                    # 处理流式数据
                    for chunk in stream_response:
                        if chunk.choices[0].delta.content:
                            chunk_content = chunk.choices[0].delta.content
                            assistant_reply += chunk_content
                            
                            # 🔥 检测和处理思考内容
                            temp_content = assistant_reply
                            
                            # 检查是否开始思考内容
                            if '<think>' in temp_content and not is_in_think:
                                is_in_think = True
                                think_start_pos = temp_content.find('<think>')
                                
                                # 创建包含思考内容的完整结构
                                if not structure_created:
                                    ai_message_container.clear()
                                    with ai_message_container:
                                        with ui.column().classes('w-full') as chat_content_container:
                                            # 创建思考区域
                                            think_expansion = ui.expansion(
                                                '💭 AI思考过程...(可点击打开查看)', 
                                                icon='psychology'
                                            ).classes('w-full mb-2')
                                            with think_expansion:
                                                think_label = ui.label('').classes('whitespace-pre-wrap bg-[#81c784] border-0 shadow-none rounded-none')
                                        
                                    structure_created = True
                                # 如果没有思考内容，且尚未创建结构，创建普通回复结构
                                elif not structure_created and '<think>' not in temp_content:
                                    ai_message_container.clear()
                                    with ai_message_container:
                                        with ui.column().classes('w-full') as chat_content_container:
                                            reply_label = ui.markdown('').classes('w-full')
                                    structure_created = True
                                    reply_created = True
                                # 检查是否结束思考内容
                                if '</think>' in temp_content and is_in_think:
                                    is_in_think = False
                                    think_end_pos = temp_content.find('</think>') + 8
                                    
                                    # 提取思考内容
                                    think_content = temp_content[think_start_pos + 7:think_end_pos - 8]
                                    if think_label:
                                        think_label.set_text(think_content.strip())
                                    
                                    # 移除思考标签，保留其他内容
                                    display_content = temp_content[:think_start_pos] + temp_content[think_end_pos:]
                                    
                                    # 现在在容器中创建回复组件
                                    if chat_content_container and not reply_created:
                                        with chat_content_container:
                                            reply_label = ui.markdown('').classes('w-full')
                                        reply_created = True
                                    
                                    # 更新回复内容
                                    if reply_label and display_content.strip():
                                        reply_label.set_content(display_content.strip())
                                else:
                                    # 根据当前状态更新显示内容
                                    if is_in_think:
                                        # 在思考中：显示思考前的内容（如果有），更新思考内容
                                        if think_start_pos >= 0:
                                            display_content = temp_content[:think_start_pos]
                                            
                                            # 更新思考内容（去除标签）
                                            current_think = temp_content[think_start_pos + 7:]
                                            if current_think and think_label:
                                                think_label.set_text(current_think.strip())
                                            
                                            # 如果有前置内容且还未创建回复组件，先创建
                                            if display_content.strip() and chat_content_container and not reply_created:
                                                with chat_content_container:
                                                    reply_label = ui.markdown('').classes('w-full')
                                                reply_created = True
                                            
                                            # 更新前置内容
                                            if reply_label and display_content.strip():
                                                reply_label.set_content(display_content.strip())
                                    else:
                                        # 正常显示内容：没有思考标签
                                        if reply_label:
                                            reply_label.set_content(temp_content)
                            
                                # 流式更新时滚动到底部
                                await self.scroll_to_bottom_smooth()
                                await asyncio.sleep(0.01)  # 流式显示的间隔

                    # 最终处理：确保所有内容正确显示
                    final_content = assistant_reply
                     # 如果包含思考内容，进行最终清理
                    if '<think>' in final_content and '</think>' in final_content:
                        think_start = final_content.find('<think>')
                        think_end = final_content.find('</think>') + 8
                        
                        # 最终的思考内容
                        final_think_content = final_content[think_start + 7:think_end - 8]
                        if think_label:
                            think_label.set_text(final_think_content.strip())
                        
                        # 最终的回复内容（移除思考标签）
                        final_reply_content = final_content[:think_start] + final_content[think_end:]
                        
                        # 确保回复组件已创建
                        if chat_content_container and not reply_created and final_reply_content.strip():
                            with chat_content_container:
                                reply_label = ui.markdown('').classes('w-full')
                            reply_created = True
                        
                        if reply_label and final_reply_content.strip():
                            reply_label.set_content(final_reply_content.strip())
                            await self.optimize_content_display(reply_label, final_reply_content,chat_content_container)
                        
                        # 用于记录到聊天历史的内容（保留思考标签）
                        assistant_reply = final_content
                    else:
                        # 没有思考内容，直接显示
                        if not structure_created:
                            ai_message_container.clear()
                            with ai_message_container:
                                with ui.column().classes('w-full') as chat_content_container:
                                    reply_label = ui.markdown('').classes('w-full')
                        
                        if reply_label:
                            reply_label.set_content(final_content)
                            await self.optimize_content_display(reply_label, final_content,chat_content_container)
                            
                            
            except Exception as api_error:
                assistant_reply = f"抱歉，调用AI服务时出现错误：{str(api_error)[:100]}..."
                ui.notify('AI服务调用失败，请稍后重试', type='negative')
                
                # 停止等待动画并显示错误信息
                animation_active = False
                if waiting_task and not waiting_task.done():
                    waiting_task.cancel()
                if waiting_message:
                    waiting_message.set_text(assistant_reply)
                    waiting_message.classes(remove='text-gray-500 italic')
            
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
            # 确保等待动画任务被取消
            animation_active = False
            if waiting_task and not waiting_task.done():
                waiting_task.cancel()
            
            # 🔓 无论是否出现异常，都要重新启用输入框和发送按钮
            self.input_ref['widget'].set_enabled(True)
            self.send_button_ref['widget'].set_enabled(True)
            # 重新聚焦到输入框，提升用户体验
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
    #endregion 用户输入提交相关处理逻辑

    # 重置和加载历史对话内容
    def restore_welcome_message(self):
        """恢复欢迎消息"""
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

    def render_chat_history(self, chat_id):
        """渲染聊天历史内容"""
        try:
            # 这里应该从数据库加载聊天历史
            # 暂时使用占位符逻辑
            ui.notify(f'加载聊天历史 {chat_id}', type='info')
            
            # 清空当前消息容器
            if self.messages:
                self.messages.clear()
            
            # 清空欢迎消息
            if self.welcome_message_container:
                self.welcome_message_container.clear()
            
            # 模拟加载历史消息
            # 实际实现时应该从数据库加载 chat_id 对应的消息
            # loaded_messages = load_chat_messages_from_db(chat_id)
            # self.chat_data_state.current_chat_messages = loaded_messages
            
            # 重新渲染所有历史消息
            # for message in self.chat_data_state.current_chat_messages:
            #     self.render_single_message(message)
            
        except Exception as e:
            ui.notify(f'加载聊天历史失败: {str(e)}', type='negative')

    def render_single_message(self, message: Dict[str, Any]):
        """渲染单条消息"""
        with self.messages:
            if message['role'] == 'user':
                user_avatar = static_manager.get_fallback_path(
                    static_manager.get_logo_path('user.svg'),
                    'https://robohash.org/user'
                )
                with ui.chat_message(
                    name='您',
                    avatar=user_avatar,
                    sent=True
                ).classes('w-full'):
                    ui.label(message['content']).classes('whitespace-pre-wrap break-words')
            
            elif message['role'] == 'assistant':
                robot_avatar = static_manager.get_fallback_path(
                    static_manager.get_logo_path('robot_txt.svg'),
                    'https://robohash.org/ui'
                )
                with ui.chat_message(
                    name='AI',
                    avatar=robot_avatar
                ).classes('w-full'):
                    ui.markdown(message['content']).classes('w-full')

    # UI主聊天区域渲染函数
    def render_ui(self):
        """渲染主聊天区域UI"""
        # 主聊天区域 - 占据剩余空间
        with ui.column().classes('flex-grow h-full').style('position: relative; overflow: hidden;'):
            # 聊天消息区域 - 使用 scroll_area 提供更好的滚动体验
            self.scroll_area = ui.scroll_area().classes('w-full').style('height: calc(100% - 80px); padding-bottom: 20px;')

            with self.scroll_area:
                self.messages = ui.column().classes('w-full gap-2')
                
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
                ).props('outlined dense rounded rows=3')

                # 使用.on()方法监听keydown事件
                self.input_ref['widget'].on('keydown', self.handle_keydown)
                
                self.send_button_ref['widget'] = ui.button(
                    icon='send',
                    on_click=self.handle_message
                ).props('round dense ').classes('ml-2')

    def set_sidebar_components(self, switch, hierarchy_selector):
        """设置来自侧边栏的组件引用
        
        Args:
            switch: 提示数据开关组件
            hierarchy_selector: 层级选择器组件
        """
        self.switch = switch
        self.hierarchy_selector = hierarchy_selector