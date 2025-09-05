<?php
/**
 * Block blockdemo
 *
 * Documentation: {@link https://moodledev.io/docs/apis/plugintypes/blocks}
 *
 * @package    block_blockdemo
 * 
 */

/*
1. Moodle加载插件时首先读取 version.php 获取插件信息
2. 当需要显示block时，实例化 block_blockdemo 类：
   - init() 方法设置基本属性
   - get_content() 方法生成要显示的内容
   - applicable_formats() 决定在哪些页面显示
3. 用户点击"配置"时：
   - 实例化 block_blockdemo_edit_form 类
   - specific_definition() 方法构建配置表单
   - 用户提交后，配置保存到 $this->config
4. 权限检查：
   - db/access.php 中定义的权限控制谁能添加/配置block
5. 多语言支持：
   - get_string() 函数从 lang/en/block_blockdemo.php 获取文本
*/
class block_blockdemo extends block_base
{

    /**
     * Block initialisation
     */
    public function init()
    {
        $this->title = get_string('pluginname', 'block_blockdemo');
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
        return true; // 这个示例不需要全局配置
    }
}
