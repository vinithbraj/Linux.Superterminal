#!/usr/bin/env bash
# -*- coding: utf-8 -*-
#=========================================================
# File:        startvllm.sh
# Author:      Vinith Balakrishnan Raj
# Created:     2026-03-06
# Description: Docker-based vLLM OpenAI server startup script
#
# Usage:
#     bash startvllm.sh
#
# Notes:
#     - Checks Docker installation and daemon status
#     - Launches or starts existing vLLM container
#     - Enables GPU support
#     - Verifies vLLM API readiness
#
# License:
#     MIT License - Copyright (c) 2026 Vinith Balakrishnan Raj
#=========================================================

set -e

CONTAINER_NAME="vllm"
IMAGE_NAME="vllm/vllm-openai:latest"
MODEL_NAME="${VLLM_MODEL:-Qwen/Qwen2.5-1.5B-Instruct}"
HOST_PORT="${VLLM_PORT:-8000}"
CONTAINER_PORT="8000"
HF_CACHE_HOST="${HF_CACHE_HOST:-$HOME/.cache/huggingface}"

# 8GB VRAM-friendly defaults (override with env vars as needed)
VLLM_DTYPE="${VLLM_DTYPE:-float16}"
VLLM_GPU_MEMORY_UTILIZATION="${VLLM_GPU_MEMORY_UTILIZATION:-0.85}"
VLLM_MAX_MODEL_LEN="${VLLM_MAX_MODEL_LEN:-2048}"
VLLM_MAX_NUM_SEQS="${VLLM_MAX_NUM_SEQS:-2}"
VLLM_CPU_OFFLOAD_GB="${VLLM_CPU_OFFLOAD_GB:-6}"
VLLM_SWAP_SPACE_GB="${VLLM_SWAP_SPACE_GB:-8}"
VLLM_EXTRA_ARGS="${VLLM_EXTRA_ARGS:-}"

# --- 1. Check Docker installation ---
if ! command -v docker &> /dev/null; then
  echo "Docker is not installed or not in PATH."
  echo "Please install Docker before continuing."
  exit 1
fi

# --- 2. Check if Docker daemon is running ---
if ! sudo systemctl is-active --quiet docker; then
  echo "Starting Docker service..."
  sudo systemctl start docker
fi

# Ensure Hugging Face cache directory exists on host
mkdir -p "$HF_CACHE_HOST"

# --- 3. Check for existing vLLM container ---
if sudo docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
  echo "vLLM container already exists."
  if [ "$(sudo docker inspect -f '{{.State.Running}}' "$CONTAINER_NAME")" != "true" ]; then
    echo "Starting existing vLLM container..."
    sudo docker start "$CONTAINER_NAME"
  else
    echo "vLLM container already running."
  fi
else
  echo "Launching new vLLM container with GPU support..."
  echo "Model: $MODEL_NAME"
  echo "vLLM params: dtype=$VLLM_DTYPE, gpu_mem_util=$VLLM_GPU_MEMORY_UTILIZATION, max_len=$VLLM_MAX_MODEL_LEN, max_num_seqs=$VLLM_MAX_NUM_SEQS, cpu_offload_gb=$VLLM_CPU_OFFLOAD_GB, swap_space_gb=$VLLM_SWAP_SPACE_GB"
  sudo docker run -d \
    --gpus all \
    -p "${HOST_PORT}:${CONTAINER_PORT}" \
    -v "${HF_CACHE_HOST}:/root/.cache/huggingface" \
    --name "$CONTAINER_NAME" \
    "$IMAGE_NAME" \
    --model "$MODEL_NAME" \
    --dtype "$VLLM_DTYPE" \
    --gpu-memory-utilization "$VLLM_GPU_MEMORY_UTILIZATION" \
    --max-model-len "$VLLM_MAX_MODEL_LEN" \
    --max-num-seqs "$VLLM_MAX_NUM_SEQS" \
    --cpu-offload-gb "$VLLM_CPU_OFFLOAD_GB" \
    --swap-space "$VLLM_SWAP_SPACE_GB" \
    --enforce-eager \
    $VLLM_EXTRA_ARGS
fi

# --- 4. Verify vLLM API is responding ---
echo "Checking vLLM readiness on http://localhost:${HOST_PORT}/v1/models ..."
for _ in {1..20}; do
  if command -v curl &> /dev/null && curl -fsS "http://localhost:${HOST_PORT}/v1/models" > /dev/null; then
    echo "vLLM is ready."
    exit 0
  fi
  sleep 2
done

echo "vLLM may still be starting. Check logs with: sudo docker logs -f ${CONTAINER_NAME}"
