# Windows PowerShell 一键 Docker 部署

param(
    [switch]$Build,
    [switch]$Down
)

$ROOT = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)

if ($Down) {
    Write-Host "停止并清理容器..." -ForegroundColor Yellow
    docker-compose -f "$ROOT\infra\docker-compose.yml" down --remove-orphans
    return
}

if ($Build) {
    Write-Host "构建镜像..." -ForegroundColor Cyan
    docker-compose -f "$ROOT\infra\docker-compose.yml" build --no-cache
}

Write-Host "启动服务..." -ForegroundColor Cyan
docker-compose -f "$ROOT\infra\docker-compose.yml" up -d

Write-Host ""
Write-Host "=== Docker 部署完成 ===" -ForegroundColor Green
Write-Host "  RAG:      http://localhost:8000/docs"
Write-Host "  Backend:  http://localhost:8081/api/qa/health"
Write-Host "  Frontend: http://localhost:5173"
Write-Host ""
Write-Host "查看日志: docker-compose -f infra\docker-compose.yml logs -f" -ForegroundColor Yellow
Write-Host "停止服务: .\scripts\docker-deploy.ps1 -Down" -ForegroundColor Yellow
