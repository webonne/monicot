---
paths:
  - ".claude/agents/walkthrough-*.md"
  - ".claude/skills/walkthrough*/**"
  - ".claude/hooks/**"
---

# 修改走读 agent 体时的不变量

改 prompt、skill、hook 之前对照这份清单。任何一条被打破，对抗结构就失效。

- 走读员不判断对错。它的输出是简报和热点，不是问题。
- 攻击方一个实例只看一个镜头，第一轮看不到辩护输出。每镜头有条数上限。
- 辩护方只看 claim 字段，不看攻击方推理；可以读测试，不能运行。
- 验证员是唯一有 Bash 写权限的角色，必须 `isolation: worktree`，不 push、不联网、不改业务代码。
- 裁判只有 Read，且只读 Ledger 和简报，不读代码，不新增 claim。
- 主编排不产生 claim，不读代码下判断。它只调度、落盘、校验、控预算。
- Ledger 只能通过 `scripts/apply_phase.py` 写入。不要给任何 agent 或 skill 直接编辑 Ledger 的路径。
- 最多两轮。第二轮只针对裁判给出的覆盖缺口。
- 子 agent 的输出契约（JSON 字段）改了，必须同步改 `docs/walkthrough-ledger.schema.json`、`validate_ledger.py`、`apply_phase.py`。
- 不要为了"更全面"给攻击方加镜头或去掉条数上限。先用 `/walkthrough-calibrate` 证明召回率不够。
- hook 脚本只用标准库，退出码 2 表示阻断，stderr 是给 agent 看的理由。
