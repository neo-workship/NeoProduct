import streamlit as st
import sys
import os
import pandas as pd  # Needed for displaying Excel data or creating dataframes
import io            # Needed for handling uploaded file bytes
import time
from bson.objectid import ObjectId

# Ensure the Streamlit app's root directory is in the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'generatearchives'))
from generate import archive_json

from utils import apply_custom_css
from 系统主页 import AuthManager, render_sidebar # Assuming AuthManager and render_sidebar are defined here
# --- Page Configuration ---
st.set_page_config(page_title="企业档案管理", page_icon="🏢", layout="wide")

# @st.cache_resource
def _check_and_connect_mongo():
    """
    Checks for existing MongoDB connection and collection selection in session state.
    """
    # Use more explicit session_state keys for MongoDB connection details
    if ("mongo_client" not in st.session_state or st.session_state["mongo_client"] is None or
        "db_name_selected" not in st.session_state or st.session_state["db_name_selected"] is None or
        "collection_name_selected" not in st.session_state or st.session_state["collection_name_selected"] is None):

        with st.spinner("正在检查数据库连接和集合选择状态..."):
            time.sleep(1.5) # Simulate check delay
            st.warning("⚠️ 警告：请先在左侧导航栏中完成 **'连接企业档案'** 步骤。")
        return None # Return None if pre-requisites are not met

    # Retrieve connection details from session state
    client = st.session_state["mongo_client"]
    db_name = st.session_state["db_name_selected"]
    collection_name = st.session_state["collection_name_selected"]

    # Attempt to connect to the collection and show dynamic feedback
    collection = None
    with st.spinner(f"🚀 正在连接到数据库 **{db_name}** 的集合 **{collection_name}**..."):
        time.sleep(1) # Simulate connection delay
        try:
            db = client[db_name]
            collection = db[collection_name]
            # Perform a simple query to confirm the connection is valid
            collection.find_one({})
            # st.success(f"✨ 成功连接到：数据库 **{db_name}** 中的集合 **{collection_name},可进行数据抽取和生成档案数据**")
            return collection
        except Exception as e:
            st.error(f"❌ 连接到集合 **{collection_name}** 失败：{e}")
            st.warning("请检查数据库和集合是否存在，或返回上一个页面重新选择。")
            return None # Return None if connection fails
        
def _insert_archive_to_mongodb(collection, archive_data):
    """
    Insert archive data to MongoDB collection.
    
    Args:
        collection: MongoDB collection object
        archive_data: JSON data to be inserted
    
    Returns:
        bool: True if insertion successful, False otherwise
    """
    try:
        with st.spinner("正在将企业档案数据写入数据库..."):
            time.sleep(1)  # Simulate processing delay
            result = collection.insert_one(archive_data)
            if result.inserted_id:
                st.success(f"✅ 企业档案已成功写入数据库！文档ID: {result.inserted_id}")
                return True
            else:
                st.error("❌ 数据写入失败，未获得有效的文档ID")
                return False
    except Exception as e:
        st.error(f"❌ 写入数据库时发生错误：{str(e)}")
        return False
        
