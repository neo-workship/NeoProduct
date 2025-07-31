# 数据绑定

## 1. 绑定命名规律

- 所有组件都有：bind_value, bind_enabled, bind_label, bind_visibility
- 每种绑定都有三个方向：无后缀(双向)、\_from(数据 →UI)、\_to(UI→ 数据)
- 特定组件有专用方法：如 bind_text(label)、bind_filter(table)

## 2. 使用步骤

- 准备数据源 (字典或对象)
- 创建 UI 组件
- 建立绑定关系
- 触发数据更新

## 绑定选择策略

- 输入控件 → 双向绑定 (bind_value)
- 显示控件 → 单向绑定 (bind_text_from)
- 状态控制 → 条件绑定 (with backward)

## 实用技巧

- 使用 backward 参数进行数据转换
- 字典数据用 update() 触发更新
- 对象属性直接赋值自动触发
- 根据数据流向选择合适的绑定方向

# NiceGUI 数据绑定完整指南

## 📋 数据绑定使用步骤

### 1. 准备数据源

```python
# 方式1：使用字典
data = {"name": "张三", "age": 25, "active": True}

# 方式2：使用类对象
class User:
    def __init__(self):
        self.name = "张三"
        self.age = 25
        self.active = True

user = User()
```

### 2. 创建 UI 组件

```python
# 创建需要绑定的UI组件
input_field = ui.input("姓名")
label_display = ui.label()
button = ui.button("提交")
```

### 3. 建立绑定关系

```python
# 绑定输入到数据
input_field.bind_value(data, "name")  # 双向绑定

# 绑定数据到显示
label_display.bind_text_from(data, "name")  # 单向绑定

# 绑定状态控制
button.bind_enabled_from(data, "active")  # 条件绑定
```

### 4. 触发数据更新

```python
# 更新字典数据（触发绑定更新）
data.update(name="李四")

# 更新对象属性（自动触发绑定）
user.name = "李四"
```

## 🔗 通用绑定方法（所有组件都有）

### **值绑定 (Value Binding)**

- `bind_value(obj, prop)` - **双向绑定**：UI ↔ 数据
- `bind_value_from(obj, prop)` - **单向绑定**：数据 → UI
- `bind_value_to(obj, prop)` - **单向绑定**：UI → 数据

### **启用状态绑定 (Enabled Binding)**

- `bind_enabled(obj, prop)` - **双向绑定**：启用状态 ↔ 数据
- `bind_enabled_from(obj, prop)` - **单向绑定**：数据 → 启用状态
- `bind_enabled_to(obj, prop)` - **单向绑定**：启用状态 → 数据

### **标签绑定 (Label Binding)**

- `bind_label(obj, prop)` - **双向绑定**：标签文本 ↔ 数据
- `bind_label_from(obj, prop)` - **单向绑定**：数据 → 标签文本
- `bind_label_to(obj, prop)` - **单向绑定**：标签文本 → 数据

### **可见性绑定 (Visibility Binding)**

- `bind_visibility(obj, prop)` - **双向绑定**：可见性 ↔ 数据
- `bind_visibility_from(obj, prop)` - **单向绑定**：数据 → 可见性
- `bind_visibility_to(obj, prop)` - **单向绑定**：可见性 → 数据

## 🎯 组件特定绑定方法

### **ui.label - 文本标签**

```python
label = ui.label()
label.bind_text(data, "message")        # 双向文本绑定
label.bind_text_from(data, "message")   # 数据 → 文本
label.bind_text_to(data, "message")     # 文本 → 数据
```

### **ui.table - 数据表格**

```python
table = ui.table(columns=cols, rows=rows)
table.bind_filter(data, "search")       # 双向过滤绑定
table.bind_filter_from(data, "search")  # 数据 → 过滤
table.bind_filter_to(data, "search")    # 过滤 → 数据
```

### **ui.input - 输入框**

```python
input_field = ui.input()
# 除了通用方法外，还有：
input_field.bind_value(data, "text")    # 主要用值绑定
```

### **ui.slider - 滑块**

```python
slider = ui.slider(min=0, max=100)
slider.bind_value(data, "progress")     # 数值双向绑定
```

### **ui.switch - 开关**

```python
switch = ui.switch()
switch.bind_value(data, "enabled")      # 布尔值双向绑定
```

## ⚙️ 绑定逻辑与参数

### **backward 参数 - 数据转换**

```python
# 格式化显示
label.bind_text_from(data, "age",
    backward=lambda x: f"年龄：{x}岁")

# 条件转换
button.bind_enabled_from(data, "score",
    backward=lambda x: x >= 60)  # 及格才启用

# 复杂计算
progress.bind_value_from(data, "current",
    backward=lambda x: x / data["total"] * 100)
```

### **绑定逻辑说明**

| 绑定类型          | 数据流向  | 使用场景                  | 示例                                 |
| ----------------- | --------- | ------------------------- | ------------------------------------ |
| `bind_xxx()`      | 双向 ↔    | 输入控件，需要读写数据    | `input.bind_value(data, "name")`     |
| `bind_xxx_from()` | 数据 → UI | 显示控件，只读数据        | `label.bind_text_from(data, "name")` |
| `bind_xxx_to()`   | UI → 数据 | 特殊场景，UI 变化写入数据 | `switch.bind_value_to(data, "flag")` |

## 💡 最佳实践

### **1. 数据源选择**

```python
# ✅ 推荐：使用字典（便于更新）
data = {"user": "张三", "count": 0}
data.update(count=data["count"] + 1)  # 触发绑定更新

# ✅ 推荐：使用类对象（结构清晰）
class AppState:
    def __init__(self):
        self.user = "张三"
        self.count = 0

state = AppState()
state.count += 1  # 自动触发绑定更新
```

### **2. 绑定模式选择**

```python
# 表单输入 - 使用双向绑定
ui.input("姓名").bind_value(user, "name")

# 状态显示 - 使用单向绑定
ui.label().bind_text_from(user, "name")

# 条件控制 - 使用转换函数
ui.button("提交").bind_enabled_from(form, "valid",
    backward=lambda x: x and len(form.get("name", "")) > 0)
```

### **3. 常见绑定模式**

```python
# 模式1：主从同步
master_input = ui.input().bind_value(data, "value")
slave_label = ui.label().bind_text_from(data, "value")

# 模式2：计算绑定
ui.label().bind_text_from(data, "price",
    backward=lambda x: f"¥{x:.2f}")

# 模式3：条件绑定
ui.button("删除").bind_enabled_from(data, "selected_count",
    backward=lambda x: x > 0)

# 模式4：多源绑定（通过计算属性）
def get_full_name():
    return f"{data['first_name']} {data['last_name']}"

ui.label().bind_text_from(data, "first_name",
    backward=lambda x: get_full_name())
```

## ⚠️ 注意事项

1. **没有 `bind_props_from` 方法** - 使用具体的属性绑定方法
2. **数据更新触发** - 字典用 `update()`，对象直接赋值
3. **backward 函数** - 必须返回转换后的值
4. **绑定方向** - 根据数据流向选择合适的绑定类型
5. **性能考虑** - 避免过度复杂的转换函数

通过掌握这些绑定方法和逻辑，你可以轻松实现组件间的数据同步，构建响应式的用户界面！
