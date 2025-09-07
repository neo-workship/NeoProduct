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
$string['morning_title'] = '上午好';
$string['afternoon_title'] = '下午好';
$string['evening_title'] = '晚上好';

// 配置表单相关
$string['customtext'] = '>>自定义文本';
$string['customtext_help'] = '>>请输入您想要在区块中显示的任何自定义文本。';
$string['displaymode'] = '>>显示模式';
$string['displaymode_simple'] = '>>简洁视图';
$string['displaymode_detailed'] = '>>详细视图';

// 配置表单相关
$string['customtext'] = '自定义文本';
$string['customtext_help'] = '输入您想要在区块中显示的任何自定义文本。';
$string['displaymode'] = '展示模式';
$string['displaymode_simple'] = '简单视图';
$string['displaymode_detailed'] = '细节试图';

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

// ==================== 模板相关字符串 ====================
$string['block_properties_title'] = '块属性和基类变量';
$string['basic_properties'] = '基本属性：';
$string['property_name'] = '属性名称';
$string['property_value'] = '值';
$string['property_type'] = '类型';
$string['footer_text'] = '{$a}';

// ==================== 天气功能相关 ====================
$string['weather_settings'] = '天气功能设置';
$string['weather_settings_desc'] = '配置天气API相关设置。';
$string['weather_api_key'] = '天气API密钥';
$string['weather_api_key_desc'] = '输入高德地图天气API的密钥。获取方式：访问高德开放平台 (https://lbs.amap.com/)';
$string['weather_cache_time'] = '天气缓存时间';
$string['weather_cache_time_desc'] = '天气数据缓存时间（分钟），建议30分钟。';
$string['default_city_code'] = '默认城市代码';
$string['default_city_code_desc'] = '默认城市的6位数字代码，例如：110101（北京）';
$string['weather_api_key_missing'] = '未配置天气API KEY';
$string['weather_title'] = '天气信息';
$string['get_weather'] = '获取天气';
$string['refresh_weather'] = '更新天气';
$string['loading'] = '获取中...';
$string['loading_weather'] = '读取数据...';
$string['click_to_load_weather'] = '点击获取';
$string['weather_loaded_successfully'] = '天气数据加载成功';
$string['weather_error_generic'] = '天气错误（通用）';


// ==================== 错误消息 ====================
$string['invalid_city_code'] = '无效的城市代码';
$string['weather_api_error'] = '天气API调用失败';
$string['curl_error'] = '网络连接错误';
$string['http_error'] = 'HTTP请求错误';
$string['json_decode_error'] = 'JSON解析错误';
$string['api_response_error'] = 'API响应错误: {$a}';
$string['no_weather_data'] = '未找到天气数据';
$string['missing_weather_field'] = '缺失天气字段: {$a}';

// ==================== 权限相关 ====================
$string['blockdemo:view'] = '查看演示区块';
// ==================== 缓存相关字符串 ====================
$string['cachedef_weather'] = '天气数据缓存';
$string['cachedef_weather_help'] = '用于缓存从外部API获取的天气数据，减少API调用次数并提高性能。';

// ==================== 调试和状态消息 ====================
$string['debug_weather_api_called'] = '天气API被调用，参数: {$a}';
$string['debug_api_key_missing'] = '天气API密钥缺失';
$string['debug_invalid_city_code'] = '无效的城市代码: {$a}';
$string['debug_cached_data_used'] = '使用缓存的天气数据';
$string['debug_fresh_data_fetched'] = '从API获取新的天气数据';
$string['debug_data_cached'] = '天气数据已缓存';

// ==================== 模板相关字符串 ====================
$string['weather_location'] = '位置';
$string['weather_condition'] = '天气状况';
$string['weather_temp'] = '温度';
$string['weather_humidity_label'] = '湿度';
$string['weather_wind_label'] = '风力';
$string['weather_update_time'] = '更新时间';
$string['weather_no_data'] = '暂无天气数据';

// ==================== 用户界面文本 ====================
$string['retry'] = '重试';
$string['weather_unavailable'] = '天气服务暂时不可用';
$string['check_connection'] = '请检查网络连接';
$string['api_key_required'] = '需要配置API密钥才能使用天气功能';