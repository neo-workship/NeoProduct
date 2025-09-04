```
blocks/neodemo/
├── version.php # 必需：版本和元数据信息
├── block_neodemo.php # 必需：主要的 block 类定义
├── edit_form.php # 可选：block 实例配置表单
├── settings.php # 可选：全局设置页面
├── README.md # 推荐：插件说明文档
├── CHANGES.md # 推荐：版本更新记录
├── db/
│ ├── access.php # 必需：权限定义
│ ├── install.xml # 可选：数据库表结构
│ ├── upgrade.php # 可选：数据库升级脚本
│ └── services.php # 可选：Web 服务定义
├── lang/
│ └── en/
│ └── block_neodemo.php # 必需：英语语言包
├── pix/
│ ├── icon.svg # 推荐：SVG 格式图标
│ ├── icon.png # 备用：PNG 格式图标
│ └── monologo.svg # 可选：单色图标
├── templates/ # 推荐：Mustache 模板
│ ├── block_content.mustache # block 内容模板
│ └── block_settings.mustache # 设置页面模板
├── classes/
│ ├── external/ # Web 服务类
│ ├── output/ # 输出渲染类
│ │ └── renderer.php # 自定义渲染器
│ ├── privacy/ # GDPR 隐私 API
│ │ └── provider.php # 隐私数据提供者
│ ├── task/ # 定时任务类
│ └── form/ # 表单类
├── amd/ # AMD JavaScript 模块
│ ├── build/ # 编译后的 JS 文件
│ └── src/ # 源代码 JS 文件
│ └── neodemo.js # 主要 JS 模块
├── styles/ # SCSS 样式文件
│ └── styles.scss # 主样式文件
├── tests/ # 单元测试
│ ├── behat/ # Behat 功能测试
│ │ └── block_neodemo.feature
│ └── phpunit/ # PHPUnit 单元测试
│ └── block_neodemo_test.php
└── backup/ # 备份/恢复支持
└── moodle2/
├── backup_block_neodemo_stepslib.php
└── restore_block_neodemo_stepslib.php
```
