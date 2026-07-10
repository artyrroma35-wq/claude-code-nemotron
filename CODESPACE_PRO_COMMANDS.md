# Exact Commands for Your Codespace Setup

## 1. Update code
```bash
cd /workspaces/claude-code-nemotron
git pull origin master
```

## 2. Create strong .env (recommended)
```bash
cat > .env << 'EOT'
NVIDIA_NIM_API_KEY="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"

MODEL="nvidia_nim/nvidia/nemotron-3-ultra-550b-a55b"

# === AUTOMATIC PRO MODE (this is the magic) ===
PRO_MODE=true
PRO_SYSTEM_PROMPT=true
MULTI_STEP_MODE=true          # Analysis → Design → Implementation → Critique
PROJECT_CONTEXT=true

# High quality parameters
PRO_TEMPERATURE=0.58
PRO_TOP_P=0.89
PRO_REASONING_BUDGET=25000

ENABLE_THINKING=true
ANTHROPIC_AUTH_TOKEN="freecc"
EOT
```

## 3. Start proxy (your exact command)
```bash
uv run uvicorn server:app --host 0.0.0.0 --port 8082
```

Leave this terminal open.

## 4. In a new terminal, launch Claude (your exact command)
```bash
ANTHROPIC_BASE_URL="http://localhost:8082" \
ANTHROPIC_AUTH_TOKEN="freecc" \
claude
```

## How to verify Pro Mode is active

In the **proxy terminal** (uvicorn) you should see:
```
PRO_MODE: Injected ultra-pro system prompt + context (multi-step=True)
```

If you see this → automatic injection is working.

## Quick toggles

Want even stronger multi-step?
```bash
# Edit .env
MULTI_STEP_MODE=true
PRO_REASONING_BUDGET=30000

# Then restart proxy (Ctrl+C + run again)
```

Want maximum quality right now:
```bash
PRO_TEMPERATURE=0.52
PRO_REASONING_BUDGET=32000
MULTI_STEP_MODE=true
```

Then restart the proxy.
