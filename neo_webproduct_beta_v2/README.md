# 微服务架构项目

## 项目概述

这是一个基于 NiceGUI 和 FastAPI 的现代化微服务架构项目，采用创新的认证集中化设计，大幅简化了微服务开发的复杂性。

# 项目目录结构

```
project/
├── auth/                     # 认证和权限管理包
│   ├── __init__.py           # 包初始化和导出
│   ├── config.py             # 认证配置
│   ├── database.py           # 数据库连接和ORM
│   ├── models.py             # 数据模型（User,Role,Permission）
│   ├── auth_manager.py       # 认证管理器（全局auth_manager）
│   ├── session_manager.py    # 会话管理器（内存缓存UserSession）
│   ├── decorators.py         # 装饰器（登录验证等）
│   ├── detached_helper.py    # 解决SQLAlchemy DetachedInstanceError问题的通用工具
│   ├── navigation.py         # 导航工具函数
│   ├── utils.py              # 工具函数
│   ├── pages/                # 认证相关页面
│   │   ├── __init__.py
│   │   ├── change_password_page.py     # 密码修改
│   │   ├── login_page.py               # 登录页面
│   │   ├── logout_page.py              # 注销页面
│   │   ├── permission_management_page.py     # 权限管理页面
│   │   ├── profile_page.py             # 个人资料页面
│   │   ├── register_page.py            # 注册页面
│   │   ├── role_management_page.py     # 角色管理页面
│   │   └── user_management_page.py     # 用户管理页面
│   ├── doc/                  # auth包相关文档
│   └── migrations/           # 数据库迁移脚本
│       └── __init__.py
├── common/                # 公共功能包
│   ├── __init__.py        # 组件包导出
│   ├── exception_handler.py # 日志记录了与异常处理
│   ├── api_client.py        # 统一HTTP客户端(异步请求)
│   ├── health_check.py      # 服务健康检查
├── logs/                  # 日志存放目录
├── component/             # 布局组件模块
│   ├── __init__.py        # 组件包导出
│   ├── layout_config.py   # 复杂布局配置类
│   ├── layout_manager.py  # 复杂布局管理器
│   ├── simple_layout_manager.py  # 简单布局管理器
│   ├── simple_spa_layout.py      # 简单布局管理器
│   ├── spa_layout.py             # SPA布局装饰器和工具函数
│   └── static_resources.py # 静态资源管理器
├── menu_pages/             # 菜单页面模块
│   ├── __init__.py         # 菜单页面包导出
│   ├── home_page.py        # 首页页面
│   ├── dashboard_page.py   # 看板页面
│   ├── enterprise_archive_page.py     # 一企一档页面
│   ├── person_archive_page.py         # 一人一档页面
│   ├── smart_audit_page.py            # 智能审计页面
│   ├── smart_index_page.py            # 智能指标页面
│   └── about_page.py       # 关于页面
├── header_pages/               # 头部功能页面模块
│   ├── __init__.py             # 头部页面包导出
│   ├── search_page.py          # 搜索页面
│   ├── messages_page.py        # 消息页面
│   ├── contact_page.py         # 联系我们页面
├── database_models/            # 共享业务表数据，认证和权限（用户、角色、权限）使用auth.auth_manager,auth.session_manager
│   ├── __init__.py                       # 统一导出所有模型
│   ├── shared_base.py                    # 基础模型类和公共字段
│   └── business_models/                  # 业务表模型
│       ├── __init__.py
│       └── openai_models.py              # OpenAI服务相关表
├── services/                             # 业务服务目录
│   ├── __init__.py                       # 统一导出所有模型
│   ├── shared/                           # 服务间共享组件，复用auth.database功能
│   │   ├── __init__.py
│   │   ├── config.py                     # 服务配置基类
│   └── openai_service/              # openai api服务
│        ├── __init__.py
│        └── requirements.txt
├── scripts/                           # 部署和运维脚本(新增)
│   ├── __init__.py
│   ├── start_services.py                 # 启动所有服务
│   ├── health_check.py                   # 健康检查脚本
│   ├── database_migrate.py               # 数据库迁移
│   ├── init_database.py                  # 初始化数据库
│   └── deploy.py                         # 部署脚本
├── config/                            # 配置目录(新增)
│   ├── __init__.py
│   ├── services.py                       # 服务配置
│   ├── database.py                       # 数据库配置
│   └── environment.py                    # 环境配置
├── static/                # 静态资源目录
│   ├── images/            # 图片资源
│   │   ├── logo/          # Logo图片
│   │   │   ├── robot.svg  # 应用Logo
│   │   │   └── favicon.ico # 网站图标
│   │   ├── avatars/        # 用户头像
│   │   │   └── default_avatar.png
│   │   └── icons/          # 图标资源
│   │       ├── menu-icons/ # 菜单图标
│   │       └── header-icons/ # 头部图标
│   ├── css/              # 样式文件
│   │   ├── custom.css    # 自定义样式
│   │   └── themes/       # 主题样式
│   │       ├── light.css # 浅色主题
│   │       └── dark.css  # 深色主题
│   ├── js/               # JavaScript文件
│   │   ├── utils.js      # 工具函数
│   │   └── components/   # 组件脚本
│   │       ├── charts.js # 图表组件
│   │       ├── forms.js  # 表单组件
│   │       └── navigation.js # 导航组件
│   ├── fonts/            # 字体文件
│   │   └── custom-fonts/
│   └── config/           # 配置文件
│       └── assets.json   # 资源配置
├── main.py               # 复杂应用程序入口
├── siample_main.py       # 简单布局应用程序入口
└── README.py             # 项目说明文档
```

