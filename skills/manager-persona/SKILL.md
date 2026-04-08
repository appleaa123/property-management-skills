---
name: manager-persona
description: "Extract the operator's communication style, decision patterns, and vocabulary from historical interactions. Outputs a persona file that all agents load at session start to mirror the operator's tone and priorities."
---

# Manager Persona Skill

Extracts the operator's communication fingerprint from historical messages in the `interactions` table. Outputs a structured persona file that all agents load at session start to mirror the operator's tone, priorities, and decision heuristics.

## Tool Requirements

- **Database client** — read interaction history from the `interactions` table (see `property-db` skill)
- **File system** — read `{STATE_DIR}/skill-feedback.jsonl`, write `{STATE_DIR}/manager-persona.md`
- **LLM API** — extract persona patterns (reference: Anthropic Claude via `ANTHROPIC_API_KEY`; adapt `scripts/extract_persona.py` to your preferred LLM)
- **Messaging** — present summary to operator for approval

> `{STATE_DIR}` is the path to your state directory. Set the `STATE_DIR` environment variable, or default to `./state/`.

## When to Run

- Weekly cron (auto-triggered, silent unless persona changes significantly)
- Operator sends `!refresh persona`

## Workflow

### Step 1: Fetch Interaction History

Query the last 90 days of outbound operator messages from your database's `interactions` table. If fewer than 20 messages are returned, extend the window to 180 days.

Example query (PostgREST/Supabase reference — adapt to your DB client):

```bash
# Last 90 days
curl -s "${DB_URL}/rest/v1/interactions?select=summary,channel,timestamp&direction=eq.outbound&channel=eq.whatsapp&timestamp=gte.<90-days-ago>&order=timestamp.desc&limit=200" \
  -H "apikey: ${DB_KEY}" -H "Authorization: Bearer ${DB_KEY}"
```

Also read recent corrections from the feedback log:

```bash
cat ${STATE_DIR:-./state}/skill-feedback.jsonl | python3 -c "
import sys, json
entries = [json.loads(l) for l in sys.stdin if l.strip()]
corrections = [e for e in entries if e.get('user_comment') and e.get('outcome') in ('disapproved','modified')]
print(json.dumps(corrections[-50:]))  # last 50 corrections
"
```

Save query results to temporary files (e.g., `/tmp/interactions.json` and `/tmp/corrections.json`) for the next step.

### Step 2: Run Persona Extraction

```bash
python3 skills/manager-persona/scripts/extract_persona.py \
  --interactions-json /tmp/interactions.json \
  --corrections-json /tmp/corrections.json \
  --output /tmp/manager-persona-draft.md
```

> The script calls an LLM API. Set `ANTHROPIC_API_KEY` for the reference implementation or edit `extract_persona.py` to use your preferred LLM.

### Step 3: Present Summary to Operator (HITL)

Send a summary to the operator via your messaging channel. Do NOT send the full extracted file — just the headline patterns:

```
🧠 PERSONA REFRESH — Draft ready

Found patterns in [N] messages + [M] corrections:
• Tone: [e.g. "Direct, uses bullet points, no pleasantries"]
• Approval style: [e.g. "Single word 'yes' or 'APPROVE', rarely explains"]
• Urgency signals: [e.g. "Caps lock, 'URGENT:', forward slashes for emphasis"]
• Common corrections: [e.g. "Always adds exemption check to rent briefs"]

Reply APPROVE to save, REJECT to discard.
```

Wait for operator reply before writing the file.

### Step 4: Write Persona File (on APPROVE only)

```bash
cp /tmp/manager-persona-draft.md ${STATE_DIR:-./state}/manager-persona.md
echo "persona updated: $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> ${STATE_DIR:-./state}/manager-persona.md
```

### Step 5: Log Feedback

```bash
python3 skills/skill-improve/scripts/log_feedback.py \
  --skill manager-persona \
  --agent manager \
  --outcome approved \
  --summary "Persona refresh from [N] messages"
```
