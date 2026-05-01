---
name: maintenance-triage
description: Handles inbound maintenance requests. Classifies the issue by trade, checks for emergency status, looks up the appropriate vendor, generates a work order, gets manager approval, and dispatches it.
---

# Maintenance Triage Skill

This skill processes inbound maintenance requests, determines the required trade, identifies emergency situations, and drafts work orders.

## Data Concepts Required

This workflow relies on the core property management entities. Ensure you know how the user tracks these before proceeding.
See: `references/data-concepts.md`

## Triage Workflow

### Step 1: Ingest Request
Check the inbound channel (e.g., `[TENANT_CONTACT_METHOD]`, email, SMS, or a portal) for new maintenance reports.
Extract: Property address, reporting tenant, description of the issue, and reported time.

### Step 2: Classify and Check Urgency
Analyze the description of the issue.
Consult `references/issue-classification.md` to:
1. Determine if this is an **Emergency** (requires immediate dispatch) or **Routine**.
2. Determine the required **Trade/Specialty** (e.g., Plumber, Electrician, HVAC).

### Step 3: Find Vendor
Query the **Vendor Record** database using the user's `[DATABASE_QUERY_TOOL]`.
Look for a vendor that matches:
1. The required **Trade/Specialty**.
2. The **Geographic Identifier** of the property.

### Step 4: Draft Work Order
Create a standardized work order document.
Format strictly according to `references/work-order-template.md`.

### Step 5: Manager Approval
Send the proposed work order and vendor assignment to the manager via `[MANAGER_CHANNEL]`.
**Wait for explicit approval.** (See `property-db` HITL rules).

### Step 6: Dispatch and Audit
Upon approval:
1. Send the work order to the Vendor via their preferred contact method.
2. Reply to the Tenant via `[TENANT_CONTACT_METHOD]` confirming the request was received and a vendor has been assigned.
3. Log the event in the **Interaction Log** (exempt from approval).
4. Create/update the **Maintenance Record** in the database to status "Assigned".