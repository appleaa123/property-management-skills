---
name: rent-adjustment
description: "Cron-triggered or manual lease review. Detect region, look up current rent control policy (cached or via web search), calculate legal rent increase limit, research market rates, and generate an adjustment brief with birthday and cheque alerts."
---

# Rent Adjustment Skill

Produces a complete rent adjustment advisory brief for a tenant/property. Triggered by a weekly cron or manually with "run rent review for [address]".

Works for any region — Ontario, other Canadian provinces, US states, or international locations. Policy data is loaded from a local cache first; if no cache exists, the agent performs a live web search and proposes saving the result.

## Tool Requirements

- **Database client** — read tenant and property records (see `property-db` skill)
- **Web search** — look up rent control policy and comparable market listings
- **Browser/page extractor** — extract text from government policy pages (optional but recommended)
- **Messaging** — send the brief to the operator via your preferred channel

## References

- `skills/rent-adjustment/references/policy-search-template.md` — Web search queries, known policy cache table, and instructions for writing new regional cache files
- `skills/rent-adjustment/references/CA-ON.md` — Ontario-specific policy details and brief format template (use as format template for all regions)
- `skills/rent-adjustment/references/[CODE].md` — Per-region cache files; check if one exists before doing a web search

## Workflow

### Step 0: Detect Region

Read `province`, `state`, and `country` from the queried property record (Step 1 populates this). Construct the region identifier:

- Canadian province: use province name (e.g., "Ontario", "British Columbia")
- US state: use state name (e.g., "California", "New York")
- International: use country + region (e.g., "New South Wales, Australia")
- If all three fields are null: ask operator before proceeding

### Step 1: Query Tenant and Property Data

Query your database for the tenant and property, joined by address match:

```sql
SELECT t.tenant_id, t.name, t.email, t.phone, t.lease_start, t.rent_amount,
       t.last_rent_adjustment_date, t.birthday,
       p.postalcode, p.city, p.address, p.province, p.state, p.country
FROM tenant t
JOIN properties p ON t.property_id = p.property_id
WHERE p.address ILIKE '%[address]%';
```

### Step 2: Load Rent Control Policy

**Substep A — Check local cache**

Look for a file at `skills/rent-adjustment/references/[REGION-CODE].md`. Use the Known Policy Cache table in `policy-search-template.md` to map region name → code.

If a cache file exists and `last_verified` is within 12 months → use it directly (skip Substep B).

**Substep B — Web search (no cache or stale cache)**

Run the primary search query using your web search tool:

```
Query: "[region] rent increase guideline [current year] site:gov OR site:tribunal OR site:legislation"
Max results: 5
```

If no clear policy number found, run the fallback query:

```
Query: "[region] rent control maximum increase [year] landlord tenant"
Max results: 5
```

For a specific government page (when search results point to a known URL), navigate to it and extract the full text. Look for: `guideline_pct`, `notice_days`, `exemption_rules`, `governing_law`, `source_url`.

If policy is ambiguous after both searches → note uncertainty in brief (see `policy-search-template.md` Step 5).

**Substep C — Propose caching new region (HITL)**

If Substep B was used, prepare a new cache file draft (format from `CA-ON.md`) and present to operator:

> "I found [region] rent control policy via web search. Shall I save it as references/[CODE].md to avoid future searches?"

Only write the file after operator approval.

### Step 3: Calculations

1. **Months to anniversary**: Count months from `last_rent_adjustment_date` (or `lease_start`) to today
2. **Legal max rent**: `rent_amount × (1 + guideline_pct / 100)` — if `guideline_pct` is null (no rent control): note in brief — no legal ceiling applies
3. **Notice required**: `notice_days` from policy (varies by region — do not assume 90 days)
4. **Exemption check**: Apply `exemption_rules` from policy — flag if property may be exempt
5. **Birthday check**: Days until next birthday — flag if within 30 days
6. **Cheque/payment check**: Flag if recurring payment method needs renewal (region-specific conventions)

### Step 4: Market Research

Search for comparable rental listings in the same city:

```
Query: "[city] [postal/zip code prefix] rental [bedrooms]"
Max results: 5
```

Also search region-specific listing sites:

- Canada: realtor.ca, zumper.com, rentals.ca
- US: zillow.com, apartments.com, zumper.com
- International: use country-appropriate portals (rightmove.co.uk, domain.com.au, etc.)

Collect 3+ comparable listings with rent prices and calculate median market rent.

### Step 5: Generate Brief

Format per the sample brief template in the region's cache file (or `CA-ON.md` as the baseline template).

Always include in the brief:

- Region name and governing legislation
- Policy source URL
- Whether a web search was performed (or cache was used)
- Exemption notice if unit may be exempt from rent control

### Step 6: Send to Operator

Send the complete brief via your messaging channel to the operator.

### Step 7: Log Feedback

```bash
python3 skills/skill-improve/scripts/log_feedback.py \
  --skill rent-adjustment \
  --agent property \
  --outcome <approved|modified|disapproved> \
  --summary "Rent brief for [tenant name], [region], [guideline_pct]% guideline" \
  [--comment "<operator correction if any>"]
```
