from nicegui import ui
from common.log_handler import (
    # 日志记录函数
    log_trace, log_debug, log_info, log_success, log_warning, log_error, log_critical,
    # 安全执行
    safe, db_safe,
    # 装饰器
    safe_protect, catch,
    # Logger 实例
    get_logger
)

@safe_protect(name="首页内容", error_msg="首页内容发生错误", return_on_error=None)
def home_content():
    """首页内容 - 左右布局展示平台功能和外部应用"""
    
    log_info("加载首页内容")
    
    # 页面标题区域
    with ui.column().classes('w-full mb-2'):
        ui.label('欢迎使用智能管理平台').classes('text-3xl font-bold text-blue-800 dark:text-blue-200 mb-2')
        ui.label('一站式 AI 智能应用管理中心').classes('text-lg text-gray-600 dark:text-gray-400')
    
    # 主体内容区域 - 左右布局
    with ui.row().classes('w-full gap-2 flex-wrap items-stretch'):
        
        # ==================== 左侧：平台应用说明 ====================
        with ui.column().classes('flex-1 min-w-[500px] gap-2'):
            
            # 左侧标题卡片
            with ui.card().classes('w-full p-2 bg-gradient-to-br from-blue-500 to-blue-600 text-white shadow-lg'):
                with ui.row().classes('items-center gap-2'):
                    ui.icon('apps').classes('text-4xl')
                    with ui.column().classes('gap-1'):
                        ui.label('平台核心应用').classes('text-xl font-bold')
                        ui.label('Platform Core Applications').classes('text-sm opacity-90')
            
            # 1. AI 档案管理
            with ui.card().classes('w-full p-2 hover:shadow-xl transition-shadow duration-300 border-l-4 border-purple-500'):
                with ui.row().classes('items-start gap-2'):
                    with ui.avatar().classes('w-14 h-14 bg-gradient-to-br from-purple-400 to-purple-600'):
                        ui.icon('folder_special').classes('text-3xl text-white')
                    
                    with ui.column().classes('flex-1 gap-2'):
                        ui.label('AI 档案管理').classes('text-xl font-bold text-gray-800 dark:text-white')                        
                        ui.label('基于 AI 技术的智能档案管理系统,支持多维度档案分类与管理').classes('text-sm text-gray-600 dark:text-gray-300 mb-3')
                        
                        # 功能列表
                        with ui.grid(columns=2).classes('gap-1'):
                            archive_features = [
                                ('person', '一人一档', '个人档案智能管理', 'blue'),
                                ('business', '一企一档', '企业信息全面整合', 'green'),
                                ('event', '一事一档', '事件追踪与分析', 'orange'),
                                ('place', '一地一档', '地理位置信息管理', 'red'),
                                ('inventory', '一物一档', '物品资产档案记录', 'purple'),
                                ('hub', '一情一档', '舆情的发现、追踪', 'pink')
                            ]
                            
                            for icon, title, desc, color in archive_features:
                                with ui.row().classes('items-center gap-2 p-2 rounded hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors'):
                                    ui.icon(icon).classes(f'text-3xl text-{color}-600 dark:text-{color}-400')
                                    with ui.column().classes('flex-1 gap-0'):
                                        ui.label(title).classes('text-base font-semibold text-gray-800 dark:text-white')
                                        ui.label(desc).classes('text-sm text-gray-500 dark:text-gray-400')
            
            # 2. AI 文档管理
            with ui.card().classes('w-full p-2 hover:shadow-xl transition-shadow duration-300 border-l-4 border-green-500'):
                with ui.row().classes('items-start gap-2'):
                    with ui.avatar().classes('w-14 h-14 bg-gradient-to-br from-green-400 to-green-600'):
                        ui.icon('description').classes('text-3xl text-white')
                    
                    with ui.column().classes('flex-1 gap-2'):
                        ui.label('AI 文档管理').classes('text-xl font-bold text-gray-800 dark:text-white')                        
                        ui.label('利用 AI 技术自动处理和分析各类文档,实现智能化文档管理').classes('text-sm text-gray-600 dark:text-gray-300 mb-3')
                        
                        # 核心能力
                        with ui.row().classes('gap-2 w-full'):
                            with ui.column().classes('flex-1 gap-2'):
                                ui.label('核心能力').classes('text-base font-semibold text-gray-700 dark:text-gray-300 mb-1')
                                
                                capabilities = [
                                    ('auto_fix_high', '多格式转文本'),
                                    ('psychology', '智能实体抽取'),
                                    ('insights', '关系图谱构建'),
                                    ('smart_toy', '语义理解分析'),
                                ]
                                
                                for icon, text in capabilities:
                                    with ui.row().classes('items-center gap-2'):
                                        ui.icon(icon).classes('text-3xl text-green-600 dark:text-green-400')
                                        ui.label(text).classes('text-sm text-gray-700 dark:text-gray-300')
                            
                            with ui.column().classes('flex-1 gap-2'):
                                ui.label('支持格式').classes('text-base font-semibold text-gray-700 dark:text-gray-300 mb-1')
                                
                                formats = [
                                    ('PDF', 'picture_as_pdf'),
                                    ('Word', 'article'),
                                    ('Excel', 'table_chart'),
                                    ('图片', 'image'),
                                ]
                                
                                for text, icon in formats:
                                    with ui.row().classes('items-center gap-2'):
                                        ui.icon(icon).classes('text-3xl text-blue-600 dark:text-blue-400')
                                        ui.label(text).classes('text-sm text-gray-700 dark:text-gray-300')
            
            # 3. MCP 管理
            with ui.card().classes('w-full p-2 hover:shadow-xl transition-shadow duration-300 border-l-4 border-orange-500'):
                with ui.row().classes('items-start gap-2'):
                    with ui.avatar().classes('w-14 h-14 bg-gradient-to-br from-orange-400 to-orange-600'):
                        ui.icon('hub').classes('text-3xl text-white')
                    
                    with ui.column().classes('flex-1 gap-2'):
                        ui.label('MCP 服务管理').classes('text-xl font-bold text-gray-800 dark:text-white')                        
                        ui.label('集中管理和调度各类 MCP 服务,提供统一的模型上下文协议接入').classes('text-sm text-gray-600 dark:text-gray-300 mb-3')
                        
                        # 特性展示
                        with ui.row().classes('gap-2 flex-wrap'):
                            mcp_features = [
                                ('统一接入', 'integration_instructions'),
                                ('服务编排', 'account_tree'),
                                ('状态监控', 'monitor_heart'),
                                ('版本管理', 'manage_history'),
                                ('性能优化', 'speed'),
                                ('安全控制', 'security'),
                            ]
                            
                            for label, icon in mcp_features:
                                with ui.row().classes('items-center gap-1.5 px-3 py-2 bg-orange-50 dark:bg-orange-900/20 rounded-full border border-orange-200 dark:border-orange-700'):
                                    ui.icon(icon).classes('text-2xl text-orange-600 dark:text-orange-400')
                                    ui.label(label).classes('text-sm font-medium text-orange-800 dark:text-orange-200')
        
        # ==================== 右侧:外部应用链接 ====================
        with ui.column().classes('flex-1 min-w-[400px] gap-2'):
            
            # 右侧标题卡片
            with ui.card().classes('w-full p-2 bg-gradient-to-br from-emerald-500 to-emerald-600 text-white shadow-lg'):
                with ui.row().classes('items-center gap-3'):
                    ui.icon('language').classes('text-4xl')
                    with ui.column().classes('gap-1'):
                        ui.label('外部应用中心').classes('text-xl font-bold')
                        ui.label('External Applications Hub').classes('text-sm opacity-90')
            
            # 应用卡片列表
            external_apps = [
                {
                    'name': '公文写作助手',
                    'name_en': 'Official Document Writer',
                    'description': '基于提示词模板的智能公文写作工具,支持多种公文格式自动生成',
                    'icon': 'edit_document',
                    'color': 'blue',
                    'url': '#',  # 替换为实际URL
                    'features': [
                        '模板库管理',
                        '智能纠错',
                        '格式规范',
                        '批量生成'
                    ],
                    'tags': ['文档处理', 'AI辅助', '效率工具']
                },
                {
                    'name': 'AI 教育平台',
                    'name_en': 'AI Education Platform',
                    'description': '面向教育场景的 AI 应用平台,提供个性化学习和智能辅导服务',
                    'icon': 'school',
                    'color': 'indigo',
                    'url': '#',  # 替换为实际URL
                    'features': [
                        '个性化学习',
                        '智能题库',
                        '学情分析',
                        '作业批改'
                    ],
                    'tags': ['在线教育', '智能辅导', '学习分析']
                },
                {
                    'name': 'AI 工作流引擎',
                    'name_en': 'AI Workflow Engine',
                    'description': '低代码 AI 工作流平台,通过可视化编排实现复杂业务流程自动化',
                    'icon': 'settings_suggest',
                    'color': 'purple',
                    'url': '#',  # 替换为实际URL
                    'features': [
                        '可视化编排',
                        '节点库扩展',
                        '流程监控',
                        '版本管理'
                    ],
                    'tags': ['流程自动化', '低代码', '企业应用']
                },
            ]
            
            # 渲染每个应用卡片
            for app in external_apps:
                with ui.card().classes(f'w-full p-2 hover:shadow-xl transition-all duration-300 border-l-4 border-{app["color"]}-500 cursor-pointer').on('click', lambda url=app['url']: ui.open(url, new_tab=True)):
                    
                    # 应用头部
                    with ui.row().classes('items-start gap-2'):
                        with ui.avatar().classes(f'w-12 h-12 bg-gradient-to-br from-{app["color"]}-400 to-{app["color"]}-600'):
                            ui.icon(app['icon']).classes('text-2xl text-white')
                        
                        with ui.column().classes('flex-1 gap-1'):
                            ui.label(app['name']).classes('text-lg font-bold text-gray-800 dark:text-white')
                            # ui.label(app['name_en']).classes('text-xs text-gray-500 dark:text-gray-400')
                            # 应用描述
                            ui.label(app['description']).classes('text-sm text-gray-600 dark:text-gray-300 mb-3 leading-relaxed')
                            
                    # 核心功能
                    with ui.column().classes('gap-2 mb-2'):
                        ui.label('核心功能').classes('text-base font-semibold text-gray-700 dark:text-gray-300 mb-1')
                        with ui.row().classes('gap-2 flex-wrap'):
                            for feature in app['features']:
                                ui.chip(feature, icon='check_circle').classes(f'bg-{app["color"]}-50 text-{app["color"]}-800 dark:bg-{app["color"]}-900/30 dark:text-{app["color"]}-200 text-sm')
                    
                    # 标签和访问按钮
                    with ui.row().classes('items-center justify-between w-full pt-1 border-t border-gray-300 dark:border-gray-700'):
                        with ui.row().classes('gap-1.5 flex-wrap'):
                            ui.label("标签：")
                            for tag in app['tags']:
                                ui.badge(tag).classes('bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300 text-sm px-2 py-1')
                
                        with ui.row().classes('pt-2 border-t border-gray-200 dark:border-gray-700 gap-2'):   
                            ui.button('编辑', icon='edit').classes(f'bg-{app["color"]}-600 hover:bg-{app["color"]}-700 text-white py-2 rounded').props('flat')
                            ui.button('访问应用',icon='open_in_new').classes(f'bg-{app["color"]}-600 hover:bg-{app["color"]}-700 text-white py-2 rounded').props('flat')
        
            # 底部提示卡片
            with ui.card().classes('w-full p-2 bg-gradient-to-r from-gray-50 to-gray-100 dark:from-gray-800 dark:to-gray-700 border border-gray-200 dark:border-gray-600 mt-2'):
                with ui.row().classes('items-center gap-2'):
                    ui.icon('info').classes('text-2xl text-blue-600 dark:text-blue-400')
                    with ui.column().classes('flex-1 gap-1'):
                        ui.label('需要更多应用?').classes('text-sm font-semibold text-gray-800 dark:text-white')
                        ui.label('点击下方按钮提交需求或联系管理员添加新应用').classes('text-xs text-gray-600 dark:text-gray-300')
                    
                    ui.button('提交需求', icon='add_circle').classes('bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded').props('flat')
    
    log_info("首页内容加载完成")
