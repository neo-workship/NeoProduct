# menu_pages/enterprise_archive_page.py 
from auth import auth_manager
from auth.decorators import require_permission
from nicegui import ui
# 导入异常处理模块
from common.exception_handler import log_info, log_error, safe, db_safe, safe_protect

@safe_protect(name="一企一档", error_msg="一企一档页面加载失败")
def enterprise_archive_content():
    user = auth_manager.current_user
    # ui.label(f'欢迎，{user.username}, 权限为：{user.permissions}')
    
    with ui.tabs().classes('w-full') as tabs:
        ai_query = ui.tab('智能问数', icon='tips_and_updates').classes('flex-grow')
        data_operator = ui.tab('数据操作', icon='precision_manufacturing').classes('flex-grow')
        data_sync = ui.tab('数据更新', icon='sync_alt').classes('flex-grow')
        setting = ui.tab('配置数据', icon='build_circle').classes('flex-grow')
    ui.separator()
    with ui.tab_panels(tabs, value=ai_query).classes('w-full'):
        with ui.tab_panel(ai_query):
            create_ai_query_content()
        with ui.tab_panel(data_operator):
            create_data_operator_content()
        with ui.tab_panel(data_sync):
            create_data_sync_content()
        with ui.tab_panel(setting):
            create_setting_content()

def create_ai_query_content():
    """创建智能问数内容"""
    with ui.column().classes('w-full'):
        ui.label('智能问数').classes('text-2xl font-bold mb-4 text-blue-600')
        
        # 创建一个卡片容器展示功能 - 使用全宽度
        with ui.card().classes('w-full mb-4 p-4'):
            ui.label('🤖 AI智能分析').classes('text-lg font-semibold mb-2')
            ui.label('通过自然语言提问，快速获取企业数据分析结果，支持多维度数据查询和可视化展示。').classes('text-gray-600 mb-4')
            
            # 搜索框 - 确保全宽度
            query_input = ui.input('请输入您的问题...', 
                                 placeholder='例：这家企业的注册资本是多少？').classes('w-full mb-2')
            
            with ui.row().classes('gap-2 w-full'):
                ui.button('提问', icon='send', 
                         on_click=lambda: handle_ai_query(query_input.value)).classes('bg-blue-500 text-white')
                ui.button('清除', icon='clear', 
                         on_click=lambda: query_input.set_value('')).classes('bg-gray-400 text-white')
        
        # 常用问题示例 - 使用全宽度
        with ui.card().classes('w-full p-4'):
            ui.label('🔥 常用问题示例').classes('text-lg font-semibold mb-2')
            example_questions = [
                '企业基本信息查询',
                '财务数据分析',
                '风险评估报告', 
                '行业对比分析'
            ]
            
            # 使用 row 和 wrap 确保按钮可以换行并占满宽度
            with ui.row().classes('gap-2 w-full flex-wrap'):
                for question in example_questions:
                    ui.button(question, icon='help_outline',
                             on_click=lambda q=question: query_input.set_value(f'请帮我分析{q}')).props('flat').classes('mb-2')
        
        # 添加一些占位内容来测试宽度占满效果
        with ui.card().classes('w-full p-4 mt-4'):
            ui.label('📊 分析结果展示区域').classes('text-lg font-semibold mb-2')
            with ui.row().classes('w-full gap-4'):
                with ui.column().classes('flex-1'):
                    ui.label('这里将显示分析结果...').classes('text-gray-500 p-4 border border-dashed border-gray-300 rounded text-center')
                with ui.column().classes('flex-1'):
                    ui.label('这里将显示图表数据...').classes('text-gray-500 p-4 border border-dashed border-gray-300 rounded text-center')
                with ui.column().classes('flex-1'):
                    ui.label('这里将显示统计信息...').classes('text-gray-500 p-4 border border-dashed border-gray-300 rounded text-center')

def create_data_operator_content():
    """创建数据操作内容"""
    with ui.column().classes('tab-content'):
        ui.label('数据操作').classes('text-2xl font-bold mb-4 text-green-600')
        
        with ui.card().classes('w-full mb-4 p-4'):
            ui.label('🛠️ 数据管理工具').classes('text-lg font-semibold mb-2')
            ui.label('提供企业数据的增删改查功能，支持批量操作和数据导入导出。').classes('text-gray-600 mb-4')
            
            with ui.row().classes('gap-4'):
                ui.button('新增数据', icon='add', 
                         on_click=lambda: ui.notify('打开新增数据对话框')).classes('bg-green-500 text-white')
                ui.button('批量导入', icon='upload', 
                         on_click=lambda: ui.notify('打开批量导入功能')).classes('bg-blue-500 text-white')
                ui.button('数据导出', icon='download', 
                         on_click=lambda: ui.notify('开始导出数据')).classes('bg-orange-500 text-white')
                ui.button('数据清理', icon='cleaning_services', 
                         on_click=lambda: ui.notify('开始数据清理')).classes('bg-purple-500 text-white')
        
        # 数据表格示例
        with ui.card().classes('w-full p-4'):
            ui.label('📊 数据列表').classes('text-lg font-semibold mb-2')
            # 这里可以添加数据表格组件
            ui.label('数据表格将在此处显示...').classes('text-gray-500 text-center p-8')

