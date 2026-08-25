from __future__ import annotations

import json
from email.message import Message

import pytest

from ecommerce_ai_skills.runtime.api import RuntimeApplication, _Handler
from ecommerce_ai_skills.runtime.errors import ValidationError
from ecommerce_ai_skills.runtime.storage import Database


def _import(
    app: RuntimeApplication,
    principal,
    *,
    report_type: str,
    filename: str,
    observed_at: str,
    raw: bytes,
):
    return app.evidence_imports.import_csv(
        principal,
        raw=raw,
        platform="amazon",
        report_type=report_type,
        filename=filename,
        observed_at=observed_at,
        idempotency_key=f"test:{filename}",
        request_id=f"request:{filename}",
    )


def test_briefing_uses_only_recognized_real_evidence_metrics(tmp_path) -> None:
    app = RuntimeApplication(Database(tmp_path / "runtime.sqlite"))
    bootstrap = app.bootstrap("A", "owner@example.com")
    principal = app.auth.authenticate(bootstrap["api_key"])

    _import(
        app,
        principal,
        report_type="amazon_business_report",
        filename="business-1.csv",
        observed_at="2026-08-20T09:00:00+08:00",
        raw=(
            b"ASIN,Sessions,Units Ordered,Ordered Product Sales\n"
            b"A1,20,3,$100.50\nA2,10,1,$50.00\n"
        ),
    )
    _import(
        app,
        principal,
        report_type="amazon_business_report",
        filename="business-2.csv",
        observed_at="2026-08-22T09:00:00+08:00",
        raw=(
            b"ASIN,Sessions,Units Ordered,Ordered Product Sales\n"
            b"A1,25,5,$200.00\nA2,15,2,$100.00\n"
        ),
    )
    _import(
        app,
        principal,
        report_type="amazon_ads_search_term",
        filename="ads.csv",
        observed_at="2026-08-22T09:15:00+08:00",
        raw=(
            b"Campaign Name,Search Term,Spend\n"
            b"SP-1,kitchen shelf,$20.00\nSP-1,storage,$30.00\n"
        ),
    )
    _import(
        app,
        principal,
        report_type="amazon_fba_inventory",
        filename="inventory.csv",
        observed_at="2026-08-22T09:30:00+08:00",
        raw=(
            b"Seller SKU,Fulfillable Quantity\n"
            b"SKU-1,0\nSKU-2,8\nSKU-3,0\n"
        ),
    )
    action = app.actions.request(
        principal,
        "amazon_spapi.import_report",
        {
            "external_account_id": "seller-us",
            "report_id": "report-1",
            "evidence_report_type": "amazon_business_report",
        },
        "action-1",
        "request-action-1",
    )

    briefing = app.briefing.get(principal, "amazon")
    metrics = {metric["key"]: metric for metric in briefing["metrics"]}
    assert briefing["platform"]["id"] == "amazon"
    assert briefing["evidence"]["source_count"] == 4
    assert briefing["evidence"]["row_count"] == 9
    assert metrics["revenue"]["value"] == 300.0
    assert [point["value"] for point in metrics["revenue"]["series"]] == [150.5, 300.0]
    assert metrics["conversion_rate"]["value"] == 17.5
    assert metrics["ad_spend"]["value"] == 50.0
    assert metrics["stockout_skus"]["value"] == 2.0
    assert briefing["approvals"][0]["id"] == action["id"]
    assert briefing["priorities"] == []
    assert briefing["agents"] == []


def test_briefing_is_tenant_scoped_and_validates_platform(tmp_path) -> None:
    app = RuntimeApplication(Database(tmp_path / "runtime.sqlite"))
    first = app.bootstrap("A", "a@example.com")
    second = app.bootstrap("B", "b@example.com")
    first_principal = app.auth.authenticate(first["api_key"])
    second_principal = app.auth.authenticate(second["api_key"])
    _import(
        app,
        first_principal,
        report_type="amazon_business_report",
        filename="private.csv",
        observed_at="2026-08-22T09:00:00+08:00",
        raw=b"ASIN,Sessions,Units Ordered\nA1,10,2\n",
    )

    assert app.briefing.get(second_principal, "amazon")["evidence"]["source_count"] == 0
    with pytest.raises(ValidationError, match="unsupported platform"):
        app.briefing.get(first_principal, "not-a-platform")


def test_http_briefing_endpoint_requires_auth_and_returns_tenant_view(tmp_path) -> None:
    app = RuntimeApplication(Database(tmp_path / "runtime.sqlite"))
    bootstrap = app.bootstrap("A", "owner@example.com")

    class Handler(_Handler):
        def __init__(self, authorization: str | None):
            self.path = "/v1/briefing?platform=amazon"
            self.headers = Message()
            if authorization:
                self.headers["Authorization"] = authorization
            self.out = None

        @property
        def app(self):
            return app

        def _json(self, status, value, request_id, **kwargs):
            self.out = (status, json.loads(json.dumps(value)))

    unauthorized = Handler(None)
    unauthorized.do_GET()
    assert unauthorized.out[0] == 401

    authorized = Handler(f"Bearer {bootstrap['api_key']}")
    authorized.do_GET()
    assert authorized.out[0] == 200
    assert authorized.out[1]["platform"]["id"] == "amazon"
