<?php
/**
 * 此文件包含Moodle块的父类block_base
 *
 * @package    core_block
 * @license    http://www.gnu.org/copyleft/gpl.html GNU Public License
 */

/// 常量定义

/**
 * 列表类型的块。块内容应作为关联数组设置在content对象的items属性中 ($this->content->items)
 * 可选择在 $this->content->footer 中包含页脚文本
 */
define('BLOCK_TYPE_LIST', 1);

/**
 * 文本类型的块。块内容应作为标准HTML文本设置在content对象的text属性中 ($this->content->text)
 * 可选择在 $this->content->footer 中包含页脚文本
 */
define('BLOCK_TYPE_TEXT', 2);

/**
 * 树形类型的块。$this->content->items 是 tree_item 对象的列表，$this->content->footer 是字符串
 */
define('BLOCK_TYPE_TREE', 3);

/**
 * 描述Moodle块的类，所有Moodle块都派生自此类
 *
 * @author Jon Papaioannou
 * @package core_block
 */
class block_base
{

    /**
     * 用于存储/缓存翻译字符串的内部变量
     * @var string $str
     */
    var $str;

    /**
     * 要在块标题区域显示的块标题
     * @var string $title
     */
    var $title = NULL;

    /**
     * 当标题为空时在块标题区域显示的块名称
     * @var string arialabel
     */
    var $arialabel = NULL;

    /**
     * 此块创建的内容类型。当前支持的选项 - BLOCK_TYPE_LIST, BLOCK_TYPE_TEXT
     * @var int $content_type
     */
    var $content_type = BLOCK_TYPE_TEXT;

    /**
     * 包含要在块中显示信息的对象
     * @var stdClass|null $content
     */
    var $content = NULL;

    /**
     * 此块对象的初始化实例
     * @var stdClass $instance
     */
    var $instance = NULL;

    /**
     * 此块出现的页面
     * @var moodle_page
     */
    public $page = NULL;

    /**
     * 此块的上下文
     * @var context
     */
    public $context = NULL;

    /**
     * 包含此块当前实例的实例配置信息的对象
     * @var stdClass $config
     */
    var $config = NULL;

    /**
     * 定时任务运行频率，0表示不运行
     * @var int $cron
     */
    var $cron = NULL;

    /// 类方法

    /**
     * 伪构造函数，保持PHP5兼容性
     */
    function __construct()
    {
        $this->init();
    }

    /**
     * 可以被重写以在删除数据库表之前进行额外清理的函数
     * （每个块调用一次，而不是每个实例！）
     */
    function before_delete()
    {
    }

    /**
     * 返回块名称，如类名、数据库、块目录等中所示
     *
     * @return string
     */
    function name()
    {
        // 返回块名称，如类名、数据库、块目录等中所示
        $myname = strtolower(get_class($this));
        return substr($myname, strpos($myname, '_') + 1);
    }

    /**
     * 此函数的父类版本只返回NULL
     * 应由派生类实现以返回内容对象
     *
     * @return stdClass
     */
    function get_content()
    {
        // 应由派生类实现
        return NULL;
    }

    /**
     * 返回类的$title变量值
     * 
     * 故意不检查是否设置了标题
     * 这已在 {@link _self_test()} 中完成
     *
     * @return string $this->title
     */
    function get_title()
    {
        // 故意不检查是否设置了标题。这已在_self_test()中完成
        return $this->title;
    }

    /**
     * 返回类的$content_type变量值
     *
     * 故意不检查是否设置了content_type
     * 这已在 {@link _self_test()} 中完成
     *
     * @return int $this->content_type
     */
    function get_content_type()
    {
        // 故意不检查是否设置了content_type。这已在_self_test()中完成
        return $this->content_type;
    }

    /**
     * 根据此块是否有要显示的内容以及用户是否有查看块的权限，返回true或false
     *
     * @return bool
     */
    function is_empty()
    {
        if (!has_capability('moodle/block:view', $this->context)) {
            return true;
        }

        $this->get_content();
        return (empty($this->content->text) && empty($this->content->footer));
    }

