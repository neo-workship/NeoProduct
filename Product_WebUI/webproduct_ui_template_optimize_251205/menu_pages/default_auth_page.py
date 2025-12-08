"""
默认场景业务模拟页面 (Default Scenario Business Demo)
========================================================

功能说明:
--------
本页面全面模拟 default 场景下的真实业务应用,基于以下数据结构:

数据源: 
  通过命令 `python scripts/init_database.py --scenario default --test-data` 创建

角色体系 (4个角色):
  1. admin (系统管理员) - 拥有所有权限
  2. editor (编辑者) - 可以创建和编辑内容  
  3. viewer (查看者) - 只能查看内容
  4. user (普通用户) - 基本权限

权限体系 (10个权限):
  系统权限:
    - system.manage: 系统管理
    - user.manage: 用户管理
    - role.manage: 角色管理
  
  内容权限:
    - content.create: 创建内容
    - content.edit: 编辑内容
    - content.delete: 删除内容
    - content.view: 查看内容
  
  个人资料权限:
    - profile.view: 查看个人资料
    - profile.edit: 编辑个人资料
    - password.change: 修改密码

测试账号:
  - admin/admin123    (系统管理员,所有权限)
  - editor/editor123  (编辑者,创建+编辑+查看+个人资料)
  - viewer/viewer123  (查看者,查看+个人资料+修改密码)
  - user/user123      (普通用户,查看+个人资料+修改密码)

业务场景设计:
-----------
1. 内容管理系统 (CMS) - 文章发布平台
   - 文章列表展示 (所有人可见)
   - 创建文章 (需要 content.create)
   - 编辑文章 (需要 content.edit)
   - 删除文章 (需要 content.delete)

2. 用户管理模块 (需要 user.manage 权限)
   - 查看用户列表
   - 修改用户状态

3. 个人中心
   - 查看个人信息 (需要 profile.view)
   - 编辑个人信息 (需要 profile.edit)

技术特点:
--------
- 严格遵循 RBAC 权限模型
- 使用装饰器进行权限控制
- 动态权限检查和UI渲染
- 完整的业务流程闭环
- 符合项目现有代码风格
"""

from nicegui import ui
from auth import auth_manager, require_login, require_permission
from auth.database import get_db
from auth.models import User, Role, Permission
from sqlmodel import select
from common.log_handler import (
    log_info, log_success, log_warning, log_error,
    safe_protect, get_logger
)
from datetime import datetime
from typing import List, Dict, Optional

logger = get_logger(__name__)


# ========================================
# 数据模型模拟 (简化的文章数据)
# ========================================

class ArticleStorage:
    """文章存储 - 使用内存存储模拟数据库"""
    
    def __init__(self):
        self.articles: List[Dict] = [
            {
                'id': 1,
                'title': 'NiceGUI 快速入门指南',
                'content': 'NiceGUI 是一个简单易用的 Python Web UI 框架...',
                'author': 'admin',
                'created_at': '2024-01-01 10:00:00',
                'status': 'published'
            },
            {
                'id': 2,
                'title': 'RBAC 权限管理最佳实践',
                'content': '基于角色的访问控制(RBAC)是企业应用中...',
                'author': 'editor',
                'created_at': '2024-01-02 14:30:00',
                'status': 'published'
            },
            {
                'id': 3,
                'title': 'SQLModel 使用技巧',
                'content': 'SQLModel 结合了 Pydantic 和 SQLAlchemy...',
                'author': 'editor',
                'created_at': '2024-01-03 09:15:00',
                'status': 'draft'
            },
        ]
        self.next_id = 4
    
    def get_all(self) -> List[Dict]:
        """获取所有文章"""
        return self.articles
    
    def get_published(self) -> List[Dict]:
        """获取已发布文章"""
        return [a for a in self.articles if a['status'] == 'published']
    
    def get_by_id(self, article_id: int) -> Optional[Dict]:
        """根据ID获取文章"""
        for article in self.articles:
            if article['id'] == article_id:
                return article
        return None
    
    def create(self, title: str, content: str, author: str) -> Dict:
        """创建新文章"""
        article = {
            'id': self.next_id,
            'title': title,
            'content': content,
            'author': author,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'status': 'draft'
        }
        self.articles.append(article)
        self.next_id += 1
        return article
    
    def update(self, article_id: int, title: str, content: str, status: str) -> bool:
        """更新文章"""
        article = self.get_by_id(article_id)
        if article:
            article['title'] = title
            article['content'] = content
            article['status'] = status
            return True
        return False
    
    def delete(self, article_id: int) -> bool:
        """删除文章"""
        article = self.get_by_id(article_id)
        if article:
            self.articles.remove(article)
            return True
        return False


