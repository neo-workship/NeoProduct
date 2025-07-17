# DetachedHelper 使用指南

## 📋 概述

`detached_helper.py` 是专门解决 SQLAlchemy `DetachedInstanceError` 问题的工具模块。它提供了安全的数据访问方法，避免在数据库会话关闭后访问关联对象时出现的错误。

## 🚨 DetachedInstanceError 问题解析

### 问题根源

```python
# ❌ 会导致 DetachedInstanceError 的代码
def get_user_info(user_id):
    with get_db() as db:
        user = db.query(User).filter(User.id == user_id).first()
        return user  # 返回 SQLAlchemy 对象

def display_user():
    user = get_user_info(1)
    # 💥 DetachedInstanceError！数据库会话已关闭
    print(user.roles)  # 访问关联对象失败
    print(user.permissions)  # 访问关联对象失败
```

### 问题发生时机

1. **会话关闭后访问关联对象**：`user.roles`, `user.permissions`
2. **跨函数传递 SQLAlchemy 对象**：对象脱离了原始数据库会话
3. **延迟加载失败**：关联数据没有在会话内预加载

## 🔧 DetachedHelper 提供的功能

### 1. 核心数据类

#### DetachedUser 数据类

```python
@dataclass
class DetachedUser:
    """分离的用户数据类 - 不依赖SQLAlchemy会话"""
    id: int
    username: str
    email: str
    full_name: Optional[str] = None
    # ... 基本字段

    # 重要：关联数据已提取为普通Python对象
    roles: List[str] = field(default_factory=list)  # 角色名称列表
    permissions: List[str] = field(default_factory=list)  # 权限名称列表
    locked_until: Optional[datetime] = None  # 锁定状态

    def has_role(self, role_name: str) -> bool:
        """检查是否有指定角色"""
        return role_name in self.roles

    def has_permission(self, permission_name: str) -> bool:
        """检查是否有指定权限"""
        return self.is_superuser or permission_name in self.permissions

    def is_locked(self) -> bool:
        """检查用户是否被锁定"""
        return self.locked_until is not None and self.locked_until > datetime.now()
```

#### DetachedRole 数据类

```python
@dataclass
class DetachedRole:
    """分离的角色数据类"""
    id: int
    name: str
    display_name: Optional[str] = None
    description: Optional[str] = None
    is_active: bool = True
    is_system: bool = False

    # 关联数据
    permissions: List[str] = field(default_factory=list)  # 权限名称列表
    user_count: int = 0  # 用户数量
    users: List[str] = field(default_factory=list)  # 用户名列表
```

### 2. 数据访问函数

#### 用户数据访问

```python
def get_user_safe(user_id: int) -> Optional[DetachedUser]
def get_users_safe(search_term: str = None, limit: int = None) -> List[DetachedUser]
def update_user_safe(user_id: int, **update_data) -> bool
def delete_user_safe(user_id: int) -> bool
```

#### 角色数据访问

```python
def get_role_safe(role_id: int) -> Optional[DetachedRole]
def get_roles_safe() -> List[DetachedRole]
def update_role_safe(role_id: int, **update_data) -> bool
def delete_role_safe(role_id: int) -> bool
def create_role_safe(name: str, display_name: str = None, description: str = None) -> Optional[int]
```

#### 用户锁定管理

```python
def lock_user_safe(user_id: int, lock_duration_minutes: int = 30) -> bool
def unlock_user_safe(user_id: int) -> bool
def batch_unlock_users_safe() -> int
```

### 3. 统计功能

```python
# 通过 detached_manager 访问
detached_manager.get_user_statistics()  # 用户统计
detached_manager.get_role_statistics()  # 角色统计
```

## 🎯 使用场景分析

### 场景 1：当前主要使用（auth/pages 中）

#### 用户管理页面

```python
# auth/pages/user_management_page.py
from ..detached_helper import (
    detached_manager,
    get_users_safe,
    get_user_safe,
    update_user_safe,
    delete_user_safe,
    lock_user_safe
)

def user_management_page():
    # ✅ 安全获取用户列表，不会有DetachedInstanceError
    users = get_users_safe()

    for user in users:
        ui.label(f'{user.username} - {", ".join(user.roles)}')

        if user.is_locked():
            ui.label('🔒 账户已锁定').classes('text-red-600')
```

