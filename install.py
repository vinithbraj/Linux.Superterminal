#!/usr/bin/env bash
set -e

echo "🚀 Setting up SuperTerm..."

# --- 1️⃣ Create venv ---
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

# --- 7️⃣ Check Ollama ---
echo "🔎 Checking Ollama..."
if pgrep -x "ollama" >/dev/null; then
  echo "✅ Ollama is running."
else
  echo "⚠️  Ollama not running. Start it with:  ollama serve"
fi

if ollama list | grep -q "llama3"; then
  echo "✅ Model 'llama3' found."
else
  echo "⚠️  Model 'llama3' not found. Run:  ollama pull llama3"
fi

# --- 8️⃣ Create desktop entry ---
echo "🖥️  Creating desktop entry..."
python3 - <<'EOF'
import os
from pathlib import Path

HOME = Path.home()
project_dir = Path.cwd()
desktop_dir = HOME / "Desktop"
apps_dir = HOME / ".local/share/applications"

entry_name = "superterm.desktop"
app_name = "SuperTerm"
comment = "AI-powered Ubuntu Terminal"
script_path = project_dir / "run_superterm.sh"
icon_path = project_dir / "icon.png"

entry_content = f"""[Desktop Entry]
Version=1.0
Type=Application
Name={app_name}
Comment={comment}
Exec=gnome-terminal -- bash -c "cd {project_dir} && ./run.sh; exec bash"
Icon={icon_path if icon_path.exists() else "utilities-terminal"}
Terminal=false
StartupNotify=true
Categories=Utility;Development;
"""

# Write to ~/.local/share/applications and Desktop
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

# Mark trusted (GNOME/Mint)
os.system(f'gio set "{apps_dir / entry_name}" metadata::trusted true 2>/dev/null')
os.system(f'gio set "{desktop_dir / entry_name}" metadata::trusted true 2>/dev/null')
print("🎉 SuperTerm launcher ready! Search in menu or double-click the desktop icon.")
EOF

echo
echo "🎉 Installation complete!"
echo "------------------------------------------------------"
echo "To start SuperTerm manually, run:"
echo "    source .superterm_env/bin/activate && superterm"
echo
echo "Or simply click the SuperTerm icon on your Desktop / Applications menu 🧠"
