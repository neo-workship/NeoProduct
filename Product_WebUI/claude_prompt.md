## project instructions

```
你是 NiceGUI 开发专家，帮我优化编写的项目的 UI，形成通用的模板。现在代码构架采用微服务构架：nicegui 作为前端（要搭配一个 fastapi 服务完成路由、认证、权限管理），然后构建若干的 fastapi 业务服务。前端的 nicegui web，分别连接不同的业务 fastapi。这样 fastapi 服务个数就有 n+1，n 表示不同的业务服务。

要认真的参考知识库文件：
1、文件“webproduct_ui_templte_目录结构.txt”是已经编写好的代码的目录结构。
2、文件“webproduct_ui_template_代码.md”是已经编写的项目源代码。
```

```
评估、理解以下需求，分析可行性和方案，先不要写代码。

在 webproduct_ui_template\component 中添加一类新的 UI 布局模式：multilayer_spa_layout。 作用类似 spa_layout.py 和 simple_spa_layout.py。

1、对于 multilayer_spa_layout 布局模式，可以参考 component\spa_layout.py，但不同的是原来左侧功能栏中的功能项是折叠 menu，打开折叠 menu，点击不同的项，调整到对应的页面。

2、考虑添加的文件有：webproduct_ui_template\component \multilayer_spa_layout.py 、webproduct_ui_template\component \multilayer_layout_manager.py、webproduct_ui_template\multilayer_main.py
```
