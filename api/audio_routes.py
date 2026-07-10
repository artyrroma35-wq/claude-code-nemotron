"""Audio API routes for Mistral voxtral integration."""
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import Response
from loguru import logger
from config.settings import Settings
from .dependencies import get_settings, require_api_key

router = APIRouter()

@router.post("/v1/audio/transcriptions")
async def transcribe_audio(
    file: UploadFile = File(...),
    model: str = Form(default="voxtral-mini-2602"),
    language: str | None = Form(default=None),
    response_format: str = Form(default="json"),
    settings: Settings = Depends(get_settings),
    _auth=Depends(require_api_key),
):
    api_key = settings.mistral_api_key
    if not api_key:
        raise HTTPException(status_code=501, detail="MISTRAL_API_KEY not configured")
    try:
        audio_data = await file.read()
        from providers.mistral.audio import transcribe_audio
        text = await transcribe_audio(api_key=api_key, audio_data=audio_data, filename=file.filename or "audio.mp3", content_type=file.content_type or "audio/mpeg", model=model, language=language)
        if text is None:
            raise HTTPException(status_code=502, detail="Transcription failed")
        return {"text": text}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/v1/audio/speech")
async def synthesize_speech(
    model: str = Form(default="voxtral-mini-tts-2603"),
    input: str = Form(...),
    voice: str = Form(default="default"),
    speed: float = Form(default=1.0),
    response_format: str = Form(default="mp3"),
    settings: Settings = Depends(get_settings),
    _auth=Depends(require_api_key),
):
    api_key = settings.mistral_api_key
    if not api_key:
        raise HTTPException(status_code=501, detail="MISTRAL_API_KEY not configured")
    try:
        from providers.mistral.audio import synthesize_speech
        audio_bytes = await synthesize_speech(api_key=api_key, text=input, model=model, voice=voice, speed=speed, response_format=response_format)
        if audio_bytes is None:
            raise HTTPException(status_code=502, detail="TTS failed")
        media_type = {"mp3": "audio/mpeg", "wav": "audio/wav", "ogg": "audio/ogg"}.get(response_format, "audio/mpeg")
        return Response(content=audio_bytes, media_type=media_type)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/v1/audio/voices")
async def list_voices(settings: Settings = Depends(get_settings), _auth=Depends(require_api_key)):
    api_key = settings.mistral_api_key
    if not api_key:
        raise HTTPException(status_code=501, detail="MISTRAL_API_KEY not configured")
    from providers.mistral.audio import list_voices
    voices = await list_voices(api_key)
    if voices is None:
        voices = [{"id": "default", "name": "Default"}, {"id": "nova", "name": "Nova"}]
    return {"data": voices}
