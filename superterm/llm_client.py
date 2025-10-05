import requests
import json

# Configuration
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3"   # you can switch to codellama / mistral / phind-codellama, etc.
TIMEOUT = 300

# --- 🔁 Context from last shell command (set in executer.py) ---
LAST_COMMAND_INPUT = None
LAST_COMMAND_OUTPUT = None


def set_last_context(cmd: str, output: str):
    """Update command context only when a real shell command is executed."""
    global LAST_COMMAND_INPUT, LAST_COMMAND_OUTPUT

    # ignore empty commands or AI prompts (those starting with '!')
    if not cmd or cmd.strip().startswith("!"):
        return  # preserve existing context

    # Update only for actual shell commands
    LAST_COMMAND_INPUT = cmd.strip()

    # Limit large outputs to last 8KB
    if output:
        trimmed_output = output.strip()
        if len(trimmed_output) > 8000:
            trimmed_output = trimmed_output[-8000:]
        LAST_COMMAND_OUTPUT = trimmed_output


# --- 🧠 System prompt (persistent LLM instruction) ---
SYSTEM_PROMPT = """
You are SuperTerm, a Linux assistant running inside Ubuntu.

Behavior Rules:
1. If input starts with 'info', provide a short, factual explanation of the topic. 
   - Do NOT output or suggest shell commands.
   - Your goal is to explain, not to execute.

2. If input starts with 'ref', analyze the provided previous shell command and its output to answer the user's question intelligently.
   - Perform reasoning, summarization, or **any necessary calculations or computations** directly in your response.
   - For example, if the previous command was 'df -h' or 'lsblk', and the user asks for total or free disk space, compute and state the value explicitly using the provided data.
   - Do NOT output or suggest shell commands.

4. For all other inputs, respond with exactly two lines:
   Explanation: <one concise sentence describing what that command does>
   Command: <a real, safe Linux command that answers the query>

Guidelines:
- Only include a single valid command after "Command:" when rule 4 applies.
- Never include ref, info, or explanatory text in the "Command:" line.
- Use the context of the last executed shell command and its output ONLY when relevant.
- For ref and info queries (alone or together), always produce analytical or computed results — not executable commands.
- If the user question does not require a command, you may output:
   Command: [None]
   Explanation: <your reasoning or conclusion>
- Use standard Linux tools (ls, df -h, du -sh, awk, grep, etc.) only when generating commands for rule 4.
- Avoid destructive or system-altering operations.
- Mount VMware folders with:
  sudo vmhgfs-fuse .host:/ /mnt/hgfs -o allow_other
"""





def query_llm(prompt: str) -> str:
    """
    Query the local Ollama model with the last shell command and its output
    always provided as contextual reference.
    """
    try:
        # --- 🧱 Compose full prompt for model ---
        full_prompt = (
            f"{SYSTEM_PROMPT.strip()}\n\n"
            f"--- Previous Command Context ---\n"
            f"Command:\n{LAST_COMMAND_INPUT or '[None]'}\n\n"
            f"Output:\n{LAST_COMMAND_OUTPUT or '[No output captured]'}\n"
            f"---------------------------------\n\n"
            f"User input:\n{prompt}\nAssistant:"
        )

        # --- 📨 Send to Ollama ---
        payload = {
            "model": MODEL_NAME,
            "prompt": full_prompt,
            "stream": False
        }
        resp = requests.post(OLLAMA_URL, json=payload, timeout=TIMEOUT)
        text = resp.text.strip()

        # --- 🧩 Parse JSON (if Ollama returns JSON) ---
        try:
            data = json.loads(text)
            result = data.get("response", text).strip()
        except json.JSONDecodeError:
            result = text

        return result

    except requests.ConnectionError:
        return "[Cannot connect to Ollama. Is 'ollama serve' running?]"
    except Exception as e:
        return f"[Unexpected error: {e}]"
