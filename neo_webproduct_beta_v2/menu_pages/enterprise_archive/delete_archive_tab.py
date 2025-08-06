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
    global select_values, select_options
    select_values = []
    select_options = []

    with ui.column().classes('w-full gap-6 p-4 items-center'):
        with ui.column().classes('w-full gap-4'):
            ui.label('删除企业档案').classes('text-h5 font-bold text-primary')
            with ui.card().classes('w-full'):
                ui.label("操作说明")

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
                ui.button("删除").classes('min-w-[100px]')
                
            with ui.row().classes('w-full gap-4 justify-end'):
                doc_log = ui.log(max_lines=20).classes('w-full h-80 border rounded overflow-y-auto scrollbar-hide')

    # 监听回车键事件
    search_input.on('keydown.enter', lambda: asyncio.create_task(on_search_enter()))
    # 监听输入值变化
    search_input.on_value_change(lambda: asyncio.create_task(on_input_change()))
    # 可选：监听输入变化，实现实时搜索（防抖）
    search_timer = None

    async def search_enterprises(search_text: str):
        """调用API搜索企业"""
        if not search_text or len(search_text.strip()) < 1:
            search_select.set_options({})
            search_status.set_text('')
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
                            
                            # 构建下拉选项：显示 enterprise_code + enterprise_name，值为 enterprise_code
                            options = {}
                            for enterprise in enterprises:
                                enterprise_code = enterprise.get('enterprise_code', '')
                                enterprise_name = enterprise.get('enterprise_name', '')
                                display_text = f"{enterprise_code} - {enterprise_name}"
                                options[enterprise_code] = display_text
                            
                            # 更新下拉选择器选项
                            search_select.set_options(options)
                            
                            # 更新状态
                            if len(enterprises) > 0:
                                # first_enterprise_code = enterprises[0].get('enterprise_code', '')
                                # if first_enterprise_code:
                                #     search_select.set_value(first_enterprise_code)

                                # 更新状态（移除ui.notify避免上下文错误）    
                                search_status.set_text(f'✅ 找到 {len(enterprises)} 条记录（共 {total_count} 条匹配）')
                                log_info(f"企业搜索成功: 找到 {len(enterprises)} 条记录")
                            else:
                                search_status.set_text('❌ 未找到匹配的企业')
                                log_info(f"企业搜索无结果: {search_text}")
                        else:
                            error_msg = data.get('message', '搜索失败')
                            search_status.set_text(f'❌ {error_msg}')
                            search_select.set_options({})
                            log_error(f"企业搜索API返回失败: {error_msg}")
                    else:
                        error_text = await response.text()
                        search_status.set_text('❌ 搜索服务异常')
                        search_select.set_options({})
                        log_error(f"企业搜索API请求失败: status={response.status}, response={error_text}")
                        
        except Exception as e:
            search_status.set_text('❌ 搜索过程发生异常')
            search_select.set_options({})
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
            # 清空输入时清空选项
            search_select.set_options({})
            search_status.set_text('')

   