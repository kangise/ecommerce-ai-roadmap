from __future__ import annotations

import io
import json
from email.message import Message
from pathlib import Path
from typing import Any, Callable
from urllib.error import HTTPError

import pytest

from ecommerce_ai_skills.runtime.accounts import MarketplaceAccountService
from ecommerce_ai_skills.runtime.agents import OpenAIResponsesProvider
from ecommerce_ai_skills.runtime.api import RuntimeApplication, _Handler
from ecommerce_ai_skills.runtime.auth import AuthService
from ecommerce_ai_skills.runtime.errors import (
    AuthorizationError,
    ConflictError,
    NotFoundError,
    RateLimitError,
    ValidationError,
)
from ecommerce_ai_skills.runtime.provider_smoke import ProviderSmokeService
from ecommerce_ai_skills.runtime.storage import Database


OPENAI_KEY = "sk-fixture-provider-smoke-never-persist"
OPENAI_MODEL = "gpt-fixture-smoke"
RAW_OUTPUT = "fixture-model-output-never-persist"
RAW_BODY_SECRET = "fixture-provider-body-never-persist"
SHOPIFY_TOKEN = "shpat_fixture-never-persist"
AMAZON_CLIENT_SECRET = "amazon-client-secret-never-persist"
AMAZON_REFRESH_TOKEN = "amazon-refresh-token-never-persist"

AMAZON_CONFIG = {
    "region": "na",
    "marketplace_ids": ["ATVPDKIKX0DER"],
    "lwa_client_id_ref": "AMAZON_CLIENT_ID",
    "lwa_client_secret_ref": "AMAZON_CLIENT_SECRET",
    "lwa_refresh_token_ref": "AMAZON_REFRESH_TOKEN",
}
SHOPIFY_CONFIG = {
    "shop_domain": "fixture.myshopify.com",
    "api_version": "2025-10",
    "credential_ref": "SHOPIFY_TOKEN",
}
SAFE_FIELDS = {
    "id",
    "tenant_id",
    "provider",
    "connector_account_id",
    "created_by",
    "status",
    "provider_request_id",
    "provider_status",
    "http_status",
    "retry_after_seconds",
    "latency_ms",
    "error_code",
    "created_at",
    "completed_at",
}


class FixtureResponse:
    def __init__(
        self,
        value: Any = None,
        *,
        raw: bytes | None = None,
        status: int = 200,
        headers: dict[str, str] | None = None,
        url: str = "https://fixture.invalid/",
    ):
        self.body = raw if raw is not None else json.dumps(value).encode("utf-8")
        self.status = status
        self.headers = headers or {}
        self.url = url
        self.read_sizes: list[int] = []

    def __enter__(self) -> "FixtureResponse":
        return self

    def __exit__(self, *_args: Any) -> bool:
        return False

    def read(self, size: int = -1) -> bytes:
        self.read_sizes.append(size)
        return self.body if size < 0 else self.body[:size]

    def geturl(self) -> str:
        return self.url


def _no_network(*_args: Any, **_kwargs: Any) -> Any:
    raise AssertionError("provider smoke tests must never use the network")


def _completed_transport(
    seen: dict[str, Any] | None = None,
) -> Callable[..., FixtureResponse]:
    calls = seen if seen is not None else {}

    def transport(request: Any, timeout: int) -> FixtureResponse:
        calls["count"] = calls.get("count", 0) + 1
        calls["url"] = request.full_url
        calls["authorization"] = request.get_header("Authorization")
        calls["headers"] = dict(request.header_items())
        calls["timeout"] = timeout
        calls["body"] = json.loads(request.data.decode("utf-8"))
        response = FixtureResponse(
            {
                "id": "resp_body_fallback",
                "status": "completed",
                "output": [{"type": "output_text", "text": RAW_OUTPUT}],
                "raw_secret": RAW_BODY_SECRET,
            },
            headers={"x-request-id": "req_live_123"},
            url=request.full_url,
        )
        calls["response"] = response
        return response

    return transport


