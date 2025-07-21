# menu_pages/enterprise_archive_page.py 
from auth import auth_manager
from auth.decorators import require_permission
from nicegui import ui
from database_models.business_models.openai_detached_helper import get_openai_configs_safe
# 导入异常处理模块
from common.exception_handler import log_info, log_error, safe, db_safe, safe_protect

@safe_protect(name="一企一档", error_msg="一企一档页面加载失败")
def enterprise_archive_content():
    user = auth_manager.current_user
    
    ui.label(f'欢迎，{user.username}！')
    
    # 根据具体权限显示不同功能
    if user.has_permission('openai.view'):
        show_openai_configs()
    
    if user.has_permission('openai.create'):
        ui.button('新建配置', on_click=safe(create_config_dialog))
    
    if user.has_permission('openai.use'):
        ui.button('开始对话', on_click=safe(start_chat))

def show_openai_configs():
    """显示OpenAI配置列表"""
    user = auth_manager.current_user
    configs = lambda:get_openai_configs_safe()
    
    if configs:
        for config in configs:
            with ui.card():
                ui.label(config.name)
                
                # 编辑按钮（需要编辑权限）
                if user.has_permission('openai.edit'):
                    ui.button('编辑', on_click=lambda c=config: edit_config(c.id))
                
                # 删除按钮（需要删除权限）
                if user.has_permission('openai.delete'):
                    ui.button('删除', on_click=lambda c=config: delete_config(c.id))
                
                # API密钥管理（需要特殊权限）
                if user.has_permission('openai.manage_api_key'):
                    ui.button('管理密钥', on_click=lambda c=config: manage_api_key(c.id))

def create_config_dialog():
    """创建配置对话框"""
    # 创建配置的逻辑
    pass

def delete_config(config_id: int):
    pass

def manage_api_key(config_id:int):
    pass

def edit_config(config_id: int):
    """编辑配置"""
    # 编辑配置的逻辑
    pass

def start_chat():
    """开始对话"""
    # 对话逻辑
    pass