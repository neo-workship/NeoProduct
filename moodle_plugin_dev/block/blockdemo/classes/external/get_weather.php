<?php
namespace block_blockdemo\external;

use core_external\external_api;
use core_external\external_function_parameters;
use core_external\external_value;
use core_external\external_single_structure;
use core_external\external_warnings;
use context_system;
use moodle_exception;

/**
 * External function for getting weather information
 */
class get_weather extends external_api
{

    /**
     * Describes the parameters for get_weather.
     * @return external_function_parameters
     */
    public static function execute_parameters()
    {
        return new external_function_parameters([
            'citycode' => new external_value(
                PARAM_ALPHANUMEXT,
                'City code for weather query (e.g., 110101 for Beijing)',
                VALUE_REQUIRED
            ),
            'refresh' => new external_value(
                PARAM_BOOL,
                'Force refresh cache',
                VALUE_DEFAULT,
                false
            ),
        ]);
    }

    /**
     * Get weather information from external API
     *
     * @param string $citycode The city code to get weather for
     * @param bool $refresh Whether to force refresh the cache
     * @return array Weather information
     * @throws moodle_exception
     */
    public static function execute($citycode, $refresh = false)
    {
        global $CFG;

        // Validate parameters.
        $params = self::validate_parameters(self::execute_parameters(), [
            'citycode' => $citycode,
            'refresh' => $refresh,
        ]);

        // Check capabilities.
        $context = context_system::instance();
        self::validate_context($context);

        // Check if user has permission to view weather data.
        require_capability('block/blockdemo:view', $context);

        // 调试输出
        debugging('Weather API called with params: ' . json_encode($params), DEBUG_DEVELOPER);

        // Get API key from configuration.
        $apikey = get_config('block_blockdemo', 'weather_api_key');
        if (empty($apikey)) {
            debugging('Weather API key is missing', DEBUG_DEVELOPER);
            throw new moodle_exception('weather_api_key_missing', 'block_blockdemo');
        }

        // Validate city code format.
        if (!self::validate_city_code($params['citycode'])) {
            debugging('Invalid city code: ' . $params['citycode'], DEBUG_DEVELOPER);
            throw new moodle_exception('invalid_city_code', 'block_blockdemo');
        }

        try {
            // Check cache first (unless refresh is requested).
            $cachekey = 'weather_' . $params['citycode'];
            $cache = \cache::make('block_blockdemo', 'weather');

            if (!$params['refresh']) {
                $cacheddata = $cache->get($cachekey);
                if ($cacheddata !== false) {
                    debugging('Returning cached weather data', DEBUG_DEVELOPER);
                    // 确保缓存数据格式正确
                    return self::ensure_return_format($cacheddata);
                }
            }

            // Call external weather API.
            debugging('Fetching fresh weather data from API', DEBUG_DEVELOPER);
            $weatherdata = self::fetch_weather_data($params['citycode'], $apikey);

            // Validate and process the response.
            $processeddata = self::process_weather_response($weatherdata);

            // Cache the result for configured time (default 30 minutes).
            $cachetime = get_config('block_blockdemo', 'weather_cache_time') ?: 30;
            $cache->set($cachekey, $processeddata, $cachetime * 60);

            debugging('Weather data processed and cached successfully', DEBUG_DEVELOPER);

            return $processeddata;

        } catch (\Exception $e) {
            // Log the error for debugging.
            debugging('Weather API error: ' . $e->getMessage(), DEBUG_DEVELOPER);

            // 返回错误信息而不是抛出异常，让前端处理
            return [
                'success' => false,
                'data' => null,
                'error' => [
                    'code' => $e->getCode(),
                    'message' => $e->getMessage(),
                    'type' => get_class($e)
                ],
                'warnings' => []
            ];
        }
    }

