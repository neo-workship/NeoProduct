# 1. OpenAI模型与用户表的关联关系详解

"""
数据库表关系图：

users 表                    openai_configs 表                openai_requests 表
┌──────────────┐           ┌─────────────────┐              ┌─────────────────┐
│ id (PK)      │           │ id (PK)         │              │ id (PK)         │
│ username     │           │ name            │              │ config_id (FK)  │
│ email        │◄──────────┤ created_by (FK) │              │ user_id (FK)    │◄────┐
│ password_hash│           │ updated_by (FK) │              │ prompt          │     │
│ ...          │           │ api_key         │◄─────────────┤ response        │     │
└──────────────┘           │ model_name      │              │ tokens_used     │     │
       ▲                   │ ...             │              │ ...             │     │
       │                   └─────────────────┘              └─────────────────┘     │
       └─────────────────────────────────────────────────────────────────────────────┘

关联关系说明：
1. openai_configs.created_by → users.id (创建者)
2. openai_configs.updated_by → users.id (最后更新者)  
3. openai_requests.user_id → users.id (请求发起者)
4. openai_requests.config_id → openai_configs.id (使用的配置)

"""

# 具体的关联实现：

# 1.1 BusinessBaseModel中的审计字段（继承自AuditMixin）
class AuditMixin:
    created_by = Column(Integer, ForeignKey('users.id'), nullable=True)  # 创建者
    updated_by = Column(Integer, ForeignKey('users.id'), nullable=True)  # 更新者

# 1.2 OpenAIConfig继承BusinessBaseModel，自动获得审计字段
class OpenAIConfig(BusinessBaseModel):  # 继承后自动有created_by、updated_by
    __tablename__ = 'openai_configs'
    
    name = Column(String(100), nullable=False)
    api_key = Column(String(255), nullable=False)
    # ... 其他字段
    
    # 继承的字段（来自BusinessBaseModel -> AuditMixin）：
    # created_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    # updated_by = Column(Integer, ForeignKey('users.id'), nullable=True)

