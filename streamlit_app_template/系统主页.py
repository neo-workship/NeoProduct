import streamlit as st
import os
import sys
import numpy as np
import pandas as pd
import altair as alt

# 将项目根目录添加到 Python 路径，以便导入 utils.py 和 auth_service.py
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

# 从封装好的服务脚本中导入 AuthManager
from auth_service import AuthManager

# 导入自定义CSS应用函数
from utils import apply_custom_css

# 全局 AuthManager 实例，确保在整个应用中只初始化一次
# Streamlit 会在每次 rerun 时重新运行整个脚本，但 AuthManager 的内部状态（如数据库连接）是独立的
# 并且 Streamlit 的 session_state 会保留会话信息
auth_manager = AuthManager()

def render_auth_page():
    """渲染认证（登录、注册、修改密码）页面。"""
    st.title("🔐 用户登录")
    
    tab1, tab2, tab3 = st.tabs(["登录", "注册", "修改密码"])
    
    with tab1:
        st.subheader("用户登录")
        with st.form("login_form"):
            username = st.text_input("用户名", key="login_username")
            password = st.text_input("密码", type="password", key="login_password")
            remember_me = st.checkbox("记住我 (3天)", key="remember_me")
            submit_login = st.form_submit_button("登录", type="primary")
            
            if submit_login:
                if username and password:
                    if auth_manager.login(username, password, remember_me):
                        st.success("登录成功！")
                        st.rerun() # 登录成功后重新运行以更新页面状态
                    else:
                        st.error("用户名或密码错误！")
                else:
                    st.warning("请填写完整信息！")
    
    with tab2:
        st.subheader("用户注册")
        with st.form("register_form"):
            reg_username = st.text_input("用户名", key="reg_username")
            reg_email = st.text_input("邮箱", key="reg_email")
            reg_password = st.text_input("密码", type="password", key="reg_password")
            reg_password_confirm = st.text_input("确认密码", type="password", key="reg_password_confirm")
            submit_register = st.form_submit_button("注册", type="primary")
            
            if submit_register:
                if all([reg_username, reg_email, reg_password, reg_password_confirm]):
                    if reg_password == reg_password_confirm:
                        # 直接通过 auth_manager 访问 DatabaseManager
                        if auth_manager.db.create_user(reg_username, reg_email, reg_password):
                            st.success("注册成功！请登录。")
                            # 注册成功后不清空表单，但可以提示用户去登录
                        else:
                            st.error("用户名或邮箱已存在！")
                    else:
                        st.error("两次输入的密码不一致！")
                else:
                    st.warning("请填写完整信息！")
    
    with tab3:
        st.subheader("修改密码")
        if auth_manager.is_authenticated():
            with st.form("change_password_form_tab"): # 使用不同的form key
                current_password = st.text_input("当前密码", type="password", key="tab_current_password")
                new_password = st.text_input("新密码", type="password", key="tab_new_password")
                new_password_confirm = st.text_input("确认新密码", type="password", key="tab_new_password_confirm")
                submit_change = st.form_submit_button("修改密码", type="primary")
                
                if submit_change:
                    if all([current_password, new_password, new_password_confirm]):
                        if new_password == new_password_confirm:
                            current_user = auth_manager.get_current_user()
                            if current_user:
                                # 直接通过 auth_manager 访问 DatabaseManager
                                if auth_manager.db.update_password(current_user['username'], current_password, new_password):
                                    st.success("密码修改成功！")
                                else:
                                    st.error("当前密码错误！")
                            else:
                                st.error("无法获取当前用户信息，请重新登录。")
                        else:
                            st.error("两次输入的新密码不一致！")
                    else:
                        st.warning("请填写完整信息！")
        else:
            st.info("请先登录后再修改密码。")