    /**
     * 确保返回数据格式正确
     * @param array $data 原始数据
     * @return array 格式化后的数据
     */
    private static function ensure_return_format($data)
    {
        // 确保所有必要字段存在
        if (!isset($data['success'])) {
            $data['success'] = true;
        }
        if (!isset($data['warnings'])) {
            $data['warnings'] = [];
        }
        if (!isset($data['data'])) {
            $data['data'] = null;
        }

        return $data;
    }

    /**
     * Validates city code format
     *
     * @param string $citycode The city code to validate
     * @return bool True if valid, false otherwise
     */
    private static function validate_city_code($citycode)
    {
        // Basic validation: should be 6 digits for Chinese city codes.
        return preg_match('/^\d{6}$/', $citycode);
    }

    /**
     * Fetch weather data from external API
     * @param string $citycode The city code
     * @param string $apikey The API key
     * @return array Raw API response
     * @throws moodle_exception
     */
    private static function fetch_weather_data($citycode, $apikey)
    {
        global $CFG;

        // Construct API URL.
        $url = 'https://restapi.amap.com/v3/weather/weatherInfo';
        $params = [
            'city' => $citycode,
            'key' => $apikey,
            'extensions' => 'base', // 获取实况天气
        ];
        $fullurl = $url . '?' . http_build_query($params);

        debugging('Calling weather API: ' . $fullurl, DEBUG_DEVELOPER);

        // Use Moodle's cURL wrapper for security and consistency.
        $curl = new \curl();
        $curl->setopt([
            'CURLOPT_TIMEOUT' => 15,           // 增加超时时间
            'CURLOPT_CONNECTTIMEOUT' => 10,    // 增加连接超时时间
            'CURLOPT_USERAGENT' => 'Moodle/' . $CFG->version,
            'CURLOPT_FOLLOWLOCATION' => true,  // 允许重定向
            'CURLOPT_SSL_VERIFYPEER' => true,  // 验证SSL
            'CURLOPT_SSL_VERIFYHOST' => 2,     // 验证主机名
        ]);

        // Make the API call.
        $response = $curl->get($fullurl);

        // Check for cURL errors.
        if ($curl->error) {
            debugging('cURL error: ' . $curl->error, DEBUG_DEVELOPER);
            throw new moodle_exception('curl_error', 'block_blockdemo', '', null, $curl->error);
        }

        // Check HTTP status.
        $info = $curl->get_info();
        $httpcode = $info['http_code'];

        debugging('API response HTTP code: ' . $httpcode, DEBUG_DEVELOPER);
        debugging('API response: ' . substr($response, 0, 500), DEBUG_DEVELOPER);

        if ($httpcode !== 200) {
            throw new moodle_exception(
                'http_error',
                'block_blockdemo',
                '',
                null,
                'HTTP ' . $httpcode
            );
        }

        // Decode JSON response.
        $data = json_decode($response, true);
        if (json_last_error() !== JSON_ERROR_NONE) {
            debugging('JSON decode error: ' . json_last_error_msg(), DEBUG_DEVELOPER);
            throw new moodle_exception(
                'json_decode_error',
                'block_blockdemo',
                '',
                null,
                json_last_error_msg()
            );
        }

        return $data;
    }

