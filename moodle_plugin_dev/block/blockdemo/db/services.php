<?php

/**
 * External functions and service definitions for block_blockdemo
 */

defined('MOODLE_INTERNAL') || die();

/**
 * List of external functions
 */
$functions = [
    'block_blockdemo_get_weather' => [
        'classname' => 'block_blockdemo\external\get_weather',
        'methodname' => 'execute',
        'description' => 'Get weather information for a specific city',
        'type' => 'read',
        'ajax' => true,
        'capabilities' => 'block/blockdemo:view',
        'services' => [MOODLE_OFFICIAL_MOBILE_SERVICE],
    ],
];

/**
 * List of external services
 */
$services = [
    'Block Demo Weather Service' => [
        'functions' => ['block_blockdemo_get_weather'],
        'restrictedusers' => 0,
        'enabled' => 1,
        'shortname' => 'block_blockdemo_weather',
        'downloadfiles' => 0,
        'uploadfiles' => 0,
    ],
];