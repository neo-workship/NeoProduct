"""
HierarchySelector多选功能使用示例
展示如何在不影响现有代码的情况下使用新的多选功能
"""
from nicegui import ui
import sys
from pathlib import Path

# 修复模块导入路径问题
# 获取当前文件的父目录（test目录）
current_dir = Path(__file__).resolve().parent
# 获取enterprise_archive目录（上一级目录）
parent_dir = current_dir.parent
# 获取项目根目录（neo_webproduct_beta_v2）
root_dir = parent_dir.parent.parent

# 将必要的目录添加到sys.path
sys.path.insert(0, str(parent_dir))  # enterprise_archive目录
sys.path.insert(0, str(root_dir))    # 项目根目录，用于导入common模块

# 现在可以直接导入hierarchy_selector_component
from hierarchy_selector_component import HierarchySelector


def example_original_usage():
    """原有使用方式 - 完全不需要修改"""
    ui.label('原有使用方式（零修改）').classes('text-xl font-bold mb-4')
    
    # 完全按照原来的方式使用，不需要任何修改
    selector = HierarchySelector()  # 默认单选模式
    selector.render_row()
    
    def show_values():
        values = selector.get_selected_values()
        field_value = values.get('field')  # 单选时返回字符串或None
        ui.notify(f"选中字段: {field_value}")
        ui.notify(f"完整路径: {values.get('full_path_name')}")
    
    ui.button('获取选中值', on_click=show_values).classes('mt-4')

def example_new_multiple_usage():
    """新的多选使用方式"""
    ui.label('新的多选使用方式').classes('text-xl font-bold mb-4 mt-8')
    
    # 启用多选模式 - 只需要添加一个参数
    selector_multi = HierarchySelector(multiple=True)
    selector_multi.render_row()
    
    def show_multi_values():
        values = selector_multi.get_selected_values()
        field_values = values.get('field')  # 多选时返回列表
        
        if isinstance(field_values, list):
            ui.notify(f"选中 {len(field_values)} 个字段: {field_values}")
            if field_values:
                # data_url等优化字段使用第一个选中项的值
                ui.notify(f"数据URL（第一个）: {values.get('data_url')}")
        else:
            ui.notify("未选中任何字段")
    
    ui.button('获取多选值', on_click=show_multi_values).classes('mt-4')

def example_compatibility_handling():
    """兼容性处理示例 - 如何写代码同时支持单选和多选"""
    ui.label('兼容性处理示例').classes('text-xl font-bold mb-4 mt-8')
    
    # 创建两个选择器用于对比
    single_selector = HierarchySelector(multiple=False)
    multi_selector = HierarchySelector(multiple=True)
    
    with ui.row().classes('w-full gap-8'):
        with ui.column().classes('flex-1'):
            ui.label('单选模式:')
            single_selector.render_column()
        
        with ui.column().classes('flex-1'):
            ui.label('多选模式:')
            multi_selector.render_column()
    
    def handle_both_types():
        """演示如何编写兼容两种模式的代码"""
        single_values = single_selector.get_selected_values()
        multi_values = multi_selector.get_selected_values()
        
        # 通用处理函数
        def process_field_value(field_value, mode_name):
            if isinstance(field_value, list):
                # 多选模式
                if field_value:
                    return f"{mode_name}: 选中 {len(field_value)} 个字段 - {field_value[:3]}{'...' if len(field_value) > 3 else ''}"
                else:
                    return f"{mode_name}: 未选中任何字段"
            else:
                # 单选模式
                return f"{mode_name}: 选中字段 - {field_value or '无'}"
        
        single_result = process_field_value(single_values.get('field'), "单选")
        multi_result = process_field_value(multi_values.get('field'), "多选")
        
        ui.notify(single_result)
        ui.notify(multi_result)
    
    ui.button('对比两种模式', on_click=handle_both_types).classes('mt-4')

# 主页面
@ui.page("/")
def create_demo_page():
    ui.page_title('HierarchySelector 多选功能演示')
    
    with ui.column().classes('w-full max-w-6xl mx-auto p-6'):
        ui.html('<h1 class="text-3xl font-bold mb-6">HierarchySelector 多选功能演示</h1>')
        
        # 兼容性说明
        with ui.card().classes('w-full mb-6 p-4 bg-green-50'):
            ui.html('''
            <div class="text-green-800">
                <h2 class="text-lg font-semibold mb-2">✅ 完全向后兼容保证</h2>
                <ul class="list-disc pl-6 space-y-1 text-sm">
                    <li>现有代码无需任何修改，直接使用</li>
                    <li>API接口保持完全一致</li>
                    <li>原有逻辑和数据加载方式完全不变</li>
                    <li>只是在创建时可选择性地启用多选模式</li>
                </ul>
            </div>
            ''')
        
        example_original_usage()
        example_new_multiple_usage()
        example_compatibility_handling()

# 如果直接运行此文件
if __name__ in {"__main__", "__mp_main__"}:
    ui.run(
        title='HierarchySelector 多选功能演示',
        host='0.0.0.0',
        port=8381,
        reload=True,
        show=True
    )