"""Explicit, isolated Demo tenant seed for Commerce Agent OS.

This module is reachable only through the ``demo-seed`` CLI command.  It is not
imported by the production Runtime API and never runs implicitly.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from .runtime.api import RuntimeApplication
from .runtime.errors import ValidationError
from .runtime.storage import Database


class DemoSeedProvider:
    """Deterministic provider used only while explicitly seeding a Demo DB."""

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
        if agent_name == "store_manager":
            by_type = {
                source["source_type"]: source["source_id"]
                for source in payload["evidence_catalog"]
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
                        "requires_approval": True,
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
                        "requires_approval": True,
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
                        "requires_approval": False,
                    },
                ],
                "risks": [
                    {
                        "risk": "当前 Demo 没有退货率历史。",
                        "mitigation": "连接真实店铺前先导入退货报告。",
                        "evidence_refs": [by_type["amazon_business_report"]],
                        "platforms": ["amazon"],
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
    reviewer = app.auth.create_user(owner, "demo-reviewer@example.test", "admin")
    reviewer_key = app.auth.issue_for_user(owner, str(reviewer["id"]))
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
    ]

    def imported(
        platform: str,
        report_type: str,
        filename: str,
        observed_at: str,
        raw: bytes,
    ) -> dict[str, Any]:
        return app.evidence_imports.import_csv(
            owner,
            raw=raw,
            platform=platform,
            report_type=report_type,
            filename=filename,
            observed_at=observed_at,
            idempotency_key=f"demo:{filename}",
            request_id=f"demo:{filename}",
        )

    today = datetime.now(timezone.utc).astimezone().replace(
        hour=9, minute=0, second=0, microsecond=0
    )
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
                "ASIN,Sessions,Units Ordered,Ordered Product Sales\n"
                f"B08-DEMO,{sessions},{units},{revenue}\n"
            ).encode(),
        )
        import_ids.append(str(item["id"]))
    ads = imported(
        "amazon",
        "amazon_ads_search_term",
        "demo-amazon-ads.csv",
        (today + timedelta(minutes=15)).isoformat(timespec="seconds"),
        b"Campaign Name,Search Term,Spend\nDEMO-SP,kitchen shelf,8400\nDEMO-SP,storage rack,6200\n",
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
        "tenant_mode": "demo",
        "reviewer_email": reviewer["email"],
        "reviewer_api_key": reviewer_key,
        "owner_email": owner.email,
        "owner_api_key": owner_key,
        "evidence_imports": len(import_ids),
        "agent_run_id": run["id"],
        "evaluation_id": evaluation["id"],
        "approval_actions": len(actions),
        "marketplace_accounts": len(marketplace_accounts),
        "schedule_id": schedule["id"],
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
