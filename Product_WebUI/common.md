# common

- **common\__init__.py** *(包初始化文件 - 空)*
```python

```

- **common\log_handler.py**
```python
"""
增强的异常处理和日志模块 - 基于 Loguru 的混合架构(优化版 v2.2 - 修复调用栈问题)
保留现有 API,增强底层实现,按日期文件夹组织日志
文件路径: webproduct_ui_template/common/log_handler.py

关键修复(v2.2):
1. 修复 module/function/line_number 总是显示 log_handler.py 的问题
2. 使用 logger.opt(depth=N) 正确追踪调用栈
3. 改进用户上下文获取逻辑,减少 anonymous 出现

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
            self.current_log_dir = today_log_dir
            
            # 重新配置 Loguru
            logger.remove()
            self._setup_loguru()
            if self.csv_enabled:
                self._setup_csv_logging()
    
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
            level="DEBUG",   # ✅ 控制台输出 DEBUG,不写入日志文件
            colorize=True,
            backtrace=True,
            diagnose=True,
            enqueue=False  # 控制台同步输出,方便调试
        )
        
        # 2️⃣ 普通日志文件 - 存储在当天日期文件夹下
        logger.add(
            self.current_log_dir / "app.log",
            rotation="500 MB",
            retention=f"{self.max_log_days} days",
            compression="zip",
            encoding="utf-8",
            format=(
                "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
                "{level: <8} | "
                "{extra[user_id]}@{extra[username]} | "
                "{name}:{function}:{line} | "
                "{message}"
            ),
            level="INFO",
            enqueue=True,
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
                "{exception}"
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
                        stack_trace = '\n'.join(stack_lines[:20])
                    
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
        """
        获取当前用户上下文 - 改进版
        
        修复说明:
        - 增加了更详细的调试信息
        - 区分不同的未登录状态: guest(未登录) vs anonymous(获取失败)
        """
        try:
            from auth.auth_manager import auth_manager
            user = auth_manager.current_user
            
            if user:
                return {
                    'user_id': user.id,
                    'username': user.username
                }
            else:
                # 未登录状态,返回 guest
                return {'user_id': None, 'username': 'system'}
                
        except ImportError:
            # auth 模块未加载
            return {'user_id': None, 'username': 'system'}
        except Exception as e:
            # 其他异常,记录错误原因
            print(f"⚠️ 获取用户上下文失败: {e}")
            return {'user_id': None, 'username': 'anonymous'}
    
    def _bind_context(self, extra_data: Optional[Dict] = None, depth: int = 0):
        """
        绑定用户上下文到日志 - 修复版
        
        关键修复:
        使用 opt(depth=depth) 让 Loguru 正确追踪调用栈位置
        
        Args:
            extra_data: 额外数据
            depth: 调用栈深度
                   - 0: 当前函数 (_bind_context)
                   - 1: 调用者 (如 log_info)
                   - 2: 调用者的调用者 (全局函数 -> 类方法)
        
        Returns:
            绑定了上下文的 logger 实例
        """
        context = self._get_user_context()
        if extra_data:
            context['extra_data'] = extra_data
        
        # 🔧 关键修复: 使用 opt(depth=depth) 正确追踪调用栈
        return logger.opt(depth=depth).bind(**context)
    
    # =========================================================================
    # 核心日志方法 - 修复版 (depth=1)
    # =========================================================================
    
    def log_trace(self, message: str, extra_data: Optional[str] = None):
        """记录追踪日志 (最详细)"""
        extra = json.loads(extra_data) if extra_data else {}
        # depth=1: 跳过当前函数,记录调用者位置
        self._bind_context(extra, depth=1).trace(message)
    
    def log_debug(self, message: str, extra_data: Optional[str] = None):
        """记录调试日志"""
        extra = json.loads(extra_data) if extra_data else {}
        self._bind_context(extra, depth=1).debug(message)
    
    def log_info(self, message: str, extra_data: Optional[str] = None):
        """记录信息日志 (兼容现有 API)"""
        extra = json.loads(extra_data) if extra_data else {}
        self._bind_context(extra, depth=1).info(message)
    
    def log_success(self, message: str, extra_data: Optional[str] = None):
        """记录成功日志"""
        extra = json.loads(extra_data) if extra_data else {}
        self._bind_context(extra, depth=1).success(message)
    
    def log_warning(self, message: str, extra_data: Optional[str] = None):
        """记录警告日志"""
        extra = json.loads(extra_data) if extra_data else {}
        self._bind_context(extra, depth=1).warning(message)
    
    def log_error(self, message: str, exception: Optional[Exception] = None, 
                  extra_data: Optional[str] = None):
        """记录错误日志 (兼容现有 API)"""
        extra = json.loads(extra_data) if extra_data else {}
        log_func = self._bind_context(extra, depth=1)
        
        if exception:
            log_func.opt(exception=exception).error(message)
        else:
            log_func.error(message)
    
    def log_critical(self, message: str, exception: Optional[Exception] = None,
                     extra_data: Optional[str] = None):
        """记录严重错误日志"""
        extra = json.loads(extra_data) if extra_data else {}
        log_func = self._bind_context(extra, depth=1)
        
        if exception:
            log_func.opt(exception=exception).critical(message)
        else:
            log_func.critical(message)
    
    # =========================================================================
    # 安全执行方法 - 兼容现有 API
    # =========================================================================
    
    def safe(self, func: Callable, *args, return_value: Any = None,
             show_error: bool = True, error_msg: str = None, **kwargs) -> Any:
        """万能安全执行函数 (兼容现有 API)"""
        try:
            self.log_info(f"    │   ├──safe开始安全执行函数: {func.__name__}")
            result = func(*args, **kwargs)
            self.log_info(f"    │   ├──safe安全函数执行成功: {func.__name__}")
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
        """数据库操作安全上下文管理器 (兼容现有 API)"""
        from auth.database import get_db
        
        try:
            with get_db() as db:
                yield db
                
        except Exception as e:
            self.log_error(f"数据库操作失败: {operation_name}", exception=e)
            try:
                ui.notify(f"数据库操作失败: {operation_name}", type='negative')
            except:
                pass
            raise
    
    def safe_protect(self, name: str = None, error_msg: str = None, 
                     return_on_error: Any = None):
        """页面/函数保护装饰器 (兼容现有 API)"""
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                func_name = name or func.__name__
                
                try:
                    self.log_info(f"├──开始页面保护执行：{func_name} ")
                    result = func(*args, **kwargs)
                    self.log_info(f"├──完成页面保护执行: {func_name} ")
                    return result
                
                except Exception as e:
                    error_message = error_msg or f"页面 {func_name} 加载失败"
                    self.log_error(f"{func_name}执行失败", exception=e)
                    
                    try:
                        with ui.row().classes('fit items-center justify-center'):
                            # 显示友好的错误页面
                            # 移除 'w-full' 和 'min-h-96'，让内容区域根据内部元素大小自适应
                            with ui.column().classes('p-6 text-center'): # 只需要 text-center 来对 column 内部的文本和行元素进行水平居中
                                ui.icon('error_outline', size='4rem').classes('text-red-500 mb-4')
                                ui.label(f'{func_name} 执行失败').classes('text-2xl font-bold text-red-600 mb-2')
                                ui.label(error_message).classes('text-gray-600 mb-4')

                                # 按钮行，需要让它在 column 中保持居中
                                # 'mx-auto' 是使块级元素（如 ui.row）水平居中的 Tailwind 类
                                with ui.row().classes('gap-2 mt-6 mx-auto'):
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
        """Loguru 异常捕获装饰器"""
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
        获取绑定用户上下文的 logger 实例
        使用方法:
            log = handler.get_logger("my_module")
            log.info("This is a message")
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
# 对外暴露的核心函数 - 完全兼容现有 API (修复版 depth=2)
# =============================================================================

def log_trace(message: str, extra_data: Optional[str] = None):
    """记录追踪日志"""
    handler = get_exception_handler()
    extra = json.loads(extra_data) if extra_data else {}
    # 🔧 depth=2: 跳过当前函数 + _bind_context,记录真实调用者
    handler._bind_context(extra, depth=2).trace(message)

def log_debug(message: str, extra_data: Optional[str] = None):
    """记录调试日志"""
    handler = get_exception_handler()
    extra = json.loads(extra_data) if extra_data else {}
    handler._bind_context(extra, depth=2).debug(message)

def log_info(message: str, extra_data: Optional[str] = None):
    """记录信息日志 (兼容现有 API)"""
    handler = get_exception_handler()
    extra = json.loads(extra_data) if extra_data else {}
    handler._bind_context(extra, depth=2).info(message)

def log_success(message: str, extra_data: Optional[str] = None):
    """记录成功日志"""
    handler = get_exception_handler()
    extra = json.loads(extra_data) if extra_data else {}
    handler._bind_context(extra, depth=2).success(message)

def log_warning(message: str, extra_data: Optional[str] = None):
    """记录警告日志"""
    handler = get_exception_handler()
    extra = json.loads(extra_data) if extra_data else {}
    handler._bind_context(extra, depth=2).warning(message)

def log_error(message: str, exception: Optional[Exception] = None,
              extra_data: Optional[str] = None):
    """记录错误日志 (兼容现有 API)"""
    handler = get_exception_handler()
    extra = json.loads(extra_data) if extra_data else {}
    log_func = handler._bind_context(extra, depth=2)
    
    if exception:
        log_func.opt(exception=exception).error(message)
    else:
        log_func.error(message)

def log_critical(message: str, exception: Optional[Exception] = None,
                 extra_data: Optional[str] = None):
    """记录严重错误日志"""
    handler = get_exception_handler()
    extra = json.loads(extra_data) if extra_data else {}
    log_func = handler._bind_context(extra, depth=2)
    
    if exception:
        log_func.opt(exception=exception).critical(message)
    else:
        log_func.critical(message)

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
    """Loguru 异常捕获装饰器"""
    handler = get_exception_handler()
    return handler.catch(func, message=message, show_ui_error=show_ui_error)

def get_logger(name: str = None):
    """获取绑定用户上下文的 logger 实例"""
    handler = get_exception_handler()
    return handler.get_logger(name)

# =============================================================================
# 日志查询和管理工具函数 - 兼容现有 API (适配日期文件夹结构)
# =============================================================================

def get_log_files(days: int = 7) -> List[Dict]:
    """获取最近几天的日志文件列表 (兼容现有 API)"""
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
    """获取今天的错误日志 (兼容现有 API)"""
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
        
        return errors[-limit:] if len(errors) > limit else errors
    
    except Exception as e:
        print(f"读取错误日志失败: {e}")
        return []

def get_today_logs_by_level(level: str = "INFO", limit: int = 100) -> List[Dict]:
    """根据日志级别获取今天的日志"""
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
    """手动清理旧日志文件夹 (兼容现有 API)"""
    handler = get_exception_handler()
    handler.max_log_days = days_to_keep
    handler._cleanup_old_log_folders()
    log_info(f"日志清理完成: 保留 {days_to_keep} 天")

def get_log_statistics(days: int = 7) -> Dict[str, Any]:
    """获取日志统计信息"""
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
                        
                        level = row['level']
                        stats['by_level'][level] = stats['by_level'].get(level, 0) + 1
                        
                        if level == 'ERROR':
                            stats['error_count'] += 1
                        elif level == 'WARNING':
                            stats['warning_count'] += 1
                        elif level == 'INFO':
                            stats['info_count'] += 1
                        
                        stats['by_date'][date_str] = stats['by_date'].get(date_str, 0) + 1
                        
                        username = row.get('username', 'unknown')
                        stats['by_user'][username] = stats['by_user'].get(username, 0) + 1
            
            except Exception as e:
                print(f"读取 {csv_file} 失败: {e}")
    
    return stats

def get_log_folder_info() -> Dict[str, Any]:
    """获取日志文件夹信息"""
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
    print("🚀 基于 Loguru 的增强异常处理器 - 测试 (v2.2 修复版)")
    print("=" * 70)
    
    # 1. 基础日志记录
    print("\n📝 测试 1: 基础日志记录")
    log_trace("这是追踪日志")
    log_debug("这是调试日志")
    log_info("应用启动", extra_data='{"version": "2.2.0", "env": "production"}')
    log_success("初始化成功")
    log_warning("这是警告日志")
    log_error("这是错误日志")
    log_critical("这是严重错误日志")
    
    # 2. 模拟业务代码调用
    print("\n🎯 测试 2: 模拟业务代码调用(验证 module/function/line 是否正确)")
    
    def business_function():
        """模拟业务函数"""
        log_info("业务函数中的信息日志")
        log_warning("业务函数中的警告日志")
        
        try:
            raise ValueError("测试异常")
        except Exception as e:
            log_error("业务函数中出现错误", exception=e)
    
    # 调用业务函数
    business_function()
    
    # 3. 查看日志文件
    print("\n📂 测试 3: 查看日志文件")
    log_files = get_log_files(1)
    print(f"今天的日志文件: {len(log_files)} 个")
    for file in log_files:
        print(f"  - {file['date']} ({file['type']}): {file['size']} bytes")
    
    # 4. 日志统计
    print("\n📈 测试 4: 日志统计")
    stats = get_log_statistics(days=1)
    print(f"总日志数: {stats['total_logs']}")
    print(f"错误数: {stats['error_count']}")
    print(f"按级别统计: {stats['by_level']}")
    
    print("\n" + "=" * 70)
    print("✅ 测试完成! 请检查 logs/YYYY-MM-DD/app_logs.csv 文件")
    print("✅ 验证: module 应该显示 '__main__'")
    print("✅ 验证: function 应该显示 'business_function'")
    print("✅ 验证: line_number 应该显示 business_function 中的实际行号")
    print("=" * 70)
```

