"""
系统提示词配置管理页面
管理 config/yaml/system_prompt_config.yaml 中的提示词模板
提供新建、修改、删除功能
"""
from nicegui import ui
from typing import Optional, Dict, Any, List
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from config.yaml_config_manager import SystemPromptConfigFileManager
from component.chat.config import get_system_prompt_manager
from common.exception_handler import safe_protect


class PromptConfigManagementPage:
    """系统提示词配置管理页面类"""
    
    def __init__(self):
        self.file_manager = SystemPromptConfigFileManager()
        self.prompts_data = []
        self.categories = []
        
        # 预定义分类选项
        self.default_categories = [
            '文档编写',
            '代码助手',
            '数据分析',
            '业务助手',
            '知识问答',
            '创意写作',
            '翻译助手',
            '教育培训',
            '其他'
        ]
    
    def render(self):
        """渲染页面"""
        # 页面标题
        with ui.row().classes('w-full items-center justify-between mb-6'):
            with ui.column():
                ui.label('系统提示词配置管理').classes('text-3xl font-bold text-green-800 dark:text-green-200')
                ui.label('管理系统中的AI提示词模板').classes('text-sm text-gray-600 dark:text-gray-400')
            
            with ui.row().classes('gap-2'):
                ui.button('分类统计', icon='analytics', 
                         on_click=self.show_category_stats_dialog).props('flat')
                ui.button('刷新列表', icon='refresh', 
                         on_click=self.refresh_page).classes('bg-gray-500 text-white')
                ui.button('新增提示词', icon='add', 
                         on_click=self.show_add_dialog).classes('bg-green-500 text-white')
        
        # 提示词列表 - 使用卡片网格布局
        self.create_cards_grid()
    
    def create_cards_grid(self):
        """创建提示词卡片网格"""
        # 加载数据
        self.load_prompts_data()
        
        with ui.card().classes('w-full'):
            ui.label(f'提示词模板列表 (共 {len(self.prompts_data)} 个)').classes('text-lg font-semibold mb-4')
            
            if not self.prompts_data:
                with ui.column().classes('w-full items-center py-8'):
                    ui.icon('description').classes('text-6xl text-gray-400 mb-4')
                    ui.label('暂无提示词模板').classes('text-lg text-gray-500')
                    ui.label('点击上方"新增提示词"按钮添加第一个提示词模板').classes('text-sm text-gray-400')
            else:
                # 使用网格布局展示卡片
                with ui.grid(columns=3).classes('w-full gap-4'):
                    for prompt in self.prompts_data:
                        self.create_prompt_card(prompt)
    
    def create_prompt_card(self, prompt_data: Dict[str, Any]):
        """创建单个提示词卡片"""
        template_key = prompt_data['template_key']
        config = prompt_data['config']
        
        name = config.get('name', template_key)
        category = config.get('category', '未分类')
        description = config.get('description', '无描述')
        enabled = config.get('enabled', True)
        system_prompt = config.get('system_prompt', '')
        
        with ui.card().classes('w-full hover:shadow-lg transition-shadow'):
            # 卡片头部 - 名称和分类
            with ui.card_section():
                with ui.row().classes('w-full items-center justify-between'):
                    with ui.column().classes('flex-1'):
                        ui.label(name).classes('text-lg font-bold text-green-700 dark:text-green-300')
                        with ui.row().classes('gap-2 items-center mt-1'):
                            ui.badge(category, color='primary').props('outline')
                            ui.badge(template_key).classes('text-xs')
                    
                    # 状态徽章
                    if enabled:
                        ui.badge('启用', color='positive')
                    else:
                        ui.badge('禁用', color='negative')
            
            ui.separator()
            
            # 卡片内容 - 描述
            with ui.card_section():
                # 截断描述文本
                display_desc = description[:80] + '...' if len(description) > 80 else description
                ui.label(display_desc).classes('text-sm text-gray-600 dark:text-gray-400 min-h-12')
            
            ui.separator()
            
            # 卡片底部 - 提示词长度和操作按钮
            with ui.card_section():
                with ui.row().classes('w-full items-center justify-between'):
                    # 提示词字数统计
                    prompt_length = len(system_prompt)
                    ui.label(f'提示词: {prompt_length} 字符').classes('text-xs text-gray-500')
                    
                    # 操作按钮
                    with ui.row().classes('gap-1'):
                        ui.button(icon='visibility', on_click=lambda k=template_key: self.show_preview_dialog(k)).props('flat dense round size=sm color=primary').tooltip('预览')
                        ui.button(icon='edit', on_click=lambda k=template_key: self.show_edit_dialog(k)).props('flat dense round size=sm color=primary').tooltip('编辑')
                        ui.button(icon='delete', on_click=lambda k=template_key: self.show_delete_confirm(k)).props('flat dense round size=sm color=negative').tooltip('删除')
    
    def load_prompts_data(self):
        """加载提示词数据"""
        self.prompts_data = self.file_manager.get_all_prompts_list()
        self.categories = self.file_manager.get_categories_from_config()
    
    def refresh_page(self):
        """刷新页面"""
        ui.notify('正在刷新...', type='info', position='top')
        self.load_prompts_data()
        ui.notify('刷新成功!', type='positive', position='top')
        ui.navigate.reload()
    
    def show_category_stats_dialog(self):
        """显示分类统计对话框"""
        with ui.dialog() as dialog, ui.card().classes('w-full max-w-2xl'):
            ui.label('提示词分类统计').classes('text-xl font-bold mb-4')
            
            # 统计各分类的提示词数量
            category_stats = {}
            for prompt in self.prompts_data:
                category = prompt['config'].get('category', '未分类')
                category_stats[category] = category_stats.get(category, 0) + 1
            
            # 使用表格展示
            if category_stats:
                columns = [
                    {'name': 'category', 'label': '分类', 'field': 'category', 'align': 'left'},
                    {'name': 'count', 'label': '数量', 'field': 'count', 'align': 'center'},
                    {'name': 'percentage', 'label': '占比', 'field': 'percentage', 'align': 'center'},
                ]
                
                total = len(self.prompts_data)
                rows = []
                for category, count in sorted(category_stats.items(), key=lambda x: x[1], reverse=True):
                    percentage = f"{(count / total * 100):.1f}%"
                    rows.append({
                        'category': category,
                        'count': count,
                        'percentage': percentage
                    })
                
                ui.table(columns=columns, rows=rows).classes('w-full')
            else:
                ui.label('暂无数据').classes('text-gray-500')
            
            with ui.row().classes('w-full justify-end mt-4'):
                ui.button('关闭', on_click=dialog.close).props('flat')
        
        dialog.open()
    
    def show_add_dialog(self):
        """显示新增提示词对话框"""
        with ui.dialog() as dialog, ui.card().classes('w-full max-w-4xl'):
            ui.label('新增系统提示词').classes('text-xl font-bold mb-4')
            
            # 表单字段
            with ui.column().classes('w-full gap-4'):
                # 基本信息
                ui.label('基本信息').classes('text-lg font-semibold text-green-600')
                
                with ui.grid(columns=2).classes('w-full gap-4'):
                    template_key_input = ui.input(
                        label='模板标识 (key) *',
                        placeholder='例如: qa_expert'
                    ).classes('w-full')
                    
                    template_name_input = ui.input(
                        label='显示名称 *',
                        placeholder='例如: 问答专家'
                    ).classes('w-full')
                
                # 分类选择 - 支持自定义
                with ui.row().classes('w-full gap-2'):
                    # 合并预定义分类和已有分类
                    all_categories = sorted(list(set(self.default_categories + self.categories)))
                    
                    category_select = ui.select(
                        label='分类 *',
                        options=all_categories,
                        value=all_categories[0] if all_categories else None,
                        with_input=True  # 允许输入自定义分类
                    ).classes('flex-1')
                    
                    category_select.props('use-input input-debounce=0 new-value-mode=add-unique')
                
                description_input = ui.textarea(
                    label='描述 *',
                    placeholder='简要描述该提示词的用途和特点...'
                ).classes('w-full').props('rows=3')
                
                # 提示词内容
                ui.separator()
                ui.label('提示词内容').classes('text-lg font-semibold text-green-600')
                
                with ui.column().classes('w-full'):
                    ui.label('系统提示词 (支持 Markdown 格式) *').classes('text-sm font-semibold')
                    ui.label('提示: 可以使用 Markdown 语法编写结构化的提示词').classes('text-xs text-gray-500')
                    
                    system_prompt_input = ui.textarea(
                        placeholder='# 角色定位\n你是一个...\n\n## 核心能力\n1. ...\n2. ...'
                    ).classes('w-full font-mono').props('rows=12')
                    
                    # 字符计数
                    char_count_label = ui.label('0 字符').classes('text-xs text-gray-500 text-right')
                    
                    def update_char_count():
                        count = len(system_prompt_input.value or '')
                        char_count_label.text = f'{count} 字符'
                    
                    system_prompt_input.on('update:model-value', lambda: update_char_count())
                
                # 高级配置
                ui.separator()
                ui.label('高级配置').classes('text-lg font-semibold text-green-600')
                
                with ui.row().classes('w-full gap-4'):
                    version_input = ui.input(
                        label='版本号',
                        value='1.0',
                        placeholder='1.0'
                    ).classes('w-32')
                    
                    enabled_switch = ui.switch(
                        '启用此提示词',
                        value=True
                    ).classes('flex-1')
            
            # 按钮
            with ui.row().classes('w-full justify-end gap-2 mt-4'):
                ui.button('取消', on_click=dialog.close).props('flat')
                ui.button(
                    '保存',
                    icon='save',
                    on_click=lambda: self.save_new_prompt(
                        dialog,
                        template_key_input.value,
                        template_name_input.value,
                        category_select.value,
                        description_input.value,
                        system_prompt_input.value,
                        version_input.value,
                        enabled_switch.value
                    )
                ).classes('bg-green-500 text-white')
        
        dialog.open()
    
    def save_new_prompt(self, dialog, template_key, name, category, description,
                        system_prompt, version, enabled):
        """保存新提示词"""
        # 验证必填字段
        if not all([template_key, name, category, description, system_prompt]):
            ui.notify('请填写所有必填字段', type='negative')
            return
        
        # 构建配置对象
        config = {
            'name': name,
            'description': description,
            'enabled': enabled,
            'version': version,
            'category': category,
            'system_prompt': system_prompt,
            'examples': {}  # 保留 examples 字段,可后续扩展
        }
        
        # 保存到文件
        success = self.file_manager.add_prompt_config(template_key, config)
        
        if success:
            ui.notify(f'成功添加提示词模板: {name}', type='positive')
            
            # 重新加载配置管理器
            get_system_prompt_manager().reload_config()
            
            dialog.close()
            
            # 刷新页面
            ui.navigate.reload()
        else:
            ui.notify('保存失败,可能模板标识已存在', type='negative')
    
    def show_preview_dialog(self, template_key: str):
        """显示提示词预览对话框"""
        prompt_config = self.file_manager.get_prompt_config(template_key)
        if not prompt_config:
            ui.notify('提示词模板不存在', type='negative')
            return
        
        with ui.dialog() as dialog, ui.card().classes('w-full max-w-4xl'):
            # 标题
            name = prompt_config.get('name', template_key)
            ui.label(f'预览: {name}').classes('text-xl font-bold mb-4')
            
            # 基本信息
            with ui.grid(columns=2).classes('w-full gap-4 mb-4'):
                with ui.column():
                    ui.label('模板标识').classes('text-sm text-gray-600')
                    ui.label(template_key).classes('text-base font-semibold')
                
                with ui.column():
                    ui.label('分类').classes('text-sm text-gray-600')
                    category = prompt_config.get('category', '未分类')
                    ui.badge(category, color='primary')
            
            with ui.column().classes('w-full mb-4'):
                ui.label('描述').classes('text-sm text-gray-600')
                ui.label(prompt_config.get('description', '')).classes('text-base')
            
            ui.separator()
            
            # 提示词内容 - 使用 Markdown 渲染
            ui.label('提示词内容').classes('text-lg font-semibold mt-4 mb-2')
            
            system_prompt = prompt_config.get('system_prompt', '')
            
            with ui.card().classes('w-full bg-gray-50 dark:bg-gray-800'):
                with ui.scroll_area().classes('w-full h-96'):
                    ui.markdown(system_prompt).classes('p-4')
            
            # 底部信息
            with ui.row().classes('w-full justify-between mt-4'):
                prompt_length = len(system_prompt)
                ui.label(f'字符数: {prompt_length}').classes('text-sm text-gray-500')
                
                version = prompt_config.get('version', '1.0')
                ui.label(f'版本: {version}').classes('text-sm text-gray-500')
            
            with ui.row().classes('w-full justify-end gap-2 mt-4'):
                ui.button('关闭', on_click=dialog.close).props('flat')
                ui.button(
                    '编辑',
                    icon='edit',
                    on_click=lambda: (dialog.close(), self.show_edit_dialog(template_key))
                ).classes('bg-green-500 text-white')
        
        dialog.open()
    
    def show_edit_dialog(self, template_key: str):
        """显示编辑提示词对话框"""
        prompt_config = self.file_manager.get_prompt_config(template_key)
        if not prompt_config:
            ui.notify('提示词模板不存在', type='negative')
            return
        
        with ui.dialog() as dialog, ui.card().classes('w-full max-w-4xl'):
            ui.label(f'编辑提示词: {prompt_config.get("name", template_key)}').classes('text-xl font-bold mb-4')
            
            # 表单字段(预填充)
            with ui.column().classes('w-full gap-4'):
                # 基本信息
                ui.label('基本信息').classes('text-lg font-semibold text-green-600')
                
                with ui.grid(columns=2).classes('w-full gap-4'):
                    # 显示模板标识(不可编辑)
                    with ui.column().classes('w-full'):
                        ui.label('模板标识').classes('text-sm text-gray-600')
                        ui.label(template_key).classes('text-base font-semibold')
                    
                    template_name_input = ui.input(
                        label='显示名称 *',
                        value=prompt_config.get('name', '')
                    ).classes('w-full')
                
                # 分类选择
                with ui.row().classes('w-full gap-2'):
                    all_categories = sorted(list(set(self.default_categories + self.categories)))
                    current_category = prompt_config.get('category', '未分类')
                    
                    category_select = ui.select(
                        label='分类 *',
                        options=all_categories,
                        value=current_category,
                        with_input=True
                    ).classes('flex-1')
                    
                    category_select.props('use-input input-debounce=0 new-value-mode=add-unique')
                
                description_input = ui.textarea(
                    label='描述 *',
                    value=prompt_config.get('description', '')
                ).classes('w-full').props('rows=3')
                
                # 提示词内容
                ui.separator()
                ui.label('提示词内容').classes('text-lg font-semibold text-green-600')
                
                with ui.column().classes('w-full'):
                    ui.label('系统提示词 (支持 Markdown 格式) *').classes('text-sm font-semibold')
                    
                    system_prompt_input = ui.textarea(
                        value=prompt_config.get('system_prompt', '')
                    ).classes('w-full font-mono').props('rows=12')
                    
                    # 字符计数
                    initial_count = len(prompt_config.get('system_prompt', ''))
                    char_count_label = ui.label(f'{initial_count} 字符').classes('text-xs text-gray-500 text-right')
                    
                    def update_char_count():
                        count = len(system_prompt_input.value or '')
                        char_count_label.text = f'{count} 字符'
                    
                    system_prompt_input.on('update:model-value', lambda: update_char_count())
                
                # 高级配置
                ui.separator()
                ui.label('高级配置').classes('text-lg font-semibold text-green-600')
                
                with ui.row().classes('w-full gap-4'):
                    version_input = ui.input(
                        label='版本号',
                        value=prompt_config.get('version', '1.0')
                    ).classes('w-32')
                    
                    enabled_switch = ui.switch(
                        '启用此提示词',
                        value=prompt_config.get('enabled', True)
                    ).classes('flex-1')
            
            # 按钮
            with ui.row().classes('w-full justify-end gap-2 mt-4'):
                ui.button('取消', on_click=dialog.close).props('flat')
                ui.button(
                    '保存修改',
                    icon='save',
                    on_click=lambda: self.save_edit_prompt(
                        dialog,
                        template_key,
                        template_name_input.value,
                        category_select.value,
                        description_input.value,
                        system_prompt_input.value,
                        version_input.value,
                        enabled_switch.value
                    )
                ).classes('bg-green-500 text-white')
        
        dialog.open()
    
    def save_edit_prompt(self, dialog, template_key, name, category, description,
                        system_prompt, version, enabled):
        """保存编辑后的提示词"""
        # 验证必填字段
        if not all([name, category, description, system_prompt]):
            ui.notify('请填写所有必填字段', type='negative')
            return
        
        # 构建配置对象
        config = {
            'name': name,
            'description': description,
            'enabled': enabled,
            'version': version,
            'category': category,
            'system_prompt': system_prompt,
            'examples': {}
        }
        
        # 更新文件
        success = self.file_manager.update_prompt_config(template_key, config)
        
        if success:
            ui.notify(f'成功更新提示词模板: {name}', type='positive')
            
            # 重新加载配置管理器
            get_system_prompt_manager().reload_config()
            
            dialog.close()
            
            # 刷新页面
            ui.navigate.reload()
        else:
            ui.notify('更新失败', type='negative')
    
    def show_delete_confirm(self, template_key: str):
        """显示删除确认对话框"""
        prompt_config = self.file_manager.get_prompt_config(template_key)
        if not prompt_config:
            ui.notify('提示词模板不存在', type='negative')
            return
        
        name = prompt_config.get('name', template_key)
        
        with ui.dialog() as dialog, ui.card():
            with ui.column().classes('items-center gap-4 p-4'):
                ui.icon('warning', size='64px').classes('text-orange-500')
                ui.label('确认删除').classes('text-xl font-bold')
                ui.label(f'确定要删除提示词模板 "{name}" 吗?').classes('text-gray-600')
                ui.label('此操作不可恢复!').classes('text-sm text-red-500')
                
                with ui.row().classes('gap-2 mt-4'):
                    ui.button('取消', on_click=dialog.close).props('flat')
                    ui.button(
                        '确认删除',
                        icon='delete',
                        on_click=lambda: self.delete_prompt(dialog, template_key, name)
                    ).classes('bg-red-500 text-white')
        
        dialog.open()
    
    def delete_prompt(self, dialog, template_key: str, name: str):
        """删除提示词"""
        success = self.file_manager.delete_prompt_config(template_key)
        
        if success:
            ui.notify(f'成功删除提示词模板: {name}', type='positive')
            
            # 重新加载配置管理器
            get_system_prompt_manager().reload_config()
            
            dialog.close()
            
            # 刷新页面
            ui.navigate.reload()
        else:
            ui.notify('删除失败', type='negative')


@safe_protect(name="系统提示词配置管理", error_msg="系统提示词配置管理页面加载失败")
def prompt_config_management_page_content():
    """系统提示词配置管理页面入口函数"""
    page = PromptConfigManagementPage()
    page.render()