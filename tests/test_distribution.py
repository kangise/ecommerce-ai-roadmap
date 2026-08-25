from __future__ import annotations

import json
import subprocess
import sys
try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib
from pathlib import Path

import pytest
import yaml


ROOT = Path(__file__).resolve().parents[1]


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_dist_and_link_cache_are_not_ignored() -> None:
    assert run("git", "check-ignore", "-q", "dist/SKILL.md").returncode == 1
    assert run("git", "check-ignore", "-q", "scripts/link-status.json").returncode == 1


def test_committed_dist_is_fresh() -> None:
    result = run(sys.executable, "scripts/build_dist.py", "--check")
    assert result.returncode == 0, result.stderr or result.stdout


def test_dist_manifest_matches_runtime(mcp_server_module) -> None:
    server = mcp_server_module.OPCServer(ROOT / "dist")
    counts = server._package_manifest["counts"]
    assert counts == {
        "chapters": 69,
        "entities": 100,
        "relations": 78,
        "constraints": 322,
        "processes": 8,
        "platforms": 15,
        "prompts": 878,
        "skills": 9,
    }


def test_missing_package_fails_closed(tmp_path: Path, mcp_server_module) -> None:
    with pytest.raises(mcp_server_module.PackageValidationError, match="package-manifest"):
        mcp_server_module.OPCServer(tmp_path)


def test_tampered_package_fails_closed(tmp_path: Path, mcp_server_module) -> None:
    target = tmp_path / "dist"
    import shutil

    shutil.copytree(ROOT / "dist", target)
    ontology = target / "ontology.json"
    ontology.write_text("{}\n", encoding="utf-8")
    with pytest.raises(mcp_server_module.PackageValidationError, match="checksum mismatch"):
        mcp_server_module.OPCServer(target)


def test_dist_contains_no_runtime_cache_files() -> None:
    forbidden = [
        p for p in (ROOT / "dist").rglob("*")
        if p.name == "__pycache__" or p.suffix == ".pyc" or p.name == ".DS_Store"
    ]
    assert forbidden == []


def test_package_manifest_is_valid_json() -> None:
    data = json.loads((ROOT / "dist" / "package-manifest.json").read_text(encoding="utf-8"))
    assert data["schema_version"] == 1
    assert data["sha256"]
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    assert data["package_version"] == project["project"]["version"]


def test_generated_docs_enumerate_all_skills_and_public_onboarding_api() -> None:
    skill_ids = sorted(path.name for path in (ROOT / "dist" / "skills").iterdir() if path.is_dir())
    readme = (ROOT / "dist" / "README.md").read_text(encoding="utf-8")
    quickstart = readme.split("## Quick Start", 1)[-1].split("## What's Inside", 1)[0]
    root_skill = (ROOT / "dist" / "SKILL.md").read_text(encoding="utf-8")
    capabilities = root_skill.split("## Your Capabilities", 1)[-1].split("2. **Domain Ontology**", 1)[0]
    system_prompt = (ROOT / "dist" / "integration" / "mcp-system-prompt.md").read_text(encoding="utf-8")
    for skill_id in skill_ids:
        assert skill_id in quickstart
        assert skill_id in capabilities
        assert skill_id in system_prompt

    contract = yaml.safe_load((ROOT / "dist" / "openapi" / "runtime-api.yaml").read_text(encoding="utf-8"))
    assert {"get", "post"} <= set(contract["paths"]["/v1/users"])
    assert "get" in contract["paths"]["/v1/demo-session"]
    assert "patch" in contract["paths"]["/v1/users/{userId}"]
    assert {"get", "post"} <= set(contract["paths"]["/v1/agent-runs"])
    assert "get" in contract["paths"]["/v1/agent-runs/{runId}"]
    assert "post" in contract["paths"]["/v1/agent-runs/{runId}/execute"]
    assert "post" in contract["paths"]["/v1/agent-runs/{runId}/evaluate"]
    assert "get" in contract["paths"]["/v1/agent-runs/{runId}/evaluations"]
    ontology = json.loads((ROOT / "dist" / "ontology.json").read_text(encoding="utf-8"))
    expected_platforms = {item["id"] for item in ontology["platforms"]} | {"cross_platform"}
    assert set(contract["components"]["schemas"]["PlatformId"]["enum"]) == expected_platforms
    assert set(contract["components"]["schemas"]["MarketplaceId"]["enum"]) == expected_platforms - {"cross_platform"}
    assert {"get", "post"} <= set(contract["paths"]["/v1/evidence-imports"])
    assert "get" in contract["paths"]["/v1/evidence-imports/{importId}"]
    from ecommerce_ai_skills.runtime.evidence import REPORT_SPECS
    assert set(contract["components"]["schemas"]["EvidenceReportType"]["enum"]) == set(REPORT_SPECS)
    schemas = contract["components"]["schemas"]
    assert "AmazonSPAPIConnectorRegistration" in schemas
    assert schemas["AmazonReportImportActionRequest"]["properties"]["operation"]["enum"] == [
        "amazon_spapi.import_report"
    ]
    assert {"get", "post"} <= set(contract["paths"]["/v1/jobs"])
    assert {"get", "post"} <= set(contract["paths"]["/v1/schedules"])
    assert "get" in contract["paths"]["/v1/mission-control"]
    assert "get" in contract["paths"]["/v1/briefing"]
    assert "get" in contract["paths"]["/v1/catalog"]
    assert {"DemoSession", "Job", "Schedule", "MissionControl", "OperatingBriefing", "BriefingMetric", "BriefingAgent", "AgentEvaluation", "RuntimeCatalog"} <= set(schemas)


