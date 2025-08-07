"""
删除数据Tab逻辑
"""
from nicegui import ui
import aiohttp
import asyncio
import re
from datetime import datetime
from common.exception_handler import log_info, log_error, safe_protect
from auth import auth_manager
MONGODB_SERVICE_URL = "http://localhost:8001"

def delete_archive_content():
    """创建配置数据内容网格"""
    global select_values, select_options, all_searched_enterprises
    select_values = []
    select_options = []
    all_searched_enterprises = {}  # 在函数开始时初始化

    with ui.column().classes('w-full gap-6 p-4 items-center'):
        with ui.column().classes('w-full gap-4'):
            ui.label('删除企业档案').classes('text-h5 font-bold text-primary')
            with ui.card().classes('w-full'):
                # ui.label("删除企业档案操作指南").classes('text-base font-bold mb-2')
                # ui.separator().classes('mb-3')
                
                with ui.column().classes('gap-2'):
                    # ui.label("📋 删除企业档案操作指南：").classes('text-subtitle1 font-medium')
                    
                    with ui.row().classes('items-start gap-2'):
                        ui.label("1.").classes('text-primary font-bold')
                        ui.label("在「企业搜索」框中输入企业代码或企业名称，系统会自动搜索匹配的企业")
                    
                    with ui.row().classes('items-start gap-2'):
                        ui.label("2.").classes('text-primary font-bold') 
                        ui.label("从「选择企业」下拉列表中选择需要删除的企业（支持多选）")
                    
                    with ui.row().classes('items-start gap-2'):
                        ui.label("3.").classes('text-primary font-bold')
                        ui.label("可以进行多次搜索，已选择的企业会自动保留，不会被新搜索结果影响")
                    
                    with ui.row().classes('items-start gap-2'):
                        ui.label("4.").classes('text-primary font-bold')
                        ui.label("确认选择后，点击「删除」按钮执行删除操作")
                    
                    ui.separator().classes('my-2')
                    
                    with ui.row().classes('items-center gap-2'):
                        ui.icon('warning').classes('text-orange-600')
                        ui.label("注意：删除操作不可恢复，请谨慎操作！").classes('text-orange-600 font-medium')

            # search_input 和 search_select的宽度比例为1：4
            with ui.row().classes('w-full gap-4 items-end'):
                # 搜索输入：search_input
                search_input = ui.input(
                    label='企业搜索',
                    placeholder='输入企业代码或企业名称进行搜索'
                ).classes('flex-1').props('clearable')
                
                # 下拉列表：search_select
                search_select = ui.select(
                    options={},
                    with_input=True,
                    clearable=True,
                    multiple=True,
                    label='选择企业'
                ).classes('flex-[4]').props('dense use-chips')

            with ui.row().classes('w-full gap-4 justify-end'):
                # 搜索结果状态标签
                search_status = ui.label('').classes('text-body2 text-grey-6')
                delete_btn = ui.button("删除").classes('min-w-[100px]')
                clear_btn = ui.button("清空").classes('min-w-[100px]')
                
            with ui.row().classes('w-full gap-4 justify-end'):
                doc_log = ui.log(max_lines=20).classes('w-full h-80 border rounded overflow-y-auto scrollbar-hide')
                doc_log.push('🚀 准备就绪......')
                
    # 全局变量用于存储所有搜索过的企业数据，用于保持选项显示
    all_searched_enterprises = {}
    # 可选：监听输入变化，实现实时搜索（防抖）
    search_timer = None

    async def search_enterprises(search_text: str):
        """调用API搜索企业"""
        global select_values, select_options, all_searched_enterprises
        
        if not search_text or len(search_text.strip()) < 1:
            # 清空输入时，需要保持已选择项的选项可见
            current_selected = search_select.value if search_select.value else []
            if current_selected:
                # 使用历史搜索数据来保持已选择项可见
                preserved_options = {}
                for selected_code in current_selected:
                    if selected_code in all_searched_enterprises:
                        enterprise_info = all_searched_enterprises[selected_code]
                        enterprise_name = enterprise_info.get('enterprise_name', '')
                        display_text = f"{selected_code} - {enterprise_name}"
                        preserved_options[selected_code] = display_text
                    else:
                        # 如果历史数据中也找不到，就只显示代码
                        preserved_options[selected_code] = selected_code
                
                search_select.set_options(preserved_options)
            else:
                search_select.set_options({})
            
            search_status.set_text('')
            select_values = []  # 清空搜索结果，但保持显示已选择的项
            return
            
        try:
            doc_log.push(f"搜索关键字:{search_text}")
            search_status.set_text('🔍 搜索中...')
            log_info(f"开始搜索企业: {search_text}")
            
            async with aiohttp.ClientSession() as session:
                # 构建请求数据
                request_data = {
                    "enterprise_text": search_text.strip(),
                    "limit": 50  # 限制返回50条结果
                }
                
                async with session.post(
                    f"{MONGODB_SERVICE_URL}/api/v1/enterprises/search",
                    json=request_data,
                    headers={'Content-Type': 'application/json'}
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if data.get('success', False):
                            enterprises = data.get('enterprises', [])
                            total_count = data.get('total_count', 0)
                            
                            # 1、每次search_input搜索到的内容，使用全局变量select_values存储
                            select_values = enterprises
                            
                            # 同时存储到历史搜索数据中，用于后续保持选项显示
                            for enterprise in enterprises:
                                enterprise_code = enterprise.get('enterprise_code', '')
                                if enterprise_code:
                                    all_searched_enterprises[enterprise_code] = enterprise
                            
                            # 构建下拉选项：显示 enterprise_code + enterprise_name，值为 enterprise_code
                            options = {}
                            
                            # 首先添加新搜索的结果
                            for enterprise in enterprises:
                                enterprise_code = enterprise.get('enterprise_code', '')
                                enterprise_name = enterprise.get('enterprise_name', '')
                                display_text = f"{enterprise_code} - {enterprise_name}"
                                options[enterprise_code] = display_text
                            
                            # 然后确保已选择的项也在选项中（即使不在当前搜索结果中）
                            current_selected = search_select.value if search_select.value else []
                            for selected_code in current_selected:
                                if selected_code not in options:  # 如果已选择的项不在新搜索结果中
                                    if selected_code in all_searched_enterprises:
                                        enterprise_info = all_searched_enterprises[selected_code]
                                        enterprise_name = enterprise_info.get('enterprise_name', '')
                                        display_text = f"{selected_code} - {enterprise_name}"
                                        options[selected_code] = display_text
                                    else:
                                        # 如果历史数据中也找不到，就只显示代码
                                        options[selected_code] = selected_code
                            
                            # 更新下拉选择器选项
                            search_select.set_options(options)
                            
                            # 保持用户当前已有的选择，不改变选中值
                            if current_selected:
                                search_select.set_value(current_selected)
                            
                            # 更新状态
                            if len(enterprises) > 0:
                                search_status.set_text(f'✅ 找到 {len(enterprises)} 条记录（共 {total_count} 条匹配）')
                                log_info(f"企业搜索成功: 找到 {len(enterprises)} 条记录")
                            else:
                                search_status.set_text('❌ 未找到匹配的企业')
                                log_info(f"企业搜索无结果: {search_text}")
                        else:
                            error_msg = data.get('message', '搜索失败')
                            search_status.set_text(f'❌ {error_msg}')
                            search_select.set_options({})
                            select_values = []  # 失败时重置全局变量
                            log_error(f"企业搜索API返回失败: {error_msg}")
                    else:
                        error_text = await response.text()
                        search_status.set_text('❌ 搜索服务异常')
                        search_select.set_options({})
                        select_values = []  # 异常时重置全局变量
                        log_error(f"企业搜索API请求失败: status={response.status}, response={error_text}")
                        
        except Exception as e:
            search_status.set_text('❌ 搜索过程发生异常')
            search_select.set_options({})
            select_values = []  # 异常时重置全局变量
            log_error("企业搜索异常", exception=e)

    # 绑定搜索输入框的回车事件
    async def on_search_enter():
        """按下回车键触发搜索"""
        search_text = search_input.value
        await search_enterprises(search_text)
    
    # 输入值变化事件
    async def on_input_change():
        """输入变化时的防抖搜索"""
        nonlocal search_timer
        if search_timer:
            search_timer.cancel()
        
        search_text = search_input.value
        if search_text and len(search_text.strip()) >= 2:  # 至少2个字符才开始搜索
            # 设置500ms防抖延迟
            search_timer = asyncio.create_task(asyncio.sleep(0.5))
            try:
                await search_timer
                await search_enterprises(search_text)
            except asyncio.CancelledError:
                pass  # 被新的输入取消了
        elif not search_text:
            # 清空输入时，需要保持已选择项的选项可见
            current_selected = search_select.value if search_select.value else []
            if current_selected:
                # 使用历史搜索数据来保持已选择项可见
                preserved_options = {}
                for selected_code in current_selected:
                    if selected_code in all_searched_enterprises:
                        enterprise_info = all_searched_enterprises[selected_code]
                        enterprise_name = enterprise_info.get('enterprise_name', '')
                        display_text = f"{selected_code} - {enterprise_name}"
                        preserved_options[selected_code] = display_text
                    else:
                        # 如果历史数据中也找不到，就只显示代码
                        preserved_options[selected_code] = selected_code
                
                search_select.set_options(preserved_options)
            else:
                search_select.set_options({})
            
            search_status.set_text('')
            select_values = []  # 清空搜索结果，但保持显示已选择的项
    
    # search_select 值变化事件处理
    def on_search_select_change():
        """每次选择的 search_select 的项，存储在全局变量select_options中"""
        global select_options
        # 只有当用户主动选择时才更新select_options，不受搜索影响
        select_options = search_select.value if search_select.value else []
        log_info(f"用户选择已更新 select_options: {select_options}")
        doc_log.push(f"用户已选择企业: {select_options}")
    
    # 初始化search_select的值变化监听
    def initialize_select_options():
        """初始化时设置select_options"""
        global select_options
        if not select_options:  # 只在首次初始化时设置
            select_options = []

    async def on_delete_archive():
        ui.notify("on_delete_archive")

    async def on_cancel_config():
        ui.notify("on_cancel_config")

    # 监听回车键事件
    search_input.on('keydown.enter', lambda: asyncio.create_task(on_search_enter()))
    # 监听输入值变化
    search_input.on_value_change(lambda: asyncio.create_task(on_input_change()))
    # 监听search_select值变化事件
    search_select.on_value_change(lambda: on_search_select_change())
    # 初始化选项
    initialize_select_options()
    # 删除操作
    delete_btn.on("click",lambda: on_delete_archive())
    clear_btn.on("click",lambda: on_cancel_config())