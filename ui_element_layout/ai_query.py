from nicegui import ui

def create_ai_query_content():
    with ui.grid(rows=2).classes('w-full h-full p-6').style('grid-template-rows: auto 1fr; gap: 1.5rem;'):
        
        # 第一行：页面标题区域 (auto)
        with ui.column().classes('w-full'):
            ui.label('智能问数').classes('text-3xl font-bold text-blue-600 mb-2')
            ui.label('通过AI智能分析快速获取企业深度洞察').classes('text-gray-600 dark:text-gray-400 text-lg')
        
        with ui.grid(columns=2).classes('w-full h-full gap-6').style('grid-template-columns: auto 1fr;'): # 关键改动     
            with ui.column().classes('h-full gap-6'): # 使用 ui.column 垂直堆叠左侧内容
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
                                     on_click=lambda: query_input.set_value('')).classes('bg-blue-500 hover:bg-blue-600 text-white px-6 py-2')
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
            with ui.card().classes('w-full h-full p-6 shadow-lg'): # 确保这里 h-full
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
