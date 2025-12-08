"""
ERP场景业务模拟页面 (ERP Scenario Business Demo)
=====================================================

功能说明:
--------
本页面全面模拟 ERP 场景下的真实业务应用,基于企业资源计划系统的业务流程。

数据源: 
  通过命令 `python scripts/init_database.py --scenario erp --test-data` 创建

角色体系 (7个角色):
  1. admin (系统管理员) - 拥有所有权限
  2. ceo (CEO) - 公司最高管理者,查看所有数据和审批
  3. finance_manager (财务经理) - 管理公司财务和账目
  4. purchase_manager (采购经理) - 管理采购订单和供应商
  5. sales_manager (销售经理) - 管理销售订单和客户
  6. warehouse_manager (仓库管理员) - 管理库存和出入库
  7. employee (普通员工) - 基础权限

权限体系 (24个权限):
  系统权限 (3个):
    - system.manage: 系统管理
    - user.manage: 用户管理
    - role.manage: 角色管理
  
  财务权限 (5个):
    - finance.view: 查看财务
    - finance.manage: 管理财务
    - invoice.create: 创建发票
    - invoice.approve: 审批发票
    - payment.manage: 管理付款
  
  采购权限 (4个):
    - purchase.view: 查看采购
    - purchase.create: 创建采购
    - purchase.approve: 审批采购
    - supplier.manage: 管理供应商
  
  销售权限 (4个):
    - sales.view: 查看销售
    - sales.create: 创建销售
    - sales.approve: 审批销售
    - customer.manage: 管理客户
  
  库存权限 (4个):
    - inventory.view: 查看库存
    - inventory.manage: 管理库存
    - warehouse.in: 入库操作
    - warehouse.out: 出库操作
  
  报表权限 (2个):
    - report.view: 查看报表
    - report.export: 导出报表
  
  个人权限 (2个):
    - profile.view: 查看资料
    - profile.edit: 编辑资料

测试账号:
  - admin/admin123        (系统管理员,所有权限)
  - ceo/ceo123           (CEO,查看所有+审批权限)
  - finance/finance123   (财务经理,财务+发票+付款)
  - purchase/purchase123 (采购经理,采购+供应商+库存查看)
  - sales/sales123       (销售经理,销售+客户+发票创建) - 需添加
  - warehouse/warehouse123 (仓库管理员,库存+出入库) - 需添加

业务场景设计:
-----------
1. 采购管理模块 (Purchase Management)
   - 采购订单列表
   - 创建采购订单 (需要 purchase.create)
   - 审批采购订单 (需要 purchase.approve)
   - 供应商管理 (需要 supplier.manage)

2. 销售管理模块 (Sales Management)
   - 销售订单列表
   - 创建销售订单 (需要 sales.create)
   - 审批销售订单 (需要 sales.approve)
   - 客户管理 (需要 customer.manage)

3. 库存管理模块 (Inventory Management)
   - 库存状态查看 (需要 inventory.view)
   - 入库操作 (需要 warehouse.in)
   - 出库操作 (需要 warehouse.out)
   - 库存调整 (需要 inventory.manage)

4. 财务管理模块 (Finance Management)
   - 财务报表查看 (需要 finance.view)
   - 发票管理 (需要 invoice.create/approve)
   - 付款管理 (需要 payment.manage)

5. 报表中心 (Report Center)
   - 查看各类报表 (需要 report.view)
   - 导出报表数据 (需要 report.export)

技术特点:
--------
- 完整的 ERP 业务流程模拟
- 审批工作流实现
- 状态机管理
- 跨模块数据关联
- 符合企业实际业务场景
"""

from nicegui import ui
from auth import auth_manager, require_login
from auth.database import get_db
from auth.models import User
from sqlmodel import select
from common.log_handler import (
    log_info, log_success, log_warning, log_error,
    safe_protect, get_logger
)
from datetime import datetime
from typing import List, Dict, Optional
from decimal import Decimal

logger = get_logger(__name__)


# ========================================
# 数据模型模拟 (ERP 业务数据)
# ========================================