def _runtime(
    tmp_path: Path,
    provider: OpenAIResponsesProvider | None = None,
) -> tuple[RuntimeApplication, dict[str, Any], dict[str, Any], dict[str, str]]:
    app = RuntimeApplication(
        Database(tmp_path / "runtime.sqlite"),
        provider_smoke_openai_provider=provider
        or OpenAIResponsesProvider(environ={}, transport=_no_network),
    )
    boot = app.bootstrap("Tenant A", "owner-a@example.com")
    principals = {"owner": app.auth.authenticate(boot["api_key"])}
    keys = {"owner": boot["api_key"]}
    for role in ("admin", "operator", "viewer"):
        user_id = app.db.create_user(boot["tenant_id"], f"{role}@example.com", role)
        keys[role] = app.auth.issue_key(boot["tenant_id"], user_id)
        principals[role] = app.auth.authenticate(keys[role])
    return app, boot, principals, keys


def _execute_openai(
    app: RuntimeApplication,
    principal: Any,
    key: str = "smoke-openai-1",
) -> dict[str, Any]:
    return app.provider_smoke.execute(
        principal,
        provider="openai",
        idempotency_key=key,
        request_id=f"request-{key}",
    )


@pytest.mark.parametrize(
    ("environment", "error_code"),
    [
        ({}, "missing_credential"),
        ({"OPENAI_API_KEY": OPENAI_KEY}, "missing_configuration"),
    ],
)
def test_openai_missing_key_or_model_is_blocked_without_network(
    tmp_path: Path,
    environment: dict[str, str],
    error_code: str,
) -> None:
    calls = 0

    def transport(*_args: Any, **_kwargs: Any) -> Any:
        nonlocal calls
        calls += 1
        raise AssertionError("missing configuration must block before transport")

    provider = OpenAIResponsesProvider(environ=environment, transport=transport)
    app, _, principals, _ = _runtime(tmp_path, provider)
    result = _execute_openai(app, principals["operator"])
    assert calls == 0
    assert result["status"] == "blocked"
    assert result["provider_status"] == "misconfigured"
    assert result["error_code"] == error_code
    assert result["http_status"] is None
    assert set(result) == SAFE_FIELDS
    persisted = app.db.get_provider_smoke_test(result["tenant_id"], result["id"])
    audit = app.db.list_audit(result["tenant_id"])
    assert OPENAI_KEY not in json.dumps([result, persisted, audit])


def test_openai_live_fixture_uses_fixed_minimal_request_and_persists_only_safe_metadata(
    tmp_path: Path,
) -> None:
    seen: dict[str, Any] = {}
    provider = OpenAIResponsesProvider(
        environ={"OPENAI_API_KEY": OPENAI_KEY, "EAI_OPENAI_MODEL": OPENAI_MODEL},
        transport=_completed_transport(seen),
        timeout_seconds=120,
    )
    app, boot, principals, _ = _runtime(tmp_path, provider)
    result = _execute_openai(app, principals["operator"])

    assert result["status"] == "succeeded"
    assert result["provider_status"] == "completed"
    assert result["http_status"] == 200
    assert result["provider_request_id"] == "req_live_123"
    assert result["retry_after_seconds"] is None
    assert result["error_code"] is None
    assert set(result) == SAFE_FIELDS
    assert seen["count"] == 1
    assert seen["url"] == "https://api.openai.com/v1/responses"
    assert seen["authorization"] == f"Bearer {OPENAI_KEY}"
    assert seen["timeout"] == 15
    assert seen["body"] == {
        "model": OPENAI_MODEL,
        "input": "Reply OK.",
        "store": False,
        "max_output_tokens": 16,
    }
    assert "tools" not in seen["body"]
    assert OPENAI_KEY not in json.dumps(seen["body"])
    assert seen["response"].read_sizes == [65_537]

    with app.db.connect() as conn:
        columns = {
            row["name"] for row in conn.execute("PRAGMA table_info(provider_smoke_tests)")
        }
        stored = dict(
            conn.execute(
                "SELECT * FROM provider_smoke_tests WHERE tenant_id=? AND id=?",
                (boot["tenant_id"], result["id"]),
            ).fetchone()
        )
    assert not ({"request_body", "response_body", "output", "api_key"} & columns)
    smoke_audit = next(
        event
        for event in app.db.list_audit(boot["tenant_id"])
        if event["action"] == "provider_smoke.execute"
    )
    assert smoke_audit["outcome"] == "succeeded"
    assert smoke_audit["metadata"] == {
        "latency_ms": result["latency_ms"],
        "provider": "openai",
        "status": "succeeded",
    }
    persisted_surface = json.dumps(
        [result, stored, smoke_audit], ensure_ascii=False, sort_keys=True
    )
    for secret in (OPENAI_KEY, RAW_OUTPUT, RAW_BODY_SECRET):
        assert secret not in persisted_surface
        assert secret.encode("utf-8") not in app.db.path.read_bytes()
    assert app.db.verify_audit_chain(boot["tenant_id"])["valid"] is True


