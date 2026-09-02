---
name: walkthrough-calibrate
description: 用种子缺陷集给走读打分：召回率（按镜头）、精确率（需人工标注）、验证员有效率、辩护方误反驳率。用于决定镜头集、条数上限、effort，以及证明每个角色的价值。
argument-hint: "<review_id> <seeds.json> [--labels labels.json]"
disable-model-invocation: true
allowed-tools: Bash(python3 ${CLAUDE_PROJECT_DIR}/.claude/skills/walkthrough-calibrate/scripts/*) Bash(python3 .claude/skills/walkthrough-calibrate/scripts/*) Bash(cat *)
---

给走读 `$0` 打分，种子文件 `$1`。

1. 种子文件格式见 `${CLAUDE_SKILL_DIR}/seeds/README.md`。没有种子文件就先按 README 建一个：取 3 到 5 个历史 PR，每个人工注入 2 到 4 个缺陷，记录 file / line / lens / description。
2. 运行：
   ```
   python3 ${CLAUDE_SKILL_DIR}/scripts/score.py .walkthrough/$0/ledger.json $1 [--labels labels.json] [--tolerance 5]
   ```
   `labels.json` 是人工复核结果 `{"C-003": true, "C-007": false}`，没有就不算精确率。
3. 把脚本输出的表格原样给用户，然后**只**做这几类判断，每条都引用表里的数字：
   - 某镜头召回率低于 0.6：该镜头的攻击方 prompt 需要改，或该类种子缺陷不在镜头定义里。
   - 辩护方误反驳率高于 0.3：辩护方在洗白，收紧 refute 的证据要求。
   - 验证员 inconclusive 占比高于 0.5：环境问题优先于 prompt 问题，先看 test_command。
   - 精确率低于 0.5：攻击方条数上限该降，或裁判对 concede-unverified 应改为 needs_human。
4. 做消融时（关掉辩护 / 验证 / 第二轮再跑），用同一份种子，把多次 score 结果并排列出。

不要因为一次跑分就改 prompt；至少两个不同 PR 的种子集上出现同样的结论再改。
