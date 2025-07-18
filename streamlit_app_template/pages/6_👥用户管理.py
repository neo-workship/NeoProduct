import streamlit as st
import sys
import os

# 添加父目录到路径，以便导入main.py中的类
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from utils import apply_custom_css
from 系统主页 import AuthManager, render_user_management, render_sidebar

# 页面配置
st.set_page_config(
    page_title="用户管理",
    page_icon="👥",
    layout="wide"
)

def main():
    """用户管理页面主函数"""
    auth_manager = AuthManager()
    
    # 渲染侧边栏
    render_sidebar()
    
    # 检查认证状态和权限
    if not auth_manager.is_authenticated():
        st.error("请先登录！")
        if st.button("🏠 返回主页"):
            st.switch_page("系统主页.py")
    elif not auth_manager.is_admin():
        st.error("您没有权限访问此页面！")
        if st.button("📊 返回仪表板"):
            st.switch_page("系统主页.py")
    else:
        # 渲染用户管理页面
        render_user_management()

if __name__ == "__main__":
    apply_custom_css()
    main()