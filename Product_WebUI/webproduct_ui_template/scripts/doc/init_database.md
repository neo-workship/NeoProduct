# 数据库初始化使用指南

## 🎯 设计理念

现在的方案完全符合您的要求：

1. **复用现有ORM模型**：直接导入 `auth/models.py` 和 `database_models/business_models/` 中的模型
2. **使用项目配置**：自动读取 `auth/config.py` 中的 `database_url` 配置
3. **独立的初始化脚本**：`scripts/init_database.py` 可以独立运行，不影响其他代码
4. **易于扩展**：新增业务表只需在对应模型文件中定义，然后在初始化脚本中添加一行导入

## 🚀 使用方法

### 1. 基础初始化（生产环境）
```bash
python scripts/init_database.py
```

### 2. 开发环境初始化（包含测试数据）
```bash
python scripts/init_database.py --test-data
```

### 3. 重置数据库（⚠️ 危险操作）
```bash
python scripts/init_database.py --reset --test-data
```

### 4. 详细输出模式
```bash
python scripts/init_database.py --verbose --test-data
```

## 📊 创建的测试账户

运行 `--test-data` 选项后，会自动创建以下测试账户：

| 用户名 | 密码 | 角色 | 权限说明 |
|--------|------|------|----------|
| admin | admin123 | 管理员 | 所有权限 |
| user | user123 | 普通用户 | 基础查看和使用权限 |
| editor | editor123 | 编辑者 | OpenAI相关权限 + 个人资料 |
| viewer | viewer123 | 查看者 | 查看权限 + 个人资料 |

## 🔧 配置说明

脚本会自动读取 `auth/config.py` 中的配置：

- **数据库类型**：`auth_config.database_type` (sqlite/mysql/postgresql)
- **数据库URL**：`auth_config.database_url`
- **默认角色**：`auth_config.default_roles`
- **默认权限**：`auth_config.default_permissions`

### 数据库文件位置

根据 `auth/config.py` 的配置：
- SQLite：`data/auth.db`
- MySQL/PostgreSQL：使用环境变量 `DATABASE_URL`

## 📈 扩展新业务表

### 步骤1：创建业务模型
```python
# database_models/business_models/new_service_models.py
from sqlalchemy import Column, String, Integer
from ..shared_base import BusinessBaseModel

class NewServiceConfig(BusinessBaseModel):
    __tablename__ = 'new_service_configs'
    
    name = Column(String(100), nullable=False)
    endpoint = Column(String(255), nullable=False)
```

### 步骤2：更新初始化脚本
```python
# 在 scripts/init_database.py 的 import_all_models 方法中添加：
from database_models.business_models.new_service_models import NewServiceConfig
self.logger.info("✅ 新服务模型导入成功")

# 在返回的 models 字典中添加：
return {
    # ... 现有模型
    'NewServiceConfig': NewServiceConfig,
}
```

### 步骤3：添加默认数据（可选）
```python
# 在 init_business_default_data 方法中添加：
self._init_new_service_default_data(models)

# 实现初始化方法：
def _init_new_service_default_data(self, models):
    # 具体的初始化逻辑
    pass
```

## ⚡ 与现有代码的关系

### 完全独立运行
- ✅ **独立脚本**：不依赖 `main.py` 或其他应用代码
- ✅ **配置复用**：使用项目现有的 `auth/config.py` 配置
- ✅ **模型复用**：直接导入现有的 ORM 模型
- ✅ **无副作用**：不会影响正在运行的应用

### 推荐工作流程
1. **开发新功能**时：先运行初始化脚本确保数据库结构最新
2. **部署生产环境**时：运行不带 `--test-data` 的初始化脚本
3. **重置开发环境**时：使用 `--reset --test-data` 选项

## 🛠️ 故障排除

### 常见问题1：模型导入失败
```bash
# 错误信息：ImportError: cannot import name 'SomeModel'
# 解决方案：检查模型文件路径和导入语句
```

### 常见问题2：数据库连接失败
```bash
# 错误信息：Could not connect to database
# 解决方案：检查 auth/config.py 中的数据库配置
```

### 常见问题3：权限初始化失败
```bash
# 错误信息：Permission initialization failed
# 解决方案：确保角色已正确创建，检查权限数据格式
```

## 📝 注意事项

1. **数据安全**：`--reset` 选项会删除所有现有数据，请谨慎使用
2. **权限设计**：建议先规划好权限体系，再运行初始化脚本
3. **配置检查**：运行前确认 `auth/config.py` 中的数据库配置正确
4. **备份习惯**：重要数据库操作前建议先备份

现在的方案实现了您要求的所有特性：使用现有配置、复用ORM模型、独立运行、易于扩展！