    /**
     * 首先将$this->content的当前值设置为NULL
     * 然后调用块的 {@link get_content()} 函数重新设置其值
     *
     * @return stdClass
     */
    function refresh_content()
    {
        // 这里没有特殊处理，依赖于content()
        $this->content = NULL;
        return $this->get_content();
    }

    /**
     * 返回表示此块完整内容的block_contents对象
     *
     * 内部调用->get_content()，然后添加编辑控件等
     *
     * 您可能不应该重写此方法，而应该重写
     * {@link html_attributes()}、{@link formatted_contents()} 或 {@link get_content()}、
     * {@link hide_header()}、{@link (get_edit_controls)} 等
     *
     * @return block_contents|null 块的表示，用于渲染
     * @since Moodle 2.0.
     */
    public function get_content_for_output($output)
    {
        global $CFG;

        // 如果当前用户没有查看块的权限，我们可以提前退出
        if (!has_capability('moodle/block:view', $this->context)) {
            return null;
        }

        $bc = new block_contents($this->html_attributes());
        $bc->attributes['data-block'] = $this->name();
        $bc->blockinstanceid = $this->instance->id;
        $bc->blockpositionid = $this->instance->blockpositionid;

        if ($this->instance->visible) {
            $bc->content = $this->formatted_contents($output);
            if (!empty($this->content->footer)) {
                $bc->footer = $this->content->footer;
            }
        } else {
            $bc->add_class('invisibleblock');
        }

        if (!$this->hide_header()) {
            $bc->title = $this->title;
        }

        if (empty($bc->title)) {
            $bc->arialabel = new lang_string('pluginname', get_class($this));
            $this->arialabel = $bc->arialabel;
        }

        if ($this->page->user_is_editing() && $this->instance_can_be_edited()) {
            $bc->controls = $this->page->blocks->edit_controls($this);
        } else {
            // 我们不能在隐藏块上使用is_empty
            if ($this->is_empty() && !$bc->controls) {
                return null;
            }
        }

        if (
            empty($CFG->allowuserblockhiding)
            || (empty($bc->content) && empty($bc->footer))
            || !$this->instance_can_be_collapsed()
        ) {
            $bc->collapsible = block_contents::NOT_HIDEABLE;
        } else if (get_user_preferences('block' . $bc->blockinstanceid . 'hidden', false)) {
            $bc->collapsible = block_contents::HIDDEN;
        } else {
            $bc->collapsible = block_contents::VISIBLE;
        }

        if ($this->instance_can_be_docked() && !$this->hide_header()) {
            $bc->dockable = true;
        }

        $bc->annotation = ''; // TODO MDL-19398 需要确定这里说什么

        return $bc;
    }

    /**
     * 返回包含外部函数返回的所有块内容的对象
     *
     * 如果您的块返回格式化内容或提供文件下载，您应该重写此方法以使用
     * \core_external\util::format_text、\core_external\util::format_string 函数进行格式化
     * 或使用 external_util::get_area_files 处理文件
     *
     * @param  core_renderer $output 用于输出的渲染器
     * @return stdClass      包含块标题、中心内容、页脚和链接文件（如果有）的对象
     * @since  Moodle 3.6
     */
    public function get_content_for_external($output)
    {
        $bc = new stdClass;
        $bc->title = null;
        $bc->content = null;
        $bc->contentformat = FORMAT_HTML;
        $bc->footer = null;
        $bc->files = [];

        if ($this->instance->visible) {
            $bc->content = $this->formatted_contents($output);
            if (!empty($this->content->footer)) {
                $bc->footer = $this->content->footer;
            }
        }

        if (!$this->hide_header()) {
            $bc->title = $this->title;
        }

        return $bc;
    }

