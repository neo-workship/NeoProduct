#!/usr/bin/env python3
"""
NiceGUI刷新机制(@ui.refreshable)示例
演示如何使用@ui.refreshable装饰器实现响应式更新
"""

from nicegui import ui
import random
from datetime import datetime
from typing import List, Dict, Any
import asyncio

# ====== 共享数据源 ======
shared_data = {
    'users': [
        {'id': 1, 'name': '张三', 'age': 25, 'score': 85, 'status': 'active'},
        {'id': 2, 'name': '李四', 'age': 30, 'score': 92, 'status': 'active'},
        {'id': 3, 'name': '王五', 'age': 28, 'score': 78, 'status': 'inactive'},
    ],
    'products': [
        {'id': 1, 'name': 'Python编程书', 'price': 59.9, 'stock': 10},
        {'id': 2, 'name': 'JavaScript指南', 'price': 49.9, 'stock': 5},
        {'id': 3, 'name': '数据结构算法', 'price': 69.9, 'stock': 8},
    ],
    'settings': {
        'theme': 'light',
        'language': 'zh',
        'show_inactive': False,
        'filter_text': '',
        'sort_by': 'name'
    },
    'notifications': [],
    'stats': {'total_users': 3, 'active_users': 2, 'total_sales': 0}
}


def create_basic_refreshable_demo():
    """基础刷新机制演示"""
    
    ui.markdown("## 🔄 基础刷新机制演示")
    
    with ui.card().classes('w-full max-w-4xl mb-6'):
        ui.label("@ui.refreshable装饰器可以让组件在数据变化时自动重新渲染").classes('text-sm text-gray-600 mb-4')
        
        with ui.row().classes('w-full gap-4'):
            
            # 左侧：控制面板
            with ui.column().classes('flex-1'):
                ui.label("🎮 控制面板").classes('text-lg font-bold mb-3')
                
                # 计数器控制
                counter_value = {'count': 0}
                
                @ui.refreshable
                def counter_display():
                    """可刷新的计数器显示"""
                    with ui.card().classes('p-4 text-center bg-blue-50'):
                        ui.label("实时计数器").classes('text-lg font-bold mb-2')
                        ui.label(f"当前值: {counter_value['count']}").classes('text-3xl font-bold text-blue-600')
                        
                        # 根据数值显示不同的状态
                        if counter_value['count'] > 10:
                            ui.icon('trending_up').classes('text-green-500 text-2xl')
                            ui.label("计数较高").classes('text-green-600')
                        elif counter_value['count'] > 5:
                            ui.icon('trending_flat').classes('text-orange-500 text-2xl')
                            ui.label("计数中等").classes('text-orange-600')
                        else:
                            ui.icon('trending_down').classes('text-red-500 text-2xl')
                            ui.label("计数较低").classes('text-red-600')
                
                counter_display()  # 初始显示
                
                # 控制按钮
                with ui.row().classes('gap-2 mt-3'):
                    ui.button("+1", on_click=lambda: increment_counter(1)).props('color=positive')
                    ui.button("+5", on_click=lambda: increment_counter(5)).props('color=positive')
                    ui.button("-1", on_click=lambda: increment_counter(-1)).props('color=negative')
                    ui.button("重置", on_click=lambda: reset_counter()).props('color=warning')
                    ui.button("随机", on_click=lambda: random_counter()).props('color=info')
                
                def increment_counter(amount):
                    counter_value['count'] += amount
                    counter_display.refresh()  # 触发刷新
                
                def reset_counter():
                    counter_value['count'] = 0
                    counter_display.refresh()
                
                def random_counter():
                    counter_value['count'] = random.randint(0, 20)
                    counter_display.refresh()
            
            # 右侧：动态列表
            with ui.column().classes('flex-1'):
                ui.label("📋 动态列表").classes('text-lg font-bold mb-3')
                
                @ui.refreshable
                def dynamic_list():
                    """可刷新的动态列表"""
                    with ui.card().classes('p-4 bg-green-50'):
                        ui.label("随机数列表").classes('text-lg font-bold mb-2')
                        
                        # 生成随机数列表
                        random_numbers = [random.randint(1, 100) for _ in range(5)]
                        
                        for i, num in enumerate(random_numbers):
                            with ui.row().classes('items-center gap-2 mb-1'):
                                ui.label(f"#{i+1}").classes('w-8 text-center')
                                ui.linear_progress(num/100).classes('flex-1')
                                ui.label(f"{num}").classes('w-12 text-right font-bold')
                
                dynamic_list()  # 初始显示
                
                ui.button("刷新列表", on_click=lambda: dynamic_list.refresh()).props('color=primary').classes('mt-3')


