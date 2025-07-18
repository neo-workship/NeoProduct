import streamlit as st
import sys
import os

# 添加父目录到路径，以便导入main.py中的类
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from utils import apply_custom_css
from 系统主页 import AuthManager, render_sidebar

# 页面配置
st.set_page_config(
    page_title="数据看板",
    page_icon="📈",
    layout="wide"
)

def render_sample_content():
    """渲染示例页面内容"""
    # st.title("📈 数据汇聚看板")
    
    auth_manager = AuthManager()
    current_user = auth_manager.get_current_user()
    
    st.success(f"欢迎访问数据看板, {current_user['username']}!")
    
    st.subheader("📊 数据汇聚情况")
    # 示例图表
    import pandas as pd
    import numpy as np
    import altair as alt

    # 设置随机种子，确保每次生成一致
    np.random.seed(42)

    # 生成日期
    dates = pd.date_range(end=pd.Timestamp.today(), periods=20)
    df = pd.DataFrame({
        '日期': dates,
        '数据总量(GB)': np.random.randint(3, 21, size=20),
        '集成API数(个)': np.random.randint(3, 21, size=20),
        '对接数据集数(个)': np.random.randint(3, 21, size=20),
        '企业档案数(份)': np.random.randint(3, 21, size=20)
    })
    # 日期选择滑块
    start_date, end_date = st.slider(
        "选择时间区间",
        min_value=dates.min().date(),
        max_value=dates.max().date(),
        value=(dates.min().date(), dates.max().date()),
        format="YYYY-MM-DD"
    )

    # 根据选择的日期过滤数据
    mask = (df['日期'].dt.date >= start_date) & (df['日期'].dt.date <= end_date)
    filtered_df = df[mask].copy()

    # 转换为长格式
    df_long = filtered_df.melt(id_vars='日期', var_name='类型', value_name='数量')

    # 绘制折线图
    chart = alt.Chart(df_long).mark_line(point=True).encode(
        x=alt.X('日期:T', axis=alt.Axis(format='%Y-%m-%d'), title='日期'),
        y=alt.Y('数量:Q', title='数量（3~20）'),
        color='类型:N',
        tooltip=['日期:T', '类型:N', '数量:Q']
    ).properties(
        width=800,
        height=400,
        title='动态数据趋势图'
    )

    st.altair_chart(chart, use_container_width=True)

def main():
    """示例页面主函数"""
    auth_manager = AuthManager()
    st.title("📈 数据汇聚看板")
    # 渲染侧边栏
    render_sidebar()
    # 检查认证状态
    if not auth_manager.is_authenticated():
        st.error("请先登录才能访问此页面！")
        if st.button("🏠 返回主页",type="primary"):
            st.switch_page("系统主页.py")
    else:
        # 渲染示例页面内容
        render_sample_content()

if __name__ == "__main__":
    apply_custom_css()
    main()