# 架构方式

采用微服务构架，nicegui 作为前端（要搭配一个 fastapi 服务完成路由、认证、权限管理），然后构建若干的 fastapi 业务服务。前端的 nicegui web，分别连接不同的业务 fastapi。这样 fastapi 服务个数就有 n+1，n 表示不同的业务服务。

```
@startuml
!theme mars
skinparam monochrome true
skinparam shadowing false
skinparam dpi 300
skinparam defaultFontName Noto Sans CJK JP
title 构架图

rectangle "客户端层" as clientLayer {
    component "浏览器 (用户界面)" as browser
}

rectangle "前端服务层" as frontendServiceLayer {
    component "NiceGUI + FastAPI\n(前端UI + 网关聚合)" as frontendApi
    note bottom of frontendApi
        UI页面渲染
        用户认证/角色和权限管理
        API网关/代理
        会话管理
    end note
}

rectangle "后端服务层" {
    component "MongoDB服务\n:8001\nFastAPI" as MongodbService
    component "OpenAI API服务\n:8002\nFastAPI" as OpenaiService
    component "智能审计服务\n:8003\nFastAPI" as SmartAuditService
    component "智能指标服务\n:8004\nFastAPI" as SmartIndexService
}

database "共享数据库" as sharedDB {
    rectangle "认证表组" as authGroup
    rectangle "业务表组" as businessGroup
}

note right of sharedDB
    认证表组：users, roles, permissions,
    role_permissions, user_permissions, user_roles

    业务表组：mongodb_server, openai_server,
    smart_audit, smart_index 等服务表
end note

browser --> frontendApi : HTTP请求
frontendApi --> MongodbService : HTTP调用
frontendApi --> OpenaiService : HTTP调用
frontendApi --> SmartAuditService : HTTP调用
frontendApi --> SmartIndexService : HTTP调用

MongodbService --> sharedDB
OpenaiService --> sharedDB
SmartAuditService --> sharedDB
SmartIndexService --> sharedDB
@enduml
```

## 业务实现逻辑

本项目通过在**NiceGUI 前端服务层**完成了用户认证、会话管理和权限控制的完整实现，使得各个 FastAPI 业务服务可以**专注于纯业务逻辑**，无需处理认证相关的复杂性。这种设计大幅简化了微服务的开发和维护工作。

