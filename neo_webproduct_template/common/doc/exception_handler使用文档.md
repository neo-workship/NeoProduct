# ExceptionHandler 完整使用指南

## 概述

`exception_handler.py` 是 NiceGUI 应用程序的核心异常处理和日志记录模块，提供了应用级别的统一异常处理机制。它采用线程安全的单例模式设计，确保在整个应用生命周期中提供一致的错误处理和日志记录服务。

## 🚀 核心功能特性

### 1. 线程安全的单例模式

- 全局唯一实例，确保所有模块使用同一个异常处理器
- 线程安全设计，支持多线程环境下的并发访问

### 2. 结构化 CSV 日志记录

- 按日期自动分割日志文件（`app_logs_YYYY-MM-DD.csv`）
- 包含完整的上下文信息：用户、模块、函数、行号、异常堆栈
- 便于后续分析和故障排查

### 3. 自动用户上下文获取

- 自动获取当前登录用户信息
- 记录用户 ID 和用户名，便于追踪操作来源

### 4. 精确的调用栈定位

- 自动获取调用者模块、函数名和行号
- 完整的异常堆栈跟踪信息

### 5. 自动日志清理

- 定期清理超期的旧日志文件
- 可配置保留天数（默认 30 天）

## 📊 日志文件结构

### 日志目录结构

```
logs/
├── app_logs_2025-07-17.csv  # 今天的日志
├── app_logs_2025-07-16.csv  # 昨天的日志
├── app_logs_2025-07-15.csv  # 前天的日志
└── ...                      # 更早的日志
```

### CSV 字段说明

| 字段             | 说明       | 示例                         |
| ---------------- | ---------- | ---------------------------- |
| `timestamp`      | 记录时间戳 | `2025-07-17T10:30:45.123456` |
| `level`          | 日志级别   | `INFO` / `ERROR`             |
| `user_id`        | 用户 ID    | `1`                          |
| `username`       | 用户名     | `admin`                      |
| `module`         | 调用模块   | `menu_pages.dashboard_page`  |
| `function`       | 调用函数   | `dashboard_page_content`     |
| `line_number`    | 行号       | `125`                        |
| `message`        | 日志消息   | `仪表板数据加载成功`         |
| `exception_type` | 异常类型   | `ValueError`                 |
| `stack_trace`    | 异常堆栈   | 完整的异常追踪信息           |
| `extra_data`     | 额外数据   | `{"count": 10}`              |

## 🔧 核心 API 接口

### 1. `log_info(message, extra_data=None)`

记录信息级别的日志，用于追踪正常的业务操作。

```python
from common.exception_handler import log_info

# 基本使用
log_info("用户登录成功")

# 带额外数据
log_info("数据加载完成", extra_data='{"count": 100, "time_cost": "2.5s"}')

# 实际应用示例
def load_dashboard_data():
    log_info("开始加载仪表板数据")
    # 数据加载逻辑...
    log_info("仪表板数据加载完成", extra_data='{"widgets": 8}')
```

### 2. `log_error(message, exception=None, extra_data=None)`

记录错误级别的日志，用于记录异常情况和错误信息。

```python
from common.exception_handler import log_error

# 记录简单错误
log_error("用户验证失败")

# 记录异常对象
try:
    risky_operation()
except Exception as e:
    log_error("操作执行失败", exception=e)

# 带上下文信息
log_error("数据库连接失败", exception=e,
          extra_data='{"host": "localhost", "retry_count": 3}')
```

### 3. `safe(func, *args, **kwargs)`

万能安全执行函数，自动捕获异常并记录日志，确保程序稳定性。

```python
from common.exception_handler import safe

# 基本使用
def risky_function():
    raise ValueError("测试异常")

result = safe(risky_function, return_value="默认值")
print(result)  # 输出: 默认值

# 带参数的函数调用
def divide(a, b):
    return a / b

result = safe(divide, 10, 0, return_value=0, error_msg="除法计算失败")

# 完整参数示例
result = safe(
    func=some_function,           # 要执行的函数
    arg1, arg2,                   # 位置参数
    return_value=None,            # 异常时返回的默认值
    show_error=True,              # 是否显示UI错误提示
    error_msg="自定义错误消息",     # 自定义错误消息
    keyword_arg="value"           # 关键字参数
)
```

### 4. `db_safe(operation_name="数据库操作")`

数据库操作安全上下文管理器，自动处理事务和异常。

```python
from common.exception_handler import db_safe

# 基本使用
try:
    with db_safe("创建用户") as db:
        user = User(username="test", email="test@example.com")
        db.add(user)
        # 自动提交，异常时自动回滚
except Exception as e:
    print(f"操作失败: {e}")

# 查询操作
def get_user_list():
    try:
        with db_safe("获取用户列表") as db:
            users = db.query(User).all()
            return users
    except Exception:
        return []  # 异常时返回空列表
```

### 5. `@safe_protect(name=None, error_msg=None, return_on_error=None)`

页面/函数保护装饰器，提供统一的异常处理和错误页面显示。

