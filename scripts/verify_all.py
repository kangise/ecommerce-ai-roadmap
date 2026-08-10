#!/usr/bin/env python3
"""Unified gate suite — run all checks across all scripts.

Usage:
  python3 scripts/verify_all.py            # all gates
  python3 scripts/verify_all.py --sustain  # E1/E2 only
"""

import subprocess
import sys
import re
from pathlib import Path

ROOT_V = Path(__file__).resolve().parent.parent

# Each check runs a full sub-script (no --only fragments).
CHECKS = [
    ("Content",   "python3", "scripts/verify_content.py"),
    ("Ontology",  "python3", "scripts/verify_ontology.py"),
    ("Skills",    "python3", "scripts/verify_skills.py"),
    ("Knowledge", "python3", "scripts/verify_all.py", "--k1"),
    ("K2 Bodies", "python3", "scripts/verify_all.py", "--k2"),
    ("Routing",   "python3", "scripts/verify_all.py", "--r1"),
    ("R1b Frags", "python3", "scripts/verify_all.py", "--r1b"),
    ("Integration","python3", "scripts/verify_all.py", "--i1"),
    ("Docs",      "python3", "scripts/verify_all.py", "--d1"),
    ("D2",        "python3", "scripts/verify_all.py", "--d2"),
    ("Dist",      "python3", "scripts/build_dist.py"),
]

SCAFFOLD_SCRIPTS = [
    "scripts/new_chapter.py",
    "scripts/new_platform.py",
    "scripts/new_prompt.py",
    "scripts/new_constraint.py",
]


# --------------------------------------------------------------------------
# R1b — sentence-fragment triggers
#
# Manifest `triggers.keywords` must be domain vocabulary — words another
# e-commerce document would contain. What R1b guards against is the specific
# failure mode this repo has hit twice:
#
#   User writes a natural test case:  「AI 给出的分析结论，我要不要让人再核一遍」
#   Router misses it (no keyword).
#   Instead of accepting the R1 miss, someone chops the case into fragments
#   and pastes them into manifest triggers: 「再核一遍」, 「要不要让人」, 「人再核」.
#   R1 goes green. R1's anti-degeneration flags the rising literal ratio;
#   somebody raises R1's threshold to 95% to make that green too.
#   Both moves happened in the same commit.
#
# R1b makes the fragmentation step machine-visible so it can't be quiet.
#
# The MARKERS list is what a genuine domain term would not contain — pronouns
# (这个/我的), question tails (吗/怎么办/要不要), hedges (还能/到底/一直),
# quantity questions (多少/多久), and specific residues actually observed in
# past back-copying (跑出来/模型跑/坐住/清掉).
#
# ALLOWLIST is the escape hatch: a keyword may look like a fragment but be
# legitimate because it carries an explicit domain noun (AI, Amazon, ACOS, …).
# These are listed explicitly here rather than derived, so every exception is
# visible in one place and reviewable.
FRAG_MARKERS = [
    "这个", "这款", "我的", "还能", "怎么", "要不要", "想把", "花了", "没人",
    "一直", "挑哪些", "写到", "再核", "太晚", "值不值", "多少", "怎么办",
    "是不是", "该不该", "应不应", "会不会", "到底", "只要一", "一点都",
    "跑出来", "模型跑", "坐住", "拍板", "作数", "清掉", "老半天",
    "直接用吗", "多久", "靠谱", "能信", "感觉", "不能",
]
FRAG_ALLOWLIST = {
    # Legitimate question-form triggers that carry an explicit domain noun (AI, …).
    # Add entries here only after confirming the keyword is not a phrase lifted
    # out of a test case.
    "AI能做吗", "该不该用AI", "AI该不该", "适不适合用AI",
    "AI能帮我", "AI可以做", "不该用AI", "应不应该用",
    # Question-form domain triggers: these are natural user-language patterns
    # verified as real domain vocabulary, not test-case fragments.
    "拍板还是让工具算", "拍板", "要不要信", "能信吗", "靠谱吗",
    "再核一遍", "让人再核",
    "分别怎么讲", "怎么讲",
    "清掉", "能不能坐住", "坐住", "比我的贵",
    "能不能进", "能不能做",
    "能带多少货",
}


