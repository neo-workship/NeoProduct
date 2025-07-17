# Auth Manager 使用指南

## 📋 概述

`auth_manager.py` 是认证系统的核心控制器，提供完整的用户认证、会话管理和权限控制功能。虽然大多数情况下使用装饰器即可，但在某些高级场景下需要直接调用 `auth_manager` 的方法。

## 🔧 AuthManager 提供的核心功能

### 1. 用户认证管理

#### 用户注册

```python
def register(self, username: str, email: str, password: str, **kwargs) -> Dict[str, Any]
```

**功能**：用户注册，支持扩展信息
**参数**：

- `username`: 用户名（3-50 字符）
- `email`: 邮箱地址
- `password`: 密码（符合密码策略）
- `**kwargs`: 扩展信息（如 `full_name`, `phone` 等）

**返回值**：

```python
{
    'success': True/False,
    'message': '操作结果信息',
    'user': UserSession对象  # 成功时返回
}
```

#### 用户登录

```python
def login(self, username: str, password: str, remember_me: bool = False) -> Dict[str, Any]
```

**功能**：用户登录验证，支持用户名或邮箱登录
**特性**：

- 账户锁定保护（连续失败自动锁定）
- 记住我功能
- 登录日志记录
- 会话自动创建

#### 用户登出

```python
def logout(self) -> None
```

**功能**：完整的登出处理
**操作**：

- 清除数据库 token
- 清除浏览器存储
- 清除内存会话
- 重置当前用户状态

#### 会话检查

```python
def check_session(self) -> Optional[UserSession]
```

**功能**：多层会话验证
**验证流程**：

1. 检查内存缓存
2. 验证浏览器 token
3. 数据库 token 验证
4. 记住我 token 处理

### 2. 用户信息管理

#### 获取用户信息

```python
def get_user_by_id(self, user_id: int) -> Optional[UserSession]
def get_user_by_username(self, username: str) -> Optional[UserSession]
```

**功能**：获取指定用户的会话信息
**优化**：自动缓存当前用户，避免重复查询

#### 更新用户资料

```python
def update_profile(self, user_id: int, **kwargs) -> Dict[str, Any]
```

**功能**：更新用户基本信息
**支持字段**：`full_name`, `phone`, `avatar`, `bio`, `email`

#### 修改密码

```python
def change_password(self, user_id: int, old_password: str, new_password: str) -> Dict[str, Any]
```

**功能**：安全的密码修改
**安全措施**：

- 验证原密码
- 密码强度验证
- 清除所有会话（强制重新登录）

### 3. 权限控制

#### 认证状态检查

```python
def is_authenticated(self) -> bool
```

**功能**：检查当前用户是否已登录

#### 角色检查

```python
def has_role(self, role_name: str) -> bool
```

**功能**：检查当前用户是否具有指定角色
**支持**：超级管理员自动通过所有角色检查

#### 权限检查

```python
def has_permission(self, permission_name: str) -> bool
```

**功能**：检查当前用户是否具有指定权限
**层级**：用户直接权限 + 角色权限

#### 当前用户访问

```python
@property
def current_user: Optional[UserSession]
```

**功能**：获取当前登录用户的会话信息
**包含信息**：用户基本信息、角色列表、权限集合

## 🎯 使用场景分析

### 场景 1：推荐使用装饰器（90%的情况）

#### 页面级权限控制

```python
from auth.decorators import require_login, require_role, require_permission

# 简单登录验证
@require_login()
def user_dashboard():
    ui.label('用户仪表盘')

# 角色验证
@require_role('admin')
def admin_panel():
    ui.label('管理员面板')

# 权限验证
@require_permission('user_management')
def user_list():
    ui.label('用户列表')
```

#### 优势

- **简洁明了**：一行装饰器搞定权限控制
- **自动处理**：未授权时自动重定向或提示
- **代码清晰**：权限要求一目了然
- **减少错误**：避免手动权限检查遗漏

### 场景 2：需要 import auth_manager 的情况

