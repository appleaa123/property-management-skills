# Setup Guide

## Prerequisites

- Python 3.9+
- An LLM with tool-use capability (Claude, GPT-4, Gemini, etc.)
- A relational database (Supabase recommended — free tier works)
- An email client tool accessible from your agent (himalaya, Gmail API, etc.)
- A messaging channel for operator notifications (WhatsApp, Slack, Telegram, etc.)

## 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

Only `pypdf` is required — for the `ltb-forms` PDF filling script. All other scripts use Python standard library only.

## 2. Set Up Your Database

The skills use a 5-table schema. See `skills/property-db/references/schema.md` for the full schema.

**Quick start with Supabase (recommended):**

1. Create a free project at [supabase.com](https://supabase.com)
2. Run the table definitions from `schema.md` in the Supabase SQL editor
3. Copy your project URL and `service_role` key

**With any PostgreSQL database:** Use the schema from `schema.md` directly. Adapt the PostgREST curl examples in each SKILL.md to your DB client (psycopg2, SQLAlchemy, etc.).

## 3. Configure Environment Variables

Create a `.env` file (never commit this):

```bash
# Database (Supabase/PostgREST reference)
DB_URL=https://your-project.supabase.co
DB_KEY=your-service-role-key

# State directory — where feedback logs and persona file are stored
STATE_DIR=./state

# Output directory — where generated PDFs and reports are saved
OUTPUT_DIR=./forms

# LLM API (for manager-persona skill)
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

Create the state and output directories:

```bash
mkdir -p state forms
```

## 4. Environment Variables Reference

| Variable | Used By | Purpose | Required? |
|---|---|---|---|
| `DB_URL` | All skills with DB queries | Database endpoint (PostgREST URL or equivalent) | Yes |
| `DB_KEY` | All skills with DB queries | Database API key or credentials | Yes |
| `STATE_DIR` | skill-improve, manager-persona | Path to state folder (`skill-feedback.jsonl`, `manager-persona.md`) | No (defaults to `./state`) |
| `OUTPUT_DIR` | ltb-forms | Directory for generated PDFs and expense reports | No (defaults to `./forms`) |
| `ANTHROPIC_API_KEY` | manager-persona | LLM API for persona extraction | Yes for manager-persona |

## 5. Tool Adapter Reference

Each skill requires specific tool capabilities. Wire these up in your agent framework:

| Skill | Email | Database | Messaging | Web Search | Browser | Shell |
|---|---|---|---|---|---|---|
| property-db | — | Required | — | — | — | — |
| maintenance-triage | Required | Required | Required | — | — | Optional |
| client-care-route | Required | Required | Required | — | — | Required (date) |
| rent-adjustment | — | Required | Required | Required | Recommended | — |
| manager-persona | — | Required | Required | — | — | Required |
| skill-improve | — | — | Required | — | — | Required |
| ltb-forms | Required | Required | Required | — | — | Required |

**Reference implementations:**
- Email: `himalaya` (CLI email client)
- Database: Supabase REST API via `curl`
- Messaging: WhatsApp via native message tool
- Web search: Any search API (Brave, Tavily, SerpAPI)
- Browser: `cli-anything-chrome` or Playwright

## 6. Load a Skill into Your Agent

**Claude Code / Claude Projects:**

Copy the contents of any `SKILL.md` into your system prompt, or use a `/load` command in your agent framework.

**Claude Project Knowledge:**

Upload the SKILL.md files as Project Knowledge documents. The agent will use them automatically.

**Other LLMs:**

Paste the SKILL.md content as a system message or into a retrieval store. The skills are written in plain language and work with any instruction-following LLM.

## 7. First Run Checklist

- [ ] Database tables created with correct schema
- [ ] `DB_URL` and `DB_KEY` set
- [ ] At least one property + tenant record in your database
- [ ] Email tool configured (if using maintenance-triage or client-care-route)
- [ ] `STATE_DIR` directory exists and is writable
- [ ] `OUTPUT_DIR` directory exists and is writable (if using ltb-forms)
- [ ] `ANTHROPIC_API_KEY` set (if using manager-persona)
