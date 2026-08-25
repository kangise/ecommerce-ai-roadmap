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
    assert "post" in contract["paths"]["/v1/evidence-imports/{importId}/metric-materialization"]
    assert "get" in contract["paths"]["/v1/metric-observations"]
    assert "get" in contract["paths"]["/v1/metric-observations/{observationId}"]
    assert "get" in contract["paths"]["/v1/metric-materializations"]
    assert "post" in contract["paths"]["/v1/metric-materializations/backfill"]
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
    assert {"DemoSession", "Job", "Schedule", "MissionControl", "OperatingBriefing", "BriefingMetric", "BriefingAgent", "AgentEvaluation", "RuntimeCatalog", "MetricObservation", "MetricMaterialization", "MetricBackfillRequest"} <= set(schemas)


def test_source_runtime_api_l1_connector_contract() -> None:
    """Keep the source contract explicit while generated dist is rebuilt separately."""
    contract = yaml.safe_load(
        (ROOT / "openapi" / "runtime-api.yaml").read_text(encoding="utf-8")
    )
    paths = contract["paths"]
    assert {"get", "post"} <= set(paths["/v1/connectors"])
    assert {"get", "patch"} <= set(paths["/v1/connectors/{accountId}"])
    assert "post" in paths["/v1/connectors/{accountId}/health-check"]

    schemas = contract["components"]["schemas"]
    account = schemas["MarketplaceAccount"]
    assert set(account["required"]) == {
        "id",
        "tenant_id",
        "provider",
        "external_account_id",
        "provider_details",
        "credential_refs",
        "health_status",
        "health_checked_at",
        "health_error_code",
        "health_error_message",
        "created_at",
        "updated_at",
    }
    assert set(schemas["ConnectorProvider"]["enum"]) == {
        "amazon_ads",
        "amazon_spapi",
        "shopify",
    }
    assert set(schemas["ConnectorUpdateRequest"]["required"]) == {"config"}
    assert set(schemas["ConnectorUpdateRequest"]["properties"]) == {
        "external_account_id",
        "config",
    }
    assert {
        "connector_providers",
        "amazon_marketplaces",
        "metric_materialization_report_types",
    } <= set(schemas["RuntimeCatalog"]["required"])
    assert set(schemas["ConnectorProviderCatalogEntry"]["required"]) == {
        "id",
        "name",
        "detail_fields",
        "credential_fields",
    }
    assert set(schemas["AmazonMarketplaceCatalogEntry"]["required"]) == {
        "id",
        "name",
        "country_code",
        "region",
    }

    post = paths["/v1/connectors"]["post"]
    assert set(
        post["requestBody"]["content"]["application/json"]["schema"]["$ref"].split("/")[-1:]
    ) == {"ConnectorRegistration"}
    patch = paths["/v1/connectors/{accountId}"]["patch"]
    assert patch["requestBody"]["content"]["application/json"]["schema"]["$ref"].endswith(
        "/ConnectorUpdateRequest"
    )
    assert "marketplaceParticipations" in paths[
        "/v1/connectors/{accountId}/health-check"
    ]["post"]["description"]
    assert "shop.json" in paths["/v1/connectors/{accountId}/health-check"]["post"]["description"]


def test_source_runtime_api_l7_agent_graph_contract() -> None:
    contract = yaml.safe_load((ROOT / "openapi" / "runtime-api.yaml").read_text(encoding="utf-8"))
    paths = contract["paths"]
    assert {"get", "post"} <= set(paths["/v1/agent-graphs"])
    assert "get" in paths["/v1/agent-graphs/{graphId}"]
    assert "post" in paths["/v1/agent-graphs/{graphId}/versions"]
    assert "post" in paths["/v1/agent-graph-versions/{versionId}/publish"]
    assert "get" in paths["/v1/agent-graph-versions/{versionId}"]
    schemas = contract["components"]["schemas"]
    assert {"AgentGraph", "AgentGraphBundle", "AgentGraphVersion", "AgentGraphDefinition", "GraphNode", "GraphEdge", "ToolPolicy", "ReviewerVerdict", "ReviewerIssue"} <= set(schemas)
    assert schemas["AgentGraphCreate"]["required"] == ["name", "definition"]
    assert set(schemas["AgentGraphDefinition"]["required"]) == {
        "schema_version", "nodes", "edges"
    }
    assert schemas["AgentGraphDefinition"]["properties"]["nodes"]["minItems"] == 5
    assert schemas["AgentGraphDefinition"]["properties"]["nodes"]["maxItems"] == 5
    assert schemas["AgentGraphDefinition"]["properties"]["edges"]["minItems"] == 6
    assert schemas["AgentGraphDefinition"]["properties"]["edges"]["maxItems"] == 6
    assert set(schemas["GraphNode"]["required"]) == {
        "key", "role", "expansion", "optional", "skill_ids",
        "instruction_key", "tool_policy",
    }
    assert set(schemas["AgentGraphVersion"]["properties"]["status"]["enum"]) == {
        "draft", "published", "retired"
    }
    assert "definition_hash" in schemas["AgentGraphVersion"]["required"]
    assert "execution_contract_hash" in schemas["AgentGraphVersion"]["required"]
    assert schemas["ToolPolicy"]["properties"]["max_tool_calls"]["maximum"] == 0
    assert schemas["ToolPolicy"]["properties"]["allowed_tools"]["maxItems"] == 0
    assert schemas["ReviewerVerdict"]["properties"]["verdict"]["enum"] == [
        "approved", "revision_required", "rejected"
    ]
    run = schemas["AgentRun"]
    assert {"graph_version_id", "graph_version_hash", "metric_observation_ids", "review_status"} <= set(run["properties"])
    assert "revision_required" in run["properties"]["review_status"]["enum"]
    request = schemas["AgentRunRequest"]
    assert {"graph_version_id", "metric_observation_ids"} <= set(request["properties"])


