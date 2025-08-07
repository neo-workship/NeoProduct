"""
聊天组件 - 类似Vue组件，可复用的聊天UI
"""
import asyncio
from nicegui import ui, app
from typing import Optional
from component import static_manager
import os
from .hierarchy_selector_component import HierarchySelector
from .config import (
    get_model_options_for_select, 
    get_model_config, 
    get_default_model,
    reload_llm_config,
    get_config_info
)
    
def chat_page():
    model_options = get_model_options_for_select()  # 返回 ['deepseek-chat', 'moonshot-v1-8k', 'qwen-plus', ...]
    default_model = get_default_model() or 'deepseek-chat'
    current_model_config = {'selected_model': default_model, 'config': None}
    # 存储当前状态
    current_state = {
        'model_options': model_options,
        'default_model': default_model,
        'selected_model': default_model,
        'model_select_widget': None
    }

    # ============= 功能逻辑区域 =============
    def on_model_change(e):
        """模型选择变化事件处理"""
        selected_model_key = e.value
        model_config = get_model_config(selected_model_key)
        
        # 更新当前模型配置
        current_model_config['selected_model'] = selected_model_key
        current_model_config['config'] = model_config
        
        # 显示选择的模型信息
        if model_config:
            ui.notify(f'已切换到模型: {model_config.get("name", selected_model_key)}')
            print(f"模型配置: {model_config}")  # 用于调试
        else:
            ui.notify(f'已切换到模型: {selected_model_key}')

    def on_refresh_model_config():
        """刷新模型配置"""
        try:
            # 显示加载提示
            ui.notify('正在刷新配置...', type='info')
            
            # 重新加载配置
            success = reload_llm_config()
            
            if success:
                # 获取新的配置数据
                new_options = get_model_options_for_select()
                new_default = get_default_model() or 'deepseek-chat'
                
                # 更新状态
                current_state['model_options'] = new_options
                current_state['default_model'] = new_default
                
                # 更新UI组件的选项
                if current_state['model_select_widget']:
                    # 保存当前选择的模型（如果仍然可用的话）
                    current_selection = current_state['selected_model']
                    if current_selection not in new_options:
                        current_selection = new_default
                    
                    # 更新select组件
                    current_state['model_select_widget'].set_options(new_options)
                    current_state['model_select_widget'].set_value(current_selection)
                    current_state['selected_model'] = current_selection
                
                # 显示刷新结果
                config_info = get_config_info()
                ui.notify(
                    f'配置刷新成功！共加载 {config_info["total_models"]} 个模型，'
                    f'其中 {config_info["enabled_models"]} 个已启用',
                    type='positive'
                )
                
            else:
                ui.notify('配置刷新失败，请检查配置文件', type='negative')
                
        except Exception as e:
            ui.notify(f'刷新配置时出错: {str(e)}', type='negative')
            
    # =============
    async def scroll_to_bottom_smooth():
        """平滑滚动到底部，使用更可靠的方法"""
        try:
            # 方法1: 使用 scroll_area 的内置方法，设置 percent > 1 确保滚动到底部
            scroll_area.scroll_to(percent=1.1)
            # 添加小延迟确保滚动完成
            await asyncio.sleep(0.05)
        except Exception as e:
            print(f"滚动出错: {e}")

    async def handle_message(event=None):
        user_message = input_ref['widget'].value.strip()
        if not user_message:
            return
        
        # 🔒 禁用输入框和发送按钮，防止重复发送
        input_ref['widget'].set_enabled(False)
        send_button_ref['widget'].set_enabled(False)
        
        # 清空输入框
        input_ref['widget'].set_value('')

        try:
            # 删除欢迎消息
            if welcome_message_container:
                welcome_message_container.clear()

            # 用户消息
            with messages:
                user_avatar = static_manager.get_fallback_path(
                    static_manager.get_logo_path('user.svg'),
                    'https://robohash.org/user'
                )
                with ui.chat_message(
                    name='您',
                    avatar=user_avatar,
                    sent=True
                ).classes('w-full'):
                    ui.label(user_message).classes('whitespace-pre-wrap break-words')

            # 添加用户消息后立即滚动到底部
            await scroll_to_bottom_smooth()

            # 机器人消息
            with messages:
                robot_avatar = static_manager.get_fallback_path(
                    static_manager.get_logo_path('robot_txt.svg'),
                    'https://robohash.org/ui'
                )
                with ui.chat_message(
                    name='AI',
                    avatar=robot_avatar
                ).classes('w-full'):
                    # 先放一个不可见的 label，用来做打字机动画
                    stream_label = ui.label('').classes('whitespace-pre-wrap')

                    full = f"我收到了您的消息：{user_message}。这是一个智能回复示例，包含更多内容来演示打字机效果。让我们看看这个功能如何工作..."  # 示例回复
                    typed = ''
                    for ch in full:
                        typed += ch
                        stream_label.text = typed
                        # 打字过程中也滚动到底部
                        await scroll_to_bottom_smooth()
                        await asyncio.sleep(0.03)

                    # 完成回复后最终滚动
                    await scroll_to_bottom_smooth()
        
        finally:
            # 🔓 无论是否出现异常，都要重新启用输入框和发送按钮
            input_ref['widget'].set_enabled(True)
            send_button_ref['widget'].set_enabled(True)
            # 重新聚焦到输入框，提升用户体验
            input_ref['widget'].run_method('focus')

    def handle_keydown(e):
        """处理键盘事件 - 使用NiceGUI原生方法"""
        # 检查输入框是否已禁用，如果禁用则不处理按键事件
        if not input_ref['widget'].enabled:
            return
            
        # 获取事件详细信息
        key = e.args.get('key', '')
        shift_key = e.args.get('shiftKey', False)
        
        if key == 'Enter':
            if shift_key:
                # Shift+Enter: 允许换行，不做任何处理
                # NiceGUI会自动处理换行，我们不需要阻止默认行为
                pass
            else:
                # 单独的Enter: 发送消息
                # 阻止默认的换行行为
                ui.run_javascript('event.preventDefault();')
                # 异步调用消息处理函数
                ui.timer(0.01, lambda: handle_message(), once=True)

    # ============= UI区域 =============
    # 添加全局样式，保持原有样式并添加scroll_area优化
    ui.add_head_html('''
        <style>
        /* 聊天组件专用样式 - 只影响聊天组件内部，不影响全局 */
        .chat-container {
            overflow: hidden !important;
            height: calc(100vh - 145px) !important;
            margin: 0 !important;
            padding: 0 !important;
        }
        .sidebar {
            border-right: 1px solid #e5e7eb;
            overflow-y: auto;
        }
        .sidebar::-webkit-scrollbar {
            width: 6px;
        }
        .sidebar::-webkit-scrollbar-track {
            background: transparent;
        }
        .sidebar::-webkit-scrollbar-thumb {
            background-color: #d1d5db;
            border-radius: 3px;
        }
        .sidebar::-webkit-scrollbar-thumb:hover {
            background-color: #9ca3af;
        }
        .chat-history-item {
            cursor: pointer;
            transition: background-color 0.2s;
        }
        .chat-history-item:hover {
            background-color: #e5e7eb;
        }
        .expansion-panel {
            margin-bottom: 8px;
        }
        /* 优化 scroll_area 内容区域的样式 */
        .q-scrollarea__content {
            min-height: 100%;
        }
    </style>
    ''')
    
    # 主容器 - 使用水平布局
    with ui.row().classes('w-full h-full chat-container').style('overflow: hidden; height: calc(100vh - 120px); margin: 0; padding: 0;'):   
        # 侧边栏 - 固定宽度
        with ui.column().classes('sidebar h-full').style('width: 280px; min-width: 280px;'):
            # 侧边栏标题
            with ui.row().classes('w-full p-4 border-b'):
                ui.icon('menu', size='md').classes('text-gray-600')
                ui.label('功能菜单').classes('text-lg font-semibold ml-2')
            
            # 侧边栏内容 - 完全按照原有结构
            with ui.column().classes('w-full p-3'):
                # 添加按钮
                ui.button('新建对话', icon='add').classes('w-full mb-3').props('outlined')
                
                # 选择模型expansion组件
                with ui.expansion('选择模型', icon='view_in_ar').classes('expansion-panel w-full'):
                    with ui.column().classes('p-1'):
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
                        ).props('autofocus dense')
                
                 # 设置expansion组件
                
                # 上下文模板expansion组件
                with ui.expansion('上下文模板', icon='pattern').classes('expansion-panel w-full'):
                    with ui.column().classes('p-2'):
                        continents = ["deepseek-chat","moonshot-v1-8k","Qwen32B"]
                        ui.select(options=continents, value='deepseek-chat', with_input=True,on_change=lambda e: ui.notify(e.value)).props('autofocus dense')

                # 数据expansion组件
                with ui.expansion('提示数据', icon='tips_and_updates').classes('expansion-panel w-full'):
                    with ui.column().classes('p-2 sidebar').style('flex-grow: 1; overflow-y: auto;'):
                        switch = ui.switch('启用')
                        HierarchySelector
                        hierarchy_selector = HierarchySelector(multiple=True)
                        hierarchy_selector.render_column()
                       
                # 历史expansion组件
                with ui.expansion('历史消息', icon='history').classes('expansion-panel w-full'):
                    with ui.column().classes('p-2'):
                        for i in range(5):
                            ui.label(f'历史对话 {i+1}').classes('chat-history-item p-2 rounded cursor-pointer').on('click', lambda: ui.notify('加载历史对话'))
        # 主聊天区域 - 占据剩余空间
        with ui.column().classes('flex-grow h-full').style('position: relative; overflow: hidden;'):
            # 聊天消息区域 - 使用 scroll_area 提供更好的滚动体验
            scroll_area = ui.scroll_area().classes('w-full').style('height: calc(100% - 80px); padding-bottom: 20px;')

            with scroll_area:
                messages = ui.column().classes('w-full p-4 gap-4')
                
                # 欢迎消息（可能会被删除）
                welcome_message_container = ui.column().classes('w-full')
                with welcome_message_container:
                    with ui.card().classes('w-full max-w-3xl mx-auto shadow-lg'):
                        with ui.column().classes('p-6 text-center'):
                            ui.icon('tips_and_updates', size='3xl').classes('text-blue-500 mb-4 text-3xl')
                            ui.label('欢迎使用一企一档智能助手').classes('text-2xl font-bold mb-2')
                            ui.label('请输入您的问题，我将为您提供帮助').classes('text-lg text-gray-600 mb-4')
                            
                            with ui.row().classes('justify-center gap-4'):
                                ui.chip('问答', icon='help_outline').classes('text-blue-600 text-lg')
                                ui.chip('翻译', icon='translate').classes('text-yellow-600 text-lg')
                                ui.chip('写作', icon='edit').classes('text-purple-600 text-lg')
                                ui.chip('分析', icon='analytics').classes('text-orange-600 text-lg')
                    
            # 输入区域 - 固定在底部，距离底部10px
            with ui.row().classes('w-full items-center gap-2 p-1 rounded ').style(
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