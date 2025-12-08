# 🚀 快速开始指南

## 文件说明

本次交付包含以下文件:

1. **init_database.py** - 优化后的数据库初始化脚本
2. **auth_test_page.py** - 认证系统测试页面
3. **任务完成说明.md** - 详细的功能说明文档

---

## ⚡ 快速开始 (5 分钟)

### 步骤 1: 替换原有文件

```bash
# 将 init_database.py 复制到项目的 scripts 目录
cp init_database.py /path/to/webproduct_ui_template/scripts/init_database.py

# 将 auth_test_page.py 复制到项目的 menu_pages 目录
cp auth_test_page.py /path/to/webproduct_ui_template/menu_pages/auth_test_page.py
```

### 步骤 2: 更新 menu_pages/**init**.py

在 `menu_pages/__init__.py` 文件中添加:

```python
from .auth_test_page import auth_test_page_content

def get_menu_page_handlers():
    return {
        'home': home_content,
        'other_page': other_page_content,
        'chat_page': chat_page_content,
        'auth_test': auth_test_page_content,  # ⬅️ 新增这一行
    }

__all__ = [
    'home_content',
    'other_page_content',
    'chat_page_content',
    'auth_test_page_content',  # ⬅️ 新增这一行
    'get_menu_page_handlers'
]
```

### 步骤 3: 添加导航菜单项

在 `multilayer_main.py` 的 `create_demo_menu_structure()` 函数中添加:

```python
def create_demo_menu_structure() -> list[MultilayerMenuItem]:
    menu_items = [
        # ... 现有菜单项 ...

        # 添加认证测试菜单
        MultilayerMenuItem(
            key='auth_test',
            label='认证系统测试',
            icon='security',
            route='auth_test',
            separator_after=True
        ),
    ]
    return menu_items
```

### 步骤 4: 初始化数据库

选择一个场景进行初始化:

```bash
# 方案A: 默认场景 (推荐新手)
python scripts/init_database.py --scenario default --test-data --reset

# 方案B: CMS场景 (内容管理系统)
python scripts/init_database.py --scenario cms --test-data --reset

# 方案C: ERP场景 (企业资源计划)
python scripts/init_database.py --scenario erp --test-data --reset
```

### 步骤 5: 启动应用并测试

```bash
# 启动应用
python multilayer_main.py

# 浏览器访问
http://localhost:8080/workbench
```

---

## 🎯 测试流程

### 测试方案 A: 默认场景快速测试

1. **启动并登录**

   ```
   URL: http://localhost:8080/login
   用户名: admin
   密码: admin123
   ```

2. **访问测试页面**

   - 在左侧菜单找到 "认证系统测试"
   - 点击进入

3. **查看权限效果**

   - 观察管理员拥有所有权限 (全部显示 ✅)
   - 点击 "查看所有用户" 按钮
   - 点击 "查看角色-权限关系" 按钮

4. **切换用户测试**
   - 退出登录
   - 使用 `user / user123` 登录
   - 再次访问测试页面
   - 观察权限变化 (部分显示 ❌)

### 测试方案 B: CMS 场景完整测试

1. **重新初始化为 CMS 场景**

   ```bash
   python scripts/init_database.py --scenario cms --test-data --reset
   ```

2. **测试主编角色**

   ```
   用户名: chief
   密码: chief123
   ```

   - 查看拥有的权限 (文章管理相关权限)

3. **测试作者角色**

   ```
   用户名: author
   密码: author123
   ```

   - 查看权限差异 (无发布权限)

4. **对比权限差异**
   - 在测试页面使用权限测试工具
   - 输入 `article.publish` 测试
   - 观察不同角色的检查结果

### 测试方案 C: 场景切换测试

1. **初始化默认场景**

   ```bash
   python scripts/init_database.py --scenario default --test-data --reset
   ```

   登录查看: 有 `content.*` 权限

2. **切换到 CMS 场景**

   ```bash
   python scripts/init_database.py --scenario cms --test-data --reset
   ```

   登录查看: 变为 `article.*` 权限

3. **切换到 ERP 场景**
   ```bash
   python scripts/init_database.py --scenario erp --test-data --reset
   ```
   登录查看: 变为 `finance.*`, `purchase.*` 等权限

