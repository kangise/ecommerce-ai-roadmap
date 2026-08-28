"""The MCP -> runtime bridge.

The knowledge tools can say what to do about a 40% ACOS; only the runtime knows
what the ACOS actually is. These tests pin the two properties that make joining
them safe: the ops surface is read-only, and an unconfigured bridge disappears
instead of failing in a client.
"""

from __future__ import annotations

import json
import urllib.error

import pytest


ROOT_DIST = "dist"


@pytest.fixture()
def server_factory(mcp_server_module):
    def build(url: str = "", api_key: str = ""):
        bridge = mcp_server_module.RuntimeBridge(url, api_key)
        return mcp_server_module.OPCServer(ROOT_DIST, bridge)
    return build


def tool_names(server) -> list[str]:
    return [t["name"] for t in server.list_tools()]


def test_unconfigured_bridge_hides_ops_tools(server_factory) -> None:
    """Knowledge-only users never set the env vars; they should not see broken tools."""
    names = tool_names(server_factory())
    assert not [n for n in names if n.startswith("opc.ops_")]
    assert "opc.route_query" in names, "knowledge tools must be unaffected"


def test_configured_bridge_adds_ops_tools(server_factory) -> None:
    names = tool_names(server_factory("http://127.0.0.1:1", "eai_test.key"))
    assert {"opc.ops_briefing", "opc.ops_metrics",
            "opc.ops_proposals", "opc.ops_evidence"} <= set(names)


def test_ops_surface_is_read_only(server_factory) -> None:
    """The approval gate is the runtime's core safety property.

    Exposing approve/execute over MCP would hand an LLM the key to the gate that
    exists to keep it out. If someone adds a write tool here, this fails.
    """
    names = tool_names(server_factory("http://127.0.0.1:1", "eai_test.key"))
    forbidden = ("approve", "execute", "create", "delete", "rotate", "update", "run")
    for name in names:
        if not name.startswith("opc.ops_"):
            continue
        assert not any(word in name for word in forbidden), name


def test_ops_tools_take_no_arguments_that_could_reach_the_runtime(server_factory) -> None:
    """Fixed paths only — no caller-supplied path or query is forwarded upstream."""
    server = server_factory("http://127.0.0.1:1", "eai_test.key")
    for tool in server.list_tools():
        if tool["name"].startswith("opc.ops_"):
            assert tool["inputSchema"].get("properties") == {}


def test_unconfigured_call_explains_how_to_configure(server_factory) -> None:
    message = server_factory().call_tool("opc.ops_briefing", {})
    assert "OPC_RUNTIME_URL" in message and "OPC_RUNTIME_API_KEY" in message


def test_payload_is_passed_through_whole(server_factory, monkeypatch, mcp_server_module) -> None:
    """Provenance rides along with every observation; the bridge must not trim it."""
    observation = {
        "metric_key": "ad_spend", "value_decimal": "14600", "platform": "amazon",
        "provenance": {"source_field": "spend", "source_row": 1, "source_sha256": "ab"},
        "quality": {"status": "accepted", "flags": []},
    }
    server = server_factory("http://runtime.test", "eai_test.key")
    monkeypatch.setattr(type(server.runtime), "_get",
                        lambda self, path: {"observations": [observation]})

    result = json.loads(server.call_tool("opc.ops_metrics", {}))
    assert result["observations"][0] == observation


def test_each_ops_tool_hits_its_own_endpoint(server_factory, monkeypatch) -> None:
    server = server_factory("http://runtime.test", "eai_test.key")
    seen = []
    monkeypatch.setattr(type(server.runtime), "_get",
                        lambda self, path: seen.append(path) or {})

    for name in ("opc.ops_briefing", "opc.ops_metrics",
                 "opc.ops_proposals", "opc.ops_evidence"):
        server.call_tool(name, {})
    assert seen == ["/v1/briefing", "/v1/metric-observations",
                    "/v1/proposals", "/v1/evidence-imports"]


@pytest.mark.parametrize("code,expected", [(401, "API key"), (403, "API key"), (500, "HTTP 500")])
def test_http_errors_say_what_to_do(server_factory, monkeypatch, code, expected) -> None:
    server = server_factory("http://runtime.test", "eai_test.key")

    def raise_http(self, path):
        raise urllib.error.HTTPError(path, code, "err", {}, None)
    monkeypatch.setattr(type(server.runtime), "_get", raise_http)

    message = server.call_tool("opc.ops_briefing", {})
    assert expected in message


def test_unreachable_runtime_names_the_url(server_factory, monkeypatch) -> None:
    server = server_factory("http://runtime.test", "eai_test.key")

    def raise_url(self, path):
        raise urllib.error.URLError("Connection refused")
    monkeypatch.setattr(type(server.runtime), "_get", raise_url)

    message = server.call_tool("opc.ops_briefing", {})
    assert "runtime.test" in message


def test_trailing_slash_in_url_does_not_double_up(mcp_server_module) -> None:
    assert mcp_server_module.RuntimeBridge("http://x/", "k").url == "http://x"


def test_bridge_reads_environment(mcp_server_module, monkeypatch) -> None:
    monkeypatch.setenv("OPC_RUNTIME_URL", "http://env.test")
    monkeypatch.setenv("OPC_RUNTIME_API_KEY", "eai_env.key")
    bridge = mcp_server_module.RuntimeBridge()
    assert bridge.configured and bridge.url == "http://env.test"


def test_half_configured_is_treated_as_unconfigured(mcp_server_module) -> None:
    """A URL with no key would fail on every call; better to stay hidden."""
    assert not mcp_server_module.RuntimeBridge("http://x", "").configured
    assert not mcp_server_module.RuntimeBridge("", "eai_k.k").configured
