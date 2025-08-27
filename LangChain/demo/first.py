# LangChain 入门示例：构建一个简单的翻译应用

# 1. 导入必要的模块
import os
import getpass
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate

# 2. 设置API密钥（以MoonShot Gemini为例）
# 如果使用其他模型，请相应调整API密钥设置
if not os.environ.get("MOONSHOT_API_KEY"):
    os.environ["MOONSHOT_API_KEY"] = getpass.getpass("请输入您的MOONSHOT API密钥: ")

# 3. 初始化聊天模型
def setup_model():
    """设置并返回聊天模型"""
    try:
        model = init_chat_model(
            "qwen-plus-2025-07-28", 
            model_provider="openai",
            base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1",
            api_key = "sk-282660fdc8cc4460943f2da2a86d3d01"
        )
        print("✅ 模型初始化成功！")
        return model
    except Exception as e:
        print(f"❌ 模型初始化失败: {e}")
        return None

# 4. 基础使用：直接调用模型
def basic_chat_example(model):
    """基础聊天示例"""
    print("\n=== 基础聊天示例 ===")
    
    # 创建消息
    messages = [
        SystemMessage("你是一个有用的AI助手。"),
        HumanMessage("你好！请介绍一下自己。")
    ]
    
    # 调用模型
    response = model.invoke(messages)
    print(f"AI回复: {response.content}")

# 5. 使用提示模板构建翻译应用
def translation_app_example(model):
    """翻译应用示例"""
    print("\n=== 翻译应用示例 ===")
    
    # 创建提示模板
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", "你是一个专业的翻译助手。请将以下文本从{source_language}翻译成{target_language}。"),
        ("human", "{text}")
    ])
    
    # 创建翻译链
    translation_chain = prompt_template | model
    
    # 测试翻译
    result = translation_chain.invoke({
        "source_language": "中文",
        "target_language": "英文", 
        "text": "今天天气很好，我们去公园散步吧。"
    })
    
    print(f"翻译结果: {result.content}")

# 6. 流式输出示例
def streaming_example(model):
    """流式输出示例"""
    print("\n=== 流式输出示例 ===")
    
    messages = [
        SystemMessage("你是一个创意写作助手。"),
        HumanMessage("请写一个关于人工智能的短故事，大约100字。")
    ]
    
    print("AI正在生成故事...")
    for chunk in model.stream(messages):
        print(chunk.content, end="", flush=True)
    print("\n")

# 7. 批量处理示例
def batch_processing_example(model):
    """批量处理示例"""
    print("\n=== 批量处理示例 ===")
    
    # 准备多个翻译任务
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", "请将以下文本翻译成英文："),
        ("human", "{text}")
    ])
    
    chain = prompt_template | model
    
    # 批量翻译
    texts = [
        {"text": "早上好！"},
        {"text": "谢谢你的帮助。"},
        {"text": "今天是星期一。"}
    ]
    
    results = chain.batch(texts)
    
    for i, result in enumerate(results):
        print(f"原文: {texts[i]['text']} -> 译文: {result.content}")

# 8. 错误处理示例
def error_handling_example():
    """错误处理示例"""
    print("\n=== 错误处理示例 ===")
    
    try:
        # 尝试使用错误的API密钥
        model = init_chat_model("gpt-4", model_provider="openai")
        response = model.invoke([HumanMessage("Hello")])
        print(f"响应: {response.content}")
    except Exception as e:
        print(f"捕获到错误: {e}")
        print("提示：请检查API密钥是否正确设置")

# 9. 主函数
def main():
    """主函数 - 运行所有示例"""
    print("🚀 欢迎使用LangChain入门教程！")
    print("=" * 50)
    
    # 设置模型
    model = setup_model()
    if not model:
        print("❌ 无法初始化模型，程序退出")
        return
    
    # 运行各种示例
    basic_chat_example(model)
    translation_app_example(model)
    streaming_example(model)
    batch_processing_example(model)
    error_handling_example()
    
    print("\n🎉 教程完成！")
    print("接下来您可以：")
    print("1. 尝试不同的模型提供商（OpenAI、Anthropic等）")
    print("2. 学习RAG（检索增强生成）")
    print("3. 探索LangGraph构建复杂的代理")
    print("4. 使用LangSmith进行应用监控")

# 10. 实用工具函数
def check_dependencies():
    """检查依赖是否安装完整"""
    print("\n=== 依赖检查 ===")
    
    required_packages = [
        'langchain',
        'langchain_core',
        'langchain_community'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} 已安装")
        except ImportError:
            print(f"❌ {package} 未安装")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n请安装缺失的包：")
        for package in missing_packages:
            print(f"pip install {package}")
    else:
        print("\n🎉 所有依赖都已正确安装！")

if __name__ == "__main__":
    # 检查依赖
    check_dependencies()
    
    # 运行主程序
    main()