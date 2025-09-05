<?php
defined('MOODLE_INTERNAL') || die();

/**
 * Block configuration form
 * 
 * 这个类定义了block的配置表单
 * 当用户点击"配置"时会调用这个表单
 */
class block_blockdemo_edit_form extends block_edit_form
{

    /**
     * 定义配置表单的具体字段
     */
    protected function specific_definition($mform)
    {
        // 表单标题
        $mform->addElement('header', 'configheader', get_string('blocksettings', 'block'));

        // 自定义文本字段
        $mform->addElement(
            'textarea',
            'config_customtext',
            get_string('customtext', 'block_blockdemo'),
            ['rows' => 4, 'cols' => 50]
        );
        $mform->setType('config_customtext', PARAM_RAW);
        $mform->addHelpButton('config_customtext', 'customtext', 'block_blockdemo');

        // 显示选项
        $options = [
            'simple' => get_string('displaymode_simple', 'block_blockdemo'),
            'detailed' => get_string('displaymode_detailed', 'block_blockdemo')
        ];
        $mform->addElement(
            'select',
            'config_displaymode',
            get_string('displaymode', 'block_blockdemo'),
            $options
        );
        $mform->setDefault('config_displaymode', 'simple');
    }
}