# 全局文章存储实例
article_storage = ArticleStorage()


# ========================================
# 主页面入口
# ========================================

@safe_protect(name="默认场景业务页面", error_msg="默认场景业务页面加载失败")
@require_login(redirect_to_login=True)
def default_auth_page_content():
    """
    默认场景业务模拟页面主入口
    
    页面结构:
    1. 页面标题和当前用户信息
    2. 权限状态面板
    3. 业务功能模块切换
       - 文章管理
       - 用户管理
       - 个人中心
    """
    
    # 获取当前用户
    current_user = auth_manager.check_session()
    if not current_user:
        ui.label('❌ 无法获取当前用户信息').classes('text-red-600')
        return
    
    # ===========================
    # 页面标题
    # ===========================
    ui.label('📋 默认场景业务模拟系统').classes('text-3xl font-bold text-blue-700 mb-2')
    ui.label('Default Scenario Business Demo').classes('text-sm text-gray-500 mb-6')
    
    # ===========================
    # 当前用户信息卡片
    # ===========================
    with ui.card().classes('w-full mb-6 bg-gradient-to-r from-blue-50 to-indigo-50'):
        ui.label('👤 当前登录用户').classes('text-lg font-bold text-blue-800 mb-2')
        
        with ui.row().classes('gap-4 w-full'):
            with ui.column().classes('flex-1'):
                ui.label(f'用户名: {current_user.username}').classes('text-sm')
                ui.label(f'姓名: {current_user.full_name or "未设置"}').classes('text-sm')
                ui.label(f'邮箱: {current_user.email}').classes('text-sm')
            
            with ui.column().classes('flex-1'):
                # 显示角色
                roles_text = ', '.join(current_user.roles) if current_user.roles else '无'
                ui.label(f'角色: {roles_text}').classes('text-sm font-semibold text-indigo-700')
                
                # 显示权限数量
                perm_count = len(current_user.permissions)
                ui.label(f'权限数量: {perm_count}').classes('text-sm text-green-700')
                
                if current_user.is_superuser:
                    ui.badge('超级管理员', color='red').classes('text-xs')
    
    # ===========================
    # 权限状态面板
    # ===========================
    with ui.expansion('🔐 当前用户权限详情', icon='security').classes('w-full mb-6'):
        render_permission_status_panel(current_user)
    
    # ===========================
    # 业务功能模块
    # ===========================
    ui.label('💼 业务功能模块').classes('text-2xl font-bold text-gray-700 mb-4 mt-8')
    
    with ui.tabs().classes('w-full') as tabs:
        tab_articles = ui.tab('📝 文章管理', icon='article')
        tab_users = ui.tab('👥 用户管理', icon='people')
        tab_profile = ui.tab('👤 个人中心', icon='account_circle')
    
    with ui.tab_panels(tabs, value=tab_articles).classes('w-full'):
        with ui.tab_panel(tab_articles):
            render_article_management(current_user)
        
        with ui.tab_panel(tab_users):
            render_user_management(current_user)
        
        with ui.tab_panel(tab_profile):
            render_personal_center(current_user)


# ========================================
# 权限状态面板
# ========================================

def render_permission_status_panel(current_user):
    """
    渲染权限状态面板
    显示用户在各个业务模块的权限情况
    """
    
    # 定义权限检查项
    permission_checks = [
        {
            'category': '系统权限',
            'permissions': [
                ('system.manage', '系统管理'),
                ('user.manage', '用户管理'),
                ('role.manage', '角色管理'),
            ]
        },
        {
            'category': '内容权限',
            'permissions': [
                ('content.create', '创建内容'),
                ('content.edit', '编辑内容'),
                ('content.delete', '删除内容'),
                ('content.view', '查看内容'),
            ]
        },
        {
            'category': '个人资料权限',
            'permissions': [
                ('profile.view', '查看个人资料'),
                ('profile.edit', '编辑个人资料'),
                ('password.change', '修改密码'),
            ]
        },
    ]
    
    # 渲染权限状态
    for check_group in permission_checks:
        with ui.card().classes('w-full mb-4'):
            ui.label(f'{check_group["category"]}').classes('text-lg font-bold mb-2')
            
            with ui.grid(columns=2).classes('w-full gap-2'):
                for perm_name, perm_display in check_group['permissions']:
                    has_perm = current_user.has_permission(perm_name)
                    
                    with ui.row().classes('items-center gap-2'):
                        if has_perm:
                            ui.icon('check_circle', color='green').classes('text-xl')
                            ui.label(perm_display).classes('text-green-700')
                        else:
                            ui.icon('cancel', color='red').classes('text-xl')
                            ui.label(perm_display).classes('text-gray-400 line-through')


