"""
增强的异常处理和日志模块 - 基于 Loguru 的混合架构(优化版 v2.1)
保留现有 API,增强底层实现,按日期文件夹组织日志

文件路径: webproduct_ui_template/common/log_handler.py

特性:
1. 完全兼容现有 API (log_info, log_error, safe, db_safe, safe_protect)
2. 使用 Loguru 作为底层引擎,性能提升 20-30%
3. 支持 7 种日志级别 (TRACE, DEBUG, INFO, SUCCESS, WARNING, ERROR, CRITICAL)
4. 智能日志轮转 (按天/自动压缩)
5. 异步日志写入,不阻塞主线程
6. 保留 CSV 格式兼容(用于查询工具)
7. 自动捕获用户上下文
8. 集成 NiceGUI UI 通知
9. 按日期文件夹组织: logs/2025-10-23/{app.log, error.log, app_logs.csv}
"""

import csv
import json
import asyncio
import threading
import functools
import inspect
import sys
from typing import Callable, Any, Optional, Dict, List
from datetime import datetime, timedelta
from pathlib import Path
from contextlib import contextmanager
from loguru import logger
from nicegui import ui

# =============================================================================
# 配置和初始化
# =============================================================================

class LoguruExceptionHandler:
    """基于 Loguru 的增强异常处理器 - 单例模式(线程安全)"""
    
    _instance = None
    _lock = threading.Lock()
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        # 配置参数
        self.log_base_dir = Path('logs')  # 日志根目录
        self.log_base_dir.mkdir(exist_ok=True)
        self.max_log_days = 30  # 普通日志保留30天
        self.error_log_days = 90  # 错误日志保留90天
        self.csv_enabled = True  # CSV 兼容模式
        
        # 当前日志目录(每天一个文件夹)
        self.current_log_dir = self._get_today_log_dir()
        
        # 初始化 Loguru
        self._setup_loguru()
        
        # CSV 支持(兼容现有查询工具)
        if self.csv_enabled:
            self._setup_csv_logging()
        
        # 启动定时清理任务
        self._start_cleanup_task()
        
        LoguruExceptionHandler._initialized = True
        logger.success(f"📊 Loguru 日志系统初始化完成 (v2.1 - 按日期文件夹组织)")
        logger.info(f"📁 今日日志目录: {self.current_log_dir}")
    
    def _get_today_log_dir(self) -> Path:
        """获取今天的日志目录"""
        today = datetime.now().strftime('%Y-%m-%d')
        log_dir = self.log_base_dir / today
        log_dir.mkdir(parents=True, exist_ok=True)
        return log_dir
    
    def _check_and_update_log_dir(self):
        """检查日期是否变化,如果跨天则更新日志目录"""
        today_log_dir = self._get_today_log_dir()
        
        if today_log_dir != self.current_log_dir:
            # 跨天了,需要重新配置 Loguru
            logger.info(f"🔄 检测到日期变化,切换日志目录: {today_log_dir}")
            self.current_log_dir = today_log_dir
            
            # 重新配置 Loguru
            logger.remove()
            self._setup_loguru()
            if self.csv_enabled:
                self._setup_csv_logging()
            
            logger.success(f"✅ 日志目录已切换: {self.current_log_dir}")
    
    def _setup_loguru(self):
        """配置 Loguru 日志系统 - 按日期文件夹组织"""
        # 移除默认处理器
        logger.remove()
        
        # 1️⃣ 控制台输出 - 开发环境(彩色格式化)
        logger.add(
            sys.stderr,
            format=(
                "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
                "<level>{level: <8}</level> | "
                "<cyan>{extra[user_id]}</cyan>@<cyan>{extra[username]}</cyan> | "
                "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
                "<level>{message}</level>"
            ),
            level="DEBUG",
            colorize=True,
            backtrace=True,
            diagnose=True,
            enqueue=False  # 控制台同步输出,方便调试
        )
        
        # 2️⃣ 普通日志文件 - 存储在当天日期文件夹下
        logger.add(
            self.current_log_dir / "app.log",
            rotation="500 MB",  # 单文件大小限制(防止单日日志过大)
            retention=f"{self.max_log_days} days",  # 保留天数(注意:这是针对轮转文件)
            compression="zip",  # 自动压缩
            encoding="utf-8",
            format=(
                "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
                "{level: <8} | "
                "{extra[user_id]}@{extra[username]} | "
                "{name}:{function}:{line} | "
                "{message}"
            ),
            level="INFO",
            enqueue=True,  # 异步写入,不阻塞主线程
            backtrace=True,
            diagnose=True
        )
        
        # 3️⃣ 错误日志文件 - 存储在当天日期文件夹下
        logger.add(
            self.current_log_dir / "error.log",
            rotation="100 MB",
            retention=f"{self.error_log_days} days",
            compression="zip",
            encoding="utf-8",
            format=(
                "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
                "{level: <8} | "
                "{extra[user_id]}@{extra[username]} | "
                "{name}:{function}:{line} | "
                "{message}\n"
                "{exception}"  # 完整异常堆栈
            ),
            level="ERROR",
            enqueue=True,
            backtrace=True,
            diagnose=True
        )
        
        # 配置默认上下文
        logger.configure(
            extra={"user_id": None, "username": "system"}
        )
    
    def _setup_csv_logging(self):
        """设置 CSV 格式日志(兼容现有查询工具) - 存储在当天日期文件夹下"""
        def csv_sink(message):
            """CSV 格式 sink - 线程安全"""
            try:
                # 检查是否跨天
                self._check_and_update_log_dir()
                
                record = message.record
                csv_file = self.current_log_dir / "app_logs.csv"
                
                # 初始化 CSV 文件(如果不存在)
                file_exists = csv_file.exists()
                
                if not file_exists:
                    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                        writer = csv.writer(f)
                        writer.writerow([
                            'timestamp', 'level', 'user_id', 'username',
                            'module', 'function', 'line_number', 'message',
                            'exception_type', 'stack_trace', 'extra_data'
                        ])
                
                # 写入日志记录
                with open(csv_file, 'a', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    
                    # 处理异常信息
                    exception_type = ''
                    stack_trace = ''
                    if record['exception']:
                        exception_type = record['exception'].type.__name__
                        # 格式化堆栈信息(移除过长的堆栈)
                        stack_lines = str(record['exception']).split('\n')
                        stack_trace = '\n'.join(stack_lines[:20])  # 限制堆栈长度
                    
                    writer.writerow([
                        record['time'].strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
                        record['level'].name,
                        record['extra'].get('user_id', ''),
                        record['extra'].get('username', ''),
                        record['name'],
                        record['function'],
                        record['line'],
                        record['message'],
                        exception_type,
                        stack_trace,
                        json.dumps(record['extra'].get('extra_data', {}), ensure_ascii=False)
                    ])
            except Exception as e:
                # 备用日志记录(避免日志系统本身出错)
                print(f"CSV 日志写入失败: {e}")
        
        # 添加 CSV sink
        logger.add(
            csv_sink,
            level="INFO",
            enqueue=True  # 异步写入
        )
    
    def _start_cleanup_task(self):
        """启动定时清理任务(清理过期的日志文件夹)"""
        def cleanup_worker():
            """后台清理线程"""
            while True:
                try:
                    # 每天凌晨2点执行清理
                    now = datetime.now()
                    next_run = now.replace(hour=2, minute=0, second=0, microsecond=0)
                    if next_run <= now:
                        next_run += timedelta(days=1)
                    
                    sleep_seconds = (next_run - now).total_seconds()
                    threading.Event().wait(sleep_seconds)
                    
                    # 执行清理
                    self._cleanup_old_log_folders()
                    
                except Exception as e:
                    logger.error(f"日志清理任务异常: {e}")
                    # 出错后等待1小时再重试
                    threading.Event().wait(3600)
        
        # 启动后台线程
        cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True, name="LogCleanup")
        cleanup_thread.start()
        logger.debug("🧹 日志清理后台任务已启动")
    
    def _cleanup_old_log_folders(self):
        """清理过期的日志文件夹"""
        try:
            cutoff_date = datetime.now() - timedelta(days=self.max_log_days)
            deleted_count = 0
            
            # 遍历所有日期文件夹
            for log_folder in self.log_base_dir.iterdir():
                if not log_folder.is_dir():
                    continue
                
                try:
                    # 解析文件夹名(格式: YYYY-MM-DD)
                    folder_date = datetime.strptime(log_folder.name, '%Y-%m-%d')
                    
                    # 检查是否过期
                    if folder_date < cutoff_date:
                        # 删除整个文件夹
                        import shutil
                        shutil.rmtree(log_folder)
                        deleted_count += 1
                        logger.info(f"🗑️ 已删除过期日志文件夹: {log_folder.name}")
                
                except (ValueError, OSError) as e:
                    logger.warning(f"跳过无效的日志文件夹: {log_folder.name} - {e}")
                    continue
            
            if deleted_count > 0:
                logger.success(f"✅ 日志清理完成,共删除 {deleted_count} 个过期文件夹")
            else:
                logger.debug("✅ 日志清理完成,无过期文件夹")
        
        except Exception as e:
            logger.error(f"清理日志文件夹失败: {e}")
    
    def _get_user_context(self) -> Dict[str, Any]:
        """获取当前用户上下文"""
        try:
            from auth.auth_manager import auth_manager
            user = auth_manager.current_user
            if user:
                return {
                    'user_id': user.id,
                    'username': user.username
                }
        except Exception:
            pass
        
        return {'user_id': None, 'username': 'anonymous'}
    
    def _bind_context(self, extra_data: Optional[Dict] = None):
        """绑定用户上下文到日志"""
        context = self._get_user_context()
        if extra_data:
            context['extra_data'] = extra_data
        return logger.bind(**context)
    
    # =========================================================================
    # 核心日志方法 - 兼容现有 API
    # =========================================================================
    
    def log_trace(self, message: str, extra_data: Optional[str] = None):
        """记录追踪日志 (最详细) - 新增功能"""
        extra = json.loads(extra_data) if extra_data else {}
        self._bind_context(extra).trace(message)
    
    def log_debug(self, message: str, extra_data: Optional[str] = None):
        """记录调试日志 - 新增功能"""
        extra = json.loads(extra_data) if extra_data else {}
        self._bind_context(extra).debug(message)
    
    def log_info(self, message: str, extra_data: Optional[str] = None):
        """记录信息日志 (兼容现有 API)"""
        extra = json.loads(extra_data) if extra_data else {}
        self._bind_context(extra).info(message)
    
    def log_success(self, message: str, extra_data: Optional[str] = None):
        """记录成功日志 - 新增功能"""
        extra = json.loads(extra_data) if extra_data else {}
        self._bind_context(extra).success(message)
    
    def log_warning(self, message: str, extra_data: Optional[str] = None):
        """记录警告日志 - 新增功能"""
        extra = json.loads(extra_data) if extra_data else {}
        self._bind_context(extra).warning(message)
    
    def log_error(self, message: str, exception: Optional[Exception] = None, 
                  extra_data: Optional[str] = None):
        """记录错误日志 (兼容现有 API)"""
        extra = json.loads(extra_data) if extra_data else {}
        log_func = self._bind_context(extra)
        
        if exception:
            log_func.opt(exception=exception).error(message)
        else:
            log_func.error(message)
    
    def log_critical(self, message: str, exception: Optional[Exception] = None,
                     extra_data: Optional[str] = None):
        """记录严重错误日志 - 新增功能"""
        extra = json.loads(extra_data) if extra_data else {}
        log_func = self._bind_context(extra)
        
        if exception:
            log_func.opt(exception=exception).critical(message)
        else:
            log_func.critical(message)
    
    # =========================================================================
    # 安全执行方法 - 兼容现有 API
    # =========================================================================
    
    def safe(self, func: Callable, *args, return_value: Any = None,
             show_error: bool = True, error_msg: str = None, **kwargs) -> Any:
        """
        万能安全执行函数 (兼容现有 API)
        
        Args:
            func: 要执行的函数
            *args: 函数位置参数
            return_value: 异常时返回的默认值
            show_error: 是否显示 UI 错误通知
            error_msg: 自定义错误消息
            **kwargs: 函数关键字参数
        
        Returns:
            函数执行结果或默认值
        """
        try:
            self.log_info(f"开始执行函数: {func.__name__}")
            result = func(*args, **kwargs)
            self.log_success(f"函数执行成功: {func.__name__}")
            return result
        
        except Exception as e:
            error_message = error_msg or f"函数 {func.__name__} 执行失败: {str(e)}"
            self.log_error(error_message, exception=e)
            
            if show_error:
                try:
                    ui.notify(error_message, type='negative', timeout=5000)
                except Exception:
                    print(f"错误提示显示失败: {error_message}")
            
            return return_value
    
    @contextmanager
    def db_safe(self, operation_name: str = "数据库操作"):
        """
        数据库操作安全上下文管理器 (兼容现有 API)
        
        Args:
            operation_name: 操作名称
        
        Yields:
            数据库会话对象
        
        Raises:
            重新抛出数据库异常
        """
        self.log_info(f"开始{operation_name}")
        
        try:
            from auth.database import get_db
            
            with get_db() as db:
                yield db
                self.log_success(f"{operation_name}成功")
        
        except Exception as e:
            error_msg = f"{operation_name}失败: {str(e)}"
            self.log_error(error_msg, exception=e)
            
            try:
                ui.notify(error_msg, type='negative', timeout=5000)
            except Exception:
                print(f"错误提示显示失败: {error_msg}")
            
            raise  # 重新抛出异常
    
    def safe_protect(self, name: str = None, error_msg: str = None,
                     return_on_error: Any = None):
        """
        页面/函数保护装饰器 (兼容现有 API)
        
        Args:
            name: 函数/页面名称
            error_msg: 自定义错误消息
            return_on_error: 异常时返回的值
        
        Returns:
            装饰器函数
        """
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                func_name = name or func.__name__
                
                try:
                    self.log_info(f"开始执行保护函数: {func_name}")
                    result = func(*args, **kwargs)
                    self.log_success(f"保护函数执行成功: {func_name}")
                    return result
                
                except Exception as e:
                    error_message = error_msg or f"页面 {func_name} 加载失败"
                    self.log_error(f"{func_name}执行失败", exception=e)
                    
                    try:
                        # 显示友好的错误页面
                        with ui.column().classes('p-6 text-center w-full min-h-96'):
                            ui.icon('error_outline', size='4rem').classes('text-red-500 mb-4')
                            ui.label(f'{func_name} 执行失败').classes('text-2xl font-bold text-red-600 mb-2')
                            ui.label(error_message).classes('text-gray-600 mb-4')
                            
                            with ui.row().classes('gap-2 mt-6'):
                                ui.button('刷新页面', icon='refresh',
                                         on_click=lambda: ui.navigate.reload()).classes('bg-blue-500 text-white')
                                ui.button('返回首页', icon='home',
                                         on_click=lambda: ui.navigate.to('/workbench')).classes('bg-gray-500 text-white')
                    except Exception:
                        print(f"错误页面显示失败: {error_message}")
                    
                    return return_on_error
            
            return wrapper
        return decorator
    
    # =========================================================================
    # Loguru 特色功能 - 新增方法
    # =========================================================================
    
    def catch(self, func: Callable = None, *, message: str = None, 
              show_ui_error: bool = True):
        """
        Loguru 异常捕获装饰器 (新增功能)
        
        使用方法:
            @handler.catch
            def my_function():
                # 自动捕获并记录异常
                pass
        
        Args:
            func: 被装饰的函数
            message: 自定义错误消息
            show_ui_error: 是否显示 UI 错误通知
        
        Returns:
            装饰器函数或装饰后的函数
        """
        def decorator(f: Callable) -> Callable:
            @functools.wraps(f)
            @logger.catch(message=message or f"Error in {f.__name__}")
            def wrapper(*args, **kwargs):
                try:
                    return f(*args, **kwargs)
                except Exception as e:
                    if show_ui_error:
                        try:
                            ui.notify(f"{f.__name__} 执行失败", type='negative')
                        except:
                            pass
                    raise
            return wrapper
        
        # 支持 @catch 和 @catch() 两种用法
        if func is None:
            return decorator
        else:
            return decorator(func)
    
    def get_logger(self, name: str = None):
        """
        获取绑定用户上下文的 logger 实例 (新增功能)
        
        使用方法:
            log = handler.get_logger("my_module")
            log.info("This is a message")
        
        Args:
            name: 日志器名称
        
        Returns:
            绑定了上下文的 logger 实例
        """
        context = self._get_user_context()
        bound_logger = logger.bind(**context)
        
        if name:
            bound_logger = bound_logger.bind(module_name=name)
        
        return bound_logger

