# menu_pages/enterprise_archive_page.py 
from auth import auth_manager
from auth.decorators import require_permission
from nicegui import app, ui
from common.exception_handler import log_info, log_error, safe, db_safe, safe_protect
import aiohttp
import asyncio
from typing import Dict, Any, List, Optional

# MongoDB服务API基础URL
MONGODB_SERVICE_URL = "http://localhost:8001"

@safe_protect(name="一企一档", error_msg="一企一档页面加载失败")
def enterprise_archive_content():
    user = auth_manager.current_user
    # with ui.row().classes('w-full'): 
    #     # 第一行：标签头部区域
    #     with ui.tabs().classes('justify-start') as tabs:
    #         ai_query = ui.tab('智能问数', icon='tips_and_updates')
    #         data_operator = ui.tab('数据操作', icon='precision_manufacturing')
    #         data_sync = ui.tab('数据更新', icon='sync')
    #         setting = ui.tab('配置数据', icon='build_circle')
            
    #     # 第二行：分隔线
    #     # ui.separator().classes('w-full')
    #     # 第三行：内容区域
    #     with ui.tab_panels(tabs, value=ai_query).classes('w-full h-full'):
    #         with ui.tab_panel(ai_query).classes('w-full'):
    #             create_ai_query_content_grid()
    #         with ui.tab_panel(data_operator).classes('w-full'):
    #             create_data_operator_content_grid()
    #         with ui.tab_panel(data_sync).classes('w-full'):
    #             create_data_sync_content_grid()
    #         with ui.tab_panel(setting).classes('w-full'):
    #             create_setting_content_grid()

    with ui.splitter(value=10).classes('w-full h-full') as splitter:
        with splitter.before:
            with ui.tabs().classes('w-20 w-min-20 w-max-20').props('vertical') as tabs:
                ai_query = ui.tab('智能问数', icon='tips_and_updates')
                data_operator = ui.tab('数据操作', icon='precision_manufacturing')
                data_sync = ui.tab('数据更新', icon='sync')
                setting = ui.tab('配置数据', icon='build_circle')
        with splitter.after:
            with ui.tab_panels(tabs, value=ai_query).props('vertical').classes('w-full h-full'):    
                with ui.tab_panel(ai_query).classes('w-full'):
                    create_ai_query_content_grid()
                with ui.tab_panel(data_operator).classes('w-full'):
                    create_data_operator_content_grid()
                with ui.tab_panel(data_sync).classes('w-full'):
                    create_data_sync_content_grid()
                with ui.tab_panel(setting).classes('w-full'):
                    create_setting_content_grid()

async def fetch_hierarchy_data() -> Optional[Dict[str, Any]]:
    """
    调用MongoDB服务的/api/v1/hierarchy接口获取4级层级数据
    
    Returns:
        Optional[Dict[str, Any]]: 层级数据，如果获取失败返回None
    """
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

async def ensure_hierarchy_data_in_storage():
    """
    确保层级数据已存储在app.storage.general中，如果没有则获取并存储
    """
    # 检查是否已经存储（兼容性检查）
    try:
        if hasattr(app.storage.general, 'hierarchy_data') and app.storage.general.hierarchy_data:
            log_info("层级数据已存在于browser storage中")
            return app.storage.general.hierarchy_data
    except:
        # 如果访问browser storage出错，继续使用API获取
        pass
    
    # 获取层级数据
    hierarchy_data = await fetch_hierarchy_data()
    
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

def get_hierarchy_data_from_storage() -> Dict[str, Any]:
    """
    从app.storage.general获取层级数据，如果获取失败则返回空字典
    
    Returns:
        Dict[str, Any]: 层级数据，如果不存在返回空字典
    """
    try:
        return getattr(app.storage.general, 'hierarchy_data', {})
    except:
        # 如果访问browser storage出错，返回空字典
        return {}


def extract_level_options(hierarchy_data: Dict[str, Any], level: str, parent_code: str = None) -> List[Dict[str, str]]:
    """
    从层级数据中提取指定级别的选项列表
    
    Args:
        hierarchy_data: 完整的层级数据
        level: 级别 ('l1', 'l2', 'l3', 'field')
        parent_code: 父级代码（用于l2、l3、field级别的筛选）
    
    Returns:
        List[Dict[str, str]]: 选项列表，每个选项包含 'value'(code) 和 'label'(name)
    """
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


