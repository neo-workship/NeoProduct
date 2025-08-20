import json
import re
from datetime import datetime, timezone
from bson import ObjectId, Regex
from typing import Any, Dict, List, Optional, Tuple, Union
import ast


def _fix_query_syntax(query_cmd: str) -> str:
    """
    修复查询语句的语法问题 - 改进版
    专门处理 MongoDB JavaScript 语法转换为 Python 兼容格式
    
    Args:
        query_cmd: 原始查询命令
        
    Returns:
        修复后的查询命令
    """
    # 移除前后空白字符
    fixed_query = query_cmd.strip()
    
    # 1. 处理 ObjectId 函数调用
    fixed_query = re.sub(r'ObjectId\s*\(\s*["\']([^"\']+)["\']\s*\)', 
                        r'{"$oid": "\1"}', fixed_query)
    
    # 2. 处理 ISODate 函数调用
    fixed_query = re.sub(r'ISODate\s*\(\s*["\']([^"\']+)["\']\s*\)', 
                        r'{"$date": "\1"}', fixed_query)
    
    # 3. 处理正则表达式 /pattern/flags
    fixed_query = re.sub(r'/([^/]+)/([gimx]*)', 
                        r'{"$regex": "\1", "$options": "\2"}', fixed_query)
    
    # 4. 处理 JavaScript 的 true/false/null
    fixed_query = re.sub(r'\btrue\b', 'true', fixed_query)
    fixed_query = re.sub(r'\bfalse\b', 'false', fixed_query)
    fixed_query = re.sub(r'\bnull\b', 'null', fixed_query)
    
    # 5. 处理未加引号的字段名和键名
    # 匹配 {key: value} 或 key: value 格式，为 key 添加引号
    fixed_query = re.sub(r'([{,]\s*)([a-zA-Z_$][a-zA-Z0-9_$]*)\s*:', 
                        r'\1"\2":', fixed_query)
    
    # 6. 处理单引号转双引号
    fixed_query = re.sub(r"'([^']*)'", r'"\1"', fixed_query)
    
    # 7. 处理 JavaScript 注释
    fixed_query = re.sub(r'//.*$', '', fixed_query, flags=re.MULTILINE)
    fixed_query = re.sub(r'/\*.*?\*/', '', fixed_query, flags=re.DOTALL)
    
    # 8. 修复缺失的括号
    open_brackets = fixed_query.count('(')
    close_brackets = fixed_query.count(')')
    if open_brackets > close_brackets:
        fixed_query += ')' * (open_brackets - close_brackets)
    
    open_braces = fixed_query.count('{')
    close_braces = fixed_query.count('}')
    if open_braces > close_braces:
        fixed_query += '}' * (open_braces - close_braces)
    
    open_squares = fixed_query.count('[')
    close_squares = fixed_query.count(']')
    if open_squares > close_squares:
        fixed_query += ']' * (open_squares - close_squares)
    
    print(f"--> fixed_query: {fixed_query}")
    return fixed_query


def _convert_js_to_python_value(value: Any) -> Any:
    """
    递归转换 JavaScript 风格的值为 Python/MongoDB 兼容的值
    
    Args:
        value: JavaScript 风格的值
        
    Returns:
        Python/MongoDB 兼容的值
    """
    if isinstance(value, dict):
        # 处理特殊的 MongoDB 类型标记
        if "$oid" in value:
            return ObjectId(value["$oid"])
        elif "$date" in value:
            return datetime.fromisoformat(value["$date"].replace('Z', '+00:00'))
        elif "$regex" in value:
            options = value.get("$options", "")
            flags = 0
            if 'i' in options:
                flags |= re.IGNORECASE
            if 'm' in options:
                flags |= re.MULTILINE
            if 's' in options:
                flags |= re.DOTALL
            return Regex(value["$regex"], flags)
        else:
            # 递归处理字典中的值
            return {k: _convert_js_to_python_value(v) for k, v in value.items()}
    
    elif isinstance(value, list):
        # 递归处理列表中的值
        return [_convert_js_to_python_value(item) for item in value]
    
    else:
        # 基本类型直接返回
        return value


