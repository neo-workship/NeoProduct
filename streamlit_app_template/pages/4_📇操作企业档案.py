import streamlit as st
import pandas as pd
from pymongo import MongoClient
from bson.objectid import ObjectId
import json
import time
import sys
import os

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from utils import apply_custom_css
from 系统主页 import AuthManager, render_sidebar # Import authentication manager and sidebar render function

st.set_page_config(page_title="操作政务集合数据", page_icon="📇", layout="wide")
# --- Core Rendering Functions for different sections ---

# @st.cache_resource
def _check_and_connect_mongo():
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
            collection.find_one({})
            # st.success(f"✨ 成功连接到：数据库 **{db_name}** 中的集合 **{collection_name}**")
            # st.info(f"您现在可以对集合 `{collection_name}` 进行文档预览、查询、插入、更新和删除操作。")
            return collection
        except Exception as e:
            st.error(f"❌ 连接到集合 **{collection_name}** 失败：{e}")
            st.warning("请检查数据库和集合是否存在，或返回上一个页面重新选择。")
            return None # Return None if connection fails

@st.fragment
def _render_document_preview(collection):
    """
    Renders the document preview and pagination section.
    Requires a valid MongoDB collection object.
    """
    # st.markdown("---") # Add separator for visual hierarchy
    st.subheader("🖥️ 1、预览企业档案")
    with st.expander("🖥️ 文档预览和分页设置", expanded=False): # Changed to False for default collapsed state
        st.subheader("集合文档预览")

        total_docs = 0
        with st.spinner(f"正在计算集合 **{collection.name}** 的文档总数..."):
            time.sleep(0.5)
            try:
                total_docs = collection.count_documents({})
                st.info(f"集合 **{collection.name}** 中共有 **{total_docs}** 个文档。")
            except Exception as e:
                st.error(f"无法获取文档总数：{e}")

        page_size = st.slider("每页显示文档数量", min_value=5, max_value=100, value=10, step=5, key="doc_preview_page_size_slider")

        # Initialize or update skip_count for pagination
        if "skip_count" not in st.session_state:
            st.session_state.skip_count = 0
        # Reset skip_count if page_size changes to avoid empty pages
        if st.session_state.get("last_page_size") != page_size:
            st.session_state.skip_count = 0
            st.session_state.last_page_size = page_size
            st.rerun() # Rerun to apply new page size immediately

        docs = []
        with st.spinner(f"正在加载文档 ({st.session_state.skip_count + 1} - {min(st.session_state.skip_count + page_size, total_docs)})..."):
            time.sleep(0.7)
            try:
                docs = list(collection.find().skip(st.session_state.skip_count).limit(page_size))
            except Exception as e:
                st.error(f"加载文档失败: {e}")

        # Column renaming map for displayed DataFrame
        rename_map = {
            "_id": "文档ID",
            "EnterpriseCode": "企业代码",
            "EnterpriseName": "企业名称",
            "Level1Nums": "一级文档数",
            "type": "类型"
        }
        columns_to_keep = ["_id", "EnterpriseCode", "EnterpriseName", "Level1Nums", "type"]

        if docs:
            df = pd.DataFrame(docs)
            df_filtered = df[[col for col in columns_to_keep if col in df.columns]]
            df_filtered = df_filtered.rename(columns=rename_map)

            if '文档ID' in df_filtered.columns:
                df_filtered['文档ID'] = df_filtered['文档ID'].astype(str)

            st.write("---")
            st.write("**完整文档数据：**")
            st.dataframe(df_filtered, use_container_width=True)

            # Pagination buttons
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("上一页", key="prev_page_btn_doc_preview"):
                    if st.session_state.skip_count >= page_size:
                        st.session_state.skip_count -= page_size
                        st.rerun()
                    else:
                        st.warning("已经是第一页了！")
            with col2:
                current_end_record = min(st.session_state.skip_count + len(docs), total_docs)
                st.markdown(f"<h5 style='text-align: center; margin-top: 15px;'>显示第 {st.session_state.skip_count + 1} - {current_end_record} 条记录 (共 {total_docs} 条)</h5>", unsafe_allow_html=True)
            with col3:
                if st.button("下一页", key="next_page_btn_doc_preview"):
                    if st.session_state.skip_count + page_size < total_docs:
                        st.session_state.skip_count += page_size
                        st.rerun()
                    else:
                        st.warning("已经是最后一页了！")
        else:
            st.info("当前集合没有找到文档或加载失败。")

