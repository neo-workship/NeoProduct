import re
import asyncio
from datetime import datetime
from nicegui import ui, app
from typing import Optional, List, Dict, Any
from component import static_manager
from .chat_data_state import ChatDataState
from .markdown_ui_parser import MarkdownUIParser

class ChatAreaManagerPro:
    """主聊天区域管理器 - 负责聊天内容展示和用户交互"""
    
    def __init__(self, chat_data_state: ChatDataState):
        """初始化聊天区域管理器
        Args:
            chat_data_state: 聊天数据状态对象
        """
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

    #region 等待效果相关方法
    async def start_waiting_effect(self, message="正在处理"):
        """启动等待效果
        Args:
            message: 等待提示文本，默认为"正在处理"
        """
        # 添加等待效果的机器人消息容器
        with self.chat_messages_container:
            self.waiting_ai_message_container = ui.chat_message(
                name='AI',
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

    #region 用户输入提交相关处理逻辑
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
            
            if not (selected_values and selected_values['l3']):
                ui.notify("未选择足够的层级数据（至少需要3级）",type="warning")
                return user_message
                
            # 5. 根据是否选择4级数据决定拼接内容
            append_text = ""
            
            if selected_values['field']:  # 选择了4级数据
                # 处理字段信息进行拼接
                full_path_code = selected_values['full_path_code']
                field_value = selected_values['field']
                
                append_text = f"\n\n[数据路径] {full_path_code} \n\n [字段信息] {field_value}"
                
            else:  # 未选择4级，使用3级内容
                full_path_code = selected_values['full_path_code']
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

    async def render_single_message(self, message: Dict[str, Any], container=None):
        """渲染单条消息
        Args:
            message: 消息字典，包含role、content等字段
            container: 可选的容器，如果不提供则使用self.chat_messages_container
        """
        target_container = container if container is not None else self.chat_messages_container
        
        with target_container:
            if message['role'] == 'user':
                with ui.chat_message(
                    name='您',
                    avatar=self.user_avatar,
                    sent=True
                ).classes('w-full'):
                    ui.label(message['content']).classes('whitespace-pre-wrap break-words')
            
            elif message['role'] == 'assistant':
                with ui.chat_message(
                    name='AI',
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
        assistant_reply = ""
        
        try:
            # 删除欢迎消息
            if self.welcome_message_container:
                self.welcome_message_container.clear()

            # 动态添加提示数据
            user_message = self.enhance_user_message(user_message)
            user_msg_dict = {
                'role': 'user',
                'content': user_message,
                'timestamp': datetime.now().isoformat()
            }
            self.chat_data_state.current_chat_messages.append(user_msg_dict)

            # 使用统一的消息渲染方法渲染用户消息
            await self.render_single_message(user_msg_dict)
            # 添加用户消息后立即滚动到底部
            await self.scroll_to_bottom_smooth()
            # 启动等待效果
            await self.start_waiting_effect("正在处理")

            # 调用AI API
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
                    await self.stop_waiting_effect()
                    if self.waiting_message_label:
                        self.waiting_message_label.set_text(assistant_reply)
                        self.waiting_message_label.classes(remove='text-gray-500 italic')
                else:
                    # 准备对话历史（取最近20条消息）
                    recent_messages = self.chat_data_state.current_chat_messages[-20:]
                    if self.chat_data_state.current_state.prompt_select_widget \
                        and self.chat_data_state.current_prompt_config.system_prompt:
                        system_message = {
                            "role": "system", 
                            "content": self.chat_data_state.current_prompt_config.system_prompt
                        }
                        # 将系统消息插入到历史消息的最前面
                        recent_messages = [system_message] + recent_messages
                    
                    # 获取实际的模型名称
                    actual_model_name = model_config.get('model_name', selected_model) if model_config else selected_model
                    
                    # 流式调用 OpenAI API
                    stream_response = await asyncio.to_thread(
                        client.chat.completions.create,
                        model=actual_model_name,
                        messages=recent_messages,
                        max_tokens=2000,
                        temperature=0.7,
                        stream=True  # 启用流式响应
                    )

                     # ⭐ 关键修复：在开始处理流式响应时才停止等待动画
                    await self.stop_waiting_effect()
                    
                    # 处理流式响应
                    is_in_think = False
                    think_start_pos = -1

                    # 清空等待消息，准备流式显示
                    self.waiting_ai_message_container.clear()
                    # 初始化组件变量 - 关键：不预先创建任何组件
                    think_expansion = None
                    think_label = None
                    # 重置类属性
                    self.reply_label = None
                    self.chat_content_container = None
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
                                    self.waiting_ai_message_container.clear()
                                    with self.waiting_ai_message_container:
                                        with ui.column().classes('w-full') as self.chat_content_container:
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
                                self.waiting_ai_message_container.clear()
                                with self.waiting_ai_message_container:
                                    with ui.column().classes('w-full') as self.chat_content_container:
                                        self.reply_label = ui.markdown('').classes('w-full')
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
                                if self.chat_content_container and not reply_created:
                                    with self.chat_content_container:
                                        self.reply_label = ui.markdown('').classes('w-full')
                                    reply_created = True
                                
                                # 更新回复内容
                                if self.reply_label and display_content.strip():
                                    self.reply_label.set_content(display_content.strip())
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
                                        if display_content.strip() and self.chat_content_container and not reply_created:
                                            with self.chat_content_container:
                                                self.reply_label = ui.markdown('').classes('w-full')
                                            reply_created = True
                                        
                                        # 更新前置内容
                                        if self.reply_label and display_content.strip():
                                            self.reply_label.set_content(display_content.strip())
                                else:
                                    # 正常显示内容：没有思考标签
                                    if self.reply_label:
                                        self.reply_label.set_content(temp_content) 
                            # 流式更新时滚动到底部
                            await self.scroll_to_bottom_smooth()
                            await asyncio.sleep(0.05)  # 流式显示的间隔

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
                        if self.chat_content_container and not reply_created and final_reply_content.strip():
                            with self.chat_content_container:
                                self.reply_label = ui.markdown('').classes('w-full')
                            reply_created = True
                        
                        if self.reply_label and final_reply_content.strip():
                            self.reply_label.set_content(final_reply_content.strip())
                            await self.markdown_parser.optimize_content_display(self.reply_label, final_reply_content, self.chat_content_container)
                        # 用于记录到聊天历史的内容（保留思考标签）
                        assistant_reply = final_content
                    else:
                        # 没有思考内容，直接显示
                        if not structure_created:
                            self.waiting_ai_message_container.clear()
                            with self.waiting_ai_message_container:
                                with ui.column().classes('w-full') as self.chat_content_container:
                                    self.reply_label = ui.markdown('').classes('w-full')
                        
                        if self.reply_label:
                            self.reply_label.set_content(final_content)
                            await self.markdown_parser.optimize_content_display(self.reply_label, final_content, self.chat_content_container)        
            except Exception as api_error:
                print(f"api error:{str(api_error)}")
                assistant_reply = f"抱歉，调用AI服务时出现错误：{str(api_error)[:300]}..."
                ui.notify('AI服务调用失败，请稍后重试', type='negative')
                # 停止等待动画并显示错误信息
                await self.stop_waiting_effect()
                if self.waiting_message_label:
                    self.waiting_message_label.set_text(assistant_reply)
                    self.waiting_message_label.classes(remove='text-gray-500 italic')
            
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
            await self.stop_waiting_effect()
            # 🔓 无论是否出现异常，都要重新启用输入框和发送按钮
            self.input_ref['widget'].set_enabled(True)
            self.send_button_ref['widget'].set_enabled(True)
            # 重新聚焦到输入框，提升用户体验
            self.input_ref['widget'].run_method('focus')

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
    
    #清空聊天的方法
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
    #endregion 用户输入提交相关处理逻辑

    # 重置和加载历史对话内容
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
            # print(f"model:{model_name}\n model_config:{self.chat_data_state.current_model_config['config']}")
            # print(f"prompt:{prompt_name}\n prompt_config:{self.chat_data_state.current_prompt_config.system_prompt}")           
            self.chat_data_state.current_state.model_select_widget.set_value(model_name)
            self.chat_data_state.current_state.prompt_select_widget.set_value(prompt_name)
            self.chat_data_state.switch =  (prompt_name == '一企一档专家')
        except Exception as e:
            await self.stop_waiting_effect()
            await self.cleanup_waiting_effect()
            self.restore_welcome_message()
            ui.notify('加载聊天失败', type='negative')    

    # UI主聊天区域渲染函数
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