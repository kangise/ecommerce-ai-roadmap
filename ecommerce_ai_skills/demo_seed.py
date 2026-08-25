"""Explicit, isolated Demo tenant seed for Commerce Agent OS.

This module is reachable only through the explicit ``demo-seed`` and ``demo``
CLI commands. It is not imported by the production Runtime API and never runs
implicitly.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from .runtime.api import RuntimeApplication
from .runtime.errors import ValidationError
from .runtime.metric_observations import SUPPORTED_REPORT_TYPES
from .runtime.storage import Database


class DemoSeedProvider:
    """Deterministic provider used only by an explicitly started Demo runtime."""

    def configuration(self) -> tuple[str, str]:
        return "demo_seed", "demo-seed-v1"

    def complete(
        self,
        *,
        agent_name: str,
        instructions: str,
        payload: dict[str, Any],
        output_schema: dict[str, Any],
        safety_identifier: str,
    ) -> dict[str, Any]:
        if agent_name == "operations_reviewer":
            return {
                "verdict": "approved",
                "issues": [],
                "evidence_refs": [
                    source["source_id"] for source in payload["evidence_catalog"]
                ],
                "limitations": payload["manager_report"].get("limitations", []),
            }
        if agent_name == "store_manager":
            by_type = {
                source["source_type"]: source["source_id"]
                for source in payload["evidence_catalog"]
            }
            seeded_types = {
                "amazon_ads_search_term",
                "amazon_fba_inventory",
                "amazon_business_report",
                "platform_generic",
            }
            if not seeded_types.issubset(by_type):
                source = payload["evidence_catalog"][0]
                platform = source["platform"]
                owner = (
                    f"platform_{platform}_operator"
                    if platform != "cross_platform"
                    else "human_operator"
                )
                return {
                    "executive_summary": "已完成所选 Demo 输入的证据约束复核。",
                    "priorities": [
                        {
                            "rank": 1,
                            "title": "复核所选 Demo 经营信号",
                            "why_now": "该结论仅来自本次明确选择的 Demo 输入。",
                            "evidence_refs": [source["source_id"]],
                            "platforms": [platform],
                            "expected_impact": "为人工经营判断提供可追溯输入。",
                            "confidence": "medium",
                            "recommended_owner": owner,
                            "downstream_action": "保留为人工经营复核记录。",
                            "action_type": "analysis",
                            "requires_approval": True,
                            "metric_claim": {
                                "operation": (
                                    "observe"
                                    if source["source_type"] == "metric_observation"
                                    else "none"
                                ),
                                "observation_refs": (
                                    [source["source_id"]]
                                    if source["source_type"] == "metric_observation"
                                    else []
                                ),
                            },
                        }
                    ],
                    "risks": [],
                    "limitations": ["这是明确标记的 Demo 数据，不可用于真实经营决策。"],
                }
            return {
                "executive_summary": "广告效率与补货风险需要优先处理；跨平台价格差异值得复核。",
                "priorities": [
                    {
                        "rank": 1,
                        "title": "广告效率正在拖累利润",
                        "why_now": "最新 Amazon 搜索词 Evidence 显示当前广告花费需要复核。",
                        "evidence_refs": [by_type["amazon_ads_search_term"]],
                        "platforms": ["amazon"],
                        "expected_impact": "减少未经验证的广告浪费",
                        "confidence": "high",
                        "recommended_owner": "platform_amazon_operator",
                        "downstream_action": "准备关键词与出价调整提案，不直接写入平台。",
                        "action_type": "external_change",
                        "requires_approval": True,
                        "metric_claim": {"operation": "none", "observation_refs": []},
                    },
                    {
                        "rank": 2,
                        "title": "3 个畅销 ASIN 面临缺货",
                        "why_now": "FBA Inventory Evidence 中有 3 个 SKU 的可售库存为零。",
                        "evidence_refs": [by_type["amazon_fba_inventory"]],
                        "platforms": ["amazon"],
                        "expected_impact": "降低断货导致的销售损失",
                        "confidence": "high",
                        "recommended_owner": "platform_amazon_operator",
                        "downstream_action": "生成补货审批草案。",
                        "action_type": "external_change",
                        "requires_approval": True,
                        "metric_claim": {"operation": "none", "observation_refs": []},
                    },
                    {
                        "rank": 3,
                        "title": "跨平台价格存在差异",
                        "why_now": "Amazon 与 Shopify 的最新商品 Evidence 需要统一核对定价边界。",
                        "evidence_refs": [
                            by_type["amazon_business_report"],
                            by_type["platform_generic"],
                        ],
                        "platforms": ["amazon", "shopify"],
                        "expected_impact": "减少渠道间利润与转化冲突",
                        "confidence": "medium",
                        "recommended_owner": "cross_platform_controller",
                        "downstream_action": "生成人工复核清单。",
                        "action_type": "analysis",
                        "requires_approval": True,
                        "metric_claim": {"operation": "none", "observation_refs": []},
                    },
                ],
                "risks": [
                    {
                        "risk": "当前 Demo 没有退货率历史。",
                        "mitigation": "连接真实店铺前先导入退货报告。",
                        "evidence_refs": [by_type["amazon_business_report"]],
                        "platforms": ["amazon"],
                        "metric_claim": {"operation": "none", "observation_refs": []},
                    }
                ],
                "limitations": ["这是明确标记的 Demo 数据，不可用于真实经营决策。"],
            }
        if "evidence" in payload:
            source_id = payload["evidence"][0]["source_id"]
            platform = payload["target_platform"]
        else:
            source_id = next(
                finding["evidence_refs"][0]
                for specialist in payload["specialist_findings"].values()
                for finding in specialist["findings"]
            )
            platform = "cross_platform"
        return {
            "platform": platform,
            "summary": f"{agent_name} completed the explicit Demo review.",
            "findings": [
                {
                    "title": "Demo evidence review completed",
                    "severity": "warning",
                    "confidence": "high",
                    "evidence_refs": [source_id],
                    "recommendation": "Keep every proposed external action behind approval.",
                }
            ],
            "data_gaps": [],
        }


def seed_demo_database(path: str | Path) -> dict[str, Any]:
    """Create a new, isolated Demo database and return one-time keys."""

    db_path = Path(path).expanduser().resolve()
    if db_path.exists():
        raise ValidationError(
            "demo-seed requires a new database path; it will not modify an existing file"
        )
    app = RuntimeApplication(Database(db_path), agent_provider=DemoSeedProvider())
    tenant_id, owner_id = app.db.create_tenant(
        "Commerce Agent OS Demo", "demo-owner@example.test", mode="demo"
    )
    owner_key = app.auth.issue_key(tenant_id, owner_id)
    owner = app.auth.authenticate(owner_key)
    graph_version = app.agent_graphs.ensure_default(owner)
    reviewer = app.auth.create_user(owner, "demo-reviewer@example.test", "admin")
    reviewer_key = app.auth.issue_for_user(owner, str(reviewer["id"]))
    reviewer_principal = app.auth.authenticate(reviewer_key)
    marketplace_accounts = [
        app.accounts.create(
            owner,
            "amazon_spapi",
            "demo-seller-us",
            {
                "region": "na",
                "marketplace_ids": ["ATVPDKIKX0DER"],
                "lwa_client_id_ref": "DEMO_AMAZON_LWA_CLIENT_ID",
                "lwa_client_secret_ref": "DEMO_AMAZON_LWA_CLIENT_SECRET",
                "lwa_refresh_token_ref": "DEMO_AMAZON_LWA_REFRESH_TOKEN",
            },
            "demo-account-amazon",
        ),
        app.accounts.create(
            owner,
            "shopify",
            "demo-shopify-store",
            {
                "shop_domain": "demo-store.myshopify.com",
                "api_version": "2026-07",
                "credential_ref": "DEMO_SHOPIFY_ACCESS_TOKEN",
            },
            "demo-account-shopify",
        ),
        app.accounts.create(
            owner,
            "amazon_ads",
            "demo-ads-profile",
            {
                "region": "na",
                "profile_id": "1234567890",
                "lwa_client_id_ref": "DEMO_AMAZON_ADS_LWA_CLIENT_ID",
                "lwa_client_secret_ref": "DEMO_AMAZON_ADS_LWA_CLIENT_SECRET",
                "lwa_refresh_token_ref": "DEMO_AMAZON_ADS_LWA_REFRESH_TOKEN",
            },
            "demo-account-amazon-ads",
        ),
    ]
    # Explicit Demo state: prove the missing-credential blocker without making
    # a network call or manufacturing a passed capability check.
    app.ads_gates.environ = {}
    ads_gate = app.ads_gates.check(
        owner,
        str(marketplace_accounts[2]["id"]),
        None,
        "demo-amazon-ads-gate",
        "demo-amazon-ads-gate",
    )
    recipe_start = datetime.now(timezone.utc).replace(
        hour=2, minute=0, second=0, microsecond=0
    ) + timedelta(days=1)
    report_recipes = []
    for index, recipe_key in enumerate(
        (
            "sales_traffic_daily",
            "fba_inventory_daily",
            "listings_daily",
            "returns_daily",
        )
    ):
        report_recipes.append(
            app.report_recipes.create(
                owner,
                connector_account_id=str(marketplace_accounts[0]["id"]),
                name=recipe_key.replace("_", " ").title(),
                recipe_key=recipe_key,
                marketplace_ids=["ATVPDKIKX0DER"],
                interval_minutes=1440,
                lookback_days=7,
                enabled=True,
                next_run_at=(recipe_start + timedelta(minutes=index * 15)).isoformat(
                    timespec="seconds"
                ),
                request_id=f"demo-report-recipe-{recipe_key}",
            )
        )

    def imported(
        platform: str,
        report_type: str,
        filename: str,
        observed_at: str,
        raw: bytes,
    ) -> dict[str, Any]:
        result = app.evidence_imports.import_csv(
            owner,
            raw=raw,
            platform=platform,
            report_type=report_type,
            filename=filename,
            observed_at=observed_at,
            idempotency_key=f"demo:{filename}",
            request_id=f"demo:{filename}",
        )
        if report_type in SUPPORTED_REPORT_TYPES:
            app.metric_observations.materialize(
                owner,
                str(result["id"]),
                f"demo-metrics:{filename}",
                f"demo-metrics:{filename}",
            )
        return result

    demo_zone = ZoneInfo("Asia/Shanghai")
    local_now = datetime.now(timezone.utc).astimezone(demo_zone)
    today = local_now.replace(hour=9, minute=0, second=0, microsecond=0)
    if today + timedelta(minutes=35) > local_now:
        today = (local_now - timedelta(minutes=40)).replace(second=0, microsecond=0)
    observations = (185000, 205000, 196000, 232000, 218000, 226000, 244000)
    import_ids: list[str] = []
    for index, revenue in enumerate(observations):
        observed = today - timedelta(days=6 - index)
        units = 920 + index * 38
        sessions = 8400 + index * 135
        filename = f"demo-amazon-business-{observed.date().isoformat()}.csv"
        item = imported(
            "amazon",
            "amazon_business_report",
            filename,
            observed.isoformat(timespec="seconds"),
            (
                "ASIN,Sessions,Units Ordered,Ordered Product Sales,Currency Code\n"
                f"B08-DEMO,{sessions},{units},{revenue},USD\n"
            ).encode(),
        )
        import_ids.append(str(item["id"]))
    ads = imported(
        "amazon",
        "amazon_ads_search_term",
        "demo-amazon-ads.csv",
        (today + timedelta(minutes=15)).isoformat(timespec="seconds"),
        b"Campaign Name,Search Term,Spend,Currency Code\nDEMO-SP,kitchen shelf,8400,USD\nDEMO-SP,storage rack,6200,USD\n",
    )
    inventory = imported(
        "amazon",
        "amazon_fba_inventory",
        "demo-amazon-inventory.csv",
        (today + timedelta(minutes=30)).isoformat(timespec="seconds"),
        b"Seller SKU,Fulfillable Quantity\nDEMO-1,0\nDEMO-2,0\nDEMO-3,0\nDEMO-4,18\n",
    )
    shopify = imported(
        "shopify",
        "platform_generic",
        "demo-shopify-products.csv",
        (today + timedelta(minutes=35)).isoformat(timespec="seconds"),
        b"SKU,Price\nDEMO-1,29.00\nDEMO-2,41.00\n",
    )
    import_ids.extend([str(ads["id"]), str(inventory["id"]), str(shopify["id"])])

    daily_schedule = app.daily_ops.create(
        owner,
        name="Demo Amazon daily pulse",
        platform="amazon",
        objective="Review the newest Demo Amazon business evidence for this local business day.",
        timezone_name="Asia/Shanghai",
        local_time=(today + timedelta(minutes=36)).strftime("%H:%M"),
        graph_version_id=str(graph_version["id"]),
        evidence_selectors=[{"report_type": "amazon_business_report"}],
        max_source_age_hours=48,
        enabled=True,
        request_id="demo-daily-ops-schedule",
    )
    daily_run = app.daily_ops.trigger(
        owner,
        str(daily_schedule["id"]),
        "demo-daily-ops-trigger",
        today.date().isoformat(),
    )
    if daily_run["status"] == "scheduled":
        daily_run = app.daily_ops.execute(
            owner, str(daily_run["id"]), "demo-daily-ops-execute"
        )

    proposal_expiry = (datetime.now(timezone.utc) + timedelta(days=7)).isoformat(
        timespec="seconds"
    )

    def seeded_proposal(
        *, key: str, operation: str, payload: dict[str, Any], rollback_plan: str
    ) -> dict[str, Any]:
        proposal = app.proposals.create(
            owner,
            daily_ops_run_id=str(daily_run["id"]),
            priority_rank=1,
            operation=operation,
            payload=payload,
            risk="low",
            rollback_plan=rollback_plan,
            idempotency_key=f"demo-proposal:{key}",
            expires_at=proposal_expiry,
            request_id=f"demo-proposal-{key}-create",
        )
        if proposal["status"] == "draft":
            proposal = app.proposals.submit(
                owner,
                str(proposal["id"]),
                expected_version=int(proposal["version"]),
                request_id=f"demo-proposal-{key}-submit",
            )
        if proposal["status"] == "submitted":
            proposal = app.proposals.decide(
                reviewer_principal,
                str(proposal["id"]),
                expected_version=int(proposal["version"]),
                decision="approve",
                comment="Approved for the isolated Demo tenant only.",
                request_id=f"demo-proposal-{key}-approve",
            )
        if proposal["status"] == "approved":
            app.proposals.execute(
                owner,
                str(proposal["id"]),
                expected_version=int(proposal["version"]),
                idempotency_key=f"demo-proposal:{key}:execution",
                request_id=f"demo-proposal-{key}-execute",
            )
        return app.proposals.get(owner, str(proposal["id"]))

    human_proposal = seeded_proposal(
        key="human-review",
        operation="human.review",
        payload={
            "instructions": "Review the Demo daily priority and record the operator decision."
        },
        rollback_plan="Close the local review record; no marketplace state was changed.",
    )
    ads_proposal = seeded_proposal(
        key="amazon-ads-blocked",
        operation="amazon_ads.campaign_update",
        payload={
            "external_account_id": "demo-ads-profile",
            "campaign_id": "DEMO-SP",
            "changes": {"state": "paused"},
        },
        rollback_plan="No rollback is required because the unavailable Ads adapter makes zero calls.",
    )

    run = app.agent_runs.request(
        owner,
        "weekly_ops",
        "Review Demo profitability, ad efficiency, inventory, and cross-platform pricing.",
        [],
        "demo-weekly-ops",
        "demo-weekly-ops-request",
        evidence_import_ids=import_ids,
    )
    app.agent_runs.execute(owner, str(run["id"]), "demo-weekly-ops-execute")
    evaluation = app.evaluator.evaluate(
        owner, str(run["id"]), "demo-weekly-ops-evaluate"
    )
    actions = []
    for index, report_id in enumerate(("DEMO-REPORT-1", "DEMO-REPORT-2"), start=1):
        actions.append(
            app.actions.request(
                owner,
                "amazon_spapi.import_report",
                {
                    "external_account_id": "demo-seller-us",
                    "report_id": report_id,
                    "evidence_report_type": "amazon_business_report",
                },
                f"demo-action-{index}",
                f"demo-action-request-{index}",
            )
        )
    schedule = app.schedules.create(
        owner,
        name="Demo Amazon weekly review",
        objective="Review the newest Demo Amazon business evidence.",
        evidence_import_ids=[],
        evidence_selectors=[
            {"platform": "amazon", "report_type": "amazon_business_report"}
        ],
        interval_minutes=10080,
        next_run_at=(today + timedelta(days=7)).isoformat(timespec="seconds"),
        request_id="demo-schedule-create",
    )
    job = app.jobs.enqueue_agent_run(
        owner,
        str(run["id"]),
        "demo-completed-run-job",
        "demo-completed-run-job-request",
    )
    completed_job = app.jobs.run_once()
    app.db.append_audit(
        tenant_id,
        owner_id,
        "demo-seed",
        "demo.seed",
        "tenant",
        tenant_id,
        "succeeded",
        {"database": str(db_path), "warning": "Demo data only"},
    )
    return {
        "warning": "DEMO DATA ONLY — never use for real business decisions",
        "database": str(db_path),
        "tenant_id": tenant_id,
        "agent_graph_version_id": graph_version["id"],
        "tenant_mode": "demo",
        "reviewer_email": reviewer["email"],
        "reviewer_api_key": reviewer_key,
        "owner_email": owner.email,
        "owner_api_key": owner_key,
        "evidence_imports": len(import_ids),
        "metric_materializations": len(
            app.metric_observations.list_materializations(owner)["materializations"]
        ),
        "agent_run_id": run["id"],
        "evaluation_id": evaluation["id"],
        "approval_actions": len(actions),
        "marketplace_accounts": len(marketplace_accounts),
        "ads_capability_gate_id": ads_gate["id"],
        "ads_capability_gate_status": ads_gate["status"],
        "report_recipes": len(report_recipes),
        "schedule_id": schedule["id"],
        "daily_ops_schedule_id": daily_schedule["id"],
        "daily_ops_run_id": daily_run["id"],
        "daily_ops_run_status": daily_run["status"],
        "proposal_count": 2,
        "human_review_proposal_id": human_proposal["id"],
        "human_review_proposal_status": human_proposal["status"],
        "amazon_ads_proposal_id": ads_proposal["id"],
        "amazon_ads_proposal_status": ads_proposal["status"],
        "job_id": job["id"],
        "job_status": completed_job["status"] if completed_job else None,
    }


def open_demo_runtime(path: str | Path) -> RuntimeApplication:
    """Open or create a Demo-only Runtime with a temporary browser session."""

    db_path = Path(path).expanduser().resolve()
    if not db_path.exists():
        seed_demo_database(db_path)
    app = RuntimeApplication(Database(db_path), agent_provider=DemoSeedProvider())
    tenants = app.db.list_tenants()
    if len(tenants) != 1 or tenants[0]["mode"] != "demo":
        raise ValidationError(
            "demo server requires a database containing exactly one Demo tenant"
        )
    users = app.db.list_users(str(tenants[0]["id"]))
    reviewer = next(
        (
            user
            for user in users
            if user["email"] == "demo-reviewer@example.test"
            and user["role"] in {"admin", "owner"}
        ),
        None,
    )
    if reviewer is None:
        raise ValidationError("demo server requires the seeded Demo reviewer")
    key = app.auth.issue_key(str(tenants[0]["id"]), str(reviewer["id"]))
    app.demo_key_id = key.rsplit(".", 1)[1]
    app.demo_session = {
        "api_key": key,
        "tenant_id": str(tenants[0]["id"]),
        "tenant_mode": "demo",
        "warning": "DEMO DATA ONLY — never use for real business decisions",
    }
    app.db.append_audit(
        str(tenants[0]["id"]),
        str(reviewer["id"]),
        "demo-session-start",
        "demo.session.start",
        "api_key",
        app.demo_key_id,
        "succeeded",
        {"bind": "127.0.0.1", "warning": "Demo data only"},
    )
    return app
