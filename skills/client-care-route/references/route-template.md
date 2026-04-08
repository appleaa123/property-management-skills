# Route Output Format

## Sample WhatsApp Route Delivery

```
📅 PROPERTY VISIT ROUTE — [DD/MM/YYYY]

✅ CONFIRMED (X properties)
─────────────────────────────
1. [Address, City] [Postal Code]
   Tenant: [Name] — [phone]
   Reason: [fix_needed: kitchen faucet / late_payment / lease renewal / routine check]

2. [Address, City] [Postal Code]
   Tenant: [Name] — [phone]
   Reason: [reason]

3. [Address, City] [Postal Code]
   Tenant: [Name] — [phone]
   Reason: [reason]

─────────────────────────────
⚠️ NO REPLY (Y properties — call before visiting)
─────────────────────────────
• [Address] — [Tenant Name] — [phone]
• [Address] — [Tenant Name] — [phone]
```

## Visit Reason Codes

| Reason          | Description                                            |
| --------------- | ------------------------------------------------------ |
| `fix_needed`    | Open maintenance issue — follow up on repair           |
| `late_payment`  | Rent overdue — cheque pickup                           |
| `lease_renewal` | Lease anniversary within 30 days — collect new cheques |
| `routine_check` | No contact in 30+ days — wellness check                |

## Postal Code Geo-Sorting Logic

Canadian postal codes are geographic:

- First 3 characters (FSA) = Forward Sortation Area
- Sort by FSA to group nearby properties
- Example: M5V and M5T are adjacent; M5V and M1P are far apart
- Sort ascending on postalcode to roughly cluster by neighborhood
