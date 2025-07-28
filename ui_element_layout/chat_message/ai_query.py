from nicegui import ui

def create_ai_query_content():
    
    # 设置页面标题和样式
    ui.page_title('NiceGUI 弹性盒子布局演示')

    # 添加简单的全局样式
    ui.add_head_html('''
    <style>
        body {
            font-family: system-ui, -apple-system, sans-serif;
        }
    </style>
    ''')

    # 页面标题
    ui.markdown('# NiceGUI 弹性盒子布局演示')
    ui.separator()

    # ===== 弹性容器属性演示 =====
    ui.markdown('## 一、弹性容器属性演示')

    # 1. flex-direction 演示
    ui.markdown('### 1. flex-direction (主轴方向)')

    with ui.card():
        ui.markdown('**flex-direction: row (默认-水平) | tailwind class(flex-row)**')
        with ui.row().classes('w-full p-4 border-2 border-dashed border-blue-400 bg-blue-50 min-h-24').style("flex-direction: row"):
            ui.label('项目1').classes('p-3 m-1 rounded bg-red-200 text-center min-h-10 flex items-center justify-center')
            ui.label('项目2').classes('p-3 m-1 rounded bg-green-200 text-center min-h-10 flex items-center justify-center')
            ui.label('项目3').classes('p-3 m-1 rounded bg-blue-200 text-center min-h-10 flex items-center justify-center')
        ui.label('属性值: flex-direction: row').classes('text-sm text-gray-600')

    with ui.card():
        ui.markdown('**flex-direction: column (垂直) | tailwind class(flex-col)**')
        with ui.column().classes('w-full p-4 border-2 border-dashed border-blue-400 bg-blue-50 min-h-48').style("flex-direction: column"):
            ui.label('项目1').classes('p-3 m-1 rounded bg-red-200 text-center min-h-10 flex items-center justify-center')
            ui.label('项目2').classes('p-3 m-1 rounded bg-green-200 text-center min-h-10 flex items-center justify-center')
            ui.label('项目3').classes('p-3 m-1 rounded bg-blue-200 text-center min-h-10 flex items-center justify-center')
        ui.label('属性值: flex-direction: column').classes('text-sm text-gray-600')

    with ui.card():
        ui.markdown('**flex-direction: row-reverse (水平反向) | tailwind class(flex-row-reverse)**')
        with ui.row().classes('w-full p-4 border-2 border-dashed border-blue-400 bg-blue-50 min-h-24').style("flex-direction: row-reverse"):
            ui.label('项目1').classes('p-3 m-1 rounded bg-red-200 text-center min-h-10 flex items-center justify-center')
            ui.label('项目2').classes('p-3 m-1 rounded bg-green-200 text-center min-h-10 flex items-center justify-center')
            ui.label('项目3').classes('p-3 m-1 rounded bg-blue-200 text-center min-h-10 flex items-center justify-center')
        ui.label('属性值: flex-direction: row-reverse').classes('text-sm text-gray-600')

    # 2. justify-content 演示
    ui.markdown('### 2. justify-content (主轴对齐)')

    with ui.card().classes("w-full"):
        ui.markdown('**justify-content: flex-start (默认-起始对齐) | tailwind class(justify-start)**')
        with ui.row().classes('w-full p-4 border-2 border-dashed border-blue-400 bg-blue-50 min-h-24').style("justify-content: flex-start"):
            ui.label('项目1').classes('p-3 m-1 rounded bg-purple-200 text-center min-h-10 flex items-center justify-center')
            ui.label('项目2').classes('p-3 m-1 rounded bg-pink-200 text-center min-h-10 flex items-center justify-center')
            ui.label('项目3').classes('p-3 m-1 rounded bg-yellow-200 text-center min-h-10 flex items-center justify-center')
        ui.label('属性值: justify-content: flex-start').classes('text-sm text-gray-600')

    with ui.card().classes("w-full"):
        ui.markdown('**justify-content: center (居中对齐) | tailwind class(justify-center)**')
        with ui.row().classes('w-full p-4 border-2 border-dashed border-blue-400 bg-blue-50 min-h-24').style("justify-content: center"):
            ui.label('项目1').classes('p-3 m-1 rounded bg-purple-200 text-center min-h-10 flex items-center justify-center')
            ui.label('项目2').classes('p-3 m-1 rounded bg-pink-200 text-center min-h-10 flex items-center justify-center')
            ui.label('项目3').classes('p-3 m-1 rounded bg-yellow-200 text-center min-h-10 flex items-center justify-center')
        ui.label('属性值: justify-content: center').classes('text-sm text-gray-600')

    with ui.card().classes("w-full"):
        ui.markdown('**justify-content: flex-end (末端对齐) | tailwind class(justify-end)**')
        with ui.row().classes('w-full p-4 border-2 border-dashed border-blue-400 bg-blue-50 min-h-24').style("justify-content: flex-end"):
            ui.label('项目1').classes('p-3 m-1 rounded bg-purple-200 text-center min-h-10 flex items-center justify-center')
            ui.label('项目2').classes('p-3 m-1 rounded bg-pink-200 text-center min-h-10 flex items-center justify-center')
            ui.label('项目3').classes('p-3 m-1 rounded bg-yellow-200 text-center min-h-10 flex items-center justify-center')
        ui.label('属性值: justify-content: flex-end').classes('text-sm text-gray-600')

    with ui.card().classes("w-full"):
        ui.markdown('**justify-content: space-between (两端对齐) | tailwind class(justify-between)**')
        with ui.row().classes('w-full p-4 border-2 border-dashed border-blue-400 bg-blue-50 min-h-24').style("justify-content: space-between"):
            ui.label('项目1').classes('p-3 m-1 rounded bg-purple-200 text-center min-h-10 flex items-center justify-center')
            ui.label('项目2').classes('p-3 m-1 rounded bg-pink-200 text-center min-h-10 flex items-center justify-center')
            ui.label('项目3').classes('p-3 m-1 rounded bg-yellow-200 text-center min-h-10 flex items-center justify-center')
        ui.label('属性值: justify-content: space-between').classes('text-sm text-gray-600')

    with ui.card().classes("w-full"):
        ui.markdown('**justify-content: space-around (环绕对齐) | tailwind class(justify-around)**')
        with ui.row().classes('w-full p-4 border-2 border-dashed border-blue-400 bg-blue-50 min-h-24').style("justify-content: space-around"):
            ui.label('项目1').classes('p-3 m-1 rounded bg-purple-200 text-center min-h-10 flex items-center justify-center')
            ui.label('项目2').classes('p-3 m-1 rounded bg-pink-200 text-center min-h-10 flex items-center justify-center')
            ui.label('项目3').classes('p-3 m-1 rounded bg-yellow-200 text-center min-h-10 flex items-center justify-center')
        ui.label('属性值: justify-content: space-around').classes('text-sm text-gray-600')

    with ui.card().classes('w-full'):
        ui.markdown('**justify-content: space-evenly (平均分布) | tailwind class(justify-evenly)**')
        with ui.row().classes('w-full p-4 border-2 border-dashed border-blue-400 bg-blue-50 min-h-24').style("justify-content: space-evenly"):
            ui.label('项目1').classes('p-3 m-1 rounded bg-purple-200 text-center min-h-10 flex items-center justify-center')
            ui.label('项目2').classes('p-3 m-1 rounded bg-pink-200 text-center min-h-10 flex items-center justify-center')
            ui.label('项目3').classes('p-3 m-1 rounded bg-yellow-200 text-center min-h-10 flex items-center justify-center')
        ui.label('属性值: justify-content: space-evenly').classes('text-sm text-gray-600')

    # 3. align-items 演示
    ui.markdown('### 3. align-items (交叉轴对齐)')

    with ui.card():
        ui.markdown('**align-items: stretch (默认-拉伸) | tailwind class(items-stretch)**')
        with ui.row().classes('w-full p-4 border-2 border-dashed border-blue-400 bg-blue-50 h-32').style("align-items: stretch"):
            ui.label('项目1').classes('p-3 m-1 rounded bg-indigo-200 text-center flex items-center justify-center')
            ui.label('项目2').classes('p-3 m-1 rounded bg-teal-200 text-center flex items-center justify-center')
            ui.label('项目3').classes('p-3 m-1 rounded bg-orange-200 text-center flex items-center justify-center')
        ui.label('属性值: align-items: stretch').classes('text-sm text-gray-600')

    with ui.card():
        ui.markdown('**align-items: center (居中) | tailwind class(items-center)**')
        with ui.row().classes('w-full p-4 border-2 border-dashed border-blue-400 bg-blue-50 h-32').style("align-items: center"):
            ui.label('项目1').classes('p-3 m-1 rounded bg-indigo-200 text-center min-h-12 flex items-center justify-center')
            ui.label('项目2').classes('p-3 m-1 rounded bg-teal-200 text-center min-h-12 flex items-center justify-center')
            ui.label('项目3').classes('p-3 m-1 rounded bg-orange-200 text-center min-h-12 flex items-center justify-center')
        ui.label('属性值: align-items: center').classes('text-sm text-gray-600')

    with ui.card():
        ui.markdown('**align-items: flex-start (起始对齐) | tailwind class(items-start)**')
        with ui.row().classes('w-full p-4 border-2 border-dashed border-blue-400 bg-blue-50 h-32').style("align-items: flex-start"):
            ui.label('项目1').classes('p-3 m-1 rounded bg-indigo-200 text-center min-h-12 flex items-center justify-center')
            ui.label('项目2').classes('p-3 m-1 rounded bg-teal-200 text-center min-h-12 flex items-center justify-center')
            ui.label('项目3').classes('p-3 m-1 rounded bg-orange-200 text-center min-h-12 flex items-center justify-center')
        ui.label('属性值: align-items: flex-start').classes('text-sm text-gray-600')

    with ui.card():
        ui.markdown('**align-items: flex-end (末端对齐) | tailwind class(items-end)**')
        with ui.row().classes('w-full p-4 border-2 border-dashed border-blue-400 bg-blue-50 h-32').style("align-items: flex-end"):
            ui.label('项目1').classes('p-3 m-1 rounded bg-indigo-200 text-center min-h-12 flex items-center justify-center')
            ui.label('项目2').classes('p-3 m-1 rounded bg-teal-200 text-center min-h-12 flex items-center justify-center')
            ui.label('项目3').classes('p-3 m-1 rounded bg-orange-200 text-center min-h-12 flex items-center justify-center')
        ui.label('属性值: align-items: flex-end').classes('text-sm text-gray-600')

    with ui.card():
        ui.markdown('**align-items: baseline (基线对齐) | tailwind class(items-baseline)**')
        with ui.row().classes('w-full p-4 border-2 border-dashed border-blue-400 bg-blue-50 h-32').style("align-items: baseline"):
            ui.label('项目1').classes('p-3 m-1 rounded bg-indigo-200 text-center min-h-12 flex items-center justify-center')
            ui.label('项目2').classes('p-3 m-1 rounded bg-teal-200 text-center min-h-12 flex items-center justify-center')
            ui.label('项目3').classes('p-3 m-1 rounded bg-orange-200 text-center min-h-12 flex items-center justify-center')
        ui.label('属性值: align-items: baseline').classes('text-sm text-gray-600')

    # 4. flex-wrap 演示
    ui.markdown('### 4. flex-wrap (换行控制)')

    with ui.card().classes("w-full"):
        ui.markdown('**flex-wrap: nowrap (不换行) | tailwind class(flex-nowrap)**')
        with ui.row(wrap=False).classes('w-196 p-4 border-2 border-dashed border-blue-400 bg-blue-50 min-h-24').classes("flex-wrap: nowrap"):
            ui.label('项目1').classes('p-3 m-1 rounded bg-red-300 w-32 text-center min-h-10 flex items-center justify-center flex-shrink-0')
            ui.label('项目2').classes('p-3 m-1 rounded bg-green-300 w-32 text-center min-h-10 flex items-center justify-center flex-shrink-0')
            ui.label('项目3').classes('p-3 m-1 rounded bg-blue-300 w-32 text-center min-h-10 flex items-center justify-center flex-shrink-0')
            ui.label('项目4').classes('p-3 m-1 rounded bg-purple-300 w-32 text-center min-h-10 flex items-center justify-center flex-shrink-0')
        ui.label('属性值: flex-wrap: nowrap').classes('text-sm text-gray-600')

    with ui.card():
        ui.markdown('**flex-wrap: wrap (换行) | tailwind class(flex-wrap)**')
        with ui.row().classes('w-96 p-4 border-2 border-dashed border-blue-400 bg-blue-50 min-h-24').classes("flex-wrap: wrap"):
            ui.label('项目1').classes('p-3 m-1 rounded bg-red-300 w-32 text-center min-h-10 flex items-center justify-center')
            ui.label('项目2').classes('p-3 m-1 rounded bg-green-300 w-32 text-center min-h-10 flex items-center justify-center')
            ui.label('项目3').classes('p-3 m-1 rounded bg-blue-300 w-32 text-center min-h-10 flex items-center justify-center')
            ui.label('项目4').classes('p-3 m-1 rounded bg-purple-300 w-32 text-center min-h-10 flex items-center justify-center')
        ui.label('属性值: flex-wrap: wrap').classes('text-sm text-gray-600')

    ui.separator()

    # ===== 弹性元素属性演示 =====
    ui.markdown('## 二、弹性元素属性演示')

    # 1. flex-grow 演示
    ui.markdown('### 1. flex-grow (放大比例)')

    with ui.card():
        ui.markdown('**flex-grow: 0 (默认-不放大) | tailwind class(grow-0)**')
        with ui.row().classes('flex w-96 p-4 border-2 border-dashed border-blue-400 bg-blue-50 min-h-24'):
            ui.label('grow-0').classes('p-3 m-1 rounded bg-red-200 text-center ').style("flex-grow: 0")
            ui.label('grow-0').classes('p-3 m-1 rounded bg-green-200 text-center').style("flex-grow: 0")
            ui.label('grow-0').classes('p-3 m-1 rounded bg-blue-200 text-center').style("flex-grow: 0")
        ui.label('属性值: flex-grow: 0').classes('text-sm text-gray-600')

    with ui.card():
        ui.markdown('**flex-grow: 1 (平均分配剩余空间) | tailwind class(grow-1)**')
        with ui.row().classes('flex w-96 p-4 border-2 border-dashed border-blue-400 bg-blue-50'):
            ui.label('grow-1').classes('p-3 m-1 rounded bg-red-200 text-center').style("flex-grow: 1")
            ui.label('grow-1').classes('p-3 m-1 rounded bg-green-200 text-center').style("flex-grow: 1")
            ui.label('grow-1').classes('p-3 m-1 rounded bg-blue-200 text-center').style("flex-grow: 1")
        ui.label('属性值: flex-grow: 1').classes('text-sm text-gray-600')

    with ui.card():
        ui.markdown('**flex-grow: 不同比例 (1:2:1) | tailwind class(grow-x)**')
        with ui.row().classes('flex w-96 p-4 border-2 border-dashed border-blue-400 bg-blue-50 min-h-24'):
            ui.label('grow-1').classes('p-3 m-1 rounded bg-red-200 text-center').style("flex-grow:1")
            ui.label('grow-2').classes('p-3 m-1 rounded bg-green-200 text-center').style("flex-grow:2")
            ui.label('grow-1').classes('p-3 m-1 rounded bg-blue-200 text-center').style("flex-grow:1")
        ui.label('属性值: flex-grow: 1, 2, 1').classes('text-sm text-gray-600')

    # 2. flex-shrink 演示
    ui.markdown('### 2. flex-shrink (缩小比例)')

    # 示例 1：所有项目等比缩小
    with ui.card():
        ui.markdown('**flex-shrink: 1 (默认-等比缩小)**')
        # 添加 flex-nowrap 来阻止换行，从而激活 shrink
        with ui.row().classes('w-80 p-4 border-2 border-dashed border-blue-400 bg-blue-50 min-h-24 flex-nowrap'):
            ui.label('项目1-长文本').classes('p-3 m-1 rounded bg-purple-200 text-center min-h-10 flex items-center justify-center shrink')
            ui.label('项目2-长文本').classes('p-3 m-1 rounded bg-pink-200 text-center min-h-10 flex items-center justify-center shrink')
            ui.label('项目3-长文本').classes('p-3 m-1 rounded bg-orange-200 text-center min-h-10 flex items-center justify-center shrink')
        ui.label('属性值: flex-shrink: 1, 1, 1 (现在会生效)').classes('text-sm text-gray-600')
        ui.label('说明: 添加 flex-nowrap 后，所有项目被强制在同一行。由于空间不足，它们会根据 shrink: 1 的比例进行收缩。').classes('text-xs text-gray-500 mt-2')


    # 示例 2：部分项目不缩小
    with ui.card():
        ui.markdown('**flex-shrink: 0 (不缩小)**')
        # 同样添加 flex-nowrap
        with ui.row().classes('w-80 p-4 border-2 border-dashed border-blue-400 bg-blue-50 min-h-24 flex-nowrap'):
            ui.label('不缩小').classes('p-3 m-1 rounded bg-purple-200 text-center min-h-10 flex items-center justify-center shrink-0')
            ui.label('会缩小').classes('p-3 m-1 rounded bg-pink-200 text-center min-h-10 flex items-center justify-center shrink')
            ui.label('会缩小').classes('p-3 m-1 rounded bg-orange-200 text-center min-h-10 flex items-center justify-center shrink')
        ui.label('属性值: flex-shrink: 0, 1, 1 (现在会生效)').classes('text-sm text-gray-600')
        ui.label('说明: 添加 flex-nowrap 后，第一个项目(shrink-0)将保持其原始宽度，而另外两个项目(shrink)将分担所有的收缩量。').classes('text-xs text-gray-500 mt-2')


    # 3. flex-basis 演示
    ui.markdown('### 3. flex-basis (初始大小)')

    with ui.card():
        ui.markdown('**flex-basis: auto (默认-根据内容) | tailwind class(basis-auto)**')
        with ui.row().classes('w-full p-4 border-2 border-dashed border-blue-400 bg-blue-50 min-h-24'):
            ui.label('短').classes('p-3 m-1 rounded bg-cyan-200 text-center min-h-10 flex items-center justify-center').style("flex-basis: auto")
            ui.label('中等长度文本').classes('p-3 m-1 rounded bg-lime-200 text-center min-h-10 flex items-center justify-center').style("flex-basis: auto")
            ui.label('这是一个很长的文本内容').classes('p-3 m-1 rounded bg-amber-200 text-center min-h-10 flex items-center justify-center').style("flex-basis: auto")
        ui.label('属性值: flex-basis: auto').classes('text-sm text-gray-600')

    with ui.card():
        ui.markdown('**flex-basis: 指定大小 | tailwind class(basis-24)**')
        with ui.row().classes('w-full p-4 border-2 border-dashed border-blue-400 bg-blue-50 min-h-24'):
            ui.label('basis-24').classes('p-3 m-1 rounded bg-cyan-200 text-center min-h-10 flex items-center justify-center basis-24')#.style("flex-basis: 24")
            ui.label('basis-32').classes('p-3 m-1 rounded bg-lime-200 text-center min-h-10 flex items-center justify-center basis-32')#.style("flex-basis: 32")
            ui.label('basis-40').classes('p-3 m-1 rounded bg-amber-200 text-center min-h-10 flex items-center justify-center basis-40')#.style("flex-basis: 40")
        ui.label('属性值: flex-basis: 96px, 128px, 160px').classes('text-sm text-gray-600')

    # 4. align-self 演示
    ui.markdown('### 4. align-self (单独对齐)')

    with ui.card():
        ui.markdown('**align-self: 不同对齐方式**')
        with ui.row().classes('w-full p-4 border-2 border-dashed border-blue-400 bg-blue-50 items-center h-40'):
            ui.label('self-start').classes('p-3 m-1 rounded bg-red-200 text-center min-h-12 flex items-center justify-center self-start')
            ui.label('self-center').classes('p-3 m-1 rounded bg-green-200 text-center min-h-12 flex items-center justify-center self-center')
            ui.label('self-end').classes('p-3 m-1 rounded bg-blue-200 text-center min-h-12 flex items-center justify-center self-end')
            ui.label('self-stretch').classes('p-3 m-1 rounded bg-purple-200 text-center flex items-center justify-center self-stretch')
        ui.label('属性值: align-self: flex-start, center, flex-end, stretch').classes('text-sm text-gray-600')

    # 5. order 演示
    ui.markdown('### 5. order (排列顺序)')

    with ui.card():
        ui.markdown('**order: 改变显示顺序**')
        with ui.row().classes('w-full p-4 border-2 border-dashed border-blue-400 bg-blue-50 min-h-24'):
            ui.label('第一个(order-3)').classes('p-3 m-1 rounded bg-red-200 text-center min-h-10 flex items-center justify-center order-3')
            ui.label('第二个(order-1)').classes('p-3 m-1 rounded bg-green-200 text-center min-h-10 flex items-center justify-center order-1')
            ui.label('第三个(order-2)').classes('p-3 m-1 rounded bg-blue-200 text-center min-h-10 flex items-center justify-center order-2')
        ui.label('属性值: order: 3, 1, 2 (显示顺序: 2, 3, 1)').classes('text-sm text-gray-600')

    ui.separator()

    # ===== 综合应用示例 =====
    ui.markdown('## 三、综合应用示例')

    with ui.card():
        ui.markdown('### 响应式卡片布局')
        ui.markdown('**使用 justify-between + items-stretch + flex-wrap**')
        
        with ui.row().classes('w-full p-4 border-2 border-dashed border-blue-400 bg-blue-50 justify-between items-stretch flex-wrap gap-4'):
            with ui.card().classes('basis-64 grow p-4'):
                ui.label('卡片 1').classes('text-lg font-bold mb-2')
                ui.label('这是第一张卡片的内容，展示了弹性布局的综合应用。')
            
            with ui.card().classes('basis-64 grow p-4'):
                ui.label('卡片 2').classes('text-lg font-bold mb-2')
                ui.label('这是第二张卡片，内容稍短一些。')
            
            with ui.card().classes('basis-64 grow p-4'):
                ui.label('卡片 3').classes('text-lg font-bold mb-2')
                ui.label('第三张卡片展示了如何在不同屏幕尺寸下保持良好的布局效果。')
        
        ui.label('属性组合: justify-content: space-between + align-items: stretch + flex-wrap: wrap + flex-basis: 256px + flex-grow: 1').classes('text-sm text-gray-600')

    # 页面底部说明
    ui.separator()
    ui.markdown('''
    ### 📝 说明
    - NiceGUI 基于 Quasar 框架，默认使用弹性盒子布局
    - 可以通过 Tailwind CSS 类名来控制弹性属性
    - `ui.row()` 默认为水平弹性容器，`ui.column()` 默认为垂直弹性容器
    - 通过 `.classes()` 方法添加 Tailwind CSS 类来实现各种布局效果
    - 注意：NiceGUI 的 `ui.row()` 默认 `wrap=True`，与标准 flexbox 不同
    ''')
