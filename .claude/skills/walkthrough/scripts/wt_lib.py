"""走读脚本公共库。只用标准库。"""
import json
import os
import re
import sys
from pathlib import Path

LENSES = {"correctness", "security", "concurrency", "api-contract", "perf"}
SEVERITIES = {"high", "medium", "low"}
VERDICTS = {"refute", "concede", "contest"}
VSTATUS = {"confirmed", "refuted", "inconclusive", "skipped"}
RSTATUS = {"accepted", "rejected", "needs_human"}
ID_RE = re.compile(r"^C-\d{3,}$")


def project_dir():
    return Path(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd())


def root():
    return project_dir() / ".walkthrough"


def review_dir(review_id=None):
    if review_id:
        return root() / review_id
    marker = root() / "ACTIVE"
    if not marker.exists():
        die("没有进行中的走读（.walkthrough/ACTIVE 不存在）。先跑 init_ledger.py 或传 --review-id")
    return root() / marker.read_text().strip()


def load_ledger(rdir):
    p = rdir / "ledger.json"
    if not p.exists():
        die(f"{p} 不存在")
    return json.loads(p.read_text())


def save_ledger(rdir, ledger):
    errs = validate(ledger)
    if errs:
        die("Ledger 校验失败，未写入：\n  - " + "\n  - ".join(errs))
    p = rdir / "ledger.json"
    tmp = p.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(ledger, ensure_ascii=False, indent=2) + "\n")
    os.replace(tmp, p)


def die(msg, code=1):
    print(msg, file=sys.stderr)
    sys.exit(code)


def load_json(path):
    try:
        return json.loads(Path(path).read_text())
    except Exception as e:
        die(f"读取 {path} 失败：{e}")


def validate(ledger):
    """返回错误列表。手写校验，和 docs/walkthrough-ledger.schema.json 保持一致。"""
    errs = []
    for k in ("review_id", "round", "scope", "brief_path", "budget", "claims"):
        if k not in ledger:
            errs.append(f"缺少顶层字段 {k}")
    if errs:
        return errs
    if ledger["round"] not in (1, 2):
        errs.append("round 必须是 1 或 2")
    if ledger.get("status") not in (None, "in_progress", "complete", "partial", "aborted"):
        errs.append("status 非法")
    sc = ledger["scope"]
    if not isinstance(sc.get("files"), list):
        errs.append("scope.files 必须是数组")
    for l in sc.get("lenses", []):
        if l not in LENSES:
            errs.append(f"未知镜头 {l}")
    b = ledger["budget"]
    for k in ("max_rounds", "max_tool_calls", "used_tool_calls"):
        if not isinstance(b.get(k), int):
            errs.append(f"budget.{k} 必须是整数")
    seen = set()
    for c in ledger["claims"]:
        cid = c.get("id", "?")
        if not ID_RE.match(str(cid)):
            errs.append(f"claim id 非法：{cid}")
        if cid in seen:
            errs.append(f"claim id 重复：{cid}")
        seen.add(cid)
        for k in ("round", "lens", "file", "line", "title", "failure_scenario", "severity", "confidence", "evidence"):
            if k not in c:
                errs.append(f"{cid} 缺少 {k}")
        if c.get("lens") not in LENSES:
            errs.append(f"{cid} 镜头非法")
        if c.get("severity") not in SEVERITIES:
            errs.append(f"{cid} severity 非法")
        try:
            if not (0 <= float(c.get("confidence", -1)) <= 1):
                errs.append(f"{cid} confidence 必须在 0..1")
        except Exception:
            errs.append(f"{cid} confidence 不是数字")
        if not isinstance(c.get("line"), int) or c.get("line", 0) < 1:
            errs.append(f"{cid} line 必须是正整数")
        if len(str(c.get("failure_scenario", ""))) < 20:
            errs.append(f"{cid} failure_scenario 太短或缺失")
        if not isinstance(c.get("evidence"), list) or not c.get("evidence"):
            errs.append(f"{cid} evidence 必须是非空数组")
        d = c.get("defense")
        if d is not None:
            if d.get("verdict") not in VERDICTS:
                errs.append(f"{cid} defense.verdict 非法")
            if not d.get("evidence"):
                errs.append(f"{cid} defense.evidence 缺失")
        v = c.get("verification")
        if v is not None and v.get("status") not in VSTATUS:
            errs.append(f"{cid} verification.status 非法")
        r = c.get("ruling")
        if r is not None:
            if r.get("status") not in RSTATUS:
                errs.append(f"{cid} ruling.status 非法")
            if not r.get("rationale"):
                errs.append(f"{cid} ruling.rationale 缺失")
    for g in ledger.get("coverage_gaps", []):
        if not g.get("hotspot") or not g.get("reason"):
            errs.append("coverage_gaps 条目缺 hotspot/reason")
    return errs


def next_id(ledger):
    n = 0
    for c in ledger["claims"]:
        try:
            n = max(n, int(c["id"].split("-")[1]))
        except Exception:
            pass
    return n + 1
