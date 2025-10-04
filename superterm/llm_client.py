import requests
import json

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3"

def query_llm(prompt: str) -> str:
    """
    Query the local LLM to suggest a command and explain it.
    Returns a tuple (command, explanation).
    """
    system_prompt = (
        "You are an Ubuntu terminal expert. "
        "When the user describes a task, respond with:\n\n"
        "Command: <exact command>\n"
        "Explanation: <short, clear explanation>\n\n"
        "Example:\n"
        "Command: sudo apt install ffmpeg\n"
        "Explanation: Installs FFmpeg from Ubuntu repositories."
    )

    data = {
        "model": MODEL,
        "prompt": f"{system_prompt}\n\nUser: {prompt}",
        "stream": False
    }

    response = requests.post(OLLAMA_URL, json=data)
    text = json.loads(response.text)["response"]
    return text.strip()
