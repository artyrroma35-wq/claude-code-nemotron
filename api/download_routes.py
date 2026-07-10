"""Download routes for Claude CLI."""
from fastapi import APIRouter
from fastapi.responses import Response, PlainTextResponse
import os

router = APIRouter()

@router.get("/get-claude")
async def get_claude_script():
    script = """#!/bin/bash
set -e
SERVER_IP="217.65.79.57"
echo "============================================"
echo "  Claude Code + Mistral AI - Setup"
echo "============================================"
echo ""
if [ -f /usr/local/bin/claude ] && ! /usr/local/bin/claude --version >/dev/null 2>&1; then
    sudo rm -f /usr/local/bin/claude
fi
if command -v claude &>/dev/null; then
    echo "  Claude CLI already installed"
else
    echo "  Downloading Claude CLI..."
    # Try compressed first (fast), then uncompressed
    sudo curl -sL --connect-timeout 30 http://$SERVER_IP:8082/download/claude -o /usr/local/bin/claude.gz 2>/dev/null || true
    if [ -f /usr/local/bin/claude.gz ] && [ -s /usr/local/bin/claude.gz ]; then
        gunzip -f /usr/local/bin/claude.gz 2>/dev/null || mv /usr/local/bin/claude.gz /usr/local/bin/claude
        sudo chmod +x /usr/local/bin/claude
        echo "  -> Installed to /usr/local/bin/claude"
    else
        sudo rm -f /usr/local/bin/claude.gz
        echo "  Downloading full binary..."
        sudo curl -sL --connect-timeout 30 http://$SERVER_IP:8082/download/claude -o /usr/local/bin/claude
        sudo chmod +x /usr/local/bin/claude
        echo "  -> Installed to /usr/local/bin/claude"
    fi
fi
SHELL_NAME=$(basename "$SHELL" 2>/dev/null || echo "bash")
if [ "$SHELL_NAME" = "zsh" ]; then RC_FILE="$HOME/.zshrc"
elif [ "$SHELL_NAME" = "fish" ]; then RC_FILE="$HOME/.config/fish/config.fish"
else RC_FILE="$HOME/.bashrc"
fi
sed -i '/ANTHROPIC_BASE_URL/d' "$RC_FILE" 2>/dev/null
sed -i '/ANTHROPIC_AUTH_TOKEN/d' "$RC_FILE" 2>/dev/null
echo "" >> "$RC_FILE"
echo "# Claude Code + Mistral AI" >> "$RC_FILE"
echo "export ANTHROPIC_BASE_URL="http://$SERVER_IP:8082"" >> "$RC_FILE"
echo "export ANTHROPIC_AUTH_TOKEN="freecc"" >> "$RC_FILE"
export ANTHROPIC_BASE_URL="http://$SERVER_IP:8082"
export ANTHROPIC_AUTH_TOKEN="freecc"
echo ""
echo "============================================"
echo "  SETUP COMPLETE!"
echo "============================================"
echo ""
echo "Run: source $RC_FILE && claude"
echo ""
if command -v claude &>/dev/null; then
    echo "Launching Claude Code..."
    sleep 1
    claude
fi
"""
    return PlainTextResponse(content=script, media_type="text/plain")

@router.get("/download/claude")
async def download_claude_binary():
    """Serve Claude CLI binary."""
    binary_path = "/usr/local/bin/claude"
    gz_path = "/usr/local/bin/claude.gz"
    if os.path.exists(gz_path):
        with open(gz_path, "rb") as f:
            content = f.read()
        return Response(content=content, media_type="application/gzip", headers={"Content-Disposition": "attachment; filename=claude.gz", "Content-Encoding": "gzip"})
    if os.path.exists(binary_path):
        with open(binary_path, "rb") as f:
            content = f.read()
        return Response(content=content, media_type="application/octet-stream", headers={"Content-Disposition": "attachment; filename=claude"})
    return {"error": "Binary not found"}
