# 运行回归测试
python -m pytest tests/test_pipeline.py -v

# 跑完显示简要结论
$exitCode = $LASTEXITCODE
if ($exitCode -eq 0) {
    Write-Host "`n=== 回归测试全部通过 ===" -ForegroundColor Green
} else {
    Write-Host "`n=== 回归测试失败（退出码: $exitCode） ===" -ForegroundColor Red
}
exit $exitCode
