## 测试代码

```py
"""
log_handler.py 功能测试页面
全面测试所有日志功能,包括装饰器、日志级别、安全执行等
"""
from nicegui import ui
from datetime import datetime

# 导入 log_handler 所有功能
from common.log_handler import (
    # 日志记录函数
    log_trace, log_debug, log_info, log_success,
    log_warning, log_error, log_critical,

    # 安全执行
    safe, db_safe,

    # 装饰器
    page_protect, catch,

    # Logger 实例
    get_logger,

    # 日志查询
    get_log_files, get_today_errors, get_today_logs_by_level,
    get_log_statistics, cleanup_logs
)

def other_page_content():
    """log_handler 测试页面内容"""

    # 页面标题
    with ui.column().classes('w-full mb-6'):
        ui.label('日志系统测试中心').classes('text-4xl font-bold text-blue-800 dark:text-blue-200 mb-2')
        ui.label('全面测试 log_handler.py 的所有功能').classes('text-lg text-gray-600 dark:text-gray-400')

    # 测试结果显示容器
    result_container = ui.column().classes('w-full')

    # ======================== 第一部分: 日志级别测试 ========================
    with ui.card().classes('w-full p-6 mb-4'):
        ui.label('1️⃣ 日志级别测试 (7个级别)').classes('text-2xl font-bold mb-4')

        with ui.row().classes('w-full gap-2 flex-wrap'):
            def test_log_levels():
                """测试所有7个日志级别"""
                result_container.clear()
                with result_container:
                    ui.label('🧪 测试所有日志级别...').classes('text-lg font-semibold mb-2')

                    # 测试每个级别
                    log_trace("这是 TRACE 级别日志 - 最详细的调试信息")
                    ui.label('✅ TRACE: 已记录').classes('text-gray-600')

                    log_debug("这是 DEBUG 级别日志 - 开发调试信息",
                             extra_data='{"function": "test_log_levels", "line": 45}')
                    ui.label('✅ DEBUG: 已记录 (带额外数据)').classes('text-gray-600')

                    log_info("这是 INFO 级别日志 - 普通运行信息")
                    ui.label('✅ INFO: 已记录').classes('text-blue-600')

                    log_success("这是 SUCCESS 级别日志 - 操作成功标记")
                    ui.label('✅ SUCCESS: 已记录').classes('text-green-600')

                    log_warning("这是 WARNING 级别日志 - 需要注意的情况")
                    ui.label('✅ WARNING: 已记录').classes('text-orange-600')

                    try:
                        raise ValueError("模拟的错误异常")
                    except Exception as e:
                        log_error("这是 ERROR 级别日志 - 捕获的错误", exception=e)
                        ui.label('✅ ERROR: 已记录 (带异常堆栈)').classes('text-red-600')

                    try:
                        raise RuntimeError("模拟的严重错误")
                    except Exception as e:
                        log_critical("这是 CRITICAL 级别日志 - 严重错误", exception=e,
                                   extra_data='{"severity": "high", "action": "alert_admin"}')
                        ui.label('✅ CRITICAL: 已记录 (带异常和额外数据)').classes('text-red-800 font-bold')

                    ui.separator()
                    ui.label('📁 查看日志文件: logs/[今天日期]/app_logs.csv').classes('text-sm text-gray-500 mt-2')
                    ui.notify('所有日志级别测试完成!', type='positive')

            ui.button('测试所有日志级别', on_click=test_log_levels, icon='bug_report').classes('bg-blue-500')

    # ======================== 第二部分: safe() 函数测试 ========================
    with ui.card().classes('w-full p-6 mb-4'):
        ui.label('2️⃣ safe() 安全执行测试').classes('text-2xl font-bold mb-4')

        with ui.row().classes('w-full gap-2 flex-wrap'):
            def test_safe_success():
                """测试 safe() 成功场景"""
                result_container.clear()
                with result_container:
                    ui.label('🧪 测试 safe() 成功场景...').classes('text-lg font-semibold mb-2')

                    def normal_function(a, b):
                        result = a + b
                        log_info(f"计算结果: {a} + {b} = {result}")
                        return result

                    result = safe(normal_function, 10, 20)
                    ui.label(f'✅ 函数正常执行: 10 + 20 = {result}').classes('text-green-600 text-lg')
                    ui.notify('Safe 执行成功!', type='positive')

            def test_safe_error():
                """测试 safe() 错误场景"""
                result_container.clear()
                with result_container:
                    ui.label('🧪 测试 safe() 错误场景...').classes('text-lg font-semibold mb-2')

                    def error_function():
                        raise ValueError("这是一个模拟的错误")

                    result = safe(
                        error_function,
                        return_value="默认返回值",
                        show_error=True,
                        error_msg="函数执行失败,已返回默认值"
                    )
                    # error_function()
                    # result = "默认值"
                    ui.label(f'✅ 错误已捕获,返回默认值: "{result}"').classes('text-orange-600 text-lg')
                    ui.label('📝 错误已记录到日志,UI已显示通知').classes('text-sm text-gray-500')

            def test_safe_with_kwargs():
                """测试 safe() 带关键字参数"""
                result_container.clear()
                with result_container:
                    ui.label('🧪 测试 safe() 带参数...').classes('text-lg font-semibold mb-2')

                    def process_user_data(user_id, name="", email="", phone=""):
                        log_info(f"处理用户数据: ID={user_id}, Name={name}, Email={email}")
                        return {"id": user_id, "name": name, "email": email, "phone": phone}

                    result = safe(
                        process_user_data,
                        123,
                        name="张三",
                        email="zhangsan@test.com",
                        phone="13800138000",
                        return_value={}
                    )
                    ui.label(f'✅ 处理结果: {result}').classes('text-green-600')
                    ui.notify('带参数的 safe 执行成功!', type='positive')

            ui.button('测试正常执行', on_click=test_safe_success, icon='check_circle').classes('bg-green-500')
            ui.button('测试错误捕获', on_click=test_safe_error, icon='error').classes('bg-orange-500')
            ui.button('测试带参数', on_click=test_safe_with_kwargs, icon='settings').classes('bg-purple-500')

    # ======================== 第三部分: 装饰器测试 ========================
    with ui.card().classes('w-full p-6 mb-4'):
        ui.label('3️⃣ 装饰器测试').classes('text-2xl font-bold mb-4')

        with ui.row().classes('w-full gap-2 flex-wrap'):
            def test_page_protect_decorator():
                """测试 @page_protect 装饰器"""
                result_container.clear()
                with result_container:
                    ui.label('🧪 测试 @page_protect 装饰器...').classes('text-lg font-semibold mb-2')

                    @page_protect(name="测试函数", error_msg="函数执行失败,已被保护")
                    def protected_function(should_fail=False):
                        log_info("进入被保护的函数")
                        if should_fail:
                            raise RuntimeError("模拟的错误")
                        return "执行成功"

                    # 测试成功场景
                    result = protected_function(should_fail=False)
                    ui.label(f'✅ 正常执行: {result}').classes('text-green-600')
                    ui.separator()
                    # 测试失败场景
                    result = protected_function(should_fail=True)
                    ui.label(f'✅ 错误已被装饰器捕获,返回: {result}').classes('text-orange-600')
                    ui.notify('page_protect 装饰器测试完成!', type='positive')

            def test_catch_decorator():
                """测试 @catch 装饰器"""
                result_container.clear()
                with result_container:
                    ui.label('🧪 测试 @catch 装饰器...').classes('text-lg font-semibold mb-2')

                    @catch(message="数据处理失败", show_ui_error=True)
                    def process_data(data):
                        log_info(f"处理数据: {data}")
                        if not data:
                            raise ValueError("数据不能为空")
                        return f"处理完成: {data}"

                    # 正常场景
                    try:
                        result = process_data(["数据1", "数据2"])
                        ui.label(f'✅ 正常处理: {result}').classes('text-green-600')
                    except:
                        pass

                    # 错误场景
                    try:
                        result = process_data(None)
                    except Exception as e:
                        ui.label(f'✅ 异常已被捕获: {type(e).__name__}').classes('text-orange-600')
                        ui.label('📝 详细堆栈已记录到日志').classes('text-sm text-gray-500')

            ui.button('测试 @safe_protect', on_click=test_page_protect_decorator, icon='shield').classes('bg-indigo-500')
            ui.button('测试 @catch', on_click=test_catch_decorator, icon='security').classes('bg-cyan-500')

    # ======================== 第四部分: Logger 实例测试 ========================
    with ui.card().classes('w-full p-6 mb-4'):
        ui.label('4️⃣ get_logger() 实例测试').classes('text-2xl font-bold mb-4')

        with ui.row().classes('w-full gap-2 flex-wrap'):
            def test_get_logger():
                """测试 get_logger 获取自定义 logger"""
                result_container.clear()
                with result_container:
                    ui.label('🧪 测试 get_logger()...').classes('text-lg font-semibold mb-2')

                    # 创建自定义 logger
                    log = get_logger("test_module")

                    log.info("使用自定义 logger 记录 INFO")
                    ui.label('✅ INFO: 已记录').classes('text-blue-600')

                    log.success("使用自定义 logger 记录 SUCCESS")
                    ui.label('✅ SUCCESS: 已记录').classes('text-green-600')

                    log.warning("使用自定义 logger 记录 WARNING")
                    ui.label('✅ WARNING: 已记录').classes('text-orange-600')

                    try:
                        raise ValueError("测试错误")
                    except Exception as e:
                        log.error(f"使用自定义 logger 记录 ERROR: {e}")
                        ui.label('✅ ERROR: 已记录').classes('text-red-600')

                    ui.separator()
                    ui.label('💡 自定义 logger 会自动绑定用户上下文信息').classes('text-sm text-gray-500 mt-2')
                    ui.notify('get_logger 测试完成!', type='positive')

            ui.button('测试自定义 Logger', on_click=test_get_logger, icon='article').classes('bg-teal-500')

    # ======================== 第五部分: db_safe 测试 ========================
    with ui.card().classes('w-full p-6 mb-4'):
        ui.label('5️⃣ db_safe() 数据库安全测试').classes('text-2xl font-bold mb-4')

        with ui.row().classes('w-full gap-2 flex-wrap'):
            def test_db_safe():
                """测试 db_safe 数据库安全上下文"""
                result_container.clear()
                with result_container:
                    ui.label('🧪 测试 db_safe()...').classes('text-lg font-semibold mb-2')

                    try:
                        with db_safe("测试数据库操作") as db:
                            ui.label('✅ 进入数据库安全上下文').classes('text-blue-600')
                            # 这里可以执行数据库操作
                            # user = db.query(User).first()
                            log_info("模拟数据库查询操作")
                            ui.label('✅ 数据库操作已记录').classes('text-green-600')
                    except Exception as e:
                        ui.label(f'⚠️ 数据库操作异常: {e}').classes('text-orange-600')

                    ui.separator()
                    ui.label('💡 db_safe 会自动捕获异常、记录日志、回滚事务').classes('text-sm text-gray-500 mt-2')
                    ui.notify('db_safe 测试完成!', type='positive')

            ui.button('测试 db_safe', on_click=test_db_safe, icon='storage').classes('bg-purple-500')

    # ======================== 第六部分: 日志查询测试 ========================
    with ui.card().classes('w-full p-6 mb-4'):
        ui.label('6️⃣ 日志查询功能测试').classes('text-2xl font-bold mb-4')

        with ui.row().classes('w-full gap-2 flex-wrap'):
            def test_get_log_files():
                """查询最近的日志文件"""
                result_container.clear()
                with result_container:
                    ui.label('📂 查询最近7天的日志文件...').classes('text-lg font-semibold mb-2')

                    files = get_log_files(days=7)

                    if files:
                        ui.label(f'找到 {len(files)} 个日志文件:').classes('text-blue-600 mb-2')
                        for f in files[:10]:  # 最多显示10个
                            ui.label(f"📄 {f['date']} - {f['type']} ({f['size']} bytes)").classes('text-sm')
                    else:
                        ui.label('暂无日志文件').classes('text-gray-500')

                    ui.notify('日志文件查询完成!', type='info')

            def test_get_today_errors():
                """查询今天的错误日志"""
                result_container.clear()
                with result_container:
                    ui.label('🔍 查询今天的错误日志...').classes('text-lg font-semibold mb-2')

                    errors = get_today_errors(limit=10)

                    if errors:
                        ui.label(f'找到 {len(errors)} 条错误日志:').classes('text-red-600 mb-2')
                        for err in errors[:5]:  # 最多显示5条
                            ui.label(f"❌ [{err['timestamp']}] {err['message']}").classes('text-sm text-red-500')
                    else:
                        ui.label('✅ 今天暂无错误日志').classes('text-green-600')

                    ui.notify('错误日志查询完成!', type='info')

            def test_get_log_statistics():
                """获取日志统计信息"""
                result_container.clear()
                with result_container:
                    ui.label('📊 获取日志统计信息...').classes('text-lg font-semibold mb-2')

                    stats = get_log_statistics(days=7)

                    ui.label(f"📈 统计周期: 最近7天").classes('text-blue-600 mb-2')
                    ui.label(f"总日志数: {stats['total_logs']}").classes('text-sm')
                    ui.label(f"错误数量: {stats['error_count']}").classes('text-sm text-red-600')
                    ui.label(f"警告数量: {stats['warning_count']}").classes('text-sm text-orange-600')
                    ui.label(f"信息数量: {stats['info_count']}").classes('text-sm text-green-600')

                    if stats['by_level']:
                        ui.separator()
                        ui.label('按级别统计:').classes('text-sm font-semibold mt-2')
                        for level, count in stats['by_level'].items():
                            ui.label(f"  {level}: {count}").classes('text-xs')

                    ui.notify('统计信息获取完成!', type='info')

            def test_get_logs_by_level():
                """按级别查询日志"""
                result_container.clear()
                with result_container:
                    ui.label('🎯 按级别查询今天的日志...').classes('text-lg font-semibold mb-2')

                    # 查询 SUCCESS 级别
                    success_logs = get_today_logs_by_level(level="SUCCESS", limit=5)
                    ui.label(f'✅ SUCCESS 级别: {len(success_logs)} 条').classes('text-green-600')

                    # 查询 WARNING 级别
                    warning_logs = get_today_logs_by_level(level="WARNING", limit=5)
                    ui.label(f'⚠️ WARNING 级别: {len(warning_logs)} 条').classes('text-orange-600')

                    # 查询 ERROR 级别
                    error_logs = get_today_logs_by_level(level="ERROR", limit=5)
                    ui.label(f'❌ ERROR 级别: {len(error_logs)} 条').classes('text-red-600')

                    ui.notify('按级别查询完成!', type='info')

            ui.button('查询日志文件', on_click=test_get_log_files, icon='folder').classes('bg-blue-500')
            ui.button('查询今天错误', on_click=test_get_today_errors, icon='error_outline').classes('bg-red-500')
            ui.button('日志统计', on_click=test_get_log_statistics, icon='analytics').classes('bg-green-500')
            ui.button('按级别查询', on_click=test_get_log_statistics, icon='filter_list').classes('bg-purple-500')

    # ======================== 第七部分: 综合场景测试 ========================
    with ui.card().classes('w-full p-6 mb-4'):
        ui.label('7️⃣ 综合场景测试').classes('text-2xl font-bold mb-4')

        with ui.row().classes('w-full gap-2 flex-wrap'):
            def test_comprehensive_scenario():
                """综合场景: 模拟真实业务流程"""
                result_container.clear()
                with result_container:
                    ui.label('🎬 模拟用户注册流程 (综合测试)...').classes('text-lg font-semibold mb-2')

                    log_info("========== 用户注册流程开始 ==========")
                    ui.label('1️⃣ 开始用户注册流程').classes('text-blue-600')

                    # 步骤1: 验证输入
                    log_debug("验证用户输入数据", extra_data='{"step": 1}')
                    ui.label('  ✓ 步骤1: 验证输入数据').classes('text-sm text-gray-600')

                    # 步骤2: 检查用户名
                    username = "test_user_" + str(datetime.now().timestamp())[:10]
                    log_info(f"检查用户名可用性: {username}")
                    ui.label(f'  ✓ 步骤2: 用户名检查 ({username})').classes('text-sm text-gray-600')

                    # 步骤3: 数据库操作(使用 db_safe)
                    try:
                        with db_safe("创建用户记录"):
                            log_info(f"创建用户记录: {username}")
                            ui.label('  ✓ 步骤3: 数据库操作').classes('text-sm text-gray-600')
                    except Exception as e:
                        log_error("数据库操作失败", exception=e)

                    # 步骤4: 发送欢迎邮件(可能失败)
                    def send_welcome_email(email):
                        log_info(f"发送欢迎邮件到: {email}")
                        # 模拟随机失败
                        import random
                        if random.random() < 0.3:
                            raise ConnectionError("邮件服务器连接失败")
                        return True

                    result = safe(
                        send_welcome_email,
                        "test@example.com",
                        return_value=False,
                        show_error=False,
                        error_msg="邮件发送失败,将稍后重试"
                    )

                    if result:
                        log_success(f"用户注册成功: {username}")
                        ui.label('  ✓ 步骤4: 欢迎邮件已发送').classes('text-sm text-gray-600')
                        ui.separator()
                        ui.label('✅ 注册流程完成!').classes('text-xl text-green-600 font-bold mt-2')
                    else:
                        log_warning("邮件发送失败,但用户已创建")
                        ui.label('  ⚠️ 步骤4: 邮件发送失败(将重试)').classes('text-sm text-orange-600')
                        ui.separator()
                        ui.label('⚠️ 注册完成,但邮件待发送').classes('text-xl text-orange-600 font-bold mt-2')

                    log_info("========== 用户注册流程结束 ==========")
                    ui.notify('综合场景测试完成!', type='positive')

            ui.button('运行综合场景', on_click=test_comprehensive_scenario, icon='rocket_launch').classes('bg-gradient-to-r from-purple-500 to-pink-500 text-lg px-6 py-3')

    # ======================== 底部说明 ========================
    with ui.card().classes('w-full p-6 bg-blue-50 dark:bg-blue-900/20'):
        ui.label('📋 日志文件位置').classes('text-xl font-bold mb-3')
        ui.label('日志保存在 logs/[日期]/ 目录下:').classes('text-sm mb-2')
        ui.label('  • app.log - 所有级别的日志(文本格式)').classes('text-xs text-gray-600')
        ui.label('  • error.log - 仅错误和严重错误(文本格式)').classes('text-xs text-gray-600')
        ui.label('  • app_logs.csv - CSV格式日志(便于查询分析)').classes('text-xs text-gray-600')

        ui.separator().classes('my-3')

        ui.label('💡 使用建议').classes('text-xl font-bold mb-3')
        ui.label('1. 先运行各个测试,生成日志记录').classes('text-sm')
        ui.label('2. 然后查看 logs/ 目录下的日志文件').classes('text-sm')
        ui.label('3. CSV 文件可用 Excel 或文本编辑器打开查看').classes('text-sm')
        ui.label('4. 观察不同日志级别的输出格式和内容').classes('text-sm')
```