def test_openai_two_xx_incomplete_response_is_a_safe_failure(tmp_path: Path) -> None:
    provider = OpenAIResponsesProvider(
        environ={"OPENAI_API_KEY": OPENAI_KEY, "EAI_OPENAI_MODEL": OPENAI_MODEL},
        transport=lambda request, timeout: FixtureResponse(
            {"id": "resp_incomplete", "status": "incomplete", "output": [RAW_OUTPUT]},
            status=202,
            headers={"x-request-id": "req_incomplete"},
            url=request.full_url,
        ),
    )
    app, _, principals, _ = _runtime(tmp_path, provider)
    result = _execute_openai(app, principals["operator"])
    assert result["status"] == "failed"
    assert result["provider_status"] == "incomplete"
    assert result["http_status"] == 202
    assert result["error_code"] == "provider_response_incomplete"
    assert RAW_OUTPUT not in json.dumps(result)


@pytest.mark.parametrize(
    ("status", "expected_code"),
    [(401, "invalid_credential"), (403, "permission_denied"), (404, "model_not_found")],
)
def test_openai_auth_and_model_http_failures_are_safe_blockers(
    tmp_path: Path,
    status: int,
    expected_code: str,
) -> None:
    def transport(request: Any, timeout: int) -> Any:
        del timeout
        raise HTTPError(
            request.full_url,
            status,
            "raw-provider-error-containing-secret",
            {"x-request-id": f"req_{status}"},
            io.BytesIO(RAW_BODY_SECRET.encode("utf-8")),
        )

    provider = OpenAIResponsesProvider(
        environ={"OPENAI_API_KEY": OPENAI_KEY, "EAI_OPENAI_MODEL": OPENAI_MODEL},
        transport=transport,
    )
    app, _, principals, _ = _runtime(tmp_path, provider)
    result = _execute_openai(app, principals["operator"])
    assert result["status"] == "blocked"
    assert result["http_status"] == status
    assert result["provider_status"] == f"http_{status}"
    assert result["provider_request_id"] == f"req_{status}"
    assert result["error_code"] == expected_code
    assert RAW_BODY_SECRET not in json.dumps(result)


def test_openai_rate_limit_preserves_bounded_retry_after(tmp_path: Path) -> None:
    def transport(request: Any, timeout: int) -> Any:
        del timeout
        raise HTTPError(
            request.full_url,
            429,
            "rate limited",
            {"Retry-After": "37", "x-request-id": "req_rate"},
            io.BytesIO(b"{}"),
        )

    provider = OpenAIResponsesProvider(
        environ={"OPENAI_API_KEY": OPENAI_KEY, "EAI_OPENAI_MODEL": OPENAI_MODEL},
        transport=transport,
    )
    app, _, principals, _ = _runtime(tmp_path, provider)
    result = _execute_openai(app, principals["operator"])
    assert result["status"] == "failed"
    assert result["error_code"] == "rate_limited"
    assert result["retry_after_seconds"] == 37
    assert result["http_status"] == 429


@pytest.mark.parametrize(
    ("transport", "provider_status", "error_code", "http_status"),
    [
        (
            lambda request, timeout: (_ for _ in ()).throw(TimeoutError("secret timeout")),
            "timeout",
            "provider_timeout",
            None,
        ),
        (
            lambda request, timeout: FixtureResponse(
                raw=b"not-json", status=200, headers={"x-request-id": "req_json"}
            ),
            "invalid_json",
            "invalid_provider_response",
            200,
        ),
        (
            lambda request, timeout: FixtureResponse(
                raw=b"x" * 65_537,
                status=200,
                headers={"x-request-id": "req_large"},
            ),
            "response_too_large",
            "invalid_provider_response",
            200,
        ),
    ],
)
def test_openai_timeout_invalid_json_and_oversize_are_safe_failures(
    tmp_path: Path,
    transport: Callable[..., Any],
    provider_status: str,
    error_code: str,
    http_status: int | None,
) -> None:
    provider = OpenAIResponsesProvider(
        environ={"OPENAI_API_KEY": OPENAI_KEY, "EAI_OPENAI_MODEL": OPENAI_MODEL},
        transport=transport,
    )
    app, _, principals, _ = _runtime(tmp_path, provider)
    result = _execute_openai(app, principals["operator"])
    assert result["status"] == "failed"
    assert result["provider_status"] == provider_status
    assert result["error_code"] == error_code
    assert result["http_status"] == http_status
    assert set(result) == SAFE_FIELDS