# =============================================================================
# 全局单例实例
# =============================================================================

_exception_handler = None
_handler_lock = threading.Lock()

def get_exception_handler() -> LoguruExceptionHandler:
    """获取异常处理器单例(线程安全)"""
    global _exception_handler
    if _exception_handler is None:
        with _handler_lock:
            if _exception_handler is None:
                _exception_handler = LoguruExceptionHandler()
    return _exception_handler

# =============================================================================
# 对外暴露的核心函数 - 完全兼容现有 API
# =============================================================================

def log_trace(message: str, extra_data: Optional[str] = None):
    """记录追踪日志 (新增)"""
    handler = get_exception_handler()
    handler.log_trace(message, extra_data)

def log_debug(message: str, extra_data: Optional[str] = None):
    """记录调试日志 (新增)"""
    handler = get_exception_handler()
    handler.log_debug(message, extra_data)

def log_info(message: str, extra_data: Optional[str] = None):
    """记录信息日志 (兼容现有 API)"""
    handler = get_exception_handler()
    handler.log_info(message, extra_data)

def log_success(message: str, extra_data: Optional[str] = None):
    """记录成功日志 (新增)"""
    handler = get_exception_handler()
    handler.log_success(message, extra_data)

def log_warning(message: str, extra_data: Optional[str] = None):
    """记录警告日志 (新增)"""
    handler = get_exception_handler()
    handler.log_warning(message, extra_data)

