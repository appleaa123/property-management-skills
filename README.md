# Property Management Skills

A collection of 7 AI agent skills for property management — built for Claude but usable with any instruction-following LLM. Each skill is a self-contained SKILL.md that teaches your AI agent how to perform a specific property management workflow.

## Skills

| Skill | Trigger | What It Does | Key Dependencies |
|---|---|---|---|
| [property-db](skills/property-db/SKILL.md) | On demand | Query/update the property database; enforces HITL approval rules | Database |
| [maintenance-triage](skills/maintenance-triage/SKILL.md) | Email received | Triage tenant emails, classify issues, generate work orders, dispatch vendors | Email, Database, Messaging |
| [client-care-route](skills/client-care-route/SKILL.md) | Daily cron | Plan geo-optimized property visit routes, send tenant confirmations | Email, Database, Messaging |
| [rent-adjustment](skills/rent-adjustment/SKILL.md) | Weekly cron | Research rent control policy, calculate legal max rent, generate advisory brief | Database, Web Search, Messaging |
| [ltb-forms](skills/ltb-forms/SKILL.md) | On demand | Fill Ontario LTB forms (N1/N4/N9/N12) using tenant data, with batch mode | Database, Python, Email |
| [manager-persona](skills/manager-persona/SKILL.md) | Weekly cron | Extract operator communication style from history, update persona profile | Database, LLM API |
| [skill-improve](skills/skill-improve/SKILL.md) | On demand | Analyze feedback logs, propose improvements to SKILL.md files | File system |

## Quick Start

**1. Clone and install dependencies**

```bash
git clone <repo-url>
cd property-management-skills
pip install -r requirements.txt
```

**2. Configure environment**

```bash
cp .env.example .env  # edit with your credentials
mkdir -p state forms
```

See [docs/setup.md](docs/setup.md) for the full environment variable reference and database setup.

**3. Load a skill into Claude**

**Claude Projects:** Upload any `SKILL.md` as a Project Knowledge document.

**Claude Code:** Paste the SKILL.md content into your system prompt or a `CLAUDE.md` file.

**Other LLMs:** Paste the SKILL.md content as a system message. Skills are written in plain language and work with any instruction-following LLM.

## How Skills Work

Each `SKILL.md` is a structured instruction file with:

- A YAML frontmatter block (`name`, `description`)
- A `## Tool Requirements` section listing capabilities needed (email, database, messaging, etc.)
- A step-by-step `## Workflow` section the agent follows
- Reference to supporting files (scripts, policy docs, templates)

The agent reads the SKILL.md and executes the workflow using whatever tools you've configured. The skills describe *what* to do — your tool integration handles *how*.

## Adapting to Your Stack

The reference implementation uses:
- **Database**: Supabase (PostgREST REST API)
- **Email**: `himalaya` (CLI email client)
- **Messaging**: WhatsApp
- **LLM API**: Anthropic Claude

Every tool-specific command in the SKILL.md files is marked as a reference implementation. Replace them with your own tools — the workflow logic, classification rules, and schema stay the same.

See [docs/setup.md](docs/setup.md) for the tool adapter reference table.

## Database Schema

All skills share a 5-table schema defined in [skills/property-db/references/schema.md](skills/property-db/references/schema.md):

- `properties` — rental units (address, status, appliances, landlord info)
- `tenant` — one tenant per property (contact, lease, rent amount)
- `interactions` — interaction log (email, WhatsApp, in-person)
- `maintenance` — work orders and maintenance history
- `vendors` — tradesperson directory

## Architecture

See [docs/architecture.md](docs/architecture.md) for the full data flow diagram, skill dependency table, and the 3-layer self-improvement feedback loop.

## Form Assets

The `ltb-forms` skill includes blank Ontario Landlord and Tenant Board (LTB) forms:

- `N1` — Notice of Rent Increase
- `N4` — Notice to End Tenancy (Non-Payment)
- `N9` — Tenant's Notice to Terminate
- `N12` — Notice to End Tenancy (Landlord's Own Use)

These are official Ontario government forms. The skill includes an onboarding workflow to add forms for other jurisdictions.

## License

MIT — see [LICENSE](LICENSE).
