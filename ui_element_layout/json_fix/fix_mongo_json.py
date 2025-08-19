import re
import logging
from typing import Any, Dict

def fix_query_syntax(query_cmd: str) -> str:
    """
    修复MongoDB查询语句 - 支持直接执行和JSON转换两种模式
    
    Args:
        query_cmd: 原始查询命令
        
    Returns:
        修复后的查询命令
    """
    try:
        # 尝试直接执行（不转换）
        if can_execute_directly(query_cmd):
            print(f"--> 查询语法正确，无需修复: {query_cmd}")
            return query_cmd.strip()
        
        # 如果直接执行失败，进行最小化修复
        fixed_query = apply_minimal_fixes(query_cmd)
        
        # 再次尝试执行
        if can_execute_directly(fixed_query):
            print(f"--> 修复后可执行: {fixed_query}")
            return fixed_query
        
        # 如果还是不行，使用传统的JSON修复方法
        fixed_query = apply_json_fixes(query_cmd)
        print(f"--> 使用JSON修复: {fixed_query}")
        return fixed_query
        
    except Exception as e:
        logging.error(f"修复查询语法时发生错误: {e}")
        return query_cmd

def can_execute_directly(query: str) -> bool:
    """
    检查查询是否可以直接执行（使用eval模拟）
    """
    try:
        # 模拟MongoDB环境
        mock_env = create_mock_mongodb_env()
        
        # 清理查询语句
        clean_query = query.strip()
        if not clean_query:
            return False
        
        # 尝试执行（安全的eval）
        result = safe_eval(clean_query, mock_env)
        return result is not None
        
    except Exception:
        return False

def create_mock_mongodb_env():
    """
    创建模拟的MongoDB执行环境
    """
    class MockCollection:
        def __init__(self, name):
            self.name = name
        
        def aggregate(self, pipeline):
            return f"aggregate({pipeline})"
        
        def find(self, *args):
            return f"find({args})"
        
        def findOne(self, *args):
            return f"findOne({args})"
        
        def distinct(self, *args):
            return f"distinct({args})"
        
        def count(self, *args):
            return f"count({args})"
        
        def countDocuments(self, *args):
            return f"countDocuments({args})"
    
    class MockDB:
        def getCollection(self, name):
            return MockCollection(name)
        
        def __getattr__(self, name):
            return MockCollection(name)
    
    # MongoDB操作符和函数
    mock_operators = {
        # 查询操作符
        '$gt': lambda x: {'$gt': x},
        '$gte': lambda x: {'$gte': x},
        '$lt': lambda x: {'$lt': x},
        '$lte': lambda x: {'$lte': x},
        '$eq': lambda x: {'$eq': x},
        '$ne': lambda x: {'$ne': x},
        '$in': lambda x: {'$in': x},
        '$nin': lambda x: {'$nin': x},
        '$exists': lambda x: {'$exists': x},
        '$regex': lambda x: {'$regex': x},
        
        # 聚合操作符
        '$match': lambda x: {'$match': x},
        '$group': lambda x: {'$group': x},
        '$sort': lambda x: {'$sort': x},
        '$project': lambda x: {'$project': x},
        '$unwind': lambda x: {'$unwind': x},
        '$lookup': lambda x: {'$lookup': x},
        '$replaceRoot': lambda x: {'$replaceRoot': x},
        '$addFields': lambda x: {'$addFields': x},
        '$limit': lambda x: {'$limit': x},
        '$skip': lambda x: {'$skip': x},
        
        # 聚合表达式
        '$sum': lambda x: {'$sum': x},
        '$avg': lambda x: {'$avg': x},
        '$max': lambda x: {'$max': x},
        '$min': lambda x: {'$min': x},
        '$first': lambda x: {'$first': x},
        '$last': lambda x: {'$last': x},
        '$push': lambda x: {'$push': x},
        '$addToSet': lambda x: {'$addToSet': x},
        
        # MongoDB函数
        'ObjectId': lambda x=None: f"ObjectId({x})" if x else "ObjectId()",
        'ISODate': lambda x: f"ISODate({x})",
        'NumberLong': lambda x: f"NumberLong({x})",
        'NumberInt': lambda x: f"NumberInt({x})",
    }
    
    return {
        'db': MockDB(),
        **mock_operators
    }

def safe_eval(expression: str, env: Dict[str, Any]) -> Any:
    """
    安全的eval执行，只允许MongoDB相关的操作
    """
    # 检查是否包含危险操作
    dangerous_keywords = [
        'import', 'exec', 'eval', '__', 'open', 'file', 'input', 'raw_input',
        'compile', 'reload', 'globals', 'locals', 'vars', 'dir', 'delattr',
        'getattr', 'setattr', 'hasattr', 'callable'
    ]
    
    expression_lower = expression.lower()
    for keyword in dangerous_keywords:
        if keyword in expression_lower:
            raise ValueError(f"不安全的操作: {keyword}")
    
    # 只允许MongoDB相关的表达式
    if not (expression.strip().startswith('db.') or 
            any(op in expression for op in ['aggregate', 'find', 'count', 'distinct'])):
        raise ValueError("不是有效的MongoDB查询")
    
    try:
        # 使用受限的环境执行
        return eval(expression, {"__builtins__": {}}, env)
    except Exception as e:
        raise ValueError(f"执行失败: {e}")

