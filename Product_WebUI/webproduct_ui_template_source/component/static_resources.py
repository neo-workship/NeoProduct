# 解决方案1: 更新static_resources.py，添加CSS加载功能

from nicegui import ui, app
import os
from pathlib import Path
from typing import Optional

class StaticResourceManager:
    """静态资源管理器"""
    
    def __init__(self, static_dir: str = "static"):
        self.static_dir = Path(static_dir)
        self.base_url = "/static"  # 静态文件的URL前缀
        self._ensure_directories()
        self._setup_static_routes()
    
    def _ensure_directories(self):
        """确保静态资源目录存在"""
        directories = [
            self.static_dir / "images" / "logo",
            self.static_dir / "images" / "avatars", 
            self.static_dir / "images" / "icons" / "menu-icons",
            self.static_dir / "images" / "icons" / "header-icons",
            self.static_dir / "css" / "themes",
            self.static_dir / "js" / "components",
            self.static_dir / "fonts" / "custom-fonts"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def _setup_static_routes(self):
        """设置静态文件路由"""
        if self.static_dir.exists():
            # 注册静态文件路由
            app.add_static_files(self.base_url, str(self.static_dir))
    
    def load_css_files(self):
        """加载所有CSS文件到页面"""
        css_files = [
            "css/custom.css",
            "css/themes/light.css", 
            "css/themes/dark.css"
        ]
        
        for css_file in css_files:
            css_path = self.static_dir / css_file
            if css_path.exists():
                # 方法1: 通过URL引用
                css_url = f"{self.base_url}/{css_file}"
                ui.add_head_html(f'<link rel="stylesheet" type="text/css" href="{css_url}">')
                print(f"✅ 已加载CSS: {css_url}")
            else:
                print(f"⚠️  CSS文件不存在: {css_path}")
    
    def load_inline_css(self, css_file: str):
        """将CSS内容内联到页面"""
        css_path = self.static_dir / css_file
        if css_path.exists():
            try:
                with open(css_path, 'r', encoding='utf-8') as f:
                    css_content = f.read()
                ui.add_head_html(f'<style type="text/css">{css_content}</style>')
                print(f"✅ 已内联加载CSS: {css_file}")
                return True
            except Exception as e:
                print(f"❌ 加载CSS失败 {css_file}: {e}")
                return False
        else:
            print(f"⚠️  CSS文件不存在: {css_path}")
            return False
    
    def get_css_url(self, filename: str) -> str:
        """获取CSS文件的URL"""
        return f"{self.base_url}/css/{filename}"
    
    def get_image_path(self, category: str, filename: str) -> str:
        """获取图片路径"""
        return f"{self.base_url}/images/{category}/{filename}"
    
    def get_logo_path(self, filename: str = "robot.svg") -> str:
        """获取Logo路径"""
        return self.get_image_path("logo", filename)
    
    def get_avatar_path(self, filename: str = "default_avatar.png") -> str:
        """获取头像路径"""
        return self.get_image_path("avatars", filename)
    
    def get_icon_path(self, category: str, filename: str) -> str:
        """获取图标路径"""
        return f"{self.base_url}/images/icons/{category}/{filename}"
    
    def get_css_path(self, filename: str) -> str:
        """获取CSS文件路径"""
        return f"{self.base_url}/css/{filename}"
    
    def get_theme_css_path(self, theme: str) -> str:
        """获取主题CSS路径"""
        return f"{self.base_url}/css/themes/{theme}.css"
    
    def get_js_path(self, filename: str) -> str:
        """获取JavaScript文件路径"""
        return f"{self.base_url}/js/{filename}"
    
    def get_font_path(self, filename: str) -> str:
        """获取字体文件路径"""
        return f"{self.base_url}/fonts/custom-fonts/{filename}"
    
    def file_exists(self, file_path: str) -> bool:
        """检查文件是否存在"""
        # 如果是URL路径，转换为本地路径检查
        if file_path.startswith(self.base_url):
            relative_path = file_path.replace(self.base_url + "/", "")
            local_path = self.static_dir / relative_path
        else:
            local_path = Path(file_path)
        return local_path.exists()
    
    def get_fallback_path(self, primary_path: str, fallback_path: str) -> str:
        """获取备用路径（如果主路径不存在）"""
        return primary_path if self.file_exists(primary_path) else fallback_path

# 全局静态资源管理器实例
static_manager = StaticResourceManager()