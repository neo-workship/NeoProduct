"""
权限管理页面 - 整合认证逻辑
"""
from nicegui import ui
from ..decorators import require_role

@require_role('admin')
def permission_management_page_content():
    """权限管理页面内容 - 仅管理员可访问"""
    ui.label('权限管理').classes('text-3xl font-bold text-green-800 dark:text-green-200')
    ui.label('管理系统权限和资源访问控制').classes('text-gray-600 dark:text-gray-400 mt-2')

    with ui.card().classes('w-full mt-4'):
        ui.label('权限矩阵').classes('text-lg font-semibold')

        # 权限操作按钮
        with ui.row().classes('gap-2 mt-4'):
            ui.button('添加权限', icon='add').classes('bg-blue-500 text-white')
            ui.button('权限模板', icon='content_copy').classes('bg-green-500 text-white')
            ui.button('导出权限', icon='download').classes('bg-purple-500 text-white')

        # 权限表格（示例数据）
        columns = [
            {'name': 'module', 'label': '模块', 'field': 'module', 'sortable': True, 'align': 'left'},
            {'name': 'permission', 'label': '权限', 'field': 'permission', 'sortable': True, 'align': 'left'},
            {'name': 'description', 'label': '描述', 'field': 'description', 'sortable': False, 'align': 'left'},
            {'name': 'admin', 'label': '管理员', 'field': 'admin', 'align': 'center'},
            {'name': 'user', 'label': '普通用户', 'field': 'user', 'align': 'center'},
            {'name': 'actions', 'label': '操作', 'field': 'actions', 'align': 'center'},
        ]

        rows = [
            {
                'module': '用户管理',
                'permission': '查看用户列表',
                'description': '查看所有用户的基本信息',
                'admin': '✅',
                'user': '❌',
                'actions': '编辑'
            },
            {
                'module': '用户管理',
                'permission': '创建用户',
                'description': '创建新的用户账户',
                'admin': '✅',
                'user': '❌',
                'actions': '编辑'
            },
            {
                'module': '数据分析',
                'permission': '查看仪表板',
                'description': '访问数据分析仪表板',
                'admin': '✅',
                'user': '✅',
                'actions': '编辑'
            },
            {
                'module': '系统设置',
                'permission': '修改系统配置',
                'description': '修改系统参数和配置',
                'admin': '✅',
                'user': '❌',
                'actions': '编辑'
            }
        ]

        ui.table(columns=columns, rows=rows, row_key='permission').classes('w-full mt-4')

    # 权限统计卡片
    with ui.row().classes('gap-4 mt-6'):
        with ui.card().classes('w-48 p-4 bg-gradient-to-r from-blue-500 to-blue-600 text-white'):
            ui.label('总权限数').classes('text-sm opacity-90')
            ui.label('24').classes('text-3xl font-bold')
            ui.icon('security').classes('text-2xl opacity-80')

        with ui.card().classes('w-48 p-4 bg-gradient-to-r from-green-500 to-green-600 text-white'):
            ui.label('已分配权限').classes('text-sm opacity-90')
            ui.label('22').classes('text-3xl font-bold')
            ui.icon('check_circle').classes('text-2xl opacity-80')

        with ui.card().classes('w-48 p-4 bg-gradient-to-r from-orange-500 to-orange-600 text-white'):
            ui.label('未分配权限').classes('text-sm opacity-90')
            ui.label('2').classes('text-3xl font-bold')
            ui.icon('warning').classes('text-2xl opacity-80')
