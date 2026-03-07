#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=========================================================
 File:        vllm_client.py
 Author:      Vinith Balakrishnan Raj
 Created:     2026-03-06
 Description: Interface for querying local vLLM OpenAI-compatible models

 Usage:
     from superterm.vllm_client import query_llm

 Notes:
     - Requires vLLM server running on localhost:8000
     - Maintains context from last executed command

 License:
     MIT License - Copyright (c) 2026 Vinith Balakrishnan Raj
=========================================================
"""

import json
import os

import requests

from superterm.llm_context import get_last_context, set_last_context

# Configuration
VLLM_BASE_URL = os.getenv("SUPERTERM_VLLM_BASE_URL", "http://localhost:8000/v1")
VLLM_CHAT_URL = f"{VLLM_BASE_URL.rstrip('/')}/chat/completions"
MODEL_NAME = os.getenv("SUPERTERM_MODEL_NAME", "Qwen/Qwen2.5-7B-Instruct")
TIMEOUT = int(os.getenv("SUPERTERM_LLM_TIMEOUT", "300"))

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
    """Query the local vLLM model with last shell command context."""
    try:
        last_command_input, last_command_output = get_last_context()

        user_prompt = (
            "--- Previous Command Context ---\n"
            f"Command:\n{last_command_input or '[None]'}\n\n"
            f"Output:\n{last_command_output or '[No output captured]'}\n"
            "---------------------------------\n\n"
            f"User input:\n{prompt}\nAssistant:"
        )

        payload = {
            "model": MODEL_NAME,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT.strip()},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0,
            "stream": False,
        }

        resp = requests.post(VLLM_CHAT_URL, json=payload, timeout=TIMEOUT)
        resp.raise_for_status()

        data = resp.json()
        choices = data.get("choices", [])
        if choices and choices[0].get("message", {}).get("content"):
            return choices[0]["message"]["content"].strip()

        return json.dumps(data)

    except requests.ConnectionError:
        return "[Cannot connect to vLLM. Is the vLLM server running on localhost:8000?]"
    except requests.HTTPError as e:
        return f"[vLLM HTTP error: {e}]"
    except Exception as e:
        return f"[Unexpected error: {e}]"


__all__ = ["query_llm", "set_last_context"]
