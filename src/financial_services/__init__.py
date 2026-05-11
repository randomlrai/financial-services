"""Financial Services SDK for Anthropic Claude integration.

This package provides tools and utilities for integrating Claude AI
into financial services workflows, including document analysis,
risk assessment, and compliance checking.

Note: Forked from anthropics/financial-services for personal learning.
Main areas of interest: document analysis and risk assessment modules.

Personal fork changes:
- Added APIConnectionError to public exports (was missing from __all__)
- Added ConnectionTimeoutError to public exports for better error handling
- Exposed __version__ in __all__ for easier version checking
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
    APIConnectionError,
)

__all__ = [
    "__version__",  # handy for quick version checks: financial_services.__version__
    "FinancialServicesClient",
    "FinancialServicesError",
    "AuthenticationError",
    "RateLimitError",
    "ValidationError",
    "APIConnectionError",
]