def test_mcp_sdk_is_an_optional_install_extra() -> None:
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    assert all(not dependency.startswith("mcp") for dependency in project.get("dependencies", []))
    assert any(dependency.startswith("mcp") for dependency in project["optional-dependencies"]["mcp"])
    assert all(not dependency.startswith("openpyxl") for dependency in project.get("dependencies", []))
    assert any(
        dependency.startswith("openpyxl")
        for dependency in project["optional-dependencies"]["xlsx"]
    )


def test_installable_package_contains_runtime_and_generated_artifact() -> None:
    package_root = ROOT / "ecommerce_ai_skills"
    assert (package_root / "cli.py").is_file()
    assert (package_root / "demo_seed.py").is_file()
    assert (package_root / "runtime" / "api.py").is_file()
    assert (package_root / "runtime" / "agents.py").is_file()
    assert (package_root / "runtime" / "evidence.py").is_file()
    assert (package_root / "runtime" / "jobs.py").is_file()
    assert (package_root / "runtime" / "evals.py").is_file()
    assert (package_root / "runtime" / "web" / "mission-control.html").is_file()
    assert (package_root / "runtime" / "web" / "app.js").is_file()
    assert (package_root / "runtime" / "web" / "styles.css").is_file()
    assert (package_root / "runtime" / "web" / "assets" / "brands" / "commerce-agent-os.png").is_file()
    assert (package_root / "runtime" / "web" / "assets" / "brands" / "walmart-spark.svg").is_file()
    assert (package_root / "runtime" / "web" / "assets" / "icons" / "house.svg").is_file()
    assert (package_root / "runtime" / "web" / "assets" / "licenses" / "phosphor-icons-LICENSE").is_file()
    package_dist = package_root / "package_data" / "dist"
    assert (package_dist / "package-manifest.json").is_file()
    assert (package_dist / "integration" / "mcp-server.py").is_file()
    assert json.loads((package_dist / "package-manifest.json").read_text(encoding="utf-8"))["sha256"]


def test_mcp_router_passes_all_acceptance_cases(mcp_server_module) -> None:
    server = mcp_server_module.OPCServer(ROOT / "dist")
    cases = yaml.safe_load(
        (ROOT / "tests" / "routing-cases.yaml").read_text(encoding="utf-8")
    )
    failures = []
    for case in cases:
        routed = json.loads(server._route_query(case["query"]))["skill"]
        if routed != case["expect"]:
            failures.append((case["query"], case["expect"], routed))
    assert failures == []


def test_tiktok_shop_product_video_has_deterministic_owner(mcp_server_module) -> None:
    server = mcp_server_module.OPCServer(ROOT / "dist")
    result = json.loads(server._route_query("TikTok Shop 商品视频怎么优化"))
    assert result["skill"] == "ecom-listing"
