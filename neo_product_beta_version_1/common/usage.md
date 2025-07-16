# ExceptionHandler 使用指南

## 概述

ExceptionHandler 是一个线程安全的单例异常处理和日志记录模块，为 NiceGUI 应用提供统一的错误处理、日志记录和安全执行功能。

## 核心特性

- **线程安全的单例模式**：确保全局唯一实例
- **CSV 格式日志**：结构化存储，便于查询和分析
- **按日期分割**：每天自动创建新的日志文件
- **用户信息记录**：自动获取当前登录用户信息
- **精确代码定位**：记录模块、函数名和行号
- **自动清理**：定期清理超期的旧日志文件

## 日志文件结构

```
logs/
├── app_logs_2024-01-15.csv  # 今天的日志
├── app_logs_2024-01-14.csv  # 昨天的日志
├── app_logs_2024-01-13.csv  # 前天的日志
└── ...
```

### CSV 日志字段

| 字段           | 说明     | 示例                            |
| -------------- | -------- | ------------------------------- |
| timestamp      | 时间戳   | 2024-01-15T10:30:45.123456      |
| level          | 日志级别 | INFO/ERROR                      |
| user_id        | 用户 ID  | 1                               |
| username       | 用户名   | admin                           |
| module         | 模块名   | auth.pages.user_management_page |
| function       | 函数名   | load_users                      |
| line_number    | 行号     | 125                             |
| message        | 消息内容 | 用户列表加载成功                |
| exception_type | 异常类型 | ValueError                      |
| stack_trace    | 调用栈   | 完整的异常堆栈信息              |
| extra_data     | 额外数据 | {"count": 10}                   |

## 核心 API

### 1. log_info(message, extra_data=None)

记录信息日志，用于记录正常的业务操作。

```python
from common.exception_handler import log_info

# 基本使用
log_info("用户登录成功")

# 带额外数据
log_info("用户列表加载完成", extra_data='{"count": 10, "filter": "active"}')

# 实际应用示例
def user_login(username):
    log_info(f"用户尝试登录: {username}")
    # 登录逻辑...
    log_info(f"用户登录成功: {username}")
```

### 2. log_error(message, exception=None, extra_data=None)

记录错误日志，用于记录异常情况。

```python
from common.exception_handler import log_error

# 记录简单错误
log_error("用户验证失败")

# 记录异常对象
try:
    risky_operation()
except Exception as e:
    log_error("操作失败", exception=e)

# 带额外上下文信息
log_error("数据库连接失败", exception=e, extra_data='{"retry_count": 3}')
```

### 3. safe(func, \*args, \*\*kwargs)

万能安全执行函数，自动处理异常并记录日志。

```python
from common.exception_handler import safe

# 基本使用
def risky_function():
    raise ValueError("测试异常")

result = safe(risky_function, return_value="默认值")
print(result)  # 输出: 默认值

# 带参数的函数
def divide(a, b):
    return a / b

result = safe(divide, 10, 0, return_value=0, error_msg="除法计算失败")

# 完整参数示例
result = safe(
    func=some_function,           # 要执行的函数
    arg1, arg2,                   # 位置参数
    return_value=None,            # 异常时返回的默认值
    show_error=True,              # 是否显示UI错误提示
    error_msg="自定义错误消息",    # 自定义错误消息
    keyword_arg="value"           # 关键字参数
)
```

### 4. db_safe(operation_name="数据库操作")

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

# 复杂操作
def update_user_roles(user_id, role_names):
    try:
        with db_safe("更新用户角色") as db:
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                user.roles.clear()
                for role_name in role_names:
                    role = db.query(Role).filter(Role.name == role_name).first()
                    if role:
                        user.roles.append(role)
            # 自动提交
            return True
    except Exception as e:
        log_error(f"更新用户角色失败: {user_id}", exception=e)
        return False
