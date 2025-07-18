#!/bin/bash

# Streamlit应用管理脚本
# 用于管理Streamlit多页面应用的启动、停止、重启等操作

# 配置参数
APP_NAME="qizhan_app"
STREAMLIT_FILE="系统主页.py"  # 主入口文件
STREAMLIT_PORT=8085
STREAMLIT_HOST="0.0.0.0"
PID_FILE="/tmp/${APP_NAME}.pid"
LOG_FILE="/tmp/${APP_NAME}.log"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_message() {
    local color=$1
    local message=$2
    echo -e "${color}[$(date '+%Y-%m-%d %H:%M:%S')] ${message}${NC}"
}

# 检查Streamlit是否已安装
check_streamlit() {
    if ! command -v streamlit &> /dev/null; then
        print_message $RED "错误: Streamlit未安装，请先安装: pip install streamlit"
        exit 1
    fi
}

# 检查应用文件是否存在
check_app_file() {
    if [ ! -f "$STREAMLIT_FILE" ]; then
        print_message $RED "错误: 找不到应用文件 $STREAMLIT_FILE"
        exit 1
    fi
}

# 获取应用进程ID
get_pid() {
    if [ -f "$PID_FILE" ]; then
        cat "$PID_FILE"
    else
        echo ""
    fi
}

# 检查应用是否正在运行
is_running() {
    local pid=$(get_pid)
    if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
        return 0
    else
        return 1
    fi
}

# 启动应用
start_app() {
    print_message $BLUE "正在启动应用..."
    
    check_streamlit
    check_app_file
    
    if is_running; then
        print_message $YELLOW "应用已在运行中 (PID: $(get_pid))"
        return 0
    fi
    
    # 创建日志文件
    touch "$LOG_FILE"
    
    # 启动Streamlit应用
    nohup streamlit run "$STREAMLIT_FILE" \
        --server.port="$STREAMLIT_PORT" \
        --server.address="$STREAMLIT_HOST" \
        --server.headless=true \
        --browser.gatherUsageStats=false \
        --server.enableCORS=false \
        --server.enableXsrfProtection=false \
        > "$LOG_FILE" 2>&1 &
    
    # 保存进程ID
    echo $! > "$PID_FILE"
    
    # 等待应用启动
    sleep 3
    
    if is_running; then
        print_message $GREEN "应用启动成功!"
        print_message $GREEN "PID: $(get_pid)"
        print_message $GREEN "访问地址: http://$STREAMLIT_HOST:$STREAMLIT_PORT"
        print_message $GREEN "日志文件: $LOG_FILE"
    else
        print_message $RED "应用启动失败，请检查日志文件: $LOG_FILE"
        return 1
    fi
}

# 停止应用
stop_app() {
    print_message $BLUE "正在停止应用..."
    
    if ! is_running; then
        print_message $YELLOW "应用未在运行"
        return 0
    fi
    
    local pid=$(get_pid)
    print_message $BLUE "正在停止进程 (PID: $pid)..."
    
    # 尝试优雅停止
    kill "$pid" 2>/dev/null
    
    # 等待进程停止
    local count=0
    while [ $count -lt 10 ] && is_running; do
        sleep 1
        count=$((count + 1))
    done
    
    # 如果进程仍在运行，强制停止
    if is_running; then
        print_message $YELLOW "正在强制停止进程..."
        kill -9 "$pid" 2>/dev/null
        sleep 2
    fi
    
    if ! is_running; then
        print_message $GREEN "应用已停止"
        rm -f "$PID_FILE"
    else
        print_message $RED "无法停止应用"
        return 1
    fi
}

# 重启应用
restart_app() {
    print_message $BLUE "正在重启应用..."
    stop_app
    sleep 2
    start_app
}

# 查看应用状态
status_app() {
    if is_running; then
        local pid=$(get_pid)
        print_message $GREEN "应用正在运行"
        print_message $GREEN "PID: $pid"
        print_message $GREEN "访问地址: http://$STREAMLIT_HOST:$STREAMLIT_PORT"
        print_message $GREEN "日志文件: $LOG_FILE"
        
        # 显示进程信息
        if command -v ps &> /dev/null; then
            echo -e "\n${BLUE}进程信息:${NC}"
            ps -p "$pid" -o pid,ppid,pcpu,pmem,etime,cmd --no-headers
        fi
    else
        print_message $RED "应用未运行"
        return 1
    fi
}

# 查看日志
show_logs() {
    if [ -f "$LOG_FILE" ]; then
        print_message $BLUE "显示应用日志 (按Ctrl+C退出):"
        tail -f "$LOG_FILE"
    else
        print_message $RED "日志文件不存在: $LOG_FILE"
    fi
}

# 清理日志
clean_logs() {
    if [ -f "$LOG_FILE" ]; then
        > "$LOG_FILE"
        print_message $GREEN "日志文件已清理"
    else
        print_message $YELLOW "日志文件不存在"
    fi
}

# 显示帮助信息
show_help() {
    echo -e "${BLUE}Streamlit应用管理脚本${NC}"
    echo -e "${BLUE}========================${NC}"
    echo ""
    echo "用法: $0 [命令]"
    echo ""
    echo "可用命令:"
    echo "  start     启动应用"
    echo "  stop      停止应用"
    echo "  restart   重启应用"
    echo "  status    查看应用状态"
    echo "  logs      查看应用日志"
    echo "  clean     清理日志文件"
    echo "  help      显示帮助信息"
    echo ""
    echo "配置参数:"
    echo "  应用名称: $APP_NAME"
    echo "  应用文件: $STREAMLIT_FILE"
    echo "  运行端口: $STREAMLIT_PORT"
    echo "  绑定地址: $STREAMLIT_HOST"
    echo "  PID文件: $PID_FILE"
    echo "  日志文件: $LOG_FILE"
    echo ""
    echo "示例:"
    echo "  $0 start    # 启动应用"
    echo "  $0 status   # 查看状态"
    echo "  $0 logs     # 查看日志"
}

# 主程序
main() {
    case "${1:-help}" in
        start)
            start_app
            ;;
        stop)
            stop_app
            ;;
        restart)
            restart_app
            ;;
        status)
            status_app
            ;;
        logs)
            show_logs
            ;;
        clean)
            clean_logs
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            print_message $RED "未知命令: $1"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# 执行主程序
main "$@"