@st.fragment
def _display_meta_tab(tab_obj, meta_key, title, meta_data_dict, col_rename_map=None):
    """Helper function to display meta data in tabs."""
    with tab_obj:
        st.markdown(f"<p class='result-data-title'>{title}：</p>", unsafe_allow_html=True)
        if meta_key in meta_data_dict and meta_data_dict[meta_key]:
            try:
                if isinstance(meta_data_dict[meta_key], dict):
                    processed_meta = {k: [v] if not isinstance(v, (list, dict)) else v for k, v in meta_data_dict[meta_key].items()}
                    if any(isinstance(v, dict) for v in processed_meta.values()):
                        st.markdown("<div class='result-code-block'>", unsafe_allow_html=True)
                        st.json(meta_data_dict[meta_key])
                        st.markdown("</div>", unsafe_allow_html=True)
                    else:
                        meta_df = pd.DataFrame([processed_meta])
                        if col_rename_map:
                            meta_df = meta_df.rename(columns=col_rename_map)
                        st.dataframe(meta_df, use_container_width=True)
                elif isinstance(meta_data_dict[meta_key], list):
                    meta_df = pd.DataFrame(meta_data_dict[meta_key])
                    if col_rename_map:
                        meta_df = meta_df.rename(columns=col_rename_map)
                    st.dataframe(meta_df, use_container_width=True)
                else:
                    st.markdown("<div class='result-code-block'>", unsafe_allow_html=True)
                    st.code(str(meta_data_dict[meta_key]), language="json")
                    st.markdown("</div>", unsafe_allow_html=True)
            except Exception as e:
                st.error(f"加载 {title} 失败: {e}")
                st.json(meta_data_dict[meta_key])
        else:
            st.info(f"无 {title} 数据")

