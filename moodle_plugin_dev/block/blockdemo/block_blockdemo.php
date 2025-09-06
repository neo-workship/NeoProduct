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

        // 构建HTML内容，包含三个数据表格
        $html = '';

        // 添加CSS样式
        $html .= '<style>
            .blockdemo-table { 
                width: 100%; 
                border-collapse: collapse; 
                margin: 10px 0; 
                font-size: 12px;
            }
            .blockdemo-table th, .blockdemo-table td { 
                border: 1px solid #ddd; 
                padding: 5px; 
                text-align: left; 
            }
            .blockdemo-table th { 
                background-color: #f2f2f2; 
                font-weight: bold; 
            }
            .blockdemo-section { 
                margin: 15px 0; 
            }
            .blockdemo-title { 
                font-weight: bold; 
                color: #333; 
                margin: 10px 0 5px 0; 
            }
        </style>';

        // 1. 展示块属性和基类变量
        $html .= $this->get_block_properties_table();

        $this->content->text = $html;

        // 添加简单的footer
        $this->content->footer = html_writer::div(
            '学习用途 - Block数据展示',
            'text-muted small text-center'
        );

        return $this->content;
    }

    /**
     * 获取块属性和基类变量表格
     * @return string HTML表格
     */
    private function get_block_properties_table()
    {
        $html = '<div class="blockdemo-section">';
        $html .= '<div class="blockdemo-title">1. 块属性和基类变量</div>';

        // 基本属性表格
        $html .= '<h5>基本属性：</h5>';
        $html .= '<table class="blockdemo-table">';
        $html .= '<thead><tr><th>属性名称</th><th>值</th><th>类型</th></tr></thead>';
        $html .= '<tbody>';

        // 基类属性
        $properties = [
            'title' => $this->title,
            'arialabel' => $this->arialabel,
            'content_type' => $this->content_type,
            'cron' => $this->cron,
        ];

        // 自定义属性
        if (isset($this->internal_state)) {
            $properties['internal_state->initialized'] = $this->internal_state->initialized ? 'true' : 'false';
            $properties['internal_state->init_time'] = date('Y-m-d H:i:s', $this->internal_state->init_time);
            $properties['internal_state->custom_property'] = $this->internal_state->custom_property;
        }

        foreach ($properties as $name => $value) {
            $type = gettype($value);
            $displayValue = is_bool($value) ? ($value ? 'true' : 'false') :
                (is_null($value) ? 'null' :
                    (is_string($value) ? htmlspecialchars($value) : $value));

            $html .= "<tr><td>{$name}</td><td>{$displayValue}</td><td>{$type}</td></tr>";
        }
        $html .= '</tbody></table>';

        $html .= '</div>';
        return $html;
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