# 1.3 OpenAIRequest有直接的用户关联 + 继承的审计字段
class OpenAIRequest(BusinessBaseModel):
    __tablename__ = 'openai_requests'
    
    config_id = Column(Integer, ForeignKey('openai_configs.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)  # 直接关联用户
    
    prompt = Column(Text, nullable=False)
    response = Column(Text)
    # ... 其他字段
    
    # 同时也继承审计字段：
    # created_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    # updated_by = Column(Integer, ForeignKey('users.id'), nullable=True)

# 1.4 实际使用示例
def create_openai_config_example():
    """创建OpenAI配置的示例"""
    from auth import auth_manager
    from database_models.business_models.openai_models import OpenAIConfig
    from auth.database import get_db
    
    # 获取当前用户
    current_user = auth_manager.current_user
    
    with get_db() as db:
        # 创建配置
        config = OpenAIConfig(
            name="我的DeepSeek配置",
            api_key="sk-xxxxxxxxxxxx",
            base_url="https://api.deepseek.com/v1",
            # 设置审计字段
            created_by=current_user.id,    # 记录是谁创建的
            updated_by=current_user.id     # 记录是谁更新的
        )
        
        db.add(config)
        db.commit()
        
        print(f"配置创建成功，创建者: {current_user.username}")

def create_openai_request_example():
    """创建OpenAI请求的示例"""
    from auth import auth_manager
    from database_models.business_models.openai_models import OpenAIRequest
    from auth.database import get_db
    
    current_user = auth_manager.current_user
    
    with get_db() as db:
        # 创建请求记录
        request = OpenAIRequest(
            config_id=1,  # 使用哪个配置
            user_id=current_user.id,      # 直接关联：谁发起的请求
            prompt="你好，请介绍一下自己",
            response="我是DeepSeek...",
            tokens_used=150,
            # 审计字段
            created_by=current_user.id,   # 记录创建者
            updated_by=current_user.id    # 记录更新者
        )
        
        db.add(request)
        db.commit()
        
        print(f"请求记录创建成功")
        print(f"请求用户: {current_user.username}")
        print(f"记录创建者: {current_user.username}")

# 1.5 查询关联数据的示例
def query_user_data_example():
    """查询用户相关数据的示例"""
    from auth.database import get_db
    from auth.models import User
    from database_models.business_models.openai_models import OpenAIConfig, OpenAIRequest
    
    with get_db() as db:
        # 查询用户创建的所有配置
        user = db.query(User).filter(User.username == 'admin').first()
        
        # 方式1：通过外键查询
        user_configs = db.query(OpenAIConfig).filter(
            OpenAIConfig.created_by == user.id
        ).all()
        
        # 方式2：通过辅助方法查询
        for config in user_configs:
            creator_info = config.get_creator_info()  # 使用shared_base.py中的方法
            print(f"配置: {config.name}, 创建者: {creator_info['username']}")
        
        # 查询用户的所有请求
        user_requests = db.query(OpenAIRequest).filter(
            OpenAIRequest.user_id == user.id
        ).all()
        
        print(f"用户 {user.username} 创建了 {len(user_configs)} 个配置")
        print(f"用户 {user.username} 发起了 {len(user_requests)} 个请求")

# --------------------------------------------------------------------

# 2. get_creator_info方法的作用和使用详解

"""
get_creator_info 的设计思路：

问题：在显示业务数据时，经常需要显示"是谁创建的"、"是谁更新的"
传统方案：定义relationship关系，但这会导致模块间强耦合
解耦方案：使用方法动态获取用户信息，避免静态关系定义
"""

# 2.1 get_creator_info方法的实现（在shared_base.py中）
class AuditMixin:
    created_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    updated_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    
    def get_creator_info(self):
        """获取创建者信息的辅助方法 - 动态获取，避免静态关系"""
        if not self.created_by:
            return None
            
        # 动态导入避免循环依赖
        try:
            from auth.database import get_db
            from auth.models import User
            
            with get_db() as db:
                creator = db.query(User).filter(User.id == self.created_by).first()
                if creator:
                    return {
                        'id': creator.id,
                        'username': creator.username,
                        'full_name': creator.full_name
                    }
        except Exception:
            pass
        return None
    
    def get_updater_info(self):
        """获取更新者信息的辅助方法"""
        # 实现类似...

# 2.2 created_by字段的赋值 - 需要手动设置
def manual_assignment_example():
    """手动赋值示例 - 在业务逻辑中设置"""
    from auth import auth_manager
    from database_models.business_models.openai_models import OpenAIConfig
    from auth.database import get_db
    
    current_user = auth_manager.current_user  # 获取当前登录用户
    
    with get_db() as db:
        # 创建新配置时 - 手动设置审计字段
        config = OpenAIConfig(
            name="新配置",
            api_key="sk-xxx",
            # 👇 手动设置审计字段
            created_by=current_user.id,   # 谁创建的
            updated_by=current_user.id    # 谁更新的（初始时与创建者相同）
        )
        
        db.add(config)
        db.commit()

def update_assignment_example():
    """更新时的赋值示例"""
    from auth import auth_manager
    from database_models.business_models.openai_models import OpenAIConfig
    from auth.database import get_db
    
    current_user = auth_manager.current_user
    
    with get_db() as db:
        # 查找要更新的配置
        config = db.query(OpenAIConfig).filter(OpenAIConfig.id == 1).first()
        
        if config:
            # 更新配置内容
            config.name = "更新后的配置名称"
            config.api_key = "新的API密钥"
            
            # 👇 手动设置更新者
            config.updated_by = current_user.id  # 记录是谁更新的
            
            # created_by 不变，只更新 updated_by
            db.commit()

# 2.3 使用get_creator_info获取用户信息 - 在UI中显示
def display_config_with_creator():
    """在UI中显示配置及其创建者信息"""
    from nicegui import ui
    from database_models.business_models.openai_models import OpenAIConfig
    from auth.database import get_db
    
    with get_db() as db:
        configs = db.query(OpenAIConfig).all()
        
        for config in configs:
            with ui.card():
                ui.label(f'配置名称: {config.name}')
                ui.label(f'模型: {config.model_name.value}')
                
                # 👇 使用get_creator_info方法获取创建者信息
                creator_info = config.get_creator_info()
                if creator_info:
                    ui.label(f'创建者: {creator_info["username"]} ({creator_info["full_name"]})')
                    ui.label(f'创建时间: {config.created_at}')
                else:
                    ui.label('创建者: 未知')
                
                # 获取更新者信息
                updater_info = config.get_updater_info()
                if updater_info:
                    ui.label(f'最后更新: {updater_info["username"]} 于 {config.updated_at}')

# 2.4 使用辅助工具类自动设置审计字段
def using_audit_helper():
    """使用business_utils.py中的辅助工具"""
    from auth import auth_manager
    from database_models.business_models.openai_models import OpenAIConfig
    from database_models.business_utils import AuditHelper
    from auth.database import get_db
    
    current_user = auth_manager.current_user
    
    with get_db() as db:
        # 创建配置
        config = OpenAIConfig(
            name="使用辅助工具的配置",
            api_key="sk-xxx"
        )
        
        # 👇 使用辅助工具自动设置审计字段
        AuditHelper.set_audit_fields(config, current_user.id, is_update=False)
        
        db.add(config)
        db.commit()
        
        # 后来更新时
        config.name = "更新后的名称"
        AuditHelper.set_audit_fields(config, current_user.id, is_update=True)
        db.commit()

# 2.5 在页面中使用装饰器自动包含用户信息
def using_decorators():
    """使用装饰器自动添加用户信息"""
    from database_models.business_utils import with_user_info, with_audit_info
    
    class OpenAIConfig(BusinessBaseModel):
        # ... 字段定义
        
        @with_user_info  # 装饰器会自动添加user_info
        @with_audit_info # 装饰器会自动添加audit_info
        def to_dict_extended(self):
            """扩展的字典转换"""
            return self.to_dict()
    
    # 使用示例
    config = OpenAIConfig.query.first()
    data = config.to_dict_extended()
    # data 现在包含：
    # {
    #   'id': 1,
    #   'name': '配置名称',
    #   'user_info': {'username': 'admin', 'full_name': '管理员'},
    #   'audit_info': {
    #       'creator': {'username': 'admin', 'full_name': '管理员'},
    #       'created_at': '2025-01-01 10:00:00'
    #   }
    # }

# 总结：get_creator_info的使用流程
"""
1. 字段赋值（手动）：
   - 创建记录时：created_by = current_user.id
   - 更新记录时：updated_by = current_user.id

2. 信息获取（自动）：
   - 调用 obj.get_creator_info() 获取创建者信息
   - 调用 obj.get_updater_info() 获取更新者信息

3. 辅助工具（半自动）：
   - 使用 AuditHelper.set_audit_fields() 设置字段
   - 使用装饰器自动包含用户信息

核心理念：解耦设计 - 业务模型不强依赖auth模型，通过方法动态获取
"""

# -------------------------------------------------------------------

# 3. business_utils.py的作用和使用场景详解

"""
business_utils.py 的设计目的：

问题1：多个业务模型都需要类似的用户信息获取功能 -> 代码重复
问题2：业务模型直接依赖auth模块 -> 强耦合
问题3：审计字段设置、查询操作重复 -> 维护困难

解决方案：提供统一的工具类，封装常用操作，实现松耦合
"""

# 3.1 UserInfoHelper - 统一用户信息获取
class UserInfoHelper:
    """解决问题：避免每个业务模型都写相同的用户查询代码"""
    
    @staticmethod
    def get_user_info(user_id: int) -> Optional[Dict[str, Any]]:
        """获取用户基本信息 - 统一接口"""
        if not user_id:
            return None
            
        try:
            from auth.database import get_db
            from auth.models import User
            
            with get_db() as db:
                user = db.query(User).filter(User.id == user_id).first()
                if user:
                    return {
                        'id': user.id,
                        'username': user.username,
                        'full_name': user.full_name,
                        'email': user.email,
                        'is_active': user.is_active
                    }
        except Exception:
            pass
        return None

# 使用场景1：在任何业务模型中获取用户信息
def usage_example_1():
    """OpenAI模型中使用"""
    from database_models.business_utils import UserInfoHelper
    
    class OpenAIConfig(BusinessBaseModel):
        # ... 字段定义
        
        def get_creator_name(self):
            """获取创建者名称 - 使用统一工具"""
            user_info = UserInfoHelper.get_user_info(self.created_by)
            return user_info['username'] if user_info else '未知'
        
        def get_full_creator_info(self):
            """获取完整创建者信息"""
            return UserInfoHelper.get_user_info(self.created_by)

# 使用场景2：MongoDB模型中复用
def usage_example_2():
    """MongoDB模型中也可以使用相同工具"""
    from database_models.business_utils import UserInfoHelper
    
    class MongoDBConnection(BusinessBaseModel):
        # ... 字段定义
        
        def get_owner_info(self):
            """获取连接所有者信息 - 复用相同工具"""
            return UserInfoHelper.get_user_info(self.created_by)

# 3.2 AuditHelper - 统一审计字段管理
class AuditHelper:
    """解决问题：统一审计字段的设置和获取逻辑"""
    
    @staticmethod
    def set_audit_fields(obj, user_id: int, is_update: bool = False):
        """统一设置审计字段"""
        if hasattr(obj, 'created_by') and not is_update:
            obj.created_by = user_id
        if hasattr(obj, 'updated_by'):
            obj.updated_by = user_id

# 使用场景3：在业务逻辑中自动设置审计字段
def usage_example_3():
    """在页面处理函数中使用"""
    from auth import auth_manager
    from database_models.business_utils import AuditHelper
    from database_models.business_models.openai_models import OpenAIConfig
    from auth.database import get_db
    
    def create_openai_config(name: str, api_key: str):
        """创建OpenAI配置 - 自动设置审计字段"""
        current_user = auth_manager.current_user
        
        with get_db() as db:
            config = OpenAIConfig(
                name=name,
                api_key=api_key
            )
            
            # 👇 使用工具类自动设置审计字段，无需手动设置
            AuditHelper.set_audit_fields(config, current_user.id)
            
            db.add(config)
            db.commit()
            return config
    
    def update_openai_config(config_id: int, name: str):
        """更新OpenAI配置 - 自动更新审计字段"""
        current_user = auth_manager.current_user
        
        with get_db() as db:
            config = db.query(OpenAIConfig).filter(OpenAIConfig.id == config_id).first()
            if config:
                config.name = name
                
                # 👇 自动设置更新者
                AuditHelper.set_audit_fields(config, current_user.id, is_update=True)
                
                db.commit()
            return config

# 3.3 BusinessQueryHelper - 统一业务查询
class BusinessQueryHelper:
    """解决问题：常见的业务查询操作重复编写"""
    
    @staticmethod
    def get_user_business_records(user_id: int, model_class, **filters):
        """获取用户的业务记录 - 通用查询方法"""
        try:
            with BusinessQueryHelper.get_business_db() as db:
                query = db.query(model_class).filter(model_class.created_by == user_id)
                
                # 应用额外过滤条件
                for field, value in filters.items():
                    if hasattr(model_class, field):
                        query = query.filter(getattr(model_class, field) == value)
                
                return query.all()
        except Exception:
            return []

# 使用场景4：统一查询用户的各种业务记录
def usage_example_4():
    """在页面中查询用户的所有相关记录"""
    from auth import auth_manager
    from database_models.business_utils import BusinessQueryHelper
    from database_models.business_models.openai_models import OpenAIConfig, OpenAIRequest
    
    def show_user_dashboard():
        """用户仪表板 - 显示用户的所有业务数据"""
        current_user = auth_manager.current_user
        
        # 👇 使用统一查询工具获取用户的各种记录
        
        # 查询用户创建的OpenAI配置
        user_configs = BusinessQueryHelper.get_user_business_records(
            current_user.id, 
            OpenAIConfig,
            is_active=True  # 额外条件：只查活跃的配置
        )
        
        # 查询用户的OpenAI请求记录
        user_requests = BusinessQueryHelper.get_user_business_records(
            current_user.id,
            OpenAIRequest,
            status='success'  # 额外条件：只查成功的请求
        )
        
        print(f"用户 {current_user.username}:")
        print(f"- 创建了 {len(user_configs)} 个配置")
        print(f"- 发起了 {len(user_requests)} 个成功请求")

# 3.4 装饰器 - 自动化常用操作
def with_user_info(func):
    """装饰器：自动添加用户信息"""
    def wrapper(self, *args, **kwargs):
        result = func(self, *args, **kwargs)
        if isinstance(result, dict) and hasattr(self, 'created_by'):
            from database_models.business_utils import UserInfoHelper
            result['user_info'] = UserInfoHelper.get_user_info(self.created_by)
        return result
    return wrapper

# 使用场景5：在模型方法中使用装饰器
def usage_example_5():
    """使用装饰器自动添加用户信息"""
    from database_models.business_utils import with_user_info, with_audit_info
    
    class OpenAIConfig(BusinessBaseModel):
        # ... 字段定义
        
        @with_user_info
        def to_display_dict(self):
            """转换为显示字典 - 自动包含用户信息"""
            return {
                'id': self.id,
                'name': self.name,
                'model_name': self.model_name.value,
                'is_public': self.is_public
            }
            # 装饰器会自动添加 'user_info' 字段
        
        @with_audit_info  
        def get_audit_summary(self):
            """获取审计摘要 - 自动包含审计信息"""
            return {
                'config_name': self.name,
                'total_requests': self.total_requests
            }
            # 装饰器会自动添加 'audit_info' 字段

# 使用场景6：在页面中使用装饰器处理的数据
def usage_example_6():
    """在UI中使用包含用户信息的数据"""
    from nicegui import ui
    from database_models.business_models.openai_models import OpenAIConfig
    from auth.database import get_db
    
    def show_config_list():
        """显示配置列表 - 自动显示用户信息"""
        with get_db() as db:
            configs = db.query(OpenAIConfig).all()
            
            for config in configs:
                # 👇 使用装饰器处理的方法，自动包含用户信息
                display_data = config.to_display_dict()
                audit_data = config.get_audit_summary()
                
                with ui.card():
                    ui.label(f"配置: {display_data['name']}")
                    ui.label(f"模型: {display_data['model_name']}")
                    
                    # 自动包含的用户信息
                    if display_data.get('user_info'):
                        user_info = display_data['user_info']
                        ui.label(f"创建者: {user_info['username']}")
                    
                    # 自动包含的审计信息
                    if audit_data.get('audit_info'):
                        audit_info = audit_data['audit_info']
                        if audit_info.get('creator'):
                            ui.label(f"创建时间: {audit_info['created_at']}")

# 总结：business_utils.py的价值
"""
1. 代码复用：避免在每个业务模型中重复写用户信息获取代码
2. 松耦合设计：业务模型不直接依赖auth模块，通过工具类解耦
3. 统一接口：所有业务模型使用相同的方式获取用户信息和设置审计字段
4. 易于维护：用户信息格式变化时，只需修改工具类
5. 自动化操作：通过装饰器和辅助方法减少手动操作
6. 扩展性：新增业务模型可以直接复用这些工具

核心思想：将通用的跨模块操作抽象成工具类，实现"一次编写，到处使用"
"""

# 实际项目中的完整使用流程示例
def complete_workflow_example():
    """完整的业务流程示例"""
    from auth import auth_manager
    from database_models.business_utils import AuditHelper, UserInfoHelper
    from database_models.business_models.openai_models import OpenAIConfig
    from auth.database import get_db
    from nicegui import ui
    
    def create_and_display_config():
        """创建并显示配置的完整流程"""
        current_user = auth_manager.current_user
        
        # 1. 创建配置（使用工具类设置审计字段）
        with get_db() as db:
            config = OpenAIConfig(
                name="完整流程示例",
                api_key="sk-example"
            )
            AuditHelper.set_audit_fields(config, current_user.id)  # 自动设置
            db.add(config)
            db.commit()
        
        # 2. 显示配置（使用工具类获取用户信息）
        creator_info = UserInfoHelper.get_user_info(config.created_by)
        
        with ui.card():
            ui.label(f"配置名: {config.name}")
            ui.label(f"创建者: {creator_info['username'] if creator_info else '未知'}")
            ui.label(f"创建时间: {config.created_at}")
        
        # 3. 更新配置（使用工具类更新审计字段）
        with get_db() as db:
            config.name = "更新后的名称"
            AuditHelper.set_audit_fields(config, current_user.id, is_update=True)
            db.commit()
        
        ui.notify("配置创建并更新完成！")