```python
from common.exception_handler import safe_protect

# 基本页面保护
@safe_protect(name="用户管理页面")
def user_management_page():
    # 页面逻辑
    pass

# 带自定义错误消息
@safe_protect(
    name="数据分析页面",
    error_msg="数据分析功能暂时不可用，请稍后重试"
)
def analysis_page():
    # 可能出错的页面逻辑
    pass

# 函数保护（带返回值）
@safe_protect(
    name="计算统计数据",
    error_msg="统计计算失败",
    return_on_error={"count": 0, "total": 0}
)
def calculate_statistics():
    return {"count": 100, "total": 5000}
```

## 🏗️ 在页面中的具体使用

### 在 header_pages 中使用

#### 示例：搜索页面（search_page.py）

```python
from nicegui import ui
from common.exception_handler import log_info, log_error, safe, safe_protect

@safe_protect(name="搜索页面", error_msg="搜索页面加载失败")
def search_page_content():
    log_info("搜索页面开始加载")

    with ui.column().classes('w-full p-6'):
        ui.label('全局搜索').classes('text-2xl font-bold mb-4')

        # 搜索功能
        def perform_search(query):
            log_info(f"执行搜索操作", extra_data=f'{{"query": "{query}"}}')
            try:
                # 搜索逻辑
                results = safe(do_search, query, return_value=[],
                             error_msg="搜索执行失败")
                log_info("搜索完成", extra_data=f'{{"result_count": {len(results)}}}')
                return results
            except Exception as e:
                log_error("搜索异常", exception=e)
                return []

        search_input = ui.input('请输入搜索关键词').classes('w-full')
        ui.button('搜索', on_click=lambda: perform_search(search_input.value))
```

#### 示例：消息页面（messages_page.py）

```python
from nicegui import ui
from common.exception_handler import log_info, log_error, db_safe, safe_protect

@safe_protect(name="消息中心", error_msg="消息页面加载失败")
def messages_page_content():
    log_info("消息中心页面开始加载")

    # 获取消息列表
    def load_messages():
        try:
            with db_safe("获取用户消息") as db:
                messages = db.query(Message).filter(
                    Message.user_id == current_user.id
                ).order_by(Message.created_at.desc()).all()
                log_info("消息列表加载成功",
                        extra_data=f'{{"message_count": {len(messages)}}}')
                return messages
        except Exception as e:
            log_error("消息加载失败", exception=e)
            return []

    messages = load_messages()

    with ui.column().classes('w-full p-6'):
        ui.label('消息中心').classes('text-2xl font-bold mb-4')

        for message in messages:
            with ui.card().classes('w-full mb-2'):
                ui.label(message.title).classes('font-bold')
                ui.label(message.content)
```

### 在 menu_pages 中使用

#### 示例：仪表板页面（dashboard_page.py）

```python
from nicegui import ui
from common.exception_handler import log_info, log_error, safe, db_safe, safe_protect

@safe_protect(name="仪表板", error_msg="仪表板加载失败")
def dashboard_page_content():
    log_info("仪表板页面开始加载")

    # 加载统计数据
    def load_statistics():
        try:
            with db_safe("获取仪表板统计数据") as db:
                stats = {
                    'total_users': db.query(User).count(),
                    'active_users': db.query(User).filter(User.is_active == True).count(),
                    'total_orders': db.query(Order).count(),
                    'today_revenue': calculate_today_revenue(db)
                }
                log_info("统计数据加载成功", extra_data=str(stats))
                return stats
        except Exception as e:
            log_error("统计数据加载失败", exception=e)
            return {}

    # 安全执行数据加载
    stats = safe(load_statistics, return_value={})

    with ui.column().classes('w-full p-6'):
        ui.label('数据仪表板').classes('text-3xl font-bold mb-6')

        # 统计卡片
        with ui.row().classes('w-full gap-4 mb-6'):
            create_stat_card("总用户数", stats.get('total_users', 0), 'people')
            create_stat_card("活跃用户", stats.get('active_users', 0), 'person')
            create_stat_card("总订单数", stats.get('total_orders', 0), 'shopping_cart')
            create_stat_card("今日收入", f"¥{stats.get('today_revenue', 0)}", 'attach_money')

def create_stat_card(title, value, icon):
    """创建统计卡片"""
    with ui.card().classes('p-4 min-w-48'):
        with ui.row().classes('items-center justify-between'):
            with ui.column():
                ui.label(title).classes('text-gray-600 text-sm')
                ui.label(str(value)).classes('text-2xl font-bold')
            ui.icon(icon).classes('text-3xl text-blue-500')
```

#### 示例：数据管理页面（data_page.py）

