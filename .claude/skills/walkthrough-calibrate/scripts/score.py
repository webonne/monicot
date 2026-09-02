#!/usr/bin/env python3
"""给一次走读打分。
用法：score.py <ledger.json> <seeds.json> [--labels labels.json] [--tolerance 5]
seeds.json: [{"id":"S1","file":"src/x.py","line":42,"lens":"correctness","description":"..."}]
labels.json: {"C-003": true, "C-007": false}   # 人工复核 accepted 是否为真
"""
import argparse
import json
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("ledger")
ap.add_argument("seeds")
ap.add_argument("--labels")
ap.add_argument("--tolerance", type=int, default=5)
a = ap.parse_args()

ledger = json.loads(Path(a.ledger).read_text())
seeds = json.loads(Path(a.seeds).read_text())
if isinstance(seeds, dict):
    seeds = seeds.get("seeds", [])
labels = json.loads(Path(a.labels).read_text()) if a.labels else None
claims = ledger.get("claims", [])


def norm(p):
    return str(p).replace("\\", "/").lstrip("./")


def matches(seed, claim):
    if norm(seed["file"]) != norm(claim["file"]) and not norm(claim["file"]).endswith(norm(seed["file"])):
        return False
    return abs(int(seed["line"]) - int(claim["line"])) <= a.tolerance


def ratio(n, d):
    return f"{n}/{d} = {n/d:.2f}" if d else "n/a"


# 召回：种子被 accepted 命中；另算"被提出但未 accepted"
lines = []
by_lens = {}
hit_acc = hit_any = 0
for s in seeds:
    acc = [c for c in claims if matches(s, c) and c.get("ruling", {}).get("status") == "accepted"]
    anyc = [c for c in claims if matches(s, c)]
    L = by_lens.setdefault(s.get("lens", "?"), {"n": 0, "acc": 0, "raised": 0})
    L["n"] += 1
    if acc:
        hit_acc += 1; L["acc"] += 1
    if anyc:
        hit_any += 1; L["raised"] += 1
    status = "accepted" if acc else ("raised-not-accepted" if anyc else "missed")
    lines.append(f"| {s.get('id','?')} | {s['file']}:{s['line']} | {s.get('lens','?')} | {status} | {', '.join(c['id'] for c in anyc) or '-'} |")

out = []
out.append(f"# 走读打分：{ledger.get('review_id')}\n")
out.append("## 召回")
out.append(f"- 种子数：{len(seeds)}")
out.append(f"- 被 accepted 命中：{ratio(hit_acc, len(seeds))}")
out.append(f"- 被提出（含未 accepted）：{ratio(hit_any, len(seeds))}\n")
out.append("| 镜头 | 种子数 | accepted 召回 | 提出率 |")
out.append("|---|---|---|---|")
for lens, L in sorted(by_lens.items()):
    out.append(f"| {lens} | {L['n']} | {ratio(L['acc'], L['n'])} | {ratio(L['raised'], L['n'])} |")
out.append("")
out.append("| 种子 | 位置 | 镜头 | 结果 | 命中 claim |")
out.append("|---|---|---|---|---|")
out.extend(lines)

# 精确率
accepted = [c for c in claims if c.get("ruling", {}).get("status") == "accepted"]
out.append("\n## 精确率")
if labels is None:
    out.append(f"- accepted 共 {len(accepted)} 条；未提供 --labels，无法算精确率。")
else:
    tp = sum(1 for c in accepted if labels.get(c["id"]) is True)
    labeled = sum(1 for c in accepted if c["id"] in labels)
    out.append(f"- accepted 中人工判真：{ratio(tp, labeled)}（已标注 {labeled}/{len(accepted)}）")
    pl = {}
    for c in accepted:
        if c["id"] in labels:
            L = pl.setdefault(c["lens"], [0, 0]); L[1] += 1; L[0] += 1 if labels[c["id"]] else 0
    for lens, (t, n) in sorted(pl.items()):
        out.append(f"  - {lens}: {ratio(t, n)}")

# 各角色
out.append("\n## 角色")
by_l = {}
for c in claims:
    L = by_l.setdefault(c["lens"], {"claims": 0, "accepted": 0})
    L["claims"] += 1
    L["accepted"] += 1 if c.get("ruling", {}).get("status") == "accepted" else 0
out.append("| 镜头 | claims | accepted | accepted 率 |")
out.append("|---|---|---|---|")
for lens, L in sorted(by_l.items()):
    out.append(f"| {lens} | {L['claims']} | {L['accepted']} | {ratio(L['accepted'], L['claims'])} |")
refutes = [c for c in claims if c.get("defense", {}).get("verdict") == "refute"]
overturned = [c for c in refutes if c.get("verification", {}).get("status") == "confirmed"]
contests = [c for c in claims if c.get("defense", {}).get("verdict") == "contest"]
vs = {}
for c in contests:
    st = c.get("verification", {}).get("status", "none"); vs[st] = vs.get(st, 0) + 1
out.append(f"\n- 辩护方 refute：{len(refutes)}，被验证员推翻：{ratio(len(overturned), len(refutes))}")
out.append(f"- 验证员处理 contest：{len(contests)}，结果分布：{vs}")
out.append(f"- dropped（无失败场景 / 超上限）：{len(ledger.get('dropped', []))}")
out.append(f"- 覆盖缺口：{len(ledger.get('coverage_gaps', []))}，轮次：{ledger.get('round')}，工具调用：{ledger.get('budget', {}).get('used_tool_calls')}")
print("\n".join(out))