    /**
     * 返回外部函数的插件配置设置
     *
     * 在某些情况下，配置需要格式化或仅在当前用户启用某些功能时返回
     *
     * @return stdClass 块实例和插件的配置（作为包含name -> value的对象）
     * @since Moodle 3.8
     */
    public function get_config_for_external()
    {
        return (object) [
            'instance' => new stdClass(),
            'plugin' => new stdClass(),
        ];
    }

    /**
     * 将块的内容转换为HTML
     *
     * 这被block_list等块基类使用，将结构化的
     * $this->content->list 和 $this->content->icons 数组转换为HTML
     * 因此，在大多数块中，您可能希望重写 {@link get_contents()} 方法，
     * 该方法生成内容的结构化表示
     *
     * @param $output 生成输出时使用的core_renderer
     * @return string 应该出现在块主体中的HTML
     * @since Moodle 2.0.
     */
    protected function formatted_contents($output)
    {
        $this->get_content();
        $this->get_required_javascript();
        if (!empty($this->content->text)) {
            return $this->content->text;
        } else {
            return '';
        }
    }

    /**
     * 测试此块是否已正确实现
     * 另外，$errors目前没有使用
     *
     * @return boolean
     */
    function _self_test()
    {
        // 测试此块是否已正确实现
        // 另外，$errors目前没有使用
        $errors = array();

        $correct = true;
        if ($this->get_title() === NULL) {
            $errors[] = 'title_not_set';
            $correct = false;
        }
        if (!in_array($this->get_content_type(), array(BLOCK_TYPE_LIST, BLOCK_TYPE_TEXT, BLOCK_TYPE_TREE))) {
            $errors[] = 'invalid_content_type';
            $correct = false;
        }
        // 当从块中使用角色和权限时，以下自测试不起作用
/*        if ($this->get_content() === NULL) {
            $errors[] = 'content_not_set';
            $correct = false;
        }*/
        $formats = $this->applicable_formats();
        if (empty($formats) || array_sum($formats) === 0) {
            $errors[] = 'no_formats';
            $correct = false;
        }

        return $correct;
    }

    /**
     * 子类应该重写此方法并在子类块有settings.php文件时返回true
     *
     * @return boolean
     */
    function has_config()
    {
        return false;
    }

    /**
     * 此块可能出现在哪些页面类型上
     *
     * 这里返回的信息由 {@link blocks_name_allowed_in_format()} 函数处理
     * 如果您需要确切了解其工作原理，请查看该函数
     *
     * 默认情况：除mod和tag外的所有页面
     *
     * @return array page-type prefix => true/false.
     */
    function applicable_formats()
    {
        // 默认情况：块可以在课程和站点索引中使用，但不能在活动中使用
        return array('all' => true, 'mod' => false, 'tag' => false);
    }

    /**
     * 默认返回false - 将显示标题
     * @return boolean
     */
    function hide_header()
    {
        return false;
    }

    /**
     * 返回您希望添加到块外部<div>的任何HTML属性
     *
     * 由于某些JS事件的连接方式，确保这里的默认值仍然被设置是个好主意
     * 我发现最简单的方法是在您的块中以以下方式重写它
     *
     * <code php>
     * function html_attributes() {
     *    $attributes = parent::html_attributes();
     *    $attributes['class'] .= ' mynewclass';
     *    return $attributes;
     * }
     * </code>
     *
     * @return array 属性名 => 值
     */
    function html_attributes()
    {
        $attributes = array(
            'id' => 'inst' . $this->instance->id,
            'class' => 'block_' . $this->name() . ' block',
        );
        $ariarole = $this->get_aria_role();
        if ($ariarole) {
            $attributes['role'] = $ariarole;
        }
        if ($this->hide_header()) {
            $attributes['class'] .= ' no-header';
        }
        if ($this->instance_can_be_docked() && get_user_preferences('docked_block_instance_' . $this->instance->id, 0)) {
            $attributes['class'] .= ' dock_on_load';
        }
        return $attributes;
    }

