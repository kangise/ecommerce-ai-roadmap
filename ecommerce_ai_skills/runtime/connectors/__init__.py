"""Credential-driven external connectors."""

from .base import ReadOnlyProductsConnector
from .amazon_spapi import AmazonSPAPIReportsConnector
from .shopify import ShopifyConnector

__all__ = ["AmazonSPAPIReportsConnector", "ReadOnlyProductsConnector", "ShopifyConnector"]
