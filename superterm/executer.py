import subprocess
import os
import sys

def run_command(command: str):
    """Run shell command with live streaming output (like real terminal)."""
    try:
        interactive_keywords = [
            "nano", "apt", "vi", "vim", "less", "top", "htop", "man", "watch", "tail -f"
        ]

        # If interactive tool, hand off directly
        if any(command.strip().startswith(k) for k in interactive_keywords):
            os.system(command)
            return "\n[Exited interactive command]"

        # Stream output live
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True,
            cwd=os.getcwd()
        )

        # Print stdout as it arrives
        for line in process.stdout:
            sys.stdout.write(f"\033[0m{line}\033[0m")
            sys.stdout.flush()

        # Print stderr as it arrives (in red)
        for line in process.stderr:
            sys.stdout.write(f"\033[91m{line}\033[0m")
            sys.stdout.flush()

        process.wait()

        if process.returncode == 0:
            return "\n✅ Command completed successfully"
        else:
            return f"\n❌ Command exited with code {process.returncode}"

    except Exception as e:
        return f"\033[91m[Error running command: {e}]\033[0m"
