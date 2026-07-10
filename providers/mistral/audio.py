"""Mistral Audio API integration."""
from __future__ import annotations
from typing import Any
import httpx
from loguru import logger

MISTRAL_AUDIO_TRANSCRIPTIONS_ENDPOINT = "https://api.mistral.ai/v1/audio/transcriptions"
MISTRAL_AUDIO_SPEECH_ENDPOINT = "https://api.mistral.ai/v1/audio/speech"
MISTRAL_AUDIO_VOICES_ENDPOINT = "https://api.mistral.ai/v1/audio/voices"

async def transcribe_audio(api_key: str, audio_data: bytes, filename: str = "audio.mp3", content_type: str = "audio/mpeg", model: str = "voxtral-mini-2602", language: str | None = None) -> str | None:
    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            files = {"file": (filename, audio_data, content_type), "model": (None, model)}
            if language: files["language"] = (None, language)
            response = await client.post(MISTRAL_AUDIO_TRANSCRIPTIONS_ENDPOINT, headers={"Authorization": f"Bearer {api_key}"}, files=files, timeout=120.0)
            if response.status_code != 200:
                logger.error(f"MISTRAL_AUDIO: transcription failed {response.status_code}")
                return None
            text = response.json().get("text", "")
            logger.info(f"MISTRAL_AUDIO: transcribed {len(audio_data)}b -> {len(text)}c")
            return text
        except Exception as e:
            logger.error(f"MISTRAL_AUDIO: transcription error: {e}")
            return None

async def synthesize_speech(api_key: str, text: str, model: str = "voxtral-mini-tts-2603", voice: str = "default", speed: float = 1.0, response_format: str = "mp3") -> bytes | None:
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(MISTRAL_AUDIO_SPEECH_ENDPOINT, headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}, json={"model": model, "input": text, "voice": voice, "speed": speed, "response_format": response_format}, timeout=60.0)
            if response.status_code != 200:
                logger.error(f"MISTRAL_AUDIO: TTS failed {response.status_code}")
                return None
            logger.info(f"MISTRAL_AUDIO: TTS {len(text)}c -> {len(response.content)}b")
            return response.content
        except Exception as e:
            logger.error(f"MISTRAL_AUDIO: TTS error: {e}")
            return None

async def list_voices(api_key: str) -> list[dict[str, Any]] | None:
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(MISTRAL_AUDIO_VOICES_ENDPOINT, headers={"Authorization": f"Bearer {api_key}"}, timeout=30.0)
            if response.status_code == 200:
                return response.json().get("data", [])
            return None
        except Exception as e:
            logger.error(f"MISTRAL_AUDIO: list voices error: {e}")
            return None
