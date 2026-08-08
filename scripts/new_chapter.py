#!/usr/bin/env python3
"""Scaffold a new trilingual chapter with boundary section and SUMMARY entry.
Usage: python3 scripts/new_chapter.py <path> <title>
Example: python3 scripts/new_chapter.py a-operators/a15-returns.md "退货管理"
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 scripts/new_chapter.py <path> <title>")
        sys.exit(1)
    rel_path = sys.argv[1]
    title_zh = sys.argv[2]
    title_en = input("English title: ")
    title_ja = input("Japanese title: ")

    for tree, title in [("src", title_zh), ("i18n/en/src", title_en), ("i18n/ja/src", title_ja)]:
        f = ROOT / tree / rel_path
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(f"# {title}\n\n> Last updated: 2026-08\n\n<!-- claims: illustrative -->\n\nContent here.\n\n## When this doesn't work / 什么时候这套不管用\n\n_TBD_\n")
        print(f"  created {tree}/{rel_path}")

    print("\nNext: fill content, add to SUMMARY.md, run verify_all.py")

if __name__ == "__main__":
    main()
