#!/usr/bin/env python3
"""PreToolUse(Bash)：验证员的执行边界。不 push、不联网、不装依赖、不碰主 checkout。"""
import re
from wt_common import read_input, deny

d = read_input()
if d.get("agent_type") != "walkthrough-verifier":
    raise SystemExit(0)
cmd = str(d.get("tool_input", {}).get("command", ""))

RULES = [
    (r"\bgit\s+push\b", "验证员不允许 git push"),
    (r"\bgit\s+(remote|fetch\s+--all)\b", "验证员不允许操作远端"),
    (r"\b(curl|wget|nc|ncat|ssh|scp|rsync)\b", "验证员不允许访问网络"),
    (r"\b(pip|pip3|uv|poetry|pipx)\s+install\b", "验证员不允许安装依赖；用仓库现有环境，装不上就报 inconclusive"),
    (r"\b(npm|pnpm|yarn)\s+(install|add|i)\b", "验证员不允许安装依赖；用仓库现有环境，装不上就报 inconclusive"),
    (r"\b(cargo|go)\s+(install|get)\b", "验证员不允许安装依赖"),
    (r"\bapt(-get)?\s+install\b|\bbrew\s+install\b", "验证员不允许安装系统包"),
    (r"\brm\s+-rf\s+(/|~|\.\.|\$HOME)", "验证员不允许删除工作区之外的内容"),
    (r"\bgit\s+(reset\s+--hard|clean\s+-[a-z]*f|checkout\s+--\s+\.)", "验证员不允许丢弃工作区改动；复现失败直接报告"),
    (r"--no-verify|\bSKIP=|\bpytest\.skip\b|\.skip\(|@skip\b|xfail", "验证员不允许跳过或标记测试；复现不成立就报 refuted"),
]
for pat, why in RULES:
    if re.search(pat, cmd):
        deny(f"{why}。被拦截的命令：{cmd[:160]}")
