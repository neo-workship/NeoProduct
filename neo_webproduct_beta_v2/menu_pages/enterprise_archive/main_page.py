"""
企业档案主页面
整合4个tab的入口文件
"""
from auth import auth_manager
from auth.decorators import require_permission
from nicegui import ui
from common.exception_handler import safe_protect
from component import static_manager

from .ai_query_tab import create_ai_query_content
from .create_archive_tab import create_archive_content
from .read_archive_tab import read_archive_content
from .edit_archive_tab import edit_archive_content
from .add_archive_filed_tab import add_archive_filed_content
from .delete_archive_tab import delete_archive_content
from .bi_analysis_tab import bi_analysis_content

@safe_protect(name="一企一档", error_msg="一企一档页面加载失败")
def enterprise_archive_content():
    """企业档案主内容"""
    user = auth_manager.current_user
    
    with ui.splitter(value=10).classes('w-full h-full') as splitter:
        with splitter.before:
            with ui.tabs().props('vertical') as tabs:
                ai_query = ui.tab('智能问数', icon='tips_and_updates')
                create_archive = ui.tab('创建档案', icon='precision_manufacturing')
                read_archive = ui.tab('查看档案', icon='plagiarism')
                edit_archive = ui.tab('修改档案', icon='edit_note')
                # add_archive_filed = ui.tab('添加属性', icon='note_add')
                delete_archive = ui.tab('删除档案', icon='delete_forever')
                separate_line = ui.tab('________')
                bi_analysis = ui.tab('BI分析',icon='auto_graph')
                dynamic_analysis = ui.tab("动态分析",icon="stacked_bar_chart")
                analysis_report = ui.tab("智能报告",icon="auto_fix_high")


        with splitter.after:
            with ui.tab_panels(tabs, value=ai_query).props('vertical').classes('w-full h-full'):    
                with ui.tab_panel(ai_query).classes('w-full'):
                    create_ai_query_content()
                with ui.tab_panel(create_archive).classes('w-full'):
                    create_archive_content()
                with ui.tab_panel(read_archive).classes('w-full'):
                    read_archive_content()
                with ui.tab_panel(edit_archive).classes('w-full'):
                    edit_archive_content()
                # with ui.tab_panel(add_archive_filed).classes('w-full'):
                #     add_archive_filed_content()
                with ui.tab_panel(delete_archive).classes('w-full'):
                    delete_archive_content()
                with ui.tab_panel(bi_analysis).classes('w-full'):
                    bi_analysis_content()