def render_user_management():
    """渲染用户管理页面。只有管理员可见。"""
    st.title("👥 用户管理")
    
    if not auth_manager.is_admin():
        st.error("您没有权限访问此页面！")
        return
    
    # 获取所有用户
    users = auth_manager.db.get_all_users()
    
    st.subheader("用户列表")
    
    # 用户统计
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("总用户数", len(users))
    with col2:
        active_users = sum(1 for user in users if user[4])
        st.metric("活跃用户", active_users)
    with col3:
        admin_users = sum(1 for user in users if user[3] == 'admin')
        st.metric("管理员", admin_users)
    with col4:
        regular_users = sum(1 for user in users if user[3] == 'user')
        st.metric("普通用户", regular_users)
    
    st.divider()
    
    # 用户表格
    if users:
        # 使用 st.data_editor 或 st.dataframe 可以更简洁地显示和编辑数据
        # 但为了保留原有交互逻辑，我们继续使用循环和列布局
        for user in users:
            user_id, username, email, role, is_active, created_at, last_login = user
            
            with st.container(border=True): # 添加边框使每行用户更清晰
                col1, col2, col3, col4, col5 = st.columns([2, 2, 1, 1, 2])
                
                with col1:
                    st.write(f"**{username}**")
                    st.caption(email)
                
                with col2:
                    status_color = "🟢" if is_active else "🔴"
                    st.write(f"{status_color} {'活跃' if is_active else '禁用'}")
                    st.caption(f"创建: {created_at[:10] if created_at else 'N/A'}")
                
                with col3:
                    role_options = ["user", "admin"]
                    # 确保索引在有效范围内，避免因数据问题导致错误
                    try:
                        current_role_index = role_options.index(role)
                    except ValueError:
                        current_role_index = 0 # 默认给个 'user' 角色
                        
                    new_role = st.selectbox(
                        "角色",
                        role_options,
                        index=current_role_index,
                        key=f"role_{user_id}",
                        label_visibility="collapsed" # 隐藏标签以节省空间
                    )
                    
                    if new_role != role:
                        if st.button("更新角色", key=f"update_role_{user_id}", use_container_width=True):
                            if auth_manager.db.update_user_role(user_id, new_role):
                                st.success("角色更新成功！")
                                st.rerun()
                            else:
                                st.error("角色更新失败！")
                
                with col4:
                    toggle_text = "禁用" if is_active else "启用"
                    toggle_button_type = "secondary" if is_active else "primary"
                    if st.button(toggle_text, key=f"toggle_{user_id}", use_container_width=True, type=toggle_button_type):
                        if auth_manager.db.toggle_user_status(user_id):
                            st.success(f"用户状态已{toggle_text}！")
                            st.rerun()
                        else:
                            st.error("状态更新失败！")
                
                with col5:
                    if last_login:
                        st.caption(f"最后登录: {last_login[:16]}")
                    else:
                        st.caption("从未登录")
                
                # st.divider() # 避免重复的 divider，因为容器已经有边框了
    else:
        st.info("暂无用户数据")

def render_change_password_modal():
    """渲染修改密码模态框。"""
    st.subheader("🔑 修改密码")

    with st.form("change_password_form_modal"): # 不同的 form key
        current_password = st.text_input("当前密码", type="password", key="modal_current_password")
        new_password = st.text_input("新密码", type="password", key="modal_new_password")
        new_password_confirm = st.text_input("确认新密码", type="password", key="modal_new_password_confirm")

        col1, col2 = st.columns(2)
        with col1:
            submit_change = st.form_submit_button("修改密码", type="primary", use_container_width=True)
        with col2:
            cancel_change = st.form_submit_button("取消", use_container_width=True)

        if cancel_change:
            st.session_state.show_change_password = False
            st.rerun()

        if submit_change:
            if all([current_password, new_password, new_password_confirm]):
                if new_password == new_password_confirm:
                    current_user = auth_manager.get_current_user()
                    if current_user:
                        if auth_manager.db.update_password(current_user['username'], current_password, new_password):
                            st.success("密码修改成功！")
                            st.session_state.show_change_password = False
                            st.rerun()
                        else:
                            st.error("当前密码错误！")
                    else:
                        st.error("无法获取当前用户信息，请重新登录。")
                else:
                    st.error("两次输入的新密码不一致！")
            else:
                st.warning("请填写完整信息！")

