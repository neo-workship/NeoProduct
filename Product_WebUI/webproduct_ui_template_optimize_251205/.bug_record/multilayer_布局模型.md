## ------ 3 种布局模式的权限问题 -------

关键在于:no_permission_page_content 函数没有添加任何装饰器,是一个纯粹的页面渲染函数。当"非 admin"用户(非 admin 角色)点击系统管理菜单中的"用户管理"等页面时:

路由直接触发 → navigate_to_route('user_management', '用户管理')
执行路由处理器 → route_handlers['user_management']()
装饰器生效 → @require_role('admin') 检测到用户不是 admin
装饰器内部逻辑 → 在 require_role 装饰器中,当权限不足时应该会显示通知并 return(阻止函数继续执行)

让我再看看 require_role 装饰器的实现:

```py
def require_role(*roles):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            user = auth_manager.check_session()
            if not user:
                ui.notify('请先登录', type='warning')
                ui.open(auth_config.login_route)
                return  # ✅ 这里return了

            if not user.is_superuser:
                user_roles = [role.name for role in user.roles]
                if not any(role in user_roles for role in roles):
                    ui.notify(f'您没有权限访问此功能,需要以下角色之一:{", ".join(roles)}', type='error')
                    return  # ✅ 这里也return了,但没有导航到no_permission!

            return func(*args, **kwargs)
        return wrapper
    return decorator
```

### 问题根源找到了!

require_role 装饰器在权限检查失败时,只是显示了一个错误通知并 return,没有调用导航到 no_permission 路由!这导致:

- 页面内容区域被清空(navigate_to_route 中的 self.content_container.clear())
- 装饰器阻止了页面内容渲染
- 但没有渲染 no_permission_page_content 来填充内容区域
- 结果就是一个空白页面,只有一个错误通知

### 解决方案

修改 auth/decorators.py 中的 require_role 装饰器,在权限不足时导航到 no_permission:

```py
def require_role(*roles):
    """
    要求用户具有指定角色的装饰器

    Args:
        *roles: 需要的角色列表
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 首先检查登录
            user = auth_manager.check_session()
            if not user:
                ui.notify('请先登录', type='warning')
                ui.open(auth_config.login_route)
                return

            # 检查角色
            if not user.is_superuser:
                user_roles = [role.name for role in user.roles]
                if not any(role in user_roles for role in roles):
                    log_warning(f"用户 {user.username} 缺少必需角色: {roles}, 当前角色: {user_roles}")
                    ui.notify(f'您没有权限访问此功能,需要以下角色之一:{", ".join(roles)}', type='error')

                    # ✅ 关键修改:导航到no_permission页面而不是简单return
                    from component import universal_navigate_to
                    try:
                        universal_navigate_to('no_permission', '权限不足')
                    except RuntimeError:
                        # 如果布局管理器未初始化,直接渲染权限不足页面
                        from .pages import no_permission_page_content
                        no_permission_page_content()

                    return

            return func(*args, **kwargs)
        return wrapper
    return decorator
```

这个修改的核心是:当权限检查失败时,不是简单地 return 留下空白页面,而是主动导航到 no_permission 路由,让其对应的页面内容填充到内容区域。同样的,require_permission 装饰器也需要类似的修改:

```py
def require_permission(*permissions):
    """
    要求用户具有指定权限的装饰器

    Args:
        *permissions: 需要的权限列表
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 首先检查登录
            user = auth_manager.check_session()
            if not user:
                ui.notify('请先登录', type='warning')
                ui.open(auth_config.login_route)
                return

            # 检查权限
            missing_permissions = []
            for permission in permissions:
                if not auth_manager.has_permission(permission):
                    missing_permissions.append(permission)

            if missing_permissions:
                log_warning(f"用户 {user.username} 缺少权限: {missing_permissions}")
                ui.notify(f'您缺少以下权限:{", ".join(missing_permissions)}', type='error')

                # ✅ 关键修改:导航到no_permission页面
                from component import universal_navigate_to
                try:
                    universal_navigate_to('no_permission', '权限不足')
                except RuntimeError:
                    from .pages import no_permission_page_content
                    no_permission_page_content()

                return

            return func(*args, **kwargs)
        return wrapper
    return decorator
```

