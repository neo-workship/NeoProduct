import streamlit as st
from pymongo import MongoClient
import time
import sys
import os

# 确保 Streamlit 应用的根目录在 Python 路径中，以便导入 '系统主页'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from utils import apply_custom_css
from 系统主页 import AuthManager, render_sidebar # 确保文件名与您的主页文件匹配

# --- 页面配置 ---
st.set_page_config(
    page_title="连接一人一档&一企一档数据",
    page_icon="🔗",
    layout="wide"
)

@st.fragment
def render_connection_form():
    """渲染连接 MongoDB 的表单和状态显示"""
    # st.title("🔗 连接档案数据库")
    st.write("请在下方输入您的<span style='color:green'>**一人一档&一企一档**</span> 连接 URI", unsafe_allow_html=True)

    uri = st.text_input(
        "政务数据 URI",
        "mongodb://localhost:27017/",
        help="例如: mongodb://localhost:27017/ 或 mongodb+srv://user:password@cluster.mongodb.net/dbname",
        key="mongo_uri_input"
    )

    connect_btn = st.button("立即连接", key="connect_mongo_button")

    if connect_btn:
        with st.spinner("正在尝试连接到数据库..."):
            time.sleep(2) # 模拟连接延迟
            try:
                # 尝试连接，设置超时
                client = MongoClient(uri, serverSelectionTimeoutMS=5000)
                client.server_info() # 测试连接是否成功
                st.success("🎉 连接成功！您现在可以访问数据库了。")

                # 保存连接到 session_state，使用更清晰的键名
                st.session_state["mongo_client"] = client
                st.session_state["mongo_uri"] = uri
                # 如果连接成功，清除之前的选择，确保状态一致
                if "db_name_selected" in st.session_state:
                    del st.session_state["db_name_selected"]
                if "collection_name_selected" in st.session_state:
                    del st.session_state["collection_name_selected"]

                st.rerun() # 成功连接后重新运行页面，以显示新的组件

            except Exception as e:
                st.error(f"❌ 连接失败: 请检查您的 URI 和网络设置。错误信息: {e}")
                st.warning("💡 提示: 如果您正在本地运行 MongoDB，请确保服务已启动且端口正确。")

    # 显示当前连接状态
    if "mongo_client" in st.session_state and st.session_state["mongo_client"] is not None:
        st.info(f"✨ 当前已连接到: `{st.session_state['mongo_uri']}`")
    elif "mongo_uri" in st.session_state:
        st.warning("💔 当前没有活动的数据库连接，请尝试重新连接。")
    else:
        st.info("⬆️ 请输入 政务数据 URI 并点击 '立即连接' 按钮。")
    st.markdown("---")