def test_source_runtime_api_l2_report_recipe_contract() -> None:
    contract = yaml.safe_load(
        (ROOT / "openapi" / "runtime-api.yaml").read_text(encoding="utf-8")
    )
    paths = contract["paths"]
    assert {"get", "post"} <= set(paths["/v1/report-recipes"])
    assert {"get", "patch"} <= set(paths["/v1/report-recipes/{recipeId}"])
    schemas = contract["components"]["schemas"]

    expected_keys = {
        "sales_traffic_daily",
        "fba_inventory_daily",
        "listings_daily",
        "returns_daily",
    }
    assert set(schemas["ReportRecipeKey"]["enum"]) == expected_keys
    assert set(schemas["ReportRecipe"]["required"]) == {
        "id",
        "tenant_id",
        "connector_account_id",
        "created_by",
        "name",
        "recipe_key",
        "amazon_report_type",
        "evidence_report_type",
        "marketplace_ids",
        "interval_minutes",
        "lookback_days",
        "enabled",
        "next_run_at",
        "created_at",
        "updated_at",
    }
    create_required = set(schemas["ReportRecipeCreate"]["required"])
    assert create_required == {
        "connector_account_id",
        "name",
        "recipe_key",
        "marketplace_ids",
        "interval_minutes",
        "lookback_days",
        "enabled",
        "next_run_at",
    }
    update_required = set(schemas["ReportRecipeUpdate"]["required"])
    assert update_required == create_required - {"connector_account_id"}
    assert "connector_account_id" not in schemas["ReportRecipeUpdate"]["properties"]
    assert set(schemas["ReportRecipeCatalogEntry"]["required"]) == {
        "key",
        "label",
        "amazon_report_type",
        "evidence_report_type",
    }
    assert "report_recipe_types" in schemas["RuntimeCatalog"]["required"]
    assert "Amazon SP-API" in paths["/v1/report-recipes"]["post"]["description"]
    assert "subset" in paths["/v1/report-recipes"]["post"]["description"]
    assert "does not call Amazon" in paths["/v1/report-recipes"]["post"]["description"]


def test_source_runtime_api_l3_report_sync_contract() -> None:
    contract = yaml.safe_load(
        (ROOT / "openapi" / "runtime-api.yaml").read_text(encoding="utf-8")
    )
    paths = contract["paths"]
    assert "post" in paths["/v1/report-recipes/{recipeId}/sync"]
    assert "get" in paths["/v1/report-syncs"]
    assert "get" in paths["/v1/report-syncs/{syncId}"]
    enqueue = paths["/v1/report-recipes/{recipeId}/sync"]["post"]
    assert any(item.get("name") == "Idempotency-Key" for item in enqueue["parameters"])
    sync = contract["components"]["schemas"]["ReportSync"]
    assert {"queued", "polling", "succeeded", "failed"} == set(
        sync["properties"]["status"]["enum"]
    )
    assert {
        "recipe_id",
        "connector_account_id",
        "amazon_report_id",
        "processing_status",
        "period_start",
        "period_end",
        "available_at",
        "attempt_count",
        "max_attempts",
        "evidence_import_id",
        "error_code",
        "error_message",
    } <= set(sync["required"])


