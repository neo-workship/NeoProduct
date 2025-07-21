"""
主应用入口 - 集成统一建表功能（简化版）
"""
import sys
import os
from pathlib import Path
from nicegui import ui, app
from component import with_spa_layout, LayoutConfig, static_manager
from menu_pages import get_menu_page_handlers
from header_pages import get_header_page_handlers
from auth import (
    auth_manager, 
    require_login, 
    require_role,
    login_page_content,
    register_page_content,
    get_auth_page_handlers
)

def init_database_simple():
    """简化的数据库初始化"""
    try:
        print("🔄 开始数据库初始化...")
        
        # 首先确保数据库连接正常
        from auth.database import init_database as auth_init
        auth_init()
        
        # 直接运行统一初始化脚本
        from scripts.init_database import DatabaseInitializer
        
        initializer = DatabaseInitializer()
        initializer.run_full_initialization(create_test_data=True)
        
        print("✅ 数据库初始化成功！")
        return True
        
    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")
        print("尝试使用基础初始化方案...")
        
        try:
            # 备用方案：只初始化基础表
            from auth.database import get_db, Base, get_engine
            
            # 导入所有模型确保表结构
            from auth.models import User, Role, Permission, LoginLog
            from auth.models import user_roles, role_permissions, user_permissions
            from database_models.business_models.openai_models import OpenAIConfig, OpenAIRequest
            
            # 创建所有表
            engine = get_engine()
            Base.metadata.create_all(bind=engine)
            
            print("✅ 基础表创建成功")
            
            # 创建默认数据
            _create_basic_data()
            
            return True
            
        except Exception as fallback_error:
            print(f"❌ 备用初始化也失败: {fallback_error}")
            return False

def _create_basic_data():
    """创建基础数据"""
    from auth.database import get_db
    from auth.models import User, Role, Permission
    
    try:
        with get_db() as db:
            # 检查是否已有数据
            if db.query(User).count() > 0:
                print("数据已存在，跳过创建")
                return
            
            # 创建基础角色
            admin_role = Role(name='admin', display_name='管理员', description='系统管理员')
            user_role = Role(name='user', display_name='普通用户', description='普通用户')
            
            db.add(admin_role)
            db.add(user_role)
            db.flush()  # 获取ID
            
            # 创建基础权限
            permissions = [
                Permission(name='openai.view', display_name='查看OpenAI配置', category='openai'),
                Permission(name='openai.use', display_name='使用OpenAI对话', category='openai'),
                Permission(name='system.admin', display_name='系统管理', category='system'),
            ]
            
            for perm in permissions:
                db.add(perm)
            
            db.flush()  # 获取权限ID
            
            # 分配权限
            admin_role.permissions.extend(permissions)  # 管理员有所有权限
            user_role.permissions.append(permissions[0])  # 用户只能查看
            user_role.permissions.append(permissions[1])  # 用户可以使用
            
            # 创建测试用户
            admin = User(
                username='admin',
                email='admin@example.com',
                full_name='系统管理员',
                is_active=True,
                is_verified=True,
                is_superuser=True
            )
            admin.set_password('admin123')
            admin.roles.append(admin_role)
            
            user = User(
                username='user',
                email='user@example.com',
                full_name='测试用户',
                is_active=True,
                is_verified=True
            )
            user.set_password('user123')
            user.roles.append(user_role)
            
            db.add(admin)
            db.add(user)
            db.commit()
            
            print("✅ 基础数据创建完成")
            print("管理员: admin/admin123")
            print("普通用户: user/user123")
            
    except Exception as e:
        print(f"基础数据创建失败: {e}")
        raise

def create_protected_handlers():
    """为需要认证的页面添加装饰器"""
    menu_handlers = get_menu_page_handlers()
    header_handlers = get_header_page_handlers()
    system_handlers = get_auth_page_handlers()
    
    return {**menu_handlers, **header_handlers, **system_handlers}

if __name__ in {"__main__", "__mp_main__"}:
    # 初始化数据库
    if not init_database_simple():
        print("⚠️ 数据库初始化失败，但尝试继续运行...")

    # 获取受保护的页面处理器
    protected_handlers = create_protected_handlers()

    # 创建自定义配置
    config = LayoutConfig()

    # 登录页面
    @ui.page('/login')
    def login_page():
        login_page_content()

    # 注册页面
    @ui.page('/register')
    def register_page():
        register_page_content()

    # 主页面
    @ui.page('/workbench')
    def main_page():
        # 检查用户认证状态
        user = auth_manager.check_session()
        if not user:
            ui.navigate.to('/login')
            return

        # 创建带认证的SPA布局
        @with_spa_layout(
            config=config,
            menu_items=[
                {'key': 'home', 'label': '首页', 'icon': 'home', 'route': 'home'},
                {'key': 'dashboard', 'label': '看板', 'icon': 'dashboard', 'route': 'dashboard', 'separator_after': True},  
                {'key': 'enterprise_archive', 'label': '一企一档', 'icon': 'business', 'route': 'enterprise_archive'},
                {'key': 'person_archive', 'label': '一人一档', 'icon': 'person', 'route': 'person_archive','separator_after': True},
                {'key': 'smart_audit', 'label': '智能审计', 'icon': 'smart_toy', 'route': 'smart_audit'},
                {'key': 'smart_index', 'label': '智能指标', 'icon': 'analytics', 'route': 'smart_index','separator_after': True},
                {'key': 'about', 'label': '关于', 'icon': 'info', 'route': 'about'},
            ],
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

    ui.run(
        title=config.app_title,
        port=8080,
        show=True,
        reload=True,
        favicon='🚀',
        dark=False,
        storage_secret='your-secret-key-here'
    )