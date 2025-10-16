#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
目录树生成器
读取指定目录并生成带注释的树形结构
"""

import os
from pathlib import Path
from typing import List, Dict, Optional


class DirectoryTreeGenerator:
    """目录树生成器类"""
    
    def __init__(self, 
                 show_hidden: bool = False,
                 exclude_dirs: Optional[List[str]] = None,
                 exclude_files: Optional[List[str]] = None,
                 comment_map: Optional[Dict[str, str]] = None):
        """
        初始化生成器
        
        Args:
            show_hidden: 是否显示隐藏文件
            exclude_dirs: 要排除的目录列表
            exclude_files: 要排除的文件列表
            comment_map: 文件/目录注释映射 {路径: 注释}
        """
        self.show_hidden = show_hidden
        self.exclude_dirs = exclude_dirs or ['.git', '__pycache__', '.venv', 'venv', 
                                             'node_modules', '.idea', '.vscode']
        self.exclude_files = exclude_files or ['.DS_Store', 'Thumbs.db']
        self.comment_map = comment_map or {}
    
    def should_exclude(self, path: Path, is_dir: bool) -> bool:
        """判断是否应该排除该路径"""
        name = path.name
        
        # 排除隐藏文件
        if not self.show_hidden and name.startswith('.'):
            return True
        
        # 排除指定的目录或文件
        if is_dir and name in self.exclude_dirs:
            return True
        if not is_dir and name in self.exclude_files:
            return True
            
        return False
    
    def get_comment(self, rel_path: str, is_dir: bool) -> str:
        """获取路径对应的注释"""
        # 尝试精确匹配
        if rel_path in self.comment_map:
            return self.comment_map[rel_path]
        
        # 尝试匹配文件名
        name = os.path.basename(rel_path)
        if name in self.comment_map:
            return self.comment_map[name]
        
        return ""
    
    def generate_tree(self, 
                     root_path: str, 
                     prefix: str = "", 
                     is_last: bool = True,
                     relative_to: Optional[str] = None) -> List[str]:
        """
        递归生成目录树
        
        Args:
            root_path: 根目录路径
            prefix: 当前行的前缀
            is_last: 是否是最后一个项目
            relative_to: 相对路径的基准目录
            
        Returns:
            目录树行的列表
        """
        root = Path(root_path)
        lines = []
        
        if relative_to is None:
            relative_to = str(root.parent)
        
        try:
            # 获取目录内容并排序(目录在前,文件在后)
            items = sorted(root.iterdir(), 
                          key=lambda x: (not x.is_dir(), x.name.lower()))
            
            # 过滤掉要排除的项目
            items = [item for item in items 
                    if not self.should_exclude(item, item.is_dir())]
            
            for i, item in enumerate(items):
                is_last_item = (i == len(items) - 1)
                
                # 确定树形符号
                if is_last_item:
                    connector = "└── "
                    new_prefix = prefix + "    "
                else:
                    connector = "├── "
                    new_prefix = prefix + "│   "
                
                # 获取相对路径用于查找注释
                rel_path = str(item.relative_to(relative_to))
                
                # 构建行内容
                name = item.name
                if item.is_dir():
                    name += "/"
                
                comment = self.get_comment(rel_path, item.is_dir())
                if comment:
                    line = f"{prefix}{connector}{name:30s} # {comment}"
                else:
                    line = f"{prefix}{connector}{name}"
                
                lines.append(line)
                
                # 如果是目录,递归处理
                if item.is_dir():
                    sub_lines = self.generate_tree(
                        str(item), 
                        new_prefix, 
                        is_last_item,
                        relative_to
                    )
                    lines.extend(sub_lines)
        
        except PermissionError:
            lines.append(f"{prefix}[Permission Denied]")
        
        return lines
    
    def generate(self, root_path: str, include_root: bool = True) -> str:
        """
        生成完整的目录树字符串
        
        Args:
            root_path: 要扫描的根目录
            include_root: 是否包含根目录名称
            
        Returns:
            格式化的目录树字符串
        """
        root = Path(root_path)
        
        if not root.exists():
            return f"Error: Path '{root_path}' does not exist"
        
        if not root.is_dir():
            return f"Error: Path '{root_path}' is not a directory"
        
        lines = []
        
        if include_root:
            root_name = root.name + "/"
            root_comment = self.get_comment(root.name, True)
            if root_comment:
                lines.append(f"{root_name:30s} # {root_comment}")
            else:
                lines.append(root_name)
            
            tree_lines = self.generate_tree(root_path, relative_to=str(root.parent))
        else:
            tree_lines = self.generate_tree(root_path, relative_to=root_path)
        
        lines.extend(tree_lines)
        
        return "\n".join(lines)


def load_comments_from_file(comment_file: str) -> Dict[str, str]:
    """
    从文件加载注释配置
    文件格式: 每行一个映射,用 | 分隔
    例如: auth|认证和权限管理包
    """
    comments = {}
    try:
        with open(comment_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    parts = line.split('|', 1)
                    if len(parts) == 2:
                        comments[parts[0].strip()] = parts[1].strip()
    except FileNotFoundError:
        pass
    return comments


# 命令行使用
if __name__ == "__main__":
    import sys
    import argparse
    
    # 默认注释映射
    default_comments = {
        "auth": "认证和权限管理包",
        "__init__.py": "包初始化和导出",
        "config.py": "配置文件",
        "database.py": "数据库连接和ORM",
        "models.py": "数据模型",
        "utils.py": "工具函数",
        "pages": "页面模块",
        "doc": "文档目录",
        "migrations": "数据库迁移脚本",
        "tests": "测试文件",
        "static": "静态资源",
        "templates": "模板文件",
    }
    
    # 解析命令行参数
    parser = argparse.ArgumentParser(
        description='生成目录树结构',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例用法:
  python DirectoryTreeGenerator.py .                    # 扫描当前目录,保存到 directory_tree.txt
  python DirectoryTreeGenerator.py ./project            # 扫描指定目录,保存到 directory_tree.txt
  python DirectoryTreeGenerator.py ./auth -o tree.txt   # 保存到指定文件
  python DirectoryTreeGenerator.py . --stdout           # 输出到终端
  python DirectoryTreeGenerator.py . --show-hidden      # 显示隐藏文件
  python DirectoryTreeGenerator.py . -c comments.txt    # 使用注释配置文件
        '''
    )
    
    parser.add_argument('directory', 
                       nargs='?',
                       default='.',
                       help='要扫描的目录路径 (默认: 当前目录)')
    
    parser.add_argument('-o', '--output',
                       help='输出文件路径 (默认: directory_tree.txt)')
    
    parser.add_argument('--stdout',
                       action='store_true',
                       help='输出到终端而不是文件')
    
    parser.add_argument('--show-hidden',
                       action='store_true',
                       help='显示隐藏文件和目录')
    
    parser.add_argument('--no-root',
                       action='store_true',
                       help='不显示根目录名称')
    
    parser.add_argument('-c', '--comments',
                       help='注释配置文件路径')
    
    parser.add_argument('--exclude-dirs',
                       help='要排除的目录,用逗号分隔')
    
    parser.add_argument('--exclude-files',
                       help='要排除的文件,用逗号分隔')
    
    args = parser.parse_args()
    
    # 加载注释
    comments = default_comments.copy()
    if args.comments:
        custom_comments = load_comments_from_file(args.comments)
        comments.update(custom_comments)
    
    # 解析排除列表
    exclude_dirs = None
    if args.exclude_dirs:
        exclude_dirs = [d.strip() for d in args.exclude_dirs.split(',')]
    
    exclude_files = None
    if args.exclude_files:
        exclude_files = [f.strip() for f in args.exclude_files.split(',')]
    
    # 创建生成器
    generator = DirectoryTreeGenerator(
        show_hidden=args.show_hidden,
        exclude_dirs=exclude_dirs,
        exclude_files=exclude_files,
        comment_map=comments
    )
    
    # 输出调用信息
    print(f"=" * 60)
    print(f"目录树生成器")
    print(f"=" * 60)
    print(f"扫描目录: {os.path.abspath(args.directory)}")
    print(f"显示隐藏文件: {args.show_hidden}")
    print(f"包含根目录: {not args.no_root}")
    
    # 确定输出文件
    if args.stdout:
        output_file = None
        print(f"输出模式: 终端")
    else:
        output_file = args.output if args.output else "directory_tree.txt"
        print(f"输出文件: {output_file}")
    
    print(f"-" * 60)
    
    # 检查目录是否存在
    if not os.path.exists(args.directory):
        print(f"错误: 目录 '{args.directory}' 不存在!")
        sys.exit(1)
    
    if not os.path.isdir(args.directory):
        print(f"错误: '{args.directory}' 不是一个目录!")
        sys.exit(1)
    
    # 生成目录树
    try:
        tree = generator.generate(args.directory, include_root=not args.no_root)
        
        # 检查是否生成了内容
        if not tree or tree.strip() == "":
            print("警告: 目录为空或所有内容都被过滤了")
            print(f"\n当前排除的目录: {generator.exclude_dirs}")
            print(f"当前排除的文件: {generator.exclude_files}")
            
            # 显示实际目录内容
            print(f"\n实际目录内容:")
            try:
                items = list(Path(args.directory).iterdir())
                if items:
                    for item in items:
                        print(f"  - {item.name} {'(目录)' if item.is_dir() else '(文件)'}")
                else:
                    print("  (目录为空)")
            except Exception as e:
                print(f"  无法读取目录: {e}")
        else:
            # 输出结果
            if output_file:
                # 保存到文件
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(tree)
                print(f"\n✓ 目录树已保存到: {os.path.abspath(output_file)}")
                print(f"  共 {len(tree.splitlines())} 行")
            else:
                # 输出到终端
                print()  # 空行分隔
                print(tree)
                print()
                print(f"✓ 共 {len(tree.splitlines())} 行")
    
    except Exception as e:
        print(f"\n错误: 生成目录树时出现异常")
        print(f"  {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    print(f"=" * 60)