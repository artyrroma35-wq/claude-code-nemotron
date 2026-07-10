"""Stats endpoint."""
from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from .dependencies import require_api_key, Depends

router = APIRouter()

@router.get("/stats")
async def get_stats(_auth=Depends(require_api_key)):
    return {"status": "ok", "provider": "gemini", "keys": 8, "model": "gemini-3.1-flash-lite"}

@router.get("/stats/ui", response_class=HTMLResponse)
async def stats_ui():
    return HTMLResponse(content="<!DOCTYPE html><html><head><meta charset=UTF-8><title>Gemini Proxy</title><style>body{font-family:sans-serif;background:#0d1117;color:#c9d1d9;padding:24px}h1{font-size:24px;margin-bottom:24px}.card{background:#161b22;border:1px solid #30363d;border-radius:8px;padding:16px;margin:12px 0}.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}.stat{text-align:center}.val{font-size:28px;font-weight:700}.lbl{color:#8b949e;font-size:12px}.green{color:#3fb950}.blue{color:#58a6ff}</style></head><body><h1>Gemini Proxy</h1><div class=grid><div class=card stat><div class=val green>8</div><div class=lbl>API Keys</div></div><div class=card stat><div class=val blue>15</div><div class=lbl>RPM per Key</div></div><div class=card stat><div class=val green>120</div><div class=lbl>Total RPM</div></div><div class=card stat><div class=val blue>1M</div><div class=lbl>TPM per Key</div></div><div class=card stat><div class=val green>8M</div><div class=lbl>Total TPM</div></div><div class=card stat><div class=val>gemini-3.1-flash-lite</div><div class=lbl>Model</div></div></div><div class=card><h3>Proxy Chain</h3><p>Your PC -> Server (NL) -> Cloudflare Worker -> Google Gemini API</p><p style=color:#8b949e;font-size:12px>Cloudflare Worker bypasses region restrictions</p></div></body></html>")
