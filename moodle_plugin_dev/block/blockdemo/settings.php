<?php
/**
 * Block Demo Plugin - Global Settings
 * 文件位置: blocks/blockdemo/settings.php
 * 
 * 这个文件定义了插件的全局配置选项，管理员可以在以下位置访问：
 * Site administration > Plugins > Blocks > Demo Block
 */

defined('MOODLE_INTERNAL') || die();

if ($ADMIN->fulltree) {

    // 插件基本设置标题
    $settings->add(new admin_setting_heading(
        'block_blockdemo_general',
        get_string('generalsettings', 'block_blockdemo'),
        get_string('generalsettings_desc', 'block_blockdemo')
    ));

    // 默认欢迎消息
    $settings->add(new admin_setting_configtext(
        'block_blockdemo/defaultwelcome',
        get_string('defaultwelcome', 'block_blockdemo'),
        get_string('defaultwelcome_desc', 'block_blockdemo'),
        'Welcome to our Moodle site!',
        PARAM_TEXT
    ));

    // 是否显示用户信息
    $settings->add(new admin_setting_configcheckbox(
        'block_blockdemo/showuserinfo',
        get_string('showuserinfo', 'block_blockdemo'),
        get_string('showuserinfo_desc', 'block_blockdemo'),
        1 // 默认启用
    ));

    // 最大自定义文本长度
    $settings->add(new admin_setting_configtext(
        'block_blockdemo/maxtextlength',
        get_string('maxtextlength', 'block_blockdemo'),
        get_string('maxtextlength_desc', 'block_blockdemo'),
        200,
        PARAM_INT
    ));

    // 显示模式选项
    $displayoptions = [
        'card' => get_string('displaymode_card', 'block_blockdemo'),
        'list' => get_string('displaymode_list', 'block_blockdemo'),
        'minimal' => get_string('displaymode_minimal', 'block_blockdemo')
    ];

    $settings->add(new admin_setting_configselect(
        'block_blockdemo/defaultdisplay',
        get_string('defaultdisplay', 'block_blockdemo'),
        get_string('defaultdisplay_desc', 'block_blockdemo'),
        'card',
        $displayoptions
    ));

    // ==================== 天气功能设置 ====================
    $settings->add(new admin_setting_heading(
        'block_blockdemo_weather',
        get_string('weather_settings', 'block_blockdemo'),
        get_string('weather_settings_desc', 'block_blockdemo')
    ));

    // 天气API密钥
    $settings->add(new admin_setting_configtext(
        'block_blockdemo/weather_api_key',
        get_string('weather_api_key', 'block_blockdemo'),
        get_string('weather_api_key_desc', 'block_blockdemo'),
        '',
        PARAM_ALPHANUMEXT
    ));

    // 缓存时间设置
    $settings->add(new admin_setting_configtext(
        'block_blockdemo/weather_cache_time',
        get_string('weather_cache_time', 'block_blockdemo'),
        get_string('weather_cache_time_desc', 'block_blockdemo'),
        30,
        PARAM_INT
    ));

    // 默认城市代码
    $settings->add(new admin_setting_configtext(
        'block_blockdemo/default_city_code',
        get_string('default_city_code', 'block_blockdemo'),
        get_string('default_city_code_desc', 'block_blockdemo'),
        '110101',
        PARAM_ALPHANUMEXT
    ));
}

/**
 * 重要说明：
 * 1. 当插件有 settings.php 文件时，block类中的 has_config() 必须返回 true
 * 2. 所有 settings.php 中使用的字符串都必须在语言包中定义
 * 3. 全局配置通过 get_config('block_blockdemo', 'setting_name') 读取
 */