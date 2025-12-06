"""
企业档案页面入口
直接使用 component/chat 可复用聊天组件
"""
from common.exception_handler import safe_protect
from component.chat import ChatComponent


@safe_protect(name="一企一档", error_msg="一企一档页面加载失败")
def enterprise_archive_content():
    """
    企业档案页面内容 - 使用可复用的聊天组件
    
    提供两种数据输入模式:
    1. selector模式(默认): 使用层级选择器逐级选择数据
    2. textarea模式: 直接输入JSON格式的数据
    """
    # 🔥 使用新的ChatComponent组件
    # 方式1: 使用默认配置(selector模式 - 保持原有功能)
    chat = ChatComponent(
        sidebar_visible=True,           # 显示侧边栏
        default_model=None,              # 使用配置文件中的默认模型
        default_prompt=None,             # 使用配置文件中的默认提示词
        data_input_mode='selector',      # 使用层级选择器(原有方式)
        is_record_history=True           # 记录聊天历史
    )
    chat.render()
    
    # 🔥 方式2: 如果想使用textarea模式，取消下面的注释，注释掉上面的代码
    # chat = ChatComponent(
    #     sidebar_visible=True,
    #     default_model='deepseek-chat',   # 可以指定默认模型
    #     default_prompt='一企一档专家',    # 可以指定默认提示词
    #     data_input_mode='textarea',       # 使用textarea输入JSON数据
    #     is_record_history=True
    # )
    # chat.render()


# 导出主要功能，保持原有接口不变
__all__ = ['enterprise_archive_content']