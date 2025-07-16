# 项目目录结构

```
project/
├── auth/                     # 认证和权限管理包
│   ├── __init__.py           # 包初始化和导出
│   ├── config.py             # 认证配置
│   ├── database.py           # 数据库连接和ORM
│   ├── models.py             # 数据模型
│   ├── auth_manager.py       # 认证管理器
│   ├── session_manager.py    # 会话管理器
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
│   └── migrations/           # 数据库迁移脚本
│       └── __init__.py
├── common/                # 公共功能包
│   ├── __init__.py        # 组件包导出
│   ├── exception_handler.py # 日志记录了与异常处理
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
│   ├── home_page.py        # 首页
│   ├── analysis_page.py    # 智能问数页面
│   ├── mcp_page.py         # MCP服务页面
│   └── about_page.py       # 关于页面
├── header_pages/               # 头部功能页面模块
│   ├── __init__.py             # 头部页面包导出
│   ├── search_page.py          # 搜索页面
│   ├── messages_page.py        # 消息页面
│   ├── contact_page.py         # 联系我们页面
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
└── main.py               # 复杂应用程序入口
└── siample_main.py       # 简单布局应用程序入口
```