# MCP集成服务平台 - 模块化架构

这是一个基于NiceGUI的模块化SPA应用程序，采用清晰的分层架构设计。

## 项目结构

```
project/
├── component/              # 布局组件模块
│   ├── __init__.py        # 组件包导出
│   ├── layout_config.py   # 布局配置类
│   ├── layout_manager.py  # 布局管理器
│   ├── spa_layout.py      # SPA布局装饰器和工具函数
│   └── static_resources.py # 静态资源管理器
├── menu_pages/            # 菜单页面模块
│   ├── __init__.py       # 菜单页面包导出
│   ├── home_page.py      # 首页
│   ├── dashboard_page.py # 看板页面
│   ├── data_page.py      # 数据连接页面
│   ├── analysis_page.py  # 智能问数页面
│   ├── mcp_page.py       # MCP服务页面
│   └── about_page.py     # 关于页面
├── header_pages/          # 头部功能页面模块
│   ├── __init__.py       # 头部页面包导出
│   ├── search_page.py    # 搜索页面
│   ├── messages_page.py  # 消息页面
│   ├── notifications_page.py # 通知页面
│   ├── contact_page.py   # 联系我们页面
│   ├── settings_page.py  # 设置页面
│   └── user_profile_page.py # 用户资料页面
├── static/                # 静态资源目录
│   ├── images/           # 图片资源
│   │   ├── logo/         # Logo图片
│   │   │   ├── robot.svg # 应用Logo
│   │   │   └── favicon.ico # 网站图标
│   │   ├── avatars/      # 用户头像
│   │   │   └── default_avatar.png
│   │   └── icons/        # 图标资源
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
└── main.py               # 应用程序入口
```

## 模块说明

### 1. Component 模块 (`component/`)

负责应用程序的布局和架构：

- **`layout_config.py`**: 定义布局配置类、菜单项类和头部配置项类
- **`layout_manager.py`**: 核心布局管理器，处理页面路由、菜单选择、头部交互等
- **`spa_layout.py`**: 提供装饰器和工具函数，用于创建SPA布局
- **`static_resources.py`**: 静态资源管理器，统一管理所有静态文件路径

### 2. Menu Pages 模块 (`menu_pages/`)

包含所有左侧菜单对应的页面处理函数：

- 首页、看板、数据连接、智能问数、MCP服务、关于等页面
- 每个页面都是独立的模块，便于维护和扩展

### 3. Header Pages 模块 (`header_pages/`)

包含所有头部功能按钮对应的页面处理函数：

- 搜索、消息、通知、联系我们、设置、用户资料等页面
- 模块化设计，便于添加新的头部功能

### 4. Static 静态资源模块 (`static/`)

统一管理所有静态资源：

- **`images/`**: 图片资源，包括Logo、图标、头像等
- **`css/`**: 样式文件，包括自定义样式和主题
- **`js/`**: JavaScript文件，包括工具函数和组件脚本
- **`fonts/`**: 字体文件
- **`config/`**: 配置文件，包括资源路径配置

## 使用方法

### 运行应用

```bash
python main.py
```

### 静态资源管理

#### 使用静态资源管理器

```python
from component.static_resources import static_manager

# 获取Logo路径
logo_path = static_manager.get_logo_path('robot.svg')

# 获取头像路径
avatar_path = static_manager.get_avatar_path('user_avatar.png')

# 获取CSS文件路径
css_path = static_manager.get_css_path('custom.css')

# 检查文件是否存在
if static_manager.file_exists(logo_path):
    # 使用文件
    pass
```

#### 添加新的静态资源

1. 将文件放入对应的 `static/` 子目录
2. 使用 `static_manager` 获取文件路径
3. 在页面中引用资源

#### 自定义主题

1. 在 `static/css/themes/` 目录下创建新的主题CSS文件
2. 使用 `static_manager.get_theme_css_path('your_theme')` 获取路径
3. 在应用中加载主题

### 添加新的菜单页面

1. 在 `menu_pages/` 目录下创建新的页面文件
2. 在 `menu_pages/__init__.py` 中导入并添加到 `get_menu_page_handlers()` 函数
3. 在 `main.py` 的 `menu_items` 配置中添加对应菜单项

### 添加新的头部功能页面

1. 在 `header_pages/` 目录下创建新的页面文件
2. 在 `header_pages/__init__.py` 中导入并添加到 `get_header_page_handlers()` 函数
3. 在 `main.py` 的 `header_config_items` 配置中添加对应配置项

### 自定义布局配置

```python
from component import LayoutConfig, static_manager

# 创建自定义配置
custom_config = LayoutConfig()
custom_config.app_title = '你的应用标题'
custom_config.app_icon = static_manager.get_logo_path('your_logo.svg')
custom_config.header_bg = 'bg-purple-600'

# 在装饰器中使用
@with_spa_layout(config=custom_config, ...)
```

## 静态资源最佳实践

