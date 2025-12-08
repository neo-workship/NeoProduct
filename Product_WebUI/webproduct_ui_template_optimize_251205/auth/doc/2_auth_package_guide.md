# webproduct_ui_template 认证和权限管理包 - 完整使用文档

## 📋 目录

1. [包概述](#包概述)
2. [核心模块详解](#核心模块详解)
3. [快速开始](#快速开始)
4. [核心功能使用](#核心功能使用)
5. [装饰器使用指南](#装饰器使用指南)
6. [页面开发指南](#页面开发指南)
7. [数据库操作](#数据库操作)
8. [配置自定义](#配置自定义)
9. [最佳实践](#最佳实践)
10. [常见问题](#常见问题)

---

## 包概述

`webproduct_ui_template\auth` 是一个基于 NiceGUI 和 SQLModel 开发的完整认证和权限管理解决方案，提供：

- ✅ 用户注册、登录、登出
- ✅ 基于角色的访问控制（RBAC）
- ✅ 细粒度权限管理
- ✅ 会话管理和持久化
- ✅ 密码加密和安全存储
- ✅ 装饰器式权限保护
- ✅ 完整的管理页面（用户/角色/权限）
- ✅ 支持 SQLite/MySQL/PostgreSQL

### 包结构

```
auth/
├── __init__.py              # 包初始化和导出
├── auth_manager.py          # 核心认证管理器
├── session_manager.py       # 会话管理
├── models.py                # 数据模型（用户/角色/权限）
├── database.py              # 数据库连接和管理
├── config.py                # 配置管理
├── decorators.py            # 权限装饰器
├── navigation.py            # 导航辅助函数
├── utils.py                 # 工具函数
└── pages/                   # 内置页面
    ├── login_page.py        # 登录页
    ├── register_page.py     # 注册页
    ├── logout_page.py       # 登出页
    ├── profile_page.py      # 个人资料
    ├── change_password_page.py  # 修改密码
    ├── user_management_page.py  # 用户管理
    ├── role_management_page.py  # 角色管理
    └── permission_management_page.py  # 权限管理
```

---

## 核心模块详解

### 1. AuthManager - 认证管理器

`AuthManager` 是认证系统的核心，负责所有认证相关操作。

#### 主要功能：

```python
from auth import auth_manager

# 1. 用户注册
result = auth_manager.register(
    username='newuser',
    email='user@example.com',
    password='password123',
    full_name='张三',
    phone='13800138000'
)

# 2. 用户登录
result = auth_manager.login(
    username='admin',
    password='admin123',
    remember_me=True  # 记住我
)

# 3. 检查当前会话
current_user = auth_manager.check_session()
if current_user:
    print(f"当前用户: {current_user.username}")

# 4. 退出登录
auth_manager.logout()

# 5. 检查权限
has_perm = auth_manager.has_permission('user.manage')
has_role = auth_manager.has_role('admin')

# 6. 修改密码
result = auth_manager.change_password(
    user_id=1,
    old_password='old_pass',
    new_password='new_pass'
)
```

#### 返回值格式：

所有认证操作都返回统一的字典格式：

```python
{
    'success': True/False,
    'message': '操作结果消息',
    'user': User对象,  # 登录成功时
    'token': '会话token'  # 登录成功时
}
```

---

### 2. SessionManager - 会话管理器

管理用户会话的内存缓存，避免频繁数据库查询。

```python
from auth import session_manager

# 创建会话（通常由 auth_manager 自动调用）
session = session_manager.create_session(token, user)

# 获取会话
session = session_manager.get_session(token)

# 更新会话（重新加载用户数据）
session = session_manager.update_session(token, user)

# 删除会话
session_manager.delete_session(token)

# 获取所有会话（管理用途）
all_sessions = session_manager.get_all_sessions()
```

#### UserSession 对象：

```python
class UserSession:
    user_id: int
    username: str
    email: str
    full_name: str
    is_active: bool
    is_superuser: bool
    roles: List[str]          # 角色名列表
    permissions: Set[str]     # 权限名集合
    created_at: datetime
    updated_at: datetime
```

---

### 3. 数据模型

#### User 模型

```python
from auth.models import User

# 用户属性
user.id              # 用户ID
user.username        # 用户名（唯一）
user.email           # 邮箱（唯一）
user.password_hash   # 密码哈希
user.full_name       # 全名
user.phone           # 电话
user.avatar          # 头像URL
user.is_active       # 是否激活
user.is_superuser    # 是否超级管理员
user.last_login      # 最后登录时间
user.login_count     # 登录次数
user.failed_login_attempts  # 失败登录次数
user.locked_until    # 锁定截止时间
user.roles           # 角色列表（关系）
user.permissions     # 直接权限列表（关系）

# 用户方法
user.verify_password(password)  # 验证密码
user.has_role(role_name)        # 检查角色
user.has_permission(perm_name)  # 检查权限
```

#### Role 模型

```python
from auth.models import Role

# 角色属性
role.id              # 角色ID
role.name            # 角色名（唯一）
role.display_name    # 显示名称
role.description     # 描述
role.is_active       # 是否启用
role.users           # 拥有此角色的用户
role.permissions     # 角色权限列表

# 角色方法
role.add_permission(permission)     # 添加权限
role.remove_permission(permission)  # 移除权限
role.has_permission(perm_name)      # 检查权限
```

#### Permission 模型

```python
from auth.models import Permission

# 权限属性
permission.id            # 权限ID
permission.name          # 权限名（唯一）
permission.display_name  # 显示名称
permission.category      # 分类
permission.description   # 描述
permission.is_active     # 是否启用
permission.roles         # 拥有此权限的角色
permission.users         # 直接拥有此权限的用户
```

---

## 快速开始

### 1. 基础集成

在主应用中初始化认证系统：

```python
from nicegui import ui, app
from auth import (
    auth_manager,
    init_database,
    get_auth_page_handlers
)

# 初始化数据库
init_database()

# 注册认证相关的路由
auth_handlers = get_auth_page_handlers()

@ui.page('/login')
def login():
    auth_handlers['login']()

@ui.page('/register')
def register():
    auth_handlers['register']()

@ui.page('/user_management')
def user_management():
    auth_handlers['user_management']()

# 启动应用
ui.run(storage_secret='your-secret-key-here')
```

### 2. 使用 SPA 布局集成

```python
from component import with_multilayer_spa_layout, LayoutConfig
from auth import get_auth_page_handlers, get_menu_page_handlers

# 合并页面处理器
all_handlers = {
    **get_menu_page_handlers(),
    **get_auth_page_handlers()
}

# 配置布局
config = LayoutConfig(
    app_title='我的应用',
    app_subtitle='认证系统演示',
    show_user_avatar=True,
    enable_breadcrumbs=True
)

# 应用布局
@with_multilayer_spa_layout(
    menu_items=menu_structure,
    page_handlers=all_handlers,
    config=config
)
def main_content(page_key: str):
    ui.label(f'当前页面: {page_key}')

ui.run()
```

---

## 核心功能使用

### 1. 用户注册

```python
from auth import auth_manager
from nicegui import ui

def register_user():
    """用户注册示例"""
    result = auth_manager.register(
        username='newuser',
        email='user@example.com',
        password='securepass123',
        full_name='新用户',
        phone='13800138000'
    )

    if result['success']:
        ui.notify('注册成功！', type='positive')
        ui.navigate.to('/login')
    else:
        ui.notify(result['message'], type='negative')
```

### 2. 用户登录

```python
def login_user():
    """用户登录示例"""
    result = auth_manager.login(
        username='admin',
        password='admin123',
        remember_me=True
    )

    if result['success']:
        user = result['user']
        ui.notify(f'欢迎回来，{user.username}！', type='positive')
        ui.navigate.to('/dashboard')
    else:
        ui.notify(result['message'], type='negative')
```

### 3. 会话检查

```python
def check_user_session():
    """检查当前用户会话"""
    user = auth_manager.check_session()

    if user:
        print(f"已登录: {user.username}")
        print(f"角色: {user.roles}")
        print(f"权限: {user.permissions}")
        return True
    else:
        print("未登录")
        return False
```

### 4. 权限检查

```python
def check_permissions():
    """检查用户权限"""
    # 检查角色
    if auth_manager.has_role('admin'):
        print("用户是管理员")

    # 检查权限
    if auth_manager.has_permission('user.manage'):
        print("用户有用户管理权限")

    # 批量检查
    required_perms = ['content.create', 'content.edit']
    has_all = all(
        auth_manager.has_permission(p)
        for p in required_perms
    )
```

### 5. 密码管理

```python
def change_user_password(user_id: int):
    """修改用户密码"""
    result = auth_manager.change_password(
        user_id=user_id,
        old_password='oldpass123',
        new_password='newpass456'
    )

    if result['success']:
        ui.notify('密码修改成功，请重新登录', type='positive')
        auth_manager.logout()
        ui.navigate.to('/login')
    else:
        ui.notify(result['message'], type='negative')
```

---

## 装饰器使用指南

### 1. @require_login - 需要登录

最基础的装饰器，要求用户必须登录才能访问。

```python
from auth import require_login
from nicegui import ui

@require_login(redirect_to_login=True)
def protected_page_content():
    """需要登录才能访问的页面"""
    ui.label('这是受保护的页面')
    ui.label('只有登录用户才能看到')
```

**参数说明：**

- `redirect_to_login`: 是否自动重定向到登录页（默认 True）

### 2. @require_role - 需要特定角色

要求用户具有指定的角色。

```python
from auth import require_role

# 单个角色
@require_role('admin')
def admin_page_content():
    """只有管理员能访问"""
    ui.label('管理员专属页面')

# 多个角色（任一即可）
@require_role('admin', 'editor')
def content_management_page():
    """管理员或编辑可以访问"""
    ui.label('内容管理页面')
```

### 3. @require_permission - 需要特定权限

要求用户具有指定的权限。

```python
from auth import require_permission

# 单个权限
@require_permission('user.manage')
def user_management_page():
    """需要用户管理权限"""
    ui.label('用户管理')

# 多个权限（必须全部拥有）
@require_permission('content.create', 'content.edit')
def content_editor_page():
    """需要创建和编辑权限"""
    ui.label('内容编辑器')
```

### 4. 装饰器组合使用

```python
from auth import require_login, require_role, require_permission

# 组合方式1：多重装饰
@require_login(redirect_to_login=True)
@require_role('admin')
@require_permission('system.manage')
def system_settings_page():
    """需要登录、管理员角色和系统管理权限"""
    ui.label('系统设置')

# 组合方式2：使用 protect_page
from auth.decorators import protect_page

@protect_page(
    roles=['admin', 'superuser'],
    permissions=['system.manage'],
    redirect_to_login=True
)
def advanced_settings_page():
    """高级设置页面"""
    ui.label('高级系统设置')
```

### 5. 公开路由标记

```python
from auth.decorators import public_route

@public_route
def public_page_content():
    """公开页面，无需认证"""
    ui.label('这是公开页面')
    ui.label('任何人都可以访问')
```

---

## 页面开发指南

### 1. 创建需要登录的页面

```python
from nicegui import ui
from auth import require_login, auth_manager

@require_login(redirect_to_login=True)
def my_protected_page():
    """受保护的页面示例"""
    # 获取当前用户
    current_user = auth_manager.check_session()

    ui.label(f'欢迎，{current_user.username}！')
    ui.label(f'您的邮箱：{current_user.email}')

    # 显示用户角色
    with ui.card():
        ui.label('您的角色：').classes('font-bold')
        for role in current_user.roles:
            ui.chip(role, color='primary')

    # 根据权限显示内容
    if current_user.has_permission('content.create'):
        ui.button('创建内容', on_click=create_content)
```

### 2. 创建管理员专属页面

```python
from auth import require_role

@require_role('admin')
def admin_dashboard():
    """管理员仪表板"""
    ui.label('管理员仪表板').classes('text-3xl font-bold')

    with ui.row():
        # 用户统计
        with ui.card():
            ui.label('用户总数')
            user_count = get_user_count()
            ui.label(str(user_count)).classes('text-4xl')

        # 角色统计
        with ui.card():
            ui.label('角色数量')
            role_count = get_role_count()
            ui.label(str(role_count)).classes('text-4xl')
```

### 3. 条件渲染内容

```python
from auth import auth_manager

def flexible_page():
    """根据权限灵活显示内容"""
    current_user = auth_manager.check_session()

    # 所有用户都能看到
    ui.label('欢迎访问')

    # 只有登录用户能看到
    if current_user:
        ui.label(f'你好，{current_user.username}')

        # 只有管理员能看到
        if current_user.has_role('admin'):
            ui.button('管理面板', on_click=open_admin_panel)

        # 只有有特定权限的用户能看到
        if current_user.has_permission('content.edit'):
            ui.button('编辑内容', on_click=edit_content)
    else:
        ui.button('登录', on_click=lambda: ui.navigate.to('/login'))
```

### 4. 在 SPA 布局中使用

```python
from component import with_multilayer_spa_layout
from auth import require_login, auth_manager

@with_multilayer_spa_layout(menu_items, page_handlers, config)
@require_login(redirect_to_login=True)
def main_app(page_key: str):
    """带认证的 SPA 应用"""
    current_user = auth_manager.check_session()

    # 在顶部显示用户信息
    with ui.header():
        ui.label(f'当前用户: {current_user.username}')
        ui.button('退出', on_click=lambda: ui.navigate.to('/logout'))

    # 根据 page_key 渲染不同页面
    page_handlers[page_key]()
```

---

## 数据库操作

### 1. 使用上下文管理器

推荐方式，自动管理会话：

```python
from auth.database import get_db
from auth.models import User
from sqlmodel import select

# 查询用户
with get_db() as session:
    users = session.exec(select(User)).all()
    for user in users:
        print(user.username)

# 创建用户
with get_db() as session:
    new_user = User(
        username='testuser',
        email='test@example.com'
    )
    new_user.set_password('password123')
    session.add(new_user)
    # 自动提交（退出 with 块时）
```

### 2. 手动管理会话

```python
from auth.database import get_session

session = get_session()
try:
    user = session.exec(
        select(User).where(User.username == 'admin')
    ).first()

    if user:
        user.login_count += 1
        session.add(user)
        session.commit()
        session.refresh(user)
finally:
    session.close()
```

### 3. 常见数据库操作

#### 查询用户

```python
from sqlmodel import select
from auth.database import get_db
from auth.models import User

# 查询所有用户
with get_db() as session:
    users = session.exec(select(User)).all()

# 按ID查询
with get_db() as session:
    user = session.get(User, user_id)

# 按用户名查询
with get_db() as session:
    user = session.exec(
        select(User).where(User.username == 'admin')
    ).first()

# 条件查询
with get_db() as session:
    active_users = session.exec(
        select(User).where(User.is_active == True)
    ).all()
```

#### 创建和更新

```python
# 创建新用户
with get_db() as session:
    user = User(
        username='newuser',
        email='new@example.com',
        full_name='新用户'
    )
    user.set_password('password123')
    session.add(user)
    # 自动提交

# 更新用户
with get_db() as session:
    user = session.get(User, user_id)
    user.full_name = '更新后的名字'
    user.phone = '13900139000'
    session.add(user)
    # 自动提交
```

#### 删除记录

```python
with get_db() as session:
    user = session.get(User, user_id)
    if user:
        session.delete(user)
        # 自动提交
```

### 4. 角色和权限操作

```python
from auth.models import Role, Permission

# 创建角色
with get_db() as session:
    role = Role(
        name='editor',
        display_name='编辑',
        description='可以编辑内容'
    )
    session.add(role)

# 为角色添加权限
with get_db() as session:
    role = session.exec(
        select(Role).where(Role.name == 'editor')
    ).first()

    permission = session.exec(
        select(Permission).where(Permission.name == 'content.edit')
    ).first()

    if role and permission:
        role.permissions.append(permission)
        session.add(role)

# 为用户分配角色
with get_db() as session:
    user = session.get(User, user_id)
    role = session.exec(
        select(Role).where(Role.name == 'editor')
    ).first()

    if user and role:
        user.roles.append(role)
        session.add(user)
```

---

## 配置自定义

### 1. 修改配置

```python
from auth import auth_config

# 修改数据库类型
auth_config.set_database_type('mysql')  # 或 'postgresql', 'sqlite'

# 修改会话超时
auth_config.session_timeout = 3600 * 2  # 2小时

# 修改密码策略
auth_config.password_min_length = 8
auth_config.password_require_uppercase = True
auth_config.password_require_numbers = True

# 修改登录限制
auth_config.max_login_attempts = 3
auth_config.lockout_duration = 1800  # 30分钟

# 关闭注册功能
auth_config.allow_registration = False
```

### 2. 自定义路由

```python
# 修改认证相关路由
auth_config.login_route = '/auth/login'
auth_config.logout_route = '/auth/logout'
auth_config.register_route = '/auth/register'
auth_config.unauthorized_redirect = '/auth/login'
```

### 3. 环境变量配置

在 `.env` 文件中设置：

```bash
# 数据库配置
DATABASE_URL=mysql://user:password@localhost/dbname

# 会话密钥
SESSION_SECRET_KEY=your-very-secret-key-here

# 其他配置
ALLOW_REGISTRATION=true
PASSWORD_MIN_LENGTH=8
```

然后在代码中读取：

```python
import os
from dotenv import load_dotenv

load_dotenv()

auth_config.session_secret_key = os.getenv('SESSION_SECRET_KEY')
auth_config.allow_registration = os.getenv('ALLOW_REGISTRATION') == 'true'
```

---

## 最佳实践

### 1. 安全建议

```python
# ✅ 好的做法
# 使用强密码策略
auth_config.password_min_length = 8
auth_config.password_require_uppercase = True
auth_config.password_require_numbers = True
auth_config.password_require_special = True

# 限制登录尝试
auth_config.max_login_attempts = 5
auth_config.lockout_duration = 1800

# 使用环境变量存储敏感信息
auth_config.session_secret_key = os.getenv('SESSION_SECRET_KEY')

# ❌ 避免的做法
# 不要硬编码密钥
auth_config.session_secret_key = 'weak-key-123'

# 不要禁用所有密码要求
auth_config.password_min_length = 1
```

### 2. 性能优化

```python
# ✅ 使用会话缓存避免重复查询
current_user = auth_manager.check_session()  # 从缓存获取

# ❌ 避免每次都查数据库
with get_db() as session:
    user = session.get(User, user_id)  # 不推荐频繁使用

# ✅ 批量操作
with get_db() as session:
    users = session.exec(select(User).limit(100)).all()
    for user in users:
        user.last_updated = datetime.now()
        session.add(user)
    # 一次性提交
```

### 3. 错误处理

```python
from auth import auth_manager
from common.log_handler import log_error, safe_protect

@safe_protect(name="用户登录", error_msg="登录失败，请稍后重试")
def handle_login():
    """带错误保护的登录处理"""
    try:
        result = auth_manager.login(username, password)
        if result['success']:
            ui.notify('登录成功', type='positive')
            ui.navigate.to('/dashboard')
        else:
            ui.notify(result['message'], type='negative')
    except Exception as e:
        log_error(f"登录异常: {e}")
        ui.notify('系统错误，请联系管理员', type='negative')
```

### 4. 代码组织

```python
# ✅ 推荐的项目结构
my_app/
├── auth/                  # 认证包（不要修改）
├── pages/                 # 业务页面
│   ├── dashboard.py
│   ├── settings.py
│   └── reports.py
├── models/                # 业务模型
│   └── business_models.py
├── config/                # 应用配置
│   └── app_config.py
└── main.py               # 应用入口

# 在业务页面中使用认证
from auth import require_login, auth_manager

@require_login(redirect_to_login=True)
def dashboard_page():
    current_user = auth_manager.check_session()
    # 业务逻辑...
```

### 5. 测试和调试

```python
# 开启数据库日志
from auth.database import init_database

# 在开发环境下开启 SQL 日志
import os
if os.getenv('DEBUG') == 'true':
    auth_config.database_url += '?echo=true'

# 使用测试账号
def create_test_users():
    """创建测试账号"""
    test_users = [
        ('admin', 'admin123', 'admin'),
        ('editor', 'editor123', 'editor'),
        ('viewer', 'viewer123', 'viewer'),
    ]

    for username, password, role_name in test_users:
        result = auth_manager.register(
            username=username,
            email=f'{username}@test.com',
            password=password
        )
        if result['success']:
            # 分配角色
            assign_role_to_user(result['user'].id, role_name)
```

---

## 常见问题

### Q1: 如何添加新的权限？

```python
from auth.database import get_db
from auth.models import Permission

def add_custom_permission():
    """添加自定义权限"""
    with get_db() as session:
        perm = Permission(
            name='report.view',
            display_name='查看报表',
            category='报表',
            description='允许查看系统报表'
        )
        session.add(perm)

    print("权限已添加")
```

### Q2: 如何给用户分配角色？

```python
from auth.database import get_db
from auth.models import User, Role
from sqlmodel import select

def assign_role(user_id: int, role_name: str):
    """为用户分配角色"""
    with get_db() as session:
        user = session.get(User, user_id)
        role = session.exec(
            select(Role).where(Role.name == role_name)
        ).first()

        if user and role:
            if role not in user.roles:
                user.roles.append(role)
                session.add(user)
                return True
    return False
```

### Q3: 如何实现"记住我"功能？

"记住我"功能已内置，在登录时设置 `remember_me=True` 即可：

```python
result = auth_manager.login(
    username='admin',
    password='admin123',
    remember_me=True  # 延长会话时间
)
```

### Q4: 如何自定义登录页面？

```python
from nicegui import ui
from auth import auth_manager, auth_config

def custom_login_page():
    """自定义登录页面"""
    with ui.card().classes('w-96 mx-auto mt-20'):
        ui.label('我的应用登录').classes('text-2xl font-bold')

        username = ui.input('用户名')
        password = ui.input('密码', password=True)

        def do_login():
            result = auth_manager.login(
                username.value,
                password.value
            )
            if result['success']:
                ui.navigate.to('/dashboard')
            else:
                ui.notify(result['message'], type='negative')

        ui.button('登录', on_click=do_login)
```

### Q5: 如何处理会话过期？

会话过期会自动处理，用户会被重定向到登录页。如需自定义行为：

```python
from auth import auth_manager

def check_and_redirect():
    """检查会话并处理过期"""
    user = auth_manager.check_session()
    if not user:
        ui.notify('会话已过期，请重新登录', type='warning')
        ui.navigate.to('/login')
        return False
    return True
```

### Q6: 如何批量导入用户？

```python
from auth import auth_manager
import csv

def import_users_from_csv(filepath: str):
    """从CSV批量导入用户"""
    success_count = 0
    fail_count = 0

    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            result = auth_manager.register(
                username=row['username'],
                email=row['email'],
                password=row['password'],
                full_name=row.get('full_name', '')
            )
            if result['success']:
                success_count += 1
            else:
                fail_count += 1
                print(f"导入失败: {row['username']} - {result['message']}")

    print(f"导入完成: 成功 {success_count}, 失败 {fail_count}")
```

### Q7: 如何实现权限继承？

权限继承已内置在角色系统中：

```python
# 用户的实际权限 = 角色权限 + 直接分配的权限

# 检查权限时会自动检查：
# 1. 用户是否是超级管理员（拥有所有权限）
# 2. 用户所有角色的权限
# 3. 用户直接分配的权限

user.has_permission('content.edit')  # 自动检查所有来源
```

### Q8: 如何切换数据库？

```python
from auth import auth_config, init_database

# 切换到 MySQL
auth_config.set_database_type('mysql')
# 设置连接字符串（或使用环境变量）
os.environ['DATABASE_URL'] = 'mysql://user:pass@localhost/dbname'

# 重新初始化
init_database()

# 切换到 PostgreSQL
auth_config.set_database_type('postgresql')
os.environ['DATABASE_URL'] = 'postgresql://user:pass@localhost/dbname'
init_database()
```

---

## 完整示例

### 示例 1：完整的登录流程

```python
from nicegui import ui, app
from auth import auth_manager, require_login

# 登录页面
@ui.page('/login')
def login_page():
    with ui.card().classes('w-96 mx-auto mt-20'):
        ui.label('用户登录').classes('text-2xl font-bold mb-4')

        username = ui.input('用户名').classes('w-full')
        password = ui.input('密码', password=True).classes('w-full')
        remember = ui.checkbox('记住我')

        def handle_login():
            result = auth_manager.login(
                username.value,
                password.value,
                remember.value
            )
            if result['success']:
                ui.notify('登录成功！', type='positive')
                ui.navigate.to('/dashboard')
            else:
                ui.notify(result['message'], type='negative')

        ui.button('登录', on_click=handle_login).classes('w-full mt-4')

# 受保护的仪表板
@ui.page('/dashboard')
@require_login(redirect_to_login=True)
def dashboard_page():
    current_user = auth_manager.check_session()

    ui.label(f'欢迎，{current_user.username}！').classes('text-2xl')
    ui.label(f'邮箱：{current_user.email}')

    with ui.row():
        ui.button('个人资料', on_click=lambda: ui.navigate.to('/profile'))
        ui.button('退出', on_click=lambda: ui.navigate.to('/logout'))

# 启动应用
ui.run(storage_secret='your-secret-key-here')
```

### 示例 2：带权限控制的内容管理

```python
from nicegui import ui
from auth import require_login, require_permission, auth_manager

@ui.page('/content')
@require_login(redirect_to_login=True)
def content_page():
    current_user = auth_manager.check_session()

    ui.label('内容管理').classes('text-3xl font-bold mb-6')

    # 显示内容列表（所有人都能看）
    with ui.card():
        ui.label('内容列表')
        display_content_list()

    # 创建按钮（需要权限）
    if current_user.has_permission('content.create'):
        ui.button('创建新内容', on_click=create_content)

    # 编辑按钮（需要权限）
    if current_user.has_permission('content.edit'):
        ui.button('编辑内容', on_click=edit_content)

    # 删除按钮（需要权限）
    if current_user.has_permission('content.delete'):
        ui.button('删除内容', on_click=delete_content, color='negative')

    # 管理面板（仅管理员）
    if current_user.has_role('admin'):
        with ui.expansion('管理面板', icon='admin_panel_settings'):
            ui.button('批量操作', on_click=bulk_operations)
            ui.button('审计日志', on_click=view_audit_log)
```

---

## 总结

`webproduct_ui_template\auth` 包提供了完整的认证和权限管理解决方案：

✅ **开箱即用**：包含完整的登录、注册、权限管理页面  
✅ **灵活配置**：支持多种数据库、自定义配置  
✅ **安全可靠**：密码加密、会话管理、防暴力破解  
✅ **易于集成**：装饰器式 API，与 NiceGUI 无缝集成  
✅ **功能完整**：RBAC、细粒度权限、用户/角色/权限管理

核心使用步骤：

1. 导入并初始化：`from auth import init_database; init_database()`
2. 使用装饰器保护页面：`@require_login`, `@require_role`, `@require_permission`
3. 调用 API 进行认证操作：`auth_manager.login()`, `check_session()` 等
4. 集成管理页面：使用 `get_auth_page_handlers()` 注册路由

更多详细信息请参考项目源码和示例。