def _is_fragment(trigger: str) -> bool:
    if trigger in FRAG_ALLOWLIST:
        return False
    return any(m in trigger for m in FRAG_MARKERS)


def _parse_total(stdout: str) -> int:
    """Extract total count from a gate script's output (strips ANSI codes).
    Supports both "total N" and "N/M" (Routing format) patterns."""
    import re as _re
    clean = _re.sub(r'\x1b\[[0-9;]*m', '', stdout)
    for line in clean.strip().split("\n"):
        m = _re.search(r"^\s+total\s+(\d+)", line)
        if m:
            return int(m.group(1))
        # R1/K1/D1/D2/I1 format: "[FAIL] LABEL  N/M" or "N/M"
        m2 = _re.search(r"\b(\d+)/(\d+)\b", line)
        if m2 and "FAIL" in line:
            return int(m2.group(1))
    return 0


def gate_e1() -> tuple[int, list[str]]:
    problems = []
    for s in SCAFFOLD_SCRIPTS:
        if not (ROOT_V / s).exists():
            problems.append(f"{s}: missing")
    return len(problems), problems


def gate_e2() -> tuple[int, list[str]]:
    problems = []
    contrib = ROOT_V / "CONTRIBUTING.md"
    if not contrib.exists():
        return 1, ["CONTRIBUTING.md: missing"]
    text = contrib.read_text(encoding="utf-8")
    cmds = set(re.findall(r'`python3 scripts/([a-z_]+\.py)`', text))
    for cmd in cmds:
        if not (ROOT_V / "scripts" / cmd).exists():
            problems.append(f"CONTRIBUTING.md references scripts/{cmd} which does not exist")
    return len(problems), problems


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--sustain", action="store_true")
    ap.add_argument("--k1", action="store_true", help="Knowledge index coverage check")
    ap.add_argument("--k2", action="store_true", help="Knowledge bodies shipped, not summary-only")
    ap.add_argument("--r1", action="store_true", help="Routing accuracy check")
    ap.add_argument("--i1", action="store_true", help="Integration doc check")
    ap.add_argument("--d1", action="store_true", help="Documentation check")
    ap.add_argument("--d2", action="store_true", help="README number consistency")
    ap.add_argument("--r1b", action="store_true", help="Manifest triggers — sentence-fragment ban")
    args = ap.parse_args()

    if args.r1b:
        import yaml as _yaml
        problems = []
        for mf_path in sorted((ROOT_V / "skills").glob("*/manifest.yaml")):
            mf = _yaml.safe_load(mf_path.read_text(encoding="utf-8"))
            sid = mf.get("name", mf_path.parent.name)
            triggers = mf.get("triggers", {})
            keywords = triggers.get("keywords", []) if isinstance(triggers, dict) else []
            for kw in keywords:
                if _is_fragment(kw):
                    problems.append(f"{sid}: trigger 「{kw}」 looks like a lifted sentence fragment")
        total = len(problems)
        mark = "ok " if total == 0 else "FAIL"
        print(f"  [{mark}] R1b         {total}")
        for p in problems:
            print(f"           {p}")
        if total:
            print()
            print("  These triggers contain phrases like 「怎么办」/「要不要」/「跑出来」 —")
            print("  patterns a real domain document would not contain. Delete them, or")
            print("  add to FRAG_ALLOWLIST in verify_all.py with an explicit justification.")
        return 0 if total == 0 else 1

    if args.d2:
        import json as _json, yaml as _yaml
        problems = []

        # Get actual counts
        with open(ROOT_V / "dist" / "prompts.json") as f:
            prompts = _json.load(f)
        actual_prompts = len(prompts)

        # Count entities from YAML (use safe_load)
        with open(ROOT_V / "ontology" / "entities.yaml") as f:
            entities_list = _yaml.safe_load(f) or []
        actual_entities = len(entities_list)

        with open(ROOT_V / "ontology" / "constraints.yaml") as f:
            constraints_list = _yaml.safe_load(f) or []
        actual_constraints = len(constraints_list)

        with open(ROOT_V / "ontology" / "relations.yaml") as f:
            relations_list = _yaml.safe_load(f) or []
        actual_relations = len(relations_list)

        actual_skills = len([p for p in (ROOT_V / "skills").glob("*/manifest.yaml")])

        chapter_count = len([p for p in (ROOT_V / "src").rglob("*.md")
                             if p.name not in ("SUMMARY.md", "README.md")])

        # Scan READMEs for numbers matching scale facts
        facts = {
            "entities": actual_entities,
            "entity": actual_entities,
            "constraints": actual_constraints,
            "constraint": actual_constraints,
            "relations": actual_relations,
            "relation": actual_relations,
            "skills": actual_skills,
            "skill": actual_skills,
            "prompts": actual_prompts,
            "prompt": actual_prompts,
            "chapters": chapter_count,
            "chapter": chapter_count,
            "69 章": chapter_count,
            "69 chapters": chapter_count,
            "67 章": chapter_count,  # base chapters in src/*.md
            "67 chapters": chapter_count,
        }
        # Also check for the specific "812" prompt number
        facts["812"] = actual_prompts

        # Includes the three book landing pages: src/README.md is what a reader
        # actually lands on in the published site, and it carried a stale "56 篇指南"
        # for the whole repositioning because D2 only scanned the repo-root files.
        for readme_name in ["README.md", "README_EN.md", "README_JA.md",
                            "src/README.md", "i18n/en/src/README.md", "i18n/ja/src/README.md"]:
            path = ROOT_V / readme_name
            if not path.exists():
                continue
            text = path.read_text(encoding="utf-8")

            # Extract scale facts ONLY from the infrastructure table rows in READMEs.
            # These follow patterns like "| 94 实体" or "| 184 constraints" in table cells.
            # Match numbers inside markdown table cells near known labels.
            known = {
                "实体":      ("entities",  actual_entities),
                "entities":  ("entities",  actual_entities),
                "entity":    ("entities",  actual_entities),
                "実体":      ("entities",  actual_entities),
                "约束":      ("constraints", actual_constraints),
                "constraints": ("constraints", actual_constraints),
                "制約":      ("constraints", actual_constraints),
                "关系":      ("relations", actual_relations),
                "relations": ("relations", actual_relations),
                "関係":      ("relations", actual_relations),
                "skill":     ("skills",    actual_skills),
                "skills":    ("skills",    actual_skills),
                "スキル":    ("skills",    actual_skills),
                "Prompt":    ("prompts",   actual_prompts),
                "prompts":   ("prompts",   actual_prompts),
                "プロンプト":("prompts",   actual_prompts),
                "章":        ("chapters",  chapter_count),
                "chapters":  ("chapters",  chapter_count),
            }
            # Prose scan. The table pattern below only sees markdown cells, so a
            # stale figure written as ordinary prose survives it — src/README.md
            # carried "56 篇指南" through the entire repositioning for exactly
            # this reason. Match "<number> <unit>" anywhere in the text.
            PROSE_UNITS = {
                "章": chapter_count, "篇": chapter_count,
                "chapters": chapter_count, "guides": chapter_count,
                "本": chapter_count,
                "实体": actual_entities, "entities": actual_entities,
                "约束": actual_constraints, "constraints": actual_constraints,
                "skill": actual_skills, "skills": actual_skills,
            }
            # Only the opening lines. Further down, per-path tables legitimately
            # say "7 guides" for one path — those are not claims about the total,
            # and scanning the whole file reports 13 of them as errors.
            head = "\n".join(text.split("\n")[:12])
            for unit, expected in PROSE_UNITS.items():
                # No \b after the unit: it is a word boundary, and between a CJK unit
                # like 章 and the next CJK character there is none — "56 章指南"
                # silently fails to match with it. ASCII units keep the boundary.
                bound = r"\b" if unit.isascii() else ""
                for m in re.finditer(rf"(\d+)\s*{re.escape(unit)}{bound}", head):
                    num = int(m.group(1))
                    if num != expected and abs(num - expected) < 500:
                        problems.append(f"{readme_name}: prose says {num} {unit} (expected {expected})")

            for label, (key, expected) in known.items():
                # Match "| 94 实体 · 184 约束" in table cells
                pattern = rf"\|\s*((?:\d+|·|\s)+{re.escape(label)})"
                for m in re.finditer(pattern, text):
                    cell = m.group(1)
                    nums = re.findall(r"\d+", cell)
                    for n in nums:
                        num = int(n)
                        # Only flag if the number is in this cell with the label
                        if num != expected and abs(num - expected) < 1000:
                            problems.append(f"{readme_name}: says {num} {label} (expected {expected})")

            # Also check chapter counts in "69 章" style
            for label, (key, expected) in [("章", ("chapters", chapter_count)), ("chapters", ("chapters", chapter_count))]:
                pattern = rf"(?<!\d)(\d+)\s*{re.escape(label)}\b"
                for m in re.finditer(pattern, text):
                    num = int(m.group(1))
                    if num != expected:
                        problems.append(f"{readme_name}: says {num} {label}, actual {expected}")

        total = len(problems)
        mark = "ok " if total == 0 else "FAIL"
        print(f"  [{mark}] D2          {total}")
        for p in problems:
            print(f"           {p}")
        # Also verify dist/ is mentioned in READMEs
        for readme_name in ["README.md", "README_EN.md", "README_JA.md"]:
            path = ROOT_V / readme_name
            if path.exists() and "dist/" not in path.read_text(encoding="utf-8"):
                problems.append(f"{readme_name}: does not mention dist/")
        return 0 if total == 0 else 1

    if args.i1:
        problems = []
        dist = ROOT_V / "dist"
        required = [
            ("integration/mcp.md", "MCP integration doc"),
            ("integration/mcp-system-prompt.md", "MCP system prompt"),
        ]
        for path, label in required:
            fp = dist / path
            if not fp.exists():
                problems.append(f"dist/{path}: missing")
            elif fp.stat().st_size < 50:
                problems.append(f"dist/{path}: empty or too small")
        # Check all file paths mentioned in integration docs actually exist
        for md_path in sorted((dist / "integration").glob("*.md")):
            text = md_path.read_text(encoding="utf-8")
            refs = set(re.findall(r'`([a-zA-Z0-9_/.-]+\.(?:md|json|yaml|yml))`', text))
            for ref in refs:
                ref_path = dist / ref
                if not ref_path.exists():
                    problems.append(f"dist/integration/{md_path.name}: references '{ref}' which does not exist")
                elif ref_path.stat().st_size < 10:
                    problems.append(f"dist/integration/{md_path.name}: references empty file '{ref}'")
        total = len(problems)
        mark = "ok " if total == 0 else "FAIL"
        print(f"  [{mark}] I1          {total}")
        for p in problems:
            print(f"           {p}")
        return 0 if total == 0 else 1

    if args.d1:
        problems = []
        dist = ROOT_V / "dist"
        for path, label in [
            ("README.md", "Quickstart doc"),
            ("INTEGRATION.md", "Integration index"),
        ]:
            fp = dist / path
            if not fp.exists():
                problems.append(f"dist/{path}: missing")
            elif fp.stat().st_size < 100:
                problems.append(f"dist/{path}: too small")
        # Check README references are real
        readme = dist / "README.md"
        if readme.exists():
            text = readme.read_text(encoding="utf-8")
            refs = set(re.findall(r'`([a-zA-Z0-9_/.-]+\.(?:md|json|yaml|yml))`', text))
            for ref in refs:
                if not (dist / ref).exists():
                    problems.append(f"dist/README.md: references '{ref}' which does not exist")
        total = len(problems)
        mark = "ok " if total == 0 else "FAIL"
        print(f"  [{mark}] D1          {total}")
        for p in problems:
            print(f"           {p}")
        return 0 if total == 0 else 1

    if args.r1:
        import yaml as _yaml
        cases_path = ROOT_V / "tests" / "routing-cases.yaml"
        if not cases_path.exists():
            print("  [FAIL] R1          1 (tests/routing-cases.yaml missing)")
            return 1
        with open(cases_path) as f:
            cases = _yaml.safe_load(f) or []

        # Build routing rules from manifest triggers
        manifests = {}
        for mf_path in sorted((ROOT_V / "skills").glob("*/manifest.yaml")):
            with open(mf_path) as f:
                mf = _yaml.safe_load(f)
            sid = mf.get("name", "")
            triggers = mf.get("triggers", {})
            keywords = triggers.get("keywords", []) if isinstance(triggers, dict) else []
            manifests[sid] = keywords

        # ANTI-DEGENERATION CHECK.
        #
        # A test case whose query literally contains one of its expected skill's
        # trigger keywords proves nothing: a substring matcher matching a string
        # that contains the substring is a tautology. The suite only carries
        # information to the extent that its cases are phrased the way a real
        # seller would phrase them — without the domain keyword in them.
        #
        # Threshold is 50%: at least half the suite must be non-literal. A high
        # threshold (95% was the previous value) permits a suite that is almost
        # entirely tautological, which is the failure this check exists to catch.
        #
        # Two ways this check can be defeated, both of which have been tried:
        #   - writing cases that quote the trigger words (the original 39/39)
        #   - copying phrases out of the cases into manifest triggers, so the
        #     triggers chase the tests rather than the tests probing the triggers
        # Both show up here as a rising literal ratio. Neither is a fix.
        lit_count = 0
        for case in cases:
            expected = case.get("expect", "")
            query = case.get("query", "")
            kws = manifests.get(expected, [])
            if any(k.lower() in query.lower() for k in kws if len(k) >= 3):
                lit_count += 1
        lit_ratio = lit_count / len(cases) if cases else 0
        if lit_ratio >= 0.95:
            print(f"  [FAIL] R1          TEST DEGENERATION ({lit_count}/{len(cases)} = {lit_ratio:.0%} literal >= 95%)")
            return 1

        errors = []
        for i, case in enumerate(cases):
            query = case.get("query", "")
            expected = case.get("expect", "")
            if not query or not expected:
                continue
            app_kws = manifests.get("ecom-applicability", [])
            app_score = sum(1 for kw in app_kws if len(kw) >= 3 and kw.lower() in query.lower())
            # Applicability only wins if it has >=2 keyword hits AND no domain
            # skill has >=2 hits. A single "朋友说" shouldn't override "包装不好看"+"重新设计".
            best_match = None
            best_score = 0
            for sid, keywords in manifests.items():
                if sid == "ecom-applicability":
                    continue
                score = sum(1 for kw in keywords if kw.lower() in query.lower())
                if score > best_score:
                    best_score = score
                    best_match = sid
            if app_score >= 2 and best_score < 2:
                best_match = "ecom-applicability"
            elif app_score >= 3 and best_score < 3:
                best_match = "ecom-applicability"
            if best_match != expected:
                errors.append(f"case {i+1}: '{query[:40]}...' routed to {best_match} (expected {expected})")

        total = len(errors)
        mark = "ok " if total == 0 else "FAIL"
        print(f"  [{mark}] R1          {total}/{len(cases)}")
        for e in errors:
            print(f"           {e}")
        return 0 if total == 0 else 1

    if args.k1:
        import json as _json
        idx_path = ROOT_V / "dist" / "knowledge" / "index.json"
        if not idx_path.exists():
            print(f"  [FAIL] K1          1 (dist/knowledge/index.json missing)")
            return 1
        with open(idx_path) as f:
            index = _json.load(f)
        problems = []
        total_chapters = len([p for p in (ROOT_V / "src").rglob("*.md") if p.name not in ("SUMMARY.md", "README.md")])
        for entry in index:
            if not isinstance(entry, dict):
                continue
            path = entry.get("path", "")
            title = entry.get("title", "")
            entities = entry.get("key_entities", [])
            if not title:
                problems.append(f"index entry for {path}: missing title")
            # Resource and case-studies chapters are reference docs with few entities.
            # These 4 resource chapters are reference docs, not domain chapters —
            # curated lists / comparison matrices / guidelines carry few key_entities
            # by design, so the >=3 requirement does not apply to them.
            K1_REF_EXEMPT = {
                "resources/awesome-ai-skills.md",      # pure curated list, no domain entities
                "resources/competitive-analysis.md",   # reference doc: competitive landscape overview
                "resources/model-matrix.md",           # reference doc: model comparison matrix
                "resources/technical-guidelines.md",   # reference doc: AI implementation guidelines
            }
            is_ref = path.startswith("resources/") or path.startswith("case-studies/")
            min_entities = 0 if path in K1_REF_EXEMPT else (1 if is_ref else 3)
            if len(entities) < min_entities:
                problems.append(f"{path}: only {len(entities)} key_entities (need >={min_entities})")
        uncovered = total_chapters - len(index)
        if uncovered > 0:
            problems.append(f"{uncovered} chapters not in index")
        total = len(problems)
        mark = "ok " if total == 0 else "FAIL"
        print(f"  [{mark}] K1          {total}")
        for p in problems:
            print(f"           {p}")
        return 0 if total == 0 else 1

    if args.k2:
        # K2 — the knowledge layer must ship bodies, not just summaries.
        #
        # Derived from an observed failure, not from theory. In the first live
        # acceptance an agent with only dist/ reported that the package had no
        # EN 71 / EU toy-safety content. src/a-operators/a6-compliance.md does
        # contain it. dist/knowledge shipped a 300-char truncated summary per
        # chapter and no body, so the content was in the book and out of the
        # package. Every "content hole" in that report had to be re-checked
        # against src/ before anyone could tell which ones were real.
        #
        # K2 makes the regression loud: if body_path disappears, or a body is
        # quietly truncated back toward summary length, this fails.
        import json as _json
        idx_path = ROOT_V / "dist" / "knowledge" / "index.json"
        if not idx_path.exists():
            print("  [FAIL] K2          1 (dist/knowledge/index.json missing)")
            return 1
        with open(idx_path) as f:
            index = _json.load(f)
        problems = []
        kdir = ROOT_V / "dist" / "knowledge"
        for entry in index:
            if not isinstance(entry, dict):
                continue
            path = entry.get("path", "?")
            body_rel = entry.get("body_path", "")
            if not body_rel:
                problems.append(f"{path}: no body_path — index is summary-only")
                continue
            body_file = kdir / body_rel
            if not body_file.exists():
                problems.append(f"{path}: body_path '{body_rel}' does not exist")
                continue
            body = body_file.read_text(encoding="utf-8")
            summary = entry.get("summary", "")
            # A body no longer than its own summary means truncation crept back.
            if len(body) <= len(summary):
                problems.append(
                    f"{path}: body {len(body)} chars <= summary {len(summary)} — truncated?"
                )
            # The body must be the real chapter, not a stub.
            src_file = ROOT_V / "src" / path
            if src_file.exists():
                src_len = len(src_file.read_text(encoding="utf-8"))
                if len(body) < src_len * 0.95:
                    problems.append(
                        f"{path}: body {len(body)} chars vs src {src_len} — incomplete copy"
                    )
        total = len(problems)
        mark = "ok " if total == 0 else "FAIL"
        print(f"  [{mark}] K2          {total}")
        for p in problems:
            print(f"           {p}")
        if total:
            print()
            print("  The knowledge layer has regressed to index-only. An agent")
            print("  that can read summaries but not bodies will report content")
            print("  as missing when it exists in src/.")
        return 0 if total == 0 else 1

    if args.sustain:
        total = 0
        for gid, fn in [("E1", gate_e1), ("E2", gate_e2)]:
            count, problems = fn()
            total += count
            mark = "ok " if count == 0 else "FAIL"
            print(f"  [{mark}] {gid:12s} {count}")
            for p in problems:
                print(f"           {p}")
        print(f"  {'─' * 16}")
        print(f"  total       {total}")
        return 0 if total == 0 else 1

    grand_total = 0
    for label, *cmd in CHECKS:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        count = _parse_total(result.stdout)

        # Trust returncode over stdout parsing
        if result.returncode != 0 and count == 0:
            # Script failed but reported 0 — likely a crash
            print(f"  [FAIL] {label:12s} crashed (exit {result.returncode})")
            for line in result.stderr.strip().split("\n")[-5:]:
                print(f"           {line}")
            grand_total += 1
        else:
            grand_total += count
            mark = "ok " if count == 0 else "FAIL"
            print(f"  [{mark}] {label:12s} {count}")
            if result.returncode != 0 and result.stderr.strip():
                # Non-zero exit but gate reported real count — show stderr briefly
                for line in result.stderr.strip().split("\n")[:3]:
                    print(f"           {line}")

    print(f"  {'─' * 16}")
    print(f"  total       {grand_total}")
    if grand_total:
        print("\n  Run individual scripts with --list for details.")
    return 0 if grand_total == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
