# menu_pages/enterprise_archive_page.py 
from auth import auth_manager
from auth.decorators import require_permission
from nicegui import ui
# 导入异常处理模块
from common.exception_handler import log_info, log_error, safe, db_safe, safe_protect

@safe_protect(name="一企一档", error_msg="一企一档页面加载失败")
def enterprise_archive_content():
    user = auth_manager.current_user
    
    with ui.grid(rows=3).classes('w-full').style('grid-template-rows: auto auto 1fr; min-height: 100vh;'):
        # 第一行：标签头部区域 (auto高度)
        with ui.tabs().classes('w-full dark:bg-gray-800 border-b shadow-sm') as tabs:
            ai_query = ui.tab('智能问数', icon='tips_and_updates').classes('flex-1 text-center')
            data_operator = ui.tab('数据操作', icon='precision_manufacturing').classes('flex-1 text-center')
            data_sync = ui.tab('数据更新', icon='sync_alt').classes('flex-1 text-center')
            setting = ui.tab('配置数据', icon='build_circle').classes('flex-1 text-center')
        
        # 第二行：分隔线 (auto高度)
        ui.separator().classes('border-gray-200 dark:border-gray-700')
        
        # 第三行：内容区域 (1fr - 占满剩余所有空间)
        with ui.tab_panels(tabs, value=ai_query).classes('w-full h-full overflow-auto'):
            with ui.tab_panel(ai_query).classes('w-full h-full'):
                create_ai_query_content_grid()
            with ui.tab_panel(data_operator).classes('w-full h-full'):
                create_data_operator_content_grid()
            with ui.tab_panel(data_sync).classes('w-full h-full'):
                create_data_sync_content_grid()
            with ui.tab_panel(setting).classes('w-full h-full'):
                create_setting_content_grid()

