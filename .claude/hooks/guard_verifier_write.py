#!/usr/bin/env python3
"""PreToolUse(Write|Edit)：验证员只能新增测试文件或复现脚本，不能改业务代码。"""
import re
from pathlib import Path
from wt_common import read_input, deny

d = read_input()
if d.get("agent_type") != "walkthrough-verifier":
    raise SystemExit(0)
path = str(d.get("tool_input", {}).get("file_path", ""))
if not path:
    raise SystemExit(0)
p = Path(path)
parts = [x.lower() for x in p.parts]
name = p.name.lower()
ok = (
    ".walkthrough" in parts
    or any(x in ("tests", "test", "__tests__", "spec", "specs", "repro") for x in parts)
    or name.startswith("test_")
    or re.search(r"(_test|\.test|\.spec|_spec)\.[a-z]+$", name) is not None
    or name.startswith("repro_")
)
if not ok:
    deny(f"验证员不允许修改业务代码：{path}。只能新增 tests/ 下的测试、test_*/ *_test.* 文件或 repro_* 脚本。若必须改业务代码才能复现，报 inconclusive 并说明原因")
if d.get("tool_name") == "Edit" and p.exists():
    # 允许编辑自己新建的文件；已有测试文件不允许改（防止改 fixture 让复现通过）
    try:
        import subprocess
        tracked = subprocess.run(["git", "ls-files", "--error-unmatch", str(p)], cwd=d.get("cwd"), capture_output=True).returncode == 0
    except Exception:
        tracked = False
    if tracked:
        deny(f"验证员不允许修改已有测试文件 {p.name}（防止改 fixture 让复现通过）。请新建文件")
