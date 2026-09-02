#!/usr/bin/env python3
"""初始化一次走读。
用法：init_ledger.py --review-id ID --lenses a,b --files f1,f2 [--base X --head Y --test-command "pytest -q"] [--max-rounds 2 --max-tool-calls 400 --max-claims-per-lens 8]
"""
import argparse
import json
from wt_lib import root, LENSES, die, save_ledger

ap = argparse.ArgumentParser()
ap.add_argument("--review-id", required=True)
ap.add_argument("--lenses", required=True)
ap.add_argument("--files", default="")
ap.add_argument("--base")
ap.add_argument("--head")
ap.add_argument("--test-command")
ap.add_argument("--max-rounds", type=int, default=2)
ap.add_argument("--max-tool-calls", type=int, default=400)
ap.add_argument("--max-tool-calls-per-agent", type=int, default=60)
ap.add_argument("--max-tool-calls-per-verifier", type=int, default=20)
ap.add_argument("--max-claims-per-lens", type=int, default=8)
a = ap.parse_args()

lenses = [x.strip() for x in a.lenses.split(",") if x.strip()]
bad = [l for l in lenses if l not in LENSES]
if bad:
    die(f"未知镜头：{bad}，可选：{sorted(LENSES)}")
rdir = root() / a.review_id
if (rdir / "ledger.json").exists():
    die(f"{rdir} 已存在。要继续请用 --resume，要重来请先删掉该目录")
for sub in ("claims", "defense", "verify", "repro"):
    (rdir / sub).mkdir(parents=True, exist_ok=True)
ledger = {
    "review_id": a.review_id,
    "round": 1,
    "status": "in_progress",
    "scope": {
        "base": a.base, "head": a.head,
        "files": [f for f in a.files.split(",") if f],
        "test_command": a.test_command,
        "lenses": lenses,
    },
    "brief_path": str(rdir / "brief.md"),
    "budget": {
        "max_rounds": a.max_rounds,
        "max_tool_calls": a.max_tool_calls,
        "max_tool_calls_per_agent": a.max_tool_calls_per_agent,
        "max_tool_calls_per_verifier": a.max_tool_calls_per_verifier,
        "max_claims_per_lens": a.max_claims_per_lens,
        "used_tool_calls": 0,
    },
    "claims": [],
    "dropped": [],
    "coverage_gaps": [],
    "injection_notes": [],
}
save_ledger(rdir, ledger)
(root() / "ACTIVE").write_text(a.review_id)
print(json.dumps({"review_dir": str(rdir), "ledger": str(rdir / "ledger.json"), "brief_path": ledger["brief_path"]}, ensure_ascii=False))
