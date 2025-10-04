import subprocess

def run_command(cmd: str) -> str:
    """Safely executes a shell command and returns combined output."""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True
        )
        return f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
    except Exception as e:
        return f"Error executing command: {e}"
