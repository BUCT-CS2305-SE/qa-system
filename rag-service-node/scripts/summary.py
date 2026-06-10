"""回归测试汇总：提取 pytest 输出中的 pass/fail 计数并输出通过率。"""

import re
import subprocess
import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent  # rag-service-node/
files = ["tests/test_pipeline.py", "tests/test_regression.py"]
total_pass = 0
total_fail = 0

for f in files:
    r = subprocess.run(
        [sys.executable, "-m", "pytest", f, "--tb=no", "-q"], capture_output=True, text=True, cwd=str(root)
    )
    out = r.stdout + r.stderr
    m_pass = re.search(r"(\d+) passed", out)
    m_fail = re.search(r"(\d+) failed", out)
    p = int(m_pass.group(1)) if m_pass else 0
    f_cnt = int(m_fail.group(1)) if m_fail else 0
    print(f"  {f}: {p} passed, {f_cnt} failed")
    total_pass += p
    total_fail += f_cnt

total = total_pass + total_fail
rate = round(total_pass * 100 / total, 1) if total > 0 else 0
print(f"\nTotal: {total} | Passed: {total_pass} | Failed: {total_fail} | Rate: {rate}%")
sys.exit(0 if total_fail == 0 else 1)
