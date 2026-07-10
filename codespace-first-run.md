# First time running `claude` in Codespace

You are currently seeing the **Claude CLI setup wizard**.

## What to do right now:

1. **Choose theme**
   - Type `2` and press Enter (Dark mode is recommended)

2. After theme selection, it will show more screens.

3. When it asks about login / "How do you want to log in?":
   - Select **Anthropic Console** (or the first option)
   - A browser tab may open
   - **Close the browser tab** or ignore the "buy credits" page
   - Go back to the terminal

4. The CLI should now start the chat interface.

## Important reminders:

- Your proxy **must be running** in another terminal:
  ```bash
  uv run uvicorn server:app --host 0.0.0.0 --port 8082
  ```

- The environment variables are set for this session.

- Once you reach the chat prompt (usually `>` or a chat box), you can type normally.

## First test message

After setup, try typing:

```
Hello! What model are you currently using? Please confirm you are Nemotron 3 Ultra.
```

You should see thinking/reasoning output and then a response.
