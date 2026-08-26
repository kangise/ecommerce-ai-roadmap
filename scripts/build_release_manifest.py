#!/usr/bin/env python3
"""Build or verify the deterministic v1.3 release-candidate manifest."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

ROOT = Path(__file__).resolve().parents[1]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tree_contract(name: str, paths: list[Path]) -> dict[str, object]:
    digest = hashlib.sha256()
    files = []
    for path in sorted({item.resolve() for item in paths}):
        if not path.is_file() or path.name in {".DS_Store"} or "__pycache__" in path.parts:
            continue
        relative = path.relative_to(ROOT.resolve()).as_posix()
        item_hash = sha256(path)
        size = path.stat().st_size
        digest.update(f"{relative}\0{item_hash}\0{size}\n".encode())
        files.append((relative, size))
    return {
        "name": name,
        "file_count": len(files),
        "byte_count": sum(size for _, size in files),
        "tree_sha256": digest.hexdigest(),
    }


def project_version() -> str:
    return tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]["version"]


def build_metadata_contracts(project: dict[str, object]) -> list[str]:
    """Resolve file-backed wheel metadata declared by pyproject plus license defaults."""
    declared: list[str] = []
    for field in ("readme", "license"):
        value = project.get(field)
        candidate = value if isinstance(value, str) else (
            value.get("file") if isinstance(value, dict) else None
        )
        if candidate:
            declared.append(str(candidate))
    # setuptools includes conventional license files in built metadata even when
    # PEP 621 uses an inline license expression/text.
    for candidate in ("LICENSE", "LICENSE.txt", "COPYING", "COPYING.txt"):
        if (ROOT / candidate).is_file():
            declared.append(candidate)
    resolved: list[str] = []
    for value in declared:
        path = (ROOT / value).resolve()
        try:
            relative = path.relative_to(ROOT.resolve()).as_posix()
        except ValueError as exc:
            raise SystemExit(f"build metadata path leaves repository: {value}") from exc
        if not path.is_file():
            raise SystemExit(f"build metadata file is missing: {relative}")
        if relative not in resolved:
            resolved.append(relative)
    return resolved


def build_manifest() -> dict[str, object]:
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    version = str(project["version"])
    package_source = (ROOT / "ecommerce_ai_skills" / "__init__.py").read_text(encoding="utf-8")
    package_match = re.search(r'^__version__\s*=\s*"([^"]+)"', package_source, re.M)
    openapi_source = (ROOT / "openapi" / "runtime-api.yaml").read_text(encoding="utf-8")
    openapi_match = re.search(r"(?ms)^info:\s*$.*?^\s+version:\s*([^\s]+)", openapi_source)
    storage_source = (ROOT / "ecommerce_ai_skills" / "runtime" / "storage.py").read_text(encoding="utf-8")
    schema_match = re.search(r"^SCHEMA_VERSION\s*=\s*(\d+)", storage_source, re.M)
    if not package_match or not openapi_match or not schema_match:
        raise SystemExit("release version contracts could not be parsed")
    versions = {
        "pyproject": version,
        "package": package_match.group(1),
        "openapi": openapi_match.group(1).strip('"\''),
    }
    if set(versions.values()) != {version}:
        raise SystemExit(f"version contract mismatch: {versions}")
    dist_manifest = json.loads((ROOT / "dist" / "package-manifest.json").read_text(encoding="utf-8"))
    packaged_manifest = json.loads((ROOT / "ecommerce_ai_skills" / "package_data" / "dist" / "package-manifest.json").read_text(encoding="utf-8"))
    if dist_manifest.get("package_version") != version or packaged_manifest != dist_manifest:
        raise SystemExit("distribution package manifests do not match the release version")

    package_files = list((ROOT / "ecommerce_ai_skills").rglob("*.py"))
    script_files = list((ROOT / "scripts").rglob("*"))
    test_files = list((ROOT / "tests").rglob("*"))
    design_evidence_files = list((ROOT / "artifacts" / "design-qa").glob("l7-ui-*.png"))
    contract_paths = [
        "pyproject.toml",
        ".gitignore",
        "openapi/runtime-api.yaml",
        ".github/workflows/release.yml",
        "scripts/build_dist.py",
        "scripts/verify_all.py",
        "CHANGELOG.md",
        "release/v1.3.0-rc.md",
        "roadmap/v1.3-amazon-operator-pilot.md",
        "roadmap/ui-design-system-l7.md",
        "design-qa.md",
        "scripts/loop/v1_3_progress.md",
        *build_metadata_contracts(project),
    ]
    return {
        "schema_version": 1,
        "release": {
            "version": version,
            "tag": f"v{version}",
            "channel": "rc",
            "runtime_schema_version": int(schema_match.group(1)),
            "python_requires": project["requires-python"],
        },
        "version_contract": versions,
        "artifacts": {
            "package_sources": tree_contract("package_sources", package_files),
            "runtime_web_assets": tree_contract(
                "runtime_web_assets",
                list((ROOT / "ecommerce_ai_skills" / "runtime" / "web").rglob("*")),
            ),
            "scripts": tree_contract("scripts", script_files),
            "tests": tree_contract("tests", test_files),
            "design_evidence": tree_contract("design_evidence", design_evidence_files),
            "dist": tree_contract("dist", list((ROOT / "dist").rglob("*"))),
            "wheel_package_data": tree_contract(
                "wheel_package_data",
                list((ROOT / "ecommerce_ai_skills" / "package_data" / "dist").rglob("*")),
            ),
        },
        "contracts": {
            relative: {"sha256": sha256(ROOT / relative), "size": (ROOT / relative).stat().st_size}
            for relative in dict.fromkeys(contract_paths)
        },
        "required_gates": [
            "release_manifest_fresh",
            "dist_fresh",
            "pytest_full",
            "verify_all",
            "cold_wheel_install",
            "wheel_runtime_smoke",
            "installed_demo_e2e",
            "backup_restore_verify",
            "installed_restore_roundtrip",
            "browser_design_qa",
            "tag_matches_version",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output")
    args = parser.parse_args()
    manifest = build_manifest()
    version = manifest["release"]["version"]
    output = Path(args.output).resolve() if args.output else ROOT / "release" / f"v{version}-rc-manifest.json"
    try:
        display = output.relative_to(ROOT)
    except ValueError:
        display = output
    expected = json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not output.is_file() or output.read_text(encoding="utf-8") != expected:
            print(f"release manifest is stale — run: python3 scripts/build_release_manifest.py", file=sys.stderr)
            return 1
        print(f"release manifest fresh: {display}")
        return 0
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(expected, encoding="utf-8")
    print(f"release manifest built: {display}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
