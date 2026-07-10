
"""Web File Manager."""
from __future__ import annotations
import os, time, mimetypes, shutil
from pathlib import Path
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, Query
from fastapi.responses import FileResponse, HTMLResponse, Response
from loguru import logger
from config.settings import Settings
from .dependencies import get_settings, require_api_key

router = APIRouter()
UPLOAD_DIR = "/root/claude-files"

def fmt_size(s):
    if s < 1024: return f"{s} B"
    elif s < 1048576: return f"{s/1024:.1f} KB"
    elif s < 1073741824: return f"{s/1048576:.1f} MB"
    else: return f"{s/1073741824:.2f} GB"

def icon(mime):
    if not mime: return "📎"
    if mime.startswith("image/"): return "🖼️"
    if mime == "application/pdf": return "📄"
    if mime.startswith("text/"): return "📝"
    if "audio" in mime: return "🎵"
    return "📎"

@router.on_event("startup")
async def setup():
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    logger.info(f"File Manager ready at {UPLOAD_DIR}")

# PUBLIC - no auth required
@router.get("/files/ui", response_class=HTMLResponse)
async def files_ui():
    return HTMLResponse(content=UI_HTML)

# AUTHENTICATED - API endpoints
@router.get("/files")
async def list_files(path: str = Query(default=""), _auth=Depends(require_api_key)):
    base = Path(UPLOAD_DIR).resolve()
    current = (base / path).resolve()
    if not str(current).startswith(str(base)):
        raise HTTPException(400, "Invalid path")
    if not current.exists():
        return {"files": [], "path": path, "total": 0, "total_size": "0 B"}
    files = []
    total_size = 0
    for f in sorted(current.iterdir()):
        if f.name.startswith("."): continue
        s = f.stat()
        is_dir = f.is_dir()
        m, _ = mimetypes.guess_type(str(f))
        m = m or "application/octet-stream"
        rel = str(f.relative_to(base))
        files.append({"name": f.name, "path": rel, "size": s.st_size, "size_formatted": fmt_size(s.st_size), "is_dir": is_dir, "icon": "📁" if is_dir else icon(m), "mime_type": m if not is_dir else "directory", "modified": s.st_mtime, "modified_str": time.strftime("%Y-%m-%d %H:%M", time.localtime(s.st_mtime)), "url": f"/files/download/{rel}" if not is_dir else None, "preview_url": f"/files/preview/{rel}" if not is_dir else None})
        if not is_dir: total_size += s.st_size
    return {"files": files, "path": path, "total": len(files), "total_size": fmt_size(total_size)}

@router.post("/files/upload")
async def upload_file(file: UploadFile = File(...), path: str = Form(default=""), _auth=Depends(require_api_key)):
    base = Path(UPLOAD_DIR).resolve()
    target = (base / path).resolve()
    if not str(target).startswith(str(base)): raise HTTPException(400, "Invalid path")
    os.makedirs(target, exist_ok=True)
    content = await file.read()
    if len(content) > 250 * 1024 * 1024: raise HTTPException(413, "File too large")
    fp = target / file.filename
    with open(fp, "wb") as f: f.write(content)
    m = file.content_type or "application/octet-stream"
    rel = str(fp.relative_to(base))
    logger.info(f"Uploaded: {file.filename} ({fmt_size(len(content))})")
    return {"status": "ok", "file": {"name": file.filename, "size": len(content), "size_formatted": fmt_size(len(content)), "mime_type": m, "path": rel, "url": f"/files/download/{rel}", "preview_url": f"/files/preview/{rel}"}}

@router.get("/files/download/{p:path}")
async def download_file(p: str, _auth=Depends(require_api_key)):
    fp = (Path(UPLOAD_DIR) / p).resolve()
    if not str(fp).startswith(str(Path(UPLOAD_DIR).resolve())): raise HTTPException(400)
    if not fp.exists() or not fp.is_file(): raise HTTPException(404)
    m, _ = mimetypes.guess_type(str(fp))
    return FileResponse(str(fp), media_type=m or "application/octet-stream", filename=fp.name)

@router.get("/files/preview/{p:path}")
async def preview_file(p: str, _auth=Depends(require_api_key)):
    fp = (Path(UPLOAD_DIR) / p).resolve()
    if not str(fp).startswith(str(Path(UPLOAD_DIR).resolve())): raise HTTPException(400)
    if not fp.exists() or not fp.is_file(): raise HTTPException(404)
    m, _ = mimetypes.guess_type(str(fp))
    m = m or "application/octet-stream"
    if m.startswith("image/"): return FileResponse(str(fp), media_type=m)
    if m.startswith("text/") or m in ("application/json", "application/xml", "application/x-yaml"):
        try:
            c = fp.read_text(encoding="utf-8", errors="replace")
            if len(c) > 10000: c = c[:10000] + f"\n\n... (truncated, {fmt_size(fp.stat().st_size)})"
            return Response(content=c, media_type="text/plain; charset=utf-8")
        except: pass
    if m == "application/pdf": return FileResponse(str(fp), media_type="application/pdf")
    return FileResponse(str(fp), media_type="application/octet-stream")

