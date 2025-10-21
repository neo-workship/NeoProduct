"""
大模型配置管理页面 - 优化版
管理 config/yaml/llm_model_config.yaml 中的模型配置
提供新建、修改、删除功能

优化内容:
1. 添加 model_name 字段配置 (API实际使用的模型名称)
2. 在 "显示名称 (name)" 旁边添加 "模型名称 (model_name)" 输入框
3. 更新保存逻辑,包含 model_name 字段
"""
from nicegui import ui
from typing import Optional, Dict, Any
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from config.yaml_config_manager import LLMConfigFileManager
from config.provider_manager import get_provider_manager, ProviderInfo
from component.chat.config import get_llm_config_manager
from common.exception_handler import safe_protect

class LLMConfigManagementPage:
    """大模型配置管理页面类"""
    
    def __init__(self):
        self.file_manager = LLMConfigFileManager()
        self.provider_manager = get_provider_manager()
        self.table = None
        self.models_data = []
    
    def render(self):
        """渲染页面"""

        ui.add_head_html('''
            <style>
            .llm_edit_dialog-hide-scrollbar {
                overflow-y: auto;
                scrollbar-width: none;
                -ms-overflow-style: none;
            }
            .llm_edit_dialog-hide-scrollbar::-webkit-scrollbar {
                display: none;
            }
            </style>
        ''')
        
        # 页面标题
        with ui.row().classes('w-full items-center justify-between mb-6'):
            with ui.column():
                ui.label('大模型配置管理').classes('text-3xl font-bold text-blue-800 dark:text-blue-200')
                ui.label('管理系统中的大模型API配置').classes('text-sm text-gray-600 dark:text-gray-400')
            
            with ui.row().classes('gap-2'):
                ui.button('Provider 列表', icon='list', 
                         on_click=self.show_provider_list_dialog).props('flat')
                ui.button('刷新列表', icon='refresh', 
                         on_click=self.refresh_table).classes('bg-gray-500 text-white')
                ui.button('新增配置', icon='add', 
                         on_click=self.show_add_dialog).classes('bg-blue-500 text-white')
        
        # 配置列表表格
        self.create_table()
    
    def create_table(self):
        """创建配置列表表格"""
        # 加载数据
        self.load_models_data()
        
        # 表格列定义
        columns = [
            {
                'name': 'provider', 
                'label': '提供商', 
                'field': 'provider', 
                'align': 'left',
                'sortable': True
            },
            {
                'name': 'model_key', 
                'label': '配置唯一标识', 
                'field': 'model_key', 
                'align': 'left',
                'sortable': True
            },
            # {
            #     'name': 'name', 
            #     'label': '显示名称', 
            #     'field': 'name', 
            #     'align': 'left'
            # },
            {
                'name': 'model_name', 
                'label': '模型名称', 
                'field': 'model_name', 
                'align': 'left'
            },
            {
                'name': 'base_url', 
                'label': 'API地址', 
                'field': 'base_url', 
                'align': 'left'
            },
            {
                'name': 'enabled', 
                'label': '状态', 
                'field': 'enabled', 
                'align': 'center',
                'sortable': True
            },
            {
                'name': 'actions', 
                'label': '操作', 
                'field': 'actions', 
                'align': 'center'
            }
        ]
        
        # 创建表格
        self.table = ui.table(
            columns=columns,
            rows=self.models_data,
            row_key='model_key',
            pagination={'rowsPerPage': 10, 'sortBy': 'provider'}
        ).classes('w-full')
        
        # 添加操作按钮列的插槽
        self.table.add_slot('body-cell-enabled', '''
            <q-td key="enabled" :props="props">
                <q-badge :color="props.row.enabled ? 'green' : 'red'">
                    {{ props.row.enabled ? '已启用' : '已禁用' }}
                </q-badge>
            </q-td>
        ''')
        
        self.table.add_slot('body-cell-actions', '''
            <q-td key="actions" :props="props">
                <q-btn flat dense icon="edit" color="blue" 
                       @click="$parent.$emit('edit', props.row)" />
                <q-btn flat dense icon="delete" color="red" 
                       @click="$parent.$emit('delete', props.row)" />
            </q-td>
        ''')
        
        # 绑定操作事件
        self.table.on('edit', lambda e: self.show_edit_dialog(e.args))
        self.table.on('delete', lambda e: self.show_delete_confirm(e.args))
    
    def load_models_data(self):
        """从配置文件加载模型数据"""
        self.models_data = []
        
        providers_config = self.file_manager.get_provider_configs()
        
        for provider_key, models in providers_config.items():
            provider_display = self.provider_manager.get_provider_display_name(provider_key)
            
            for model_key, config in models.items():
                if isinstance(config, dict):
                    self.models_data.append({
                        'provider_key': provider_key,  # 原始 key
                        'provider': provider_display,   # 显示名称
                        'model_key': model_key,
                        'name': config.get('name', model_key),
                        'model_name': config.get('model_name', model_key),  # ✅ 添加 model_name
                        'base_url': config.get('base_url', ''),
                        'enabled': config.get('enabled', True),
                        '_raw_config': config  # 保存完整配置用于编辑
                    })
    
    def refresh_table(self):
        """刷新表格数据"""
        self.load_models_data()
        if self.table:
            self.table.update()
        ui.notify('配置列表已刷新', type='positive')
    
    def show_provider_list_dialog(self):
        """显示 Provider 列表对话框"""
        with ui.dialog() as dialog, ui.card().classes('w-full max-w-3xl'):
            ui.label('可用的模型提供商').classes('text-xl font-bold mb-4')
            
            providers = self.provider_manager.get_all_providers()
            
            # 使用卡片展示 Provider
            with ui.grid(columns=2).classes('w-full gap-4 llm_edit_dialog-hide-scrollbar'):
                for provider in providers:
                    with ui.card().classes('w-full'):
                        with ui.card_section():
                            with ui.row().classes('items-center gap-2'):
                                ui.icon(provider.icon).classes('text-2xl text-blue-500')
                                ui.label(provider.display_name).classes('text-lg font-bold')
                                ui.badge(provider.key).classes('ml-2')
                        
                        with ui.card_section():
                            ui.label(provider.description).classes('text-sm text-gray-600')
                        
                        with ui.card_section():
                            ui.label(f'默认地址: {provider.default_base_url}').classes('text-xs text-gray-500')
                        
                        with ui.card_actions().classes('justify-end'):
                            # 显示该 Provider 下的模型数量
                            models_count = len([
                                m for m in self.models_data 
                                if m['provider'] == provider.key
                            ])
                            ui.label(f'{models_count} 个模型').classes('text-sm text-gray-500')
            
            with ui.row().classes('w-full justify-end mt-4'):
                ui.button('关闭', on_click=dialog.close).props('flat')
        
        dialog.open()
    
    def show_add_dialog(self):
        """显示新增配置对话框"""
        # 获取所有 provider 选项
        provider_options = {
            p.key: p.display_name 
            for p in self.provider_manager.get_all_providers()
        }
        
        with ui.dialog() as dialog, ui.card().classes('w-full max-w-2xl'):
            ui.label('新增模型配置').classes('text-xl font-bold mb-4')
            
            # 表单字段
            with ui.column().classes('w-full gap-4 llm_edit_dialog-hide-scrollbar'):
                # 基本信息
                ui.label('基本信息').classes('text-lg font-semibold text-blue-600')
                with ui.grid(columns=2).classes('w-full gap-4'):
                    provider_select = ui.select(
                        options=provider_options,
                        label='选择 Provider *',
                        with_input=True
                    ).classes('w-full')
                    
                    model_key_input = ui.input(
                        label='配置唯一标识*',
                        placeholder='说明：可以是任意的唯一字符串'
                    ).classes('w-full')
                
                # ✅ 优化: 将 name 和 model_name 放在一起
                with ui.grid(columns=2).classes('w-full gap-4'):
                    model_name_input = ui.input(
                        label='显示名称 *',
                        placeholder='说明: 任何有意义名称，便于用户检索区分'
                    ).classes('w-full')
                    
                    # ✅ 新增: model_name 字段
                    model_name_api_input = ui.input(
                        label='模型名称 *',
                        placeholder='大模型名称，如：deepseek-chat'
                    ).classes('w-full')
                
                # API配置
                ui.separator()
                ui.label('API配置').classes('text-lg font-semibold text-blue-600')
                
                base_url_input = ui.input(
                    label='API地址 *',
                    placeholder='如：https://api.example.com/v1'
                ).classes('w-full')
                
                api_key_input = ui.input(
                    label='API Key *',
                    placeholder='sk-...',
                    password=True,
                    password_toggle_button=True
                ).classes('w-full')
                
                # 高级配置
                ui.separator()
                ui.label('高级配置').classes('text-lg font-semibold text-blue-600')
                
                with ui.grid(columns=3).classes('w-full gap-4'):
                    timeout_input = ui.number(
                        label='超时时间(秒)',
                        value=60,
                        min=10,
                        max=300
                    ).classes('w-full')
                    
                    max_retries_input = ui.number(
                        label='最大重试次数',
                        value=3,
                        min=0,
                        max=10
                    ).classes('w-full')
                    
                    stream_switch = ui.switch(
                        '支持流式输出',
                        value=True
                    ).classes('w-full')
                
                enabled_switch = ui.switch(
                    '启用此配置',
                    value=True
                ).classes('w-full')
                
                description_input = ui.textarea(
                    label='描述',
                    placeholder='简要描述该模型配置...'
                ).classes('w-full').props('rows=2')
            
            # 按钮
            with ui.row().classes('w-full justify-end gap-2 mt-4'):
                ui.button('取消', on_click=dialog.close).props('flat')
                ui.button(
                    '保存',
                    icon='save',
                    on_click=lambda: self.save_new_config(
                        dialog,
                        provider_select.value,
                        model_key_input.value,
                        model_name_input.value,
                        model_name_api_input.value,  # ✅ 新增参数
                        base_url_input.value,
                        api_key_input.value,
                        timeout_input.value,
                        max_retries_input.value,
                        stream_switch.value,
                        enabled_switch.value,
                        description_input.value
                    )
                ).classes('bg-blue-500 text-white')
        
        dialog.open()
    
    def save_new_config(self, dialog, provider, model_key, name, model_name_api,
                        base_url, api_key, timeout, max_retries, stream, enabled, description):
        """保存新配置"""
        # 验证必填字段
        if not all([provider, model_key, name, model_name_api, base_url, api_key]):
            ui.notify('请填写所有必填字段', type='negative')
            return
        
        # 构建配置对象
        config = {
            'name': name,
            'provider': provider,
            'model_name': model_name_api,  # ✅ 添加 model_name 字段
            'base_url': base_url,
            'api_key': api_key,
            'timeout': int(timeout),
            'max_retries': int(max_retries),
            'stream': stream,
            'enabled': enabled,
            'description': description,
        }
        
        # 保存到文件
        success = self.file_manager.add_model_config(provider, model_key, config)
        
        if success:
            ui.notify(f'成功添加模型配置: {name}', type='positive')
            
            # 重新加载配置管理器
            get_llm_config_manager().reload_config()
            
            dialog.close()
            
            # 刷新页面
            ui.navigate.reload()
        else:
            ui.notify('保存失败,可能配置已存在', type='negative')
    
    def show_edit_dialog(self, row_data):
        """显示编辑配置对话框"""
        provider = row_data['provider_key']  # 使用原始 key
        model_key = row_data['model_key']
        config = row_data['_raw_config']
        
        with ui.dialog() as dialog, ui.card().classes('w-full max-w-2xl'):
            ui.label(f'编辑配置: {row_data["name"]}').classes('text-xl font-bold mb-4')
            
            # 表单字段(预填充)
            with ui.column().classes('w-full gap-4 llm_edit_dialog-hide-scrollbar'):
                # 基本信息
                ui.label('基本信息').classes('text-lg font-semibold text-blue-600')
                
                with ui.grid(columns=2).classes('w-full gap-4'):
                    # 显示 Provider 和 model_key (不可编辑)
                    provider_display = self.provider_manager.get_provider_display_name(provider)
                    with ui.column().classes('w-full'):
                        ui.label('提供商').classes('text-sm text-gray-600')
                        ui.label(f'{provider_display} ({provider})').classes('text-base font-semibold')
                    
                    with ui.column().classes('w-full'):
                        ui.label('配置唯一标识').classes('text-sm text-gray-600')
                        ui.label(model_key).classes('text-base font-semibold')
                
                # ✅ 优化: 将 name 和 model_name 放在一起
                with ui.grid(columns=2).classes('w-full gap-4'):
                    model_name_input = ui.input(
                        label='显示名称 *',
                        value=config.get('name', '')
                    ).classes('w-full')
                    
                    # ✅ 新增: model_name 字段
                    model_name_api_input = ui.input(
                        label='模型名称 *',
                        value=config.get('model_name', model_key)  # 如果没有则使用 model_key
                    ).classes('w-full')
                
                # API配置
                ui.separator()
                ui.label('API配置').classes('text-lg font-semibold text-blue-600')
                
                base_url_input = ui.input(
                    label='API地址 *',
                    value=config.get('base_url', '')
                ).classes('w-full')
                
                api_key_input = ui.input(
                    label='API Key *',
                    value=config.get('api_key', ''),
                    password=True,
                    password_toggle_button=True
                ).classes('w-full')
                
                # 高级配置
                ui.separator()
                ui.label('高级配置').classes('text-lg font-semibold text-blue-600')
                
                with ui.grid(columns=3).classes('w-full gap-4'):
                    timeout_input = ui.number(
                        label='超时时间(秒)',
                        value=config.get('timeout', 60),
                        min=10,
                        max=300
                    ).classes('w-full')
                    
                    max_retries_input = ui.number(
                        label='最大重试次数',
                        value=config.get('max_retries', 3),
                        min=0,
                        max=10
                    ).classes('w-full')
                    
                    stream_switch = ui.switch(
                        '支持流式输出',
                        value=config.get('stream', True)
                    ).classes('w-full')
                
                enabled_switch = ui.switch(
                    '启用此配置',
                    value=config.get('enabled', True)
                ).classes('w-full')
                
                description_input = ui.textarea(
                    label='描述',
                    value=config.get('description', '')
                ).classes('w-full').props('rows=2')
            
            # 按钮
            with ui.row().classes('w-full justify-end gap-2 mt-4'):
                ui.button('取消', on_click=dialog.close).props('flat')
                ui.button(
                    '保存修改',
                    icon='save',
                    on_click=lambda: self.save_edit_config(
                        dialog,
                        provider,
                        model_key,
                        model_name_input.value,
                        model_name_api_input.value,  # ✅ 新增参数
                        base_url_input.value,
                        api_key_input.value,
                        timeout_input.value,
                        max_retries_input.value,
                        stream_switch.value,
                        enabled_switch.value,
                        description_input.value
                    )
                ).classes('bg-blue-500 text-white')
        
        dialog.open()
    
    def save_edit_config(self, dialog, provider, model_key, name, model_name_api,
                        base_url, api_key, timeout, max_retries, stream, enabled, description):
        """保存编辑后的配置"""
        # 验证必填字段
        if not all([name, model_name_api, base_url, api_key]):
            ui.notify('请填写所有必填字段', type='negative')
            return
        
        # 构建配置对象
        config = {
            'name': name,
            'provider': provider,
            'model_name': model_name_api,  # ✅ 添加 model_name 字段
            'base_url': base_url,
            'api_key': api_key,
            'timeout': int(timeout),
            'max_retries': int(max_retries),
            'stream': stream,
            'enabled': enabled,
            'description': description,
        }
        
        # 更新文件
        success = self.file_manager.update_model_config(provider, model_key, config)
        
        if success:
            ui.notify(f'成功更新模型配置: {name}', type='positive')
            
            # 重新加载配置管理器
            get_llm_config_manager().reload_config()
            
            dialog.close()
            
            # 刷新页面
            ui.navigate.reload()
        else:
            ui.notify('更新失败', type='negative')
    
    def show_delete_confirm(self, row_data):
        """显示删除确认对话框"""
        provider = row_data['provider_key']  # 使用原始 key
        model_key = row_data['model_key']
        name = row_data['name']
        
        with ui.dialog() as dialog, ui.card():
            with ui.column().classes('items-center gap-4 p-4'):
                ui.icon('warning', size='64px').classes('text-orange-500')
                ui.label('确认删除').classes('text-xl font-bold')
                ui.label(f'确定要删除模型配置 "{name}" 吗?').classes('text-gray-600')
                ui.label('此操作不可恢复!').classes('text-sm text-red-500')
                
                with ui.row().classes('gap-2 mt-4'):
                    ui.button('取消', on_click=dialog.close).props('flat')
                    ui.button(
                        '确认删除',
                        icon='delete',
                        on_click=lambda: self.delete_config(dialog, provider, model_key, name)
                    ).classes('bg-red-500 text-white')
        
        dialog.open()
    
    def delete_config(self, dialog, provider, model_key, name):
        """删除配置"""
        success = self.file_manager.delete_model_config(provider, model_key)
        
        if success:
            ui.notify(f'成功删除模型配置: {name}', type='positive')
            
            # 重新加载配置管理器
            get_llm_config_manager().reload_config()
            
            dialog.close()
            
            # 刷新页面
            ui.navigate.reload()
        else:
            ui.notify('删除失败', type='negative')


@safe_protect(name="大模型配置管理", error_msg="大模型配置管理页面加载失败")
def llm_config_management_page_content():
    """大模型配置管理页面入口函数"""
    page = LLMConfigManagementPage()
    page.render()