from nicegui import ui
from common.log_handler import (
    # 日志记录函数
    log_trace, log_debug, log_info, log_success, log_warning, log_error, log_critical,
    # 安全执行
    safe, db_safe,
    # 装饰器
    safe_protect, catch,
    # Logger 实例
    get_logger
)

@safe_protect(name="首页内容", error_msg="首页内容发生错误", return_on_error=None)
def home_content():
    """首页内容"""
    ui.label('欢迎回到首页!').classes('text-3xl font-bold text-green-800 dark:text-green-200')
    ui.label('这是您个性化的仪表板。').classes('text-gray-600 dark:text-gray-400 mt-4')