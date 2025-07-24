#!/usr/bin/env python3

from nicegui import ui

def create_data_sync_content():
    create_flexbox_demo()

def create_container_item(items, container_classes, description, container_height="h-24"):
    """创建一个弹性容器演示项目"""
    with ui.column().classes('mb-6').classes('w-full'):
        # 说明文字
        ui.label(description).classes('font-semibold text-blue-700 mb-2')
        ui.code(f'classes="{container_classes}"').classes('text-sm bg-gray-100 p-1 rounded mb-2')
        
        # 演示容器
        with ui.row().classes(f'{container_classes} {container_height} w-full bg-gray-100 border-2 border-dashed border-gray-400 p-2'):
            for i, (text, color) in enumerate(items):
                ui.button(text=text,color=color).classes(f'{color} text-white px-3 py-1 text-sm')

def create_item_demo(items_with_classes, container_class, description):
    """创建一个弹性元素属性演示项目"""
    with ui.column().classes('mb-6'):
        # 说明文字
        ui.label(description).classes('font-semibold text-green-700 mb-2')
        
        # 演示容器
        with ui.row().classes(f'w-full {container_class} h-26 bg-gray-100 border-2 border-dashed border-gray-400 p-2'):
            for text, item_class, color in items_with_classes:
                ui.button(text).classes(f'{item_class} {color} text-white px-3 py-1 text-sm')
                # 显示当前项目的类名
                
        # 显示各项目的类名
        item_descriptions = [f'{text}: {item_class}' for text, item_class, _ in items_with_classes]
        ui.markdown(f"**项目类:** {' | '.join(item_descriptions)}").classes('text-sm text-gray-600 mt-1')

