#!/usr/bin/env python3
"""Content audit — validity, completeness, reader-friendliness.

Usage:
  python3 scripts/audit_content.py               # everything
  python3 scripts/audit_content.py --axis V      # one axis: V, C, or F
  python3 scripts/audit_content.py --only V1
  python3 scripts/audit_content.py --list        # show offending items, not just counts
  python3 scripts/audit_content.py --json

Why this exists alongside verify_content.py
-------------------------------------------
The gate suite answers "is anything broken". It runs at 0 and should stay there.
This answers a different question — "is the content actually good" — and is
expected to return findings. They are judgment calls, not defects, so this never
gates a build.

The gap it was written to close: M1 requires prose figures to carry a source, a
verification date, or a hedge, but `prose_lines()` skips any line starting with
`|`. Tables are exempt. That exemption is reasonable for spec tables — nobody
needs a citation for "title max 200 characters" — but market-scale figures live
in tables too, and those are the volatile, high-stakes ones: GMV, MAU, market
share, growth rates, efficacy percentages. V1 covers exactly that blind spot.
"""

from __future__ import annotations

import argparse
import collections
import json
import re
import statistics
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
LINK_CACHE = ROOT / "scripts" / "link-status.json"

# Figures that describe the world and therefore rot: market size, audience,
# share, growth, efficacy. Deliberately excludes platform specs (character
# limits, pixel dimensions, aspect ratios), which are constraints, not claims.
WORLD_FIGURE = re.compile(
    # The label and its value usually sit in adjacent cells, so the gap between
    # them contains a "|". Excluding it here missed the commonest table layout
    # outright — "| 市场份额 | 24% |" did not match.
    r"(?:GMV|MAU|DAU|市场份额|市占|渗透率|增长|营收|收入|用户数|卖家数|销售额)"
    r".{0,24}?\d"
    r"|\$\s?\d+(?:\.\d+)?\s*[BMK]\b"
    r"|\d+(?:\.\d+)?\s*(?:亿|万亿)"
    r"|(?:提升|增长|提高|降低|减少|节省|省时)\s*\d+(?:\.\d+)?\s*[%％]"
    r"|\d+(?:\.\d+)?\s*[%％][^|]{0,12}?(?:份额|增长|提升|渗透)"
)
# A real citation: a link to an external source, or a dated verification marker.
# Keyword matches like "来源" are not usable here — that word appears inside every
# prompt template's data-discipline block ("每个结论标注来源"), which would clear
# a chapter that cites nothing.
CITATION = re.compile(r"\]\(https?://|claims:\s*verified")

# A chapter that states its figures are practitioner estimates, with no public
# source to check them against, is not the same failure as one that quietly
# presents an estimate as a measurement. Reporting both identically buries the
# second in the first. ai-landscape carries such a note: its timings are the
# author's own, and saying so is the honest treatment, not a citation gap.
ESTIMATE_DISCLOSURE = re.compile(
    r"这一章的数字是怎么来的|基于实操的估算"
    r"|numbers in this chapter come from|hands-on estimates"
    r"|本章の数字の出どころ|実務にもとづく見積り"
)

# A chapter is a guide if it teaches a workflow; resources/case-studies are
# reference material and are held to different expectations.
def chapters() -> list[Path]:
    return [p for p in sorted(SRC.rglob("*.md"))
            if p.name not in ("SUMMARY.md", "README.md")]


def is_guide(p: Path) -> bool:
    return p.parent.name not in ("resources", "case-studies")


def outside_fences(text: str) -> str:
    """Text with fenced blocks removed.

    Prompt templates quote citation vocabulary, so anything scanned for evidence
    of sourcing has to ignore them.
    """
    out, fence = [], False
    for line in text.split("\n"):
        if line.strip().startswith(("```", "~~~")):
            fence = not fence
            continue
        if not fence:
            out.append(line)
    return "\n".join(out)


MD_LINK = re.compile(r"\[[^\]]*\]\([^)]*\)")


def strip_link_text(row: str) -> str:
    """Drop markdown links before scanning a row for figures.

    A chapter-index cell like "[A13 增长](../a-operators/a13-ai-growth-hack.md)"
    contains the word 增长 and the digit 13, which looks like a growth figure and
    is a navigation label. Keeping it would train a reader to ignore the report.
    """
    return MD_LINK.sub(" ", row)


def table_rows(text: str) -> list[tuple[int, str]]:
    """Table lines outside fenced blocks."""
    out, fence = [], False
    for ln, line in enumerate(text.split("\n"), 1):
        s = line.strip()
        if s.startswith(("```", "~~~")):
            fence = not fence
            continue
        if not fence and s.startswith("|"):
            out.append((ln, s))
    return out


