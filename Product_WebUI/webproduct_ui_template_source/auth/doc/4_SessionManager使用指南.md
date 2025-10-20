# SessionManager 完整使用指南

## 📋 概述

`session_manager.py` 是用于管理用户会话和缓存的核心组件，提供内存中的用户会话存储，避免频繁的数据库查询。

## 🔧 核心组件

### 1. UserSession 数据类

```python
@dataclass
class UserSession:
    """用户会话数据类 - 内存中的用户信息"""
    id: int
    username: str
    email: str
    full_name: Optional[str] = None
    # ... 其他字段
    roles: list = field(default_factory=list)
    permissions: set = field(default_factory=set)

    def has_role(self, role_name: str) -> bool:
        """检查是否有指定角色"""
        return role_name in self.roles

    def has_permission(self, permission_name: str) -> bool:
        """检查是否有指定权限"""
        return self.is_superuser or permission_name in self.permissions
```

### 2. SessionManager 管理器

```python
class SessionManager:
    """会话管理器"""

    def __init__(self):
        self._sessions: Dict[str, UserSession] = {}  # 内存存储

    def create_session(self, token: str, user) -> UserSession
    def get_session(self, token: str) -> Optional[UserSession]
    def delete_session(self, token: str)
    def clear_all_sessions(self)
```

## 🕒 Session 生命周期详解

### 1. 什么时候、在哪里生成 Session

**时机**：用户登录成功时
**位置**：`auth_manager.py` 的 `login()` 方法

```python
def login(self, username: str, password: str, remember_me: bool = False):
    """用户登录流程"""
    with get_db() as db:
        # 1. 验证用户凭据
        user = db.query(User).filter(...).first()
        if not user.check_password(password):
            return {'success': False, 'message': '密码错误'}

        # 2. 生成会话令牌
        session_token = user.generate_session_token()  # 生成唯一token

        # 3. 保存到NiceGUI用户存储
        app.storage.user[self._session_key] = session_token

        # 4. 创建内存会话 ⭐️ 这里生成session
        user_session = session_manager.create_session(session_token, user)
        self.current_user = user_session

        return {'success': True, 'user': user_session}
```

**生成过程**：

1. 用户登录验证成功
2. 生成唯一的 `session_token`
3. 将 `session_token` 保存到 `app.storage.user`
4. 调用 `session_manager.create_session()` 创建内存会话
5. 将 `UserSession` 对象保存到 `auth_manager.current_user`

### 2. 什么时候需要调用/使用

**主要调用场景**：

#### A. 装饰器中的自动调用

```python
@require_login()
def protected_page():
    # 装饰器内部会自动调用
    user = auth_manager.check_session()  # 内部使用session_manager
    if not user:
        ui.navigate.to('/login')
        return
    # 页面逻辑...
```

#### B. 页面中获取当前用户

```python
def home_page_content():
    """首页内容"""
    from auth import auth_manager

    # 获取当前用户会话
    user = auth_manager.current_user  # 来自session_manager

    ui.label(f'欢迎，{user.username}！')

    # 根据角色显示不同内容
    if user.has_role('admin'):
        ui.button('管理面板', on_click=admin_panel)
```

#### C. 权限检查

```python
def feature_button():
    """根据权限显示功能按钮"""
    user = auth_manager.current_user

    if user.has_permission('data_export'):
        ui.button('导出数据', on_click=export_data)

    if user.has_role('admin'):
        ui.button('用户管理', on_click=user_management)
```

#### D. 会话状态检查

```python
def check_auth_status():
    """检查认证状态"""
    user = auth_manager.check_session()  # 内部使用session_manager

    if user:
        print(f"用户 {user.username} 已登录")
        return True
    else:
        print("用户未登录")
        return False
```

### 3. 与 app.storage.user.get(self.\_session_key) 的关系

**两者的关系和作用**：

