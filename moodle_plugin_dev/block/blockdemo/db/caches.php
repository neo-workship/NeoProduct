<?php
/**
 * Cache definitions for block_blockdemo
 */

defined('MOODLE_INTERNAL') || die();

/**
 * Cache definitions
 */
$definitions = [
    'weather' => [
        'mode' => cache_store::MODE_APPLICATION,
        'simplekeys' => true,
        'simpledata' => false,
        'staticacceleration' => true,
        'staticaccelerationsize' => 10,
        'ttl' => 1800, // 30 minutes
        'invalidationevents' => [
            'block_blockdemo_weather_updated',
        ],
    ],
];