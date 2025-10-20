# Auth 装饰器完整使用指南

## 📋 可用装饰器概览

`auth/decorators.py` 提供了以下装饰器：

### 1. 核心装饰器

- **`@require_login()`** - 要求用户登录
- **`@require_role()`** - 要求用户具有特定角色
- **`@require_permission()`** - 要求用户具有特定权限
- **`@public_route`** - 标记公开路由（无需认证）

### 2. 便捷装饰器

- **`@admin_only`** - 仅管理员可访问
- **`@authenticated_only`** - 仅需登录即可访问
- **`@protect_page()`** - 综合页面保护装饰器

## 🔧 装饰器详细说明

### 1. @require_login(redirect_to_login=True)

**功能**：验证用户是否已登录

**参数**：

- `redirect_to_login` (bool): 未登录时是否重定向到登录页，默认 True

**使用场景**：

- 需要用户登录才能访问的页面
- 个人中心、设置页面等

**示例**：

```python
from auth.decorators import require_login

# 基本用法 - 未登录重定向到登录页
@require_login()
def profile_page():
    ui.label('个人资料页面')

# 不重定向，仅显示错误消息
@require_login(redirect_to_login=False)
def ajax_api():
    return {'data': 'sensitive_data'}
```

### 2. @require_role(\*roles)

**功能**：验证用户是否具有指定角色

**参数**：

- `*roles` (str): 允许的角色列表，支持多个角色

**使用场景**：

- 管理员页面
- 特定权限的功能模块
- 角色分级访问控制

**示例**：

```python
from auth.decorators import require_role

# 单个角色
@require_role('admin')
def admin_panel():
    ui.label('管理员面板')

# 多个角色（或关系）
@require_role('admin', 'manager', 'moderator')
def management_page():
    ui.label('管理功能页面')

# 组合使用
@require_role('admin')
def user_management():
    ui.label('用户管理')
```

### 3. @require_permission(\*permissions)

**功能**：验证用户是否具有指定权限

**参数**：

- `*permissions` (str): 需要的权限列表

**使用场景**：

- 细粒度权限控制
- 特定功能权限验证
- 跨角色的权限管理

**示例**：

```python
from auth.decorators import require_permission

# 单个权限
@require_permission('user_management')
def user_list():
    ui.label('用户列表')

# 多个权限（且关系）
@require_permission('data_export', 'report_view')
def export_report():
    ui.label('导出报告')

# 权限组合
@require_permission('user_create', 'user_edit')
def user_form():
    ui.label('用户表单')
```

### 4. @public_route

**功能**：标记公开路由，不需要认证

**使用场景**：

- 登录、注册页面
- 公开的 API 接口
- 帮助文档、关于页面

**示例**：

```python
from auth.decorators import public_route

@public_route
def login_page():
    ui.label('登录页面')

@public_route
def about_page():
    ui.label('关于我们')
```

### 5. @admin_only

**功能**：仅管理员可访问的简化装饰器

**等价于**：`@require_role('admin')`

**示例**：

```python
from auth.decorators import admin_only

@admin_only
def system_settings():
    ui.label('系统设置')
```

### 6. @authenticated_only

**功能**：仅需登录即可访问的简化装饰器

**等价于**：`@require_login(redirect_to_login=True)`

**示例**：

```python
from auth.decorators import authenticated_only

@authenticated_only
def dashboard():
    ui.label('仪表盘')
```

### 7. @protect_page(roles=None, permissions=None, redirect_to_login=True)

**功能**：综合页面保护装饰器

**参数**：

- `roles` (list): 允许的角色列表
- `permissions` (list): 需要的权限列表
- `redirect_to_login` (bool): 未登录时是否重定向

**使用场景**：

- 复杂的权限组合验证
- 页面级的综合保护
- 灵活的权限控制

**示例**：

```python
from auth.decorators import protect_page

# 角色和权限组合
@protect_page(
    roles=['admin', 'manager'],
    permissions=['user_management', 'data_view']
)
def advanced_admin_page():
    ui.label('高级管理页面')

# 仅角色验证
@protect_page(roles=['admin'])
def admin_only_page():
    ui.label('管理员专属页面')

# 仅权限验证
@protect_page(permissions=['special_feature'])
def special_feature_page():
    ui.label('特殊功能页面')
```

