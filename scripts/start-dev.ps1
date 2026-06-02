# Windows PowerShell 开发环境启动脚本
# 需要 Java 17 / Python 3.13 / Node 22 / pnpm

$ErrorActionPreference = "Stop"
$ROOT = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)

Write-Host "=== 1/3 启动 RAG 服务（FastAPI :8000） ===" -ForegroundColor Cyan
$ragJob = Start-Job -Name "rag-service" -ScriptBlock {
    param($root)
    Set-Location "$root\rag-service-node"
    pip install -q -r requirements.txt 2>$null
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
} -ArgumentList $ROOT

Write-Host "=== 2/3 启动后端网关（Spring Boot :8081） ===" -ForegroundColor Cyan
$springJob = Start-Job -Name "spring-backend" -ScriptBlock {
    param($root)
    Set-Location "$root\backend-spring"
    mvn spring-boot:run -q
} -ArgumentList $ROOT

Write-Host "=== 3/3 启动前端（Vite :5173） ===" -ForegroundColor Cyan
$viteJob = Start-Job -Name "vite-frontend" -ScriptBlock {
    param($root)
    Set-Location "$root\web-frontend"
    pnpm install --frozen-lockfile 2>$null
    pnpm dev
} -ArgumentList $ROOT

Write-Host ""
Write-Host "=== 全栈已启动 ===" -ForegroundColor Green
Write-Host "  RAG:      http://localhost:8000/docs"
Write-Host "  Backend:  http://localhost:8081/api/qa/health"
Write-Host "  Frontend: http://localhost:5173"
Write-Host ""
Write-Host "运行 .\scripts\stop-dev.ps1 停止所有服务" -ForegroundColor Yellow
Write-Host "查看日志：" -ForegroundColor Yellow
Write-Host "  Get-Job -Name rag-service | Receive-Job"
Write-Host "  Get-Job -Name spring-backend | Receive-Job"
Write-Host "  Get-Job -Name vite-frontend | Receive-Job"
