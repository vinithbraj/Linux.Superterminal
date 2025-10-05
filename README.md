# 🧠 SuperTerm  
### AI-Powered Terminal Assistant for Ubuntu & Linux

**SuperTerm** is an intelligent command-line interface that blends the power of a Linux shell with the understanding of AI.  
It lets you type natural-language commands (e.g., “!show large log files”) and translates them into real shell operations — while explaining every action before it runs.

SuperTerm connects to a **local Ollama server** for reasoning, allowing you to run open LLMs like `llama3`, `mistral`, or `phi3` fully offline on your own system.

---

## 🌍 Overview

SuperTerm brings **AI to your terminal** — locally, securely, and transparently.  
It runs a small Python application on top of your system shell and communicates with an [Ollama](https://ollama.com) instance running in the background.

You can:
- run commands normally (`ls`, `grep`, etc.), or  
- ask for things conversationally (`!find all python files modified today`)  

SuperTerm interprets your intent, proposes a shell command, explains what it will do, and executes it safely inside your terminal.

---

## 🚀 Key Features

- 🗣️ **Natural-Language Commands** — Use `!` to ask questions instead of memorizing syntax.  
- 💡 **Explanations** — Before execution, SuperTerm explains what the command does.  
- 🧩 **Persistent History** — Stores only executed commands in `~/.superterm_cmd_history`.  
- 🧠 **Local AI Model Integration** — Uses Ollama for local, private, offline reasoning.  
- 🪄 **Desktop Launcher** — Automatically adds an icon to your Ubuntu desktop and menu.  
- 🔒 **No Cloud Calls** — Everything runs locally; no internet required after install.

---

## 🧰 Requirements

- Ubuntu 22.04+ or any modern Linux distro  
- `python3`, `python3-venv`, and `pip`  
- [Docker](https://docs.docker.com/get-docker/) (for Ollama GPU support, optional)  
- [Ollama](https://ollama.com) (the local AI server)

---

## 🧠 Dependency: Ollama Server

SuperTerm depends on the **Ollama** server to interpret natural language.  
You must have Ollama running before launching SuperTerm.

### 🔗 Official Setup Instructions:
👉 [https://hub.docker.com/r/ollama/ollama](https://hub.docker.com/r/ollama/ollama)

### 🐋 Run Ollama via Docker (recommended)
```bash
docker run -d --gpus=all \
  -v ollama:/root/.ollama \
  -p 11434:11434 \
  --name ollama \
  ollama/ollama
### 

