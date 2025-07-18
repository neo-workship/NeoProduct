现在开始拆分工作，对现有的 github 工程中的 auth_service.py 登录认证功能进行拆分、优化到新构造的项目结构中,构建优雅、健壮的优化代码：
1、将数据库表结构设计功能迁移到 models 包中，创建的模型脚本
2、将数据库管理功能迁移到 core/database_manager.py 脚本中（可以灵活切换使用 sqlite、mysql 2 种数据库）；
3、将登录认证工作迁移到 core/auth_manager.py 脚本中
4、将 session 管理功能迁移到 core/session_manager.py 表
是否充分考虑使用 streamlit 框架的功能特点；数据库连接是否有效率问题，是否要用连接池