#### 角色管理页面

```python
# auth/pages/role_management_page.py
from ..detached_helper import (
    get_roles_safe,
    get_role_safe,
    update_role_safe,
    create_role_safe
)

def role_management_page():
    # ✅ 安全获取角色列表
    roles = get_roles_safe()

    for role in roles:
        ui.label(f'{role.name} - {role.user_count}个用户')
        ui.label(f'权限：{", ".join(role.permissions)}')
```

### 场景 2：需要 import 使用的情况

#### A. 显示用户列表和统计信息

```python
from auth.detached_helper import get_users_safe, get_user_safe

def user_statistics_widget():
    """用户统计小组件"""
    users = get_users_safe(limit=10)  # 获取最近10个用户

    ui.label(f'系统用户：{len(users)}')

    for user in users:
        with ui.row().classes('items-center gap-2'):
            ui.avatar(user.avatar or '/static/default_avatar.png')
            ui.label(user.username)

            # 显示角色标签
            for role in user.roles:
                ui.badge(role).classes('bg-blue-500')

            # 显示状态
            if user.is_locked():
                ui.badge('锁定').classes('bg-red-500')
            elif user.is_active:
                ui.badge('活跃').classes('bg-green-500')
```

#### B. 搜索和过滤功能

```python
from auth.detached_helper import get_users_safe

def user_search_component():
    """用户搜索组件"""
    search_input = ui.input('搜索用户', placeholder='输入用户名、邮箱或姓名')
    results_container = ui.column()

    def search_users():
        results_container.clear()

        # ✅ 安全搜索，支持模糊匹配
        users = get_users_safe(search_term=search_input.value, limit=20)

        if not users:
            with results_container:
                ui.label('未找到匹配的用户').classes('text-gray-500')
            return

        with results_container:
            for user in users:
                with ui.card().classes('p-4 mb-2'):
                    ui.label(f'{user.username} ({user.email})')
                    ui.label(f'角色：{", ".join(user.roles)}').classes('text-sm text-gray-600')

                    # 显示特殊状态
                    if user.is_superuser:
                        ui.badge('超级管理员').classes('bg-purple-500')
                    if user.is_locked():
                        ui.badge('已锁定').classes('bg-red-500')

    search_input.on('input', search_users)
```

#### C. 角色和权限展示

```python
from auth.detached_helper import get_roles_safe, get_role_safe

def role_overview_component():
    """角色概览组件"""
    roles = get_roles_safe()

    ui.label('系统角色概览').classes('text-xl font-bold mb-4')

    with ui.grid(columns=3).classes('gap-4'):
        for role in roles:
            with ui.card().classes('p-4'):
                # 角色基本信息
                ui.label(role.display_name or role.name).classes('text-lg font-semibold')
                ui.label(role.description or '暂无描述').classes('text-sm text-gray-600')

                # 统计信息
                ui.label(f'用户数：{role.user_count}').classes('text-sm')
                ui.label(f'权限数：{len(role.permissions)}').classes('text-sm')

                # 状态标签
                if role.is_system:
                    ui.badge('系统角色').classes('bg-gray-500')
                if not role.is_active:
                    ui.badge('已禁用').classes('bg-red-500')

def role_detail_popup(role_id: int):
    """角色详情弹窗"""
    role = get_role_safe(role_id)
    if not role:
        ui.notify('角色不存在', type='error')
        return

    with ui.dialog() as dialog:
        with ui.card().classes('w-96'):
            ui.label(f'角色详情：{role.name}').classes('text-lg font-bold mb-4')

            # 基本信息
            ui.label(f'显示名称：{role.display_name or "未设置"}')
            ui.label(f'描述：{role.description or "暂无描述"}')
            ui.label(f'创建时间：{role.created_at}')

            # 权限列表
            if role.permissions:
                ui.label('权限列表：').classes('font-semibold mt-4')
                for perm in role.permissions:
                    ui.badge(perm).classes('mr-1 mb-1')

            # 用户列表
            if role.users:
                ui.label('关联用户：').classes('font-semibold mt-4')
                for username in role.users:
                    ui.label(f'• {username}')

    dialog.open()
```

#### D. 数据分析和报表

