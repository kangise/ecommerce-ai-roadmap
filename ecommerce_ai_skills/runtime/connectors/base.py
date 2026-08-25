"""Connector contracts shared by platform adapters."""

from __future__ import annotations

from typing import Any, Protocol


class ReadOnlyProductsConnector(Protocol):
    """Minimum contract for a connector used by the sync action."""

    def list_products(self, *, limit: int = 50, page_info: str | None = None) -> dict[str, Any]:
        ...


class HealthCheckConnector(Protocol):
    """Connector contract used by account health checks."""

    def health_check(self) -> dict[str, Any]:
        ...
