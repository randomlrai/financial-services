"""Financial Services SDK for Anthropic Claude integration.

This package provides tools and utilities for integrating Claude AI
into financial services workflows, including document analysis,
risk assessment, and compliance checking.
"""

__version__ = "0.1.0"
__author__ = "Anthropic"
__license__ = "MIT"

from financial_services.client import FinancialServicesClient
from financial_services.exceptions import (
    FinancialServicesError,
    AuthenticationError,
    RateLimitError,
    ValidationError,
)

__all__ = [
    "FinancialServicesClient",
    "FinancialServicesError",
    "AuthenticationError",
    "RateLimitError",
    "ValidationError",
]