# --------------------------------------------------------------- validity


def v1_unsourced_world_figures() -> list[str]:
    """Market-scale figures inside tables, in chapters that cite nothing for them.

    A chapter is cleared if it carries any citation or verification marker at all
    — the point is to find content resting on nothing, not to demand a footnote
    per cell.
    """
    hits = []
    for p in chapters():
        text = p.read_text(encoding="utf-8")
        if CITATION.search(outside_fences(text)) or ESTIMATE_DISCLOSURE.search(text):
            continue
        rel = str(p.relative_to(SRC))
        for ln, row in table_rows(text):
            if WORLD_FIGURE.search(strip_link_text(row)):
                hits.append(f"{rel}:{ln}  {row[:88]}")
    return hits


def v2_quantitative_but_unsourced() -> list[str]:
    """Chapters carrying many concrete figures with no external source anywhere.

    A chapter that discloses its figures as estimates is excluded: the finding is
    "presents unsourced numbers as fact", and that chapter does the opposite.
    """
    hits = []
    num = re.compile(r"\d+(?:\.\d+)?\s*(?:%|％|亿|万|美元|\$|倍)")
    for p in chapters():
        text = p.read_text(encoding="utf-8")
        if CITATION.search(outside_fences(text)) or ESTIMATE_DISCLOSURE.search(text):
            continue
        count = len(num.findall(text))
        if count >= 10:
            hits.append(f"{str(p.relative_to(SRC))}  {count} concrete figures, no external source")
    return hits


def v3_link_probe_staleness() -> list[str]:
    """Cited links that did not answer 200, grouped by what a maintainer can do.

    A flat count is not actionable: 403 usually means a bot wall in front of a
    page that is perfectly alive, while 308 means the URL moved and the citation
    should be updated to where it now points. M4 treats both as non-fatal, which
    is right for a gate and useless for triage.

    A cached 3xx is reported as "destination unverified" rather than "moved, page
    is fine". The cache records one response, not the end of the chain, so a
    redirect landing on a 404 is indistinguishable here — smoothed.io sat in the
    "moved" bucket for exactly that reason while its target had been dead for
    some time. Run --refresh-links to resolve them.
    """
    if not LINK_CACHE.exists():
        return ["link-status.json missing — run verify_content.py --probe-links"]
    cache = json.loads(LINK_CACHE.read_text(encoding="utf-8"))
    buckets = collections.defaultdict(list)
    for url, st in sorted(cache.items()):
        status = st.get("status")
        if status == 200:
            continue
        if status in (301, 302, 307, 308):
            buckets["redirect — destination unverified, run --refresh-links"].append(f"{status} {url}")
        elif status in (403, 429):
            buckets["bot-walled — page is likely fine, cannot be re-verified"].append(f"{status} {url}")
        elif isinstance(status, int) and status >= 400:
            buckets["broken — needs a replacement source"].append(f"{status} {url}")
        else:
            buckets["probe failed — retry before judging"].append(f"{status} {url}")
    out = []
    for label in sorted(buckets):
        out.append(f"[{len(buckets[label]):>3}] {label}")
        out.extend(f"      {u[:96]}" for u in buckets[label][:6])
        if len(buckets[label]) > 6:
            out.append(f"      … and {len(buckets[label]) - 6} more")
    return out


# ----------------------------------------------------------- completeness


def c1_guides_without_boundary() -> list[str]:
    """M2 covers guide chapters. This reports the rest, which it exempts."""
    pat = re.compile(r"什么时候.*(不管用|不适用)|失效边界|局限|Limitations")
    return [str(p.relative_to(SRC)) for p in chapters()
            if not is_guide(p) and not pat.search(p.read_text(encoding="utf-8"))]


def c2_platforms_without_chapters() -> list[str]:
    path = ROOT / "ontology" / "platforms.yaml"
    if not path.exists():
        return ["ontology/platforms.yaml missing"]
    out = []
    for entry in yaml.safe_load(path.read_text(encoding="utf-8")) or []:
        if not isinstance(entry, dict):
            continue
        refs = entry.get("chapters") or []
        if not refs:
            out.append(f"{entry.get('id', '?')}: no chapter listed")
            continue
        for ref in refs:
            if not (SRC / ref).exists() and not (ROOT / ref).exists():
                out.append(f"{entry.get('id','?')}: chapter {ref} does not exist")
    return out


