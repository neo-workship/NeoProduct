"""
层级选择器组件 - 类似Vue组件，可复用
包含原有的4个select组件和所有相关逻辑
优化版本：添加了 data_url、full_path_code、full_path_name 的自动计算逻辑
多选版本：增加了multiple参数支持多选字段功能，完全保持原有逻辑不变
"""
from nicegui import app, ui
from common.exception_handler import log_info, log_error
import aiohttp
import asyncio
from typing import Dict, Any, List, Optional

# MongoDB服务API基础URL
MONGODB_SERVICE_URL = "http://localhost:8001"

class HierarchySelector:
    """层级选择器组件，类似Vue组件"""
    
    def __init__(self, multiple: bool = False):
        """
        初始化层级选择器
        
        Args:
            multiple: 是否启用多选模式（仅对field字段生效）
        # 多选模式
        selector = HierarchySelector(multiple=True)
        values = selector.get_selected_values()
        field_list = values['field']  # 返回列表 ['field1', 'field2']
        data_url = values['data_url']  # 使用第一个字段的data_url

        # 单选模式  
        selector = HierarchySelector(multiple=False)
        values = selector.get_selected_values()
        field_value = values['field']  # 返回单值 'field1'
        """
        self.multiple = multiple
        
        # 存储选中的值 - 优化版本，添加了新字段
        # 根据multiple参数决定field的数据类型
        self.selected_values = {
            'l1': None,
            'l2': None, 
            'l3': None,
            'field': [] if multiple else None,  # 多选时为列表，单选时为单值
            # 新添加的优化字段
            'data_url': None,        # 如果field不为None，对应的值为field的data_url
            'full_path_code': None,  # 完整路径编码
            'full_path_name': None   # 完整路径名称
        }
        
        # UI元素引用
        self.selects = {}
        
        # 在内存中存储层级数据，避免修改app.storage.general
        self.hierarchy_data_cache = {'data': None, 'loading': False}
    
    def render_row(self):
        """渲染组件 - 对应Vue的template部分"""
        # 4级级联选择器
        with ui.grid(columns=4).classes('w-full gap-4'):
            self._create_l1_select()
            self._create_l2_select()
            self._create_l3_select()
            self._create_field_select()
        self._load_hierarchy_data()

    def render_column(self):
        """渲染组件 - 对应Vue的template部分"""
        # 4级级联选择器
        with ui.grid(rows=4).classes('w-full gap-4'):
        # with ui.column().classes('w-full gap-2'):
            self._create_l1_select()
            self._create_l2_select()
            self._create_l3_select()
            self._create_field_select()       
        # 页面加载时初始化层级数据
        self._load_hierarchy_data()
    
    def _create_l1_select(self):
        """创建一级选择器"""
        with ui.column().classes('w-full h-10'):
            l1_select = ui.select(
                options={},  # 初始为空，将通过加载数据更新
                with_input=True,
                clearable=True,
                label='加载中...'
            ).classes('w-full').props('dense')

            def on_l1_change(event):
                self.selected_values['l1'] = event.value
                self.selected_values['l2'] = None
                self.selected_values['l3'] = None
                self.selected_values['field'] = [] if self.multiple else None

                # 清空下级选择器
                if 'l2' in self.selects:
                    self.selects['l2'].set_value(None)
                if 'l3' in self.selects:
                    self.selects['l3'].set_value(None)
                if 'field' in self.selects:
                    self.selects['field'].set_value([] if self.multiple else None)

                # 更新二级选择器选项
                self._update_l2_options()
                
                # 更新优化字段
                self._update_optimized_values()

            l1_select.on_value_change(on_l1_change)
            self.selects['l1'] = l1_select
    
    def _create_l2_select(self):
        """创建二级选择器"""
        with ui.column().classes('w-full h-10'):
            l2_select = ui.select(
                options={},
                with_input=True,
                clearable=True,
                label='请先选择一级分类'
            ).classes('w-full').props('dense')
            
            def on_l2_change(event):
                self.selected_values['l2'] = event.value
                self.selected_values['l3'] = None
                self.selected_values['field'] = [] if self.multiple else None
                
                # 清空下级选择器
                if 'l3' in self.selects:
                    self.selects['l3'].set_value(None)
                if 'field' in self.selects:
                    self.selects['field'].set_value([] if self.multiple else None)
                
                # 更新三级选择器选项
                self._update_l3_options()
                
                # 更新优化字段
                self._update_optimized_values()
                
            l2_select.on_value_change(on_l2_change)
            self.selects['l2'] = l2_select
    
    def _create_l3_select(self):
        """创建三级选择器"""
        with ui.column().classes('w-full h-10'):
            l3_select = ui.select(
                options={},
                with_input=True,
                clearable=True,
                label='请先选择二级分类'
            ).classes('w-full').props('dense')
            
            def on_l3_change(event):
                self.selected_values['l3'] = event.value
                self.selected_values['field'] = [] if self.multiple else None
                
                # 清空下级选择器
                if 'field' in self.selects:
                    self.selects['field'].set_value([] if self.multiple else None)
                
                # 更新字段选择器选项
                self._update_field_options()
                
                # 更新优化字段
                self._update_optimized_values()
                
            l3_select.on_value_change(on_l3_change)
            self.selects['l3'] = l3_select
    
    def _create_field_select(self):
        """创建字段选择器 - 根据multiple参数决定是否多选"""
        with ui.column().classes('w-full h-10'):
            if self.multiple:
                # 多选模式
                field_select = ui.select(
                    options={},
                    with_input=True,
                    clearable=True,
                    multiple=True,  # 启用多选
                    label='请先选择三级分类'
                ).classes('w-full').props('dense use-chips')  # 添加use-chips属性
            else:
                # 单选模式（原有逻辑）
                field_select = ui.select(
                    options={},
                    with_input=True,
                    clearable=True,
                    label='请先选择三级分类'
                ).classes('w-full').props('dense')
            
            def on_field_change(event):
                self.selected_values['field'] = event.value
                
                # 更新优化字段
                self._update_optimized_values()
                
            field_select.on_value_change(on_field_change)
            self.selects['field'] = field_select
    
    def _update_optimized_values(self):
        """
        更新优化字段：data_url、full_path_code、full_path_name
        优先级：field > l3 > l2 > l1
        """
        try:
            hierarchy_data = self.hierarchy_data_cache['data'] or self._get_hierarchy_data_from_storage()
            if not hierarchy_data:
                return
            
            # 重置优化字段
            self.selected_values['data_url'] = None
            self.selected_values['full_path_code'] = None
            self.selected_values['full_path_name'] = None
            
            # 获取当前选中的层级信息
            current_l1_code = self.selected_values['l1']
            current_l2_code = self.selected_values['l2']
            current_l3_code = self.selected_values['l3']
            current_field_code = self.selected_values['field']
            
            # 如果field不为空，优先使用field的信息
            if current_field_code:
                if self.multiple and isinstance(current_field_code, list) and current_field_code:
                    # 多选模式：使用列表中的第一个值
                    first_field_code = current_field_code[0]
                    field_info = self._find_field_info(hierarchy_data, first_field_code)
                    if field_info:
                        self.selected_values['data_url'] = field_info.get('data_url')
                        self.selected_values['full_path_code'] = field_info.get('full_path_code')
                        self.selected_values['full_path_name'] = field_info.get('full_path_name')
                        return
                elif not self.multiple and current_field_code:
                    # 单选模式：直接使用选中的值
                    field_info = self._find_field_info(hierarchy_data, current_field_code)
                    if field_info:
                        self.selected_values['data_url'] = field_info.get('data_url')
                        self.selected_values['full_path_code'] = field_info.get('full_path_code')
                        self.selected_values['full_path_name'] = field_info.get('full_path_name')
                        return
            
            # 如果field为空但l3不为空，使用l3的信息
            if current_l3_code:
                l3_info = self._find_l3_info(hierarchy_data, current_l3_code)
                if l3_info:
                    self.selected_values['full_path_code'] = l3_info.get('path_code')
                    self.selected_values['full_path_name'] = l3_info.get('path_name')
                    return
            
            # 如果l3为空但l2不为空，使用l2的信息
            if current_l2_code:
                l2_info = self._find_l2_info(hierarchy_data, current_l2_code)
                if l2_info:
                    self.selected_values['full_path_code'] = l2_info.get('path_code')
                    self.selected_values['full_path_name'] = l2_info.get('path_name')
                    return
            
            # 如果l2为空但l1不为空，使用l1的信息
            if current_l1_code:
                l1_info = self._find_l1_info(hierarchy_data, current_l1_code)
                if l1_info:
                    self.selected_values['full_path_code'] = l1_info.get('l1_code')
                    self.selected_values['full_path_name'] = l1_info.get('l1_name')
                    return
                    
        except Exception as e:
            log_error("更新优化字段失败", exception=e)
    
    def _find_field_info(self, hierarchy_data: Dict[str, Any], field_code: str) -> Optional[Dict[str, Any]]:
        """查找字段信息"""
        try:
            l1_categories = hierarchy_data.get('l1_categories', [])
            for l1 in l1_categories:
                for l2 in l1.get('l2_categories', []):
                    for l3 in l2.get('l3_categories', []):
                        for field in l3.get('fields', []):
                            if field.get('field_code') == field_code:
                                return field
            return None
        except Exception as e:
            log_error("查找字段信息失败", exception=e)
            return None
    
    def _find_l3_info(self, hierarchy_data: Dict[str, Any], l3_code: str) -> Optional[Dict[str, Any]]:
        """查找三级分类信息"""
        try:
            l1_categories = hierarchy_data.get('l1_categories', [])
            for l1 in l1_categories:
                for l2 in l1.get('l2_categories', []):
                    for l3 in l2.get('l3_categories', []):
                        if l3.get('l3_code') == l3_code:
                            return l3
            return None
        except Exception as e:
            log_error("查找三级分类信息失败", exception=e)
            return None
    
    def _find_l2_info(self, hierarchy_data: Dict[str, Any], l2_code: str) -> Optional[Dict[str, Any]]:
        """查找二级分类信息"""
        try:
            l1_categories = hierarchy_data.get('l1_categories', [])
            for l1 in l1_categories:
                for l2 in l1.get('l2_categories', []):
                    if l2.get('l2_code') == l2_code:
                        return l2
            return None
        except Exception as e:
            log_error("查找二级分类信息失败", exception=e)
            return None
    
    def _find_l1_info(self, hierarchy_data: Dict[str, Any], l1_code: str) -> Optional[Dict[str, Any]]:
        """查找一级分类信息"""
        try:
            l1_categories = hierarchy_data.get('l1_categories', [])
            for l1 in l1_categories:
                if l1.get('l1_code') == l1_code:
                    return l1
            return None
        except Exception as e:
            log_error("查找一级分类信息失败", exception=e)
            return None
    
    def _update_l2_options(self):
        """更新二级选择器选项"""
        if self.selected_values['l1'] and 'l2' in self.selects:
            hierarchy_data = self.hierarchy_data_cache['data'] or self._get_hierarchy_data_from_storage()
            l2_options = self._extract_level_options(hierarchy_data, 'l2', self.selected_values['l1'])
            options_dict = {opt['value']: opt['label'] for opt in l2_options}
            self.selects['l2'].set_options(options_dict)
            self.selects['l2'].set_label('请选择二级分类' if options_dict else '暂无二级分类')
    
    def _update_l3_options(self):
        """更新三级选择器选项"""
        if self.selected_values['l2'] and 'l3' in self.selects:
            hierarchy_data = self.hierarchy_data_cache['data'] or self._get_hierarchy_data_from_storage()
            l3_options = self._extract_level_options(hierarchy_data, 'l3', self.selected_values['l2'])
            options_dict = {opt['value']: opt['label'] for opt in l3_options}
            self.selects['l3'].set_options(options_dict)
            self.selects['l3'].set_label('请选择三级分类' if options_dict else '暂无三级分类')
    
    def _update_field_options(self):
        """更新字段选择器选项"""
        if self.selected_values['l3'] and 'field' in self.selects:
            hierarchy_data = self.hierarchy_data_cache['data'] or self._get_hierarchy_data_from_storage()
            field_options = self._extract_level_options(hierarchy_data, 'field', self.selected_values['l3'])
            options_dict = {opt['value']: opt['label'] for opt in field_options}
            self.selects['field'].set_options(options_dict)
            self.selects['field'].set_label('请选择数据字段' if options_dict else '暂无数据字段')
    
    def _load_hierarchy_data(self):
        """同步加载层级数据并更新UI - 保持原有逻辑不变"""
        async def do_load():
            if self.hierarchy_data_cache['loading']:
                return
            
            self.hierarchy_data_cache['loading'] = True
            try:
                # 获取层级数据
                hierarchy_data = await self._ensure_hierarchy_data_in_storage()
                self.hierarchy_data_cache['data'] = hierarchy_data
                
                # 更新一级选择器选项
                if hierarchy_data and 'l1' in self.selects:
                    l1_options = self._extract_level_options(hierarchy_data, 'l1')
                    options_dict = {opt['value']: opt['label'] for opt in l1_options}
                    self.selects['l1'].set_options(options_dict)
                    self.selects['l1'].set_label('请选择一级分类' if options_dict else '暂无分类数据')
                else:
                    self.selects['l1'].set_label('数据加载失败')
                    
            except Exception as e:
                log_error("加载层级数据失败", exception=e)
                self.selects['l1'].set_label('数据加载失败')
            finally:
                self.hierarchy_data_cache['loading'] = False
        
        asyncio.create_task(do_load())
    
    async def _fetch_hierarchy_data(self) -> Optional[Dict[str, Any]]:
        """调用MongoDB服务的/api/v1/hierarchy接口获取4级层级数据 - 保持原有API不变"""
        try:
            log_info("开始获取层级数据", extra_data='{"api": "/api/v1/hierarchy"}')
            
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{MONGODB_SERVICE_URL}/api/v1/hierarchy") as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # 检查响应格式
                        if isinstance(data, dict) and data.get('success', False):
                            hierarchy_data = data.get('data', {})
                            log_info("成功获取层级数据", 
                                    extra_data=f'{{"categories_count": {len(hierarchy_data.get("l1_categories", []))}}}')
                            return hierarchy_data
                        else:
                            log_error("层级数据响应格式错误", 
                                     extra_data=f'{{"response": {data}}}')
                            return None
                    else:
                        error_text = await response.text()
                        log_error("获取层级数据失败", 
                                 extra_data=f'{{"status": {response.status}, "response": "{error_text}"}}')
                        return None
                        
        except Exception as e:
            log_error("获取层级数据异常", exception=e)
            return None
    
    async def _ensure_hierarchy_data_in_storage(self) -> Optional[Dict[str, Any]]:
        """确保存储中有层级数据，如果没有则获取并存储 - 保持原有逻辑不变"""
        try:
            # 尝试从缓存中获取
            if self.hierarchy_data_cache['data']:
                return self.hierarchy_data_cache['data']
            
            # 尝试从app.storage.general中获取
            hierarchy_data = self._get_hierarchy_data_from_storage()
            if hierarchy_data:
                self.hierarchy_data_cache['data'] = hierarchy_data
                return hierarchy_data
            
            # 如果存储中没有，则通过API获取
            hierarchy_data = await self._fetch_hierarchy_data()
            if hierarchy_data:
                # 存储到app.storage.general
                app.storage.general['hierarchy_data'] = hierarchy_data
                app.storage.general['hierarchy_data_timestamp'] = asyncio.get_event_loop().time()
                
                # 更新缓存
                self.hierarchy_data_cache['data'] = hierarchy_data
                log_info("层级数据已缓存到storage")
                return hierarchy_data
            
            return None
            
        except Exception as e:
            log_error("确保层级数据存在失败", exception=e)
            return None
    
    def _get_hierarchy_data_from_storage(self) -> Optional[Dict[str, Any]]:
        """从app.storage.general中获取层级数据 - 保持原有逻辑不变"""
        try:
            hierarchy_data = app.storage.general.get('hierarchy_data')
            if hierarchy_data:
                # 检查数据是否过期（可选，这里设置为1小时过期）
                timestamp = app.storage.general.get('hierarchy_data_timestamp', 0)
                current_time = asyncio.get_event_loop().time()
                if current_time - timestamp < 3600:  # 1小时内的数据认为有效
                    return hierarchy_data
                else:
                    log_info("层级数据已过期，需要重新获取")
                    return None
            return None
        except Exception as e:
            log_error("从存储获取层级数据失败", exception=e)
            return None
    
    def _extract_level_options(self, hierarchy_data: Dict[str, Any], level: str, parent_code: str = "") -> List[Dict[str, str]]:
        """从层级数据中提取指定层级的选项 - 保持原有逻辑不变"""
        options = []
        try:
            if not hierarchy_data:
                return options
                
            l1_categories = hierarchy_data.get('l1_categories', [])
            
            if level == 'l1':
                # 第一级分类
                for l1 in l1_categories:
                    options.append({
                        'value': l1.get('l1_code', ''),
                        'label': l1.get('l1_name', '')
                    })
                    
            elif level == 'l2' and parent_code:
                # 第二级分类
                for l1 in l1_categories:
                    if l1.get('l1_code') == parent_code:
                        for l2 in l1.get('l2_categories', []):
                            options.append({
                                'value': l2.get('l2_code', ''),
                                'label': l2.get('l2_name', '')
                            })
                        break
                        
            elif level == 'l3' and parent_code:
                # 第三级分类
                for l1 in l1_categories:
                    for l2 in l1.get('l2_categories', []):
                        if l2.get('l2_code') == parent_code:
                            for l3 in l2.get('l3_categories', []):
                                options.append({
                                    'value': l3.get('l3_code', ''),
                                    'label': l3.get('l3_name', '')
                                })
                            break
                            
            elif level == 'field' and parent_code:
                # 第四级（字段）
                for l1 in l1_categories:
                    for l2 in l1.get('l2_categories', []):
                        for l3 in l2.get('l3_categories', []):
                            if l3.get('l3_code') == parent_code:
                                for field in l3.get('fields', []):
                                    options.append({
                                        'value': field.get('field_code', ''),
                                        'label': field.get('field_name', '')
                                    })
                                break                    
        except Exception as e:
            log_error(f"提取{level}级别选项失败", exception=e)
        return options
    
    def get_selected_values(self) -> Dict[str, Any]:
        """
        获取当前选中的所有值，包括优化字段 - 保持原有API不变
        
        Returns:
            Dict: 包含所有选中值的字典，包括新增的优化字段
        """
        return self.selected_values.copy()
    
    def reset_all_selections(self):
        """重置所有选择 - 针对多选做了适配"""
        # 重置选中值
        for key in self.selected_values:
            if key == 'field' and self.multiple:
                self.selected_values[key] = []
            else:
                self.selected_values[key] = None
        
        # 重置UI组件
        for key, select in self.selects.items():
            if key == 'field' and self.multiple:
                select.set_value([])
            else:
                select.set_value(None)
        
        # 更新选项
        if 'l2' in self.selects:
            self.selects['l2'].set_options({})
            self.selects['l2'].set_label('请先选择一级分类')
        if 'l3' in self.selects:
            self.selects['l3'].set_options({})
            self.selects['l3'].set_label('请先选择二级分类')
        if 'field' in self.selects:
            self.selects['field'].set_options({})
            self.selects['field'].set_label('请先选择三级分类')

    def get_is_multiple(self) -> bool:
        """获取当前是否为多选模式"""
        return self.multiple