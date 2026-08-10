#!/usr/bin/env python3
"""Content checks for the trilingual mdBook.

Two families of check, both run by default:

  Structure — things that are broken rather than merely unsourced.
    anchors      an in-page [x](#a) with no heading that generates `a`
    xanchors     [x](other.md#a) where `a` does not exist in that file
    links        [x](other.md) where the file does not exist
    python       a ```python block that does not compile
    parity       a file under src/ missing from en/ja, or whose structure differs

  Gates — the content-discipline rules this book holds itself to.
    M1 claims    a hard number in prose with no source, no date, no hedge, no marker
    M2 boundary  a guide chapter with no "when this doesn't work" section
    M4 deadlinks an external URL that is dead, or one never probed
    M5 orphans   a body file no other chapter links to

Every one reports a count; the repository's standing requirement is that all of
them are zero. CI runs this after the books build and fails the deploy on any
non-zero.

Anchor generation mirrors mdBook and is validated against real build output —
see --anchors-vs-build, which diffs what this script derives from the markdown
against the ids mdBook actually emitted. Run it after changing anything in
slugify(), and after a mdBook version bump.

Usage
  verify_content.py                     everything offline (what CI runs)
  verify_content.py --list              print each offending item, not just counts
  verify_content.py --only M1           one check by name
  verify_content.py --probe-links       re-probe every external URL, refresh the cache
  verify_content.py --anchors-vs-build docs
                                        diff derived anchors against built HTML
"""
from __future__ import annotations

from __future__ import annotations

import argparse
import collections
import json
import html as htmlmod
import pathlib
import re
import subprocess
import sys
import unicodedata

ROOT = pathlib.Path(__file__).resolve().parent.parent
TREES = ("src", "i18n/en/src", "i18n/ja/src")
LINK_CACHE = ROOT / "scripts" / "link-status.json"
ALLOWLIST = ROOT / "scripts" / "content-allowlist.txt"

# --------------------------------------------------------------------------
# anchors
# --------------------------------------------------------------------------

FENCE = re.compile(r"^(```|~~~)")
HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*$")
HTML_ID = re.compile(r'id="([^"]+)"')
LINK = re.compile(r"\[(?:[^\]\[]|\[[^\]]*\])*\]\(([^()\s]+)\)")


def slugify(text: str) -> str:
    """mdBook's heading -> anchor transformation, as observed in its output.

    Three behaviours here are not obvious and were each found by diffing against
    a real build rather than reasoned from the source:
      - smart punctuation is on by default, so `--` becomes an en dash and `---`
        an em dash, both of which are then dropped. A lone `-` survives.
      - the heading text is trimmed first, so a leading space does not become a
        leading hyphen.
      - lowercasing is full Unicode, not ASCII-only.
    """
    text = re.sub(r"`([^`]*)`", r"\1", text)
    text = re.sub(r"\*\*?([^*]*)\*\*?", r"\1", text)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = text.replace("---", "—").replace("--", "–")
    text = text.strip().lower()
    out = []
    for ch in text:
        if ch in " \t":
            out.append("-")
        elif ch in "-_":
            out.append(ch)
        elif unicodedata.category(ch)[0] in ("L", "N"):
            out.append(ch)
    return "".join(out)


def page_anchors(text: str) -> set[str]:
    """Every anchor a page offers: ATX headings plus explicit HTML ids.

    Setext headings are deliberately not modelled. A paragraph followed by `---`
    becomes an H2 in mdBook, but in this book every such case has been an
    accident, so the divergence is left visible rather than absorbed — run
    --anchors-vs-build and a new one shows up as a page that disagrees.
    """
    anchors: set[str] = set()
    seen: collections.Counter[str] = collections.Counter()
    in_fence = False
    for line in text.split("\n"):
        if FENCE.match(line.strip()):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        anchors.update(HTML_ID.findall(line))
        m = HEADING.match(line)
        if not m:
            continue
        base = slugify(m.group(2))
        if not base:
            continue
        n = seen[base]
        seen[base] += 1
        anchors.add(base if n == 0 else f"{base}-{n}")
    return anchors


def page_links(text: str) -> list[str]:
    out, in_fence = [], False
    for line in text.split("\n"):
        if FENCE.match(line.strip()):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        for target in LINK.findall(line):
            if re.match(r"^[a-z][a-z0-9+.-]*:", target) or target.startswith("//"):
                continue
            out.append(target)
    return out


# --------------------------------------------------------------------------
# claims discipline
# --------------------------------------------------------------------------

