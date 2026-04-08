---
name: skill-improve
description: "Review skill performance, analyze feedback logs, and propose improvements to a skill based on past task outcomes and operator corrections."
---

# Skill Improve

Analyze accumulated task feedback for a given skill and propose concrete SKILL.md improvements.

## Tool Requirements

- **File system** — read feedback log (`{STATE_DIR}/skill-feedback.jsonl`), read and write SKILL.md files
- **Messaging** — present proposals to operator for approval

> `{STATE_DIR}` is the path to your state directory. Set the `STATE_DIR` environment variable, or default to `./state/`.

## When to Use

- Operator requests a skill review
- A skill has 5+ feedback entries in the log
- A pattern of operator corrections or disapprovals is noticed
- A skill step fails — triggers the Fix flow below

## Workflow

### Step 1 — Read feedback log

```sh
cat ${STATE_DIR:-./state}/skill-feedback.jsonl | grep '"skill":"<skill_name>"'
```

### Step 2 — Read current skill

```sh
cat skills/<skill_name>/SKILL.md
```

### Step 3 — Identify patterns

Look for recurring themes across feedback entries:

- Steps that were consistently skipped or wrong
- Tone/format corrections from the operator
- Missing edge cases
- Outdated instructions

### Step 4 — Propose a diff

Present to operator via your messaging channel:

```
SKILL IMPROVEMENT PROPOSAL: <skill_name>

CURRENT:
<exact current section>

PROPOSED:
<new version>

REASON: <one-sentence pattern summary from N feedback entries>

Reply APPROVE to apply, REJECT to discard.
```

### Step 5 — Apply (on APPROVE only)

```sh
python3 skills/skill-improve/scripts/apply_skill_patch.py \
  --skill <skill_name> \
  --old "<old_section>" \
  --new "<new_section>"
```

---

## Evolution Capture (after every APPROVED task)

After any task that is APPROVED, log it as a winning pattern for future analysis:

```sh
python3 skills/skill-improve/scripts/log_feedback.py \
  --skill <skill_name> \
  --agent <agent_id> \
  --outcome approved \
  --summary "<one sentence task description>" \
  --capture-pattern
```

The `--capture-pattern` flag marks the entry as a successful execution trace, useful for identifying high-signal winning patterns when reviewing skill performance.

---

## Fix Flow (on skill step failure)

When any step in a skill returns a non-zero exit code or errors out:

1. **Capture the failure** — log with outcome `partial`:

```sh
python3 skills/skill-improve/scripts/log_feedback.py \
  --skill <skill_name> \
  --agent <agent_id> \
  --outcome partial \
  --summary "Step [N] failed: <error description>" \
  --comment "<exact error output>"
```

2. **Propose a fix** — present to operator:

```
⚠️ SKILL FIX PROPOSAL: <skill_name>

FAILED STEP:
<exact failing command>

ERROR:
<error output, max 200 chars>

PROPOSED FIX:
<updated command or workflow change>

REASON: <one-sentence diagnosis>

Reply APPROVE to apply fix, REJECT to leave as-is.
```

3. **Apply fix on APPROVE only** — same as Step 5 above.
