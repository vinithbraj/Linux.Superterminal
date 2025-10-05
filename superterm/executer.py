import subprocess
import os

def run_command(command: str):
    """Run shell command safely. Attach TTY for interactive commands like 'watch'."""
    try:
        # Commands that require a real terminal (TTY)
        interactive_keywords = [
            "nano", "vi", "vim", "less", "top", "htop", "man", "watch", "tail -f"
        ]

        # If it starts with an interactive command, attach to terminal directly
        if any(command.strip().startswith(k) for k in interactive_keywords):
            os.system(command)
            return "\n[Exited interactive command]"

        # Otherwise, run normally (captured, colorized output)
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            cwd=os.getcwd()
        )

        if result.returncode == 0:
            # ✅ Normal output — Ubuntu gray
            output = result.stdout.strip() or "[No output]"
            return f"\033[0m{output}\033[0m"
        else:
            # ❌ Error output — Ubuntu red
            error_output = result.stderr.strip() or "[Command failed with no stderr]"
            return f"\033[91m{error_output}\033[0m"

    except Exception as e:
        return f"\033[91m[Error running command: {e}]\033[0m"