def create_flexbox_demo():
    """创建完整的弹性盒子属性演示"""
    
    # 页面标题
    ui.markdown('# NiceGUI 弹性容器与元素属性完整演示')
    ui.markdown('**详细展示CSS Flexbox所有属性值的布局效果**')
    
    # ========== 弹性容器属性演示 ==========
    ui.markdown('## 一、弹性容器属性 (Flex Container Properties)')
    
    # 1. flex-direction 属性
    ui.markdown('### 1. flex-direction - 主轴方向')
    
    items = [('Item 1', 'bg-red-500'), ('Item 2', 'bg-blue-500'), ('Item 3', 'bg-green-700')]
    
    create_container_item(items, 'flex flex-row', 'flex-direction: row (默认) - 水平方向，从左到右')
    create_container_item(items, 'flex flex-row-reverse', 'flex-direction: row-reverse - 水平方向，从右到左')
    create_container_item(items, 'flex flex-col w-64', 'flex-direction: column - 垂直方向，从上到下', 'h-32')
    create_container_item(items, 'flex flex-col-reverse w-64', 'flex-direction: column-reverse - 垂直方向，从下到上', 'h-32')
    
    # 2. flex-wrap 属性
    ui.markdown('### 2. flex-wrap - 换行控制')
    
    many_items = [(f'Item {i+1}', f'bg-purple-{500 + (i%3)*100}') for i in range(8)]
    
    with ui.column().classes('mb-6'):
        ui.label('flex-wrap: nowrap (默认) - 不换行，可能溢出').classes('font-semibold text-blue-700 mb-2')
        ui.code('classes="flex flex-nowrap"').classes('text-sm bg-gray-100 p-1 rounded mb-2')
        with ui.row().classes('flex flex-nowrap w-196 bg-gray-100 border-2 border-dashed border-gray-400 p-2 overflow-x-auto'):
            for text, color in many_items:
                ui.button(text=text,color=color).classes(f'{color} text-white px-3 py-1 text-sm flex-none')
    
    with ui.column().classes('mb-6'):
        ui.label('flex-wrap: wrap - 允许换行').classes('font-semibold text-blue-700 mb-2')
        ui.code('classes="flex flex-wrap w-96"').classes('text-sm bg-gray-100 p-1 rounded mb-2')
        with ui.row().classes('flex flex-wrap w-96 bg-gray-100 border-2 border-dashed border-gray-400 p-2'):
            for text, color in many_items:
                ui.button(text=text,color=color).classes(f'{color} text-white px-3 py-1 text-sm')
    
    with ui.column().classes('mb-6'):
        ui.label('flex-wrap: wrap-reverse - 反向换行').classes('font-semibold text-blue-700 mb-2')
        ui.code('classes="flex flex-wrap-reverse w-96"').classes('text-sm bg-gray-100 p-1 rounded mb-2')
        with ui.row().classes('flex flex-wrap-reverse w-96 bg-gray-100 border-2 border-dashed border-gray-400 p-2'):
            for text, color in many_items:
                ui.button(text=text,color=color).classes(f'{color} text-white px-3 py-1 text-sm')
    
    # 3. justify-content 属性
    ui.markdown('### 3. justify-content - 主轴对齐')
    
    create_container_item(items, 'flex justify-start', 'justify-content: flex-start (默认) - 主轴起点对齐')
    create_container_item(items, 'flex justify-end', 'justify-content: flex-end - 主轴终点对齐')
    create_container_item(items, 'flex justify-center', 'justify-content: center - 主轴居中对齐')
    create_container_item(items, 'flex justify-between', 'justify-content: space-between - 两端对齐，项目间等距')
    create_container_item(items, 'flex justify-around', 'justify-content: space-around - 项目周围等距')
    create_container_item(items, 'flex justify-evenly', 'justify-content: space-evenly - 项目间距离相等')
    
    # 4. align-items 属性
    ui.markdown('### 4. align-items - 交叉轴对齐')
    
    varied_items = [('Short', 'bg-red-500'), ('Medium Text', 'bg-blue-500'), ('Very Long Text Content', 'bg-green-500')]
    
    create_container_item(varied_items, 'flex items-stretch', 'align-items: stretch (默认) - 拉伸填满容器')
    create_container_item(varied_items, 'flex items-start', 'align-items: flex-start - 交叉轴起点对齐')
    create_container_item(varied_items, 'flex items-end', 'align-items: flex-end - 交叉轴终点对齐')
    create_container_item(varied_items, 'flex items-center', 'align-items: center - 交叉轴居中对齐')
    create_container_item(varied_items, 'flex items-baseline', 'align-items: baseline - 基线对齐')
    
    # 5. align-content 属性（多行时有效）
    ui.markdown('### 5. align-content - 多行交叉轴对齐')
    
    with ui.column().classes('mb-6'):
        ui.label('align-content: flex-start - 多行起点对齐').classes('font-semibold text-blue-700 mb-2')
        ui.code('classes="flex flex-wrap content-start w-64 h-32"').classes('text-sm bg-gray-100 p-1 rounded mb-2')
        with ui.row().classes('flex flex-wrap content-start w-64 h-32 bg-gray-100 border-2 border-dashed border-gray-400 p-2'):
            for i in range(6):
                ui.button(f'Item {i+1}').classes(f'bg-indigo-{400 + (i%3)*100} text-white px-3 py-1 text-sm')
    
    with ui.column().classes('mb-6'):
        ui.label('align-content: center - 多行居中对齐').classes('font-semibold text-blue-700 mb-2')
        ui.code('classes="flex flex-wrap content-center w-64 h-32"').classes('text-sm bg-gray-100 p-1 rounded mb-2')
        with ui.row().classes('flex flex-wrap content-center w-64 h-32 bg-gray-100 border-2 border-dashed border-gray-400 p-2'):
            for i in range(6):
                ui.button(f'Item {i+1}').classes(f'bg-teal-{400 + (i%3)*100} text-white px-3 py-1 text-sm')
    
    with ui.column().classes('mb-6'):
        ui.label('align-content: space-between - 多行两端对齐').classes('font-semibold text-blue-700 mb-2')
        ui.code('classes="flex flex-wrap content-between w-64 h-32"').classes('text-sm bg-gray-100 p-1 rounded mb-2')
        with ui.row().classes('flex flex-wrap content-between w-64 h-32 bg-gray-100 border-2 border-dashed border-gray-400 p-2'):
            for i in range(6):
                ui.button(f'Item {i+1}').classes(f'bg-orange-{400 + (i%3)*100} text-white px-3 py-1 text-sm')
    
    # 6. gap 属性
    ui.markdown('### 6. gap - 项目间距')
    
    create_container_item(items, 'flex gap-0', 'gap: 0 - 无间距')
    create_container_item(items, 'flex gap-2', 'gap: 0.5rem - 小间距')
    create_container_item(items, 'flex gap-4', 'gap: 1rem - 中等间距')
    create_container_item(items, 'flex gap-8', 'gap: 2rem - 大间距')
    
    # ========== 弹性元素属性演示 ==========
    ui.markdown('## 二、弹性元素属性 (Flex Item Properties)')
    
    # 1. flex-grow 属性
    ui.markdown('### 1. flex-grow - 增长因子')
    
    create_item_demo([
        ('Normal', '', 'bg-gray-500'),
        ('Grow 1', 'flex-grow', 'bg-blue-500'),
        ('Normal', '', 'bg-gray-500')
    ], 'flex w-96', 'flex-grow: 1 - 中间项目占据剩余空间')
    
    create_item_demo([
        ('Grow 1', 'flex-grow', 'bg-blue-500'),
        ('Grow 2', 'flex-grow-2', 'bg-red-500'),
        ('Grow 1', 'flex-grow', 'bg-green-500')
    ], 'flex w-96', 'flex-grow: 不同增长比例 (1:2:1)')
    
    # 2. flex-shrink 属性
    ui.markdown('### 2. flex-shrink - 收缩因子')
    
    create_item_demo([
        ('Shrink 0', 'flex-shrink-0', 'bg-red-500'),
        ('Normal', '', 'bg-blue-500'),
        ('Normal', '', 'bg-green-500')
    ], 'flex w-96', 'flex-shrink: 0 - 第一项不收缩，保持宽度')
    
    create_item_demo([
        ('Normal', '', 'bg-blue-500'),
        ('Shrink 2', 'flex-shrink-2', 'bg-red-500'),
        ('Normal', '', 'bg-green-500')
    ], 'flex w-96', 'flex-shrink: 2 - 中间项收缩2倍')
    
    # 3. flex-basis 属性
    ui.markdown('### 3. flex-basis - 基础尺寸')
    
    create_item_demo([
        ('Basis 1/4', 'basis-1/4', 'bg-red-500'),
        ('Basis 1/2', 'basis-1/2', 'bg-blue-500'),
        ('Basis 1/4', 'basis-1/4', 'bg-green-500')
    ], 'flex w-96', 'flex-basis: 分数值 (1/4, 1/2, 1/4)')
    
    create_item_demo([
        ('Auto', 'basis-auto', 'bg-purple-500'),
        ('100px', 'basis-24', 'bg-indigo-500'),
        ('Auto', 'basis-auto', 'bg-teal-500')
    ], 'flex w-96', 'flex-basis: 固定值和auto')
    
    # 4. flex 复合属性
    ui.markdown('### 4. flex - 复合属性 (grow shrink basis)')
    
    create_item_demo([
        ('flex-none', 'flex-none', 'bg-red-500'),
        ('flex-1', 'flex-1', 'bg-blue-500'),
        ('flex-none', 'flex-none', 'bg-green-500')
    ], 'flex w-96', 'flex: none(0 0 auto) vs flex: 1(1 1 0%)')
    
    create_item_demo([
        ('flex-auto', 'flex-auto', 'bg-orange-500'),
        ('flex-initial', 'flex-initial', 'bg-purple-500'),
        ('flex-auto', 'flex-auto', 'bg-teal-500')
    ], 'flex w-96', 'flex: auto(1 1 auto) vs flex: initial(0 1 auto)')
    
    # 5. align-self 属性
    ui.markdown('### 5. align-self - 个别项目的交叉轴对齐')
    
    create_item_demo([
        ('Normal', '', 'bg-gray-500'),
        ('Self Start', 'self-start', 'bg-red-500'),
        ('Self Center', 'self-center', 'bg-blue-500'),
        ('Self End', 'self-end', 'bg-green-500')
    ], 'flex items-stretch h-20', 'align-self: 覆盖容器的align-items设置')
    
    create_item_demo([
        ('Self Auto', 'self-auto', 'bg-purple-500'),
        ('Self Stretch', 'self-stretch', 'bg-indigo-500'),
        ('Self Baseline', 'self-baseline', 'bg-teal-500')
    ], 'flex items-center h-20', 'align-self: auto, stretch, baseline')
    
    # 6. order 属性
    ui.markdown('### 6. order - 显示顺序')
    
    create_item_demo([
        ('Order 3', 'order-3', 'bg-red-500'),
        ('Order 1', 'order-1', 'bg-blue-500'),
        ('Order 2', 'order-2', 'bg-green-500'),
        ('Order 0', 'order-none', 'bg-purple-500')
    ], 'flex w-96', 'order: 改变显示顺序 (实际顺序: 3,1,2,0 → 显示顺序: 0,1,2,3)')
    
    # 综合示例
    ui.markdown('## 三、综合应用示例')
    
    with ui.column().classes('mb-6'):
        ui.label('综合布局: 导航栏布局').classes('font-semibold text-purple-700 mb-2')
        with ui.row().classes('flex justify-between items-center w-full bg-blue-600 text-white p-4'):
            ui.label('Logo').classes('flex-none font-bold text-lg')
            
            with ui.row().classes('flex-1 justify-center gap-4'):
                ui.button('首页').classes('bg-transparent hover:bg-blue-700 px-3 py-1')
                ui.button('产品').classes('bg-transparent hover:bg-blue-700 px-3 py-1')
                ui.button('服务').classes('bg-transparent hover:bg-blue-700 px-3 py-1')
            
            ui.button('登录').classes('flex-none bg-blue-500 hover:bg-blue-400 px-4 py-1 rounded')
    
    with ui.column().classes('mb-6'):
        ui.label('综合布局: 卡片网格').classes('font-semibold text-purple-700 mb-2')
        with ui.row().classes('flex flex-wrap gap-4 justify-center'):
            for i in range(6):
                with ui.card().classes('flex-none w-32 h-32 p-4 bg-gradient-to-br from-blue-400 to-purple-500 text-white'):
                    ui.label(f'卡片 {i+1}').classes('font-semibold')
                    ui.label('内容描述').classes('text-sm mt-2')
    
    # 总结
    ui.markdown('## 总结')
    ui.markdown('''
    ### 弹性容器属性 (设置在父元素上):
    - **flex-direction**: 控制主轴方向 (row, column, row-reverse, column-reverse)  
    - **flex-wrap**: 控制换行 (nowrap, wrap, wrap-reverse)
    - **justify-content**: 主轴对齐 (start, end, center, between, around, evenly)
    - **align-items**: 交叉轴对齐 (stretch, start, end, center, baseline)
    - **align-content**: 多行交叉轴对齐 (start, end, center, between, around, stretch)
    - **gap**: 项目间距
    
    ### 弹性元素属性 (设置在子元素上):
    - **flex-grow**: 增长因子，分配剩余空间
    - **flex-shrink**: 收缩因子，空间不足时收缩比例  
    - **flex-basis**: 基础尺寸，分配多余空间前的默认尺寸
    - **flex**: 复合属性 (grow shrink basis)
    - **align-self**: 单独设置交叉轴对齐
    - **order**: 改变显示顺序
    
    **在NiceGUI中使用时，通过 `.classes()` 方法添加对应的Tailwind CSS类名即可实现这些效果。**
    ''')
