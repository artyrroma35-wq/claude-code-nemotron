# ⚡ Быстрый запуск в GitHub Codespaces

## 1. Создай Codespace
Перейди сюда: https://github.com/artyrroma35-wq/claude-code-nemotron  
Нажми **Code** → **Codespaces** → **Create codespace on master**

## 2. Установи зависимости
В терминале выполни:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv sync
```

## 3. Добавь ключ (вставь свой)
```bash
cp .env.example .env
```

Открой `.env` и замени ключ:
```dotenv
NVIDIA_NIM_API_KEY="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"
```

## 4. Запусти сервер
```bash
uv run uvicorn server:app --host 0.0.0.0 --port 8082
```

## 5. Сделай порт публичным (ОБЯЗАТЕЛЬНО!)
- Перейди на вкладку **PORTS**
- Найди порт **8082**
- Кликни на иконку 🌐 (globe), чтобы сделать **Public**

## 6. Запусти Claude
Открой **новый терминал** и выполни:
```bash
ANTHROPIC_BASE_URL="http://localhost:8082" \
ANTHROPIC_AUTH_TOKEN="freecc" \
claude
```

Готово! Теперь ты используешь **Nemotron 3 Ultra** как Claude Code.
