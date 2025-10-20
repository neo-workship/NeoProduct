"""
多层布局主应用入口 - 演示多层折叠菜单布局
基于 multilayer_spa_layout 构建UI的启动脚本
"""
import sys
import os
from pathlib import Path
from nicegui import ui, app

# 导入多层布局组件
from component import (
    with_multilayer_spa_layout, 
    LayoutConfig, 
    MultilayerMenuItem,
    static_manager
)

# 导入页面处理器
from menu_pages import get_menu_page_handlers
from header_pages import get_header_page_handlers

# 导入认证模块
from auth import (
    auth_manager,
    require_login,
    require_role,
    login_page_content,
    register_page_content,
    get_auth_page_handlers
)


def create_demo_menu_structure() -> list[MultilayerMenuItem]:
    """
    创建演示用的多层菜单结构
    这里展示了2-3层的菜单结构
    """
    menu_items = [
        # 首页 - 单独的顶层菜单(无子菜单)
        MultilayerMenuItem(
            key='home',
            label='首页',
            icon='home',
            route='home',
            separator_after=True  # 后面显示分隔线
        ),
        
        # 企业档案管理 - 第一个分组
        MultilayerMenuItem(
            key='enterprise',
            label='企业档案管理',
            icon='business',
            expanded=True,  # 默认展开
            children=[
                MultilayerMenuItem(
                    key='chat',
                    label='AI对话',
                    icon='chat',
                    route='chat_page'
                ),
                MultilayerMenuItem(
                    key='doc',
                    label='文档管理',
                    icon='description',
                    route='other_page'  # 暂时复用other_page
                ),
            ]
        ),
        
        # 个人档案管理 - 第二个分组
        MultilayerMenuItem(
            key='personal',
            label='个人档案管理',
            icon='people',
            children=[
                MultilayerMenuItem(
                    key='profile',
                    label='个人资料',
                    icon='person',
                    route='other_page'
                ),
                MultilayerMenuItem(
                    key='settings',
                    label='个人设置',
                    icon='settings',
                    route='other_page'
                ),
            ],
            separator_after=True
        ),
        
        # 系统管理 - 第三个分组(演示更多子项)
        MultilayerMenuItem(
            key='system',
            label='系统管理',
            icon='admin_panel_settings',
            children=[
                MultilayerMenuItem(
                    key='users',
                    label='用户管理',
                    icon='group',
                    route='user_management'
                ),
                MultilayerMenuItem(
                    key='roles',
                    label='角色管理',
                    icon='badge',
                    route='role_management'
                ),
                MultilayerMenuItem(
                    key='permissions',
                    label='权限管理',
                    icon='lock',
                    route='permission_management'
                ),
            ]
        ),
        
        # 配置中心 - 第四个分组
        MultilayerMenuItem(
            key='config',
            label='配置中心',
            icon='tune',
            children=[
                MultilayerMenuItem(
                    key='llm',
                    label='大模型配置',
                    icon='psychology',
                    route='llm_config_management'
                ),
                MultilayerMenuItem(
                    key='prompt',
                    label='提示词配置',
                    icon='article',
                    route='prompt_config_management'
                ),
            ]
        ),
    ]
    
    return menu_items


def create_protected_handlers():
    """为需要认证的页面添加装饰器"""
    menu_handlers = get_menu_page_handlers()
    header_handlers = get_header_page_handlers()
    system_handlers = get_auth_page_handlers()
    
    return {**menu_handlers, **header_handlers, **system_handlers}


if __name__ in {"__main__", "__mp_main__"}:
    
    print("=" * 70)
    print("🚀 启动多层布局演示应用")
    print("=" * 70)
    
    # 获取受保护的页面处理器
    protected_handlers = create_protected_handlers()
    
    # 创建自定义配置
    config = LayoutConfig()
    config.app_title = 'NeoUI多层布局演示'
    config.menu_title = '功能导航'
    
    # 登录页面
    @ui.page('/login')
    def login_page():
        login_page_content()
    
    # 注册页面
    @ui.page('/register')
    def register_page():
        register_page_content()
    
    # 主工作台页面 - 使用多层布局
    @ui.page('/workbench')
    def main_page():
        # 检查用户认证状态
        user = auth_manager.check_session()
        if not user:
            ui.navigate.to('/login')
            return
        
        print(f"✅ 用户 {user.username} 已登录,创建多层布局")
        
        # 创建多层菜单结构
        menu_items = create_demo_menu_structure()
        
        # 创建带认证的多层SPA布局
        @with_multilayer_spa_layout(
            config=config,
            menu_items=menu_items,
            header_config_items=[
                {'key': 'search', 'label': '搜索', 'icon': 'search', 'route': 'search'},
                {'key': 'messages', 'label': '消息', 'icon': 'mail', 'route': 'messages'},
                {'key': 'contact', 'label': '联系我们', 'icon': 'contact_support', 'route': 'contact'},
            ],
            route_handlers=protected_handlers
        )
        def spa_content():
            pass
        
        return spa_content()
    
    # 直接跳转到工作台
    @ui.page('/')
    def index():
        ui.navigate.to('/workbench')
    
    # 打印菜单结构信息
    print("\n📋 多层菜单结构:")
    menu_items = create_demo_menu_structure()
    for item in menu_items:
        if item.is_leaf:
            print(f"  📄 {item.label} (route: {item.route})")
        else:
            print(f"  📁 {item.label} (展开: {item.expanded})")
            for child in item.children:
                print(f"     └─ {child.label} (route: {child.route})")
    
    print("\n" + "=" * 70)
    print("✨ 多层布局特性:")
    print("  - 🎯 支持多层级折叠菜单(无限层级)")
    print("  - 📂 自动展开/收起父节点")
    print("  - 🔖 面包屑导航自动生成")
    print("  - 💾 刷新页面保持状态(路由+展开状态)")
    print("  - 🎨 高亮选中的叶子节点")
    print("  - 🔐 集成完整的认证和权限管理")
    print("=" * 70)
    print(f"🌐 应用启动在: http://localhost:8080")
    print("=" * 70 + "\n")
    
    # 启动应用
    ui.run(
        title=config.app_title,
        port=8080,
        show=True,
        reload=True,
        favicon='🚀',
        dark=False,
        storage_secret='your-secret-key-here'
    )