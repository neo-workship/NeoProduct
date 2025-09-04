<?php
/**
 * Form for editing block_neodemo instances
 *
 */
class block_neodemo_edit_form extends block_edit_form
{

    /**
     * Form fields specific to this type of block
     *
     * @param MoodleQuickForm $mform
     */
    protected function specific_definition($mform)
    {
        $mform->addElement('header', 'configheader', get_string('blocksettings', 'block'));

    }
}
