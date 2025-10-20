"""
ChatSidebarManager - 聊天侧边栏管理器
负责管理侧边栏的UI和相关业务逻辑
"""
from datetime import datetime
from nicegui import ui
from typing import Literal, Optional
from .chat_data_state import ChatDataState

# 注意: HierarchySelector 仍然从原位置导入
# from menu_pages.enterprise_archive.hierarchy_selector_component import HierarchySelector

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

class ChatSidebarManager:
    """聊天侧边栏管理器"""
    
    def __init__(
        self, 
        chat_data_state: ChatDataState, 
        chat_area_manager,
        sidebar_visible: bool = True, 
        default_model: Optional[str] = None, 
        default_prompt: Optional[str] = None,
        is_record_history: bool = True,
        data_input_mode: Literal['selector', 'textarea'] = 'selector'  # 🔥 新增参数
    ):
        """
        初始化侧边栏管理器
        
        Args:
            chat_data_state: 聊天数据状态对象
            chat_area_manager: 聊天区域管理器实例
            sidebar_visible: 侧边栏是否可见,默认为True
            default_model: 指定的默认模型,默认为None
            default_prompt: 指定的默认提示词,默认为None
            is_record_history: 是否记录聊天历史,默认为True
            data_input_mode: 数据输入模式,'selector'或'textarea'  # 🔥 新增说明
        """
        self.chat_data_state = chat_data_state
        self.chat_area_manager = chat_area_manager
        
        # UI组件引用
        self.history_list_container = None
        self.switch = None
        self.hierarchy_selector = None
        self.data_input_textarea = None  # 🔥 新增: textarea引用
        
        # 存储侧边栏可见性配置
        self.sidebar_visible = sidebar_visible
        self.is_record_history = is_record_history
        self.data_input_mode = data_input_mode  # 🔥 新增: 存储输入模式

        # 初始化数据
        self._initialize_data(default_model, default_prompt)
    
    # ... [保持原有的所有方法不变,包括 _initialize_data, on_model_change 等] ...

    def _initialize_data(self,default_model_param: str = None, default_prompt_param: str = None):
        """初始化数据状态"""
        # 初始化模型相关数据
        self.chat_data_state.model_options = get_model_options_for_select()
        # self.chat_data_state.default_model = get_default_model() or 'deepseek-chat'
        if default_model_param and \
           default_model_param in self.chat_data_state.model_options:
            self.chat_data_state.default_model = default_model_param
        else:
            self.chat_data_state.default_model = get_default_model() or 'deepseek-chat'
            if default_model_param:
                ui.notify(f"指定的模型 '{default_model_param}' 不存在，使用默认模型", type='warning')

        self.chat_data_state.current_model_config = {
            'selected_model': self.chat_data_state.default_model, 
            'config': get_model_config(self.chat_data_state.default_model)
        }
        
        # 初始化当前状态
        self.chat_data_state.current_state.model_options = self.chat_data_state.model_options
        self.chat_data_state.current_state.default_model = self.chat_data_state.default_model
        self.chat_data_state.current_state.selected_model = self.chat_data_state.default_model
        
        # 初始化提示词数据
        self.chat_data_state.prompt_options = get_prompt_options_for_select()
        # self.chat_data_state.default_prompt = get_default_prompt() or (
        #     self.chat_data_state.prompt_options[0] if self.chat_data_state.prompt_options else None
        # )
        if default_prompt_param and \
           default_prompt_param in self.chat_data_state.prompt_options:
            self.chat_data_state.default_prompt = default_prompt_param
        else:
            self.chat_data_state.default_prompt = get_default_prompt() or (
                self.chat_data_state.prompt_options[0] if self.chat_data_state.prompt_options else None
            )
            if default_prompt_param:
                ui.notify(f"指定的提示词 '{default_prompt_param}' 不存在，使用默认提示词", type='warning')

        self.chat_data_state.current_prompt_config.selected_prompt = self.chat_data_state.default_prompt
        self.chat_data_state.current_prompt_config.system_prompt = (
            get_system_prompt(self.chat_data_state.default_prompt) 
            if self.chat_data_state.default_prompt else ''
        )
        self.chat_data_state.current_prompt_config.examples = (
            get_examples(self.chat_data_state.default_prompt) 
            if self.chat_data_state.default_prompt else {}
        )
        self.chat_data_state.current_chat_id = None

    #region 模型选择相关处理逻辑
    def on_model_change(self, e):
        """模型选择变化事件处理"""
        selected_model = e.value
        
        # 更新当前状态
        self.chat_data_state.current_state.selected_model = selected_model
        self.chat_data_state.current_model_config['selected_model'] = selected_model
        self.chat_data_state.current_model_config['config'] = get_model_config(selected_model)
        
        # 显示选择信息
        ui.notify(f'已切换到模型: {selected_model}')
    
    def on_refresh_model_config(self):
        """刷新模型配置"""
        try:
            ui.notify('正在刷新模型配置...', type='info')
            success = reload_llm_config()
            
            if success:
                # 重新获取配置
                new_options = get_model_options_for_select()
                new_default = get_default_model() or 'deepseek-chat'
                
                # 更新数据状态
                self.chat_data_state.model_options = new_options
                self.chat_data_state.default_model = new_default
                self.chat_data_state.current_state.model_options = new_options
                self.chat_data_state.current_state.default_model = new_default
                
                # 更新UI组件
                if self.chat_data_state.current_state.model_select_widget:
                    current_selection = self.chat_data_state.current_state.selected_model
                    if current_selection not in new_options:
                        current_selection = new_default
                    
                    self.chat_data_state.current_state.model_select_widget.set_options(new_options)
                    self.chat_data_state.current_state.model_select_widget.set_value(current_selection)
                    self.chat_data_state.current_state.selected_model = current_selection
                    
                    # 同步更新 current_model_config
                    self.chat_data_state.current_model_config['selected_model'] = current_selection
                    self.chat_data_state.current_model_config['config'] = get_model_config(current_selection)
                
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
    
    def on_prompt_change(self, e):
        """提示词选择变化事件处理"""
        selected_prompt_key = e.value
        
        # 获取系统提示词内容和示例
        system_prompt = get_system_prompt(selected_prompt_key)
        examples = get_examples(selected_prompt_key)
        
        # 更新当前提示词配置
        self.chat_data_state.current_prompt_config.selected_prompt = selected_prompt_key
        self.chat_data_state.current_prompt_config.system_prompt = system_prompt or ''
        self.chat_data_state.current_prompt_config.examples = examples or {}
        
        # 显示选择信息
        ui.notify(f'已切换到提示词: {selected_prompt_key}')
    
    def on_refresh_prompt_config(self):
        """刷新提示词配置"""
        try:
            ui.notify('正在刷新提示词配置...', type='info')
            success = reload_prompt_config()
            
            if success:
                # 重新获取配置
                prompt_options = get_prompt_options_for_select()
                new_default = get_default_prompt() or (prompt_options[0] if prompt_options else None)
                
                # 更新数据状态
                self.chat_data_state.prompt_options = prompt_options
                self.chat_data_state.default_prompt = new_default
                
                # 更新UI组件
                if self.chat_data_state.current_state.prompt_select_widget:
                    current_selection = self.chat_data_state.current_prompt_config.selected_prompt
                    if current_selection not in prompt_options:
                        current_selection = new_default
                    
                    self.chat_data_state.current_state.prompt_select_widget.set_options(prompt_options)
                    self.chat_data_state.current_state.prompt_select_widget.set_value(current_selection)
                    
                    self.chat_data_state.current_prompt_config.selected_prompt = current_selection
                    self.chat_data_state.current_prompt_config.system_prompt = (
                        get_system_prompt(current_selection) if current_selection else ''
                    )
                    self.chat_data_state.current_prompt_config.examples = (
                        get_examples(current_selection) if current_selection else {}
                    )
                
                ui.notify(f'提示词配置刷新成功，共加载 {len(prompt_options)} 个模板', type='positive')
            else:
                ui.notify('提示词配置刷新失败', type='negative')
                
        except Exception as e:
            ui.notify(f'刷新提示词配置时发生错误: {str(e)}', type='negative')
    #endregion 模型选择相关逻辑
    
    #region 新建会话相关逻辑
    async def on_create_new_chat(self):
        """新建聊天会话"""
        try:
            # 🔥 新增：先判断是否已有聊天记录，执行插入或更新操作
            if self.chat_data_state.current_chat_messages:
                # 检查当前是否为加载的历史对话（通过检查 current_chat_messages 是否与某个历史记录匹配）
                existing_chat_id = self.get_current_loaded_chat_id()
                
                if existing_chat_id:
                    # 更新现有聊天记录
                    update_success = self.update_existing_chat_to_database(existing_chat_id)
                    if update_success:
                        ui.notify('对话已更新', type='positive')
                    else:
                        ui.notify('更新对话失败', type='negative')
                        return
                else:
                    # 插入新的聊天记录
                    save_success = self.save_chat_to_database()
                    if save_success:
                        ui.notify('对话已保存', type='positive')
                    else:
                        ui.notify('保存对话失败', type='negative')
                        return
                
                # 清空当前聊天记录
                self.chat_data_state.current_chat_messages.clear()
                # 恢复欢迎消息
                self.chat_area_manager.restore_welcome_message()
                # 新增：自动刷新聊天历史列表
                self.refresh_chat_history_list()
                # 重置当前加载的聊天ID
                self.reset_current_loaded_chat_id()     
            else:
                self.chat_area_manager.restore_welcome_message()
                ui.notify('界面已重置', type='info')
                
        except Exception as e:
            ui.notify(f'创建新对话失败: {str(e)}', type='negative')
    
    def get_current_loaded_chat_id(self):
        """获取当前加载的聊天记录ID"""
        return self.chat_data_state.current_chat_id

    def set_current_loaded_chat_id(self, chat_id):
        """设置当前加载的聊天记录ID"""
        self.chat_data_state.current_chat_id = chat_id

    def reset_current_loaded_chat_id(self):
        """重置当前加载的聊天记录ID"""
        self.chat_data_state.current_chat_id = None

    def update_existing_chat_to_database(self, chat_id):
        """更新现有的聊天记录到数据库"""
        if chat_id is None:
            return True
        try:
            from auth import auth_manager
            from database_models.business_models.chat_history_model import ChatHistory
            from auth.database import get_db
            
            current_user = auth_manager.current_user
            if not current_user:
                ui.notify('用户未登录，无法更新聊天记录', type='warning')
                return False
            
            if not self.chat_data_state.current_chat_messages:
                ui.notify('没有聊天记录需要更新', type='info')
                return False
            
            with get_db() as db:
                chat_history = db.query(ChatHistory).filter(
                    ChatHistory.id == chat_id,
                    ChatHistory.created_by == current_user.id,
                    ChatHistory.is_deleted == False
                ).first()
                
                if not chat_history:
                    ui.notify('聊天记录不存在或无权限', type='negative')
                    return False
                
                # 更新聊天记录
                chat_history.messages = self.chat_data_state.current_chat_messages.copy()
                chat_history.model_name = self.chat_data_state.current_state.selected_model
                
                # 使用模型的内置方法更新统计信息
                chat_history.update_message_stats()
                chat_history.updated_at = datetime.now()
                
                db.commit()
                return True
                
        except Exception as e:
            ui.notify(f'更新聊天记录失败: {str(e)}', type='negative')
            return False

    def save_chat_to_database(self):
        """保存新的聊天记录到数据库"""
        try:
            from auth import auth_manager
            from database_models.business_models.chat_history_model import ChatHistory
            from database_models.business_utils import AuditHelper
            from auth.database import get_db
            
            current_user = auth_manager.current_user
            if not current_user:
                ui.notify('用户未登录，无法保存聊天记录', type='warning')
                return False
            
            if not self.chat_data_state.current_chat_messages:
                ui.notify('没有聊天记录需要保存', type='info')
                return False
            
            # 生成聊天标题（使用第一条用户消息的前20个字符）
            title = "新对话"
            for msg in self.chat_data_state.current_chat_messages:
                if msg.get('role') == 'user':
                    content = msg.get('content', '')
                    title = content[:20] + ('...' if len(content) > 20 else '')
                    break
            
            # 处理think内容：检测是否有think内容，有则移除
            messages_to_save = self.chat_data_state.current_chat_messages.copy()
            if self.chat_area_manager.has_think_content(messages_to_save):
                messages_to_save = self.chat_area_manager.remove_think_content(messages_to_save)
            
            with get_db() as db:
                chat_history = ChatHistory(
                    title=title,
                    model_name=self.chat_data_state.current_state.selected_model,
                    prompt_name = self.chat_data_state.current_prompt_config.selected_prompt,
                    messages=messages_to_save
                )
                
                # 使用模型的内置方法更新统计信息
                chat_history.update_message_stats()
                
                # 设置审计字段
                AuditHelper.set_audit_fields(chat_history, current_user.id)
                
                db.add(chat_history)
                db.commit()
                
                return True
                
        except Exception as e:
            ui.notify(f'保存聊天记录失败: {str(e)}', type='negative')
            return False
    #endregion 新建会话相关逻辑
    
    #region 历史记录相关逻辑
    def load_chat_histories(self):
        """从数据库加载聊天历史列表"""
        try:
            from auth import auth_manager
            from database_models.business_models.chat_history_model import ChatHistory
            from auth.database import get_db
            
            current_user = auth_manager.current_user
            if not current_user:
                return []
            
            with get_db() as db:
                chat_histories = ChatHistory.get_user_recent_chats(
                    db_session=db, 
                    user_id=current_user.id, 
                    limit=20
                )
                
                # 转换为UI需要的数据结构
                history_list = []
                for chat in chat_histories:
                    preview = chat.get_message_preview(30)
                    duration_info = chat.get_duration_info()
                    
                    history_list.append({
                        'id': chat.id,
                        'title': chat.title,
                        'preview': preview,
                        'created_at': chat.created_at.strftime('%Y-%m-%d %H:%M'),
                        'updated_at': chat.updated_at.strftime('%Y-%m-%d %H:%M'),
                        'last_message_at': chat.last_message_at.strftime('%Y-%m-%d %H:%M') if chat.last_message_at else None,
                        'message_count': chat.message_count,
                        'model_name': chat.model_name,
                        'duration_minutes': duration_info['duration_minutes'],
                        'chat_object': chat
                    })
                return history_list        
        except Exception as e:
            ui.notify('加载聊天历史失败', type='negative')
            return []
        
    async def on_load_chat_history(self, chat_id):
        """加载指定的聊天历史到当前对话中"""
        # 设置当前加载的聊天ID，用于后续更新判断
        self.set_current_loaded_chat_id(chat_id)
        # 调用聊天区域管理器渲染聊天历史
        await self.chat_area_manager.render_chat_history(chat_id)
    
    def on_edit_chat_history(self, chat_id):
        """编辑聊天历史记录"""
        def save_title():
            try:
                from auth import auth_manager
                from database_models.business_models.chat_history_model import ChatHistory
                from auth.database import get_db
                
                current_user = auth_manager.current_user
                if not current_user:
                    ui.notify('用户未登录', type='warning')
                    return
                
                new_title = title_input.value.strip()
                if not new_title:
                    ui.notify('标题不能为空', type='warning')
                    return
                
                with get_db() as db:
                    chat_history = db.query(ChatHistory).filter(
                        ChatHistory.id == chat_id,
                        ChatHistory.created_by == current_user.id,
                        ChatHistory.is_deleted == False
                    ).first()
                    
                    if chat_history:
                        chat_history.title = new_title
                        chat_history.updated_at = datetime.now()
                        db.commit()
                        
                        # 刷新历史记录列表
                        self.refresh_chat_history_list()
                        ui.notify('标题修改成功', type='positive')
                        dialog.close()
                    else:
                        ui.notify('聊天记录不存在', type='negative')
                        
            except Exception as e:
                ui.notify(f'修改失败: {str(e)}', type='negative')
        
        # 获取当前标题
        try:
            from auth import auth_manager
            from database_models.business_models.chat_history_model import ChatHistory
            from auth.database import get_db
            
            current_user = auth_manager.current_user
            if not current_user:
                ui.notify('用户未登录', type='warning')
                return
            
            with get_db() as db:
                chat_history = db.query(ChatHistory).filter(
                    ChatHistory.id == chat_id,
                    ChatHistory.created_by == current_user.id,
                    ChatHistory.is_deleted == False
                ).first()
                
                if not chat_history:
                    ui.notify('聊天记录不存在', type='negative')
                    return
                
                current_title = chat_history.title
        except Exception as e:
            ui.notify('获取聊天记录失败', type='negative')
            return
        
        # 显示编辑对话框
        with ui.dialog() as dialog:
            with ui.card().classes('w-96'):
                with ui.column().classes('w-full gap-4'):
                    ui.label('编辑聊天标题').classes('text-lg font-medium')
                    title_input = ui.input('聊天标题', value=current_title).classes('w-full')
                    
                    with ui.row().classes('w-full justify-end gap-2'):
                        ui.button('取消', on_click=dialog.close).props('flat')
                        ui.button('保存', on_click=save_title).props('color=primary')
        
        dialog.open()
    
    def on_delete_chat_history(self, chat_id):
        """删除聊天历史记录"""
        def confirm_delete():
            try:
                from auth import auth_manager
                from database_models.business_models.chat_history_model import ChatHistory
                from auth.database import get_db
                
                current_user = auth_manager.current_user
                if not current_user:
                    ui.notify('用户未登录，无法删除聊天记录', type='warning')
                    return
                
                with get_db() as db:
                    chat_history = db.query(ChatHistory).filter(
                        ChatHistory.id == chat_id,
                        ChatHistory.created_by == current_user.id,
                        ChatHistory.is_deleted == False
                    ).first()
                    
                    if not chat_history:
                        ui.notify('聊天记录不存在或无权限删除', type='negative')
                        return
                    
                    chat_title = chat_history.title
                    
                    # 软删除操作
                    chat_history.is_deleted = True
                    chat_history.deleted_at = datetime.now()
                    chat_history.deleted_by = current_user.id
                    chat_history.is_active = False
                    
                    db.commit()
                    
                    # 如果删除的是当前加载的聊天，需要重置界面
                    current_loaded_id = self.get_current_loaded_chat_id()
                    if current_loaded_id == chat_id:
                        self.chat_data_state.current_chat_messages.clear()
                        self.chat_area_manager.restore_welcome_message()
                        self.reset_current_loaded_chat_id()
                        
                    # 刷新聊天历史列表
                    self.refresh_chat_history_list()
                    
                    ui.notify(f'已删除聊天: {chat_title}', type='positive')
                    
            except Exception as e:
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
    
    def create_chat_history_list(self):
        """创建聊天历史列表组件"""
        chat_histories = self.load_chat_histories()
        
        if not chat_histories:
            with ui.column().classes('w-full text-center'):
                ui.icon('chat_bubble_outline', size='lg').classes('text-gray-400 mb-2')
                ui.label('暂无聊天记录').classes('text-gray-500 text-sm')
            return
        
        with ui.list().classes('w-full').props('dense separator'):
            for history in chat_histories:
                with ui.item(on_click=lambda chat_id=history['id']: self.on_load_chat_history(chat_id)).classes('cursor-pointer'):
                    with ui.item_section():
                        ui.item_label(history['title']).classes('font-medium')
                        info_text = f"{history['updated_at']} • {history['message_count']}条消息"
                        if history['duration_minutes'] > 0:
                            info_text += f" • {history['duration_minutes']}分钟"
                        if history['model_name']:
                            info_text += f" • {history['model_name']}"
                        ui.item_label(info_text).props('caption').classes('text-xs')
                    
                    with ui.item_section().props('side'):
                        with ui.row().classes('gap-1'):
                            ui.button(
                                icon='edit'
                            ).on('click.stop', lambda chat_id=history['id']: self.on_edit_chat_history(chat_id)).props('dense flat round size="sm"').classes('text-blue-600').tooltip('编辑')
                            
                            ui.button(
                                icon='delete'
                            ).on('click.stop', lambda chat_id=history['id']: self.on_delete_chat_history(chat_id)).props('dense flat round size="sm"').classes('text-red-600').tooltip('删除')
        
    def refresh_chat_history_list(self):
        """刷新聊天历史列表"""
        try:
            if self.history_list_container:
                self.history_list_container.clear()
                with self.history_list_container:
                    self.create_chat_history_list()
                ui.notify('聊天历史已刷新', type='positive')
        except Exception as e:
            ui.notify('刷新失败', type='negative')
    #endregion 历史记录相关逻辑
    
    def render_ui(self):
        """渲染侧边栏UI"""
        visibility_style = 'display: none;' if not self.sidebar_visible else ''
        with ui.column().classes('chat-archive-sidebar h-full').style(
            f'width: 280px; min-width: 280px; {visibility_style}'
        ):
            # 侧边栏标题
            with ui.row().classes('w-full'):
                ui.icon('menu', size='md').classes('text-gray-600')
                ui.label('功能菜单').classes('text-lg font-semibold')
            
            # 侧边栏内容
            with ui.column().classes('w-full items-center'):
                # 新建对话按钮
                ui.button(
                    '新建对话', 
                    icon='add', 
                    on_click=self.on_create_new_chat
                ).classes('w-64').props('outlined rounded').tooltip('创建新聊天/保存当前聊天')
                        
                # 选择模型expansion组件
                with ui.expansion('选择模型', icon='view_in_ar').classes('w-full').tooltip('选择大语言模型'):
                    with ui.column().classes('w-full'):
                        # 配置管理按钮行
                        with ui.row().classes('w-full'):
                            ui.button(
                                '刷新配置', 
                                icon='refresh',
                                on_click=self.on_refresh_model_config
                            ).classes('text-xs').props('dense flat color="primary"').style('min-width: 80px;')
                        
                        # 模型选择下拉框
                        self.chat_data_state.current_state.model_select_widget = ui.select(
                            options=self.chat_data_state.current_state.model_options,
                            value=self.chat_data_state.current_state.default_model,
                            with_input=True,
                            on_change=self.on_model_change
                        ).classes('w-full').props('autofocus dense')

                # 上下文模板expansion组件
                with ui.expansion('上下文模板', icon='pattern').classes('w-full').tooltip('选择上下文模型'):
                    with ui.column().classes('w-full'):
                        # 配置管理按钮行
                        with ui.row().classes('w-full'):
                            ui.button(
                                '刷新配置', 
                                icon='refresh',
                                on_click=self.on_refresh_prompt_config
                            ).classes('text-xs').props('dense flat color="primary"').style('min-width: 80px;')
                        
                        # 提示词选择下拉框
                        self.chat_data_state.current_state.prompt_select_widget = ui.select(
                            options=self.chat_data_state.prompt_options, 
                            value=self.chat_data_state.default_prompt, 
                            with_input=True,
                            on_change=self.on_prompt_change
                        ).classes('w-full').props('autofocus dense')

                # 🔥 修改: 根据data_input_mode渲染不同的输入组件
                with ui.expansion('提示数据', icon='tips_and_updates').classes('w-full').tooltip('选择提示数据'):
                    with ui.column().classes('w-full chathistorylist-hide-scrollbar').style('flex-grow: 1;'):
                        self.switch = ui.switch('启用', value=False).bind_value(self.chat_data_state, 'switch')
                        
                        # 根据模式渲染不同组件
                        if self.data_input_mode == 'selector':
                            self._render_hierarchy_selector()
                        elif self.data_input_mode == 'textarea':
                            self._render_textarea_input()
                    
                # 聊天历史expansion组件
                with ui.expansion('历史消息', icon='history').classes('w-full').tooltip('操作历史聊天内容'):
                    with ui.column().classes('w-full'):
                        # 添加刷新按钮
                        with ui.row().classes('w-full'):
                            ui.button(
                                '刷新历史', 
                                icon='refresh',
                                on_click=self.refresh_chat_history_list
                            ).classes('text-xs').props('dense flat color="primary"').style('min-width: 80px;')
                        
                        # 聊天历史列表容器
                        self.history_list_container = ui.column().classes('w-full h-96 chathistorylist-hide-scrollbar')
                        with self.history_list_container:
                            self.create_chat_history_list()
    
    def _render_hierarchy_selector(self):
        """渲染层级选择器(原有逻辑)"""
        from menu_pages.enterprise_archive.hierarchy_selector_component import HierarchySelector
        self.hierarchy_selector = HierarchySelector(multiple=True)
        self.hierarchy_selector.render_column()
        self.chat_data_state.selected_values = self.hierarchy_selector.selected_values
    
    def _render_textarea_input(self):
        """🔥 新增: 渲染textarea输入框"""
        self.data_input_textarea = ui.textarea(
            placeholder='请输入数据查询条件(JSON格式)\n示例:\n{\n  "l1":"分类1",\n  "l2":"分类2",\n  "l3":"分类3",\n  "field":["字段1","字段2"]\n}',
            value=''
        ).classes('w-full').props('outlined dense').style('min-height: 150px;')
        
        # 添加解析按钮
        ui.button(
            '解析并应用', 
            icon='check_circle',
            on_click=self._parse_textarea_data
        ).classes('w-full mt-2').props('outlined')
    
    def _parse_textarea_data(self):
        """🔥 新增: 解析textarea中的JSON数据"""
        import json
        
        try:
            if not self.data_input_textarea or not self.data_input_textarea.value:
                ui.notify('请输入数据', type='warning')
                return
            
            # 解析JSON
            raw_data = json.loads(self.data_input_textarea.value)
            
            # 验证必填字段
            if 'l3' not in raw_data or not raw_data['l3']:
                ui.notify('至少需要包含l3级别的数据', type='warning')
                return
            
            # 更新selected_values
            self.chat_data_state.selected_values['l1'] = raw_data.get('l1')
            self.chat_data_state.selected_values['l2'] = raw_data.get('l2')
            self.chat_data_state.selected_values['l3'] = raw_data.get('l3')
            self.chat_data_state.selected_values['field'] = raw_data.get('field')
            self.chat_data_state.selected_values['field_name'] = raw_data.get('field_name')
            
            # 可选: 设置其他字段
            self.chat_data_state.selected_values['data_url'] = raw_data.get('data_url')
            self.chat_data_state.selected_values['full_path_code'] = raw_data.get('full_path_code')
            self.chat_data_state.selected_values['full_path_name'] = raw_data.get('full_path_name')
            
            ui.notify('数据解析成功', type='positive')
            
        except json.JSONDecodeError as e:
            ui.notify(f'JSON格式错误: {str(e)}', type='negative')
        except Exception as e:
            ui.notify(f'数据解析失败: {str(e)}', type='negative')
    
    # ... [保持原有的其他所有方法不变] ...