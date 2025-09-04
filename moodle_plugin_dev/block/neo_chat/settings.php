<?php
// This file is part of Moodle - http://moodle.org/
//
// Moodle is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// Moodle is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with Moodle.  If not, see <http://www.gnu.org/licenses/>.

/**
 * TODO describe file settings
 *
 * @package    block_neo_chat
 * @copyright  2025 YOUR NAME <your@email.com>
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

use function DI\get;

/**
 * 防止直接访问文件的保护机制
 * 
 * 这段代码确保文件只能通过Moodle内部系统访问
 * 如果不是通过合法途径访问，将终止脚本执行
 */
defined('MOODLE_INTERNAL') || die();


/**
 * 检查当前用户是否具有站点配置权限
 * 
 * @global bool $hassiteconfig 表示用户是否有站点配置权限的全局变量
 */
if ($hassiteconfig) {

    /**
     * 检查当前是否不在Behat测试环境中运行
     * 
     * BEHAT_SITE_RUNNING是Behat测试框架定义的常量，用于标识测试环境
     * 此条件用于确保某些代码只在非测试环境下执行
     */
    if (!defined('BEHAT_SITE_RUNNING')) {
        /**
         * 将Neo聊天报告页面添加到管理员报告菜单中
         * 
         * 创建一个外部管理页面链接，指向聊天报告页面，并设置所需权限
         * 该链接将显示在Moodle后台的"报告"菜单下
         * 
         * @param string $parent 父菜单项（此处为'reports'）
         * @param admin_externalpage $page 外部页面配置对象
         * @param string $capability 访问该页面所需的权限（此处为'moodle/site:config'）
         */
        $ADMIN->add(
            'reports',
             new admin_externalpage(
                'neo_chat_report',
                get_string('neo_chat_logs', 'block_neo_chat'),
                /**
                 * 生成指向 neo_chat 模块报告页面的 URL，并传递课程 ID 参数
                 * 
                 * @param int $courseid 课程 ID，默认为 1
                 * @return moodle_url 返回配置好的报告页面 URL 对象，`$CFG->wwwroot`：Moodle站点的根URL
                 */
                new moodle_url("$CFG->wwwroot/blocks/neo_chat/report.php", ['courseid' => 1]),

                /**
                 * 定义访问控制权限字符串，表示拥有站点配置权限
                 * 
                 * 该字符串用于权限检查，标识用户是否具备修改Moodle站点配置的权限
                 * moodle/site:config 是一个最高级别的权限，通常仅授予站点管理员
                 */
                'moodle/site:config'
            )
        );
    }

    /**
     * 检查是否在管理员设置的全树模式下，用于确定是否显示完整的配置选项
     */
    if ($ADMIN->fulltree) {
        /**
         * 引入 neo_chat 模块的核心库文件
         * 
         * 该代码用于加载位于 /blocks/neo_chat/ 目录下的 lib.php 库文件
         * 通过全局配置 $CFG 中的 dirroot 获取 Moodle 根目录路径
         */
        require_once($CFG->dirroot . '/blocks/neo_chat/lib.php');

        /**
         * 根据显示类型获取助手数组
         * 
         * 首先获取当前显示类型，若类型为'assistant'则调用fetch_assistants_array()获取助手数组，
         * 否则返回空数组。主要用于动态加载不同类型的显示数据。
         */
        $type = get_type_to_display();
        $assistant_array = [];
        if( $type === 'assistant') {
            $assistant_array = fetch_assistants_array();
        }

        /**
         * 加载 block_neo_chat/settings 模块的 AMD JavaScript 并初始化
         * 
         * 使用 Moodle 的 $PAGE->requires->js_call_amd() 方法调用指定的 AMD 模块
         * 该代码通常在设置页面中使用，用于初始化聊天模块的相关设置
         */
        global $PAGE;
        $PAGE->requires->js_call_amd('block_neo_chat/settings', 'init');

        /**
         * 添加API密钥配置项到插件设置
         * 
         * 创建一个文本输入类型的配置项，用于存储Neo Chat插件的API密钥。
         * 配置项包含显示名称、描述信息，默认值为空字符串，参数类型为PARAM_TEXT。
         */
        $settings->add(new admin_setting_configtext(
            'block_neo_chat/apikey',
            get_string('apikey','block_neo_chat'),
            get_string('apikey_desc','block_neo_chat'),
            '',
            PARAM_TEXT
        ));

 
        /**
         * 添加聊天区块类型设置选项
         * 
         * 该设置允许管理员在区块配置中选择聊天类型，
         * 可选值为 'chat'（普通聊天）或 'assistant'（AI助手模式）。
         * 设置项使用下拉选择框形式呈现。
         */
        $settings->add(new admin_setting_configselect(
            'block_neo_chat/type',
            get_string('type','block_neo_chat'),
            get_string('type_desc','block_neo_chat'),
            'chat',
            ['chat'=>'chat','assistant'=>'assistant']
        ));

        /**
         * 添加一个管理设置复选框，用于限制聊天功能的使用
         * 
         * 该设置项允许管理员控制是否限制聊天功能的使用，
         * 默认值为1（启用限制）
         * 
         * @param string $name 设置项名称（'block_neo_chat/restrictusage'）
         * @param string $visiblename 显示名称（通过get_string获取）
         * @param string $description 描述文本（通过get_string获取）
         * @param int $defaultvalue 默认值（1表示启用）
         */
        $settings->add(new admin_setting_configcheckbox(
            'block_neo_chat/restrictusage',
            get_string('restrictusage','block_neo_chat'),
            get_string('restrictusage_desc','block_neo_chat'),
            1
        ));

        /**
         * 添加一个管理设置项，用于配置聊天助手的名称
         * 
         * 该设置项允许管理员在后台配置聊天助手的显示名称，
         * 默认值为"AI助手"，参数类型为PARAM_TEXT纯文本格式
         * 
         * @param string $name 设置项名称（'block_neo_chat/assistant'）
         * @param string $title 设置项标题（通过语言字符串获取）
         * @param string $description 设置项描述（通过语言字符串获取）
         * @param string $default 默认值"AI助手"
         * @param int $paramtype 参数类型PARAM_TEXT
         */
        $settings->add(new admin_setting_configtext(
            'block_neo_chat/assistant',
            get_string('assistantname','block_neo_chat'),
            get_string('assistantname_desc','block_neo_chat'),
            'AI助手',
            PARAM_TEXT
        ));


        /**
         * 添加聊天块用户名配置设置
         * 
         * 创建一个文本输入类型的配置项，用于设置聊天功能的默认用户名。
         * 包含配置标题、描述信息和默认值 '用户'。
         * 参数类型为 PARAM_TEXT 确保输入内容为纯文本格式。
         */
        $settings->add(new admin_setting_configtext(
            'block_neo_chat/username',
            get_string('username','block_neo_chat'),
            get_string('username_desc','block_neo_chat'),
            '用户',
            PARAM_TEXT
        ));


        /**
         * 添加一个管理设置复选框，用于控制聊天模块的日志记录功能
         * 
         * 该设置项包含：
         * - 设置名称：block_neo_chat/logging
         * - 显示标题：从语言包获取的'logging'字符串
         * - 描述信息：从语言包获取的'logging_desc'字符串
         * - 默认值：0（禁用）
         */
        $settings->add(new admin_setting_configcheckbox(
            'block_neo_chat/logging',
            get_string('logging','block_neo_chat'),
            get_string('logging_desc','block_neo_chat'),
            0
        ));


        /**
         * 添加聊天功能区块的设置标题
         * 
         * 创建一个管理设置标题，用于在区块设置页面中显示聊天功能的标题和描述。
         * 标题和描述文本通过语言字符串获取（chatheading 和 chatheading_desc）。
         */
        $settings->add(new admin_setting_heading(
            'block_neo_chat/chatheading',
            get_string('chatheading','block_neo_chat'),
            get_string('chatheading_desc','block_neo_chat'),
        ));


        /**
         * 添加一个文本区域设置项用于配置聊天提示语
         * 
         * 该设置项允许管理员配置聊天模块的初始提示语内容，
         * 使用 admin_setting_configtextarea 类型创建表单元素，
         * 包含标题、描述和默认值，输入内容将作为PARAM_TEXT类型进行过滤
         */
        $settings->add(new admin_setting_configtextarea(
            'block_neo_chat/prompt',
            get_string('prompt','block_neo_chat'),
            get_string('prompt_desc','block_neo_chat'),
            '下面是用户和系统支持AI助理之间的对话，用于进行辅助学习',
            PARAM_TEXT
        ));


        /**
         * 添加一个管理设置项：文本区域配置，用于设置聊天模块的"真相来源"内容
         * 
         * - 设置项ID: block_neo_chat/sourceoftruth
         * - 显示名称: 使用语言字符串'block_neo_chat'中的'sourceoftruth'
         * - 描述文本: 使用语言字符串'block_neo_chat'中的'sourceoftruth_desc'
         * - 默认值: 空字符串
         * - 参数类型: PARAM_TEXT (纯文本格式)
         */
        $settings->add(new admin_setting_configtextarea(
            'block_neo_chat/sourceoftruth',
            get_string('sourceoftruth','block_neo_chat'),
            get_string('sourceoftruth_desc','block_neo_chat'),
            '',
            PARAM_TEXT
        ));


        /**
         * 添加一个高级设置标题到管理设置页面
         * 
         * 该设置项用于显示区块的高级配置部分，包含标题和描述信息。
         * 标题和描述使用语言字符串从语言文件中获取。
         */
        $settings->add(new admin_setting_heading(
            'block_neo_chat/advanced',
            get_string('advanced','block_neo_chat'),
            get_string('advanced_desc','block_neo_chat')
        ));

        /**
         * 添加一个管理设置复选框，用于控制是否允许neo_chat块的实例设置
         * 
         * 该设置项允许管理员配置是否在neo_chat块中启用实例级别的设置选项
         * 默认值为0(禁用)，可通过管理界面切换
         */
        $settings->add(new admin_setting_configcheckbox(
            'block_neo_chat/allowinstancesettings',
            get_string('allowinstancesettings','block_neo_chat'),
            get_string('allowinstancesettings_desc','block_neo_chat'),
            0
        ));

        /**
         * 添加模型选择设置项
         * 
         * 创建一个下拉菜单设置项，用于选择聊天模型。
         * 默认值为 'deepseek-chat'，选项列表由 get_models() 函数提供。
         * 设置项标题和描述使用语言字符串 'model' 和 'model_desc'。
         */
        $settings->add(new admin_setting_configselect(
            'block_neo_chat/model',
            get_string('model','block_neo_chat'),
            get_string('model_desc','block_neo_chat'),
            'deepseek-chat',
            get_models()['models']
        ));


        /**
         * 添加温度设置项到区块配置中
         * 
         * 创建一个管理设置项用于配置聊天AI的温度参数（影响回答随机性）
         * 默认值为0.5，参数类型为浮点数
         * 使用语言包中的'temperature'作为标题，'temperature_desc'作为描述
         */
        $settings->add(new admin_setting_configtext(
            'block_neo_chat/temperature',
            get_string('temperature','block_neo_chat'),
            get_string('temperature_desc','block_neo_chat'),
            0.5,
            PARAM_FLOAT
        ));


        /**
         * 添加一个管理设置项，用于配置聊天模块的最大令牌数限制
         * 
         * 该设置项允许管理员在后台配置聊天模块允许使用的最大令牌数量，
         * 默认值为5000，参数类型为整数(PARAM_INT)
         * 
         * @param string $name 设置项名称标识符 'block_neo_chat/max_tokens'
         * @param string $visiblename 显示名称(通过语言字符串获取)
         * @param string $description 设置项描述(通过语言字符串获取)
         * @param mixed $defaultvalue 默认值 5000
         * @param int $paramtype 参数类型 PARAM_INT
         */
        $settings->add(new admin_setting_configtext(
            'block_neo_chat/max_tokens',
            get_string('max_tokens','block_neo_chat'),
            get_string('max_tokens_desc','block_neo_chat'),
            5000,
            PARAM_INT
        ));

        /**
         * 添加一个管理设置项，用于配置聊天模块的Top-P参数
         * 
         * 该设置项允许管理员在后台配置生成文本时的Top-P采样值，
         * 参数类型为浮点数，默认值为1。
         * 
         * @param string $name 设置项名称（格式：插件名/参数名）
         * @param string $visiblename 显示名称（通过语言字符串获取）
         * @param string $description 设置项描述（通过语言字符串获取）
         * @param mixed $defaultvalue 默认值
         * @param int $paramtype 参数类型（PARAM_FLOAT表示浮点数）
         */
        $settings->add(new admin_setting_configtext(
            'block_neo_chat/top_p',
            get_string('top_p','block_neo_chat'),
            get_string('top_p_desc','block_neo_chat'),
            1,
            PARAM_FLOAT
        ));


        /**
         * 添加频率惩罚设置项
         * 
         * 用于配置聊天模块中生成回复时的频率惩罚参数，
         * 该参数影响模型避免重复生成相同内容的倾向性。
         * 值为浮点数类型，默认值为1。
         */
        $settings->add(new admin_setting_configtext(
            'block_neo_chat/frequency_penalty',
            get_string('frequency_penalty','block_neo_chat'),
            get_string('frequency_penalty_desc','block_neo_chat'),
            1,
            PARAM_FLOAT
        ));

        /**
         * 添加一个管理设置项，用于配置聊天模块的存在惩罚值
         * 
         * 该设置项允许管理员在后台设置聊天模块的存在惩罚参数，
         * 参数类型为浮点数，默认值为1。
         * 设置项包含显示名称和描述文本，通过语言字符串获取。
         */
        $settings->add(new admin_setting_configtext(
            'block_neo_chat/presence_penalty',
            get_string('presence_penalty','block_neo_chat'),   
            get_string('presence_penalty_desc','block_neo_chat'),
            1,
            PARAM_FLOAT
        ));

    }
}