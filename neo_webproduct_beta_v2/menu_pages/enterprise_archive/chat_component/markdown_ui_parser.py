import re
import asyncio
from typing import Optional, List, Dict, Any
from nicegui import ui


class MarkdownUIParser:
    """
    Markdown 内容解析器和 UI 组件映射器
    负责将 Markdown 内容解析为结构化块，并将其映射为相应的UI组件
    """
    
    def __init__(self):
        """初始化解析器"""
        pass
    
    # ==================== 主要接口方法 ====================
    async def optimize_content_display(self, reply_label, content: str, chat_content_container=None):
        """
        优化内容显示 - 将特殊内容转换为专业UI组件 
        Args:
            reply_label: 当前的markdown组件引用
            content: 完整的AI回复内容
            chat_content_container: 聊天内容容器引用
        """
        try:
            # 1. 解析内容，检测特殊块
            parsed_blocks = self.parse_content_with_regex(content)
            
            # 2. 判断是否需要优化
            if self.has_special_content(parsed_blocks):
                # 3. 显示优化提示
                self.show_optimization_hint(reply_label)
                
                # 4. 短暂延迟，让用户看到提示
                await asyncio.sleep(0.1)
                
                # 5. 获取正确的容器
                container = chat_content_container if chat_content_container else reply_label
                
                # 6. 重新渲染混合组件
                await self.render_optimized_content(container, parsed_blocks)
            
        except Exception as e:
            ui.notify(f"内容优化失败，保持原始显示: {e}")

    def parse_content_with_regex(self, content: str) -> List[Dict[str, Any]]:
        """
        使用正则表达式解析内容为结构化块
        
        Args:
            content: 需要解析的 Markdown 内容
            
        Returns:
            List[Dict]: 解析后的内容块列表
            [{
                'type': 'table|mermaid|code|heading|math|text',
                'content': '原始内容',
                'data': '解析后的数据'(可选),
                'start_pos': 开始位置,
                'end_pos': 结束位置
            }]
        """
        blocks = []
        
        # 1. 检测表格
        table_blocks = self.extract_tables(content)
        blocks.extend(table_blocks)
        
        # 2. 检测Mermaid图表
        mermaid_blocks = self.extract_mermaid(content)
        blocks.extend(mermaid_blocks)
        
        # 3. 检测代码块
        code_blocks = self.extract_code_blocks(content)
        blocks.extend(code_blocks)
        
        # 4. 检测LaTeX公式
        math_blocks = self.extract_math(content)
        blocks.extend(math_blocks)
        
        # 5. 检测标题
        heading_blocks = self.extract_headings(content)
        blocks.extend(heading_blocks)
        
        # 6. 按位置排序
        blocks.sort(key=lambda x: x['start_pos'])
        
        # 7. 填充文本块
        text_blocks = self.fill_text_blocks(content, blocks)
        
        # 8. 合并并重新排序
        all_blocks = blocks + text_blocks
        all_blocks.sort(key=lambda x: x['start_pos'])
        
        return all_blocks
    
    # ==================== 内容提取方法 ====================
    
    def extract_tables(self, content: str) -> List[Dict[str, Any]]:
        """提取表格内容"""
        tables = []
        # 匹配markdown表格模式
        pattern = r'(\|.*\|.*\n\|[-\s\|]*\|.*\n(?:\|.*\|.*\n)*)'
        
        for match in re.finditer(pattern, content):
            table_data = self.parse_table_data(match.group(1))
            if table_data:  # 确保解析成功
                tables.append({
                    'type': 'table',
                    'content': match.group(1),
                    'data': table_data,
                    'start_pos': match.start(),
                    'end_pos': match.end()
                })
        
        return tables

    def extract_mermaid(self, content: str) -> List[Dict[str, Any]]:
        """提取Mermaid图表"""
        mermaid_blocks = []
        pattern = r'```mermaid\n(.*?)```'
        
        for match in re.finditer(pattern, content, re.DOTALL):
            mermaid_blocks.append({
                'type': 'mermaid',
                'content': match.group(1).strip(),
                'start_pos': match.start(),
                'end_pos': match.end()
            })
    
        return mermaid_blocks

    def extract_code_blocks(self, content: str) -> List[Dict[str, Any]]:
        """提取代码块（排除mermaid）"""
        code_blocks = []
        pattern = r'```(\w+)?\n(.*?)```'
        
        for match in re.finditer(pattern, content, re.DOTALL):
            language = match.group(1) or 'text'
            if language.lower() != 'mermaid':  # 排除mermaid
                code_blocks.append({
                    'type': 'code',
                    'content': match.group(2).strip(),
                    'language': language,
                    'start_pos': match.start(),
                    'end_pos': match.end()
                })
        
        return code_blocks

    def extract_math(self, content: str) -> List[Dict[str, Any]]:
        """提取LaTeX数学公式"""
        math_blocks = []
        
        # 块级公式 $$...$$
        block_pattern = r'\$\$(.*?)\$\$'
        for match in re.finditer(block_pattern, content, re.DOTALL):
            math_blocks.append({
                'type': 'math',
                'content': match.group(1).strip(),
                'display_mode': 'block',
                'start_pos': match.start(),
                'end_pos': match.end()
            })
        
        # 行内公式 $...$
        inline_pattern = r'(?<!\$)\$([^\$\n]+)\$(?!\$)'
        for match in re.finditer(inline_pattern, content):
            math_blocks.append({
                'type': 'math',
                'content': match.group(1).strip(),
                'display_mode': 'inline',
                'start_pos': match.start(),
                'end_pos': match.end()
            })
        
        return math_blocks

    def extract_headings(self, content: str) -> List[Dict[str, Any]]:
        """提取标题"""
        headings = []
        pattern = r'^(#{1,6})\s+(.+)$'
        
        for match in re.finditer(pattern, content, re.MULTILINE):
            level = len(match.group(1))
            text = match.group(2).strip()
            headings.append({
                'type': 'heading',
                'content': text,
                'level': level,
                'start_pos': match.start(),
                'end_pos': match.end()
            })
        
        return headings

    def fill_text_blocks(self, content: str, special_blocks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """填充普通文本块"""
        if not special_blocks:
            return [{
                'type': 'text',
                'content': content,
                'start_pos': 0,
                'end_pos': len(content)
            }]
        
        text_blocks = []
        last_end = 0
        
        for block in special_blocks:
            if block['start_pos'] > last_end:
                text_content = content[last_end:block['start_pos']].strip()
                if text_content:
                    text_blocks.append({
                        'type': 'text',
                        'content': text_content,
                        'start_pos': last_end,
                        'end_pos': block['start_pos']
                    })
            last_end = block['end_pos']
        
        # 添加最后的文本内容
        if last_end < len(content):
            text_content = content[last_end:].strip()
            if text_content:
                text_blocks.append({
                    'type': 'text',
                    'content': text_content,
                    'start_pos': last_end,
                    'end_pos': len(content)
                })
        
        return text_blocks
    
    # ==================== 数据解析方法 ====================
    
    def parse_table_data(self, table_text: str) -> Optional[Dict[str, Any]]:
        """解析表格数据为NiceGUI table格式"""
        try:
            lines = [line.strip() for line in table_text.strip().split('\n') if line.strip()]
            if len(lines) < 3:  # 至少需要header、separator、data
                return None
            
            # 解析表头
            headers = [cell.strip() for cell in lines[0].split('|')[1:-1]]
            if not headers:
                return None
            
            # 解析数据行（跳过分隔行）
            rows = []
            for line in lines[2:]:
                cells = [cell.strip() for cell in line.split('|')[1:-1]]
                if len(cells) == len(headers):
                    row_data = dict(zip(headers, cells))
                    rows.append(row_data)
            
            return {
                'columns': [{'name': col, 'label': col, 'field': col} for col in headers],
                'rows': rows
            }
        
        except Exception as e:
            ui.notify(f"表格解析失败: {e}")
            return None
    
    # ==================== 检测和渲染方法 ====================
    
    def has_special_content(self, blocks: List[Dict[str, Any]]) -> bool:
        """检查是否包含需要优化的特殊内容"""
        special_types = {'table', 'mermaid', 'code', 'math', 'heading'}
        return any(block['type'] in special_types for block in blocks)

    def show_optimization_hint(self, reply_label):
        """显示优化提示"""
        try:
            reply_label.set_content("🔄 正在优化内容显示...")
        except:
            pass  # 如果设置失败，忽略错误

    async def render_optimized_content(self, container, blocks: List[Dict[str, Any]]):
        """渲染优化后的混合内容"""
        container.clear()
        
        with container:
            for block in blocks:
                try:
                    if block['type'] == 'table':
                        self.create_table_component(block['data'])
                    elif block['type'] == 'mermaid':
                        self.create_mermaid_component(block['content'])
                    elif block['type'] == 'code':
                        self.create_code_component(block['content'], block['language'])
                    elif block['type'] == 'math':
                        self.create_math_component(block['content'], block['display_mode'])
                    elif block['type'] == 'heading':
                        self.create_heading_component(block['content'], block['level'])
                    elif block['type'] == 'text':
                        self.create_text_component(block['content'])
                    else:
                        # 兜底：用markdown显示
                        ui.markdown(block['content']).classes('w-full')
                except Exception as e:
                    # 错误兜底：显示为代码块
                    ui.markdown(f"```\n{block['content']}\n```").classes('w-full')
    
    # ==================== UI组件创建方法 ====================
    
    def create_table_component(self, table_data: Dict[str, Any]):
        """创建表格组件"""
        if table_data and 'columns' in table_data and 'rows' in table_data:
            ui.table(
                columns=table_data['columns'],
                rows=table_data['rows']
            ).classes('w-full max-w-full')

    def create_mermaid_component(self, mermaid_content: str):
        """创建Mermaid图表组件"""
        try:
            ui.mermaid(mermaid_content).classes('w-full')
        except Exception as e:
            ui.notify(f"流程图渲染失败: {e}",type="info")
            ui.code(mermaid_content, language='mermaid').classes('w-full')

    def create_code_component(self, code_content: str, language: str):
        """创建代码组件"""
        ui.code(code_content, language=language).classes('w-full')

    def create_math_component(self, math_content: str, display_mode: str):
        """创建数学公式组件"""
        if display_mode == 'block':
            ui.markdown(f'$$\n{math_content}\n$$',extras=['latex']).classes('w-full text-center')
        else:
            ui.markdown(f'${math_content}$',extras=['latex']).classes('w-full')

    def create_heading_component(self, text: str, level: int):
        """创建标题组件"""
        # 标题级别映射：向下调整2级
        # # -> ###, ## -> ####, ### -> #####, #### -> ######
        adjusted_level = level + 2
        
        # 限制最大级别为6（markdown支持的最大级别）
        if adjusted_level > 6:
            adjusted_level = 6
        
        # 生成对应级别的markdown标题
        markdown_heading = '#' * adjusted_level + ' ' + text
        
        # 使用ui.markdown渲染，这样可以保持**加粗**等markdown格式
        ui.markdown(markdown_heading).classes('w-full')

    def create_text_component(self, text_content: str):
        """创建文本组件"""
        if text_content.strip():
            ui.markdown(text_content, extras=['tables', 'mermaid', 'latex', 'fenced-code-blocks']).classes('w-full')
    
    # ==================== 便捷方法 ====================
    
    def get_supported_content_types(self) -> List[str]:
        """获取支持的内容类型列表"""
        return ['table', 'mermaid', 'code', 'math', 'heading', 'text']
    
    def is_content_optimizable(self, content: str) -> bool:
        """快速检查内容是否可优化"""
        blocks = self.parse_content_with_regex(content)
        return self.has_special_content(blocks)