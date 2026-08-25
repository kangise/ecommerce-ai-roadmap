"""Local-only populated UI fixture for browser design QA.

This module is never packaged or used by production runtime paths.  It binds to
loopback, creates an isolated temporary database, and accepts the literal
non-secret browser key ``test`` so visual QA can exercise the real UI without
transmitting a real credential.
"""

from __future__ import annotations

import tempfile
import sys
from http.server import ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ecommerce_ai_skills.runtime.api import RuntimeApplication, _Handler
from ecommerce_ai_skills.runtime.storage import Database


class PreviewProvider:
    def configuration(self):
        return "ui_preview_fixture", "fixture-model"

    def complete(
        self, *, agent_name, instructions, payload, output_schema, safety_identifier
    ):
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
                "risks": [],
                "limitations": ["Fixture is for browser design QA only."],
            }
        if "evidence" in payload:
            sources = payload["evidence"]
            source_id = sources[0]["source_id"]
            platform = payload["target_platform"]
        else:
            findings = payload["specialist_findings"].values()
            source_id = next(
                finding["evidence_refs"][0]
                for specialist in findings
                for finding in specialist["findings"]
            )
            platform = "cross_platform"
        return {
            "platform": platform,
            "summary": f"{agent_name} completed an evidence-bound review.",
            "findings": [
                {
                    "title": "Evidence review completed",
                    "severity": "warning",
                    "confidence": "high",
                    "evidence_refs": [source_id],
                    "recommendation": "Keep the proposed action behind approval.",
                }
            ],
            "data_gaps": [],
        }


def seed(app: RuntimeApplication):
    tenant_id, owner_id = app.db.create_tenant(
        "UI Preview Demo", "director@example.test", mode="demo"
    )
    principal = app.auth.authenticate(app.auth.issue_key(tenant_id, owner_id))

    def imported(platform, report_type, filename, observed_at, raw):
        return app.evidence_imports.import_csv(
            principal,
            raw=raw,
            platform=platform,
            report_type=report_type,
            filename=filename,
            observed_at=observed_at,
            idempotency_key=f"preview:{filename}",
            request_id=f"preview:{filename}",
        )

    import_ids = []
    for day, revenue, units, sessions in (
        ("16", 185000, 920, 8400),
        ("17", 205000, 980, 8600),
        ("18", 196000, 950, 8500),
        ("19", 232000, 1100, 9000),
        ("20", 218000, 1040, 8900),
        ("21", 226000, 1070, 9050),
        ("22", 244000, 1150, 9200),
    ):
        item = imported(
            "amazon",
            "amazon_business_report",
            f"business-2026-08-{day}.csv",
            f"2026-08-{day}T09:00:00+08:00",
            (
                "ASIN,Sessions,Units Ordered,Ordered Product Sales\n"
                f"B08-A,{sessions},{units},{revenue}\n"
            ).encode(),
        )
        import_ids.append(item["id"])
    ads = imported(
        "amazon",
        "amazon_ads_search_term",
        "ads-2026-08-22.csv",
        "2026-08-22T09:15:00+08:00",
        b"Campaign Name,Search Term,Spend\nSP-1,kitchen shelf,8400\nSP-1,storage rack,6200\n",
    )
    inventory = imported(
        "amazon",
        "amazon_fba_inventory",
        "inventory-2026-08-22.csv",
        "2026-08-22T09:30:00+08:00",
        b"Seller SKU,Fulfillable Quantity\nSKU-1,0\nSKU-2,0\nSKU-3,0\nSKU-4,18\n",
    )
    shopify = imported(
        "shopify",
        "platform_generic",
        "shopify-products-2026-08-22.csv",
        "2026-08-22T09:35:00+08:00",
        b"SKU,Price\nSKU-1,29.00\nSKU-2,41.00\n",
    )
    import_ids.extend([ads["id"], inventory["id"], shopify["id"]])
    run = app.agent_runs.request(
        principal,
        "weekly_ops",
        "Review current profitability, ad efficiency, inventory, and cross-platform pricing.",
        [],
        "preview-run",
        "preview-run-request",
        evidence_import_ids=import_ids,
    )
    app.agent_runs.execute(principal, run["id"], "preview-run-execute")
    for index, report_id in enumerate(("report-1", "report-2"), start=1):
        app.actions.request(
            principal,
            "amazon_spapi.import_report",
            {
                "external_account_id": "seller-us",
                "report_id": report_id,
                "evidence_report_type": "amazon_business_report",
            },
            f"preview-action-{index}",
            f"preview-action-request-{index}",
        )
    return principal


def main() -> None:
    root = Path(tempfile.mkdtemp(prefix="eai-ui-preview-"))
    app = RuntimeApplication(
        Database(root / "runtime.sqlite"), agent_provider=PreviewProvider()
    )
    principal = seed(app)

    class PreviewHandler(_Handler):
        def _principal(self):
            return principal

    server = ThreadingHTTPServer(("127.0.0.1", 8794), PreviewHandler)
    server.app = app
    print("UI preview fixture listening on http://127.0.0.1:8794/app", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
