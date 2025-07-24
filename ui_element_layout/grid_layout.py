from nicegui import ui

# 定义通用样式，用于所有方块
# w-20 h-20: 设置宽度和高度
# text-2xl: 设置字体大小
# font-bold: 设置字体加粗
# flex items-center justify-center: 使数字在方块内水平和垂直居中
common_style = 'text-2xl font-bold flex items-center justify-center'

def create_grid_layout_content():
    # 顶部的 "foo" 标签
    ui.label('foo').classes('text-2xl font-bold')
    # 创建一个3列的网格布局
    # 使用 with 上下文管理器，在其内部创建的所有元素都将成为网格的子项
    with ui.grid(columns=3).classes('gap-2 w-full h-full').style(" grid-template-columns: 200px 1fr 2fr;"): # gap-2 用于设置方块之间的间距
        # 第1行
        ui.label('1').classes(f'{common_style} bg-red-500 text-white')
        ui.label('2').classes(f'{common_style} bg-orange-500 text-white')
        ui.label('3').classes(f'{common_style} bg-green-500 text-white')
        
        # 第2行
        ui.label('4').classes(f'{common_style} bg-blue-600 text-white')
        ui.label('5').classes(f'{common_style} bg-purple-500 text-white')
        ui.label('6').classes(f'{common_style} bg-orange-200 text-black')
        
        # 第3行
        ui.label('7').classes(f'{common_style} bg-gray-400 text-black')
        ui.label('8').classes(f'{common_style} bg-lime-200 text-black')
        ui.label('9').classes(f'{common_style} bg-cyan-400 text-black')

    # 底部的 "bar" 标签
    ui.label('bar').classes('text-2xl font-bold')
