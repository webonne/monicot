#!/usr/bin/env python3
"""Stop：走读进行中且没有报告时，阻止主 agent 停下来。每个 review 只拦一次，避免死循环。"""
import sys
from wt_common import read_input, active_review

d = read_input()
if d.get("agent_type"):
    raise SystemExit(0)  # 子 agent 的 Stop 不管
if d.get("stop_hook_active"):
    raise SystemExit(0)
rdir, ledger = active_review()
if rdir is None:
    raise SystemExit(0)
nag = rdir / ".stop-nagged"
if (rdir / "report.md").exists() or nag.exists():
    raise SystemExit(0)
nag.write_text("1")
print(f"走读 {rdir.name} 还没有 report.md。继续按 /walkthrough 协议跑完剩余阶段；如果确实要中止，运行 python3 .claude/skills/walkthrough/scripts/finish.py --abort 并说明原因", file=sys.stderr)
sys.exit(2)
