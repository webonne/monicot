#!/usr/bin/env python3
"""PreToolUse(Write|Edit)：ledger.json 只能由 apply_phase.py 写。"""
from wt_common import read_input, deny

d = read_input()
path = str(d.get("tool_input", {}).get("file_path", ""))
if path.endswith("ledger.json") and "/.walkthrough/" in path.replace("\\", "/") + "/":
    deny("ledger.json 不允许直接编辑。用 python3 .claude/skills/walkthrough/scripts/apply_phase.py --phase <attack|defense|verify|judge> --input <file>")
if path.endswith("/toolcalls.jsonl"):
    deny("toolcalls.jsonl 由 hook 维护，不允许编辑")