### 认证与会话管理

项目已经实现了完善的认证体系，请充分合理复用 auth/auth_manager.py、auth/database.py 的功能

- **`auth.auth_manager`**: 全局认证管理器，处理用户登录、注销、会话验证;使用对象 self.current_user
- **`auth.session_manager`**: 内存会话管理器，缓存用户信息（UserSession 对象）
- **`auth.database`**: 数据库连接和 ORM
- **多层验证机制**: 浏览器存储 → 内存缓存 → 数据库验证的完整链路
- **权限控制**: 用户角色、权限的内存缓存和实时验证，对应方法有：has_role、has_permission

### 开发新业务服务的简化流程

#### 第一步：业务数据模型设计

```python
# \database_models\business_models\openai_models.py
class OpenAIConfig(Base):
    __tablename__ = 'openai_configs'

    id = Column(Integer, primary_key=True)
    api_key = Column(String(255), nullable=False)
    model_name = Column(String(100), default='gpt-3.5-turbo')
    max_tokens = Column(Integer, default=1000)
    created_by = Column(Integer, ForeignKey('users.id'))
```

#### 第二步：纯业务服务实现（极简化）

- 无需实现：
- ❌ 用户认证中间件
- ❌ 会话验证
- ❌ 权限检查
- ❌ JWT token 处理

```python
# \services\openai_service\main.py
from fastapi import FastAPI
from openai import OpenAI

app = FastAPI(title="OpenAI API Service")

@app.post("/api/v1/chat")
async def chat_completion(request: ChatRequest):
    """纯业务逻辑，无需认证检查"""
    client = OpenAI(api_key=settings.openai_api_key)

    response = client.chat.completions.create(
        model=request.model,
        messages=request.messages
    )

    return {"result": response.choices[0].message.content}
```

#### 第三步：前端页面集成（已有完整用户信息）

```python
# \menu_pages\enterprise_archive_page.py
from nicegui import ui
from auth import auth_manager  # 👈 已有完整用户信息
from common.api_client import ApiClient

def enterprise_archive_content():
    user = auth_manager.current_user  # 👈 内存中的完整用户信息

    ui.label(f'欢迎，{user.username}！')
    ui.label(f'您的角色：{", ".join(user.roles)}')

    # 根据权限显示功能
    if user.has_permission('openai.use'):
        ui.button('调用OpenAI', on_click=call_openai_api)

    if user.has_role('admin'):
        ui.button('管理配置', on_click=manage_config)

async def call_openai_api():
    user = auth_manager.current_user

    # 调用业务服务（无需传递认证信息）
    client = ApiClient()
    result = await client.post('http://localhost:8002/api/v1/chat',
                              data={
                                  'model': 'gpt-3.5-turbo',
                                  'messages': [{'role': 'user', 'content': '你好'}],
                                  'user_id': user.id,  # 可选：传递用户上下文
                                  'username': user.username
                              })
    ui.notify(f'OpenAI回复：{result["result"]}')
```

#### 安全设计建议

```py
# 业务服务可以添加简单的来源验证
from fastapi import HTTPException, Request

@app.middleware("http")
async def verify_internal_request(request: Request, call_next):
    # 验证请求来源（内网IP）
    if not request.client.host.startswith('10.') and \
       not request.client.host.startswith('192.168.'):
        raise HTTPException(status_code=403, detail="Access denied")

    response = await call_next(request)
    return response
```

#### 服务间通信验证

```py
# 可以添加简单的服务间密钥验证
API_SECRET = "your-internal-api-secret"

@app.middleware("http")
async def verify_api_secret(request: Request, call_next):
    if request.headers.get("X-API-Secret") != API_SECRET:
        raise HTTPException(status_code=401, detail="Invalid API secret")

    response = await call_next(request)
    return response
```