## 测试模块说明:

```
模块1: 日志级别测试 (7个级别)
测试内容:
    TRACE: 最详细的调试信息
    DEBUG: 开发调试信息(带额外数据)
    INFO: 普通运行信息
    SUCCESS: 操作成功标记
    WARNING: 需要注意的情况
    ERROR: 捕获的错误(带异常堆栈)
    CRITICAL: 严重错误(带异常和额外数据)

操作步骤:
    点击 "测试所有日志级别" 按钮
    观察页面显示的结果
    查看日志文件: logs/[今天日期]/app_logs.csv

预期结果:
    页面显示7条成功记录
    CSV文件包含所有级别的日志条目
    每条日志包含: 时间戳、级别、用户信息、模块、消息等
```

```
模块2: safe() 安全执行测试
测试内容:
    ✅ 正常执行场景
    ❌ 错误捕获场景
    ⚙️ 带参数执行场景

操作步骤:
    点击 "测试正常执行" - 观察函数正常返回
    点击 "测试错误捕获" - 观察错误被捕获,返回默认值
    点击 "测试带参数" - 观察复杂参数传递

预期结果:
    正常场景: 返回计算结果
    错误场景: 显示错误通知,返回默认值
    日志记录所有执行过程
```

```
模块3: 装饰器测试
测试内容:
    @page_protect - 页面/函数保护
    @catch - 异常捕获

操作步骤:
    点击 "测试 @page_protect" - 观察装饰器如何保护函数
    点击 "测试 @catch" - 观察异常捕获机制

预期结果:
    装饰器自动捕获异常
    UI 显示友好错误信息
    详细堆栈记录到日志
```