## 🏗️ 在 header_pages 和 menu_pages 中使用装饰器

### 1. header_pages 包中的使用

**目录结构**：

```
header_pages/
├── __init__.py
├── search_page.py
├── messages_page.py
├── contact_page.py
└── ...
```

**使用示例**：

#### search_page.py

```python
from nicegui import ui
from auth.decorators import require_login

@require_login()
def search_page_content():
    """搜索页面 - 需要登录"""
    ui.label('搜索功能').classes('text-3xl font-bold')

    search_input = ui.input('搜索关键词', placeholder='请输入搜索内容')

    with ui.row().classes('gap-2 mt-4'):
        ui.button('搜索', icon='search', on_click=lambda: perform_search(search_input.value))
        ui.button('高级搜索', icon='tune')

def perform_search(query):
    """执行搜索 - 使用当前用户信息"""
    from auth import auth_manager
    user = auth_manager.current_user
    ui.notify(f'用户 {user.username} 搜索: {query}', type='info')
```

#### messages_page.py

```python
from nicegui import ui
from auth.decorators import require_login, require_permission

@require_login()
def messages_page_content():
    """消息页面 - 需要登录"""
    ui.label('消息中心').classes('text-3xl font-bold')

    with ui.tabs().classes('w-full') as tabs:
        inbox = ui.tab('收件箱')
        sent = ui.tab('已发送')

        # 管理员可以看到系统消息
        if auth_manager.current_user.has_role('admin'):
            system = ui.tab('系统消息')

    with ui.tab_panels(tabs, value=inbox).classes('w-full'):
        with ui.tab_panel(inbox):
            show_inbox_messages()

        with ui.tab_panel(sent):
            show_sent_messages()

        if auth_manager.current_user.has_role('admin'):
            with ui.tab_panel(system):
                show_system_messages()

@require_permission('message_admin')
def show_system_messages():
    """显示系统消息 - 需要特定权限"""
    ui.label('系统消息管理').classes('text-lg font-semibold')
    # 系统消息内容...
```

#### contact_page.py

```python
from nicegui import ui
from auth.decorators import public_route

@public_route
def contact_page_content():
    """联系我们页面 - 公开页面"""
    ui.label('联系我们').classes('text-3xl font-bold text-emerald-800 dark:text-emerald-200')
    ui.label('如有任何问题或建议，请随时联系我们。').classes('text-gray-600 dark:text-gray-400 mt-4')

    with ui.card().classes('w-full mt-4'):
        ui.label('联系方式').classes('text-lg font-semibold')
        ui.label('📧 邮箱: support@example.com').classes('mt-2')
        ui.label('📞 电话: +86 400-123-4567').classes('mt-2')
        ui.label('💬 在线客服: 工作日 9:00-18:00').classes('mt-2')

    with ui.card().classes('w-full mt-4'):
        ui.label('意见反馈').classes('text-lg font-semibold')
        feedback_input = ui.textarea('请输入您的意见或建议', placeholder='我们很重视您的反馈...').classes('w-full mt-2')
        ui.button('提交反馈', icon='send', on_click=lambda: submit_feedback(feedback_input.value)).classes('mt-2')

def submit_feedback(content):
    """提交反馈 - 可以区分登录用户和匿名用户"""
    from auth import auth_manager

    user = auth_manager.current_user
    if user:
        # 登录用户提交反馈
        ui.notify(f'感谢您的反馈，{user.username}！', type='positive')
    else:
        # 匿名用户提交反馈
        ui.notify('感谢您的反馈！', type='positive')
```

### 2. menu_pages 包中的使用

**目录结构**：

```
menu_pages/
├── __init__.py
├── home_page.py
├── dashboard_page.py
├── data_page.py
├── analysis_page.py
├── mcp_page.py
└── about_page.py
```

**使用示例**：

#### home_page.py

