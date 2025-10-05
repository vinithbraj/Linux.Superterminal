import requests
import json

# Configuration
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3"   # you can switch to codellama / mistral / phind-codellama, etc.
TIMEOUT = 300
SESSION_HISTORY = []
MAX_HISTORY = 2   # keep last 5 exchanges

# --- 🧠 System prompt (persistent instruction) ---
SYSTEM_PROMPT = """
You are SuperTerm, a Linux assistant inside Ubuntu.

If input starts with '!info', reply with a short factual paragraph.

Otherwise, output two lines only:
Command: <safe shell command>
Explanation: <brief purpose>

Use standard Linux tools (ls, df -h, du -sh).
Mount VMware folders with:
sudo vmhgfs-fuse .host:/ /mnt/hgfs -o allow_other
Avoid destructive commands.
"""



def query_llm(prompt: str) -> str:
    """
    Query the local Ollama model with short-term memory of previous commands.
    """
    try:
        # Build rolling context
        context = "\n".join(SESSION_HISTORY[-MAX_HISTORY:])
        full_prompt = (
            f"{SYSTEM_PROMPT.strip()}\n\n"
            f"Conversation so far:\n{context}\n\n"
            f"User: {prompt}\nAssistant:"
        )

        payload = {"model": MODEL_NAME, "prompt": full_prompt, "stream": False}
        resp = requests.post(OLLAMA_URL, json=payload, timeout=TIMEOUT)
        text = resp.text.strip()

        try:
            data = json.loads(text)
            if "response" in data:
                result = data["response"].strip()
            else:
                result = text
        except json.JSONDecodeError:
            result = text

        # Save to session history
        SESSION_HISTORY.append(f"User: {prompt}")
        SESSION_HISTORY.append(f"Assistant: {result}")

        return result

    except requests.ConnectionError:
        return "[Cannot connect to Ollama. Is 'ollama serve' running?]"
    except Exception as e:
        return f"[Unexpected error: {e}]"
