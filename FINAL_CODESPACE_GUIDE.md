# GitHub Codespaces — Самый простой способ

## Шаг 1: Создай Codespace
1. Перейди: https://github.com/artyrroma35-wq/claude-code-nemotron
2. Нажми большую зелёную кнопку **Code**
3. Выбери вкладку **Codespaces**
4. Нажми **Create codespace on master**

Подожди 40–60 секунд.

## Шаг 2: Установи проект
В терминале внизу выполни одну команду:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh && uv sync
```

## Шаг 3: Вставь свой ключ NVIDIA
```bash
cp .env.example .env
```

Открой файл `.env` (в проводнике слева) и замени строку:

```dotenv
NVIDIA_NIM_API_KEY="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"
```

## Шаг 4: Запусти сервер
```bash
uv run uvicorn server:app --host 0.0.0.0 --port 8082
```

**Оставь этот терминал открытым!**

## Шаг 5: Сделай порт публичным (ОБЯЗАТЕЛЬНО!)
1. Вверху найди вкладку **PORTS**
2. Найди строку с портом **8082**
3. Кликни на иконку **глобуса** (🌐) в колонке "Visibility"
4. Выбери **Public**

## Шаг 6: Запусти Claude Code
Открой **новый терминал** (кнопка `+` или `Ctrl+Shift+5`)

Выполни:

```bash
ANTHROPIC_BASE_URL="http://localhost:8082" \
ANTHROPIC_AUTH_TOKEN="freecc" \
claude
```

Готово! Теперь ты общаешься с **Nemotron 3 Ultra 550B** как с Claude Code.

---

**Файлы с инструкциями в репозитории:**
- `QUICK_CODESPACE.md` — короткая версия
- `CODESPACE_INSTRUCTIONS.md` — подробная версия
