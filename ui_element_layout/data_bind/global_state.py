#!/usr/bin/env python3
"""
NiceGUI全局状态管理示例
演示通过全局对象和字典实现组件间数据共享
"""

from nicegui import ui
from typing import Dict, List, Any
from dataclasses import dataclass
from datetime import datetime


# ====== 方法1：全局字典状态管理 ======
global_state = {
    'user': {'name': '游客', 'level': 1, 'score': 0},
    'app': {'theme': 'light', 'language': 'zh', 'notifications': True},
    'cart': {'items': [], 'total': 0.0},
    'logs': []
}


# ====== 方法2：全局类状态管理 ======
@dataclass
class UserState:
    name: str = "游客"
    email: str = ""
    is_logged_in: bool = False
    preferences: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.preferences is None:
            self.preferences = {'theme': 'light', 'notifications': True}


class AppStateManager:
    """应用状态管理器"""
    
    def __init__(self):
        self.user = UserState()
        self.shopping_cart: List[Dict] = []
        self.notifications: List[str] = []
        self.current_page = 'home'
        self.ui_components = {}  # 存储需要更新的UI组件
    
    def add_to_cart(self, item: Dict):
        """添加商品到购物车"""
        self.shopping_cart.append(item)
        self.add_notification(f"已添加 {item['name']} 到购物车")
        self.update_ui('cart')
    
    def remove_from_cart(self, index: int):
        """从购物车移除商品"""
        if 0 <= index < len(self.shopping_cart):
            item = self.shopping_cart.pop(index)
            self.add_notification(f"已移除 {item['name']}")
            self.update_ui('cart')
    
    def add_notification(self, message: str):
        """添加通知"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.notifications.append(f"[{timestamp}] {message}")
        if len(self.notifications) > 10:  # 保持最新10条
            self.notifications.pop(0)
        self.update_ui('notifications')
    
    def register_ui_component(self, component_id: str, update_func):
        """注册需要更新的UI组件"""
        self.ui_components[component_id] = update_func
    
    def update_ui(self, component_id: str):
        """更新指定的UI组件"""
        if component_id in self.ui_components:
            self.ui_components[component_id]()

# 创建全局状态管理器实例
app_state = AppStateManager()

def create_global_dict_demo():
    """演示全局字典状态管理"""
    
    ui.markdown("## 📚 方法1：全局字典状态管理")
    
    with ui.card().classes('w-full max-w-4xl mb-6'):
        ui.label("全局字典可以在任何地方访问和修改，适合简单的状态管理").classes('text-sm text-gray-600 mb-4')
        
        with ui.row().classes('w-full gap-4'):
            
            # 用户信息面板
            with ui.column().classes('flex-1'):
                ui.label("👤 用户信息").classes('text-lg font-bold mb-2')
                
                # 显示用户信息
                user_name_label = ui.label()
                user_level_label = ui.label()
                user_score_label = ui.label()
                
                def update_user_display():
                    user = global_state['user']
                    user_name_label.text = f"姓名: {user['name']}"
                    user_level_label.text = f"等级: {user['level']}"
                    user_score_label.text = f"积分: {user['score']}"
                
                update_user_display()
                
                # 用户操作
                with ui.row().classes('gap-2 mt-2'):
                    ui.button("升级", on_click=lambda: level_up()).props('size=sm color=positive')
                    ui.button("加分", on_click=lambda: add_score()).props('size=sm color=primary')
                    ui.button("重置", on_click=lambda: reset_user()).props('size=sm color=negative')
            
            # 应用设置面板  
            with ui.column().classes('flex-1'):
                ui.label("⚙️ 应用设置").classes('text-lg font-bold mb-2')
                
                # 主题切换
                theme_select = ui.select(
                    options=['light', 'dark', 'auto'], 
                    value=global_state['app']['theme'],
                    label="主题"
                ).classes('mb-2 w-full')
                
                # 语言切换
                language_select = ui.select(
                    options=['zh', 'en', 'ja'],
                    value=global_state['app']['language'], 
                    label="语言"
                ).classes('mb-2 w-full')
                
                # 通知开关
                notification_switch = ui.switch(
                    "启用通知",
                    value=global_state['app']['notifications']
                )
                
                # 设置变化处理
                def on_theme_change():
                    global_state['app']['theme'] = theme_select.value
                    add_log(f"主题切换为: {theme_select.value}")
                
                def on_language_change():
                    global_state['app']['language'] = language_select.value
                    add_log(f"语言切换为: {language_select.value}")
                
                def on_notification_change():
                    global_state['app']['notifications'] = notification_switch.value
                    add_log(f"通知 {'开启' if notification_switch.value else '关闭'}")
                
                theme_select.on('update:model-value', on_theme_change)
                language_select.on('update:model-value', on_language_change)
                notification_switch.on('update:model-value', on_notification_change)
        
        # 操作日志
        ui.separator().classes('my-4')
        ui.label("📝 操作日志").classes('text-lg font-bold mb-2 w-full')
        
        logs_container = ui.column().classes('bg-gray-50 p-3 rounded max-h-32 overflow-y-auto w-full scrollbar-hide')
        
        def update_logs():
            logs_container.clear()
            with logs_container:
                recent_logs = global_state['logs'][-5:]  # 获取最新5条
                if not recent_logs:
                    ui.label("暂无操作日志").classes('text-sm text-gray-500 w-full')
                else:
                    for log in recent_logs:
                        ui.label(log).classes('text-sm text-gray-700 w-full')
        # 全局函数定义
        def level_up():
            global_state['user']['level'] += 1
            global_state['user']['score'] += 100
            update_user_display()
            add_log(f"用户 {global_state['user']['name']} 升级到 {global_state['user']['level']} 级")
        
        def add_score():
            global_state['user']['score'] += 50
            update_user_display()
            add_log(f"用户获得50积分，当前积分: {global_state['user']['score']}")
        
        def reset_user():
            global_state['user'] = {'name': '游客', 'level': 1, 'score': 0}
            update_user_display()
            add_log("用户信息已重置")
        
        def add_log(message: str):
            timestamp = datetime.now().strftime("%H:%M:%S")
            global_state['logs'].append(f"[{timestamp}] {message}")
            # 保持日志数量在合理范围内
            if len(global_state['logs']) > 20:
                global_state['logs'] = global_state['logs'][-10:]  # 保留最新30条
            update_logs()
        
        update_logs()

def create_global_class_demo():
    """演示全局类状态管理"""
    
    ui.markdown("## 🏗️ 方法2：全局类状态管理")
    
    with ui.card().classes('w-full max-w-4xl mb-6'):
        ui.label("全局类提供更好的结构化和类型安全，适合复杂的状态管理").classes('text-sm text-gray-600 mb-4')
        
        with ui.row().classes('w-full gap-4'):
            
            # 购物车管理
            with ui.column().classes('flex-1'):
                ui.label("🛒 购物车管理").classes('text-lg font-bold mb-2')
                
                # 商品列表
                products = [
                    {'name': 'Python编程书', 'price': 59.9},
                    {'name': 'NiceGUI教程', 'price': 29.9},
                    {'name': '代码咖啡杯', 'price': 19.9}
                ]
                
                for product in products:
                    with ui.row().classes('items-center gap-2 mb-1'):
                        ui.label(f"{product['name']} - ¥{product['price']}").classes('flex-1')
                        ui.button("加入购物车", 
                                on_click=lambda p=product: app_state.add_to_cart(p)).props('size=sm')
                
                ui.separator().classes('my-3')
                
                # 购物车显示
                cart_container = ui.column().classes('bg-blue-50 p-3 rounded')
                
                def update_cart_display():
                    cart_container.clear()
                    with cart_container:
                        ui.label(f"购物车 ({len(app_state.shopping_cart)} 件商品)").classes('font-bold mb-2')
                        
                        if not app_state.shopping_cart:
                            ui.label("购物车为空").classes('text-gray-500')
                        else:
                            total = 0
                            for i, item in enumerate(app_state.shopping_cart):
                                with ui.row().classes('items-center gap-2 mb-1'):
                                    ui.label(f"{item['name']} - ¥{item['price']}").classes('flex-1')
                                    ui.button("×", 
                                            on_click=lambda idx=i: app_state.remove_from_cart(idx)).props('size=sm color=negative')
                                total += item['price']
                            
                            ui.separator().classes('my-2')
                            ui.label(f"总计: ¥{total:.2f}").classes('font-bold text-lg')
                
                # 注册购物车更新函数
                app_state.register_ui_component('cart', update_cart_display)
                update_cart_display()
            
            # 通知中心
            with ui.column().classes('flex-1'):
                ui.label("🔔 通知中心").classes('text-lg font-bold mb-2')
                
                notifications_container = ui.column().classes('bg-yellow-50 p-3 rounded max-h-64 overflow-y-auto')
                
                def update_notifications_display():
                    notifications_container.clear()
                    with notifications_container:
                        if not app_state.notifications:
                            ui.label("暂无通知").classes('text-gray-500')
                        else:
                            for notification in app_state.notifications[-8:]:  # 显示最新8条
                                ui.label(notification).classes('text-sm mb-1')
                
                # 注册通知更新函数
                app_state.register_ui_component('notifications', update_notifications_display)
                update_notifications_display()
                
                # 操作按钮
                with ui.row().classes('gap-2 mt-3'):
                    ui.button("清空通知", 
                            on_click=lambda: clear_notifications()).props('size=sm color=warning')
                    ui.button("测试通知", 
                            on_click=lambda: app_state.add_notification("这是一条测试通知")).props('size=sm')
                
                def clear_notifications():
                    app_state.notifications.clear()
                    app_state.update_ui('notifications')

def create_state_sync_demo():
    """演示状态同步"""
    
    ui.markdown("## 🔄 状态同步演示")
    
    with ui.card().classes('w-full max-w-4xl'):
        ui.label("展示全局状态在不同组件间的同步效果").classes('text-sm text-gray-600 mb-4')
        
        # 共享计数器
        shared_counter = {'value': 0}
        
        with ui.row().classes('w-full gap-6'):
            
            # 计数器控制面板1
            with ui.column().classes('flex-1 text-center'):
                ui.label("📊 控制面板 A").classes('text-lg font-bold mb-3')
                
                counter_display_a = ui.label("0").classes('text-4xl font-bold text-blue-600 mb-3')
                
                with ui.row().classes('gap-2 justify-center'):
                    ui.button("+1", on_click=lambda: increment_counter(1)).props('color=positive')
                    ui.button("+5", on_click=lambda: increment_counter(5)).props('color=positive') 
                    ui.button("重置", on_click=lambda: reset_counter()).props('color=warning')
            
            # 计数器控制面板2
            with ui.column().classes('flex-1 text-center'):
                ui.label("📊 控制面板 B").classes('text-lg font-bold mb-3')
                
                counter_display_b = ui.label("0").classes('text-4xl font-bold text-green-600 mb-3')
                
                with ui.row().classes('gap-2 justify-center'):
                    ui.button("-1", on_click=lambda: increment_counter(-1)).props('color=negative')
                    ui.button("-5", on_click=lambda: increment_counter(-5)).props('color=negative')
                    ui.button("x2", on_click=lambda: multiply_counter()).props('color=info')
        
        # 状态同步函数
        def update_counter_displays():
            value = shared_counter['value']
            counter_display_a.text = str(value)
            counter_display_b.text = str(value)
            
            # 添加全局日志
            add_global_log(f"计数器更新为: {value}")
        
        def increment_counter(amount):
            shared_counter['value'] += amount
            update_counter_displays()
        
        def multiply_counter():
            shared_counter['value'] *= 2
            update_counter_displays()
        
        def reset_counter():
            shared_counter['value'] = 0
            update_counter_displays()
        
        def add_global_log(message):
            """添加到全局日志"""
            timestamp = datetime.now().strftime("%H:%M:%S")
            global_state['logs'].append(f"[{timestamp}] {message}")


def main():
    """主演示函数"""
    
    # 页面标题和样式
    ui.page_title("NiceGUI 全局状态管理演示")
    
    with ui.column().classes('w-full items-center p-4'):
        ui.markdown("# 🌐 NiceGUI 全局状态管理演示")
        ui.label("学习如何通过全局对象和字典实现组件间数据共享").classes('text-lg text-gray-600 mb-6')
        
        create_global_dict_demo()
        create_global_class_demo() 
        create_state_sync_demo()
        
        # 说明文档
        ui.separator().classes('my-6')
        with ui.expansion("📚 全局状态管理说明", icon="help").classes('w-full max-w-4xl'):
            ui.markdown("""
            ### 全局状态管理的两种方式：
            
            **1. 全局字典方式：**
            ```python
            global_state = {'user': {...}, 'app': {...}}
            
            # 更新状态
            global_state['user']['name'] = '新用户'
            global_state.update({'new_key': 'new_value'})
            ```
            
            **2. 全局类方式：**
            ```python
            class AppState:
                def __init__(self):
                    self.user = UserState()
                    self.data = []
            
            app_state = AppState()
            
            # 更新状态
            app_state.user.name = '新用户'
            ```
            
            ### 优缺点对比：
            
            | 方式 | 优点 | 缺点 | 适用场景 |
            |------|------|------|----------|
            | 全局字典 | 简单直接，易于理解 | 缺乏类型安全，难以维护 | 小型应用，原型开发 |
            | 全局类 | 结构清晰，类型安全 | 需要更多代码设计 | 中大型应用，团队开发 |
            
            ### 最佳实践：
            - 合理组织状态结构，避免过深嵌套
            - 提供统一的状态更新方法
            - 在状态变化时主动更新相关UI组件
            - 考虑状态的生命周期和清理
            """)

if __name__ in {"__main__", "__mp_main__"}:
    main()
    ui.run(title="NiceGUI 全局数据演示", 
           port=8181,
           reload=True,
           prod_js=False,
           show=True
        )