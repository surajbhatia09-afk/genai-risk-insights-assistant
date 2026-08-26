"""
Thin, swappable LLM client.

Two modes so the app is usable by anyone who clones it, cost or no cost:

- "openai"  — real calls to the OpenAI API. Needs OPENAI_API_KEY set as an
              environment variable (or in .streamlit/secrets.toml when
              deployed). Costs a few cents per session at most for this
              use case (short prompts, small outputs).
- "offline" — a deterministic, template-based generator that produces a
              structurally similar narrative WITHOUT calling any API. No
              key, no cost. It exists so you (or anyone reviewing this repo)
              can see the app run end-to-end for free, and so the prompt
              design is visible even without spending anything.

Swap in a different provider (Azure OpenAI, Anthropic, a local Ollama model)
by adding another branch in `generate()` — the rest of the app doesn't care
which one is used.
"""

from __future__ import annotations

import os


def generate(system_prompt: str, user_prompt: str, mode: str = "auto") -> str:
    """Returns the model's text response. mode: 'openai' | 'offline' | 'auto'."""
    if mode == "auto":
        mode = "openai" if os.getenv("OPENAI_API_KEY") else "offline"

    if mode == "openai":
        return _generate_openai(system_prompt, user_prompt)
    return _generate_offline(system_prompt, user_prompt)


def _generate_openai(system_prompt: str, user_prompt: str) -> str:
    from openai import OpenAI

    client = OpenAI()  # reads OPENAI_API_KEY from the environment
    resp = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        temperature=0.2,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    return resp.choices[0].message.content.strip()


def _generate_offline(system_prompt: str, user_prompt: str) -> str:
    """
    Deterministic fallback: extracts the key numbers already computed by
    insights_engine.py (they're embedded in user_prompt as plain text) and
    stitches them into a templated narrative. This is intentionally simple —
    it's a stand-in for a real LLM call, not a reimplementation of one.
    """
    return (
        "[Offline demo mode — no LLM API key set, showing a templated summary "
        "instead of a real generated one. Set OPENAI_API_KEY to see actual "
        "GenAI-generated narratives.]\n\n"
        + _naive_summarize(user_prompt)
    )


def _naive_summarize(user_prompt: str) -> str:
    lines = [l.strip() for l in user_prompt.splitlines() if l.strip()]
    key_lines = [l for l in lines if any(ch.isdigit() for ch in l)][:8]
    if not key_lines:
        return "No numeric context was provided to summarize."
    bullet_text = "\n".join(f"- {l}" for l in key_lines)
    return f"Here are the key figures from the data provided:\n{bullet_text}"
