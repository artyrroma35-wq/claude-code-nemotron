# 🚀 Claude Pro Mode — Full Guide

You now have a **significantly upgraded** experience with Nemotron 3 Ultra.

## Quick Start (Recommended)

```bash
# 1. Start proxy + launch in Pro quality
./bin/claude-pro
```

Or even stronger modes:

```bash
./bin/claude-architect     # For system design
./bin/claude-super         # Very high quality
./bin/claude-max           # Maximum intelligence mode
```

All of them set better parameters (lower temperature, high reasoning budget, etc.).

---

## Prompt Templates (Copy & Paste)

These dramatically improve quality. Start your conversations with them.

### Best general prompt
```bash
cat prompts/claude-pro-system.txt
```

### Architecture work
```bash
cat prompts/architect.txt
```

### Senior engineer quality
```bash
cat prompts/senior-engineer.txt
```

### Ultra mode
```bash
cat prompts/ultra.txt
```

### Self-critique (very powerful)
```bash
cat prompts/self-critique.txt
```

### Full rigorous workflow
```bash
cat prompts/full-workflow.txt
```

**Usage example:**
```
You are an elite software engineer. [paste content from prompts/ultra.txt]

Now: Design and implement ...
```

---

## Pro Prompting Techniques

**For maximum quality:**

```
Think like a principal staff engineer. Consider multiple approaches and their trade-offs. Show your reasoning, then implement the best solution at a very high standard.
```

**For architecture:**

```
Act as a principal architect. Explore 3 different designs, evaluate trade-offs (scalability, complexity, maintainability), then recommend and detail the best one.
```

**For code:**

```
Write production-grade, clean, well-tested code. Focus on clarity and long-term maintainability.
```

**Self-review trick:**

```
After you finish, critically review your own work and suggest improvements.
```

---

## Current Quality Stack

| Layer                    | Setting                          | Effect                     |
|--------------------------|----------------------------------|----------------------------|
| Model                    | Nemotron 3 Ultra 550B            | Very strong reasoning      |
| Thinking                 | Enabled + high budget            | Shows internal reasoning   |
| Temperature              | 0.55 – 0.65                      | More consistent & precise  |
| Max tokens               | 32k–65k                          | Long, complete answers     |
| Launch scripts           | Tuned per mode                   | Best params per use case   |
| Prompt templates         | Multiple expert personas         | Better role + instructions |

---

## Daily Recommendations

- **Normal work** → `./bin/claude-pro`
- **Big design / refactoring** → `./bin/claude-architect`
- **Most important / complex task** → `./bin/claude-max` + paste `prompts/ultra.txt`

---

## Future Ideas (already planned)

- Auto-inject system prompt
- Self-critique loop
- Project memory
- Multi-agent workflows

You already have one of the strongest free setups possible right now.

Enjoy the higher quality!
