#!/usr/bin/env python3
"""
NiceGUI数据绑定示例
演示各种数据绑定方式：双向绑定、单向绑定、属性绑定、自定义绑定
"""

from nicegui import ui


class UserProfile:
    """用户配置类 - 作为数据模型"""
    def __init__(self):
        self.name = "张三"
        self.age = 25
        self.email = "zhangsan@example.com"
        self.is_active = True
        self.theme = "light"

def create_data_binding_demo():
    """创建数据绑定演示"""
    
    # 创建数据模型
    user = UserProfile()
    
    ui.markdown("## 🔗 NiceGUI 数据绑定演示")
    
    with ui.card().classes('w-full max-w-4xl'):
        ui.label("数据绑定让组件之间自动同步数据，无需手动更新").classes('text-lg mb-4')
        
        with ui.row().classes('w-full gap-6'):
            
            # === 左侧：输入控件 ===
            with ui.column().classes('flex-1'):
                ui.label("📝 输入控件").classes('text-xl font-bold mb-3')
                
                # 1. 双向绑定 - 姓名
                ui.label("姓名 (双向绑定)").classes('font-medium')
                name_input = ui.input("姓名").classes('mb-3').bind_value(user, 'name')
                
                # 2. 数值绑定 - 年龄  
                ui.label("年龄 (数值绑定)").classes('font-medium')
                age_slider = ui.slider(min=18, max=80, value=25).classes('mb-3').bind_value(user, 'age')
                
                # 3. 布尔绑定 - 激活状态
                ui.label("状态 (布尔绑定)").classes('font-medium')
                active_switch = ui.switch("激活用户").classes('mb-3').bind_value(user, 'is_active')
                
                # 4. 选择绑定 - 主题
                ui.label("主题 (选择绑定)").classes('font-medium')
                theme_select = ui.select(
                    options=['light', 'dark', 'auto'], 
                    value='light'
                ).classes('mb-3').bind_value(user, 'theme')
            
            # === 右侧：显示控件 ===
            with ui.column().classes('flex-1'):
                ui.label("📊 实时显示").classes('text-xl font-bold mb-3')
                
                # 单向绑定 - 从数据源到显示
                ui.label("用户信息预览:").classes('font-medium')
                
                with ui.card().classes('p-4 bg-gray-50'):
                    # 文本绑定
                    ui.label().bind_text_from(user, 'name', 
                             backward=lambda x: f"👤 姓名: {x}")
                    
                    # 数值绑定 + 格式化
                    ui.label().bind_text_from(user, 'age',
                             backward=lambda x: f"🎂 年龄: {x} 岁")
                    
                    # 邮箱显示（手动更新）
                    email_label = ui.label(f"📧 邮箱: {user.email}")
                    
                    # 状态绑定 + 样式联动
                    status_label = ui.label().bind_text_from(user, 'is_active',
                                  backward=lambda x: f"⚡ 状态: {'激活' if x else '未激活'}")
                    
                    # 主题绑定 + 图标显示
                    theme_label = ui.label().bind_text_from(user, 'theme',
                                 backward=lambda x: f"🎨 主题: {x.upper()}")


