from superterm.llm_client import query_llm
from superterm.executor import run_command
import re

def parse_response(response: str):
    """Extract command and explanation from model output."""
    match = re.search(r"Command:\s*(.*?)\nExplanation:\s*(.*)", response, re.S)
    if match:
        return match.group(1).strip(), match.group(2).strip()
    return response.strip(), "No explanation found."

def main():
    print("🧠 SuperTerm — AI-powered Ubuntu Terminal (local model)")
    print("Type natural commands. Ctrl+C to exit.\n")

    while True:
        try:
            user_input = input("> ")
            if user_input.lower() in ["exit", "quit"]:
                break

            response = query_llm(user_input)
            command, explanation = parse_response(response)

            print(f"\n🔹 Suggested command: {command}")
            print(f"💬 {explanation}")

            confirm = input("Run it? [y/N] ").lower()
            if confirm == "y":
                print(run_command(command))
        except KeyboardInterrupt:
            print("\nExiting SuperTerm.")
            break
        except Exception as e:
            print("Error:", e)

if __name__ == "__main__":
    main()
