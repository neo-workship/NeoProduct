"""
创建档案Tab逻辑
企业档案创建功能页面
"""
from nicegui import ui,app
from .hierarchy_selector_component import HierarchySelector
import aiohttp
import asyncio
import re
from datetime import datetime
from common.exception_handler import log_info, log_error, safe_protect
from auth import auth_manager

# MongoDB服务API基础URL
MONGODB_SERVICE_URL = "http://localhost:8001"

@safe_protect(name="创建档案页面", error_msg="创建档案页面加载失败")
def create_archive_content():
    """创建档案内容页面"""
    # ==================== UI设计 ====================
    with ui.column().classes('w-full gap-6 p-4'):
        # ==================== 第一部分：输入区域 ====================
        with ui.column().classes('w-full gap-4'):
            ui.label('创建企业档案').classes('text-h5 font-bold text-primary')
            ui.separator()
            
            # 输入框容器
            input_container = ui.row().classes('w-full gap-4')
            
            with input_container:
                # 统一信用代码输入框
                credit_code_input = ui.input(
                    label='统一信用代码',
                    placeholder='请输入18位统一社会信用代码'
                ).classes('flex-1').props('clearable outlined')
                
                # 企业名称输入框
                enterprise_name_input = ui.input(
                    label='企业名称',
                    placeholder='请输入企业名称'
                ).classes('flex-1').props('clearable outlined')
            
            # 按钮和进度条容器
            button_progress_container = ui.row().classes('w-full gap-4 items-center')
            
            with button_progress_container:
                # 创建档案按钮
                create_button = ui.button(
                    '创建档案',
                    icon='add_business',
                    color='positive'
                ).classes('px-6')
                
                # 进度条 (初始隐藏)
                progress_bar = ui.linear_progress(
                    value=0,
                    show_value=True
                ).classes('flex-1').style('display: none')
                
                # 状态标签
                status_label = ui.label('').classes('text-caption')
        ui.separator()
        
        # ==================== 第二部分：功能卡片区域 ====================
        with ui.row().classes('w-full gap-6 items-stretch'):  
            # ========== 左侧卡片：文档生成器 ==========
            with ui.card().classes('flex-1 p-4'):
                ui.label('全量同步').classes('text-h6 font-medium mb-4')
                with ui.row().classes('w-full gap-4'):
                    # 左侧：控制区域
                    with ui.column().classes('w-full gap-3'):
                        code_input_left = ui.input(
                            label='企业代码',
                            placeholder='企业代码'
                        ).classes('w-full').props('outlined')
                        
                        generate_doc_button = ui.button(
                            '档案同步',
                            icon='description',
                            color='secondary'
                        ).classes('w-full')
                    
                    # 右侧：日志区域
                    with ui.column().classes('w-full'):
                        ui.label('同步日志').classes('text-subtitle2 mb-2')
                        doc_log = ui.log(max_lines=20).classes('w-full h-52 border rounded overflow-y-auto scrollbar-hide')
            
            # ========== 右侧卡片：层级选择器与数据源 ==========
            with ui.card().classes('flex-1 p-4'):
                ui.label('字段同步').classes('text-h6 font-medium mb-4')
                
                code_input_right = ui.input(
                    label='企业代码',
                    placeholder='企业代码'
                ).classes('w-full').props('outlined')

                # 层级选择器 - 使用现有组件
                ui.label('数据分类选择').classes('text-subtitle2 mb-2')
                hierarchy_selector = HierarchySelector()
                hierarchy_selector.render_row()
                
                # 数据源
                ui.label('数据源URL').classes('text-subtitle2 mt-4 mb-2')
                data_api_input = ui.input(
                    label='字段数据源地址',
                    placeholder='输入数据源URL或路径'
                ).classes('w-full') \
                 .props('outlined') \
                 .bind_value_from(hierarchy_selector.selected_values,"data_url")
                
                # 字段同步按钮
                sync_filed_container = ui.row().classes('w-full mt-3 gap-4 items-center')
                with sync_filed_container:
                    sync_filed_button = ui.button(
                        '字段同步',
                        icon='settings',
                        color='accent'
                    ).classes('w-full mt-3')

                    config_progress = ui.circular_progress(
                        value=0,
                        show_value=True,
                        size='sm'
                    ).classes('').style('display: none')
                    config_status_label = ui.label('').classes('text-caption')
    
    # ==================== 事件处理函数 ====================
    @safe_protect(name="执行创建档案操作", error_msg="创建档案失败")
    async def create_archive():
        """创建档案的主要函数"""
        try:
            # 获取输入值
            credit_code = credit_code_input.value.strip() if credit_code_input.value else ""
            enterprise_name = enterprise_name_input.value.strip() if enterprise_name_input.value else ""

            if credit_code and not re.match(r'^[0-9A-HJ-NPQRTUWXY]{2}\d{6}[0-9A-HJ-NPQRTUWXY]{10}$', credit_code):
                ui.notify('请输入正确的18位统一社会信用代码', type='warning')
                return
            
            # 验证输入
            if not credit_code or not enterprise_name:
                ui.notify('请输入统一信用代码与企业名称', type='warning')
                return
            
            # 显示进度条和更新状态
            progress_bar.style('display: block')
            progress_bar.set_value(0)
            status_label.set_text('正在创建档案...')
            create_button.set_enabled(False)
            
            log_info(f"开始创建企业档案", 
                    extra_data=f'{{"enterprise_code": "{credit_code}", "enterprise_name": "{enterprise_name}"}}')
            
            # 模拟进度更新
            for i in range(1, 4):
                progress_bar.set_value(i * 25)
                status_label.set_text(f'正在处理... ({i * 25}%)')
                await asyncio.sleep(0.5)
            
            # 调用MongoDB服务API
            async with aiohttp.ClientSession() as session:
                request_data = {
                    "enterprise_code": credit_code,
                    "enterprise_name": enterprise_name
                }
                
                async with session.post(
                    f"{MONGODB_SERVICE_URL}/api/v1/documents",
                    json=request_data,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    
                    progress_bar.set_value(100)
                    
                    if response.status == 200:
                        result = await response.json()
                        
                        if result.get('success', False):
                            status_label.set_text('创建成功！')
                            
                            ui.notify(
                                f'企业档案创建成功！文档ID: {result.get("document_id")}',
                                type='positive',
                                timeout=5000
                            )
                            
                            # 记录成功日志
                            doc_log.push(f'✅ 档案创建成功: {enterprise_name}')
                            doc_log.push(f'📄 文档ID: {result.get("document_id")}')
                            doc_log.push(f'📊 创建字段数: {result.get("documents_count", 0)}')
                            
                            # 自动填入文档名称
                            code_input_right.set_value(credit_code)
                            code_input_left.set_value(credit_code) 
                            
                            # 清空输入框
                            credit_code_input.set_value('')
                            enterprise_name_input.set_value('')
                            
                            log_info("企业档案创建成功", 
                                    extra_data=f'{{"document_id": "{result.get("document_id")}"}}')
                        else:
                            error_msg = result.get('message', '创建失败')
                            status_label.set_text(f'创建失败: {error_msg}')
                            ui.notify(f'创建失败: {error_msg}', type='negative')
                    else:
                        error_text = await response.text()
                        status_label.set_text('服务器错误')
                        ui.notify(f'服务器错误 ({response.status})', type='negative')
                        log_error(f"API调用失败", extra_data=f'{{"status": {response.status}, "response": "{error_text}"}}')
                        
        except Exception as e:
            progress_bar.set_value(0)
            status_label.set_text('创建失败')
            ui.notify('创建档案时发生错误', type='negative')
            log_error("创建档案异常", exception=e)
        
        finally:
            # 恢复按钮状态，隐藏进度条
            create_button.set_enabled(True)
            await asyncio.sleep(2)  # 显示结果2秒后隐藏进度条
            progress_bar.style('display: none')
    
    #============================ 2、同步文档 ===========================
    @safe_protect(name="企业档案同步操作", error_msg="企业同步失败")
    async def sync_document():
        """生成文档函数 - 修改后的版本"""
        credit_code = code_input_left.value.strip() if code_input_left.value else ""
        
        # 验证输入
        if not credit_code:
            ui.notify('请输入统一信用代码', type='warning')
            return
        
        doc_log.push(f'📝 开始生成文档: {credit_code}')
        doc_log.push(f'⏱️ {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
        
        # 启动异步同步流程
        asyncio.create_task(perform_document_sync(credit_code))

    async def perform_document_sync(credit_code: str):
        """执行文档同步的异步函数"""
        try:
            # 1. 获取层级数据 - 从storage或API获取
            hierarchy_data = await get_hierarchy_data()
            if not hierarchy_data:
                doc_log.push('❌ 无法获取层级数据,请检查API服务')
                return
            doc_log.push('🔧 连接创建API...')
            
            # 2. 遍历hierarchy_selector中的各层级下的fields数组
            fields_to_sync = []
            
            # 从hierarchy_data中提取所有字段
            l1_categories = hierarchy_data.get('l1_categories', [])
            
            for l1 in l1_categories:
                for l2 in l1.get('l2_categories', []):
                    for l3 in l2.get('l3_categories', []):
                        fields = l3.get('fields', [])
                        for field in fields:
                            # 获取字段信息
                            full_path_code = field.get('full_path_code', '')
                            data_url = field.get('data_url', '')
                            field_name = field.get('field_name', '')
                            
                            if full_path_code and field_name:
                                fields_to_sync.append({
                                    'full_path_code': full_path_code,
                                    'data_url': data_url,
                                    'field_name': field_name
                                })
            
            doc_log.push(f'📋 发现 {len(fields_to_sync)} 个字段需要同步')
            
            # 3. 遍历字段并执行同步
            sync_success_count = 0
            sync_error_count = 0
            
            for idx, field_info in enumerate(fields_to_sync):
                full_path_code = field_info['full_path_code']
                data_url = field_info['data_url']
                field_name = field_info['field_name']
                
                # 显示当前同步信息
                doc_log.push(f'🔄 [{idx+1}/{len(fields_to_sync)}] {data_url}{credit_code}')
                
                # 调用MongoDB服务的/api/v1/fields/update API
                try:
                    success = await call_fields_update_api(
                        enterprise_code=credit_code,
                        full_path_code=full_path_code,
                        field_value=field_name  # 这里使用field_name作为默认值，您可能需要根据实际需求修改
                    )
                    
                    if success:
                        sync_success_count += 1
                        doc_log.push(f'✅ {field_name} 同步成功')
                    else:
                        sync_error_count += 1
                        doc_log.push(f'❌ {field_name} 同步失败')
                        
                except Exception as e:
                    sync_error_count += 1
                    doc_log.push(f'⚠️ {field_name} 同步异常: {str(e)}')
                    log_error(f"字段同步异常: {field_name}", exception=e)
                
                # 添加短暂延迟，避免API调用过于频繁
                await asyncio.sleep(0.1)
            
            # 4. 显示同步结果
            doc_log.push(f'✅ 文档同步完成！成功: {sync_success_count}, 失败: {sync_error_count}')
            
            if sync_error_count == 0:
                doc_log.push(f'✅ 文档同步成功！共同步 {sync_success_count} 个字段')
            else:
                doc_log.push(f'❌文档同步完成，成功: {sync_success_count}, 失败: {sync_error_count}')
                
        except Exception as e:
            doc_log.push(f'❌ 同步过程发生异常: {str(e)}')
            log_error("文档同步异常", exception=e)

    async def get_hierarchy_data():
        """获取层级数据 - 优先从app.storage.general获取，否则从API获取"""
        try:
            # 1. 首先尝试从app.storage.general获取
            hierarchy_data = app.storage.general.get('hierarchy_data')
            if hierarchy_data:
                # 检查数据是否过期（可选，这里设置为1小时过期）
                timestamp = app.storage.general.get('hierarchy_data_timestamp', 0)
                current_time = asyncio.get_event_loop().time()
                if current_time - timestamp < 3600:  # 1小时内的数据认为有效
                    log_info("从存储获取层级数据成功")
                    return hierarchy_data
            
            # 2. 如果存储中没有或已过期，从API获取
            log_info("从API获取层级数据")
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{MONGODB_SERVICE_URL}/api/v1/hierarchy") as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # 检查响应格式
                        if isinstance(data, dict) and data.get('success', False):
                            hierarchy_data = data.get('data', {})
                            
                            # 缓存到storage
                            app.storage.general['hierarchy_data'] = hierarchy_data
                            app.storage.general['hierarchy_data_timestamp'] = asyncio.get_event_loop().time()
                            
                            log_info("API获取层级数据成功并已缓存")
                            return hierarchy_data
                        else:
                            log_error("层级数据响应格式错误", extra_data=f'{{"response": {data}}}')
                            return None
                    else:
                        error_text = await response.text()
                        log_error("获取层级数据API失败", 
                                extra_data=f'{{"status": {response.status}, "response": "{error_text}"}}')
                        return None
                        
        except Exception as e:
            log_error("获取层级数据异常", exception=e)
            return None

    async def call_fields_update_api(enterprise_code: str, full_path_code: str, field_value: str) -> bool:
        """调用MongoDB服务的/api/v1/fields/update API"""
        try:
            # 构建API请求数据
            request_data = {
                "enterprise_code": enterprise_code,
                "full_path_code": full_path_code,
                "dict_fields": {
                    "value": field_value
                }
            }
            
            # 调用API
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{MONGODB_SERVICE_URL}/api/v1/fields/update",
                    json=request_data,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        if result.get('success', False):
                            # 使用API返回的message内容
                            api_message = result.get('message', '字段更新成功')
                            log_info(f"字段更新API调用成功: {api_message}", 
                                    extra_data=f'{{"enterprise_code": "{enterprise_code}", "full_path_code": "{full_path_code}"}}')
                            return True
                        else:
                            # 使用API返回的message内容
                            api_message = result.get('message', '字段更新失败')
                            log_error(f"字段更新API返回失败: {api_message}", 
                                    extra_data=f'{{"enterprise_code": "{enterprise_code}", "full_path_code": "{full_path_code}"}}')
                            # 显示API返回的具体错误信息
                            ui.notify(f'字段更新失败: {api_message}', type='negative')
                            return False
                    else:
                        error_text = await response.text()
                        log_error(f"字段更新API调用失败", 
                                extra_data=f'{{"status": {response.status}, "enterprise_code": "{enterprise_code}", "full_path_code": "{full_path_code}", "response": "{error_text}"}}')
                        # 显示HTTP错误信息
                        ui.notify(f'API调用失败 (状态码: {response.status}): {error_text}', type='negative')
                        return False
                            
        except Exception as e:
            log_error("字段更新API调用异常", exception=e, 
                    extra_data=f'{{"enterprise_code": "{enterprise_code}", "full_path_code": "{full_path_code}"}}')
            ui.notify(f'API调用异常: {str(e)}', type='negative')
            return False

    # ============================ 3、同步字段 ===========================
    @safe_protect(name="字段同步操作", error_msg="字段同步失败")
    async def sync_field():
        """字段同步函数 - 修复版本"""
        try:
            # 获取层级选择器的值和数据源
            selected_values = hierarchy_selector.selected_values
            data_source = data_api_input.value.strip() if data_api_input.value else ""
            credit_code = code_input_right.value.strip() if code_input_right.value else ""

            # 验证输入
            if not data_source or not credit_code or not selected_values:
                ui.notify('请选择数据分类与填写企业代码', type='warning')
                return
            
            # 显示进度指示器
            config_progress.style('display: block')
            config_progress.set_value(0)
            config_status_label.set_text('准备开始...')
            sync_filed_button.set_enabled(False)
            
            log_info(f"开始字段同步", 
                    extra_data=f'{{"data_source": "{data_source}", "selected_values": "{selected_values}"}}')
            
            # 模拟同步进度
            config_progress.set_value(20)
            config_status_label.set_text(f'调用API:{data_source}{credit_code}')
            await asyncio.sleep(0.5)

            success = await call_fields_update_api(
                enterprise_code=credit_code,
                full_path_code=selected_values["full_path_code"],
                field_value=f'更新值_{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
            )
            await asyncio.sleep(0.5)

            if success:
                # 完成同步
                config_progress.set_value(100)
                config_status_label.set_text('✅同步完成！')
                # 使用更具体的成功信息
                ui.notify(f'字段同步成功！企业代码：{credit_code}, 字段路径：{selected_values["full_path_code"]}', type='positive')
                log_info("字段同步成功", 
                    extra_data=f'{{"selected_values": "{selected_values}", "data_source": "{data_source}", "enterprise_code": "{credit_code}"}}')
            else:
                config_progress.set_value(100)
                config_status_label.set_text('❌同步失败！')
                # 错误信息已在call_fields_update_api函数中显示，这里不重复显示
                log_error("字段同步失败", 
                    extra_data=f'{{"selected_values": "{selected_values}", "data_source": "{data_source}", "enterprise_code": "{credit_code}"}}')
            
        except Exception as e:
            config_progress.set_value(0)
            config_status_label.set_text('同步失败')
            ui.notify(f'字段同步时发生错误: {str(e)}', type='negative')
            log_error("字段同步异常", exception=e)
        
        finally:
            # 恢复按钮状态，延迟隐藏进度指示器
            sync_filed_button.set_enabled(True)
            await asyncio.sleep(2)  # 显示结果2秒后隐藏
            config_progress.style('display: none')
            config_status_label.set_text('')
       
    # ==================== 绑定事件 ====================
    create_button.on_click(create_archive)
    generate_doc_button.on_click(sync_document)
    sync_filed_button.on_click(sync_field)
    
    # 初始化日志
    doc_log.push('🚀 准备就绪')