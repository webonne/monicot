#!/usr/bin/env python3
"""PreToolUse(*)：预算门。PostToolUse(*)：计数。只对 walkthrough-* 子 agent 生效。"""
import json
import time
from wt_common import read_input, deny, active_review, is_walkthrough_agent

d = read_input()
if not is_walkthrough_agent(d):
    raise SystemExit(0)
rdir, ledger = active_review()
if rdir is None:
    raise SystemExit(0)
log = rdir / "toolcalls.jsonl"
event = d.get("hook_event_name")
agent_type = d.get("agent_type", "")
agent_id = d.get("agent_id", "")

if event == "PostToolUse":
    with open(log, "a") as f:
        f.write(json.dumps({"t": time.time(), "agent_type": agent_type, "agent_id": agent_id, "tool": d.get("tool_name")}) + "\n")
    raise SystemExit(0)

if event == "PreToolUse" and ledger:
    total = 0
    mine = 0
    if log.exists():
        for line in log.read_text().splitlines():
            try:
                rec = json.loads(line)
            except Exception:
                continue
            total += 1
            if rec.get("agent_id") == agent_id:
                mine += 1
    budget = ledger.get("budget", {})
    max_total = int(budget.get("max_tool_calls", 400))
    per_agent = int(budget.get("max_tool_calls_per_agent", 60))
    if agent_type == "walkthrough-verifier":
        per_agent = int(budget.get("max_tool_calls_per_verifier", 20))
    if total >= max_total:
        deny(f"本次走读总预算已耗尽（{total}/{max_total}）。立即停止调用工具，用已有信息输出结论；未完成的部分标 inconclusive 或说明未检查")
    if mine >= per_agent:
        deny(f"你的工具调用预算已耗尽（{mine}/{per_agent}）。立即停止调用工具，用已有信息输出结论；验证员报 inconclusive 并写明卡点")
