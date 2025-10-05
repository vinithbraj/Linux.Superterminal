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
readline.parse_and_bind("tab: complete")
readline.parse_and_bind('"\\C-r": reverse-search-history')

app = typer.Typer()


# ============================================================
# Utility functions
# ============================================================

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
    match = re.search(r"Explanation:\s*(.*?)\nCommand:\s*(.*)", response, re.S)
    if match:
        return match.group(1).strip(), match.group(2).strip()
    return response.strip(),"none"


def change_directory(path: str):
    """Change SuperTerm’s working directory persistently."""
    try:
        os.chdir(os.path.expanduser(path))
    except FileNotFoundError:
        print(f"❌ Directory not found: {path}")
    except Exception as e:
        print(f"❌ Error changing directory: {e}")


# ============================================================
# Main interactive loop
# ============================================================

@app.command()
def run():
    """Interactive SuperTerm loop."""
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
                print(f"🧠 Sending to LLM: {llm_prompt}")

                response = query_llm(llm_prompt)
                explanation, command = parse_response(response)

                # If LLM returns no actual command, just display reasoning
                if not command or command.lower() in ("[none]", "none"):
                    print(f"\n💬 {explanation}\n")
                    continue

                print(f"\n🔹 Suggested command: {command}")
                print(f"💬 {explanation}")

                # --- Only prompt if the command is truly runnable ---
                if command:
                    if "none" not in command.lower():
                        confirm = input(f"Run it -> {command}? [y/N] ").strip().lower()
                        if confirm == "y" and "command:" not in command.lower():
                            if command.startswith("cd "):
                                change_directory(command[3:].strip())
                            else:
                                print(run_command(command))
                            add_to_history(command)
                    else:
                        print("\n💬 No command to execute.\n")
                continue

            # --- Normal shell command ---
            if user_input.startswith("cd "):
                change_directory(user_input[3:].strip())
            else:
                print(run_command(user_input))
            add_to_history(user_input)

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