def test_amazon_and_shopify_reuse_real_health_adapters_and_update_connector_health(
    tmp_path: Path,
) -> None:
    app, boot, principals, _ = _runtime(tmp_path)
    app.accounts.environ = {
        "AMAZON_CLIENT_ID": "amazon-client-id",
        "AMAZON_CLIENT_SECRET": AMAZON_CLIENT_SECRET,
        "AMAZON_REFRESH_TOKEN": AMAZON_REFRESH_TOKEN,
        "SHOPIFY_TOKEN": SHOPIFY_TOKEN,
    }
    amazon_calls: list[tuple[str, str, int]] = []
    shopify_calls: list[tuple[str, str | None, int]] = []

    def amazon_transport(request: Any, timeout: int) -> FixtureResponse:
        amazon_calls.append((request.method, request.full_url, timeout))
        if request.full_url == "https://api.amazon.com/auth/o2/token":
            return FixtureResponse(
                {"access_token": "amazon-access-token-never-persist"},
                url=request.full_url,
            )
        assert request.get_header("X-amz-access-token") == "amazon-access-token-never-persist"
        return FixtureResponse(
            {
                "payload": {
                    "marketplaceParticipations": [
                        {"marketplace": {"id": "ATVPDKIKX0DER"}}
                    ]
                }
            },
            headers={"x-amzn-requestid": "amazon_req_1"},
            url=request.full_url,
        )

    def shopify_transport(request: Any, timeout: int) -> FixtureResponse:
        shopify_calls.append(
            (request.full_url, request.get_header("X-shopify-access-token"), timeout)
        )
        return FixtureResponse(
            {"shop": {"id": 123}},
            headers={"x-shopify-request-id": "shopify_req_1"},
            url=request.full_url,
        )

    app.accounts.amazon_transport = amazon_transport
    app.accounts.shopify_transport = shopify_transport
    amazon = app.accounts.create(
        principals["owner"], "amazon_spapi", "seller-a", AMAZON_CONFIG, "create-amazon"
    )
    shopify = app.accounts.create(
        principals["owner"], "shopify", "shop-a", SHOPIFY_CONFIG, "create-shopify"
    )
    amazon_result = app.provider_smoke.execute(
        principals["operator"],
        provider="amazon_spapi",
        connector_account_id=amazon["id"],
        idempotency_key="amazon-smoke-1",
        request_id="request-amazon-smoke",
    )
    shopify_result = app.provider_smoke.execute(
        principals["operator"],
        provider="shopify",
        connector_account_id=shopify["id"],
        idempotency_key="shopify-smoke-1",
        request_id="request-shopify-smoke",
    )

    assert amazon_result["status"] == "succeeded"
    assert amazon_result["provider_request_id"] == "amazon_req_1"
    assert shopify_result["status"] == "succeeded"
    assert shopify_result["provider_request_id"] == "shopify_req_1"
    assert app.db.get_connector_account(boot["tenant_id"], amazon["id"])["health_status"] == "healthy"
    assert app.db.get_connector_account(boot["tenant_id"], shopify["id"])["health_status"] == "healthy"
    assert amazon_calls == [
        ("POST", "https://api.amazon.com/auth/o2/token", 30),
        (
            "GET",
            "https://sellingpartnerapi-na.amazon.com/sellers/v1/marketplaceParticipations",
            30,
        ),
    ]
    assert shopify_calls == [
        (
            "https://fixture.myshopify.com/admin/api/2025-10/shop.json",
            SHOPIFY_TOKEN,
            30,
        )
    ]
    persisted = json.dumps(
        [
            amazon_result,
            shopify_result,
            app.db.list_audit(boot["tenant_id"]),
            app.db.list_provider_smoke_tests(boot["tenant_id"]),
        ],
        sort_keys=True,
    )
    for secret in (
        AMAZON_CLIENT_SECRET,
        AMAZON_REFRESH_TOKEN,
        "amazon-access-token-never-persist",
        SHOPIFY_TOKEN,
    ):
        assert secret not in persisted
    assert app.db.verify_audit_chain(boot["tenant_id"])["valid"] is True


