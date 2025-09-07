<?php

/**
 * Block properties renderable class.
 */

namespace block_blockdemo\output;

use renderable;
use templatable;
use renderer_base;
use stdClass;

/**
 * Class block_properties
 * 用于展示块属性和基类变量的可渲染类
 * @package block_blockdemo\output
 */
class block_properties implements renderable, templatable
{

    /** @var object The block instance */
    private $block;

    /**
     * Constructor.
     * @param object $block The block instance
     */
    public function __construct($block)
    {
        $this->block = $block;
    }

    /**
     * Export this data so it can be used as the context for a mustache template.
     * @param renderer_base $output
     * @return stdClass
     */
    public function export_for_template(renderer_base $output)
    {
        $data = new stdClass();

        // 基本属性
        $data->section_title = get_string('block_properties_title', 'block_blockdemo');
        $data->basic_properties_title = get_string('basic_properties', 'block_blockdemo');

        // 准备表格数据
        $data->properties = [];

        // 基类属性
        $properties = [
            'title' => $this->block->title,
            'arialabel' => $this->block->arialabel,
            'content_type' => $this->block->content_type,
            'cron' => $this->block->cron,
        ];

        // 自定义属性
        if (isset($this->block->internal_state)) {
            $properties['internal_state->initialized'] = $this->block->internal_state->initialized ? 'true' : 'false';
            $properties['internal_state->init_time'] = date('Y-m-d H:i:s', $this->block->internal_state->init_time);
            $properties['internal_state->custom_property'] = $this->block->internal_state->custom_property ?? 'null';
        }

        // 转换属性为模板数据
        foreach ($properties as $name => $value) {
            $type = gettype($value);
            $displayvalue = $this->format_value($value);

            $data->properties[] = [
                'name' => $name,
                'value' => $displayvalue,
                'type' => $type
            ];
        }

        return $data;
    }

    /**
     * Format value for display.
     * @param mixed $value The value to format
     * @return string Formatted value
     */
    private function format_value($value)
    {
        if (is_bool($value)) {
            return $value ? 'true' : 'false';
        } else if (is_null($value)) {
            return 'null';
        } else if (is_string($value)) {
            return htmlspecialchars($value);
        } else {
            return (string) $value;
        }
    }
}