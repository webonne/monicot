# 种子缺陷集

一个种子文件对应一次走读目标（一个 PR 或一个 diff）。格式：

```json
{
  "target": "main..seeded/pr-128",
  "seeds": [
    {
      "id": "S1",
      "file": "src/order/service.py",
      "line": 88,
      "lens": "concurrency",
      "description": "去掉了 deduct() 前的幂等键校验，超时重试会重复扣减",
      "injected_by": "手工",
      "expected_severity": "high"
    }
  ]
}
```

规则：

- 一个种子只对应一个根因，`line` 指向根因所在行，不是症状行。
- `lens` 必须是五个镜头之一，这样才能按镜头算召回。
- 注入方式：改边界条件（`<` 变 `<=`）、去掉一次校验、去掉锁或事务、吞掉异常、改默认值、改序列化字段名。每种至少一个。
- 注入后把分支推到 `seeded/<name>`，走读时用 `main..seeded/<name>`。
- 不要把种子文件放进被走读的分支里。
- 打分时 `--tolerance` 默认 5 行；重构过的文件可以放宽到 10。

`example.json` 是一个可直接用来测 score.py 的样例。
