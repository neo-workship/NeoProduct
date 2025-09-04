<?php
/**
 * Moodle 聊天块插件
 * 
 * 这个类实现了 Moodle 平台上的 neo_chat 块功能。
 * 提供基本的块初始化、内容获取和配置检查功能。
 * 
 * @package    block_neo_chat
 * @copyright  2023
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */
class block_neo_chat extends block_base
{

    /**
     * 初始化区块实例，设置区块标题为插件名称
     * 
     * 使用语言包中的'pluginname'字符串作为区块标题
     */
    public function init()
    {
        $this->title = get_string('pluginname', 'block_neo_chat');
    }

    /**
     * 检查插件是否拥有配置页面
     * 
     * @return bool 始终返回true，表示该插件有配置页面
     */
    public function has_config()
    {
        return true;
    }

    /**
     * 定义该区块适用的页面格式
     * 
     * @return array 返回一个关联数组，键为页面格式，值为布尔值表示是否适用
     * 当前设置为适用于所有页面格式 ('all'=>true)
     */
    public function applicable_formats()
    {
        return array('all' => true);
    }

    /**
     * 当区块实例有自定义标题时，设置区块标题
     * 
     * 该方法检查配置中是否存在自定义标题，若存在则将其赋值给区块的title属性
     */
    public function specialization()
    {
        /** $this 是插件对象 */
        if (!empty($this->config->title)) {
            $this->title = $this->config->title;
        }
    }

    /**
     * Get content，方法用于生成块的内容。
     * 这个方法通常会在块被渲染到页面上时调用，负责生成块的 HTML 和其他显示内容。
     * content 指的是块的具体显示内容，包括 HTML、文本、图像等所有需要在页面上展示的元素。
     * 将一个块添加到课程页面时，Moodle 会在渲染页面时自动调用 get_content 方法，以便生成并显示该块的内容
     * @return stdClass
     */
    public function get_content()
    {
        /**
         * 声明全局变量 $OUTPUT，用于输出内容到页面
         */
        global $OUTPUT;

        /**
         * 声明全局变量 $PAGE，用于访问 Moodle 页面渲染器对象
         */
        global $PAGE;

        /**
         * get_content 方法在之前已经被调用过并且生成了内容，
         * 那么 $this->content 将包含这些生成的数据，否则它将是 null。
         * $this->content 返回给调用 get_content 方法的代码，通常是 Moodle 页面的渲染器。
         * 内容会在 Moodle 页面渲染过程中被整合到页面的整体布局中，最终发送到用户的浏览器，从而在页面上显示出来。
         * 以下说明不是第一次调用 get_content 方法，因此 $this->content 不为空
         */
        if ($this->content !== null) {
            return $this->content;
        }

        // Send data to front end
        $this->page->requires->js_call_amd(
            'block_neo_chat/lib',
            'init',
            [
                [
                    'blockId' => $this->instance->id,
                    'api_type' => get_config('block_neo_chat', 'type') ? get_config('block_neo_chat', 'type') : 'chat',
                    'persistConvo' => 'persistConvo'
                ]
            ]
        );

        //确定是否应该显示名称标签
        $showlabelscss = '';
        /** $this->config存在 , $this->config->showlabels为真 
         * 如果条件满足，则将特定的CSS规则赋值给$showlabelscss变量
         */
        if (!empty($this->config) && $this->config->showlabels) {
            $showlabelscss = '
                .neochat_message:before{
                    display:none;
                }
                .neochat_message{
                    margin-bottom:05.rem;
                }
            ';
        }

        $assistantname = get_config('block_neo_chat', 'assistantname') ? get_config('block_neo_chat', 'assistantname') : 'AI助手';
        $username = get_config('block_neo_chat', 'username') ? get_config('block_neo_chat', 'username') : '用户';

        if (!empty($this->config)) {
            $assistantname = (property_exists($this->config, 'assistantname') && $this->config->assistantname) ? $this->config->assistantname : $assistantname;
            $username = (property_exists($this->config, 'username') && $this->config->username) ? $this->config->username : $username;
        }

        /**
         * 对聊天模块中的用户名和助手名称进行格式化处理
         * $assistantname：待格式化的原始助手名称字符串。
         * true：表示启用多语言过滤器（若配置了多语言内容，会进行相应转换）
         * ['context' => $this->context]：传递当前块的上下文（context），确保格式化时遵循 Moodle 的权限和安全性规则（如防止 XSS 攻击）
         * 结果：返回一个经过转义和处理的字符串，确保其安全显示。
         */
        $assistantname = format_string($assistantname, true, ['context' => $this->context]);
        $username = format_string($username, true, ['context' => $this->context]);

        /**
         *  初始化区块内容:$this->content = new stdClass();
         *  创建一个新的标准类对象stdClass()并赋值给$this->content，用于存储区块的渲染内容。
         */
        $this->content = new stdClass();

        /**
         * showlabels用于控制是否显示聊天消息的发送者标签
         * .neochat_message:before{display:none;} 会覆盖后面的规则，
         * 即虽然设置了 .user:before 和 .bot:before 的内容，但因为 display:none 的存在，这些内容实际上不会显示出来。
         * 
         * role="log" 是 ARIA 属性，表示该区域会动态更新内容（如聊天消息），辅助技术（如屏幕阅读器）会通知用户内容变化。
         */
        $this->content->text = '
            <script>
                var assistantName = "' . $assistantname . '";
                var userName = "' . $username . '";
            </script>

            <style>
                ' . $showlabelscss . '
                .neochat_message.user:before{
                    content: "' . $username . '";
                }
                .neochat_message.bot:before{
                    content: "' . $assistantname . '";
                }
            </style>

            <div id="neochat_log" role="log"></div>
        ';

        /**
         * empty(get_config('block_neo_chat', 'apikey')) - 检查全局配置中是否没有设置API密钥
         * 同时（&&）满足以下条件
         * !get_config('block_neo_chat', 'allowinstancesettings') - 不允许在实例级别进行设置
         * 或者 empty($this->config->apikey) - 当前实例的API密钥为空
         */
        if (
            empty(get_config('block_neo_chat', 'apikey')) &&
            (!get_config('block_neo_chat', 'allowinstancesettings') || empty($this->config->apikey))
        ) {
            /**如果缺少API密钥，页脚会显示一个错误消息，使用语言字符串 'apikeymissing' 从block_neo_chat语言包中获取 */
            $this->content->footer = get_string('apikeymissing', 'block_neo_chat');
        } else {
            $contextdata = [
                'logging_enabled' => get_config('block_neo_chat', 'logging'),
                'is_edit_mode' => $PAGE->user_is_editing(),
                'pix_popout' => '/blocks/neo_chat/pix/arrow-up-right-from-square.svg',
                'pix_arrow_right' => '/blocks/neo_chat/pix/arrow-right.svg',
                'pix_refresh' => '/blocks/neo_chat/pix/refresh.svg',
            ];
            // 渲染'block_neo_chat/control_bar'模板，
            // 将$contextdata作为上下文数据传递，并将结果设置为页脚内容。
            $this->content->footer = $OUTPUT->render_from_template('block_neo_chat/control_bar', $contextdata);
        }

        return $this->content;

    }
}
