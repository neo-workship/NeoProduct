#!/usr/bin/env python3
"""
项目代码转Markdown工具
将Python项目的代码文件转换为单个Markdown文档
支持处理代码中包含的markdown代码块标记
"""

import os
import sys
import argparse
import re
from pathlib import Path
from typing import Set, List

# 常见的代码文件扩展名
CODE_EXTENSIONS = {
    '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.c', '.cpp', '.h', '.hpp',
    '.cs', '.go', '.rs', '.php', '.rb', '.swift', '.kt', '.scala', '.sh',
    '.bash', '.sql', '.html', '.css', '.scss', '.less', '.vue', '.json',
    '.xml', '.yaml', '.yml'
}

# 扩展名到语言标识的映射
LANGUAGE_MAP = {
    '.py': 'python',
    '.js': 'javascript',
    '.ts': 'typescript',
    '.jsx': 'jsx',
    '.tsx': 'tsx',
    '.java': 'java',
    '.c': 'c',
    '.cpp': 'cpp',
    '.h': 'c',
    '.hpp': 'cpp',
    '.cs': 'csharp',
    '.go': 'go',
    '.rs': 'rust',
    '.php': 'php',
    '.rb': 'ruby',
    '.swift': 'swift',
    '.kt': 'kotlin',
    '.scala': 'scala',
    '.sh': 'bash',
    '.bash': 'bash',
    '.sql': 'sql',
    '.html': 'html',
    '.css': 'css',
    '.scss': 'scss',
    '.vue': 'vue',
    '.json': 'json',
    '.xml': 'xml',
    '.yaml': 'yaml',
    '.yml': 'yaml',
    '.md': 'markdown',
}


def get_fence_length(content: str) -> int:
    """
    检测内容中最长的连续反引号序列长度
    返回需要使用的围栏长度（至少为3，且比内容中最长的多1）
    """
    # 查找所有连续的反引号序列
    backtick_sequences = re.findall(r'`+', content)
    
    if not backtick_sequences:
        return 3  # 默认使用3个反引号
    
    # 找到最长的序列
    max_length = max(len(seq) for seq in backtick_sequences)
    
    # 返回比最长序列多1的长度，且至少为3
    return max(3, max_length + 1)


def create_code_fence(content: str, language: str) -> tuple:
    """
    创建代码围栏，返回开始和结束标记
    """
    fence_length = get_fence_length(content)
    fence = '`' * fence_length
    
    return f"{fence}{language}", fence


def should_ignore(path: Path, ignore_patterns: Set[str]) -> bool:
    """检查路径是否应该被忽略"""
    # 检查路径的每一部分是否在忽略列表中
    for part in path.parts:
        if part in ignore_patterns:
            return True
    
    # 检查完整路径
    if path.name in ignore_patterns:
        return True
    
    return False


def is_code_file(file_path: Path) -> bool:
    """判断是否为代码文件"""
    return file_path.suffix.lower() in CODE_EXTENSIONS


def get_language_identifier(file_path: Path) -> str:
    """获取文件的语言标识符"""
    ext = file_path.suffix.lower()
    return LANGUAGE_MAP.get(ext, '')


def read_file_content(file_path: Path) -> str:
    """读取文件内容，处理各种编码"""
    encodings = ['utf-8', 'gbk', 'gb2312', 'latin-1']
    
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
        except Exception as e:
            return f"# 读取文件出错: {str(e)}"
    
    return "# 无法读取文件内容（编码问题）"