@st.fragment
def render_db_collection_selector():
    """
    渲染数据库和数据集选择界面。
    只有在 MongoDB 客户端成功连接后才会被调用。
    """
    st.title("📂 选择数据库/数据集")

    # 再次检查 MongoDB 连接，确保万无一失
    if "mongo_client" not in st.session_state or st.session_state["mongo_client"] is None:
        st.warning("⚠️ 警告：数据库连接已丢失或未建立，请返回 '连接政务数据' 页面重新连接。")
        return # 如果没有连接，直接返回，不渲染后续内容

    client = st.session_state["mongo_client"] # 使用正确的 session_state key

    # 显示当前连接的URI
    if "mongo_uri" in st.session_state:
        st.info(f"🎉 已连接到 数字政府 服务：`{st.session_state['mongo_uri']}`")

    db_list = []
    # 动态显示加载数据库列表的过程
    with st.spinner("正在加载数据库列表..."):
        time.sleep(1) # 模拟延迟
        try:
            db_list = client.list_database_names()
            if not db_list:
                st.warning("🧐 未找到任何数据库。请确保您的 数字政府 服务中有数据。")
                db_list = ["<无可用数据库>"]
        except Exception as e:
            st.error(f"❌ 获取数据库列表失败：{e}")
            st.stop() # 获取失败则停止后续操作

    # 添加一个初始的空选项，提示用户选择
    db_options = ["--- 请选择数据库 ---"] + db_list

    # 从 session_state 中获取上次选择的数据库，用于保持状态
    # 使用唯一的 key 防止与其他 selectbox 冲突
    db_name_selected = st.session_state.get("db_name_selected", db_options[0])
    db_index = db_options.index(db_name_selected) if db_name_selected in db_options else 0

    db_name = st.selectbox(
        "选择数据库",
        db_options,
        index=db_index, # 默认选中上次选择的或第一个提示项
        key="db_selector" # 唯一的 key
    )

    # 保存当前选择的数据库到 session_state
    if db_name and db_name != "--- 请选择数据库 ---" and db_name != "<无可用数据库>":
        st.session_state["db_name_selected"] = db_name
    elif "db_name_selected" in st.session_state: # 如果用户选择了提示项，清除之前的选择
        del st.session_state["db_name_selected"]
        if "collection_name_selected" in st.session_state:
            del st.session_state["collection_name_selected"]
        st.rerun() # 重新运行以清除集合选择

    # 只有当用户选择了有效的数据库名时才继续加载集合
    if "db_name_selected" in st.session_state:
        db = client[st.session_state["db_name_selected"]]
        collection_list = []
        # 动态显示加载集合列表的过程
        with st.spinner(f"正在加载 {st.session_state['db_name_selected']} 数据库中的集合..."):
            time.sleep(1) # 模拟延迟
            try:
                collection_list = db.list_collection_names()
                if not collection_list:
                    st.warning(f"🧐 数据库 '{st.session_state['db_name_selected']}' 中未找到任何集合。")
                    collection_list = ["<无可用集合>"]
            except Exception as e:
                st.error(f"❌ 获取集合列表失败：{e}")
                st.stop()

        col_options = ["--- 请选择集合 ---"] + collection_list

        # 从 session_state 获取上次选择的集合
        collection_name_selected = st.session_state.get("collection_name_selected", col_options[0])
        col_index = col_options.index(collection_name_selected) if collection_name_selected in col_options else 0

        collection_name = st.selectbox(
            "选择集合",
            col_options,
            index=col_index, # 默认选中上次选择的或第一个提示项
            key="collection_selector" # 唯一的 key
        )

        # 保存当前选择的集合到 session_state
        if collection_name and collection_name != "--- 请选择集合 ---" and collection_name != "<无可用集合>":
            if collection_name != st.session_state.get("collection_name_selected"): # 仅当选择有变化时更新
                st.session_state["collection_name_selected"] = collection_name
                st.success(f"✅ 成功选择：数据库 **{st.session_state['db_name_selected']}** 中的集合 **{collection_name}**")
                st.info("💡 您现在可以进行数据操作了！")
                # 可以在这里添加跳转到下一个操作页面的逻辑
        elif collection_name == "--- 请选择集合 ---":
            if "collection_name_selected" in st.session_state: # 如果用户选择了提示项，清除之前的选择
                del st.session_state["collection_name_selected"]
            st.info("⬆️ 请从下拉菜单中选择一个集合。")
        elif collection_name == "<无可用集合>":
            st.warning("⚠️ 数据库中没有可用集合，请重新选择数据库或检查数据。")
    else:
        st.info("⬆️ 请从下拉菜单中选择一个数据库。")
    st.markdown("---")

# --- 主函数：控制页面渲染逻辑 ---
def main():
    """页面主函数：控制访问权限和渲染内容"""
    auth_manager = AuthManager()
    st.title("🔗 连接档案数据库")
    # 渲染侧边栏
    render_sidebar()

    # 检查认证状态
    if not auth_manager.is_authenticated():
        st.error("请先登录才能访问此页面！")
        if st.button("🏠 返回主页", type="primary", key="back_to_main_login"):
            st.switch_page("系统主页.py")
    else:
        # 登录成功后，应用自定义 CSS
        apply_custom_css()
        # 渲染连接 MongoDB 的表单
        render_connection_form()
        # 只有在 mongo_client 存在且不为 None 时才渲染数据库和集合选择器
        if "mongo_client" in st.session_state and st.session_state["mongo_client"] is not None:
            st.markdown("##") # 添加一些空间
            render_db_collection_selector()
        else:
            st.info("⬆️ 请先成功连接 MongoDB 数据库，才能选择数据库和数据集。")

if __name__ == "__main__":
    main()