def create_data_sync_content():
    """创建数据更新内容"""
    with ui.column().classes('tab-content'):
        ui.label('数据更新').classes('text-2xl font-bold mb-4 text-orange-600')
        
        with ui.card().classes('w-full mb-4 p-4'):
            ui.label('🔄 同步管理').classes('text-lg font-semibold mb-2')
            ui.label('管理企业数据的同步更新，包括自动同步和手动同步功能。').classes('text-gray-600 mb-4')
            
            # 同步状态
            with ui.row().classes('gap-4 mb-4'):
                ui.badge('最后同步: 2024-01-15 10:30', color='positive')
                ui.badge('待同步: 15条记录', color='warning')
                ui.badge('同步状态: 正常', color='positive')
            
            with ui.row().classes('gap-4'):
                ui.button('立即同步', icon='sync', 
                         on_click=lambda: handle_sync()).classes('bg-orange-500 text-white')
                ui.button('同步设置', icon='settings', 
                         on_click=lambda: ui.notify('打开同步设置')).classes('bg-gray-500 text-white')
                ui.button('同步日志', icon='history', 
                         on_click=lambda: ui.notify('查看同步日志')).classes('bg-blue-500 text-white')
        
        # 同步进度
        with ui.card().classes('w-full p-4'):
            ui.label('📈 同步进度').classes('text-lg font-semibold mb-2')
            progress = ui.linear_progress(value=0.0).classes('w-full mb-2')
            progress_label = ui.label('准备就绪').classes('text-sm text-gray-600')

def create_setting_content():
    """创建配置数据内容"""
    with ui.column().classes('tab-content'):
        ui.label('配置数据').classes('text-2xl font-bold mb-4 text-purple-600')
        
        with ui.card().classes('w-full mb-4 p-4'):
            ui.label('⚙️ 系统配置').classes('text-lg font-semibold mb-2')
            ui.label('管理企业档案系统的各项配置参数和业务规则。').classes('text-gray-600 mb-4')
            
            # 配置项
            with ui.column().classes('gap-4'):
                with ui.row().classes('items-center gap-4'):
                    ui.label('数据源配置:').classes('font-medium min-w-fit')
                    ui.input('数据库连接字符串', placeholder='请输入数据库连接信息').classes('flex-1')
                
                with ui.row().classes('items-center gap-4'):
                    ui.label('同步频率:').classes('font-medium min-w-fit')
                    ui.select(['每小时', '每天', '每周', '手动'], value='每天').classes('flex-1')
                
                with ui.row().classes('items-center gap-4'):
                    ui.label('自动备份:').classes('font-medium min-w-fit')
                    ui.switch('启用自动备份', value=True)
                
                with ui.row().classes('items-center gap-4'):
                    ui.label('日志级别:').classes('font-medium min-w-fit')
                    ui.select(['DEBUG', 'INFO', 'WARNING', 'ERROR'], value='INFO').classes('flex-1')
        
        with ui.card().classes('w-full p-4'):
            ui.label('💾 操作').classes('text-lg font-semibold mb-2')
            with ui.row().classes('gap-4'):
                ui.button('保存配置', icon='save', 
                         on_click=lambda: ui.notify('配置已保存', type='positive')).classes('bg-green-500 text-white')
                ui.button('重置配置', icon='restart_alt', 
                         on_click=lambda: ui.notify('配置已重置', type='info')).classes('bg-gray-500 text-white')
                ui.button('导出配置', icon='file_download', 
                         on_click=lambda: ui.notify('配置导出中...', type='info')).classes('bg-blue-500 text-white')

def handle_ai_query(query):
    """处理AI问答"""
    if not query.strip():
        ui.notify('请输入问题', type='warning')
        return
    
    ui.notify(f'正在分析问题: {query}', type='info')
    # 这里可以添加实际的AI问答逻辑

def handle_sync():
    """处理数据同步"""
    ui.notify('开始同步数据...', type='info')
    # 这里可以添加实际的同步逻辑