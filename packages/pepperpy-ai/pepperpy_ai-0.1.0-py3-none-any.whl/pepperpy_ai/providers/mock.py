"""Mock provider implementation."""

from collections.abc import AsyncGenerator
from typing import NotRequired, TypedDict, cast

from ..ai_types import Message
from ..responses import AIResponse, ResponseMetadata
from .base import BaseProvider
from .exceptions import ProviderError


class MockConfig(TypedDict):
    """Mock provider configuration."""

    model: str  # Required field
    temperature: NotRequired[float]
    max_tokens: NotRequired[int]
    top_p: NotRequired[float]
    frequency_penalty: NotRequired[float]
    presence_penalty: NotRequired[float]
    timeout: NotRequired[float]


class MockProvider(BaseProvider[MockConfig]):
    """Mock provider implementation."""

    def __init__(self, config: MockConfig, api_key: str) -> None:
        """Initialize provider.

        Args:
            config: Provider configuration
            api_key: Mock API key
        """
        super().__init__(config, api_key)

    async def initialize(self) -> None:
        """Initialize provider."""
        if not self._initialized:
            self._initialized = True

    async def cleanup(self) -> None:
        """Cleanup provider resources."""
        self._initialized = False

    async def stream(
        self,
        messages: list[Message],
        *,
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> AsyncGenerator[AIResponse, None]:
        """Stream responses from mock provider.

        Args:
            messages: List of messages to send
            model: Model to use for completion
            temperature: Temperature to use for completion
            max_tokens: Maximum number of tokens to generate

        Returns:
            AsyncGenerator yielding AIResponse objects

        Raises:
            ProviderError: If provider is not initialized or streaming fails
        """
        if not self.is_initialized:
            raise ProviderError(
                "Provider not initialized",
                provider="mock",
                operation="stream",
            )

        try:
            for message in messages:
                yield AIResponse(
                    content=f"Mock response to: {message.content}",
                    metadata=cast(ResponseMetadata, {
                        "model": model or self.config["model"],
                        "provider": "mock",
                        "usage": {"total_tokens": 0},
                        "finish_reason": "stop",
                    }),
                )
        except Exception as e:
            raise ProviderError(
                "Failed to stream responses",
                provider="mock",
                operation="stream",
                cause=e,
            ) from e