def create_data_table_demo():
    """数据表格刷新演示"""
    
    ui.markdown("## 📊 数据表格刷新演示")
    
    with ui.card().classes('w-full max-w-4xl mb-6'):
        ui.label("演示表格数据的动态更新和过滤").classes('text-sm text-gray-600 mb-4')
        
        # 表格列定义
        user_columns = [
            {'name': 'id', 'label': 'ID', 'field': 'id', 'required': True, 'align': 'center'},
            {'name': 'name', 'label': '姓名', 'field': 'name', 'sortable': True},
            {'name': 'age', 'label': '年龄', 'field': 'age', 'sortable': True},
            {'name': 'score', 'label': '分数', 'field': 'score', 'sortable': True},
            {'name': 'status', 'label': '状态', 'field': 'status'},
        ]
        
        with ui.row().classes('w-full gap-4'):
            
            # 左侧：过滤控制
            with ui.column().classes('w-80'):
                ui.label("🔍 过滤控制").classes('text-lg font-bold mb-3')
                
                # 搜索框
                search_input = ui.input("搜索用户", 
                                      value=shared_data['settings']['filter_text']).classes('mb-2')
                
                # 状态过滤
                show_inactive = ui.switch("显示非活跃用户", 
                                        value=shared_data['settings']['show_inactive']).classes('mb-2')
                
                # 排序选择
                sort_select = ui.select(
                    options=['name', 'age', 'score'],
                    value=shared_data['settings']['sort_by'],
                    label="排序字段"
                ).classes('mb-3')
                
                # 数据操作按钮
                ui.label("📝 数据操作").classes('text-lg font-bold mb-2')
                
                with ui.column().classes('gap-2'):
                    ui.button("添加用户", on_click=lambda: add_random_user()).props('color=positive size=sm')
                    ui.button("删除最后一个", on_click=lambda: remove_last_user()).props('color=negative size=sm')
                    ui.button("随机分数", on_click=lambda: randomize_scores()).props('color=info size=sm')
                    ui.button("切换状态", on_click=lambda: toggle_status()).props('color=warning size=sm')
            
            # 右侧：数据表格
            with ui.column().classes('flex-1'):
                ui.label("👥 用户列表").classes('text-lg font-bold mb-3')
                
                # 先定义数据过滤函数
                def get_filtered_users():
                    """获取过滤后的用户数据"""
                    users = shared_data['users'].copy()
                    
                    # 文本过滤
                    filter_text = shared_data['settings']['filter_text'].lower()
                    if filter_text:
                        users = [u for u in users if filter_text in u['name'].lower()]
                    
                    # 状态过滤
                    if not shared_data['settings']['show_inactive']:
                        users = [u for u in users if u['status'] == 'active']
                    
                    # 排序
                    sort_by = shared_data['settings']['sort_by']
                    users.sort(key=lambda x: x[sort_by])
                    
                    return users
                
                @ui.refreshable
                def user_table():
                    """可刷新的用户表格"""
                    # 获取过滤后的数据
                    filtered_users = get_filtered_users()
                    
                    if not filtered_users:
                        with ui.card().classes('p-8 text-center'):
                            ui.icon('search_off').classes('text-4xl text-gray-400 mb-2')
                            ui.label("没有找到匹配的用户").classes('text-gray-500')
                    else:
                        # 显示统计信息
                        with ui.row().classes('gap-4 mb-3'):
                            ui.badge(f"总计: {len(filtered_users)}", color='blue')
                            active_count = len([u for u in filtered_users if u['status'] == 'active'])
                            ui.badge(f"活跃: {active_count}", color='green')
                            avg_score = sum(u['score'] for u in filtered_users) / len(filtered_users)
                            ui.badge(f"平均分: {avg_score:.1f}", color='orange')
                        
                        # 显示表格
                        table = ui.table(
                            columns=user_columns,
                            rows=filtered_users,
                            selection='single'
                        ).classes('w-full')
                        
                        # 表格样式定制
                        table.add_slot('body-cell-status', '''
                            <q-td :props="props">
                                <q-badge :color="props.value === 'active' ? 'green' : 'grey'">
                                    {{ props.value === 'active' ? '活跃' : '非活跃' }}
                                </q-badge>
                            </q-td>
                        ''')
                
                user_table()  # 初始显示
                
                # 绑定事件处理
                def on_search_change():
                    shared_data['settings']['filter_text'] = search_input.value
                    user_table.refresh()
                
                def on_filter_change():
                    shared_data['settings']['show_inactive'] = show_inactive.value
                    user_table.refresh()
                
                def on_sort_change():
                    shared_data['settings']['sort_by'] = sort_select.value
                    user_table.refresh()
                
                search_input.on('input', on_search_change)
                show_inactive.on('update:model-value', on_filter_change)
                sort_select.on('update:model-value', on_sort_change)
        
        # 数据操作函数
        def add_random_user():
            names = ['赵六', '孙七', '周八', '吴九', '郑十']
            new_id = max(u['id'] for u in shared_data['users']) + 1
            new_user = {
                'id': new_id,
                'name': random.choice(names),
                'age': random.randint(20, 40),
                'score': random.randint(60, 100),
                'status': random.choice(['active', 'inactive'])
            }
            shared_data['users'].append(new_user)
            user_table.refresh()
            add_notification(f"已添加用户: {new_user['name']}")
        
        def remove_last_user():
            if shared_data['users']:
                removed = shared_data['users'].pop()
                user_table.refresh()
                add_notification(f"已删除用户: {removed['name']}")
        
        def randomize_scores():
            for user in shared_data['users']:
                user['score'] = random.randint(60, 100)
            user_table.refresh()
            add_notification("已随机化所有用户分数")
        
        def toggle_status():
            for user in shared_data['users']:
                user['status'] = 'inactive' if user['status'] == 'active' else 'active'
            user_table.refresh()
            add_notification("已切换所有用户状态")