# A hard claim is a number a reader could act on.
HARD = re.compile(r"(\d+(?:\.\d+)?%|\$\s?\d[\d,]*(?:\.\d+)?|\d+(?:\.\d+)?\s?[倍x×]\b|\d+\s?万)")
# A hedge means the sentence is not asserting a measurement. "typically 5-10%" is
# a heuristic a reader can argue with; "40% of users do X" needs a source.
HEDGE = re.compile(
    r"(约|大致|假设|示例|举例|比如|例如|^-?\s*例[：:]|通常|一般|往往|可能|左右|上下|"
    r"多数情况|经验值|起步价|"
    r"estimate|roughly|hypothetical|for example|e\.g\.|typically|usually|may be|"
    r"could be|rule of thumb|around |"
    r"仮|例えば|たとえば|通常は|一般に|経験則|程度|くらい|かもしれ)"
)
VERIFIED = re.compile(r"(核验(日期)?|verified|検証)\s*[:：]?\s*20\d\d")

# Section markers, written as HTML comments so readers never see them. Placed
# before the first H2 they cover the whole chapter; otherwise up to the next H2.
#   illustrative     numbers constructed to show a shape, not measurements
#   verified YYYY-MM checkable facts with a shelf life, and when they were checked
#   benchmark        thresholds this book recommends for judging your own numbers.
#                    Not somebody else's measurement — mislabelling a published
#                    statistic as a benchmark is worse than leaving it unlabelled.
MARKER = re.compile(r"<!--\s*claims:\s*(illustrative|verified\s+\d{4}-\d{2}|benchmark)\s*-->")

# "Sources: [a](…), [b](…)" attributes the block above it, not just its own line.
SOURCE_LINE = re.compile(r"(Sources?|来源|出典|參考|参考)\s*[:：]")

BOUNDARY = {
    "src": re.compile(r"^#{2}\s.*什么时候这套不管用", re.M),
    "i18n/en/src": re.compile(r"^#{2}\s.*When this doesn't work", re.M | re.I),
    "i18n/ja/src": re.compile(r"^#{2}\s.*この方法が効かないとき", re.M),
}


def guide_chapters() -> list[str]:
    """Guide chapters only. Case studies and resource pages have a different shape."""
    out = []
    for md in sorted((ROOT / "src").rglob("*.md")):
        rel = str(md.relative_to(ROOT / "src"))
        if rel == "SUMMARY.md" or rel.startswith(("case-studies/", "resources/")):
            continue
        if pathlib.Path(rel).name == "README.md":
            continue
        out.append(rel)
    return out


def prose_lines(text: str):
    """(lineno, line) for unmarked prose: no fences, tables, quotes or headings."""
    whole_file = bool(MARKER.search(text.split("\n## ", 1)[0]))
    fence, marked = False, whole_file
    for ln, line in enumerate(text.split("\n"), 1):
        s = line.strip()
        if s.startswith(("```", "~~~")):
            fence = not fence
            continue
        if not fence and s.startswith("## ") and not whole_file:
            marked = False
        if not fence and MARKER.search(s):
            marked = True
            continue
        if fence or marked or not s or s.startswith(("|", ">", "#")):
            continue
        yield ln, s


def cited_lines(text: str) -> set[int]:
    """Lines covered by a citation line that follows their block."""
    covered: set[int] = set()
    lines = text.split("\n")
    for i, line in enumerate(lines):
        if not (SOURCE_LINE.search(line) and "](http" in line):
            continue
        j, seen_blank = i - 1, False
        while j >= 0:
            s = lines[j].strip()
            if not s:
                if seen_blank:
                    break
                seen_blank = True
            elif s.startswith("#"):
                break
            else:
                covered.add(j + 1)
                seen_blank = False
            j -= 1
    return covered


def fingerprint(text: str):
    """Structure only: heading depths in order, fence count, table-row count."""
    headings, fences, rows, fence = [], 0, 0, False
    for line in text.split("\n"):
        s = line.strip()
        if s.startswith(("```", "~~~")):
            fence = not fence
            fences += fence
            continue
        if fence:
            continue
        m = re.match(r"^(#{1,6})\s", line)
        if m:
            headings.append(len(m.group(1)))
        if re.match(r"^\|.*\|\s*$", line):
            rows += 1
    return (tuple(headings), fences, rows)


def load_allowlist() -> set[str]:
    if not ALLOWLIST.exists():
        return set()
    out = set()
    for line in ALLOWLIST.read_text(encoding="utf-8").split("\n"):
        line = line.split("#")[0].strip()
        if line:
            out.add(line)
    return out