---

## 📋 功能验证清单

使用以下清单确保所有功能正常:

### 数据库初始化功能

- [ ] 可以正常运行 `--scenario default`
- [ ] 可以正常运行 `--scenario cms`
- [ ] 可以正常运行 `--scenario erp`
- [ ] `--test-data` 参数创建测试用户
- [ ] `--reset` 参数清空数据库
- [ ] `--verbose` 参数显示详细日志
- [ ] 命令行帮助信息完整

### 认证测试页面功能

- [ ] 页面可以正常访问
- [ ] 当前用户信息正确显示
- [ ] 权限检查测试功能正常
- [ ] "查看所有用户" 按钮工作正常
- [ ] "查看所有角色" 按钮工作正常
- [ ] "查看所有权限" 按钮工作正常
- [ ] "查看角色-权限关系" 按钮工作正常
- [ ] 权限测试工具功能正常
- [ ] 使用不同用户登录看到不同效果

### 权限系统验证

- [ ] 超级管理员拥有所有权限
- [ ] 普通用户只有限定权限
- [ ] 角色权限正确分配
- [ ] 切换场景后权限配置改变
- [ ] 测试账户可以正常登录

---

## 🐛 常见问题

### Q1: 运行 init_database.py 报错

**A**: 确保在项目根目录运行,并且已安装所有依赖:

```bash
pip install sqlmodel nicegui loguru pyyaml
```

### Q2: 测试页面无法访问

**A**: 检查是否已登录,该页面需要登录权限

### Q3: 看不到新增的菜单项

**A**: 确保已更新 `menu_pages/__init__.py` 和 `multilayer_main.py`

### Q4: 切换场景后看不到变化

**A**: 必须使用 `--reset` 参数清空旧数据:

```bash
python scripts/init_database.py --scenario cms --reset --test-data
```

### Q5: 权限检查始终显示无权限

**A**:

1. 检查是否正确登录
2. 确认用户有对应角色
3. 查看角色是否分配了权限

### Q6: 表格不显示数据

**A**:

1. 确保数据库已初始化
2. 使用 `--test-data` 创建测试数据
3. 检查数据库连接是否正常

---

## 💡 最佳实践

### 开发环境

1. 使用 `default` 场景开始
2. 启用 `--test-data` 创建测试账户
3. 使用 `--verbose` 查看详细日志

### 测试不同角色

1. 为每个角色创建浏览器配置文件
2. 或使用无痕模式切换账户
3. 记录每个角色的权限效果

### 场景定制

1. 复制现有场景类作为模板
2. 修改角色和权限定义
3. 注册到 `SCENARIOS` 字典
4. 更新命令行参数

### 调试权限问题

1. 使用认证测试页面查看数据
2. 使用权限测试工具验证
3. 检查角色权限关系展示
4. 查看数据库原始数据

---

## 📚 相关文档

- **任务完成说明.md** - 详细的功能文档
- **原项目文档** - webproduct-ui-template.md

---

## 🎓 学习建议

### 初级用户

1. 先运行默认场景
2. 使用不同账户登录体验
3. 在测试页面查看权限效果
4. 理解角色和权限的关系

### 中级用户

1. 尝试所有三个场景
2. 对比不同场景的权限配置
3. 修改现有场景的权限
4. 在实际页面中使用权限控制

### 高级用户

1. 创建自定义场景
2. 设计复杂的权限体系
3. 实现动态权限分配
4. 集成到实际业务系统

---

## ✨ 下一步

完成基础测试后,可以:

1. **集成到实际页面**

   - 在业务页面使用 `@require_permission` 装饰器
   - 根据权限显示/隐藏 UI 元素

2. **扩展权限系统**

   - 添加数据级权限 (只能看自己的数据)
   - 实现权限继承
   - 添加权限有效期

3. **优化用户体验**

   - 添加权限申请流程
   - 实现权限审批
   - 权限变更通知

4. **监控和审计**
   - 记录权限检查日志
   - 统计权限使用情况
   - 发现异常权限访问

---

**祝使用愉快!** 🎉

如有问题,请参考 **任务完成说明.md** 获取更多详细信息。
