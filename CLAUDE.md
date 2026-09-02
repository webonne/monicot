# monicot

对抗式代码走读 agent 体。主编排 + 五个子 agent（走读员 / 攻击方 / 辩护方 / 验证员 / 裁判），设计见 `docs/code-walkthrough-agent-architecture.md`。

## 组成

- `.claude/agents/walkthrough-*.md`：五个子 agent，角色边界在各自 prompt 里，改动前先读 `.claude/rules/walkthrough-roles.md`。
- `.claude/skills/walkthrough/`：`/walkthrough` 主编排；`scripts/` 是唯一允许写 Ledger 的途径。
- `.claude/skills/walkthrough-brief/`：只跑走读员，快速理解一段代码。
- `.claude/skills/walkthrough-publish/`：把一次走读的结果发成 PR review。
- `.claude/skills/walkthrough-calibrate/`：用种子缺陷集算精确率 / 召回率。
- `.claude/hooks/`：确定性护栏（验证员执行边界、Ledger 写保护、预算、未完成提醒）。
- `.claude/rules/`：证据标准与角色不变量。

## 约定

- 走读产物在 `.walkthrough/<review_id>/`，已 gitignore，不提交。
- Ledger（`ledger.json`）只能通过 `python3 .claude/skills/walkthrough/scripts/apply_phase.py` 写入；hook 会拒绝直接 Write/Edit。
- 子 agent 不写文件（验证员除外，且只在自己的 worktree 里写复现）。它们把结果作为最终回复返回，由编排器落盘。
- 报告和简报用中文；claim 字段名用英文。
- 校验：`python3 .claude/skills/walkthrough/scripts/validate_ledger.py <ledger.json>`。