    /**
     * 根据block_instances表的数据和当前页面设置此类的特定实例
     * （参见 {@link block_manager::load_blocks()}）
     *
     * @param stdClass $instance 来自block_instances、block_positions等的数据
     * @param moodle_page $page 此块所在的页面
     */
    function _load_instance($instance, $page)
    {
        if (!empty($instance->configdata)) {
            $this->config = unserialize_object(base64_decode($instance->configdata));
        }
        $this->instance = $instance;
        $this->context = context_block::instance($instance->id);
        $this->page = $page;
        $this->specialization();
    }

    /**
     * 允许块将其需要的任何JS加载到页面中
     *
     * 默认情况下，此函数只是允许用户停靠块（如果它是可停靠的）
     *
     * 根据MDL-64506保留为null
     */
    function get_required_javascript()
    {
    }

    /**
     * 在加载实例后立即在您的子类上调用此函数
     * 使用此函数在加载实例数据后且在执行任何其他操作之前对实例数据进行操作
     * 例如：如果您的块将根据位置（站点、课程、博客等）有不同的标题
     */
    function specialization()
    {
        // 只是为了确保此方法存在
    }

    /**
     * 此类型的每个块是否将有特定于实例的配置？
     * 通常，此设置由 {@link instance_allow_multiple()} 控制：如果允许多个实例，
     * 那么每个都肯定需要自己的配置。但在某些情况下，可能需要为不希望
     * 允许多个实例的块提供实例配置。在这种情况下，让此函数返回true。
     * 我再次强调，这只有在 {@link instance_allow_multiple()} 返回false时才有区别。
     * @return boolean
     */
    function instance_allow_config()
    {
        return false;
    }

    /**
     * 您是否要允许每个块的多个实例？
     * 如果是，则假定块将使用每个实例的配置
     * @return boolean
     */
    function instance_allow_multiple()
    {
        // 您是否要允许每个块的多个实例？
        // 如果是，则假定块将使用每个实例的配置
        return false;
    }

    /**
     * 序列化并存储配置数据
     */
    function instance_config_save($data, $nolongerused = false)
    {
        global $DB;
        $DB->update_record('block_instances', [
            'id' => $this->instance->id,
            'configdata' => base64_encode(serialize($data)),
            'timemodified' => time()
        ]);
    }

    /**
     * 用$this->config中当前的配置数据替换实例的配置数据
     */
    function instance_config_commit($nolongerused = false)
    {
        global $DB;
        $this->instance_config_save($this->config);
    }

    /**
     * 在创建新块实例时执行您可能需要的任何额外初始化
     * @return boolean
     */
    function instance_create()
    {
        return true;
    }

    /**
     * 复制到新块实例时复制任何特定于块的数据
     * @param int $fromid 要复制的块实例的id号
     * @return boolean
     */
    public function instance_copy($fromid)
    {
        return true;
    }

    /**
     * 如果您使用了configdata字段以外的持久存储，删除与此实例相关的所有内容
     * @return boolean
     */
    function instance_delete()
    {
        return true;
    }

    /**
     * 允许块类对用户编辑（即配置）此类型块的能力有发言权
     * 框架首先决定是否允许这样做（例如，除非处于编辑模式，否则不允许编辑）
     * 但如果框架允许，块仍然可以决定拒绝
     * @return boolean
     */
    function user_can_edit()
    {
        global $USER;

        if (has_capability('moodle/block:edit', $this->context)) {
            return true;
        }

        // My Moodle中的块是特殊情况。我们希望它们从用户上下文继承
        if (
            !empty($USER->id)
            && $this->instance->parentcontextid == $this->page->context->id   // 块属于此页面
            && $this->page->context->contextlevel == CONTEXT_USER             // 页面属于用户
            && $this->page->context->instanceid == $USER->id
        ) {               // 页面属于此用户
            return has_capability('moodle/my:manageblocks', $this->page->context);
        }

        return false;
    }