@router.delete("/files/{p:path}")
async def delete_file(p: str, _auth=Depends(require_api_key)):
    fp = (Path(UPLOAD_DIR) / p).resolve()
    if not str(fp).startswith(str(Path(UPLOAD_DIR).resolve())): raise HTTPException(400)
    if not fp.exists(): raise HTTPException(404)
    if fp.is_dir(): shutil.rmtree(fp); logger.info(f"Dir deleted: {p}")
    else: fp.unlink(); logger.info(f"File deleted: {p}")
    return {"status": "ok", "deleted": p}

UI_HTML = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>File Manager</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#0d1117;color:#c9d1d9;min-height:100vh}
.header{background:#161b22;border-bottom:1px solid #30363d;padding:16px 24px;display:flex;align-items:center;justify-content:space-between}
.header h1{font-size:20px;display:flex;align-items:center;gap:8px}
.subtitle{color:#8b949e;font-size:13px}
.container{max-width:1200px;margin:0 auto;padding:20px}
.upload-zone{background:#161b22;border:2px dashed #30363d;border-radius:12px;padding:40px;text-align:center;cursor:pointer;transition:.3s;margin-bottom:20px}
.upload-zone:hover{border-color:#58a6ff;background:rgba(88,166,255,.05)}
.upload-zone .icon{font-size:48px;margin-bottom:12px}
.upload-zone .text{color:#8b949e;font-size:14px}
.upload-zone .text strong{color:#58a6ff}
.upload-zone input[type=file]{display:none}
.progress{display:none;margin-top:16px}
.progress-bar{height:4px;background:#30363d;border-radius:2px;overflow:hidden}
.progress-fill{height:100%;background:#58a6ff;width:0%;transition:.3s}
.progress-text{margin-top:8px;font-size:12px;color:#8b949e}
.status-bar{display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;flex-wrap:wrap;gap:8px}
.status-info{color:#8b949e;font-size:13px}
.actions{display:flex;gap:8px}
.btn{padding:8px 16px;border:1px solid #30363d;background:#161b22;color:#c9d1d9;border-radius:6px;cursor:pointer;font-size:13px;transition:.2s;text-decoration:none;display:inline-flex;align-items:center;gap:6px}
.btn:hover{background:#30363d}
.file-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:12px}
.file-card{background:#161b22;border:1px solid #30363d;border-radius:8px;padding:16px;transition:.2s;cursor:pointer;position:relative}
.file-card:hover{border-color:#58a6ff;transform:translateY(-1px)}
.file-card .icon{font-size:32px;margin-bottom:8px}
.file-card .name{font-size:13px;word-break:break-all;line-height:1.4;margin-bottom:4px}
.file-card .meta{font-size:11px;color:#8b949e}
.file-card .del{position:absolute;top:8px;right:8px;width:24px;height:24px;border:none;background:rgba(248,81,73,.1);color:#f85149;border-radius:4px;cursor:pointer;font-size:14px;display:none;align-items:center;justify-content:center}
.file-card:hover .del{display:flex}
.file-card .del:hover{background:#f85149;color:#fff}
.empty{text-align:center;padding:60px 20px;color:#8b949e}
.empty .icon{font-size:64px;margin-bottom:16px}
.empty h3{font-size:18px;margin-bottom:8px;color:#c9d1d9}
.toast{position:fixed;bottom:24px;right:24px;background:#161b22;border:1px solid #30363d;border-radius:8px;padding:12px 20px;font-size:14px;box-shadow:0 8px 24px rgba(0,0,0,.4);display:none;z-index:1000;animation:slideIn .3s}
.toast.success{border-color:#3fb950}
.toast.error{border-color:#f85149}
@keyframes slideIn{from{transform:translateY(100px);opacity:0}to{transform:translateY(0);opacity:1}}
.modal{display:none;position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,.7);z-index:999;align-items:center;justify-content:center}
.modal.active{display:flex}
.modal-box{background:#161b22;border:1px solid #30363d;border-radius:12px;padding:24px;max-width:90vw;max-height:90vh;overflow:auto;position:relative}
.modal-box pre{white-space:pre-wrap;font-family:monospace;font-size:12px;line-height:1.5;max-height:70vh;overflow:auto}
.modal-box .close{position:absolute;top:12px;right:12px;background:none;border:none;color:#8b949e;font-size:20px;cursor:pointer}
.modal-box img{max-width:100%;border-radius:8px}
@media(max-width:600px){.header{padding:12px 16px}.file-grid{grid-template-columns:repeat(auto-fill,minmax(140px,1fr))}}
</style>
</head>
<body>
<div class="header"><div><h1>📁 File Manager</h1><div class="subtitle">Claude Code Proxy</div></div><div><a href="/" class="btn">🏠 Home</a></div></div>
<div class="container">
<div class="upload-zone" id="dropZone"><div class="icon">📤</div><div class="text"><strong>Click to upload</strong> or drag & drop<br><small>Max 250 MB</small></div><input type="file" id="fileInput" multiple><div class="progress" id="progress"><div class="progress-bar"><div class="progress-fill" id="progressFill"></div></div><div class="progress-text" id="progressText"></div></div></div>
<div class="status-bar"><div class="status-info" id="statusInfo">Loading...</div><div class="actions"><button class="btn" onclick="refresh()">🔄 Refresh</button></div></div>
<div class="file-grid" id="fileGrid"></div></div>
<div class="modal" id="modal"><div class="modal-box"><button class="close" onclick="closeModal()">✕</button><div id="modalContent"></div></div></div>
<div class="toast" id="toast"></div>
<script>
let curPath='',API=window.location.origin;
async function refresh(){try{const r=await fetch(API+'/files?path='+encodeURIComponent(curPath),{headers:{'x-api-key':'freecc'}});render(await r.json())}catch(e){document.getElementById('statusInfo').textContent='Error'}}
function render(d){const g=document.getElementById('fileGrid'),i=document.getElementById('statusInfo');i.textContent=d.total+' items, '+d.total_size;
if(!d.files.length){g.innerHTML='<div class=empty><div class=icon>📂</div><h3>No files</h3><p>Upload files above</p></div>';return}
let h='';if(curPath){const p=curPath.split('/').slice(0,-1).join('/');h+='<div class="file-card" onclick="navigate(\''+p+'\')"><div class=icon>📁</div><div class=name>..</div><div class=meta>Parent</div></div>'}
for(const f of d.files){if(f.is_dir)h+='<div class="file-card" onclick="navigate(\''+f.path+'\')"><div class=icon>📁</div><div class=name>'+esc(f.name)+'</div><div class=meta>'+f.modified_str+'</div></div>'
else h+='<div class="file-card" data-path="'+f.path+'" data-mime="'+f.mime_type+'"><button class=del onclick="delFile(\''+f.path+'\',event)">✕</button><div class=icon>'+f.icon+'</div><div class=name>'+esc(f.name)+'</div><div class=meta>'+f.size_formatted+'</div></div>'}
g.innerHTML=h;for(const c of g.querySelectorAll('.file-card[data-path]'))c.addEventListener('click',function(e){if(e.target.tagName!='BUTTON')preview(this.dataset.path,this.dataset.mime)})}
function navigate(p){curPath=p;refresh()}
async function preview(p,m){const modal=document.getElementById('modal'),c=document.getElementById('modalContent');
modal.classList.add('active');
if(m.startsWith('image/'))c.innerHTML='<img src="'+API+'/files/preview/'+p+'">';
else if(m=='application/pdf')c.innerHTML='<iframe src="'+API+'/files/preview/'+p+'" style="width:100%;height:80vh;border:none;border-radius:8px"></iframe>';
else{try{const r=await fetch(API+'/files/preview/'+p,{headers:{'x-api-key':'freecc'}});c.innerHTML='<pre>'+esc(await r.text())+'</pre>'}catch(e){c.innerHTML='<p>Error</p>'}}}
function closeModal(){document.getElementById('modal').classList.remove('active')}
async function delFile(p,e){if(e)e.stopPropagation();if(!confirm('Delete?'))return;try{const r=await fetch(API+'/files/'+p,{method:'DELETE',headers:{'x-api-key':'freecc'}});if(r.ok){toast('Deleted','success');refresh()}else toast('Failed','error')}catch(e){toast('Error','error')}}
function esc(t){const d=document.createElement('div');d.textContent=t;return d.innerHTML}
function toast(m,t){const o=document.getElementById('toast');o.textContent=m;o.className='toast '+t;o.style.display='block';setTimeout(()=>o.style.display='none',3000)}
const dz=document.getElementById('dropZone'),fi=document.getElementById('fileInput');
dz.onclick=()=>fi.click();
dz.ondragover=e=>{e.preventDefault();dz.style.borderColor='#58a6ff'};
dz.ondragleave=()=>dz.style.borderColor='#30363d';
dz.ondrop=e=>{e.preventDefault();dz.style.borderColor='#30363d';if(e.dataTransfer.files.length)upload(e.dataTransfer.files)};
fi.onchange=()=>{if(fi.files.length)upload(fi.files)};
async function upload(files){const p=document.getElementById('progress'),f=document.getElementById('progressFill'),t=document.getElementById('progressText');p.style.display='block';
for(let i=0;i<files.length;i++){const file=files[i];f.style.width='0%';t.textContent=file.name+' ('+(i+1)+'/'+files.length+')';
const fd=new FormData();fd.append('file',file);fd.append('path',curPath);
try{const r=await fetch(API+'/files/upload',{method:'POST',headers:{'x-api-key':'freecc'},body:fd});f.style.width='100%';if(r.ok)toast('Uploaded: '+file.name,'success');else toast('Upload failed','error')}catch(e){toast('Error','error')}}
setTimeout(()=>p.style.display='none',1000);refresh()}
refresh();
</script></body></html>"""
