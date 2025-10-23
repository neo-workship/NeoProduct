"""
优化的异常处理和日志模块 - 单例模式（线程安全）
提供统一的日志记录、异常处理和安全执行功能
"""
import csv
import asyncio
import threading
import functools
import traceback
import inspect
from typing import Callable, Any, Optional, Dict
from datetime import datetime
from pathlib import Path
from contextlib import contextmanager
from nicegui import ui


class ExceptionHandler:
    """线程安全的单例异常处理器"""
    
    _instance = None
    _lock = threading.Lock()
    _async_lock = asyncio.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        # 配置参数
        self.log_dir = Path('logs')
        self.max_stack_depth = 10  # 限制调用栈深度
        self.max_log_days = 30     # 保留日志天数
        
        # 创建日志目录
        self.log_dir.mkdir(exist_ok=True)
        
        # 线程锁
        self._file_lock = threading.Lock()
        
        # 清理旧日志文件
        self._cleanup_old_logs()
        
        self._initialized = True
    
    def _get_today_log_file(self) -> Path:
        """获取今天的日志文件路径"""
        today = datetime.now().strftime('%Y-%m-%d')
        return self.log_dir / f'app_logs_{today}.csv'
    
    def _init_csv_log(self, log_file: Path):
        """初始化CSV日志文件"""
        if not log_file.exists():
            with open(log_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'timestamp',      # 时间戳
                    'level',          # 日志级别 (INFO/ERROR)
                    'user_id',        # 用户ID
                    'username',       # 用户名
                    'module',         # 模块名
                    'function',       # 函数名
                    'line_number',    # 行号
                    'message',        # 消息内容
                    'exception_type', # 异常类型
                    'stack_trace',    # 调用栈
                    'extra_data'      # 额外数据（JSON格式）
                ])
    
    def _cleanup_old_logs(self):
        """清理超过保留期的旧日志文件"""
        try:
            from datetime import timedelta
            cutoff_date = datetime.now() - timedelta(days=self.max_log_days)
            
            for log_file in self.log_dir.glob('app_logs_*.csv'):
                try:
                    # 从文件名提取日期 app_logs_2024-01-15.csv
                    filename = log_file.stem  # app_logs_2024-01-15
                    date_part = filename.split('_')[-1]  # 2024-01-15
                    file_date = datetime.strptime(date_part, '%Y-%m-%d')
                    
                    if file_date < cutoff_date:
                        log_file.unlink()
                        print(f"✅ 已删除旧日志文件: {log_file.name}")
                        
                except (ValueError, IndexError) as e:
                    # 文件名格式不正确，跳过
                    print(f"⚠️  跳过格式异常的日志文件: {log_file.name}")
                    continue
                    
        except Exception as e:
            print(f"❌ 清理旧日志文件失败: {e}")
    
    def _get_current_user(self) -> Dict[str, Any]:
        """获取当前用户信息"""
        try:
            from auth.session_manager import session_manager
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
    
    def _get_caller_info(self, skip_frames: int = 2) -> Dict[str, Any]:
        """获取调用者信息"""
        try:
            frame = inspect.currentframe()
            # 跳过指定数量的帧
            for _ in range(skip_frames):
                frame = frame.f_back if frame else None
            
            if frame:
                return {
                    'module': frame.f_globals.get('__name__', 'unknown'),
                    'function': frame.f_code.co_name,
                    'line_number': frame.f_lineno
                }
        except Exception:
            pass
        
        return {
            'module': 'unknown',
            'function': 'unknown', 
            'line_number': 0
        }
    
    def _get_stack_trace(self, exception: Optional[Exception] = None, limit: int = None) -> str:
        """获取调用栈信息"""
        try:
            if exception:
                # 异常的堆栈跟踪
                tb_lines = traceback.format_exception(
                    type(exception), exception, exception.__traceback__,
                    limit=limit or self.max_stack_depth
                )
            else:
                # 当前调用栈
                tb_lines = traceback.format_stack(limit=limit or self.max_stack_depth)
            
            return ''.join(tb_lines).strip()
        except Exception:
            return 'Stack trace unavailable'
    
    def _write_log(self, level: str, message: str, exception: Optional[Exception] = None, 
                   extra_data: Optional[str] = None, skip_frames: int = 3):
        """写入日志到CSV文件（线程安全）"""
        try:
            with self._file_lock:
                # 获取今天的日志文件
                log_file = self._get_today_log_file()
                
                # 如果文件不存在则初始化
                if not log_file.exists():
                    self._init_csv_log(log_file)
                
                user_info = self._get_current_user()
                caller_info = self._get_caller_info(skip_frames)
                
                # 准备日志数据
                log_data = [
                    datetime.now().isoformat(),
                    level,
                    user_info['user_id'],
                    user_info['username'],
                    caller_info['module'],
                    caller_info['function'],
                    caller_info['line_number'],
                    message,
                    type(exception).__name__ if exception else '',
                    self._get_stack_trace(exception) if exception else '',
                    extra_data or ''
                ]
                
                # 写入CSV
                with open(log_file, 'a', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(log_data)
                    
        except Exception as e:
            # 备用日志记录（避免日志系统本身出错）
            print(f"[{datetime.now()}] 日志写入失败: {e}")
            print(f"[{datetime.now()}] 原始消息: {message}")
    
    def log_info(self, message: str, extra_data: Optional[str] = None):
        """记录信息日志"""
        self._write_log('INFO', message, extra_data=extra_data, skip_frames=2)
    
    def log_error(self, message: str, exception: Optional[Exception] = None, 
                  extra_data: Optional[str] = None):
        """记录错误日志"""
        self._write_log('ERROR', message, exception, extra_data, skip_frames=2)
    
    def safe(self, func: Callable, *args, return_value: Any = None, 
             show_error: bool = True, error_msg: str = None, **kwargs) -> Any:
        """万能安全执行函数"""
        try:
            self.log_info(f"开始执行函数: {func.__name__}")
            result = func(*args, **kwargs)
            self.log_info(f"函数执行成功: {func.__name__}")
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
        """数据库操作安全上下文管理器"""
        self.log_info(f"开始{operation_name}")
        
        try:
            from auth.database import get_db
            
            with get_db() as db:
                yield db
                self.log_info(f"{operation_name}成功")
                
        except Exception as e:
            error_msg = f"{operation_name}失败: {str(e)}"
            self.log_error(error_msg, exception=e)
            
            try:
                ui.notify(error_msg, type='negative', timeout=5000)
            except Exception:
                print(f"错误提示显示失败: {error_msg}")
            
            raise  # 重新抛出异常让调用者处理
    
    def safe_protect(self, name: str = None, error_msg: str = None, 
                     return_on_error: Any = None):
        """页面/函数保护装饰器"""
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                func_name = name or func.__name__
                
                try:
                    self.log_info(f"开始执行保护函数: {func_name}")
                    result = func(*args, **kwargs)
                    self.log_info(f"保护函数执行成功: {func_name}")
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
                        # 如果UI显示失败，只记录错误
                        print(f"错误页面显示失败: {error_message}")
                    
                    return return_on_error
                    
            return wrapper
        return decorator

# 全局单例实例
_exception_handler = None
_handler_lock = threading.Lock()

def get_exception_handler() -> ExceptionHandler:
    """获取异常处理器单例（线程安全）"""
    global _exception_handler
    if _exception_handler is None:
        with _handler_lock:
            if _exception_handler is None:
                _exception_handler = ExceptionHandler()
    return _exception_handler

# 对外暴露的5个核心函数
def log_info(message: str, extra_data: Optional[str] = None):
    """记录信息日志"""
    handler = get_exception_handler()
    handler.log_info(message, extra_data)

def log_error(message: str, exception: Optional[Exception] = None, 
              extra_data: Optional[str] = None):
    """记录错误日志"""
    handler = get_exception_handler()
    handler.log_error(message, exception, extra_data)

def safe(func: Callable, *args, return_value: Any = None, 
         show_error: bool = True, error_msg: str = None, **kwargs) -> Any:
    """万能安全执行函数"""
    handler = get_exception_handler()
    return handler.safe(func, *args, return_value=return_value, 
                       show_error=show_error, error_msg=error_msg, **kwargs)

@contextmanager
def db_safe(operation_name: str = "数据库操作"):
    """数据库操作安全上下文管理器"""
    handler = get_exception_handler()
    with handler.db_safe(operation_name) as db:
        yield db

def safe_protect(name: str = None, error_msg: str = None, return_on_error: Any = None):
    """页面/函数保护装饰器"""
    handler = get_exception_handler()
    return handler.safe_protect(name, error_msg, return_on_error)

# =============================================================================
# 日志查询和管理工具函数
# =============================================================================

def get_log_files(days: int = 7) -> list:
    """获取最近几天的日志文件列表"""
    handler = get_exception_handler()
    log_files = []
    
    from datetime import timedelta
    for i in range(days):
        date = datetime.now() - timedelta(days=i)
        date_str = date.strftime('%Y-%m-%d')
        log_file = handler.log_dir / f'app_logs_{date_str}.csv'
        if log_file.exists():
            log_files.append({
                'date': date_str,
                'file_path': log_file,
                'size': log_file.stat().st_size
            })
    
    return log_files

def get_today_errors(limit: int = 50) -> list:
    """获取今天的错误日志"""
    handler = get_exception_handler()
    log_file = handler._get_today_log_file()
    
    if not log_file.exists():
        return []
    
    try:
        errors = []
        with open(log_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['level'] == 'ERROR':
                    errors.append(row)
        
        # 返回最近的错误（最后limit条）
        return errors[-limit:] if len(errors) > limit else errors
        
    except Exception as e:
        print(f"读取错误日志失败: {e}")
        return []

def cleanup_logs(days_to_keep: int = 30):
    """手动清理旧日志文件"""
    handler = get_exception_handler()
    handler.max_log_days = days_to_keep
    handler._cleanup_old_logs()

# =============================================================================
# 使用示例和测试
# =============================================================================

if __name__ == "__main__":
    # 使用示例
    
    # 1. 记录信息日志
    log_info("应用启动", extra_data='{"version": "1.0.0"}')
    
    # 2. 安全执行函数
    def risky_function():
        raise ValueError("测试异常")
    
    result = safe(risky_function, return_value="默认值")
    print(f"安全执行结果: {result}")
    
    # 3. 数据库安全操作
    try:
        with db_safe("测试数据库操作") as db:
            # 执行数据库操作
            pass
    except Exception as e:
        print(f"数据库操作异常: {e}")
    
    # 4. 页面保护装饰器
    @safe_protect(name="测试页面", error_msg="页面加载失败")
    def test_page():
        raise RuntimeError("页面异常")
    
    test_page()
    
    # 5. 查看日志文件
    log_files = get_log_files(3)
    print(f"最近3天的日志文件: {[f['date'] for f in log_files]}")
    
    # 6. 查看今天的错误
    today_errors = get_today_errors(10)
    print(f"今天的错误数量: {len(today_errors)}")
    
    print("✅ 异常处理模块测试完成")