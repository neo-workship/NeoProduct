<?php
/**
 * Renderer for block_blockdemo plugin.
 */

namespace block_blockdemo\output;
use plugin_renderer_base;

/**
 * Renderer class for block_blockdemo.
 * @package block_blockdemo\output
 */
class renderer extends plugin_renderer_base
{
    /**
     * Render block properties.
     * @param block_properties $blockproperties The block properties renderable
     * @return string HTML output
     */
    public function render_block_properties(block_properties $blockproperties)
    {
        $data = $blockproperties->export_for_template($this);
        return $this->render_from_template('block_blockdemo/block_properties', $data);
    }
}