#!/usr/bin/env bash
set -e

echo "🚀 Setting up SuperTerm..."

# --- 0️⃣ Ensure Python venv support ---
echo "🐍 Checking Python venv module..."
sudo apt-get update -y
sudo apt-get install -y python3-venv python3.12-venv || true

# --- 1️⃣ Create virtual environment ---
if [ ! -d ".superterm_env" ]; then
  echo "📦 Creating virtual environment..."
  python3 -m venv .superterm_env
fi

# --- 2️⃣ Activate venv ---
source .superterm_env/bin/activate

# --- 3️⃣ Upgrade pip ---
echo "⬆️  Upgrading pip..."
pip install --upgrade pip setuptools wheel

# --- 4️⃣ Install Python dependencies ---
echo "📥 Installing dependencies..."
pip install typer rich requests

# --- 5️⃣ Ensure __init__.py exists ---
if [ ! -f "superterm/__init__.py" ]; then
  echo "⚙️  Creating __init__.py..."
  touch superterm/__init__.py
fi

# --- 6️⃣ Install SuperTerm in editable mode ---
echo "🔧 Installing SuperTerm (editable)..."
pip install -e .

# --- 7️⃣ Ollama Setup (user choice) ---
echo
echo "🧠 Ollama Setup Options"
echo "------------------------"
echo "1️⃣ Install Ollama locally on this machine"
echo "2️⃣ Use Ollama via Docker (recommended for GPU)"
echo "3️⃣ Skip Ollama setup for now"
echo
read -p "Choose an option (1/2/3): " OLLAMA_OPTION

case $OLLAMA_OPTION in
  1)
    echo "⚙️ Installing Ollama locally..."
    curl -fsSL https://ollama.com/install.sh | sh
    echo "✅ Ollama installed successfully."
    ;;
  2)
    echo "🐋 Using Ollama via Docker..."
    echo "📎 Please follow the official Docker instructions here:"
    echo "👉 https://hub.docker.com/r/ollama/ollama"
    echo
    echo "Example command (CPU only):"
    echo "   docker run -d -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama"
    echo
    echo "For GPU (if supported):"
    echo "   docker run -d --gpus=all -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama"
    echo
    ;;
  3)
    echo "⚠️ Skipping Ollama setup. You can configure it later."
    ;;
  *)
    echo "❌ Invalid option. Skipping Ollama setup."
    ;;
esac

# --- 8️⃣ Create desktop entry ---
echo "🖥️  Creating desktop entry..."
python3 <<'EOF'
import os
from pathlib import Path

HOME = Path.home()
project_dir = Path(__file__).resolve().parent
desktop_dir = HOME / "Desktop"
apps_dir = HOME / ".local/share/applications"

entry_name = "superterm.desktop"
app_name = "SuperTerm"
comment = "AI-powered Ubuntu Terminal"
script_path = project_dir / "run.sh"
icon_path = project_dir / "icon.png"

entry_content = f"""[Desktop Entry]
Version=1.0
Type=Application
Name={app_name}
Comment={comment}
Exec=gnome-terminal --title="SuperTerm – AI Terminal" -- bash -c "cd {project_dir} && ./run.sh; exec bash"
Icon={icon_path if icon_path.exists() else "utilities-terminal"}
Terminal=false
StartupNotify=true
Categories=Utility;Development;
"""

apps_dir.mkdir(parents=True, exist_ok=True)
(apps_dir / entry_name).write_text(entry_content)
os.chmod(apps_dir / entry_name, 0o755)

if desktop_dir.exists():
    (desktop_dir / entry_name).write_text(entry_content)
    os.chmod(desktop_dir / entry_name, 0o755)
    print(f"✅ Created Desktop icon: {desktop_dir / entry_name}")
else:
    print("⚠️  Desktop folder not found — skipped desktop shortcut.")

print(f"✅ Created application entry: {apps_dir / entry_name}")

os.system(f'gio set "{apps_dir / entry_name}" metadata::trusted true 2>/dev/null')
os.system(f'gio set "{desktop_dir / entry_name}" metadata::trusted true 2>/dev/null')
print('🎉 SuperTerm launcher ready! Search in menu or double-click the desktop icon.')
EOF

echo
echo "🎉 Installation complete!"
echo "------------------------------------------------------"
echo "To start SuperTerm manually, run:"
echo "    source .superterm_env/bin/activate && superterm"
echo
echo "Or simply click the SuperTerm icon on your Desktop / Applications menu 🧠"
echo
echo "💡 If you chose Docker Ollama, make sure the container is running before launching SuperTerm."
