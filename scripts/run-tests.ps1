# Run full regression test suite (unit tests + 33-item question set)
# Usage: .\scripts\run-tests.ps1

$ErrorActionPreference = "Continue"
Push-Location (Join-Path $PSScriptRoot "..\rag-service-node")

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  qa-system Regression Tests" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# -- 1. Unit tests --
Write-Host ""
Write-Host "[1/2] Unit tests (19 cases)" -ForegroundColor Yellow
python -m pytest tests/test_pipeline.py -v --tb=short
$unitExit = $LASTEXITCODE

# -- 2. Regression question set --
Write-Host ""
Write-Host "[2/2] Regression set (36 cases)" -ForegroundColor Yellow
python -m pytest tests/test_regression.py -v --tb=short
$regrExit = $LASTEXITCODE

# -- Summary --
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
python scripts/summary.py
$summaryExit = $LASTEXITCODE

Pop-Location

if ($unitExit -ne 0 -or $regrExit -ne 0 -or $summaryExit -ne 0) {
    Write-Host ""
    Write-Host "*** Tests FAILED ***" -ForegroundColor Red
    exit 1
} else {
    Write-Host ""
    Write-Host "*** All tests PASSED ***" -ForegroundColor Green
    exit 0
}
