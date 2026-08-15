---
title: Spreadsheet Data Agent
emoji: 📊
colorFrom: blue
colorTo: pink
sdk: gradio
sdk_version: 6.24.0
python_version: '3.13'
app_file: app.py
pinned: false
license: apache-2.0
models:
  - Spreadsheet-RL/Spreadsheet-RL-4B
  - mradermacher/Spreadsheet-RL-4B-GGUF
---

# Spreadsheet Data Agent

A basic text-and-file inference app for Spreadsheet-RL-4B, modeled on the prompt entry point in the Spreadsheet-RL agent-system diagram.

The app accepts a system prompt, user prompt, and optional text or spreadsheet file. Its quantization selector exposes the 4B GGUF variants captured in the project reference material, with Q4_K_M selected by default.

ZeroGPU support is enabled with the `spaces` package and `@spaces.GPU`. Select ZeroGPU in the Hugging Face Space hardware settings after deployment.