#### A. 获取当前用户信息

```python
from auth import auth_manager

def profile_page():
    """个人资料页面"""
    user = auth_manager.current_user

    ui.label(f'欢迎，{user.username}！')
    ui.label(f'邮箱：{user.email}')
    ui.label(f'角色：{", ".join(user.roles)}')
    ui.label(f'登录次数：{user.login_count}')
```

#### B. 动态权限检查

```python
from auth import auth_manager

def dynamic_menu():
    """根据权限动态显示菜单"""
    user = auth_manager.current_user

    # 基础菜单
    ui.button('首页', on_click=lambda: navigate_to('home'))

    # 管理员菜单
    if user.has_role('admin'):
        ui.button('用户管理', on_click=lambda: navigate_to('user_management'))
        ui.button('系统设置', on_click=lambda: navigate_to('settings'))

    # 基于权限的菜单
    if user.has_permission('data_export'):
        ui.button('数据导出', on_click=data_export)

    if user.has_permission('report_view'):
        ui.button('报表查看', on_click=view_reports)
```

#### C. 业务逻辑中的权限控制

```python
from auth import auth_manager

def process_data_export(export_type: str):
    """数据导出处理"""
    user = auth_manager.current_user

    # 基础权限检查
    if not user.has_permission('data_export'):
        ui.notify('您没有数据导出权限', type='error')
        return

    # 高级权限检查
    if export_type == 'sensitive' and not user.has_role('senior_admin'):
        ui.notify('敏感数据导出需要高级管理员权限', type='error')
        return

    # 执行导出逻辑
    perform_export(export_type, user.id)
```

#### D. 用户状态管理

```python
from auth import auth_manager

def user_status_widget():
    """用户状态小组件"""
    if not auth_manager.is_authenticated():
        ui.button('登录', on_click=lambda: ui.navigate.to('/login'))
        return

    user = auth_manager.current_user

    with ui.row().classes('items-center gap-2'):
        # 用户头像
        ui.avatar(user.avatar or '/static/images/default_avatar.png')

        # 用户信息
        with ui.column().classes('gap-0'):
            ui.label(user.full_name or user.username).classes('font-medium')
            ui.label(f'角色：{", ".join(user.roles)}').classes('text-sm text-gray-600')

        # 登出按钮
        ui.button('登出', icon='logout', on_click=auth_manager.logout)
```

#### E. 表单处理和验证

```python
from auth import auth_manager

def handle_profile_update():
    """处理个人资料更新"""
    user = auth_manager.current_user

    # 收集表单数据
    new_full_name = full_name_input.value
    new_phone = phone_input.value
    new_bio = bio_input.value

    # 调用 auth_manager 更新
    result = auth_manager.update_profile(
        user_id=user.id,
        full_name=new_full_name,
        phone=new_phone,
        bio=new_bio
    )

    if result['success']:
        ui.notify('资料更新成功', type='positive')
        # 可能需要刷新当前用户信息
    else:
        ui.notify(result['message'], type='negative')

def handle_password_change():
    """处理密码修改"""
    user = auth_manager.current_user

    result = auth_manager.change_password(
        user_id=user.id,
        old_password=old_password_input.value,
        new_password=new_password_input.value
    )

    if result['success']:
        ui.notify('密码修改成功，请重新登录', type='positive')
        ui.navigate.to('/login')
    else:
        ui.notify(result['message'], type='negative')
```

#### F. 获取其他用户信息（管理员功能）

```python
from auth import auth_manager

@require_role('admin')
def user_detail_page(user_id: int):
    """用户详情页面（管理员查看）"""

    # 获取指定用户信息
    target_user = auth_manager.get_user_by_id(user_id)
    if not target_user:
        ui.notify('用户不存在', type='error')
        return

    # 显示用户信息
    ui.label(f'用户详情：{target_user.username}')
    ui.label(f'邮箱：{target_user.email}')
    ui.label(f'角色：{", ".join(target_user.roles)}')
    ui.label(f'注册时间：{target_user.created_at}')
    ui.label(f'最后登录：{target_user.last_login}')
```

