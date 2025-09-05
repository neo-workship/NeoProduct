<?php
defined('MOODLE_INTERNAL') || die();

// 插件基本信息
$string['pluginname'] = '演示区块';
$string['blockdemo'] = '演示区块';
$string['blockdemo:addinstance'] = '添加一个新的演示区块';
$string['blockdemo:myaddinstance'] = '添加一个新的演示区块到仪表盘';

// Block内容相关
$string['welcome'] = '欢迎，{$a}！';
$string['viewprofile'] = '查看个人资料';

// 配置表单相关
$string['customtext'] = '>>自定义文本';
$string['customtext_help'] = '>>请输入您想要在区块中显示的任何自定义文本。';
$string['displaymode'] = '>>显示模式';
$string['displaymode_simple'] = '>>简洁视图';
$string['displaymode_detailed'] = '>>详细视图';

// 配置表单相关
$string['customtext'] = 'Custom text';
$string['customtext_help'] = 'Enter any custom text you want to display in the block.';
$string['displaymode'] = 'Display mode';
$string['displaymode_simple'] = 'Simple view';
$string['displaymode_detailed'] = 'Detailed view';

// ==================== 全局配置相关 (settings.php) ====================
$string['generalsettings'] = '常规设置';
$string['generalsettings_desc'] = '为所有演示区块实例配置全局设置。';

$string['defaultwelcome'] = '默认欢迎消息';
$string['defaultwelcome_desc'] = '该消息将默认显示在所有演示区块实例中。';

$string['showuserinfo'] = '显示用户信息';
$string['showuserinfo_desc'] = '启用后将在区块中显示用户名。';

$string['maxtextlength'] = '最大文本长度';
$string['maxtextlength_desc'] = '自定义文本字段允许的最大字符数。';

$string['defaultdisplay'] = '默认显示模式';
$string['defaultdisplay_desc'] = '选择新区块实例的默认显示样式。';

$string['displaymode_card'] = '卡片样式';
$string['displaymode_list'] = '列表样式';
$string['displaymode_minimal'] = '极简样式';

// 隐私相关
$string['privacy:metadata'] = '>>演示区块插件不会存储任何个人数据。';

// ==================== 错误和通知消息 ====================
$string['error:confignotfound'] = '未找到配置。';
$string['error:invaliddata'] = '提供的数据无效。';
$string['notice:texttoolong'] = '文本已截断至允许的最大长度。';

// ==================== 帮助文本 ====================
$string['help:configuration'] = '使用此表单配置当前区块实例的外观和内容。';
$string['help:globalsettings'] = '这些设置将影响全站所有演示区块插件的实例。';