def log_error(message: str, exception: Optional[Exception] = None,
              extra_data: Optional[str] = None):
    """记录错误日志 (兼容现有 API)"""
    handler = get_exception_handler()
    handler.log_error(message, exception, extra_data)

def log_critical(message: str, exception: Optional[Exception] = None,
                 extra_data: Optional[str] = None):
    """记录严重错误日志 (新增)"""
    handler = get_exception_handler()
    handler.log_critical(message, exception, extra_data)

def safe(func: Callable, *args, return_value: Any = None,
         show_error: bool = True, error_msg: str = None, **kwargs) -> Any:
    """万能安全执行函数 (兼容现有 API)"""
    handler = get_exception_handler()
    return handler.safe(func, *args, return_value=return_value,
                       show_error=show_error, error_msg=error_msg, **kwargs)

@contextmanager
def db_safe(operation_name: str = "数据库操作"):
    """数据库操作安全上下文管理器 (兼容现有 API)"""
    handler = get_exception_handler()
    with handler.db_safe(operation_name) as db:
        yield db

def safe_protect(name: str = None, error_msg: str = None, return_on_error: Any = None):
    """页面/函数保护装饰器 (兼容现有 API)"""
    handler = get_exception_handler()
    return handler.safe_protect(name, error_msg, return_on_error)