```python
from nicegui import ui
from auth.decorators import require_login

@require_login()
def home_page_content():
    """首页 - 需要登录"""
    from auth import auth_manager

    user = auth_manager.current_user
    ui.label(f'欢迎回来，{user.full_name or user.username}！').classes('text-4xl font-bold')

    # 显示用户角色相关的内容
    if user.has_role('admin'):
        with ui.card().classes('w-full mt-4'):
            ui.label('管理员快捷操作').classes('text-lg font-semibold')
            with ui.row().classes('gap-2'):
                ui.button('用户管理', icon='people', on_click=lambda: navigate_to('user_management'))
                ui.button('系统设置', icon='settings', on_click=lambda: navigate_to('system_settings'))

    # 显示个人统计信息
    with ui.card().classes('w-full mt-4'):
        ui.label('个人统计').classes('text-lg font-semibold')
        ui.label(f'登录次数: {user.login_count}').classes('mt-2')
        ui.label(f'上次登录: {user.last_login or "首次登录"}').classes('mt-2')
```

#### analysis_page.py

```python
from nicegui import ui
from auth.decorators import require_permission

@require_permission('data_analysis')
def analysis_page_content():
    """智能问数页面 - 需要数据分析权限"""
    ui.label('智能问数').classes('text-3xl font-bold text-blue-800 dark:text-blue-200')
    ui.label('使用自然语言查询您的数据。').classes('text-gray-600 dark:text-gray-400 mt-4')

    query_input = ui.input('请输入您的问题', placeholder='例如：上个月销售额是多少？').classes('w-full mt-2')

    with ui.row().classes('gap-2 mt-4'):
        ui.button('开始分析', icon='analytics', on_click=lambda: start_analysis(query_input.value))

        # 高级功能需要额外权限
        if auth_manager.current_user.has_permission('advanced_analysis'):
            ui.button('高级分析', icon='science', on_click=lambda: advanced_analysis(query_input.value))

def start_analysis(query):
    """开始分析"""
    from auth import auth_manager
    user = auth_manager.current_user
    ui.notify(f'正在为用户 {user.username} 分析问题: {query}', type='info')

@require_permission('advanced_analysis')
def advanced_analysis(query):
    """高级分析功能"""
    ui.notify('启动高级分析模式...', type='info')
```

#### mcp_page.py

```python
from nicegui import ui
from auth.decorators import require_role, require_permission

@require_role('admin', 'developer')
def mcp_page_content():
    """MCP服务页面 - 需要管理员或开发者角色"""
    ui.label('MCP服务管理').classes('text-3xl font-bold text-purple-800 dark:text-purple-200')

    with ui.tabs().classes('w-full') as tabs:
        services = ui.tab('服务列表')
        config = ui.tab('配置管理')

        # 仅管理员可以看到系统监控
        if auth_manager.current_user.has_role('admin'):
            monitor = ui.tab('系统监控')

    with ui.tab_panels(tabs, value=services).classes('w-full'):
        with ui.tab_panel(services):
            show_services()

        with ui.tab_panel(config):
            show_config_management()

        if auth_manager.current_user.has_role('admin'):
            with ui.tab_panel(monitor):
                show_system_monitor()

def show_services():
    """显示服务列表"""
    ui.label('MCP服务列表').classes('text-lg font-semibold')
    # 服务列表内容...

@require_permission('config_management')
def show_config_management():
    """显示配置管理 - 需要配置管理权限"""
    ui.label('配置管理').classes('text-lg font-semibold')
    # 配置管理内容...

@require_role('admin')
def show_system_monitor():
    """显示系统监控 - 仅管理员"""
    ui.label('系统监控').classes('text-lg font-semibold')
    # 系统监控内容...
```

#### about_page.py

```python
from nicegui import ui
from auth.decorators import public_route

@public_route
def about_page_content():
    """关于页面 - 公开页面"""
    ui.label('关于我们').classes('text-3xl font-bold text-gray-800 dark:text-gray-200')
    ui.label('了解我们的产品和团队。').classes('text-gray-600 dark:text-gray-400 mt-4')

    with ui.card().classes('w-full mt-4'):
        ui.label('产品信息').classes('text-lg font-semibold')
        ui.label('版本: 1.0.0').classes('mt-2')
        ui.label('发布日期: 2024年').classes('mt-2')
        ui.label('技术栈: NiceGUI + Python').classes('mt-2')
```

## 🔧 高级使用技巧

### 1. 装饰器组合使用

```python
from auth.decorators import require_login, require_role
from common.exception_handler import safe_protect

# 多个装饰器组合
@require_role('admin')
@safe_protect(name="高级管理页面")
def advanced_admin_page():
    """组合使用认证和异常处理装饰器"""
    pass

# 条件装饰器
def conditional_auth(func):
    """根据条件选择装饰器"""
    from auth import auth_config

    if auth_config.require_auth:
        return require_login()(func)
    else:
        return public_route(func)

@conditional_auth
def maybe_protected_page():
    """可能需要认证的页面"""
    pass
```

