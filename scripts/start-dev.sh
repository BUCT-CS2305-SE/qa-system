#!/usr/bin/env bash
# 启动全栈开发环境（需要 Java 17 / Python 3.13 / Node 22）

set -e

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "=== 1/3 启动 RAG 服务（FastAPI :8000） ==="
cd "$ROOT/rag-service-node"
pip install -q -r requirements.txt 2>/dev/null || true
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
RAG_PID=$!

echo "=== 2/3 启动后端网关（Spring Boot :8081） ==="
cd "$ROOT/backend-spring"
mvn spring-boot:run -q &
SPRING_PID=$!

echo "=== 3/3 启动前端（Vite :5173） ==="
cd "$ROOT/web-frontend"
pnpm install --frozen-lockfile 2>/dev/null || true
pnpm dev &
VITE_PID=$!

echo ""
echo "=== 全栈已启动 ==="
echo "  RAG:     http://localhost:8000/docs"
echo "  Backend: http://localhost:8081/api/qa/health"
echo "  Frontend: http://localhost:5173"
echo ""
echo "按 Ctrl+C 停止所有服务"

trap "kill $RAG_PID $SPRING_PID $VITE_PID 2>/dev/null; exit" INT TERM
wait