def render_dashboard():
    """渲染仪表板页面（个人主页）。"""
    st.title("📊 个人主页")
    
    current_user = auth_manager.get_current_user()
    
    if not current_user:
        st.warning("请先登录。")
        # 强制rerun以显示登录页面，避免用户停留在未授权页面
        st.rerun() 
        return

    st.success(f"欢迎, {current_user['username']}!")
    
    # 检查是否需要显示修改密码界面
    if st.session_state.get('show_change_password', False):
        render_change_password_modal()
        st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("👤 用户基本信息")
        st.info(f"**用户名:** {current_user['username']}")
        st.info(f"**邮箱:** {current_user['email']}")
        st.info(f"**角色:** {current_user['role']}")
        st.info(f"**状态:** {'活跃' if current_user['is_active'] else '禁用'}")
    
    with col2:
        st.subheader("📊 用户使用统计")
        # 生成日期和正整数数据
        dates = pd.date_range(end=pd.Timestamp.today(), periods=12)
        data = pd.DataFrame(
            np.random.randint(1, 100, size=(12, 3)),
            columns=['查看文档数', '查看接口数', '查看字段数']
        )
        data['日期'] = dates

        # 转为长格式以便 Altair 画多个柱状系列
        data_long = data.melt(id_vars=['日期'], var_name='类型', value_name='数量')

        # 创建 Altair 图表，格式化日期为 dd/mm/yy
        chart = alt.Chart(data_long).mark_bar().encode(
            x=alt.X('yearmonthdate(日期):O', title='日期', axis=alt.Axis(format='%d/%m/%y')),
            y=alt.Y('数量:Q'),
            color='类型:N',
            tooltip=['日期:T', '类型:N', '数量:Q']
        ).properties(
            width=800,
            height=400,
            title='每日访问统计'
        )

        st.altair_chart(chart, use_container_width=True)

    st.divider()
    
    # 快速导航
    st.subheader("🚀 数据说明")
    col_image, col_text = st.columns([1, 2]) # 调整这里的比例来控制左右宽度

    # 添加第一张图片 (确保 welcome-3.svg 在你的应用目录下)
    with col_image:
        st.image("welcome-3.svg", 
                 caption="一人一档&一企一档数据系统", 
                 width=200,
                 use_container_width = False
                 )
        
    with col_text:
        st.write("""
            🛠️本平台旨在为您提供高效便捷的数字政务服务。通过“一人一档”和“一企一档”功能，
            我们致力于整合和管理个人与企业的多维度数据，实现数据共享和业务协同。

            **主要功能包括：**
            * **连接政务数据：** 安全高效地接入各类政府部门数据源。
            * **选择数据集：** 灵活筛选所需数据，构建个性化数据集。
            * **操作集合数据：** 提供丰富的数据清洗、分析、可视化工具。

            请根据您的需求，使用左侧的导航栏选择相应的操作页面。我们期待为您带来卓越的数据服务体验！
        """)

def render_sidebar():
    """渲染侧边栏导航和用户状态信息。"""
    with st.sidebar:
        if auth_manager.is_authenticated():
            current_user = auth_manager.get_current_user()
            if current_user:
                st.success(f"已登录: {current_user['username']}")
                # st.write(f"角色: **{current_user['role'].upper()}**") # 显示角色
            else:
                # 理论上is_authenticated为True时current_user不应为None，但以防万一
                auth_manager.logout()
                st.rerun() 
                return
            
            st.subheader("👤 用户操作")
            # 侧边栏导航按钮使用 st.switch_page
            if st.button("📊 个人主页", use_container_width=True):
                # 切换到主页 (当前页面，但会重置URL查询参数)
                # 或者，如果这是主页，点击后不切换页面
                if st.session_state.get('current_page') != 'dashboard':
                    st.session_state.current_page = 'dashboard'
                    st.rerun()
                
            if st.button("🔑 修改密码", key="sidebar_change_password_button", use_container_width=True):
                st.session_state.show_change_password = True
                st.rerun()

            if current_user['role'] == 'admin':
                if st.button("👥 用户管理", use_container_width=True):
                    # 如果用户管理页面是独立的.py文件
                    st.switch_page("pages/5_用户管理.py")

            # 登出按钮
            if st.button("🚪 登出系统", use_container_width=True, type="secondary"):
                auth_manager.logout()
                st.rerun() # 登出后重新运行以显示登录页面
        else:
            st.warning("请先登录")
            st.info("请在系统主页面完成登录")

def main():
    """主函数，控制应用的流程和页面渲染。"""
    # 每次运行脚本时清理过期会话
    auth_manager.db.cleanup_expired_sessions()

    # 初始化 Streamlit session_state 变量
    # 这些变量会在 Streamlit 重新运行时保持其值，除非显式修改或删除
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'show_change_password' not in st.session_state:
        st.session_state.show_change_password = False
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'dashboard' # 默认显示仪表板

    # 渲染侧边栏
    # 侧边栏的显示内容依赖于认证状态
    render_sidebar()

    # 根据认证状态渲染不同的主内容区域
    if not auth_manager.is_authenticated():
        render_auth_page()
    else:
        # 如果是多页面应用，这里可以根据 st.session_state.current_page 或其他逻辑来分发页面
        # 由于你的用户管理是单独的.py文件，这里只处理个人主页和认证页面
        render_dashboard()

if __name__ == "__main__":
    # 页面配置，只在脚本首次运行时设置
    st.set_page_config(
        page_title="用户管理系统",
        page_icon="🔐",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    apply_custom_css() # 应用自定义CSS
    main()