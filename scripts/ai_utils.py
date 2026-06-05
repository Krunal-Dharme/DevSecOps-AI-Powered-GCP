#!/usr/bin/env python3
"""
Simple LLM client using ONLY Ollama (mistral:7b)
Requires:
  - Ollama running: ollama serve
  - Model pulled: ollama pull mistral:7b
"""

import os
import json
import urllib.request
import urllib.error

OLLAMA_HOST  = os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "mistral:7b")


def _http_post(url, headers, body, timeout=1500):
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _ensure_ollama_model():
    """Ensure model exists locally"""
    try:
        url = f"{OLLAMA_HOST}/api/tags"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        models = [m["name"] for m in data.get("models", [])]

        if OLLAMA_MODEL not in models:
            print(f"[AI] Pulling model {OLLAMA_MODEL} ...")
            _http_post(
                f"{OLLAMA_HOST}/api/pull",
                {"Content-Type": "application/json"},
                {"name": OLLAMA_MODEL}
            )
            print("[AI] Model pulled successfully.")
        else:
            print(f"[AI] Model {OLLAMA_MODEL} already available.")

    except Exception as e:
        print(f"[AI] Warning: could not verify model list: {e}")


def _call_ollama(prompt):
    print("[AI] Calling Ollama (mistral:7b)...")

    _ensure_ollama_model()

    result = _http_post(
        f"{OLLAMA_HOST}/api/generate",
        {"Content-Type": "application/json"},
        {
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False
        },
        timeout=1500,
    )

    return result.get("response", "")


def ask_llm(prompt):
    """Single provider: Ollama only"""
    try:
        return _call_ollama(prompt)
    except Exception as e:
        return f"""
## AI Error (Ollama failed)

Error: {e}

Fix checklist:
- Run: ollama serve
- Pull model: ollama pull mistral:7b
- Check: curl http://localhost:11434/api/tags
"""
