#!/usr/bin/env python3

from nicegui import ui

def create_data_operator_content():
    """
    NiceGUI 网格布局与弹性盒子布局对比演示
    展示Grid Layout和Flexbox的不同应用场景和特点
    """
    # 设置页面标题
    ui.page_title('NiceGUI 网格布局与弹性盒子布局对比')

    # 添加简单的全局样式
    ui.add_head_html('''
    <style>
        body {
            font-family: system-ui, -apple-system, sans-serif;
        }
    </style>
    ''')

    # 页面标题
    ui.markdown('# NiceGUI 网格布局与弹性盒子布局对比')
    ui.separator()

    # ===== 网格布局基础演示 =====
    ui.markdown('## 一、网格布局（Grid Layout）基础')

    # 1. 基本网格
    ui.markdown('### 1. 基本网格结构')

    with ui.card().classes("w-full"):
        ui.markdown('**grid-cols-3 (3列网格)**')
        with ui.grid(columns=3).classes('w-full p-4 border-2 border-dashed border-green-400 bg-green-50 gap-2'):
            for i in range(9):
                ui.button(i).classes('p-4 rounded bg-blue-200 text-center flex items-center justify-center').text = f'项目{i+1}'
        ui.label('属性值: display: grid; grid-template-columns: repeat(3, 1fr)').classes('text-sm text-gray-600')

    with ui.card():
        ui.markdown('**grid-cols-4 (4列网格)**')
        with ui.grid(columns=4).classes('w-full p-4 border-2 border-dashed border-green-400 bg-green-50 gap-2'):
            for i in range(8):
                ui.element('div').classes('p-4 rounded bg-purple-200 text-center flex items-center justify-center').text = f'项目{i+1}'
        ui.label('属性值: display: grid; grid-template-columns: repeat(4, 1fr)').classes('text-sm text-gray-600')

    # 2. 网格间距
    ui.markdown('### 2. 网格间距控制')

    with ui.card():
        ui.markdown('**gap-1 (小间距)**')
        with ui.grid(columns=3).classes('w-full p-4 border-2 border-dashed border-green-400 bg-green-50 gap-1'):
            for i in range(6):
                ui.element('div').classes('p-3 rounded bg-red-200 text-center flex items-center justify-center').text = f'项目{i+1}'
        ui.label('属性值: gap: 4px').classes('text-sm text-gray-600')

    with ui.card():
        ui.markdown('**gap-4 (中等间距)**')
        with ui.grid(columns=3).classes('w-full p-4 border-2 border-dashed border-green-400 bg-green-50 gap-4'):
            for i in range(6):
                ui.element('div').classes('p-3 rounded bg-green-200 text-center flex items-center justify-center').text = f'项目{i+1}'
        ui.label('属性值: gap: 16px').classes('text-sm text-gray-600')

    with ui.card():
        ui.markdown('**gap-8 (大间距)**')
        with ui.grid(columns=3).classes('w-full p-4 border-2 border-dashed border-green-400 bg-green-50 gap-8'):
            for i in range(6):
                ui.element('div').classes('p-3 rounded bg-blue-200 text-center flex items-center justify-center').text = f'项目{i+1}'
        ui.label('属性值: gap: 32px').classes('text-sm text-gray-600')

    # 3. 不等宽列
    ui.markdown('### 3. 自定义列宽')

    with ui.card():
        ui.markdown('**grid-cols-[1fr_2fr_1fr] (不等宽列)**')
        with ui.element('div').classes('w-full p-4 border-2 border-dashed border-green-400 bg-green-50 grid grid-cols-[1fr_2fr_1fr] gap-2'):
            ui.element('div').classes('p-4 rounded bg-yellow-200 text-center flex items-center justify-center').text = '1fr'
            ui.element('div').classes('p-4 rounded bg-orange-200 text-center flex items-center justify-center').text = '2fr (更宽)'
            ui.element('div').classes('p-4 rounded bg-pink-200 text-center flex items-center justify-center').text = '1fr'
        ui.label('属性值: grid-template-columns: 1fr 2fr 1fr').classes('text-sm text-gray-600')

    with ui.card():
        ui.markdown('**grid-cols-[200px_1fr_100px] (固定+自适应列)**')
        with ui.element('div').classes('w-full p-4 border-2 border-dashed border-green-400 bg-green-50 grid grid-cols-[200px_1fr_100px] gap-2'):
            ui.element('div').classes('p-4 rounded bg-cyan-200 text-center flex items-center justify-center').text = '200px'
            ui.element('div').classes('p-4 rounded bg-lime-200 text-center flex items-center justify-center').text = '自适应(1fr)'
            ui.element('div').classes('p-4 rounded bg-amber-200 text-center flex items-center justify-center').text = '100px'
        ui.label('属性值: grid-template-columns: 200px 1fr 100px').classes('text-sm text-gray-600')

    # 4. 网格项目跨越
    ui.markdown('### 4. 网格项目跨越（span）')

    with ui.card():
        ui.markdown('**col-span 和 row-span**')
        with ui.grid(columns=4).classes('w-full p-4 border-2 border-dashed border-green-400 bg-green-50 gap-2'):
            ui.element('div').classes('p-4 rounded bg-red-300 text-center flex items-center justify-center col-span-2').text = 'col-span-2'
            ui.element('div').classes('p-4 rounded bg-blue-300 text-center flex items-center justify-center').text = '普通'
            ui.element('div').classes('p-4 rounded bg-green-300 text-center flex items-center justify-center').text = '普通'
            ui.element('div').classes('p-4 rounded bg-purple-300 text-center flex items-center justify-center').text = '普通'
            ui.element('div').classes('p-4 rounded bg-yellow-300 text-center flex items-center justify-center col-span-3').text = 'col-span-3'
            ui.element('div').classes('p-4 rounded bg-pink-300 text-center flex items-center justify-center').text = '普通'
        ui.label('属性值: grid-column: span 2 / span 3').classes('text-sm text-gray-600')

    # 5. 网格对齐
    ui.markdown('### 5. 网格内容对齐')

    with ui.card():
        ui.markdown('**justify-items + align-items**')
        with ui.grid(columns=3).classes('w-full p-4 border-2 border-dashed border-green-400 bg-green-50 gap-2 h-40 justify-items-center items-center'):
            ui.element('div').classes('p-2 rounded bg-indigo-200 text-center w-16 h-8 flex items-center justify-center').text = '居中'
            ui.element('div').classes('p-2 rounded bg-teal-200 text-center w-20 h-10 flex items-center justify-center').text = '居中'
            ui.element('div').classes('p-2 rounded bg-orange-200 text-center w-12 h-6 flex items-center justify-center').text = '居中'
        ui.label('属性值: justify-items: center; align-items: center').classes('text-sm text-gray-600')

    ui.separator()

    # ===== 弹性盒子布局对比 =====
    ui.markdown('## 二、弹性盒子布局对比')

    ui.markdown('### 相同布局的不同实现方式')

    with ui.card():
        ui.markdown('**使用 Grid 实现 3 列布局**')
        with ui.grid(columns=3).classes('w-full p-4 border-2 border-dashed border-green-400 bg-green-50 gap-4'):
            ui.element('div').classes('p-4 rounded bg-blue-200 text-center flex items-center justify-center').text = 'Grid 项目1'
            ui.element('div').classes('p-4 rounded bg-blue-200 text-center flex items-center justify-center').text = 'Grid 项目2'
            ui.element('div').classes('p-4 rounded bg-blue-200 text-center flex items-center justify-center').text = 'Grid 项目3'
        ui.label('Grid: 明确定义3列，自动排列').classes('text-sm text-gray-600')

    with ui.card():
        ui.markdown('**使用 Flexbox 实现 3 列布局**')
        with ui.row().classes('w-full p-4 border-2 border-dashed border-blue-400 bg-blue-50 gap-4'):
            ui.element('div').classes('p-4 rounded bg-purple-200 text-center flex items-center justify-center grow').text = 'Flex 项目1'
            ui.element('div').classes('p-4 rounded bg-purple-200 text-center flex items-center justify-center grow').text = 'Flex 项目2'
            ui.element('div').classes('p-4 rounded bg-purple-200 text-center flex items-center justify-center grow').text = 'Flex 项目3'
        ui.label('Flexbox: 通过 flex-grow 平均分配空间').classes('text-sm text-gray-600')

    ui.separator()

    # ===== 复杂布局对比 =====
    ui.markdown('## 三、复杂布局应用场景')

    # 1. 卡片网格布局（Grid优势）
    ui.markdown('### 1. 卡片网格布局 - Grid 的优势')

    with ui.card():
        ui.markdown('**响应式卡片网格**')
        with ui.grid(columns='repeat(auto-fit, minmax(200px, 1fr))').classes('w-full p-4 border-2 border-dashed border-green-400 bg-green-50 gap-4'):
            for i in range(6):
                with ui.card().classes('p-4'):
                    ui.label(f'卡片 {i+1}').classes('text-lg font-bold mb-2')
                    ui.label(f'这是卡片{i+1}的内容，Grid布局能自动调整列数。')
        ui.label('Grid: 自动响应式，根据空间自动调整列数').classes('text-sm text-gray-600')

    # 2. 导航栏布局（Flexbox优势）
    ui.markdown('### 2. 导航栏布局 - Flexbox 的优势')

    with ui.card():
        ui.markdown('**导航栏布局**')
        with ui.row().classes('w-full p-4 border-2 border-dashed border-blue-400 bg-blue-50 justify-between items-center'):
            ui.element('div').classes('p-2 rounded bg-red-200 font-bold').text = 'LOGO'
            with ui.row().classes('gap-4'):
                ui.element('div').classes('p-2 rounded bg-green-200').text = '首页'
                ui.element('div').classes('p-2 rounded bg-green-200').text = '产品'
                ui.element('div').classes('p-2 rounded bg-green-200').text = '关于'
            ui.element('div').classes('p-2 rounded bg-blue-200').text = '登录'
        ui.label('Flexbox: 适合一维布局，空间分配灵活').classes('text-sm text-gray-600')

    # 3. 复杂页面布局（Grid优势）
    ui.markdown('### 3. 页面整体布局 - Grid 的优势')

    with ui.card():
        ui.markdown('**经典页面布局**')
        with ui.element('div').classes('w-full h-80 border-2 border-dashed border-green-400 bg-green-50 grid grid-cols-[200px_1fr_150px] grid-rows-[60px_1fr_40px] gap-2 p-2'):
            ui.element('div').classes('p-2 rounded bg-red-200 text-center flex items-center justify-center col-span-3').text = 'Header'
            ui.element('div').classes('p-2 rounded bg-blue-200 text-center flex items-center justify-center').text = 'Sidebar'
            ui.element('div').classes('p-2 rounded bg-green-200 text-center flex items-center justify-center').text = 'Main Content'
            ui.element('div').classes('p-2 rounded bg-yellow-200 text-center flex items-center justify-center').text = 'Aside'
            ui.element('div').classes('p-2 rounded bg-purple-200 text-center flex items-center justify-center col-span-3').text = 'Footer'
        ui.label('Grid: 二维布局，精确控制行列位置').classes('text-sm text-gray-600')

    ui.separator()

    # ===== 详细对比表格 =====
    ui.markdown('## 四、Grid vs Flexbox 详细对比')

    with ui.card().classes('p-4'):
        ui.markdown('''
    ### 📊 对比总结

    | 特性 | Grid Layout | Flexbox |
    |------|-------------|---------|
    | **维度** | 二维布局（行+列） | 一维布局（主轴） |
    | **适用场景** | 复杂页面布局、卡片网格 | 导航栏、按钮组、内容对齐 |
    | **布局控制** | 精确的行列定位 | 灵活的空间分配 |
    | **响应式** | 自动调整网格列数 | 通过wrap实现换行 |
    | **对齐方式** | justify-items, align-items | justify-content, align-items |
    | **学习难度** | 相对复杂 | 相对简单 |

    ### 🎯 选择建议

    **使用 Grid 当你需要：**
    - 创建复杂的二维布局
    - 精确控制项目的行列位置
    - 响应式网格系统
    - 整体页面架构

    **使用 Flexbox 当你需要：**
    - 简单的一维排列
    - 灵活的空间分配
    - 内容居中对齐
    - 组件内部布局

    ### 💡 实际开发中
    两者经常结合使用：
    - Grid 负责页面整体布局
    - Flexbox 负责组件内部对齐
    - 根据具体需求选择最合适的布局方式
        ''')

    ui.separator()

    # ===== 交互演示 =====
    ui.markdown('## 五、交互演示')

    # 创建一个可以切换布局方式的演示
    layout_type = ui.select(['Grid 布局', 'Flexbox 布局'], value='Grid 布局').classes('mb-4')
    demo_container = ui.element('div').classes('w-full p-4 border-2 border-dashed border-gray-400 bg-gray-50 min-h-60')

    def update_layout():
        demo_container.clear()
        if layout_type.value == 'Grid 布局':
            with demo_container:
                with ui.grid(columns=3).classes('gap-4 h-full'):
                    for i in range(9):
                        ui.element('div').classes('p-4 rounded bg-blue-200 text-center flex items-center justify-center').text = f'Grid项目{i+1}'
        else:
            with demo_container:
                with ui.column().classes('gap-4 h-full'):
                    with ui.row().classes('gap-4'):
                        for i in range(3):
                            ui.element('div').classes('p-4 rounded bg-purple-200 text-center flex items-center justify-center grow').text = f'Flex项目{i+1}'
                    with ui.row().classes('gap-4'):
                        for i in range(3, 6):
                            ui.element('div').classes('p-4 rounded bg-purple-200 text-center flex items-center justify-center grow').text = f'Flex项目{i+1}'
                    with ui.row().classes('gap-4'):
                        for i in range(6, 9):
                            ui.element('div').classes('p-4 rounded bg-purple-200 text-center flex items-center justify-center grow').text = f'Flex项目{i+1}'

    layout_type.on('update:model-value', lambda: update_layout())
    update_layout()  # 初始化

    ui.label('切换上方选择器查看不同布局方式的实现').classes('text-sm text-gray-600 mt-2')

    ui.separator()

    ui.markdown('''
    ### 📝 总结
    - **Grid Layout** 是为二维布局设计的强大工具，适合复杂的页面架构
    - **Flexbox** 专注于一维布局，在组件级别的对齐和空间分配方面表现出色
    - 在实际项目中，两者往往配合使用，Grid 处理整体布局，Flexbox 处理细节对齐
    - NiceGUI 通过 `ui.grid()` 和 `ui.row()/ui.column()` 提供了便捷的布局组件
    - 配合 Tailwind CSS 类可以实现更精细的布局控制
    ''')