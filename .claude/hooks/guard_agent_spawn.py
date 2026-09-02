#!/usr/bin/env python3
"""PreToolUse(Agent)：验证员必须在 worktree 里跑；走读子 agent 不允许再生子 agent。"""
from wt_common import read_input, deny, is_walkthrough_agent

d = read_input()
ti = d.get("tool_input", {})
sub = str(ti.get("subagent_type", ""))
if is_walkthrough_agent(d):
    deny("走读子 agent 不允许再派生子 agent，把任务在自己上下文里完成")
if sub == "walkthrough-verifier" and ti.get("isolation") != "worktree":
    deny("walkthrough-verifier 必须以 isolation: \"worktree\" 启动")