```python
from auth.detached_helper import detached_manager, get_users_safe

def user_analytics_dashboard():
    """用户分析仪表盘"""
    # 获取统计数据
    stats = detached_manager.get_user_statistics()

    # 统计卡片
    with ui.row().classes('gap-4 mb-6'):
        with ui.card().classes('p-4'):
            ui.label('总用户数').classes('text-sm text-gray-600')
            ui.label(str(stats['total_users'])).classes('text-2xl font-bold')

        with ui.card().classes('p-4'):
            ui.label('活跃用户').classes('text-sm text-gray-600')
            ui.label(str(stats['active_users'])).classes('text-2xl font-bold')

        with ui.card().classes('p-4'):
            ui.label('锁定用户').classes('text-sm text-gray-600')
            ui.label(str(stats.get('locked_users', 0))).classes('text-2xl font-bold text-red-600')

    # 角色分布分析
    users = get_users_safe()
    role_counts = {}

    for user in users:
        for role in user.roles:
            role_counts[role] = role_counts.get(role, 0) + 1

    ui.label('角色分布').classes('text-lg font-bold mt-6 mb-4')

    with ui.row().classes('gap-2'):
        for role, count in role_counts.items():
            ui.badge(f'{role}: {count}').classes('text-lg p-2')
```

### 场景 3：需要避免 DetachedInstanceError 的情况

#### 跨模块数据传递

```python
# ❌ 错误做法 - 传递SQLAlchemy对象
def get_user_from_db(user_id):
    with get_db() as db:
        return db.query(User).filter(User.id == user_id).first()

def process_user_data():
    user = get_user_from_db(1)
    # 💥 DetachedInstanceError！
    print(user.roles)

# ✅ 正确做法 - 使用DetachedUser
from auth.detached_helper import get_user_safe

def process_user_data():
    user = get_user_safe(1)  # 返回DetachedUser
    # ✅ 安全访问
    print(user.roles)  # List[str]，不会出错
```

#### 异步操作中的数据访问

```python
from auth.detached_helper import get_user_safe

async def send_user_notification(user_id: int):
    """发送用户通知（异步操作）"""
    # ✅ 在异步函数中安全获取用户数据
    user = get_user_safe(user_id)
    if not user:
        return

    # 可以安全访问用户信息
    message = f"您好 {user.username}，您有新的通知"

    # 根据用户角色发送不同类型的通知
    if 'admin' in user.roles:
        await send_admin_notification(user.email, message)
    else:
        await send_regular_notification(user.email, message)
```

## 🏗️ 在 header_pages 和 menu_pages 中的使用

### ✅ 完全可以使用！

#### 1. header_pages 使用示例

```python
# header_pages/user_status.py
from nicegui import ui
from auth import auth_manager
from auth.detached_helper import get_user_safe
from auth.decorators import require_login

@require_login()
def user_status_header():
    """用户状态头部组件"""
    current_user = auth_manager.current_user

    # 获取更详细的用户信息（包括最新状态）
    user_detail = get_user_safe(current_user.id)

    with ui.row().classes('items-center gap-3'):
        # 用户头像
        ui.avatar(user_detail.avatar or '/static/default_avatar.png')

        # 用户信息
        with ui.column().classes('gap-0'):
            ui.label(user_detail.full_name or user_detail.username).classes('font-medium')

            # 显示角色标签
            with ui.row().classes('gap-1'):
                for role in user_detail.roles:
                    ui.badge(role).classes('text-xs')

            # 显示特殊状态
            if user_detail.is_superuser:
                ui.label('🌟 超级管理员').classes('text-xs text-yellow-600')

            if user_detail.is_locked():
                remaining = user_detail.get_lock_remaining_minutes()
                ui.label(f'🔒 账户锁定中 ({remaining}分钟)').classes('text-xs text-red-600')
```

```python
# header_pages/system_status.py
from nicegui import ui
from auth.detached_helper import detached_manager, get_users_safe
from auth.decorators import require_role

@require_role('admin')
def system_status_header():
    """系统状态头部组件（管理员可见）"""
    # 获取系统统计
    stats = detached_manager.get_user_statistics()

    with ui.row().classes('items-center gap-4'):
        # 在线用户数
        ui.label(f'👥 {stats["active_users"]}').classes('text-sm')

        # 锁定用户数
        locked_count = stats.get('locked_users', 0)
        if locked_count > 0:
            ui.label(f'🔒 {locked_count}').classes('text-sm text-red-600')

        # 快速解锁按钮
        if locked_count > 0:
            def batch_unlock():
                from auth.detached_helper import batch_unlock_users_safe
                unlocked = batch_unlock_users_safe()
                ui.notify(f'已解锁 {unlocked} 个用户账户', type='positive')

            ui.button('批量解锁', size='sm', on_click=batch_unlock)
```

