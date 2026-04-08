---
name: property-db
description: "Query and update property management data. Defines the schema contract, HITL rules, and query patterns for all property, tenant, vendor, maintenance, and interaction records."
---

# Property Database Skill

All property management data lives in your database. This skill defines the schema, HITL approval rules, and query patterns used by all other skills.

**Reference implementation:** Supabase (PostgREST REST API). The examples below use `curl` against a PostgREST endpoint. Adapt them to your own database client (SQL, ORM, REST API, etc.) — the schema and HITL rules apply regardless of implementation.

## Tool Requirements

- Database client with read/write access to the 5 tables below
- Environment variables: `DB_URL` (your database endpoint) and `DB_KEY` (your API key or credentials)

## References

- `skills/property-db/references/schema.md` — All 5 table schemas, field descriptions, valid enum values, and relationship map

## Database Schema Overview

| Table | Purpose |
|---|---|
| **properties** | One record per property — address, rent, status, appliances, landlord info |
| **tenant** | One tenant per property — name, contact, lease dates, rent amount |
| **interactions** | Log of every contact with a tenant — channel, summary, timestamp |
| **maintenance** | Maintenance requests and work orders per property |
| **vendors** | Tradesperson contact directory |

See `skills/property-db/references/schema.md` for full field definitions and valid enum values.

## Query Patterns

### Security: URL-encode filter values

Always URL-encode variable data used in query-string filters (addresses, names, UUIDs). For PostgREST: simple equality filters use `eq.<value>` syntax; ILIKE patterns use `ilike.*value*`. Never concatenate raw user input directly into filter strings without encoding.

### Read Examples (PostgREST/Supabase reference)

```bash
# Get all properties with current status
curl -s "$DB_URL/rest/v1/properties?select=property_id,address,city,status,fix" \
  -H "apikey: $DB_KEY" -H "Authorization: Bearer $DB_KEY"

# Get tenant for a property (join via address match)
curl -s "$DB_URL/rest/v1/tenant?select=name,email,phone,lease_start,rent_amount,birthday,properties(address)&properties.address=ilike.*123+Main*" \
  -H "apikey: $DB_KEY" -H "Authorization: Bearer $DB_KEY"

# Get vendors by trade type and city
curl -s "$DB_URL/rest/v1/vendors?select=name,phone,email,notes&trade_type=eq.plumber&city=eq.Toronto" \
  -H "apikey: $DB_KEY" -H "Authorization: Bearer $DB_KEY"

# Get maintenance history for a property
curl -s "$DB_URL/rest/v1/maintenance?select=issue_type,status,assigned_worker,expense_amount,time_stamp&property_id=eq.<uuid>&order=time_stamp.desc" \
  -H "apikey: $DB_KEY" -H "Authorization: Bearer $DB_KEY"

# Get last 5 interactions for a tenant
curl -s "$DB_URL/rest/v1/interactions?select=channel,summary,timestamp&tenant_id=eq.<uuid>&order=timestamp.desc&limit=5" \
  -H "apikey: $DB_KEY" -H "Authorization: Bearer $DB_KEY"
```

### Write Examples

```bash
# Insert new maintenance record
curl -s -X POST "$DB_URL/rest/v1/maintenance" \
  -H "apikey: $DB_KEY" -H "Authorization: Bearer $DB_KEY" \
  -H "Content-Type: application/json" -H "Prefer: return=representation" \
  -d '{"property_id":"<uuid>","property_address":"123 Main St","issue_type":"appliance","status":"problem raised","proof":"https://..."}'

# Update maintenance status
curl -s -X PATCH "$DB_URL/rest/v1/maintenance?maintenance_id=eq.<uuid>" \
  -H "apikey: $DB_KEY" -H "Authorization: Bearer $DB_KEY" \
  -H "Content-Type: application/json" \
  -d '{"status":"assigned","assigned_worker":"Bob Plumbing"}'

# Log an interaction (HITL-exempt — execute immediately)
curl -s -X POST "$DB_URL/rest/v1/interactions" \
  -H "apikey: $DB_KEY" -H "Authorization: Bearer $DB_KEY" \
  -H "Content-Type: application/json" -H "Prefer: return=representation" \
  -d '{"tenant_id":"<uuid>","name":"Jane Doe","channel":"email","summary":"Sent rent increase notice"}'

# Update property status
curl -s -X PATCH "$DB_URL/rest/v1/properties?property_id=eq.<uuid>" \
  -H "apikey: $DB_KEY" -H "Authorization: Bearer $DB_KEY" \
  -H "Content-Type: application/json" \
  -d '{"status":"fix_needed","fix":"Leaking kitchen faucet"}'
```

## HITL Rules

- **Read operations**: execute freely to answer questions
- **Write operations (INSERT/UPDATE)**: show the proposed change to the operator and wait for "Approve" before executing
- **Interaction logging (POST to interactions)**: EXEMPT from HITL — execute immediately after every tenant-facing action. Logging is an audit trail, not an operational decision.
- **DELETE**: never delete records without explicit written operator approval
- **Financial data**: read freely, but updating rent or expense fields requires APPROVE

## Date Handling

- Database format: `YYYY-MM-DD` (ISO 8601)
- Display format to humans: `DD/MM/YYYY`
- Omit timestamp fields from INSERT bodies — all timestamp columns have `DEFAULT now()` and are set automatically. Never pass the string `"now()"` in a JSON body.

## Standard Lookup Pattern

When the operator asks about a property or tenant:

1. Query properties by address ILIKE match
2. Join tenant to get occupant info
3. Query last 3 maintenance records
4. Query last 3 interactions
5. Return a summary: tenant name, rent, status, open issues, last contact
6. **Immediately log this lookup** to the interactions table (HITL-exempt). Log even if no results were found — use `tenant_id: null` and describe what was searched.

When asked for a vendor: query vendors by `trade_type` + `city`, return top 3 results (name, phone, email, notes).
