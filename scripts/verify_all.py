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

# Each check runs a full sub-script (no --only fragments). The distributable is
# checked first because several later gates intentionally read it. `--check`
# rebuilds into a temporary directory and never mutates the worktree.
CHECKS = [
    ("Dist",      "python3", "scripts/build_dist.py", "--check"),
    ("Content",   "python3", "scripts/verify_content.py"),
    ("Ontology",  "python3", "scripts/verify_ontology.py"),
    ("Skills",    "python3", "scripts/verify_skills.py"),
    ("Knowledge", "python3", "scripts/verify_all.py", "--k1"),
    ("K2 Bodies", "python3", "scripts/verify_all.py", "--k2"),
    ("Routing",   "python3", "scripts/verify_all.py", "--r1"),
    ("R1b Frags", "python3", "scripts/verify_all.py", "--r1b"),
    ("R2 Natural","python3", "scripts/verify_all.py", "--r2"),
    ("S6 Attrib", "python3", "scripts/verify_all.py", "--s6"),
    ("Integration","python3", "scripts/verify_all.py", "--i1"),
    ("Docs",      "python3", "scripts/verify_all.py", "--d1"),
    ("D2",        "python3", "scripts/verify_all.py", "--d2"),
    ("Sustain",   "python3", "scripts/verify_all.py", "--sustain"),
]


def _interp(cmd):
    """Run subchecks under the *same* interpreter as the parent.

    The CHECKS table spells the interpreter as "python3" so it reads like the
    documented command line, but a literal "python3" resolves via PATH — under a
    venv or tox that can be a different interpreter than the one running this
    file, and the subcheck then fails on imports the parent already has.
    """
    return [sys.executable if cmd[0] == "python3" else cmd[0], *cmd[1:]]


# R1 combines domain keywords with reusable conversational intent patterns.
# Every case is blocking; R1b and R2 prevent gaming it with copied fragments or
# tautological tests.
R1_MAX_MISROUTES = 0

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
    # Second sweep — 11709a3 slipped 17 fragments past R1b by adding them to the
    # allowlist instead. These markers catch that shape: command verbs (帮我, 写一个,
    # 重写), residues (没出, 一单, 让人, 让工具), and comparison/quantity tails.
    "帮我", "写一个", "重写", "改一下", "没出", "一单", "没写", "涨到",
    "让人", "让工具", "能带", "能不能", "比我", "还是让", "得不好", "一下",
    "换季了", "算下来", "数据不多", "交给机器", "风险大", "上要", "上开始",
]
FRAG_ALLOWLIST = {
    # An escape hatch, not a bypass. Entries must be genuine domain vocabulary
    # that merely resembles a fragment — a term another e-commerce document would
    # contain. It carries an explicit domain noun (AI). Nothing goes here to
    # silence R1b; a fragment lifted from a test case is deleted, not allowlisted.
    #
    # 11709a3 added 17 entries here labelled "verified as real domain vocabulary"
    # — 拍板, 能信吗, 靠谱吗, 清掉, 坐住, 比我的贵 … none of which any e-commerce
    # document contains. That is the fifth time this gate was routed around; the
    # entries were removed and the triggers deleted from the manifests.
    "AI能做吗", "该不该用AI", "AI该不该", "适不适合用AI",
    "AI能帮我", "AI可以做", "不该用AI", "应不应该用",
}


def _is_fragment(trigger: str) -> bool:
    if trigger in FRAG_ALLOWLIST:
        return False
    return any(m in trigger for m in FRAG_MARKERS)


def _normalize(text: str) -> str:
    """Fold a query or trigger to a comparable form: strip whitespace, lowercase,
    fullwidth -> halfwidth.

    Why: the live acceptance run (v4 S5) routed 「能用 AI 做补货预测吗」 to the wrong
    skill because the applicability trigger 「AI做」 has no space and the query does.
    The MCP server already normalizes (integration/mcp-server.py `_norm`), but this
    gate matched raw, so R1 said 0 while the real router failed. Both sides must
    fold identically or R1 keeps green-lighting a router that misroutes. Fullwidth
    digits/letters (１２３ＡＢＣ) also fold, since sellers paste both forms.
    """
    folded = []
    for ch in text:
        o = ord(ch)
        if 0xFF01 <= o <= 0xFF5E:      # fullwidth ASCII -> halfwidth
            ch = chr(o - 0xFEE0)
        elif o == 0x3000:              # ideographic space -> normal space
            ch = " "
        folded.append(ch)
    return re.sub(r"\s+", "", "".join(folded)).lower()


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


