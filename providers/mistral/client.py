
"""Mistral AI provider with Smart Key Aggregator."""
from __future__ import annotations
import time
from typing import Any
from loguru import logger
from providers.base import ProviderConfig
from providers.defaults import MISTRAL_DEFAULT_BASE_URL
from providers.openai_compat import OpenAIChatTransport
from .request import (
    MISTRAL_DEFAULT_TEXT_MODEL, MISTRAL_DEFAULT_VISION_MODEL,
    build_request_body, detect_content_type,
)
from .key_aggregator import get_mistral_pool

class MistralProvider(OpenAIChatTransport):
    def __init__(self, config: ProviderConfig, *, text_model: str = MISTRAL_DEFAULT_TEXT_MODEL, vision_model: str = MISTRAL_DEFAULT_VISION_MODEL, all_keys: list[str] | None = None):
        super().__init__(config, provider_name="MISTRAL", base_url=config.base_url or MISTRAL_DEFAULT_BASE_URL, api_key=config.api_key)
        self._text_model = text_model
        self._vision_model = vision_model
        logger.info(f"MISTRAL: text={text_model} vision={vision_model}")

    def _build_request_body(self, request: Any) -> dict:
        content_type = detect_content_type(request.messages)
        is_vision = content_type == "vision"
        model = self._vision_model if is_vision else self._text_model
        return build_request_body(request, thinking_enabled=False, is_vision_request=is_vision, model_override=model)

    def _is_thinking_enabled(self, request: Any) -> bool:
        return False

    async def _create_stream(self, body: dict) -> tuple[Any, dict]:
        pool = get_mistral_pool()
        key, _ = await pool.get_key()
        logger.debug(f"MISTRAL: key={key[:12]}... model={body.get('model')}")
        import httpx
        from openai import AsyncOpenAI
        self._api_key = key
        self._client = AsyncOpenAI(api_key=key, base_url=self._base_url, max_retries=0, timeout=httpx.Timeout(self._config.http_read_timeout, connect=self._config.http_connect_timeout, read=self._config.http_read_timeout, write=self._config.http_write_timeout))
        start = time.time()
        try:
            stream = await self._global_rate_limiter.execute_with_retry(self._client.chat.completions.create, **body, stream=True)
            pool.record_success(key, time.time() - start)
            return stream, body
        except Exception as e:
            pool.record_failure(key)
            raise