#### 2. menu_pages 使用示例

```python
# menu_pages/user_center.py
from nicegui import ui
from auth import auth_manager
from auth.detached_helper import get_user_safe, get_users_safe
from auth.decorators import require_login

@require_login()
def user_center_page():
    """用户中心页面"""
    current_user = auth_manager.current_user

    # 获取详细用户信息
    user_detail = get_user_safe(current_user.id)

    ui.label('用户中心').classes('text-3xl font-bold mb-6')

    # 用户信息卡片
    with ui.card().classes('w-full p-6 mb-6'):
        with ui.row().classes('items-center gap-4'):
            ui.avatar(user_detail.avatar or '/static/default_avatar.png', size='lg')

            with ui.column():
                ui.label(user_detail.full_name or user_detail.username).classes('text-xl font-bold')
                ui.label(user_detail.email).classes('text-gray-600')

                # 角色信息
                with ui.row().classes('gap-2 mt-2'):
                    for role in user_detail.roles:
                        ui.badge(role)

                # 状态信息
                status_info = []
                if user_detail.is_superuser:
                    status_info.append('超级管理员')
                if user_detail.is_verified:
                    status_info.append('已验证')
                if user_detail.is_locked():
                    status_info.append('账户锁定')

                if status_info:
                    ui.label(' | '.join(status_info)).classes('text-sm text-blue-600')

    # 用户统计
    with ui.card().classes('w-full p-6'):
        ui.label('账户统计').classes('text-lg font-bold mb-4')

        with ui.grid(columns=3).classes('gap-4'):
            ui.label(f'登录次数：{user_detail.login_count}')
            ui.label(f'注册时间：{user_detail.created_at.strftime("%Y-%m-%d") if user_detail.created_at else "未知"}')
            ui.label(f'最后登录：{user_detail.last_login.strftime("%Y-%m-%d %H:%M") if user_detail.last_login else "未知"}')
```

```python
# menu_pages/team_overview.py
from nicegui import ui
from auth.detached_helper import get_users_safe, get_roles_safe
from auth.decorators import require_permission

@require_permission('team_view')
def team_overview_page():
    """团队概览页面"""
    ui.label('团队概览').classes('text-3xl font-bold mb-6')

    # 获取团队成员
    team_members = get_users_safe(limit=50)  # 限制50个用户

    # 按角色分组显示
    roles = get_roles_safe()

    for role in roles:
        if not role.is_active:
            continue

        # 过滤该角色的用户
        role_users = [user for user in team_members if role.name in user.roles]

        if not role_users:
            continue

        ui.label(f'{role.display_name or role.name} ({len(role_users)}人)').classes('text-xl font-bold mt-6 mb-4')

        with ui.grid(columns=4).classes('gap-4'):
            for user in role_users:
                with ui.card().classes('p-4 text-center'):
                    ui.avatar(user.avatar or '/static/default_avatar.png')
                    ui.label(user.full_name or user.username).classes('font-medium mt-2')
                    ui.label(user.email).classes('text-sm text-gray-600')

                    # 状态指示
                    if user.is_superuser:
                        ui.badge('超管').classes('bg-purple-500 mt-1')
                    elif user.is_locked():
                        ui.badge('锁定').classes('bg-red-500 mt-1')
                    elif user.is_active:
                        ui.badge('活跃').classes('bg-green-500 mt-1')
```