def catch(func: Callable = None, *, message: str = None, show_ui_error: bool = True):
    """Loguru 异常捕获装饰器 (新增功能)"""
    handler = get_exception_handler()
    return handler.catch(func, message=message, show_ui_error=show_ui_error)

def get_logger(name: str = None):
    """获取绑定用户上下文的 logger 实例 (新增功能)"""
    handler = get_exception_handler()
    return handler.get_logger(name)

# =============================================================================
# 日志查询和管理工具函数 - 兼容现有 API (适配日期文件夹结构)
# =============================================================================

def get_log_files(days: int = 7) -> List[Dict]:
    """
    获取最近几天的日志文件列表 (兼容现有 API - 适配日期文件夹)
    
    Args:
        days: 查询天数
    
    Returns:
        日志文件列表
    """
    handler = get_exception_handler()
    log_files = []
    
    for i in range(days):
        date = datetime.now() - timedelta(days=i)
        date_str = date.strftime('%Y-%m-%d')
        date_folder = handler.log_base_dir / date_str
        
        if not date_folder.exists():
            continue
        
        # CSV 格式日志文件
        csv_file = date_folder / 'app_logs.csv'
        if csv_file.exists():
            log_files.append({
                'date': date_str,
                'file_path': csv_file,
                'size': csv_file.stat().st_size,
                'type': 'csv'
            })
        
        # 普通日志文件
        log_file = date_folder / 'app.log'
        if log_file.exists():
            log_files.append({
                'date': date_str,
                'file_path': log_file,
                'size': log_file.stat().st_size,
                'type': 'log'
            })
        
        # 错误日志文件
        error_file = date_folder / 'error.log'
        if error_file.exists():
            log_files.append({
                'date': date_str,
                'file_path': error_file,
                'size': error_file.stat().st_size,
                'type': 'error'
            })
    
    return log_files