```

### 5. @safe_protect(name=None, error_msg=None, return_on_error=None)

页面/函数保护装饰器，提供统一的异常处理和错误页面。

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
    # 复杂计算逻辑
    return {"count": 100, "total": 5000}

# 组合使用：页面级 + 认证装饰器
from auth.decorators import require_role

@require_role('admin')
@safe_protect(name="管理员页面", error_msg="管理页面加载失败")
def admin_page():
    # 管理员页面逻辑
    pass
```

## 实际应用场景

### 场景 1：用户管理功能

```python
from common.exception_handler import log_info, log_error, safe, db_safe, safe_protect
from auth.decorators import require_role

@require_role('admin')
@safe_protect(name="用户管理页面", error_msg="用户管理页面加载失败")
def user_management_page():
    log_info("用户管理页面开始加载")

    # 加载用户统计
    def load_statistics():
        with db_safe("获取用户统计") as db:
            total = db.query(User).count()
            active = db.query(User).filter(User.is_active == True).count()
            return total, active

    total, active = safe(load_statistics, return_value=(0, 0))

    # 创建用户
    def create_user(username, email, password):
        log_info(f"开始创建用户: {username}")
        try:
            with db_safe("创建新用户") as db:
                user = User(username=username, email=email)
                user.set_password(password)
                db.add(user)
                log_info(f"用户创建成功: {username}")
                return True
        except Exception as e:
            log_error(f"用户创建失败: {username}", exception=e)
            return False

    # UI 按钮事件
    ui.button('创建用户', on_click=lambda: safe(
        lambda: create_user("test", "test@example.com", "password"),
        error_msg="用户创建失败"
    ))
```

### 场景 2：数据导入功能

```python
@safe_protect(name="数据导入", error_msg="数据导入功能异常")
def import_data_page():
    log_info("数据导入页面加载")

    def process_csv_file(file_path):
        log_info(f"开始处理CSV文件: {file_path}")

        try:
            with db_safe("批量导入数据") as db:
                # 读取CSV
                import pandas as pd
                df = pd.read_csv(file_path)
                log_info(f"CSV文件读取成功，共{len(df)}行数据")

                # 批量插入
                for index, row in df.iterrows():
                    record = DataRecord(
                        name=row['name'],
                        value=row['value']
                    )
                    db.add(record)

                log_info(f"数据导入完成，共导入{len(df)}条记录")
                return len(df)

        except Exception as e:
            log_error("CSV文件处理失败", exception=e)
            raise

    def handle_file_upload(file):
        result = safe(
            process_csv_file,
            file.path,
            return_value=0,
            error_msg="文件处理失败，请检查文件格式"
        )

        if result > 0:
            ui.notify(f'成功导入 {result} 条记录', type='positive')
        else:
            ui.notify('导入失败', type='negative')
```

### 场景 3：API 调用

```python
def api_service():
    """API 服务类"""

    @safe_protect(name="API调用", return_on_error={})
    def call_external_api(endpoint, data):
        log_info(f"调用外部API: {endpoint}")

        try:
            import requests
            response = requests.post(endpoint, json=data, timeout=30)
            response.raise_for_status()

            result = response.json()
            log_info(f"API调用成功: {endpoint}")
            return result

        except requests.RequestException as e:
            log_error(f"API调用失败: {endpoint}", exception=e)
            raise

    def sync_user_data():
        """同步用户数据"""
        try:
            with db_safe("同步用户数据") as db:
                users = db.query(User).filter(User.need_sync == True).all()

                for user in users:
                    # 安全调用API
                    result = safe(
                        call_external_api,
                        "https://api.example.com/sync",
                        {"user_id": user.id, "username": user.username},
                        return_value=None,
                        show_error=False  # 不显示UI错误，只记录日志
                    )

                    if result:
                        user.need_sync = False
                        log_info(f"用户数据同步成功: {user.username}")
                    else:
                        log_error(f"用户数据同步失败: {user.username}")

        except Exception as e:
            log_error("批量同步用户数据失败", exception=e)
```

