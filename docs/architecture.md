# Architecture

## How the Skills Form a System

These 7 skills are designed to work together as a property management AI agent, but each skill is also independently usable. The diagram below shows how they relate:

```
                        ┌─────────────────┐
                        │   property-db   │  ← Central data hub
                        │  (schema + HITL │    (all skills read/write here)
                        │    rules)       │
                        └────────┬────────┘
                                 │
          ┌──────────────────────┼────────────────────────┐
          │                      │                        │
          ▼                      ▼                        ▼
┌──────────────────┐  ┌──────────────────┐  ┌────────────────────┐
│ maintenance-     │  │  rent-adjustment │  │  client-care-route │
│ triage           │  │                  │  │                    │
│ (email → work    │  │ (policy + market  │  │ (visit planning +  │
│  order → vendor) │  │  brief → manager)│  │  route delivery)   │
└──────────────────┘  └──────────────────┘  └────────────────────┘
          │                      │                        │
          │                      │                        │
          ▼                      ▼                        ▼
                        ┌─────────────────┐
                        │   ltb-forms     │
                        │ (PDF generation │
                        │  + delivery)    │
                        └─────────────────┘

                        ┌─────────────────┐
                        │ manager-persona │  ← All agents load this at session start
                        │ (communication  │
                        │  fingerprint)   │
                        └─────────────────┘

                        ┌─────────────────┐
                        │  skill-improve  │  ← Reads feedback from all skills
                        │ (self-improving  │    Proposes SKILL.md patches
                        │  feedback loop) │
                        └─────────────────┘
```

## Skill Dependencies

| Skill | Depends On | Optional |
|---|---|---|
| property-db | (none — foundation layer) | — |
| maintenance-triage | property-db | skill-improve |
| client-care-route | property-db | skill-improve |
| rent-adjustment | property-db | skill-improve |
| ltb-forms | property-db | — |
| manager-persona | property-db | skill-improve |
| skill-improve | (file system only) | — |

## Trigger Types

| Skill | Trigger | Frequency |
|---|---|---|
| maintenance-triage | Email received / manual | On demand |
| client-care-route | Cron (7am + 5pm) / manual | Daily |
| rent-adjustment | Cron (weekly) / manual | Weekly |
| ltb-forms | Manual ("generate N1 for...") | On demand |
| manager-persona | Cron (weekly) / "!refresh persona" | Weekly |
| skill-improve | Manual / pattern trigger (5+ feedback entries) | As needed |

## Data Flow

1. **Tenant emails** → maintenance-triage → work order → vendor dispatched
2. **Cron trigger** → rent-adjustment → policy lookup → brief to operator
3. **Operator request** → ltb-forms → PDF filled → delivered to tenant
4. **Cron trigger** → client-care-route → confirmation emails → route to operator
5. **Weekly cron** → manager-persona → interaction history → persona file updated
6. **Feedback accumulates** → skill-improve → SKILL.md patch proposals

## Feedback Loop (3-Layer Self-Improvement)

```
Layer 1: Capture
  Every APPROVED or REJECTED task → log_feedback.py → skill-feedback.jsonl

Layer 2: Analyze
  skill-improve reads skill-feedback.jsonl → identifies patterns

Layer 3: Apply
  skill-improve proposes SKILL.md patch → operator APPROVEs → apply_skill_patch.py
```

This creates a closed loop where operator corrections gradually improve agent behavior over time.

## HITL (Human-in-the-Loop) Philosophy

All skills follow a consistent approval model:

- **Read operations**: execute freely
- **Write operations**: show proposed change → wait for APPROVE
- **Interaction logging**: EXEMPT — always execute (it's an audit trail)
- **Emergency situations**: bypass HITL, notify operator immediately
- **Financial updates**: always require APPROVE

The operator is never bypassed for consequential actions, but the agent operates autonomously for safe read/log operations to minimize friction.
