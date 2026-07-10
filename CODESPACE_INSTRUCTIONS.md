# 🚀 Запуск в GitHub Codespaces

Это самый простой способ запустить проект **без установки ничего на свой компьютер**.

## Пошаговая инструкция

### 1. Открой Codespace

1. Перейди по ссылке:  
   **https://github.com/artyrroma35-wq/claude-code-nemotron**

2. Нажми зелёную кнопку **Code** (вверху справа)

3. Перейди на вкладку **Codespaces**

4. Нажми **Create codespace on master**

5. Подожди 30–60 секунд, пока откроется VS Code в браузере.

### 2. Установи зависимости (один раз)

В терминале внизу выполни:

```bash
# Установка uv (если ещё нет)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Установка проекта
uv sync
```

### 3. Добавь свой NVIDIA API ключ

**Вариант A — через .env (рекомендуется)**

```bash
cp .env.example .env
```

Открой файл `.env` и вставь свой ключ:

```dotenv
NVIDIA_NIM_API_KEY="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"

MODEL="nvidia_nim/nvidia/nemotron-3-ultra-550b-a55b"
ENABLE_THINKING=true
```

**Вариант B — быстро (без файла)**

```bash
export NVIDIA_NIM_API_KEY="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"
```

### 4. Запусти прокси-сервер

```bash
uv run uvicorn server:app --host 0.0.0.0 --port 8082
```

Оставь этот терминал открытым.

### 5. Настрой порт (важно!)

1. В левой панели найди вкладку **PORTS** (или нажми `Ctrl+Shift+P` → "Ports: Focus on Ports View")
2. Найди порт **8082**
3. Кликни на иконку "globe" (🌐) рядом с портом, чтобы сделать его **Public**
4. Скопируй публичный URL (он будет вида `https://xxxx-8082.app.github.dev`)

### 6. Запусти Claude Code

Открой **новый терминал** (кнопка "Split Terminal" или `Ctrl+Shift+5`)

Выполни:

```bash
ANTHROPIC_BASE_URL="http://localhost:8082" \
ANTHROPIC_AUTH_TOKEN="freecc" \
claude
```

Готово! Теперь ты общаешься с **Nemotron 3 Ultra** через интерфейс Claude Code.

---

## Дополнительно

### Как использовать в Codespace как в VS Code

1. Установи расширение **Claude Code** (если ещё не стоит)
2. Открой настройки (`Ctrl+,`) и добавь:

```json
"claude-code.environmentVariables": [
  { "name": "ANTHROPIC_BASE_URL", "value": "http://localhost:8082" },
  { "name": "ANTHROPIC_AUTH_TOKEN", "value": "freecc" }
]
```

3. Перезагрузи расширение.

### Остановить сервер

В терминале с сервером нажми `Ctrl+C`.

### Перезапуск

Просто снова запусти:

```bash
uv run uvicorn server:app --host 0.0.0.0 --port 8082
```

---

## Полезные советы для Codespaces

- Codespace автоматически выключается через 30 минут бездействия.
- Твой `.env` файл сохраняется внутри Codespace.
- Чтобы добавить ключ навсегда — используй **GitHub Secrets** (Settings → Secrets and variables → Codespaces).

**Готово!** Теперь у тебя есть полноценный Claude Code на базе Nemotron 3 Ultra прямо в браузере.