def create_complex_refreshable_demo():
    """复杂刷新场景演示"""
    
    ui.markdown("## ⚡ 复杂刷新场景演示")
    
    with ui.card().classes('w-full max-w-4xl mb-6'):
        ui.label("演示多个相互关联的可刷新组件").classes('text-sm text-gray-600 mb-4')
        
        # 仪表板数据
        dashboard_data = {
            'sales': [
                {'month': '1月', 'amount': 12000},
                {'month': '2月', 'amount': 15000},
                {'month': '3月', 'amount': 18000},
            ],
            'kpi': {'revenue': 45000, 'orders': 156, 'customers': 89}
        }
        
        with ui.row().classes('w-full gap-4'):
            
            # 左侧：KPI卡片
            with ui.column().classes('flex-1'):
                ui.label("📈 关键指标").classes('text-lg font-bold mb-3')
                
                @ui.refreshable
                def kpi_cards():
                    """可刷新的KPI卡片"""
                    kpi = dashboard_data['kpi']
                    
                    # 收入卡片
                    with ui.card().classes('p-4 mb-2 bg-gradient-to-r from-blue-400 to-blue-600 text-white'):
                        ui.label("总收入").classes('text-sm opacity-80')
                        ui.label(f"¥{kpi['revenue']:,}").classes('text-2xl font-bold')
                        ui.icon('attach_money').classes('text-3xl opacity-60')
                    
                    # 订单卡片
                    with ui.card().classes('p-4 mb-2 bg-gradient-to-r from-green-400 to-green-600 text-white'):
                        ui.label("总订单").classes('text-sm opacity-80')
                        ui.label(f"{kpi['orders']}").classes('text-2xl font-bold')
                        ui.icon('shopping_cart').classes('text-3xl opacity-60')
                    
                    # 客户卡片
                    with ui.card().classes('p-4 bg-gradient-to-r from-purple-400 to-purple-600 text-white'):
                        ui.label("客户数").classes('text-sm opacity-80')
                        ui.label(f"{kpi['customers']}").classes('text-2xl font-bold')
                        ui.icon('people').classes('text-3xl opacity-60')
                
                kpi_cards()  # 初始显示
            
            # 右侧：销售图表
            with ui.column().classes('flex-1'):
                ui.label("📊 销售趋势").classes('text-lg font-bold mb-3')
                
                @ui.refreshable
                def sales_chart():
                    """可刷新的销售图表"""
                    # 使用matplotlib创建简单图表
                    try:
                        import matplotlib.pyplot as plt
                        from io import BytesIO
                        import base64
                        
                        # 创建图表
                        fig, ax = plt.subplots(figsize=(6, 4))
                        months = [item['month'] for item in dashboard_data['sales']]
                        amounts = [item['amount'] for item in dashboard_data['sales']]
                        
                        ax.plot(months, amounts, marker='o', linewidth=2, markersize=8)
                        ax.set_title('月度销售趋势')
                        ax.set_ylabel('销售额 (¥)')
                        ax.grid(True, alpha=0.3)
                        
                        # 转换为base64
                        buffer = BytesIO()
                        plt.savefig(buffer, format='png', bbox_inches='tight', dpi=100)
                        buffer.seek(0)
                        image_base64 = base64.b64encode(buffer.getvalue()).decode()
                        plt.close()
                        
                        # 显示图表
                        ui.html(f'<img src="data:image/png;base64,{image_base64}" style="width: 100%;">')
                        
                    except ImportError:
                        # 如果没有matplotlib，显示文本表格
                        with ui.card().classes('p-4'):
                            ui.label("销售数据").classes('font-bold mb-2')
                            for item in dashboard_data['sales']:
                                with ui.row().classes('justify-between mb-1'):
                                    ui.label(item['month'])
                                    ui.label(f"¥{item['amount']:,}").classes('font-bold')
                
                sales_chart()  # 初始显示
        
        # 操作按钮
        ui.separator().classes('my-4')
        with ui.row().classes('gap-2'):
            ui.button("模拟销售", on_click=lambda: simulate_sale()).props('color=positive')
            ui.button("添加月份", on_click=lambda: add_month()).props('color=primary')
            ui.button("重置数据", on_click=lambda: reset_dashboard()).props('color=warning')
        
        def simulate_sale():
            """模拟销售"""
            sale_amount = random.randint(1000, 5000)
            dashboard_data['kpi']['revenue'] += sale_amount
            dashboard_data['kpi']['orders'] += 1
            if random.random() > 0.7:  # 30%概率新客户
                dashboard_data['kpi']['customers'] += 1
            
            kpi_cards.refresh()
            add_notification(f"新增销售: ¥{sale_amount}")
        
        def add_month():
            """添加新月份"""
            month_num = len(dashboard_data['sales']) + 1
            new_amount = random.randint(10000, 25000)
            dashboard_data['sales'].append({
                'month': f'{month_num}月',
                'amount': new_amount
            })
            sales_chart.refresh()
            add_notification(f"添加{month_num}月数据: ¥{new_amount}")
        
        def reset_dashboard():
            """重置仪表板"""
            dashboard_data['kpi'] = {'revenue': 45000, 'orders': 156, 'customers': 89}
            dashboard_data['sales'] = [
                {'month': '1月', 'amount': 12000},
                {'month': '2月', 'amount': 15000},
                {'month': '3月', 'amount': 18000},
            ]
            kpi_cards.refresh()
            sales_chart.refresh()
            add_notification("仪表板数据已重置")


