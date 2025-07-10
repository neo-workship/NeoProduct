from nicegui import ui, app
from component import with_spa_layout, LayoutConfig, static_manager
from menu_pages import get_menu_page_handlers
from header_pages import get_header_page_handlers

def setup_static_files():
    """设置静态文件服务和CSS加载"""
    print("🚀 开始设置静态文件...")
    
    # 方法1: 通过URL加载CSS（推荐）
    try:
        static_manager.load_css_files()
    except Exception as e:
        print(f"❌ URL方式加载CSS失败: {e}")
        
        # 方法2: 如果URL方式失败，尝试内联加载
        print("🔄 尝试内联方式加载CSS...")
        static_manager.load_inline_css("css/custom.css")
        static_manager.load_inline_css("css/themes/light.css")
        static_manager.load_inline_css("css/themes/dark.css")
    
    # 方法3: 直接添加一些基础样式（确保至少有些样式生效）
    ui.add_head_html('''
        <style>
            /* 确保基础样式生效 */
            .custom-card {
                border-radius: 12px !important;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1) !important;
                transition: all 0.3s ease !important;
                background: white !important;
                border: 1px solid #e5e7eb !important;
            }
            
            .custom-card:hover {
                box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1) !important;
                transform: translateY(-2px) !important;
            }
            
            .custom-button {
                border-radius: 8px !important;
                font-weight: 500 !important;
                transition: all 0.2s ease !important;
            }
            
            .custom-button:hover {
                transform: translateY(-1px) !important;
            }
            
            .fade-in {
                animation: fadeIn 0.3s ease-in-out !important;
            }
            
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(10px); }
                to { opacity: 1; transform: translateY(0); }
            }
            
            .menu-item-hover {
                transition: all 0.2s ease !important;
            }
            
            .menu-item-hover:hover {
                background: linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(99, 102, 241, 0.1)) !important;
                border-left: 3px solid #3b82f6 !important;
            }
            
            /* 深色主题适配 */
            [data-theme="dark"] .custom-card {
                background: #1f2937 !important;
                border: 1px solid #374151 !important;
                color: #f9fafb !important;
            }
            
            /* 移动端适配 */
            @media (max-width: 768px) {
                .mobile-hidden {
                    display: none !important;
                }
            }
        </style>
    ''')
    
    print("✅ 静态文件设置完成")

def notify_user_clicked_contact():
    """联系我们按钮的回调函数"""
    ui.notify('您点击了联系我们！')

if __name__ in {"__main__", "__mp_main__"}:
    # 第一步：设置静态文件服务
    # setup_static_files()
    
    # 获取所有页面处理函数
    menu_handlers = get_menu_page_handlers()
    header_handlers = get_header_page_handlers()
    
    # 合并所有路由处理器
    all_route_handlers = {**menu_handlers, **header_handlers}

    # 创建自定义配置
    config = LayoutConfig()
    
    @ui.page('/')
    @with_spa_layout(
        config=config,
        menu_items=[
            {'key': 'home', 'label': '首页', 'icon': 'home', 'route': 'home'},
            {'key': 'dashboard', 'label': '看板', 'icon': 'dashboard', 'route': 'dashboard', 'separator_after': True},
            {'key': 'data', 'label': '连接数据', 'icon': 'electrical_services', 'route': 'data'},
            {'key': 'analysis', 'label': '智能问数', 'icon': 'question_answer', 'route': 'analysis'},
            {'key': 'mcp', 'label': 'mcp服务', 'icon': 'api', 'route': 'mcp', 'separator_after': True},
            {'key': 'about', 'label': '关于', 'icon': 'info', 'route': 'about'}
        ],
        header_config_items=[
            {'key': 'search', 'icon': 'search', 'label': '查询', 'route': 'search_page'},
            {'key': 'messages', 'icon': 'mail', 'label': '消息', 'route': 'messages_page'},
            {'key': 'notifications', 'icon': 'notifications', 'label': '提醒', 'route': 'notifications_page'},
            {'key': 'contact', 'label': '联系我们', 'icon': 'support', 'route': 'contact_page'}
        ],
        route_handlers=all_route_handlers
    )
    def main_page():
        """主页面入口函数"""
        pass

    # 启动应用
    print("🌐 启动应用服务器...")
    ui.run(
        title=config.app_title, 
        port=8080, 
        show=True,
        reload=True,
        favicon='🚀',
        dark=False
    )