```python
# menu_pages/admin_dashboard.py
from nicegui import ui
from auth.detached_helper import detached_manager, get_users_safe, get_roles_safe
from auth.decorators import require_role

@require_role('admin')
def admin_dashboard_page():
    """管理员仪表盘"""
    ui.label('管理员仪表盘').classes('text-3xl font-bold mb-6')

    # 系统统计
    user_stats = detached_manager.get_user_statistics()
    role_stats = detached_manager.get_role_statistics()

    with ui.row().classes('gap-6 mb-6'):
        # 用户统计卡片
        with ui.card().classes('p-6'):
            ui.label('用户统计').classes('text-lg font-bold mb-4')
            ui.label(f'总用户：{user_stats["total_users"]}')
            ui.label(f'活跃用户：{user_stats["active_users"]}')
            ui.label(f'已验证：{user_stats["verified_users"]}')
            ui.label(f'管理员：{user_stats["admin_users"]}')

        # 角色统计卡片
        with ui.card().classes('p-6'):
            ui.label('角色统计').classes('text-lg font-bold mb-4')
            ui.label(f'总角色：{role_stats["total_roles"]}')
            ui.label(f'活跃角色：{role_stats["active_roles"]}')
            ui.label(f'系统角色：{role_stats["system_roles"]}')

    # 最近用户活动
    recent_users = get_users_safe(limit=10)

    ui.label('最近用户').classes('text-xl font-bold mb-4')

    with ui.table(columns=[
        {'name': 'username', 'label': '用户名'},
        {'name': 'email', 'label': '邮箱'},
        {'name': 'roles', 'label': '角色'},
        {'name': 'last_login', 'label': '最后登录'},
        {'name': 'status', 'label': '状态'}
    ], rows=[]).classes('w-full') as table:

        for user in recent_users:
            # 状态标签
            status_badges = []
            if user.is_superuser:
                status_badges.append('超管')
            if user.is_locked():
                status_badges.append('锁定')
            elif user.is_active:
                status_badges.append('活跃')

            table.add_row({
                'username': user.username,
                'email': user.email,
                'roles': ', '.join(user.roles),
                'last_login': user.last_login.strftime('%Y-%m-%d %H:%M') if user.last_login else '从未',
                'status': ' | '.join(status_badges)
            })
```

## 📋 使用建议和最佳实践

### 1. 何时使用 DetachedHelper

#### ✅ 推荐使用的场景：

- **数据展示页面**：用户列表、角色列表等
- **统计分析**：用户统计、角色分布等
- **搜索功能**：用户搜索、角色搜索
- **跨模块数据传递**：避免 DetachedInstanceError
- **异步操作**：在异步函数中访问用户数据
- **批量操作**：批量更新、批量锁定等

#### ❌ 不推荐使用的场景：

- **简单权限检查**：使用装饰器或 auth_manager.current_user
- **当前用户信息**：直接使用 auth_manager.current_user
- **实时数据要求极高**：DetachedHelper 有数据延迟

### 2. 性能考虑

```python
# ✅ 推荐：一次获取，多次使用
users = get_users_safe()
for user in users:
    process_user(user)

# ❌ 避免：多次调用
for user_id in user_ids:
    user = get_user_safe(user_id)  # 多次数据库查询
    process_user(user)
```

### 3. 错误处理

```python
# ✅ 推荐：完整的错误处理
user = get_user_safe(user_id)
if not user:
    ui.notify('用户不存在', type='error')
    return

# 安全访问
print(f"用户角色：{user.roles}")
```

### 4. 数据一致性

```python
# ⚠️ 注意：DetachedHelper 返回的是快照数据
user = get_user_safe(user_id)
print(f"角色：{user.roles}")  # 查询时的角色

# 如果其他地方修改了用户角色，需要重新获取
user = get_user_safe(user_id)  # 获取最新数据
print(f"更新后角色：{user.roles}")
```

## 🎯 总结

### DetachedHelper 的核心价值：

1. **解决技术问题**：彻底避免 DetachedInstanceError
2. **提供安全访问**：预加载所有关联数据
3. **简化开发**：提供便捷的数据访问函数
4. **支持复杂操作**：用户锁定、批量操作等

### 使用原则：

1. **数据展示场景**：优先使用 DetachedHelper
2. **权限检查**：优先使用装饰器和 auth_manager
3. **性能考虑**：批量获取，避免循环查询
4. **错误处理**：检查返回值，处理 None 情况

### 在 header_pages 和 menu_pages 中：

- **完全支持使用**
- **推荐场景**：用户列表、团队展示、统计分析
- **避免场景**：简单的当前用户信息获取

通过合理使用 DetachedHelper，可以构建更稳定、更高效的用户界面，避免 SQLAlchemy 相关的技术问题。
