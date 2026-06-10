# quality.ps1 — 一键代码质量检查
# 用法: .\scripts\quality.ps1           # 全部检查
#       .\scripts\quality.ps1 -Fast     # 仅 lint + 单元测试
#       .\scripts\quality.ps1 -Frontend # 仅前端
#       .\scripts\quality.ps1 -Backend  # 仅后端
#       .\scripts\quality.ps1 -Python   # 仅 Python

param(
  [switch]$Fast,
  [switch]$Frontend,
  [switch]$Backend,
  [switch]$Python
)

$ErrorActionPreference = "Continue"
$repoRoot = Split-Path -Parent $PSScriptRoot
$pass = 0
$fail = 0
$results = @()

$all = !$Frontend -and !$Backend -and !$Python

function Run-Step($label, $workdir, $cmd, $desc) {
  Write-Host "`n==== $label : $desc ====" -ForegroundColor Cyan
  Push-Location (Join-Path $repoRoot $workdir)
  try {
    Invoke-Expression $cmd
    if ($LASTEXITCODE -eq 0) {
      Write-Host "[PASS] $label" -ForegroundColor Green
      $script:pass++
      $script:results += "  PASS  $label"
    } else {
      Write-Host "[FAIL] $label (exit code $LASTEXITCODE)" -ForegroundColor Red
      $script:fail++
      $script:results += "  FAIL  $label"
    }
  } catch {
    Write-Host "[FAIL] $label : $_" -ForegroundColor Red
    $script:fail++
    $script:results += "  FAIL  $label"
  } finally {
    Pop-Location
  }
}

# ── Frontend ──
if ($all -or $Frontend) {
  Run-Step "Frontend Lint"   "web-frontend" "pnpm lint"           "ESLint"
  Run-Step "Frontend Test"   "web-frontend" "pnpm test"           "Vitest"
}

# ── Backend (Java) ──
if ($all -or $Backend) {
  Run-Step "Backend Test"    "backend-spring" "mvn test -Dcheckstyle.skip=true -q"   "JUnit + JaCoCo"
}

# ── Python (RAG) ──
if ($all -or $Python) {
  Run-Step "Python Lint"     "rag-service-node" "ruff check ."                   "Ruff"
  Run-Step "Python Format"   "rag-service-node" "ruff format --check ."           "Ruff format"
  Run-Step "Python Test"     "rag-service-node" "python -m pytest tests/test_pipeline.py tests/test_regression.py -v --tb=short" "pytest"
}

# ── Python Integration (skip in Fast mode) ──
if (!$Fast -and ($all -or $Python)) {
  Run-Step "Python Integration" "rag-service-node" "python -m pytest tests/test_integration.py -v --tb=short 2>&1" "pytest (real KG)"
}

# ── Summary ──
Write-Host "`n==============================" -ForegroundColor Cyan
Write-Host "  Quality Check Summary" -ForegroundColor Cyan
Write-Host "==============================" -ForegroundColor Cyan
foreach ($r in $results) { Write-Host $r }
Write-Host "------------------------------"
Write-Host "Total: PASS=$pass  FAIL=$fail" -ForegroundColor $(if ($fail -eq 0) { "Green" } else { "Red" })
exit $fail
