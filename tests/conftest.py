from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session")
def mcp_server_module():
    path = ROOT / "integration" / "mcp-server.py"
    spec = importlib.util.spec_from_file_location("ecommerce_mcp_server", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
