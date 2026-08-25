"""Runtime primitives for the e-commerce AI infrastructure package."""

__all__ = ["__version__"]

try:
    from importlib.metadata import version

    __version__ = version("ecommerce-ai-skills")
except Exception:  # pragma: no cover - source checkouts are not installed
    __version__ = "1.2.0"
