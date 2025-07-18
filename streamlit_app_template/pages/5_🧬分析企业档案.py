import streamlit as st
import pandas as pd
from openai import OpenAI
from pymongo import MongoClient
from bson.objectid import ObjectId
import re
import sys
import os

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
from system_prompt import PROMPT_TEMPLATES


from utils import apply_custom_css
from 系统主页 import AuthManager, render_sidebar
st.set_page_config(page_title="分析政务集合数据", page_icon="🧬", layout="wide")

def process_response_with_think(response_text):
    """
    处理包含<think>标签的响应内容
    将思考内容放在可折叠的expander中
    """
    # 使用正则表达式匹配<think>内容
    think_pattern = r'<think>(.*?)</think>'
    think_matches = re.findall(think_pattern, response_text, re.DOTALL)
    if think_matches:
        # 移除原始响应中的<think>标签内容
        clean_response = re.sub(think_pattern, '', response_text, flags=re.DOTALL).strip()
        # 显示思考内容（折叠状态）
        with st.expander("🤔 查看模型思考过程", expanded=False):
            for i, think_content in enumerate(think_matches):
                if len(think_matches) > 1:
                    st.markdown(f"**思考片段 {i+1}:**")
                st.markdown(think_content.strip())
                if i < len(think_matches) - 1:
                    st.divider()
        
        # 显示清理后的响应内容
        if clean_response:
            st.markdown(clean_response)
        return clean_response
    else:
        # 没有思考内容，直接显示
        st.markdown(response_text)
        return response_text

