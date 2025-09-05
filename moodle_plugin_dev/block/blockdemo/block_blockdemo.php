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

        // 2. 展示实例配置数据
        $html .= $this->get_instance_config_table();

        // 3. 展示全局配置数据
        $html .= $this->get_global_config_table();

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

        // $this->page 对象详细信息
        if ($this->page) {
            $html .= '<h5>Page对象信息 ($this->page)：</h5>';
            $html .= '<table class="blockdemo-table">';
            $html .= '<thead><tr><th>属性</th><th>值</th><th>说明</th></tr></thead>';
            $html .= '<tbody>';

            $pageInfo = [
                'class' => get_class($this->page),
                'pagetype' => $this->page->pagetype ?? 'null',
                'subpage' => $this->page->subpage ?? 'null',
                'url' => $this->page->url ? $this->page->url->out() : 'null',
                'title' => $this->page->title ?? 'null',
                'course_id' => $this->page->course ? $this->page->course->id : 'null',
                'course_shortname' => $this->page->course ? $this->page->course->shortname : 'null',
                'theme_name' => $this->page->theme ? $this->page->theme->name : 'null',
                'user_is_editing' => $this->page->user_is_editing() ? 'true' : 'false',
            ];

            foreach ($pageInfo as $key => $value) {
                $description = $this->getPagePropertyDescription($key);
                $html .= "<tr><td>{$key}</td><td>" . htmlspecialchars($value) . "</td><td>{$description}</td></tr>";
            }
            $html .= '</tbody></table>';
        }

        // $this->context 对象详细信息
        if ($this->context) {
            $html .= '<h5>Context对象信息 ($this->context)：</h5>';
            $html .= '<table class="blockdemo-table">';
            $html .= '<thead><tr><th>属性</th><th>值</th><th>说明</th></tr></thead>';
            $html .= '<tbody>';

            $contextInfo = [
                'class' => get_class($this->context),
                'id' => $this->context->id,
                'contextlevel' => $this->context->contextlevel,
                'contextlevel_name' => $this->getContextLevelName($this->context->contextlevel),
                'instanceid' => $this->context->instanceid,
                'path' => $this->context->path,
                'depth' => $this->context->depth,
            ];

            // 获取父上下文信息
            $parentcontext = $this->context->get_parent_context();
            if ($parentcontext) {
                $contextInfo['parent_context_id'] = $parentcontext->id;
                $contextInfo['parent_context_level'] = $this->getContextLevelName($parentcontext->contextlevel);
            }

            foreach ($contextInfo as $key => $value) {
                $description = $this->getContextPropertyDescription($key);
                $html .= "<tr><td>{$key}</td><td>" . htmlspecialchars($value) . "</td><td>{$description}</td></tr>";
            }
            $html .= '</tbody></table>';
        }

        // $this->instance 对象详细信息
        if ($this->instance) {
            $html .= '<h5>Instance对象信息 ($this->instance)：</h5>';
            $html .= '<table class="blockdemo-table">';
            $html .= '<thead><tr><th>属性</th><th>值</th><th>说明</th></tr></thead>';
            $html .= '<tbody>';

            $instanceInfo = [
                'id' => $this->instance->id,
                'blockname' => $this->instance->blockname,
                'parentcontextid' => $this->instance->parentcontextid,
                'showinsubcontexts' => $this->instance->showinsubcontexts,
                'pagetypepattern' => $this->instance->pagetypepattern,
                'subpagepattern' => $this->instance->subpagepattern,
                'defaultregion' => $this->instance->defaultregion,
                'defaultweight' => $this->instance->defaultweight,
                'visible' => $this->instance->visible ? 'true' : 'false',
                'timecreated' => date('Y-m-d H:i:s', $this->instance->timecreated),
                'timemodified' => date('Y-m-d H:i:s', $this->instance->timemodified),
            ];

            foreach ($instanceInfo as $key => $value) {
                $description = $this->getInstancePropertyDescription($key);
                $html .= "<tr><td>{$key}</td><td>" . htmlspecialchars($value) . "</td><td>{$description}</td></tr>";
            }
            $html .= '</tbody></table>';
        }

        $html .= '</div>';
        return $html;
    }

    /**
     * 获取页面属性描述
     */
    private function getPagePropertyDescription($property)
    {
        $descriptions = [
            'class' => 'Page对象的类名',
            'pagetype' => '页面类型标识符',
            'subpage' => '子页面标识符',
            'url' => '当前页面的完整URL',
            'title' => '页面标题',
            'course_id' => '所属课程ID',
            'course_shortname' => '课程简称',
            'theme_name' => '当前使用的主题名称',
            'user_is_editing' => '用户是否处于编辑模式',
        ];
        return $descriptions[$property] ?? '未知属性';
    }

    /**
     * 获取上下文属性描述
     */
    private function getContextPropertyDescription($property)
    {
        $descriptions = [
            'class' => 'Context对象的类名',
            'id' => '上下文唯一标识符',
            'contextlevel' => '上下文级别数值',
            'contextlevel_name' => '上下文级别名称',
            'instanceid' => '关联实例的ID',
            'path' => '上下文路径',
            'depth' => '上下文深度',
            'parent_context_id' => '父上下文ID',
            'parent_context_level' => '父上下文级别',
        ];
        return $descriptions[$property] ?? '未知属性';
    }

    /**
     * 获取实例属性描述
     */
    private function getInstancePropertyDescription($property)
    {
        $descriptions = [
            'id' => '块实例唯一标识符',
            'blockname' => '块的名称',
            'parentcontextid' => '父上下文ID',
            'showinsubcontexts' => '是否在子上下文中显示',
            'pagetypepattern' => '页面类型模式',
            'subpagepattern' => '子页面模式',
            'defaultregion' => '默认显示区域',
            'defaultweight' => '默认权重',
            'visible' => '是否可见',
            'timecreated' => '创建时间',
            'timemodified' => '最后修改时间',
        ];
        return $descriptions[$property] ?? '未知属性';
    }

    /**
     * 获取上下文级别名称
     */
    private function getContextLevelName($level)
    {
        $levels = [
            CONTEXT_SYSTEM => 'SYSTEM',
            CONTEXT_USER => 'USER',
            CONTEXT_COURSECAT => 'COURSECAT',
            CONTEXT_COURSE => 'COURSE',
            CONTEXT_MODULE => 'MODULE',
            CONTEXT_BLOCK => 'BLOCK',
        ];
        return $levels[$level] ?? "UNKNOWN({$level})";
    }


    /**
     * 获取实例配置表格
     * @return string HTML表格
     */
    private function get_instance_config_table()
    {
        $html = '<div class="blockdemo-section">';
        $html .= '<div class="blockdemo-title">2. 实例配置数据 ($this->config)</div>';
        $html .= '<table class="blockdemo-table">';
        $html .= '<thead><tr><th>配置项</th><th>值</th><th>说明</th></tr></thead>';
        $html .= '<tbody>';

        if (empty($this->config)) {
            $html .= '<tr><td colspan="3">暂无实例配置数据（请通过编辑区块进行配置）</td></tr>';
        } else {
            // 显示配置的数据
            $configs = [
                'customtext' => isset($this->config->customtext) ? $this->config->customtext : '未设置',
                'displaymode' => isset($this->config->displaymode) ? $this->config->displaymode : '未设置',
            ];

            foreach ($configs as $key => $value) {
                $description = '';
                switch ($key) {
                    case 'customtext':
                        $description = '用户自定义的文本内容';
                        break;
                    case 'displaymode':
                        $description = '显示模式设置';
                        break;
                }

                $displayValue = is_string($value) ? htmlspecialchars($value) : $value;
                $html .= "<tr><td>{$key}</td><td>{$displayValue}</td><td>{$description}</td></tr>";
            }
        }

        $html .= '</tbody></table></div>';
        return $html;
    }

    /**
     * 获取全局配置表格
     * @return string HTML表格
     */
    private function get_global_config_table()
    {
        $html = '<div class="blockdemo-section">';
        $html .= '<div class="blockdemo-title">3. 全局配置数据 (get_config)</div>';
        $html .= '<table class="blockdemo-table">';
        $html .= '<thead><tr><th>配置项</th><th>值</th><th>说明</th></tr></thead>';
        $html .= '<tbody>';

        // 获取全局配置数据
        $globalConfigs = [
            'defaultwelcome' => get_config('block_blockdemo', 'defaultwelcome'),
            'showuserinfo' => get_config('block_blockdemo', 'showuserinfo'),
            'maxtextlength' => get_config('block_blockdemo', 'maxtextlength'),
            'defaultdisplay' => get_config('block_blockdemo', 'defaultdisplay'),
        ];

        foreach ($globalConfigs as $key => $value) {
            $description = '';
            switch ($key) {
                case 'defaultwelcome':
                    $description = '默认欢迎消息';
                    break;
                case 'showuserinfo':
                    $description = '是否显示用户信息';
                    break;
                case 'maxtextlength':
                    $description = '最大文本长度限制';
                    break;
                case 'defaultdisplay':
                    $description = '默认显示模式';
                    break;
            }

            $displayValue = is_bool($value) ? ($value ? 'true' : 'false') :
                (is_null($value) ? '未设置' :
                    (is_string($value) ? htmlspecialchars($value) : $value));

            $html .= "<tr><td>{$key}</td><td>{$displayValue}</td><td>{$description}</td></tr>";
        }

        $html .= '</tbody></table></div>';
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
