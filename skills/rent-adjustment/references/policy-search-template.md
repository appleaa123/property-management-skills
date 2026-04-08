# Rent Control Policy — Web Search Template

Use this template when the agent encounters a region without a cached policy file.

## Search Strategy

### Step 1: Primary Search (government/tribunal sources)

```
Query: "[region] rent increase guideline [year] site:gov OR site:tribunal OR site:legislation"
Tool:  tavily_search
Params:
  topic: "general"
  time_range: "1y"
  max_results: 5
```

Replace `[region]` with the full region name (e.g., "British Columbia", "California", "New South Wales").
Replace `[year]` with the current year.

### Step 2: Fallback Search (if Step 1 yields no policy number)

```
Query: "[region] rent control maximum increase [year] landlord tenant"
Tool:  tavily_search
Params:
  topic: "news"
  time_range: "1y"
  max_results: 5
```

### Step 3: Extract from Results

From search results, identify and record:

| Field             | What to look for                                              |
| ----------------- | ------------------------------------------------------------- |
| `guideline_pct`   | Annual cap on rent increases (e.g. "3.5%", "CPI + 1%")        |
| `notice_days`     | Required notice period before increase takes effect           |
| `exemption_rules` | Which units are exempt (new builds, luxury, commercial, etc.) |
| `governing_law`   | Name of the legislation (e.g. "Residential Tenancy Act")      |
| `authority`       | Tribunal or government body that administers the rules        |
| `source_url`      | Direct URL to official policy page                            |

### Step 4: Handle Variable-Rate Policies

Some jurisdictions use formulas instead of fixed percentages:

| Policy type       | How to apply                                              |
| ----------------- | --------------------------------------------------------- |
| `CPI-based`       | Search for current CPI for that region + apply formula    |
| `CPI + N%`        | Add N to found CPI                                        |
| `Fixed %`         | Use directly                                              |
| `No rent control` | Set `guideline_pct = null`, note in brief, advise manager |

### Step 5: Uncertainty Handling

If after two searches the policy is ambiguous:

1. Note in the brief: "⚠ Policy data for [region] is uncertain — verify before issuing notice"
2. Include the source URLs found
3. Suggest manager confirm with local legal counsel

---

## Known Policy Cache

Pre-researched jurisdictions. Use these directly without web search. Verify `last_verified` is within 12 months — if older, run web search to confirm no changes.

### Canada — Provinces

| Code  | Name                 | Guideline (year)                 | Notice   | Exempt?                                                | Source                      | Last Verified |
| ----- | -------------------- | -------------------------------- | -------- | ------------------------------------------------------ | --------------------------- | ------------- |
| CA-ON | Ontario              | 2.1% (2026)                      | 90 days  | Units first occupied after Nov 15/18                   | See CA-ON.md                | 2026-01-01    |
| CA-BC | British Columbia     | 3.0% (2025)                      | 3 months | Units built after Dec 31, 2021                         | gov.bc.ca/landlordtenant    | 2025-01-01    |
| CA-AB | Alberta              | No rent control                  | 3 months | N/A — no provincial cap                                | alberta.ca/rta              | 2025-01-01    |
| CA-QC | Quebec               | Tribunal-set (% varies per unit) | 3 months | N/A — Tribunal administratif du logement sets per-unit | tal.gouv.qc.ca              | 2025-01-01    |
| CA-MB | Manitoba             | No guideline                     | 3 months | N/A                                                    | gov.mb.ca/consumer/tenancy  | 2025-01-01    |
| CA-SK | Saskatchewan         | No rent control                  | 2 months | N/A                                                    | saskatchewan.ca             | 2025-01-01    |
| CA-NS | Nova Scotia          | 5.0% (2025)                      | 4 months | N/A                                                    | novascotia.ca/just/rent-cap | 2025-01-01    |
| CA-PE | Prince Edward Island | 3.0% (2025)                      | 3 months | N/A                                                    | irac.pe.ca                  | 2025-01-01    |

### United States — Selected States

| Code  | Name          | Guideline / Cap          | Notice  | Notes                                            | Source                   | Last Verified |
| ----- | ------------- | ------------------------ | ------- | ------------------------------------------------ | ------------------------ | ------------- |
| US-CA | California    | 5% + local CPI, max 10%  | 90 days | AB 1482 — applies to multi-family built pre-2005 | tenants.dca.ca.gov       | 2025-01-01    |
| US-NY | New York City | RGBO-set (varies yearly) | 90 days | Only rent-stabilised/controlled units            | nyc.gov/hpd              | 2025-01-01    |
| US-OR | Oregon        | 7% + CPI, max 10%        | 90 days | HB 2001 — statewide; new construction exempt     | oregon.gov/ohcs          | 2025-01-01    |
| US-WA | Washington    | No statewide cap         | 20 days | Some cities have local ordinances                | atg.wa.gov               | 2025-01-01    |
| US-TX | Texas         | No rent control          | 30 days | State preempts local rent control                | texasattorneygeneral.gov | 2025-01-01    |
| US-FL | Florida       | No rent control          | 15 days | State preempts local rent control                | myfloridalegal.com       | 2025-01-01    |

### International

| Code   | Name            | Guideline / Cap | Notes                                            | Source                 | Last Verified |
| ------ | --------------- | --------------- | ------------------------------------------------ | ---------------------- | ------------- |
| GB-ENG | England (UK)    | Open market     | 2 months — no cap, but "reasonable" test applies | gov.uk/private-renting | 2025-01-01    |
| AU-NSW | New South Wales | No cap          | 60 days                                          | fairtrading.nsw.gov.au | 2025-01-01    |
| AU-VIC | Victoria        | No cap          | 60 days; max 1 increase per year                 | consumer.vic.gov.au    | 2025-01-01    |

---

## After Web Search — Write a Cache File

Once you successfully extract policy data for a new region, create a cache file at:
`skills/rent-adjustment/references/[CODE].md`

Use the same format as CA-ON.md:

- Policy Summary table (guideline_pct, notice_days, exemption, source, last_verified)
- Calculation formula
- Sample brief format with region-specific fields

Propose the file to manager via HITL before writing. This prevents repeated web searches for the same region.
