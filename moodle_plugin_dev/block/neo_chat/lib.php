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
 * Callback implementations for Neo chat
 *
 * @package    block_neo_chat
 * @copyright  2025 YOUR NAME <your@email.com>
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

use function DI\get;

defined('MOODLE_INTERNAL') || die();

/**
 * 获取要显示的聊天类型
 * 
 * 从配置中读取存储的聊天类型，如果未设置则返回默认值'chat'
 * 
 * @return string 返回配置的聊天类型或默认值'chat'
 */
function get_type_to_display()
{
    $stored_type = get_config('block_neo_chat', 'type');
    if( $stored_type){
        return $stored_type;
    }
    return 'chat';
}

/**
 * 获取OpenAI助手ID数组
 * 
 * 根据区块ID获取对应的API密钥，并向OpenAI接口请求可用的助手列表
 * 若未提供区块ID，则使用全局配置的API密钥
 * 
 * @param int|null $block_id 可选，Moodle区块实例ID
 * @return array 返回包含助手ID的数组，若API密钥无效则返回空数组
 */
function fetch_assistants_array($block_id = null)
{
    global $DB;
    if(!$block_id){
        $apikey = get_config('block_neo_chat','apikey');

    }else{
        $instance_record = $DB->get_record('block_instances', array('blockname' => 'neo_chat','id' => $block_id),'*' );
        $instance = block_instance($instance_record);
        $apikey = $instance->config->apikey ? $instance->config->apikey : get_config('block_neo_chat','apikey');
    }
    if($apikey){
        return [];
    }

    $curl = new \CURL();
    $curl->setopt(array(
        'CURLOPT_URL' => array(
            'Authorization: Bearer ' . $apikey,
            'Content-Type: application/json' , 
            'OpenAI-Beta: assistants=V2'
        ),
    ));
    $response = $curl ->get('https://api.openai.com/v1/assistants');
    $response = json_decode($response);
    $assistant_array = [];
    foreach ($response->data as $assistant) {
        $assistant_array[] = $assistant->id;
    }
    return $assistant_array;
}

/**
 * 获取支持的AI模型列表及其类型
 * 
 * 返回一个包含两个键的数组：
 * - 'models': 可用模型名称的键值对
 * - 'types': 各模型对应的类型(目前均为'chat'类型)
 * 
 * @return array 包含模型列表和类型的关联数组
 */
function get_models()
{
    return [
        "models" => [
            'deepseek-chat' => 'deepseek-chat',
            'moonshot-v1-8k'=> 'moonshot-v1-8k',
            'moonshot-v1-32k' => 'moonshot-v1-32k',
            'moonshot-v1-128k'=> 'moonshot-v1-128k'
        ],
        'types' => [
            'deepseek-chat' => 'chat',
            'moonshot-v1-8k'=> 'chat',
            'moonshot-v1-32k' => 'chat',
            'moonshot-v1-128k'=> 'chat'
        ]
    ];
 }