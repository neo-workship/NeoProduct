from nicegui import ui, app
def demo():
    ui.add_head_html('''
            <style>
            /* 聊天组件专用样式 - 只影响聊天组件内部，不影响全局 */
            .chat-archive-container {
                /*overflow: hidden !important;*/
                height: calc(100vh - 145px) !important;
                margin: 0 !important;
                padding: 0 !important;
                overflow-y: auto !important;
            }
                        
            .chat-archive-sidebar {
                border-right: 1px solid #e5e7eb;
                overflow-y: auto;
                transition: width 0.3s ease, opacity 0.3s ease;
            }
            
            .chat-archive-sidebar::-webkit-scrollbar {
                width: 2px;
            }
            .chat-archive-sidebar::-webkit-scrollbar-track {
                background: transparent;
            }
            .chat-archive-sidebar::-webkit-scrollbar-thumb {
                background-color: #d1d5db;
                border-radius: 3px;
            }
            .chat-archive-sidebar::-webkit-scrollbar-thumb:hover {
                background-color: #9ca3af;
            }
            /* 优化 scroll_area 内容区域的样式 */
            .q-scrollarea__content {
                min-height: 100%;
            }
            .chathistorylist-hide-scrollbar {
                overflow-y: auto;
                scrollbar-width: none;
                -ms-overflow-style: none;
            }
            .chathistorylist-scrollbar::-webkit-scrollbar {
                display: none;
            }
            
            /* 菜单图标的悬停效果 */
            .menu-toggle-icon {
                cursor: pointer;
                transition: color 0.2s ease;
            }
            .menu-toggle-icon:hover {
                color: #3b82f6 !important;
            }
            
            /* 悬浮按钮的悬停效果 */
            .floating-menu-btn:hover {
                background-color: #2563eb !important;
                transform: scale(1.05);
                transition: all 0.2s ease;
            }
            </style>
        ''')

    # 侧边栏显示状态控制 - 使用字典来避免作用域问题
    sidebar_state = {'visible': True}

    def toggle_sidebar():
        sidebar_state['visible'] = not sidebar_state['visible']
        if sidebar_state['visible']:
            # 显示侧边栏 - 还原到原始状态
            sidebar.style('width: 280px; min-width: 280px; opacity: 1; overflow-y: auto; border-right: 1px solid #e5e7eb;')
            # 隐藏悬浮按钮
            floating_menu.style('display: none;')
        else:
            # 隐藏侧边栏
            sidebar.style('width: 0; min-width: 0; opacity: 0; overflow: hidden; border-right: none;')
            # 显示悬浮按钮
            floating_menu.style('display: flex;')

    # 主容器 - 使用水平布局
    with ui.row().classes('w-full h-full chat-archive-container').style('height: calc(100vh - 120px); margin: 0; padding: 0;'):   
        # 侧边栏 - 固定宽度，添加可隐藏功能
        sidebar = ui.column().classes('chat-archive-sidebar h-full').style('width: 280px; min-width: 280px;')
        with sidebar:
            # 侧边栏标题
            with ui.row().classes('w-full'):
                # 菜单图标 - 添加点击事件来切换侧边栏
                menu_icon = ui.icon('keyboard_double_arrow_left', size='md').classes('text-gray-600 menu-toggle-icon')
                menu_icon.on('click', toggle_sidebar)
                ui.label('功能菜单').classes('text-lg font-semibold')
            
            # 侧边栏内容 - 完全按照原有结构
            with ui.column().classes('w-full items-center'):
                # 添加按钮
                ui.button('新建对话', icon='add', on_click=on_create_new_chat).props('outlined')
                
                # 选择模型expansion组件
                with ui.expansion('选择模型', icon='view_in_ar').classes('w-full'):
                    with ui.column().classes('w-full'):
                        # 配置管理按钮行
                        with ui.row().classes('w-full'):
                            ui.button(
                                '刷新配置', 
                                icon='refresh',
                                on_click=on_refresh_model_config
                            ).classes('text-xs').props('dense flat color="primary"').style('min-width: 80px;')
                        
                        # 模型选择下拉框
                        current_state['model_select_widget'] = ui.select(
                            options=current_state['model_options'],
                            value=current_state['default_model'],
                            with_input=True,
                            on_change=on_model_change
                        ).classes('w-full').props('autofocus dense')

                # 上下文模板expansion组件
                with ui.expansion('上下文模板', icon='pattern').classes('w-full'):
                    with ui.column().classes('w-full'):
                        continents = ["deepseek-chat","moonshot-v1-8k","Qwen32B"]
                        ui.select(options=continents, 
                                value='deepseek-chat', 
                                with_input=True,
                                on_change=lambda e: ui.notify(e.value)).classes('w-full').props('autofocus dense')

                # select数据expansion组件
                with ui.expansion('提示数据', icon='tips_and_updates').classes('w-full'):
                    with ui.column().classes('w-full chathistorylist-hide-scrollbar').style('flex-grow: 1; '):
                        switch = ui.switch('启用')
                        HierarchySelector
                        hierarchy_selector = HierarchySelector(multiple=True)
                        hierarchy_selector.render_column()
                    
                # 聊天历史expansion组件
                with ui.expansion('历史消息', icon='history').classes('w-full'):
                    with ui.column().classes('w-full'):
                        # 添加刷新按钮
                        with ui.row().classes('w-full'):
                            ui.button(
                                '刷新历史', 
                                icon='refresh',
                                on_click=lambda: refresh_chat_history_list()
                            ).classes('text-xs').props('dense flat color="primary"').style('min-width: 80px;')
                        
                        # 聊天历史列表容器
                        history_list_container = ui.column().classes('w-full h-96 chathistorylist-hide-scrollbar')
                        with history_list_container:
                            create_chat_history_list()
        
        # 主聊天区域 - 占据剩余空间
        with ui.column().classes('flex-grow h-full').style('position: relative; overflow: hidden;'):
            # 悬浮菜单按钮 - 当侧边栏隐藏时显示
            floating_menu = ui.icon('keyboard_double_arrow_right', size='sm').classes('text-white rounded-full p-2 cursor-pointer floating-menu-btn').style(
                'position: absolute; top: 5px; left: 5px; z-index: 1001; display: none; '
                'width:15px; height: 15px; align-items: center; justify-content: center;'
            )
            floating_menu.on('click', toggle_sidebar)
            
            # 聊天消息区域 - 使用 scroll_area 提供更好的滚动体验
            scroll_area = ui.scroll_area().classes('w-full').style('height: calc(100% - 80px); padding-bottom: 20px;')

            with scroll_area:
                messages = ui.column().classes('w-full gap-2')
                
                # 欢迎消息（可能会被删除）
                welcome_message_container = ui.column().classes('w-full')
                with welcome_message_container:
                    restore_welcome_message()
                    
            # 输入区域 - 固定在底部，距离底部10px
            with ui.row().classes('w-full items-center gap-2 rounded ').style(
                'position: absolute; bottom: 10px; left: 10px; right: 10px; z-index: 1000; '
                'margin: 0 auto; max-width: calc(100% - 20px);'
            ):    
                # 提前声明可变对象，供内部嵌套函数读写
                input_ref = {'widget': None}

                # 为发送按钮创建引用容器
                send_button_ref = {'widget': None}

                # 创建textarea并绑定事件
                input_ref['widget'] = ui.textarea(
                    placeholder='请输入您的消息...(Enter发送，Shift+Enter换行)'
                ).classes('flex-grow').style(
                    'min-height: 44px; max-height: 120px; resize: none;'
                ).props('outlined dense rounded rows=3')

                # 使用.on()方法监听keydown事件
                input_ref['widget'].on('keydown', handle_keydown)
                
                send_button_ref['widget'] = ui.button(
                    icon='send',
                    on_click=handle_message
                ).props('round dense ').classes('ml-2')