#!/usr/bin/env python3
"""校验 Ledger。用法：validate_ledger.py <ledger.json>。退出码 0 通过，1 失败。"""
import sys
from wt_lib import load_json, validate

if len(sys.argv) < 2:
    print("用法：validate_ledger.py <ledger.json>", file=sys.stderr)
    sys.exit(1)
errs = validate(load_json(sys.argv[1]))
if errs:
    print("校验失败：\n  - " + "\n  - ".join(errs), file=sys.stderr)
    sys.exit(1)
print("ok")