@st.fragment
def _render_subdocument_selector(collection):
    """
    Renders the multi-level sub-document selector and displays selected field data and meta-data.
    Requires a valid MongoDB collection object.
    """
    st.subheader("🔍 2、查询企业数据")
    with st.expander("🔍 查询企业数据", expanded=False):
        all_docs_summary = []
        with st.spinner("正在加载企业文档列表 (0级)..."):
            time.sleep(0.5)
            try:
                # Only fetch necessary fields for summary, improve performance
                # all_docs_cursor = collection.find({}, {"EnterpriseCode": 1, "EnterpriseName": 1})
                all_docs_cursor = collection.find({}, {"EnterpriseCode": 1, "EnterpriseName": 1}).limit(10)
                for doc in all_docs_cursor:
                    code = doc.get("EnterpriseCode", "未知代码")
                    name = doc.get("EnterpriseName", "未知名称")
                    all_docs_summary.append({"_id": str(doc["_id"]), "display": f"{code} - {name}"})
            except Exception as e:
                st.error(f"加载0级文档列表失败：{e}")
                all_docs_summary = []

        if not all_docs_summary:
            st.warning("无可用文档进行0级选择，请确认集合中存在数据。")
        else:
            zero_level_options = [doc["display"] for doc in all_docs_summary]
            
            # Initialize session state for all levels of dropdowns if not present
            if "selected_zero_level_display" not in st.session_state:
                st.session_state.selected_zero_level_display = zero_level_options[0]
            if "selected_level1" not in st.session_state: st.session_state.selected_level1 = None
            if "selected_level2" not in st.session_state: st.session_state.selected_level2 = None
            if "selected_level3" not in st.session_state: st.session_state.selected_level3 = None
            if "selected_level4" not in st.session_state: st.session_state.selected_level4 = None

            st.markdown("##### **选择企业档案**")
            # 0-level dropdown (Enterprise Document)
            selected_zero_level_display = st.selectbox(
                " ",
                options=zero_level_options,
                index=zero_level_options.index(st.session_state.selected_zero_level_display) if st.session_state.selected_zero_level_display in zero_level_options else 0,
                key="zero_level_select",
                help="选择一个企业文档以查看其详细子文档结构",
                on_change=lambda: [
                    st.session_state.__setitem__("selected_zero_level_display", st.session_state["zero_level_select"]),
                    st.session_state.__setitem__("selected_level1", None), # Reset all lower levels on 0-level change
                    st.session_state.__setitem__("selected_level2", None),
                    st.session_state.__setitem__("selected_level3", None),
                    st.session_state.__setitem__("selected_level4", None),
                    st.rerun() # Rerun to update options based on new 0-level selection
                ]
            )
            st.session_state.selected_zero_level_display = selected_zero_level_display

            selected_doc_id = None
            for doc_summary in all_docs_summary:
                if doc_summary["display"] == st.session_state.selected_zero_level_display:
                    selected_doc_id = doc_summary["_id"]
                    break

            selected_full_doc = None
            if selected_doc_id:
                with st.spinner("正在加载完整企业文档..."):
                    time.sleep(0.5)
                    try:
                        selected_full_doc = collection.find_one({"_id": selected_doc_id})
                    except Exception as e:
                        st.error(f"加载选中的完整文档失败：{e}")

            if selected_full_doc:
                enterprise_info_cols = st.columns(2)
                with enterprise_info_cols[0]:
                    st.markdown(
                        f"<span style='color:green; font-weight:bold;'>企业代码：</span> "
                        f"<span style='color:green;'>{selected_full_doc.get('EnterpriseCode', 'N/A')}</span>",
                        unsafe_allow_html=True
                    )
                with enterprise_info_cols[1]:
                    st.markdown(
                        f"<span style='color:green; font-weight:bold;'>企业名称：</span> "
                        f"<span style='color:green;'>{selected_full_doc.get('EnterpriseName', 'N/A')}</span>",
                        unsafe_allow_html=True
                    )
                st.write("---")

                if "children" not in selected_full_doc or not selected_full_doc["children"]:
                    st.error("❗ 选中的文档中没有找到 `children` 字段或 `children` 为空。此部分功能无法使用。")
                else:
                    level1_options = [child.get("name", "") for child in selected_full_doc["children"] if child.get("name")]
                    if not level1_options:
                        st.error("❗ 第一级子文档中没有找到有效的 `name` 字段。")
                    
                    row1_col1, row1_col2 = st.columns(2)
                    row2_col1, row2_col2 = st.columns(2)
                    
                
                    # Level 1 Selectbox
                    with row1_col1:      
                        if level1_options:
                            current_l1_index = 0
                            if st.session_state.selected_level1 is None and level1_options:
                                st.session_state.selected_level1 = level1_options[0] # Default to first if not set
                            if st.session_state.selected_level1 in level1_options:
                                current_l1_index = level1_options.index(st.session_state.selected_level1)
                            
                            selected_level1 = st.selectbox(
                                "📊 **一级企业文档**",
                                options=level1_options,
                                index=current_l1_index,
                                key="level1_select",
                                help="选择第一级子文档（例如：基本信息，财务信息等）",
                                on_change=lambda: [st.session_state.__setitem__("selected_level1", st.session_state["level1_select"]),
                                                st.session_state.__setitem__("selected_level2", None), # Reset lower levels
                                                st.session_state.__setitem__("selected_level3", None),
                                                st.session_state.__setitem__("selected_level4", None),
                                                st.rerun()] # Rerun to update options
                            )
                        else:
                            st.selectbox("📊 **一级企业文档**", options=["无可用选项"], disabled=True, key="level1_select_disabled")

                    st.session_state.selected_level1 = selected_level1 # Ensure session state is updated

                    selected_level1_doc = None
                    if st.session_state.selected_level1:
                        for child in selected_full_doc["children"]:
                            if child.get("name") == st.session_state.selected_level1:
                                selected_level1_doc = child
                                break
                    
                    level2_options = []
                    if selected_level1_doc and "children" in selected_level1_doc:
                        level2_options = [child.get("name", "") for child in selected_level1_doc["children"] if child.get("name")]
                    
                    # Level 2 Selectbox
                    with row1_col2:
                        if level2_options:
                            current_l2_index = 0
                            if st.session_state.selected_level2 is None and level2_options:
                                st.session_state.selected_level2 = level2_options[0] # Default to first if not set
                            if st.session_state.selected_level2 in level2_options:
                                current_l2_index = level2_options.index(st.session_state.selected_level2)

                            selected_level2 = st.selectbox(
                                "📈 **二级企业文档**",
                                options=level2_options,
                                index=current_l2_index,
                                key="level2_select",
                                help="选择第二级子文档（例如：登记信息，人员构成等）",
                                on_change=lambda: [st.session_state.__setitem__("selected_level2", st.session_state["level2_select"]),
                                                st.session_state.__setitem__("selected_level3", None), # Reset lower levels
                                                st.session_state.__setitem__("selected_level4", None),
                                                st.rerun()]
                            )
                        else:
                            st.selectbox("📈 **二级企业文档**", options=["无可用选项"], disabled=True, key="level2_select_disabled")

                    st.session_state.selected_level2 = selected_level2

                    selected_level2_doc = None
                    if selected_level1_doc and "children" in selected_level1_doc and st.session_state.selected_level2:
                        for child in selected_level1_doc["children"]:
                            if child.get("name") == st.session_state.selected_level2:
                                selected_level2_doc = child
                                break
                    
                    level3_options = []
                    if selected_level2_doc and "children" in selected_level2_doc:
                        level3_options = [child.get("name", "") for child in selected_level2_doc["children"] if child.get("name")]
                    
                    # Level 3 Selectbox
                    with row2_col1:
                        if level3_options:
                            current_l3_index = 0
                            if st.session_state.selected_level3 is None and level3_options:
                                st.session_state.selected_level3 = level3_options[0] # Default to first if not set
                            if st.session_state.selected_level3 in level3_options:
                                current_l3_index = level3_options.index(st.session_state.selected_level3)

                            selected_level3 = st.selectbox(
                                "📉 **三级企业文档**",
                                options=level3_options,
                                index=current_l3_index,
                                key="level3_select",
                                help="选择第三级子文档（例如：企业基本信息，股东信息等）",
                                on_change=lambda: [st.session_state.__setitem__("selected_level3", st.session_state["level3_select"]),
                                                st.session_state.__setitem__("selected_level4", None), # Reset lower levels
                                                st.rerun()]
                            )
                        else:
                            st.selectbox("📉 **三级企业文档**", options=["无可用选项"], disabled=True, key="level3_select_disabled")

                    st.session_state.selected_level3 = selected_level3

                    selected_level3_doc = None
                    if selected_level2_doc and "children" in selected_level2_doc and st.session_state.selected_level3:
                        for child in selected_level2_doc["children"]:
                            if child.get("name") == st.session_state.selected_level3:
                                selected_level3_doc = child
                                break
                    
                    level4_options = []
                    if selected_level3_doc and "fields" in selected_level3_doc:
                        level4_options = [field.get("field_name", "") for field in selected_level3_doc["fields"] if field.get("field_name")]
                    
                    # Level 4 Selectbox
                    with row2_col2:
                        if level4_options:
                            current_l4_index = 0
                            if st.session_state.selected_level4 is None and level4_options:
                                st.session_state.selected_level4 = level4_options[0] # Default to first if not set
                            if st.session_state.selected_level4 in level4_options:
                                current_l4_index = level4_options.index(st.session_state.selected_level4)

                            selected_level4 = st.selectbox(
                                "📑 **企业属性字段**",
                                options=level4_options,
                                index=current_l4_index,
                                key="level4_select",
                                help="选择第四级字段名（例如：统一社会信用代码，企业名称等）",
                                on_change=lambda: st.session_state.__setitem__("selected_level4", st.session_state["level4_select"])
                            )
                        else:
                            st.selectbox("📑 企业属性字段", options=["无可用选项"], disabled=True, key="level4_select_disabled")

                    st.session_state.selected_level4 = selected_level4

                    st.markdown("##### **当前选择路径:**")
                    path_info = f"一级: **{st.session_state.selected_level1 if st.session_state.selected_level1 else '未选择'}**"
                    if st.session_state.selected_level2:
                        path_info += f" → 二级: **{st.session_state.selected_level2}**"
                    if st.session_state.selected_level3:
                        path_info += f" → 三级: **{st.session_state.selected_level3}**"
                    if st.session_state.selected_level4:
                        path_info += f" → 四级: **{st.session_state.selected_level4}**"
                    st.info(path_info)
                    
                    # Display selected field data and meta-data
                    if st.session_state.selected_level4 and selected_level3_doc:
                        selected_field_data = None
                        for field in selected_level3_doc.get("fields", []):
                            if field.get("field_name") == st.session_state.selected_level4:
                                selected_field_data = field
                                break
                        
                        if selected_field_data:
                            st.markdown("##### **字段详细信息:**")
                            field_info_cols = st.columns(3)
                            with field_info_cols[0]:
                                st.markdown(
                                    f"<span style='font-weight:bold;'>字段名：</span> "
                                    f"<span style='color:green;'>{selected_field_data.get('field_name', 'N/A')}</span>",
                                    unsafe_allow_html=True
                                )
                            with field_info_cols[1]:
                                st.markdown(
                                    f"<span style='font-weight:bold;'>备注：</span> "
                                    f"<span style='color:green;'>{selected_field_data.get('remark', '无')}</span>",
                                    unsafe_allow_html=True
                                )
                            with field_info_cols[2]:
                                st.markdown(
                                    f"<span style='font-weight:bold;'>行号：</span> "
                                    f"<span style='color:green;'>{selected_field_data.get('row_number', 'N/A')}</span>",
                                    unsafe_allow_html=True
                                )

                            st.markdown("<p class='result-data-title'>字段数据值：</p>", unsafe_allow_html=True)
                            if "data" in selected_field_data:
                                try:
                                    if isinstance(selected_field_data["data"], dict):
                                        data_rename_map = {
                                            "value": "字段值", "relate_pic": "关联图片",
                                            "relate_doc": "关联文档", "relate_video": "关联视频"
                                        }
                                        data_df = pd.DataFrame([selected_field_data["data"]]).rename(columns=data_rename_map)
                                        st.markdown("<div class='result-dataframe-container'>", unsafe_allow_html=True)
                                        st.dataframe(data_df, use_container_width=True)
                                        st.markdown("</div>", unsafe_allow_html=True)
                                    elif isinstance(selected_field_data["data"], list):
                                        data_rename_map = {
                                            "value": "字段值", "relate_pic": "关联图片",
                                            "relate_doc": "关联文档", "relate_video": "关联视频"
                                        }
                                        data_df = pd.DataFrame(selected_field_data["data"]).rename(columns=data_rename_map)
                                        st.markdown("<div class='result-dataframe-container'>", unsafe_allow_html=True)
                                        st.dataframe(data_df, use_container_width=True)
                                        st.markdown("</div>", unsafe_allow_html=True)
                                    else:
                                        st.markdown("<div class='result-code-block'>", unsafe_allow_html=True)
                                        st.code(str(selected_field_data["data"]), language="json")
                                        st.markdown("</div>", unsafe_allow_html=True)
                                except Exception as e:
                                    st.error(f"字段数据展示失败: {e}")
                                    st.json(selected_field_data["data"])
                            else:
                                st.info("当前字段无 `data` 信息。")
                            
                            if selected_field_data and "meta" in selected_field_data:
                                meta_data = selected_field_data["meta"]
                                st.markdown("##### **字段元数据：**")
                                
                                tab1, tab2, tab3, tab4 = st.tabs(["基本元数据", "技术元数据", "管理元数据", "数据字典"])
                                
                                # Renaming maps for meta data tabs
                                basic_meta_rename_map = {
                                    "meta_content": "元数据说明", "identifier": "数据的唯一标识符", "title": "数据资源名称",
                                    "description": "简要说明", "create_date": "数据创建时间", "update_date": "最后修改时间",
                                    "creator": "数据作者或创建机构", "subject": "数据关键词或分类代码"
                                }
                                tech_meta_rename_map = {
                                    "meta_content": "技术性描述元数据", "format": "数据格式或媒体类型", "size": "数据量大小",
                                    "location": "数据存储位置或URL", "version": "数据版本", "encoding": "数据字符编码"
                                }
                                manage_meta_rename_map = {
                                    "meta_content": "管理字段元数据", "rights": "访问和使用权限", "license": "数据使用许可条款",
                                    "source": "数据原始来源", "quality": "数据质量评估", "history": "数据创建和处理记录"
                                }
                                data_dic_rename_map = {
                                    "meta_content": "字段取值字典", "value1": "取值1", "value2": "取值2", "value3": "取值3"
                                }

                                _display_meta_tab(tab1, "basic_meta", "基本元数据信息", meta_data, basic_meta_rename_map)
                                _display_meta_tab(tab2, "tech_meta", "技术元数据信息", meta_data, tech_meta_rename_map)
                                _display_meta_tab(tab3, "manage_meta", "管理元数据信息", meta_data, manage_meta_rename_map)
                                _display_meta_tab(tab4, "data_dic", "数据字典信息", meta_data, data_dic_rename_map)
                            else:
                                st.info("当前选中字段无 `meta` 数据。")
                        else:
                            st.warning("未找到选中的四级字段的详细信息。")
                    else:
                        st.info("请通过上述下拉列表选择一个四级字段以查看其详细信息。")
            else:
                st.info("请先从 '选择企业文档' 下拉列表选择一个文档。")

