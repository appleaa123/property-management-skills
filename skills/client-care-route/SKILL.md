---
name: client-care-route
description: "Daily geo-optimized property visit route. Query properties needing visits, send tenant confirmation emails, compile confirmed/unconfirmed route, and deliver it to the operator at 5pm."
---

# Client Care Route Skill

Runs daily (7am trigger) to plan property visits and (5pm) deliver the confirmed route to the operator.

## Tool Requirements

- **Email client** — send confirmation emails, read replies (reference: `himalaya`)
- **Database client** — read properties/tenant, write interaction logs (see `property-db` skill)
- **Messaging** — deliver route to operator via your preferred channel
- **Shell** — get today's date

## References

- `skills/client-care-route/references/route-template.md` — Output format for confirmed and unconfirmed lists

## Daily Workflow

### Morning Phase (7am trigger)

**Step 1: Query Properties Needing Visits**

Query your database for all properties with `fix_needed` or `late_payment` status, ordered by postal code. For each property returned, query the corresponding tenant record.

Example (PostgREST/Supabase reference):

```bash
curl -s "$DB_URL/rest/v1/properties?select=property_id,address,city,postalcode,status,fix&status=in.(fix_needed,late_payment)&order=postalcode" \
  -H "apikey: $DB_KEY" -H "Authorization: Bearer $DB_KEY"
```

**Step 2: Send Confirmation Emails**

For each property, send a confirmation email via your email tool:

```
Subject: Visit Confirmation — [address]
Body:
Hi [tenant name],

Our team is planning to visit [address] on [today's date in DD/MM/YYYY].
Please reply YES or OK to confirm this visit works for you.

Thank you,
[operator name]
```

**Step 3: Log Confirmation Requests**

For each outbound confirmation, log to interactions immediately (HITL-exempt — see `property-db` skill):

```
tenant_id: [tenant_id]
name: [name]
channel: email
summary: "Sent visit confirmation request for [date]"
```

**Step 3b: Log Morning Phase Feedback**

After confirmation emails are sent (or if operator modifies the wording):

```bash
python3 skills/skill-improve/scripts/log_feedback.py \
  --skill client-care-route \
  --agent property \
  --outcome <approved|modified|disapproved> \
  --summary "Morning confirmations: [N] emails sent, [city], [date]" \
  --comment "<operator's wording correction verbatim, if any>"
```

### Evening Phase (5pm or when operator requests route)

**Step 4: Check Replies**

Get today's date:

```bash
date +%Y-%m-%d
```

**Step 4a: Scan inbox for tenant confirmation replies**

List recent emails using your email client. For each tenant in the visit list (from Step 1), read any email from their address that arrived today. If the email body contains any of the following (case-insensitive): `yes`, `ok`, `okay`, `sure`, `confirm`, `confirmed` — treat it as a confirmation and log to interactions immediately:

```
tenant_id: [tenant_id]
name: [name]
channel: email
summary: "Tenant confirmed visit for [today_date]"
```

**Step 4b: Query interactions for confirmed tenants**

Query interactions for today's logged confirmations (use `*` wildcards for PostgREST `ilike` — not `%`):

```bash
curl -s "$DB_URL/rest/v1/interactions?select=tenant_id,summary,timestamp&channel=eq.email&summary=ilike.*confirmed visit*&order=timestamp.desc&limit=100" \
  -H "apikey: $DB_KEY" -H "Authorization: Bearer $DB_KEY"
```

From results, keep only rows where `timestamp` starts with today's date string (e.g., `2026-03-19`).

**Step 5: Compile Route**

- **Confirmed**: tenants whose `tenant_id` appears in Step 4 results — sort by postal code
- **Unconfirmed**: remaining tenants from Step 1 — separate list with note "no reply received"

**Step 6: Send Route to Operator**

Format per `skills/client-care-route/references/route-template.md` and send via your messaging channel.

**Step 7: Log Evening Phase Feedback**

After the route is delivered (or if operator edits the sort order or adds/removes properties):

```bash
python3 skills/skill-improve/scripts/log_feedback.py \
  --skill client-care-route \
  --agent property \
  --outcome <approved|modified> \
  --summary "Route delivered: [N] confirmed, [M] unconfirmed, sorted by postal code, [date]" \
  --comment "<operator's route edits verbatim, if any>"
```

## Manual Trigger

Operator can say: "Build today's route" or "Check who confirmed for today's visit".
Respond with current confirmation status and route.

## Notes

- AI sends confirmation requests autonomously (morning phase)
- Operator sees and approves the final confirmed route before any visits are made
- Unconfirmed tenants should be called by the operator, not visited unannounced
- **Geo-sorting by postal code:** Canadian postal codes group geographically (e.g., M5V → downtown Toronto). Ascending postal code sort clusters neighboring properties. Adapt this logic for your region's ZIP/postcode format.
