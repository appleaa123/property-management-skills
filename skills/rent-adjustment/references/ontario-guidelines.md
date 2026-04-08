# Ontario Rent Increase Guidelines

## 2026 Guideline

**Ontario Rent Increase Guideline 2026: 2.1%**

Formula: `new_max_rent = current_rent × 1.021`

Example: $2,000/mo → max increase to $2,042.20/mo

## Legal Requirements (Residential Tenancies Act)

- **Notice period**: Minimum 90 days written notice before increase takes effect
- **Frequency**: Maximum one increase per 12-month period
- **Form**: Written notice (N1 form optional but recommended)
- **Exempt**: Units first occupied after November 15, 2018 are NOT rent-controlled

## Calculation Steps

1. Confirm last increase date (use `last_rent_adjustment_date` or `lease_start`)
2. Verify 12 months have passed since last increase
3. Calculate: `current_rent × 1.021 = legal_max`
4. Calculate 90-day notice deadline: `target_increase_date - 90 days`

## Sample Brief Format

```
RENT ADJUSTMENT ADVISORY
Tenant: [Name] | [Address]
Generated: [DD/MM/YYYY]

CURRENT RENT:        $[amount]/mo
LEGAL MAX (2026):    $[current × 1.021]/mo (+$[difference])
LAST ADJUSTED:       [date or "original lease"]
ELIGIBLE DATE:       [12 months after last adjustment]
NOTICE DEADLINE:     [eligible date - 90 days]

MARKET COMPARABLES ([city] area):
  1. [address/listing] — $[rent]/mo ([source])
  2. [address/listing] — $[rent]/mo ([source])
  3. [address/listing] — $[rent]/mo ([source])
  Median market: $[median]/mo

RECOMMENDATION:
  [Below market → recommend increase to legal max]
  [At/above market → hold rent to retain good tenant]

ALERTS:
  [⚠ Birthday: [name] turns [age] on [date] — e-card needed (manager to approve message)]
  [⚠ Post-dated cheques: approximately [N] months remaining — cheque renewal conversation needed]

SUGGESTED ACTION:
  [One sentence recommendation for manager]
```

## Notice Timeline Example

- Today: March 9
- 90-day notice by: June 7 (latest)
- Increase effective: September 7

## Post-Dated Cheques

Standard practice: tenants provide 6-12 months of post-dated cheques at lease start.

- Calculate remaining: `(lease_start month + cheques_provided) - today`
- Flag if < 3 months remain → manager needs to collect next batch
