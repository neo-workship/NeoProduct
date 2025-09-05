<?php
/*
 * Block blockdemo
 * Documentation: {@link https://moodledev.io/docs/apis/plugintypes/blocks}
 */
class block_blockdemo extends block_base
{
    /*
    统一接口                        
     init()           初始化        
     get_content()    获取UI内容    
     specialization() 个性化配置  
     applicable_formats() 适用范围
    */

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

        # 动态内容Block
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
        global $USER;

        if ($this->content !== null) {
            return $this->content;
        }

        $this->content = new stdClass();

        // 从配置中获取自定义消息
        $customtext = isset($this->config->customtext) ? $this->config->customtext : '';

        // 构建显示内容
        $this->content->text = html_writer::div(
            get_string('welcome', 'block_blockdemo', fullname($USER)),
            'block-demo-welcome'
        );

        if (!empty($customtext)) {
            $this->content->text .= html_writer::div(
                format_text($customtext, FORMAT_HTML),
                'block-demo-custom'
            );
        }

        // 添加一个简单的链接到footer
        $this->content->footer = html_writer::link(
            new moodle_url('/user/profile.php'),
            get_string('viewprofile', 'block_blockdemo'),
            ['class' => 'btn btn-sm btn-secondary']
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
        return true;    // 这个示例不需要全局配置
    }

    /**
     * 在加载实例后立即在您的子类上调用此函数
     */
    public function specialization()
    {

    }
}
