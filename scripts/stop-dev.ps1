# Windows PowerShell 停止开发环境

Get-Job -Name "rag-service" -ErrorAction SilentlyContinue | Stop-Job -PassThru | Remove-Job
Get-Job -Name "spring-backend" -ErrorAction SilentlyContinue | Stop-Job -PassThru | Remove-Job
Get-Job -Name "vite-frontend" -ErrorAction SilentlyContinue | Stop-Job -PassThru | Remove-Job

Write-Host "所有服务已停止" -ForegroundColor Green
