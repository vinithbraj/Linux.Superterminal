import typer
from superterm.llm_client import query_llm
from superterm.executer import run_command
import re

app = typer.Typer()  # 👈 define the app Typer expects

def parse_response(response: str):
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

            if user_input.lower() in ["exit", "quit"]:
                break

            # 🔹 NEW: If starts with '!', send to LLM
            if user_input.startswith("!"):
                llm_prompt = user_input[1:].strip()
                print(f"🧠 Sending to LLM: {llm_prompt}")

                response = query_llm(llm_prompt)
                command, explanation = parse_response(response)

                print(f"\n🔹 Suggested command: {command}")
                print(f"💬 {explanation}")

                confirm = input("Run it? [y/N] ").lower()
                if confirm == "y":
                    print(run_command(command))
                continue

            # 🔹 Otherwise, run it directly
            print(f"⚙️  Executing: {user_input}")
            print(run_command(user_input))

        except KeyboardInterrupt:
            print("\nExiting SuperTerm.")
            break
        except Exception as e:
            print("Error:", e)
