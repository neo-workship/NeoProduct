# 项目结构

```
streamlit_universal_template/
├── 📄 main.py                      # 应用主入口文件
├── 🔧 requirements.txt             # 依赖包文件
├── 📝 README.md                   # 项目说明文档
├── 🚀 app_manager.sh             # 应用管理脚本
├── ⚙️ config.py                   # 配置文件
├── 🌐 .env                        # 环境变量文件
├── 📋 .gitignore                  # Git忽略文件
│
├── 📂 core/                       # 核心模块
│   ├── 📄 __init__.py
│   ├── 🔐 auth_manager.py         # 认证管理模块
│   ├── 🗄️ database_manager.py     # 数据库管理模块
│   ├── 📊 session_manager.py      # 会话管理模块
│   └── 🔧 utils.py                # 工具函数集合
│
├── 📂 pages/                      # 页面模块
│   ├── 📄 __init__.py
│   ├── 🏠 01_dashboard.py         # 仪表板页面
│   ├── 📊 02_data_view.py         # 数据查看页面
│   ├── ⚙️ 03_settings.py          # 设置页面
│   ├── 👥 04_user_management.py   # 用户管理页面
│   └── 📝 05_about.py             # 关于页面
│
├── 📂 services/                   # 业务服务层
│   ├── 📄 __init__.py
│   ├── 🔌 api_service.py          # API服务
│   ├── 📊 data_service.py         # 数据服务
│   ├── 📧 email_service.py        # 邮件服务
│   └── 📁 file_service.py         # 文件服务
│
├── 📂 models/                     # 数据模型
│   ├── 📄 __init__.py
│   ├── 👤 user.py                 # 用户模型
│   ├── 📊 data_models.py          # 数据模型
│   └── 🏢 business_models.py      # 业务模型
│
├── 📂 utils/                      # 工具模块
│   ├── 📄 __init__.py
│   ├── 🔧 helpers.py              # 辅助函数
│   ├── 🎯 validators.py           # 验证器
│   ├── 📅 date_utils.py           # 日期工具
│   └── 📊 data_utils.py           # 数据处理工具
│
├── 📂 assets/                     # 静态资源（精简）
│   └── 📂 images/
│       ├── 🖼️ logo.png            # 应用Logo
│       └── 🖼️ favicon.ico         # 网站图标
│
├── 📂 templates/                  # 模板文件
│   ├── 📧 email_templates/        # 邮件模板
│   └── 📝 report_templates/       # 报告模板
│
├── 📂 tests/                      # 测试文件
│   ├── 📄 __init__.py
│   ├── 🧪 test_auth.py            # 认证测试
│   └── 🧪 test_utils.py           # 工具测试
│
├── 📂 docs/                       # 文档
│   ├── 📖 user_guide.md          # 用户指南
│   └── 🔧 development_guide.md   # 开发指南
│
├── 📂 data/                       # 数据文件
│   ├── 📊 sample_data.csv         # 示例数据
│   └── 💾 backups/                # 备份文件
│
└── 📂 scripts/                    # 脚本文件
    ├── 🚀 deploy.sh               # 部署脚本
    ├── 📊 init_data.py            # 初始化数据脚本
    └── 🔧 maintenance.py          # 维护脚本
```
