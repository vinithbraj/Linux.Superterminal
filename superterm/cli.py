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
import sys
import threading
import time
from pathlib import Path
import json

# --- Third-party imports ---
import typer

# --- Local application imports ---
from superterm.executer import run_command
from superterm.llm_client import query_llm



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
    """Parse LLM JSON output and return (explanation, command)."""
    try:
        # Trim whitespace and extract JSON portion if extra text is present
        json_start = response.find("{")
        json_end = response.rfind("}") + 1
        json_text = response[json_start:json_end].strip()

        data = json.loads(json_text)

        explanation = data.get("explanation", "").strip()
        command = data.get("command", "").strip()
        return explanation, command
    except Exception as e:
        print(f"⚠️  Failed to parse LLM response as JSON: {e}")
        return response.strip(), "none"

def change_directory(path: str):
    try:
        os.chdir(os.path.expanduser(path))
    except FileNotFoundError:
        print(f"  Directory not found: {path}")
    except Exception as e:
        print(f"❌ Error changing directory: {e}")

def spinning_cursor(message="🧠 Sending to LLM"):
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
            print(run_command(command))
        add_to_history(command)
    except Exception as e:
        print(f"❌ Error executing command '{command}': {e}")


# ============================================================
# Main interactive loop
# ============================================================

@app.command()
def run():
    print("🧠 SuperTerm — AI-powered Ubuntu Terminal")
    print("💡 Tip: Prefix '!' for AI (e.g., '!ref why?', '!info ubuntu'), normal commands run as shell.\n")

    while True:
        try:
            prompt = f"{os.getcwd()} > "
            user_input = input(prompt).strip()
            if not user_input:
                continue

            # Exit
            if user_input.lower() in ["exit", "quit"]:
                break

            # --- Handle AI-assisted modes ---
            if user_input.startswith("!"):
                llm_prompt = user_input[1:].strip()
                stop_spinner = spinning_cursor(f"🧠 Thinking...")
                response = query_llm(llm_prompt)
                stop_spinner()

                explanation, command = parse_response(response)

                print(f"💬 {explanation}\n")

                if command:
                    if "none" not in command.lower():

                        # show it once
                        print(f"💡 Suggested command: {command}\n")

                        # preload it into the input line without reprinting
                        def prefill():
                            readline.insert_text(command)

                        readline.set_startup_hook(prefill)
                        try:
                            user_input = input(f"{os.getcwd()} > ").strip()
                        finally:
                            readline.set_startup_hook(None)

            execute_shell_command(user_input)

        except KeyboardInterrupt:
            print("\nExiting SuperTerm.")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            try:
                readline.write_history_file(HISTORY_FILE)
            except Exception:
                pass


if __name__ == "__main__":
    app()