def create_ai_query_content_grid():
    """使用ui.grid的AI查询内容 - 完全填充父容器，并实现左右两栏布局"""
    with ui.grid(rows=2).classes('w-full p-6 gap-1').style('grid-template-rows: auto 1fr; gap: 1rem;'):
        # 第一行：页面标题区域 (auto)
        with ui.column().classes('w-full'):
            ui.label('智能问数').classes('text-3xl font-bold text-blue-600 mb-2')
            ui.label('通过AI智能分析快速获取企业深度洞察').classes('text-gray-600 dark:text-gray-400 text-lg')
        
        # 第二行：主要内容区域 - 改为左右两列布局 (1fr - 占满剩余所有空间)
        with ui.grid(columns=2).classes('w-full gap-6').style('grid-template-columns: auto 1fr;'): # 关键改动
            # 左列：包含AI分析卡片、常用问题和快捷操作 (auto宽度)
            with ui.column().classes('h-full gap-6'):
                # 主要功能卡片
                with ui.card().classes('w-full p-6 shadow-lg border border-blue-100 dark:border-blue-800'):
                    ui.label('🤖 AI智能分析').classes('text-xl font-semibold mb-3 text-blue-700 dark:text-blue-300')
                    ui.label('通过自然语言提问，快速获取企业数据分析结果，支持多维度数据查询和可视化展示。').classes('text-gray-600 dark:text-gray-400 mb-4 leading-relaxed')
                    
                    # 搜索区域
                    with ui.column().classes('w-full gap-3'):
                        query_input = ui.input(
                            label='请输入您的问题', 
                            placeholder='例：这家企业的注册资本是多少？近三年的营收趋势如何？'
                        ).classes('w-full').props('outlined clearable')
                        
                        with ui.row().classes('gap-3 w-full'):
                            ui.button('🚀 开始分析', icon='send', 
                                     on_click=lambda: handle_ai_query(query_input.value)).classes('bg-blue-500 hover:bg-blue-600 text-white px-6 py-2')
                            ui.button('清除', icon='clear_all', 
                                     on_click=lambda: query_input.set_value('')).classes('bg-gray-400 hover:bg-gray-500 text-white px-4 py-2')
                            ui.button('语音输入', icon='mic').classes('bg-green-500 hover:bg-green-600 text-white px-4 py-2')
                
                # 双列卡片区域 - 常用问题示例 & 快捷操作 (垂直堆叠在AI分析卡片下方)
                with ui.grid(columns=2).classes('w-full gap-6'):
                    # 左列：常用问题示例
                    with ui.card().classes('w-full p-6 shadow-lg'):
                        ui.label('🔥 常用问题示例').classes('text-xl font-semibold mb-4 text-orange-600 dark:text-orange-400')
                        
                        with ui.grid(columns=2).classes('w-full gap-3'):
                            example_questions = [
                                {'text': '企业基本信息查询', 'icon': 'business'},
                                {'text': '财务数据分析', 'icon': 'analytics'},
                                {'text': '风险评估报告', 'icon': 'warning'},
                                {'text': '行业对比分析', 'icon': 'compare_arrows'},
                                {'text': '投资价值评估', 'icon': 'trending_up'},
                                {'text': '合规状态检查', 'icon': 'verified'}
                            ]
                            for question in example_questions:
                                ui.button(question['text'], icon=question['icon'],
                                          on_click=lambda q=question['text']: query_input.set_value(f'请帮我分析{q}')).classes('w-full justify-start bg-blue-50 hover:bg-blue-100 text-blue-700 border border-blue-200 p-3 rounded-lg')
                    
                    # 右列：快捷操作
                    with ui.card().classes('w-full p-6 shadow-lg'):
                        ui.label('⚡ 快捷操作').classes('text-xl font-semibold mb-4 text-purple-600 dark:text-purple-400')
                        
                        with ui.grid(columns=1).classes('w-full gap-3'):
                            quick_actions = [
                                {'text': '上传企业文档', 'icon': 'upload_file'},
                                {'text': '生成分析报告', 'icon': 'assessment'},
                                {'text': '导出数据', 'icon': 'download'},
                                {'text': '设置分析模板', 'icon': 'settings'}
                            ]
                            for action in quick_actions:
                                ui.button(action['text'], icon=action['icon']).classes('w-full justify-start bg-gray-50 hover:bg-gray-100 text-gray-700 border border-gray-200 p-3 rounded-lg')
            # 右列：分析结果展示区域 - 占满剩余空间 (1fr宽度)
            with ui.card().classes('w-full h-full p-6 shadow-lg'): 
                ui.label('📊 分析结果展示区域').classes('text-xl font-semibold mb-4 text-green-600 dark:text-green-400')
                
                # 使用ui.grid创建三列等宽结果展示区
                with ui.grid(columns=3).classes('w-full h-full gap-6').style('grid-template-rows: 1fr;'):
                    # 结果展示区
                    with ui.element('div').classes('bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20 border border-blue-200 dark:border-blue-700 rounded-lg p-6 flex flex-col items-center justify-center h-full'):
                        ui.icon('analytics', size='3rem').classes('text-blue-500 mb-3')
                        ui.label('分析结果').classes('text-lg font-semibold text-blue-700 dark:text-blue-300 mb-2')
                        ui.label('AI分析结果将在此展示').classes('text-blue-600 dark:text-blue-400 text-center text-sm')
                    
                    # 图表数据区
                    with ui.element('div').classes('bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/20 border border-green-200 dark:border-green-700 rounded-lg p-6 flex flex-col items-center justify-center h-full'):
                        ui.icon('insert_chart', size='3rem').classes('text-green-500 mb-3')
                        ui.label('可视化图表').classes('text-lg font-semibold text-green-700 dark:text-green-300 mb-2')
                        ui.label('数据图表将在此展示').classes('text-green-600 dark:text-green-400 text-center text-sm')
                    
                    # 统计信息区
                    with ui.element('div').classes('bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-900/20 dark:to-purple-800/20 border border-purple-200 dark:border-purple-700 rounded-lg p-6 flex flex-col items-center justify-center h-full'):
                        ui.icon('bar_chart', size='3rem').classes('text-purple-500 mb-3')
                        ui.label('统计摘要').classes('text-lg font-semibold text-purple-700 dark:text-purple-300 mb-2')
                        ui.label('关键指标统计在此展示').classes('text-purple-600 dark:text-purple-400 text-center text-sm')

