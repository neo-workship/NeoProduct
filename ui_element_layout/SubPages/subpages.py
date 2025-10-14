from nicegui import ui
from uuid import uuid4

@ui.page('/')
def root():
    # ui.page 装饰器将这个函数注册为应用的根路由 '/'
    
    # 这里的 ID 仍然只在页面首次加载时生成一次
    ui.label(f'This ID {str(uuid4())[:6]} changes only on reload.')
    ui.separator()
    
    # ui.sub_pages 现在在 ui.page 装饰的函数中调用，
    # 确保它运行在一个私有客户端上下文中。
    ui.sub_pages({'/': main, '/other': other})

def main():
    ui.label('Main page content')
    # 链接路径是相对于当前 sub_pages 的根路径 '/'
    ui.link('Go to other page', 'other') 

def other():
    ui.label('Another page content')
    ui.link('Go to main page', '/')

# 只需要运行，NiceGUI 会自动找到所有 @ui.page 装饰的函数
# ui.run()

if __name__ in {"__main__", "__mp_main__"}:
    ui.run(
        title='弹性布局页面',
        host='0.0.0.0',
        port=8001,
        reload=True,
        show=True
    )