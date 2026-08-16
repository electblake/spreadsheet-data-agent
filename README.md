---
title: Spreadsheet Data Agent
emoji: 📊
colorFrom: blue
colorTo: pink
sdk: gradio
sdk_version: 6.17.3
python_version: '3.12.12'
app_file: app.py
pinned: false
license: apache-2.0
preload_from_hub:
  - mradermacher/Spreadsheet-RL-4B-GGUF Spreadsheet-RL-4B.Q4_K_M.gguf
models:
  - Spreadsheet-RL/Spreadsheet-RL-4B
  - mradermacher/Spreadsheet-RL-4B-GGUF
---

# Spreadsheet Data Agent

[Code](https://github.com/electblake/Spreadsheet-RL-Data-Agent) | [Demo](https://huggingface.co/spaces/electblake/spreadsheet-data-agent) | [Paper](https://arxiv.org/abs/2605.22642) | [Spreadsheet-RL Model](https://huggingface.co/Spreadsheet-RL/Spreadsheet-RL-4B)

A basic text-and-file inference app for Spreadsheet-RL-4B, modeled on the prompt entry point in the Spreadsheet-RL agent-system diagram.

The app accepts a system prompt, user prompt, and optional text or spreadsheet file. Its quantization selector exposes the 4B GGUF variants captured in the project reference material, with Q4_K_M selected by default. Inference runs directly on the selected quantized tensors through llama.cpp without converting them into full PyTorch weights.

ZeroGPU support is enabled with the `spaces` package and `@spaces.GPU`. Select ZeroGPU in the Hugging Face Space hardware settings after deployment.
