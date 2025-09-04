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
 * English language pack for Neo chat
 *
 * @package    block_neo_chat
 * @category   string
 * @copyright  2025 YOUR NAME <your@email.com>
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

defined('MOODLE_INTERNAL') || die();
// 常规设置
$string['pluginname'] = 'Neo 智能';
$string['neo_chat_logs'] = 'Neo Chat 日志';
$string['apikey'] = 'API 密钥';
$string['type'] = '类型';
$string['type_desc'] = 'API类型';
$string['restrictusage'] = '限制登录用户使用';
$string['restrictusage_desc'] = '如果选中此框，则只有登录的用户才能使用聊天框';
$string['assistantname'] = 'AI助手名称';
$string['assistantname_desc'] = '这些设置仅适用于AI助手名称';
$string['username'] = '用户名';
$string['username_desc'] = 'AI内部为用户使用的名称，它也用于聊天窗口中的用户界面标题';

// 聊天设置
$string['chatheading'] = '聊天设置';
$string['chatheading_desc'] = '设置适用于Openai Chat 兼容的API格式';
$string['prompt'] = '提示词';
$string['prompt_desc'] = '在对话记录之前给出提示';
$string['sourceoftruth'] = '少样本学习';
$string['sourceoftruth_desc'] = '在提示中的作用是通过少量样本引导模型对特定任务进行学习和执行，例如通过提供少量风格或主题示例，引导模型产出具有相似风格或主题的创作';
$string['allowinstancesettings'] = '实例级设置';
$string['allowinstancesettings_desc'] = '此设置将允许教师或任何有能力在上下文中添加块的人在每个块级别调整设置。启用此功能可能会产生额外的费用，因为它允许非管理员选择成本更高的模型或其他设置';

// 高级设置
$string['advanced'] = '高级设置';
$string['advanced_desc'] = '发送给大模型的高级参数。除非你知道你在做什么，否则不要修改！';
$string['model'] = '模型';
$string['model_desc'] = '生成完成的模型。一些模型适用于自然语言任务，另一些则专门用于代码';
$string['temperature'] = '温度';
$string['temperature_desc'] = '控制随机性：降低结果导致更少的随机完成。当温度接近零度时，模型将变得确定性和重复性';
$string['max_tokens'] = '最大令牌';
$string['max_tokens_desc'] = '要生成的令牌的最大数量。请求可以在提示和完成之间共享最多2,048或4,000个令牌。确切的极限因型号而异';
$string['top_p'] = 'top p';
$string['top_p_desc'] = '通过核抽样控制多样性：0.5表示考虑了所有可能性加权选项的一半';
$string['frequency_penalty'] = '频率惩罚';
$string['frequency_penalty_desc'] = '根据到目前为止文本中存在的频率对新标记进行多少惩罚。降低模型逐字重复同一行的可能性';
$string['presence_penalty'] = '存在惩罚';
$string['presence_penalty_desc'] = '根据新标记到目前为止是否出现在文本中，对它们进行多少惩罚。增加模型谈论新话题的可能性';

// 默认配置项
$string['loggingenabled'] = "启用日志记录。在此发送或接收的任何信息都将被记录下来，并可由网站管理员查看";
$string['apikeymissing'] = '请输入API密钥';
$string['loggingenbaled'] = '启用日志记录,在此发送或接收的任何信息都将被记录下来，并可由网站管理员查看';
$string['popout'] = '打开聊天窗口';
$string['askaquestion'] = '输入问题...';
$string['new_chat'] = '新聊天';