def create_ai_query_content_grid():
    """
    创建智能问数内容网格，包含4级级联选择器
    """
    
    # 存储选中的值
    selected_values = {
        'l1': None,
        'l2': None, 
        'l3': None,
        'field': None
    }
    
    # UI元素引用
    selects = {}
    
    # 在内存中存储层级数据，避免修改app.storage.general
    hierarchy_data_cache = {'data': None, 'loading': False}
    
    with ui.grid(columns=1).classes('w-full gap-4'):
        ui.label('智能问数 - 数据层级选择').classes(' font-weight-bold')
        
        # 4级级联选择器
        with ui.grid(columns=4).classes('w-full gap-4').style('height: 120px;'):
            
            # 第一级选择器
            def create_l1_select():
                with ui.column().classes('w-full h-10'):
                    # ui.label('一级分类').classes('text-subtitle2 q-mb-sm')
                    l1_select = ui.select(
                        options={},  # 初始为空，将通过加载数据更新
                        with_input=True,
                        clearable=True,
                        label='加载中...'
                    ).classes('w-full')

                    def on_l1_change(event): # Change 'value' to 'event'
                        selected_values['l1'] = event.value # Access event.value
                        selected_values['l2'] = None
                        selected_values['l3'] = None
                        selected_values['field'] = None

                        # 清空下级选择器
                        if 'l2' in selects:
                            selects['l2'].set_value(None)
                        if 'l3' in selects:
                            selects['l3'].set_value(None)
                        if 'field' in selects:
                            selects['field'].set_value(None)

                        # 更新二级选择器选项
                        update_l2_options()

                    l1_select.on_value_change(on_l1_change)
                    selects['l1'] = l1_select
                    return l1_select
            
            # 第二级选择器
            def create_l2_select():
                with ui.column().classes('w-full h-10'):
                    # ui.label('二级分类').classes('text-subtitle2 q-mb-sm')
                    l2_select = ui.select(
                        options={},
                        with_input=True,
                        clearable=True,
                        label='请先选择一级分类'
                    ).classes('w-full')
                    
                    def on_l2_change(event):
                        selected_values['l2'] = event.value
                        selected_values['l3'] = None
                        selected_values['field'] = None
                        
                        # 清空下级选择器
                        if 'l3' in selects:
                            selects['l3'].set_value(None)
                        if 'field' in selects:
                            selects['field'].set_value(None)
                        
                        # 更新三级选择器选项
                        update_l3_options()
                        
                    l2_select.on_value_change(on_l2_change)
                    selects['l2'] = l2_select
                    return l2_select
            
            # 第三级选择器
            def create_l3_select():
                with ui.column().classes('w-full h-10'):
                    # ui.label('三级分类').classes('text-subtitle2 q-mb-sm')
                    l3_select = ui.select(
                        options={},
                        with_input=True,
                        clearable=True,
                        label='请先选择二级分类'
                    ).classes('w-full')
                    
                    def on_l3_change(event):
                        selected_values['l3'] = event.value
                        selected_values['field'] = None
                        
                        # 清空下级选择器
                        if 'field' in selects:
                            selects['field'].set_value(None)
                        
                        # 更新字段选择器选项
                        update_field_options()
                        
                    l3_select.on_value_change(on_l3_change)
                    selects['l3'] = l3_select
                    return l3_select
            
            # 第四级选择器（字段）
            def create_field_select():
                with ui.column().classes('w-full h-10'):
                    # ui.label('数据字段').classes('text-subtitle2 q-mb-sm')
                    field_select = ui.select(
                        options={},
                        with_input=True,
                        clearable=True,
                        label='请先选择三级分类'
                    ).classes('w-full')
                    
                    def on_field_change(event):
                        selected_values['field'] = event.value
                        
                    field_select.on_value_change(on_field_change)
                    selects['field'] = field_select
                    return field_select
            
            # 更新选择器选项的函数
            def update_l2_options():
                if selected_values['l1'] and 'l2' in selects:
                    hierarchy_data = hierarchy_data_cache['data'] or get_hierarchy_data_from_storage()
                    l2_options = extract_level_options(hierarchy_data, 'l2', selected_values['l1'])
                    options_dict = {opt['value']: opt['label'] for opt in l2_options}
                    selects['l2'].set_options(options_dict)
                    selects['l2'].set_label('请选择二级分类' if options_dict else '暂无二级分类')
            
            def update_l3_options():
                if selected_values['l2'] and 'l3' in selects:
                    hierarchy_data = hierarchy_data_cache['data'] or get_hierarchy_data_from_storage()
                    l3_options = extract_level_options(hierarchy_data, 'l3', selected_values['l2'])
                    options_dict = {opt['value']: opt['label'] for opt in l3_options}
                    selects['l3'].set_options(options_dict)
                    selects['l3'].set_label('请选择三级分类' if options_dict else '暂无三级分类')
            
            def update_field_options():
                if selected_values['l3'] and 'field' in selects:
                    hierarchy_data = hierarchy_data_cache['data'] or get_hierarchy_data_from_storage()
                    field_options = extract_level_options(hierarchy_data, 'field', selected_values['l3'])
                    options_dict = {opt['value']: opt['label'] for opt in field_options}
                    selects['field'].set_options(options_dict)
                    selects['field'].set_label('请选择数据字段' if options_dict else '暂无数据字段')
            
            def load_hierarchy_data():
                """同步加载层级数据并更新UI"""
                async def do_load():
                    if hierarchy_data_cache['loading']:
                        return
                    
                    hierarchy_data_cache['loading'] = True
                    try:
                        # 获取层级数据
                        hierarchy_data = await ensure_hierarchy_data_in_storage()
                        hierarchy_data_cache['data'] = hierarchy_data
                        
                        # 更新一级选择器选项
                        if hierarchy_data and 'l1' in selects:
                            l1_options = extract_level_options(hierarchy_data, 'l1')
                            options_dict = {opt['value']: opt['label'] for opt in l1_options}
                            selects['l1'].set_options(options_dict)
                            selects['l1'].set_label('请选择一级分类' if options_dict else '暂无分类数据')
                        else:
                            selects['l1'].set_label('数据加载失败')
                            
                    except Exception as e:
                        log_error("加载层级数据失败", exception=e)
                        selects['l1'].set_label('数据加载失败')
                    finally:
                        hierarchy_data_cache['loading'] = False
                
                asyncio.create_task(do_load())
            
            # 创建所有选择器
            create_l1_select()
            create_l2_select()
            create_l3_select()
            create_field_select()
        
        # 操作按钮区域
        # with ui.row().classes('w-full q-mt-md'):
        #     ui.button('重置选择', 
        #              on_click=lambda: reset_selections(),
        #              icon='refresh').classes('q-mr-md')
            
        #     ui.button('查询数据', 
        #              on_click=lambda: query_data(),
        #              icon='search').classes('q-mr-md')
            
        #     ui.button('刷新层级数据', 
        #              on_click=lambda: refresh_hierarchy_data(),
        #              icon='sync').classes('q-mr-md')
        
        # 选中信息显示区域 - 隐藏
        # selection_info = ui.card().classes('w-full q-mt-md').style('display: none;')
        
        def reset_selections():
            """重置所有选择"""
            for key in selected_values:
                selected_values[key] = None
            
            for select in selects.values():
                select.set_value(None)
            
            # 重置下级选择器选项
            selects['l2'].set_options({})
            selects['l2'].set_label('请先选择一级分类')
            selects['l3'].set_options({})
            selects['l3'].set_label('请先选择二级分类')
            selects['field'].set_options({})
            selects['field'].set_label('请先选择三级分类')
            
            update_selection_info()
        
        def query_data():
            """查询数据"""
            if not any(selected_values.values()):
                ui.notify('请至少选择一个分类', type='warning')
                return
            
            ui.notify(f'查询数据: {selected_values}', type='info')
            update_selection_info()
        
        def refresh_hierarchy_data():
            """刷新层级数据"""
            async def do_refresh():
                # 清除已存储的数据
                try:
                    if hasattr(app.storage.general, 'hierarchy_data'):
                        delattr(app.storage.general, 'hierarchy_data')
                except:
                    pass
                
                # 清除内存缓存
                hierarchy_data_cache['data'] = None
                
                # 重新获取数据
                hierarchy_data = await ensure_hierarchy_data_in_storage()
                hierarchy_data_cache['data'] = hierarchy_data
                
                # 重置选择器
                reset_selections()
                
                # 重新初始化一级选择器选项
                if hierarchy_data and 'l1' in selects:
                    l1_options = extract_level_options(hierarchy_data, 'l1')
                    options_dict = {opt['value']: opt['label'] for opt in l1_options}
                    selects['l1'].set_options(options_dict)
                    selects['l1'].set_label('请选择一级分类' if options_dict else '暂无分类数据')
                
                ui.notify('层级数据已刷新', type='positive')
            
            asyncio.create_task(do_refresh())
        
        def update_selection_info():
            """更新选中信息显示 - 当前已隐藏"""
            pass
    
    # 页面加载时初始化层级数据
    load_hierarchy_data()


def create_data_operator_content_grid():
    """创建数据操作内容网格"""
    with ui.grid(columns=1).classes('w-full gap-4'):
        ui.label('数据操作功能').classes('text-h6')
        ui.label('此功能正在开发中...').classes('text-body1 text-grey-6')


def create_data_sync_content_grid():
    """创建数据更新内容网格"""
    with ui.grid(columns=1).classes('w-full gap-4'):
        ui.label('数据更新功能').classes('text-h6')
        ui.label('此功能正在开发中...').classes('text-body1 text-grey-6')


def create_setting_content_grid():
    """创建配置数据内容网格"""
    with ui.grid(columns=1).classes('w-full gap-4'):
        ui.label('配置数据功能').classes('text-h6')
        ui.label('此功能正在开发中...').classes('text-body1 text-grey-6')