# ========================================
# 模块1: 文章管理
# ========================================

def render_article_management(current_user):
    """
    文章管理模块
    
    功能:
    - 查看文章列表 (需要 content.view)
    - 创建文章 (需要 content.create)
    - 编辑文章 (需要 content.edit)
    - 删除文章 (需要 content.delete)
    """
    
    ui.label('📝 文章管理系统').classes('text-2xl font-bold text-blue-700 mb-4')
    
    # 权限检查
    can_view = current_user.has_permission('content.view')
    can_create = current_user.has_permission('content.create')
    can_edit = current_user.has_permission('content.edit')
    can_delete = current_user.has_permission('content.delete')
    
    # 显示权限提示
    with ui.card().classes('w-full mb-4 bg-blue-50'):
        ui.label('当前模块权限:').classes('font-bold mb-2')
        with ui.row().classes('gap-4'):
            ui.label(f'查看: {"✅" if can_view else "❌"}').classes('text-sm')
            ui.label(f'创建: {"✅" if can_create else "❌"}').classes('text-sm')
            ui.label(f'编辑: {"✅" if can_edit else "❌"}').classes('text-sm')
            ui.label(f'删除: {"✅" if can_delete else "❌"}').classes('text-sm')
    
    # 如果没有查看权限,显示提示
    if not can_view:
        ui.label('⚠️ 您没有查看文章的权限').classes('text-orange-600 text-lg')
        ui.label('请联系管理员分配 content.view 权限').classes('text-gray-600 text-sm')
        return
    
    # 创建文章按钮
    if can_create:
        ui.button('➕ 创建新文章', icon='add', on_click=lambda: show_create_article_dialog(current_user))\
            .classes('mb-4 bg-green-600 text-white')
    else:
        ui.button('➕ 创建新文章', icon='add').props('disable')\
            .classes('mb-4 bg-gray-400 text-white').tooltip('需要 content.create 权限')
    
    # 文章列表容器
    article_list_container = ui.column().classes('w-full gap-4')
    
    def refresh_article_list():
        """刷新文章列表"""
        article_list_container.clear()
        
        with article_list_container:
            # 根据权限决定显示哪些文章
            if can_edit or can_delete:
                # 有编辑/删除权限,显示所有文章
                articles = article_storage.get_all()
                ui.label(f'文章列表 (共 {len(articles)} 篇,包括草稿)').classes('text-lg font-bold mb-2')
            else:
                # 只能查看,显示已发布文章
                articles = article_storage.get_published()
                ui.label(f'已发布文章 (共 {len(articles)} 篇)').classes('text-lg font-bold mb-2')
            
            if not articles:
                ui.label('暂无文章').classes('text-gray-500 text-center py-8')
                return
            
            # 渲染文章列表
            for article in articles:
                render_article_card(article, current_user, refresh_article_list)
    
    # 初始加载
    refresh_article_list()


