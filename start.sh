#!/bin/bash
# 热点聚合后端启动脚本
# 用法: ./start.sh

HERE="$(cd "$(dirname "$0")" && pwd)"
cd "$HERE"

# 尝试找可用的 Python 环境
if [ -f "venv2/bin/python3" ]; then
    PY="venv2/bin/python3"
elif [ -f "venv/bin/python3" ]; then
    PY="venv/bin/python3"
else
    # 使用系统 python3（会检查依赖）
    PY="python3"
fi

echo "使用 Python: $($PY --version)"
echo "启动 API 服务器 (端口 8000)..."
echo "  GET  http://localhost:8000    — 服务信息"
echo "  GET  http://localhost:8000/hot — 所有热点"
echo ""

$PY -m uvicorn server:app --host 0.0.0.0 --port 8000 --reload