def test_rbac_tenant_isolation_and_provider_account_validation(tmp_path: Path) -> None:
    provider = OpenAIResponsesProvider(
        environ={"OPENAI_API_KEY": OPENAI_KEY, "EAI_OPENAI_MODEL": OPENAI_MODEL},
        transport=_completed_transport(),
    )
    app, boot_a, principals, _ = _runtime(tmp_path, provider)
    shopify = app.accounts.create(
        principals["owner"], "shopify", "shop-a", SHOPIFY_CONFIG, "create-shopify"
    )
    created = _execute_openai(app, principals["operator"])
    with pytest.raises(AuthorizationError):
        _execute_openai(app, principals["viewer"], "viewer-smoke")

    boot_b = app.bootstrap("Tenant B", "owner-b@example.com")
    operator_b_id = app.db.create_user(boot_b["tenant_id"], "operator-b@example.com", "operator")
    operator_b = app.auth.authenticate(app.auth.issue_key(boot_b["tenant_id"], operator_b_id))
    with pytest.raises(NotFoundError):
        app.provider_smoke.get(operator_b, created["id"])
    with pytest.raises(NotFoundError):
        app.provider_smoke.execute(
            operator_b,
            provider="shopify",
            connector_account_id=shopify["id"],
            idempotency_key="cross-tenant",
            request_id="cross-tenant",
        )
    assert app.db.list_provider_smoke_tests(boot_b["tenant_id"]) == []

    with pytest.raises(ValidationError, match="does not match"):
        app.provider_smoke.execute(
            principals["operator"],
            provider="amazon_spapi",
            connector_account_id=shopify["id"],
            idempotency_key="mismatch",
            request_id="mismatch",
        )
    with pytest.raises(ValidationError, match="must not be supplied"):
        app.provider_smoke.execute(
            principals["operator"],
            provider="openai",
            connector_account_id=shopify["id"],
            idempotency_key="openai-account",
            request_id="openai-account",
        )
    with pytest.raises(ValidationError, match="provider must be"):
        app.provider_smoke.execute(
            principals["operator"],
            provider="amazon_ads",
            idempotency_key="unsupported",
            request_id="unsupported",
        )
    with pytest.raises(ValidationError, match="Idempotency-Key"):
        app.provider_smoke.execute(
            principals["operator"],
            provider="openai",
            idempotency_key=f"unsafe {OPENAI_KEY}",
            request_id="unsafe-key",
        )
    assert app.db.list_provider_smoke_tests(boot_a["tenant_id"])[0]["id"] == created["id"]


def test_idempotent_replay_does_not_call_provider_twice_and_changed_target_conflicts(
    tmp_path: Path,
) -> None:
    seen: dict[str, Any] = {}
    provider = OpenAIResponsesProvider(
        environ={"OPENAI_API_KEY": OPENAI_KEY, "EAI_OPENAI_MODEL": OPENAI_MODEL},
        transport=_completed_transport(seen),
    )
    app, _, principals, _ = _runtime(tmp_path, provider)
    shopify = app.accounts.create(
        principals["owner"], "shopify", "shop-a", SHOPIFY_CONFIG, "create-shopify"
    )
    first = _execute_openai(app, principals["operator"], "same-key")
    replay = _execute_openai(app, principals["operator"], "same-key")
    assert replay == first
    assert seen["count"] == 1
    assert not ({"idempotency_key", "request_fingerprint", "lease_token", "attempt_count"} & set(replay))
    with pytest.raises(ConflictError, match="another provider smoke target"):
        app.provider_smoke.execute(
            principals["operator"],
            provider="shopify",
            connector_account_id=shopify["id"],
            idempotency_key="same-key",
            request_id="changed-target",
        )
    assert seen["count"] == 1


def test_cooldown_returns_retry_after_without_a_second_provider_call(tmp_path: Path) -> None:
    seen: dict[str, Any] = {}
    provider = OpenAIResponsesProvider(
        environ={"OPENAI_API_KEY": OPENAI_KEY, "EAI_OPENAI_MODEL": OPENAI_MODEL},
        transport=_completed_transport(seen),
    )
    app, _, principals, _ = _runtime(tmp_path, provider)
    _execute_openai(app, principals["operator"], "cooldown-first")
    with pytest.raises(RateLimitError) as caught:
        _execute_openai(app, principals["operator"], "cooldown-second")
    assert 1 <= caught.value.retry_after <= 30
    assert seen["count"] == 1


