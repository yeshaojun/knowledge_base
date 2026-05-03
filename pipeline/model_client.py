"""Unified LLM API client with multi-provider support.

Supports DeepSeek, Qwen, and OpenAI through OpenAI-compatible API.
Configuration via environment variables: LLM_PROVIDER, API_KEY.
"""

import asyncio
import logging
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

import httpx

logger = logging.getLogger(__name__)


class Provider(Enum):
    """Supported LLM providers."""

    DEEPSEEK = "deepseek"
    QWEN = "qwen"
    OPENAI = "openai"


@dataclass
class Usage:
    """Token usage statistics."""

    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


@dataclass
class LLMResponse:
    """Unified LLM response structure."""

    content: str
    usage: Usage = field(default_factory=Usage)
    model: str = ""
    provider: str = ""
    finish_reason: str = ""


@dataclass
class ModelConfig:
    """Model configuration for each provider."""

    base_url: str
    default_model: str
    pricing: dict[str, float]


PROVIDER_CONFIGS: dict[Provider, ModelConfig] = {
    Provider.DEEPSEEK: ModelConfig(
        base_url="https://api.deepseek.com/v1",
        default_model="deepseek-v4-flash",
        pricing={
            "deepseek-chat": 0.00014,
            "deepseek-reasoner": 0.00055,
        },
    ),
    Provider.QWEN: ModelConfig(
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        default_model="qwen-plus",
        pricing={
            "qwen-turbo": 0.0002,
            "qwen-plus": 0.0004,
            "qwen-max": 0.002,
        },
    ),
    Provider.OPENAI: ModelConfig(
        base_url="https://api.openai.com/v1",
        default_model="gpt-4o-mini",
        pricing={
            "gpt-4o-mini": 0.00015,
            "gpt-4o": 0.0025,
            "gpt-4-turbo": 0.01,
        },
    ),
}


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    async def chat(
        self,
        messages: list[dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs: Any,
    ) -> LLMResponse:
        """Send chat completion request.

        Args:
            messages: List of message dicts with 'role' and 'content'.
            model: Model identifier, uses default if None.
            temperature: Sampling temperature (0-2).
            max_tokens: Maximum tokens to generate.
            **kwargs: Additional provider-specific parameters.

        Returns:
            LLMResponse with content and usage stats.
        """
        pass

    @abstractmethod
    async def embed(
        self,
        text: str | list[str],
        model: Optional[str] = None,
    ) -> list[float] | list[list[float]]:
        """Generate embeddings for text.

        Args:
            text: Single text or list of texts.
            model: Embedding model identifier.

        Returns:
            Embedding vector(s).
        """
        pass


class OpenAICompatibleProvider(LLMProvider):
    """OpenAI-compatible API provider implementation."""

    def __init__(
        self,
        provider: Provider,
        api_key: str,
        timeout: float = 60.0,
    ):
        """Initialize provider with API configuration.

        Args:
            provider: Provider enum value.
            api_key: API key for authentication.
            timeout: Request timeout in seconds.
        """
        self.provider = provider
        self.api_key = api_key
        self.timeout = timeout
        self.config = PROVIDER_CONFIGS[provider]
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=self.timeout)
        return self._client

    async def close(self) -> None:
        """Close HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def chat(
        self,
        messages: list[dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs: Any,
    ) -> LLMResponse:
        """Send chat completion request via OpenAI-compatible API.

        Args:
            messages: List of message dicts with 'role' and 'content'.
            model: Model identifier, uses default if None.
            temperature: Sampling temperature (0-2).
            max_tokens: Maximum tokens to generate.
            **kwargs: Additional parameters passed to API.

        Returns:
            LLMResponse with content and usage stats.

        Raises:
            httpx.HTTPError: API request failed.
        """
        client = await self._get_client()
        model = model or self.config.default_model

        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            **kwargs,
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        url = f"{self.config.base_url}/chat/completions"

        logger.debug(f"Sending chat request to {self.provider.value}: {model}")

        response = await client.post(url, json=payload, headers=headers)
        response.raise_for_status()

        data = response.json()
        choice = data["choices"][0]

        usage = Usage(
            prompt_tokens=data["usage"]["prompt_tokens"],
            completion_tokens=data["usage"]["completion_tokens"],
            total_tokens=data["usage"]["total_tokens"],
        )

        return LLMResponse(
            content=choice["message"]["content"],
            usage=usage,
            model=model,
            provider=self.provider.value,
            finish_reason=choice.get("finish_reason", ""),
        )

    async def embed(
        self,
        text: str | list[str],
        model: Optional[str] = None,
    ) -> list[float] | list[list[float]]:
        """Generate embeddings via OpenAI-compatible API.

        Args:
            text: Single text or list of texts.
            model: Embedding model identifier.

        Returns:
            Embedding vector(s).
        """
        client = await self._get_client()
        model = model or self._get_default_embedding_model()

        payload = {
            "model": model,
            "input": text,
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        url = f"{self.config.base_url}/embeddings"

        logger.debug(f"Sending embedding request to {self.provider.value}: {model}")

        response = await client.post(url, json=payload, headers=headers)
        response.raise_for_status()

        data = response.json()

        if isinstance(text, str):
            return data["data"][0]["embedding"]
        else:
            return [item["embedding"] for item in data["data"]]

    def _get_default_embedding_model(self) -> str:
        """Get default embedding model for provider."""
        embedding_models = {
            Provider.DEEPSEEK: "deepseek-embed",
            Provider.QWEN: "text-embedding-v3",
            Provider.OPENAI: "text-embedding-3-small",
        }
        return embedding_models[self.provider]


async def chat_with_retry(
    provider: LLMProvider,
    messages: list[dict[str, str]],
    max_retries: int = 3,
    base_delay: float = 1.0,
    **kwargs: Any,
) -> LLMResponse:
    """Send chat request with exponential backoff retry.

    Args:
        provider: LLM provider instance.
        messages: Chat messages.
        max_retries: Maximum retry attempts.
        base_delay: Base delay for exponential backoff.
        **kwargs: Additional chat parameters.

    Returns:
        LLMResponse from successful request.

    Raises:
        Exception: All retries exhausted.
    """
    last_error: Optional[Exception] = None

    for attempt in range(max_retries + 1):
        try:
            return await provider.chat(messages, **kwargs)
        except Exception as e:
            last_error = e
            if attempt < max_retries:
                delay = base_delay * (2**attempt)
                logger.warning(
                    f"Chat attempt {attempt + 1} failed: {e}. "
                    f"Retrying in {delay:.1f}s..."
                )
                await asyncio.sleep(delay)

    raise Exception(f"All {max_retries} retries exhausted. Last error: {last_error}")


def estimate_tokens(text: str) -> int:
    """Estimate token count for text.

    Uses rough approximation: ~4 characters per token for English,
    ~2 characters per token for Chinese.

    Args:
        text: Input text.

    Returns:
        Estimated token count.
    """
    chinese_chars = sum(1 for c in text if "\u4e00" <= c <= "\u9fff")
    other_chars = len(text) - chinese_chars

    return chinese_chars // 2 + other_chars // 4 + 1


def calculate_cost(
    prompt_tokens: int,
    completion_tokens: int,
    model: str,
    provider: Provider,
) -> float:
    """Calculate API cost in USD.

    Args:
        prompt_tokens: Number of prompt tokens.
        completion_tokens: Number of completion tokens.
        model: Model identifier.
        provider: Provider enum.

    Returns:
        Cost in USD.
    """
    config = PROVIDER_CONFIGS.get(provider)
    if not config:
        return 0.0

    price_per_1k = config.pricing.get(model, 0.0)
    total_tokens = prompt_tokens + completion_tokens

    return (total_tokens / 1000) * price_per_1k


def get_provider_from_env() -> Provider:
    """Get provider from LLM_PROVIDER environment variable.

    Returns:
        Provider enum value.

    Raises:
        ValueError: Invalid provider name.
    """
    provider_name = os.getenv("LLM_PROVIDER", "deepseek").lower()

    for provider in Provider:
        if provider.value == provider_name:
            return provider

    raise ValueError(
        f"Invalid LLM_PROVIDER: {provider_name}. "
        f"Valid options: {[p.value for p in Provider]}"
    )


def get_api_key(provider: Provider) -> str:
    """Get API key for provider from environment.

    Args:
        provider: Provider enum.

    Returns:
        API key string.

    Raises:
        ValueError: API key not found.
    """
    env_vars = {
        Provider.DEEPSEEK: "DEEPSEEK_API_KEY",
        Provider.QWEN: "QWEN_API_KEY",
        Provider.OPENAI: "OPENAI_API_KEY",
    }

    var_name = env_vars[provider]
    api_key = os.getenv(var_name)

    if not api_key:
        raise ValueError(f"API key not found: set {var_name} environment variable")

    return api_key


def create_client(
    provider: Optional[Provider] = None,
    api_key: Optional[str] = None,
    timeout: float = 60.0,
) -> OpenAICompatibleProvider:
    """Create LLM client from configuration.

    Args:
        provider: Provider enum, reads from env if None.
        api_key: API key, reads from env if None.
        timeout: Request timeout in seconds.

    Returns:
        Configured OpenAICompatibleProvider instance.
    """
    provider = provider or get_provider_from_env()
    api_key = api_key or get_api_key(provider)

    return OpenAICompatibleProvider(provider, api_key, timeout)


async def quick_chat(
    prompt: str,
    system: Optional[str] = None,
    model: Optional[str] = None,
    provider: Optional[Provider] = None,
    **kwargs: Any,
) -> str:
    """Simple one-shot chat function.

    Args:
        prompt: User prompt text.
        system: Optional system prompt.
        model: Model identifier.
        provider: Provider enum, reads from env if None.
        **kwargs: Additional chat parameters.

    Returns:
        Generated text content.
    """
    client = create_client(provider)

    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    try:
        response = await client.chat(messages, model=model, **kwargs)
        return response.content
    finally:
        await client.close()


if __name__ == "__main__":
    import json

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    async def test_client():
        """Test LLM client functionality."""
        print("=" * 60)
        print("Testing LLM Client")
        print("=" * 60)

        provider = get_provider_from_env()
        print(f"\nProvider: {provider.value}")

        client = create_client(provider)
        print(f"Base URL: {client.config.base_url}")
        print(f"Default Model: {client.config.default_model}")

        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What is 2+2? Answer in one word."},
        ]

        print("\n" + "-" * 60)
        print("Test 1: Basic Chat")
        print("-" * 60)

        try:
            response = await client.chat(messages)
            print(f"Response: {response.content}")
            print(f"Usage: {response.usage}")
            print(f"Model: {response.model}")
            print(f"Finish Reason: {response.finish_reason}")
        except Exception as e:
            print(f"Error: {e}")

        print("\n" + "-" * 60)
        print("Test 2: Chat with Retry")
        print("-" * 60)

        try:
            response = await chat_with_retry(client, messages, max_retries=2)
            print(f"Response: {response.content}")
            print(f"Usage: {response.usage}")
        except Exception as e:
            print(f"Error after retries: {e}")

        print("\n" + "-" * 60)
        print("Test 3: Token Estimation")
        print("-" * 60)

        test_texts = [
            "Hello, world!",
            "这是一个中文测试",
            "Mixed English and 中文混合测试",
        ]

        for text in test_texts:
            tokens = estimate_tokens(text)
            print(f"Text: {text!r} -> Est. {tokens} tokens")

        print("\n" + "-" * 60)
        print("Test 4: Cost Calculation")
        print("-" * 60)

        cost = calculate_cost(
            prompt_tokens=1000,
            completion_tokens=500,
            model=client.config.default_model,
            provider=provider,
        )
        print(f"1500 tokens with {client.config.default_model}: ${cost:.6f}")

        print("\n" + "-" * 60)
        print("Test 5: Quick Chat")
        print("-" * 60)

        try:
            result = await quick_chat(
                "Name one color.",
                system="Answer in one word.",
            )
            print(f"Quick chat result: {result}")
        except Exception as e:
            print(f"Error: {e}")

        print("\n" + "-" * 60)
        print("Test 6: Embeddings")
        print("-" * 60)

        try:
            embedding = await client.embed("Hello, world!")
            print(f"Embedding dimension: {len(embedding)}")
            print(f"First 5 values: {embedding[:5]}")
        except Exception as e:
            print(f"Error: {e}")

        await client.close()

        print("\n" + "=" * 60)
        print("Tests completed")
        print("=" * 60)

    asyncio.run(test_client())
