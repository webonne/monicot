"""走读 hook 公共函数。只用标准库。"""
import json
import os
import sys
from pathlib import Path


def read_input():
    try:
        return json.load(sys.stdin)
    except Exception:
        return {}


def project_dir():
    return Path(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd())


def active_review():
    """返回 (review_dir, ledger) 或 (None, None)。ACTIVE 文件里是 review_id。"""
    root = project_dir() / ".walkthrough"
    marker = root / "ACTIVE"
    if not marker.exists():
        return None, None
    rid = marker.read_text().strip()
    rdir = root / rid
    ledger_path = rdir / "ledger.json"
    if not ledger_path.exists():
        return rdir, None
    try:
        return rdir, json.loads(ledger_path.read_text())
    except Exception:
        return rdir, None


def deny(reason):
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }, ensure_ascii=False))
    sys.exit(0)


def is_walkthrough_agent(data):
    return str(data.get("agent_type", "")).startswith("walkthrough-")