@st.fragment
def _render_insert_operation_2(collection):
    st.subheader("➕ 3、插入企业数据")
    with st.expander("➕ 插入企业数据", expanded=False):
        st.markdown("将JSON数据插入到指定企业的文档中。")
        
        # 添加统一社会信用代码输入框
        social_credit_code = st.text_input(
            "企业统一社会信用代码",
            help="输入要更新的企业统一社会信用代码 (例如: 91110000MA01LBCD17)",
            key="insert_social_credit_code_input"
        )
        
        new_doc_str = st.text_area(
            "要插入的 JSON 数据",
            height=200,
            help="输入符合 JSON 格式的数据，将会合并到现有企业文档中。",
            key="insert_doc_input"
        )
        
        # 添加操作选项
        operation_type = st.radio(
            "选择操作类型",
            ["更新现有文档", "创建新文档"],
            help="选择是更新现有企业文档还是创建新的企业文档",
            key="insert_operation_type"
        )
        
        if st.button("执行操作", key="insert_btn"):
            if not social_credit_code.strip():
                st.warning("⚠️ 请输入企业统一社会信用代码。")
                return
                
            if not new_doc_str.strip():
                st.warning("⚠️ 请输入JSON数据。")
                return
                
            with st.spinner("正在处理数据..."):
                time.sleep(1)
                try:
                    # 解析JSON数据
                    doc_data = json.loads(new_doc_str)
                    social_credit_code = social_credit_code.strip()
                    
                    if operation_type == "更新现有文档":
                        # 更新现有文档
                        result = collection.update_one(
                            {"_id": social_credit_code},
                            {"$set": doc_data}
                        )
                        
                        if result.matched_count > 0:
                            if result.modified_count > 0:
                                st.success(f"🎉 更新成功！")
                                st.success(f"✅ 统一社会信用代码: **{social_credit_code}** 的企业档案已更新。")
                                st.info(f"📊 匹配文档数: {result.matched_count}, 修改文档数: {result.modified_count}")
                            else:
                                st.info("📋 文档已存在且数据相同，未进行修改。")
                        else:
                            st.warning("⚠️ 未找到匹配的企业文档。")
                            st.info(f"📋 请检查统一社会信用代码是否正确: `{social_credit_code}`")
                            
                    else:  # 创建新文档
                        # 设置统一社会信用代码作为文档ID
                        doc_data["_id"] = social_credit_code
                        
                        try:
                            result = collection.insert_one(doc_data)
                            st.success(f"🎉 创建成功！")
                            st.success(f"✅ 新企业档案已创建，统一社会信用代码: **{social_credit_code}**")
                        except Exception as insert_error:
                            if "duplicate key" in str(insert_error).lower():
                                st.error(f"❌ 创建失败：企业档案已存在！")
                                st.info(f"📋 统一社会信用代码 `{social_credit_code}` 已被使用，请选择'更新现有文档'选项。")
                            else:
                                raise insert_error
                    st.rerun()
                    
                except json.JSONDecodeError as e:
                    st.error(f"❌ JSON 格式错误：{str(e)}")
                    st.warning("请检查输入的JSON数据格式是否正确。")
                except Exception as e:
                    st.error(f"❌ 操作失败：{str(e)}")
                    # 显示详细错误信息用于调试
                    with st.expander("🔍 查看详细错误信息"):
                        import traceback
                        st.code(traceback.format_exc())

