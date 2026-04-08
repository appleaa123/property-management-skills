#!/usr/bin/env python3
"""
Append a task feedback entry to skill-feedback.jsonl.

Usage:
  python3 log_feedback.py \
    --skill himalaya \
    --agent legal \
    --outcome approved \
    --summary "Draft lease renewal email for unit 3B" \
    [--comment "Email was too formal, use casual tone"] \
    [--session-id "abc123"]
"""
import argparse
import json
import os
import time
from pathlib import Path

FEEDBACK_LOG = Path(os.environ.get("OPENCLAW_STATE_DIR", "/data/.openclaw")) / "skill-feedback.jsonl"

VALID_OUTCOMES = ["approved", "disapproved", "modified", "partial"]


def main() -> None:
    parser = argparse.ArgumentParser(description="Log task feedback for a skill.")
    parser.add_argument("--skill", required=True, help="Skill name (e.g. himalaya)")
    parser.add_argument("--agent", required=True, help="Agent ID (e.g. legal, rent, maintenance)")
    parser.add_argument(
        "--outcome",
        required=True,
        choices=VALID_OUTCOMES,
        help="Task outcome: approved | disapproved | modified | partial",
    )
    parser.add_argument("--summary", required=True, help="One-sentence task description")
    parser.add_argument("--comment", default="", help="Verbatim user correction (if any)")
    parser.add_argument("--session-id", default="", help="Session identifier for cross-referencing logs")
    parser.add_argument(
        "--capture-pattern",
        action="store_true",
        default=False,
        help="Flag this entry as a winning pattern to capture (set after APPROVED tasks)",
    )
    args = parser.parse_args()

    entry = {
        "ts": int(time.time() * 1000),
        "skill": args.skill,
        "agent": args.agent,
        "outcome": args.outcome,
        "task_summary": args.summary,
        "user_comment": args.comment,
        "session_id": args.session_id,
        "capture_pattern": args.capture_pattern,
    }

    FEEDBACK_LOG.parent.mkdir(parents=True, exist_ok=True)
    with FEEDBACK_LOG.open("a") as f:
        f.write(json.dumps(entry) + "\n")

    print(f"feedback logged: {args.skill} / {args.outcome}")


if __name__ == "__main__":
    main()
