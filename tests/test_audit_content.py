"""Content audit.

This is a report, not a gate — it is *supposed* to return findings, so the tests
cannot assert "zero". What they pin is that the detection is honest: that it does
not clear a chapter on evidence quoted inside a prompt template, that it never
fails a build, and that each axis measures what its name says.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_module():
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "audit_content", ROOT / "scripts" / "audit_content.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "scripts/audit_content.py", *args],
        cwd=ROOT, text=True, capture_output=True, check=False,
    )


def test_audit_never_gates_a_build() -> None:
    """Findings are judgment calls. A build must not go red because of them."""
    for args in ([], ["--axis", "V"], ["--list"], ["--json"]):
        assert run(*args).returncode == 0, args


def test_json_shape_is_stable() -> None:
    data = json.loads(run("--json").stdout)
    assert {"V1", "V2", "V3", "C1", "C2", "C3", "F1", "F2", "F3"} <= set(data)
    for aid, entry in data.items():
        assert entry["count"] == len(entry["items"]), aid
        assert entry["label"]


def test_citation_check_ignores_prompt_templates() -> None:
    """The trap this audit was written around.

    Every prompt template in the corpus contains the words "标注来源" inside its
    data-discipline block. A naive keyword scan clears a chapter that cites
    nothing at all — which is how 56 unsourced figures sat behind a green gate.
    """
    module = load_module()
    fenced = "# T\n\n```\n每个结论标注来源：[我提供的信息]\n```\n\n| GMV | $830B |\n"
    assert not module.CITATION.search(module.outside_fences(fenced))

    real = "# T\n\n见 [来源](https://example.com/report)\n\n| GMV | $830B |\n"
    assert module.CITATION.search(module.outside_fences(real))


def test_world_figures_are_distinguished_from_platform_specs() -> None:
    """Spec values are constraints, not claims; demanding citations for them is noise."""
    module = load_module()
    for claim in ("| GMV | $830B |", "| MAU | 2.46 亿 |",
                  "| 市场份额 | 24% |", "| 效率 | 省时 70% |"):
        assert module.WORLD_FIGURE.search(claim), claim
    for spec in ("| 标题 | 200 字符 |", "| 图片 | 1000x1500px |",
                 "| 比例 | 2:3 |", "| Bullet | 5 条 |"):
        assert not module.WORLD_FIGURE.search(spec), spec


def test_outside_fences_strips_every_block() -> None:
    module = load_module()
    text = "keep1\n```\ndrop\n```\nkeep2\n~~~\ndrop2\n~~~\nkeep3"
    result = module.outside_fences(text)
    assert "drop" not in result
    assert all(k in result for k in ("keep1", "keep2", "keep3"))


def test_navigation_check_sees_the_nav_section() -> None:
    """The nav block is itself an H2, so slicing at the first '## ' hides it.

    That bug reported 59 of 69 chapters as navigation-less.
    """
    module = load_module()
    findings = module.f2_missing_navigation()
    assert len(findings) < 10, f"detector looks broken again: {len(findings)} findings"


def test_link_findings_are_grouped_by_required_action() -> None:
    module = load_module()
    joined = "\n".join(module.v3_link_probe_staleness())
    for action in ("moved", "bot-walled", "broken"):
        assert action in joined


def test_only_and_axis_filters_narrow_the_run() -> None:
    assert set(json.loads(run("--only", "V1", "--json").stdout)) == {"V1"}
    assert all(k.startswith("C") for k in json.loads(run("--axis", "C", "--json").stdout))
