---
name: client-care-route
description: Daily geo-optimized property visit route. Query properties needing visits, send tenant confirmation requests, compile confirmed/unconfirmed lists, and deliver the final route to the manager.
---

# Client Care Route Skill

This skill plans daily property visits and delivers a geographically optimized route to the manager.

## Data Concepts Required

This workflow relies on the core property management entities.
See: `references/data-concepts.md`

## Daily Workflow

### Phase 1: Planning and Outreach (Morning)

**Step 1: Identify Properties**
Query the **Property Record** database using the user's `[DATABASE_QUERY_TOOL]`.
Find properties where the **Current Status** indicates a visit is needed (e.g., `fix_needed`, `late_payment`, or other user-defined flags).

**Step 2: Lookup Tenants**
For each property identified, query the **Tenant Record** to retrieve the primary contact name and their preferred `[TENANT_CONTACT_METHOD]`.

**Step 3: Send Confirmation Requests**
Autonomously send a brief, polite message to each tenant requesting confirmation for a visit today.
*Example: "Hi [Name], our team is planning to visit [Address] today. Please reply YES or OK to confirm this works for you."*

**Step 4: Audit**
Autonomously log each outbound request in the **Interaction Log**.

### Phase 2: Route Compilation (Evening or on demand)

**Step 5: Check Replies**
Scan the inbound `[TENANT_CONTACT_METHOD]` channels for replies from the tenants contacted in Step 3.
Treat phrases like `yes`, `ok`, `okay`, `sure`, `confirm`, `confirmed` as confirmations.
Log all received confirmations in the **Interaction Log**.

**Step 6: Sort and Compile Route**
Compile the list of properties needing visits into two groups:
1.  **Confirmed Visits**: Tenants who replied positively.
2.  **Unconfirmed Visits**: Tenants who did not reply.

**Geographic Sorting Requirement**: Within each group, sort the properties geographically to minimize travel time. Do not sort alphabetically by street name. Instead, sort by the **Geographic Identifier** (e.g., the first 3 characters of a Canadian postal code, or a US zip code prefix) to cluster nearby properties together.

**Step 7: Delivery**
Format the final route strictly according to `references/route-template.md`.
Send the compiled route to the manager via `[MANAGER_CHANNEL]`.