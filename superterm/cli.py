import typer
from superterm.llm_client import query_llm
from superterm.executer import run_command
import re
import readline
import os
from pathlib import Path

# Persistent history file
HISTORY_FILE = Path.home() / ".superterm_cmd_history"

# Load previous history
if HISTORY_FILE.exists():
    readline.read_history_file(HISTORY_FILE)

# Limit history length and enable completion
readline.set_history_length(1000)
readline.parse_and_bind("tab: complete")               # Tab autocompletion
readline.parse_and_bind('"\\C-r": reverse-search-history')  # Ctrl+R search

app = typer.Typer()  # Typer expects this app instance

def add_to_history(command: str):
    """Add executed command to readline history if not duplicate or empty."""
    if not command:
        return
    hist_len = readline.get_current_history_length()
    last = readline.get_history_item(hist_len) if hist_len else None
    if last != command:
        readline.add_history(command)

def parse_response(response: str):
    """Extract Command and Explanation lines from LLM output."""
    match = re.search(r"Command:\s*(.*?)\nExplanation:\s*(.*)", response, re.S)
    if match:
        return match.group(1).strip(), match.group(2).strip()
    return response.strip(), "No explanation found."

@app.command()
def run():
    """Interactive SuperTerm loop."""
    print("🧠 SuperTerm — AI-powered Ubuntu Terminal (local model)")
    print("Type normal Linux commands, or prefix with ! to ask the LLM. Ctrl+C to exit.\n")

    while True:
        try:
            user_input = input("> ").strip()
            if not user_input:
                continue

            # Exit
            if user_input.lower() in ["exit", "quit"]:
                break

            # 🔹 Info-only mode: respond but don’t store
            if user_input.startswith("!info"):
                info_prompt = user_input[1:].strip()
                print(f"🧠 Info request: {info_prompt}")
                response = query_llm(info_prompt)
                print(f"\n💬 {response}\n")
                continue

            # 🔹 Command suggestion mode (LLM)
            if user_input.startswith("!"):
                llm_prompt = user_input[1:].strip()
                print(f"🧠 Sending to LLM: {llm_prompt}")

                response = query_llm(llm_prompt)
                command, explanation = parse_response(response)

                print(f"\n🔹 Suggested command: {command}")
                print(f"💬 {explanation}")

                confirm = input("Run it? [y/N] ").lower()
                if confirm == "y" and command and "Command:" not in command:
                    print(run_command(command))
                    add_to_history(command)  # ✅ only executed commands stored
                continue

            # 🔹 Direct user command
            print(f"⚙️  Executing: {user_input}")
            print(run_command(user_input))
            add_to_history(user_input)  # ✅ store only actually executed commands

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