def render_article_card(article: Dict, current_user, refresh_callback):
    """
    渲染单个文章卡片
    """
    can_edit = current_user.has_permission('content.edit')
    can_delete = current_user.has_permission('content.delete')
    
    with ui.card().classes('w-full'):
        with ui.row().classes('w-full items-start justify-between'):
            # 左侧: 文章信息
            with ui.column().classes('flex-1'):
                # 标题和状态
                with ui.row().classes('items-center gap-2 mb-2'):
                    ui.label(article['title']).classes('text-xl font-bold text-gray-800')
                    
                    # 状态标签
                    if article['status'] == 'published':
                        ui.badge('已发布', color='green')
                    else:
                        ui.badge('草稿', color='gray')
                
                # 内容预览
                content_preview = article['content'][:100] + ('...' if len(article['content']) > 100 else '')
                ui.label(content_preview).classes('text-gray-600 text-sm mb-2')
                
                # 元信息
                with ui.row().classes('gap-4 text-xs text-gray-500'):
                    ui.label(f'👤 作者: {article["author"]}')
                    ui.label(f'📅 创建时间: {article["created_at"]}')
                    ui.label(f'🆔 ID: {article["id"]}')
            
            # 右侧: 操作按钮
            with ui.column().classes('gap-2'):
                # 编辑按钮
                if can_edit:
                    ui.button('编辑', icon='edit', 
                             on_click=lambda a=article: show_edit_article_dialog(a, current_user, refresh_callback))\
                        .props('flat color=primary size=sm')
                else:
                    ui.button('编辑', icon='edit').props('flat disable size=sm')\
                        .tooltip('需要 content.edit 权限')
                
                # 删除按钮
                if can_delete:
                    ui.button('删除', icon='delete',
                             on_click=lambda a=article: confirm_delete_article(a, refresh_callback))\
                        .props('flat color=negative size=sm')
                else:
                    ui.button('删除', icon='delete').props('flat disable size=sm')\
                        .tooltip('需要 content.delete 权限')


def show_create_article_dialog(current_user):
    """显示创建文章对话框"""
    
    with ui.dialog() as dialog, ui.card().classes('w-[600px]'):
        ui.label('➕ 创建新文章').classes('text-2xl font-bold mb-4')
        
        title_input = ui.input('文章标题', placeholder='请输入文章标题').classes('w-full')
        content_input = ui.textarea('文章内容', placeholder='请输入文章内容').classes('w-full').props('rows=10')
        
        with ui.row().classes('w-full justify-end gap-2 mt-4'):
            ui.button('取消', on_click=dialog.close).props('flat')
            
            def create_article():
                if not title_input.value or not content_input.value:
                    ui.notify('请填写完整信息', type='warning')
                    return
                
                try:
                    article_storage.create(
                        title=title_input.value,
                        content=content_input.value,
                        author=current_user.username
                    )
                    ui.notify('文章创建成功!', type='positive')
                    dialog.close()
                    ui.navigate.reload()  # 刷新页面
                except Exception as e:
                    log_error(f"创建文章失败: {e}")
                    ui.notify(f'创建失败: {str(e)}', type='negative')
            
            ui.button('创建', on_click=create_article).props('color=primary')
    
    dialog.open()


def show_edit_article_dialog(article: Dict, current_user, refresh_callback):
    """显示编辑文章对话框"""
    
    with ui.dialog() as dialog, ui.card().classes('w-[600px]'):
        ui.label(f'✏️ 编辑文章 (ID: {article["id"]})').classes('text-2xl font-bold mb-4')
        
        title_input = ui.input('文章标题', value=article['title']).classes('w-full')
        content_input = ui.textarea('文章内容', value=article['content']).classes('w-full').props('rows=10')
        
        status_select = ui.select(
            label='状态',
            options=['draft', 'published'],
            value=article['status']
        ).classes('w-full')
        
        with ui.row().classes('w-full justify-end gap-2 mt-4'):
            ui.button('取消', on_click=dialog.close).props('flat')
            
            def update_article():
                try:
                    article_storage.update(
                        article_id=article['id'],
                        title=title_input.value,
                        content=content_input.value,
                        status=status_select.value
                    )
                    ui.notify('文章更新成功!', type='positive')
                    dialog.close()
                    refresh_callback()
                except Exception as e:
                    log_error(f"更新文章失败: {e}")
                    ui.notify(f'更新失败: {str(e)}', type='negative')
            
            ui.button('保存', on_click=update_article).props('color=primary')
    
    dialog.open()


def confirm_delete_article(article: Dict, refresh_callback):
    """确认删除文章"""
    
    with ui.dialog() as dialog, ui.card():
        ui.label('确认删除?').classes('text-xl font-bold mb-2')
        ui.label(f'确定要删除文章 "{article["title"]}" 吗?').classes('mb-4')
        ui.label('此操作不可恢复!').classes('text-red-600 text-sm mb-4')
        
        with ui.row().classes('w-full justify-end gap-2'):
            ui.button('取消', on_click=dialog.close).props('flat')
            
            def delete_article():
                try:
                    article_storage.delete(article['id'])
                    ui.notify('文章已删除', type='positive')
                    dialog.close()
                    refresh_callback()
                except Exception as e:
                    log_error(f"删除文章失败: {e}")
                    ui.notify(f'删除失败: {str(e)}', type='negative')
            
            ui.button('确认删除', on_click=delete_article).props('color=negative')
    
    dialog.open()


