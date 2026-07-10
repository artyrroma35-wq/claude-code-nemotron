# Claude Pro Mode — Enhanced Nemotron Experience

This setup turns the free Nemotron 3 Ultra into a **much stronger** coding experience.

## What's Improved

### 1. Better System Prompt
- Stronger architectural thinking
- Higher quality standards
- More deliberate reasoning

### 2. Optimized Parameters
- Lower temperature (0.7) for more consistent, high-quality output
- Higher max tokens (32k)
- Thinking mode always enabled

### 3. Quality-Focused Workflow

Use these techniques when talking to Claude:

**For deep work:**
```
Think step by step as a senior staff engineer. Consider multiple approaches and trade-offs before recommending a solution.
```

**For architecture:**
```
Act as a principal engineer. Design a scalable, maintainable solution. Explain the reasoning and alternatives considered.
```

**For code quality:**
```
Write production-grade code. Include proper error handling, logging, and tests. Follow best practices for this language.
```

**For refactoring:**
```
Refactor this code with a focus on clarity, performance, and maintainability. Show before/after with explanation.
```

## How to Launch "Pro Mode"

```bash
./start-claude-pro.sh
```

Then in a new terminal:

```bash
claude
```

## Recommended Settings Inside Claude

Once inside the CLI, you can use:

- `/model` — to confirm you're on Nemotron
- Large context tasks (it handles them well)
- Ask for explicit reasoning

## Pro Tips

1. **Ask for reasoning explicitly**
   - "Show your thinking process"
   - "Consider alternatives and trade-offs"

2. **Use structured requests**
   - "Analyze → Design → Implement → Test"

3. **Leverage the model size**
   - Nemotron 550B is very strong at complex reasoning
   - Give it big, multi-file tasks

4. **Iterate with quality feedback**
   - "Make this more robust"
   - "Improve the architecture"
   - "Add proper error handling"

## Future Enhancements (possible)

- Custom system prompt injection
- Tool use improvements
- Better memory / project context
- Multi-agent mode

Currently this is the strongest free configuration possible with Nemotron 3 Ultra.