## 🏗️ 在 header_pages 和 menu_pages 中的使用

### ✅ 完全可以在这些包中使用

#### 1. header_pages 使用示例

```python
# header_pages/user_menu.py
from nicegui import ui
from auth import auth_manager
from auth.decorators import require_login

@require_login()
def user_menu_content():
    """用户菜单内容"""
    user = auth_manager.current_user

    with ui.dropdown_button(user.username, icon='person'):
        with ui.item(on_click=lambda: navigate_to('profile')):
            ui.item_section(avatar=True)
            ui.icon('person')
            ui.item_section().text('个人资料')

        with ui.item(on_click=lambda: navigate_to('settings')):
            ui.item_section(avatar=True)
            ui.icon('settings')
            ui.item_section().text('账户设置')

        # 管理员菜单
        if user.has_role('admin'):
            ui.separator()
            with ui.item(on_click=lambda: navigate_to('admin_panel')):
                ui.item_section(avatar=True)
                ui.icon('admin_panel_settings')
                ui.item_section().text('管理面板')

        ui.separator()
        with ui.item(on_click=auth_manager.logout):
            ui.item_section(avatar=True)
            ui.icon('logout')
            ui.item_section().text('退出登录')
```

```python
# header_pages/notifications.py
from nicegui import ui
from auth import auth_manager
from auth.decorators import require_login

@require_login()
def notifications_content():
    """通知中心"""
    user = auth_manager.current_user

    ui.label('通知中心').classes('text-2xl font-bold')

    # 根据用户角色显示不同通知
    if user.has_role('admin'):
        ui.label('🔧 系统维护通知').classes('text-lg')
        ui.label('📊 系统报告可用').classes('text-lg')

    if user.has_permission('data_access'):
        ui.label('📈 新数据报告').classes('text-lg')

    ui.label('👋 欢迎回来！').classes('text-lg')
```

#### 2. menu_pages 使用示例

```python
# menu_pages/dashboard.py
from nicegui import ui
from auth import auth_manager
from auth.decorators import require_login

@require_login()
def dashboard_page_content():
    """仪表盘页面"""
    user = auth_manager.current_user

    # 个性化欢迎
    ui.label(f'欢迎回来，{user.full_name or user.username}！').classes('text-3xl font-bold')

    # 基于角色的功能区域
    with ui.row().classes('w-full gap-6'):
        # 用户统计卡片
        with ui.card().classes('p-6'):
            ui.label('个人统计').classes('text-xl font-semibold mb-4')
            ui.label(f'登录次数：{user.login_count}')
            ui.label(f'账户角色：{", ".join(user.roles)}')
            ui.label(f'上次登录：{user.last_login or "首次登录"}')

        # 管理员专属功能
        if user.has_role('admin'):
            with ui.card().classes('p-6'):
                ui.label('管理功能').classes('text-xl font-semibold mb-4')
                ui.button('用户管理', icon='people',
                         on_click=lambda: navigate_to('user_management'))
                ui.button('系统监控', icon='monitor',
                         on_click=lambda: navigate_to('system_monitor'))

        # 基于权限的功能
        if user.has_permission('data_analysis'):
            with ui.card().classes('p-6'):
                ui.label('数据分析').classes('text-xl font-semibold mb-4')
                ui.button('数据报表', icon='analytics',
                         on_click=lambda: navigate_to('reports'))
                ui.button('趋势分析', icon='trending_up',
                         on_click=lambda: navigate_to('trends'))
```