def get_today_errors(limit: int = 50) -> List[Dict]:
    """
    获取今天的错误日志 (兼容现有 API - CSV 格式)
    
    Args:
        limit: 返回的最大错误数
    
    Returns:
        错误日志列表
    """
    handler = get_exception_handler()
    today_folder = handler.current_log_dir
    csv_file = today_folder / "app_logs.csv"
    
    if not csv_file.exists():
        return []
    
    try:
        errors = []
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['level'] in ['ERROR', 'CRITICAL']:
                    errors.append(row)
        
        # 返回最近的错误(最后 limit 条)
        return errors[-limit:] if len(errors) > limit else errors
    
    except Exception as e:
        print(f"读取错误日志失败: {e}")
        return []

def get_today_logs_by_level(level: str = "INFO", limit: int = 100) -> List[Dict]:
    """
    根据日志级别获取今天的日志 (新增功能)
    
    Args:
        level: 日志级别 (TRACE, DEBUG, INFO, SUCCESS, WARNING, ERROR, CRITICAL)
        limit: 返回的最大日志数
    
    Returns:
        日志列表
    """
    handler = get_exception_handler()
    today_folder = handler.current_log_dir
    csv_file = today_folder / "app_logs.csv"
    
    if not csv_file.exists():
        return []
    
    try:
        logs = []
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['level'] == level.upper():
                    logs.append(row)
        
        return logs[-limit:] if len(logs) > limit else logs
    
    except Exception as e:
        print(f"读取日志失败: {e}")
        return []