@st.fragment
def _render_insert_operation(collection):
    st.subheader("➕ 3、插入企业数据")
    with st.expander("➕ 插入企业数据", expanded=False):
        st.markdown("将JSON数据插入到指定企业文档的指定层级中。")
        
        # 添加统一社会信用代码输入框
        social_credit_code = st.text_input(
            "企业统一社会信用代码",
            help="输入要更新的企业统一社会信用代码 (例如: 91110000MA01LBCD17)",
            key="insert_social_credit_code_input"
        )
        
        # 选择插入层级
        insert_level = st.selectbox(
            "选择插入层级",
            ["Level1", "Level2", "Level3"],
            help="选择要在哪个层级下插入新的子文档",
            key="insert_level_select"
        )
        
        # 根据选择的层级显示不同的输入框
        if insert_level == "Level1":
            st.markdown("**插入到 Level1 层级** - 直接添加到企业文档的 children 数组中")
            parent_path = "children"
            
        elif insert_level == "Level2":
            st.markdown("**插入到 Level2 层级** - 添加到指定 Level1 节点的 children 数组中")
            level1_name = st.text_input(
                "Level1 节点名称",
                help="输入要插入到的 Level1 节点名称 (例如: 基本信息)",
                key="insert_level1_name"
            )
            parent_path = f"Level1节点: {level1_name}"
            
        else:  # Level3
            st.markdown("**插入到 Level3 层级** - 添加到指定 Level2 节点的 children 数组中")
            level1_name = st.text_input(
                "Level1 节点名称",
                help="输入 Level1 节点名称 (例如: 基本信息)",
                key="insert_level1_name"
            )
            level2_name = st.text_input(
                "Level2 节点名称",
                help="输入要插入到的 Level2 节点名称 (例如: 登记信息)",
                key="insert_level2_name"
            )
            parent_path = f"Level1节点: {level1_name} -> Level2节点: {level2_name}"
        
        st.info(f"📍 插入路径: {parent_path}")
        
        # JSON数据输入
        new_doc_str = st.text_area(
            "要插入的 JSON 数据",
            height=200,
            help="输入符合 JSON 格式的子文档数据",
            key="insert_doc_input",
            placeholder='{\n  "name": "新节点名称",\n  "type": "level2",\n  "children": []\n}'
        )
        
        # 显示不同层级的JSON示例
        with st.expander("📋 JSON 格式示例", expanded=False):
            if insert_level == "Level1":
                st.code('''
{
  "name": "新的Level1节点",
  "type": "level1",
  "children": []
}
                ''', language='json')
            elif insert_level == "Level2":
                st.code('''
{
  "name": "新的Level2节点",
  "type": "level2",
  "children": []
}
                ''', language='json')
            else:  # Level3
                st.code('''
{
  "name": "新的Level3节点",
  "type": "level3",
  "fields": [
    {
      "field_name": "字段名称",
      "remark": "",
      "row_number": 1,
      "data": {
        "value": "字段值",
        "relate_pic": "图片.jpg",
        "relate_doc": "文档.doc"
      }
    }
  ]
}
                ''', language='json')
        
        if st.button("插入数据", key="insert_btn"):
            if not social_credit_code.strip():
                st.warning("⚠️ 请输入企业统一社会信用代码。")
                return
                
            if not new_doc_str.strip():
                st.warning("⚠️ 请输入JSON数据。")
                return
            
            # 检查必填字段
            if insert_level == "Level2" and not level1_name.strip():
                st.warning("⚠️ 请输入Level1节点名称。")
                return
                
            if insert_level == "Level3" and (not level1_name.strip() or not level2_name.strip()):
                st.warning("⚠️ 请输入Level1和Level2节点名称。")
                return
                
            with st.spinner("正在插入数据..."):
                time.sleep(1)
                try:
                    # 解析JSON数据
                    doc_data = json.loads(new_doc_str)
                    social_credit_code = social_credit_code.strip()
                    
                    # 根据层级构建不同的更新操作
                    if insert_level == "Level1":
                        # 直接添加到根级别的children数组
                        update_op = {
                            "$push": {
                                "children": doc_data
                            }
                        }
                        result = collection.update_one(
                            {"_id": social_credit_code},
                            update_op
                        )
                        
                    elif insert_level == "Level2":
                        # 添加到指定Level1节点的children数组
                        update_op = {
                            "$push": {
                                "children.$[level1].children": doc_data
                            }
                        }
                        array_filters = [
                            {"level1.name": level1_name.strip()}
                        ]
                        result = collection.update_one(
                            {"_id": social_credit_code},
                            update_op,
                            array_filters=array_filters
                        )
                        
                    else:  # Level3
                        # 添加到指定Level2节点的children数组
                        update_op = {
                            "$push": {
                                "children.$[level1].children.$[level2].children": doc_data
                            }
                        }
                        array_filters = [
                            {"level1.name": level1_name.strip()},
                            {"level2.name": level2_name.strip()}
                        ]
                        result = collection.update_one(
                            {"_id": social_credit_code},
                            update_op,
                            array_filters=array_filters
                        )
                    
                    # 处理结果
                    if result.matched_count > 0:
                        if result.modified_count > 0:
                            st.success(f"🎉 插入成功!")
                            st.success(f"✅ 已成功插入数据到 **{insert_level}** 层级")
                            st.info(f"📊 企业代码: {social_credit_code}")
                            st.info(f"📍 插入路径: {parent_path}")
                        else:
                            st.warning("⚠️ 未能插入数据，可能是因为找不到指定的父节点。")
                            if insert_level == "Level2":
                                st.info(f"请检查Level1节点名称是否正确: `{level1_name}`")
                            elif insert_level == "Level3":
                                st.info(f"请检查Level1节点名称: `{level1_name}` 和Level2节点名称: `{level2_name}` 是否正确")
                    else:
                        st.warning("⚠️ 未找到匹配的企业文档。")
                        st.info(f"📋 请检查统一社会信用代码是否正确: `{social_credit_code}`")
                    
                    st.rerun()
                    
                except json.JSONDecodeError as e:
                    st.error(f"❌ JSON 格式错误:{str(e)}")
                    st.warning("请检查输入的JSON数据格式是否正确。")
                except Exception as e:
                    st.error(f"❌ 插入失败:{str(e)}")
                    # 显示详细错误信息用于调试
                    with st.expander("🔍 查看详细错误信息"):
                        import traceback
                        st.code(traceback.format_exc())