def external_urls() -> dict[str, set[str]]:
    urls: dict[str, set[str]] = collections.defaultdict(set)
    for tree in TREES:
        for md in (ROOT / tree).rglob("*.md"):
            body = md.read_text(encoding="utf-8")
            for u in re.findall(r"\]\((https?://[^)\s]+)\)", body):
                urls[u.rstrip(".,")].add(f"{tree}/{md.relative_to(ROOT / tree)}")
    return urls


# --------------------------------------------------------------------------
# the checks
# --------------------------------------------------------------------------


def check_structure() -> dict[str, list[str]]:
    found: dict[str, list[str]] = collections.defaultdict(list)
    for tree in TREES:
        root = ROOT / tree
        anchors = {p.resolve(): page_anchors(p.read_text(encoding="utf-8")) for p in root.rglob("*.md")}
        for p in sorted(root.rglob("*.md")):
            text = p.read_text(encoding="utf-8")
            rel = f"{tree}/{p.relative_to(root)}"
            for target in page_links(text):
                path_part, _, frag = target.partition("#")
                if not path_part:
                    if frag and frag not in anchors[p.resolve()]:
                        found["anchors"].append(f"{rel} -> #{frag}")
                    continue
                dest = (p.parent / path_part).resolve()
                if not dest.exists():
                    found["links"].append(f"{rel} -> {path_part}")
                elif frag and dest.suffix == ".md" and frag not in anchors.get(dest, set()):
                    found["xanchors"].append(f"{rel} -> {path_part}#{frag}")
            for i, body in enumerate(re.findall(r"```python\n(.*?)```", text, re.S)):
                try:
                    compile(body, "<block>", "exec")
                except SyntaxError:
                    found["python"].append(f"{rel} block {i}")

    for md in sorted((ROOT / "src").rglob("*.md")):
        rel = md.relative_to(ROOT / "src")
        fps = {}
        for tree in TREES:
            p = ROOT / tree / rel
            if not p.exists():
                found["parity"].append(f"missing {tree}/{rel}")
                fps[tree] = None
            else:
                fps[tree] = fingerprint(p.read_text(encoding="utf-8"))
        vals = [v for v in fps.values() if v is not None]
        if len(vals) == 3 and len({repr(v) for v in vals}) > 1:
            which = []
            if len({repr(v[0]) for v in vals}) > 1:
                which.append(f"headings {[len(v[0]) for v in vals]}")
            if len({v[1] for v in vals}) > 1:
                which.append(f"fences {[v[1] for v in vals]}")
            if len({v[2] for v in vals}) > 1:
                which.append(f"table rows {[v[2] for v in vals]}")
            found["parity"].append(f"drift {rel}: {' '.join(which)}")
    return found


def gate_m1() -> list[str]:
    allow = load_allowlist()
    hits = []
    for md in sorted((ROOT / "src").rglob("*.md")):
        rel = str(md.relative_to(ROOT / "src"))
        text = md.read_text(encoding="utf-8")
        cited = cited_lines(text)
        for ln, s in prose_lines(text):
            if ln in cited or not HARD.search(s):
                continue
            if "](" in s or "http" in s or HEDGE.search(s) or VERIFIED.search(s):
                continue
            if f"{rel}:{ln}" in allow:
                continue
            hits.append(f"{rel}:{ln}  {s[:90]}")
    return hits


def gate_m2() -> list[str]:
    missing = []
    for rel in guide_chapters():
        for tree in TREES:
            p = ROOT / tree / rel
            if not p.exists() or not BOUNDARY[tree].search(p.read_text(encoding="utf-8")):
                missing.append(f"{tree}/{rel}")
    return missing


def gate_m4() -> list[str]:
    """Offline: every URL must be in the cache and not marked dead.

    Deliberately not a live probe. A new link that nobody probed is a failure —
    which forces --probe-links before the link reaches main — and the build does
    not depend on the network being up or on some vendor's bot policy.
    """
    urls = external_urls()
    if not LINK_CACHE.exists():
        return [f"no cache; run --probe-links ({len(urls)} unique URLs)"]
    cache = json.loads(LINK_CACHE.read_text(encoding="utf-8"))
    allow = load_allowlist()
    dead = []
    for u in sorted(urls):
        if u in allow:
            continue
        st = cache.get(u)
        if st is None:
            dead.append(f"never probed: {u}  <- {sorted(urls[u])[0]}")
        elif st.get("hard_fail"):
            dead.append(f"{st['status']} {u}  <- {sorted(urls[u])[0]}")
    return dead


