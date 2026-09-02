#!/usr/bin/env python3
"""结束一次走读：汇总工具调用数、设置 status、删除 ACTIVE 标记。
用法：finish.py [--abort] [--review-id ID]
"""
import argparse
import json
from wt_lib import review_dir, load_ledger, save_ledger, root

ap = argparse.ArgumentParser()
ap.add_argument("--abort", action="store_true")
ap.add_argument("--review-id")
a = ap.parse_args()
rdir = review_dir(a.review_id)
ledger = load_ledger(rdir)

used = 0
per_type = {}
log = rdir / "toolcalls.jsonl"
if log.exists():
    for line in log.read_text().splitlines():
        try:
            rec = json.loads(line)
        except Exception:
            continue
        used += 1
        per_type[rec.get("agent_type", "?")] = per_type.get(rec.get("agent_type", "?"), 0) + 1
ledger["budget"]["used_tool_calls"] = used
ledger["budget"]["used_by_agent_type"] = per_type

claims = ledger["claims"]
unruled = [c["id"] for c in claims if "ruling" not in c]
if a.abort:
    ledger["status"] = "aborted"
elif unruled or not (rdir / "report.md").exists():
    ledger["status"] = "partial"
else:
    ledger["status"] = "complete"
save_ledger(rdir, ledger)

marker = root() / "ACTIVE"
if marker.exists() and marker.read_text().strip() == rdir.name:
    marker.unlink()
nag = rdir / ".stop-nagged"
if nag.exists():
    nag.unlink()

summary = {
    "review_id": rdir.name, "status": ledger["status"], "round": ledger["round"],
    "claims": len(claims),
    "accepted": sum(1 for c in claims if c.get("ruling", {}).get("status") == "accepted"),
    "needs_human": sum(1 for c in claims if c.get("ruling", {}).get("status") == "needs_human"),
    "rejected": sum(1 for c in claims if c.get("ruling", {}).get("status") == "rejected"),
    "dropped": len(ledger.get("dropped", [])),
    "coverage_gaps": len(ledger.get("coverage_gaps", [])),
    "tool_calls": used, "tool_calls_by_agent": per_type,
}
print(json.dumps(summary, ensure_ascii=False, indent=2))
