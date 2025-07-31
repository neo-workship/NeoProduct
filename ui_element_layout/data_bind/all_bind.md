## 主要的数据通信方式

### 1. 数据绑定 (Data Binding)

NiceGUI 提供了强大的内置数据绑定机制，支持组件之间的值绑定。主要包括：

双向绑定: 使用 bind_value()
单向绑定: 使用 bind_value_from() 和 bind_value_to()
属性绑定: 如 bind_text(), bind_enabled() 等

```python
from nicegui import ui
# 双向绑定示例
radio = ui.radio([1, 2, 3], value=1)
toggle = ui.toggle({1: 'A', 2: 'B', 3: 'C'}).bind_value(radio, 'value')
```

### 2. 全局状态管理

可以通过全局对象或字典来共享数据:

```python
# 全局状态示例
shared_data = {"count": 0, "user": None}
@ui.page("/")
def page1():
    ui.label().bind_text_from(shared_data, "count")
    ui.button("增加", on_click=lambda: shared_data.update(count=shared_data["count"]+1))
```

### 3. 刷新机制 (Refreshable)

使用 @ui.refreshable 装饰器来实现响应式更新：

```python
@ui.refreshable
def data_table(): # 当数据变化时重新渲染
    ui.table(columns=cols, rows=get_current_data())
# 数据更新时调用
data_table.refresh()
```

### 4. 事件驱动通信

通过观察者模式实现组件间通信：

```py
class DataStore:
def __init__(self):
    self._data = {}
    self._callbacks = []

        def register_callback(self, callback):
            self._callbacks.append(callback)

        def notify_observers(self):
            for callback in self._callbacks:
                callback()
```

### 5. 页面间数据传递

可以通过 URL 参数、全局对象或应用状态来实现：

```python
@ui.page("/page1/{data}")
def page1(data):
    shared_state["data"] = data

@ui.page("/page2")
def page2():
    ui.label().bind_text_from(shared_state, "data")
```
