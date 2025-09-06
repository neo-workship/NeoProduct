## Moodle 的自动渲染机制

当你调用 $OUTPUT->render($blockproperties) 时，Moodle 会自动执行以下逻辑：

- 检查对象类型: Moodle 检查 $blockproperties 的类名是 block_blockdemo\output\block_properties
- 查找对应的渲染方法: Moodle 会自动查找名为 render_block_properties 的方法
- 自动调用: 如果找到该方法，就会自动调用；如果没找到，则使用默认渲染逻辑

## 方法命名规则

Moodle 使用以下命名约定：

- 类名: block_properties
- 对应的渲染方法: render_block_properties
- 规则: render\_ + 类名

## 两种实现方式

- 方式 1: 使用自定义渲染器（当前方案）

```php
// 在 get_content() 中
$blockproperties = new \block_blockdemo\output\block_properties($this);
$this->content->text = $OUTPUT->render($blockproperties);
```

这种方式会调用 renderer.php 中的 render_block_properties 方法。

- 方式 2: 直接使用模板（更简单的方案）
  实际上，根据最新的 Moodle 规范，我们可以简化这个过程：

```php
// 方式2: 直接使用模板（更简单，不需要自定义渲染器）
$blockproperties = new \block_blockdemo\output\block_properties($this);
$data = $blockproperties->export_for_template($OUTPUT);
$this->content->text = $OUTPUT->render_from_template('block_blockdemo/block_properties', $data);
```

## 1. 渲染函数命名约定

```php
// 如果类名是: block_properties
// 对应的渲染方法名就是: render_block_properties
// 规则: render_ + 下划线命名的类名
```

### 自动查找机制

当调用 $OUTPUT->render($object) 时，Moodle 会：

- 获取对象的类名（去掉命名空间）
- 构造渲染方法名: render\_ + 类名
- 按优先级查找渲染器:

- 首先在插件的自定义渲染器中查找
- 如果没找到，在主题渲染器中查找
- 最后在核心渲染器中查找
- 如果都没找到，使用默认渲染逻辑

```php
/**
 * 自动查找流程：
 * 获取类名: get_class($widget) → 去掉命名空间 → 得到 block_properties
 * 构造方法名: 'render_' . $classname → 得到 render_block_properties
 * 检查方法是否存在: method_exists($this, $rendermethod)
 * 调用方法: 如果存在就调用，否则使用默认处理
 */
class renderer_base {
    public function render(renderable $widget) {
        $classparts = explode('\\', get_class($widget)); // Strip namespaces.
        $classname = array_pop($classparts); // Remove _renderable suffixes
        $classname = preg_replace('/_renderable$/', '', $classname);
        $rendermethod = 'render_'.$classname;
        if (method_exists($this, $rendermethod)) {
            return $this->$rendermethod($widget);
        }
        // 如果没找到，且对象实现了templatable接口，则自动使用模板
        if ($widget instanceof templatable) {
            // 自动模板查找逻辑...
        }
    }
}
```

## 关于 $OUTPUT 对象

$OUTPUT 的真实身份
$OUTPUT 是一个全局变量，它是当前的 core_renderer 实例 Block plugins | Moodle Developer Resources，但它有强大的动态查找能力。

### 渲染器查找优先级

当你调用 $OUTPUT->render($object) 时，Moodle 按以下优先级查找渲染方法：

- 插件的自定义渲染器 (如 block_blockdemo\output\renderer)
- 主题重写的渲染器 (如 theme_boost\output\block_blockdemo\renderer)
- 核心渲染器 (core_renderer)
- 默认模板处理 (如果对象实现了 templatable)
