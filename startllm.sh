#!/usr/bin/env bash
# -*- coding: utf-8 -*-
#=========================================================
# File:        startllm.sh
# Author:      Vinith Balakrishnan Raj
# Created:     2025-10-05
# Description: Docker-based Ollama LLM server startup script
#
# Usage:
#     bash startllm.sh
#
# Notes:
#     - Checks Docker installation and daemon status
#     - Launches or starts existing Ollama container
#     - Enables GPU support if available
#     - Verifies Ollama readiness
#
# License:
#     MIT License - Copyright (c) 2025 Vinith Balakrishnan Raj
#=========================================================

set -e

# --- 2. Check Docker installation ---
if ! command -v docker &> /dev/null; then
  echo "Docker is not installed or not in PATH."
  echo "   Please install Docker before continuing."
  exit 1
fi

# --- 3. Check if Docker daemon is running ---
if ! sudo systemctl is-active --quiet docker; then
  echo "Starting Docker service..."
  sudo systemctl start docker
fi

# --- 4. Check for existing Ollama container ---
if sudo docker ps -a --format '{{.Names}}' | grep -q '^ollama$'; then
  echo "Ollama container already exists."
  if [ "$(sudo docker inspect -f '{{.State.Running}}' ollama)" != "true" ]; then
    echo "Starting existing Ollama container..."
    sudo docker start ollama
  else
    echo "Ollama container already running."
  fi
else
  echo "Launching new Ollama container with GPU support..."
  sudo docker run -d \
    --gpus=all \
    -v ollama:/root/.ollama \
    -p 11434:11434 \
    -e OLLAMA_HOST=0.0.0.0 \
    -e OLLAMA_ORIGINS=* \
    --name ollama \
    ollama/ollama
fi

# --- 5. Verify Ollama is responding ---
echo "Checking Ollama readiness..."
sleep 3
if ! sudo docker exec ollama ollama list &> /dev/null; then
  echo "Ollama may not be ready yet. Waiting a few seconds..."
  sleep 5
fi