def gate_m6() -> list[str]:
    """Section numbering: sequential, and the visible ordinal agrees with the anchor.

    Two failures that look different and are the same bug. A chapter numbered
    1..7 then 9 has lost a section or mis-numbered its last one. And a chapter
    nav reading `7. [Done](#8-done)` is what you get when the heading was
    renumbered and the label above it was not — the link still works, so nothing
    else catches it, and the reader sees two different numbers for one section.
    """
    problems = []
    for tree in TREES:
        for md in sorted((ROOT / tree).rglob("*.md")):
            rel = f"{tree}/{md.relative_to(ROOT / tree)}"
            text = md.read_text(encoding="utf-8")
            nums, fence = [], False
            for line in text.split("\n"):
                if line.strip().startswith(("```", "~~~")):
                    fence = not fence
                    continue
                if fence:
                    continue
                m = re.match(r"^##\s+(\d+)\.\s", line)
                if m:
                    nums.append(int(m.group(1)))
            if nums and nums != list(range(1, len(nums) + 1)):
                problems.append(f"{rel}: numbering {nums}")
            for m in re.finditer(r"(?<![\d.])(\d+)\.\s*\[[^\]]+\]\(#(\d+)-", text):
                if m.group(1) != m.group(2):
                    problems.append(f"{rel}: nav label {m.group(1)} vs anchor {m.group(2)}")
    return problems


# --------------------------------------------------------------------------
# runnability
# --------------------------------------------------------------------------

PROMPT_TAGS_BY_TREE = {
    "src": [
        "角色", "输入数据", "任务", "数据纪律", "输出格式", "自检",
        "文案纪律", "输入数据边界", "计算纪律", "数据来源",
    ],
    "i18n/en/src": [
        "role", "input_data", "task", "data_discipline", "output_format", "self_check",
        "copy_discipline", "input_boundary", "calculation_discipline", "data_source",
    ],
    "i18n/ja/src": [
        "役割", "入力データ", "タスク", "データ規律", "出力形式", "セルフチェック",
        "コピー規律", "入力データ境界", "計算規律", "データソース",
    ],
}

# Modules that ship with Python, and names that are this chapter's own files
# rather than anything installable.
STDLIB = {
    "os", "sys", "re", "json", "time", "math", "random", "datetime", "pathlib", "typing",
    "collections", "itertools", "functools", "subprocess", "argparse", "logging", "csv",
    "io", "gzip", "zipfile", "glob", "shutil", "hashlib", "base64", "urllib", "http",
    "socket", "threading", "asyncio", "concurrent", "dataclasses", "enum", "abc", "copy",
    "string", "textwrap", "unicodedata", "warnings", "traceback", "pickle", "sqlite3",
    "statistics", "decimal", "uuid", "tempfile", "operator", "contextlib", "inspect",
    "__future__",
}
LOCAL_MODULES = {"config", "extract", "transform", "report", "src", "utils", "models",
                 "app", "main", "pipeline", "loader"}
# import name -> distribution name, where they differ
DIST = {
    "sklearn": "scikit-learn", "cv2": "opencv-python", "PIL": "pillow", "yaml": "pyyaml",
    "bs4": "beautifulsoup4", "dotenv": "python-dotenv", "sp_api": "python-amazon-sp-api",
    "google": "google-generativeai", "dateutil": "python-dateutil",
    "vaderSentiment": "vadersentiment", "llama_index": "llama-index",
    "langchain_openai": "langchain-openai", "langchain_core": "langchain-core",
    "prometheus_client": "prometheus-client",
}
INSTALL_CMD = re.compile(
    r"(?:pip3?|uv pip|python3? -m pip)\s+install\s+([^\n`]+)"
    r"|conda install\s+([^\n`]+)|poetry add\s+([^\n`]+)"
)
# A block that opens by declaring itself conceptual is illustrating an approach,
# not claiming to run, so its imports are not a dependency promise.
CONCEPTUAL = re.compile(r"^#\s*(概念代码|Conceptual|概念コード)")


