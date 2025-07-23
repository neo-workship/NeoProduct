
from nicegui import ui

def create_setting_content():
    with ui.row().classes('flex h-screen w-full bg-gray-100 gap-2 p-2'):
    
        # 左侧大容器 - 使用卡片组件
        with ui.card().classes('flex-1'):
            ui.label('左侧主要内容区域').classes('text-xl font-bold text-gray-700 mb-4')
            
            # 使用容器组件代替div
            with ui.column().classes('gap-4'):
                ui.markdown('''
                ### 主要内容区域
                这是页面的主要内容区域，占据了大部分空间。''')
        
        # 右侧容器 - 使用列布局
        with ui.column().classes('w-80 gap-2'):
            
            # 右上角容器 - 使用卡片组件
            with ui.card().classes('flex-1'):
                ui.label('右上区域').classes('text-lg font-semibold text-gray-700 mb-2')
                
                with ui.column().classes('gap-2'):
                    ui.markdown('''
                    **侧边栏上部**
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