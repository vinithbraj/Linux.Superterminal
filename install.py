#!/usr/bin/env bash
set -e

echo "🧠 SuperTerm Setup Script (with virtual environment)"
echo "===================================================="
echo ""

# Variables
VENV_DIR=".superterm_env"
MODEL=${1:-llama3}

# Step 1: Ensure Python3 & venv
if ! command -v python3 >/dev/null 2>&1; then
  echo "Installing Python3..."
  sudo apt update && sudo apt install -y python3 python3-venv python3-pip
fi

# Step 2: Create and activate virtual environment
if [ ! -d "$VENV_DIR" ]; then
  echo "📦 Creating virtual environment at $VENV_DIR"
  python3 -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"
echo "✅ Virtual environment activated: $VENV_DIR"
echo ""

# Step 3: Upgrade pip & install dependencies
pip install --upgrade pip
pip install requests setuptools wheel

# Step 4: Install Ollama (system-wide)
if ! command -v ollama >/dev/null 2>&1; then
  echo "📦 Installing Ollama..."
  curl -fsSL https://ollama.com/install.sh | sh
  echo "✅ Ollama installed."
else
  echo "✅ Ollama already installed."
fi

# Step 5: Start Ollama service
echo "🚀 Starting Ollama service..."
sudo systemctl enable ollama || true
sudo systemctl start ollama || true
sleep 3

# Step 6: Pull the model
echo "📥 Pulling model: $MODEL"
ollama pull "$MODEL"

# Step 7: Verify server health
echo "🔎 Checking Ollama server..."
if curl -s http://localhost:11434/api/tags | grep -q "$MODEL"; then
  echo "✅ Ollama is running and model '$MODEL' is available."
else
  echo "❌ Ollama service check failed."
  echo "Run 'sudo systemctl status ollama' to troubleshoot."
  deactivate
  exit 1
fi

# Step 8: Install SuperTerm
if [ -f "setup.py" ]; then
  echo "📦 Installing SuperTerm package into virtual env..."
  pip install -e .
else
  echo "⚠️ setup.py not found. Run this script from the project root."
  deactivate
  exit 1
fi

# Step 9: Create run helper
cat <<EOF > run_superterm.sh
#!/usr/bin/env bash
source "$VENV_DIR/bin/activate"
superterm "\$@"
EOF

chmod +x run_superterm.sh

echo ""
echo "🎉 Installation complete!"
echo "------------------------------------------------------"
echo "To start SuperTerm, run:"
echo "    ./run_superterm.sh"
echo ""
echo "Your virtual environment is located in: $VENV_DIR"
echo "To manually activate it:"
echo "    source $VENV_DIR/bin/activate"
echo ""
echo "Enjoy your LLM-powered terminal 🚀"
