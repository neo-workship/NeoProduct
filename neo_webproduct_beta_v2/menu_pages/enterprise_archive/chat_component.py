"""
聊天组件 - 类似Vue组件，可复用的聊天UI
"""
import re
import asyncio
from datetime import datetime
from nicegui import ui, app
from typing import Optional, List, Dict,Any
from component import static_manager
from .hierarchy_selector_component import HierarchySelector
from .config import (
    get_model_options_for_select, 
    get_model_config, 
    get_default_model,
    reload_llm_config,
    get_model_config_info,
    get_prompt_options_for_select,
    get_system_prompt,
    get_examples,
    get_default_prompt,
    reload_prompt_config
)
    
def chat_page():
    model_options = get_model_options_for_select()  # 返回 ['deepseek-chat', 'moonshot-v1-8k', 'qwen-plus', ...]
    default_model = get_default_model() or 'deepseek-chat'
    current_model_config = {'selected_model': default_model, 'config': None}
    
    # 存储当前状态
    current_state = {
        'model_options': model_options,
        'default_model': default_model,
        'selected_model': default_model,
        'model_select_widget': None,
        'prompt_select_widget': None  # 添加这行
    }
    
    # 🔥 新增：记录当前聊天中的消息
    current_chat_messages: List[Dict] = []
    # 添加以下代码 - 提示词初始化
    prompt_options = get_prompt_options_for_select()
    default_prompt = get_default_prompt() or (prompt_options[0] if prompt_options else None)
    current_prompt_config = {
        'selected_prompt': default_prompt,
        'system_prompt': get_system_prompt(default_prompt) if default_prompt else '',
        'examples': get_examples(default_prompt) if default_prompt else {}
    }

    #region 解析markdown并映射为ui组件展示 
    async def optimize_content_display(reply_label, content: str, chat_content_container=None):
        """
        优化内容显示 - 将特殊内容转换为专业NiceGUI组件
        
        Args:
            reply_label: 当前的markdown组件引用
            content: 完整的AI回复内容
            chat_content_container: 聊天内容容器引用
        """
        try:
            # 1. 解析内容，检测特殊块
            parsed_blocks = parse_content_with_mistune(content)
            
            # 2. 判断是否需要优化
            if has_special_content(parsed_blocks):
                # 3. 显示优化提示
                show_optimization_hint(reply_label)
                
                # 4. 短暂延迟，让用户看到提示
                await asyncio.sleep(0.1)
                
                # 5. 获取正确的容器
                container = chat_content_container if chat_content_container else reply_label
                
                # 6. 重新渲染混合组件
                await render_optimized_content(container, parsed_blocks)
            
        except Exception as e:
            print(f"内容优化失败，保持原始显示: {e}")
    # ==================== Mistune解析 ====================
    def parse_content_with_mistune(content: str) -> List[Dict[str, Any]]:
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
        table_blocks = extract_tables(content)
        blocks.extend(table_blocks)
        
        # 2. 检测Mermaid图表
        mermaid_blocks = extract_mermaid(content)
        blocks.extend(mermaid_blocks)
        
        # 3. 检测代码块
        code_blocks = extract_code_blocks(content)
        blocks.extend(code_blocks)
        
        # 4. 检测LaTeX公式
        math_blocks = extract_math(content)
        blocks.extend(math_blocks)
        
        # 5. 检测标题
        heading_blocks = extract_headings(content)
        blocks.extend(heading_blocks)
        
        # 6. 按位置排序
        blocks.sort(key=lambda x: x['start_pos'])
        
        # 7. 填充文本块
        text_blocks = fill_text_blocks(content, blocks)
        
        # 8. 合并并重新排序
        all_blocks = blocks + text_blocks
        all_blocks.sort(key=lambda x: x['start_pos'])
        
        return all_blocks

    # ==================== 内容检测函数 ====================
    def extract_tables(content: str) -> List[Dict[str, Any]]:
        """提取表格内容"""
        tables = []
        # 匹配markdown表格模式
        pattern = r'(\|.*\|.*\n\|[-\s\|]*\|.*\n(?:\|.*\|.*\n)*)'
        
        for match in re.finditer(pattern, content):
            table_data = parse_table_data(match.group(1))
            if table_data:  # 确保解析成功
                tables.append({
                    'type': 'table',
                    'content': match.group(1),
                    'data': table_data,
                    'start_pos': match.start(),
                    'end_pos': match.end()
                })
        
        return tables

    def extract_mermaid(content: str) -> List[Dict[str, Any]]:
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

    def extract_code_blocks(content: str) -> List[Dict[str, Any]]:
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

    def extract_math(content: str) -> List[Dict[str, Any]]:
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

    def extract_headings(content: str) -> List[Dict[str, Any]]:
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

    def fill_text_blocks(content: str, special_blocks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
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

    # ==================== 数据解析函数 ====================
    def parse_table_data(table_text: str) -> Optional[Dict[str, Any]]:
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
            print(f"表格解析失败: {e}")
            return None

    # ==================== 检测和渲染函数 ====================
    def has_special_content(blocks: List[Dict[str, Any]]) -> bool:
        """检查是否包含需要优化的特殊内容"""
        special_types = {'table', 'mermaid', 'code', 'math', 'heading'}
        return any(block['type'] in special_types for block in blocks)

    def show_optimization_hint(reply_label):
        """显示优化提示"""
        try:
            reply_label.set_text("🔄 正在优化内容显示...")
        except:
            pass  # 如果设置失败，忽略错误

    async def render_optimized_content(container, blocks: List[Dict[str, Any]]):
        """渲染优化后的混合内容"""
        from nicegui import ui
        
        container.clear()
        
        with container:
            for block in blocks:
                try:
                    if block['type'] == 'table':
                        create_table_component(block['data'])
                    elif block['type'] == 'mermaid':
                        create_mermaid_component(block['content'])
                    elif block['type'] == 'code':
                        create_code_component(block['content'], block.get('language', 'text'))
                    elif block['type'] == 'math':
                        create_math_component(block['content'], block.get('display_mode', 'block'))
                    elif block['type'] == 'heading':
                        create_heading_component(block['content'], block.get('level', 1))
                    elif block['type'] == 'text':
                        create_text_component(block['content'])
                    else:
                        # 兜底：用markdown显示
                        ui.markdown(block['content']).classes('w-full')
                
                except Exception as e:
                    print(f"渲染块失败 {block['type']}: {e}")
                    # 失败时用markdown显示原内容
                    ui.markdown(block['content']).classes('w-full')

    # ==================== NiceGUI组件创建函数 ====================
    def create_table_component(table_data: Dict[str, Any]):
        """创建表格组件"""
        from nicegui import ui
        
        if table_data and table_data.get('columns') and table_data.get('rows'):
            ui.table(
                columns=table_data['columns'],
                rows=table_data['rows']
            ).classes('w-full').props('flat bordered dense')
        else:
            ui.label("⚠️ 表格数据解析失败").classes('text-orange-600')

    def create_mermaid_component(mermaid_content: str):
        """创建Mermaid图表组件"""
        from nicegui import ui
        
        try:
            ui.mermaid(mermaid_content).classes('w-full')
        except Exception as e:
            print(f"Mermaid渲染失败: {e}")
            ui.code(mermaid_content, language='mermaid').classes('w-full')

    def create_code_component(code_content: str, language: str):
        """创建代码块组件"""
        from nicegui import ui
        
        ui.code(code_content, language=language).classes('w-full')

    def create_math_component(math_content: str, display_mode: str):
        """创建数学公式组件"""
        from nicegui import ui
        
        if display_mode == 'block':
            # 块级公式
            ui.markdown(f"$${math_content}$$", extras=['latex']).classes('w-full text-center')
        else:
            # 行内公式
            ui.markdown(f"${math_content}$", extras=['latex']).classes('w-full')

    def create_heading_component(text: str, level: int):
        """创建标题组件"""
        from nicegui import ui
        
        size_classes = {
            1: 'text-3xl',
            2: 'text-2xl', 
            3: 'text-xl',
            4: 'text-lg',
            5: 'text-base',
            6: 'text-sm'
        }
        
        size_class = size_classes.get(level, 'text-base')
        ui.label(text).classes(f'{size_class} font-bold text-primary mb-2 mt-4')

    def create_text_component(text_content: str):
        """创建普通文本组件"""
        from nicegui import ui
        
        if text_content.strip():
            ui.markdown(text_content, extras=['tables', 'mermaid', 'latex', 'fenced-code-blocks']).classes('w-full')

    #endregion  解析markdown并映射为ui组件展示 

    #region 模型选择相关逻辑 
    def on_model_change(e):
        """模型选择变化事件处理"""
        selected_model_key = e.value
        model_config = get_model_config(selected_model_key)
        
        # 更新当前模型配置
        current_model_config['selected_model'] = selected_model_key
        current_model_config['config'] = model_config
        
        # 🔥 同步更新 current_state，保持状态一致性
        current_state['selected_model'] = selected_model_key
        
        # 显示选择的模型信息
        if model_config:
            ui.notify(f'已切换到模型: {model_config.get("name", selected_model_key)}')
            print(f"模型配置: {model_config}")  # 用于调试
        else:
            ui.notify(f'已切换到模型: {selected_model_key}')

    def on_refresh_model_config():
        """刷新模型配置"""
        try:
            # 显示加载提示
            ui.notify('正在刷新配置...', type='info')
            
            # 重新加载配置
            success = reload_llm_config()
            
            if success:
                # 获取新的配置数据
                new_options = get_model_options_for_select()
                new_default = get_default_model() or 'deepseek-chat'
                
                # 更新状态
                current_state['model_options'] = new_options
                current_state['default_model'] = new_default
                
                # 更新UI组件的选项
                if current_state['model_select_widget']:
                    # 保存当前选择的模型（如果仍然可用的话）
                    current_selection = current_state['selected_model']
                    if current_selection not in new_options:
                        current_selection = new_default
                    
                    # 更新select组件
                    current_state['model_select_widget'].set_options(new_options)
                    current_state['model_select_widget'].set_value(current_selection)
                    current_state['selected_model'] = current_selection
                    
                    # 🔥 同步更新 current_model_config，保持状态一致性
                    current_model_config['selected_model'] = current_selection
                    current_model_config['config'] = get_model_config(current_selection)
                
                # 显示刷新结果
                config_info = get_model_config_info()
                ui.notify(
                    f'配置刷新成功！共加载 {config_info["total_models"]} 个模型，'
                    f'其中 {config_info["enabled_models"]} 个已启用',
                    type='positive'
                )
                
            else:
                ui.notify('配置刷新失败，请检查配置文件', type='negative')
                
        except Exception as e:
            ui.notify(f'刷新配置时出错: {str(e)}', type='negative')
    
    def on_prompt_change(e):
        """提示词选择变化事件处理"""
        selected_prompt_key = e.value
        
        # 获取系统提示词内容和示例
        system_prompt = get_system_prompt(selected_prompt_key)
        examples = get_examples(selected_prompt_key)
        
        # 更新当前提示词配置
        current_prompt_config['selected_prompt'] = selected_prompt_key
        current_prompt_config['system_prompt'] = system_prompt or ''
        current_prompt_config['examples'] = examples or {}
        
        # 显示选择信息
        ui.notify(f'已切换到提示词: {selected_prompt_key}')
    
    def on_refresh_prompt_config():
        """刷新提示词配置"""
        try:
            ui.notify('正在刷新提示词配置...', type='info')
            success = reload_prompt_config()
            
            if success:
                nonlocal prompt_options, default_prompt
                prompt_options = get_prompt_options_for_select()
                new_default = get_default_prompt() or (prompt_options[0] if prompt_options else None)
                
                if current_state.get('prompt_select_widget'):
                    current_selection = current_prompt_config['selected_prompt']
                    if current_selection not in prompt_options:
                        current_selection = new_default
                    
                    current_state['prompt_select_widget'].set_options(prompt_options)
                    current_state['prompt_select_widget'].set_value(current_selection)
                    
                    current_prompt_config['selected_prompt'] = current_selection
                    current_prompt_config['system_prompt'] = get_system_prompt(current_selection) if current_selection else ''
                    current_prompt_config['examples'] = get_examples(current_selection) if current_selection else {}
                
                ui.notify(f'提示词配置刷新成功，共加载 {len(prompt_options)} 个模板', type='positive')
            else:
                ui.notify('提示词配置刷新失败', type='negative')
                
        except Exception as e:
            ui.notify(f'刷新提示词配置时发生错误: {str(e)}', type='negative')
    # endregion 模型选择相关逻辑
    
    #region 输入提交相关逻辑
    async def scroll_to_bottom_smooth():
        """平滑滚动到底部，使用更可靠的方法"""
        try:
            # 方法1: 使用 scroll_area 的内置方法，设置 percent > 1 确保滚动到底部
            scroll_area.scroll_to(percent=1.1)
            # 添加小延迟确保滚动完成
            await asyncio.sleep(0.09)
        except Exception as e:
            print(f"滚动出错: {e}")

    # 完整的handle_message函数实现
    async def handle_message(event=None):
        user_message = input_ref['widget'].value.strip()
        if not user_message:
            return
        # 🔒 禁用输入框和发送按钮，防止重复发送
        input_ref['widget'].set_enabled(False)
        send_button_ref['widget'].set_enabled(False)
        
        # 清空输入框
        input_ref['widget'].set_value('')

        # 等待效果相关变量
        waiting_message = None
        waiting_dots = ""
        assistant_reply = ""
        waiting_task = None  # 初始化变量
        
        try:
            # 删除欢迎消息
            if welcome_message_container:
                welcome_message_container.clear()

            # 🔥 记录用户消息到聊天历史
            from datetime import datetime
            current_chat_messages.append({
                'role': 'user',
                'content': user_message,
                'timestamp': datetime.now().isoformat()
            })

            # 用户消息
            with messages:
                user_avatar = static_manager.get_fallback_path(
                    static_manager.get_logo_path('user.svg'),
                    'https://robohash.org/user   '
                )
                with ui.chat_message(
                    name='您',
                    avatar=user_avatar,
                    sent=True
                ).classes('w-full'):
                    ui.label(user_message).classes('whitespace-pre-wrap break-words')

            # 添加用户消息后立即滚动到底部
            await scroll_to_bottom_smooth()

            # 🔥 添加等待效果的机器人消息
            with messages:
                robot_avatar = static_manager.get_fallback_path(
                    static_manager.get_logo_path('robot_txt.svg'),
                    'https://robohash.org/ui   '
                )
                with ui.chat_message(
                    name='AI',
                    avatar=robot_avatar
                ).classes('w-full') as ai_message_container:
                    waiting_message = ui.label('正在思考...').classes('whitespace-pre-wrap text-gray-500 italic')

            await scroll_to_bottom_smooth()

            # 🔥 启动等待动画 - 使用标志变量控制
            animation_active = True
            
            async def animate_waiting():
                nonlocal waiting_dots, animation_active
                dots_count = 0
                while animation_active and waiting_message:
                    dots_count = (dots_count % 3) + 1
                    waiting_dots = "." * dots_count
                    try:
                        waiting_message.set_text(f'正在思考{waiting_dots}')
                        await asyncio.sleep(0.5)  # 稍微放慢动画速度
                    except Exception:
                        # 如果组件已被销毁，退出动画
                        break

            # 启动等待动画任务
            waiting_task = asyncio.create_task(animate_waiting())

            # 🔥 使用真实的 AI 模型进行流式回复
            try:
                # 导入OpenAI客户端池
                from common.safe_openai_client_pool import get_openai_client
                from menu_pages.enterprise_archive.config import get_model_config
                
                # 使用 current_model_config 获取当前选择的模型，确保状态一致性
                selected_model = current_model_config['selected_model']
                model_config = current_model_config['config']
                
                # 如果配置为空，重新获取
                if not model_config:
                    model_config = get_model_config(selected_model)
                    current_model_config['config'] = model_config
                
                # 创建 OpenAI 客户端
                client = await get_openai_client(selected_model, get_model_config)
                
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
                    recent_messages = current_chat_messages[-20:]
                    print(f"prompt:{current_prompt_config['system_prompt']}")
                    if current_state.get('prompt_select_widget') and current_prompt_config.get('system_prompt'):
                        system_message = {
                            "role": "system", 
                            "content": current_prompt_config['system_prompt']
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
                                        reply_label = ui.label('').classes('w-full')
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
                                        reply_label = ui.label('').classes('w-full')
                                    reply_created = True
                                
                                # 更新回复内容
                                if reply_label and display_content.strip():
                                    reply_label.set_text(display_content.strip())
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
                                                reply_label = ui.label('').classes('w-full')
                                            reply_created = True
                                        
                                        # 更新前置内容
                                        if reply_label and display_content.strip():
                                            reply_label.set_text(display_content.strip())
                                else:
                                    # 正常显示内容：没有思考标签
                                    if reply_label:
                                        reply_label.set_text(temp_content)
                            
                            # 流式更新时滚动到底部
                            await scroll_to_bottom_smooth()
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
                                reply_label = ui.label('').classes('w-full')
                            reply_created = True
                        
                        if reply_label and final_reply_content.strip():
                            reply_label.set_text(final_reply_content.strip())
                            await optimize_content_display(reply_label, final_reply_content,chat_content_container)
                        
                        # 用于记录到聊天历史的内容（保留思考标签）
                        assistant_reply = final_content
                    else:
                        # 没有思考内容，直接显示
                        if not structure_created:
                            ai_message_container.clear()
                            with ai_message_container:
                                with ui.column().classes('w-full') as chat_content_container:
                                    reply_label = ui.label('').classes('w-full')
                        
                        if reply_label:
                            reply_label.set_text(final_content)
                            await optimize_content_display(reply_label, final_content,chat_content_container)
                            
                    
            except Exception as api_error:
                print(f"API调用错误: {api_error}")
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
            # print(f"🤖 AI的回复：", {assistant_reply})
            current_chat_messages.append({
                'role': 'assistant', 
                'content': assistant_reply,
                'timestamp': datetime.now().isoformat(),
                'model': current_model_config['selected_model']
            })

            # 完成回复后最终滚动
            await scroll_to_bottom_smooth()
        
        finally:
            # 确保等待动画任务被取消
            animation_active = False
            if waiting_task and not waiting_task.done():
                waiting_task.cancel()
            
            # 🔓 无论是否出现异常，都要重新启用输入框和发送按钮
            input_ref['widget'].set_enabled(True)
            send_button_ref['widget'].set_enabled(True)
            # 重新聚焦到输入框，提升用户体验
            input_ref['widget'].run_method('focus')

    # 保存聊天时去除think内容的辅助函数
    def has_think_content(messages):
        """检测消息列表是否包含think内容"""
        for msg in messages:
            if msg.get('role') == 'assistant' and '<think>' in msg.get('content', ''):
                return True
        return False

    # 移除<think>...</think>内容
    def remove_think_content(messages):
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

    # 聊天输入框事件处理
    def handle_keydown(e):
        """处理键盘事件 - 使用NiceGUI原生方法"""
        # 检查输入框是否已禁用，如果禁用则不处理按键事件
        if not input_ref['widget'].enabled:
            return
            
        # 获取事件详细信息
        key = e.args.get('key', '')
        shift_key = e.args.get('shiftKey', False)
        
        if key == 'Enter':
            if shift_key:
                # Shift+Enter: 允许换行，不做任何处理
                # NiceGUI会自动处理换行，我们不需要阻止默认行为
                pass
            else:
                # 单独的Enter: 发送消息
                # 阻止默认的换行行为
                ui.run_javascript('event.preventDefault();')
                # 异步调用消息处理函数
                ui.timer(0.01, lambda: handle_message(), once=True)
    #endregion 输入提交相关逻辑

    #region 新建会话相关逻辑
    async def on_create_new_chat():
        """新建对话 - 保存当前聊天记录并清空界面"""
        try:
            # 🔥 新增：先判断是否已有聊天记录，执行插入或更新操作
            if current_chat_messages:
                # 检查当前是否为加载的历史对话（通过检查 current_chat_messages 是否与某个历史记录匹配）
                existing_chat_id = get_current_loaded_chat_id()
                
                if existing_chat_id:
                    # 更新现有聊天记录
                    update_success = update_existing_chat_to_database(existing_chat_id)
                    if update_success:
                        ui.notify('对话已更新', type='positive')
                    else:
                        ui.notify('更新对话失败', type='negative')
                        return
                else:
                    # 插入新的聊天记录
                    save_success = save_chat_to_database()
                    if save_success:
                        ui.notify('对话已保存', type='positive')
                    else:
                        ui.notify('保存对话失败', type='negative')
                        return
                
                # 清空当前聊天记录
                current_chat_messages.clear()
                
                # 清空聊天界面
                messages.clear()
                
                # 恢复欢迎消息
                restore_welcome_message()
                
                # 🔥 新增：自动刷新聊天历史列表
                refresh_chat_history_list()
                
                # 滚动到顶部
                scroll_area.scroll_to(percent=0)
                
                # 重置当前加载的聊天ID
                reset_current_loaded_chat_id()
                
            else:
                # 如果没有聊天内容，仅清空界面
                messages.clear()
                welcome_message_container.clear()
                restore_welcome_message()
                scroll_area.scroll_to(percent=0)
                ui.notify('界面已重置', type='info')
                
        except Exception as e:
            ui.notify(f'创建新对话失败: {str(e)}', type='negative')
            print(f"创建新对话错误: {e}")
    
    def get_current_loaded_chat_id():
        """获取当前加载的聊天记录ID"""
        # 🔥 新增：通过全局变量跟踪当前加载的聊天ID
        if hasattr(get_current_loaded_chat_id, 'current_chat_id'):
            return get_current_loaded_chat_id.current_chat_id
        return None

    def set_current_loaded_chat_id(chat_id):
        """设置当前加载的聊天记录ID"""
        get_current_loaded_chat_id.current_chat_id = chat_id

    def reset_current_loaded_chat_id():
        """重置当前加载的聊天记录ID"""
        get_current_loaded_chat_id.current_chat_id = None

    def update_existing_chat_to_database(chat_id):
        """更新现有的聊天记录到数据库"""
        try:
            from auth import auth_manager
            from database_models.business_models.chat_history_model import ChatHistory
            from auth.database import get_db
            
            current_user = auth_manager.current_user
            if not current_user:
                ui.notify('用户未登录，无法更新聊天记录', type='warning')
                return False
            
            if not current_chat_messages:
                ui.notify('没有聊天记录需要更新', type='info')
                return False
            
            with get_db() as db:
                # 查找现有聊天记录
                chat_history = db.query(ChatHistory).filter(
                    ChatHistory.id == chat_id,
                    ChatHistory.created_by == current_user.id,
                    ChatHistory.is_deleted == False
                ).first()
                
                if not chat_history:
                    ui.notify('聊天记录不存在或无权限', type='negative')
                    return False
                
                # 更新聊天记录
                chat_history.messages = current_chat_messages.copy()
                chat_history.model_name = current_state['selected_model']
                
                # 🔥 使用模型的内置方法更新统计信息
                chat_history.update_message_stats()
                
                # 更新时间戳
                from sqlalchemy.sql import func
                chat_history.updated_at = func.now()
                
                db.commit()
                
                print(f"已更新聊天记录: {chat_history.title}")
                return True
                
        except Exception as e:
            print(f"更新聊天记录错误: {e}")
            ui.notify(f'更新聊天记录失败: {str(e)}', type='negative')
            return False

    def save_chat_to_database():
        """保存新的聊天记录到数据库 - 增加think内容处理"""
        try:
            from auth import auth_manager
            from database_models.business_models.chat_history_model import ChatHistory
            from database_models.business_utils import AuditHelper
            from auth.database import get_db
            
            current_user = auth_manager.current_user
            if not current_user:
                ui.notify('用户未登录，无法保存聊天记录', type='warning')
                return False
            
            if not current_chat_messages:
                ui.notify('没有聊天记录需要保存', type='info')
                return False
            
            # 生成聊天标题（使用第一条用户消息的前20个字符）
            title = "新对话"
            for msg in current_chat_messages:
                if msg.get('role') == 'user':
                    content = msg.get('content', '')
                    title = content[:20] + ('...' if len(content) > 20 else '')
                    break
            
            # 🔥 处理think内容：检测是否有think内容，有则移除
            messages_to_save = current_chat_messages.copy()
            if has_think_content(messages_to_save):
                messages_to_save = remove_think_content(messages_to_save)
            
            with get_db() as db:
                # 创建聊天历史记录
                chat_history = ChatHistory(
                    title=title,
                    model_name=current_state['selected_model'],
                    messages=messages_to_save  # 🔥 使用处理后的消息
                )
                
                # 使用模型的内置方法更新统计信息
                chat_history.update_message_stats()
                
                # 设置审计字段
                AuditHelper.set_audit_fields(chat_history, current_user.id)
                
                db.add(chat_history)
                db.commit()
                
                print(f'聊天记录已保存: {title} (ID: {chat_history.id})')
                return True
                
        except Exception as e:
            print(f"保存聊天记录错误: {e}")
            ui.notify(f'保存聊天记录失败: {str(e)}', type='negative')
            return False

    def restore_welcome_message():
        """恢复欢迎消息"""
        with welcome_message_container:
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
    #endregion 新建会话相关逻辑

    #region 历史记录相关逻辑
    def load_chat_histories():
        """从数据库加载聊天历史列表 - 使用模型的优化方法"""
        try:
            from auth import auth_manager
            from database_models.business_models.chat_history_model import ChatHistory
            from auth.database import get_db
            
            current_user = auth_manager.current_user
            if not current_user:
                return []
            
            with get_db() as db:
                # 🔥 使用模型已定义的优化方法
                chat_histories = ChatHistory.get_user_recent_chats(
                    db_session=db, 
                    user_id=current_user.id, 
                    limit=20
                )
                
                # 转换为UI需要的数据结构
                history_list = []
                for chat in chat_histories:
                    # 🔥 利用模型的实例方法获取更丰富的信息
                    preview = chat.get_message_preview(30)  # 获取消息预览
                    duration_info = chat.get_duration_info()  # 获取时长信息
                    
                    history_list.append({
                        'id': chat.id,
                        'title': chat.title,
                        'preview': preview,  # 新增：消息预览
                        'created_at': chat.created_at.strftime('%Y-%m-%d %H:%M'),
                        'updated_at': chat.updated_at.strftime('%Y-%m-%d %H:%M'),
                        'last_message_at': chat.last_message_at.strftime('%Y-%m-%d %H:%M') if chat.last_message_at else None,  # 新增：最后消息时间
                        'message_count': chat.message_count,
                        'model_name': chat.model_name,
                        'duration_minutes': duration_info['duration_minutes'],  # 新增：对话时长
                        'chat_object': chat  # 保存完整对象，供后续操作使用
                    })
                
                return history_list
                
        except Exception as e:
            print(f"加载聊天历史失败: {e}")
            ui.notify('加载聊天历史失败', type='negative')
            return []
        
    def on_load_chat_history(chat_id):
        """加载指定的聊天历史到当前对话中 - 完善现有实现"""
        try:
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
                
                # 🔥 设置当前加载的聊天ID，用于后续更新判断
                set_current_loaded_chat_id(chat_id)
                
                # 清空当前聊天消息并加载历史消息
                current_chat_messages.clear()
                current_chat_messages.extend(chat.messages)
                
                # 清空聊天界面
                messages.clear()
                welcome_message_container.clear()
                
                # 重新渲染聊天历史消息
                for msg in chat.messages:
                    with messages:
                        if msg.get('role') == 'user':
                            user_avatar = static_manager.get_fallback_path(
                                static_manager.get_logo_path('user.svg'),
                                'https://robohash.org/user'
                            )
                            with ui.chat_message(
                                name='您',
                                avatar=user_avatar,
                                sent=True
                            ).classes('w-full'):
                                ui.label(msg.get('content', '')).classes('whitespace-pre-wrap break-words')
                        
                        elif msg.get('role') == 'assistant':
                            robot_avatar = static_manager.get_fallback_path(
                                static_manager.get_logo_path('robot_txt.svg'),
                                'https://robohash.org/ui'
                            )
                            with ui.chat_message(
                                name='AI',
                                avatar=robot_avatar
                            ).classes('w-full'):
                                ui.label(msg.get('content', '')).classes('whitespace-pre-wrap')
                
                # 滚动到底部
                ui.timer(0.1, lambda: scroll_area.scroll_to(percent=1), once=True)
                ui.notify(f'已加载聊天: {chat.title}', type='positive')
                
        except Exception as e:
            print(f"加载聊天历史错误: {e}")
            ui.notify('加载聊天失败', type='negative')
    
    def on_edit_chat_history(chat_id):
        """编辑聊天历史标题"""
        
        try:
            from auth import auth_manager
            from database_models.business_models.chat_history_model import ChatHistory
            from auth.database import get_db
            from sqlalchemy.sql import func
            
            current_user = auth_manager.current_user
            if not current_user:
                ui.notify('用户未登录，无法编辑聊天记录', type='warning')
                return
            
            with get_db() as db:
                # 查找聊天记录
                chat_history = db.query(ChatHistory).filter(
                    ChatHistory.id == chat_id,
                    ChatHistory.created_by == current_user.id,
                    ChatHistory.is_deleted == False
                ).first()
                
                if not chat_history:
                    ui.notify('聊天记录不存在或无权限编辑', type='negative')
                    return
                
                # 获取当前数据用于显示
                current_title = chat_history.title
                created_at = chat_history.created_at.strftime("%Y-%m-%d %H:%M")
                message_count = chat_history.message_count
                model_name = chat_history.model_name
                
                # 创建编辑对话框
                with ui.dialog() as dialog:
                    with ui.card().classes('w-96'):
                        with ui.column().classes('w-full '):
                            ui.label('编辑聊天标题').classes('text-lg font-medium')
                            
                            # 标题输入框
                            title_input = ui.input(
                                label='聊天标题',
                                value=current_title,
                                placeholder='请输入新的聊天标题'
                            ).classes('w-full')
                            
                            # 显示聊天信息
                            with ui.column().classes('gap-1'):
                                ui.label(f'创建时间: {created_at}').classes('text-sm text-gray-600')
                                ui.label(f'消息数量: {message_count}条').classes('text-sm text-gray-600')
                                if model_name:
                                    ui.label(f'AI模型: {model_name}').classes('text-sm text-gray-600')
                            
                            def save_title():
                                """保存新标题"""
                                new_title = title_input.value.strip()
                                if not new_title:
                                    ui.notify('标题不能为空', type='warning')
                                    return
                                
                                if len(new_title) > 200:
                                    ui.notify('标题长度不能超过200个字符', type='warning')
                                    return
                                
                                try:
                                    # 重新在新的数据库会话中查找并更新
                                    with get_db() as update_db:
                                        update_chat = update_db.query(ChatHistory).filter(
                                            ChatHistory.id == chat_id,
                                            ChatHistory.created_by == current_user.id,
                                            ChatHistory.is_deleted == False
                                        ).first()
                                        
                                        if not update_chat:
                                            ui.notify('聊天记录不存在', type='negative')
                                            return
                                        
                                        # 直接更新字段
                                        update_chat.title = new_title
                                        update_chat.updated_at = func.now()
                                        
                                        update_db.commit()
                                    
                                    # 刷新聊天历史列表
                                    refresh_chat_history_list()
                                    
                                    ui.notify(f'标题已更新为: {new_title}', type='positive')
                                    dialog.close()
                                    
                                except Exception as e:
                                    print(f"更新聊天标题错误: {e}")
                                    ui.notify(f'更新标题失败: {str(e)}', type='negative')
                            
                            # 按钮区域
                            with ui.row().classes('w-full justify-end gap-2'):
                                ui.button('取消', on_click=dialog.close).props('flat')
                                ui.button('保存', on_click=save_title).props('color=primary')
                
                dialog.open()
                
        except Exception as e:
            print(f"编辑聊天历史错误: {e}")
            ui.notify(f'编辑聊天失败: {str(e)}', type='negative')

    def on_delete_chat_history(chat_id):
        """删除聊天历史 - 使用软删除功能"""
        
        def confirm_delete():
            """确认删除操作"""
            try:
                from auth import auth_manager
                from database_models.business_models.chat_history_model import ChatHistory
                from auth.database import get_db
                from sqlalchemy.sql import func
                
                current_user = auth_manager.current_user
                if not current_user:
                    ui.notify('用户未登录，无法删除聊天记录', type='warning')
                    return
                
                with get_db() as db:
                    # 查找聊天记录
                    chat_history = db.query(ChatHistory).filter(
                        ChatHistory.id == chat_id,
                        ChatHistory.created_by == current_user.id,
                        ChatHistory.is_deleted == False
                    ).first()
                    
                    if not chat_history:
                        ui.notify('聊天记录不存在或无权限删除', type='negative')
                        return
                    
                    # 保存标题用于通知
                    chat_title = chat_history.title
                    
                    # 直接在数据库会话中进行软删除操作，避免会话问题
                    chat_history.is_deleted = True
                    chat_history.deleted_at = func.now()
                    chat_history.deleted_by = current_user.id
                    chat_history.is_active = False
                    
                    db.commit()
                    
                    # 如果删除的是当前加载的聊天，需要重置界面
                    current_loaded_id = get_current_loaded_chat_id()
                    if current_loaded_id == chat_id:
                        # 清空当前聊天
                        current_chat_messages.clear()
                        messages.clear()
                        welcome_message_container.clear()
                        restore_welcome_message()
                        reset_current_loaded_chat_id()
                        
                    # 刷新聊天历史列表
                    refresh_chat_history_list()
                    
                    ui.notify(f'已删除聊天: {chat_title}', type='positive')
                    
            except Exception as e:
                print(f"删除聊天历史错误: {e}")
                ui.notify(f'删除聊天失败: {str(e)}', type='negative')
        
        # 显示确认对话框
        with ui.dialog() as dialog:
            with ui.card().classes('w-80'):
                with ui.column().classes('w-full'):
                    ui.icon('warning', size='lg').classes('text-orange-500 mx-auto')
                    ui.label('确认删除聊天记录？').classes('text-lg font-medium text-center')
                    ui.label('删除后可以在回收站中恢复').classes('text-sm text-gray-600 text-center')
                    
                    with ui.row().classes('w-full justify-end gap-2'):
                        ui.button('取消', on_click=dialog.close).props('flat')
                        ui.button('删除', on_click=lambda: [confirm_delete(), dialog.close()]).props('color=negative')
        
        dialog.open()
    
    def create_chat_history_list():
        """创建聊天历史列表组件"""
        # 加载聊天历史数据
        chat_histories = load_chat_histories()
        
        if not chat_histories:
            # 如果没有历史记录，显示空状态
            with ui.column().classes('w-full text-center'):
                ui.icon('chat_bubble_outline', size='lg').classes('text-gray-400 mb-2')
                ui.label('暂无聊天记录').classes('text-gray-500 text-sm')
            return
        
        # 创建聊天历史列表
        with ui.list().classes('w-full').props('dense separator'):
            for history in chat_histories:
                # 为每个历史记录创建一个item容器，直接绑定点击事件
                with ui.item(on_click=lambda chat_id=history['id']: on_load_chat_history(chat_id)).classes('cursor-pointer'):
                    # 主要内容区域
                    with ui.item_section():
                        # 聊天标题
                        ui.item_label(history['title']).classes('font-medium')
                        # 时间和统计信息
                        info_text = f"{history['updated_at']} • {history['message_count']}条消息"
                        if history['duration_minutes'] > 0:
                            info_text += f" • {history['duration_minutes']}分钟"
                        if history['model_name']:
                            info_text += f" • {history['model_name']}"
                        ui.item_label(info_text).props('caption').classes('text-xs')
                    
                    # 右侧按钮区域
                    with ui.item_section().props('side'):
                        with ui.row().classes('gap-1'):
                            # 🔥 使用 click.stop 阻止事件冒泡
                            # 编辑按钮
                            ui.button(
                                icon='edit'
                            ).on('click.stop', lambda chat_id=history['id']: on_edit_chat_history(chat_id)).props('dense flat round size="sm"').classes('text-blue-600').tooltip('编辑')
                            
                            # 删除按钮
                            ui.button(
                                icon='delete'
                            ).on('click.stop', lambda chat_id=history['id']: on_delete_chat_history(chat_id)).props('dense flat round size="sm"').classes('text-red-600').tooltip('删除')
        
    def refresh_chat_history_list():
        """刷新聊天历史列表 - 完善现有实现"""
        try:
            # 清空容器
            history_list_container.clear()
            
            # 重新创建列表
            with history_list_container:
                create_chat_history_list()
                
            ui.notify('聊天历史已刷新', type='positive')
            
        except Exception as e:
            print(f"刷新聊天历史失败: {e}")
            ui.notify('刷新失败', type='negative')
    #endregion 历史记录相关逻辑
    
    #region UI区域
    # 添加全局样式，保持原有样式并添加scroll_area优化
    ui.add_head_html('''
        <style>
        /* 聊天组件专用样式 - 只影响聊天组件内部，不影响全局 */
        .chat-archive-container {
            /*overflow: hidden !important;*/
            height: calc(100vh - 145px) !important;
            margin: 0 !important;
            padding: 0 !important;
            overflow-y: auto !important;
        }
                     
        .chat-archive-sidebar {
            border-right: 1px solid #e5e7eb;
            overflow-y: auto;
        }
        .chat-archive-sidebar::-webkit-scrollbar {
            width: 2px;
        }
        .chat-archive-sidebar::-webkit-scrollbar-track {
            background: transparent;
        }
        .chat-archive-sidebar::-webkit-scrollbar-thumb {
            background-color: #d1d5db;
            border-radius: 3px;
        }
        .chat-archive-sidebar::-webkit-scrollbar-thumb:hover {
            background-color: #9ca3af;
        }
        /* 优化 scroll_area 内容区域的样式 */
        .q-scrollarea__content {
            min-height: 100%;
        }
        .chathistorylist-hide-scrollbar {
            overflow-y: auto;
            scrollbar-width: none;
            -ms-overflow-style: none;
        }
        .chathistorylist-scrollbar::-webkit-scrollbar {
            display: none;
        }
    </style>
    ''')
    
    # 主容器 - 使用水平布局
    with ui.row().classes('w-full h-full chat-archive-container').style('height: calc(100vh - 120px); margin: 0; padding: 0;'):   
        # 侧边栏 - 固定宽度
        with ui.column().classes('chat-archive-sidebar h-full').style('width: 280px; min-width: 280px;'):
            # 侧边栏标题
            with ui.row().classes('w-full'):
                ui.icon('menu', size='md').classes('text-gray-600')
                ui.label('功能菜单').classes('text-lg font-semibold')
            
            # 侧边栏内容 - 完全按照原有结构
            with ui.column().classes('w-full items-center'):
                # 添加按钮
                ui.button('新建对话', icon='add', on_click=on_create_new_chat).classes('w-64').props('outlined')
                
                # 选择模型expansion组件
                with ui.expansion('选择模型', icon='view_in_ar').classes('w-full'):
                    with ui.column().classes('w-full'):
                        # 配置管理按钮行
                        with ui.row().classes('w-full'):
                            ui.button(
                                '刷新配置', 
                                icon='refresh',
                                on_click=on_refresh_model_config
                            ).classes('text-xs').props('dense flat color="primary"').style('min-width: 80px;')
                        
                        # 模型选择下拉框
                        current_state['model_select_widget'] = ui.select(
                            options=current_state['model_options'],
                            value=current_state['default_model'],
                            with_input=True,
                            on_change=on_model_change
                        ).classes('w-full').props('autofocus dense')

                # 上下文模板expansion组件
                with ui.expansion('上下文模板', icon='pattern').classes('w-full'):
                    with ui.column().classes('w-full'):
                        # 配置管理按钮行
                        with ui.row().classes('w-full'):
                            ui.button(
                                '刷新配置', 
                                icon='refresh',
                                on_click=on_refresh_prompt_config
                            ).classes('text-xs').props('dense flat color="primary"').style('min-width: 80px;')
                        
                        # 提示词选择下拉框
                        current_state['prompt_select_widget'] = ui.select(
                            options=prompt_options, 
                            value=default_prompt, 
                            with_input=True,
                            on_change=on_prompt_change
                        ).classes('w-full').props('autofocus dense')

                # select数据expansion组件
                with ui.expansion('提示数据', icon='tips_and_updates').classes('w-full'):
                    with ui.column().classes('w-full chathistorylist-hide-scrollbar').style('flex-grow: 1; '):
                        switch = ui.switch('启用')
                        HierarchySelector
                        hierarchy_selector = HierarchySelector(multiple=True)
                        hierarchy_selector.render_column()
                       
                # 聊天历史expansion组件
                with ui.expansion('历史消息', icon='history').classes('w-full'):
                    with ui.column().classes('w-full'):
                        # 添加刷新按钮
                        with ui.row().classes('w-full'):
                            ui.button(
                                '刷新历史', 
                                icon='refresh',
                                on_click=lambda: refresh_chat_history_list()
                            ).classes('text-xs').props('dense flat color="primary"').style('min-width: 80px;')
                        
                        # 聊天历史列表容器
                        history_list_container = ui.column().classes('w-full h-96 chathistorylist-hide-scrollbar')
                        with history_list_container:
                            create_chat_history_list()
        
        # 主聊天区域 - 占据剩余空间
        with ui.column().classes('flex-grow h-full').style('position: relative; overflow: hidden;'):
            # 聊天消息区域 - 使用 scroll_area 提供更好的滚动体验
            scroll_area = ui.scroll_area().classes('w-full').style('height: calc(100% - 80px); padding-bottom: 20px;')

            with scroll_area:
                messages = ui.column().classes('w-full gap-2')
                
                # 欢迎消息（可能会被删除）
                welcome_message_container = ui.column().classes('w-full')
                with welcome_message_container:
                    restore_welcome_message()
                    
            # 输入区域 - 固定在底部，距离底部10px
            with ui.row().classes('w-full items-center gap-2 rounded ').style(
                'position: absolute; bottom: 10px; left: 10px; right: 10px; z-index: 1000; '
                'margin: 0 auto; max-width: calc(100% - 20px);'
            ):    
                # 提前声明可变对象，供内部嵌套函数读写
                input_ref = {'widget': None}

                # 为发送按钮创建引用容器
                send_button_ref = {'widget': None}

                # 创建textarea并绑定事件
                input_ref['widget'] = ui.textarea(
                    placeholder='请输入您的消息...(Enter发送，Shift+Enter换行)'
                ).classes('flex-grow').style(
                    'min-height: 44px; max-height: 120px; resize: none;'
                ).props('outlined dense rounded rows=3')

                # 使用.on()方法监听keydown事件
                input_ref['widget'].on('keydown', handle_keydown)
                
                send_button_ref['widget'] = ui.button(
                    icon='send',
                    on_click=handle_message
                ).props('round dense ').classes('ml-2')
    #endregion UI区域