```python
# 在 auth_manager.py 中
class AuthManager:
    def __init__(self):
        self._session_key = 'auth_session_token'  # 存储在浏览器的key
        self._remember_key = 'auth_remember_token'

    def check_session(self) -> Optional[UserSession]:
        """检查会话状态的多层机制"""

        # 第1层：从浏览器存储获取token
        session_token = app.storage.user.get(self._session_key)

        if session_token:
            # 第2层：从内存缓存获取会话
            user_session = session_manager.get_session(session_token)
            if user_session:
                return user_session  # 命中缓存，直接返回

            # 第3层：从数据库验证并重建会话
            with get_db() as db:
                user = db.query(User).filter(
                    User.session_token == session_token
                ).first()

                if user:
                    # 重建内存会话
                    user_session = session_manager.create_session(session_token, user)
                    return user_session

        return None
```

**关系图解**：

```
浏览器存储 (app.storage.user)
    ↓ 存储 session_token
    ↓
内存缓存 (session_manager)
    ↓ 存储 UserSession 对象
    ↓
数据库 (User.session_token)
    ↓ 持久化存储
```

**各层的作用**：

1. **`app.storage.user`** (浏览器存储)：

   - 存储用户的 `session_token` 和 `remember_token`
   - 页面刷新后依然存在
   - 用于识别用户身份

2. **`session_manager`** (内存缓存)：

   - 存储完整的 `UserSession` 对象
   - 包含用户信息、角色、权限等
   - 避免频繁查询数据库
   - 应用重启后消失

3. **`User.session_token`** (数据库)：
   - 持久化存储 token
   - 用于验证 token 有效性
   - 支持跨设备登录管理

### 4. 什么时候销毁

**销毁时机**：

#### A. 用户主动登出

```python
def logout(self):
    """用户登出 - 销毁会话"""
    session_token = app.storage.user.get(self._session_key)

    if self.current_user:
        # 1. 清除数据库中的token
        with get_db() as db:
            user = db.query(User).filter(User.id == self.current_user.id).first()
            if user:
                user.session_token = None
                user.remember_token = None
                db.commit()

    # 2. 清除内存会话缓存 ⭐️
    if session_token:
        session_manager.delete_session(session_token)

    # 3. 清除浏览器存储
    app.storage.user.clear()

    # 4. 清除当前用户引用
    self.current_user = None
```

#### B. 修改密码时（安全考虑）

```python
def change_password(self, user_id: int, old_password: str, new_password: str):
    """修改密码 - 清除所有会话"""
    with get_db() as db:
        user = db.query(User).filter(User.id == user_id).first()

        # 设置新密码
        user.set_password(new_password)

        # 清除所有会话（安全考虑）⭐️
        user.session_token = None
        user.remember_token = None

        db.commit()

    # 用户需要重新登录
    return {'success': True, 'message': '密码修改成功，请重新登录'}
```

#### C. 应用重启时

```python
# 应用重启时，内存中的 session_manager._sessions 会被清空
# 但浏览器存储中的 token 依然存在
# 下次访问时会触发从数据库重建会话的机制
```

#### D. 会话过期（可扩展）

```python
# 可以扩展添加会话过期机制
def cleanup_expired_sessions(self):
    """清理过期会话"""
    current_time = datetime.now()
    expired_tokens = []

    for token, session in self._sessions.items():
        if session.expires_at < current_time:
            expired_tokens.append(token)

    for token in expired_tokens:
        self.delete_session(token)
```

## 🔄 在 menu_pages 中的使用场景

### 1. 不需要直接调用 session_manager

在 `menu_pages` 包中，**通常不需要直接调用 `session_manager`**，而是通过以下方式使用：

#### A. 通过装饰器自动处理

```python
# menu_pages/home_page.py
from auth.decorators import require_login

@require_login()  # 装饰器内部会处理session
def home_page_content():
    """首页内容"""
    # 装饰器确保 auth_manager.current_user 可用
    from auth import auth_manager

    user = auth_manager.current_user  # 来自session_manager
    ui.label(f'欢迎，{user.username}！')
```

#### B. 通过 auth_manager 间接使用

```python
# menu_pages/dashboard_page.py
from auth.decorators import require_login
from auth import auth_manager

@require_login()
def dashboard_page_content():
    """仪表盘页面"""
    user = auth_manager.current_user  # 间接使用session_manager

    # 根据用户角色显示不同内容
    if user.has_role('admin'):
        show_admin_dashboard()
    elif user.has_role('manager'):
        show_manager_dashboard()
    else:
        show_user_dashboard()
```