def gate_n1() -> list[str]:
    """Prompt blocks are well-formed: every six-block tag that opens also closes.

    Counting is fiddlier than it looks. `<角色>text</角色>` sits on one line, and
    the discipline text legitimately *mentions* tag names mid-sentence ("only use
    numbers that appear in <输入数据>"). So: drop same-line pairs first, then count
    only what starts a line. Anything else produces false alarms on correct prose.
    """
    problems = []
    for tree in TREES:
        tags = PROMPT_TAGS_BY_TREE.get(tree, PROMPT_TAGS_BY_TREE["src"])
        for md in sorted((ROOT / tree).rglob("*.md")):
            text = md.read_text(encoding="utf-8")
            for m in re.finditer(r"```[a-z]*\n(.*?)```", text, re.S):
                body = m.group(1)
                ln = text[: m.start()].count("\n") + 1
                for tag in tags:
                    stripped = re.sub(rf"<{tag}>[^\n]*?</{tag}>", "", body)
                    opens = len(re.findall(rf"^\s*<{tag}>", stripped, re.M))
                    closes = len(re.findall(rf"^\s*</{tag}>", stripped, re.M))
                    if opens != closes:
                        rel = f"{tree}/{md.relative_to(ROOT / tree)}"
                        problems.append(f"{rel}:{ln} <{tag}> {opens} open / {closes} closed")
    return problems


def gate_n2() -> list[str]:
    """Every third-party import in a chapter's code is declared installable there.

    A reader copying a block and hitting ModuleNotFoundError has been handed
    something that does not run, which is the same class of defect as a block
    that does not compile.
    """
    def norm(s: str) -> str:
        return s.lower().replace("_", "-")

    problems = []
    for md in sorted((ROOT / "src").rglob("*.md")):
        text = md.read_text(encoding="utf-8")
        used = set()
        for body in re.findall(r"```python\n(.*?)```", text, re.S):
            if CONCEPTUAL.match(body.lstrip()):
                continue
            for m in re.finditer(r"^\s*(?:from|import)\s+([A-Za-z_][\w]*)", body, re.M):
                name = m.group(1)
                if name not in STDLIB and name not in LOCAL_MODULES:
                    used.add(name)
        declared = set()
        for m in INSTALL_CMD.finditer(text):
            for grp in m.groups():
                if grp:
                    declared |= {
                        norm(tok.split("==")[0].split("[")[0])
                        for tok in grp.split()
                        if not tok.startswith("-")
                    }
        for m in re.finditer(r"^([a-zA-Z0-9_.-]+)[=><]=", text, re.M):
            declared.add(norm(m.group(1)))
        declared |= {d.split(".")[0] for d in declared}
        for u in sorted(used):
            if norm(DIST.get(u, u)) in declared or norm(u) in declared:
                continue
            if norm(u).split("-")[0] in declared:
                continue
            problems.append(f"{md.relative_to(ROOT / 'src')}: imports {u}, never declared")
    return problems


def gate_m5() -> list[str]:
    base = ROOT / "src"
    inbound = {str(p.relative_to(base)): 0 for p in base.rglob("*.md")}
    for md in base.rglob("*.md"):
        src_rel = str(md.relative_to(base))
        if src_rel == "SUMMARY.md":
            continue
        body = md.read_text(encoding="utf-8")
        targets = re.findall(r"\]\(([^)\s#]+\.md)(?:#[^)]*)?\)", body)
        # a directory link resolves to that directory's README
        targets += [d + "README.md" for d in re.findall(r"\]\(([^)\s#]*?/)\)", body)]
        for tgt in targets:
            try:
                r = str((md.parent / tgt).resolve().relative_to(base.resolve()))
            except ValueError:
                continue
            if r in inbound and r != src_rel:
                inbound[r] += 1
    return sorted(f for f, n in inbound.items() if n == 0 and f != "SUMMARY.md")


def _prompt_marker_tags(tree: str) -> list[str]:
    return PROMPT_TAGS_BY_TREE.get(tree, PROMPT_TAGS_BY_TREE["src"])


def _is_prompt_block(body: str, tree: str) -> bool:
    """A code block is a production prompt only if it has >=2 different structure tags."""
    markers = _prompt_marker_tags(tree)
    found = sum(1 for tag in markers if f"<{tag}>" in body)
    return found >= 2


def gate_n3() -> list[str]:
    """Prompt blocks that are missing a self-check section."""
    self_check_tags = {
        "src": "<自检>",
        "i18n/en/src": "<self_check>",
        "i18n/ja/src": "<セルフチェック>",
    }
    EXCLUDE = {"f2-prompt-engineering.md"}

    problems = []
    for tree in TREES:
        check_tag = self_check_tags.get(tree, "<自检>")
        for md in sorted((ROOT / tree).rglob("*.md")):
            if md.name in EXCLUDE:
                continue
            text = md.read_text(encoding="utf-8")
            for m in re.finditer(r"```[a-z]*\n(.*?)```", text, re.S):
                body = m.group(1)
                if not _is_prompt_block(body, tree):
                    continue
                ln = text[: m.start()].count("\n") + 1
                if check_tag not in body:
                    rel = f"{tree}/{md.relative_to(ROOT / tree)}"
                    problems.append(f"{rel}:{ln} missing self-check block")
    return problems


