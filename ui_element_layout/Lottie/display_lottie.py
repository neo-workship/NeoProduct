from nicegui import ui

@ui.page("/")
def main():
    # 1. 引入 Lottie Player 的 JS 脚本
    ui.add_body_html(
        '<script src="https://unpkg.com/@lottiefiles/lottie-player@latest/dist/lottie-player.js"></script>'
    )

    # 2. 加载远程或本地的 .json 动画
    lottie_src = './Loading.json'
    ui.html(f'<lottie-player src="{lottie_src}" loop autoplay style="height: 200px;"></lottie-player>')

    # 启动

if __name__ in {"__main__", "__mp_main__"}:
    ui.run(
        title='弹性布局页面',
        host='0.0.0.0',
        port=8081,
        reload=True,
        show=True
    )