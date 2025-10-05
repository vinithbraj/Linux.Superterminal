import typer
from superterm.llm_client import query_llm
from superterm.executer import run_command
import re
import readline
import os
from pathlib import Path

# ============================================================
# 🧠 SuperTerm — AI-powered Ubuntu Terminal (local model)
# ============================================================

# Persistent history file
HISTORY_FILE = Path.home() / ".superterm_cmd_history"

# Load previous history
if HISTORY_FILE.exists():
    readline.read_history_file(HISTORY_FILE)

# History settings
readline.set_history_length(1000)
readline.parse_and_bind("tab: complete")               # Tab autocompletion
readline.parse_and_bind('"\\C-r": reverse-search-history')  # Ctrl+R search

app = typer.Typer()  # Typer expects this app instance


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
    # Match 'Command:' followed by anything (until 'Explanation:')
    match = re.search(r"Command:\s*(.*?)\s*(?:\n|$)Explanation:\s*(.*)", response, re.S | re.IGNORECASE)
    if match:
        command = match.group(1).strip()
        explanation = match.group(2).strip()
        return command, explanation
    else:
        # Fallback: if only one line is returned, treat whole thing as command
        return response.strip(), "No explanation found."



def change_directory(path: str):
    """Handle 'cd' commands internally so the working directory persists."""
    try:
        os.chdir(os.path.expanduser(path))
        print(f"📂 Changed directory to: {os.getcwd()}")
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
    print("🧠 SuperTerm — AI-powered Ubuntu Terminal (local model)")
    print("Type normal Linux commands, or prefix with ! to ask the LLM. Ctrl+C to exit.\n")

    while True:
        try:
            # Show current directory as part of the prompt
            prompt = f"{os.getcwd()} > "
            user_input = input(prompt).strip()
            if not user_input:
                continue

            # Exit
            if user_input.lower() in ["exit", "quit"]:
                print("👋 Goodbye!")
                break

            # 🔹 Info-only mode
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
                    if command.startswith("cd "):
                        change_directory(command[3:].strip())
                    else:
                        run_command(command)
                    add_to_history(command)
                continue

            # 🔹 Direct user command
            if user_input.startswith("cd "):
                change_directory(user_input[3:].strip())
            else:
                run_command(user_input)
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
