"""
层级选择器组件 - 类似Vue组件，可复用
包含原有的4个select组件和所有相关逻辑
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
    
    def __init__(self):
        # 存储选中的值
        self.selected_values = {
            'l1': None,
            'l2': None, 
            'l3': None,
            'field': None
        }
        
        # UI元素引用
        self.selects = {}
        
        # 在内存中存储层级数据，避免修改app.storage.general
        self.hierarchy_data_cache = {'data': None, 'loading': False}
    
    def render(self):
        """渲染组件 - 对应Vue的template部分"""
        # 4级级联选择器
        with ui.grid(columns=4).classes('w-full gap-4').style('height: 120px;'):
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
            ).classes('w-full')

            def on_l1_change(event):
                self.selected_values['l1'] = event.value
                self.selected_values['l2'] = None
                self.selected_values['l3'] = None
                self.selected_values['field'] = None

                # 清空下级选择器
                if 'l2' in self.selects:
                    self.selects['l2'].set_value(None)
                if 'l3' in self.selects:
                    self.selects['l3'].set_value(None)
                if 'field' in self.selects:
                    self.selects['field'].set_value(None)

                # 更新二级选择器选项
                self._update_l2_options()

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
            ).classes('w-full')
            
            def on_l2_change(event):
                self.selected_values['l2'] = event.value
                self.selected_values['l3'] = None
                self.selected_values['field'] = None
                
                # 清空下级选择器
                if 'l3' in self.selects:
                    self.selects['l3'].set_value(None)
                if 'field' in self.selects:
                    self.selects['field'].set_value(None)
                
                # 更新三级选择器选项
                self._update_l3_options()
                
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
            ).classes('w-full')
            
            def on_l3_change(event):
                self.selected_values['l3'] = event.value
                self.selected_values['field'] = None
                
                # 清空下级选择器
                if 'field' in self.selects:
                    self.selects['field'].set_value(None)
                
                # 更新字段选择器选项
                self._update_field_options()
                
            l3_select.on_value_change(on_l3_change)
            self.selects['l3'] = l3_select
    
    def _create_field_select(self):
        """创建字段选择器"""
        with ui.column().classes('w-full h-10'):
            field_select = ui.select(
                options={},
                with_input=True,
                clearable=True,
                label='请先选择三级分类'
            ).classes('w-full')
            
            def on_field_change(event):
                self.selected_values['field'] = event.value
                
            field_select.on_value_change(on_field_change)
            self.selects['field'] = field_select
    
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
        """同步加载层级数据并更新UI"""
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
        """调用MongoDB服务的/api/v1/hierarchy接口获取4级层级数据"""
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
                            log_error("层级数据API返回失败", 
                                     extra_data=f'{{"response": "{str(data)}"}}')
                            return None
                    else:
                        log_error(f"获取层级数据失败，状态码: {response.status}")
                        return None
                        
        except Exception as e:
            log_error("获取层级数据异常", exception=e)
            return None
    
    async def _ensure_hierarchy_data_in_storage(self):
        """确保层级数据已存储在app.storage.general中，如果没有则获取并存储"""
        # 检查是否已经存储（兼容性检查）
        try:
            if hasattr(app.storage.general, 'hierarchy_data') and app.storage.general.hierarchy_data:
                log_info("层级数据已存在于browser storage中")
                return app.storage.general.hierarchy_data
        except:
            # 如果访问browser storage出错，继续使用API获取
            pass
        
        # 获取层级数据
        hierarchy_data = await self._fetch_hierarchy_data()
        
        if hierarchy_data:
            # 尝试存储到general storage，如果失败则只返回数据
            try:
                app.storage.general['hierarchy_data'] = hierarchy_data
                log_info("层级数据已成功存储到browser storage")
            except Exception as e:
                log_info(f"无法存储到browser storage，使用内存缓存: {str(e)}")
            
            return hierarchy_data
        else:
            log_error("无法获取层级数据")
            return {}
    
    def _get_hierarchy_data_from_storage(self) -> Dict[str, Any]:
        """从app.storage.general获取层级数据，如果获取失败则返回空字典"""
        try:
            return getattr(app.storage.general, 'hierarchy_data', {})
        except:
            # 如果访问browser storage出错，返回空字典
            return {}
    
    def _extract_level_options(self, hierarchy_data: Dict[str, Any], level: str, parent_code: str = None) -> List[Dict[str, str]]:
        """从层级数据中提取指定级别的选项列表"""
        options = []
        
        try:
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