def create_notification_system():
    """通知系统"""
    
    ui.separator().classes('my-6')
    ui.markdown("## 🔔 实时通知系统")
    
    with ui.card().classes('w-full max-w-4xl'):
        
        @ui.refreshable
        def notification_list():
            """可刷新的通知列表"""
            if not shared_data['notifications']:
                ui.label("暂无通知").classes('text-gray-500 text-center p-4')
            else:
                for i, notif in enumerate(shared_data['notifications'][-10:]):  # 显示最新10条
                    with ui.card().classes('p-3 mb-2 bg-blue-50'):
                        with ui.row().classes('items-center gap-2'):
                            ui.icon('info').classes('text-blue-500')
                            ui.label(notif['message']).classes('flex-1')
                            ui.label(notif['time']).classes('text-xs text-gray-500')
        
        notification_list()  # 初始显示
        
        ui.button("清空通知", on_click=lambda: clear_notifications()).props('color=warning size=sm').classes('mt-3')
        
        def clear_notifications():
            shared_data['notifications'].clear()
            notification_list.refresh()


def add_notification(message: str):
    """添加通知"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    shared_data['notifications'].append({
        'message': message,
        'time': timestamp
    })
    # 这里应该调用notification_list.refresh()，但由于作用域问题，在实际应用中需要更好的设计


def main():
    """主演示函数"""
    
    # 页面标题和样式
    ui.page_title("NiceGUI 刷新机制演示")
    
    with ui.column().classes('w-full items-center p-4'):
        ui.markdown("# 🔄 NiceGUI 刷新机制 (@ui.refreshable) 演示")
        ui.label("学习如何使用@ui.refreshable装饰器实现响应式更新").classes('text-lg text-gray-600 mb-6')
        
        create_basic_refreshable_demo()
        create_data_table_demo()
        create_complex_refreshable_demo()
        create_notification_system()
        
        # 说明文档
        ui.separator().classes('my-6')
        with ui.expansion("📚 @ui.refreshable 使用说明", icon="help").classes('w-full max-w-4xl'):
            ui.markdown("""
            ### @ui.refreshable 装饰器的工作原理：
            
            **1. 装饰器作用：**
            ```python
            @ui.refreshable
            def my_component():
                # 组件内容
                ui.label(data['value'])
            
            # 触发刷新
            my_component.refresh()
            ```
            
            **2. 刷新流程：**
            - 调用 `.refresh()` 方法
            - 清除原有组件内容
            - 重新执行被装饰的函数
            - 生成新的组件内容
            
            **3. 适用场景：**
            - 数据驱动的组件更新
            - 复杂的条件渲染
            - 动态表格和列表
            - 实时仪表板
            
            **4. 最佳实践：**
            - 将数据源与UI组件分离
            - 在数据变化后立即调用refresh()
            - 避免在refreshable函数内部定义大量逻辑
            - 考虑性能影响，避免频繁刷新
            
            **5. 注意事项：**
            - 刷新会重建所有子组件
            - 组件状态会丢失（如输入框内容）
            - 需要手动调用refresh()方法
            """)

if __name__ in {"__main__", "__mp_main__"}:
    main()
    ui.run(title="NiceGUI 全局数据演示", 
           port=8182,
           reload=True,
           prod_js=False,
           show=True
        )