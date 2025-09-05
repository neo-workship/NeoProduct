<?php
/**
 * Capability definitions for 演示区块
 *
 * Documentation: {@link https://moodledev.io/docs/apis/subsystems/access}
 *
 * @package    block_blockdemo
 * @category   access
 * @copyright  2025 YOUR NAME <your@email.com>
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

defined('MOODLE_INTERNAL') || die();

/**
 * 定义插件的权限能力
 * 
 * 这里定义了谁可以添加和管理这个block
 */
$capabilities = [
    // 在课程页面添加block的权限
    'block/blockdemo:addinstance' => [
        'riskbitmask' => RISK_SPAM | RISK_XSS,
        'captype' => 'write',
        'contextlevel' => CONTEXT_BLOCK,
        'archetypes' => [
            'editingteacher' => CAP_ALLOW,
            'manager' => CAP_ALLOW
        ],
        'clonepermissionsfrom' => 'moodle/site:manageblocks'
    ],

    // 在用户仪表板添加block的权限
    'block/blockdemo:myaddinstance' => [
        'captype' => 'write',
        'contextlevel' => CONTEXT_SYSTEM,
        'archetypes' => [
            'user' => CAP_ALLOW
        ]
    ]
];