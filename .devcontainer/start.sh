#!/bin/bash
set -e
cd /workspaces/claude-code-nemotron 2>/dev/null || cd /root/claude-code-proxy 2>/dev/null || cd /home
pip install -e . 2>/dev/null | tail -1
nohup python3 -m uvicorn server:app --host 0.0.0.0 --port 8082 --log-level info > /tmp/proxy.log 2>&1 &
sleep 3
curl -s http://localhost:8082/health && echo " - Proxy OK" || echo "FAIL: cat /tmp/proxy.log"
echo ""
echo "ANTHROPIC_BASE_URL=http://localhost:8082 ANTHROPIC_AUTH_TOKEN=freecc claude"
