#!/usr/bin/env python3
"""
Extract manager persona patterns from interaction history.

Reads historical outbound WhatsApp messages and skill-feedback corrections,
calls Claude API to synthesize communication patterns, and writes a structured
manager-persona.md file.

Usage:
  python3 extract_persona.py \
    --interactions-json /tmp/interactions.json \
    --corrections-json /tmp/corrections.json \
    --output /tmp/manager-persona-draft.md
"""
import argparse
import json
import os
import sys
from pathlib import Path

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
CLAUDE_MODEL = "claude-haiku-4-5-20251001"  # Lightweight — persona extraction is straightforward

PERSONA_PROMPT = """You are analyzing a property manager's communication history to extract their professional persona.

Below are their outbound WhatsApp messages (the "interactions" array) and explicit corrections they made to an AI agent's outputs (the "corrections" array).

Your task: extract a structured persona profile. Be specific and concrete — use exact phrases and examples from the messages where possible.

Return a markdown document with these exact sections:

## Communication Style
- Sentence length and structure (short/long, bullets/prose)
- Formality level (casual/professional/terse)
- Emoji usage (none/occasional/frequent — give examples)
- Signature phrases or filler words they use

## Decision Patterns
- How they signal urgency (exact phrases)
- How they signal approval (exact phrases, e.g. "yes", "go ahead", "APPROVE")
- How they signal disapproval (exact phrases)
- Risk tolerance signals (do they ask for more detail, or just decide?)

## Domain Priorities
- What they always check before approving (e.g. "always asks about exemptions")
- Topics they care most about (rent control, tenant relations, vendor costs, etc.)
- Red lines (topics that always escalate to them)

## Vocabulary Fingerprint
- 10-15 characteristic words or phrases they use
- Words or phrases they dislike (based on corrections)

## Correction History Summary
- Recurring themes from their agent corrections (max 5 bullet points)
- Skills most frequently corrected

Keep each section concise — 3-6 bullet points max. This file is loaded into every AI agent session.

---

INTERACTIONS (last 90-180 days of outbound WhatsApp messages):
{interactions}

CORRECTIONS (explicit agent output corrections):
{corrections}"""


def call_claude(prompt: str) -> str:
    """Call Claude API via HTTP (avoids anthropic SDK dependency)."""
    import urllib.request
    import urllib.error

    if not ANTHROPIC_API_KEY:
        raise ValueError("ANTHROPIC_API_KEY environment variable is not set")

    payload = {
        "model": CLAUDE_MODEL,
        "max_tokens": 1024,
        "messages": [{"role": "user", "content": prompt}],
    }

    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=json.dumps(payload).encode(),
        headers={
            "x-api-key": ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            response = json.loads(resp.read())
            return response["content"][0]["text"]
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        raise RuntimeError(f"Claude API error {e.code}: {body}") from e


def summarize_interactions(interactions: list) -> str:
    """Summarize interactions for the prompt — keep token count manageable."""
    if not interactions:
        return "(no messages found)"
    # Take up to 100 messages, most recent first
    sample = interactions[:100]
    lines = []
    for entry in sample:
        msg = entry.get("message", "").strip()
        if msg:
            ts = entry.get("created_at", "")[:10]
            lines.append(f"[{ts}] {msg[:200]}")
    return "\n".join(lines) if lines else "(no message content)"


def summarize_corrections(corrections: list) -> str:
    """Summarize corrections for the prompt."""
    if not corrections:
        return "(no corrections found)"
    lines = []
    for entry in corrections[:50]:
        comment = entry.get("user_comment", "").strip()
        skill = entry.get("skill", "unknown")
        outcome = entry.get("outcome", "")
        if comment:
            lines.append(f"[{skill} / {outcome}] {comment[:200]}")
    return "\n".join(lines) if lines else "(no corrections with comments)"


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract manager persona from interaction history.")
    parser.add_argument("--interactions-json", required=True, help="Path to interactions JSON file")
    parser.add_argument("--corrections-json", required=True, help="Path to corrections JSON file")
    parser.add_argument("--output", required=True, help="Output path for manager-persona.md")
    args = parser.parse_args()

    # Load input data
    interactions_path = Path(args.interactions_json)
    corrections_path = Path(args.corrections_json)

    interactions = []
    if interactions_path.exists():
        try:
            interactions = json.loads(interactions_path.read_text())
            if not isinstance(interactions, list):
                interactions = []
        except (json.JSONDecodeError, OSError):
            pass

    corrections = []
    if corrections_path.exists():
        try:
            corrections = json.loads(corrections_path.read_text())
            if not isinstance(corrections, list):
                corrections = []
        except (json.JSONDecodeError, OSError):
            pass

    if not interactions and not corrections:
        print("ERROR: no interaction or correction data found — cannot extract persona", file=sys.stderr)
        sys.exit(1)

    interactions_text = summarize_interactions(interactions)
    corrections_text = summarize_corrections(corrections)

    prompt = PERSONA_PROMPT.format(
        interactions=interactions_text,
        corrections=corrections_text,
    )

    print(f"Extracting persona from {len(interactions)} messages, {len(corrections)} corrections...")
    persona_md = call_claude(prompt)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(f"# Manager Persona\n\n{persona_md}\n")

    print(f"persona draft written to: {output_path}")


if __name__ == "__main__":
    main()
