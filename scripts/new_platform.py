#!/usr/bin/env python3
"""Scaffold a new platform chapter + platforms.yaml entry + SUMMARY entry.
Usage: python3 scripts/new_platform.py <id> <zh_name> <en_name> <ja_name>
Example: python3 scripts/new_platform.py ozon "Ozon" "Ozon" "Ozon"
"""
import sys, yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def main():
    if len(sys.argv) < 4:
        print("Usage: python3 scripts/new_platform.py <id> <zh_name> <en_name> <ja_name>")
        sys.exit(1)
    pid = sys.argv[1]
    zh = sys.argv[2]
    en = sys.argv[3]
    ja = sys.argv[4] if len(sys.argv) > 4 else en

    # 1. Create chapter file in all 3 trees
    # Find next d-number
    existing = sorted([int(f.stem[1:3]) for f in (ROOT / "src" / "d-platforms").glob("d[0-9][0-9]-*.md")
                       if f.stem[1:3].isdigit()], reverse=True)
    next_num = (existing[0] + 1) if existing else 14
    filename = f"d{next_num}-{pid}-ai-guide.md"

    for tree, title in [("src", zh), ("i18n/en/src", en), ("i18n/ja/src", ja)]:
        f = ROOT / tree / "d-platforms" / filename
        f.parent.mkdir(parents=True, exist_ok=True)
        boundary = {"src": "## 什么时候这套不管用", "i18n/en/src": "## When this doesn't work", "i18n/ja/src": "## この方法が効かないとき"}
        b = boundary.get(tree, boundary["src"])
        f.write_text(f"""# D{next_num}. {title} AI Guide

> **Path**: Path D: Multi-Platform · **Module**: D{next_num}
> **Last updated**: 2026-08

<!-- claims: illustrative -->

## Overview

_TBD — platform-specific AI applications for {title}._

## Key Differences from Amazon

_TBD_

## Prompt Templates

_TBD_

{b}

_TBD_
""")
        print(f"  created {tree}/d-platforms/{filename}")

    # 2. Add to platforms.yaml
    pf = ROOT / "ontology" / "platforms.yaml"
    platforms = yaml.safe_load(pf.read_text(encoding="utf-8"))
    platforms.append({
        "id": pid,
        "label": {"zh": zh, "en": en, "ja": ja},
        "first_class": True,
        "chapters": [f"src/d-platforms/{filename}"],
    })
    pf.write_text(yaml.dump(platforms, allow_unicode=True, default_flow_style=False, sort_keys=False))
    print(f"  added {pid} to ontology/platforms.yaml")

    print(f"\nNext: fill chapter content, run verify_all.py")

if __name__ == "__main__":
    main()