def gate_n4() -> list[str]:
    """Prompt blocks that are missing an output-format section."""
    output_format_tags = {
        "src": "<输出格式>",
        "i18n/en/src": "<output_format>",
        "i18n/ja/src": "<出力形式>",
    }
    EXCLUDE = {"f2-prompt-engineering.md"}

    problems = []
    for tree in TREES:
        out_tag = output_format_tags.get(tree, "<输出格式>")
        for md in sorted((ROOT / tree).rglob("*.md")):
            if md.name in EXCLUDE:
                continue
            text = md.read_text(encoding="utf-8")
            for m in re.finditer(r"```[a-z]*\n(.*?)```", text, re.S):
                body = m.group(1)
                if not _is_prompt_block(body, tree):
                    continue
                ln = text[: m.start()].count("\n") + 1
                if out_tag not in body:
                    rel = f"{tree}/{md.relative_to(ROOT / tree)}"
                    problems.append(f"{rel}:{ln} missing output-format block")
    return problems


def _extract_self_check_text(body: str, tree: str) -> str | None:
    """Extract the normalized self-check text from a prompt block."""
    tag_map = {"src": "自检", "i18n/en/src": "self_check", "i18n/ja/src": "セルフチェック"}
    tag = tag_map.get(tree, "自检")
    m = re.search(rf"<{tag}>\s*\n(.*?)</{tag}>", body, re.S)
    if not m:
        return None
    text = m.group(1).strip()
    text = re.sub(r"\s+", " ", text)
    return text


def gate_n5() -> list[str]:
    """Self-check blocks must not be identical across different chapters."""
    EXCLUDE = {"f2-prompt-engineering.md"}
    checks: dict[str, list[tuple[str, int]]] = collections.defaultdict(list)

    for tree in TREES:
        for md in sorted((ROOT / tree).rglob("*.md")):
            if md.name in EXCLUDE:
                continue
            rel = f"{tree}/{md.relative_to(ROOT / tree)}"
            text = md.read_text(encoding="utf-8")
            for m in re.finditer(r"```[a-z]*\n(.*?)```", text, re.S):
                body = m.group(1)
                ln = text[: m.start()].count("\n") + 1
                sc = _extract_self_check_text(body, tree)
                if sc and len(sc) > 10:
                    checks[sc].append((rel, ln))

    problems = []
    for text, locations in checks.items():
        filenames = {loc[0].split("/")[-1] for loc in locations}
        if len(filenames) > 1:
            for rel, ln in locations:
                problems.append(f"{rel}:{ln} self-check identical to other chapters")
    return problems


def gate_n6() -> list[str]:
    """Trilingual prompt structure block count must be equal per file."""
    # Meta/teaching chapters whose tagged code blocks are illustrative, not
    # operational prompts a reader copies, so trilingual tag parity does not
    # apply to them:
    #   - f1-ai-evolution: AI history chapter; the zh source has zero structure
    #     tags, and the tags in en/ja sit inside illustrative example blocks
    #     added during translation (multimodal timeline, hands-on image analysis).
    #   - f2-prompt-engineering: the chapter that TEACHES the six-block prompt
    #     structure; its tagged blocks are teaching examples (e.g. the
    #     Claude-XML example whose <task> tag collides with the en tag list).
    #     Already excluded from N3/N4/N5 for the same reason.
    EXCLUDE = {
        "f1-ai-evolution.md", "f2-prompt-engineering.md",
    }

    def count_blocks(md: Path, tree: str) -> int:
        if not md.exists():
            return -1
        tags = PROMPT_TAGS_BY_TREE[tree]
        text = md.read_text(encoding="utf-8")
        total = 0
        for m in re.finditer(r"```[a-z]*\n(.*?)```", text, re.S):
            body = m.group(1)
            for tag in tags:
                stripped = re.sub(rf"<{tag}>[^\n]*?</{tag}>", "", body)
                total += len(re.findall(rf"^\s*<{tag}>", stripped, re.M))
        return total

    problems = []
    prompted = set()
    for tree in TREES:
        for md in (ROOT / tree).rglob("*.md"):
            rel = str(md.relative_to(ROOT / tree))
            if rel == "SUMMARY.md":
                continue
            prompted.add(rel)

    for rel in sorted(prompted):
        if pathlib.Path(rel).name in EXCLUDE:
            continue
        counts = {}
        for tree in TREES:
            md = ROOT / tree / rel
            if md.exists():
                c = count_blocks(md, tree)
                counts[tree] = c  # include 0 so missing trees are flagged
        if len(counts) >= 2 and len(set(counts.values())) > 1:
            detail = ", ".join(f"{t}={c}" for t, c in counts.items())
            problems.append(f"{rel}: {detail}")

    return problems