def test_source_runtime_api_l4_metric_materialization_contract() -> None:
    contract = yaml.safe_load(
        (ROOT / "openapi" / "runtime-api.yaml").read_text(encoding="utf-8")
    )
    paths = contract["paths"]
    materialize_path = "/v1/evidence-imports/{importId}/metric-materialization"
    required_operations = {
        "/v1/metric-observations": "get",
        "/v1/metric-observations/{observationId}": "get",
        "/v1/metric-materializations": "get",
        materialize_path: "post",
        "/v1/metric-materializations/backfill": "post",
    }
    for route, method in required_operations.items():
        assert method in paths[route]

    materialize = paths[materialize_path]["post"]
    assert "operator or higher" in materialize["description"]
    assert "never rolls back" in materialize["description"]
    assert any(
        parameter.get("name") == "Idempotency-Key" and parameter.get("required")
        for parameter in materialize["parameters"]
    )
    backfill = paths["/v1/metric-materializations/backfill"]["post"]
    assert "admin or owner" in backfill["description"]
    assert "at most 100" in backfill["description"]

    schemas = contract["components"]["schemas"]
    assert {"MetricObservation", "MetricMaterialization", "MetricBackfillRequest"} <= set(
        schemas
    )
    observation = schemas["MetricObservation"]
    assert {
        "tenant_id",
        "materialization_id",
        "evidence_import_id",
        "metric_key",
        "value_decimal",
        "currency",
        "period_start",
        "period_end",
        "time_grain",
        "provenance",
        "quality",
    } <= set(observation["required"])
    decimal = observation["properties"]["value_decimal"]
    assert decimal["type"] == "string"
    assert decimal["maxLength"] == 40
    assert "NaN" in decimal["description"] and "overflow" in decimal["description"]
    assert observation["properties"]["currency"]["pattern"] == "^[A-Z]{3}$"
    assert "ZZZ" not in observation["properties"]["currency"]["enum"]

    materialization = schemas["MetricMaterialization"]
    assert {"running", "succeeded", "partial", "quarantined", "failed"} == set(
        materialization["properties"]["status"]["enum"]
    )
    assert {"observation_count", "quarantine_count", "quality_summary"} <= set(
        materialization["required"]
    )
    request = schemas["MetricBackfillRequest"]
    assert request["additionalProperties"] is False
    assert request["properties"]["limit"]["minimum"] == 1
    assert request["properties"]["limit"]["maximum"] == 100
    assert "cursor" in request["properties"]


def test_source_runtime_api_l5_ads_capability_gate_contract() -> None:
    contract = yaml.safe_load((ROOT / "openapi" / "runtime-api.yaml").read_text(encoding="utf-8"))
    paths = contract["paths"]
    assert {"get", "post"} <= set(paths["/v1/ads-capability-gates"])
    assert "get" in paths["/v1/ads-capability-gates/{gateId}"]
    post = paths["/v1/ads-capability-gates"]["post"]
    assert any(p.get("name") == "Idempotency-Key" and p.get("required") for p in post["parameters"])
    assert "admin or owner" in post["description"]
    assert "201" in post["responses"]
    schemas = contract["components"]["schemas"]
    assert {
        "AmazonAdsConnectorRegistration",
        "AmazonAdsConnectorConfig",
        "AmazonAdsProviderDetails",
    } <= set(schemas)
    assert schemas["AmazonAdsConnectorConfig"]["properties"]["profile_id"][
        "pattern"
    ] == "^[0-9]{1,32}$"
    gate = schemas["AdsCapabilityGate"]
    assert {"checking", "passed", "blocked", "failed"} == set(gate["properties"]["status"]["enum"])
    assert {"required_capabilities", "observed_capabilities", "checks", "request_ids"} <= set(gate["required"])
    assert {"created_by", "region", "profile_id", "retry_after_seconds"} <= set(
        gate["required"]
    )
    assert gate["properties"]["checks"]["items"]["required"] == ["name", "status"]
    request = schemas["AdsCapabilityGateRequest"]
    assert request["required"] == ["connector_account_id"]
    assert request["additionalProperties"] is False


def test_source_runtime_api_l6_ads_adapter_negative_contract() -> None:
    contract = yaml.safe_load((ROOT / "openapi" / "runtime-api.yaml").read_text(encoding="utf-8"))
    route = contract["paths"]["/v1/ads-adapter-status"]["get"]
    assert "connector_account_id" in {p["name"] for p in route["parameters"]}
    schema = contract["components"]["schemas"]["AdsAdapterStatus"]
    assert schema["properties"]["status"]["enum"] == ["blocked", "eligible_not_installed"]
    assert schema["properties"]["adapter_registered"]["enum"] == [False]
    assert schema["properties"]["write_operations"]["maxItems"] == 0
    assert set(schema["properties"]["reason_codes"]["items"]["enum"]) == {
        "no_amazon_ads_account", "no_capability_gate", "gate_not_passed",
        "required_capabilities_missing", "gate_account_config_mismatch",
        "gate_not_checked", "gate_stale_account_changed", "gate_expired",
        "gate_checked_in_future", "adapter_not_installed", "write_surface_disabled",
    }
    for field in ("connector_account_id", "gate_id", "gate_checked_at", "account_updated_at", "profile_id", "region"):
        assert schema["properties"][field]["nullable"] is True
    assert schema["properties"]["evaluated_at"]["format"] == "date-time"
    assert "POST /v1/ads-adapter-status" not in contract["paths"]


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