class PurchaseOrderStorage:
    """采购订单存储"""
    
    def __init__(self):
        self.orders: List[Dict] = [
            {
                'id': 'PO-2024-001',
                'supplier': '深圳科技有限公司',
                'items': '笔记本电脑 × 10',
                'amount': Decimal('50000.00'),
                'status': 'pending',  # pending, approved, rejected
                'created_by': 'purchase',
                'created_at': '2024-01-15 09:30:00',
                'approved_by': None,
                'approved_at': None
            },
            {
                'id': 'PO-2024-002',
                'supplier': '办公用品批发商',
                'items': '办公桌椅 × 20',
                'amount': Decimal('30000.00'),
                'status': 'approved',
                'created_by': 'purchase',
                'created_at': '2024-01-10 14:20:00',
                'approved_by': 'ceo',
                'approved_at': '2024-01-11 10:00:00'
            },
        ]
        self.next_id = 3
    
    def get_all(self) -> List[Dict]:
        return self.orders
    
    def get_by_status(self, status: str) -> List[Dict]:
        return [o for o in self.orders if o['status'] == status]
    
    def create(self, supplier: str, items: str, amount: Decimal, created_by: str) -> Dict:
        order = {
            'id': f'PO-2024-{self.next_id:03d}',
            'supplier': supplier,
            'items': items,
            'amount': amount,
            'status': 'pending',
            'created_by': created_by,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'approved_by': None,
            'approved_at': None
        }
        self.orders.append(order)
        self.next_id += 1
        return order
    
    def approve(self, order_id: str, approved_by: str) -> bool:
        for order in self.orders:
            if order['id'] == order_id:
                order['status'] = 'approved'
                order['approved_by'] = approved_by
                order['approved_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                return True
        return False
    
    def reject(self, order_id: str) -> bool:
        for order in self.orders:
            if order['id'] == order_id:
                order['status'] = 'rejected'
                return True
        return False


class SalesOrderStorage:
    """销售订单存储"""
    
    def __init__(self):
        self.orders: List[Dict] = [
            {
                'id': 'SO-2024-001',
                'customer': '北京贸易公司',
                'items': '产品A × 100',
                'amount': Decimal('80000.00'),
                'status': 'pending',
                'created_by': 'purchase',  # 模拟数据,实际应该是 sales
                'created_at': '2024-01-16 10:00:00',
                'approved_by': None,
                'approved_at': None
            },
            {
                'id': 'SO-2024-002',
                'customer': '上海集团',
                'items': '产品B × 50',
                'amount': Decimal('120000.00'),
                'status': 'approved',
                'created_by': 'purchase',
                'created_at': '2024-01-12 15:30:00',
                'approved_by': 'ceo',
                'approved_at': '2024-01-13 09:00:00'
            },
        ]
        self.next_id = 3
    
    def get_all(self) -> List[Dict]:
        return self.orders
    
    def get_by_status(self, status: str) -> List[Dict]:
        return [o for o in self.orders if o['status'] == status]
    
    def create(self, customer: str, items: str, amount: Decimal, created_by: str) -> Dict:
        order = {
            'id': f'SO-2024-{self.next_id:03d}',
            'customer': customer,
            'items': items,
            'amount': amount,
            'status': 'pending',
            'created_by': created_by,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'approved_by': None,
            'approved_at': None
        }
        self.orders.append(order)
        self.next_id += 1
        return order
    
    def approve(self, order_id: str, approved_by: str) -> bool:
        for order in self.orders:
            if order['id'] == order_id:
                order['status'] = 'approved'
                order['approved_by'] = approved_by
                order['approved_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                return True
        return False


class InventoryStorage:
    """库存存储"""
    
    def __init__(self):
        self.items: List[Dict] = [
            {
                'id': 'SKU-001',
                'name': '笔记本电脑',
                'category': '电子产品',
                'quantity': 50,
                'unit_price': Decimal('5000.00'),
                'min_stock': 10,
                'location': 'A区-01货架'
            },
            {
                'id': 'SKU-002',
                'name': '办公桌椅',
                'category': '办公家具',
                'quantity': 8,
                'unit_price': Decimal('1500.00'),
                'min_stock': 5,
                'location': 'B区-03货架'
            },
            {
                'id': 'SKU-003',
                'name': '产品A',
                'category': '主营产品',
                'quantity': 200,
                'unit_price': Decimal('800.00'),
                'min_stock': 50,
                'location': 'C区-05货架'
            },
        ]
    
    def get_all(self) -> List[Dict]:
        return self.items
    
    def get_low_stock(self) -> List[Dict]:
        """获取低库存商品"""
        return [item for item in self.items if item['quantity'] <= item['min_stock']]
    
    def adjust_stock(self, item_id: str, quantity_change: int, operation: str) -> bool:
        """调整库存 operation: 'in' 或 'out'"""
        for item in self.items:
            if item['id'] == item_id:
                if operation == 'in':
                    item['quantity'] += quantity_change
                elif operation == 'out':
                    if item['quantity'] >= quantity_change:
                        item['quantity'] -= quantity_change
                    else:
                        return False
                return True
        return False


# 全局存储实例
purchase_storage = PurchaseOrderStorage()
sales_storage = SalesOrderStorage()
inventory_storage = InventoryStorage()


# ========================================
# 主页面入口
# ========================================

@safe_protect(name="ERP场景业务页面", error_msg="ERP场景业务页面加载失败")
@require_login(redirect_to_login=True)
def erp_auth_page_content():
    """
    ERP场景业务模拟页面主入口
    
    页面结构:
    1. 页面标题和当前用户信息
    2. 权限状态面板
    3. 业务功能模块切换
       - 采购管理
       - 销售管理
       - 库存管理
       - 财务管理
       - 报表中心
    """
    
    # 获取当前用户
    current_user = auth_manager.check_session()
    if not current_user:
        ui.label('❌ 无法获取当前用户信息').classes('text-red-600')
        return
    
    # ===========================
    # 页面标题
    # ===========================
    ui.label('🏢 ERP 企业资源计划系统').classes('text-3xl font-bold text-indigo-700 mb-2')
    ui.label('ERP Scenario Business Demo').classes('text-sm text-gray-500 mb-6')
    
    # ===========================
    # 当前用户信息卡片
    # ===========================
    with ui.card().classes('w-full mb-6 bg-gradient-to-r from-indigo-50 to-purple-50'):
        ui.label('👤 当前登录用户').classes('text-lg font-bold text-indigo-800 mb-2')
        
        with ui.row().classes('gap-4 w-full'):
            with ui.column().classes('flex-1'):
                ui.label(f'用户名: {current_user.username}').classes('text-sm')
                ui.label(f'姓名: {current_user.full_name or "未设置"}').classes('text-sm')
                ui.label(f'邮箱: {current_user.email}').classes('text-sm')
            
            with ui.column().classes('flex-1'):
                # 显示角色
                roles_text = ', '.join(current_user.roles) if current_user.roles else '无'
                ui.label(f'角色: {roles_text}').classes('text-sm font-semibold text-purple-700')
                
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
        tab_purchase = ui.tab('🛒 采购管理', icon='shopping_cart')
        tab_sales = ui.tab('💰 销售管理', icon='attach_money')
        tab_inventory = ui.tab('📦 库存管理', icon='inventory')
        tab_finance = ui.tab('💳 财务管理', icon='account_balance')
        tab_report = ui.tab('📊 报表中心', icon='assessment')
    
    with ui.tab_panels(tabs, value=tab_purchase).classes('w-full'):
        with ui.tab_panel(tab_purchase):
            render_purchase_management(current_user)
        
        with ui.tab_panel(tab_sales):
            render_sales_management(current_user)
        
        with ui.tab_panel(tab_inventory):
            render_inventory_management(current_user)
        
        with ui.tab_panel(tab_finance):
            render_finance_management(current_user)
        
        with ui.tab_panel(tab_report):
            render_report_center(current_user)


# ========================================
# 权限状态面板
# ========================================

def render_permission_status_panel(current_user):
    """渲染权限状态面板"""
    
    permission_groups = [
        {
            'category': '系统权限',
            'permissions': [
                ('system.manage', '系统管理'),
                ('user.manage', '用户管理'),
                ('role.manage', '角色管理'),
            ]
        },
        {
            'category': '财务权限',
            'permissions': [
                ('finance.view', '查看财务'),
                ('finance.manage', '管理财务'),
                ('invoice.create', '创建发票'),
                ('invoice.approve', '审批发票'),
                ('payment.manage', '管理付款'),
            ]
        },
        {
            'category': '采购权限',
            'permissions': [
                ('purchase.view', '查看采购'),
                ('purchase.create', '创建采购'),
                ('purchase.approve', '审批采购'),
                ('supplier.manage', '管理供应商'),
            ]
        },
        {
            'category': '销售权限',
            'permissions': [
                ('sales.view', '查看销售'),
                ('sales.create', '创建销售'),
                ('sales.approve', '审批销售'),
                ('customer.manage', '管理客户'),
            ]
        },
        {
            'category': '库存权限',
            'permissions': [
                ('inventory.view', '查看库存'),
                ('inventory.manage', '管理库存'),
                ('warehouse.in', '入库操作'),
                ('warehouse.out', '出库操作'),
            ]
        },
        {
            'category': '报表权限',
            'permissions': [
                ('report.view', '查看报表'),
                ('report.export', '导出报表'),
            ]
        },
    ]
    
    for group in permission_groups:
        with ui.card().classes('w-full mb-4'):
            ui.label(f'{group["category"]}').classes('text-lg font-bold mb-2')
            
            with ui.grid(columns=2).classes('w-full gap-2'):
                for perm_name, perm_display in group['permissions']:
                    has_perm = current_user.has_permission(perm_name)
                    
                    with ui.row().classes('items-center gap-2'):
                        if has_perm:
                            ui.icon('check_circle', color='green').classes('text-xl')
                            ui.label(perm_display).classes('text-green-700')
                        else:
                            ui.icon('cancel', color='red').classes('text-xl')
                            ui.label(perm_display).classes('text-gray-400 line-through')


# ========================================
# 模块1: 采购管理
# ========================================

def render_purchase_management(current_user):
    """采购管理模块"""
    
    ui.label('🛒 采购管理系统').classes('text-2xl font-bold text-blue-700 mb-4')
    
    can_view = current_user.has_permission('purchase.view')
    can_create = current_user.has_permission('purchase.create')
    can_approve = current_user.has_permission('purchase.approve')
    
    # 权限提示
    with ui.card().classes('w-full mb-4 bg-blue-50'):
        ui.label('当前模块权限:').classes('font-bold mb-2')
        with ui.row().classes('gap-4'):
            ui.label(f'查看: {"✅" if can_view else "❌"}').classes('text-sm')
            ui.label(f'创建: {"✅" if can_create else "❌"}').classes('text-sm')
            ui.label(f'审批: {"✅" if can_approve else "❌"}').classes('text-sm')
    
    if not can_view:
        ui.label('⚠️ 您没有查看采购订单的权限').classes('text-orange-600 text-lg')
        ui.label('需要 purchase.view 权限').classes('text-gray-600 text-sm')
        return
    
    # 创建按钮
    if can_create:
        ui.button('➕ 创建采购订单', icon='add',
                 on_click=lambda: show_create_purchase_dialog(current_user))\
            .classes('mb-4 bg-blue-600 text-white')
    
    # 订单列表
    order_list_container = ui.column().classes('w-full gap-4')
    
    def refresh_orders():
        order_list_container.clear()
        
        with order_list_container:
            orders = purchase_storage.get_all()
            ui.label(f'采购订单列表 (共 {len(orders)} 个)').classes('text-lg font-bold mb-2')
            
            for order in orders:
                render_purchase_order_card(order, current_user, refresh_orders)
    
    refresh_orders()


def render_purchase_order_card(order: Dict, current_user, refresh_callback):
    """渲染采购订单卡片"""
    
    can_approve = current_user.has_permission('purchase.approve')
    
    with ui.card().classes('w-full'):
        with ui.row().classes('w-full items-start justify-between'):
            # 订单信息
            with ui.column().classes('flex-1'):
                with ui.row().classes('items-center gap-2 mb-2'):
                    ui.label(order['id']).classes('text-xl font-bold text-blue-800')
                    
                    # 状态标签
                    if order['status'] == 'approved':
                        ui.badge('已审批', color='green')
                    elif order['status'] == 'rejected':
                        ui.badge('已拒绝', color='red')
                    else:
                        ui.badge('待审批', color='orange')
                
                with ui.grid(columns=2).classes('w-full gap-2 text-sm'):
                    ui.label('供应商:').classes('font-semibold')
                    ui.label(order['supplier'])
                    
                    ui.label('采购物品:').classes('font-semibold')
                    ui.label(order['items'])
                    
                    ui.label('采购金额:').classes('font-semibold')
                    ui.label(f'¥{order["amount"]:,.2f}').classes('text-green-700 font-bold')
                    
                    ui.label('创建人:').classes('font-semibold')
                    ui.label(order['created_by'])
                    
                    ui.label('创建时间:').classes('font-semibold')
                    ui.label(order['created_at'])
                    
                    if order['approved_by']:
                        ui.label('审批人:').classes('font-semibold')
                        ui.label(order['approved_by'])
            
            # 操作按钮
            with ui.column().classes('gap-2'):
                if order['status'] == 'pending' and can_approve:
                    ui.button('✅ 审批通过', icon='check',
                             on_click=lambda o=order: approve_purchase_order(o, current_user, refresh_callback))\
                        .props('flat color=positive size=sm')
                    
                    ui.button('❌ 拒绝', icon='close',
                             on_click=lambda o=order: reject_purchase_order(o, refresh_callback))\
                        .props('flat color=negative size=sm')


def show_create_purchase_dialog(current_user):
    """创建采购订单对话框"""
    
    with ui.dialog() as dialog, ui.card().classes('w-[600px]'):
        ui.label('➕ 创建采购订单').classes('text-2xl font-bold mb-4')
        
        supplier_input = ui.input('供应商名称', placeholder='请输入供应商名称').classes('w-full')
        items_input = ui.input('采购物品', placeholder='例如: 笔记本电脑 × 10').classes('w-full')
        amount_input = ui.number('采购金额', value=0, step=100).classes('w-full')
        
        with ui.row().classes('w-full justify-end gap-2 mt-4'):
            ui.button('取消', on_click=dialog.close).props('flat')
            
            def create_order():
                if not supplier_input.value or not items_input.value or amount_input.value <= 0:
                    ui.notify('请填写完整信息', type='warning')
                    return
                
                try:
                    purchase_storage.create(
                        supplier=supplier_input.value,
                        items=items_input.value,
                        amount=Decimal(str(amount_input.value)),
                        created_by=current_user.username
                    )
                    ui.notify('采购订单创建成功!', type='positive')
                    dialog.close()
                    ui.navigate.reload()
                except Exception as e:
                    log_error(f"创建采购订单失败: {e}")
                    ui.notify(f'创建失败: {str(e)}', type='negative')
            
            ui.button('创建', on_click=create_order).props('color=primary')
    
    dialog.open()


def approve_purchase_order(order: Dict, current_user, refresh_callback):
    """审批采购订单"""
    try:
        purchase_storage.approve(order['id'], current_user.username)
        ui.notify(f'采购订单 {order["id"]} 已审批通过', type='positive')
        refresh_callback()
    except Exception as e:
        log_error(f"审批采购订单失败: {e}")
        ui.notify(f'审批失败: {str(e)}', type='negative')


def reject_purchase_order(order: Dict, refresh_callback):
    """拒绝采购订单"""
    try:
        purchase_storage.reject(order['id'])
        ui.notify(f'采购订单 {order["id"]} 已拒绝', type='warning')
        refresh_callback()
    except Exception as e:
        log_error(f"拒绝采购订单失败: {e}")
        ui.notify(f'操作失败: {str(e)}', type='negative')


# ========================================
# 模块2: 销售管理
# ========================================

def render_sales_management(current_user):
    """销售管理模块"""
    
    ui.label('💰 销售管理系统').classes('text-2xl font-bold text-green-700 mb-4')
    
    can_view = current_user.has_permission('sales.view')
    can_create = current_user.has_permission('sales.create')
    can_approve = current_user.has_permission('sales.approve')
    
    # 权限提示
    with ui.card().classes('w-full mb-4 bg-green-50'):
        ui.label('当前模块权限:').classes('font-bold mb-2')
        with ui.row().classes('gap-4'):
            ui.label(f'查看: {"✅" if can_view else "❌"}').classes('text-sm')
            ui.label(f'创建: {"✅" if can_create else "❌"}').classes('text-sm')
            ui.label(f'审批: {"✅" if can_approve else "❌"}').classes('text-sm')
    
    if not can_view:
        ui.label('⚠️ 您没有查看销售订单的权限').classes('text-orange-600 text-lg')
        ui.label('需要 sales.view 权限').classes('text-gray-600 text-sm')
        return
    
    # 创建按钮
    if can_create:
        ui.button('➕ 创建销售订单', icon='add',
                 on_click=lambda: show_create_sales_dialog(current_user))\
            .classes('mb-4 bg-green-600 text-white')
    
    # 订单列表
    order_list_container = ui.column().classes('w-full gap-4')
    
    def refresh_orders():
        order_list_container.clear()
        
        with order_list_container:
            orders = sales_storage.get_all()
            ui.label(f'销售订单列表 (共 {len(orders)} 个)').classes('text-lg font-bold mb-2')
            
            for order in orders:
                render_sales_order_card(order, current_user, refresh_orders)
    
    refresh_orders()


def render_sales_order_card(order: Dict, current_user, refresh_callback):
    """渲染销售订单卡片"""
    
    can_approve = current_user.has_permission('sales.approve')
    
    with ui.card().classes('w-full'):
        with ui.row().classes('w-full items-start justify-between'):
            # 订单信息
            with ui.column().classes('flex-1'):
                with ui.row().classes('items-center gap-2 mb-2'):
                    ui.label(order['id']).classes('text-xl font-bold text-green-800')
                    
                    if order['status'] == 'approved':
                        ui.badge('已审批', color='green')
                    elif order['status'] == 'rejected':
                        ui.badge('已拒绝', color='red')
                    else:
                        ui.badge('待审批', color='orange')
                
                with ui.grid(columns=2).classes('w-full gap-2 text-sm'):
                    ui.label('客户:').classes('font-semibold')
                    ui.label(order['customer'])
                    
                    ui.label('销售物品:').classes('font-semibold')
                    ui.label(order['items'])
                    
                    ui.label('销售金额:').classes('font-semibold')
                    ui.label(f'¥{order["amount"]:,.2f}').classes('text-green-700 font-bold')
                    
                    ui.label('创建人:').classes('font-semibold')
                    ui.label(order['created_by'])
                    
                    ui.label('创建时间:').classes('font-semibold')
                    ui.label(order['created_at'])
            
            # 操作按钮
            with ui.column().classes('gap-2'):
                if order['status'] == 'pending' and can_approve:
                    ui.button('✅ 审批通过', icon='check',
                             on_click=lambda o=order: approve_sales_order(o, current_user, refresh_callback))\
                        .props('flat color=positive size=sm')


def show_create_sales_dialog(current_user):
    """创建销售订单对话框"""
    
    with ui.dialog() as dialog, ui.card().classes('w-[600px]'):
        ui.label('➕ 创建销售订单').classes('text-2xl font-bold mb-4')
        
        customer_input = ui.input('客户名称', placeholder='请输入客户名称').classes('w-full')
        items_input = ui.input('销售物品', placeholder='例如: 产品A × 100').classes('w-full')
        amount_input = ui.number('销售金额', value=0, step=100).classes('w-full')
        
        with ui.row().classes('w-full justify-end gap-2 mt-4'):
            ui.button('取消', on_click=dialog.close).props('flat')
            
            def create_order():
                if not customer_input.value or not items_input.value or amount_input.value <= 0:
                    ui.notify('请填写完整信息', type='warning')
                    return
                
                try:
                    sales_storage.create(
                        customer=customer_input.value,
                        items=items_input.value,
                        amount=Decimal(str(amount_input.value)),
                        created_by=current_user.username
                    )
                    ui.notify('销售订单创建成功!', type='positive')
                    dialog.close()
                    ui.navigate.reload()
                except Exception as e:
                    log_error(f"创建销售订单失败: {e}")
                    ui.notify(f'创建失败: {str(e)}', type='negative')
            
            ui.button('创建', on_click=create_order).props('color=primary')
    
    dialog.open()


def approve_sales_order(order: Dict, current_user, refresh_callback):
    """审批销售订单"""
    try:
        sales_storage.approve(order['id'], current_user.username)
        ui.notify(f'销售订单 {order["id"]} 已审批通过', type='positive')
        refresh_callback()
    except Exception as e:
        log_error(f"审批销售订单失败: {e}")
        ui.notify(f'审批失败: {str(e)}', type='negative')


# ========================================
# 模块3: 库存管理
# ========================================

def render_inventory_management(current_user):
    """库存管理模块"""
    
    ui.label('📦 库存管理系统').classes('text-2xl font-bold text-purple-700 mb-4')
    
    can_view = current_user.has_permission('inventory.view')
    can_manage = current_user.has_permission('inventory.manage')
    can_in = current_user.has_permission('warehouse.in')
    can_out = current_user.has_permission('warehouse.out')
    
    # 权限提示
    with ui.card().classes('w-full mb-4 bg-purple-50'):
        ui.label('当前模块权限:').classes('font-bold mb-2')
        with ui.row().classes('gap-4'):
            ui.label(f'查看: {"✅" if can_view else "❌"}').classes('text-sm')
            ui.label(f'管理: {"✅" if can_manage else "❌"}').classes('text-sm')
            ui.label(f'入库: {"✅" if can_in else "❌"}').classes('text-sm')
            ui.label(f'出库: {"✅" if can_out else "❌"}').classes('text-sm')
    
    if not can_view:
        ui.label('⚠️ 您没有查看库存的权限').classes('text-orange-600 text-lg')
        ui.label('需要 inventory.view 权限').classes('text-gray-600 text-sm')
        return
    
    # 库存状态统计
    items = inventory_storage.get_all()
    low_stock = inventory_storage.get_low_stock()
    total_value = sum(item['quantity'] * item['unit_price'] for item in items)
    
    with ui.card().classes('w-full mb-4 bg-gradient-to-r from-purple-100 to-pink-100'):
        ui.label('📊 库存概览').classes('text-lg font-bold mb-2')
        with ui.row().classes('gap-6'):
            with ui.column().classes('items-center'):
                ui.label(str(len(items))).classes('text-3xl font-bold text-purple-700')
                ui.label('总商品数').classes('text-sm text-gray-600')
            
            with ui.column().classes('items-center'):
                ui.label(str(sum(item['quantity'] for item in items))).classes('text-3xl font-bold text-blue-700')
                ui.label('总库存量').classes('text-sm text-gray-600')
            
            with ui.column().classes('items-center'):
                ui.label(f'¥{total_value:,.2f}').classes('text-3xl font-bold text-green-700')
                ui.label('库存总值').classes('text-sm text-gray-600')
            
            with ui.column().classes('items-center'):
                ui.label(str(len(low_stock))).classes('text-3xl font-bold text-red-700')
                ui.label('低库存预警').classes('text-sm text-gray-600')
    
    # 库存列表
    ui.label('库存明细').classes('text-lg font-bold mb-2')
    
    for item in items:
        render_inventory_item_card(item, current_user)


def render_inventory_item_card(item: Dict, current_user):
    """渲染库存项目卡片"""
    
    can_in = current_user.has_permission('warehouse.in')
    can_out = current_user.has_permission('warehouse.out')
    
    is_low_stock = item['quantity'] <= item['min_stock']
    
    with ui.card().classes('w-full'):
        with ui.row().classes('w-full items-start justify-between'):
            # 商品信息
            with ui.column().classes('flex-1'):
                with ui.row().classes('items-center gap-2 mb-2'):
                    ui.label(f'{item["name"]} ({item["id"]})').classes('text-xl font-bold')
                    
                    if is_low_stock:
                        ui.badge('低库存预警', color='red').classes('animate-pulse')
                
                with ui.grid(columns=3).classes('w-full gap-2 text-sm'):
                    ui.label('分类:').classes('font-semibold')
                    ui.label(item['category']).props('colspan=2')
                    
                    ui.label('当前库存:').classes('font-semibold')
                    stock_color = 'text-red-700' if is_low_stock else 'text-green-700'
                    ui.label(f'{item["quantity"]} 件').classes(f'{stock_color} font-bold').props('colspan=2')
                    
                    ui.label('最低库存:').classes('font-semibold')
                    ui.label(f'{item["min_stock"]} 件').props('colspan=2')
                    
                    ui.label('单价:').classes('font-semibold')
                    ui.label(f'¥{item["unit_price"]:,.2f}').props('colspan=2')
                    
                    ui.label('库存位置:').classes('font-semibold')
                    ui.label(item['location']).props('colspan=2')
            
            # 操作按钮
            with ui.column().classes('gap-2'):
                if can_in:
                    ui.button('📥 入库', icon='add',
                             on_click=lambda i=item: show_warehouse_in_dialog(i))\
                        .props('flat color=positive size=sm')
                
                if can_out:
                    ui.button('📤 出库', icon='remove',
                             on_click=lambda i=item: show_warehouse_out_dialog(i))\
                        .props('flat color=primary size=sm')


def show_warehouse_in_dialog(item: Dict):
    """入库操作对话框"""
    
    with ui.dialog() as dialog, ui.card().classes('w-[400px]'):
        ui.label(f'📥 入库操作 - {item["name"]}').classes('text-xl font-bold mb-4')
        
        ui.label(f'当前库存: {item["quantity"]} 件').classes('text-sm mb-2')
        
        quantity_input = ui.number('入库数量', value=0, min=1, step=1).classes('w-full')
        
        with ui.row().classes('w-full justify-end gap-2 mt-4'):
            ui.button('取消', on_click=dialog.close).props('flat')
            
            def warehouse_in():
                if quantity_input.value <= 0:
                    ui.notify('请输入有效数量', type='warning')
                    return
                
                try:
                    inventory_storage.adjust_stock(item['id'], int(quantity_input.value), 'in')
                    ui.notify(f'入库成功! {item["name"]} +{int(quantity_input.value)} 件', type='positive')
                    dialog.close()
                    ui.navigate.reload()
                except Exception as e:
                    log_error(f"入库操作失败: {e}")
                    ui.notify(f'入库失败: {str(e)}', type='negative')
            
            ui.button('确认入库', on_click=warehouse_in).props('color=positive')
    
    dialog.open()


def show_warehouse_out_dialog(item: Dict):
    """出库操作对话框"""
    
    with ui.dialog() as dialog, ui.card().classes('w-[400px]'):
        ui.label(f'📤 出库操作 - {item["name"]}').classes('text-xl font-bold mb-4')
        
        ui.label(f'当前库存: {item["quantity"]} 件').classes('text-sm mb-2')
        
        quantity_input = ui.number('出库数量', value=0, min=1, max=item['quantity'], step=1).classes('w-full')
        
        with ui.row().classes('w-full justify-end gap-2 mt-4'):
            ui.button('取消', on_click=dialog.close).props('flat')
            
            def warehouse_out():
                if quantity_input.value <= 0 or quantity_input.value > item['quantity']:
                    ui.notify('请输入有效数量', type='warning')
                    return
                
                try:
                    success = inventory_storage.adjust_stock(item['id'], int(quantity_input.value), 'out')
                    if success:
                        ui.notify(f'出库成功! {item["name"]} -{int(quantity_input.value)} 件', type='positive')
                        dialog.close()
                        ui.navigate.reload()
                    else:
                        ui.notify('库存不足', type='warning')
                except Exception as e:
                    log_error(f"出库操作失败: {e}")
                    ui.notify(f'出库失败: {str(e)}', type='negative')
            
            ui.button('确认出库', on_click=warehouse_out).props('color=primary')
    
    dialog.open()


# ========================================
# 模块4: 财务管理
# ========================================

def render_finance_management(current_user):
    """财务管理模块"""
    
    ui.label('💳 财务管理系统').classes('text-2xl font-bold text-yellow-700 mb-4')
    
    can_view = current_user.has_permission('finance.view')
    can_manage = current_user.has_permission('finance.manage')
    
    # 权限提示
    with ui.card().classes('w-full mb-4 bg-yellow-50'):
        ui.label('当前模块权限:').classes('font-bold mb-2')
        with ui.row().classes('gap-4'):
            ui.label(f'查看财务: {"✅" if can_view else "❌"}').classes('text-sm')
            ui.label(f'管理财务: {"✅" if can_manage else "❌"}').classes('text-sm')
    
    if not can_view:
        ui.label('⚠️ 您没有查看财务数据的权限').classes('text-orange-600 text-lg')
        ui.label('需要 finance.view 权限').classes('text-gray-600 text-sm')
        ui.label('提示: finance_manager 或 ceo 角色拥有此权限').classes('text-blue-600 text-sm mt-2')
        return
    
    # 财务概览
    purchase_orders = purchase_storage.get_all()
    sales_orders = sales_storage.get_all()
    
    total_purchase = sum(o['amount'] for o in purchase_orders if o['status'] == 'approved')
    total_sales = sum(o['amount'] for o in sales_orders if o['status'] == 'approved')
    profit = total_sales - total_purchase
    
    with ui.card().classes('w-full mb-4 bg-gradient-to-r from-yellow-100 to-orange-100'):
        ui.label('💰 财务概览').classes('text-lg font-bold mb-4')
        
        with ui.row().classes('gap-8'):
            with ui.column().classes('items-center'):
                ui.label(f'¥{total_sales:,.2f}').classes('text-3xl font-bold text-green-700')
                ui.label('总销售额').classes('text-sm text-gray-600')
            
            with ui.column().classes('items-center'):
                ui.label(f'¥{total_purchase:,.2f}').classes('text-3xl font-bold text-red-700')
                ui.label('总采购额').classes('text-sm text-gray-600')
            
            with ui.column().classes('items-center'):
                profit_color = 'text-green-700' if profit >= 0 else 'text-red-700'
                ui.label(f'¥{profit:,.2f}').classes(f'text-3xl font-bold {profit_color}')
                ui.label('毛利润').classes('text-sm text-gray-600')
    
    # 待审批订单统计
    pending_purchase = len([o for o in purchase_orders if o['status'] == 'pending'])
    pending_sales = len([o for o in sales_orders if o['status'] == 'pending'])
    
    with ui.card().classes('w-full mb-4'):
        ui.label('📋 待处理事项').classes('text-lg font-bold mb-2')
        with ui.row().classes('gap-4'):
            ui.label(f'待审批采购订单: {pending_purchase} 个').classes('text-sm')
            ui.label(f'待审批销售订单: {pending_sales} 个').classes('text-sm')
    
    # 发票管理提示
    if can_manage:
        with ui.card().classes('w-full'):
            ui.label('📄 发票管理').classes('text-lg font-bold mb-2')
            ui.label('发票管理功能开发中...').classes('text-gray-500')
            ui.label('包括: 创建发票、审批发票、付款管理等功能').classes('text-sm text-gray-600')


# ========================================
# 模块5: 报表中心
# ========================================

def render_report_center(current_user):
    """报表中心模块"""
    
    ui.label('📊 报表中心').classes('text-2xl font-bold text-teal-700 mb-4')
    
    can_view = current_user.has_permission('report.view')
    can_export = current_user.has_permission('report.export')
    
    # 权限提示
    with ui.card().classes('w-full mb-4 bg-teal-50'):
        ui.label('当前模块权限:').classes('font-bold mb-2')
        with ui.row().classes('gap-4'):
            ui.label(f'查看报表: {"✅" if can_view else "❌"}').classes('text-sm')
            ui.label(f'导出报表: {"✅" if can_export else "❌"}').classes('text-sm')
    
    if not can_view:
        ui.label('⚠️ 您没有查看报表的权限').classes('text-orange-600 text-lg')
        ui.label('需要 report.view 权限').classes('text-gray-600 text-sm')
        return
    
    # 报表列表
    reports = [
        {'name': '采购订单报表', 'description': '查看所有采购订单统计', 'icon': '🛒'},
        {'name': '销售订单报表', 'description': '查看所有销售订单统计', 'icon': '💰'},
        {'name': '库存状态报表', 'description': '查看库存现状和预警', 'icon': '📦'},
        {'name': '财务报表', 'description': '查看收入、支出和利润', 'icon': '💳'},
        {'name': '综合经营报表', 'description': '查看整体经营状况', 'icon': '📈'},
    ]
    
    for report in reports:
        with ui.card().classes('w-full'):
            with ui.row().classes('w-full items-center justify-between'):
                with ui.row().classes('items-center gap-4'):
                    ui.label(report['icon']).classes('text-3xl')
                    with ui.column():
                        ui.label(report['name']).classes('text-lg font-bold')
                        ui.label(report['description']).classes('text-sm text-gray-600')
                
                with ui.row().classes('gap-2'):
                    ui.button('查看', icon='visibility',
                             on_click=lambda r=report: show_report_preview(r))\
                        .props('flat color=primary size=sm')
                    
                    if can_export:
                        ui.button('导出', icon='download',
                                 on_click=lambda r=report: export_report(r))\
                            .props('flat color=positive size=sm')
                    else:
                        ui.button('导出', icon='download').props('flat disable size=sm')\
                            .tooltip('需要 report.export 权限')


def show_report_preview(report: Dict):
    """显示报表预览"""
    ui.notify(f'正在加载 {report["name"]}...', type='info')
    # 这里可以实现具体的报表展示逻辑


def export_report(report: Dict):
    """导出报表"""
    ui.notify(f'正在导出 {report["name"]}...', type='info')
    # 这里可以实现具体的报表导出逻辑


# ========================================
# 导出
# ========================================

__all__ = ['erp_auth_page_content']