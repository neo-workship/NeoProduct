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

    # 新增的查询档案数据函数
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
                            await edit_query_results(query_results)
                            
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

    # ----------------------------------------------------------------
    # 在 edit_archive_content 函数末尾添加初始化显示
    def display_empty_state():
        """显示空数据状态"""
        # ui.label('查询结果').classes('text-sm font-bold text-primary mb-4')
        
        with ui.row().classes('w-full gap-4'):
            # 左侧card展示字段信息标题
            with ui.card().classes('flex-1 p-4'):
                ui.label('字段信息').classes('text-subtitle1 font-medium mb-3')
                
                with ui.row().classes('gap-2 items-center mb-2'):
                    ui.icon('label').classes('text-primary')
                    ui.label('字段名称:').classes('font-medium')
                    ui.label('暂无数据').classes('text-body1 text-grey-6')
                
                with ui.row().classes('gap-2 items-center mb-2'):
                    ui.icon('data_object').classes('text-blue-600')
                    ui.label('字段值:').classes('font-medium')
                    ui.label('暂无数据').classes('text-body1 text-grey-6')
                
                with ui.row().classes('gap-2 items-center mb-2'):
                    ui.icon('image').classes('text-green-600')
                    ui.label('关联图片:').classes('font-medium')
                    ui.label('暂无数据').classes('text-body1 text-grey-6')
                
                with ui.row().classes('gap-2 items-center mb-2'):
                    ui.icon('description').classes('text-orange-600')
                    ui.label('关联文档:').classes('font-medium')
                    ui.label('暂无数据').classes('text-body1 text-grey-6')
                
                with ui.row().classes('gap-2 items-center mb-2'):
                    ui.icon('videocam').classes('text-red-600')
                    ui.label('关联视频:').classes('font-medium')
                    ui.label('暂无数据').classes('text-body1 text-grey-6')
            
            # 右侧card展示数据元信息标题
            with ui.card().classes('flex-1 p-4'):
                ui.label('数据元信息').classes('text-subtitle1 font-medium mb-3')
                
                with ui.row().classes('gap-2 items-center mb-2'):
                    ui.icon('api').classes('text-purple-600')
                    ui.label('数据API:').classes('font-medium')
                    ui.label('暂无数据').classes('text-body1 text-grey-6')
                
                with ui.row().classes('gap-2 items-center mb-2'):
                    ui.icon('code').classes('text-teal-600')
                    ui.label('编码方式:').classes('font-medium')
                    ui.label('暂无数据').classes('text-body1 text-grey-6')
                
                with ui.row().classes('gap-2 items-center mb-2'):
                    ui.icon('settings').classes('text-grey-600')
                    ui.label('格式:').classes('font-medium')
                    ui.label('暂无数据').classes('text-body1 text-grey-6')
                
                with ui.row().classes('gap-2 items-center mb-2'):
                    ui.icon('gavel').classes('text-amber-600')
                    ui.label('使用许可:').classes('font-medium')
                    ui.label('暂无数据').classes('text-body1 text-grey-6')
                
                with ui.row().classes('gap-2 items-center mb-2'):
                    ui.icon('security').classes('text-red-500')
                    ui.label('使用权限:').classes('font-medium')
                    ui.label('暂无数据').classes('text-body1 text-grey-6')
                
                with ui.row().classes('gap-2 items-center mb-2'):
                    ui.icon('update').classes('text-blue-500')
                    ui.label('更新频率:').classes('font-medium')
                    ui.label('暂无数据').classes('text-body1 text-grey-6')
                
                with ui.row().classes('gap-2 items-center mb-2'):
                    ui.icon('book').classes('text-green-500')
                    ui.label('数据字典:').classes('font-medium')
                    ui.label('暂无数据').classes('text-body1 text-grey-6') 
    
    # 初始化空数据页面
    def initialize_results_display():
        """初始化结果显示区域 - 显示空数据状态"""
        with results_container:
            display_empty_state()
    
    # results_container 将在上面的布局中定义
    @safe_protect(name="显示要编辑的档案数据", error_msg="显示要编辑档案数据")
    async def edit_query_results(query_results):
        """显示要编辑的查询结果 - 根据数据条数选择不同的显示方式"""
        # 清空结果容器
        results_container.clear()
        edit_all_btn.enable()
        cancel_btn.enable()
        
        # 根据数据条数选择显示方式
        if len(query_results) <= 1:
            # 无数据或只有一条数据时，使用卡片方式显示
            await edit_results_as_cards(query_results)
        else:
            # 多条数据时，使用表格分页方式显示
            await edit_results_as_table(query_results)

    @safe_protect(name="卡片方式显示要修改的档案数据", error_msg="卡片方式显示要修改的档案数据")
    async def edit_results_as_cards(query_results):
        """卡片方式显示要修改的查询结果（无数据或只有一条数据）"""
        with results_container:
            # ui.label('查询结果').classes('text-sm font-bold text-primary mb-4')
            
            if not query_results:
                # 无数据情况，显示空状态（与初始化状态相同）
                display_empty_state()
                return
            
            # 有一条数据时，按现有方式显示
            for i, result in enumerate(query_results):
                with ui.row().classes('w-full gap-4'):
                    # 左侧card展示：full_path_name、value、value_pic_url、value_doc_url、value_video_url
                    with ui.card().classes('flex-1 p-4'):
                        ui.label('字段信息').classes('text-subtitle1 font-medium mb-3')
                        
                        # full_path_name（标题）
                        full_path_name = result.get('full_path_name', '未知字段')
                        ui.label(full_path_name).classes('text-h6 font-bold text-primary mb-2')
                        
                        # value（字段值）
                        value = result.get('value', '暂无数据') or '暂无数据'
                        with ui.row().classes('gap-2 items-center mb-2'):
                            ui.icon('data_object').classes('text-blue-600')
                            ui.label('字段值:').classes('font-medium')
                            ui.input(str(value)).classes('').props('dense')
                        
                        # value_pic_url（字段关联图片）
                        value_pic_url = result.get('value_pic_url', '') or ''
                        with ui.row().classes('gap-2 items-center mb-2'):
                            ui.icon('image').classes('text-green-600')
                            ui.label('关联图片:').classes('font-medium')
                            if value_pic_url:
                                ui.link(value_pic_url, new_tab=True).classes('text-blue-500 underline')
                            else:
                                ui.label('暂无数据').classes('text-body1 text-grey-6')
                        
                        # value_doc_url（字段关联文档）
                        value_doc_url = result.get('value_doc_url', '') or ''
                        with ui.row().classes('gap-2 items-center mb-2'):
                            ui.icon('description').classes('text-orange-600')
                            ui.label('关联文档:').classes('font-medium')
                            if value_doc_url:
                                ui.link(value_doc_url, new_tab=True).classes('text-blue-500 underline')
                            else:
                                ui.label('暂无数据').classes('text-body1 text-grey-6')
                        
                        # value_video_url（字段关联视频）
                        value_video_url = result.get('value_video_url', '') or ''
                        with ui.row().classes('gap-2 items-center mb-2'):
                            ui.icon('videocam').classes('text-red-600')
                            ui.label('关联视频:').classes('font-medium')
                            if value_video_url:
                                ui.link(value_video_url, new_tab=True).classes('text-blue-500 underline')
                            else:
                                ui.label('暂无数据').classes('text-body1 text-grey-6')

                    # 右侧card展示：data_url、encoding、format、license、rights、update_frequency、value_dict
                    with ui.card().classes('flex-1 p-4'):
                        ui.label('数据元信息').classes('text-subtitle1 font-medium mb-3')
                        
                        # data_url（数据API）
                        data_url = result.get('data_url', '') or ''
                        with ui.row().classes('gap-2 items-center mb-2'):
                            ui.icon('api').classes('text-purple-600')
                            ui.label('数据API:').classes('font-medium')
                            if data_url:
                                ui.link(data_url, new_tab=True).classes('text-blue-500 underline')
                            else:
                                ui.label('暂无数据').classes('text-body1 text-grey-6')
                        
                        # encoding（编码方式）
                        encoding = result.get('encoding', '未指定') or '未指定'
                        with ui.row().classes('gap-2 items-center mb-2'):
                            ui.icon('code').classes('text-teal-600')
                            ui.label('编码方式:').classes('font-medium')
                            ui.label(str(encoding)).classes('text-body1')
                        
                        # format（格式）
                        format_info = result.get('format', '未指定') or '未指定'
                        with ui.row().classes('gap-2 items-center mb-2'):
                            ui.icon('settings').classes('text-grey-600')
                            ui.label('格式:').classes('font-medium')
                            ui.label(str(format_info)).classes('text-body1')
                        
                        # license（使用许可）
                        license_info = result.get('license', '未指定') or '未指定'
                        with ui.row().classes('gap-2 items-center mb-2'):
                            ui.icon('gavel').classes('text-amber-600')
                            ui.label('使用许可:').classes('font-medium')
                            ui.label(str(license_info)).classes('text-body1')
                        
                        # rights（使用权限）
                        rights = result.get('rights', '未指定') or '未指定'
                        with ui.row().classes('gap-2 items-center mb-2'):
                            ui.icon('security').classes('text-red-500')
                            ui.label('使用权限:').classes('font-medium')
                            ui.label(str(rights)).classes('text-body1')
                        
                        # update_frequency（更新频率）
                        update_frequency = result.get('update_frequency', '未指定') or '未指定'
                        with ui.row().classes('gap-2 items-center mb-2'):
                            ui.icon('update').classes('text-blue-500')
                            ui.label('更新频率:').classes('font-medium')
                            ui.label(str(update_frequency)).classes('text-body1')
                        
                        # value_dict（数据字典）
                        value_dict = result.get('value_dict', '') or ''
                        with ui.row().classes('gap-2 items-center mb-2'):
                            ui.icon('book').classes('text-green-500')
                            ui.label('数据字典:').classes('font-medium')
                            if value_dict:
                                if isinstance(value_dict, str):
                                    ui.label(value_dict).classes('text-body1')
                                else:
                                    ui.label(str(value_dict)).classes('text-body1')
                            else:
                                ui.label('暂无数据').classes('text-body1 text-grey-6')

    @safe_protect(name="表格方式显示要修改档案数据", error_msg="表格方式显示要修改的档案数据")
    async def edit_results_as_table(query_results):
        """表格方式显示要修改的查询结果（多条数据，分页模式）"""
        with results_container:
            ui.label(f'找到 {len(query_results)} 条数据').classes('text-body2 text-grey-7 mb-4')
            
            # 定义表格列
            columns = [
                {'name': 'field_name', 'label': '字段名称', 'field': 'field_name', 'sortable': True, 'align': 'left'},
                {'name': 'value', 'label': '字段值', 'field': 'value', 'sortable': True, 'align': 'left'},
                {'name': 'encoding', 'label': '编码方式', 'field': 'encoding', 'sortable': True, 'align': 'left'},
                {'name': 'format', 'label': '格式', 'field': 'format', 'sortable': True, 'align': 'left'},
            ]
            
            # 准备行数据
            rows = []
            for i, result in enumerate(query_results):
                row = {
                    'id': i,
                    'field_name': result.get('field_name', '未知字段'),
                    'value': result.get('value', '暂无数据') or '暂无数据',
                    'encoding': result.get('encoding', '未指定') or '未指定',
                    'format': result.get('format', '未指定') or '未指定',
                    # 保存完整的原始数据用于展开行
                    '_raw_data': result
                }
                rows.append(row)
            
            # 创建表格
            table = ui.table(
                columns=columns, 
                rows=rows, 
                row_key='id',
                pagination=10  # 每页显示10条
            ).classes('w-full')
            
            # 添加表头（包含展开按钮列）
            table.add_slot('header', r'''
                <q-tr :props="props">
                    <q-th auto-width />
                    <q-th v-for="col in props.cols" :key="col.name" :props="props">
                        {{ col.label }}
                    </q-th>
                </q-tr>
            ''')
            
            # 添加表格主体（包含展开功能）
            table.add_slot('body', r'''
                <q-tr :props="props">
                    <q-td auto-width>
                        <q-btn size="sm" color="accent" round dense
                            @click="props.expand = !props.expand"
                            :icon="props.expand ? 'remove' : 'add'" />
                    </q-td>
                    <q-td v-for="col in props.cols" :key="col.name" :props="props">
                        <div style="max-width: 200px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                            {{ col.value }}
                        </div>
                    </q-td>
                </q-tr>
                <q-tr v-show="props.expand" :props="props">
                    <q-td colspan="100%">
                        <div class="text-left q-pa-md">
                            <div class="row q-col-gutter-md">
                                <!-- 左侧：字段信息 -->
                                <div class="col-6">
                                    <div class="text-h6 text-primary q-mb-md">字段信息</div>
                                    
                                    <div class="q-mb-sm">
                                        <q-icon name="label" color="primary" class="q-mr-sm" />
                                        <span class="text-weight-medium">字段名称：</span>
                                        <span>{{ props.row._raw_data.full_path_name || '未知字段' }}</span>
                                    </div>
                                    
                                    <div class="q-mb-sm">
                                        <q-icon name="data_object" color="blue-6" class="q-mr-sm" />
                                        <span class="text-weight-medium">字段值：</span>
                                        <span>{{ props.row._raw_data.value || '暂无数据' }}</span>
                                    </div>
                                    
                                    <div class="q-mb-sm" v-if="props.row._raw_data.value_pic_url">
                                        <q-icon name="image" color="green-6" class="q-mr-sm" />
                                        <span class="text-weight-medium">关联图片：</span>
                                        <a :href="props.row._raw_data.value_pic_url" target="_blank" class="text-blue-500">查看图片</a>
                                    </div>
                                    <div class="q-mb-sm" v-else>
                                        <q-icon name="image" color="green-6" class="q-mr-sm" />
                                        <span class="text-weight-medium">关联图片：</span>
                                        <span class="text-grey-6">暂无数据</span>
                                    </div>
                                    
                                    <div class="q-mb-sm" v-if="props.row._raw_data.value_doc_url">
                                        <q-icon name="description" color="orange-6" class="q-mr-sm" />
                                        <span class="text-weight-medium">关联文档：</span>
                                        <a :href="props.row._raw_data.value_doc_url" target="_blank" class="text-blue-500">查看文档</a>
                                    </div>
                                    <div class="q-mb-sm" v-else>
                                        <q-icon name="description" color="orange-6" class="q-mr-sm" />
                                        <span class="text-weight-medium">关联文档：</span>
                                        <span class="text-grey-6">暂无数据</span>
                                    </div>
                                    
                                    <div class="q-mb-sm" v-if="props.row._raw_data.value_video_url">
                                        <q-icon name="videocam" color="red-6" class="q-mr-sm" />
                                        <span class="text-weight-medium">关联视频：</span>
                                        <a :href="props.row._raw_data.value_video_url" target="_blank" class="text-blue-500">查看视频</a>
                                    </div>
                                    <div class="q-mb-sm" v-else>
                                        <q-icon name="videocam" color="red-6" class="q-mr-sm" />
                                        <span class="text-weight-medium">关联视频：</span>
                                        <span class="text-grey-6">暂无数据</span>
                                    </div>
                                </div>
                                
                                <!-- 右侧：数据元信息 -->
                                <div class="col-6">
                                    <div class="text-h6 text-primary q-mb-md">数据元信息</div>
                                    
                                    <div class="q-mb-sm" v-if="props.row._raw_data.data_url">
                                        <q-icon name="api" color="purple-6" class="q-mr-sm" />
                                        <span class="text-weight-medium">数据API：</span>
                                        <a :href="props.row._raw_data.data_url" target="_blank" class="text-blue-500">查看API</a>
                                    </div>
                                    <div class="q-mb-sm" v-else>
                                        <q-icon name="api" color="purple-6" class="q-mr-sm" />
                                        <span class="text-weight-medium">数据API：</span>
                                        <span class="text-grey-6">暂无数据</span>
                                    </div>
                                    
                                    <div class="q-mb-sm">
                                        <q-icon name="code" color="teal-6" class="q-mr-sm" />
                                        <span class="text-weight-medium">编码方式：</span>
                                        <span>{{ props.row._raw_data.encoding || '未指定' }}</span>
                                    </div>
                                    
                                    <div class="q-mb-sm">
                                        <q-icon name="settings" color="grey-6" class="q-mr-sm" />
                                        <span class="text-weight-medium">格式：</span>
                                        <span>{{ props.row._raw_data.format || '未指定' }}</span>
                                    </div>
                                    
                                    <div class="q-mb-sm">
                                        <q-icon name="gavel" color="amber-6" class="q-mr-sm" />
                                        <span class="text-weight-medium">使用许可：</span>
                                        <span>{{ props.row._raw_data.license || '未指定' }}</span>
                                    </div>
                                    
                                    <div class="q-mb-sm">
                                        <q-icon name="security" color="red-5" class="q-mr-sm" />
                                        <span class="text-weight-medium">使用权限：</span>
                                        <span>{{ props.row._raw_data.rights || '未指定' }}</span>
                                    </div>
                                    
                                    <div class="q-mb-sm">
                                        <q-icon name="update" color="blue-5" class="q-mr-sm" />
                                        <span class="text-weight-medium">更新频率：</span>
                                        <span>{{ props.row._raw_data.update_frequency || '未指定' }}</span>
                                    </div>
                                    
                                    <div class="q-mb-sm" v-if="props.row._raw_data.value_dict">
                                        <q-icon name="book" color="green-5" class="q-mr-sm" />
                                        <span class="text-weight-medium">数据字典：</span>
                                        <span>{{ props.row._raw_data.value_dict }}</span>
                                    </div>
                                    <div class="q-mb-sm" v-else>
                                        <q-icon name="book" color="green-5" class="q-mr-sm" />
                                        <span class="text-weight-medium">数据字典：</span>
                                        <span class="text-grey-6">暂无数据</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </q-td>
                </q-tr>
            ''')         

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
            with ui.row().classes("w-full justify-end"):
                edit_all_btn = ui.button("全部修改").classes('min-w-[100px] disabled')
                cancel_btn = ui.button("取消修改").classes('min-w-[100px] disabled')
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