@st.fragment
def _render_update_operation(collection):
    st.subheader("✏️ 4、更新企业数据")
    with st.expander("✏️ 更新企业数据", expanded=False):
        st.markdown("根据企业统一信用代码和字段名称更新对应字段的值。")
        
        # 基本信息输入
        id_to_update = st.text_input(
            "要更新的文档 EnterpriseCode",
            help="输入要更新文档的 'EnterpriseCode' (例如: 91110000MA01ABCD01)",
            key="update_id_input"
        )
        
        # 字段名称输入
        field_name_to_update = st.text_input(
            "要更新的字段名称",
            help="输入要更新的字段名称 (例如: 统一社会信用代码)",
            key="field_name_input"
        )
        
        # 新值输入
        new_value = st.text_input(
            "新的值",
            help="输入要设置的新值",
            key="new_value_input"
        )
        
        if st.button("更新字段值", key="update_btn"):
            with st.spinner("正在更新文档..."):
                time.sleep(1)
                try:
                    # 使用数组过滤器更新嵌套数组中的特定字段
                    update_op = {
                        "$set": {
                            "children.$[].children.$[].children.$[].fields.$[field].data.value": new_value
                        }
                    }
                    
                    # 数组过滤器，根据 field_name 找到对应的字段
                    array_filters = [
                        {"field.field_name": field_name_to_update}
                    ]
                    
                    result = collection.update_one(
                        {"_id": id_to_update.strip()}, 
                        update_op,
                        array_filters=array_filters
                    )
                    
                    if result.matched_count > 0:
                        if result.modified_count > 0:
                            st.success(f"✅ 更新成功！已更新字段 '{field_name_to_update}' 的值为 '{new_value}'")
                        else:
                            st.warning(f"⚠️ 找到匹配的文档，但未找到字段名称为 '{field_name_to_update}' 的字段，或该字段值未发生变化。")
                        st.rerun()
                    else:
                        st.warning("⚠️ 未找到匹配的文档。请检查 EnterpriseCode 是否正确。")
                        
                except Exception as e:
                    st.error(f"更新失败：`{e}`")

