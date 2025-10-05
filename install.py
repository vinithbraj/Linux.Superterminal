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

echo
echo "🎉 Installation complete!"
echo "------------------------------------------------------"
echo "To start SuperTerm, run:"
echo "    source .superterm_env/bin/activate && superterm"
echo
echo "Enjoy your LLM-powered terminal 🧠"