### 图片资源
- **Logo**: 使用SVG格式，支持矢量缩放
- **图标**: 优先使用SVG，备选PNG（24x24, 48x48）
- **头像**: 使用PNG或JPG，建议尺寸128x128
- **背景图**: 使用WebP格式，提供JPG备选

### CSS样式
- **模块化**: 按功能分割CSS文件
- **主题化**: 使用CSS变量支持多主题
- **响应式**: 确保移动端适配
- **优化**: 压缩CSS文件，移除未使用的样式

### JavaScript
- **组件化**: 按功能模块拆分JS文件
- **工具函数**: 提供通用的辅助函数
- **性能**: 使用防抖节流，避免内存泄漏
- **兼容性**: 确保浏览器兼容性

## 特性

- 🎨 **现代化设计**: 支持暗色主题，响应式布局
- 🧩 **模块化架构**: 清晰的代码组织，易于维护和扩展
- 🚀 **SPA体验**: 单页应用路由，无刷新页面切换
- ⚙️ **可配置**: 灵活的布局配置和菜单定制
- 📱 **响应式**: 适配不同屏幕尺寸
- 🎯 **资源管理**: 统一的静态资源管理系统
- 🎨 **主题支持**: 内置浅色/深色主题切换

## 扩展指南

### 添加新功能模块

1. 创建新的包目录
2. 定义页面处理函数
3. 在主文件中导入并配置路由
4. 更新菜单或头部配置

### 自定义样式

通过修改 `LayoutConfig` 类或在页面处理函数中使用 NiceGUI 的 CSS 类来自定义样式。

### 集成外部服务

在对应的页面模块中添加外部API调用、数据库连接等功能。

### 添加新的静态资源类型

1. 在 `static/` 目录下创建新的子目录
2. 更新 `StaticResourceManager` 类添加对应的方法
3. 在配置文件中添加新的资源路径

## 依赖

- NiceGUI: 用于构建Web界面
- Python 3.7+

## 许可证

MIT License   ├── __init__.py       # 头部页面包导出
│   ├── search_page.py    # 搜索页面
│   ├── messages_page.py  # 消息页面
│   ├── notifications_page.py # 通知页面
│   ├── contact_page.py   # 联系我们页面
│   ├── settings_page.py  # 设置页面
│   └── user_profile_page.py # 用户资料页面
└── main.py               # 应用程序入口
```

## 模块说明

### 1. Component 模块 (`component/`)

负责应用程序的布局和架构：

- **`layout_config.py`**: 定义布局配置类、菜单项类和头部配置项类
- **`layout_manager.py`**: 核心布局管理器，处理页面路由、菜单选择、头部交互等
- **`spa_layout.py`**: 提供装饰器和工具函数，用于创建SPA布局

### 2. Menu Pages 模块 (`menu_pages/`)

包含所有左侧菜单对应的页面处理函数：

- 首页、看板、数据连接、智能问数、MCP服务、关于等页面
- 每个页面都是独立的模块，便于维护和扩展

### 3. Header Pages 模块 (`header_pages/`)

包含所有头部功能按钮对应的页面处理函数：

- 搜索、消息、通知、联系我们、设置、用户资料等页面
- 模块化设计，便于添加新的头部功能

## 使用方法

### 运行应用

```bash
python main.py
```

### 添加新的菜单页面

1. 在 `menu_pages/` 目录下创建新的页面文件
2. 在 `menu_pages/__init__.py` 中导入并添加到 `get_menu_page_handlers()` 函数
3. 在 `main.py` 的 `menu_items` 配置中添加对应菜单项

### 添加新的头部功能页面

1. 在 `header_pages/` 目录下创建新的页面文件
2. 在 `header_pages/__init__.py` 中导入并添加到 `get_header_page_handlers()` 函数
3. 在 `main.py` 的 `header_config_items` 配置中添加对应配置项

### 自定义布局配置

```python
from component import LayoutConfig

# 创建自定义配置
custom_config = LayoutConfig()
custom_config.app_title = '你的应用标题'
custom_config.app_icon = './your_icon.svg'
custom_config.header_bg = 'bg-purple-600'

# 在装饰器中使用
@with_spa_layout(config=custom_config, ...)
```

## 特性

- 🎨 **现代化设计**: 支持暗色主题，响应式布局
- 🧩 **模块化架构**: 清晰的代码组织，易于维护和扩展
- 🚀 **SPA体验**: 单页应用路由，无刷新页面切换
- ⚙️ **可配置**: 灵活的布局配置和菜单定制
- 📱 **响应式**: 适配不同屏幕尺寸

## 扩展指南

### 添加新功能模块

1. 创建新的包目录
2. 定义页面处理函数
3. 在主文件中导入并配置路由
4. 更新菜单或头部配置

### 自定义样式

通过修改 `LayoutConfig` 类或在页面处理函数中使用 NiceGUI 的 CSS 类来自定义样式。

### 集成外部服务

在对应的页面模块中添加外部API调用、数据库连接等功能。

## 依赖

- NiceGUI: 用于构建Web界面
- Python 3.7+

## 许可证

MIT License