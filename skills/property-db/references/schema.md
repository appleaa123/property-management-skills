# Supabase Schema Reference

## PostgREST Query Rules (Read Before Writing Any curl Command)

1. **No RPC functions exist** — never use `/rest/v1/rpc/` — always fails with PGRST202
2. **ilike wildcards use `*` not `%`** — e.g. `name=ilike.*Alice*` (not `%Alice%`)
3. **Column naming inconsistency**:
   - `interactions` uses `timestamp` (no underscore)
   - All other tables use `time_stamp` (with underscore)
4. **Never include PK columns in INSERT** — all PKs auto-generate via `gen_random_uuid()`
5. **Omit all timestamp fields from INSERT** — all have `DEFAULT now()`
6. **No FK enforcement at DB level** — all FK columns are nullable; inserts won't reject bad UUIDs
7. **`maintenance` has no `tenant_id` column** — to get maintenance for a tenant, query via `property_id`
8. **`interactions.timestamp` cannot be used as a horizontal filter** — `timestamp` is a PostgreSQL reserved word; using `?timestamp=gte.VALUE` crashes the Supabase Cloudflare Worker (error 1101). Instead use `order=timestamp.desc&limit=N` and filter the returned rows by date value client-side.

---

## Table 1: properties

| Column         | Type          | Description                                                    |
| -------------- | ------------- | -------------------------------------------------------------- |
| property_id    | UUID PK       | Auto-generated                                                 |
| address        | TEXT NOT NULL | Street address                                                 |
| city           | TEXT NOT NULL | City                                                           |
| province       | TEXT NOT NULL | Province (e.g., Ontario)                                       |
| postalcode     | TEXT NOT NULL | Postal code                                                    |
| landlord_name  | TEXT          | Owner name                                                     |
| landlord_phone | TEXT          | Landlord day phone (for LTB forms RDayPhone[0])                |
| rent           | NUMERIC(10,2) | Monthly rent                                                   |
| status         | TEXT          | `normal` \| `late_payment` \| `fix_needed`                     |
| fix            | TEXT          | Description of current fix needed                              |
| note           | TEXT          | General notes                                                  |
| appliances     | JSONB         | `{"washer": "Samsung WF45T6000AW", "furnace": "Carrier 58TP"}` |
| time_stamp     | TIMESTAMPTZ   | Record created time                                            |

## Table 2: tenant

| Column                    | Type                 | Description                         |
| ------------------------- | -------------------- | ----------------------------------- |
| tenant_id                 | UUID PK              | Auto-generated                      |
| property_id               | UUID FK → properties | Linked property                     |
| address                   | TEXT                 | Tenant's address (matches property) |
| city                      | TEXT                 | City                                |
| province                  | TEXT                 | Province                            |
| postalcode                | TEXT                 | Postal code                         |
| name                      | TEXT NOT NULL        | Full name                           |
| phone                     | TEXT                 | Phone number                        |
| email                     | TEXT                 | Email address                       |
| lease_start               | DATE                 | Lease start date (YYYY-MM-DD)       |
| rent_amount               | NUMERIC(10,2)        | Current monthly rent                |
| birthday                  | DATE                 | Tenant's birthday                   |
| last_rent_adjustment_date | DATE                 | Date of last rent increase          |
| note                      | TEXT                 | General notes                       |
| time_stamp                | TIMESTAMPTZ          | Record created time                 |

## Table 3: interactions

| Column         | Type             | Description                                   |
| -------------- | ---------------- | --------------------------------------------- |
| interaction_id | UUID PK          | Auto-generated                                |
| tenant_id      | UUID FK → tenant | Linked tenant                                 |
| name           | TEXT             | Tenant name (denormalized for quick display)  |
| channel        | TEXT             | `email` \| `whatsapp` \| `sms` \| `in-person` |
| summary        | TEXT             | Summary of the interaction                    |
| timestamp      | TIMESTAMPTZ      | When it occurred                              |

## Table 4: maintenance

| Column           | Type                 | Description                                                                                                             |
| ---------------- | -------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| maintenance_id   | UUID PK              | Auto-generated                                                                                                          |
| property_id      | UUID FK → properties | Linked property                                                                                                         |
| property_address | TEXT                 | Address (denormalized)                                                                                                  |
| issue_type       | TEXT                 | `Improper Surface Grading` \| `water damage` \| `electrical damage` \| `appliance` \| `roof` \| `HVAC` \| `maintenance` |
| proof            | TEXT                 | Comma-separated photo/video attachment URLs                                                                             |
| status           | TEXT                 | `problem raised` \| `waiting` \| `assigned` \| `fixing` \| `solved`                                                     |
| assigned_worker  | TEXT                 | Name of vendor/contractor assigned                                                                                      |
| expense_amount   | NUMERIC(10,2)        | Repair cost including tax                                                                                               |
| expense_note     | TEXT                 | Expense description                                                                                                     |
| time_stamp       | TIMESTAMPTZ          | Record created time                                                                                                     |

## Table 5: vendors

| Column     | Type          | Description                                                                  |
| ---------- | ------------- | ---------------------------------------------------------------------------- |
| vendor_id  | UUID PK       | Auto-generated                                                               |
| name       | TEXT NOT NULL | Vendor/company name                                                          |
| trade_type | TEXT          | `plumber` \| `electrician` \| `HVAC` \| `roofer` \| `appliance` \| `general` |
| phone      | TEXT          | Contact phone                                                                |
| email      | TEXT          | Contact email                                                                |
| city       | TEXT          | City they serve                                                              |
| notes      | TEXT          | Rates, availability, preferences                                             |
| time_stamp | TIMESTAMPTZ   | Record created time                                                          |

## Relationships

```
properties (1) ──< tenant (many)
properties (1) ──< maintenance (many)
tenant (1) ──< interactions (many)
```

## Valid Enum Values

### properties.status

- `normal` — no issues
- `late_payment` — rent overdue
- `fix_needed` — maintenance required

### maintenance.issue_type

- `Improper Surface Grading`
- `water damage`
- `electrical damage`
- `appliance`
- `roof`
- `HVAC`
- `maintenance`

### maintenance.status

- `problem raised` — logged, not yet assigned
- `waiting` — waiting on vendor availability
- `assigned` — vendor confirmed
- `fixing` — repair in progress
- `solved` — resolved

### vendors.trade_type

- `plumber`
- `electrician`
- `HVAC`
- `roofer`
- `appliance`
- `general`

### interactions.channel

- `email`
- `whatsapp`
- `sms`
- `in-person`
