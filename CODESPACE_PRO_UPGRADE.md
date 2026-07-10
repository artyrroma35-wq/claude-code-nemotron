# Codespaces + Pro Mode (Automatic High Quality)

## Что было сделано (полный апгрейд)

1. **Автоматическая инъекция сильного системного промпта** — больше не нужно копировать вручную
2. **Multi-step режим** — Analysis → Design → Implementation → Critique
3. **Project context** — Claude автоматически видит структуру проекта (CLAUDE.md, ARCHITECTURE.md и т.д.)

Всё происходит на уровне прокси.

---

## Как запустить в Codespaces (твои команды)

### 1. Обнови код

```bash
cd /workspaces/claude-code-nemotron
git pull origin master
```

### 2. Создай/обнови `.env`

```bash
cat > .env << 'EOT'
NVIDIA_NIM_API_KEY="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"

MODEL="nvidia_nim/nvidia/nemotron-3-ultra-550b-a55b"

# === PRO MODE (самое важное) ===
PRO_MODE=true
PRO_SYSTEM_PROMPT=true
MULTI_STEP_MODE=true          # ← Включи для Analysis → Design → Impl → Critique
PROJECT_CONTEXT=true

# Качественные параметры
PRO_TEMPERATURE=0.60
PRO_TOP_P=0.90
PRO_REASONING_BUDGET=22000

ENABLE_THINKING=true
ANTHROPIC_AUTH_TOKEN="freecc"
EOT
```

### 3. Запусти прокси (твоя команда)

```bash
uv run uvicorn server:app --host 0.0.0.0 --port 8082
```

**Оставь терминал открытым.**

### 4. В новом терминале запускай Claude

```bash
ANTHROPIC_BASE_URL="http://localhost:8082" \
ANTHROPIC_AUTH_TOKEN="freecc" \
claude
```

---

## Как проверить, что Pro Mode работает

В логе прокси (терминал с uvicorn) ищи строку:

```
PRO_MODE: Injected ultra-pro system prompt + context
```

Если видишь — значит автоматическая инъекция сработала.

---

## Режимы

- `MULTI_STEP_MODE=false` (по умолчанию) — просто очень сильный промпт
- `MULTI_STEP_MODE=true` — принудительно заставляет Claude проходить фазы:
  1. Analysis
  2. Design
  3. Implementation
  4. Critique

Можно переключать в `.env` и перезапускать прокси.

---

## Дополнительно

Хочешь максимальное качество прямо сейчас:

```bash
# В .env поставь
MULTI_STEP_MODE=true
PRO_TEMPERATURE=0.55
PRO_REASONING_BUDGET=30000
```

Потом перезапусти прокси.

Готово. Теперь каждый запрос будет автоматически получать мощный системный промпт + контекст проекта.
