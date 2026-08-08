#!/usr/bin/env python3
from __future__ import annotations
"""Apply a hand-reindented Python block back into all three language trees.

Why this exists: every fenced Python block in this book once had its leading
whitespace stripped, and reconstructing it is not automatable. An `if x:`
followed by non-terminal statements gives no syntactic signal about where its
body ends, so a heuristic re-indenter produces plausible-looking wrong code —
which is worse than an obviously broken block, because a reader copies it. The
rule is: rebuild by hand, then use this to propagate.

The three trees are line-for-line aligned inside code fences, so the leading
whitespace computed from the Chinese source transfers verbatim; only comment and
string text differs. Every write is compile-checked first, and a line-count
mismatch aborts that tree rather than guessing.

That alignment does break occasionally — a translated docstring can wrap onto an
extra line. Do not relax the line-count guard to get past it; that guard is what
stops a bad fix from being written. Pass --only <tree> and run once per tree with
a fix file matching that tree's line count.

Usage:
  apply_indent.py <chapter-rel-path> <block-index> <fixed-file> [--only <tree>]

  apply_indent.py b-developers/b1-data-pipeline.md 7 /tmp/fixed.py
  apply_indent.py b-developers/b2-prediction-models.md 1 /tmp/en.py --only i18n/en/src
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
TREES = ("src", "i18n/en/src", "i18n/ja/src")


def main(rel: str, idx: int, fixed_path: str, only: "str | None" = None) -> int:
    fixed = pathlib.Path(fixed_path).read_text(encoding="utf-8").rstrip("\n")
    indents = [len(l) - len(l.lstrip()) for l in fixed.split("\n")]

    trees = (only,) if only else TREES
    applied = []
    for tree in trees:
        p = ROOT / tree / rel
        if not p.exists():
            print(f"  x {tree}: file missing")
            return 1
        text = p.read_text(encoding="utf-8")
        spans = [(m.start(1), m.end(1)) for m in re.finditer(r"```python\n(.*?)```", text, re.S)]
        if idx >= len(spans):
            print(f"  x {tree}: block {idx} out of range ({len(spans)} blocks)")
            return 1
        s, e = spans[idx]
        lines = text[s:e].rstrip("\n").split("\n")
        if len(lines) != len(indents):
            print(f"  x {tree}: {len(lines)} lines vs {len(indents)} in the fix — skipped")
            return 1
        new = "\n".join(
            (" " * ind + l.strip()) if l.strip() else "" for ind, l in zip(indents, lines)
        )
        try:
            compile(new, "<block>", "exec")
        except SyntaxError as err:
            print(f"  x {tree}: still not compilable — {err}")
            return 1
        applied.append((p, text[:s] + new + "\n" + text[e:]))

    for p, content in applied:
        p.write_text(content, encoding="utf-8")
    print(f"  ok {rel} block {idx} -> {only or '3 trees'}, all compile")
    return 0


if __name__ == "__main__":
    only = sys.argv[5] if len(sys.argv) > 5 and sys.argv[4] == "--only" else None
    sys.exit(main(sys.argv[1], int(sys.argv[2]), sys.argv[3], only))