def gate_e3() -> tuple[int, list[str]]:
    """Front-door files exist and are non-empty.

    Replaces tests/test_repo_properties.py, a pytest file that was 11/18 failing
    and wired into nothing. It asserted a Jekyll-era layout (`_config.yml`,
    `paths/`, `prompts/`) the repo replaced with mdBook long ago, and looked for
    case studies as `docs/case-studies/*.md` — docs/ is mdBook's HTML output, so
    that glob could only ever return 0. A checker nobody runs and that cannot
    pass is worse than no checker: it reads as coverage while asserting fiction.

    What survives here is the part still true and not covered elsewhere: the
    files a visitor or contributor lands on first.
    """
    problems = []
    required = [
        "README.md", "README_EN.md", "README_JA.md",
        "CHANGELOG.md", "CONTRIBUTING.md", "DISCLAIMER.md",
    ]
    for rel in required:
        p = ROOT_V / rel
        if not p.exists():
            problems.append(f"{rel}: missing")
        elif p.stat().st_size == 0:
            problems.append(f"{rel}: empty")

    # GitHub honours CODEOWNERS in any of three locations; this repo keeps it at
    # the root. Check all three rather than a hardcoded one — the first draft of
    # this gate asserted `.github/CODEOWNERS` and reported a missing file that
    # was present and working.
    owners = [ROOT_V / "CODEOWNERS", ROOT_V / ".github" / "CODEOWNERS",
              ROOT_V / "docs" / "CODEOWNERS"]
    found = [p for p in owners if p.exists() and p.stat().st_size > 0]
    if not found:
        problems.append("CODEOWNERS: missing from all of /, .github/, docs/")

    tmpl = ROOT_V / ".github" / "ISSUE_TEMPLATE"
    if not tmpl.is_dir():
        problems.append(".github/ISSUE_TEMPLATE/: missing")
    elif not any(tmpl.glob("*.md")):
        problems.append(".github/ISSUE_TEMPLATE/: no templates")

    # Case studies were an explicit content requirement; keep the floor, but
    # point it at the source tree rather than the build output.
    cases = ROOT_V / "src" / "case-studies"
    n = len([f for f in cases.glob("*.md") if f.name.lower() != "readme.md"]) if cases.is_dir() else 0
    if n < 2:
        problems.append(f"src/case-studies/: {n} case studies (minimum 2)")

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
    ap.add_argument("--r2", action="store_true", help="Natural-language routing probe (< 40%% literal)")
    ap.add_argument("--s6", action="store_true", help="Constraint attribution: playbook refs, no foreign ids, fresh")
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

    if args.s6:
        # S6 — constraint attribution. Three checks, all a consequence of
        # constraints.md being generated from the manifest rather than hand-kept:
        #   a. every id a playbook self-check references (<!-- ref: id -->) is in
        #      that skill's uses_constraints (else the skill cites a rule it
        #      doesn't declare — live-run G9, ecom-listing missing Shopify ids)
        #   b. constraints.md contains no id outside uses_constraints (else it
        #      carries foreign-domain rules — live-run G8, compliance holding
        #      advertising rules)
        #   c. the generated file is fresh (re-run the generator, expect no diff)
        import yaml as _yaml
        problems = []
        onto = _yaml.safe_load((ROOT_V / "ontology" / "constraints.yaml").read_text(encoding="utf-8")) or []
        valid = {c["id"] for c in onto if isinstance(c, dict) and "id" in c}
        for sk in sorted((ROOT_V / "skills").iterdir()):
            if not sk.is_dir():
                continue
            mf = sk / "manifest.yaml"
            if not mf.exists():
                continue
            m = _yaml.safe_load(mf.read_text(encoding="utf-8"))
            uses = set(m.get("uses_constraints") or [])
            pf = sk / "references" / "playbook.md"
            if pf.exists():
                refs = set(re.findall(r"<!--\s*ref:\s*([a-z0-9_.]+)\s*-->", pf.read_text(encoding="utf-8")))
                for r in refs & valid:
                    if r not in uses:
                        problems.append(f"{sk.name}: playbook references `{r}` not in uses_constraints")
            cf = sk / "references" / "constraints.md"
            if cf.exists():
                cited = set(re.findall(r"`([a-z_]+\.[a-z0-9_.]+)`", cf.read_text(encoding="utf-8")))
                for c in cited:
                    if c in valid and c not in uses:
                        problems.append(f"{sk.name}: constraints.md contains `{c}` outside uses_constraints")
        # freshness: regenerate to a temp and diff
        import subprocess as _sp
        before = {}
        for sk in sorted((ROOT_V / "skills").iterdir()):
            cf = sk / "references" / "constraints.md"
            if cf.exists():
                before[cf] = cf.read_text(encoding="utf-8")
        _sp.run(["python3", "scripts/gen_skill_constraints.py"], cwd=ROOT_V,
                capture_output=True, text=True)
        for cf, old in before.items():
            if cf.read_text(encoding="utf-8") != old:
                problems.append(f"{cf.parent.parent.name}: constraints.md is stale — run gen_skill_constraints.py")
        total = len(problems)
        mark = "ok " if total == 0 else "FAIL"
        print(f"  [{mark}] S6          {total}")
        for p in problems:
            print(f"           {p}")
        return 0 if total == 0 else 1

    if args.r2:
        # R2 — the phrasing-first probe. routing-cases.yaml co-evolves with the
        # triggers (R1's residual is the honest gap on it); this set is written
        # query-first without looking at triggers, so its literal-hit ratio must
        # stay low or it has drifted into the same tautology R1 already fights.
        # Threshold 40% < R1's 50%: this set is meant to be the harder one.
        import yaml as _yaml
        path = ROOT_V / "tests" / "routing-cases-natural.yaml"
        if not path.exists():
            print("  [FAIL] R2          1 (tests/routing-cases-natural.yaml missing)")
            return 1
        cases = _yaml.safe_load(path.read_text(encoding="utf-8")) or []
        manifests = {}
        for mf_path in sorted((ROOT_V / "skills").glob("*/manifest.yaml")):
            mf = _yaml.safe_load(mf_path.read_text(encoding="utf-8"))
            triggers = mf.get("triggers", {})
            manifests[mf.get("name", "")] = (
                triggers.get("keywords", []) if isinstance(triggers, dict) else []
            )
        lit = sum(
            1 for c in cases
            if any(_normalize(k) in _normalize(c.get("query", ""))
                   for k in manifests.get(c.get("expect", ""), []) if len(k) >= 3)
        )
        ratio = lit / len(cases) if cases else 0
        if ratio >= 0.40:
            print(f"  [FAIL] R2          {lit}/{len(cases)} = {ratio:.0%} literal >= 40%")
            return 1
        print(f"  [ok ] R2          {lit}/{len(cases)} = {ratio:.0%} literal (< 40%)")
        return 0

    if args.d2:
        import json as _json, yaml as _yaml
        problems = []
        expected_gate_count = 43

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

            # Public READMEs must state the same total as CONTRIBUTING's gate
            # inventory. This drifted at 24 while the real suite grew to 42.
            for m in re.finditer(r"(\d+)\s*(?:项|項目の)?\s*CI\s+(?:门禁|ゲート|gates)", text, re.I):
                if int(m.group(1)) != expected_gate_count:
                    problems.append(
                        f"{readme_name}: says {m.group(1)} CI gates "
                        f"(expected {expected_gate_count})"
                    )

            # Extract scale facts ONLY from the infrastructure table rows in READMEs.
            # These follow patterns like "| 100 实体" or "| 322 constraints" in table cells.
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
                # Match "| 100 实体 · 322 约束" in table cells
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

        # Also verify dist/ is mentioned in READMEs
        for readme_name in ["README.md", "README_EN.md", "README_JA.md"]:
            path = ROOT_V / readme_name
            if path.exists() and "dist/" not in path.read_text(encoding="utf-8"):
                problems.append(f"{readme_name}: does not mention dist/")
        total = len(problems)
        mark = "ok " if total == 0 else "FAIL"
        print(f"  [{mark}] D2          {total}")
        for p in problems:
            print(f"           {p}")
        return 0 if total == 0 else 1

    if args.i1:
        problems = []
        dist = ROOT_V / "dist"
        required = [
            ("integration/mcp.md", "MCP integration doc"),
            ("integration/mcp-system-prompt.md", "MCP system prompt"),
            ("integration/runtime-api.md", "Runtime API guide"),
            ("openapi/runtime-api.yaml", "Runtime OpenAPI contract"),
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

        skill_ids = sorted(p.name for p in (dist / "skills").iterdir() if p.is_dir()) if (dist / "skills").is_dir() else []
        system_prompt = dist / "integration" / "mcp-system-prompt.md"
        if system_prompt.exists():
            prompt_text = system_prompt.read_text(encoding="utf-8")
            for skill_id in skill_ids:
                if skill_id not in prompt_text:
                    problems.append(f"dist/integration/mcp-system-prompt.md: missing skill {skill_id}")

        openapi_path = dist / "openapi" / "runtime-api.yaml"
        if openapi_path.exists():
            try:
                import json as _json
                import yaml as _yaml
                contract = _yaml.safe_load(openapi_path.read_text(encoding="utf-8")) or {}
                paths = contract.get("paths", {})
                required_operations = {
                    "/v1/users": {"get", "post"},
                    "/v1/demo-session": {"get"},
                    "/v1/users/{userId}": {"patch"},
                    "/v1/connectors": {"get", "post"},
                    "/v1/connectors/{accountId}": {"get", "patch"},
                    "/v1/connectors/{accountId}/health-check": {"post"},
                    "/v1/report-recipes": {"get", "post"},
                    "/v1/report-recipes/{recipeId}": {"get", "patch"},
                    "/v1/report-recipes/{recipeId}/sync": {"post"},
                    "/v1/report-syncs": {"get"},
                    "/v1/report-syncs/{syncId}": {"get"},
                    "/v1/actions": {"post"},
                    "/v1/actions/{actionId}/approve": {"post"},
                    "/v1/proposals": {"get", "post"},
                    "/v1/proposals/{proposalId}": {"get", "patch"},
                    "/v1/proposals/{proposalId}/submit": {"post"},
                    "/v1/proposals/{proposalId}/decisions": {"post"},
                    "/v1/proposals/{proposalId}/execute": {"post"},
                    "/v1/proposals/{proposalId}/retry": {"post"},
                    "/v1/proposal-executions": {"get"},
                    "/v1/proposal-executions/{executionId}": {"get"},
                    "/v1/evidence-imports": {"get", "post"},
                    "/v1/evidence-imports/{importId}": {"get"},
                    "/v1/evidence-imports/{importId}/metric-materialization": {"post"},
                    "/v1/metric-observations": {"get"},
                    "/v1/metric-observations/{observationId}": {"get"},
                    "/v1/metric-materializations": {"get"},
                    "/v1/metric-materializations/backfill": {"post"},
                    "/v1/agent-runs": {"get", "post"},
                    "/v1/agent-runs/{runId}": {"get"},
                    "/v1/agent-runs/{runId}/execute": {"post"},
                    "/v1/agent-runs/{runId}/evaluate": {"post"},
                    "/v1/agent-runs/{runId}/evaluations": {"get"},
                    "/v1/agent-graphs": {"get", "post"},
                    "/v1/agent-graphs/{graphId}": {"get"},
                    "/v1/agent-graphs/{graphId}/versions": {"post"},
                    "/v1/agent-graph-versions/{versionId}": {"get"},
                    "/v1/agent-graph-versions/{versionId}/publish": {"post"},
                    "/v1/daily-ops-schedules": {"get", "post"},
                    "/v1/daily-ops-schedules/{scheduleId}": {"get", "patch"},
                    "/v1/daily-ops-schedules/{scheduleId}/trigger": {"post"},
                    "/v1/daily-ops-runs": {"get"},
                    "/v1/daily-ops-runs/{runId}": {"get"},
                    "/v1/daily-ops-runs/{runId}/brief": {"get"},
                    "/v1/daily-ops-runs/{runId}/execute": {"post"},
                    "/v1/daily-ops-runs/{runId}/retry": {"post"},
                    "/v1/jobs": {"get", "post"},
                    "/v1/jobs/{jobId}": {"get"},
                    "/v1/schedules": {"get", "post"},
                    "/v1/schedules/{scheduleId}": {"patch"},
                    "/v1/approvals": {"get"},
                    "/v1/mission-control": {"get"},
                    "/v1/mission-control/events": {"get"},
                    "/v1/pilot-status": {"get"},
                    "/v1/assurance-runs": {"get", "post"},
                    "/v1/assurance-runs/{assuranceRunId}": {"get"},
                    "/v1/briefing": {"get"},
                    "/v1/catalog": {"get"},
                }
                for route, methods in required_operations.items():
                    route_contract = paths.get(route, {})
                    for method in methods:
                        if method not in route_contract:
                            problems.append(f"dist/openapi/runtime-api.yaml: missing {method.upper()} {route}")
                ontology = _json.loads((dist / "ontology.json").read_text(encoding="utf-8"))
                expected_platforms = {
                    item["id"] for item in ontology.get("platforms", []) if isinstance(item, dict)
                } | {"cross_platform"}
                actual_platforms = set(
                    contract.get("components", {})
                    .get("schemas", {})
                    .get("PlatformId", {})
                    .get("enum", [])
                )
                if actual_platforms != expected_platforms:
                    problems.append(
                        "dist/openapi/runtime-api.yaml: PlatformId enum does not match ontology"
                    )
                marketplace_platforms = set(
                    contract.get("components", {})
                    .get("schemas", {})
                    .get("MarketplaceId", {})
                    .get("enum", [])
                )
                if marketplace_platforms != expected_platforms - {"cross_platform"}:
                    problems.append(
                        "dist/openapi/runtime-api.yaml: MarketplaceId enum does not match ontology"
                    )
                import ast as _ast
                evidence_tree = _ast.parse(
                    (ROOT_V / "ecommerce_ai_skills" / "runtime" / "evidence.py").read_text(
                        encoding="utf-8"
                    )
                )
                runtime_report_types = set()
                for node in evidence_tree.body:
                    if not isinstance(node, _ast.AnnAssign):
                        continue
                    if not isinstance(node.target, _ast.Name) or node.target.id != "REPORT_SPECS":
                        continue
                    if isinstance(node.value, _ast.Dict):
                        runtime_report_types = {
                            key.value
                            for key in node.value.keys
                            if isinstance(key, _ast.Constant) and isinstance(key.value, str)
                        }
                report_types = set(
                    contract.get("components", {})
                    .get("schemas", {})
                    .get("EvidenceReportType", {})
                    .get("enum", [])
                )
                if not runtime_report_types or report_types != runtime_report_types:
                    problems.append(
                        "dist/openapi/runtime-api.yaml: EvidenceReportType enum does not match runtime"
                    )
                schemas = contract.get("components", {}).get("schemas", {})
                for schema_name in (
                    "AmazonSPAPIConnectorRegistration",
                    "AmazonAdsConnectorRegistration",
                    "AmazonAdsConnectorConfig",
                    "AmazonAdsProviderDetails",
                    "MarketplaceAccount",
                    "ConnectorUpdateRequest",
                    "ConnectorProviderCatalogEntry",
                    "AmazonMarketplaceCatalogEntry",
                    "DemoSession",
                    "AmazonReportImportActionRequest",
                    "Job",
                    "Schedule",
                    "MissionControl",
                    "MissionEvent",
                    "PilotStatus", "PilotTenantReadiness", "PilotTenantComponents",
                    "PilotBlocker", "PilotSchemaComponent", "PilotAmazonSpapiComponent",
                    "PilotCountComponent", "PilotOpenAIComponent", "PilotAdsComponent",
                    "PilotWorkerStatus", "PilotRuntimeStatus",
                    "AssuranceRunKind", "AssuranceRunRequest", "AssuranceCheck",
                    "AssuranceSummary", "AssuranceRun",
                    "OperatingBriefing",
                    "BriefingMetric",
                    "BriefingAgent",
                    "AgentEvaluation",
                    "RuntimeCatalog",
                    "ReportRecipe",
                    "ReportRecipeCreate",
                    "ReportRecipeUpdate",
                    "ReportRecipeKey",
                    "ReportRecipeAmazonReportType",
                    "ReportRecipeEvidenceReportType",
                    "ReportRecipeCatalogEntry",
                    "ReportSync",
                    "MetricObservation",
                    "MetricMaterialization",
                    "MetricBackfillRequest",
                    "AdsCapabilityGate",
                    "AdsCapabilityGateRequest",
                    "AdsAdapterStatus",
                    "AgentGraph", "AgentGraphBundle", "AgentGraphVersion",
                    "AgentGraphDefinition", "GraphNode", "GraphEdge",
                    "ToolPolicy", "ReviewerVerdict", "ReviewerIssue",
                    "DailyOpsEvidenceSelector", "DailyOpsScheduleCreate",
                    "DailyOpsScheduleUpdate", "DailyOpsSchedule",
                    "DailyOpsTriggerRequest", "DailyOpsSourceGap",
                    "DailyOpsScheduleSnapshot", "DailyOpsRun",
                    "DailyOpsBrief", "DailyOpsBriefEnvelope",
                    "ProposalOperation", "ProposalRisk", "ProposalStatus",
                    "ProposalDecisionType", "ProposalExecutionStatus",
                    "HumanReviewProposalPayload", "ShopifySyncProductsProposalPayload",
                    "AmazonSpapiImportReportProposalPayload",
                    "AmazonAdsCampaignUpdateProposalPayload", "ProposalPayload",
                    "ProposalCreateRequest", "HumanReviewProposalCreateRequest",
                    "ShopifySyncProductsProposalCreateRequest",
                    "AmazonSpapiImportReportProposalCreateRequest",
                    "AmazonAdsCampaignUpdateProposalCreateRequest",
                    "ProposalVersionRequest", "ProposalExecutionRequest",
                    "ProposalRevisionRequest", "ProposalDecisionRequest",
                    "ProposalDecision", "ProposalVersion", "Proposal",
                    "ProposalCapabilityBlock", "ProposalExecution",
                ):
                    if schema_name not in schemas:
                        problems.append(
                            f"dist/openapi/runtime-api.yaml: missing schema {schema_name}"
                        )
                proposal_create = schemas.get("ProposalCreateRequest", {})
                if len(proposal_create.get("oneOf", [])) != 4 or (
                    proposal_create.get("discriminator", {}).get("propertyName") != "operation"
                ):
                    problems.append(
                        "dist/openapi/runtime-api.yaml: Proposal create must discriminate four closed operation contracts"
                    )
                for schema_name in (
                    "HumanReviewProposalPayload", "ShopifySyncProductsProposalPayload",
                    "AmazonSpapiImportReportProposalPayload",
                    "AmazonAdsCampaignUpdateProposalPayload",
                ):
                    if schemas.get(schema_name, {}).get("additionalProperties") is not False:
                        problems.append(
                            f"dist/openapi/runtime-api.yaml: {schema_name} must be closed"
                        )
                human_payload = schemas.get("HumanReviewProposalPayload", {})
                if human_payload.get("required") != ["instructions"]:
                    problems.append(
                        "dist/openapi/runtime-api.yaml: human.review payload must require only instructions"
                    )
                proposal_schema = schemas.get("Proposal", {})
                if "versions" not in proposal_schema.get("required", []):
                    problems.append(
                        "dist/openapi/runtime-api.yaml: Proposal must include immutable versions history"
                    )
                proposal_version = schemas.get("ProposalVersion", {})
                if proposal_version.get("additionalProperties") is not False or "expires_at" not in proposal_version.get("required", []):
                    problems.append(
                        "dist/openapi/runtime-api.yaml: ProposalVersion must be closed and include expiry"
                    )
                block_codes = schemas.get("ProposalCapabilityBlock", {}).get("properties", {}).get("code", {}).get("enum", [])
                if set(block_codes) != {
                    "CONNECTOR_CAPABILITY_UNAVAILABLE", "AMAZON_ADS_CAPABILITY_UNAVAILABLE"
                }:
                    problems.append(
                        "dist/openapi/runtime-api.yaml: Proposal capability blocks must enumerate connector and Ads hard blocks"
                    )
                ads_paths = contract.get("paths", {})
                if not {"get", "post"} <= set(ads_paths.get("/v1/ads-capability-gates", {})):
                    problems.append("dist/openapi/runtime-api.yaml: missing Ads capability gate list/create contract")
                if "get" not in ads_paths.get("/v1/ads-capability-gates/{gateId}", {}):
                    problems.append("dist/openapi/runtime-api.yaml: missing Ads capability gate detail contract")
                adapter_path = ads_paths.get("/v1/ads-adapter-status", {})
                if "get" not in adapter_path:
                    problems.append("dist/openapi/runtime-api.yaml: missing conditional Ads adapter status contract")
                adapter_schema = schemas.get("AdsAdapterStatus", {})
                if adapter_schema.get("properties", {}).get("adapter_registered", {}).get("enum") != [False]:
                    problems.append("dist/openapi/runtime-api.yaml: Ads adapter status must prove adapter_registered=false")
                if adapter_schema.get("properties", {}).get("write_operations", {}).get("maxItems") != 0:
                    problems.append("dist/openapi/runtime-api.yaml: Ads adapter status write_operations must be empty")
                connector_providers = set(
                    schemas.get("ConnectorProvider", {}).get("enum", [])
                )
                if connector_providers != {"amazon_ads", "amazon_spapi", "shopify"}:
                    problems.append(
                        "dist/openapi/runtime-api.yaml: ConnectorProvider enum does not match runtime"
                    )
                expected_recipe_keys = {
                    "sales_traffic_daily",
                    "fba_inventory_daily",
                    "listings_daily",
                    "returns_daily",
                }
                actual_recipe_keys = set(
                    schemas.get("ReportRecipeKey", {}).get("enum", [])
                )
                if actual_recipe_keys != expected_recipe_keys:
                    problems.append(
                        "dist/openapi/runtime-api.yaml: ReportRecipeKey enum does not match L2 allowlist"
                    )
                catalog_required = set(
                    schemas.get("RuntimeCatalog", {}).get("required", [])
                )
                if "report_recipe_types" not in catalog_required:
                    problems.append(
                        "dist/openapi/runtime-api.yaml: RuntimeCatalog missing report_recipe_types"
                    )
                if "metric_materialization_report_types" not in catalog_required:
                    problems.append(
                        "dist/openapi/runtime-api.yaml: RuntimeCatalog missing metric_materialization_report_types"
                    )
                metric_materialize = paths.get(
                    "/v1/evidence-imports/{importId}/metric-materialization", {}
                ).get("post", {})
                if not any(
                    parameter.get("name") == "Idempotency-Key"
                    and parameter.get("required") is True
                    for parameter in metric_materialize.get("parameters", [])
                    if isinstance(parameter, dict)
                ):
                    problems.append(
                        "dist/openapi/runtime-api.yaml: L4 materialization must require Idempotency-Key"
                    )
                observation = schemas.get("MetricObservation", {})
                observation_required = set(observation.get("required", []))
                required_observation_fields = {
                    "tenant_id",
                    "materialization_id",
                    "evidence_import_id",
                    "value_decimal",
                    "currency",
                    "period_start",
                    "period_end",
                    "time_grain",
                    "provenance",
                    "quality",
                }
                if not required_observation_fields <= observation_required:
                    problems.append(
                        "dist/openapi/runtime-api.yaml: MetricObservation missing L4 lineage/currency fields"
                    )
                decimal_value = observation.get("properties", {}).get("value_decimal", {})
                if decimal_value.get("type") != "string" or "pattern" not in decimal_value:
                    problems.append(
                        "dist/openapi/runtime-api.yaml: MetricObservation value must be a bounded Decimal string"
                    )
                backfill = schemas.get("MetricBackfillRequest", {}).get("properties", {}).get(
                    "limit", {}
                )
                if backfill.get("minimum") != 1 or backfill.get("maximum") != 100:
                    problems.append(
                        "dist/openapi/runtime-api.yaml: MetricBackfillRequest limit must be 1..100"
                    )
                tool_policy = schemas.get("ToolPolicy", {})
                if tool_policy.get("properties", {}).get("max_tool_calls", {}).get("maximum") != 0:
                    problems.append("dist/openapi/runtime-api.yaml: L7 tool policy must cap model tools at zero")
                if tool_policy.get("properties", {}).get("allowed_tools", {}).get("maxItems") != 0:
                    problems.append("dist/openapi/runtime-api.yaml: L7 allowed_tools must be empty")
                graph_definition = schemas.get("AgentGraphDefinition", {}).get("properties", {})
                if (
                    graph_definition.get("nodes", {}).get("minItems") != 5
                    or graph_definition.get("nodes", {}).get("maxItems") != 5
                    or graph_definition.get("edges", {}).get("minItems") != 6
                    or graph_definition.get("edges", {}).get("maxItems") != 6
                ):
                    problems.append(
                        "dist/openapi/runtime-api.yaml: L7 graph must expose the canonical 5-node/6-edge topology"
                    )
                daily_brief = schemas.get("DailyOpsBrief", {})
                daily_gap = schemas.get("DailyOpsSourceGap", {})
                if daily_brief.get("additionalProperties") is not False:
                    problems.append(
                        "dist/openapi/runtime-api.yaml: L8 DailyOpsBrief must be a closed schema"
                    )
                if daily_gap.get("additionalProperties") is not False:
                    problems.append(
                        "dist/openapi/runtime-api.yaml: L8 source gaps must be a closed schema"
                    )
                sse_operation = paths.get("/v1/mission-control/events", {}).get("get", {})
                sse_content = sse_operation.get("responses", {}).get("200", {}).get("content", {})
                if "text/event-stream" not in sse_content:
                    problems.append("dist/openapi/runtime-api.yaml: L10 SSE must return text/event-stream")
                sse_parameters = {
                    item.get("$ref", "").split("/")[-1]
                    for item in sse_operation.get("parameters", []) if isinstance(item, dict)
                }
                if sse_parameters != {"lastEventId", "missionEventsAfter"}:
                    problems.append("dist/openapi/runtime-api.yaml: L10 SSE must define header-first resume cursors")
                event = schemas.get("MissionEvent", {})
                if event.get("additionalProperties") is not False or event.get("required") != [
                    "cursor", "event_type", "resource_type", "resource_id", "status",
                    "previous_status", "metadata", "created_at",
                ]:
                    problems.append("dist/openapi/runtime-api.yaml: L10 MissionEvent must be a closed safe metadata schema")
                if event.get("properties", {}).get("metadata", {}).get("additionalProperties") is not False:
                    problems.append("dist/openapi/runtime-api.yaml: L10 MissionEvent metadata must be closed")
                reset = schemas.get("MissionReset", {})
                reconnect = schemas.get("MissionReconnect", {})
                if reset.get("additionalProperties") is not False or reconnect.get("additionalProperties") is not False:
                    problems.append("dist/openapi/runtime-api.yaml: L10 reset/reconnect controls must be closed")
                cursor_parameters = contract.get("components", {}).get("parameters", {})
                if any(cursor_parameters.get(name, {}).get("schema", {}).get("type") != "integer" for name in ("lastEventId", "missionEventsAfter")):
                    problems.append("dist/openapi/runtime-api.yaml: L10 cursors must be tenant-local integers")
                if not {"401", "403", "422", "429"} <= set(sse_operation.get("responses", {})):
                    problems.append("dist/openapi/runtime-api.yaml: L10 SSE missing required auth/validation/limit responses")
                if schemas.get("MissionControl", {}).get("additionalProperties") is not True:
                    problems.append("dist/openapi/runtime-api.yaml: Mission Control snapshot must remain extension-compatible")
                if "event_cursor" not in schemas.get("MissionControl", {}).get("required", []) or schemas.get("MissionEventCursor", {}).get("additionalProperties") is not False:
                    problems.append("dist/openapi/runtime-api.yaml: L10 snapshot must expose a closed tenant cursor")
                pilot_operation = paths.get("/v1/pilot-status", {}).get("get", {})
                pilot_response = pilot_operation.get("responses", {}).get("200", {}).get("content", {}).get("application/json", {}).get("schema", {})
                if not pilot_response.get("$ref", "").endswith("/PilotStatus"):
                    problems.append("dist/openapi/runtime-api.yaml: L11 pilot status must return PilotStatus")
                if not {"401", "403"} <= set(pilot_operation.get("responses", {})):
                    problems.append("dist/openapi/runtime-api.yaml: L11 pilot status missing viewer auth responses")
                for schema_name in (
                    "PilotStatus", "PilotTenantReadiness", "PilotTenantComponents", "PilotBlocker",
                    "PilotSchemaComponent", "PilotAmazonSpapiComponent", "PilotCountComponent",
                    "PilotOpenAIComponent", "PilotAdsComponent", "PilotWorkerStatus", "PilotRuntimeStatus",
                ):
                    if schemas.get(schema_name, {}).get("additionalProperties") is not False:
                        problems.append(f"dist/openapi/runtime-api.yaml: L11 {schema_name} must be closed")
                pilot_worker = schemas.get("PilotWorkerStatus", {}).get("properties", {})
                if pilot_worker.get("name", {}).get("enum") != [
                    "scheduler", "job_worker", "report_worker", "daily_scheduler", "daily_worker", "proposal_worker",
                ] or pilot_worker.get("status", {}).get("enum") != [
                    "starting", "healthy", "stale", "degraded", "stopped",
                ]:
                    problems.append("dist/openapi/runtime-api.yaml: L11 worker heartbeat statuses must match the runtime")
                pilot_status = schemas.get("PilotStatus", {})
                if pilot_status.get("required") != ["status", "blockers", "warnings", "runtime", "tenant"] or pilot_status.get("properties", {}).get("status", {}).get("enum") != ["ready", "attention", "blocked"]:
                    problems.append("dist/openapi/runtime-api.yaml: L11 pilot status must distinguish ready/attention/blocked")
                pilot_amazon = schemas.get("PilotAmazonSpapiComponent", {})
                if pilot_amazon.get("required") != [
                    "required", "status", "account_count", "healthy_count", "fresh_healthy_count",
                    "credential_ready_count", "health_max_age_seconds",
                ] or pilot_amazon.get("properties", {}).get("status", {}).get("enum") != [
                    "missing", "unhealthy", "stale", "missing_credentials", "ready",
                ]:
                    problems.append("dist/openapi/runtime-api.yaml: L11 Amazon readiness must expose freshness and credential counts")
                pilot_runtime = schemas.get("PilotRuntimeStatus", {}).get("properties", {})
                if pilot_runtime.get("status", {}).get("enum") != [
                    "starting", "healthy", "stale", "degraded", "stopping", "stopped", "superseded",
                ] or pilot_runtime.get("stop_reason", {}).get("enum") != [
                    "graceful_shutdown", "startup_failure", "worker_shutdown_timeout",
                ]:
                    problems.append("dist/openapi/runtime-api.yaml: L11 runtime shutdown states must match the supervisor")
                assurance_list = paths.get("/v1/assurance-runs", {})
                assurance_detail = paths.get("/v1/assurance-runs/{assuranceRunId}", {})
                if not {"get", "post"} <= set(assurance_list) or "get" not in assurance_detail:
                    problems.append("dist/openapi/runtime-api.yaml: L12 assurance list/detail operations are missing")
                assurance_post = assurance_list.get("post", {})
                if not {"401", "403", "409", "422"} <= set(assurance_post.get("responses", {})):
                    problems.append("dist/openapi/runtime-api.yaml: L12 assurance post must retain auth/idempotency failures")
                audit = schemas.get("AuditEvent", {})
                if audit.get("additionalProperties") is not False or not {"previous_hash", "event_hash"} <= set(audit.get("required", [])):
                    problems.append("dist/openapi/runtime-api.yaml: L12 audit events must expose hash-chain links")
                for schema_name in ("AssuranceRunRequest", "AssuranceCheck", "AssuranceSummary", "AssuranceRun"):
                    if schemas.get(schema_name, {}).get("additionalProperties") is not False:
                        problems.append(f"dist/openapi/runtime-api.yaml: L12 {schema_name} must be closed")
                request_kind = schemas.get("AssuranceRunRequest", {}).get("properties", {}).get("kind", {}).get("enum")
                if request_kind != ["eval", "security"]:
                    problems.append("dist/openapi/runtime-api.yaml: L12 restore assurance must remain CLI-only")
                assurance_status = schemas.get("AssuranceCheck", {}).get("properties", {}).get("status", {}).get("enum")
                if assurance_status != ["passed", "failed", "blocked"]:
                    problems.append("dist/openapi/runtime-api.yaml: L12 assurance checks must include blocked")
                assurance_run = schemas.get("AssuranceRun", {})
                if not {"lease_until", "attempt_count"} <= set(assurance_run.get("required", [])) or assurance_run.get("properties", {}).get("attempt_count", {}).get("minimum") != 1:
                    problems.append("dist/openapi/runtime-api.yaml: L12 assurance runs must expose lease-resume attempts")
                pilot_openai = schemas.get("PilotOpenAIComponent", {}).get("properties", {})
                if set(pilot_openai) != {"required", "status", "api_key_present", "model_present"}:
                    problems.append("dist/openapi/runtime-api.yaml: L11 OpenAI status may expose presence only")
            except Exception as exc:
                problems.append(f"dist/openapi/runtime-api.yaml: invalid YAML ({exc})")
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
            quickstart = text.split("## Quick Start", 1)[-1].split("## What's Inside", 1)[0]
            skill_ids = sorted(p.name for p in (dist / "skills").iterdir() if p.is_dir()) if (dist / "skills").is_dir() else []
            for skill_id in skill_ids:
                if skill_id not in quickstart:
                    problems.append(f"dist/README.md: Quick Start omits skill {skill_id}")

            root_skill = dist / "SKILL.md"
            if root_skill.exists():
                skill_text = root_skill.read_text(encoding="utf-8")
                capability_section = skill_text.split("## Your Capabilities", 1)[-1].split("2. **Domain Ontology**", 1)[0]
                for skill_id in skill_ids:
                    if skill_id not in capability_section:
                        problems.append(f"dist/SKILL.md: capability list omits skill {skill_id}")
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
            patterns = triggers.get("patterns", []) if isinstance(triggers, dict) else []
            manifests[sid] = {"keywords": keywords, "patterns": patterns}

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
            qn = _normalize(case.get("query", ""))
            kws = manifests.get(expected, {}).get("keywords", [])
            if any(_normalize(k) in qn for k in kws if len(k) >= 3):
                lit_count += 1
        lit_ratio = lit_count / len(cases) if cases else 0
        # Threshold is 50% (see CONTRIBUTING.md § R1 hard rules). It was raised to
        # 95% in 11709a3 with "was too strict"; that is the fourth time this gate
        # was weakened to go green, and 95% permits a 94%-tautological suite. The
        # fix for a high ratio is more non-literal cases, never a higher threshold.
        if lit_ratio > 0.50:
            print(f"  [FAIL] R1          TEST DEGENERATION ({lit_count}/{len(cases)} = {lit_ratio:.0%} literal > 50%)")
            return 1

        errors = []
        for i, case in enumerate(cases):
            query = case.get("query", "")
            expected = case.get("expect", "")
            if not query or not expected:
                continue
            qn = _normalize(query)
            app_rule = manifests.get("ecom-applicability", {})
            app_kws = app_rule.get("keywords", [])
            app_score = sum(1 for kw in app_kws if len(kw) >= 3 and _normalize(kw) in qn)
            app_score += 2 * sum(
                1 for pattern in app_rule.get("patterns", [])
                if re.search(pattern, qn, re.IGNORECASE)
            )
            # Applicability only wins if it has >=2 keyword hits AND no domain
            # skill has >=2 hits. A single "朋友说" shouldn't override "包装不好看"+"重新设计".
            best_match = None
            best_score = 0
            for sid, rule in manifests.items():
                if sid == "ecom-applicability":
                    continue
                keywords = rule.get("keywords", [])
                score = sum(1 for kw in keywords if _normalize(kw) in qn)
                score += 2 * sum(
                    1 for pattern in rule.get("patterns", [])
                    if re.search(pattern, qn, re.IGNORECASE)
                )
                if score > best_score:
                    best_score = score
                    best_match = sid
            # "Should I use AI for X" is a meta-question about whether AI fits,
            # not a request to do X. When applicability ties or leads a domain
            # skill, it wins: 「能用 AI 做补货预测吗」 hits inventory (补货, 预测) and
            # applicability (AI做, 用AI做) 2-2, but the user is asking whether to
            # use AI at all, so it belongs to applicability. (Live-run S5.)
            if app_score >= 2 and app_score >= best_score:
                best_match = "ecom-applicability"
            if best_match != expected:
                errors.append(f"case {i+1}: '{query[:40]}...' routed to {best_match} (expected {expected})")

        total = len(errors)
        blocking = total > R1_MAX_MISROUTES
        mark = "FAIL" if blocking else "ok "
        print(
            f"  [{mark}] R1          {total}/{len(cases)} misroutes "
            f"(budget <= {R1_MAX_MISROUTES})"
        )
        for e in errors:
            print(f"           {e}")
        return 1 if blocking else 0

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
        for gid, fn in [("E1", gate_e1), ("E2", gate_e2), ("E3", gate_e3)]:
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
        result = subprocess.run(_interp(cmd), capture_output=True, text=True, timeout=120)
        if label == "Dist" and result.returncode == 0:
            release_result = subprocess.run(
                _interp(["python3", "scripts/build_release_manifest.py", "--check"]),
                capture_output=True,
                text=True,
                timeout=120,
            )
            if release_result.returncode != 0:
                result = release_result
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
