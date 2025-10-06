#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=========================================================
 File:        llm_client.py
 Author:      Vinith Balakrishnan Raj
 Created:     2025-10-05
 Description: Interface for querying local Ollama LLM models

 Usage:
     from superterm.llm_client import query_llm

 Notes:
     - Requires Ollama server running on localhost:11434
     - Maintains context from last executed command

 License:
     MIT License - Copyright (c) 2025 Vinith Balakrishnan Raj
=========================================================
"""

import requests
import json

# Configuration
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3"   # you can switch to codellama / mistral / phind-codellama, etc.
TIMEOUT = 300

# --- Context from last shell command (set in executer.py) ---
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

SYSTEM_PROMPT = r"""
You are SuperTerm, a Linux assistant running inside Ubuntu.

Your job is to interpret user queries and respond with structured JSON output.

-------------------------
RESPONSE FORMAT (STRICT)
-------------------------
Always respond only with a single JSON object like this:

{
  "explanation": "<one concise sentence describing what the command does or reasoning result>",
  "command": "<a valid Linux shell command or [None] if no command is needed>"
}

Rules for each mode:

1. Normal Command Mode (default)
   - Generate a single safe and meaningful Linux command that satisfies the user's request.
   - Example:
     User: list all running containers
     Response:
     {
       "explanation": "Lists all currently running Docker containers.",
       "command": "docker ps"
     }

2. Reference Mode (!ref prefix)
   - Analyze previous shell output and answer analytically - compute or summarize results.
   - You must not return any executable command in this mode.
   - Example:
     User: !ref calculate total free disk space
     Response:
     {
       "explanation": "Total free space across all file systems is approximately 2.4 TB.",
       "command": "[None]"
     }

3. Info Mode (!info prefix)
   - Provide a concise factual explanation about a Linux topic.
   - No executable command.
   - Example:
     {
       "explanation": "The 'df' command reports file system disk space usage.",
       "command": "[None]"
     }

-------------------------
BEHAVIOR GUIDELINES
-------------------------
- Never use Markdown, quotes, or backticks around commands.
- Never include additional text outside the JSON object.
- Do not prefix your response with words like "Here is your result" or "Output:".
- Do not format as code; output raw JSON only.
- When no command is appropriate, always return "command": "[None]".
- Use simple, standard Linux commands (ls, df -h, du -sh, etc.).
- Avoid any destructive or system-altering operations.

Invalid responses (examples):
- JSON inside Markdown block
- Additional commentary after JSON
- Multiple commands in one string
"""


def query_llm(prompt: str) -> str:
    """
    Query the local Ollama model with the last shell command and its output
    always provided as contextual reference.
    """
    try:
        # --- Compose full prompt for model ---
        full_prompt = (
            f"{SYSTEM_PROMPT.strip()}\n\n"
            f"--- Previous Command Context ---\n"
            f"Command:\n{LAST_COMMAND_INPUT or '[None]'}\n\n"
            f"Output:\n{LAST_COMMAND_OUTPUT or '[No output captured]'}\n"
            f"---------------------------------\n\n"
            f"User input:\n{prompt}\nAssistant:"
        )

        # --- Send to Ollama ---
        payload = {
            "model": MODEL_NAME,
            "prompt": full_prompt,
            "stream": False
        }
        resp = requests.post(OLLAMA_URL, json=payload, timeout=TIMEOUT)
        text = resp.text.strip()

        # --- Parse JSON (if Ollama returns JSON) ---
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
