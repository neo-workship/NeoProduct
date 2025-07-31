from nicegui import ui, run
import asyncio

# 全局变量用于存储UI组件引用
progress_bar = None
log_area = None

async def start_process():
    """开始处理流程"""
    if progress_bar:
        progress_bar.value = 0
        # 模拟进度更新
        for i in range(101):
            progress_bar.value = i / 100
            if log_area:
                log_area.push(f'处理进度: {i}%')
            await asyncio.sleep(0.05)  # 模拟处理时间
        
        if log_area:
            log_area.push('处理完成!')

def clear_log():
    """清空日志"""
    if log_area:
        log_area.clear()

def save_config():
    """保存配置"""
    ui.notify('配置已保存', type='positive')

def load_config():
    """加载配置"""
    ui.notify('配置已加载', type='info')

def reset_config():
    """重置配置"""
    ui.notify('配置已重置', type='warning')

# 创建主界面
@ui.page('/')
def main_page():
    global progress_bar, log_area
    
    ui.label('ui.label (标签组件)').classes('text-lg font-bold mb-4')
    
    with ui.card().classes('w-full max-w-4xl mx-auto p-4'):
        # 第一行输入框
        with ui.row().classes('w-full gap-4 mb-4'):
            ui.input('ui.label (基本一般输入框)', placeholder='ui.input').classes('flex-1')
        
        # 第二行输入框
        with ui.row().classes('w-full gap-4 mb-4'):
            ui.input('ui.label (企业名称)', placeholder='ui.input').classes('flex-1')
        
        # 进度条
        with ui.row().classes('w-full gap-4 mb-4'):
            ui.label('ui.linear_progress (进度)').classes('w-32')
            progress_bar = ui.linear_progress(value=0).classes('flex-1')
        
        # ui.label 可以设置
        ui.label('ui.label(可以设置)').classes('text-md font-semibold mb-2')
        
        # 主要内容区域
        with ui.row().classes('w-full gap-4'):
            # 左侧面板
            with ui.card().classes('flex-1 p-4'):
                ui.label('ui.show(主要显示)').classes('text-sm font-medium mb-2')
                
                with ui.column().classes('gap-2'):
                    ui.button('ui.label', on_click=lambda: ui.notify('Label clicked')).classes('w-full')
                    ui.button('ui.button(按钮)', on_click=start_process).classes('w-full')
                
                ui.separator().classes('my-4')
                
                ui.label('ui.log').classes('text-sm font-medium mb-2')
            
            # 右侧面板
            with ui.card().classes('flex-1 p-4'):
                ui.label('ui.show(辅助显示)').classes('text-sm font-medium mb-2')
                
                # 按钮组
                with ui.row().classes('gap-2 mb-4'):
                    ui.button('保存配置', on_click=save_config).classes('text-xs')
                    ui.button('加载配置', on_click=load_config).classes('text-xs')
                    ui.button('重置配置', on_click=reset_config).classes('text-xs')
                    ui.button('清空日志', on_click=clear_log).classes('text-xs')
                
                # 日志显示区域
                ui.label('ui.output(对齐显示)').classes('text-sm font-medium mb-2')
                log_area = ui.log().classes('h-32 w-full border')
                
                ui.separator().classes('my-4')
                
                ui.label('ui.button(辅助)').classes('text-sm font-medium mb-2')

if __name__ in {"__main__", "__mp_main__"}:
    ui.run(title="NiceGUI 全局数据演示", 
           port=8181,
           reload=True,
           prod_js=False,
           show=True
        )