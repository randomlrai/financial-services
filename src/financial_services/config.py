"""Configuration management for financial-services.

Loads and validates settings from environment variables and optional
configuration files, providing a single source of truth for runtime
parameters across the package.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class AnthropicConfig:
    """Settings for communicating with the Anthropic API."""

    api_key: str
    model: str = "claude-opus-4-5"
    max_tokens: int = 4096
    timeout: float = 60.0
    base_url: Optional[str] = None  # Override for proxies / enterprise endpoints


@dataclass
class RateLimitConfig:
    """Token-bucket rate-limit parameters."""

    requests_per_minute: int = 60
    tokens_per_minute: int = 100_000


@dataclass
class LoggingConfig:
    """Logging verbosity and output format."""

    level: str = "INFO"  # DEBUG | INFO | WARNING | ERROR | CRITICAL
    json_format: bool = False
    log_file: Optional[str] = None


@dataclass
class AppConfig:
    """Top-level application configuration."""

    anthropic: AnthropicConfig
    rate_limit: RateLimitConfig = field(default_factory=RateLimitConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    environment: str = "development"  # development | staging | production
    debug: bool = False


def _require_env(name: str) -> str:
    """Return the value of *name* from the environment or raise."""
    value = os.getenv(name)
    if not value:
        raise EnvironmentError(
            f"Required environment variable '{name}' is not set. "
            "Please add it to your .env file or export it in your shell."
        )
    return value


def load_config() -> AppConfig:
    """Build an :class:`AppConfig` from environment variables.

    Required environment variables
    ------------------------------
    ANTHROPIC_API_KEY
        Secret key issued by Anthropic.

    Optional environment variables
    ------------------------------
    ANTHROPIC_MODEL            Default: claude-opus-4-5
    ANTHROPIC_MAX_TOKENS       Default: 4096
    ANTHROPIC_TIMEOUT          Default: 60.0  (seconds)
    ANTHROPIC_BASE_URL         Default: (unset — uses SDK default)
    RATE_LIMIT_RPM             Default: 60
    RATE_LIMIT_TPM             Default: 100000
    LOG_LEVEL                  Default: INFO
    LOG_JSON                   Default: false
    LOG_FILE                   Default: (unset — stdout only)
    APP_ENV                    Default: development
    APP_DEBUG                  Default: false
    """
    anthropic_cfg = AnthropicConfig(
        api_key=_require_env("ANTHROPIC_API_KEY"),
        model=os.getenv("ANTHROPIC_MODEL", "claude-opus-4-5"),
        max_tokens=int(os.getenv("ANTHROPIC_MAX_TOKENS", "4096")),
        timeout=float(os.getenv("ANTHROPIC_TIMEOUT", "60.0")),
        base_url=os.getenv("ANTHROPIC_BASE_URL") or None,
    )

    rate_limit_cfg = RateLimitConfig(
        requests_per_minute=int(os.getenv("RATE_LIMIT_RPM", "60")),
        tokens_per_minute=int(os.getenv("RATE_LIMIT_TPM", "100000")),
    )

    logging_cfg = LoggingConfig(
        level=os.getenv("LOG_LEVEL", "INFO").upper(),
        json_format=os.getenv("LOG_JSON", "false").lower() in {"1", "true", "yes"},
        log_file=os.getenv("LOG_FILE") or None,
    )

    return AppConfig(
        anthropic=anthropic_cfg,
        rate_limit=rate_limit_cfg,
        logging=logging_cfg,
        environment=os.getenv("APP_ENV", "development"),
        debug=os.getenv("APP_DEBUG", "false").lower() in {"1", "true", "yes"},
    )


# Module-level singleton — import and reuse rather than calling load_config() repeatedly.
# Re-export so callers can do: from financial_services.config import config
try:
    config: AppConfig = load_config()
except EnvironmentError:
    # Allow the module to be imported (e.g. for docs/tests) without crashing;
    # callers that actually need the config will receive the error at call time.
    config = None  # type: ignore[assignment]
