"""Application services for the Claude-compatible API."""

from __future__ import annotations

import traceback
import uuid
from collections.abc import Callable
from typing import Any

from fastapi import HTTPException
from fastapi.responses import StreamingResponse
from loguru import logger

from config.settings import Settings
from core.anthropic import get_token_count, get_user_facing_error_message
from providers.base import BaseProvider
from providers.exceptions import InvalidRequestError, ProviderError

from .model_router import ModelRouter
from .models.anthropic import MessagesRequest, TokenCountRequest
from .models.responses import TokenCountResponse
from .optimization_handlers import try_optimizations
from .web_server_tools import (
    is_web_server_tool_request,
    stream_web_server_tool_response,
)

TokenCounter = Callable[[list[Any], str | list[Any] | None, list[Any] | None], int]

ProviderGetter = Callable[[str], BaseProvider]


class ClaudeProxyService:
    """Coordinate request optimization, model routing, token count, and providers."""

    def __init__(
        self,
        settings: Settings,
        provider_getter: ProviderGetter,
        model_router: ModelRouter | None = None,
        token_counter: TokenCounter = get_token_count,
    ):
        self._settings = settings
        self._provider_getter = provider_getter
        self._model_router = model_router or ModelRouter(settings)
        self._token_counter = token_counter

    async def create_message(self, request_data: MessagesRequest) -> object:
        """Create a message response or streaming response."""
        try:
            if not request_data.messages:
                raise InvalidRequestError("messages cannot be empty")

            # === PRO MODE: Auto-inject strong system prompt + project context + multi-step ===
            try:
                from config.pro_mode import inject_pro_system

                pro_mode = getattr(self._settings, "pro_mode", True)
                multi_step = getattr(self._settings, "multi_step_mode", False)
                proj_ctx = getattr(self._settings, "project_context", True)

                if pro_mode:
                    msg_dicts = []
                    for m in request_data.messages:
                        if hasattr(m, "model_dump"):
                            msg_dicts.append(m.model_dump())
                        else:
                            msg_dicts.append({"role": getattr(m, "role", "user"), "content": getattr(m, "content", "")})

                    enhanced = inject_pro_system(
                        msg_dicts,
                        pro_mode=True,
                        multi_step=multi_step,
                        project_context=proj_ctx,
                        workspace=getattr(self._settings, "claude_workspace", "."),
                    )

                    from .models.anthropic import Message
                    request_data.messages = [Message(**m) for m in enhanced if isinstance(m, dict)]
            except Exception as e:
                logger.debug(f"Pro mode injection skipped: {e}")
            # === END PRO MODE ===

            routed = self._model_router.resolve_messages_request(request_data)
            if is_web_server_tool_request(routed.request):
                input_tokens = self._token_counter(
                    routed.request.messages, routed.request.system, routed.request.tools
                )
                logger.info("Optimization: Handling Anthropic web server tool")
                return StreamingResponse(
                    stream_web_server_tool_response(
                        routed.request, input_tokens=input_tokens
                    ),
                    media_type="text/event-stream",
                    headers={
                        "X-Accel-Buffering": "no",
                        "Cache-Control": "no-cache",
                        "Connection": "keep-alive",
                    },
                )

            optimized = try_optimizations(routed.request, self._settings)
            if optimized is not None:
                return optimized
            logger.debug("No optimization matched, routing to provider")

            provider = self._provider_getter(routed.resolved.provider_id)

            request_id = f"req_{uuid.uuid4().hex[:12]}"
            logger.info(
                "API_REQUEST: request_id={} model={} messages={}",
                request_id,
                routed.request.model,
                len(routed.request.messages),
            )
            logger.debug(
                "FULL_PAYLOAD [{}]: {}", request_id, routed.request.model_dump()
            )

            input_tokens = self._token_counter(
                routed.request.messages, routed.request.system, routed.request.tools
            )
            return StreamingResponse(
                provider.stream_response(
                    routed.request,
                    input_tokens=input_tokens,
                    request_id=request_id,
                ),
                media_type="text/event-stream",
                headers={
                    "X-Accel-Buffering": "no",
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                },
            )

        except ProviderError:
            raise
        except Exception as e:
            logger.error(f"Error: {e!s}\n{traceback.format_exc()}")
            raise HTTPException(
                status_code=getattr(e, "status_code", 500),
                detail=get_user_facing_error_message(e),
            ) from e

    def count_tokens(self, request_data: TokenCountRequest) -> TokenCountResponse:
        """Count tokens for a request after applying configured model routing."""
        request_id = f"req_{uuid.uuid4().hex[:12]}"
        with logger.contextualize(request_id=request_id):
            try:
                routed = self._model_router.resolve_token_count_request(request_data)
                tokens = self._token_counter(
                    routed.request.messages, routed.request.system, routed.request.tools
                )
                logger.info(
                    "COUNT_TOKENS: request_id={} model={} messages={} input_tokens={}",
                    request_id,
                    routed.request.model,
                    len(routed.request.messages),
                    tokens,
                )
                return TokenCountResponse(input_tokens=tokens)
            except Exception as e:
                logger.error(
                    "COUNT_TOKENS_ERROR: request_id={} error={}\n{}",
                    request_id,
                    get_user_facing_error_message(e),
                    traceback.format_exc(),
                )
                raise HTTPException(
                    status_code=500, detail=get_user_facing_error_message(e)
                ) from e
