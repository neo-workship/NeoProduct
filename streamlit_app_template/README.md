```
streamlit_app_template/ # streamlit多页面应用模板
├── 系统主页.py          # 主页面文件，应用入口
├── app_manager.sh      # 应用管理脚本，管理Streamlit多页面应用的启动、停止、重启等操作
├── auth_service.py     # Streamlit多页面应用登录认证模块
├── style.css           # 自定义 CSS 样式文件
├── utils.py            # 工具函数模块
├── system_prompt.py    # 系统提示词配置
├── welcome-1.svg       # 使用的图片资源1
├── welcome-2.svg       # 使用的图片资源2
│
├── pages/                  # 页面文件夹
│ ├── 1_📈 数据看板.py        # 页面1
│ ├── 2_🔗 连接企业档案.py    # 页面2
│ ├── 3_📝 创建企业档案.py    # 页面3
│ ├── 4_📇 操作企业档案.py    # 页面4
│ ├── 5_🧬 分析企业档案.py    # 页面5
│ └── 6_👥 用户管理.py        # 页面6
│
├── generatearchives/        # 具体
│ ├── __init__.py
│ ├── generate.py            # 核心档案生成逻辑
│ ├── 一企一档数据项.xlsx     # 企业档案数据项Excel模板
└──
```
