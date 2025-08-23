from nicegui import ui , app
from typing import Optional, List, Dict, Any

TEST_RESULT = {
    "type": "汇总",
    "period": "3.79 ms",
    "messages": "正常处理",
    "result_data": [
        {"_id": 1, "name": "企业 A", "capital": 1000000},
        {"_id": 2, "name": "企业 B", "capital": 2000000},
        {"_id": 3, "name": "企业 C", "capital": 3000000},
    ]
}

@ui.page("/")
def display_query_statistics():
        """
        显示查询统计信息
        
        Args:
            result: MongoDB查询结果字典
        """
        result = TEST_RESULT
        result_data = result.get('result_data', [])
        data_count = len(result_data) if isinstance(result_data, list) else 1
        
        stats_text = (
            f"<b>📊 查询统计:</b>\n"
            f"•<b>查询类型</b>:{result.get('type', 'N/A')} &nbsp;&nbsp;&nbsp;&nbsp; •<b>运行耗时</b>: {result.get('period', '0ms')} &nbsp;&nbsp;&nbsp;&nbsp; •<b>处理信息</b>: {result.get('messages', '未知')} &nbsp;&nbsp;&nbsp;&nbsp; •<b>数据数量</b>: {data_count}"
        )
        ui.html(stats_text).classes(
            'whitespace-pre-wrap w-full text-base bg-blue-50 border-l-4 border-blue-500 p-3 mb-2'
        )

if __name__ in {"__main__", "__mp_main__"}:
    ui.run(title="NiceGUI 全局数据演示", 
            port=8280,
            reload=True,
            prod_js=False,
            show=True)