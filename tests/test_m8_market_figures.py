"""M8 — market-scale figures in tables must carry a source.

The gate exists because M1 skips any line starting with "|", so twelve
marketplaces' GMV shipped behind a green build. Its value is entirely in
precision: a gate that also fires on formula rows and worked examples teaches
people to allowlist reflexively, and then it protects nothing. These tests pin
both edges — what it must catch, and what it must leave alone.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ALLOWLIST = ROOT / "scripts" / "content-allowlist.txt"


def load_module():
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "verify_content", ROOT / "scripts" / "verify_content.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def flags(module, row: str) -> bool:
    """Would M8 fire on this table row, ignoring citations and the allowlist?"""
    return bool(module.WORLD_FIGURE.search(row)) and not module.NOT_A_WORLD_CLAIM.search(row)


def test_gate_is_registered_and_currently_clean() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/verify_content.py", "--only", "M8"],
        cwd=ROOT, text=True, capture_output=True, check=False)
    assert result.returncode == 0, result.stdout
    assert "M8" in result.stdout


def test_catches_market_scale_figures() -> None:
    module = load_module()
    for row in (
        "| **Amazon** | GMV $830B | 稳定 | 全球 |",
        "| **Zalando** | GMV €17.6B | 5-10% | 欧洲 |",
        "| MAU | 2.46 亿 | 全球电商 App 第三 |",
        "| 活跃用户 | 5200 万 | 增长 |",
        "| 卖家数量 | ~5,000+（精选） | 数十万 |",
        "| 集团收入 | €12.3B | +16.8% |",
    ):
        assert flags(module, row), row


def test_leaves_platform_specs_alone() -> None:
    """Specs are constraints, not claims about the world."""
    module = load_module()
    for row in (
        "| 标题 | 不超过 200 字符 |",
        "| 图片 | 1000x1500px（2:3 竖版） |",
        "| Bullet | 5 条，每条 ≤200 字符 |",
        "| 描述 | 2200 字符 |",
    ):
        assert not flags(module, row), row


def test_leaves_formulas_and_examples_alone() -> None:
    """The false positives that made the first draft unusable at 94 findings."""
    module = load_module()
    for row in (
        "| **ROAS** | 广告销售额 ÷ 广告花费 | $400 ÷ $100 = 4.0 | > 3.0（盈利） |",
        "| **ACOS** | 广告花费 ÷ 广告销售额 × 100% | $100 ÷ $400 = 25% |",
        "| 利润 | 毛利率 | (收入-COGS)/收入 | 50-70% | <40% |",
        "| 销售数据 | 用百分比代替绝对值 | “产品 A 销量增长 30%” 而非 “月销 5000 件” |",
        "| 成功标准 | 1 个场景效率提升 50%+ | 80%+ 的人每天用 AI |",
    ):
        assert not flags(module, row), row


def test_a_citation_in_the_row_clears_it(tmp_path, monkeypatch) -> None:
    module = load_module()
    doc = tmp_path / "src" / "x.md"
    doc.parent.mkdir(parents=True)
    doc.write_text("# t\n\n| **NewMart** | GMV $42B | [来源](https://example.com/ir) |\n",
                   encoding="utf-8")
    monkeypatch.setattr(module, "ROOT", tmp_path)
    monkeypatch.setattr(module, "ALLOWLIST", tmp_path / "nope.txt")
    assert module.gate_m8() == []


def test_the_same_row_without_a_citation_is_caught(tmp_path, monkeypatch) -> None:
    module = load_module()
    doc = tmp_path / "src" / "x.md"
    doc.parent.mkdir(parents=True)
    doc.write_text("# t\n\n| **NewMart** | GMV $42B | 20% | 全球 |\n", encoding="utf-8")
    monkeypatch.setattr(module, "ROOT", tmp_path)
    monkeypatch.setattr(module, "ALLOWLIST", tmp_path / "nope.txt")
    assert len(module.gate_m8()) == 1


def test_allowlist_entries_point_at_real_lines() -> None:
    """A stale entry silently re-opens the hole it was covering."""
    for raw in ALLOWLIST.read_text(encoding="utf-8").split("\n"):
        entry = raw.split("#")[0].strip()
        if not entry:
            continue
        rel, _, lineno = entry.rpartition(":")
        path = ROOT / "src" / rel
        assert path.exists(), entry
        assert int(lineno) <= path.read_text(encoding="utf-8").count("\n") + 1, entry


def test_allowlist_states_that_it_is_debt() -> None:
    """Framing matters: the next person must not read this as a place to file things."""
    header = ALLOWLIST.read_text(encoding="utf-8")[:900]
    assert "debt register" in header
    assert "not an exemption list" in header
