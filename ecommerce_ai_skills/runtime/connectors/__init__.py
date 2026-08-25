"""Credential-driven external connectors."""

from .base import HealthCheckConnector, ReadOnlyProductsConnector
from .amazon_spapi import AMAZON_MARKETPLACES, AmazonSPAPIReportsConnector
from .amazon_ads import ADS_REGION_ENDPOINTS, AmazonAdsConnector
from .shopify import ShopifyConnector

__all__ = ["ADS_REGION_ENDPOINTS", "AMAZON_MARKETPLACES", "AmazonAdsConnector", "AmazonSPAPIReportsConnector", "HealthCheckConnector", "ReadOnlyProductsConnector", "ShopifyConnector"]
