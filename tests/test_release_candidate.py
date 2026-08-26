from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

import yaml
import pytest

from ecommerce_ai_skills import USER_AGENT, __version__
from ecommerce_ai_skills.runtime.api import _Handler
from ecommerce_ai_skills.runtime.storage import SCHEMA_VERSION

ROOT = Path(__file__).resolve().parents[1]
VERSION = "1.3.0"


def run(*args: str, cwd: Path = ROOT, env: dict[str, str] | None = None):
    return subprocess.run(args, cwd=cwd, env=env, text=True, capture_output=True, check=False)


def test_release_version_contract_is_uniform() -> None:
    try:
        import tomllib
    except ModuleNotFoundError:
        import tomli as tomllib

    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    contract = yaml.safe_load((ROOT / "openapi" / "runtime-api.yaml").read_text(encoding="utf-8"))
    assert project["project"]["version"] == VERSION
    assert contract["info"]["version"] == VERSION
    assert __version__ == VERSION
    assert USER_AGENT == f"ecommerce-ai-skills/{VERSION}"
    assert _Handler.server_version == f"EcommerceAI/{VERSION}"
    assert SCHEMA_VERSION == 21
    candidates = [ROOT / "pyproject.toml", *list((ROOT / "openapi").rglob("*"))]
    candidates += [
        path for path in (ROOT / "ecommerce_ai_skills").rglob("*")
        if "package_data" not in path.parts
    ]
    stale = []
    pattern = re.compile(r"1\.2\.0|ecommerce-ai-skills/1\.[0-2]|EcommerceAI/1\.[0-2]")
    for path in candidates:
        if path.is_file():
            try:
                if pattern.search(path.read_text(encoding="utf-8")):
                    stale.append(path)
            except UnicodeDecodeError:
                pass
    assert stale == []


def test_release_manifest_is_deterministic_fresh_and_tamper_evident(tmp_path: Path) -> None:
    committed = ROOT / "release" / f"v{VERSION}-rc-manifest.json"
    checked = run(sys.executable, "scripts/build_release_manifest.py", "--check")
    assert checked.returncode == 0, checked.stderr
    first, second = tmp_path / "first.json", tmp_path / "second.json"
    for output in (first, second):
        built = run(sys.executable, "scripts/build_release_manifest.py", "--output", str(output))
        assert built.returncode == 0, built.stderr
    assert first.read_bytes() == second.read_bytes() == committed.read_bytes()
    manifest = json.loads(first.read_text(encoding="utf-8"))
    assert manifest["release"] == {
        "channel": "rc",
        "python_requires": ">=3.10",
        "runtime_schema_version": 21,
        "tag": "v1.3.0",
        "version": VERSION,
    }
    assert set(manifest["version_contract"].values()) == {VERSION}
    try:
        import tomllib
    except ModuleNotFoundError:
        import tomli as tomllib
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    readme = project["readme"]
    readme_path = readme if isinstance(readme, str) else readme["file"]
    assert {
        ".gitignore", readme_path, "LICENSE", "design-qa.md",
        "roadmap/ui-design-system-l7.md",
    }.issubset(manifest["contracts"])
    assert manifest["artifacts"]["dist"]["file_count"] == 153
    assert manifest["artifacts"]["design_evidence"]["file_count"] >= 10
    first.write_text(first.read_text(encoding="utf-8") + " ", encoding="utf-8")
    stale = run(sys.executable, "scripts/build_release_manifest.py", "--check", "--output", str(first))
    assert stale.returncode == 1 and "stale" in stale.stderr


def test_cli_version_and_supported_python_wheel_metadata(tmp_path: Path) -> None:
    cli = run(sys.executable, "-m", "ecommerce_ai_skills.cli", "--version")
    assert cli.returncode == 0 and cli.stdout.strip() == f"opc-ecommerce {VERSION}"
    if sys.version_info < (3, 10):
        pytest.skip("wheel metadata smoke requires the project's supported Python >=3.10")
    wheelhouse = tmp_path / "wheelhouse"
    wheelhouse.mkdir()
    built = run(
        sys.executable, "-m", "pip", "wheel", "--no-deps",
        "--wheel-dir", str(wheelhouse), ".",
    )
    assert built.returncode == 0, built.stderr
    wheel = next(wheelhouse.glob("ecommerce_ai_skills-*.whl"))
    assert VERSION in wheel.name
    venv = tmp_path / "venv"
    assert run(sys.executable, "-m", "venv", str(venv)).returncode == 0
    python = venv / "bin" / "python"
    pip = venv / "bin" / "pip"
    installed = run(str(pip), "install", "--no-deps", "--no-index", str(wheel), cwd=tmp_path)
    assert installed.returncode == 0, installed.stderr
    environment = dict(os.environ)
    environment.pop("PYTHONPATH", None)
    smoke = run(
        str(python), "-c",
        "from importlib.metadata import version; from ecommerce_ai_skills import __version__; "
        "assert version('ecommerce-ai-skills') == __version__ == '1.3.0'",
        cwd=tmp_path,
        env=environment,
    )
    assert smoke.returncode == 0, smoke.stderr


def test_release_workflow_enforces_rc_and_cold_install() -> None:
    workflow = (ROOT / ".github" / "workflows" / "release.yml").read_text(encoding="utf-8")
    for required in (
        "scripts/build_release_manifest.py --check",
        "does not match pyproject version",
        "python3 -m pip wheel",
        "--no-index --find-links",
        "Cold-wheel RC smoke outside checkout",
        "demo-seed",
        '--db "$RC_DIR/restored.sqlite"',
        'RuntimeApplication(Database(root / "restored.sqlite"))',
        "verify_audit_chain(principal.tenant_id)",
        '("restore", "passed")',
        'restored.sqlite.evidence_objects',
        "release/v1.3.0-rc-manifest.json",
        "release/v1.3.0-rc.md",
        "cp release/v1.3.0-rc-manifest.json v1.3.0-rc-manifest.json",
        "cp release/v1.3.0-rc.md v1.3.0-rc.md",
        "sha256sum",
        "sha256sum -c SHA256SUMS",
        "SHA256SUMS",
        "gh release create \"$GITHUB_REF_NAME\" --draft",
        "gh release upload \"$GITHUB_REF_NAME\"",
        "gh release download \"$GITHUB_REF_NAME\"",
        "--draft=false",
    ):
        assert required in workflow
    assert workflow.count('"$RC_DIR/venv/bin/opc-ecommerce" restore --backup') == 2
    assert workflow.index("--draft") < workflow.index("gh release upload")
    assert workflow.index("gh release upload") < workflow.index("gh release download")
    assert workflow.index("gh release download") < workflow.index("--draft=false")
    checksum_inputs = workflow.split("sha256sum \\\n", 1)[1].split("> SHA256SUMS", 1)[0]
    assert "release/" not in checksum_inputs
    assert "v1.3.0-rc-manifest.json" in checksum_inputs
    assert "v1.3.0-rc.md" in checksum_inputs
    assert "pip install --no-deps --no-index --target" not in workflow


def test_rc_human_contracts_are_closed() -> None:
    progress = (ROOT / "scripts" / "loop" / "v1_3_progress.md").read_text(encoding="utf-8")
    roadmap = (ROOT / "roadmap" / "v1.3-amazon-operator-pilot.md").read_text(encoding="utf-8")
    assert re.search(r"\|\s*L13\s*\|\s*RC\s*\|\s*done\s*\|", progress)
    assert "L0–L13 实现已验证" in roadmap
    assert "L13 Release Candidate 待开始" not in roadmap
