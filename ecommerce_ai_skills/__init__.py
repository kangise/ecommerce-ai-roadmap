"""Runtime primitives for the e-commerce AI infrastructure package."""

__all__ = ["USER_AGENT", "__version__"]

# Runtime clients import these constants; the RC gate verifies this value
# matches wheel metadata, pyproject, OpenAPI, server headers, and release tag.
__version__ = "1.3.0"
USER_AGENT = f"ecommerce-ai-skills/{__version__}"
