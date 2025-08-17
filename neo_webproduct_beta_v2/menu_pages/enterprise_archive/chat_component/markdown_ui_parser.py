import re
import asyncio
from typing import Optional, List, Dict, Any
from nicegui import ui
import io
import json
import csv

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
            
            # 创建容器来包含表格和下载按钮
            with ui.card().classes('w-full relative bg-[#81c784]'):
                # 下载按钮 - 绝对定位在右上角
                with ui.row().classes('absolute top-2 right-2 z-10'):
                    ui.button(
                        # '下载', 
                        icon='download',
                        on_click=lambda: self.download_table_data(table_data)
                    ).classes('bg-blue-500 hover:bg-blue-600 text-white').props('flat round size=sm').tooltip('下载')     
                    # 表格组件
                ui.table(
                    columns=table_data['columns'],
                    rows=table_data['rows'],
                    column_defaults={
                        'align': 'left',
                        'headerClasses': 'uppercase text-primary',
                    },
                    pagination=5
                ).classes('w-full bg-[#81c784] text-gray-800')

    def download_table_data(self,table_data: Dict[str, Any]):
        """下载表格数据为CSV文件"""
        if not table_data or 'columns' not in table_data or 'rows' not in table_data:
            ui.notify('没有可下载的数据', type='warning')
            return
        try:
            # 创建CSV内容
            output = io.StringIO()
            writer = csv.writer(output)
            
            # 写入表头
            headers = [col['label'] if isinstance(col, dict) else col for col in table_data['columns']]
            writer.writerow(headers)
            
            # 写入数据行
            for row in table_data['rows']:
                if isinstance(row, dict):
                    # 如果行是字典，按列的顺序提取值
                    row_values = []
                    for col in table_data['columns']:
                        col_name = col['name'] if isinstance(col, dict) else col
                        row_values.append(row.get(col_name, ''))
                    writer.writerow(row_values)
                else:
                    # 如果行是列表，直接写入
                    writer.writerow(row)
            # 获取CSV内容
            csv_content = output.getvalue()
            output.close()
            
            # 触发下载
            ui.download(csv_content.encode('utf-8-sig'), 'table_data.csv')
            ui.notify('文件下载成功', type='positive')
        except Exception as e:
            ui.notify(f'下载失败: {str(e)}', type='negative')

    def create_mermaid_component(self, mermaid_content: str):
        """创建Mermaid图表组件"""
        try:
            # 创建容器，使用相对定位
            with ui.row().classes('w-full relative bg-[#81c784]'):
                # 右上角全屏按钮
                with ui.row().classes('absolute top-2 right-2 z-10'):
                    ui.button(
                        icon='fullscreen', 
                        on_click=lambda: self.show_fullscreen_mermaid_enhanced(mermaid_content)
                    ).props('flat round size=sm').classes('bg-blue-500 hover:bg-blue-600 text-white').tooltip('全屏显示') 
                # Mermaid图表
                ui.mermaid(mermaid_content).classes('w-full')     
        except Exception as e:
            ui.notify(f"流程图渲染失败: {e}", type="info")
            # 错误情况下也保持相同的布局结构
            ui.code(mermaid_content, language='mermaid').classes('w-full')

    def show_fullscreen_mermaid_enhanced(self, mermaid_content: str):
        """增强版全屏显示Mermaid图表"""
        
        mermaid_id = 'neo_container'
        
        def close_dialog():
            dialog.close()

        def export_image():
            """导出Mermaid图表为PNG图片"""
            try:
                # JavaScript代码：使用多种方法导出SVG
                js_code = f"""
                async function exportMermaidImage() {{
                    try {{
                        // 查找mermaid容器
                        const mermaidContainer = document.getElementById('{mermaid_id}');
                        if (!mermaidContainer) {{
                            console.error('未找到Mermaid容器');
                            return false;
                        }}
                        
                        // 查找SVG元素
                        const svgElement = mermaidContainer.querySelector('svg');
                        if (!svgElement) {{
                            console.error('未找到SVG元素');
                            return false;
                        }}
                        
                        // 克隆SVG元素以避免修改原始元素
                        const clonedSvg = svgElement.cloneNode(true);
                        
                        // 获取SVG的实际尺寸
                        const bbox = svgElement.getBBox();
                        const width = Math.max(bbox.width, svgElement.clientWidth, 400);
                        const height = Math.max(bbox.height, svgElement.clientHeight, 300);
                        
                        // 设置克隆SVG的属性
                        clonedSvg.setAttribute('width', width);
                        clonedSvg.setAttribute('height', height);
                        clonedSvg.setAttribute('viewBox', `0 0 ${{width}} ${{height}}`);
                        clonedSvg.setAttribute('xmlns', 'http://www.w3.org/2000/svg');
                        clonedSvg.setAttribute('xmlns:xlink', 'http://www.w3.org/1999/xlink');
                        
                        // 内联样式到SVG中
                        const styleSheets = Array.from(document.styleSheets);
                        let allStyles = '';
                        
                        try {{
                            for (let sheet of styleSheets) {{
                                try {{
                                    const rules = Array.from(sheet.cssRules || sheet.rules || []);
                                    for (let rule of rules) {{
                                        if (rule.type === CSSRule.STYLE_RULE) {{
                                            allStyles += rule.cssText + '\\n';
                                        }}
                                    }}
                                }} catch (e) {{
                                    // 跳过跨域样式表
                                    console.warn('跳过样式表:', e);
                                }}
                            }}
                            
                            if (allStyles) {{
                                const styleElement = document.createElement('style');
                                styleElement.textContent = allStyles;
                                clonedSvg.insertBefore(styleElement, clonedSvg.firstChild);
                            }}
                        }} catch (e) {{
                            console.warn('样式处理失败:', e);
                        }}
                        
                        // 序列化SVG
                        const serializer = new XMLSerializer();
                        let svgString = serializer.serializeToString(clonedSvg);
                        
                        // 方法1：尝试使用html2canvas式的方法
                        try {{
                            return await exportViaCanvas(svgString, width, height);
                        }} catch (canvasError) {{
                            console.warn('Canvas方法失败，尝试直接下载SVG:', canvasError);
                            // 方法2：直接下载SVG文件
                            return exportAsSVG(svgString);
                        }}
                        
                    }} catch (error) {{
                        console.error('导出图片错误:', error);
                        return false;
                    }}
                }}
                
                async function exportViaCanvas(svgString, width, height) {{
                    return new Promise((resolve, reject) => {{
                        // 创建canvas
                        const canvas = document.createElement('canvas');
                        const ctx = canvas.getContext('2d');
                        const scale = 2; // 高分辨率
                        
                        canvas.width = width * scale;
                        canvas.height = height * scale;
                        ctx.scale(scale, scale);
                        
                        // 白色背景
                        ctx.fillStyle = 'white';
                        ctx.fillRect(0, 0, width, height);
                        
                        // 创建Data URL
                        const svgBlob = new Blob([svgString], {{ type: 'image/svg+xml;charset=utf-8' }});
                        const url = URL.createObjectURL(svgBlob);
                        
                        const img = new Image();
                        img.onload = function() {{
                            try {{
                                ctx.drawImage(img, 0, 0, width, height);
                                
                                // 使用getImageData方式避免toBlob的跨域问题
                                try {{
                                    const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
                                    const newCanvas = document.createElement('canvas');
                                    const newCtx = newCanvas.getContext('2d');
                                    newCanvas.width = canvas.width;
                                    newCanvas.height = canvas.height;
                                    newCtx.putImageData(imageData, 0, 0);
                                    
                                    newCanvas.toBlob(function(blob) {{
                                        if (blob) {{
                                            downloadBlob(blob, 'flowchart_' + new Date().getTime() + '.png');
                                            resolve(true);
                                        }} else {{
                                            reject('Blob转换失败');
                                        }}
                                    }}, 'image/png', 1.0);
                                }} catch (e) {{
                                    // 如果还是失败，使用toDataURL
                                    const dataUrl = canvas.toDataURL('image/png', 1.0);
                                    downloadDataUrl(dataUrl, 'flowchart_' + new Date().getTime() + '.png');
                                    resolve(true);
                                }}
                            }} catch (error) {{
                                reject('绘制失败: ' + error.message);
                            }} finally {{
                                URL.revokeObjectURL(url);
                            }}
                        }};
                        
                        img.onerror = function() {{
                            URL.revokeObjectURL(url);
                            reject('图像加载失败');
                        }};
                        
                        img.src = url;
                    }});
                }}
                
                function exportAsSVG(svgString) {{
                    try {{
                        const blob = new Blob([svgString], {{ type: 'image/svg+xml;charset=utf-8' }});
                        downloadBlob(blob, 'flowchart_' + new Date().getTime() + '.svg');
                        return true;
                    }} catch (error) {{
                        console.error('SVG导出失败:', error);
                        return false;
                    }}
                }}
                
                function downloadBlob(blob, filename) {{
                    const url = URL.createObjectURL(blob);
                    const link = document.createElement('a');
                    link.href = url;
                    link.download = filename;
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                    setTimeout(() => URL.revokeObjectURL(url), 100);
                }}
                
                function downloadDataUrl(dataUrl, filename) {{
                    const link = document.createElement('a');
                    link.href = dataUrl;
                    link.download = filename;
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                }}
                
                // 执行导出
                exportMermaidImage().then(result => {{
                    if (result) {{
                        console.log('图片导出成功');
                    }} else {{
                        console.error('图片导出失败');
                    }}
                }}).catch(error => {{
                    console.error('导出过程中出错:', error);
                }});
                """
                
                # 执行JavaScript代码
                ui.run_javascript(js_code)
                
                # 给用户反馈
                ui.notify('正在导出图片...', type='info')
                
            except Exception as e:
                ui.notify(f'导出失败: {str(e)}', type='negative')
                print(f"Export error: {e}")
        
        # 创建全屏对话框
        with ui.dialog().props('maximized transition-show="slide-up" transition-hide="slide-down"') as dialog:
            with ui.card().classes('w-full no-shadow bg-white'):
                # 顶部工具栏
                with ui.row().classes('w-full justify-between items-center p-1 bg-gradient-to-r from-blue-500 to-purple-600 text-white'):
                    with ui.row().classes('items-center gap-3'):
                        ui.icon('account_tree', size='md')
                        ui.label('流程图全屏显示').classes('text-xl font-bold')
                    
                    with ui.row().classes('gap-1'):
                        ui.button(
                            icon='download',
                            on_click=export_image
                        ).props('flat round').classes('text-white hover:bg-white/20').tooltip('导出图片')
                        
                        ui.button(
                            icon='close',
                            on_click=close_dialog
                        ).props('flat round').classes('text-white hover:bg-white/20').tooltip('退出全屏')
                
                # 图表容器
                with ui.scroll_area().classes('flex-1 p-6 bg-gray-50'):
                    try:
                        # 重点：为ui.mermaid组件添加一个ID
                        ui.mermaid(mermaid_content).classes('w-full min-h-96 bg-white rounded-lg shadow-sm p-4').props(f'id="{mermaid_id}"')
                    except Exception as e:
                        ui.notify(f"全屏图表渲染失败: {e}", type="warning")
                        with ui.card().classes('w-full bg-white'):
                            ui.label('图表渲染失败，显示源代码:').classes('font-semibold mb-2 text-red-600')
                            ui.code(mermaid_content, language='mermaid').classes('w-full')
        
        # 添加键盘事件监听（ESC键关闭）
        dialog.on('keydown.esc', close_dialog)
        # 打开对话框
        dialog.open()

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