```python
# menu_pages/settings.py
from nicegui import ui
from auth import auth_manager
from auth.decorators import require_login

@require_login()
def settings_page_content():
    """设置页面"""
    user = auth_manager.current_user

    ui.label('账户设置').classes('text-3xl font-bold mb-6')

    # 基本信息设置
    with ui.card().classes('w-full p-6 mb-6'):
        ui.label('基本信息').classes('text-xl font-semibold mb-4')

        full_name = ui.input('姓名', value=user.full_name or '').classes('w-full mb-2')
        phone = ui.input('电话', value=user.phone or '').classes('w-full mb-2')
        bio = ui.textarea('个人简介', value=user.bio or '').classes('w-full mb-4')

        def save_profile():
            result = auth_manager.update_profile(
                user_id=user.id,
                full_name=full_name.value,
                phone=phone.value,
                bio=bio.value
            )

            if result['success']:
                ui.notify('资料更新成功', type='positive')
            else:
                ui.notify(result['message'], type='negative')

        ui.button('保存资料', icon='save', on_click=save_profile)

    # 密码修改
    with ui.card().classes('w-full p-6 mb-6'):
        ui.label('修改密码').classes('text-xl font-semibold mb-4')

        old_password = ui.input('当前密码', password=True).classes('w-full mb-2')
        new_password = ui.input('新密码', password=True).classes('w-full mb-2')
        confirm_password = ui.input('确认新密码', password=True).classes('w-full mb-4')

        def change_password():
            if new_password.value != confirm_password.value:
                ui.notify('两次输入的密码不一致', type='negative')
                return

            result = auth_manager.change_password(
                user_id=user.id,
                old_password=old_password.value,
                new_password=new_password.value
            )

            if result['success']:
                ui.notify('密码修改成功，请重新登录', type='positive')
                ui.navigate.to('/login')
            else:
                ui.notify(result['message'], type='negative')

        ui.button('修改密码', icon='lock', on_click=change_password)

    # 权限信息（只读）
    with ui.card().classes('w-full p-6'):
        ui.label('权限信息').classes('text-xl font-semibold mb-4')
        ui.label(f'用户角色：{", ".join(user.roles)}')
        ui.label(f'权限数量：{len(user.permissions)}')

        if user.is_superuser:
            ui.label('🌟 超级管理员').classes('text-lg text-yellow-600 font-medium')
```

## 📋 最佳实践建议

### 1. 优先使用装饰器

```python
# ✅ 推荐：页面级权限控制
@require_role('admin')
def admin_page():
    pass

# ❌ 不推荐：手动权限检查
def admin_page():
    if not auth_manager.has_role('admin'):
        ui.notify('权限不足')
        return
```

### 2. 合理使用 auth_manager

```python
# ✅ 适合的场景：获取用户信息
user = auth_manager.current_user
ui.label(f'欢迎，{user.username}')

# ✅ 适合的场景：动态权限控制
if user.has_permission('advanced_feature'):
    ui.button('高级功能')

# ✅ 适合的场景：业务逻辑处理
result = auth_manager.update_profile(user.id, full_name='新名字')
```

### 3. 错误处理

```python
# ✅ 推荐：完整的错误处理
result = auth_manager.login(username, password)
if result['success']:
    ui.notify('登录成功', type='positive')
    ui.navigate.to('/dashboard')
else:
    ui.notify(result['message'], type='negative')
```

### 4. 性能考虑

```python
# ✅ 推荐：缓存用户信息
user = auth_manager.current_user
if user:
    # 在函数内多次使用 user，避免重复调用
    pass

# ❌ 避免：重复调用
if auth_manager.current_user.has_role('admin'):
    name = auth_manager.current_user.username  # 重复调用
```

## 🎯 总结

### 使用装饰器的场景（推荐）：

- 页面级权限控制
- 简单的角色/权限验证
- 标准的认证流程

### 使用 auth_manager 的场景（高级）：

- 获取当前用户详细信息
- 动态权限检查和菜单生成
- 用户资料更新和密码修改
- 复杂的业务逻辑权限控制
- 管理员功能（查看其他用户信息）

### 在 header_pages 和 menu_pages 中：

- **完全支持**使用 auth_manager
- **推荐场景**：用户信息显示、动态菜单、个性化内容
- **最佳实践**：装饰器 + auth_manager 结合使用

通过合理使用装饰器和 auth_manager，可以构建既安全又用户友好的认证系统。