def _safe_json_loads(json_str: str) -> Any:
    """
    安全的 JSON 解析，支持 MongoDB JavaScript 语法
    
    Args:
        json_str: JSON 字符串
        
    Returns:
        解析后的 Python 对象
    """
    try:
        # 首先尝试标准 JSON 解析
        parsed = json.loads(json_str)
        return _convert_js_to_python_value(parsed)
    except json.JSONDecodeError as e:
        print(f"JSON 解析失败: {e}, 尝试替代方案")
        
        # 如果标准 JSON 解析失败，尝试使用 ast.literal_eval
        # 但首先需要将一些 JavaScript 语法转换为 Python 语法
        try:
            # 将 JavaScript 的 true/false/null 转换为 Python 的 True/False/None
            python_str = json_str.replace('true', 'True').replace('false', 'False').replace('null', 'None')
            parsed = ast.literal_eval(python_str)
            return _convert_js_to_python_value(parsed)
        except (ValueError, SyntaxError) as e2:
            print(f"AST 解析也失败: {e2}")
            # 如果都失败了，返回空字典或空列表
            stripped = json_str.strip()
            if stripped.startswith('['):
                return []
            else:
                return {}


def _parse_query_parameters(query_cmd: str, query_type: str) -> Tuple[Optional[str], Dict[str, Any]]:
    """
    解析查询参数 - 改进版
    专门处理 MongoDB 的 aggregate pipeline 参数
    
    Args:
        query_cmd: 查询命令
        query_type: 查询类型
        
    Returns:
        (集合名(始终返回None), 查询参数字典)
    """
    collection_name = None  # 使用配置的默认集合
    
    try:
        if query_type in ["find", "findOne"]:
            # 提取 find/findOne 的参数
            pattern = rf'\.{query_type}\s*\((.*)\)'
            match = re.search(pattern, query_cmd, re.DOTALL)
            if match:
                params_str = match.group(1).strip()
                if params_str:
                    try:
                        # 处理多个参数的情况：filter, projection, options
                        # 简单解析：按逗号分割，但要考虑嵌套结构
                        params = _split_params(params_str)
                        filter_dict = _safe_json_loads(params[0]) if params else {}
                        
                        result = {"filter": filter_dict}
                        
                        # 如果有第二个参数（projection）
                        if len(params) > 1 and params[1].strip():
                            projection = _safe_json_loads(params[1])
                            result["projection"] = projection
                            
                        return collection_name, result
                    except Exception as e:
                        print(f"解析 find/findOne 参数失败: {e}")
                        return collection_name, {"filter": {}}
                else:
                    return collection_name, {"filter": {}}
        
        elif query_type == "aggregate":
            # 重点改进：提取 aggregate 的 pipeline 参数
            pattern = r'\.aggregate\s*\((.*)\)'
            match = re.search(pattern, query_cmd, re.DOTALL)
            if match:
                params_str = match.group(1).strip()
                if params_str:
                    try:
                        # pipeline 应该是一个数组
                        pipeline = _safe_json_loads(params_str)
                        
                        # 确保 pipeline 是列表格式
                        if not isinstance(pipeline, list):
                            # 如果不是列表，可能是单个 stage，包装成列表
                            pipeline = [pipeline] if pipeline else []
                        
                        # 转换每个 stage 中的特殊值
                        converted_pipeline = []
                        for stage in pipeline:
                            converted_stage = _convert_js_to_python_value(stage)
                            converted_pipeline.append(converted_stage)
                        
                        print(f"解析到的 pipeline: {converted_pipeline}")
                        return collection_name, {"pipeline": converted_pipeline}
                        
                    except Exception as e:
                        print(f"解析 aggregate pipeline 失败: {e}")
                        print(f"原始参数: {params_str}")
                        return collection_name, {"pipeline": []}
                else:
                    return collection_name, {"pipeline": []}
        
        elif query_type in ["count", "countDocuments"]:
            # 提取 count/countDocuments 的参数
            if query_type == "countDocuments":
                pattern = r'\.countDocuments\s*\((.*)\)'
            else:
                pattern = r'\.count\s*\((.*)\)'
                
            match = re.search(pattern, query_cmd, re.DOTALL)
            if match:
                params_str = match.group(1).strip()
                if params_str:
                    try:
                        filter_dict = _safe_json_loads(params_str)
                        return collection_name, {"filter": filter_dict}
                    except Exception as e:
                        print(f"解析 count 参数失败: {e}")
                        return collection_name, {"filter": {}}
                else:
                    return collection_name, {"filter": {}}
        
        elif query_type == "distinct":
            # 提取 distinct 的参数
            pattern = r'\.distinct\s*\((.*)\)'
            match = re.search(pattern, query_cmd, re.DOTALL)
            if match:
                params_str = match.group(1).strip()
                try:
                    # distinct 参数格式：field, filter
                    params = _split_params(params_str)
                    
                    # 第一个参数是字段名
                    field_name = params[0].strip(' "\'') if params else ""
                    
                    # 第二个参数是过滤条件（可选）
                    filter_dict = {}
                    if len(params) > 1 and params[1].strip():
                        filter_dict = _safe_json_loads(params[1])
                    
                    return collection_name, {"field": field_name, "filter": filter_dict}
                    
                except Exception as e:
                    print(f"解析 distinct 参数失败: {e}")
                    return collection_name, {"field": "", "filter": {}}
        
        return collection_name, {}
        
    except Exception as e:
        print(f"解析查询参数失败: {e}")
        return collection_name, {}