# ========================================
# 模块2: 用户管理
# ========================================

def render_user_management(current_user):
    """
    用户管理模块
    
    功能:
    - 查看用户列表 (需要 user.manage)
    - 修改用户状态 (需要 user.manage)
    """
    
    ui.label('👥 用户管理系统').classes('text-2xl font-bold text-purple-700 mb-4')
    
    # 权限检查
    can_manage = current_user.has_permission('user.manage')
    
    # 显示权限提示
    with ui.card().classes('w-full mb-4 bg-purple-50'):
        ui.label('当前模块权限:').classes('font-bold mb-2')
        ui.label(f'用户管理: {"✅ 可以管理用户" if can_manage else "❌ 无权限"}').classes('text-sm')
    
    if not can_manage:
        ui.label('⚠️ 您没有用户管理权限').classes('text-orange-600 text-lg')
        ui.label('请联系管理员分配 user.manage 权限').classes('text-gray-600 text-sm')
        ui.label('提示: admin 角色拥有此权限').classes('text-blue-600 text-sm mt-2')
        return
    
    # 用户列表容器
    user_list_container = ui.column().classes('w-full gap-4')
    
    def refresh_user_list():
        """刷新用户列表"""
        user_list_container.clear()
        
        with user_list_container:
            try:
                with get_db() as session:
                    users = session.exec(select(User)).all()
                    
                    ui.label(f'系统用户列表 (共 {len(users)} 个用户)').classes('text-lg font-bold mb-2')
                    
                    for user in users:
                        render_user_card(user, refresh_user_list)
                        
            except Exception as e:
                log_error(f"获取用户列表失败: {e}")
                ui.label(f'加载失败: {str(e)}').classes('text-red-600')
    
    # 初始加载
    refresh_user_list()


def render_user_card(user: User, refresh_callback):
    """渲染用户卡片"""
    
    with ui.card().classes('w-full'):
        with ui.row().classes('w-full items-start justify-between'):
            # 用户信息
            with ui.column().classes('flex-1'):
                with ui.row().classes('items-center gap-2 mb-2'):
                    ui.label(user.username).classes('text-xl font-bold')
                    
                    # 状态标签
                    if user.is_superuser:
                        ui.badge('超级管理员', color='red')
                    if user.is_active:
                        ui.badge('激活', color='green')
                    else:
                        ui.badge('禁用', color='gray')
                    if user.is_verified:
                        ui.badge('已验证', color='blue')
                
                with ui.row().classes('gap-4 text-sm text-gray-600'):
                    ui.label(f'📧 {user.email}')
                    ui.label(f'👤 {user.full_name or "未设置"}')
                    ui.label(f'🆔 ID: {user.id}')
                
                # 角色信息
                try:
                    roles_text = ', '.join([role.display_name for role in user.roles]) if user.roles else '无角色'
                    ui.label(f'🎭 角色: {roles_text}').classes('text-sm text-purple-700 mt-1')
                except:
                    ui.label('🎭 角色: 加载失败').classes('text-sm text-gray-500 mt-1')
            
            # 操作按钮
            with ui.column().classes('gap-2'):
                # 切换激活状态
                def toggle_active():
                    try:
                        with get_db() as session:
                            db_user = session.get(User, user.id)
                            if db_user:
                                db_user.is_active = not db_user.is_active
                                session.commit()
                                ui.notify(f'用户 {user.username} 状态已更新', type='positive')
                                refresh_callback()
                    except Exception as e:
                        log_error(f"更新用户状态失败: {e}")
                        ui.notify(f'操作失败: {str(e)}', type='negative')
                
                if user.is_active:
                    ui.button('禁用', icon='block', on_click=toggle_active)\
                        .props('flat color=negative size=sm')
                else:
                    ui.button('激活', icon='check_circle', on_click=toggle_active)\
                        .props('flat color=positive size=sm')


# ========================================
# 模块3: 个人中心
# ========================================