```
模块4: get_logger() 实例测试
测试内容:
    创建自定义模块 logger
    使用 logger 记录不同级别日志
    自动绑定用户上下文

操作步骤:
    点击 "测试自定义 Logger"
    观察不同级别的日志输出
    在 CSV 文件中查看 module_name 字段

预期结果:
    日志的 module_name 字段显示 "test_module"
    自动包含用户名、IP 等上下文信息
```

```
模块5: db_safe() 数据库安全测试
测试内容:
    数据库安全上下文管理
    自动异常捕获
    自动回滚机制

操作步骤:
    点击 "测试 db_safe"
    观察数据库操作的安全包裹
    查看日志记录

预期结果:
    操作被安全包裹
    异常自动捕获并记录
    事务自动回滚(如果失败)
```

```
模块6: 日志查询功能测试
测试内容:
    查询最近7天日志文件
    查询今天的错误日志
    获取日志统计信息
    按级别查询日志

操作步骤:
    先运行前面的测试,生成日志数据
    点击 "查询日志文件" - 查看文件列表
    点击 "查询今天错误" - 查看错误列表
    点击 "日志统计" - 查看统计信息

预期结果:
    显示日志文件的日期、类型、大小
    列出所有错误日志条目
    按级别统计日志数量
```

```
模块7: 综合场景测试
测试内容:
    模拟用户注册流程
    综合使用多种日志功能
    展示真实业务场景

操作步骤:
    点击 "运行综合场景"
    观察完整的业务流程日志
    查看 CSV 文件中的完整记录

预期结果:
    完整的流程日志记录
    每个步骤都有对应日志
    错误处理和成功提示正确显示
```