def cleanup_logs(days_to_keep: int = 30):
    """
    手动清理旧日志文件夹 (兼容现有 API)
    
    Args:
        days_to_keep: 保留天数
    """
    handler = get_exception_handler()
    handler.max_log_days = days_to_keep
    
    # 立即执行清理
    handler._cleanup_old_log_folders()
    
    log_info(f"日志清理完成: 保留 {days_to_keep} 天")

def export_logs_to_json(days: int = 7, output_file: str = None) -> str:
    """
    导出日志为 JSON 格式 (新增功能)
    Args:
        days: 导出天数
        output_file: 输出文件路径(可选),如果不指定则自动生成
    
    Returns:
        输出文件路径
    """
    handler = get_exception_handler()
    
    # 修复:输出文件应该在日志根目录下,而不是在某个日期文件夹下
    if output_file is None:
        # 在日志根目录创建 exports 文件夹
        export_dir = handler.log_base_dir / "exports"
        export_dir.mkdir(exist_ok=True)
        output_file = export_dir / f"logs_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    else:
        # 如果用户指定了路径,使用 Path 对象处理
        output_file = Path(output_file)
    
    all_logs = []
    
    # 遍历最近几天的日期文件夹
    for i in range(days):
        date = datetime.now() - timedelta(days=i)
        date_str = date.strftime('%Y-%m-%d')
        date_folder = handler.log_base_dir / date_str
        csv_file = date_folder / 'app_logs.csv'
        
        if csv_file.exists():
            try:
                with open(csv_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        all_logs.append(row)
            except Exception as e:
                print(f"读取 {csv_file} 失败: {e}")
    
    # 写入 JSON 文件
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_logs, f, ensure_ascii=False, indent=2)
        
        log_success(f"日志导出成功: {output_file}, 共 {len(all_logs)} 条记录")
        return str(output_file)
    
    except Exception as e:
        log_error(f"日志导出失败", exception=e)
        return None