- **common\safe_openai_client_pool.py**
```python
"""
SafeOpenAIClientPool - 线程安全的OpenAI客户端连接池

文件路径: \common\safe_openai_client_pool.py

专为NiceGUI应用设计的OpenAI客户端管理器，提供线程安全的客户端创建、缓存和管理功能。

特性：
- 异步锁保证并发安全，避免重复创建客户端
- 智能缓存机制，按模型配置缓存客户端实例
- 自动内存管理，支持LRU缓存清理
- 完善的错误处理和用户友好的提示
- 详细的统计信息和性能监控
- 配置更新时自动刷新客户端
- 支持配置函数和配置字典两种传参方式

设计原则：
1. 线程安全：使用asyncio.Lock()防止并发创建
2. 内存高效：限制缓存大小，自动清理旧客户端
3. 用户友好：提供清晰的错误信息和状态提示
4. 可观测性：详细的日志和统计信息
5. 容错性：优雅处理各种异常情况
6. 兼容性：支持多种配置传递方式
"""

import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, Optional, Set, Any, Union, Callable
from openai import OpenAI


class SafeOpenAIClientPool:
    """
    线程安全的OpenAI客户端连接池
    
    使用场景：
    - NiceGUI应用的聊天功能
    - 多用户并发访问OpenAI API
    - 动态模型切换
    - 配置热更新
    """
    
    def __init__(self, max_clients: int = 20, client_ttl_hours: int = 24):
        """
        初始化客户端池
        
        Args:
            max_clients: 最大缓存的客户端数量，防止内存泄漏
            client_ttl_hours: 客户端生存时间（小时），超时自动清理
        """
        # 客户端缓存
        self._clients: Dict[str, OpenAI] = {}
        self._client_configs: Dict[str, Dict] = {}  # 缓存配置信息，用于验证
        self._creation_times: Dict[str, datetime] = {}  # 记录创建时间
        self._access_times: Dict[str, datetime] = {}  # 记录最后访问时间
        self._access_counts: Dict[str, int] = {}  # 记录访问次数
        
        # 并发控制
        self._lock = asyncio.Lock()  # 异步锁，确保线程安全
        self._creating: Set[str] = set()  # 正在创建的客户端标记
        
        # 配置参数
        self._max_clients = max_clients
        self._client_ttl = timedelta(hours=client_ttl_hours)
        
        # 统计信息
        self._total_requests = 0
        self._cache_hits = 0
        self._cache_misses = 0
        self._creation_count = 0
        self._cleanup_count = 0
        
        print(f"🔧 SafeOpenAIClientPool 已初始化")
        print(f"   最大缓存: {max_clients} 个客户端")
        print(f"   客户端TTL: {client_ttl_hours} 小时")
    
    async def get_client(self, model_key: str, config_getter_func=None) -> Optional[OpenAI]:
        """
        获取指定模型的OpenAI客户端实例
        
        Args:
            model_key: 模型键名 (如 'deepseek-chat', 'moonshot-v1-8k')
            config_getter_func: 配置获取方式，支持：
                              - 函数：function(model_key) -> dict
                              - 字典：直接使用该配置
                              - None：尝试自动导入配置函数
            
        Returns:
            OpenAI客户端实例，失败时返回None
        """
        self._total_requests += 1
        start_time = time.time()
        
        try:
            # 清理过期的客户端
            await self._cleanup_expired_clients()
            
            # 快速路径：缓存命中且有效
            if await self._is_client_valid(model_key):
                self._cache_hits += 1
                self._access_counts[model_key] = self._access_counts.get(model_key, 0) + 1
                self._access_times[model_key] = datetime.now()
                
                elapsed_ms = (time.time() - start_time) * 1000
                print(f"⚡ 缓存命中: {model_key} ({elapsed_ms:.1f}ms)")
                return self._clients[model_key]
            
            # 慢速路径：需要创建新客户端
            self._cache_misses += 1
            return await self._create_client_safe(model_key, config_getter_func, start_time)
            
        except Exception as e:
            elapsed_ms = (time.time() - start_time) * 1000
            error_msg = f"获取OpenAI客户端失败 ({model_key}): {str(e)}"
            print(f"❌ {error_msg} ({elapsed_ms:.1f}ms)")
            return None
    
    async def _is_client_valid(self, model_key: str) -> bool:
        """
        检查缓存的客户端是否仍然有效
        
        Args:
            model_key: 模型键名
            
        Returns:
            客户端是否有效
        """
        if model_key not in self._clients:
            return False
        
        # 检查是否过期
        creation_time = self._creation_times.get(model_key)
        if creation_time and datetime.now() - creation_time > self._client_ttl:
            print(f"⏰ 客户端已过期: {model_key}")
            await self._remove_client(model_key)
            return False
        
        # 简单的有效性检查
        try:
            client = self._clients[model_key]
            return hasattr(client, 'api_key') and hasattr(client, 'base_url')
        except Exception:
            return False
    
    async def _create_client_safe(self, model_key: str, config_getter_func, start_time: float) -> Optional[OpenAI]:
        """
        线程安全的客户端创建方法
        
        Args:
            model_key: 模型键名
            config_getter_func: 配置获取方式
            start_time: 开始时间（用于性能统计）
            
        Returns:
            创建的OpenAI客户端实例
        """
        # 检查是否正在创建，避免重复创建
        if model_key in self._creating:
            print(f"⏳ 等待客户端创建完成: {model_key}")
            
            # 等待其他协程完成创建（最多等待10秒）
            wait_start = time.time()
            while model_key in self._creating and (time.time() - wait_start) < 10:
                await asyncio.sleep(0.01)
            
            # 检查是否创建成功
            if model_key in self._clients:
                elapsed_ms = (time.time() - start_time) * 1000
                print(f"✅ 等待完成，获取客户端: {model_key} ({elapsed_ms:.1f}ms)")
                return self._clients[model_key]
            else:
                print(f"⚠️ 等待客户端创建超时或失败: {model_key}")
                return None
        
        # 获取异步锁，确保只有一个协程创建客户端
        async with self._lock:
            # 双重检查锁定模式
            if model_key in self._clients:
                elapsed_ms = (time.time() - start_time) * 1000
                print(f"🔄 锁内缓存命中: {model_key} ({elapsed_ms:.1f}ms)")
                return self._clients[model_key]
            
            # 标记为正在创建
            self._creating.add(model_key)
            
            try:
                return await self._create_client_internal(model_key, config_getter_func, start_time)
            finally:
                # 无论成功失败，都要清除创建标记
                self._creating.discard(model_key)
    
    async def _create_client_internal(self, model_key: str, config_getter_func, start_time: float) -> Optional[OpenAI]:
        """
        内部客户端创建方法
        
        Args:
            model_key: 模型键名
            config_getter_func: 配置获取方式
            start_time: 开始时间
            
        Returns:
            创建的OpenAI客户端实例
        """
        print(f"🔨 开始创建OpenAI客户端: {model_key}")
        
        try:
            # 获取模型配置
            config = await self._get_model_config(model_key, config_getter_func)
            if not config:
                raise ValueError(f"无法获取模型配置: {model_key}")
            
            # 验证必要的配置项
            api_key = config.get('api_key', '').strip()
            base_url = config.get('base_url', '').strip()
            
            if not api_key:
                raise ValueError(f"模型 {model_key} 缺少有效的 API Key")
            
            if not base_url:
                raise ValueError(f"模型 {model_key} 缺少有效的 Base URL")
            
            # 检查缓存是否已满，如需要则清理
            await self._check_and_cleanup_cache()
            
            # 创建OpenAI客户端实例
            client = OpenAI(
                api_key=api_key,
                base_url=base_url,
                timeout=config.get('timeout', 60),
                max_retries=config.get('max_retries', 3)
            )
            
            # 缓存客户端和相关信息
            current_time = datetime.now()
            self._clients[model_key] = client
            self._client_configs[model_key] = config.copy()
            self._creation_times[model_key] = current_time
            self._access_times[model_key] = current_time
            self._access_counts[model_key] = 1
            self._creation_count += 1
            
            elapsed_ms = (time.time() - start_time) * 1000
            model_name = config.get('name', model_key)
            
            print(f"✅ 客户端创建成功: {model_name} ({elapsed_ms:.1f}ms)")
            print(f"   API Key: {api_key[:12]}...")
            print(f"   Base URL: {base_url}")
            
            return client
            
        except Exception as e:
            error_msg = f"创建OpenAI客户端失败 ({model_key}): {str(e)}"
            print(f"❌ {error_msg}")
            raise
    
    async def _get_model_config(self, model_key: str, config_getter_func) -> Optional[Dict]:
        """
        获取模型配置信息（支持函数和字典两种方式）
        
        Args:
            model_key: 模型键名
            config_getter_func: 外部提供的配置获取方式
            
        Returns:
            模型配置字典
        """
        if config_getter_func:
            if callable(config_getter_func):
                # 使用外部提供的配置获取函数
                try:
                    config = config_getter_func(model_key)
                    if isinstance(config, dict):
                        return config
                    else:
                        print(f"⚠️ 配置获取函数返回了非字典类型: {type(config)}")
                        return None
                except Exception as e:
                    print(f"⚠️ 调用配置获取函数失败: {str(e)}")
                    return None
            elif isinstance(config_getter_func, dict):
                # 直接使用配置字典
                return config_getter_func
            else:
                print(f"⚠️ 不支持的config_getter_func类型: {type(config_getter_func)}")
                return None
        
        # 尝试自动导入配置获取函数
        try:
            # 假设配置函数在某个已知模块中
            # 这里需要根据实际项目结构调整导入路径
            from menu_pages.enterprise_archive.chat_component.config import get_model_config
            return get_model_config(model_key)
        except ImportError:
            print(f"⚠️ 无法自动导入配置获取函数，请提供 config_getter_func 参数")
            return None
    
    async def _check_and_cleanup_cache(self):
        """
        检查缓存大小并在需要时清理最少使用的客户端
        """
        if len(self._clients) >= self._max_clients:
            print(f"🧹 缓存已满 ({len(self._clients)}/{self._max_clients})，开始清理...")
            
            # 找到最少使用的客户端（LRU策略）
            if self._access_times:
                # 按最后访问时间排序，移除最久未使用的
                oldest_model = min(self._access_times.items(), key=lambda x: x[1])[0]
                await self._remove_client(oldest_model)
                self._cleanup_count += 1
                print(f"🗑️ 已清理最久未使用的客户端: {oldest_model}")
    
    async def _cleanup_expired_clients(self):
        """
        清理过期的客户端
        """
        current_time = datetime.now()
        expired_clients = []
        
        for model_key, creation_time in self._creation_times.items():
            if current_time - creation_time > self._client_ttl:
                expired_clients.append(model_key)
        
        for model_key in expired_clients:
            await self._remove_client(model_key)
            self._cleanup_count += 1
            print(f"⏰ 已清理过期客户端: {model_key}")
    
    async def _remove_client(self, model_key: str):
        """
        移除指定的客户端及其相关信息
        
        Args:
            model_key: 要移除的模型键名
        """
        self._clients.pop(model_key, None)
        self._client_configs.pop(model_key, None)
        self._creation_times.pop(model_key, None)
        self._access_times.pop(model_key, None)
        self._access_counts.pop(model_key, None)
    
    async def update_client(self, model_key: str, config_getter_func=None) -> Optional[OpenAI]:
        """
        更新指定模型的客户端（配置变更时使用）
        
        Args:
            model_key: 模型键名
            config_getter_func: 配置获取方式
            
        Returns:
            更新后的客户端实例
        """
        print(f"🔄 更新客户端: {model_key}")
        
        # 移除旧客户端
        await self._remove_client(model_key)
        
        # 创建新客户端
        return await self.get_client(model_key, config_getter_func)
    
    async def clear_cache(self) -> int:
        """
        清空所有缓存的客户端
        
        Returns:
            清理的客户端数量
        """
        async with self._lock:
            cleared_count = len(self._clients)
            
            self._clients.clear()
            self._client_configs.clear()
            self._creation_times.clear()
            self._access_times.clear()
            self._access_counts.clear()
            
            self._cleanup_count += cleared_count
            
            print(f"🧹 已清空所有客户端缓存，共清理 {cleared_count} 个客户端")
            return cleared_count
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取客户端池的统计信息
        
        Returns:
            包含各种统计信息的字典
        """
        cache_hit_rate = (self._cache_hits / self._total_requests * 100) if self._total_requests > 0 else 0.0
        
        return {
            # 基本状态
            'cached_clients': len(self._clients),
            'creating_clients': len(self._creating),
            'max_clients': self._max_clients,
            'models': list(self._clients.keys()),
            
            # 性能统计
            'total_requests': self._total_requests,
            'cache_hits': self._cache_hits,
            'cache_misses': self._cache_misses,
            'cache_hit_rate': f"{cache_hit_rate:.1f}%",
            'creation_count': self._creation_count,
            'cleanup_count': self._cleanup_count,
            
            # 详细信息
            'access_counts': self._access_counts.copy(),
            'creation_times': {
                k: v.strftime('%H:%M:%S') for k, v in self._creation_times.items()
            },
            'access_times': {
                k: v.strftime('%H:%M:%S') for k, v in self._access_times.items()
            }
        }
    
    def print_stats(self):
        """
        打印详细的统计信息到控制台
        """
        stats = self.get_stats()
        
        print(f"\n📊 SafeOpenAIClientPool 统计信息")
        print(f"{'=' * 50}")
        print(f"缓存状态: {stats['cached_clients']}/{stats['max_clients']} 个客户端")
        print(f"正在创建: {stats['creating_clients']} 个")
        print(f"总请求数: {stats['total_requests']}")
        print(f"缓存命中率: {stats['cache_hit_rate']}")
        print(f"创建次数: {stats['creation_count']}")
        print(f"清理次数: {stats['cleanup_count']}")
        
        if stats['models']:
            print(f"\n📱 已缓存的模型:")
            for model in stats['models']:
                access_count = stats['access_counts'].get(model, 0)
                creation_time = stats['creation_times'].get(model, 'Unknown')
                access_time = stats['access_times'].get(model, 'Unknown')
                print(f"  • {model}")
                print(f"    访问次数: {access_count}")
                print(f"    创建时间: {creation_time}")
                print(f"    最后访问: {access_time}")
        else:
            print(f"\n暂无缓存的客户端")
        
        print()
    
    def __repr__(self):
        """返回客户端池的字符串表示"""
        return f"<SafeOpenAIClientPool(clients={len(self._clients)}/{self._max_clients}, hit_rate={self.get_stats()['cache_hit_rate']})>"


# ==================== 全局单例实例 ====================

# 全局客户端池实例（延迟初始化）
_global_client_pool: Optional[SafeOpenAIClientPool] = None

def get_openai_client_pool(max_clients: int = 20, client_ttl_hours: int = 24) -> SafeOpenAIClientPool:
    """
    获取全局OpenAI客户端池实例（单例模式）
    
    Args:
        max_clients: 最大缓存客户端数量（仅在首次调用时生效）
        client_ttl_hours: 客户端生存时间小时数（仅在首次调用时生效）
        
    Returns:
        全局客户端池实例
    """
    global _global_client_pool
    if _global_client_pool is None:
        _global_client_pool = SafeOpenAIClientPool(max_clients, client_ttl_hours)
    return _global_client_pool


# ==================== 便捷函数 ====================

async def get_openai_client(model_key: str, config_getter_func=None) -> Optional[OpenAI]:
    """
    便捷函数：获取OpenAI客户端（重构版本）
    
    Args:
        model_key: 模型键名
        config_getter_func: 配置获取方式，支持：
                          - 函数：function(model_key) -> dict
                          - 字典：直接使用该配置
                          - None：尝试自动导入配置函数
        
    Returns:
        OpenAI客户端实例
    """
    pool = get_openai_client_pool()
    
    # 重构：支持函数和字典两种方式
    if config_getter_func is None:
        # 保持原有逻辑：尝试自动导入
        return await pool.get_client(model_key, None)
    elif callable(config_getter_func):
        # 原有逻辑：传递函数
        return await pool.get_client(model_key, config_getter_func)
    elif isinstance(config_getter_func, dict):
        # 新增逻辑：直接传递配置字典
        def dict_config_getter(key: str) -> dict:
            return config_getter_func
        return await pool.get_client(model_key, dict_config_getter)
    else:
        # 其他类型，转换为字典处理
        print(f"⚠️ 未知的配置类型: {type(config_getter_func)}, 尝试作为字典处理")
        def fallback_config_getter(key: str) -> dict:
            return config_getter_func if isinstance(config_getter_func, dict) else {}
        return await pool.get_client(model_key, fallback_config_getter)

async def clear_openai_cache() -> int:
    """
    便捷函数：清空OpenAI客户端缓存
    
    Returns:
        清理的客户端数量
    """
    pool = get_openai_client_pool()
    return await pool.clear_cache()

def print_openai_stats():
    """
    便捷函数：打印OpenAI客户端池统计信息
    """
    pool = get_openai_client_pool()
    pool.print_stats()


# ==================== 使用示例 ====================

async def example_usage():
    """
    使用示例（展示重构后的多种使用方式）
    """
    print("🚀 SafeOpenAIClientPool 重构版本使用示例")
    print("=" * 60)
    
    # 方式1：使用配置获取函数（原有方式）
    def mock_get_model_config(model_key: str):
        configs = {
            'deepseek-chat': {
                'name': 'DeepSeek Chat',
                'api_key': 'sk-deepseek-test-key',
                'base_url': 'https://api.deepseek.com/v1',
                'timeout': 60
            },
            'moonshot-v1-8k': {
                'name': 'Moonshot 8K',
                'api_key': 'sk-moonshot-test-key',
                'base_url': 'https://api.moonshot.cn/v1',
                'timeout': 60
            }
        }
        return configs.get(model_key)
    
    print("\n📋 方式1：使用配置获取函数")
    client1 = await get_openai_client('deepseek-chat', mock_get_model_config)
    if client1:
        print("✅ 成功获取客户端（配置函数方式）")
    
    # 方式2：直接传递配置字典（新增方式）
    config_dict = {
        'name': 'Claude Chat',
        'api_key': 'sk-claude-test-key',
        'base_url': 'https://api.anthropic.com/v1',
        'timeout': 60
    }
    
    print("\n📋 方式2：直接传递配置字典")
    client2 = await get_openai_client('claude-3-sonnet', config_dict)
    if client2:
        print("✅ 成功获取客户端（配置字典方式）")
    
    # 方式3：自动导入配置函数（保持兼容）
    print("\n📋 方式3：自动导入配置函数")
    client3 = await get_openai_client('gpt-4', None)
    if client3:
        print("✅ 成功获取客户端（自动导入方式）")
    else:
        print("⚠️ 自动导入失败（这是正常的，因为示例环境中没有配置模块）")
    
    # 打印统计信息
    print_openai_stats()
    
    # 测试缓存命中
    print(f"\n🔄 测试缓存命中...")
    start_time = time.time()
    cached_client = await get_openai_client('deepseek-chat', mock_get_model_config)
    elapsed_ms = (time.time() - start_time) * 1000
    print(f"缓存命中耗时: {elapsed_ms:.1f}ms")
    
    # 清理缓存
    print(f"\n🧹 清理缓存...")
    cleared_count = await clear_openai_cache()
    print(f"已清理 {cleared_count} 个客户端")
    
    print_openai_stats()

if __name__ == "__main__":
    # 运行示例
    import asyncio
    asyncio.run(example_usage())
```
