---
name: rent-adjustment
description: Lease review and rent increase advisory. Queries tenant/lease data to find upcoming lease anniversaries, researches local rent control laws, conducts market research, and drafts an advisory brief for the manager.
---

# Rent Adjustment Skill

This skill proactively monitors lease anniversaries and generates rent increase advisory briefs based on local laws and market conditions.

## Data Concepts Required

This workflow relies on the core property management entities.
See: `references/data-concepts.md`

## Workflow

### Step 1: Identify Upcoming Anniversaries
Query the **Tenant Record** using the user's `[DATABASE_QUERY_TOOL]`.
Look for tenants whose `Lease Start Date` anniversary is approaching within the next 4 months (or a timeframe specified by the manager).

### Step 2: Research Local Regulations
For each identified property, you MUST determine the local rent control laws for its specific jurisdiction.
Use a web search tool to find current government regulations for the property's state/province/city.
You must extract:
1.  The maximum allowable rent increase percentage (the guideline amount).
2.  The required notice period (e.g., 60 days, 90 days).
3.  Any exemptions that might apply (e.g., new buildings built after a certain year).
See: `references/policy-research-guide.md` for known examples.

### Step 3: Conduct Market Research
Perform a web search to find current market rental rates for comparable properties in the same neighborhood (matching bedroom/bathroom counts). Determine if the current rent is below, at, or above market value.

### Step 4: Calculate Adjustment Options
Calculate the maximum allowable rent increase based on the local guideline percentage:
`New Max Rent = Current Rent * (1 + Guideline Percentage / 100)`

Calculate the final date a notice must be served to be legally valid:
`Notice Deadline = Anniversary Date - Required Notice Period (in days)`

### Step 5: Draft Advisory Brief
Synthesize the lease data, local regulations, and market research into a concise brief for the manager.
Format strictly according to `references/brief-template.md`.

### Step 6: Delivery
Send the drafted advisory brief to the manager via `[MANAGER_CHANNEL]`.
**Do not send any notices to the tenant without explicit manager approval** (See `property-db` HITL rules).