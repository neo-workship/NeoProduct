"""
导航工具模块
"""
from nicegui import ui

def navigate_to(path: str):
    """导航到指定路径"""
    ui.navigate.to(path)

def redirect_to_login():
    """重定向到登录页"""
    from .config import auth_config
    ui.navigate.to(auth_config.login_route)

def redirect_to_home():
    """重定向到首页"""
    ui.navigate.to('/workbench')