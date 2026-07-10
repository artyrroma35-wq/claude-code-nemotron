# Claude Code + Google Gemini (через Cloudflare Worker)

**Используйте Claude Code с Gemini 3.1 Flash Lite бесплатно**  
8 API ключей × Cloudflare Worker = обход региональных блокировок

## 🚀 Быстрый старт

### GitHub Codespaces (рекомендуется)

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://github.com/artyrroma35-wq/claude-code-nemotron)

1. Нажми кнопку выше или **Code → Codespaces → Create codespace on master**
2. Дождись загрузки (1-2 минуты)
3. Укажи свой Gemini API ключ в `.env`
4. Запусти: `python3 -m uvicorn server:app --host 0.0.0.0 --port 8082 &`
5. В новом терминале: `ANTHROPIC_BASE_URL=http://localhost:8082 ANTHROPIC_AUTH_TOKEN=freecc claude`

### Через сервер

```bash
curl -sL http://217.65.79.57:8082/get-claude | bash
export ANTHROPIC_BASE_URL="http://217.65.79.57:8082"
export ANTHROPIC_AUTH_TOKEN="freecc"
claude
```

### Локально

```bash
git clone https://github.com/artyrroma35-wq/claude-code-nemotron.git
cd claude-code-nemotron
pip install -e .
# Настрой .env с твоим Gemini ключом
python3 -m uvicorn server:app --host 0.0.0.0 --port 8082
# В другом терминале:
ANTHROPIC_BASE_URL=http://localhost:8082 ANTHROPIC_AUTH_TOKEN=freecc claude
```

## 📊 Модели

| Модель | Статус |
|---|---|
| **Gemini 3.1 Flash Lite** | ✅ **Стабильно** |
| Gemini 3.5 Flash | ⚠️ 503 (перегрузка) |
| Gemini 2.5 Flash | ✅ Работает |

## 🔑 API Ключи

8 ключей Google AI Studio, ротация через Cloudflare Worker (обход региона).

## 📁 File Manager

`http://ваш-сервер:8082/files/ui`

## 📊 Stats Dashboard

`http://ваш-сервер:8082/stats/ui`