def apply_minimal_fixes(query: str) -> str:
    """
    应用最小化修复，只修复明显的语法错误
    """
    fixed = query.strip()
    
    # 1. 修复括号匹配
    fixed = fix_bracket_balance(fixed)
    
    # 2. 修复明显的逗号问题
    fixed = re.sub(r'}\s*{', '},{', fixed)
    fixed = re.sub(r']\s*\[', '],[', fixed)
    fixed = re.sub(r',\s*([}\]])', r'\1', fixed)
    
    # 3. 修复单引号为双引号（只修复字符串值）
    fixed = re.sub(r":\s*'([^']*)'", r': "\1"', fixed)
    
    return fixed

def apply_json_fixes(query: str) -> str:
    """
    应用完整的JSON修复（作为最后手段）
    """
    fixed = query.strip()
    
    # 修复字段名引号（避免MongoDB操作符）
    mongodb_operators = [
        '$match', '$group', '$sort', '$project', '$unwind', '$lookup', '$replaceRoot',
        '$addFields', '$limit', '$skip', '$sum', '$avg', '$max', '$min', '$first',
        '$last', '$push', '$addToSet', '$gt', '$gte', '$lt', '$lte', '$eq', '$ne',
        '$in', '$nin', '$exists', '$regex', '$elemMatch', '$all', '$size'
    ]
    
    # 为未加引号的字段名添加引号，但排除MongoDB操作符
    pattern = r'([{,\[\s]\s*)([a-zA-Z_$][a-zA-Z0-9_$]*)\s*:'
    
    def replace_field_name(match):
        prefix = match.group(1)
        field_name = match.group(2)
        
        # 不处理MongoDB操作符
        if field_name.startswith('$') or field_name in ['newRoot', '_id']:
            return match.group(0)
        
        return f'{prefix}"{field_name}":'
    
    fixed = re.sub(pattern, replace_field_name, fixed)
    
    # 其他修复
    fixed = apply_minimal_fixes(fixed)
    
    return fixed

def fix_bracket_balance(text: str) -> str:
    """
    修复括号平衡
    """
    # 统计括号
    brackets = {'(': ')', '{': '}', '[': ']'}
    counts = {')': 0, '}': 0, ']': 0}
    
    for char in text:
        if char in brackets:
            counts[brackets[char]] += 1
        elif char in counts:
            counts[char] -= 1
    
    # 添加缺失的闭合括号
    for close_bracket, count in counts.items():
        if count > 0:
            text += close_bracket * count
    
    return text

# 方法2: 使用JavaScript风格的执行
def execute_mongodb_query_js_style(query: str) -> str:
    """
    使用JavaScript风格直接执行MongoDB查询（不需要JSON转换）
    """
    try:
        # 清理查询
        clean_query = query.strip()
        
        # 检查基本语法
        if not validate_basic_syntax(clean_query):
            # 只做最基本的修复
            clean_query = apply_minimal_fixes(clean_query)
        
        print(f"--> JavaScript风格执行: {clean_query}")
        return clean_query
        
    except Exception as e:
        logging.error(f"JavaScript风格执行失败: {e}")
        return query

def validate_basic_syntax(query: str) -> bool:
    """
    验证基本语法（括号匹配等）
    """
    stack = []
    brackets = {'(': ')', '{': '}', '[': ']'}
    
    in_string = False
    string_char = None
    
    for char in query:
        if char in ['"', "'"] and not in_string:
            in_string = True
            string_char = char
        elif char == string_char and in_string:
            in_string = False
            string_char = None
        elif not in_string:
            if char in brackets:
                stack.append(brackets[char])
            elif char in brackets.values():
                if not stack or stack.pop() != char:
                    return False
    
    return len(stack) == 0

# 测试函数
def test_direct_execution():
    """
    测试直接执行的效果
    """
    test_queries = [
        # 您的测试用例
        """db.getCollection('一企一档').aggregate([
        {
            "$unwind": "$fields"
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
        ])""",
        
        # 其他测试
        "db.users.find({name: 'John', age: {$gt: 20}})",
        "db.users.aggregate([{$match: {status: 'active'}}])",
        "db.products.count({price: {$lt: 100}})",
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n=== 测试 {i} ===")
        print("原查询:")
        print(query)
        print("\n直接执行结果:")
        
        # 方法1: 模拟执行
        result1 = fix_query_syntax(query)
        
        print("\nJavaScript风格:")
        # 方法2: JavaScript风格
        result2 = execute_mongodb_query_js_style(query)
        
        print("-" * 60)

if __name__ == "__main__":
    test_direct_execution()