def render_personal_center(current_user):
    """
    个人中心模块
    
    功能:
    - 查看个人信息 (需要 profile.view)
    - 编辑个人信息 (需要 profile.edit)
    """
    
    ui.label('👤 个人中心').classes('text-2xl font-bold text-green-700 mb-4')
    
    # 权限检查
    can_view = current_user.has_permission('profile.view')
    can_edit = current_user.has_permission('profile.edit')
    
    # 显示权限提示
    with ui.card().classes('w-full mb-4 bg-green-50'):
        ui.label('当前模块权限:').classes('font-bold mb-2')
        with ui.row().classes('gap-4'):
            ui.label(f'查看资料: {"✅" if can_view else "❌"}').classes('text-sm')
            ui.label(f'编辑资料: {"✅" if can_edit else "❌"}').classes('text-sm')
    
    if not can_view:
        ui.label('⚠️ 您没有查看个人资料的权限').classes('text-orange-600 text-lg')
        return
    
    # 个人信息展示
    with ui.card().classes('w-full mb-4'):
        ui.label('📋 基本信息').classes('text-lg font-bold mb-4')
        
        with ui.grid(columns=2).classes('w-full gap-4'):
            ui.label('用户名:').classes('font-semibold')
            ui.label(current_user.username)
            
            ui.label('姓名:').classes('font-semibold')
            ui.label(current_user.full_name or '未设置')
            
            ui.label('邮箱:').classes('font-semibold')
            ui.label(current_user.email)
            
            ui.label('手机:').classes('font-semibold')
            ui.label(current_user.phone or '未设置')
            
            ui.label('个人简介:').classes('font-semibold')
            ui.label(current_user.bio or '未设置')
    
    # 角色和权限信息
    with ui.card().classes('w-full mb-4'):
        ui.label('🎭 角色与权限').classes('text-lg font-bold mb-4')
        
        # 角色
        with ui.row().classes('gap-2 mb-3'):
            ui.label('拥有角色:').classes('font-semibold')
            if current_user.roles:
                for role in current_user.roles:
                    ui.badge(role, color='purple')
            else:
                ui.label('无角色').classes('text-gray-500')
        
        # 权限
        with ui.column().classes('w-full'):
            ui.label('拥有权限:').classes('font-semibold mb-2')
            
            if current_user.is_superuser:
                ui.badge('所有权限 (超级管理员)', color='red')
            elif current_user.permissions:
                with ui.grid(columns=3).classes('w-full gap-2'):
                    for perm in sorted(current_user.permissions):
                        ui.badge(perm, color='blue').classes('text-xs')
            else:
                ui.label('无直接权限').classes('text-gray-500')
    
    # 编辑按钮
    if can_edit:
        ui.button('✏️ 编辑个人资料', icon='edit',
                 on_click=lambda: show_edit_profile_dialog(current_user))\
            .classes('bg-green-600 text-white')
    else:
        ui.label('提示: 您没有编辑个人资料的权限').classes('text-gray-500 text-sm mt-4')


def show_edit_profile_dialog(current_user):
    """显示编辑个人资料对话框"""
    
    with ui.dialog() as dialog, ui.card().classes('w-[500px]'):
        ui.label('✏️ 编辑个人资料').classes('text-2xl font-bold mb-4')
        
        # 获取最新用户数据
        with get_db() as session:
            db_user = session.get(User, current_user.id)
            if not db_user:
                ui.label('无法加载用户数据').classes('text-red-600')
                return
            
            full_name_input = ui.input('姓名', value=db_user.full_name or '').classes('w-full')
            phone_input = ui.input('手机', value=db_user.phone or '').classes('w-full')
            bio_input = ui.textarea('个人简介', value=db_user.bio or '').classes('w-full').props('rows=3')
        
        with ui.row().classes('w-full justify-end gap-2 mt-4'):
            ui.button('取消', on_click=dialog.close).props('flat')
            
            def save_profile():
                try:
                    with get_db() as session:
                        db_user = session.get(User, current_user.id)
                        if db_user:
                            db_user.full_name = full_name_input.value
                            db_user.phone = phone_input.value
                            db_user.bio = bio_input.value
                            session.commit()
                            
                            ui.notify('个人资料更新成功!', type='positive')
                            dialog.close()
                            ui.navigate.reload()
                except Exception as e:
                    log_error(f"更新个人资料失败: {e}")
                    ui.notify(f'更新失败: {str(e)}', type='negative')
            
            ui.button('保存', on_click=save_profile).props('color=primary')
    
    dialog.open()


# ========================================
# 导出
# ========================================

__all__ = ['default_auth_page_content']