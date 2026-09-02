---
paths:
  - ".walkthrough/**"
---

# 走读产物目录规则

- `ledger.json` 不手改。用 `python3 .claude/skills/walkthrough/scripts/apply_phase.py --phase <attack|defense|verify|judge> ...`。
- `brief.md`、`report.md`、`claims/*.json`、`defense/*.json`、`verify/*.json`、`judge.json` 由编排器根据子 agent 的最终回复落盘，内容原样保存，不润色。
- `repro/` 里是验证员的复现文件副本，只读。
- `toolcalls.jsonl` 由 hook 追加，不编辑。
- `ACTIVE` 文件存在表示走读进行中；`finish.py` 负责删除，不手删。
- 这个目录不提交到 git。
