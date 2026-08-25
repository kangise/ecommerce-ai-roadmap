from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args, cwd=ROOT, text=True, capture_output=True, check=False
    )


def test_routing_has_no_known_misroutes() -> None:
    result = run(sys.executable, "scripts/verify_all.py", "--r1")
    assert result.returncode == 0, result.stdout + result.stderr
    assert "0/117" in result.stdout


def test_all_notebooks_are_valid_json() -> None:
    notebooks = sorted((ROOT / "notebooks").glob("*.ipynb"))
    assert len(notebooks) == 18
    for notebook in notebooks:
        data = json.loads(notebook.read_text(encoding="utf-8"))
        assert data.get("nbformat") == 4, notebook
        assert isinstance(data.get("cells"), list) and data["cells"], notebook


def test_notebooks_do_not_generate_runtime_mock_data() -> None:
    forbidden = ("np.random", "random.", "模拟数据", "示例数据", "sample data")
    for notebook in sorted((ROOT / "notebooks").glob("*.ipynb")):
        text = notebook.read_text(encoding="utf-8").lower()
        hits = [term for term in forbidden if term.lower() in text]
        assert hits == [], f"{notebook.name} contains runtime mock-data paths: {hits}"


@pytest.mark.parametrize(
    ("name", "fixture_name", "fixture_data"),
    [
        (
            "a1-product-research.ipynb",
            "reviews.csv",
            "rating,text\n5,Durable and compact\n2,Battery failed early\n",
        ),
        (
            "a3-advertising.ipynb",
            "amazon-search-terms.csv",
            "Search Term,Impressions,Clicks,Spend,Orders,Sales\n"
            "portable fan,1000,20,25,4,120\n"
            "desk fan,800,15,30,0,0\n",
        ),
    ],
)
def test_core_notebooks_execute_with_explicit_inputs(
    tmp_path: Path,
    name: str,
    fixture_name: str,
    fixture_data: str,
) -> None:
    (tmp_path / fixture_name).write_text(fixture_data, encoding="utf-8")
    notebook = json.loads((ROOT / "notebooks" / name).read_text(encoding="utf-8"))
    namespace: dict[str, object] = {}
    previous_cwd = Path.cwd()
    try:
        os.chdir(tmp_path)
        for cell in notebook["cells"]:
            if cell.get("cell_type") != "code":
                continue
            source = "".join(cell.get("source", []))
            assert not any(
                line.lstrip().startswith(("!", "%")) for line in source.splitlines()
            ), f"{name} contains a shell or notebook magic command"
            exec(compile(source, name, "exec"), namespace)
    finally:
        os.chdir(previous_cwd)


def test_python_sources_compile() -> None:
    files = [
        *sorted((ROOT / "scripts").rglob("*.py")),
        *sorted((ROOT / "integration").rglob("*.py")),
        *sorted((ROOT / "ecommerce_ai_skills").rglob("*.py")),
        *sorted((ROOT / "examples").rglob("*.py")),
        *sorted((ROOT / "tools").rglob("*.py")),
    ]
    for path in files:
        compile(path.read_text(encoding="utf-8"), str(path), "exec")
