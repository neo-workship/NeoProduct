<?php
/**
 * Block Neodemo
 * Documentation: {@link https://moodledev.io/docs/apis/plugintypes/blocks}
 */

class block_neodemo extends block_base
{
    /**
     * Block initialisation
     * init() 函数是block插件的第一道初始化关口，相当于对象的"出生证明"和"身份证办理"。
     * 必须实现：所有block都必须有此方法；单次执行：每个block实例只调用一次。
     * 此时用户配置($this->config)还没加载，不可调用；尽量进行轻量化的设置操作。
     */
    public function init()
    {
        $this->title = get_string('pluginname', 'block_neodemo');

        // 根据环境设置不同标题
        if (debugging()) {
            $this->title .= ' (Debug Mode)';
            $hour = (int) date('H');
            if ($hour < 12) {
                $this->title .= " 上午好";
            } else if ($hour < 18) {
                $this->title .= " 下午好";
            } else {
                $this->title .= " 晚上好";
            }
        }

        // 设置技术属性
        $this->content_type = BLOCK_TYPE_TEXT;

        // 初始化内部状态（但不访问外部数据）
        $this->internal_state = new stdClass();
        $this->internal_state->initialized = true;
        $this->internal_state->init_time = time();
    }

    /**
     * 重写父类的 specialization 方法
     * 提供自定义的个性化逻辑
     */
    public function specialization()
    {
        // 你的自定义实现
        if (isset($this->config->custom_title)) {
            $this->title = format_string($this->config->custom_title, true, [
                'context' => $this->context
            ]);
        }
    }

    /**
     * Get content
     * @return stdClass
     */
    public function get_content()
    {
        if ($this->content !== null) {
            return $this->content;
        }
        $this->content = (object) [
            'footer' => '',
            'text' => '',
        ];
        return $this->content;
    }
}