def test_expired_lease_is_reclaimed_and_old_attempt_is_fenced(tmp_path: Path) -> None:
    app, boot, principals, _ = _runtime(tmp_path)
    fingerprint = ProviderSmokeService._fingerprint("openai", None)
    first, replay, old_token = app.db.reserve_provider_smoke_test(
        boot["tenant_id"],
        principals["operator"].user_id,
        "openai",
        None,
        "lease-reclaim",
        fingerprint,
    )
    assert replay is False and old_token
    with app.db.transaction() as conn:
        conn.execute(
            "UPDATE provider_smoke_tests SET lease_until='2000-01-01T00:00:00+00:00' WHERE id=?",
            (first["id"],),
        )
    reclaimed, replay, new_token = app.db.reserve_provider_smoke_test(
        boot["tenant_id"],
        principals["operator"].user_id,
        "openai",
        None,
        "lease-reclaim",
        fingerprint,
    )
    assert replay is False
    assert reclaimed["id"] == first["id"]
    assert reclaimed["attempt_count"] == 2
    assert new_token and new_token != old_token
    with pytest.raises(ConflictError, match="lease is no longer active"):
        app.db.complete_provider_smoke_test(
            boot["tenant_id"],
            first["id"],
            lease_token=old_token,
            actor_user_id=principals["operator"].user_id,
            request_id="old-attempt",
            status="succeeded",
            provider_request_id="old_request",
            provider_status="completed",
            http_status=200,
            retry_after_seconds=None,
            latency_ms=1,
            error_code=None,
        )
    completed = app.db.complete_provider_smoke_test(
        boot["tenant_id"],
        first["id"],
        lease_token=new_token,
        actor_user_id=principals["operator"].user_id,
        request_id="new-attempt",
        status="succeeded",
        provider_request_id="new_request",
        provider_status="completed",
        http_status=200,
        retry_after_seconds=None,
        latency_ms=2,
        error_code=None,
    )
    assert completed["status"] == "succeeded"
    assert completed["attempt_count"] == 2
    assert completed["provider_request_id"] == "new_request"
    assert app.db.verify_audit_chain(boot["tenant_id"])["valid"] is True


def test_list_get_limit_and_persistence_expose_only_safe_fields(tmp_path: Path) -> None:
    app, boot, principals, _ = _runtime(tmp_path)
    amazon_id = app.db.add_connector_account(
        boot["tenant_id"], "amazon_spapi", "seller-a", AMAZON_CONFIG
    )
    shopify_id = app.db.add_connector_account(
        boot["tenant_id"], "shopify", "shop-a", SHOPIFY_CONFIG
    )
    targets = [
        ("openai", None),
        ("amazon_spapi", amazon_id),
        ("shopify", shopify_id),
    ]
    created_ids = set()
    for index, (provider, account_id) in enumerate(targets, 1):
        row, replay, lease_token = app.db.reserve_provider_smoke_test(
            boot["tenant_id"],
            principals["operator"].user_id,
            provider,
            account_id,
            f"persist-{index}",
            ProviderSmokeService._fingerprint(provider, account_id),
        )
        assert replay is False and lease_token
        completed = app.db.complete_provider_smoke_test(
            boot["tenant_id"],
            row["id"],
            lease_token=lease_token,
            actor_user_id=principals["operator"].user_id,
            request_id=f"persist-{index}",
            status="succeeded",
            provider_request_id=f"request_{index}",
            provider_status="completed" if provider == "openai" else "healthy",
            http_status=200 if provider == "openai" else None,
            retry_after_seconds=None,
            latency_ms=index,
            error_code=None,
        )
        created_ids.add(completed["id"])

    reopened = Database(app.db.path)
    service = ProviderSmokeService(
        reopened,
        AuthService(reopened),
        MarketplaceAccountService(reopened, AuthService(reopened)),
        openai_provider=OpenAIResponsesProvider(environ={}, transport=_no_network),
    )
    listed = service.list(principals["viewer"], limit=2)
    assert len(listed) == 2
    assert set(listed[0]) == SAFE_FIELDS
    assert {item["id"] for item in listed} <= created_ids
    detail = service.get(principals["viewer"], next(iter(created_ids)))
    assert detail["id"] in created_ids
    assert set(detail) == SAFE_FIELDS