    /**
     * 允许块类对用户创建此块新实例的能力有发言权
     * 框架首先决定是否允许这样做（例如，除非处于编辑模式，否则不允许添加）
     * 但如果框架允许，块仍然可以决定拒绝
     * 此函数可以访问完整的页面对象，正在确定与之相关的创建
     *
     * @param moodle_page $page
     * @return boolean
     */
    function user_can_addto($page)
    {
        global $CFG;
        require_once($CFG->dirroot . '/user/lib.php');

        // 此块支持的格式列表
        $formats = $this->applicable_formats();

        // 检查用户是否试图将块添加到其个人资料页面
        $userpagetypes = user_page_type_list($page->pagetype, null, null);
        if (array_key_exists($page->pagetype, $userpagetypes)) {
            $capability = 'block/' . $this->name() . ':addinstance';
            return $this->has_add_block_capability($page, $capability)
                && has_capability('moodle/user:manageownblocks', $page->context);
        }

        // My Moodle中的块是特殊情况，使用不同的权限
        $mypagetypes = my_page_type_list($page->pagetype); // 获取可能的my页面类型列表

        if (array_key_exists($page->pagetype, $mypagetypes)) { // 确保我们在my页面类型的页面上
            // 如果块无法在/my上显示，如果未定义myaddinstance能力也没关系
            // 'my'是否被明确禁止？
            // 如果'all'未被允许，'my'是否被明确允许？
            if (
                (isset($formats['my']) && $formats['my'] == false)
                || (empty($formats['all']) && empty($formats['my']))
            ) {

                // 无论权限如何，块都不能添加到/my
                return false;
            } else {
                $capability = 'block/' . $this->name() . ':myaddinstance';
                return $this->has_add_block_capability($page, $capability)
                    && has_capability('moodle/my:manageblocks', $page->context);
            }
        }
        // 检查这是否是仅用于/my的块
        unset($formats['my']);
        if (empty($formats)) {
            // 块只能添加到/my - 返回false
            return false;
        }

        $capability = 'block/' . $this->name() . ':addinstance';
        if (
            $this->has_add_block_capability($page, $capability)
            && has_capability('moodle/block:edit', $page->context)
        ) {
            return true;
        }

        return false;
    }

    /**
     * 如果用户可以向页面添加块，则返回true
     *
     * @param moodle_page $page
     * @param string $capability 要检查的权限
     * @return boolean 如果用户可以添加块则返回true，否则返回false
     */
    private function has_add_block_capability($page, $capability)
    {
        // 检查权限是否存在
        if (!get_capability_info($capability)) {
            // 调试警告：权限不存在，但每页不超过一次
            static $warned = array();
            if (!isset($warned[$this->name()])) {
                debugging('The block ' . $this->name() . ' does not define the standard capability ' .
                    $capability, DEBUG_DEVELOPER);
                $warned[$this->name()] = 1;
            }
            // 如果权限不存在，总是可以添加块
            return true;
        } else {
            return has_capability($capability, $page->context);
        }
    }

    static function get_extra_capabilities()
    {
        return array('moodle/block:view', 'moodle/block:edit');
    }

    /**
     * 可以被块重写以防止块被停靠
     *
     * @return bool
     *
     * 根据MDL-64506返回false
     */
    public function instance_can_be_docked()
    {
        return false;
    }

    /**
     * 如果被块重写并设置为false，则在开启编辑时不可隐藏
     *
     * @return bool
     */
    public function instance_can_be_hidden()
    {
        return true;
    }

    /**
     * 如果被块重写并设置为false，则不可折叠
     *
     * @return bool
     */
    public function instance_can_be_collapsed()
    {
        return true;
    }

    /**
     * 如果被块重写并设置为false，则不可编辑
     *
     * @return bool
     */
    public function instance_can_be_edited()
    {
        return true;
    }

    /** @callback 评论API的回调函数 */
    public static function comment_template($options)
    {
        $ret = <<<EOD
<div class="comment-userpicture">___picture___</div>
<div class="comment-content">
    ___name___ - <span>___time___</span>
    <div>___content___</div>
</div>
EOD;
        return $ret;
    }
    public static function comment_permissions($options)
    {
        return array('view' => true, 'post' => true);
    }
    public static function comment_url($options)
    {
        return null;
    }
    public static function comment_display($comments, $options)
    {
        return $comments;
    }
    public static function comment_add(&$comments, $options)
    {
        return true;
    }

