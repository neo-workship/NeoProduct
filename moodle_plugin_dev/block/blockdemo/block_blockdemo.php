<?php
/**
 * Block blockdemo
 * 
 * Documentation: {@link https://moodledev.io/docs/apis/plugintypes/blocks}
 */
class block_blockdemo extends block_base
{
    /**
     * Block initialisation
     */
    public function init()
    {
        $this->title = get_string('pluginname', 'block_blockdemo');

        // 根据环境设置不同标题
        if (debugging()) {
            $this->title .= ' (Debug)';
        }
        // 动态内容Block
        $hour = (int) date('H');
        if ($hour < 12) {
            $this->title .= get_string('morning_title', 'block_blockdemo');
        } else if ($hour < 18) {
            $this->title .= get_string('afternoon_title', 'block_blockdemo');
        } else {
            $this->title .= get_string('evening_title', 'block_blockdemo');
        }
        // 设置技术属性
        $this->content_type = BLOCK_TYPE_TEXT;
        // 初始化内部状态（但不访问外部数据）
        $this->internal_state = new stdClass();
        $this->internal_state->initialized = true;
        $this->internal_state->init_time = time();
    }

    /**
     * 返回block的内容
     * 这个方法定义了block显示的主要内容
     */
    public function get_content()
    {
        global $OUTPUT;

        if ($this->content !== null) {
            return $this->content;
        }

        $this->content = new stdClass();

        // 方式1: 使用自定义渲染器（会调用 renderer.php 中的 render_block_properties）
        // 创建块属性显示对象
        $blockproperties = new \block_blockdemo\output\block_properties($this);
        // 使用模板渲染内容
        /**
         * 当调用 $OUTPUT->render($blockproperties) 时，Moodle会自动执行以下逻辑：
         *   检查对象类型: Moodle检查 $blockproperties 的类名是 block_blockdemo\output\block_properties
         *   查找对应的渲染方法: Moodle会自动查找名为 render_block_properties 的方法
         *   自动调用: 如果找到该方法，就会自动调用；如果没找到，则使用默认渲染逻辑
         */
        $this->content->text = $OUTPUT->render($blockproperties);

        // 方式2: 直接使用模板（更简单，不需要自定义渲染器）
        // $blockproperties = new \block_blockdemo\output\block_properties($this);
        // $data = $blockproperties->export_for_template($OUTPUT);
        // $this->content->text = $OUTPUT->render_from_template('block_blockdemo/block_properties', $data);

        // 添加简单的footer
        $this->content->footer = html_writer::div(
            '学习用途 - Block数据展示',
            'text-muted small text-center'
        );

        return $this->content;
    }

    /**
     * 定义这个block可以在哪些页面类型中使用
     */
    public function applicable_formats()
    {
        return [
            'course-view' => true,      // 课程页面
            'my' => true,               // 用户仪表板
            'site' => true,             // 站点首页
        ];
    }

    /**
     * 是否允许配置实例
     */
    public function instance_allow_config()
    {
        return true;
    }

    /**
     * 是否允许多个实例
     */
    public function instance_allow_multiple()
    {
        return true;
    }

    /**
     * 是否有全局配置
     */
    public function has_config()
    {
        return true;
    }

    /**
     * 在加载实例后立即在您的子类上调用此函数
     */
    public function specialization()
    {
        // 可以在这里添加特定的初始化代码
    }
}