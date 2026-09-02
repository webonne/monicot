#!/usr/bin/env python3
"""SessionStart：提示未完成的走读。"""
from wt_common import read_input, active_review

read_input()
rdir, ledger = active_review()
if rdir is None:
    raise SystemExit(0)
status = (ledger or {}).get("status", "?")
n = len((ledger or {}).get("claims", []))
print(f"有一次未完成的走读：{rdir.name}（status={status}，claims={n}）。用 /walkthrough --resume {rdir.name} 继续，或 python3 .claude/skills/walkthrough/scripts/finish.py --abort 放弃。")