def create_advanced_binding_demo():
    """创建高级绑定演示"""
    
    ui.separator().classes('my-6')
    ui.markdown("## ⚡ 高级绑定特性")
    
    # 共享数据对象
    shared_data = {'counter': 0, 'message': 'Hello'}
    
    with ui.card().classes('w-full max-w-4xl'):
        
        with ui.row().classes('w-full gap-4'):
            
            # 多组件绑定到同一数据
            with ui.column().classes('flex-1'):
                ui.label("🔄 多组件同步").classes('text-lg font-bold')
                
                # 多个组件绑定到同一个计数器
                counter_label1 = ui.label().bind_text_from(shared_data, 'counter',
                                           backward=lambda x: f"计数器A: {x}")
                counter_label2 = ui.label().bind_text_from(shared_data, 'counter', 
                                           backward=lambda x: f"计数器B: {x}")
                counter_progress = ui.linear_progress().bind_value_from(shared_data, 'counter',
                                                      backward=lambda x: x / 100)
                
                with ui.row():
                    ui.button("➕new", on_click=lambda: shared_data.__setitem__('counter', shared_data['counter'] + 1))
                    ui.button("➕", on_click=lambda: shared_data.update(counter=shared_data['counter'] + 1))
                    ui.button("➖", on_click=lambda: shared_data.update(counter=max(0, shared_data['counter'] - 1)))
                    ui.button("🔄", on_click=lambda: shared_data.update(counter=0))
            
            # 条件绑定
            with ui.column().classes('flex-1'):
                ui.label("🎯 条件绑定").classes('text-lg font-bold')
                
                # 按钮启用状态绑定
                action_button = ui.button("执行操作").bind_enabled_from(shared_data, 'counter',
                                         backward=lambda x: x > 0)
                
                # 样式条件绑定
                status_badge = ui.badge().bind_text_from(shared_data, 'counter',
                             backward=lambda x: "就绪" if x > 5 else "等待")
                
                # 图标条件绑定 - 使用样式属性绑定
                indicator = ui.icon('circle').classes('text-2xl')
                
                # 绑定图标名称
                indicator.bind_name_from(shared_data, 'counter',
                        backward=lambda x: 'check_circle' if x > 10 else 'radio_button_unchecked' if x > 5 else 'cancel')
                
                # 绑定颜色样式
                def update_icon_color():
                    count = shared_data['counter']
                    if count > 10:
                        indicator.style('color: green')
                    elif count > 5:
                        indicator.style('color: orange') 
                    else:
                        indicator.style('color: red')
                
                # 创建一个隐藏的标签来触发颜色更新
                ui.label().bind_text_from(shared_data, 'counter', 
                          backward=lambda x: update_icon_color() or "").classes('hidden')


def create_custom_binding_demo():
    """创建自定义绑定演示"""
    
    ui.separator().classes('my-6')
    ui.markdown("## 🛠️ 自定义绑定")
    
    # 温度数据
    temperature_data = {'celsius': 20}
    
    with ui.card().classes('w-full max-w-4xl'):
        ui.label("温度转换器 - 自定义双向绑定").classes('text-lg font-bold mb-4')
        
        with ui.row().classes('gap-6'):
            # 摄氏度输入
            celsius_input = ui.number("摄氏度 (°C)", value=20).classes('flex-1')
            celsius_input.bind_value(temperature_data, 'celsius')
            
            # 华氏度显示（单向绑定 + 转换）
            fahrenheit_label = ui.label().classes('flex-1 text-center text-lg')
            fahrenheit_label.bind_text_from(temperature_data, 'celsius',
                           backward=lambda c: f"华氏度: {c * 9/5 + 32:.1f}°F")
            
            # 开尔文显示
            kelvin_label = ui.label().classes('flex-1 text-center text-lg')
            kelvin_label.bind_text_from(temperature_data, 'celsius',
                       backward=lambda c: f"开尔文: {c + 273.15:.1f}K")


# 主函数
def main():
    """主演示函数"""
    
    # 页面标题和样式
    ui.page_title("NiceGUI 数据绑定演示")
    
    with ui.column().classes('w-full items-center p-4'):
        create_data_binding_demo()
        create_advanced_binding_demo() 
        create_custom_binding_demo()
        
        # 说明文档
        ui.separator().classes('my-6')
        with ui.expansion("📚 绑定方法说明", icon="help").classes('w-full max-w-4xl'):
            ui.markdown("""
            ### 常用绑定方法：
            
            **基础绑定：**
            - `bind_value(obj, prop)` - 双向绑定值
            - `bind_value_from(obj, prop)` - 单向绑定（从源到目标）
            - `bind_value_to(obj, prop)` - 单向绑定（从目标到源）
            
            **属性绑定：**
            - `bind_text_from()` - 绑定文本内容
            - `bind_enabled_from()` - 绑定启用状态
            - `bind_visible_from()` - 绑定可见性
            - `bind_props_from()` - 绑定组件属性
            
            **高级特性：**
            - `backward` 参数 - 数据转换函数
            - 多组件绑定同一数据源
            - 条件绑定和动态样式
            """)

if __name__ in {"__main__", "__mp_main__"}:
    main()
    ui.run(title="NiceGUI数据绑定演示", 
           port=8180,
           reload=True,
           prod_js=False,
           show=True
        )