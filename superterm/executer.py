import subprocess
import shlex
import sys
import os

def run_command(command: str):
    """Run shell command safely. Attach to terminal if it's interactive."""
    try:
        # Detect interactive commands
        interactive_keywords = ["nano", "vi", "vim", "less", "top", "htop", "man"]
        if any(command.strip().startswith(k) for k in interactive_keywords):
            # Run interactively (no output capture)
            os.system(command)
            return "\n[Exited interactive command]"
        else:
            # Run non-interactive normally
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True
            )
            output = result.stdout.strip() or result.stderr.strip() or "[No output]"
            return f"STDOUT:\n{output}"
    except Exception as e:
        return f"[Error running command: {e}]"