def create_data_operator_content_grid():
    """使用ui.grid的数据操作内容"""
    with ui.element('div').classes('flex h-screen w-full bg-gray-100'):
    
        # 左侧大容器 - 占据2/3的宽度
        with ui.element('div').classes('flex-1 bg-white border-2 border-gray-800 m-2 rounded-lg shadow-lg'):
            ui.label('左侧主要内容区域').classes('p-4 text-xl font-bold text-gray-700')
            
            # 可以在这里添加更多内容
            with ui.element('div').classes('p-4'):
                ui.markdown('''
                ### 主要内容区域
                
                这是页面的主要内容区域，占据了大部分空间。
                您可以在这里放置：
                - 图表和数据可视化
                - 表格和列表
                - 表单和输入控件
                - 其他主要功能组件
                ''')
        
        # 右侧容器 - 包含两个垂直排列的框
        with ui.element('div').classes('flex flex-col w-80 gap-2 m-2'):
            
            # 右上角容器 - 占据右侧1/2高度
            with ui.element('div').classes('flex-1 bg-white border-2 border-gray-800 rounded-lg shadow-lg'):
                ui.label('右上区域').classes('p-4 text-lg font-semibold text-gray-700')
                
                with ui.element('div').classes('p-4'):
                    ui.markdown('''
                    **侧边栏上部**
                    
                    这里可以放置：
                    - 快速操作按钮
                    - 重要通知
                    - 用户信息
                    ''')
            
            # 右下角容器 - 占据右侧1/2高度
            with ui.element('div').classes('flex-1 bg-white border-2 border-gray-800 rounded-lg shadow-lg'):
                ui.label('右下区域').classes('p-4 text-lg font-semibold text-gray-700')
                
                with ui.element('div').classes('p-4'):
                    ui.markdown('''
                    **侧边栏下部**
                    
                    这里可以放置：
                    - 设置选项
                    - 统计信息
                    - 辅助工具
                    ''')

