"""
创建档案Tab逻辑
企业档案创建功能页面
"""
from nicegui import ui
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
        with ui.row().classes('w-full gap-6'):
            
            # ========== 左侧卡片：文档生成器 ==========
            with ui.card().classes('flex-1 p-4'):
                ui.label('全量同步').classes('text-h6 font-medium mb-4')
                
                with ui.row().classes('w-full gap-4'):
                    # 左侧：控制区域
                    with ui.column().classes('w-full gap-3'):
                        code_input_right = ui.input(
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
                        doc_log = ui.log().classes('w-full h-32 border rounded overflow-y-auto scrollbar-hide')
            
            # ========== 右侧卡片：层级选择器与数据源 ==========
            with ui.card().classes('flex-1 p-4'):
                ui.label('字段同步').classes('text-h6 font-medium mb-4')
                
                code_input_left = ui.input(
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
            if not credit_code:
                ui.notify('请输入统一信用代码', type='warning')
                return
            
            if not enterprise_name:
                ui.notify('请输入企业名称', type='warning')
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
    
    def sync_document():
        """生成文档函数"""
        doc_name = code_input_right.value.strip() if code_input_right.value else "默认文档"
        doc_log.push(f'📝 开始生成文档: {doc_name}')
        doc_log.push(f'⏱️ {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
        
        # 模拟文档生成过程
        ui.timer(1.0, lambda: doc_log.push('🔧 连接创建API...'), once=True)
        ui.timer(2.0, lambda: doc_log.push('📋 正在填充数据...'), once=True)
        ui.timer(3.0, lambda: doc_log.push('✅ 文档生成完成'), once=True)
        
        ui.notify(f'开始生成文档: {doc_name}', type='info')
    
    @safe_protect(name="字段同步操作", error_msg="字段同步失败")
    async def sync_field():
        """字段同步函数"""
        try:
            # 获取层级选择器的值和数据源
            selected_values = hierarchy_selector.selected_values
            # data_api_input.set_value(selected_values["data_url"])
            data_source = data_api_input.value.strip() if data_api_input.value else ""
            
            # 验证输入
            if not data_source:
                ui.notify('请输入数据源地址', type='warning')
                return
            
            if not selected_values:
                ui.notify('请选择数据分类', type='warning')
                return
            
            # 显示进度指示器
            config_progress.style('display: block')
            config_progress.set_value(0)
            config_status_label.set_text('正在连接数据源...')
            sync_filed_button.set_enabled(False)
            
            log_info(f"开始字段同步", 
                    extra_data=f'{{"data_source": "{data_source}", "selected_values": "{selected_values}"}}')
            
            # 模拟同步进度
            for i in range(1, 5):
                config_progress.set_value(i * 20)
                if i == 1:
                    config_status_label.set_text('验证数据源...')
                elif i == 2:
                    config_status_label.set_text('分析字段结构...')
                elif i == 3:
                    config_status_label.set_text('映射字段关系...')
                elif i == 4:
                    config_status_label.set_text('应用配置...')
                
                await asyncio.sleep(0.8)  # 模拟处理时间
            
            # 完成同步
            config_progress.set_value(100)
            config_status_label.set_text('同步完成！')
            
            ui.notify(f'字段同步成功！选择层级：{selected_values}', type='positive')
            
            # 可以在这里添加实际的同步逻辑
            # await perform_actual_sync(selected_values, data_source)
            
            log_info("字段同步成功", 
                    extra_data=f'{{"selected_values": "{selected_values}", "data_source": "{data_source}"}}')
            
        except Exception as e:
            config_progress.set_value(0)
            config_status_label.set_text('同步失败')
            ui.notify('字段同步时发生错误', type='negative')
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