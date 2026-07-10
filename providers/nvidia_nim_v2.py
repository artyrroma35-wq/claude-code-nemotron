
"""NVIDIA NIM provider - UNLIMITED edition."""
from __future__ import annotations
import asyncio, time, random
from typing import Any
from openai import AsyncOpenAI, RateLimitError, APIStatusError, APITimeoutError
import httpx
from loguru import logger
from providers.base import ProviderConfig
from providers.defaults import NVIDIA_NIM_DEFAULT_BASE
from providers.openai_compat import OpenAIChatTransport
from .mistral.key_aggregator import get_nvidia_pool, get_models

class NvidiaNimProvider(OpenAIChatTransport):
    def __init__(self, config: ProviderConfig, *, model: str = "meta/llama-3.3-70b-instruct"):
        self._default_model = model
        super().__init__(config, provider_name="NVIDIA_NIM", base_url=config.base_url or "https://integrate.api.nvidia.com/v1", api_key=config.api_key)

    def _build_request_body(self, request: Any) -> dict:
        from core.anthropic import build_base_request_body
        body = build_base_request_body(request, include_thinking=True)
        # Model will be set dynamically in _create_stream
        return body

    def _is_thinking_enabled(self, request: Any) -> bool:
        return True

    async def _create_stream(self, body: dict) -> tuple[Any, dict]:
        pool = get_nvidia_pool()
        models = get_models()
        
        # Determine which model family to use based on request
        model_choice = self._default_model
        if "reasoning" in str(body.get("messages", "")) or "math" in str(body.get("messages", "")):
            model_choice = models["deepseek-pro"]["name"]
        elif "code" in str(body.get("messages", "")) or "```" in str(body.get("messages", "")):
            model_choice = models["deepseek-flash"]["name"]
        
        max_retries = 5
        last_error = None
        
        for attempt in range(max_retries):
            key, model = await pool.get_key(model_choice)
            body["model"] = model
            
            logger.info(f"NVIDIA_NIM: attempt {attempt+1}/{max_retries} key={key[:12]}... model={model}")
            
            # Recreate client with this key
            self._api_key = key
            self._client = AsyncOpenAI(
                api_key=key, base_url=self._base_url, max_retries=0,
                timeout=httpx.Timeout(self._config.http_read_timeout, connect=self._config.http_connect_timeout, read=self._config.http_read_timeout, write=self._config.http_write_timeout),
            )
            
            try:
                start = time.time()
                stream = await self._global_rate_limiter.execute_with_retry(
                    self._client.chat.completions.create, **body, stream=True
                )
                pool.record_success(key, time.time() - start)
                return stream, body
                
            except RateLimitError as e:
                pool.record_failure(key, model)
                logger.warning(f"NVIDIA 429: key={key[:12]}... retrying with different key")
                await asyncio.sleep(random.uniform(1, 3))
                last_error = e
                
            except APIStatusError as e:
                if e.status_code == 503:
                    pool.record_failure(key, model)
                    logger.warning(f"NVIDIA 503: {model} overloaded, trying fallback model...")
                    await asyncio.sleep(random.uniform(2, 5))
                    last_error = e
                elif e.status_code == 400:
                    # Bad model - try next model
                    logger.warning(f"NVIDIA 400: bad model {model}, trying next...")
                    model_choice = models["llama-3.3"]["name"]
                    last_error = e
                else:
                    pool.record_failure(key, model)
                    raise
                    
            except APITimeoutError as e:
                pool.record_failure(key, model)
                logger.warning(f"NVIDIA timeout: key={key[:12]}... retrying")
                await asyncio.sleep(random.uniform(1, 2))
                last_error = e
                
            except Exception as e:
                pool.record_failure(key, model)
                if "connection" in str(e).lower():
                    logger.warning(f"NVIDIA connection error, retrying...")
                    await asyncio.sleep(random.uniform(2, 4))
                    last_error = e
                else:
                    logger.error(f"NVIDIA unexpected error: {e}")
                    raise
        
        raise last_error or Exception("All NVIDIA NIM retries exhausted")