def generate_markdown(root_path: Path, ignore_patterns: Set[str]) -> str:
    """生成Markdown内容"""
    markdown_lines = []
    root_name = root_path.name
    
    # 添加标题
    markdown_lines.append(f"# {root_name}\n")
    
    # 检查目录是否包含代码文件（递归检查）
    def has_code_files(dir_path: Path) -> bool:
        """检查目录及其子目录是否包含代码文件"""
        try:
            for item in dir_path.iterdir():
                # 跳过忽略的项目
                if should_ignore(item.relative_to(root_path), ignore_patterns):
                    continue
                
                if item.is_file() and is_code_file(item):
                    return True
                elif item.is_dir() and has_code_files(item):
                    return True
        except (PermissionError, Exception):
            pass
        
        return False
    
    # 递归遍历目录
    def traverse_directory(current_path: Path, level: int = 1):
        try:
            # 获取当前目录的所有项目
            items = sorted(current_path.iterdir(), key=lambda x: (x.is_file(), x.name))
            
            files = []
            dirs = []
            
            for item in items:
                # 跳过忽略的文件和文件夹
                if should_ignore(item.relative_to(root_path), ignore_patterns):
                    continue
                
                if item.is_file() and is_code_file(item):
                    files.append(item)
                elif item.is_dir():
                    # 只添加包含代码文件的目录
                    if has_code_files(item):
                        dirs.append(item)
            
            # 先处理文件
            for file_path in files:
                # 获取相对于根目录的路径，包含根目录名称
                relative_path = Path(root_name) / file_path.relative_to(root_path)
                lang = get_language_identifier(file_path)
                content = read_file_content(file_path)
                
                # 创建适当长度的代码围栏
                fence_start, fence_end = create_code_fence(content, lang)
                
                # 特殊处理 __init__.py
                if file_path.name == '__init__.py':
                    # 检查是否为空文件或仅包含注释/空行
                    content_stripped = '\n'.join(
                        line for line in content.split('\n') 
                        if line.strip() and not line.strip().startswith('#')
                    )
                    
                    if not content_stripped:
                        markdown_lines.append(f"- **{relative_path}** *(包初始化文件 - 空)*")
                        markdown_lines.append(fence_start)
                        markdown_lines.append(content)
                        markdown_lines.append(fence_end)
                        markdown_lines.append("")
                    else:
                        markdown_lines.append(f"- **{relative_path}** *(包初始化文件)*")
                        markdown_lines.append(fence_start)
                        markdown_lines.append(content)
                        markdown_lines.append(fence_end)
                        markdown_lines.append("")
                else:
                    markdown_lines.append(f"- **{relative_path}**")
                    markdown_lines.append(fence_start)
                    markdown_lines.append(content)
                    markdown_lines.append(fence_end)
                    markdown_lines.append("")
            
            # 再处理子目录
            for dir_path in dirs:
                # 获取相对于根目录的路径，包含根目录名称
                relative_dir_path = Path(root_name) / dir_path.relative_to(root_path)
                # 添加子目录标题
                header_prefix = "#" * (level + 1)
                markdown_lines.append(f"{header_prefix} {relative_dir_path}\n")
                
                # 递归处理子目录
                traverse_directory(dir_path, level + 1)
        
        except PermissionError:
            markdown_lines.append(f"\n> ⚠️ 无权限访问: {current_path}\n")
        except Exception as e:
            markdown_lines.append(f"\n> ❌ 处理目录出错 {current_path}: {str(e)}\n")
    
    # 开始遍历
    traverse_directory(root_path)
    
    return "\n".join(markdown_lines)


def main():
    parser = argparse.ArgumentParser(
        description='将项目代码转换为Markdown文档',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  %(prog)s my_project -e __pycache__ .git node_modules
  %(prog)s ./src -e tests build -o output.md
        '''
    )
    
    parser.add_argument(
        'root_folder',
        help='项目根文件夹路径'
    )
    
    parser.add_argument(
        '-e', '--exclude',
        nargs='*',
        default=[],
        help='要忽略的文件夹或文件名（支持多个）'
    )
    
    parser.add_argument(
        '-o', '--output',
        default=None,
        help='输出文件名（默认: <项目名>.md）'
    )
    
    args = parser.parse_args()
    
    # 处理路径
    root_path = Path(args.root_folder).resolve()
    
    # 检查路径是否存在
    if not root_path.exists():
        print(f"❌ 错误: 路径不存在: {root_path}", file=sys.stderr)
        sys.exit(1)
    
    if not root_path.is_dir():
        print(f"❌ 错误: 不是一个文件夹: {root_path}", file=sys.stderr)
        sys.exit(1)
    
    # 默认忽略的目录
    default_ignores = {
        '__pycache__', '.git', '.svn', '.hg', 
        'node_modules', 'venv', 'env', '.venv',
        '.idea', '.vscode', 'dist', 'build'
    }
    
    # 合并用户指定的忽略项
    ignore_patterns = default_ignores.union(set(args.exclude))
    
    # 确定输出文件名
    if args.output:
        output_file = Path(args.output)
    else:
        output_file = Path(f"{root_path.name}.md")
    
    # 显示信息
    print(f"📂 项目路径: {root_path}")
    print(f"🚫 忽略项: {', '.join(sorted(ignore_patterns))}")
    print(f"📝 输出文件: {output_file}")
    print("\n⏳ 正在处理...\n")
    
    # 生成Markdown
    try:
        markdown_content = generate_markdown(root_path, ignore_patterns)
        
        # 写入文件
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        print(f"✅ 成功! Markdown文件已生成: {output_file.absolute()}")
        
        # 统计信息
        line_count = len(markdown_content.split('\n'))
        file_size = output_file.stat().st_size
        print(f"📊 总行数: {line_count}")
        print(f"📊 文件大小: {file_size / 1024:.2f} KB")
        
    except Exception as e:
        print(f"❌ 生成失败: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()