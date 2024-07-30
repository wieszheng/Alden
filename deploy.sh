#!/bin/bash

# 定义变量
COMPOSE_FILE="docker-compose.yaml"
ACTION="$1"

# 检查 docker 和 docker-compose 是否已安装
command -v docker > /dev/null 2>&1 || { echo "Docker not found. Please install Docker before proceeding."; exit 1; }
command -v docker-compose > /dev/null 2>&1 || { echo "Docker Compose not found. Please install Docker Compose before proceeding."; exit 1; }

# 自动部署功能函数
function deploy() {
    echo "Deploying with docker-compose..."

    # 构建服务（可选，取决于是否需要重新构建镜像）
    docker-compose build --no-cache

    # 启动服务
    echo "Starting services..."
    docker-compose up -d

    echo "Deployment completed."
}

# 停止并删除所有容器及网络（清理环境）
function teardown() {
    echo "Tearing down the environment..."

    docker-compose down --remove-orphans

    echo "Environment teardown completed."
}

# 根据传入的参数执行相应操作
case $ACTION in
    "deploy")
        deploy
        ;;
    "teardown")
        teardown
        ;;
    *)
        echo "Usage: $0 [deploy|teardown]"
        exit 1
        ;;
esac

exit 0