def create_data_sync_content_grid():
    """使用ui.grid的数据同步内容"""
    with ui.grid(rows=2).classes('w-full h-full p-6').style('grid-template-rows: auto 1fr; gap: 1.5rem;'):
        
        # 页面标题
        with ui.column().classes('w-full'):
            ui.label('数据更新').classes('text-3xl font-bold text-orange-600 mb-2')
            ui.label('企业数据同步与更新管理中心').classes('text-gray-600 dark:text-gray-400 text-lg')
        
        # 主要内容区域
        with ui.grid(rows=2).classes('w-full h-full').style('grid-template-rows: auto 1fr; gap: 1.5rem;'):
            
            # 同步状态概览卡片
            with ui.card().classes('w-full p-6 shadow-lg border border-orange-100 dark:border-orange-800'):
                ui.label('🔄 同步管理').classes('text-xl font-semibold mb-3 text-orange-700 dark:text-orange-300')
                ui.label('管理企业数据的同步更新，包括自动同步和手动同步功能。').classes('text-gray-600 dark:text-gray-400 mb-4 leading-relaxed')
                
                # 使用ui.grid创建状态指标布局
                with ui.grid(columns=3, rows=2).classes('w-full gap-4').style('grid-template-rows: auto auto;'):
                    
                    # 第一行：状态指标
                    with ui.element('div').classes('bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-700 rounded-lg p-4'):
                        ui.label('最后同步').classes('text-sm text-green-600 dark:text-green-400 mb-1')
                        ui.label('2024-01-15 10:30').classes('text-lg font-semibold text-green-700 dark:text-green-300')
                    
                    with ui.element('div').classes('bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-700 rounded-lg p-4'):
                        ui.label('待同步记录').classes('text-sm text-yellow-600 dark:text-yellow-400 mb-1')
                        ui.label('15 条').classes('text-lg font-semibold text-yellow-700 dark:text-yellow-300')
                    
                    with ui.element('div').classes('bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-700 rounded-lg p-4'):
                        ui.label('同步状态').classes('text-sm text-blue-600 dark:text-blue-400 mb-1')
                        ui.label('正常运行').classes('text-lg font-semibold text-blue-700 dark:text-blue-300')
                    
                    # 第二行：操作按钮 - 跨3列
                    with ui.element('div').classes('col-span-3'):
                        with ui.grid(columns=3).classes('w-full gap-4'):
                            ui.button('立即同步', icon='sync', 
                                     on_click=lambda: handle_sync()).classes('bg-orange-500 hover:bg-orange-600 text-white py-3 px-6 rounded-lg shadow')
                            ui.button('同步设置', icon='settings', 
                                     on_click=lambda: ui.notify('打开同步设置')).classes('bg-gray-500 hover:bg-gray-600 text-white py-3 px-6 rounded-lg shadow')
                            ui.button('同步日志', icon='history', 
                                     on_click=lambda: ui.notify('查看同步日志')).classes('bg-blue-500 hover:bg-blue-600 text-white py-3 px-6 rounded-lg shadow')
            
            # 同步进度展示区域
            with ui.card().classes('w-full h-full p-6 shadow-lg'):
                ui.label('📈 同步进度').classes('text-xl font-semibold mb-4 text-gray-700 dark:text-gray-300')
                
                with ui.column().classes('w-full h-full gap-4'):
                    progress = ui.linear_progress(value=0.0).classes('w-full h-2 rounded')
                    progress_label = ui.label('准备就绪').classes('text-sm text-gray-600 dark:text-gray-400')
                    
                    # 同步历史记录 - 占满剩余空间
                    with ui.element('div').classes('w-full flex-1 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg flex items-center justify-center').style('min-height: 200px;'):
                        with ui.column().classes('items-center gap-3'):
                            ui.icon('history', size='3rem').classes('text-gray-400')
                            ui.label('同步历史记录').classes('text-gray-500 text-lg')
                            ui.label('显示最近的同步操作记录').classes('text-gray-400 text-sm')

def create_setting_content_grid():
    with ui.row().classes('flex h-screen w-full bg-gray-100 gap-2 p-2'):
    
        # 左侧大容器 - 使用卡片组件
        with ui.card().classes('flex-1'):
            ui.label('左侧主要内容区域').classes('text-xl font-bold text-gray-700 mb-4')
            
            # 使用容器组件代替div
            with ui.column().classes('gap-4'):
                ui.markdown('''
                ### 主要内容区域
                
                这是页面的主要内容区域，占据了大部分空间。
                您可以在这里放置：
                - 图表和数据可视化
                - 表格和列表
                - 表单和输入控件
                - 其他主要功能组件
                ''')
        
        # 右侧容器 - 使用列布局
        with ui.column().classes('w-80 gap-2'):
            
            # 右上角容器 - 使用卡片组件
            with ui.card().classes('flex-1'):
                ui.label('右上区域').classes('text-lg font-semibold text-gray-700 mb-2')
                
                with ui.column().classes('gap-2'):
                    ui.markdown('''
                    **侧边栏上部**
                    
                    这里可以放置：
                    - 快速操作按钮
                    - 重要通知
                    - 用户信息
                    ''')
            
            # 右下角容器 - 使用卡片组件
            with ui.card().classes('flex-1'):
                ui.label('右下区域').classes('text-lg font-semibold text-gray-700 mb-2')
                
                with ui.column().classes('gap-2'):
                    ui.markdown('''
                    **侧边栏下部**
                    
                    这里可以放置：
                    - 设置选项
                    - 统计信息
                    - 辅助工具
                    ''')

def handle_ai_query(query):
    """处理AI问答"""
    if not query or not query.strip():
        ui.notify('请输入问题', type='warning')
        return
    
    ui.notify(f'正在分析问题: {query}', type='info')
    # 这里可以添加实际的AI问答逻辑

def handle_sync():
    """处理数据同步"""
    ui.notify('开始同步数据...', type='info')
    # 这里可以添加实际的同步逻辑