    /**
     * 返回最能描述此块的aria role属性
     *
     * Region是默认值，但如果有region子元素，甚至更好的是landmark子元素，则应该被块重写
     *
     * 选项如下：
     *    - application
     *    - landmark
     *      - form
     *      - navigation
     *      - search
     *
     * 请不要使用顶级landmark角色，如'banner'、'complementary'、'contentinfo'或'main'
     * 更多信息请阅读 {@link https://www.w3.org/WAI/ARIA/apg/practices/landmark-regions/ ARIA编写实践指南 - 地标区域}
     *
     * @return string
     */
    public function get_aria_role()
    {
        return 'region';
    }

    /**
     * 此方法可以被重写以添加一些额外检查来决定是否可以将块添加到页面
     * 它不需要执行标准权限检查，因为这些将由has_add_block_capability()执行
     * 此方法与用户无关。如果您想检查用户是否可以添加块，应该使用user_can_addto()
     *
     * @param moodle_page $page 将添加此块的页面
     * @return bool 是否可以将块添加到给定页面
     */
    public function can_block_be_added(moodle_page $page): bool
    {
        return true;
    }
}

/**
 * 用于显示带有图标/文本标签列表的块的专门类
 *
 * get_content方法应设置$this->content->items和（可选）
 * $this->content->icons，而不是$this->content->text
 *
 * @author Jon Papaioannou
 * @package core_block
 */
class block_list extends block_base
{
    var $content_type = BLOCK_TYPE_LIST;

    function is_empty()
    {
        if (!has_capability('moodle/block:view', $this->context)) {
            return true;
        }

        $this->get_content();
        return (empty($this->content->items) && empty($this->content->footer));
    }

    protected function formatted_contents($output)
    {
        $this->get_content();
        $this->get_required_javascript();
        if (!empty($this->content->items)) {
            return $output->list_block_contents($this->content->icons, $this->content->items);
        } else {
            return '';
        }
    }

    function html_attributes()
    {
        $attributes = parent::html_attributes();
        $attributes['class'] .= ' list_block';
        return $attributes;
    }
}

/**
 * 用于显示树形菜单的专门类
 *
 * {@link get_content()} 方法涉及使用 {@link tree_item} 对象数组
 * 设置 <code>$this->content->items</code> 的内容（这些是顶级节点）
 * {@link tree_item::children} 属性可能包含更多tree_item对象，等等
 * tree_item类本身是抽象的，不打算使用，请使用其子类之一
 *
 * 与 {@link block_list} 不同，图标指定为项目的一部分，不在单独的数组中
 *
 * @author Alan Trick
 * @package core_block
 * @internal 此类扩展block_list，因此我们免费获得is_empty()
 */
class block_tree extends block_list
{

    /**
     * @var int 指定应将内容添加到此块类型的方式
     * 在这种情况下，使用 <code>$this->content->items</code> 与 {@link tree_item} 对象
     */
    public $content_type = BLOCK_TYPE_TREE;

    /**
     * 生成格式化的HTML输出
     *
     * 还将所需的JavaScript调用添加到页面输出
     *
     * @param core_renderer $output
     * @return string HTML
     */
    protected function formatted_contents($output)
    {
        // 基于admin_tree中的代码
        global $PAGE; // TODO 当块有适当的方式将内容放入head时更改此代码
        static $eventattached;
        if ($eventattached === null) {
            $eventattached = true;
        }
        if (!$this->content) {
            $this->content = new stdClass;
            $this->content->items = array();
        }
        $this->get_required_javascript();
        $this->get_content();
        $content = $output->tree_block_contents($this->content->items, array('class' => 'block_tree list'));
        return $content;
    }
}