def _split_params(params_str: str) -> List[str]:
    """
    智能分割参数字符串，考虑嵌套的括号和引号
    
    Args:
        params_str: 参数字符串
        
    Returns:
        参数列表
    """
    params = []
    current_param = ""
    depth = 0
    in_string = False
    string_char = None
    
    for i, char in enumerate(params_str):
        if char in ['"', "'"] and (i == 0 or params_str[i-1] != '\\'):
            if not in_string:
                in_string = True
                string_char = char
            elif char == string_char:
                in_string = False
                string_char = None
        
        if not in_string:
            if char in ['{', '[', '(']:
                depth += 1
            elif char in ['}', ']', ')']:
                depth -= 1
            elif char == ',' and depth == 0:
                params.append(current_param.strip())
                current_param = ""
                continue
        
        current_param += char
    
    if current_param.strip():
        params.append(current_param.strip())
    
    return params


# 使用示例和测试
def test_pipeline_parsing():
    """测试 pipeline 解析功能"""
    
    test_cases = [
        # 基本聚合查询
        'db.collection.aggregate([{"$match": {"status": "active"}}, {"$group": {"_id": "$category", "count": {"$sum": 1}}}])',
        
        # 包含 ObjectId 的查询
        'db.collection.aggregate([{"$match": {"_id": ObjectId("507f1f77bcf86cd799439011")}}, {"$project": {"name": 1}}])',
        
        # 包含日期的查询
        'db.collection.aggregate([{"$match": {"createdAt": {"$gte": ISODate("2023-01-01T00:00:00.000Z")}}}, {"$sort": {"createdAt": -1}}])',
        
        # 包含正则表达式的查询
        'db.collection.aggregate([{"$match": {"name": /^test/i}}, {"$count": "total"}])',
        
        # 复杂的聚合管道
        '''db.collection.aggregate([
            {
                $unwind: "$fields"
            },
            {
                $match: {
                "fields.path_code": "L19E5FFA.L279A000.L336E6A6",
                "fields.field_code": { $in: ["FB17AB0"] }
                }
            },
            {
                $replaceRoot: {
                newRoot: "$fields"
                }
            }
        ])'''

        """
        db.getCollection('一企一档').aggregate([
        {
            $unwind: "$fields"
        },
        {
            $match: {
            "fields.path_code": "L19E5FFA.L279A000.L336E6A6",
            "fields.field_code": { $in: ["FB17AB0"] }
            }
        },
        {
            $replaceRoot: {
            newRoot: 22
            }
        }
        ])
        """
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n=== 测试用例 {i} ===")
        print(f"原始查询: {test_case}")
        
        # 修复语法
        fixed_query = _fix_query_syntax(test_case)
        print(f"修复后: {fixed_query}")
        
        # 解析查询类型
        query_type = _parse_query_type(fixed_query)
        print(f"查询类型: {query_type}")
        
        # 解析参数
        _, params = _parse_query_parameters(fixed_query, query_type)
        print(f"解析参数: {params}")
        
        # 检查 pipeline 类型
        if "pipeline" in params:
            pipeline = params["pipeline"]
            print(f"Pipeline 类型: {type(pipeline)}")
            print(f"Pipeline 长度: {len(pipeline) if isinstance(pipeline, list) else 'N/A'}")
            if isinstance(pipeline, list) and pipeline:
                print(f"第一个 stage: {pipeline[0]}")


def _parse_query_type(query_cmd: str) -> Optional[str]:
    """解析查询操作类型 - 与原代码保持一致"""
    query_cmd_clean = query_cmd.strip().lower()
    
    if ".find(" in query_cmd_clean and ".findone(" not in query_cmd_clean:
        return "find"
    elif ".findone(" in query_cmd_clean:
        return "findOne"
    elif ".aggregate(" in query_cmd_clean:
        return "aggregate"
    elif ".countdocuments(" in query_cmd_clean:
        return "countDocuments"
    elif ".count(" in query_cmd_clean:
        return "count"
    elif ".distinct(" in query_cmd_clean:
        return "distinct"
    
    return None


if __name__ == "__main__":
    # 运行测试
    test_pipeline_parsing()