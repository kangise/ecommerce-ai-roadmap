from __future__ import annotations

from datetime import datetime, timezone
from email.message import Message
from pathlib import Path

import pytest

from ecommerce_ai_skills.runtime.ads_adapter_status import AdsAdapterStatusService
from ecommerce_ai_skills.runtime.ads_gates import REQUIRED_CAPABILITIES
from ecommerce_ai_skills.runtime.actions import ActionService
from ecommerce_ai_skills.runtime.api import RuntimeApplication, _Handler
from ecommerce_ai_skills.runtime.auth import AuthService
from ecommerce_ai_skills.runtime.errors import NotFoundError, ValidationError
from ecommerce_ai_skills.runtime.storage import Database


CONFIG = {
    "region": "na",
    "profile_id": "1234567890",
    "lwa_client_id_ref": "ADS_CLIENT_ID",
    "lwa_client_secret_ref": "ADS_CLIENT_SECRET",
    "lwa_refresh_token_ref": "ADS_REFRESH_TOKEN",
}


def fixture(tmp_path: Path):
    db = Database(tmp_path / "runtime.sqlite")
    tenant, owner_id = db.create_tenant("A", "owner@example.com")
    auth = AuthService(db)
    owner = auth.authenticate(auth.issue_key(tenant, owner_id))
    viewer_id = db.create_user(tenant, "viewer@example.com", "viewer")
    viewer = auth.authenticate(auth.issue_key(tenant, viewer_id))
    account = db.add_connector_account(tenant, "amazon_ads", "profile", CONFIG)
    return db, auth, owner, viewer, account


def passed_gate(
    db: Database,
    tenant: str,
    user: str,
    account: str,
    *,
    key: str = "gate-passed",
):
    gate, _ = db.create_ads_capability_gate(
        tenant, user, account, key, region="na", profile_id="1234567890",
        required_capabilities=REQUIRED_CAPABILITIES, attestation_reference="attest-1",
    )
    db.claim_ads_capability_gate(tenant, gate["id"])
    return db.finish_ads_capability_gate(
        tenant, gate["id"], status="passed", observed_capabilities=REQUIRED_CAPABILITIES,
        checks=[], request_ids=[],
    )


def test_no_account_is_blocked_and_no_adapter_is_registered(tmp_path: Path):
    db = Database(tmp_path / "empty.sqlite")
    tenant, user = db.create_tenant("A", "a@example.com")
    auth = AuthService(db)
    principal = auth.authenticate(auth.issue_key(tenant, user))
    result = AdsAdapterStatusService(db, auth).get(principal)
    assert result["status"] == "blocked"
    assert result["reason_codes"] == [
        "no_amazon_ads_account",
        "adapter_not_installed",
        "write_surface_disabled",
    ]
    assert result["adapter_registered"] is False
    assert result["write_operations"] == []


def test_blocked_without_gate_and_eligible_passed_but_not_installed(tmp_path: Path):
    db, auth, owner, _, account = fixture(tmp_path)
    service = AdsAdapterStatusService(db, auth)
    blocked = service.get(owner, account)
    assert blocked["status"] == "blocked"
    assert "no_capability_gate" in blocked["reason_codes"]
    passed_gate(db, owner.tenant_id, owner.user_id, account)
    eligible = service.get(owner, account)
    assert eligible["status"] == "eligible_not_installed"
    assert eligible["reason_codes"] == [
        "adapter_not_installed",
        "write_surface_disabled",
    ]
    assert eligible["adapter_registered"] is False
    assert eligible["write_operations"] == []
    assert set(eligible) == {
        "status",
        "adapter_registered",
        "write_operations",
        "reason_codes",
        "connector_account_id",
        "gate_id",
        "gate_checked_at",
        "account_updated_at",
        "profile_id",
        "region",
        "evaluated_at",
    }


