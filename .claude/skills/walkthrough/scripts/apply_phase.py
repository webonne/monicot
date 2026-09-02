#!/usr/bin/env python3
"""把某个阶段的子 agent 输出并入 Ledger。这是唯一允许写 Ledger 的途径，按阶段只写自己的字段。

用法：
  apply_phase.py --phase attack  --input claims/correctness.json [claims/security.json ...]
  apply_phase.py --phase defense --input defense/batch-1.json [...]
  apply_phase.py --phase verify  --input verify/C-003.json [...]
  apply_phase.py --phase judge   --input judge.json
  apply_phase.py --phase round2                       # 进入第二轮
  apply_phase.py --phase note --text "..."            # 记录 injection_notes
可选：--review-id ID（默认读 ACTIVE）
"""
import argparse
from wt_lib import (review_dir, load_ledger, save_ledger, load_json, next_id, die,
                    VERDICTS, VSTATUS, RSTATUS, SEVERITIES)

ap = argparse.ArgumentParser()
ap.add_argument("--phase", required=True, choices=["attack", "defense", "verify", "judge", "round2", "note"])
ap.add_argument("--input", nargs="*", default=[])
ap.add_argument("--text")
ap.add_argument("--review-id")
a = ap.parse_args()

rdir = review_dir(a.review_id)
ledger = load_ledger(rdir)
report = []


def find(cid):
    for c in ledger["claims"]:
        if c["id"] == cid:
            return c
    return None


if a.phase == "attack":
    cap = int(ledger["budget"].get("max_claims_per_lens", 8))
    for path in a.input:
        data = load_json(path)
        if isinstance(data, dict) and "claims" in data:
            data = data["claims"]
        if not isinstance(data, list):
            die(f"{path} 不是 claim 数组")
        kept = 0
        for raw in data:
            lens = raw.get("lens")
            missing = [k for k in ("file", "line", "title", "failure_scenario", "evidence") if not raw.get(k)]
            if missing or len(str(raw.get("failure_scenario", ""))) < 20:
                ledger["dropped"].append({"lens": lens or "?", "title": raw.get("title", "?"), "reason": f"缺少 {missing or ['具体失败场景']}"})
                continue
            if raw.get("severity") not in SEVERITIES:
                raw["severity"] = "medium"
            try:
                raw["confidence"] = min(1.0, max(0.0, float(raw.get("confidence", 0.5))))
            except Exception:
                raw["confidence"] = 0.5
            if kept >= cap:
                ledger["dropped"].append({"lens": lens or "?", "title": raw["title"], "reason": f"超过每镜头上限 {cap}"})
                continue
            claim = {
                "id": f"C-{next_id(ledger):03d}",
                "round": ledger["round"],
                "lens": lens,
                "file": raw["file"],
                "line": int(raw["line"]),
                "title": raw["title"],
                "failure_scenario": raw["failure_scenario"],
                "severity": raw["severity"],
                "confidence": raw["confidence"],
                "evidence": list(raw["evidence"]) if isinstance(raw["evidence"], list) else [str(raw["evidence"])],
            }
            ledger["claims"].append(claim)
            kept += 1
        report.append(f"{path}: 收录 {kept}")

elif a.phase == "defense":
    for path in a.input:
        data = load_json(path)
        if isinstance(data, dict):
            data = [data]
        for d in data:
            c = find(d.get("id"))
            if not c:
                report.append(f"忽略未知 claim {d.get('id')}")
                continue
            verdict = d.get("verdict")
            refs = [r for r in d.get("refs", []) if r]
            note = None
            if verdict not in VERDICTS:
                verdict, note = "contest", "verdict 非法，按 contest 处理"
            elif verdict == "refute" and not refs:
                verdict, note = "contest", "refute 没有 refs，降为 contest"
            c["defense"] = {"verdict": verdict, "evidence": d.get("evidence") or "(无)", "refs": refs, "related": d.get("related", [])}
            if note:
                c["defense"]["note"] = note
            report.append(f"{c['id']}: {verdict}" + (f"（{note}）" if note else ""))

elif a.phase == "verify":
    for path in a.input:
        data = load_json(path)
        if isinstance(data, dict):
            data = [data]
        for v in data:
            c = find(v.get("id"))
            if not c:
                report.append(f"忽略未知 claim {v.get('id')}")
                continue
            status = v.get("status") if v.get("status") in VSTATUS else "inconclusive"
            c["verification"] = {k: v[k] for k in ("method", "artifact", "observed", "severity_adjustment", "notes") if v.get(k)}
            c["verification"]["status"] = status
            report.append(f"{c['id']}: {status}")

elif a.phase == "judge":
    if len(a.input) != 1:
        die("judge 阶段只接受一个输入文件")
    j = load_json(a.input[0])
    for r in j.get("rulings", []):
        c = find(r.get("id"))
        if not c:
            report.append(f"忽略未知 claim {r.get('id')}")
            continue
        status = r.get("status")
        if status not in RSTATUS:
            die(f"{c['id']} ruling.status 非法：{status}")
        c["ruling"] = {"status": status, "rationale": r.get("rationale") or "(无)"}
        if r.get("final_severity") in SEVERITIES:
            c["ruling"]["final_severity"] = r["final_severity"]
        if r.get("unverified"):
            c["ruling"]["unverified"] = True
        if r.get("merged_into"):
            c["merged_into"] = r["merged_into"]
        report.append(f"{c['id']}: {status}")
    ledger["coverage_gaps"] = [g for g in j.get("coverage_gaps", []) if g.get("hotspot") and g.get("reason")]
    if j.get("calibration"):
        ledger["calibration"] = j["calibration"]
    unruled = [c["id"] for c in ledger["claims"] if "ruling" not in c]
    if unruled:
        report.append(f"警告：未裁决的 claim：{unruled}")

elif a.phase == "round2":
    if ledger["round"] != 1:
        die("已经是第二轮")
    if not ledger.get("coverage_gaps"):
        die("没有覆盖缺口，不需要第二轮")
    if ledger["budget"]["max_rounds"] < 2:
        die("预算只允许一轮")
    ledger["round"] = 2
    report.append("进入第二轮")

elif a.phase == "note":
    if not a.text:
        die("--text 必填")
    ledger.setdefault("injection_notes", []).append(a.text)
    report.append("已记录")

save_ledger(rdir, ledger)
print("\n".join(report) if report else "无变更")