# --- Function to render the "Register/Create Enterprise Archives" section ---
@st.fragment
def _render_register_archive_section():
    """
    Renders the section for registering/creating enterprise archives.
    Includes options for manual creation or template-based creation.
    """
    # st.title("📝 登记/创建企业档案")
    # Use a form to better control the input clearing
    with st.form("enterprise_creation_form", clear_on_submit=True):
        enterprise_name = st.text_input("企业名称", key="form_enterprise_name")
        social_credit_code = st.text_input("统一社会信用代码", key="form_social_credit_code")
        submitted = st.form_submit_button("创建",type="primary")
    
    if submitted:
        if enterprise_name and social_credit_code:
            # Get MongoDB collection from session state
            collection = None
            if ("mongo_client" in st.session_state and 
                "db_name_selected" in st.session_state and 
                "collection_name_selected" in st.session_state): 
                client = st.session_state["mongo_client"]
                db_name = st.session_state["db_name_selected"]
                collection_name = st.session_state["collection_name_selected"]
                db = client[db_name]
                collection = db[collection_name]
            
            if collection is not None:
                try:
                    # Show progress for generating archive data
                    with st.spinner("正在生成企业档案数据..."):
                        time.sleep(1)  # Simulate processing delay
                        # Call archive_json function from generatearchives.generate module
                        archive_data = archive_json(social_credit_code, enterprise_name)     
                    # Check if archive_data is valid
                    if archive_data is None:
                        st.error("❌ 生成企业档案数据失败：archive_json 函数返回了空值")
                        st.warning("请检查 generatearchives.generate 模块中的文件路径和配置。")
                        return
                    
                    if not isinstance(archive_data, dict):
                        st.error(f"❌ 生成的数据格式错误：期望字典类型，实际得到 {type(archive_data)}")
                        st.warning("请检查 archive_json 函数的返回值格式。")
                        return
                    
                    # Check if the returned data contains error information
                    if archive_data.get("error", False):
                        st.error(f"❌ 生成企业档案时发生错误：{archive_data.get('error_message', '未知错误')}")
                        st.warning(f"错误类型：{archive_data.get('error_type', '未知')}")
                        
                        # 如果是文件未找到错误，显示路径信息
                        if archive_data.get('error_type') == 'FileNotFoundError':
                            st.info("📂 文件路径信息：")
                            st.write(f"• 尝试的文件路径: `{archive_data.get('file_path_attempted', 'N/A')}`")
                            st.write(f"• 脚本所在目录: `{archive_data.get('script_directory', 'N/A')}`")
                            st.write(f"• 当前工作目录: `{archive_data.get('working_directory', 'N/A')}`")
                            st.warning("请确保 '一企一档数据项.xlsx' 文件位于脚本目录或当前工作目录中。")  
                        with st.expander("🔍 查看详细错误信息"):
                            st.json(archive_data)
                        return
                    
                    # 设置 social_credit_code 作为文档的 _id
                    archive_data["_id"] = social_credit_code
                    
                    st.success(f"🎉 已生成企业档案数据：\n- 企业名称: **{enterprise_name}**\n- 统一社会信用代码: **{social_credit_code}**")
                   
                    # Insert data to MongoDB
                    if _insert_archive_to_mongodb(collection, archive_data):
                        # st.balloons()  # Celebrate successful creation
                        st.success("✨ 企业档案创建完成！表单已自动清空，可以继续创建下一个企业档案。")
                        
                except Exception as e:
                    st.error(f"❌ 生成企业档案时发生错误：{str(e)}")
                    st.warning("请检查 generatearchives.generate 模块是否正确配置。")
                    # 显示详细错误信息用于调试
                    with st.expander("🔍 查看详细错误信息"):
                        import traceback
                        st.code(traceback.format_exc())
            else:
                st.error("❌ 数据库连接不可用，无法创建企业档案")
                st.warning("请确保已正确连接到 MongoDB 数据库和集合。")
        else:
            st.warning("⚠️ 请填写企业名称和统一社会信用代码。")
#region

