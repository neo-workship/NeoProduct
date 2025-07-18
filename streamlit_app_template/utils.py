# utils.py
import streamlit as st
import os

def apply_custom_css():
    """
    读取 style.css 文件并将其作为自定义 CSS 注入到 Streamlit 页面。
    假定 style.css 位于与此脚本相同的目录下。
    """
    # 构建 style.css 文件的绝对路径
    # os.path.dirname(__file__) 获取当前文件 (utils.py) 的目录
    css_file_path = os.path.join(os.path.dirname(__file__), "style.css")

    if not os.path.exists(css_file_path):
        st.error(f"错误：找不到 CSS 文件 '{css_file_path}'。请确保 style.css 文件存在于 '{os.path.dirname(__file__)}' 目录下。")
        return

    with open(css_file_path, "r", encoding="utf-8") as f:
        # 使用 st.markdown 注入 CSS。unsafe_allow_html=True 是必须的。
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# 您可以在这里添加其他公共函数，例如数据库连接、认证管理等