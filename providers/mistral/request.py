
"""Mistral request builder - fixed."""
from __future__ import annotations
from typing import Any
from loguru import logger
from core.anthropic import build_base_request_body, set_if_not_none

MISTRAL_DEFAULT_TEXT_MODEL = "mistral-large-2512"
MISTRAL_DEFAULT_VISION_MODEL = "mistral-small-2603"
MISTRAL_DEFAULT_LARGE_MODEL = "mistral-large-2512"

def detect_content_type(messages: list[Any]) -> str:
    for msg in messages:
        content = getattr(msg, "content", None)
        if isinstance(content, list):
            for block in content:
                bt = block.get("type", "") if isinstance(block, dict) else getattr(block, "type", "")
                if bt == "image":
                    return "vision"
    return "text"

def convert_messages_for_mistral(messages, *, is_vision_request=False, include_thinking=True):
    from core.anthropic.conversion import AnthropicToOpenAIConverter
    result = []
    for msg in messages:
        role = getattr(msg, "role", "user")
        content = getattr(msg, "content", "")
        if isinstance(content, str):
            result.append({"role": role, "content": content})
        elif isinstance(content, list):
            if role == "assistant":
                result.extend(AnthropicToOpenAIConverter._convert_assistant_message(content, include_thinking=include_thinking, include_reasoning_content=True))
            elif role == "user":
                result.extend(_convert_user_with_vision(content, is_vision_request=is_vision_request))
        else:
            result.append({"role": role, "content": str(content)})
    return result

def _convert_user_with_vision(content, *, is_vision_request=False):
    result, text_parts, content_parts, has_media = [], [], [], False
    for block in content:
        bt = block.get("type", "") if isinstance(block, dict) else getattr(block, "type", "")
        if bt == "text":
            txt = block.get("text", "") if isinstance(block, dict) else getattr(block, "text", "")
            if is_vision_request:
                content_parts.append({"type": "text", "text": txt})
            else:
                text_parts.append(txt)
        elif bt == "image" and is_vision_request:
            src = block.get("source") if isinstance(block, dict) else getattr(block, "source", None)
            if isinstance(src, dict):
                img_url = None
                if src.get("type") == "base64":
                    img_url = f"data:{src.get('media_type', 'image/jpeg')};base64,{src.get('data', '')}"
                elif src.get("type") == "url":
                    img_url = src.get("url")
                if img_url:
                    has_media = True
                    if text_parts:
                        content_parts.append({"type": "text", "text": "\n".join(text_parts)})
                        text_parts.clear()
                    content_parts.append({"type": "image_url", "image_url": {"url": img_url}})
        elif bt == "tool_result":
            if text_parts:
                result.append({"role": "user", "content": "\n".join(text_parts)})
                text_parts.clear()
            tc = block.get("content", "") if isinstance(block, dict) else getattr(block, "content", "")
            if isinstance(tc, list):
                tc = "\n".join(str(x.get("text", str(x))) if isinstance(x, dict) else str(x) for x in tc)
            tid = block.get("tool_use_id", "") if isinstance(block, dict) else getattr(block, "tool_use_id", "")
            result.append({"role": "tool", "tool_call_id": tid, "content": str(tc) if tc else ""})
    if text_parts and not is_vision_request:
        result.append({"role": "user", "content": "\n".join(text_parts)})
    elif text_parts and is_vision_request:
        content_parts.append({"type": "text", "text": "\n".join(text_parts)})
    if content_parts:
        result.append({"role": "user", "content": content_parts})
    elif not text_parts and not has_media:
        result.append({"role": "user", "content": " "})
    return result

def build_request_body(request_data, *, thinking_enabled=False, is_vision_request=False, model_override=None):
    logger.debug("MISTRAL_REQ: start model={} msgs={} vision={}", model_override or getattr(request_data, "model", "?"), len(getattr(request_data, "messages", [])), is_vision_request)
    
    messages = convert_messages_for_mistral(request_data.messages, is_vision_request=is_vision_request, include_thinking=thinking_enabled)
    
    # Handle system prompt
    system = getattr(request_data, "system", None)
    if system:
        from core.anthropic.conversion import AnthropicToOpenAIConverter
        sm = AnthropicToOpenAIConverter.convert_system_prompt(system)
        if sm:
            messages.insert(0, sm)
    
    # Get model
    model = model_override or getattr(request_data, "model", MISTRAL_DEFAULT_TEXT_MODEL)
    if "/" in model:
        model = model.split("/", 1)[1]
    
    body = {"model": model, "messages": messages}
    
    # Optimal settings
    body["max_tokens"] = getattr(request_data, "max_tokens", None) or 81920
    body["temperature"] = getattr(request_data, "temperature", None) or 0.3
    body["top_p"] = getattr(request_data, "top_p", None) or 0.95
    
    ss = getattr(request_data, "stop_sequences", None)
    if ss: body["stop"] = ss
    tools = getattr(request_data, "tools", None)
    if tools:
        from core.anthropic.conversion import AnthropicToOpenAIConverter
        body["tools"] = AnthropicToOpenAIConverter.convert_tools(tools)
    tc = getattr(request_data, "tool_choice", None)
    if tc:
        from core.anthropic.conversion import AnthropicToOpenAIConverter
        body["tool_choice"] = AnthropicToOpenAIConverter.convert_tool_choice(tc)
    
    logger.debug("MISTRAL_REQ: done model={} msgs={}", body.get("model"), len(body.get("messages", [])))
    return body
