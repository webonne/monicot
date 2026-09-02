---
name: walkthrough-brief
description: 只跑走读员，快速产出一段代码或一个 diff 的走读简报（意图、变更地图、不变量、风险热点），不做审查。适合"先帮我看懂这段改动"。
argument-hint: "<base..head | PR号 | 路径>"
allowed-tools: Bash(git diff *) Bash(git log *) Bash(git rev-parse *) Bash(mkdir *)
---

对 `$ARGUMENTS` 做只读走读。

1. 解析目标（base..head / PR 号 / 路径），用 `git diff --name-only` 拿文件列表。
2. 调用 `walkthrough-reader`，给它范围，要求把简报作为最终回复返回。
3. 把简报原样输出给用户；若用户后续要完整走读，提示 `/walkthrough <同样的目标>`，简报可以复用（写到 `.walkthrough/<id>/brief.md` 后用 `--resume`）。

不要自己补充审查意见。这个 skill 的产出只有简报。