class ProviderSmokeHandler(_Handler):
    def __init__(
        self,
        app: RuntimeApplication,
        method: str,
        path: str,
        api_key: str | None,
        *,
        body: dict[str, Any] | None = None,
        idempotency_key: str | None = None,
    ):
        self._app = app
        self.path = path
        self.headers = Message()
        if api_key is not None:
            self.headers["Authorization"] = f"Bearer {api_key}"
        if idempotency_key is not None:
            self.headers["Idempotency-Key"] = idempotency_key
        self.client_address = ("provider-smoke-test", 1)
        self.body = body or {}
        self.method = method
        self.out: tuple[int, dict[str, Any], dict[str, Any]] | None = None

    @property
    def app(self) -> RuntimeApplication:
        return self._app

    def _body(self) -> dict[str, Any]:
        return self.body

    def _json(
        self,
        status: int,
        value: dict[str, Any],
        request_id: str,
        **kwargs: Any,
    ) -> None:
        self.out = (status, value, {"request_id": request_id, **kwargs})

    def run(self) -> tuple[int, dict[str, Any], dict[str, Any]]:
        getattr(self, f"do_{self.method}")()
        assert self.out is not None
        return self.out


def test_provider_smoke_http_status_headers_strict_body_rbac_and_tenant_scope(
    tmp_path: Path,
) -> None:
    seen: dict[str, Any] = {}
    provider = OpenAIResponsesProvider(
        environ={"OPENAI_API_KEY": OPENAI_KEY, "EAI_OPENAI_MODEL": OPENAI_MODEL},
        transport=_completed_transport(seen),
    )
    app, _, principals, keys = _runtime(tmp_path, provider)
    shopify = app.accounts.create(
        principals["owner"], "shopify", "shop-a", SHOPIFY_CONFIG, "create-shopify"
    )
    unauthorized = ProviderSmokeHandler(
        app, "GET", "/v1/provider-smoke-tests", None
    ).run()
    assert unauthorized[0] == 401
    forbidden = ProviderSmokeHandler(
        app,
        "POST",
        "/v1/provider-smoke-tests",
        keys["viewer"],
        body={"provider": "openai"},
        idempotency_key="viewer-post",
    ).run()
    assert forbidden[0] == 403

    missing_header = ProviderSmokeHandler(
        app,
        "POST",
        "/v1/provider-smoke-tests",
        keys["operator"],
        body={"provider": "openai"},
    ).run()
    assert missing_header[0] == 422
    secret_value = "secret-body-value-never-echo"
    unknown_secret = ProviderSmokeHandler(
        app,
        "POST",
        "/v1/provider-smoke-tests",
        keys["operator"],
        body={"provider": "openai", "api_key": secret_value},
        idempotency_key="unknown-secret",
    ).run()
    assert unknown_secret[0] == 422
    assert secret_value not in json.dumps(unknown_secret)
    mismatch = ProviderSmokeHandler(
        app,
        "POST",
        "/v1/provider-smoke-tests",
        keys["operator"],
        body={"provider": "amazon_spapi", "connector_account_id": shopify["id"]},
        idempotency_key="mismatch-api",
    ).run()
    assert mismatch[0] == 422
    invalid_provider = ProviderSmokeHandler(
        app,
        "POST",
        "/v1/provider-smoke-tests",
        keys["operator"],
        body={"provider": "amazon_ads"},
        idempotency_key="invalid-provider",
    ).run()
    assert invalid_provider[0] == 422

    created = ProviderSmokeHandler(
        app,
        "POST",
        "/v1/provider-smoke-tests",
        keys["operator"],
        body={"provider": "openai"},
        idempotency_key="http-create",
    ).run()
    assert created[0] == 201
    assert set(created[1]) == SAFE_FIELDS
    listed = ProviderSmokeHandler(
        app, "GET", "/v1/provider-smoke-tests?limit=1", keys["viewer"]
    ).run()
    assert listed[0] == 200
    assert listed[1]["provider_smoke_tests"] == [created[1]]
    detail = ProviderSmokeHandler(
        app,
        "GET",
        f"/v1/provider-smoke-tests/{created[1]['id']}",
        keys["viewer"],
    ).run()
    assert detail[0] == 200 and detail[1] == created[1]
    bad_limit = ProviderSmokeHandler(
        app, "GET", "/v1/provider-smoke-tests?limit=0", keys["viewer"]
    ).run()
    assert bad_limit[0] == 422
    bad_query = ProviderSmokeHandler(
        app, "GET", "/v1/provider-smoke-tests?provider=openai", keys["viewer"]
    ).run()
    assert bad_query[0] == 422

    boot_b = app.bootstrap("Tenant B", "owner-b@example.com")
    cross_tenant = ProviderSmokeHandler(
        app,
        "GET",
        f"/v1/provider-smoke-tests/{created[1]['id']}",
        boot_b["api_key"],
    ).run()
    assert cross_tenant[0] == 404

    cooldown = ProviderSmokeHandler(
        app,
        "POST",
        "/v1/provider-smoke-tests",
        keys["operator"],
        body={"provider": "openai"},
        idempotency_key="http-cooldown",
    ).run()
    assert cooldown[0] == 429
    retry_after = cooldown[2]["extra_headers"]["Retry-After"]
    assert retry_after.isdigit() and 1 <= int(retry_after) <= 30
    assert seen["count"] == 1


