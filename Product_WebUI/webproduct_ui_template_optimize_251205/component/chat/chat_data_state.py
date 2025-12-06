"""
聊天数据状态管理
定义聊天组件使用的所有数据结构
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Union

@dataclass
class SelectedValues:
    """数据输入值数据结构 - 通过 textarea JSON 输入"""
    # 层级数据
    # l1: Optional[str] = None
    # l2: Optional[str] = None
    # l3: Optional[str] = None
    # field: Union[List[str], str, None] = None
    # field_name: Union[List[str], str, None] = None
    
    # # 扩展字段
    # data_url: Optional[str] = None
    # full_path_code: Optional[str] = None
    # full_path_name: Optional[str] = None
    
    # textarea 输入相关
    raw_input: Optional[str] = None  # textarea原始输入内容

@dataclass
class CurrentState:
    """当前状态数据结构"""
    model_options: List[str] = field(default_factory=list)
    default_model: str = 'deepseek-chat'
    selected_model: str = 'deepseek-chat'
    model_select_widget: Optional[Any] = None
    prompt_select_widget: Optional[Any] = None

@dataclass
class CurrentPromptConfig:
    """当前提示词配置数据结构"""
    selected_prompt: Optional[str] = None
    system_prompt: str = ''
    examples: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ChatDataState:
    """聊天数据状态主类"""
    # 模型相关
    model_options: List[str] = field(default_factory=list)
    default_model: str = 'deepseek-chat'
    current_model_config: Dict[str, Any] = field(default_factory=dict)
    
    # 当前状态
    current_state: CurrentState = field(default_factory=CurrentState)
    
    # 记录当前聊天中的消息
    current_chat_messages: List[Dict] = field(default_factory=list)
    
    # 提示词初始化
    prompt_options: List[str] = field(default_factory=list)
    default_prompt: Optional[str] = None
    current_prompt_config: CurrentPromptConfig = field(default_factory=CurrentPromptConfig)
    
    # 数据输入开关和值
    switch: bool = False
    selected_values: SelectedValues = field(default_factory=SelectedValues)

    # 当前聊天id
    current_chat_id: Optional[int] = None