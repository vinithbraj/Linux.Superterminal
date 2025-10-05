#!/usr/bin/env bash
set -e

# --- Change to script directory ---
cd "$(dirname "$0")"

# --- 1️⃣ Activate Python virtual environment ---
if [ ! -d ".superterm_env" ]; then
  echo "❌ Virtual environment not found. Please run ./install.sh first."
  exit 1
fi

source .superterm_env/bin/activate
echo "🐍 Activated SuperTerm virtual environment."

# --- 2️⃣ Check Docker installation ---
if ! command -v docker &> /dev/null; then
  echo "❌ Docker is not installed or not in PATH."
  echo "   Please install Docker before continuing."
  exit 1
fi

# --- 3️⃣ Check if Docker daemon is running ---
if ! sudo systemctl is-active --quiet docker; then
  echo "🚀 Starting Docker service..."
  sudo systemctl start docker
fi

# --- 4️⃣ Check for existing Ollama container ---
if sudo docker ps -a --format '{{.Names}}' | grep -q '^ollama$'; then
  echo "🧱 Ollama container already exists."
  if [ "$(sudo docker inspect -f '{{.State.Running}}' ollama)" != "true" ]; then
    echo "▶️  Starting existing Ollama container..."
    sudo docker start ollama
  else
    echo "✅ Ollama container already running."
  fi
else
  echo "🐋 Launching new Ollama container with GPU support..."
  sudo docker run -d \
    --gpus=all \
    -v ollama:/root/.ollama \
    -p 11434:11434 \
    --name ollama \
    ollama/ollama
fi

# --- 5️⃣ Verify Ollama is responding ---
echo "⏳ Checking Ollama readiness..."
sleep 3
if ! sudo docker exec ollama ollama list &> /dev/null; then
  echo "⚠️  Ollama may not be ready yet. Waiting a few seconds..."
  sleep 5
fi

# --- 6️⃣ Run SuperTerm ---
echo "🧠 Starting SuperTerm..."
exec superterm