def gate_m7() -> list[str]:
    """Expired verified facts. Shelf life: 18 months.

    Scans claims markers (<!-- claims: verified YYYY-MM -->) in chapter prose
    and `verified:` fields in constraints.yaml. Reports any older than
    SHELF_LIFE_MONTHS.
    """
    import datetime
    SHELF_LIFE_MONTHS = 18

    now = datetime.date.today()
    cutoff = now.replace(year=now.year - SHELF_LIFE_MONTHS // 12)
    # Proper 18-month cutoff
    months_ago = now.month - SHELF_LIFE_MONTHS
    year_adj = now.year
    while months_ago <= 0:
        months_ago += 12
        year_adj -= 1
    cutoff = datetime.date(year_adj, months_ago, now.day)

    problems = []
    CLAIMS_PATTERN = re.compile(r"<!--\s*claims:\s*verified\s+(\d{4}-\d{2})\s*-->")

    for tree in TREES:
        for md in sorted((ROOT / tree).rglob("*.md")):
            text = md.read_text(encoding="utf-8")
            for m in CLAIMS_PATTERN.finditer(text):
                verified_str = m.group(1)
                try:
                    verified_date = datetime.date.fromisoformat(verified_str + "-01")
                except ValueError:
                    continue
                if verified_date < cutoff:
                    rel = f"{tree}/{md.relative_to(ROOT / tree)}"
                    line_no = text[:m.start()].count("\n") + 1
                    problems.append(f"{rel}:{line_no} verified {verified_str} (expired)")

    # Check constraints.yaml
    constraints_path = ROOT / "ontology" / "constraints.yaml"
    if constraints_path.exists():
        import yaml
        with open(constraints_path) as f:
            constraints = yaml.safe_load(f)
        for c in constraints:
            if isinstance(c, dict):
                verified_str = c.get("verified", "")
                if verified_str:
                    try:
                        verified_date = datetime.date.fromisoformat(verified_str + "-01")
                    except ValueError:
                        continue
                    if verified_date < cutoff:
                        problems.append(
                            f"ontology/constraints.yaml: {c.get('id', '?')} verified {verified_str} (expired)"
                        )

    return sorted(problems)


# Structure checks all come out of one pass over the trees; gates are independent.
STRUCTURE = [
    ("anchors", "in-page anchors"),
    ("xanchors", "cross-file anchors"),
    ("links", "cross-file links"),
    ("python", "python blocks compile"),
    ("parity", "trilingual parity"),
]
GATES = [
    ("M1", "claims sourced", gate_m1),
    ("M2", "boundary sections", gate_m2),
    ("M4", "external links", gate_m4),
    ("M5", "orphan pages", gate_m5),
    ("M6", "section numbering", gate_m6),
    ("N1", "prompt tags balanced", gate_n1),
    ("N2", "deps declared", gate_n2),
    ("N3", "prompt self-check", gate_n3),
    ("N4", "prompt output format", gate_n4),
    ("N5", "self-check uniqueness", gate_n5),
    ("N6", "trilingual prompt parity", gate_n6),
    ("M7", "expired verified facts", gate_m7),
]


# --------------------------------------------------------------------------
# link probe
# --------------------------------------------------------------------------


def probe_links() -> None:
    """One network pass. Hard failure means 404, 410 or DNS.

    A HEAD failure is never trusted: Kaggle Learn and shopify.com/magic both
    answer HEAD with 404 while serving fine over GET, and treating those as dead
    sends you editing links that work in a browser. 403 and 429 are soft — plenty
    of sites simply refuse scripted requests.
    """
    import time
    import urllib.error
    import urllib.request

    ua = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
          "(KHTML, like Gecko) Chrome/125 Safari/537.36")
    urls = external_urls()
    cache = json.loads(LINK_CACHE.read_text(encoding="utf-8")) if LINK_CACHE.exists() else {}
    cache = {u: v for u, v in cache.items() if u in urls}      # drop URLs no longer referenced
    todo = [u for u in sorted(urls) if u not in cache]
    print(f"probing {len(todo)} of {len(urls)} unique URLs ({len(urls) - len(todo)} cached)")

    for i, u in enumerate(todo, 1):
        req = urllib.request.Request(u, method="HEAD", headers={"User-Agent": ua})
        try:
            with urllib.request.urlopen(req, timeout=15) as r:
                cache[u] = {"status": r.status, "hard_fail": False}
        except urllib.error.HTTPError:
            try:
                req.method = "GET"
                with urllib.request.urlopen(req, timeout=20) as r:
                    cache[u] = {"status": r.status, "hard_fail": False}
            except urllib.error.HTTPError as e2:
                cache[u] = {"status": e2.code, "hard_fail": e2.code in (404, 410)}
            except Exception as e2:
                cache[u] = {"status": str(e2)[:40], "hard_fail": False}
        except Exception as e:
            reason = str(getattr(e, "reason", e))
            hard = any(k in reason.lower() for k in ("name or service", "nodename", "getaddrinfo"))
            cache[u] = {"status": reason[:60], "hard_fail": hard}
        if i % 25 == 0:
            print(f"  {i}/{len(todo)}")
            LINK_CACHE.write_text(json.dumps(cache, ensure_ascii=False, indent=1, sort_keys=True), encoding="utf-8")
        time.sleep(0.3)

    LINK_CACHE.write_text(json.dumps(cache, ensure_ascii=False, indent=1, sort_keys=True), encoding="utf-8")
    hard = sum(1 for v in cache.values() if v.get("hard_fail"))
    print(f"done: {len(cache)} cached, {hard} dead")


