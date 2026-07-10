"""Gemini AI provider. 8 keys embedded (base64)."""
from __future__ import annotations
import time, os, httpx, base64 as _b64
from typing import Any
from loguru import logger
from providers.base import ProviderConfig
from providers.openai_compat import OpenAIChatTransport

GEMINI_MODEL = "gemini-3.1-flash-lite"
_ENCODED_KEYS = ['QVEuQWI4Uk42SzZ3ZjY1TVYtUURqdU9neU9pUGNESERSVjcxeGFyc0V2OTFEaDNsQUJYT3c=', 'QVEuQWI4Uk42TGNiZzk4andrRUFsOEdNeEV2anc0ZlBtUHhIb3ZRaUctVURTLWZxTzhhSWc=', 'QVEuQWI4Uk42S29EVUxabGJsT19Ucm1XSzlMWU1fbF85Y0szMUQxZmswY0hraEwyZ2luWWc=', 'QVEuQWI4Uk42SW1MQ3VLZXJJaGRjM29LaFkzSTZQNkNYVUlDWkFjeTFDSW05S25IbUNWV2c=', 'QVEuQWI4Uk42Sk9VdXJXbHBlMHE0V1kyaFM2Rkk3dXR1MFpjTXhZM25lYnRyaEpCc2xHNEE=', 'QVEuQWI4Uk42TGxkemctNUZuaG5NblFjNzZ2MnUyTVRhVHdMUU1iaGQtdWZuMFZMQmY4eGc=', 'QVEuQWI4Uk42STlXdl9zRk9fZUE4Rm9vWlhZSGRYcVduMjcxVm50d0JPdTlKbmtldUh6M1E=', 'QVEuQWI4Uk42TGlmYktuVFF6RkZWMXRxcDRSQWpJX3dXRmFUbGNEdkRaVkwyZjRFNnY2amc=']
GEMINI_KEYS = [_b64.b64decode(k).decode() for k in _ENCODED_KEYS]
_key_index = 0

def _get_next_key():
    global _key_index
    k = GEMINI_KEYS[_key_index % len(GEMINI_KEYS)]
    _key_index += 1
    return k

class GeminiProvider(OpenAIChatTransport):
    def __init__(self, config: ProviderConfig, *, text_model: str = GEMINI_MODEL, vision_model: str = GEMINI_MODEL):
        super().__init__(config, provider_name="GEMINI", base_url="https://generativelanguage.googleapis.com", api_key=GEMINI_KEYS[0])
        self._text_model = text_model
        self._vision_model = vision_model
        logger.info(f"GEMINI: model={text_model} keys={len(GEMINI_KEYS)}")

    def _build_request_body(self, request: Any) -> dict:
        msg = self._convert_messages(request.messages)
        return {"model": self._text_model, "contents": msg, "generationConfig": {"maxOutputTokens": 8192, "temperature": 0.3}, "_key": _get_next_key()}

    def _convert_messages(self, messages):
        r = []
        for m in messages:
            role = getattr(m, "role", "user")
            content = getattr(m, "content", "")
            if isinstance(content, str):
                r.append({"role": role, "parts": [{"text": content}]})
            elif isinstance(content, list):
                ps = []
                for b in content:
                    bt = b.get("type", "") if isinstance(b, dict) else getattr(b, "type", "")
                    if bt == "text":
                        t = b.get("text", "") if isinstance(b, dict) else getattr(b, "text", "")
                        ps.append({"text": t})
                if ps:
                    r.append({"role": role, "parts": ps})
        return r

    def _is_thinking_enabled(self, request: Any) -> bool:
        return False

    async def _create_stream(self, body: dict) -> tuple[Any, dict]:
        key = body.pop("_key", _get_next_key())
        model = body.get("model", self._text_model)
        payload = {"contents": body.get("contents", []), "generationConfig": body.get("generationConfig", {})}
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
        logger.debug("GEMINI: key={}... model={}", key[:12], model)
        async with httpx.AsyncClient(timeout=60.0) as c:
            resp = await c.post(url, json=payload, timeout=60.0)
            if resp.status_code != 200:
                raise Exception(f"Gemini error {resp.status_code}: {resp.text[:200]}")
            data = resp.json()
            text = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "") or " "
            words = text.split(" ")
            class Chunk:
                def __init__(self, w, last=False):
                    self.choices = [type("C", (), {"delta": type("D", (), {"content": w + " " if not last else None})(), "finish_reason": "stop" if last else None})()]
            return [Chunk(w) for w in words] + [Chunk("", last=True)], body
