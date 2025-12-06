# log_handler.py 功能清单

## 1. 装饰器类

### @safe_protect - 页面/函数保护装饰器

```py
@safe_protect(name="页面名称", error_msg="自定义错误信息", return_on_error=None)
def your_function():
    # 可能出错的代码
    pass
```

- 使用场景:
  ✅ 保护 NiceGUI 页面函数,防止页面崩溃
  ✅ 需要在 UI 上显示友好错误提示的场景
  ✅ 需要在出错时返回特定值的场景
  ✅ 自动显示错误页面,提供"重新加载"和"返回首页"按钮
- 特点:
  ✅ 自动捕获异常并记录日志
  ✅ 在 UI 上显示错误通知
  ✅ 可以自定义错误消息
  ✅ 出错时返回指定的默认值

### @catch - Loguru 异常捕获装饰器

```py
@catch(message="自定义错误信息", show_ui_error=True)
def your_function():
    # 可能出错的代码
    pass
```

- 使用场景:
  ✅ 需要记录详细异常堆栈的场景
  ✅ 不需要自定义错误页面,只需要日志记录
  ✅ 可选择是否在 UI 上显示错误通知
- 特点:
  ✅ 基于 Loguru 的异常捕获
  ✅ 自动记录完整的异常堆栈
  ✅ 可配置是否显示 UI 错误通知

## 2. 日志记录函数

- 按级别分类的日志函数:

```py
# 1. 追踪日志 - 最详细的调试信息
log_trace(message: str, extra_data: Optional[str] = None)
# 2. 调试日志 - 开发时的调试信息
log_debug(message: str, extra_data: Optional[str] = None)
# 3. 信息日志 - 普通运行信息(最常用)
log_info(message: str, extra_data: Optional[str] = None)
# 4. 成功日志 - 标记成功操作
log_success(message: str, extra_data: Optional[str] = None)
# 5. 警告日志 - 需要注意的情况
log_warning(message: str, extra_data: Optional[str] = None)
# 6. 错误日志 - 错误但不影响运行
log_error(message: str, exception: Optional[Exception] = None,
          extra_data: Optional[str] = None)
# 7. 严重错误日志 - 严重错误
log_critical(message: str, exception: Optional[Exception] = None,
             extra_data: Optional[str] = None)
```

- 使用场景对比:
  | 函数 | 使用场景 | 示例 |
  |--------------|------------------------------|------|
  | log_trace | 非常详细的执行路径追踪 | 追踪函数调用顺序 |
  | log_debug | 开发调试，变量值输出 | 记录中间计算结果 |
  | log_info | 正常业务流程记录 | 用户登录成功 |
  | log_success | 重要操作成功标记 | 配置更新成功 |
  | log_warning | 需注意但不影响运行 | 配置文件缺失，使用默认值 |
  | log_error | 捕获的错误但不中断 | API 调用失败，将重试 |
  | log_critical | 严重错误，可能需要人工介入 | 数据库连接失败 |

## 3. 安全执行函数

### safe() - 万能安全执行函数

```py
result = safe(
    func,                    # 要执行的函数
    *args,                   # 位置参数
    return_value=None,       # 出错时的返回值
    show_error=True,         # 是否显示错误UI
    error_msg=None,          # 自定义错误消息
    **kwargs                 # 关键字参数
)
```

- 使用场景:
  ✅ 调用第三方 API 可能失败
  ✅ 执行可能抛出异常的操作
  ✅ 需要在失败时返回默认值

- 示例

```py
# API调用
result = safe(call_external_api,
              return_value={"status": "error"},
              error_msg="API调用失败")
# 文件操作
data = safe(read_config_file,
            'config.yaml',
            return_value={},
            show_error=False)
```

### db_safe() - 数据库操作安全上下文

```py
with db_safe(operation_name="数据库操作名称") as db:
    # 执行数据库操作
    user = db.query(User).filter_by(id=1).first()
```

- 使用场景:
  ✅ 所有数据库 CRUD 操作
  ✅ 需要事务管理的场景
  ✅ 需要自动回滚的场景
- 特点:
  ✅ 自动捕获数据库异常
  ✅ 自动记录操作日志
  ✅ 异常时自动回滚

## 4. Logger 实例获取

- get_logger() - 获取绑定用户上下文的 logger

```py
log = get_logger("模块名称")
log.info("这是一条信息")
log.error("这是一条错误")
```

- 使用场景:
  ✅ 需要在类或模块中多次记录日志
  ✅ 需要自定义模块名称
  ✅ 需要更灵活的日志控制
- 特点:
  ✅ 自动绑定用户上下文(用户名、IP 等)
  ✅ 支持链式调用
  ✅ 支持 Loguru 的所有高级特性

## 5. 日志查询工具

```py
# 1. 获取最近N天的日志文件列表
files = get_log_files(days=7)
# 2. 获取今天的错误日志
errors = get_today_errors(limit=50)
# 3. 按级别获取今天的日志
logs = get_today_logs_by_level(level="INFO", limit=100)
# 4. 获取日志统计信息
stats = get_log_statistics(days=7)
# 5. 获取日志文件夹信息
folder_info = get_log_folder_info()
# 6. 手动清理旧日志
cleanup_logs(days_to_keep=30)
```
