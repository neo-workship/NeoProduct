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
├── database_models/            # 共享数据模型，认证和权限（用户、角色、权限）使用auth.auth_manager,auth.session_manager
│   ├── __init__.py                       # 统一导出所有模型
│   ├── shared_base.py                    # 基础模型类和公共字段
│   └── business_models/                  # 业务表模型
│       ├── __init__.py
│       ├── mongodb_models.py             # MongoDB服务相关表
│       ├── openai_models.py              # OpenAI服务相关表
│       ├── smart_audit_models.py         # 智能审计服务相关表
│       └── smart_index_models.py         # 智能指标服务相关表
├── services/                             # 业务服务目录
│   ├── __init__.py                       # 统一导出所有模型
│   ├── shared/                           # 服务间共享组件，复用auth.database功能
│   │   ├── __init__.py
│   │   ├── config.py                     # 服务配置基类
│   ├── mongodb_service/                  # mongodb服务
│   │    ├── __init__.py
│   │    └── requirements.txt
|   ├── openai_service/                   # openai api服务
│   │    ├── __init__.py
│   │    └── requirements.txt
|   ├── smart_audit_service/              # smart audit业务表模型
│   │    ├── __init__.py
│   │    └── requirements.txt
│   └── smart_index_service/              # smart_index业务表模型
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

采用微服务构架，nicegui 作为前端（要搭配一个 fastapi 服务完成路由、认证、权限管理），然后构建若干的 fastapi 业务服务。前端的 nicegui web，分别连接不同的业务 fastapi。这样 fastapi 服务个数就有 n+1，n 表示不同的业务服务,以下构架图。

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
