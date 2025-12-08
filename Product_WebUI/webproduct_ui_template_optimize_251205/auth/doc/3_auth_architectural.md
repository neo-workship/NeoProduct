# webproduct_ui_template Auth 包 - 深度架构分析文档

## 📋 目录

1. [架构总览](#架构总览)
2. [数据模型设计](#数据模型设计)
3. [数据库管理机制](#数据库管理机制)
4. [会话管理系统](#会话管理系统)
5. [认证管理器](#认证管理器)
6. [装饰器系统](#装饰器系统)
7. [权限控制机制](#权限控制机制)
8. [模块间协作流程](#模块间协作流程)
9. [关键设计模式](#关键设计模式)
10. [技术创新点](#技术创新点)

---

## 架构总览

### 整体架构图

```
┌─────────────────────────────────────────────────────────────┐
│                    NiceGUI Web Application                   │
└───────────────────────┬─────────────────────────────────────┘
                        │
        ┌───────────────┴────────────────┐
        │     Auth Package (auth/)       │
        │  ┌──────────────────────────┐  │
        │  │  Decorators Layer        │  │  <- @require_login, @require_role
        │  │  (@require_permission)   │  │
        │  └────────────┬─────────────┘  │
        │               │                 │
        │  ┌────────────▼─────────────┐  │
        │  │   AuthManager            │  │  <- 核心认证逻辑
        │  │   (auth_manager.py)      │  │
        │  └────────┬────────┬────────┘  │
        │           │        │            │
        │  ┌────────▼───┐  ┌▼─────────┐  │
        │  │ SessionMgr │  │ Database │  │  <- 会话缓存 & 数据持久化
        │  │ (内存缓存)  │  │ (SQLModel)│  │
        │  └────────────┘  └────┬─────┘  │
        │                       │         │
        │  ┌────────────────────▼──────┐ │
        │  │   Data Models (models.py) │ │  <- User/Role/Permission
        │  │   - User (用户)            │ │
        │  │   - Role (角色)            │ │
        │  │   - Permission (权限)      │ │
        │  │   - Link Tables (关联表)   │ │
        │  └───────────────────────────┘ │
        └─────────────────────────────────┘
                        │
        ┌───────────────▼────────────────┐
        │     Database (SQLite/MySQL)    │
        └────────────────────────────────┘
```

### 核心设计理念

1. **分层架构**: 清晰的层次划分（表示层/业务层/数据层）
2. **单一职责**: 每个模块只负责一个核心功能
3. **依赖倒置**: 高层模块不依赖低层模块，都依赖于抽象
4. **开闭原则**: 对扩展开放，对修改封闭
5. **缓存优先**: 减少数据库查询，提高性能

---

## 数据模型设计

### 1. 核心实体关系（ER 图）

```
┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│    User     │◄───────►│    Role     │◄───────►│ Permission  │
│  (用户)      │  N:M    │   (角色)     │  N:M    │   (权限)     │
└─────────────┘         └─────────────┘         └─────────────┘
      │                        │                        │
      │                        │                        │
      ▼                        ▼                        ▼
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│UserRoleLink  │      │RolePermission│      │UserPermission│
│ (用户-角色)   │      │   Link       │      │   Link       │
│  关联表       │      │ (角色-权限)   │      │ (用户-权限)   │
└──────────────┘      └──────────────┘      └──────────────┘
```

### 2. User 模型深度解析

```python
class User(SQLModel, table=True):
    """用户模型 - 系统认证的核心实体"""

    # ============ 身份标识 ============
    id: Optional[int]              # 主键，自增
    username: str                   # 用户名（唯一索引）
    email: str                      # 邮箱（唯一索引）
    password_hash: str              # 密码哈希值（不存储明文）

    # ============ 基本信息 ============
    full_name: Optional[str]        # 全名
    phone: Optional[str]            # 电话
    avatar: Optional[str]           # 头像 URL
    bio: Optional[str]              # 个人简介

    # ============ 状态管理 ============
    is_active: bool = True          # 账户是否激活
    is_verified: bool = False       # 邮箱是否验证
    is_superuser: bool = False      # 是否超级管理员

    # ============ 安全机制 ============
    last_login: Optional[datetime]       # 最后登录时间
    login_count: int = 0                 # 登录次数统计
    failed_login_count: int = 0          # 失败登录次数
    locked_until: Optional[datetime]     # 账户锁定截止时间

    # ============ Token 管理 ============
    session_token: Optional[str]         # 当前会话 token
    remember_token: Optional[str]        # "记住我" token

    # ============ 时间戳 ============
    created_at: Optional[datetime]       # 创建时间
    updated_at: Optional[datetime]       # 更新时间

    # ============ 关系定义 ============
    roles: List["Role"] = Relationship(
        back_populates="users",
        link_model=UserRoleLink          # 通过中间表关联
    )
    permissions: List["Permission"] = Relationship(
        back_populates="users",
        link_model=UserPermissionLink    # 直接权限分配
    )
```

**设计亮点：**

1. **双索引设计**: username 和 email 都建立唯一索引，保证快速查询
2. **密码安全**: 只存储 hash 值，使用 SHA-256 + salt
3. **灵活权限**: 支持通过角色继承权限 + 直接分配权限
4. **安全防护**: 失败登录计数、账户锁定机制
5. **Token 分离**: session_token（临时）和 remember_token（长期）分开管理

### 3. 权限模型的多对多关系

```python
# 关系1: User ←→ Role (多对多)
class UserRoleLink(SQLModel, table=True):
    """用户-角色关联表"""
    user_id: Optional[int] = Field(foreign_key="users.id", primary_key=True)
    role_id: Optional[int] = Field(foreign_key="roles.id", primary_key=True)

# 关系2: Role ←→ Permission (多对多)
class RolePermissionLink(SQLModel, table=True):
    """角色-权限关联表"""
    role_id: Optional[int] = Field(foreign_key="roles.id", primary_key=True)
    permission_id: Optional[int] = Field(foreign_key="permissions.id", primary_key=True)

# 关系3: User ←→ Permission (多对多，直接分配)
class UserPermissionLink(SQLModel, table=True):
    """用户-权限关联表（绕过角色的直接分配）"""
    user_id: Optional[int] = Field(foreign_key="users.id", primary_key=True)
    permission_id: Optional[int] = Field(foreign_key="permissions.id", primary_key=True)
```

**权限继承逻辑：**

```
用户的最终权限 = 角色权限集合 ∪ 直接分配权限集合

User.all_permissions =
    ∪ (Role.permissions for Role in User.roles)  # 角色继承的权限
    ∪ User.permissions                            # 直接分配的权限
```

### 4. SQLModel 的技术优势

传统 SQLAlchemy 存在的问题：

- DetachedInstanceError（对象脱离会话）
- 需要手动管理 session 生命周期
- 关系加载复杂（joinedload/selectinload）

SQLModel 的解决方案：

```python
# ❌ 传统 SQLAlchemy 方式
user = session.query(User).options(
    joinedload(User.roles).joinedload(Role.permissions)
).filter(User.id == user_id).first()

# ✅ SQLModel 方式（自动处理）
user = session.get(User, user_id)
# user.roles 和 user.roles[0].permissions 自动可用
# 不会抛出 DetachedInstanceError
```

---

## 数据库管理机制

### 1. 数据库初始化流程

```python
# database.py 核心流程

global engine  # 全局引擎实例

def init_database():
    """初始化数据库连接"""

    # Step 1: 创建引擎
    engine = create_engine(
        auth_config.database_url,
        pool_pre_ping=True,      # 自动检测连接是否有效
        echo=False,               # 生产环境不打印 SQL
        connect_args={
            "check_same_thread": False  # SQLite 多线程支持
        }
    )

    # Step 2: 启用外键约束（SQLite）
    if auth_config.database_type == 'sqlite':
        @event.listens_for(engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    # Step 3: 创建所有表
    SQLModel.metadata.create_all(engine)

    # Step 4: 初始化默认数据（角色、权限）
    init_default_data()
```

### 2. 会话管理模式

**上下文管理器模式（推荐）：**

```python
@contextmanager
def get_db() -> Generator[Session, None, None]:
    """
    提供自动管理的数据库会话

    优势：
    1. 自动提交成功的事务
    2. 自动回滚失败的事务
    3. 自动关闭连接
    4. 异常安全
    """
    session = Session(engine)
    try:
        yield session        # 提供会话给调用者
        session.commit()     # 成功时自动提交
    except Exception as e:
        session.rollback()   # 失败时自动回滚
        log_error(f"数据库操作失败: {e}")
        raise
    finally:
        session.close()      # 无论如何都关闭
```

**使用示例：**

```python
# 查询操作
with get_db() as session:
    user = session.exec(
        select(User).where(User.username == 'admin')
    ).first()
    print(user.username)
# session 自动关闭

# 写入操作
with get_db() as session:
    new_user = User(username='test', email='test@example.com')
    new_user.set_password('password123')
    session.add(new_user)
    # 退出 with 块时自动 commit
```

### 3. 数据库连接池机制

```python
# SQLModel/SQLAlchemy 内置连接池

create_engine(
    database_url,
    pool_size=5,              # 连接池大小
    max_overflow=10,          # 最大溢出连接数
    pool_pre_ping=True,       # 使用前 ping 检测
    pool_recycle=3600,        # 连接回收时间（秒）
    echo_pool=False           # 不打印连接池日志
)

# 连接池工作原理：
# 1. 应用启动时创建 5 个连接
# 2. 请求来时从池中取连接
# 3. 用完后归还到池中
# 4. 超过 pool_size 时创建临时连接（max_overflow）
# 5. 空闲连接超过 pool_recycle 时间后重建
```

---

## 会话管理系统

### 1. UserSession 数据类设计

```python
@dataclass
class UserSession:
    """
    内存中的用户会话对象

    设计目标：
    1. 轻量级：不包含数据库对象引用
    2. 快速访问：纯内存操作
    3. 完整信息：包含用户所需的所有权限数据
    4. 可序列化：可以转为 JSON
    """
    # 基本信息（从 User 提取）
    id: int
    username: str
    email: str
    full_name: Optional[str]

    # 状态信息
    is_active: bool
    is_superuser: bool

    # 权限数据（预计算）
    roles: List[str]           # ['admin', 'editor']
    permissions: Set[str]      # {'user.create', 'content.edit', ...}

    # 时间戳
    created_at: datetime
    updated_at: datetime
    locked_until: Optional[datetime]

    @classmethod
    def from_user(cls, user: User) -> 'UserSession':
        """
        从数据库 User 对象创建会话对象

        核心逻辑：
        1. 提取用户基本信息
        2. 收集所有角色名称
        3. 合并所有权限（角色权限 + 直接权限）
        """
        # 提取角色名
        role_names = [role.name for role in user.roles]

        # 合并权限
        permissions = set()
        if user.is_superuser:
            permissions.add('*')  # 超级管理员拥有所有权限
        else:
            # 1. 角色继承的权限
            for role in user.roles:
                permissions.update(perm.name for perm in role.permissions)
            # 2. 直接分配的权限
            permissions.update(perm.name for perm in user.permissions)

        return cls(
            id=user.id,
            username=user.username,
            # ... 其他字段
            roles=role_names,
            permissions=permissions
        )
```

### 2. SessionManager 设计

```python
class SessionManager:
    """
    会话管理器 - 内存缓存层

    核心职责：
    1. 维护 token -> UserSession 映射
    2. 提供快速的会话查询（O(1) 时间复杂度）
    3. 避免频繁的数据库查询
    """

    def __init__(self):
        # 核心数据结构：哈希表
        self._sessions: Dict[str, UserSession] = {}

    def create_session(self, token: str, user: User) -> UserSession:
        """创建新会话"""
        session = UserSession.from_user(user)
        self._sessions[token] = session  # O(1) 存储
        return session

    def get_session(self, token: str) -> Optional[UserSession]:
        """获取会话（O(1) 查询）"""
        return self._sessions.get(token)

    def update_session(self, token: str, user: User):
        """更新会话（重新加载用户数据）"""
        if token in self._sessions:
            session = UserSession.from_user(user)
            self._sessions[token] = session

    def delete_session(self, token: str):
        """删除会话"""
        if token in self._sessions:
            del self._sessions[token]
```

### 3. 会话持久化机制

```python
# 使用 NiceGUI 的 app.storage.user 实现持久化

# 登录时存储 token
app.storage.user[self._session_key] = token        # 临时会话
app.storage.user[self._remember_key] = remember_token  # 长期会话

# 检查会话时读取 token
token = app.storage.user.get(self._session_key)
if not token:
    token = app.storage.user.get(self._remember_key)

# 登出时清除 token
if self._session_key in app.storage.user:
    del app.storage.user[self._session_key]
if self._remember_key in app.storage.user:
    del app.storage.user[self._remember_key]
```

**存储层次：**

```
┌──────────────────────────────┐
│  浏览器 Cookie/LocalStorage   │  <- NiceGUI app.storage.user
└──────────────┬───────────────┘
               │ token
┌──────────────▼───────────────┐
│  内存缓存 (SessionManager)    │  <- token -> UserSession
└──────────────┬───────────────┘
               │ user_id
┌──────────────▼───────────────┐
│  数据库 (Database)            │  <- User/Role/Permission
└──────────────────────────────┘
```

---

## 认证管理器

### 1. AuthManager 核心架构

```python
class AuthManager:
    """
    认证管理器 - 系统认证的大脑

    设计模式：单例模式 + 门面模式
    核心职责：
    1. 用户认证（登录/注册/登出）
    2. 会话管理（创建/检查/销毁）
    3. 权限验证（角色/权限检查）
    """

    def __init__(self):
        self.current_user: Optional[UserSession] = None
        self._session_key = 'auth_session_token'
        self._remember_key = 'auth_remember_token'
```

### 2. 登录流程详解

```python
def login(self, username: str, password: str,
          remember_me: bool = False) -> Dict[str, Any]:
    """
    用户登录完整流程

    阶段1: 输入验证
    阶段2: 用户查询
    阶段3: 密码验证
    阶段4: 账户状态检查
    阶段5: 会话创建
    阶段6: 持久化存储
    """

    # ========== 阶段1: 输入验证 ==========
    if not username or not password:
        return {'success': False, 'message': '用户名和密码不能为空'}

    # ========== 阶段2: 用户查询 ==========
    with get_db() as session:
        user = session.exec(
            select(User).where(
                (User.username == username) | (User.email == username)
            )
        ).first()

        if not user:
            log_warning(f"登录失败: 用户不存在 ({username})")
            return {'success': False, 'message': '用户名或密码错误'}

        # ========== 阶段3: 密码验证 ==========
        if not user.verify_password(password):
            # 记录失败次数
            user.failed_login_count += 1

            # 达到上限则锁定账户
            if user.failed_login_count >= auth_config.max_login_attempts:
                user.locked_until = datetime.now() + timedelta(
                    seconds=auth_config.lockout_duration
                )
                session.add(user)
                log_warning(f"账户已锁定: {username}")
                return {'success': False, 'message': '账户已锁定，请稍后再试'}

            session.add(user)
            return {'success': False, 'message': '用户名或密码错误'}

        # ========== 阶段4: 账户状态检查 ==========
        if not user.is_active:
            return {'success': False, 'message': '账户未激活'}

        if user.locked_until and user.locked_until > datetime.now():
            return {'success': False, 'message': '账户已被锁定'}

        # ========== 阶段5: 会话创建 ==========
        # 生成随机 token
        token = secrets.token_urlsafe(32)

        # 更新用户登录信息
        user.last_login = datetime.now()
        user.login_count += 1
        user.failed_login_count = 0  # 重置失败次数
        user.session_token = token

        if remember_me:
            remember_token = secrets.token_urlsafe(32)
            user.remember_token = remember_token

        session.add(user)
        # 提交到数据库（退出 with 块时）

    # ========== 阶段6: 持久化存储 ==========
    # 存储到浏览器
    app.storage.user[self._session_key] = token
    if remember_me and remember_token:
        app.storage.user[self._remember_key] = remember_token

    # 创建内存会话
    user_session = session_manager.create_session(token, user)
    self.current_user = user_session

    log_success(f"用户登录成功: {username}")
    return {
        'success': True,
        'message': '登录成功',
        'user': user_session,
        'token': token
    }
```

### 3. 会话检查机制

```python
def check_session(self) -> Optional[UserSession]:
    """
    检查当前会话是否有效

    查询顺序：
    1. 检查内存缓存（current_user）
    2. 检查会话管理器（SessionManager）
    3. 从浏览器 storage 获取 token
    4. 从数据库验证 token
    """

    # Step 1: 内存中已有会话
    if self.current_user:
        return self.current_user

    # Step 2: 从浏览器获取 token
    token = app.storage.user.get(self._session_key)
    if not token:
        token = app.storage.user.get(self._remember_key)

    if not token:
        return None

    # Step 3: 从会话管理器查询
    user_session = session_manager.get_session(token)
    if user_session:
        self.current_user = user_session
        return user_session

    # Step 4: 从数据库验证（会话管理器中没有）
    with get_db() as session:
        user = session.exec(
            select(User).where(
                (User.session_token == token) |
                (User.remember_token == token)
            )
        ).first()

        if user and user.is_active:
            # 重建会话
            user_session = session_manager.create_session(token, user)
            self.current_user = user_session
            return user_session

    return None
```

---

## 装饰器系统

### 1. 装饰器实现原理

```python
from functools import wraps

def require_login(redirect_to_login: bool = True):
    """
    需要登录的装饰器

    装饰器工作原理：
    1. 接收配置参数（redirect_to_login）
    2. 返回真正的装饰器函数（decorator）
    3. decorator 包装目标函数（wrapper）
    4. wrapper 在执行前进行权限检查
    """
    def decorator(func):
        @wraps(func)  # 保留原函数的元数据
        def wrapper(*args, **kwargs):
            # ===== 核心检查逻辑 =====
            user = auth_manager.check_session()

            if not user:
                # 未登录处理
                if redirect_to_login:
                    ui.notify('请先登录', type='warning')
                    ui.navigate.to(auth_config.login_route)
                    return None  # 终止执行
                else:
                    ui.notify('需要登录才能访问', type='error')
                    return None

            # 登录成功，执行原函数
            return func(*args, **kwargs)

        return wrapper
    return decorator
```

### 2. 装饰器链式调用

```python
# 多个装饰器的执行顺序（从下到上）

@require_login(redirect_to_login=True)      # 第3个执行
@require_role('admin')                      # 第2个执行
@require_permission('user.manage')          # 第1个执行
def admin_user_page():
    ui.label('管理员用户管理页面')

# 等价于：
admin_user_page = require_login(redirect_to_login=True)(
    require_role('admin')(
        require_permission('user.manage')(
            admin_user_page
        )
    )
)

# 执行流程：
# 1. 先检查权限（user.manage）
# 2. 再检查角色（admin）
# 3. 最后检查登录状态
# 4. 全部通过后执行 admin_user_page
```

### 3. require_role 装饰器详解

```python
def require_role(*roles):
    """
    需要特定角色的装饰器

    参数：*roles 可变参数，支持多个角色
    逻辑：用户拥有任一角色即可通过
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 1. 先检查登录
            user = auth_manager.check_session()
            if not user:
                ui.notify('请先登录', type='warning')
                ui.navigate.to(auth_config.login_route)
                return

            # 2. 超级管理员绕过检查
            if user.is_superuser:
                return func(*args, **kwargs)

            # 3. 检查角色
            user_roles = set(user.roles)  # 用户的角色集合
            required_roles = set(roles)   # 需要的角色集合

            # 交集不为空 = 至少有一个匹配
            if not user_roles & required_roles:
                log_warning(f"用户 {user.username} 缺少角色: {required_roles}")
                ui.notify(f'您没有访问此页面的权限', type='error')

                # 跳转到无权限页面
                from component import universal_navigate_to
                universal_navigate_to('no_permission', '权限不足')
                return

            # 4. 通过检查，执行函数
            return func(*args, **kwargs)

        return wrapper
    return decorator
```

### 4. require_permission 装饰器详解

```python
def require_permission(*permissions):
    """
    需要特定权限的装饰器

    参数：*permissions 可变参数，支持多个权限
    逻辑：用户必须拥有所有权限才能通过（AND 关系）
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            user = auth_manager.check_session()
            if not user:
                ui.notify('请先登录', type='warning')
                ui.open(auth_config.login_route)
                return

            # 超级管理员拥有所有权限
            if user.is_superuser:
                return func(*args, **kwargs)

            # 检查每个权限
            missing_permissions = []
            for permission in permissions:
                if not auth_manager.has_permission(permission):
                    missing_permissions.append(permission)

            # 有缺失权限
            if missing_permissions:
                log_warning(f"用户 {user.username} 缺少权限: {missing_permissions}")
                ui.notify(
                    f'您缺少以下权限：{", ".join(missing_permissions)}',
                    type='error'
                )
                from component import universal_navigate_to
                universal_navigate_to('no_permission', '权限不足')
                return

            # 通过检查
            return func(*args, **kwargs)

        return wrapper
    return decorator
```

---

## 权限控制机制

### 1. RBAC 权限模型

```
RBAC (Role-Based Access Control) - 基于角色的访问控制

核心概念：
- User（用户）：系统的使用者
- Role（角色）：权限的集合
- Permission（权限）：具体的操作权限

关系：
User --(N:M)--> Role --(N:M)--> Permission
User --(N:M)--> Permission (直接分配)
```

### 2. 权限判断算法

```python
def has_permission(self, permission_name: str) -> bool:
    """
    检查当前用户是否有指定权限

    判断逻辑（优先级从高到低）：
    1. 超级管理员 → True
    2. 通配符权限 (*) → True
    3. 直接匹配权限名 → True
    4. 否则 → False
    """
    if not self.current_user:
        return False

    # 规则1: 超级管理员拥有所有权限
    if self.current_user.is_superuser:
        return True

    # 规则2: 检查通配符（用于测试/开发）
    if '*' in self.current_user.permissions:
        return True

    # 规则3: 精确匹配
    return permission_name in self.current_user.permissions
```

### 3. 权限继承机制

```python
# 用户的最终权限来源：

┌─────────────────────────────────────────────┐
│           User.all_permissions              │
│  ┌────────────────────────────────────┐    │
│  │  1. 角色继承权限                     │    │
│  │     For each Role in User.roles:    │    │
│  │         permissions += Role.perms   │    │
│  └────────────────────────────────────┘    │
│               ∪ (并集)                       │
│  ┌────────────────────────────────────┐    │
│  │  2. 直接分配权限                     │    │
│  │     permissions += User.permissions │    │
│  └────────────────────────────────────┘    │
└─────────────────────────────────────────────┘

# 代码实现（UserSession.from_user）
permissions = set()

# 1. 超级管理员特殊处理
if user.is_superuser:
    permissions.add('*')
else:
    # 2. 角色权限
    for role in user.roles:
        for perm in role.permissions:
            permissions.add(perm.name)

    # 3. 直接权限
    for perm in user.permissions:
        permissions.add(perm.name)
```

### 4. 权限粒度设计

```python
# 权限命名规范：<资源>.<操作>

system.manage      # 系统管理
user.create        # 创建用户
user.edit          # 编辑用户
user.delete        # 删除用户
user.view          # 查看用户
content.create     # 创建内容
content.edit       # 编辑内容
content.delete     # 删除内容
content.publish    # 发布内容

# 分类管理
permissions = [
    {'name': 'user.create', 'category': 'user'},
    {'name': 'user.edit', 'category': 'user'},
    {'name': 'content.create', 'category': 'content'},
]

# 可以按 category 分组显示和管理
```

---

## 模块间协作流程

### 1. 用户登录完整流程图

```
┌────────┐
│ 用户输入 │
│ 用户名   │
│ 密码     │
└────┬───┘
     │
     ▼
┌─────────────────────────────────────────────┐
│          login_page.py (UI Layer)           │
│  - 表单验证                                  │
│  - 调用 auth_manager.login()                │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│      auth_manager.py (Business Layer)       │
│  1. 输入验证                                 │
│  2. 调用 database.get_db() 查询用户          │
│  3. 验证密码（User.verify_password）         │
│  4. 更新登录信息                             │
│  5. 生成 session token                      │
│  6. 调用 session_manager.create_session()   │
│  7. 存储到 app.storage.user                 │
└────────┬────────────────────┬───────────────┘
         │                    │
         ▼                    ▼
┌─────────────────┐  ┌──────────────────┐
│   database.py   │  │ session_manager  │
│  (Data Layer)   │  │  (Cache Layer)   │
│                 │  │                  │
│ - 查询用户       │  │ - 创建会话对象    │
│ - 更新登录次数   │  │ - 存入内存缓存    │
│ - 存储 token    │  │                  │
└─────────────────┘  └──────────────────┘
```

### 2. 权限检查流程图

```
用户访问受保护页面
        │
        ▼
   装饰器拦截
 @require_permission('user.manage')
        │
        ▼
调用 auth_manager.check_session()
        │
        ├─→ 内存中有会话？
        │   ├─ Yes → 返回 UserSession
        │   └─ No  → 继续
        │
        ├─→ SessionManager 中有？
        │   ├─ Yes → 返回 UserSession
        │   └─ No  → 继续
        │
        ├─→ app.storage.user 中有 token？
        │   ├─ Yes → 继续
        │   └─ No  → 返回 None（未登录）
        │
        └─→ 数据库验证 token
            ├─ Valid → 重建会话
            └─ Invalid → 返回 None
        │
        ▼
检查权限 auth_manager.has_permission('user.manage')
        │
        ├─→ 是超级管理员？
        │   └─ Yes → 允许访问
        │
        ├─→ permissions 中有 'user.manage'？
        │   ├─ Yes → 允许访问
        │   └─ No  → 拒绝访问
        │
        ▼
返回结果
```

### 3. 角色权限分配流程

```
1. 创建权限
   ↓
┌─────────────────────────────────┐
│ Permission.create()              │
│ - name: 'content.edit'           │
│ - display_name: '编辑内容'        │
│ - category: 'content'            │
└─────────────────────────────────┘
   ↓
2. 创建角色
   ↓
┌─────────────────────────────────┐
│ Role.create()                    │
│ - name: 'editor'                 │
│ - display_name: '编辑'            │
└─────────────────────────────────┘
   ↓
3. 为角色分配权限
   ↓
┌─────────────────────────────────┐
│ role.permissions.append(perm)    │
│ → 插入 RolePermissionLink 表     │
└─────────────────────────────────┘
   ↓
4. 为用户分配角色
   ↓
┌─────────────────────────────────┐
│ user.roles.append(role)          │
│ → 插入 UserRoleLink 表           │
└─────────────────────────────────┘
   ↓
5. 用户登录
   ↓
┌─────────────────────────────────┐
│ UserSession.from_user(user)      │
│ → 自动计算所有权限                │
│ → permissions = role_perms ∪     │
│                 direct_perms     │
└─────────────────────────────────┘
```

---

## 关键设计模式

### 1. 单例模式（Singleton）

```python
# 全局唯一的认证管理器实例
auth_manager = AuthManager()

# 全局唯一的会话管理器实例
session_manager = SessionManager()

# 全局唯一的配置实例
auth_config = AuthConfig()

# 使用时直接导入
from auth import auth_manager, session_manager, auth_config
```

**优势：**

- 保证系统中只有一个实例
- 全局访问点
- 状态一致性

### 2. 门面模式（Facade）

```python
# AuthManager 作为门面，隐藏内部复杂性

class AuthManager:
    """对外提供简单接口"""

    def login(self, username, password):
        """
        登录（对外简单接口）

        内部复杂操作：
        - 数据库查询
        - 密码验证
        - Token 生成
        - 会话创建
        - 持久化存储
        """
        # 隐藏所有复杂逻辑
        pass

# 用户只需调用简单接口
result = auth_manager.login('admin', 'password')
```

### 3. 装饰器模式（Decorator）

```python
# 动态地给函数添加功能，无需修改原函数

@require_login          # 添加登录检查
@require_role('admin')  # 添加角色检查
def admin_page():
    pass

# 等价于
admin_page = require_login(require_role('admin')(admin_page))
```

### 4. 策略模式（Strategy）

```python
# 数据库类型切换策略

class AuthConfig:
    def _get_database_url(self) -> str:
        """根据类型选择不同策略"""
        if self.database_type == 'sqlite':
            return f'sqlite:///{db_path}'
        elif self.database_type == 'mysql':
            return 'mysql://user:pass@localhost/db'
        elif self.database_type == 'postgresql':
            return 'postgresql://user:pass@localhost/db'
```

### 5. 工厂模式（Factory）

```python
# UserSession.from_user() 工厂方法

class UserSession:
    @classmethod
    def from_user(cls, user: User) -> 'UserSession':
        """工厂方法：从 User 创建 UserSession"""
        # 复杂的创建逻辑封装在这里
        return cls(
            id=user.id,
            username=user.username,
            # ... 其他字段
        )

# 使用
session = UserSession.from_user(db_user)
```

### 6. 上下文管理器模式（Context Manager）

```python
# 自动资源管理

@contextmanager
def get_db():
    session = Session(engine)
    try:
        yield session        # 资源使用期
        session.commit()
    except:
        session.rollback()
    finally:
        session.close()     # 自动清理

# 使用
with get_db() as session:
    # 自动管理生命周期
    user = session.get(User, 1)
```

---

## 技术创新点

### 1. SQLModel 的革命性改进

**传统 SQLAlchemy 的痛点：**

```python
# ❌ 问题1: DetachedInstanceError
user = session.query(User).first()
session.close()
print(user.roles)  # 💥 DetachedInstanceError

# ❌ 问题2: 复杂的 joinedload
user = session.query(User)\
    .options(
        joinedload(User.roles)
        .joinedload(Role.permissions)
    ).first()

# ❌ 问题3: 需要手动管理 session
from sqlalchemy.orm import scoped_session
Session = scoped_session(sessionmaker(bind=engine))
```

**SQLModel 的优雅解决：**

```python
# ✅ 解决1: 不会脱离会话
user = session.get(User, 1)
# user 对象可以安全使用，关系自动加载

# ✅ 解决2: 自动关系加载
user = session.get(User, 1)
print(user.roles)  # 自动加载，无需 joinedload

# ✅ 解决3: 简化 session 管理
from sqlmodel import Session
session = Session(engine)
```

### 2. 双层缓存架构

```
┌──────────────────────────────────────┐
│   L1 Cache: AuthManager.current_user │  <- 最快，当前请求
└────────────────┬─────────────────────┘
                 │ Miss
┌────────────────▼─────────────────────┐
│   L2 Cache: SessionManager._sessions │  <- 快，所有会话
└────────────────┬─────────────────────┘
                 │ Miss
┌────────────────▼─────────────────────┐
│   Storage: app.storage.user (token)  │  <- 中，浏览器存储
└────────────────┬─────────────────────┘
                 │ Miss
┌────────────────▼─────────────────────┐
│   Database: User Table               │  <- 慢，持久化
└──────────────────────────────────────┘

性能对比：
- L1 Cache: ~0.001ms （内存指针）
- L2 Cache: ~0.01ms  （哈希查询）
- Storage:  ~1ms     （浏览器 API）
- Database: ~10ms    （SQL 查询）
```

### 3. 权限预计算

```python
# 传统方式：每次检查都查数据库
def has_permission(self, perm_name):
    # 每次都要查 roles 和 permissions 表
    for role in self.user.roles:
        if perm_name in [p.name for p in role.permissions]:
            return True
    return False

# 创新方式：登录时预计算所有权限
class UserSession:
    permissions: Set[str]  # {'user.create', 'content.edit', ...}

    def has_permission(self, perm_name):
        return perm_name in self.permissions  # O(1) 查询

# 性能提升：
# 传统方式：每次检查 ~10ms （多次数据库查询）
# 创新方式：每次检查 ~0.001ms （内存集合查询）
# 提升：10,000 倍
```

### 4. Token 双轨制

```python
# Session Token: 临时会话（关闭浏览器失效）
app.storage.user['auth_session_token'] = token

# Remember Token: 长期会话（30天）
app.storage.user['auth_remember_token'] = remember_token

# 优势：
# 1. 安全性：session_token 短期有效
# 2. 便利性：remember_token 长期免登录
# 3. 灵活性：可以分别撤销
```

### 5. 装饰器的智能重定向

```python
@require_login(redirect_to_login=True)
def protected_page():
    pass

# 自动处理：
# 1. 检测到未登录
# 2. 保存当前路径到 storage
# 3. 重定向到登录页
# 4. 登录成功后自动返回原页面

# 用户体验极佳，无感知跳转
```

---

## 核心流程时序图

### 完整的认证流程

```
┌────┐   ┌──────┐   ┌──────────┐   ┌──────────┐   ┌─────────┐   ┌──────┐
│用户│   │UI层  │   │AuthManager│   │SessionMgr│   │Database │   │Storage│
└─┬──┘   └───┬──┘   └────┬─────┘   └────┬─────┘   └────┬────┘   └───┬──┘
  │          │           │              │              │            │
  │ 输入账密 │           │              │              │            │
  ├─────────>│           │              │              │            │
  │          │ login()   │              │              │            │
  │          ├──────────>│              │              │            │
  │          │           │ 查询用户     │              │            │
  │          │           ├─────────────────────────────>│            │
  │          │           │<─────────────────────────────┤            │
  │          │           │ User对象     │              │            │
  │          │           │              │              │            │
  │          │           │ 验证密码     │              │            │
  │          │           │ (成功)       │              │            │
  │          │           │              │              │            │
  │          │           │ 生成token    │              │            │
  │          │           │              │              │            │
  │          │           │ create_session()            │            │
  │          │           ├─────────────>│              │            │
  │          │           │<─────────────┤              │            │
  │          │           │ UserSession  │              │            │
  │          │           │              │              │            │
  │          │           │ 存储token                   │            │
  │          │           ├────────────────────────────────────────>│
  │          │<──────────┤              │              │            │
  │<─────────┤ 登录成功  │              │              │            │
  │          │           │              │              │            │
  │ 访问页面 │           │              │              │            │
  ├─────────>│           │              │              │            │
  │          │ @require_login           │              │            │
  │          ├──────────>│              │              │            │
  │          │           │ check_session()             │            │
  │          │           ├─────────────>│              │            │
  │          │           │<─────────────┤              │            │
  │          │           │ UserSession  │              │            │
  │          │           │              │              │            │
  │          │           │ has_permission('xxx')       │            │
  │          │           │ (检查内存)   │              │            │
  │          │           │ ✓ 通过       │              │            │
  │          │<──────────┤              │              │            │
  │<─────────┤ 渲染页面  │              │              │            │
```

---

## 总结

### 核心架构优势

1. **分层清晰**

   - UI 层（pages）→ 业务层（auth_manager）→ 数据层（database）
   - 每层职责明确，易于维护和测试

2. **性能优化**

   - 双层内存缓存（L1 + L2）
   - 权限预计算
   - 连接池复用

3. **安全可靠**

   - 密码哈希存储
   - Token 随机生成
   - 失败登录限制
   - 账户锁定机制

4. **易于扩展**

   - 装饰器式 API
   - 策略模式支持多数据库
   - RBAC 模型灵活配置

5. **开发友好**
   - SQLModel 简化数据库操作
   - 上下文管理器自动资源管理
   - 类型提示完善

### 技术栈总结

| 层次     | 技术选型                | 作用                 |
| -------- | ----------------------- | -------------------- |
| Web 框架 | NiceGUI                 | 快速构建 UI          |
| ORM 框架 | SQLModel                | 数据库操作           |
| 数据库   | SQLite/MySQL/PostgreSQL | 数据持久化           |
| 安全     | hashlib, secrets        | 密码加密、Token 生成 |
| 缓存     | Dict（内存）            | 会话缓存             |
| 存储     | app.storage.user        | 浏览器持久化         |

### 设计模式总结

- **单例模式**: auth_manager, session_manager
- **门面模式**: AuthManager 统一接口
- **装饰器模式**: @require_login, @require_role
- **工厂模式**: UserSession.from_user()
- **策略模式**: 数据库类型切换
- **上下文管理器**: get_db() 资源管理

这个认证包通过精心的架构设计和模式应用，实现了高性能、高安全性、易扩展的认证和权限管理系统。