def anchors_vs_build(build_dir: str) -> int:
    """Diff anchors derived from markdown against the ids mdBook emitted.

    This is the check that keeps slugify() honest. Everything else in this file
    trusts it, so it is worth re-running whenever slugify changes or mdBook is
    upgraded.
    """
    pat = re.compile(r'<h[1-6] id="([^"]+)"><a class="header" href="#[^"]+">(.*?)</a></h[1-6]>', re.S)
    built: dict[str, set[str]] = collections.defaultdict(set)
    total = 0
    root = pathlib.Path(build_dir)
    for f in sorted(root.rglob("*.html")):
        rel = str(f.relative_to(root))
        if rel == "print.html" or rel.startswith(("en/", "ja/")):
            continue
        for m in pat.finditer(f.read_text(encoding="utf-8")):
            built[rel].add(htmlmod.unescape(m.group(1)))
            total += 1
    bad = 0
    for html_rel, anchors in sorted(built.items()):
        md = ROOT / "src" / html_rel.replace(".html", ".md")
        if not md.exists():
            continue
        mine = page_anchors(md.read_text(encoding="utf-8"))
        if anchors - mine or mine - anchors:
            bad += 1
            print(f"  {html_rel}")
            if anchors - mine:
                print(f"     only in build:  {sorted(anchors - mine)[:3]}")
            if mine - anchors:
                print(f"     only in source: {sorted(mine - anchors)[:3]}")
    print(f"\n{total} headings in {len(built)} pages; {bad} pages disagree")
    return 1 if bad else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--list", action="store_true", help="print offending items, not just counts")
    ap.add_argument("--only", metavar="NAME", help="run one check (anchors, M1, …)")
    ap.add_argument("--probe-links", action="store_true", help="re-probe external URLs")
    ap.add_argument("--anchors-vs-build", metavar="DIR", help="diff anchors against built HTML")
    args = ap.parse_args()

    if args.probe_links:
        probe_links()
        return 0
    if args.anchors_vs_build:
        return anchors_vs_build(args.anchors_vs_build)

    wanted = [n for n, _ in STRUCTURE] + [n for n, _, _ in GATES]
    if args.only:
        if args.only not in wanted:
            print(f"unknown check: {args.only} (have {', '.join(wanted)})")
            return 2
        wanted = [args.only]

    results = []
    if any(n in wanted for n, _ in STRUCTURE):
        structure = check_structure()
        results += [(n, lb, structure[n]) for n, lb in STRUCTURE if n in wanted]
    results += [(n, lb, fn()) for n, lb, fn in GATES if n in wanted]

    total = 0
    for name, label, items in results:
        total += len(items)
        mark = "ok " if not items else "FAIL"
        print(f"  [{mark}] {name:9s} {label:24s} {len(items)}")
        if args.list:
            for it in items:
                print(f"           {it}")
    print(f"\n  total {total}")
    if total and not args.list:
        print("  re-run with --list to see them")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