## 三种布局模式的关键差异

### 1. SimpleLayoutManager (工作正常)

```py
def handle_settings_menu_item_click(self, route: str, label: str):
    """处理设置菜单项点击事件"""
    from auth.auth_manager import auth_manager

    if not auth_manager.is_authenticated():
        ui.notify('请先登录', type='warning')
        self.navigate_to_route('login', '登录')
        return

    if not auth_manager.has_role('admin') and not auth_manager.current_user.is_superuser:
        ui.notify('您没有管理员权限,无法访问此功能', type='error')
        self.navigate_to_route('no_permission', '权限不足')  # ✅ 关键:主动导航
        return

    ui.notify(f'访问管理功能: {label}')
    self.navigate_to_route(route, label)
```

### 2. LayoutManager (spa_layout, 工作正常)

```py
def handle_settings_menu_item_click(self, route: str, label: str):
    """处理设置菜单项点击事件"""
    from auth.auth_manager import auth_manager

    if not auth_manager.is_authenticated():
        ui.notify('请先登录', type='warning')
        self.navigate_to_route('login', '登录')
        return

    if not auth_manager.has_role('admin') and not auth_manager.current_user.is_superuser:
        ui.notify('您没有管理员权限,无法访问此功能', type='error')
        self.navigate_to_route('no_permission', '权限不足')  # ✅ 关键:主动导航
        return

    ui.notify(f'访问管理功能: {label}')
    self.navigate_to_route(route, label)
```

### 3. MultilayerLayoutManager (有问题)

```py
def handle_settings_menu_item_click(self, route: str, label: str):
    """
    处理设置菜单项点击事件

    Args:
        route: 目标路由
        label: 菜单项标签
    """
    from auth.auth_manager import auth_manager

    # 第一层检查:是否已登录
    if not auth_manager.is_authenticated():
        logger.debug(f"⚠️ 未登录用户尝试访问管理功能: {label}")
        ui.notify('请先登录', type='warning')
        self.navigate_to_route('login', '登录')
        return

    # 第二层检查:是否有管理员权限
    if not auth_manager.has_role('admin') and not auth_manager.current_user.is_superuser:
        logger.warning(f"⚠️ 用户 {auth_manager.current_user.username} 无权限访问: {label}")
        ui.notify('您没有管理员权限,无法访问此功能', type='error')
        # ✅ 关键:导航到无权限页面,不触发目标页面的装饰器
        self.navigate_to_route('no_permission', '权限不足')
        return

    # 第三层:权限验证通过,导航到目标页面
    logger.info(f"✅ 用户 {auth_manager.current_user.username} 访问管理功能: {label}")
    ui.notify(f'访问管理功能: {label}')
    self.navigate_to_route(route, label)
```

### 问题根源

三个布局管理器的 handle_settings_menu_item_click 方法逻辑完全一致! 都会在权限检查失败时主动导航到 no_permission 路由。
真正的差异在于菜单项的调用方式:SimpleLayoutManager 和 LayoutManager (正常工作)在头部的设置菜单中,管理菜单项直接绑定到 handle_settings_menu_item_click:

```py
# 设置菜单
with ui.button(icon='settings').props('flat color=white round'):
    with ui.menu() as settings_menu:
        ui.menu_item('用户管理',
                     lambda: self.handle_settings_menu_item_click('user_management', '用户管理'))
        # ✅ 点击时先执行权限检查,再决定是否导航
```

MultilayerLayoutManager (有问题)
在 multilayer_main.py 中,系统管理菜单项直接配置了 route:

```py
MultilayerMenuItem(
    key='system',
    label='系统管理',
    icon='admin_panel_settings',
    children=[
        MultilayerMenuItem(
            key='users',
            label='用户管理',
            icon='group',
            route='user_management'  # ❌ 直接配置route,绕过了权限检查
        ),
    ]
)
```

当用户点击这些菜单项时:

- 直接触发 select_leaf_item → navigate_to_route
- 没有经过 handle_settings_menu_item_click 的权限检查
- 直接执行 route_handlers['user_management']()
- 装饰器生效 @require_role('admin') 检测失败
- 装饰器只 return 没有导航到 no_permission
- 结果:空白页面