@st.fragment
def _render_delete_operation(collection):
    st.subheader("❌ 5、删除企业数据")
    with st.expander("❌ 删除企业数据", expanded=False):
        st.markdown("根据企业统一社会信用代码删除单个文档。")
        id_to_delete = st.text_input(
            "要删除的统一社会信用代码",
            help="输入要删除企业的统一社会信用代码 (例如: 91110000MA01LBCD17)",
            key="delete_id_input"
        )
        if st.button("删除文档", key="delete_btn"):
            if not id_to_delete.strip():
                st.warning("⚠️ 请输入统一社会信用代码。")
                return
                
            with st.spinner("正在删除文档..."):
                time.sleep(1)
                try:
                    # 直接使用字符串查询，不需要转换为 ObjectId
                    result = collection.delete_one({"_id": id_to_delete.strip()})
                    if result.deleted_count > 0:
                        st.success(f"🗑️ 删除成功！已删除 **{result.deleted_count}** 个文档。")
                        st.success(f"✅ 统一社会信用代码: **{id_to_delete.strip()}** 的企业档案已被删除。")
                        st.rerun()
                    else:
                        st.warning("⚠️ 未找到匹配的文档进行删除。")
                        st.info(f"📋 请检查统一社会信用代码是否正确: `{id_to_delete.strip()}`")
                except Exception as e:
                    st.error(f"❌ 删除失败：{str(e)}")
                    # 显示详细错误信息用于调试
                    with st.expander("🔍 查看详细错误信息"):
                        import traceback
                        st.code(traceback.format_exc())

# --- Main function: Controls page rendering logic and authentication ---
def main():
    """Page main function: controls access permissions and renders content."""
    auth_manager = AuthManager()
    st.title("📇 操作企业档案")
    render_sidebar()
    # Check authentication status
    if not auth_manager.is_authenticated():
        st.error("请先登录才能访问此页面！")
        if st.button("🏠 返回主页",type="primary", key="back_to_main_login_ops"):
            st.switch_page("系统主页.py")
    else:
        apply_custom_css()
        collection = _check_and_connect_mongo()
        # Only render operations if collection is successfully connected
        if collection is not None:
            _render_document_preview(collection)
            st.markdown("---") 
            _render_subdocument_selector(collection)
            st.markdown("---") 
            _render_insert_operation(collection)
            st.markdown("---") 
            _render_update_operation(collection)
            st.markdown("---") 
            _render_delete_operation(collection)

if __name__ == "__main__":
    main()