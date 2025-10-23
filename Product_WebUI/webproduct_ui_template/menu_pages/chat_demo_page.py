"""
企业档案页面入口
使用 component/chat 可复用聊天组件（自由文本输入）
"""
from common.exception_handler import safe_protect
from component.chat import ChatComponent

@safe_protect(name="一企一档", error_msg="一企一档页面加载失败")
def chat_page_content():
    """
    企业档案页面内容
    功能说明:
    1. 在侧边栏的"提示数据"中可以输入任意格式的提示文本
    2. 开启"启用"开关后，输入的提示数据会自动附加到对话中
    3. 无需特定格式，支持自由文本输入
    """
    chat = ChatComponent(
        sidebar_visible=True,
        default_model=None,
        default_prompt=None,
        is_record_history=True
    )
    chat.render()


# 导出主要功能，保持原有接口不变
__all__ = ['chat_page_content']