# --- Function to render the "Extract/Generate Enterprise Archives" section ---
@st.fragment
def _render_extract_archive_section():
    st.title("🛠️ 抽取/生成档案数据")
    # Get MongoDB collection
    collection = _check_and_connect_mongo()
    if collection is None:
        st.error("无法连接到 MongoDB，请检查连接配置。")
        return

    # Initialize session states for dropdowns if not present
    if "extract_zero_level_display" not in st.session_state: st.session_state.extract_zero_level_display = None
    if "extract_level1" not in st.session_state: st.session_state.extract_level1 = None
    if "extract_level2" not in st.session_state: st.session_state.extract_level2 = None
    if "extract_level3" not in st.session_state: st.session_state.extract_level3 = None
    if "extract_field" not in st.session_state: st.session_state.extract_field = None
    if "current_data_url" not in st.session_state: st.session_state.current_data_url = ""
    if "docs_summary_cache" not in st.session_state: st.session_state.docs_summary_cache = []

    # Function to load documents from MongoDB
    def load_documents_summary():
        """加载文档摘要数据"""
        all_docs_summary = []
        try:
            # Only fetch necessary fields for summary, improve performance
            # 限制查询结果为10条
            all_docs_cursor = collection.find({}, {"EnterpriseCode": 1, "EnterpriseName": 1}).limit(10)
            for doc in all_docs_cursor:
                code = doc.get("EnterpriseCode", "未知代码")
                name = doc.get("EnterpriseName", "未知名称")
                all_docs_summary.append({"_id": str(doc["_id"]), "display": f"{code} - {name}", "code": code})
        except Exception as e:
            st.error(f"加载0级文档列表失败：{e}")
            all_docs_summary = []
        return all_docs_summary

    # Load all documents summary (0-level) - 限制显示最多10条数据
    if not st.session_state.docs_summary_cache:
        with st.spinner("正在加载企业文档列表 (0级)..."):
            time.sleep(0.5)
            st.session_state.docs_summary_cache = load_documents_summary()

    all_docs_summary = st.session_state.docs_summary_cache

    if not all_docs_summary:
        st.warning("无可用文档进行选择，请确认集合中存在数据")
        return

    # 0-level dropdown (Enterprise Document Selection)
    zero_level_options = [doc["display"] for doc in all_docs_summary]
    if st.session_state.extract_zero_level_display is None:
        st.session_state.extract_zero_level_display = zero_level_options[0]

    col1, col2, col3 = st.columns([4, 1, 1])
    with col1:
        selected_zero_level_display = st.selectbox(
            "📜 全量档案数据抽取",
            options=zero_level_options,
            index=zero_level_options.index(st.session_state.extract_zero_level_display) if st.session_state.extract_zero_level_display in zero_level_options else 0,
            key="extract_zero_level_select",
            help="选择一个企业文档以查看其详细子文档结构。",
            on_change=lambda: [
                st.session_state.__setitem__("extract_zero_level_display", st.session_state["extract_zero_level_select"]),
                st.session_state.__setitem__("extract_level1", None), # Reset all lower levels
                st.session_state.__setitem__("extract_level2", None),
                st.session_state.__setitem__("extract_level3", None),
                st.session_state.__setitem__("extract_field", None),
                st.session_state.__setitem__("current_data_url", ""),  # Reset data URL
                # st.rerun()
            ]
        )
    
    # 封装全量抽取函数
    def perform_full_extraction(enterprise_code, collection, progress_placeholder, status_placeholder):
        """
        执行全量抽取操作，向所有空字段插入测试数据
        """
        try:
            # 查找对应的完整文档
            query = {"EnterpriseCode": enterprise_code}
            full_doc = collection.find_one(query)
            
            if not full_doc:
                return False, "未找到对应的企业文档"
            
            updated_count = 0
            total_fields = 0
            
            # 首先计算总字段数
            def count_fields_recursive(children):
                nonlocal total_fields
                for level1_child in children:
                    if "children" in level1_child:
                        for level2_child in level1_child["children"]:
                            if "children" in level2_child:
                                for level3_child in level2_child["children"]:
                                    if "fields" in level3_child:
                                        total_fields += len(level3_child["fields"])
            
            # 计算总字段数
            if "children" in full_doc:
                count_fields_recursive(full_doc["children"])
            
            processed_fields = 0
            
            # 递归遍历所有子文档的字段
            def insert_test_data_recursive(children, path=""):
                nonlocal updated_count, processed_fields
                for level1_child in children:
                    if "children" in level1_child:
                        for level2_child in level1_child["children"]:
                            if "children" in level2_child:
                                for level3_child in level2_child["children"]:
                                    if "fields" in level3_child:
                                        for field in level3_child["fields"]:
                                            processed_fields += 1
                                            field_name = field.get("field_name", "")
                                            
                                            # 更新进度条
                                            progress = processed_fields / total_fields if total_fields > 0 else 0
                                            progress_placeholder.progress(progress,f"抽取进度: {processed_fields}/{total_fields}")
                                            # progress_placeholder.progress(progress)

                                            if field_name:
                                                # 确保data子文档存在
                                                if "data" not in field:
                                                    field["data"] = {}
                                                
                                                data_obj = field["data"]
                                                field_updated = False
                                                
                                                # 检查并更新value字段
                                                current_value = data_obj.get("value", "")
                                                if current_value == "" or current_value == "*空字段*":
                                                    data_obj["value"] = f"{field_name}测试值"
                                                    field_updated = True
                                                
                                                # 检查并更新relate_pic字段
                                                current_pic = data_obj.get("relate_pic", "")
                                                if current_pic == "" or current_pic == "*空字段*":
                                                    data_obj["relate_pic"] = f"{field_name}测试图片.jpg"
                                                    field_updated = True
                                                
                                                # 检查并更新relate_doc字段
                                                current_doc = data_obj.get("relate_doc", "")
                                                if current_doc == "" or current_doc == "*空字段*":
                                                    data_obj["relate_doc"] = f"{field_name}测试文档.doc"
                                                    field_updated = True
                                                
                                                # 检查并更新relate_video字段
                                                current_video = data_obj.get("relate_video", "")
                                                if current_video == "" or current_video == "*空字段*":
                                                    data_obj["relate_video"] = f"{field_name}测试视频.mp4"
                                                    field_updated = True
                                                
                                                if field_updated:
                                                    updated_count += 1
                                                    time.sleep(0.03)
                                                    # 只显示当前正在处理的字段
                                                    status_placeholder.write(f"✅ 正在更新字段: {field_name}")
                                                
                                                # 添加短暂延迟以便用户看到进度
                                                time.sleep(0.01)
            
            # 开始递归插入测试数据
            if "children" in full_doc:
                insert_test_data_recursive(full_doc["children"])
                
                if updated_count > 0:
                    # 更新数据库
                    status_placeholder.write("📝 正在保存到数据库...")
                    result = collection.replace_one(
                        {"EnterpriseCode": enterprise_code}, 
                        full_doc
                    )
                    
                    if result.matched_count > 0:
                        return True, f"成功更新了 {updated_count} 个字段的数据"
                    else:
                        return False, "数据库更新失败"
                else:
                    return True, "没有找到需要更新的空字段"
            else:
                return False, "该文档没有子文档结构"
                
        except Exception as e:
            return False, f"操作失败: {str(e)}"

    with col2:
        # Add some vertical spacing to align the button with the selectbox
        st.write("") 
        st.write("") 
        if st.button("刷新", type="primary",help="刷新企业文档列表"):
            with st.spinner("正在刷新企业文档列表..."):
                st.session_state.docs_summary_cache = load_documents_summary()
                # 重新获取选项列表
                zero_level_options = [doc["display"] for doc in st.session_state.docs_summary_cache]
                if zero_level_options:
                    st.session_state.extract_zero_level_display = zero_level_options[0]
                st.success("✅ 文档列表已刷新！")
                st.rerun()

    with col3:
        # Add some vertical spacing to align the button with the selectbox
        st.write("") 
        st.write("") 
        if st.button("全量抽取"):
            # 全量抽取功能实现
            selected_enterprise_code = None
            for doc_summary in all_docs_summary:
                if doc_summary["display"] == selected_zero_level_display:
                    selected_enterprise_code = doc_summary["code"]
                    break
            
            if selected_enterprise_code:
                # 创建进度条和状态显示区域
                progress_placeholder = st.empty()
                status_placeholder = st.empty()
                
                with st.spinner("正在进行全量抽取，向所有子文档插入数据..."):
                    success, message = perform_full_extraction(
                        selected_enterprise_code, 
                        collection,
                        progress_placeholder,
                        status_placeholder
                    )
                    
                    # 清除状态显示
                    status_placeholder.empty()
                    
                    if success:
                        progress_placeholder.empty()
                        st.success(f"🎉 全量抽取成功！企业代码: {selected_enterprise_code}\n{message}")
                    else:
                        progress_placeholder.empty()
                        st.error(f"❌ 全量抽取失败：{message}")
            else:
                st.error("无法获取企业代码。")
    
    st.session_state.extract_zero_level_display = selected_zero_level_display
    st.write("---")

    # Get selected document ID and code
    selected_doc_id = None
    selected_enterprise_code = None
    for doc_summary in all_docs_summary:
        if doc_summary["display"] == st.session_state.extract_zero_level_display:
            selected_doc_id = doc_summary["_id"]
            selected_enterprise_code = doc_summary["code"]
            break

    # Load full document
    selected_full_doc = None
    if selected_doc_id:
        with st.spinner("正在加载完整企业文档..."):
            time.sleep(0.5)
            try:
                selected_full_doc = collection.find_one({"_id": selected_doc_id.strip()})
            except Exception as e:
                st.error(f"加载选中的完整文档失败：{e}")

    if not selected_full_doc:
        st.error("无法加载选中的企业文档。")
        return

    # Get level 1 options from MongoDB data
    level1_options = [child.get("name", "") for child in selected_full_doc["children"] if child.get("name")]
    if not level1_options:
        st.error("❗ 第一级子文档中没有找到有效的 `name` 字段。")
        return

    # Horizontal arrangement of dropdowns
    col1, col2, col3, col4 = st.columns(4)
    # Level 1 dropdown
    with col1:
        if st.session_state.extract_level1 is None and level1_options:
            st.session_state.extract_level1 = level1_options[0]
        
        selected_level1 = st.selectbox(
            "一级档案",
            options=level1_options,
            index=level1_options.index(st.session_state.extract_level1) if st.session_state.extract_level1 in level1_options else 0,
            key="extract_level1_select",
            on_change=lambda: [
                st.session_state.__setitem__("extract_level1", st.session_state["extract_level1_select"]),
                st.session_state.__setitem__("extract_level2", None), # Reset lower levels
                st.session_state.__setitem__("extract_level3", None),
                st.session_state.__setitem__("extract_field", None),
                st.session_state.__setitem__("current_data_url", ""),  # Reset data URL
                # st.rerun()
            ]
        )
    st.session_state.extract_level1 = selected_level1

    # Get level 1 document for level 2 options
    selected_level1_doc = None
    if st.session_state.extract_level1:
        for child in selected_full_doc["children"]:
            if child.get("name") == st.session_state.extract_level1:
                selected_level1_doc = child
                break

    # Level 2 dropdown
    level2_options = []
    if selected_level1_doc and "children" in selected_level1_doc:
        level2_options = [child.get("name", "") for child in selected_level1_doc["children"] if child.get("name")]

    with col2:
        if level2_options:
            if st.session_state.extract_level2 is None and level2_options:
                st.session_state.extract_level2 = level2_options[0]
            
            selected_level2 = st.selectbox(
                "二级档案",
                options=level2_options,
                index=level2_options.index(st.session_state.extract_level2) if st.session_state.extract_level2 in level2_options else 0,
                key="extract_level2_select",
                on_change=lambda: [
                    st.session_state.__setitem__("extract_level2", st.session_state["extract_level2_select"]),
                    st.session_state.__setitem__("extract_level3", None),
                    st.session_state.__setitem__("extract_field", None),
                    st.session_state.__setitem__("current_data_url", ""),  # Reset data URL
                    # st.rerun()
                ]
            )
        else:
            st.selectbox("二级档案", options=["无可用选项"], disabled=True, key="extract_level2_select_disabled")
            selected_level2 = None
    st.session_state.extract_level2 = selected_level2

    # Get level 2 document for level 3 options
    selected_level2_doc = None
    if selected_level1_doc and "children" in selected_level1_doc and st.session_state.extract_level2:
        for child in selected_level1_doc["children"]:
            if child.get("name") == st.session_state.extract_level2:
                selected_level2_doc = child
                break

    # Level 3 dropdown
    level3_options = []
    if selected_level2_doc and "children" in selected_level2_doc:
        level3_options = [child.get("name", "") for child in selected_level2_doc["children"] if child.get("name")]

    with col3:
        if level3_options:
            if st.session_state.extract_level3 is None and level3_options:
                st.session_state.extract_level3 = level3_options[0]
            
            selected_level3 = st.selectbox(
                "三级档案",
                options=level3_options,
                index=level3_options.index(st.session_state.extract_level3) if st.session_state.extract_level3 in level3_options else 0,
                key="extract_level3_select",
                on_change=lambda: [
                    st.session_state.__setitem__("extract_level3", st.session_state["extract_level3_select"]),
                    st.session_state.__setitem__("extract_field", None),
                    st.session_state.__setitem__("current_data_url", ""),  # Reset data URL
                    # st.rerun()
                ]
            )
        else:
            st.selectbox("三级档案", options=["无可用选项"], disabled=True, key="extract_level3_select_disabled")
            selected_level3 = None
    st.session_state.extract_level3 = selected_level3

    # Get level 3 document for field options
    selected_level3_doc = None
    if selected_level2_doc and "children" in selected_level2_doc and st.session_state.extract_level3:
        for child in selected_level2_doc["children"]:
            if child.get("name") == st.session_state.extract_level3:
                selected_level3_doc = child
                break
    # Field dropdown
    field_options = []
    if selected_level3_doc and "fields" in selected_level3_doc:
        field_options = [field.get("field_name", "") for field in selected_level3_doc["fields"] if field.get("field_name")]

    with col4:
        if field_options:
            if st.session_state.extract_field is None and field_options:
                st.session_state.extract_field = field_options[0]
            
            selected_field = st.selectbox(
                "字段名称",
                options=field_options,
                index=field_options.index(st.session_state.extract_field) if st.session_state.extract_field in field_options else 0,
                key="extract_field_select",
                on_change=lambda: [
                    st.session_state.__setitem__("extract_field", st.session_state["extract_field_select"]),
                    st.session_state.__setitem__("current_data_url", ""),  # Reset data URL when field changes
                ]
            )
        else:
            st.selectbox("字段名称", options=["无可用选项"], disabled=True, key="extract_field_select_disabled")
            selected_field = None
    st.session_state.extract_field = selected_field

    # 查找并显示data_url
    def get_data_url():
        """根据选择的层级和字段查找data_url"""
        if not all([selected_enterprise_code, st.session_state.extract_level1, 
                   st.session_state.extract_level2, st.session_state.extract_level3, 
                   st.session_state.extract_field]):
            return ""
        
        try:
            # 使用企业代码和层级信息查找对应的字段
            query = {"EnterpriseCode": selected_enterprise_code}
            doc = collection.find_one(query)
            
            if not doc:
                return ""
            
            # 遍历文档结构找到对应的字段
            for level1_child in doc.get("children", []):
                if level1_child.get("name") == st.session_state.extract_level1:
                    for level2_child in level1_child.get("children", []):
                        if level2_child.get("name") == st.session_state.extract_level2:
                            for level3_child in level2_child.get("children", []):
                                if level3_child.get("name") == st.session_state.extract_level3:
                                    for field in level3_child.get("fields", []):
                                        if field.get("field_name") == st.session_state.extract_field:
                                            data_obj = field.get("data", {})
                                            return data_obj.get("data_url", "")
            return ""
        except Exception as e:
            st.error(f"查找data_url失败：{e}")
            return ""

    # 更新data_url
    if (st.session_state.extract_level1 and st.session_state.extract_level2 and 
        st.session_state.extract_level3 and st.session_state.extract_field):
        if not st.session_state.current_data_url:  # 只有当前为空时才查找
            st.session_state.current_data_url = get_data_url()

    # 显示当前数据接口值
    st.text_input(
        "当前数据接口值", 
        value=st.session_state.current_data_url, 
        disabled=True, 
        key="data_interface_final_display"
    )

    # 封装字段值更新函数
    def update_field_value(enterprise_code, level1, level2, level3, field_name, collection):
        """
        更新指定字段的值
        """
        try:
            # 使用企业代码查找文档
            query = {"EnterpriseCode": enterprise_code}
            doc = collection.find_one(query)
            
            if not doc:
                return False, "未找到对应的企业文档"
            
            field_found = False
            field_updated = False
            
            # 遍历文档结构找到对应的字段并更新
            for level1_child in doc.get("children", []):
                if level1_child.get("name") == level1:
                    for level2_child in level1_child.get("children", []):
                        if level2_child.get("name") == level2:
                            for level3_child in level2_child.get("children", []):
                                if level3_child.get("name") == level3:
                                    for field in level3_child.get("fields", []):
                                        if field.get("field_name") == field_name:
                                            field_found = True
                                            
                                            # 确保data子文档存在
                                            if "data" not in field:
                                                field["data"] = {}
                                            
                                            # 获取当前value值
                                            current_value = field["data"].get("value", "")
                                            
                                            # 创建新的测试数据
                                            new_test_value = f"{field_name}更新测试值"
                                            
                                            # 更新或插入value
                                            if current_value != new_test_value:
                                                field["data"]["value"] = new_test_value
                                                field_updated = True
                                                st.write(f"✅ 字段 {field_name} 值已更新为: {new_test_value}")
                                            
                                            break
            
            if not field_found:
                return False, "未找到指定的字段路径"
            
            if field_updated:
                # 更新数据库
                result = collection.replace_one(
                    {"EnterpriseCode": enterprise_code}, 
                    doc
                )
                
                if result.matched_count > 0:
                    return True, f"字段值更新成功"
                else:
                    return False, "数据库更新失败"
            else:
                return True, "字段值已经是最新的，无需更新"
                
        except Exception as e:
            return False, f"操作失败: {str(e)}"

    # Generate button - 更新字段值功能
    if st.button("更新字段值", key="generate_archive_btn"):
        if st.session_state.extract_level1 and st.session_state.extract_level2 and \
           st.session_state.extract_level3 and st.session_state.extract_field:
            with st.spinner("正在更新字段值..."):
                success, message = update_field_value(
                    selected_enterprise_code,
                    st.session_state.extract_level1,
                    st.session_state.extract_level2,
                    st.session_state.extract_level3,
                    st.session_state.extract_field,
                    collection
                )
                
                if success:
                    st.success(f"🎉 {message}\n"
                             f"- 企业代码: **{selected_enterprise_code}**\n"
                             f"- 一级: **{st.session_state.extract_level1}**\n"
                             f"- 二级: **{st.session_state.extract_level2}**\n"
                             f"- 三级: **{st.session_state.extract_level3}**\n"
                             f"- 字段: **{st.session_state.extract_field}**")
                    # 刷新当前data_url显示
                    st.session_state.current_data_url = get_data_url()
                else:
                    st.error(f"❌ {message}")
        else:
            st.warning("请完整选择所有档案层级和字段名称。")
    st.write("---")
#endregion

# --- Main Function: Controls page rendering logic and authentication ---
def main():
    """Page main function: controls access permissions and renders content."""
    auth_manager = AuthManager()
    st.title("📝 登记/创建企业档案")
    render_sidebar()
    if not auth_manager.is_authenticated():
        st.error("请先登录才能访问此页面！")
        if st.button("🏠 返回主页", type="primary" ,key="back_to_main_login_ops"):
            st.switch_page("系统主页.py")
    else:
        apply_custom_css()  
        collection = _check_and_connect_mongo()  
        if collection is not None:       
            _render_register_archive_section()
            st.markdown("---")
            _render_extract_archive_section()

if __name__ == "__main__":
    main()