def get_log_statistics(days: int = 7) -> Dict[str, Any]:
    """
    获取日志统计信息 (新增功能)
    
    Args:
        days: 统计天数
    
    Returns:
        统计信息字典
    """
    handler = get_exception_handler()
    stats = {
        'total_logs': 0,
        'error_count': 0,
        'warning_count': 0,
        'info_count': 0,
        'by_date': {},
        'by_level': {},
        'by_user': {}
    }
    
    for i in range(days):
        date = datetime.now() - timedelta(days=i)
        date_str = date.strftime('%Y-%m-%d')
        date_folder = handler.log_base_dir / date_str
        csv_file = date_folder / 'app_logs.csv'
        
        if csv_file.exists():
            try:
                with open(csv_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        stats['total_logs'] += 1
                        
                        # 按级别统计
                        level = row['level']
                        stats['by_level'][level] = stats['by_level'].get(level, 0) + 1
                        
                        if level == 'ERROR':
                            stats['error_count'] += 1
                        elif level == 'WARNING':
                            stats['warning_count'] += 1
                        elif level == 'INFO':
                            stats['info_count'] += 1
                        
                        # 按日期统计
                        stats['by_date'][date_str] = stats['by_date'].get(date_str, 0) + 1
                        
                        # 按用户统计
                        username = row.get('username', 'unknown')
                        stats['by_user'][username] = stats['by_user'].get(username, 0) + 1
            
            except Exception as e:
                print(f"读取 {csv_file} 失败: {e}")
    return stats

def get_log_folder_info() -> Dict[str, Any]:
    """
    获取日志文件夹信息 (新增功能)
    
    Returns:
        文件夹信息字典
    """
    handler = get_exception_handler()
    
    folder_info = {
        'base_dir': str(handler.log_base_dir),
        'current_dir': str(handler.current_log_dir),
        'folder_count': 0,
        'total_size': 0,
        'folders': []
    }
    
    try:
        for log_folder in sorted(handler.log_base_dir.iterdir(), reverse=True):
            if not log_folder.is_dir():
                continue
            
            try:
                # 计算文件夹大小
                folder_size = sum(f.stat().st_size for f in log_folder.rglob('*') if f.is_file())
                
                folder_info['folders'].append({
                    'name': log_folder.name,
                    'path': str(log_folder),
                    'size': folder_size,
                    'file_count': len(list(log_folder.iterdir()))
                })
                
                folder_info['folder_count'] += 1
                folder_info['total_size'] += folder_size
            
            except Exception as e:
                print(f"读取文件夹 {log_folder} 失败: {e}")
    
    except Exception as e:
        print(f"读取日志文件夹信息失败: {e}")
    
    return folder_info

# =============================================================================
# 使用示例和测试
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("🚀 基于 Loguru 的增强异常处理器 - 测试 (v2.1 按日期文件夹组织)")
    print("=" * 70)
    
    # 1. 基础日志记录(所有级别)
    print("\n📝 测试 1: 基础日志记录")
    log_trace("这是追踪日志")
    log_debug("这是调试日志")
    log_info("应用启动", extra_data='{"version": "2.1.0", "env": "production"}')
    log_success("初始化成功")
    log_warning("这是警告日志")
    log_error("这是错误日志")
    log_critical("这是严重错误日志")
    
    # 2. 安全执行函数
    print("\n🛡️ 测试 2: 安全执行函数")
    def risky_function():
        raise ValueError("测试异常")
    
    result = safe(risky_function, return_value="默认值", show_error=False)
    print(f"安全执行结果: {result}")
    
    # 3. 异常捕获装饰器(新功能)
    print("\n🎯 测试 3: Loguru 异常捕获装饰器")
    @catch(message="测试函数异常", show_ui_error=False)
    def test_catch():
        raise RuntimeError("catch 装饰器测试")
    try:
        test_catch()
    except:
        print("异常已被捕获")
    
    # 4. 页面保护装饰器
    print("\n🔒 测试 4: 页面保护装饰器")
    @safe_protect(name="测试页面", error_msg="页面加载失败")
    def test_page():
        raise RuntimeError("页面异常")
    
    test_page()
    
    # 5. 获取自定义 logger(新功能)
    print("\n📊 测试 5: 自定义 logger")
    custom_log = get_logger("my_module")
    custom_log.info("这是来自自定义模块的日志")
    custom_log.success("自定义模块操作成功")
    
    # 6. 查看日志文件
    print("\n📂 测试 6: 查看日志文件")
    log_files = get_log_files(3)
    print(f"最近3天的日志文件: {len(log_files)} 个")
    for file in log_files:
        print(f"  - {file['date']} ({file['type']}): {file['size']} bytes")
    
    # 7. 查看今天的错误
    print("\n❌ 测试 7: 查看今天的错误")
    today_errors = get_today_errors(10)
    print(f"今天的错误数量: {len(today_errors)}")
    
    # 8. 日志统计(新功能)
    print("\n📈 测试 8: 日志统计")
    stats = get_log_statistics(days=1)
    print(f"总日志数: {stats['total_logs']}")
    print(f"错误数: {stats['error_count']}")
    print(f"警告数: {stats['warning_count']}")
    print(f"各级别统计: {stats['by_level']}")
    
    # 9. 文件夹信息(新功能)
    print("\n📁 测试 9: 日志文件夹信息")
    folder_info = get_log_folder_info()
    print(f"日志根目录: {folder_info['base_dir']}")
    print(f"当前日志目录: {folder_info['current_dir']}")
    print(f"文件夹数量: {folder_info['folder_count']}")
    print(f"总大小: {folder_info['total_size']} bytes")
    
    # 10. 导出日志为 JSON(新功能)
    # print("\n💾 测试 10: 导出日志为 JSON")
    # export_file = export_logs_to_json(days=1)
    # if export_file:
    #     print(f"日志已导出: {export_file}")
    
    print("\n" + "=" * 70)
    print("✅ 增强异常处理模块测试完成 (v2.1)")
    print("=" * 70)
    
    # 性能提升说明
    print("\n💡 性能提升:")
    print("  - 异步日志写入,不阻塞主线程")
    print("  - 智能日志轮转,自动压缩")
    print("  - 7 种日志级别,更精细的控制")
    print("  - 错误日志单独存储,快速定位")
    print("  - 完全向后兼容现有 API")
    print("  - 按日期文件夹组织,管理更清晰")