### 2. 动态权限检查

```python
from auth.decorators import require_login
from auth import auth_manager

@require_login()
def dynamic_permission_page():
    """动态权限检查页面"""
    user = auth_manager.current_user

    # 在函数内部进行动态权限检查
    if user.has_permission('feature_a'):
        ui.button('功能A', on_click=feature_a_handler)

    if user.has_permission('feature_b'):
        ui.button('功能B', on_click=feature_b_handler)

    # 角色相关的UI
    if user.has_role('admin'):
        ui.separator()
        ui.label('管理员功能').classes('text-lg font-semibold')
        ui.button('管理面板', on_click=admin_panel_handler)
```

### 3. 自定义认证装饰器

```python
from functools import wraps
from auth.decorators import require_login
from auth import auth_manager

def require_department(department_name):
    """要求用户属于特定部门的装饰器"""
    def decorator(func):
        @require_login()
        @wraps(func)
        def wrapper(*args, **kwargs):
            user = auth_manager.current_user

            # 假设用户有部门属性
            if hasattr(user, 'department') and user.department == department_name:
                return func(*args, **kwargs)
            else:
                ui.notify(f'此功能仅限{department_name}部门使用', type='error')
                return
        return wrapper
    return decorator

@require_department('技术部')
def tech_department_page():
    """技术部专属页面"""
    ui.label('技术部内部页面')
```

### 4. 批量页面保护

```python
# 在 __init__.py 中批量应用装饰器
from auth.decorators import require_login, require_role, protect_page

def apply_auth_decorators():
    """批量应用认证装饰器"""

    # 需要登录的页面
    login_required_pages = [
        'home_page_content',
        'dashboard_page_content',
        'search_page_content',
        'messages_page_content'
    ]

    # 需要管理员权限的页面
    admin_required_pages = [
        'user_management_page_content',
        'system_settings_page_content'
    ]

    # 应用装饰器
    for page_name in login_required_pages:
        if page_name in globals():
            globals()[page_name] = require_login()(globals()[page_name])

    for page_name in admin_required_pages:
        if page_name in globals():
            globals()[page_name] = require_role('admin')(globals()[page_name])

# 调用批量装饰器应用
apply_auth_decorators()
```

## 🎯 最佳实践

### 1. 装饰器选择原则

```python
# ✅ 推荐做法
@require_login()          # 仅需要登录
@require_role('admin')    # 需要特定角色
@require_permission('specific_action')  # 需要特定权限
@public_route            # 公开页面

# ❌ 避免的做法
def manual_auth_check():
    """手动检查认证（不推荐）"""
    if not auth_manager.current_user:
        ui.notify('请先登录')
        return
    # 页面逻辑...
```

### 2. 错误处理

```python
from auth.decorators import require_role
from common.exception_handler import safe_protect

@require_role('admin')
@safe_protect(name="管理员页面", error_msg="管理页面访问失败")
def admin_page_with_error_handling():
    """带错误处理的管理员页面"""
    # 页面逻辑...
```

### 3. 用户体验优化

```python
@require_login()
def user_friendly_page():
    """用户友好的页面"""
    user = auth_manager.current_user

    # 显示个性化欢迎信息
    ui.label(f'欢迎，{user.full_name or user.username}！')

    # 根据权限显示不同内容
    if user.has_role('admin'):
        ui.label('管理员功能').classes('text-lg font-semibold text-red-600')
    elif user.has_role('manager'):
        ui.label('经理功能').classes('text-lg font-semibold text-blue-600')
    else:
        ui.label('用户功能').classes('text-lg font-semibold text-green-600')
```

## 📝 总结

Auth 装饰器提供了完整的认证和授权解决方案：

1. **简单易用**：通过装饰器即可快速添加认证功能
2. **灵活强大**：支持角色、权限、组合验证等多种方式
3. **无缝集成**：完美集成到 menu_pages 和 header_pages 中
4. **用户友好**：提供清晰的错误提示和重定向机制

使用这些装饰器，您可以轻松地为应用添加完整的认证和授权功能，确保应用的安全性和用户体验。
