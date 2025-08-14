from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Union

@dataclass
class SelectedValues:
    """层级选择器选中值数据结构"""
    l1: Optional[str] = None
    l2: Optional[str] = None
    l3: Optional[str] = None
    field: Union[List[str], str, None] = None  # 多选时为列表，单选时为单值
    # 优化字段
    data_url: Optional[str] = None        # 如果field不为None，对应的值为field的data_url
    full_path_code: Optional[str] = None  # 完整路径编码
    full_path_name: Optional[str] = None  # 完整路径名称

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
    # 模型相关
    model_options: List[str] = field(default_factory=list)  # 返回 ['deepseek-chat', 'moonshot-v1-8k', 'qwen-plus', ...]
    default_model: str = 'deepseek-chat'
    current_model_config: Dict[str, Any] = field(default_factory=dict)  # {'selected_model': default_model, 'config': None}
    
    # 当前状态
    current_state: CurrentState = field(default_factory=CurrentState)
    
    # 记录当前聊天中的消息
    current_chat_messages: List[Dict] = field(default_factory=list)
    
    # 提示词初始化
    prompt_options: List[str] = field(default_factory=list)
    default_prompt: Optional[str] = None
    current_prompt_config: CurrentPromptConfig = field(default_factory=CurrentPromptConfig)
    
    # 层级选择器选中值
    switch: bool = False
    selected_values: SelectedValues = field(default_factory=SelectedValues)