---
name: rent-adjustment
description: Lease review and rent increase advisory. Queries tenant/lease data to find upcoming lease anniversaries, researches local rent control laws, conducts market research, and drafts an advisory brief for the manager.
---

# Rent Adjustment Skill

This skill monitors lease anniversaries and provides data-backed rent adjustment advice.

## Linear Workflow Steps

### Step 1: Identify Candidates
Query Tenant/Lease records for anniversaries in the next 90-120 days.
*   **Meaning**: Understand that "Lease Start" + 12 months = the earliest legal increase date.

### Step 2: Research-First Policy Search
**Mandatory**: Perform a web search for "[Year] rent increase guideline [City/State]".
Extract:
1.  Guideline % (e.g. 2.5%).
2.  Notice Period (e.g. 90 days).
3.  Exemptions (e.g. "new builds").
See `references/policy-research-guide.md` for structure.

### Step 3: Market Comparison
Search for current listings of similar properties in the same neighborhood. Determine if the current rent is below or at market.

### Step 4: Synthesis & Briefing
Calculate the max legal rent vs. market rent. Draft the advisory brief using `references/brief-template.md`.

### Step 5: Fiduciary Delivery
Send the brief to the manager via `[MANAGER_CHANNEL]`.
**Wait for approval**. Do not execute any increases or send notices autonomously.

## Reference Files
- `references/policy-research-guide.md` — How to search and structure policy data (with Ontario/BC/CA examples).
- `references/brief-template.md` — The advisory brief output format.
- `references/data-concepts.md` — Lease/Property data needs.