#!/bin/bash
set -e
cd "$(dirname "$0")"

# Start proxy in background
echo "Starting proxy..."
python3 -m uvicorn server:app --host 0.0.0.0 --port 8082 --log-level info &
PROXY_PID=$!
sleep 3

# Check if proxy is running
if curl -s http://localhost:8082/health > /dev/null 2>&1; then
    echo "Proxy is running on http://localhost:8082"
else
    echo "ERROR: Proxy failed to start!"
    exit 1
fi

# Run Claude Code
export ANTHROPIC_BASE_URL="http://localhost:8082"
export ANTHROPIC_AUTH_TOKEN="freecc"
echo ""
echo "Running Claude Code..."
echo "----------------------------------------"
claude 2>&1 || echo "Claude not found, try: npm install -g @anthropic-ai/claude-code"
echo "----------------------------------------"

# Cleanup
kill $PROXY_PID 2>/dev/null || true