## 日志查询和管理

```python
from common.exception_handler import get_log_files, get_today_errors, cleanup_logs

# 获取最近7天的日志文件
log_files = get_log_files(7)
for log_file in log_files:
    print(f"日期: {log_file['date']}, 大小: {log_file['size']} bytes")

# 获取今天的错误日志
today_errors = get_today_errors(20)  # 最近20条错误
for error in today_errors:
    print(f"时间: {error['timestamp']}, 用户: {error['username']}, 错误: {error['message']}")

# 手动清理30天前的日志
cleanup_logs(30)
```

## 最佳实践

### 1. 日志记录原则

```python
# ✅ 好的做法
log_info("用户登录成功")                    # 简洁明确
log_info(f"加载用户列表完成，共{count}个用户") # 包含关键信息
log_error("数据库连接失败", exception=e)      # 记录异常对象

# ❌ 避免的做法
log_info("Something happened")              # 信息不明确
log_error("Error occurred")                 # 没有异常对象
log_info("Debug info: " + str(huge_data))  # 日志过于详细
```

### 2. 异常处理层次

```python
# 页面级保护
@safe_protect(name="用户页面")
def user_page():

    # 业务逻辑安全执行
    users = safe(load_users, return_value=[])

    # 数据库操作安全执行
    def create_user():
        with db_safe("创建用户") as db:
            # 数据库操作
            pass

    # UI事件安全执行
    ui.button('创建', on_click=lambda: safe(create_user))
```

### 3. 错误信息用户友好化

```python
# 为不同类型的操作提供友好的错误消息
error_messages = {
    'user_create': '用户创建失败，请检查输入信息',
    'data_import': '数据导入失败，请检查文件格式',
    'password_reset': '密码重置失败，请稍后重试',
    'email_send': '邮件发送失败，请检查网络连接'
}

def create_user():
    result = safe(
        do_create_user,
        error_msg=error_messages['user_create'],
        show_error=True
    )
```

### 4. 性能考虑

```python
# 对于高频操作，考虑是否需要详细日志
def high_frequency_operation():
    # 只在关键节点记录日志
    if critical_condition:
        log_info("关键操作执行")

    # 避免在循环中大量记录日志
    for item in large_list:
        # 不要在这里记录日志
        process_item(item)

    log_info(f"批量处理完成，共处理{len(large_list)}项")
```

## 故障排查

### 1. 查看今天的错误日志

```python
errors = get_today_errors(50)
for error in errors:
    print(f"[{error['timestamp']}] {error['username']}: {error['message']}")
    if error['exception_type']:
        print(f"异常类型: {error['exception_type']}")
        print(f"位置: {error['module']}.{error['function']}:{error['line_number']}")
```

### 2. 分析特定功能的日志

```bash
# 使用 CSV 工具查询特定模块的日志
grep "user_management" logs/app_logs_2024-01-15.csv
```

### 3. 监控异常趋势

```python
import pandas as pd

# 读取最近几天的日志，分析异常趋势
df = pd.read_csv('logs/app_logs_2024-01-15.csv')
error_df = df[df['level'] == 'ERROR']
error_counts = error_df.groupby('exception_type').size()
print("异常类型统计:", error_counts)
```

## 注意事项

1. **线程安全**：ExceptionHandler 是线程安全的，可以在多线程环境中使用
2. **性能影响**：每次日志写入都会进行文件操作，避免在高频循环中记录大量日志
3. **磁盘空间**：定期检查日志文件大小，必要时调整保留天数
4. **敏感信息**：避免在日志中记录密码、令牌等敏感信息
5. **异常传播**：`db_safe` 会重新抛出异常，确保上层代码能够处理

通过合理使用 ExceptionHandler，可以大大提高应用的稳定性和可维护性，同时提供完整的操作审计日志。
