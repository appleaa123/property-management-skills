# Rent Control Policy — Ontario, Canada (CA-ON)

## Policy Summary

| Key                 | Value                                                                |
| ------------------- | -------------------------------------------------------------------- |
| **2026 guideline**  | 2.1%                                                                 |
| **Notice period**   | 90 days written notice before increase takes effect                  |
| **Frequency limit** | Maximum one increase per 12-month period                             |
| **Exemption**       | Units first occupied after November 15, 2018 are NOT rent-controlled |
| **Governing law**   | Residential Tenancies Act (Ontario RTA)                              |
| **Form**            | N1 (optional but recommended for notice)                             |
| **Source**          | https://www.ontario.ca/document/guide-landlords/rent-increases       |
| **Last verified**   | 2026-01-01                                                           |

## Calculation

```
legal_max_rent = current_rent × 1.021
```

Example: $2,000/mo → max $2,042.20/mo

## Calculation Steps

1. Confirm `last_rent_adjustment_date` (fall back to `lease_start` if null)
2. Verify 12 months have passed since last increase
3. Calculate: `current_rent × (1 + guideline_pct / 100) = legal_max`
4. Calculate 90-day notice deadline: `target_increase_date − 90 days`

## Notice Timeline Example

- Today: March 9
- 90-day notice by: June 7 (latest)
- Increase effective: September 7

## Post-Dated Cheques

Standard practice in Ontario: tenants provide 6–12 months of post-dated cheques at lease start.

- Calculate remaining: `(lease_start month + cheques_provided) − today`
- Flag if < 3 months remain → manager needs to collect next batch

## Sample Brief Format

```
RENT ADJUSTMENT ADVISORY
Region: Ontario, Canada
Tenant: [Name] | [Address]
Generated: [DD/MM/YYYY]

POLICY SOURCE:    Ontario Residential Tenancies Act
GUIDELINE:        2.1% (2026) — source: ontario.ca

CURRENT RENT:        $[amount]/mo
LEGAL MAX (2026):    $[current × 1.021]/mo (+$[difference])
LAST ADJUSTED:       [date or "original lease"]
ELIGIBLE DATE:       [12 months after last adjustment]
NOTICE DEADLINE:     [eligible date − 90 days]

MARKET COMPARABLES ([city] area):
  1. [address/listing] — $[rent]/mo ([source])
  2. [address/listing] — $[rent]/mo ([source])
  3. [address/listing] — $[rent]/mo ([source])
  Median market: $[median]/mo

RECOMMENDATION:
  [Below market → recommend increase to legal max]
  [At/above market → hold rent to retain good tenant]

ALERTS:
  [⚠ Birthday: [name] turns [age] on [date] — e-card needed]
  [⚠ Post-dated cheques: approximately [N] months remaining — renewal needed]

SUGGESTED ACTION:
  [One sentence recommendation for manager]
```