def c3_depth_outliers() -> list[str]:
    """Guide chapters far shorter than their track's median — likely stubs."""
    by_track = collections.defaultdict(list)
    for p in chapters():
        if is_guide(p):
            by_track[p.parent.name].append((p, p.read_text(encoding="utf-8").count("\n") + 1))
    out = []
    for track, items in sorted(by_track.items()):
        if len(items) < 3:
            continue
        med = statistics.median(n for _p, n in items)
        for p, n in items:
            if n < med * 0.35:
                out.append(f"{p.relative_to(SRC)}  {n} lines vs {track} median {med:.0f}")
    return out


# ------------------------------------------------------------ friendliness


def f1_guides_without_prompts() -> list[str]:
    """A guide with no runnable prompt leaves the reader to invent one."""
    return [str(p.relative_to(SRC)) for p in chapters()
            if is_guide(p) and "```" not in p.read_text(encoding="utf-8")]


def f2_missing_navigation() -> list[str]:
    """Long chapters with no in-page table of contents."""
    out = []
    for p in chapters():
        text = p.read_text(encoding="utf-8")
        if text.count("\n") < 300:
            continue
        # The nav block is itself an H2 section, so slicing at the first "## "
        # cuts it off. Look at the opening of the document instead.
        head = "\n".join(text.split("\n")[:60])
        if not re.search(r"章节导航|Chapter Navigation|章ナビ|目次", head):
            out.append(f"{p.relative_to(SRC)}  {text.count(chr(10))} lines, no in-page nav")
    return out


def f3_wall_of_text() -> list[str]:
    """Sections running long with no subheading to break them up."""
    out = []
    for p in chapters():
        text = p.read_text(encoding="utf-8")
        rel = str(p.relative_to(SRC))
        fence = False
        start, title, since_sub = None, "", 0
        for ln, line in enumerate(text.split("\n"), 1):
            s = line.strip()
            if s.startswith("```"):
                fence = not fence
            if fence:
                continue
            if s.startswith("## "):
                if start and since_sub > 220:
                    out.append(f"{rel}:{start}  '{title[:40]}' runs {since_sub} lines, no ###")
                start, title, since_sub = ln, s[3:], 0
            elif s.startswith("### "):
                since_sub = 0
            elif start:
                since_sub += 1
        if start and since_sub > 220:
            out.append(f"{rel}:{start}  '{title[:40]}' runs {since_sub} lines, no ###")
    return out


AUDITS = [
    ("V1", "unsourced market figures in tables", v1_unsourced_world_figures),
    ("V2", "quantitative chapters with no source", v2_quantitative_but_unsourced),
    ("V3", "links not answering 200 at last probe", v3_link_probe_staleness),
    ("C1", "reference pages without a limits section", c1_guides_without_boundary),
    ("C2", "platforms without a real chapter", c2_platforms_without_chapters),
    ("C3", "chapters far shorter than their track", c3_depth_outliers),
    ("F1", "guides with no runnable prompt", f1_guides_without_prompts),
    ("F2", "long chapters with no in-page nav", f2_missing_navigation),
    ("F3", "sections running long with no subheading", f3_wall_of_text),
]
AXIS = {"V": "有效性 validity", "C": "完整性 completeness", "F": "友好度 friendliness"}


def main() -> int:
    ap = argparse.ArgumentParser(description="Content audit (report, never a gate)")
    ap.add_argument("--axis", choices=sorted(AXIS))
    ap.add_argument("--only", help="single audit id, e.g. V1")
    ap.add_argument("--list", action="store_true", dest="show", help="print offending items")
    ap.add_argument("--json", action="store_true", dest="as_json")
    args = ap.parse_args()

    selected = [a for a in AUDITS
                if (not args.axis or a[0][0] == args.axis)
                and (not args.only or a[0] == args.only.upper())]
    if not selected:
        sys.exit("no audit matched")

    results = {aid: (label, fn()) for aid, label, fn in selected}

    if args.as_json:
        print(json.dumps({aid: {"label": lbl, "count": len(items), "items": items}
                          for aid, (lbl, items) in results.items()}, indent=2, ensure_ascii=False))
        return 0

    print("  content audit — findings are judgment calls, not defects")
    print("  (the pass/fail gates live in verify_content.py and run at 0)")
    current = None
    for aid, (label, items) in results.items():
        if aid[0] != current:
            current = aid[0]
            print(f"\n  {AXIS[current]}")
        print(f"    {aid}  {label:<46} {len(items):>4}")
        if args.show:
            for item in items[:40]:
                print(f"         {item}")
            if len(items) > 40:
                print(f"         … and {len(items) - 40} more")
    print(f"\n  total findings: {sum(len(i) for _l, i in results.values())}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