def config_section():
    with st.sidebar:
        st.title("模型配置")
        # 提示词模板选择
        # st.subheader("系统提示词")
        template_names = list(PROMPT_TEMPLATES.keys())
        selected_template_name = st.selectbox(
            "选择提示词模板:",
            template_names,
            index=0,
            help="选择不同的提示词模板来改变AI的回答风格"
        )
        # 存储选择的模板到session_state
        st.session_state["selected_template_name"] = selected_template_name
        st.session_state["selected_template_content"] = PROMPT_TEMPLATES[selected_template_name]["content"]
        # 模型选择下拉列表
        # st.subheader("模型选择")
        model_options = [
            "moonshot-v1-8k",
            "moonshot-v1-32k", 
            "deepseek-chat",
            "deepseek-r1:8b",
            "deepseek-r1:14b",
            "deepseek-r1:32b",
            "deepseek-r1:671b",
            "qwen2.5:latest",
            "qwen3:8b",
            "qwen3:32b",
            "qwen2.5:14b",
            "qwen2.5:32b",
            "qwen2.5:72b"
        ]
        selected_model = st.selectbox("选择模型:",model_options,index=0)
        # 添加分隔线
        st.divider()
        
        # 模型参数配置
        st.subheader("模型参数") 
        temperature = st.slider(
            "Temperature (温度)",
            min_value=0.0,
            max_value=2.0,
            value=0.7,
            step=0.1,
            help="控制生成文本的随机性。值越高，生成的文本越随机；值越低，生成的文本越确定。"
        )
        
        top_p = st.slider(
            "Top-p (核采样)",
            min_value=0.0,
            max_value=1.0,
            value=0.9,
            step=0.05,
            help="控制生成时考虑的词汇范围。值越小，生成的文本越集中于高概率词汇。"
        )
        
        # 添加分隔线
        st.divider()
        
        # 清除按钮
        if st.button("清除聊天记录", key="clear_chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
    
    # 根据选择的模型确定API配置
    if selected_model in ["moonshot-v1-8k", "moonshot-v1-32k"]:
        api_key = st.secrets["MOONSHOT_API_KEY"]
        base_url = st.secrets["MOONSHOT_BASE_URL"]
    elif selected_model == "deepseek-chat":
        api_key = st.secrets["DEEPSEEK_API_KEY"]
        base_url = st.secrets["DEEPSEEK_BASE_URL"]
    else:  # deepseek-r1系列和qwen系列
        api_key = st.secrets["LOCAL_API_KEY"]
        base_url = st.secrets["LOCAL_BASE_URL"]
    
    # 创建OpenAI Client
    client = OpenAI(
        api_key=api_key,
        base_url=base_url
    )
    
    # 设置session state
    st.session_state["openai_model"] = selected_model
    st.session_state["temperature"] = temperature
    st.session_state["top_p"] = top_p
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.messages.append({"role": "assistant", "content": "🎉🎉欢迎使用智能问答！！您可以先选择提示模板，然后再进行对话。"})
    
    return client

def make_api_request_with_system_prompt(client, messages, system_content):
    """
    使用系统提示词发起API请求
    """
    # 构建包含系统消息的消息列表
    api_messages = []
    
    # 添加系统消息（如果有内容）
    if system_content:
        api_messages.append({"role": "system", "content": system_content})
    
    # 添加用户和助手的历史消息
    api_messages.extend([
        {"role": m["role"], "content": m["content"]} 
        for m in messages
    ])
    
    # 发起API请求
    stream = client.chat.completions.create(
        model=st.session_state["openai_model"],
        messages=api_messages,
        temperature=st.session_state.get("temperature", 0.7),
        top_p=st.session_state.get("top_p", 0.9),
        stream=True
    )
    
    return stream

def make_api_request_default(client, messages):
    """
    不使用系统提示词的默认API请求
    """
    stream = client.chat.completions.create(
        model=st.session_state["openai_model"],
        messages=[
            {"role": m["role"], "content": m["content"]} 
            for m in messages
        ],
        temperature=st.session_state.get("temperature", 0.7),
        top_p=st.session_state.get("top_p", 0.9),
        stream=True
    )
    return stream

# ---------------------------------------------------------------------
def make_mongodb_request(client, messages):
    """
    处理一企一档助手的MongoDB查询请求
    1. 先让大模型生成MongoDB查询语句
    2. 执行查询获取数据
    3. 将结果提交给大模型进行分析和总结
    """
    from pymongo import MongoClient
    from bson.json_util import dumps
    import streamlit as st
    import re
    import json
    
    # 第一步：生成MongoDB查询语句
    try:
        # 构建生成查询语句的消息
        query_messages = []
        # 从session_state中获取选择的提示词模板
        system_content = st.session_state.get('selected_template_content', '')
        if system_content:
            query_messages.append({"role": "system", "content": system_content})
        # 添加历史对话
        query_messages.extend([
            {"role": m["role"], "content": m["content"]} 
            for m in messages
        ])
        # 请求大模型生成查询语句
        query_stream = client.chat.completions.create(
            model=st.session_state["openai_model"],
            messages=query_messages,
            temperature=0.1,  # 使用较低温度确保查询语句准确
            top_p=0.8,
            stream=False  # 不使用流式，确保完整获取查询语句
        )
        
        # 获取生成的查询语句
        mongo_query = query_stream.choices[0].message.content.strip() 
        # 清理查询语句，移除可能的代码块标记
        if mongo_query.startswith('```'):
            lines = mongo_query.split('\n')
            mongo_query = '\n'.join([line for line in lines if not line.startswith('```')])
        
        # 第二步：连接MongoDB并执行查询
        try:
            # 连接MongoDB数据库
            mongo_client = MongoClient("mongodb://localhost:27017/")
            db = mongo_client["数字政府"]
            collection = db["一企一档"]
            # 为了安全起见，我们解析常见的查询模式
            query_result = None    
            
            if "find(" in mongo_query:
                # 处理find查询
                query_result = _handle_find_query(collection, mongo_query)
                
            elif "aggregate(" in mongo_query:
                # 处理聚合查询
                query_result = _handle_aggregate_query(collection, mongo_query)
                
            elif "count(" in mongo_query or "countDocuments(" in mongo_query:
                # 处理计数查询
                query_result = _handle_count_query(collection, mongo_query)
                
            elif "distinct(" in mongo_query:
                # 处理distinct查询
                query_result = _handle_distinct_query(collection, mongo_query)
                
            else:
                # 默认查询
                query_result = list(collection.find({}).limit(3))
            print("查询结果:", query_result)
            # 关闭数据库连接
            mongo_client.close()
            
            # 调试输出：显示查询结果
            if isinstance(query_result, dict) and "error" in query_result:
                st.error(f"❌ 数据库查询错误：{query_result['error']}")
            else:
                result_preview = dumps(query_result, indent=2, ensure_ascii=False)
                if len(result_preview) > 1000:
                    result_preview = result_preview[:1000] + "\n...(预览已截断)"
                result_count = len(query_result) if isinstance(query_result, list) else 1
                st.success(f"✅ 查询成功，返回 {result_count} 条记录")
                
        except Exception as db_error:
            query_result = {"error": f"数据库查询错误: {str(db_error)}"}
            st.error(f"❌ 数据库连接或查询失败：{str(db_error)}")
        # 第三步：将查询结果提交给大模型进行分析
        return _analyze_query_result(client, messages, query_result)
    
    except Exception as e:
        # 处理整体错误
        error_message = f"处理MongoDB请求时发生错误：{str(e)}"
        return _create_mock_stream(error_message)

def _handle_find_query(collection, mongo_query):
    """处理find查询"""
    import re
    try:
        # 提取find()中的查询条件和投影
        find_pattern = r'find\s*\(\s*({[^}]*}|[^,)]*)\s*(?:,\s*({[^}]*}))?\s*\)'
        match = re.search(find_pattern, mongo_query)
        # cmd_str=validate_and_fix_json(match)
        if match:
            query_dict_str = match.group(1).strip()
            projection_str = match.group(2).strip() if match.group(2) else None
            
            # 解析查询条件
            query_dict = {}
            if query_dict_str and query_dict_str != '{}':
                query_dict = _safe_eval_query(query_dict_str)
            
            # 解析投影
            projection = None
            if projection_str and projection_str != '{}':
                projection = _safe_eval_query(projection_str)
            
            # 执行查询
            cursor = collection.find(query_dict, projection).limit(20)
            return list(cursor)
        else:
            # 如果没有匹配到find模式，尝试简单查询
            return list(collection.find({}).limit(5))
            
    except Exception as e:
        return {"error": f"find查询解析错误: {str(e)}"}

def _handle_aggregate_query(collection, mongo_query):
    """处理聚合查询"""
    import re
    
    try:
        # 提取aggregate()中的管道操作
        # 匹配 aggregate([...]) 或 aggregate( [...] )
        aggregate_pattern = r'aggregate\s*\(\s*(\[.*?\])\s*\)'
        match = re.search(aggregate_pattern, mongo_query, re.DOTALL)
        
        if match:
            pipeline_str = match.group(1).strip()
            
            # 安全解析聚合管道
            try:
                pipeline = _safe_eval_pipeline(pipeline_str)
                # 执行聚合查询，限制结果数量
                cursor = collection.aggregate(pipeline)
                result = list(cursor)
                # 限制返回结果数量
                if len(result) > 50:
                    result = result[:50]
                    result.append({"_info": f"结果已截断，实际返回前50条记录"})
                
                return result
                
            except Exception as parse_error:
                return {"error": f"聚合管道解析错误: {str(parse_error)}"}
        else:
            return {"error": "无法解析聚合查询语法"}
            
    except Exception as e:
        return {"error": f"聚合查询执行错误: {str(e)}"}

def _handle_count_query(collection, mongo_query):
    """处理计数查询"""
    import re
    try:
        # 提取count或countDocuments中的查询条件
        count_pattern = r'(?:count|countDocuments)\s*\(\s*({[^}]*}|[^)]*)?\s*\)'
        match = re.search(count_pattern, mongo_query)
        
        if match:
            query_dict_str = match.group(1).strip() if match.group(1) else '{}'
            
            # 解析查询条件
            query_dict = {}
            if query_dict_str:
                query_dict = _safe_eval_query(query_dict_str)
            
            # 执行计数
            count = collection.count_documents(query_dict)
            return [{"count": count, "_query": query_dict}]
        else:
            # 默认计数
            count = collection.count_documents({})
            return [{"count": count, "_query": {}}]
            
    except Exception as e:
        return {"error": f"计数查询错误: {str(e)}"}

def _handle_distinct_query(collection, mongo_query):
    """处理distinct查询"""
    import re
    
    try:
        # 提取distinct中的字段和查询条件
        distinct_pattern = r'distinct\s*\(\s*["\']([^"\']+)["\']\s*(?:,\s*({[^}]*}))?\s*\)'
        match = re.search(distinct_pattern, mongo_query)
        
        if match:
            field = match.group(1)
            query_dict_str = match.group(2).strip() if match.group(2) else '{}'
            
            # 解析查询条件
            query_dict = {}
            if query_dict_str and query_dict_str != '{}':
                query_dict = _safe_eval_query(query_dict_str)
            
            # 执行distinct查询
            distinct_values = collection.distinct(field, query_dict)
            
            # 限制返回结果数量
            if len(distinct_values) > 100:
                distinct_values = distinct_values[:100]
                result = [{"distinct_values": distinct_values, "_field": field, "_truncated": True}]
            else:
                result = [{"distinct_values": distinct_values, "_field": field}]
            
            return result
        else:
            return {"error": "无法解析distinct查询语法"}
            
    except Exception as e:
        return {"error": f"distinct查询错误: {str(e)}"}

def _safe_eval_query(query_str):
    """安全解析查询字符串"""
    import json
    
    try:
        # 首先尝试JSON解析
        return json.loads(query_str)
    except json.JSONDecodeError:
        try:
            # 如果JSON解析失败，尝试eval（仅限安全的字典表达式）
            if query_str.strip().startswith('{') and query_str.strip().endswith('}'):
                # 基本的安全检查
                dangerous_keywords = ['import', 'exec', 'eval', '__', 'open', 'file']
                if not any(keyword in query_str.lower() for keyword in dangerous_keywords):
                    return eval(query_str)
            raise ValueError("不安全的查询表达式")
        except:
            raise ValueError(f"无法解析查询条件: {query_str}")

def _safe_eval_pipeline(pipeline_str):
    """安全解析聚合管道"""
    import json
    
    try:
        # 首先尝试JSON解析
        return json.loads(pipeline_str)
    except json.JSONDecodeError:
        try:
            # 如果JSON解析失败，尝试eval
            if pipeline_str.strip().startswith('[') and pipeline_str.strip().endswith(']'):
                # 基本的安全检查
                dangerous_keywords = ['import', 'exec', 'eval', '__', 'open', 'file']
                if not any(keyword in pipeline_str.lower() for keyword in dangerous_keywords):
                    return eval(pipeline_str)
            raise ValueError("不安全的管道表达式")
        except:
            raise ValueError(f"无法解析聚合管道: {pipeline_str}")

def _analyze_query_result(client, messages, query_result):
    """分析查询结果"""
    import streamlit as st
    from bson.json_util import dumps
    
    if query_result:
        # 将查询结果转换为JSON字符串
        if isinstance(query_result, dict) and "error" in query_result:
            result_text = f"查询出现错误：{query_result['error']}"
        else:
            # 使用bson.json_util.dumps来处理MongoDB的特殊类型
            result_text = dumps(query_result, indent=2, ensure_ascii=False) 
            # 如果结果太长，进行截断
            if len(result_text) > 5000:
                result_text = result_text[:5000] + "\n...(结果已截断，显示前5000字符)"
        
        # 构建分析请求的消息
        analysis_messages = []
        # 添加分析系统提示词
        analysis_system_prompt = """你是一个专业的数据分析助手。用户刚刚执行了一个MongoDB查询，现在需要你对查询结果进行分析和总结。
                            请根据查询结果：
                            1. 结合用户的原始问题，分析数据的关键特征
                            2. 最好能以markdown表格呈现结果
                            3. 如果数据有异常或问题，请指出
                            请用简洁清晰的语言进行分析，重点突出对用户有价值的信息。"""
        
        analysis_messages.append({"role": "system", "content": analysis_system_prompt})
        # 添加用户的原始问题（最后一条用户消息）
        user_question = messages[-1]["content"] if messages and messages[-1]["role"] == "user" else "请分析以下数据"
        print("user question:", user_question)
        # 构建包含查询结果的消息
        analysis_content = f"""用户问题：{user_question}
        查询结果：
        {result_text}
        请基于以上查询结果回答用户的问题并进行分析总结。"""
        
        analysis_messages.append({"role": "user", "content": analysis_content})
        
        # 请求大模型进行分析
        analysis_stream = client.chat.completions.create(
            model=st.session_state["openai_model"],
            messages=analysis_messages,
            temperature=st.session_state.get("temperature", 0.7),
            top_p=st.session_state.get("top_p", 0.9),
            stream=True
        )
        return analysis_stream
        
    else:
        # 如果没有查询结果，返回错误信息
        error_message = "很抱歉，查询没有返回任何结果。请检查查询条件或数据库连接。"
        return _create_mock_stream(error_message)

def _create_mock_stream(content):
    """创建模拟的流式响应"""
    class MockStream:
        def __init__(self, content):
            self.content = content
            self.sent = False
        
        def __iter__(self):
            return self
        
        def __next__(self):
            if not self.sent:
                self.sent = True
                from types import SimpleNamespace
                choice = SimpleNamespace()
                choice.delta = SimpleNamespace()
                choice.delta.content = self.content
                chunk = SimpleNamespace()
                chunk.choices = [choice]
                return chunk
            else:
                raise StopIteration
    
    return MockStream(content)
# ---------------------------------------------------------------------

# @st.fragment
def chatbot_section(client):
    st.subheader("智能问数")
    current_template = st.session_state.get('selected_template_name', '默认')
    st.caption(f"当前模型: {st.session_state.get('openai_model', 'N/A')} | "
              f"提示词模板: {current_template} | "
              f"Temperature: {st.session_state.get('temperature', 0.7)} | "
              f"Top-p: {st.session_state.get('top_p', 0.9)}")
    # 显示聊天历史
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if message["role"] == "assistant":
                # 对助手消息进行<think>标签处理
                process_response_with_think(message["content"])
            else:
                st.markdown(message["content"])  
    if prompt := st.chat_input("请输入问题....."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
            
        # 生成AI响应
        with st.chat_message("assistant"):
            try:
                with st.spinner(f"正在使用 {st.session_state['openai_model']} 生成回复..."):
                    # 创建一个占位符来显示响应
                    response_placeholder = st.empty()   
                    # 根据选择的模板类型发起不同的API请求
                    template_name = st.session_state.get('selected_template_name', '默认')
                    template_content = st.session_state.get('selected_template_content', '')
                    
                    if template_name == "默认" or not template_content:
                        stream = make_api_request_default(client, st.session_state.messages)
                    elif template_name == "一企一档助手" or template_name == "一企一档助手2":
                        stream = make_mongodb_request(client,st.session_state.messages)
                    else:
                        # 使用系统提示词
                        stream = make_api_request_with_system_prompt(
                            client, 
                            st.session_state.messages, 
                            template_content
                        )
                    # 收集完整的响应
                    full_response = ""
                    for chunk in stream:
                        if chunk.choices[0].delta.content is not None:
                            full_response += chunk.choices[0].delta.content
                            # 实时显示内容（暂时不处理think标签）
                            response_placeholder.markdown(full_response)  
                
                # 响应完成后，处理<think>标签
                response_placeholder.empty()  # 清空占位符
                process_response_with_think(full_response)
                
                # 保存原始响应到session state
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                
            except Exception as e:
                error_msg = f"错误: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

def main():
    auth_manager = AuthManager()
    st.title("🧬 分析企业档案")
    if not auth_manager.is_authenticated():
        st.error("请先登录才能访问此页面！")
        if st.button("🏠 返回主页",type="primary", key="back_to_main_login_ops"):
            st.switch_page("系统主页.py")
    else:
        apply_custom_css()
        st.set_page_config(page_title="智能问数", layout="wide")
        client = config_section()
        chatbot_section(client)

if __name__ == "__main__":
    main()