```python
from nicegui import ui
from common.exception_handler import log_info, log_error, safe, db_safe, safe_protect

@safe_protect(name="数据管理", error_msg="数据管理页面加载失败")
def data_page_content():
    log_info("数据管理页面开始加载")

    # 数据导入功能
    async def handle_data_import(file):
        log_info(f"开始数据导入", extra_data=f'{{"filename": "{file.name}"}}')

        try:
            # 安全执行文件处理
            result = safe(
                process_import_file,
                file,
                return_value={"success": False, "message": "导入失败"},
                error_msg="文件处理失败"
            )

            if result["success"]:
                log_info("数据导入成功", extra_data=str(result))
                ui.notify("数据导入成功", type='positive')
            else:
                log_error("数据导入失败", extra_data=str(result))
                ui.notify(result["message"], type='negative')

        except Exception as e:
            log_error("数据导入异常", exception=e)
            ui.notify("数据导入失败", type='negative')

    # 数据查询功能
    def load_data_list(page=1, size=20):
        try:
            with db_safe("查询数据列表") as db:
                offset = (page - 1) * size
                data_list = db.query(DataModel).offset(offset).limit(size).all()
                total = db.query(DataModel).count()

                log_info("数据列表查询成功",
                        extra_data=f'{{"page": {page}, "size": {size}, "total": {total}}}')
                return data_list, total
        except Exception as e:
            log_error("数据查询失败", exception=e)
            return [], 0

    with ui.column().classes('w-full p-6'):
        ui.label('数据管理').classes('text-3xl font-bold mb-6')

        # 文件上传
        ui.upload(on_upload=handle_data_import).classes('mb-4')

        # 数据列表
        data_list, total = load_data_list()

        with ui.table(columns=[
            {'name': 'id', 'label': 'ID', 'field': 'id'},
            {'name': 'name', 'label': '名称', 'field': 'name'},
            {'name': 'created_at', 'label': '创建时间', 'field': 'created_at'}
        ], rows=data_list).classes('w-full'):
            pass
```

## 🔍 日志查询和分析工具

### 查看今天的错误日志

```python
from common.exception_handler import get_today_errors

# 获取今天的错误日志
errors = get_today_errors(50)
for error in errors:
    print(f"[{error['timestamp']}] {error['username']}: {error['message']}")
    if error['exception_type']:
        print(f"异常类型: {error['exception_type']}")
        print(f"位置: {error['module']}.{error['function']}:{error['line_number']}")
```

### 获取日志文件列表

```python
from common.exception_handler import get_log_files

# 获取最近7天的日志文件
log_files = get_log_files(7)
for log_file in log_files:
    print(f"日期: {log_file['date']}, 大小: {log_file['size']} bytes")
```

### 手动清理旧日志

```python
from common.exception_handler import cleanup_logs

# 清理30天前的日志
cleanup_logs(days_to_keep=30)
```

## 🎯 最佳实践建议

### 1. 合理使用日志级别

```python
# ✅ 正确使用
log_info("用户登录成功")  # 正常业务操作
log_error("数据库连接失败", exception=e)  # 异常情况

# ❌ 避免过度使用
# 不要在循环中大量记录日志
for i in range(1000):
    log_info(f"处理第{i}项")  # 会产生大量日志
```

### 2. 装饰器使用策略

```python
# ✅ 页面级保护
@safe_protect(name="用户管理页面", error_msg="页面加载失败")
def user_management_page():
    pass

# ✅ 关键函数保护
@safe_protect(name="支付处理", error_msg="支付处理失败", return_on_error=False)
def process_payment(amount):
    pass

# ❌ 避免过度使用装饰器
@safe_protect()  # 不必要的保护
def simple_getter():
    return self.value
```

### 3. 异常信息优化

```python
# ✅ 提供有用的上下文信息
log_error(f"用户 {user_id} 权限验证失败",
          exception=e,
          extra_data=f'{{"required_role": "admin", "user_role": "user"}}')

# ❌ 信息不足
log_error("验证失败")
```

### 4. 数据库操作最佳实践

```python
# ✅ 使用 db_safe 确保事务安全
def create_user_with_profile(user_data, profile_data):
    try:
        with db_safe("创建用户和档案") as db:
            user = User(**user_data)
            db.add(user)
            db.flush()  # 获取用户ID

            profile = UserProfile(user_id=user.id, **profile_data)
            db.add(profile)
            # 自动提交事务
            return True
    except Exception:
        return False
```

## ⚠️ 注意事项

1. **线程安全性**：ExceptionHandler 是线程安全的，可在多线程环境中使用
2. **性能考虑**：避免在高频循环中记录大量日志
3. **磁盘空间管理**：定期检查日志目录大小，必要时调整保留天数
4. **敏感信息保护**：避免在日志中记录密码、令牌等敏感信息
5. **异常传播**：`db_safe` 会重新抛出异常，确保上层代码能够适当处理

## 🚀 总结

`exception_handler.py` 是整个 NiceGUI 应用的核心基础设施，提供了：

- **统一的异常处理机制**：确保应用稳定性
- **完整的操作审计日志**：便于问题追踪和分析
- **用户友好的错误提示**：提升用户体验
- **开发人员友好的调试信息**：加速问题定位

通过合理使用这个模块，可以大大提高应用的健壮性、可维护性和用户体验。建议在所有页面逻辑和关键业务函数中都使用相应的异常处理机制。
