"""
一级分类选择器组件 - 专门用于只显示L1层级的选择器
# 在你的页面中使用
from .l1_selector_component import L1Selector, create_l1_selector

# 方式1：直接创建
selector = L1Selector(multiple=True)
selector.render()

# 方式2：便捷函数创建
selector = create_l1_selector(multiple=True, with_label="请选择企业分类")

# 获取选中值
values = selector.get_selected_values()
selected_codes = selector.get_selected_l1_codes()  # ['code1', 'code2']
selected_names = selector.get_selected_l1_names()  # ['名称1', '名称2']
"""
from nicegui import app, ui
from common.exception_handler import log_info, log_error
import aiohttp
import asyncio
from typing import Dict, Any, List, Optional

# MongoDB服务API基础URL
MONGODB_SERVICE_URL = "http://localhost:8001"

class L1Selector:
    """一级分类选择器组件"""
    
    def __init__(self, multiple: bool = True):
        """
        初始化一级分类选择器
        
        Args:
            multiple: 是否启用多选模式，默认为True
            
        使用示例:
        # 多选模式（默认）
        selector = L1Selector(multiple=True)
        values = selector.get_selected_values()
        l1_list = values['l1']  # 返回列表 ['l1_code1', 'l1_code2']
        
        # 单选模式
        selector = L1Selector(multiple=False)
        values = selector.get_selected_values()
        l1_value = values['l1']  # 返回单值 'l1_code1'
        """
        self.multiple = multiple
        
        # 存储选中的值
        self.selected_values = {
            'l1': [] if multiple else None
        }
        
        # UI元素引用
        self.l1_select = None
        
        # 在内存中存储层级数据，复用HierarchySelector的缓存机制
        self.hierarchy_data_cache = {'data': None, 'loading': False}
    
    def render(self):
        """渲染L1选择器组件"""
        with ui.column().classes('w-full'):
            self._create_l1_select()
        self._load_hierarchy_data()
    
    def render_with_label(self, label: str = "请选择一级分类"):
        """渲染带自定义标签的L1选择器组件"""
        with ui.column().classes('w-full'):
            ui.label(label).classes('text-sm font-medium mb-2')
            self._create_l1_select()
        self._load_hierarchy_data()
    
    def _create_l1_select(self):
        """创建一级选择器"""
        if self.multiple:
            # 多选模式
            self.l1_select = ui.select(
                options={},
                with_input=True,
                clearable=True,
                multiple=True,
                label='请选择一级分类'
            ).classes('w-full').props('dense use-chips')
        else:
            # 单选模式
            self.l1_select = ui.select(
                options={},
                with_input=True,
                clearable=True,
                label='请选择一级分类'
            ).classes('w-full').props('dense')
        
        def on_l1_change(event):
            self.selected_values['l1'] = event.value
            
        self.l1_select.on_value_change(on_l1_change)
    
    def _load_hierarchy_data(self):
        """加载层级数据并更新L1选择器选项"""
        async def do_load():
            if self.hierarchy_data_cache['loading']:
                return
            
            self.hierarchy_data_cache['loading'] = True
            try:
                # 获取层级数据
                hierarchy_data = await self._ensure_hierarchy_data_in_storage()
                self.hierarchy_data_cache['data'] = hierarchy_data
                
                # 更新一级选择器选项
                if hierarchy_data and self.l1_select:
                    l1_options = self._extract_level_options(hierarchy_data, 'l1')
                    options_dict = {opt['value']: opt['label'] for opt in l1_options}
                    self.l1_select.set_options(options_dict)
                    self.l1_select.set_label('请选择一级分类' if options_dict else '暂无分类数据')
                else:
                    if self.l1_select:
                        self.l1_select.set_label('数据加载失败')
                    
            except Exception as e:
                log_error("加载层级数据失败", exception=e)
                if self.l1_select:
                    self.l1_select.set_label('数据加载失败')
            finally:
                self.hierarchy_data_cache['loading'] = False
        
        asyncio.create_task(do_load())
    
    async def _fetch_hierarchy_data(self) -> Optional[Dict[str, Any]]:
        """调用MongoDB服务的/api/v1/hierarchy接口获取层级数据"""
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
        """确保存储中有层级数据，如果没有则获取并存储"""
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
        """从app.storage.general中获取层级数据"""
        try:
            hierarchy_data = app.storage.general.get('hierarchy_data')
            if hierarchy_data:
                # 检查数据是否过期（1小时过期）
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
    
    def _extract_level_options(self, hierarchy_data: Dict[str, Any], level: str) -> List[Dict[str, str]]:
        """从层级数据中提取一级分类选项"""
        options = []
        try:
            if not hierarchy_data:
                return options
                
            l1_categories = hierarchy_data.get('l1_categories', [])
            
            if level == 'l1':
                # 提取一级分类
                for l1 in l1_categories:
                    options.append({
                        'value': l1.get('l1_code', ''),
                        'label': l1.get('l1_name', '')
                    })
                    
        except Exception as e:
            log_error(f"提取{level}级别选项失败", exception=e)
        return options
    
    def get_selected_values(self) -> Dict[str, Any]:
        """
        获取当前选中的值
        
        Returns:
            Dict: 包含选中值的字典
            - multiple=True时，返回 {'l1': ['code1', 'code2', ...]}
            - multiple=False时，返回 {'l1': 'code1'} 或 {'l1': None}
        """
        return self.selected_values.copy()
    
    def get_selected_l1_codes(self) -> List[str] | str | None:
        """
        获取选中的L1代码
        
        Returns:
            - multiple=True时返回列表: ['code1', 'code2', ...]
            - multiple=False时返回字符串或None: 'code1' 或 None
        """
        return self.selected_values['l1']
    
    def get_selected_l1_names(self) -> List[str] | str | None:
        """
        根据选中的L1代码获取对应的名称
        
        Returns:
            - multiple=True时返回名称列表: ['名称1', '名称2', ...]
            - multiple=False时返回字符串或None: '名称1' 或 None
        """
        if not self.selected_values['l1']:
            return [] if self.multiple else None
        
        try:
            hierarchy_data = self.hierarchy_data_cache['data'] or self._get_hierarchy_data_from_storage()
            if not hierarchy_data:
                return [] if self.multiple else None
            
            l1_categories = hierarchy_data.get('l1_categories', [])
            
            if self.multiple:
                # 多选模式：返回名称列表
                names = []
                for l1_code in self.selected_values['l1']:
                    for l1 in l1_categories:
                        if l1.get('l1_code') == l1_code:
                            names.append(l1.get('l1_name', ''))
                            break
                return names
            else:
                # 单选模式：返回单个名称
                l1_code = self.selected_values['l1']
                for l1 in l1_categories:
                    if l1.get('l1_code') == l1_code:
                        return l1.get('l1_name', '')
                return None
                
        except Exception as e:
            log_error("获取L1名称失败", exception=e)
            return [] if self.multiple else None
    
    def reset_selection(self):
        """重置选择"""
        # 重置选中值
        self.selected_values['l1'] = [] if self.multiple else None
        
        # 重置UI组件
        if self.l1_select:
            if self.multiple:
                self.l1_select.set_value([])
            else:
                self.l1_select.set_value(None)
    
    def set_selected_values(self, l1_codes: List[str] | str):
        """
        设置选中的值
        
        Args:
            l1_codes: 
                - multiple=True时传入列表: ['code1', 'code2']
                - multiple=False时传入字符串: 'code1'
        """
        try:
            if self.multiple:
                if isinstance(l1_codes, list):
                    self.selected_values['l1'] = l1_codes
                    if self.l1_select:
                        self.l1_select.set_value(l1_codes)
                else:
                    log_error("多选模式下l1_codes必须是列表")
            else:
                if isinstance(l1_codes, str):
                    self.selected_values['l1'] = l1_codes
                    if self.l1_select:
                        self.l1_select.set_value(l1_codes)
                else:
                    log_error("单选模式下l1_codes必须是字符串")
                    
        except Exception as e:
            log_error("设置选中值失败", exception=e)
    
    def get_is_multiple(self) -> bool:
        """获取当前是否为多选模式"""
        return self.multiple
    
    def get_hierarchy_data(self) -> Optional[Dict[str, Any]]:
        """获取层级数据（供外部使用）"""
        return self.hierarchy_data_cache.get('data')


# 便捷函数
def create_l1_selector(multiple: bool = True, with_label: str = None) -> L1Selector:
    """
    便捷函数：创建L1选择器实例
    
    Args:
        multiple: 是否多选模式，默认True
        with_label: 自定义标签，如果提供则使用render_with_label渲染
    
    Returns:
        L1Selector: 选择器实例
    """
    selector = L1Selector(multiple=multiple)
    
    if with_label:
        selector.render_with_label(with_label)
    else:
        selector.render()
    
    return selector