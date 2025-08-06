"""
编辑数据Tab逻辑
"""

from nicegui import ui
from .hierarchy_selector_component import HierarchySelector
from common.exception_handler import log_info, log_error, safe_protect
import aiohttp
import asyncio

# MongoDB服务API基础URL
MONGODB_SERVICE_URL = "http://localhost:8001"

@safe_protect(name="编辑档案页面", error_msg="编辑档案页面加载失败")
def edit_archive_content():
    """编辑档案内容页面"""
    global current_original_data, current_input_refs, display_model
    current_original_data = {}
    current_input_ref = {}
    display_model = ""
    # ----------------- 1、Search 逻辑 -----------------
    # 调用搜索API 
    async def search_enterprises(search_text: str):
        """调用API搜索企业"""
        if not search_text or len(search_text.strip()) < 1:
            search_select.set_options({})
            search_status.set_text('')
            return
            
        try:
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
                                first_enterprise_code = enterprises[0].get('enterprise_code', '')
                                if first_enterprise_code:
                                    search_select.set_value(first_enterprise_code)

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
    # 清空内容
    async def on_clear_enter():
        search_input.set_value('')
        results_container.clear()
        hierarchy_selector.reset_all_selections()
        search_status.set_text('')
        
    # 调用查询API
    @safe_protect(name="查询档案数据", error_msg="查询档案数据失败")
    async def on_query_enter():
        """查询档案数据函数"""
        try:
            # 1. 首先判断search_select、hierarchy_selector.selected_values["l3"]是否有值
            selected_enterprise = search_select.value
            selected_values = hierarchy_selector.get_selected_values()
            selected_l3 = selected_values.get("l3")
            
            if not selected_enterprise:
                query_status.set_text('❌ 请先选择企业')
                # ui.notify('请先选择企业', type='warning')
                return
                
            if not selected_l3:
                query_status.set_text('❌ 请先选择三级分类')
                # ui.notify('请先选择三级分类', type='warning')
                return

            query_status.set_text('🔍 查询中...')
            log_info(f"开始查询档案数据: enterprise={selected_enterprise}, l3={selected_l3}")

            # 2. 构建API调用参数
            enterprise_code = selected_enterprise
            
            # 构建 path_code_param: l1.l2.l3
            l1_code = selected_values.get("l1", "")
            l2_code = selected_values.get("l2", "")
            l3_code = selected_values.get("l3", "")
            path_code_param = f"{l1_code}.{l2_code}.{l3_code}"
            
            # 获取 fields_param
            fields_param = selected_values.get("field", [])
            if not isinstance(fields_param, list):
                fields_param = [fields_param] if fields_param else []

            # 3. 调用API: /api/v1/enterprises/query_fields
            async with aiohttp.ClientSession() as session:
                request_data = {
                    "enterprise_code": enterprise_code,
                    "path_code_param": path_code_param,
                    "fields_param": fields_param
                }
                
                async with session.post(
                    f"{MONGODB_SERVICE_URL}/api/v1/enterprises/query_fields",
                    json=request_data,
                    headers={'Content-Type': 'application/json'}
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get('success', False):
                            # 4. 成功调用API后，首先判断返回结果是否正确
                            query_results = data.get('fields', [])
                            
                            if not query_results:
                                query_status.set_text('❌ 未查询到相关数据')
                                # ui.notify('未查询到相关数据', type='info')
                                return

                            query_status.set_text(f'✅ 查询成功，找到 {len(query_results)} 条数据')
                            log_info(f"档案数据查询成功: 找到 {len(query_results)} 条记录")
                            
                            # 显示要修改的查询结果
                            await display_query_results(query_results)
                            
                        else:
                            error_msg = data.get('message', '查询失败')
                            query_status.set_text(f'❌ {error_msg}')
                            log_error(f"档案数据查询API返回失败: {error_msg}")
                    else:
                        error_text = await response.text()
                        query_status.set_text('❌ 查询服务异常')
                        log_error(f"档案数据查询API请求失败: status={response.status}, response={error_text}")
                        
        except Exception as e:
            query_status.set_text('❌ 查询过程发生异常')
            log_error("档案数据查询异常", exception=e)

    # ----------------- 2、Query 逻辑 -----------------
    # 在 edit_archive_content 函数末尾添加初始化显示
    def display_empty_state():
        """显示空数据状态"""
        # ui.label('查询结果').classes('text-sm font-bold text-primary mb-4')
        
        with ui.row().classes('w-full gap-4 items-stretch'):
            # 左侧card展示字段信息标题
            with ui.card().classes('flex-1 p-4 w-full'):
                ui.label('字段信息').classes('text-subtitle1 font-medium mb-3')
                
                with ui.row().classes('gap-2 items-center mb-2'):
                    ui.icon('label').classes('text-lg text-primary')
                    ui.label('字段名称:').classes('text-lg font-medium')
                    ui.label('暂无数据').classes('text-lg text-grey-6 flex-grow').props('dense')
                
                with ui.row().classes('gap-2 items-center mb-2'):
                    ui.icon('data_object').classes('text-lg text-blue-600')
                    ui.label('字段值:').classes('text-lg font-medium')
                    ui.label('暂无数据').classes('text-lg text-grey-6')
                
                with ui.row().classes('gap-2 items-center mb-2'):
                    ui.icon('image').classes('text-lg text-green-600')
                    ui.label('关联图片:').classes('text-lg font-medium')
                    ui.label('暂无数据').classes('text-lg text-grey-6')
                
                with ui.row().classes('gap-2 items-center mb-2'):
                    ui.icon('description').classes('text-lg text-orange-600')
                    ui.label('关联文档:').classes('text-lg font-medium')
                    ui.label('暂无数据').classes('text-lg text-grey-6')
                
                with ui.row().classes('gap-2 items-center mb-2'):
                    ui.icon('videocam').classes('text-lg text-red-600')
                    ui.label('关联视频:').classes('text-lg font-medium')
                    ui.label('暂无数据').classes('text-lg text-grey-6')
            
            # 右侧card展示数据元信息标题
            with ui.card().classes('flex-1 p-4 w-full'):
                ui.label('数据元信息').classes('text-subtitle1 font-medium mb-3')
                
                with ui.row().classes('gap-2 items-center mb-2'):
                    ui.icon('api').classes('text-lg text-purple-600')
                    ui.label('数据API:').classes('text-lg font-medium')
                    ui.label('暂无数据').classes('text-lg text-grey-6')
                
                with ui.row().classes('gap-2 items-center mb-2'):
                    ui.icon('code').classes('text-lg text-teal-600')
                    ui.label('编码方式:').classes('text-lg font-medium')
                    ui.label('暂无数据').classes('text-lg text-grey-6')
                
                with ui.row().classes('gap-2 items-center mb-2'):
                    ui.icon('settings').classes('text-lg text-grey-600')
                    ui.label('格式:').classes('text-lg font-medium')
                    ui.label('暂无数据').classes('text-lg text-grey-6')
                
                with ui.row().classes('gap-2 items-center mb-2'):
                    ui.icon('gavel').classes('text-lg text-amber-600')
                    ui.label('使用许可:').classes('text-lg font-medium')
                    ui.label('暂无数据').classes('text-lg text-grey-6')
                
                with ui.row().classes('gap-2 items-center mb-2'):
                    ui.icon('security').classes('text-lg text-red-500')
                    ui.label('使用权限:').classes('text-lg font-medium')
                    ui.label('暂无数据').classes('text-lg text-grey-6')
                
                with ui.row().classes('gap-2 items-center mb-2'):
                    ui.icon('update').classes('text-lg text-blue-500')
                    ui.label('更新频率:').classes('text-lg font-medium')
                    ui.label('暂无数据').classes('text-lg text-grey-6')
                
                with ui.row().classes('gap-2 items-center mb-2'):
                    ui.icon('book').classes('text-lg text-green-500')
                    ui.label('数据字典:').classes('text-lg font-medium')
                    ui.label('暂无数据').classes('text-lg text-grey-6') 
    
    # 初始化空数据页面
    def initialize_results_display():
        """初始化结果显示区域 - 显示空数据状态"""
        with results_container:
            display_empty_state()
    
    # results_container 将在上面的布局中定义
    @safe_protect(name="显示要编辑的档案数据", error_msg="显示要编辑档案数据")
    async def display_query_results(query_results):
        """显示要编辑的查询结果 - 根据数据条数选择不同的显示方式"""
        global display_model
        # 清空结果容器
        results_container.clear()
        # 根据数据条数选择显示方式
        if len(query_results) <= 2:
            display_model = "card"
            # 无数据或只有一条数据时，使用卡片方式显示
            await display_results_as_cards(query_results)
        else:
            display_model = "table"
            # 多条数据时，使用表格分页方式显示
            await display_results_as_table(query_results)

    # 全局变量用于存储当前UI组件引用（仅为了数据收集，不是状态管理）
    @safe_protect(name="卡片方式显示要修改的档案数据", error_msg="卡片方式显示要修改的档案数据")
    async def display_results_as_cards(query_results):
        """卡片方式显示要修改的查询结果（无数据或只有一条数据）"""
        global current_original_data, current_input_refs
        current_original_data = {}
        current_input_refs = {}
        
        with results_container:            
            if not query_results:
                # 无数据情况，显示空状态（与初始化状态相同）
                display_empty_state()
                return
            
            # 有一条数据时，按现有方式显示，但改为可编辑的输入框
            for i, result in enumerate(query_results):
                # 存储当前记录的原始数据
                current_original_data[i] = result
                current_input_refs[i] = {}

                with ui.row().classes('w-full gap-4 items-stretch'):
                    # 左侧card展示：full_path_name、value、value_pic_url、value_doc_url、value_video_url
                    with ui.card().classes('flex-1 p-4'):
                        ui.label('字段信息').classes('text-subtitle1 font-medium mb-3')
                        
                        # full_path_name（标题）- 只读显示
                        full_path_name = result.get('full_path_name', '未知字段')
                        ui.label(full_path_name).classes('text-base font-bold text-primary mb-2')
                        
                        # value（字段值）- 可编辑
                        value = result.get('value', '') or ''
                        current_value_label = f"字段值: {value}" if value and value != '暂无数据' else "字段值"
                        with ui.row().classes('w-full gap-2 items-center mb-2'):
                            ui.icon('data_object').classes('text-lg text-blue-600')
                            ui.label('字段值:').classes('text-lg font-medium')
                            value_input = ui.input(label=current_value_label, placeholder='请输入新的字段值').classes('text-lg flex-grow').props('dense')
                            current_input_refs[i]['value'] = value_input
                        
                        # value_pic_url（字段关联图片）- 可编辑
                        value_pic_url = result.get('value_pic_url', '') or ''
                        current_pic_label = f"关联图片: {value_pic_url}" if value_pic_url and value_pic_url != '暂无数据' else "关联图片"
                        with ui.row().classes('w-full gap-2 items-center mb-2'):
                            ui.icon('image').classes('text-lg text-green-600')
                            ui.label('关联图片:').classes('text-lg font-medium')
                            pic_input = ui.input(label=current_pic_label, placeholder='请输入新的图片URL').classes('text-lg flex-grow').props('dense')
                            current_input_refs[i]['value_pic_url'] = pic_input
                        
                        # value_doc_url（字段关联文档）- 可编辑
                        value_doc_url = result.get('value_doc_url', '') or ''
                        current_doc_label = f"关联文档: {value_doc_url}" if value_doc_url and value_doc_url != '暂无数据' else "关联文档"
                        with ui.row().classes('w-full gap-2 items-center mb-2'):
                            ui.icon('description').classes('text-lg text-orange-600')
                            ui.label('关联文档:').classes('text-lg font-medium')
                            doc_input = ui.input(label=current_doc_label, placeholder='请输入新的文档URL').classes('text-lg flex-grow').props('dense')
                            current_input_refs[i]['value_doc_url'] = doc_input
                        
                        # value_video_url（字段关联视频）- 可编辑
                        value_video_url = result.get('value_video_url', '') or ''
                        current_video_label = f"关联视频: {value_video_url}" if value_video_url and value_video_url != '暂无数据' else "关联视频"
                        with ui.row().classes('w-full gap-2 items-center mb-2'):
                            ui.icon('videocam').classes('text-lg text-purple-600')
                            ui.label('关联视频:').classes('text-lg font-medium')
                            video_input = ui.input(label=current_video_label, placeholder='请输入新的视频URL').classes('text-lg flex-grow').props('dense')
                            current_input_refs[i]['value_video_url'] = video_input
                    
                    # 右侧card展示：data_url、encoding、format、license、rights、update_frequency、value_dict
                    with ui.card().classes('flex-1 p-4'):
                        ui.label('字段属性').classes('text-subtitle1 font-medium mb-3')
                        
                        # data_url（数据API）- 可编辑
                        data_url = result.get('data_url', '') or ''
                        current_api_label = f"数据API: {data_url}" if data_url and data_url != '暂无数据' else "数据API"
                        with ui.row().classes('w-full gap-2 items-center mb-2'):
                            ui.icon('api').classes('text-lg text-indigo-600')
                            ui.label('数据API:').classes('text-lg font-medium')
                            api_input = ui.input(label=current_api_label, placeholder='请输入新的API地址').classes('text-lg flex-grow').props('dense')
                            current_input_refs[i]['data_url'] = api_input
                        
                        # encoding（编码方式）- 可编辑
                        encoding = result.get('encoding', '') or ''
                        current_encoding_label = f"编码方式: {encoding}" if encoding and encoding != '未指定' else "编码方式"
                        with ui.row().classes('w-full gap-2 items-center mb-2'):
                            ui.icon('code').classes('text-lg text-cyan-600')
                            ui.label('编码方式:').classes('text-lg font-medium')
                            encoding_input = ui.input(label=current_encoding_label, placeholder='请输入新的编码方式').classes('text-lg flex-grow').props('dense')
                            current_input_refs[i]['encoding'] = encoding_input
                        
                        # format（格式）- 可编辑
                        format_info = result.get('format', '') or ''
                        current_format_label = f"格式: {format_info}" if format_info and format_info != '未指定' else "格式"
                        with ui.row().classes('w-full gap-2 items-center mb-2'):
                            ui.icon('code').classes('text-lg text-teal-600')
                            ui.label('格式:').classes('text-lg font-medium')
                            format_input = ui.input(label=current_format_label, placeholder='请输入新的数据格式').classes('text-lg flex-grow').props('dense')
                            current_input_refs[i]['format'] = format_input
                        
                        # license（使用许可）- 可编辑
                        license_info = result.get('license', '') or ''
                        current_license_label = f"使用许可: {license_info}" if license_info and license_info != '未指定' else "使用许可"
                        with ui.row().classes('w-full gap-2 items-center mb-2'):
                            ui.icon('gavel').classes('text-lg text-amber-600')
                            ui.label('使用许可:').classes('text-lg font-medium')
                            license_input = ui.input(label=current_license_label, placeholder='请输入新的使用许可').classes('text-lg flex-grow').props('dense')
                            current_input_refs[i]['license'] = license_input
                        
                        # rights（使用权限）- 可编辑
                        rights = result.get('rights', '') or ''
                        current_rights_label = f"使用权限: {rights}" if rights and rights != '未指定' else "使用权限"
                        with ui.row().classes('w-full gap-2 items-center mb-2'):
                            ui.icon('security').classes('text-lg text-red-500')
                            ui.label('使用权限:').classes('text-lg font-medium')
                            rights_input = ui.input(label=current_rights_label, placeholder='请输入新的使用权限').classes('text-lg flex-grow').props('dense')
                            current_input_refs[i]['rights'] = rights_input
                        
                        # update_frequency（更新频率）- 可编辑
                        update_frequency = result.get('update_frequency', '') or ''
                        current_freq_label = f"更新频率: {update_frequency}" if update_frequency and update_frequency != '未指定' else "更新频率"
                        with ui.row().classes('w-full gap-2 items-center mb-2'):
                            ui.icon('update').classes('text-lg text-blue-500')
                            ui.label('更新频率:').classes('text-lg font-medium')
                            freq_input = ui.input(label=current_freq_label, placeholder='请输入新的更新频率').classes('text-lg flex-grow').props('dense')
                            current_input_refs[i]['update_frequency'] = freq_input
                        
                        # value_dict（数据字典）- 可编辑
                        value_dict = result.get('value_dict', '') or ''
                        current_dict_label = f"数据字典: {value_dict}" if value_dict and value_dict != '暂无数据' else "数据字典"
                        with ui.row().classes('w-full gap-2 items-center mb-2'):
                            ui.icon('book').classes('text-lg text-green-500')
                            ui.label('数据字典:').classes('text-lg font-medium')
                            dict_input = ui.input(label=current_dict_label, placeholder='请输入新的数据字典').classes('text-lg flex-grow').props('dense')
                            current_input_refs[i]['value_dict'] = dict_input

            with ui.row().classes("w-full justify-end"):
                ui.button("全部修改",on_click=lambda: on_edit_card_results()).classes('min-w-[100px]')
                ui.button("取消修改").classes('min-w-[100px]')
            
    @safe_protect(name="表格方式显示要修改档案数据", error_msg="表格方式显示要修改的档案数据")
    async def display_results_as_table(query_results):
        """表格方式显示要修改的查询结果（多条数据，分页模式）"""
        global current_original_data, current_input_refs
        current_original_data = {}
        current_input_refs = {}
        
        with results_container:
            # 定义表格列 - 添加操作列
            columns = [
                {'name': 'field_name', 'label': '字段名称', 'field': 'field_name', 'sortable': True, 'align': 'left'},
                {'name': 'value', 'label': '字段值', 'field': 'value', 'sortable': True, 'align': 'left'},
                {'name': 'encoding', 'label': '编码方式', 'field': 'encoding', 'sortable': True, 'align': 'left'},
                {'name': 'format', 'label': '格式', 'field': 'format', 'sortable': True, 'align': 'left'},
                {'name': 'actions', 'label': '操作', 'field': 'actions', 'sortable': False, 'align': 'center'},
            ]
            
            # 准备行数据
            rows = []
            for i, result in enumerate(query_results):
                # 存储原始数据用于编辑
                current_original_data[i] = result
                
                row = {
                    'id': i,
                    'field_name': result.get('field_name', '未知字段'),
                    'value': result.get('value', '暂无数据') or '暂无数据',
                    'encoding': result.get('encoding', '未指定') or '未指定',
                    'format': result.get('format', '未指定') or '未指定',
                    'actions': '',  # 操作列占位
                    '_raw_data': result
                }
                rows.append(row)
            
            # 创建表格
            table = ui.table(
                columns=columns, 
                rows=rows, 
                row_key='id',
                pagination=10,  # 每页显示10条
                column_defaults={
                    'align': 'left',
                    'headerClasses': 'uppercase text-primary text-base font-bold',
                }
            ).classes('w-full')
            
            # 自定义操作列的槽
            table.add_slot('body-cell-actions', '''
                <q-td :props="props">
                    <q-btn flat dense color="primary" icon="edit" size="base" 
                        @click="$parent.$emit('edit-row', props.row)"
                        class="q-mr-xs">
                        <q-tooltip>编辑</q-tooltip>
                    </q-btn>
                </q-td>
            ''')
            
            # 处理编辑和更新事件
            table.on('edit-row', lambda e: open_edit_dialog(e.args['id']))
            # table.on('update-row', lambda e: update_single_row(e.args['id']))
    
    async def open_edit_dialog(row_id: int):
        """打开编辑对话框 - 参考 display_results_as_cards 的布局"""
        global current_original_data, current_input_refs
        # current_input_refs[row_id] = {}
        if row_id not in current_original_data:
            ui.notify('数据不存在', type='negative')
            return
        
        result = current_original_data[row_id]
        ui.add_head_html('''
            <style>
            .editdialog-hide-scrollbar {
                overflow-y: auto;
                scrollbar-width: none;
                -ms-overflow-style: none;
            }
            .editdialog-hide-scrollbar::-webkit-scrollbar {
                display: none;
            }
            </style>
        ''')
        
        with ui.dialog() as dialog, ui.card().classes('w-full max-w-4xl overflow-y-auto'):
            ui.label(f'编辑: {result.get("field_name", "未知字段")}').classes('text-h6 mb-4')
            
            with ui.column().classes('w-full gap-4 items-stretch editdialog-hide-scrollbar'):
                # 左侧卡片 - 字段信息
                with ui.card().classes('flex-1 p-4'):
                    ui.label('字段信息').classes('text-subtitle1 font-medium mb-3')
                    
                    # full_path_name（标题）- 只读显示
                    full_path_name = result.get('full_path_name', '未知字段')
                    ui.label(full_path_name).classes('text-sm font-bold text-primary mb-2')
                    
                    # value（字段值）- 可编辑
                    value = result.get('value', '') or ''
                    current_value_value = f"{value}" if value else "暂无数据"
                    with ui.row().classes('w-full gap-2 items-center mb-2'):
                        ui.icon('data_object').classes('text-sm text-blue-600')
                        ui.label('字段值:').classes('text-sm font-medium')
                        value_input = ui.input(
                            # label=current_value_value, 
                            placeholder='请输入新的字段值', 
                            value=current_value_value  # 回显已编辑的值
                        ).classes('text-sm flex-grow').props('dense')
                        current_input_refs['value'] = value_input
                    
                    # value_pic_url（字段关联图片）- 可编辑
                    value_pic_url = result.get('value_pic_url', '') or ''
                    current_pic_value = f"{value_pic_url}" if value_pic_url else "暂无数据"
                    with ui.row().classes('w-full gap-2 items-center mb-2'):
                        ui.icon('image').classes('text-sm text-green-600')
                        ui.label('关联图片:').classes('text-sm font-medium')
                        pic_input = ui.input(
                            # label=current_pic_value, 
                            placeholder='请输入新的图片URL', 
                            value=current_pic_value  # 回显已编辑的值
                        ).classes('text-sm flex-grow').props('dense')
                        current_input_refs['value_pic_url'] = pic_input
                    
                    # value_doc_url（字段关联文档）- 可编辑
                    value_doc_url = result.get('value_doc_url', '') or ''
                    current_doc_value = f"{value_doc_url}" if value_doc_url else "暂无数据"
                    with ui.row().classes('w-full gap-2 items-center mb-2'):
                        ui.icon('article').classes('text-sm text-orange-600')
                        ui.label('关联文档:').classes('text-sm font-medium')
                        doc_input = ui.input(
                            # label=current_doc_value, 
                            placeholder='请输入新的文档URL', 
                            value=current_doc_value  # 回显已编辑的值
                        ).classes('text-sm flex-grow').props('dense')
                        current_input_refs['value_doc_url'] = doc_input
                    
                    # value_video_url（字段关联视频）- 可编辑
                    value_video_url = result.get('value_video_url', '') or ''
                    current_video_value = f"{value_video_url}" if value_video_url else "暂无数据"
                    with ui.row().classes('w-full gap-2 items-center mb-2'):
                        ui.icon('video_library').classes('text-sm text-red-600')
                        ui.label('关联视频:').classes('text-sm font-medium')
                        video_input = ui.input(
                            # label=current_video_value, 
                            placeholder='请输入新的视频URL', 
                            value=current_video_value  # 回显已编辑的值
                        ).classes('text-sm flex-grow').props('dense')
                        current_input_refs['value_video_url'] = video_input
                
                # 右侧卡片 - 数据信息
                with ui.card().classes('flex-1 p-4'):
                    ui.label('元数据信息').classes('text-subtitle1 font-medium mb-3')
                    
                    # data_url（数据API）- 可编辑
                    data_url = result.get('data_url', '') or ''
                    current_data_url_value = f"{data_url}" if data_url else "暂无数据"
                    with ui.row().classes('w-full gap-2 items-center mb-2'):
                        ui.icon('api').classes('text-sm text-purple-600')
                        ui.label('数据API:').classes('text-sm font-medium')
                        data_url_input = ui.input(
                            # label=current_data_url_value, 
                            placeholder='请输入新的数据API', 
                            value=current_data_url_value  # 回显已编辑的值
                        ).classes('text-sm flex-grow').props('dense')
                        current_input_refs['data_url'] = data_url_input
                    
                    # encoding（编码方式）- 可编辑
                    encoding = result.get('encoding', '') or ''
                    current_encoding_value = f"{encoding}" if encoding else "暂无数据"
                    with ui.row().classes('w-full gap-2 items-center mb-2'):
                        ui.icon('code').classes('text-sm text-indigo-600')
                        ui.label('编码方式:').classes('text-sm font-medium')
                        encoding_input = ui.input(
                            # label=current_encoding_value, 
                            placeholder='请输入新的编码方式', 
                            value=current_encoding_value  # 回显已编辑的值
                        ).classes('text-sm flex-grow').props('dense')
                        current_input_refs['encoding'] = encoding_input
                    
                    # format（格式）- 可编辑
                    format_val = result.get('format', '') or ''
                    current_format_value = f"{format_val}" if format_val else "暂无数据"
                    with ui.row().classes('w-full gap-2 items-center mb-2'):
                        ui.icon('description').classes('text-sm text-teal-600')
                        ui.label('格式:').classes('text-sm font-medium')
                        format_input = ui.input(
                            # label=current_format_value, 
                            placeholder='请输入新的格式', 
                            value=current_format_value  # 回显已编辑的值
                        ).classes('text-sm flex-grow').props('dense')
                        current_input_refs['format'] = format_input
                    
                    # license（使用许可）- 可编辑
                    license_val = result.get('license', '') or ''
                    current_license_value = f"{license_val}" if license_val else "暂无数据"
                    with ui.row().classes('w-full gap-2 items-center mb-2'):
                        ui.icon('gavel').classes('text-sm text-amber-600')
                        ui.label('使用许可:').classes('text-sm font-medium')
                        license_input = ui.input(
                            # label=current_license_value, 
                            placeholder='请输入新的使用许可', 
                            value=current_license_value  # 回显已编辑的值
                        ).classes('text-sm flex-grow').props('dense')
                        current_input_refs['license'] = license_input
                    
                    # rights（使用权限）- 可编辑
                    rights = result.get('rights', '') or ''
                    current_rights_value = f"{rights}" if rights else "暂无数据"
                    with ui.row().classes('w-full gap-2 items-center mb-2'):
                        ui.icon('security').classes('text-sm text-red-500')
                        ui.label('使用权限:').classes('text-sm font-medium')
                        rights_input = ui.input(
                            # label=current_rights_value, 
                            placeholder='请输入新的使用权限', 
                            value=current_rights_value  # 回显已编辑的值
                        ).classes('text-sm flex-grow').props('dense')
                        current_input_refs['rights'] = rights_input
                    
                    # update_frequency（更新频率）- 可编辑
                    update_frequency = result.get('update_frequency', '') or ''
                    current_freq_value = f"{update_frequency}" if update_frequency else "暂无数据"
                    with ui.row().classes('w-full gap-2 items-center mb-2'):
                        ui.icon('update').classes('text-sm text-blue-500')
                        ui.label('更新频率:').classes('text-sm font-medium')
                        freq_input = ui.input(
                            # label=current_freq_value, 
                            placeholder='请输入新的更新频率', 
                            value=current_freq_value  # 回显已编辑的值
                        ).classes('text-sm flex-grow').props('dense')
                        current_input_refs['update_frequency'] = freq_input
                    
                    # value_dict（数据字典）- 可编辑
                    value_dict = result.get('value_dict', '') or ''
                    current_dict_value = f"{value_dict}" if value_dict else "暂无数据"
                    with ui.row().classes('w-full gap-2 items-center mb-2'):
                        ui.icon('book').classes('text-sm text-green-500')
                        ui.label('数据字典:').classes('text-sm font-medium')
                        dict_input = ui.input(
                            # label=current_dict_value, 
                            placeholder='请输入新的数据字典', 
                            value=current_dict_value  # 回显已编辑的值
                        ).classes('text-sm flex-grow').props('dense')
                        current_input_refs['value_dict'] = dict_input

            async def handle_edit():
                dialog_update_status.set_text('🔄 正在提交修改...')  
                await on_edit_table_results(row_id)  
            # 对话框底部按钮
            with ui.row().classes('w-full justify-end gap-2 mt-4'):
                dialog_update_status = ui.label('').classes('text-body2 text-grey-6')
                ui.button('确认修改', on_click=handle_edit).classes('min-w-[80px]').props('color=primary')
                ui.button('取消编辑', on_click=lambda: dialog.close()).classes('min-w-[80px]')
        dialog.open()
        
    # ----------------- 3、修改逻辑 -----------------
    @safe_protect(name="提交Card编辑结果", error_msg="提交编辑结果失败")
    async def on_edit_card_results():
        global current_original_data, current_input_refs
        # 1. 验证必要的选择信息
        if not search_select.value:
            ui.notify('请先选择企业', type='warning')
            return
        
        # 2. 获取层级路径
        selected_values = hierarchy_selector.selected_values
        if not (selected_values.get("l1") and selected_values.get("l2") and selected_values.get("l3")):
            ui.notify('请先选择完整的层级路径（L1、L2、L3）', type='warning')
            return
        
        # 构建path_code
        path_code = f"{selected_values['l1']}.{selected_values['l2']}.{selected_values['l3']}"
        enterprise_code = search_select.value
        
        # 3. 收集有数据的UI组件 - 简化版
        dict_fields = []
        
        # 遍历每个记录
        for record_index, input_refs in current_input_refs.items():
            # 获取该记录的原始数据
            original_data = current_original_data.get(record_index, {})
            field_code = original_data.get('field_code', '')
            if not field_code:
                continue
            
            # 构建该记录的更新字段
            field_updates = {'field_code': field_code}
            has_changes = False
            
            # 直接检查每个输入框是否有值
            if input_refs.get('value') and input_refs['value'].value.strip():
                field_updates['value'] = input_refs['value'].value.strip()
                has_changes = True
                
            if input_refs.get('value_pic_url') and input_refs['value_pic_url'].value.strip():
                field_updates['value_pic_url'] = input_refs['value_pic_url'].value.strip()
                has_changes = True
                
            if input_refs.get('value_doc_url') and input_refs['value_doc_url'].value.strip():
                field_updates['value_doc_url'] = input_refs['value_doc_url'].value.strip()
                has_changes = True
                
            if input_refs.get('value_video_url') and input_refs['value_video_url'].value.strip():
                field_updates['value_video_url'] = input_refs['value_video_url'].value.strip()
                has_changes = True
                
            if input_refs.get('data_url') and input_refs['data_url'].value.strip():
                field_updates['data_url'] = input_refs['data_url'].value.strip()
                has_changes = True
                
            if input_refs.get('encoding') and input_refs['encoding'].value.strip():
                field_updates['encoding'] = input_refs['encoding'].value.strip()
                has_changes = True
                
            if input_refs.get('format') and input_refs['format'].value.strip():
                field_updates['format'] = input_refs['format'].value.strip()
                has_changes = True
                
            if input_refs.get('license') and input_refs['license'].value.strip():
                field_updates['license'] = input_refs['license'].value.strip()
                has_changes = True
                
            if input_refs.get('rights') and input_refs['rights'].value.strip():
                field_updates['rights'] = input_refs['rights'].value.strip()
                has_changes = True
                
            if input_refs.get('update_frequency') and input_refs['update_frequency'].value.strip():
                field_updates['update_frequency'] = input_refs['update_frequency'].value.strip()
                has_changes = True
                
            if input_refs.get('value_dict') and input_refs['value_dict'].value.strip():
                field_updates['value_dict'] = input_refs['value_dict'].value.strip()
                has_changes = True

            # 如果有修改的字段，添加到dict_fields
            if has_changes:
                dict_fields.append(field_updates)
        
        # 4. 验证是否有修改的数据
        if not dict_fields:
            ui.notify('没有检测到任何修改的数据', type='info')
            return
        
        # 5. 调用API进行更新
        try:
            # 显示加载状态
            query_status.set_text('🔄 正在提交修改...')               
            log_info(f"开始提交字段编辑: enterprise_code={enterprise_code}, path_code={path_code}, fields_count={len(dict_fields)}")
            # 调用API
            print(enterprise_code,path_code,field_updates)
            await call_edit_field_api(enterprise_code,path_code,dict_fields)
        except Exception as e:
            query_status.set_text('❌ 提交过程发生异常')
            ui.notify('提交过程发生异常，请稍后重试', type='negative')
            log_error("字段编辑提交异常", exception=e)
    
    async def on_edit_table_results(row_id):
        global current_original_data, current_input_refs

        selected_values = hierarchy_selector.selected_values
        if not (selected_values.get("l1") and selected_values.get("l2") and selected_values.get("l3")):
            ui.notify('请先选择完整的层级路径（L1、L2、L3）', type='warning')
            return
        # 构建path_code
        path_code = f"{selected_values['l1']}.{selected_values['l2']}.{selected_values['l3']}"
        enterprise_code = search_select.value

        dict_fields = []
        current_original_item = current_original_data[row_id]
        # 构建该记录的更新字段
        field_code = current_original_item.get('field_code', '')
        if not field_code:
            ui.notify("未发现filed code")
            return
        field_updates = {'field_code': field_code}
        has_changes = False
        
        # 直接检查每个输入框是否有值
        # dialog_update_status.set_text('🔄 正在提交修改...')  
        if current_input_refs['value'].value != current_original_item['value']:
            field_updates['value'] = current_input_refs['value'].value
            has_changes = True
            
        if current_input_refs['value_pic_url'].value != current_original_item['value_pic_url']:
            field_updates['value_pic_url'] = current_input_refs['value_pic_url'].value
            has_changes = True
            
        if current_input_refs.get('value_doc_url').value != current_original_item['value_doc_url']:
            field_updates['value_doc_url'] = current_input_refs['value_doc_url'].value
            has_changes = True
            
        if current_input_refs.get('value_video_url').value != current_original_item['value_video_url']:
            field_updates['value_video_url'] = current_input_refs['value_video_url'].value
            has_changes = True
            
        if current_input_refs.get('data_url').value != current_original_item['data_url']:
            field_updates['data_url'] = current_input_refs['data_url'].value
            has_changes = True
            
        if current_input_refs.get('encoding').value != current_original_item['encoding']:
            field_updates['encoding'] = current_input_refs['encoding'].value
            has_changes = True
            
        if current_input_refs.get('format').value != current_original_item['format']:
            field_updates['format'] = current_input_refs['format'].value
            has_changes = True
            
        if current_input_refs.get('license').value != current_original_item['license']:
            field_updates['license'] = current_input_refs['license'].value
            has_changes = True
            
        if current_input_refs.get('rights').value != current_original_item['rights']:
            field_updates['rights'] = current_input_refs['rights'].value
            has_changes = True
            
        if current_input_refs.get('update_frequency').value != current_original_item['update_frequency']:
            field_updates['update_frequency'] = current_input_refs['update_frequency'].value
            has_changes = True
            
        if current_input_refs.get('value_dict').value != current_original_item['value_dict']:
            field_updates['value_dict'] = current_input_refs['value_dict'].value
            has_changes = True

        # 如果有修改的字段，添加到dict_fields
        if has_changes:
            dict_fields.append(field_updates)
            # ui.notify(dict_fields)
            print(enterprise_code,path_code,field_updates)
            await call_edit_field_api(enterprise_code,path_code,dict_fields)
        else:
            ui.notify("未检测到修改的数据",type='warning')
    
    async def call_edit_field_api(enterprise_code: str, path_code_param: str, dict_fields: list):
        """调用编辑字段API的独立函数"""
        try:
            log_info(f"开始调用编辑字段API", 
                    extra_data=f'{{"enterprise_code": "{enterprise_code}", "path_code_param": "{path_code_param}", "fields_count": {len(dict_fields)}}}')
            
            async with aiohttp.ClientSession() as session:
                request_data = {
                    "enterprise_code": enterprise_code,
                    "path_code_param": path_code_param,
                    "dict_fields": dict_fields
                }
                
                async with session.post(
                    f"{MONGODB_SERVICE_URL}/api/v1/enterprises/edit_field_value",
                    json=request_data,
                    headers={'Content-Type': 'application/json'}
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if data.get('success', False):
                            query_status.set_text(f'✅ 字段更新成功！更新了 {data.get("updated_count", 0)} 个字段')  
                            ui.notify(f'字段更新成功！更新了 {data.get("updated_count", 0)} 个字段', type='positive')
                            log_info(f"字段更新成功: 更新了 {data.get('updated_count', 0)} 个字段")
                            return True
                        else:
                            error_msg = data.get('message', '更新失败')
                            query_status.set_text(f'❌ 更新失败: {error_msg}')  
                            ui.notify(f'更新失败: {error_msg}', type='negative')
                            log_error(f"字段更新API返回失败: {error_msg}")
                            return False
                    else:
                        error_text = await response.text()
                        ui.notify(f'服务器错误 (状态码: {response.status})', type='negative')
                        log_error(f"字段更新API请求失败: status={response.status}, response={error_text}")
                        return False
                        
        except Exception as e:
            ui.notify(f'API调用异常: {str(e)}', type='negative')
            log_error("字段更新API调用异常", exception=e)

    # ----------------- 4、UI布局 -----------------
    with ui.column().classes('w-full gap-6 p-4 items-center'):
        with ui.column().classes('w-full gap-4'):
            ui.label('编辑企业档案').classes('text-h5 font-bold text-primary')
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
                    label='选择企业'
                ).classes('flex-[4]').props('dense')

            # 搜索结果状态标签
            search_status = ui.label('').classes('text-body2 text-grey-6')

            with ui.column().classes('w-full').style('overflow-y: auto;'):
                # hierarchy_selector组件展示
                hierarchy_selector = HierarchySelector(multiple=True)
                hierarchy_selector.render_row()

            with ui.row().classes('w-full justify-start'):
                query_btn=ui.button('查询').classes('min-w-[100px]')
                clear_btn=ui.button('清空').classes('min-w-[100px]')
                query_status = ui.label('').classes('text-body2 text-grey-6')

        # 展示搜索结果
        with ui.column().classes('w-full gap-4'):
            ui.separator()
            results_container = ui.column().classes('w-full gap-4')
        
        initialize_results_display()
            
    # 监听回车键事件
    search_input.on('keydown.enter', lambda: asyncio.create_task(on_search_enter()))
    # 监听输入值变化
    search_input.on_value_change(lambda: asyncio.create_task(on_input_change()))
    # 触发查询按钮事件
    query_btn.on('click', lambda: asyncio.create_task(on_query_enter()))
    # 清空事件触发
    clear_btn.on('click',lambda: on_clear_enter())
    # 可选：监听输入变化，实现实时搜索（防抖）
    search_timer = None