    /**
     * Process and validate the weather API response
     * @param array $data Raw API response
     * @return array Processed weather data
     * @throws moodle_exception
     */
    private static function process_weather_response($data)
    {
        debugging('Processing weather response: ' . json_encode($data), DEBUG_DEVELOPER);

        // Check API response status.
        if (!isset($data['status']) || $data['status'] !== '1') {
            $error = isset($data['info']) ? $data['info'] : 'Unknown API error';
            debugging('API response error: ' . $error, DEBUG_DEVELOPER);
            throw new moodle_exception('api_response_error', 'block_blockdemo', '', null, $error);
        }

        // Check if we have weather data.
        if (!isset($data['lives']) || !is_array($data['lives']) || empty($data['lives'])) {
            debugging('No weather data in API response', DEBUG_DEVELOPER);
            throw new moodle_exception('no_weather_data', 'block_blockdemo');
        }

        // Get the first (and usually only) weather record.
        $weather = $data['lives'][0];

        // Validate required fields.
        $requiredfields = ['province', 'city', 'weather', 'temperature', 'reporttime'];
        foreach ($requiredfields as $field) {
            if (!isset($weather[$field])) {
                debugging('Missing required field: ' . $field, DEBUG_DEVELOPER);
                throw new moodle_exception('missing_weather_field', 'block_blockdemo', '', $field);
            }
        }

        // Return structured data with safe values.
        $result = [
            'success' => true,
            'data' => [
                'province' => clean_text($weather['province']),
                'city' => clean_text($weather['city']),
                'adcode' => isset($weather['adcode']) ? clean_param($weather['adcode'], PARAM_ALPHANUMEXT) : '',
                'weather' => clean_text($weather['weather']),
                'temperature' => is_numeric($weather['temperature']) ? (int) $weather['temperature'] : null,
                'temperature_float' => isset($weather['temperature_float']) ?
                    clean_param($weather['temperature_float'], PARAM_FLOAT) : null,
                'winddirection' => isset($weather['winddirection']) ?
                    clean_text($weather['winddirection']) : '',
                'windpower' => isset($weather['windpower']) ?
                    clean_text($weather['windpower']) : '',
                'humidity' => isset($weather['humidity']) && is_numeric($weather['humidity']) ?
                    (int) $weather['humidity'] : null,
                'humidity_float' => isset($weather['humidity_float']) ?
                    clean_param($weather['humidity_float'], PARAM_FLOAT) : null,
                'reporttime' => clean_text($weather['reporttime']),
                'last_updated' => time(),
            ],
            'warnings' => [],
        ];

        debugging('Weather data processed successfully: ' . json_encode($result), DEBUG_DEVELOPER);
        return $result;
    }

    /**
     * Describes the return value for get_weather.
     *
     * @return external_single_structure
     */
    public static function execute_returns()
    {
        return new external_single_structure([
            'success' => new external_value(PARAM_BOOL, 'Whether the operation was successful'),
            'data' => new external_single_structure([
                'province' => new external_value(PARAM_TEXT, 'Province name', VALUE_OPTIONAL),
                'city' => new external_value(PARAM_TEXT, 'City name', VALUE_OPTIONAL),
                'adcode' => new external_value(PARAM_ALPHANUMEXT, 'Administrative division code', VALUE_OPTIONAL),
                'weather' => new external_value(PARAM_TEXT, 'Weather description', VALUE_OPTIONAL),
                'temperature' => new external_value(PARAM_INT, 'Temperature in Celsius', VALUE_OPTIONAL),
                'temperature_float' => new external_value(PARAM_FLOAT, 'Temperature as float', VALUE_OPTIONAL),
                'winddirection' => new external_value(PARAM_TEXT, 'Wind direction', VALUE_OPTIONAL),
                'windpower' => new external_value(PARAM_TEXT, 'Wind power', VALUE_OPTIONAL),
                'humidity' => new external_value(PARAM_INT, 'Humidity percentage', VALUE_OPTIONAL),
                'humidity_float' => new external_value(PARAM_FLOAT, 'Humidity as float', VALUE_OPTIONAL),
                'reporttime' => new external_value(PARAM_TEXT, 'Report time', VALUE_OPTIONAL),
                'last_updated' => new external_value(PARAM_INT, 'Last update timestamp', VALUE_OPTIONAL),
            ], 'Weather data', VALUE_OPTIONAL),
            'error' => new external_single_structure([
                'code' => new external_value(PARAM_INT, 'Error code', VALUE_OPTIONAL),
                'message' => new external_value(PARAM_TEXT, 'Error message', VALUE_OPTIONAL),
                'type' => new external_value(PARAM_TEXT, 'Error type', VALUE_OPTIONAL),
            ], 'Error information', VALUE_OPTIONAL),
            'warnings' => new external_warnings(),
        ]);
    }
}