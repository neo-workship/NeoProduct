
ChatSidebarManager:
    ChatAreaManger chat_area_manager     # uses-a，调用使用一些功能
    
    #region 模型选择相关处理逻辑
    def on_model_change(e)
    def on_refresh_model_config()
    def on_prompt_change(e)
    def on_refresh_prompt_config()
    # endregion 模型选择相关逻辑
    
    #region 新建会话相关逻辑
    async def on_create_new_chat()       # 要调用 chat_area_manager.restore_welcome_message
    def get_current_loaded_chat_id()
    def set_current_loaded_chat_id(chat_id)
    def reset_current_loaded_chat_id()
    def update_existing_chat_to_database(chat_id)
    def save_chat_to_database()
    #endregion 新建会话相关逻辑

    #region 历史记录相关逻辑
    def load_chat_histories()
    def on_load_chat_history(chat_id)    # 要调用 chat_area_manager.render_chat_history
    def on_edit_chat_history(chat_id)
    def on_delete_chat_history(chat_id)  # 要调用 chat_area_manager.restore_welcome_message
    def create_chat_history_list()
    def refresh_chat_history_list()
    #endregion 历史记录相关逻辑

ChatAreaManger:
    #region 解析markdown并映射为ui组件展示相关逻辑 
    async def optimize_content_display(reply_label, content: str, chat_content_container=None)
    def parse_content_with_regex(content: str) -> List[Dict[str, Any]]
    def extract_tables(content: str) -> List[Dict[str, Any]]
    def extract_mermaid(content: str) -> List[Dict[str, Any]]
    def extract_code_blocks(content: str) -> List[Dict[str, Any]]
    def extract_math(content: str) -> List[Dict[str, Any]]
    def extract_headings(content: str) -> List[Dict[str, Any]]
    def fill_text_blocks(content: str, special_blocks: List[Dict[str, Any]]) -> List[Dict[str, Any]]
    def parse_table_data(table_text: str) -> Optional[Dict[str, Any]]
    def has_special_content(blocks: List[Dict[str, Any]]) -> bool
    def show_optimization_hint(reply_label)
    async def render_optimized_content(container, blocks: List[Dict[str, Any]])
    def create_table_component(table_data: Dict[str, Any])
    def create_mermaid_component(mermaid_content: str)
    def create_code_component(code_content: str, language: str)
    def create_math_component(math_content: str, display_mode: str)
    def create_heading_component(text: str, level: int)
    def create_text_component(text_content: str)
    #endregion  解析markdown并映射为ui组件展示相关逻辑

    #region 用户输入提交相关处理逻辑
    async def scroll_to_bottom_smooth()
    def enhance_user_message(user_message: str, current_chat_messages: list, switch, current_state: dict, hierarchy_selector) -> str
    async def handle_message(event=None)
    def has_think_content(messages)
    def remove_think_content(messages)
    def handle_keydown(e)
    #endregion 用户输入提交相关处理逻辑

    # 是
    def restore_welcome_message()
    def render_chat_history(chat_id)
