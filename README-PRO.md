# Claude + Nemotron 3 Ultra — Pro Mode

This repository is configured for **maximum quality** with the free Nemotron 3 Ultra 550B model.

## Quick Start (Pro Mode)

```bash
# 1. Start the enhanced proxy
./start-claude-pro.sh

# 2. In another terminal
claude
```

Or use the dedicated pro launcher:

```bash
./bin/claude-pro
```

## Quality Optimizations Applied

| Setting              | Value     | Reason                          |
|----------------------|-----------|---------------------------------|
| `ENABLE_THINKING`    | true      | Full reasoning output           |
| `TEMPERATURE`        | 0.65      | More consistent, high-quality   |
| `TOP_P`              | 0.92      | Better coherence                |
| `MAX_TOKENS`         | 32768     | Large, thoughtful responses     |
| `REASONING_BUDGET`   | 16384     | Strong chain-of-thought         |

## Best Prompting Techniques

### For Maximum Quality

```text
Think like a principal engineer. Consider 3 different approaches, evaluate trade-offs, then implement the best one with full reasoning.
```

### Architecture Tasks

```text
You are a principal architect. Design a scalable solution. Show alternatives considered and why you chose this approach.
```

### Code Quality

```text
Write production-grade code. Focus on clarity, robustness, and maintainability. Include proper error handling and tests.
```

### Deep Refactoring

```text
Refactor this with a focus on long-term maintainability. Show before/after with detailed explanation of improvements.
```

## Included Prompt Templates

- `prompts/claude-pro-system.txt` — Main high-quality system prompt
- `prompts/architect.txt` — Principal architect persona
- `prompts/senior-engineer.txt` — Staff engineer persona

You can copy these into your conversation or use them as inspiration.

## Pro Tips

1. **Always ask for reasoning** — Nemotron is very strong at it.
2. **Give big context** — The 550B model handles large codebases well.
3. **Iterate with quality feedback**:
   - "Make this more robust"
   - "Improve the design"
   - "Add proper observability"
4. **Use structured workflows**:
   - "Analyze → Design → Implement → Review"

## Current Limitations & Workarounds

- The proxy doesn't auto-inject custom system prompts yet (future improvement)
- Best results come from **explicit instructions** in your messages

## Want Even More Power?

Future ideas implemented here:
- [ ] Custom system prompt injection
- [ ] Quality scoring / self-critique loop
- [ ] Multi-step agent mode
- [ ] Project memory

For now, the combination of **strong model + good prompting + tuned parameters** gives excellent results.

Enjoy building at a higher level.