### 2. 需要调用 session_manager 的场景

#### A. 获取其他用户信息（较少见）

```python
# menu_pages/user_list_page.py
from auth import auth_manager, session_manager
from auth.decorators import require_role

@require_role('admin')
def user_list_page_content():
    """用户列表页面"""
    current_user = auth_manager.current_user

    # 如果需要获取其他用户的会话信息（很少见）
    # 通常使用 detached_helper 或直接查询数据库

    # 显示当前用户信息
    ui.label(f'当前管理员：{current_user.username}')
```

#### B. 会话状态检查（较少见）

```python
# menu_pages/system_status_page.py
from auth import auth_manager, session_manager
from auth.decorators import require_role

@require_role('admin')
def system_status_page_content():
    """系统状态页面"""
    current_user = auth_manager.current_user

    # 显示当前活跃会话数（管理员功能）
    active_sessions = len(session_manager._sessions)
    ui.label(f'当前活跃会话数：{active_sessions}')
```

### 3. 推荐的使用模式

```python
# menu_pages/example_page.py
from nicegui import ui
from auth.decorators import require_login, require_role
from auth import auth_manager

@require_login()
def example_page_content():
    """示例页面 - 推荐模式"""

    # ✅ 推荐：通过 auth_manager 获取当前用户
    user = auth_manager.current_user

    # 显示用户信息
    ui.label(f'当前用户：{user.username}')
    ui.label(f'用户角色：{", ".join(user.roles)}')

    # 根据权限显示功能
    if user.has_permission('data_export'):
        ui.button('导出数据', on_click=export_data)

    if user.has_role('admin'):
        ui.button('用户管理', on_click=user_management)

    # ❌ 不推荐：直接使用 session_manager
    # token = app.storage.user.get('auth_session_token')
    # session = session_manager.get_session(token)

def export_data():
    """导出数据功能"""
    user = auth_manager.current_user
    ui.notify(f'用户 {user.username} 正在导出数据...')

def user_management():
    """用户管理功能"""
    from component.spa_layout import navigate_to
    navigate_to('user_management', '用户管理')
```

## 🎯 最佳实践

### 1. 在 menu_pages 中的推荐做法

```python
# ✅ 推荐模式
@require_login()
def my_page():
    user = auth_manager.current_user
    # 使用 user 对象...

# ❌ 不推荐模式
def my_page():
    token = app.storage.user.get('auth_session_token')
    session = session_manager.get_session(token)
    # 手动处理会话...
```

### 2. 会话状态检查

```python
# ✅ 推荐：使用装饰器
@require_login()
def protected_page():
    # 装饰器确保用户已登录
    user = auth_manager.current_user

# ❌ 不推荐：手动检查
def protected_page():
    user = auth_manager.check_session()
    if not user:
        ui.navigate.to('/login')
        return
```

### 3. 权限检查

```python
# ✅ 推荐：使用装饰器 + 动态检查
@require_login()
def feature_page():
    user = auth_manager.current_user

    if user.has_permission('feature_a'):
        ui.button('功能A')

    if user.has_role('admin'):
        ui.button('管理功能')

# ✅ 也可以：专门的权限装饰器
@require_permission('feature_a')
def feature_a_page():
    ui.label('功能A页面')
```

## 📊 总结

### Session 的核心作用：

1. **性能优化**：避免频繁查询数据库获取用户信息
2. **状态管理**：在内存中缓存用户的角色和权限
3. **会话持久化**：配合浏览器存储实现会话持久化
4. **安全控制**：提供会话失效和清理机制

### 在 menu_pages 中的使用原则：

1. **优先使用装饰器**：自动处理认证和会话管理
2. **通过 auth_manager 间接使用**：获取当前用户信息
3. **避免直接操作 session_manager**：除非有特殊需求
4. **利用 UserSession 的便捷方法**：如 `has_role()`, `has_permission()`

这种设计使得 session_manager 在后台默默工作，而开发者可以专注于业务逻辑的实现。
