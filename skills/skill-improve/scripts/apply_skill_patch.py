#!/usr/bin/env python3
"""
Apply a proposed improvement to a SKILL.md file.

Creates a timestamped backup before writing. Exits non-zero if the old
section is not found (no partial writes).

Usage:
  python3 apply_skill_patch.py \
    --skill himalaya \
    --old "## Tone\nFormal professional." \
    --new "## Tone\nCasual and direct. Avoid corporate language."
"""
import argparse
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

APP_DIR = Path(os.environ.get("APP_DIR", "/app"))


def main() -> None:
    parser = argparse.ArgumentParser(description="Apply a HITL-approved skill patch.")
    parser.add_argument("--skill", required=True, help="Skill name (e.g. himalaya)")
    parser.add_argument("--old", required=True, help="Exact text to replace")
    parser.add_argument("--new", required=True, help="Replacement text")
    args = parser.parse_args()

    skill_path = APP_DIR / "skills" / args.skill / "SKILL.md"
    if not skill_path.exists():
        print(f"error: skill not found: {skill_path}", file=sys.stderr)
        sys.exit(1)

    content = skill_path.read_text()
    old_text = args.old.replace("\\n", "\n")
    new_text = args.new.replace("\\n", "\n")

    if old_text not in content:
        print(
            f"error: old section not found in {skill_path}. No changes made.",
            file=sys.stderr,
        )
        sys.exit(1)

    backup_path = skill_path.with_suffix(
        f".md.bak.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    )
    shutil.copy2(skill_path, backup_path)
    print(f"backup created: {backup_path}")

    updated = content.replace(old_text, new_text, 1)
    skill_path.write_text(updated)
    print(f"skill updated: {skill_path}")


if __name__ == "__main__":
    main()
