# Multi-Language Code Converter

A Gradio app that uses LLMs to convert and run code across **Python**, **C++**, and **Rust**. Paste code in one language, pick a target, and get an optimized, compile-ready translation with one-click execution.

## Features

- **LLM-powered conversion** — structured prompts enforce valid, optimized output with no markdown or explanations leaked through
- **Multi-model support** — switch between GPT-5 (OpenAI), Grok-4, Gemini 2.5 Pro, and GPT-OSS-120B (via OpenRouter) from the UI
- **One-click run** — execute Python inline; compile and run C++ (MSVC) and Rust (`rustc`) via subprocess
- **System-aware** — `system_info.py` detects your OS, CPU, and toolchain so the LLM can generate correct compile flags

## Requirements

- Python 3.11+
- **For C++**: MSVC (`cl.exe`) — run from a Visual Studio Developer Command Prompt
- **For Rust**: `rustc` installed via [rustup](https://rustup.rs/)

## Setup

1. Install Python dependencies

   ```bash
   pip install -r requirements.txt
   ```

2. Create a `.env` file with your API keys

   ```env
   OPENAI_API_KEY=your_openai_key
   OPENROUTER_API_KEY=your_openrouter_key
   ```

3. Run the app

   ```bash
   python app.py
   ```

## Project Structure

```
.
├── app.py          # Gradio UI
├── converter.py    # Core logic: LLM conversion, prompts, compile & run
├── styles.py       # Gradio CSS theme
├── system_info.py  # OS, CPU, and toolchain detection utility
└── requirements.txt
```

## Models

| Model | Provider |
|-------|----------|
| `gpt-5` | OpenAI (direct) |
| `x-ai/grok-4` | OpenRouter |
| `google/gemini-2.5-pro` | OpenRouter |
| `openai/gpt-oss-120b` | OpenRouter |
