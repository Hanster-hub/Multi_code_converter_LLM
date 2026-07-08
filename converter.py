import os
import io
import sys
import subprocess
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(override=True)

openrouter_api_key = os.getenv("OPENROUTER_API_KEY")

openai_client = OpenAI()
openrouter_client = OpenAI(
    api_key=openrouter_api_key,
    base_url="https://openrouter.ai/api/v1",
)

MODELS = ["gpt-5", "x-ai/grok-4", "google/gemini-2.5-pro", "openai/gpt-oss-120b"]

CLIENTS = {
    "gpt-5": openai_client,
    "x-ai/grok-4": openrouter_client,
    "google/gemini-2.5-pro": openrouter_client,
    "openai/gpt-oss-120b": openrouter_client,
}

LANG_CONFIG = {
    "py": {
        "name": "Python",
        "extension": "py",
    },
    "cpp": {
        "name": "C++",
        "extension": "cpp",
        "compile_command": ["cl", "main.cpp", "/O2", "/Fe:main.exe"],
        "run_command": [".\\main.exe"],
    },
    "rs": {
        "name": "Rust",
        "extension": "rs",
        "compile_command": [
            "rustc", "main.rs",
            "-C", "opt-level=3",
            "-C", "target-cpu=native",
            "-o", "main.exe",
        ],
        "run_command": [".\\main.exe"],
    },
}


def system_prompt_for(lang_from, lang_to):
    from_name = LANG_CONFIG[lang_from]["name"]
    to_name = LANG_CONFIG[lang_to]["name"]
    return f"""
Convert {from_name} code into high performance {to_name} code.

Respond ONLY with valid {to_name} code.
Do NOT include markdown, explanations, or text outside the code.

Requirements:
- The output must produce identical results.
- Optimize for performance (use O(n) where possible instead of O(n^2)).
- The code must compile and run without errors.

Language-specific rules:

For Rust:
- Use proper Rust formatting syntax (e.g. {{:.6}} instead of {{:.6f}})
- Use `println!` correctly
- Use `fn main()` as entry point

For C++:
- Use standard C++ (MSVC compatible)
- Include necessary headers (iostream, vector, etc.)
- Use `int main()`

General:
- Do NOT use Python-specific syntax
- Do NOT assume dynamic typing
- Ensure all variables are properly declared

Return ONLY the code.
"""


def user_prompt_for(code, lang_from, lang_to):
    from_name = LANG_CONFIG[lang_from]["name"]
    to_name = LANG_CONFIG[lang_to]["name"]
    ext = LANG_CONFIG[lang_to]["extension"]
    compile_cmd = LANG_CONFIG[lang_to].get("compile_command")

    if compile_cmd:
        compile_text = (
            f"\nThe output will be written to main.{ext} and compiled using:\n"
            f"{compile_cmd}\n"
        )
    else:
        compile_text = f"\nThe output will be written to main.{ext} and executed directly.\n"

    return (
        f"Convert the following {from_name} code into {to_name}.\n\n"
        f"{compile_text}\n"
        f"Respond ONLY with {to_name} code.\n\n"
        f"Input code:\n\n"
        f"```{from_name.lower()}\n"
        f"{code}\n"
        f"```"
    )


def messages_for(code, lang_from, lang_to):
    return [
        {"role": "system", "content": system_prompt_for(lang_from, lang_to)},
        {"role": "user", "content": user_prompt_for(code, lang_from, lang_to)},
    ]


def clean_code(code):
    if "```" in code:
        parts = code.split("```")
        if len(parts) >= 2:
            code = parts[1]
            lines = code.split("\n")
            if lines and lines[0].strip().isalpha():
                code = "\n".join(lines[1:])
    return code.strip()


def write_output(code, lang_key):
    ext = LANG_CONFIG[lang_key]["extension"]
    with open(f"main.{ext}", "w", encoding="utf-8") as f:
        f.write(code)


def port(model, code, lang_from, lang_to):
    client = CLIENTS[model]
    reasoning_effort = "high" if "gpt" in model else None
    response = client.chat.completions.create(
        model=model,
        messages=messages_for(code, lang_from, lang_to),
        reasoning_effort=reasoning_effort,
    )
    return clean_code(response.choices[0].message.content)


def run_python(code):
    buffer = io.StringIO()
    old_stdout = sys.stdout
    sys.stdout = buffer
    try:
        exec(code, {"__builtins__": __builtins__})
        output = buffer.getvalue()
    except Exception as e:
        output = f"Error: {e}"
    finally:
        sys.stdout = old_stdout
    return output or "<empty>"


def compile_and_run(code, lang_to):
    cfg = LANG_CONFIG[lang_to]
    try:
        write_output(code, lang_to)
        compile_result = subprocess.run(
            cfg["compile_command"], check=True, text=True, capture_output=True
        )
        run_result = subprocess.run(
            cfg["run_command"], check=True, text=True, capture_output=True
        )
        return run_result.stdout or "<empty>"
    except subprocess.CalledProcessError as e:
        return f"An error occurred:\n{e.stderr}"


def run_code(code, lang_key):
    if lang_key == "py":
        return run_python(code)
    return compile_and_run(code, lang_key)