def test_v21_migration_creates_empty_provider_smoke_ledger_and_guards(
    tmp_path: Path,
) -> None:
    path = tmp_path / "runtime.sqlite"
    db = Database(path)
    with db.transaction() as conn:
        conn.execute("DROP TABLE provider_smoke_tests")
        conn.execute("UPDATE runtime_meta SET value='21' WHERE key='schema_version'")
    migrated = Database(path)
    assert migrated.readiness()["schema_version"] == 22
    with migrated.connect() as conn:
        assert conn.execute("SELECT COUNT(*) FROM provider_smoke_tests").fetchone()[0] == 0
        triggers = {
            row["name"]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='trigger' AND name LIKE 'provider_smoke_tests_%'"
            )
        }
    assert triggers == {
        "provider_smoke_tests_actor_insert",
        "provider_smoke_tests_connector_insert",
        "provider_smoke_tests_initial_insert",
        "provider_smoke_tests_terminal_transition",
        "provider_smoke_tests_lease_reclaim",
        "provider_smoke_tests_identity_update",
        "provider_smoke_tests_terminal_update",
        "provider_smoke_tests_delete",
    }


def test_openapi_provider_smoke_contract_is_strict_and_complete() -> None:
    import yaml

    document = yaml.safe_load(
        (Path(__file__).resolve().parents[1] / "openapi" / "runtime-api.yaml").read_text(
            encoding="utf-8"
        )
    )
    collection = document["paths"]["/v1/provider-smoke-tests"]
    detail = document["paths"]["/v1/provider-smoke-tests/{smokeTestId}"]
    assert set(collection) == {"get", "post"}
    assert set(detail) == {"get"}
    assert set(collection["post"]["responses"]) == {
        "201",
        "401",
        "403",
        "404",
        "409",
        "422",
        "429",
    }
    assert collection["post"]["parameters"] == [
        {"$ref": "#/components/parameters/providerSmokeIdempotencyKey"}
    ]
    assert detail["get"]["parameters"] == [
        {"$ref": "#/components/parameters/smokeTestId"}
    ]
    schemas = document["components"]["schemas"]
    request = schemas["ProviderSmokeRequest"]
    assert request["oneOf"] == [
        {"$ref": "#/components/schemas/OpenAIProviderSmokeRequest"},
        {"$ref": "#/components/schemas/MarketplaceProviderSmokeRequest"},
    ]
    openai_request = schemas["OpenAIProviderSmokeRequest"]
    marketplace_request = schemas["MarketplaceProviderSmokeRequest"]
    assert openai_request["additionalProperties"] is False
    assert openai_request["required"] == ["provider"]
    assert set(openai_request["properties"]) == {"provider"}
    assert marketplace_request["additionalProperties"] is False
    assert marketplace_request["required"] == ["provider", "connector_account_id"]
    assert marketplace_request["properties"]["provider"]["enum"] == [
        "amazon_spapi",
        "shopify",
    ]
    smoke_key = document["components"]["parameters"]["providerSmokeIdempotencyKey"]
    assert smoke_key["name"] == "Idempotency-Key"
    assert smoke_key["required"] is True
    assert smoke_key["schema"]["pattern"] == "^[A-Za-z0-9][A-Za-z0-9._:-]{0,199}$"
    assert schemas["ProviderSmokeProvider"]["enum"] == [
        "openai",
        "amazon_spapi",
        "shopify",
    ]
    response = schemas["ProviderSmokeTest"]
    assert response["additionalProperties"] is False
    assert set(response["required"]) == SAFE_FIELDS
    assert response["properties"]["status"]["enum"] == [
        "running",
        "succeeded",
        "failed",
        "blocked",
    ]
    assert not (
        {
            "idempotency_key",
            "request_fingerprint",
            "request_body",
            "response_body",
            "output",
            "lease_token",
            "api_key",
        }
        & set(response["properties"])
    )
