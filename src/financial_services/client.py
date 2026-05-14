"""Anthropic API client wrapper for financial services.

Provides a configured client with retry logic, rate limiting,
and structured error handling appropriate for financial workloads.
"""

import logging
import time
from typing import Any, Optional

import anthropic
from anthropic import APIConnectionError, APIStatusError, RateLimitError

from .config import AppConfig, load_config

logger = logging.getLogger(__name__)


class FinancialServicesClient:
    """Wrapper around the Anthropic client with financial-services-specific configuration.

    Handles rate limiting, retries, and provides a consistent interface
    for interacting with Claude models in financial contexts.
    """

    def __init__(self, config: Optional[AppConfig] = None) -> None:
        """Initialize the client with the given configuration.

        Args:
            config: Application configuration. If None, loads from environment.
        """
        self.config = config or load_config()
        self._client = anthropic.Anthropic(
            api_key=self.config.anthropic.api_key,
            max_retries=self.config.anthropic.max_retries,
            timeout=self.config.anthropic.timeout_seconds,
        )
        self._request_timestamps: list[float] = []

    def _enforce_rate_limit(self) -> None:
        """Enforce the configured requests-per-minute rate limit.

        Blocks until a request slot is available based on a sliding window.
        """
        now = time.monotonic()
        window = 60.0  # 1-minute sliding window
        rpm = self.config.rate_limit.requests_per_minute

        # Prune timestamps outside the current window
        self._request_timestamps = [
            ts for ts in self._request_timestamps if now - ts < window
        ]

        if len(self._request_timestamps) >= rpm:
            oldest = self._request_timestamps[0]
            sleep_for = window - (now - oldest) + 0.05  # small buffer
            if sleep_for > 0:
                logger.debug("Rate limit reached; sleeping %.2fs", sleep_for)
                time.sleep(sleep_for)

        self._request_timestamps.append(time.monotonic())

    def complete(
        self,
        prompt: str,
        system: Optional[str] = None,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> str:
        """Send a completion request and return the response text.

        Args:
            prompt: The user message to send.
            system: Optional system prompt to prepend.
            max_tokens: Maximum tokens in the response. Defaults to config value.
            **kwargs: Additional keyword arguments forwarded to the Messages API.

        Returns:
            The assistant's response as a plain string.

        Raises:
            RateLimitError: When the Anthropic API rate limit is exceeded after retries.
            APIConnectionError: When the API cannot be reached.
            APIStatusError: For non-retryable API errors.
        """
        self._enforce_rate_limit()

        messages = [{"role": "user", "content": prompt}]
        request_params: dict[str, Any] = {
            "model": self.config.anthropic.model,
            "max_tokens": max_tokens or self.config.anthropic.max_tokens,
            "messages": messages,
            **kwargs,
        }
        if system:
            request_params["system"] = system

        try:
            logger.debug(
                "Sending request to model=%s max_tokens=%s",
                request_params["model"],
                request_params["max_tokens"],
            )
            response = self._client.messages.create(**request_params)
            text = response.content[0].text
            logger.debug("Received response (%d chars)", len(text))
            return text
        except RateLimitError:
            logger.warning("Anthropic rate limit exceeded")
            raise
        except APIConnectionError:
            logger.error("Failed to connect to Anthropic API")
            raise
        except APIStatusError as exc:
            logger.error("Anthropic API error %s: %s", exc.status_code, exc.message)
            raise

    def health_check(self) -> bool:
        """Verify connectivity to the Anthropic API.

        Returns:
            True if a minimal request succeeds, False otherwise.
        """
        try:
            self.complete("Reply with the single word: OK", max_tokens=5)
            return True
        except Exception as exc:  # noqa: BLE001
            logger.warning("Health check failed: %s", exc)
            return False
