"""
聊天组件包 - 可复用的聊天UI组件
从 menu_pages/enterprise_archive/chat_component 迁移而来

提供完整的聊天功能,包括:
- 聊天数据状态管理
- 聊天区域UI管理
- 侧边栏UI管理
- LLM模型配置
- Markdown内容解析
"""

from .chat_data_state import ChatDataState, SelectedValues, CurrentState, CurrentPromptConfig
from .chat_area_manager import ChatAreaManager
from .chat_sidebar_manager import ChatSidebarManager
from .chat_component import ChatComponent
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
    reload_prompt_config,
    get_prompt_config_info
)
from .markdown_ui_parser import MarkdownUIParser

__all__ = [
    # 数据状态
    'ChatDataState',
    'SelectedValues',
    'CurrentState',
    'CurrentPromptConfig',
    
    # 管理器
    'ChatAreaManager',
    'ChatSidebarManager',
    
    # 主组件
    'ChatComponent',
    
    # 配置函数
    'get_model_options_for_select',
    'get_model_config',
    'get_default_model',
    'reload_llm_config',
    'get_model_config_info',
    'get_prompt_options_for_select',
    'get_system_prompt',
    'get_examples',
    'get_default_prompt',
    'reload_prompt_config',
    'get_prompt_config_info',
    
    # 工具类
    'MarkdownUIParser',
]