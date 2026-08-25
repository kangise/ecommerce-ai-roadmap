from __future__ import annotations

import io
import re
import subprocess
from email.message import Message
from pathlib import Path

from ecommerce_ai_skills.runtime.api import RuntimeApplication, _Handler
from ecommerce_ai_skills.runtime.storage import Database


ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "ecommerce_ai_skills" / "runtime" / "web"


def test_mission_control_assets_are_real_and_javascript_compiles() -> None:
    html = (WEB / "mission-control.html").read_text(encoding="utf-8")
    script = (WEB / "app.js").read_text(encoding="utf-8")
    styles = (WEB / "styles.css").read_text(encoding="utf-8")
    assert "<script src=\"/app/app.js\" defer>" in html
    assert "<style" not in html and "onclick=" not in html
    assert len(styles) > 1000 and len(script) > 5000
    assert "linear-gradient" not in styles and "radial-gradient" not in styles
    assert "data-view-panel=\"briefing\"" in html
    assert "Agent Brief" in html and "需要你决定" in html
    assert 'data-view-panel="accounts"' in html
    assert 'id="connector-dialog"' in html
    assert "Accounts Center" in html
    assert "Report Recipes" in html
    assert 'id="recipe-dialog"' in html
    assert 'id="recipe-list"' in html
    assert "Sync Activity" in html
    assert 'id="sync-list"' in html
    assert "Metric Observations" in html
    assert 'id="metric-observation-list"' in html
    assert 'id="metric-materialization-list"' in html
    assert "Amazon Ads 准入" in html
    assert 'id="ads-capability-list"' in html
    assert 'id="ads-capability-dialog"' in html
    assert 'id="amazon-ads-connector-fields"' in html
    assert 'id="demo-badge"' in html and 'id="demo-banner"' in html
    assert 'state.me?.tenant_mode === "demo"' in script
    assert 'fetch("/v1/demo-session"' in script
    result = subprocess.run(
        ["node", "--check", str(WEB / "app.js")],
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr


def test_every_static_button_is_wired_to_a_real_action() -> None:
    html = (WEB / "mission-control.html").read_text(encoding="utf-8")
    script = (WEB / "app.js").read_text(encoding="utf-8")
    button_tags = re.findall(r"<button\b[^>]*>", html)
    assert button_tags
    actions = []
    for tag in button_tags:
        match = re.search(r'data-action="([a-z-]+)"', tag)
        assert match, f"visible button has no data-action: {tag}"
        actions.append(match.group(1))
    form_actions = {"upload-evidence", "create-run", "create-schedule", "save-connector", "save-recipe", "run-ads-capability-check"}
    switched = {
        "navigate",
        "select-platform",
        "open-connection",
        "connect",
        "disconnect",
        "refresh",
        "close-dialog",
        "close-dialog",
        "view-json",
        "view-import",
        "view-job",
        "view-action",
        "view-run",
        "execute-run",
        "queue-run",
        "evaluate-run",
        "approve-action",
        "toggle-schedule",
        "open-connector-form",
        "edit-connector",
        "health-check-connector",
        "open-recipe-form",
        "edit-recipe",
        "enqueue-report-sync",
        "view-report-sync",
        "view-metric-observation",
        "materialize-evidence-metrics",
        "retry-metric-materialization",
        "open-ads-capability-form",
        "view-ads-capability-gate",
    }
    form_wiring = {
        "upload-evidence": '$("evidence-form").addEventListener',
        "create-run": '$("run-form").addEventListener',
        "create-schedule": '$("schedule-form").addEventListener',
        "save-connector": '$("connector-form").addEventListener',
        "save-recipe": '$("recipe-form").addEventListener',
        "run-ads-capability-check": '$("ads-capability-form").addEventListener',
    }
    for action in actions:
        assert action in form_actions | switched
        if action in form_actions:
            assert form_wiring[action] in script
        else:
            assert f'case "{action}"' in script
    for endpoint in (
        "/v1/catalog",
        "/v1/briefing",
        "/v1/demo-session",
        "/v1/mission-control",
        "/v1/evidence-imports",
        "/v1/agent-runs",
        "/v1/jobs",
        "/v1/schedules",
        "/v1/audit",
        "/v1/connectors",
        "/health-check",
        "/v1/report-recipes",
        "/v1/report-syncs",
        "/sync",
        "/v1/metric-observations",
        "/v1/metric-materializations",
        "/metric-materialization",
        "/v1/ads-capability-gates",
    ):
        assert endpoint in script
    assert "需要 admin 或 owner 角色" in script
    assert "需要 operator、admin 或 owner 执行健康检查" in script
    assert "需要 operator、admin 或 owner 角色" in script
    assert "recipeCanManage" in script
    assert "recipeSyncAvailability" in script
    assert '"Idempotency-Key": idempotency("ui-report-sync")' in script
    assert '"Idempotency-Key": idempotency("ui-metric-materialization")' in script
    assert "L3 Worker" in script
    assert "metricCanMaterialize" in script
    assert "metric_materialization_report_types" in script
    assert "该报告类型尚无指标映射" in script
    assert "metric.series_id || metric.key" in script
    assert "adsCapabilityCanRun" in script
    assert '"Idempotency-Key": idempotency("ui-ads-capability")' in script
    assert "这是管理员提供的外部批准引用" in html
    assert "阻塞原因" in script
    assert "完整历史可通过 API 分页查看" in script
    assert "Metric 来源与质量" in script
    assert "value_decimal ?? observation.value" in script
    assert 'case "materialize-evidence-metrics"' in script
    assert "指标物化结果已刷新。" in script


def test_runtime_serves_ui_with_security_headers_and_live_catalog(tmp_path: Path) -> None:
    app = RuntimeApplication(Database(tmp_path / "runtime.sqlite"))
    bootstrap = app.bootstrap("A", "owner@example.com")

    class StaticHandler(_Handler):
        def __init__(self, path: str):
            self.path = path
            self.headers = Message()
            self.status = None
            self.response_headers = {}
            self.wfile = io.BytesIO()

        @property
        def app(self):
            return app

        def send_response(self, status, *args):
            self.status = status

        def send_header(self, name, value):
            self.response_headers[name] = value

        def end_headers(self):
            pass

    handler = StaticHandler("/app")
    handler.do_GET()
    assert handler.status == 200
    assert b"Commerce Agent OS" in handler.wfile.getvalue()
    assert "script-src 'self'" in handler.response_headers["Content-Security-Policy"]
    assert handler.response_headers["Cache-Control"] == "no-store"

    icon_handler = StaticHandler("/app/assets/icons/house.svg")
    icon_handler.do_GET()
    assert icon_handler.status == 200
    assert icon_handler.response_headers["Content-Type"] == "image/svg+xml"
    assert b"<svg" in icon_handler.wfile.getvalue()

    class CatalogHandler(_Handler):
        def __init__(self):
            self.path = "/v1/catalog"
            self.headers = Message()
            self.headers["Authorization"] = f"Bearer {bootstrap['api_key']}"
            self.out = None

        @property
        def app(self):
            return app

        def _json(self, status, value, request_id, **kwargs):
            self.out = (status, value)

    catalog = CatalogHandler()
    catalog.do_GET()
    assert catalog.out[0] == 200
    assert len(catalog.out[1]["platforms"]) == 15
    assert "amazon_business_report" in catalog.out[1]["report_types"]
    assert "amazon_spapi.import_report" in catalog.out[1]["action_operations"]
    assert "amazon_business_report" in catalog.out[1][
        "metric_materialization_report_types"
    ]
