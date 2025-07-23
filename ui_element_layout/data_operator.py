#!/usr/bin/env python3

from nicegui import ui

def create_data_operator_content():
    """创建NiceGUI弹性盒子布局演示页面"""
    
    # 页面标题和说明
    ui.markdown('# NiceGUI 弹性盒子布局演示')
    ui.markdown('**NiceGUI基于Quasar框架，布局组件默认使用CSS flexbox**')
    
    # 示例1: 基础行布局 (flex-direction: row)
    ui.markdown('## 1. 基础行布局 (ui.row)')
    ui.markdown('`ui.row()` 创建水平方向的弹性容器，等价于 `flex-direction: row`')
    
    with ui.row().classes('bg-blue-100 p-4 gap-4 w-full justify-around'):
        ui.button('按钮1').classes('bg-blue-500 text-white px-4 py-2')
        ui.button('按钮2').classes('bg-green-500 text-white px-4 py-2')
        ui.button('按钮3').classes('bg-red-500 text-white px-4 py-2')
    
    # 示例2: 基础列布局 (flex-direction: column)
    ui.markdown('## 2. 基础列布局 (ui.column)')
    ui.markdown('`ui.column()` 创建垂直方向的弹性容器，等价于 `flex-direction: column`')
    
    with ui.column().classes('bg-green-100 p-4 gap-4 w-64'):
        ui.button('按钮A').classes('bg-purple-500 text-white px-4 py-2')
        ui.button('按钮B').classes('bg-orange-500 text-white px-4 py-2')
        ui.button('按钮C').classes('bg-teal-500 text-white px-4 py-2')
    
    # 示例3: 弹性项目大小控制 (flex-basis, flex-grow, flex-shrink)
    ui.markdown('## 3. 弹性项目大小控制')
    ui.markdown('使用Tailwind的flex工具类控制项目的弹性行为')
    
    with ui.row(wrap=False).classes('bg-yellow-100 p-4 gap-2 w-full'):
        with ui.card().classes('basis-1/4 bg-indigo-200 p-4'):
            ui.label('basis-1/4')
            ui.markdown('占据1/4宽度')
        
        with ui.card().classes('basis-1/2 bg-pink-200 p-4'):
            ui.label('basis-1/2')
            ui.markdown('占据1/2宽度')
        
        with ui.card().classes('basis-1/4 bg-cyan-200 p-4'):
            ui.label('basis-1/4')
            ui.markdown('占据1/4宽度')
    
    # 示例4: 对齐控制 (justify-content, align-items)
    ui.markdown('## 4. 弹性盒子对齐控制')
    ui.markdown('使用Tailwind的justify和items类控制主轴和交叉轴对齐')
    
    # 主轴对齐示例
    ui.markdown('### 主轴对齐 (justify-content)')
    with ui.row().classes('bg-gray-100 p-4 h-20 justify-center items-center border-2 border-dashed'):
        ui.chip('justify-center', color='primary')
    
    with ui.row().classes('bg-gray-100 p-4 h-20 justify-between items-center mt-2 border-2 border-dashed'):
        ui.chip('左', color='positive')
        ui.chip('justify-between', color='primary')
        ui.chip('右', color='negative')
    
    with ui.row().classes('bg-gray-100 p-4 h-20 justify-around items-center mt-2 border-2 border-dashed'):
        ui.chip('A', color='accent')
        ui.chip('justify-around', color='primary')
        ui.chip('B', color='warning')
    
    # 交叉轴对齐示例
    ui.markdown('### 交叉轴对齐 (align-items)')
    with ui.row().classes('bg-gray-200 p-4 h-32 justify-center items-start border-2 border-dashed'):
        ui.chip('items-start', color='primary')
    
    with ui.row().classes('bg-gray-200 p-4 h-32 justify-center items-center mt-2 border-2 border-dashed'):
        ui.chip('items-center', color='primary')
    
    with ui.row().classes('bg-gray-200 p-4 h-32 justify-center items-end mt-2 border-2 border-dashed'):
        ui.chip('items-end', color='primary')
    
    # 示例5: 嵌套布局
    ui.markdown('## 5. 嵌套弹性布局')
    ui.markdown('行和列可以相互嵌套，创建复杂的弹性布局')
    
    with ui.row().classes('bg-slate-100 p-4 gap-4 w-full'):
        # 左侧导航列
        with ui.column().classes('basis-1/4 bg-blue-50 p-4 rounded'):
            ui.label('侧边栏').classes('font-bold text-lg')
            with ui.column().classes('gap-2 mt-4'):
                ui.button('导航1').classes('w-full justify-start')
                ui.button('导航2').classes('w-full justify-start')
                ui.button('导航3').classes('w-full justify-start')
        
        # 右侧内容区
        with ui.column().classes('basis-3/4 bg-white p-4 rounded shadow'):
            ui.label('主内容区').classes('font-bold text-lg')
            
            # 内容区的水平布局
            with ui.row().classes('gap-4 mt-4'):
                with ui.card().classes('flex-1 p-4'):
                    ui.label('卡片1').classes('font-semibold')
                    ui.markdown('这是一个弹性卡片，会自动伸缩')
                
                with ui.card().classes('flex-1 p-4'):
                    ui.label('卡片2').classes('font-semibold')
                    ui.markdown('这也是一个弹性卡片')
                
                with ui.card().classes('flex-1 p-4'):
                    ui.label('卡片3').classes('font-semibold')
                    ui.markdown('三个卡片等宽分布')
    
    # 示例6: 响应式弹性布局
    ui.markdown('## 6. 响应式弹性布局')
    ui.markdown('结合Tailwind的响应式前缀，创建适应不同屏幕尺寸的布局')
    
    with ui.row().classes('bg-gradient-to-r from-purple-100 to-pink-100 p-4 gap-4 flex-col md:flex-row w-full'):
        with ui.card().classes('w-full md:w-1/3 p-4 bg-white shadow-lg'):
            ui.label('响应式卡片1').classes('font-bold')
            ui.markdown('在小屏幕上垂直堆叠，大屏幕上水平排列')
        
        with ui.card().classes('w-full md:w-1/3 p-4 bg-white shadow-lg'):
            ui.label('响应式卡片2').classes('font-bold')
            ui.markdown('使用 `flex-col md:flex-row` 实现响应式')
        
        with ui.card().classes('w-full md:w-1/3 p-4 bg-white shadow-lg'):
            ui.label('响应式卡片3').classes('font-bold')
            ui.markdown('`w-full md:w-1/3` 控制响应式宽度')
    
    # 示例7: 弹性增长和收缩
    ui.markdown('## 7. 弹性增长和收缩')
    ui.markdown('演示flex-grow、flex-shrink和flex属性的使用')
    
    with ui.row().classes('bg-amber-100 p-4 gap-2 w-full'):
        with ui.card().classes('flex-none w-32 bg-red-200 p-4'):
            ui.label('固定宽度')
            ui.markdown('flex-none')
        
        with ui.card().classes('flex-1 bg-green-200 p-4'):
            ui.label('弹性增长')
            ui.markdown('flex-1 (flex-grow: 1)')
        
        with ui.card().classes('flex-2 bg-blue-200 p-4'):
            ui.label('2倍增长')
            ui.markdown('flex-2 (flex-grow: 2)')
    
    # 示例8: 包装控制
    ui.markdown('## 8. 弹性包装控制')
    ui.markdown('控制弹性项目是否换行 (flex-wrap)')
    
    ui.markdown('### 不换行 (flex-nowrap)')
    with ui.row(wrap=False).classes('bg-red-100 p-4 gap-2 w-80 overflow-x-auto'):
        for i in range(6):
            ui.button(f'按钮{i+1}').classes('flex-none bg-red-500 text-white px-4 py-2')
    
    ui.markdown('### 换行 (flex-wrap) - NiceGUI默认行为')
    with ui.row(wrap=True).classes('bg-green-100 p-4 gap-2 w-80'):
        for i in range(6):
            ui.button(f'按钮{i+1}').classes('flex-none bg-green-500 text-white px-4 py-2')
    
    # 总结说明
    ui.markdown('## 总结')
    ui.markdown('''
    **NiceGUI的弹性盒子特性：**
    
    - `ui.row()`: 创建水平弹性容器 (flex-direction: row)
    - `ui.column()`: 创建垂直弹性容器 (flex-direction: column) 
    - `ui.card()`: 可作为弹性项目使用
    - 默认支持换行 (wrap=True)，可通过参数控制
    - 完全兼容Tailwind CSS的flex工具类
    - 基于Quasar框架的弹性布局系统
    
    **常用Tailwind弹性类：**
    - 大小控制: `basis-1/4`, `flex-1`, `flex-none`
    - 对齐控制: `justify-center`, `items-center`, `justify-between`
    - 方向控制: `flex-row`, `flex-col`, `flex-row-reverse`
    - 包装控制: `flex-wrap`, `flex-nowrap`
    - 响应式: `md:flex-row`, `lg:basis-1/3`
    ''')