def test_nonpassed_missing_caps_stale_and_config_change_are_blocked(tmp_path: Path):
    db, auth, owner, _, account = fixture(tmp_path)
    gate, _ = db.create_ads_capability_gate(
        owner.tenant_id, owner.user_id, account, "gate-1", region="na", profile_id="1234567890",
        required_capabilities=REQUIRED_CAPABILITIES, attestation_reference="attest-1",
    )
    db.claim_ads_capability_gate(owner.tenant_id, gate["id"])
    db.finish_ads_capability_gate(owner.tenant_id, gate["id"], status="blocked", observed_capabilities=["lwa"], checks=[], request_ids=[])
    result = AdsAdapterStatusService(db, auth).get(owner, account)
    assert result["status"] == "blocked"
    assert {"gate_not_passed", "required_capabilities_missing"} <= set(result["reason_codes"])
    passed_gate(db, owner.tenant_id, owner.user_id, account)
    db.update_connector_account(owner.tenant_id, account, "profile", {**CONFIG, "profile_id": "9999999999"})
    with db.transaction() as conn:
        conn.execute(
            "UPDATE connector_accounts SET updated_at=? WHERE id=?",
            ("2099-01-01T00:00:00+00:00", account),
        )
    changed = AdsAdapterStatusService(db, auth).get(owner, account)
    assert changed["status"] == "blocked"
    assert {"gate_account_config_mismatch", "gate_stale_account_changed"} <= set(changed["reason_codes"])


def test_expired_and_future_gate_times_are_blocked(tmp_path: Path):
    db, auth, owner, _, account = fixture(tmp_path)
    gate = passed_gate(db, owner.tenant_id, owner.user_id, account)
    service = AdsAdapterStatusService(
        db,
        auth,
        clock=lambda: datetime(2026, 8, 26, tzinfo=timezone.utc),
    )
    with db.transaction() as conn:
        conn.execute(
            "UPDATE ads_capability_gates SET completed_at=? WHERE id=?",
            ("2000-01-01T00:00:00+00:00", gate["id"]),
        )
    assert "gate_expired" in service.get(owner, account)["reason_codes"]
    with db.transaction() as conn:
        conn.execute(
            "UPDATE ads_capability_gates SET completed_at=? WHERE id=?",
            ("2030-01-01T00:00:00+00:00", gate["id"]),
        )
    assert "gate_checked_in_future" in service.get(owner, account)["reason_codes"]


def test_tenant_rbac_and_validation_are_enforced(tmp_path: Path):
    db, auth, owner, viewer, account = fixture(tmp_path)
    service = AdsAdapterStatusService(db, auth)
    assert service.get(viewer, account)["connector_account_id"] == account
    other_tenant, other_user = db.create_tenant("B", "b@example.com")
    other = auth.authenticate(auth.issue_key(other_tenant, other_user))
    with pytest.raises(NotFoundError):
        service.get(other, account)
    with pytest.raises(ValidationError):
        service.get(owner, "")


def test_ads_write_surface_is_absent():
    assert all("amazon_ads" not in operation for operation in ActionService.OPERATIONS)
    assert "amazon_ads.adapter.register" not in ActionService.OPERATIONS


def test_gate_lookup_is_directly_scoped_to_the_selected_account(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    db, auth, owner, _, account = fixture(tmp_path)
    passed_gate(db, owner.tenant_id, owner.user_id, account)

    def bounded_tenant_page_must_not_be_used(*_args, **_kwargs):
        raise AssertionError("adapter status must query the account gate directly")

    monkeypatch.setattr(
        db, "list_ads_capability_gates", bounded_tenant_page_must_not_be_used
    )
    result = AdsAdapterStatusService(db, auth).get(owner, account)
    assert result["status"] == "eligible_not_installed"


def test_ads_adapter_status_http_route_is_read_only_and_validated(tmp_path: Path):
    app = RuntimeApplication(Database(tmp_path / "api.sqlite"))
    bootstrap = app.bootstrap("A", "owner@example.com")
    owner = app.auth.authenticate(bootstrap["api_key"])
    account = app.db.add_connector_account(
        owner.tenant_id, "amazon_ads", "profile", CONFIG
    )

    class Handler(_Handler):
        def __init__(self, path: str):
            self.path = path
            self.headers = Message()
            self.headers["Authorization"] = f"Bearer {bootstrap['api_key']}"
            self.out = None

        @property
        def app(self):
            return app

        def _json(self, status, value, request_id, **kwargs):
            self.out = (status, value)

    status = Handler(
        f"/v1/ads-adapter-status?connector_account_id={account}"
    )
    status.do_GET()
    assert status.out[0] == 200
    assert status.out[1]["connector_account_id"] == account
    assert status.out[1]["adapter_registered"] is False
    invalid = Handler("/v1/ads-adapter-status?unknown=true")
    invalid.do_GET()
    assert invalid.out[0] == 422
