#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=========================================================
 File:        cli.py
 Author:      Vinith Balakrishnan Raj
 Created:     2025-10-05
 Description: AI-powered terminal interface with LLM integration

 Usage:
     superterm

 Notes:
     - Requires Ollama running locally
     - Prefix commands with '!' for AI assistance

 License:
     MIT License - Copyright (c) 2025 Vinith Balakrishnan Raj
=========================================================
"""

# --- Standard library imports ---
import itertools
import os
import re
import readline
import subprocess
import sys
import threading
import time
from pathlib import Path
import json

# --- Third-party imports ---
import typer

# --- Local application imports ---
from superterm.executer import run_command
from superterm.llm_client import query_llm as query_ollama_llm
from superterm.vllm_client import query_llm as query_vllm_llm



# ============================================================
# Globals functions
# ============================================================

HISTORY_FILE = Path.home() / ".superterm_cmd_history"

if HISTORY_FILE.exists():
    readline.read_history_file(HISTORY_FILE)

readline.set_history_length(1000)
readline.parse_and_bind("tab: complete")
readline.parse_and_bind('"\\C-r": reverse-search-history')

app = typer.Typer()
SUGGESTED_COMMAND_COLOR = typer.colors.BRIGHT_CYAN
INJECTED_PROMPT = "\001\033[32m\002{cwd} > \001\033[0m\002"
SUPPORTED_BACKENDS = {"ollama", "vllm"}
DEFAULT_LLM_BACKEND = os.getenv("SUPERTERM_LLM_BACKEND", "ollama").strip().lower()
if DEFAULT_LLM_BACKEND not in SUPPORTED_BACKENDS:
    DEFAULT_LLM_BACKEND = "ollama"

LLM_BACKEND = DEFAULT_LLM_BACKEND
QUERY_LLM = query_vllm_llm if LLM_BACKEND == "vllm" else query_ollama_llm

# ============================================================
# Utility functions
# ============================================================

def add_to_history(command: str):
    if not command:
        return
    hist_len = readline.get_current_history_length()
    last = readline.get_history_item(hist_len) if hist_len else None
    if last != command:
        readline.add_history(command)

def parse_response(response: str):
    def load_json_with_escape_repair(text: str):
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # Repair invalid JSON escapes often produced in shell commands,
            # e.g. "\;" in `find ... -exec ... \;`
            repaired = re.sub(r'\\(?!["\\/bfnrtu])', r"\\\\", text)
            return json.loads(repaired)

    def extract_json_string_field(text: str, field: str) -> str:
        # Fallback: pull a JSON-like string field even if full JSON is malformed.
        pattern = rf'"{re.escape(field)}"\s*:\s*"((?:\\.|[^"\\])*)"'
        match = re.search(pattern, text, flags=re.DOTALL)
        if not match:
            return ""
        raw_value = match.group(1)
        repaired = re.sub(r'\\(?!["\\/bfnrtu])', r"\\\\", raw_value)
        try:
            return json.loads(f'"{repaired}"')
        except json.JSONDecodeError:
            return raw_value.replace('\\"', '"').replace("\\\\", "\\")

    try:
        json_start = response.find("{")
        json_end = response.rfind("}") + 1
        json_text = response[json_start:json_end].strip()

        data = load_json_with_escape_repair(json_text)

        explanation = data.get("explanation", "").strip()
        command = data.get("command", "").strip()
        return explanation, command
    except Exception as e:
        print(f"Warning: Failed to parse LLM response as JSON: {e}")
        explanation = extract_json_string_field(response, "explanation") or response.strip()
        command = extract_json_string_field(response, "command") or "none"
        return explanation.strip(), command.strip()

def change_directory(path: str):
    try:
        os.chdir(os.path.expanduser(path))
    except FileNotFoundError:
        print(f"Directory not found: {path}")
    except Exception as e:
        print(f"Error changing directory: {e}")

def spinning_cursor(message=""):
    spinner = itertools.cycle(["|", "/", "-", "\\"])
    stop_flag = threading.Event()

    def spin():
        while not stop_flag.is_set():
            sys.stdout.write(f"\r{message} " + next(spinner))
            sys.stdout.flush()
            time.sleep(0.1)
        sys.stdout.flush()

    thread = threading.Thread(target=spin)
    thread.daemon = True  # auto-terminate with main process
    thread.start()

    # return a closure to stop it safely
    return lambda: stop_flag.set()

def select_llm_backend():
    global LLM_BACKEND, QUERY_LLM

    default_choice = "2" if DEFAULT_LLM_BACKEND == "vllm" else "1"
    print("Select LLM backend:")
    print("  1) Ollama (localhost:11434)")
    print("  2) vLLM (localhost:8000)")
    choice = input(f"Choose backend [1/2] (default {default_choice}): ").strip().lower()

    if choice in {"", default_choice}:
        selected = DEFAULT_LLM_BACKEND
    elif choice in {"1", "ollama"}:
        selected = "ollama"
    elif choice in {"2", "vllm"}:
        selected = "vllm"
    else:
        print(f"Invalid choice '{choice}', using default backend: {DEFAULT_LLM_BACKEND}")
        selected = DEFAULT_LLM_BACKEND

    LLM_BACKEND = selected
    QUERY_LLM = query_vllm_llm if LLM_BACKEND == "vllm" else query_ollama_llm

def initialize_llm_backend():
    script_name = "startvllm.sh" if LLM_BACKEND == "vllm" else "startllm.sh"
    repo_root = Path(__file__).resolve().parent.parent
    script_path = repo_root / script_name

    if not script_path.exists():
        print(f"Warning: startup script not found: {script_path}")
        return

    print(f"Initializing {LLM_BACKEND} backend using {script_name} ...")
    try:
        result = subprocess.run(
            ["bash", str(script_path)],
            cwd=str(repo_root),
            check=False,
        )
        if result.returncode != 0:
            print(
                f"Warning: {script_name} exited with code {result.returncode}. "
                "Continuing, but LLM calls may fail until backend is running."
            )
    except Exception as e:
        print(
            f"Warning: failed to run {script_name}: {e}. "
            "Continuing without automatic backend startup."
        )

def execute_shell_command(command: str):
    command = command.strip()
    if not command:
        return

    #Prevent accidental execution of AI/LLM commands
    if "!" in command:
        return

    try:
        if command.startswith("cd "):
            change_directory(command[3:].strip())
        else:
            result = run_command(command)
            if result:
                print(result)
        add_to_history(command)
    except Exception as e:
        print(f"Error executing command '{command}': {e}")

def process_user_prompt(user_input: str):
    def has_executable_command(command: str) -> bool:
        normalized = command.strip().lower()
        return normalized not in {"", "none", "[none]"}

    if user_input.startswith("!"):
        llm_prompt = user_input[1:].strip()
        stop_spinner = spinning_cursor()
        response = QUERY_LLM(llm_prompt)
        stop_spinner()

        explanation, command = parse_response(response)

        print(f"{explanation}\n")

        if has_executable_command(command):

            # show it once, colorized for visibility
            typer.secho(
                f"Suggested command: {command}\n",
                fg=SUGGESTED_COMMAND_COLOR,
            )

            # preload it into the input line without reprinting
            def prefill():
                readline.insert_text(command)

            readline.set_startup_hook(prefill)
            try:
                user_input = input(
                    INJECTED_PROMPT.format(cwd=os.getcwd())
                ).strip()
            finally:
                readline.set_startup_hook(None)
            process_user_prompt(user_input)
    else:
        execute_shell_command(user_input)




# ============================================================
# Main interactive loop
# ============================================================

@app.command()
def run():
    print("SuperTerm — AI-powered Ubuntu Terminal")
    select_llm_backend()
    initialize_llm_backend()
    print(f"LLM backend: {LLM_BACKEND}")
    print("Tip: Prefix '!' for AI (e.g., '!ref why?', '!info ubuntu'), normal commands run as shell.\n")

    while True:
        try:
            prompt = f"{os.getcwd()} > "
            user_input = input(prompt).strip()
            if not user_input:
                continue

            # Exit
            if user_input.lower() in ["exit", "quit"]:
                break

            process_user_prompt(user_input)

        except KeyboardInterrupt:
            print("\nExiting SuperTerm.")
            break
        except Exception as e:
            print(f"Error: {e}")
        finally:
            try:
                readline.write_history_file(HISTORY_FILE)
            except Exception:
                pass


if __name__ == "__main__":
    app()
