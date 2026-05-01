---
name: ltb-forms
description: Legal notice form workflow. Detects the required form based on jurisdiction and situation (e.g., eviction, late rent, entering unit), gathers required data, drafts the form, and manages the approval/delivery process.
---

# Legal Notice Form Workflow

This skill teaches you the universal workflow for identifying, drafting, and delivering legal property management notices across any jurisdiction.

## Data Concepts Required

This workflow relies on the core property management entities to populate forms accurately.
See: `references/data-concepts.md`

## Universal Form Workflow

Legal forms carry significant risk. You must follow a strict, 6-step process to ensure compliance, accuracy, and manager approval.
Do not skip steps.
See: `references/form-workflow.md`

### Step 1: Jurisdiction & Form Detection
When the manager requests a form (e.g., "I need to evict the tenant at 123 Main St for non-payment"), first identify the property's jurisdiction (State/Province).
Determine the correct form name or number for that specific jurisdiction. If you do not know it, use a web search tool to find the official government landlord-tenant forms for that region.

### Step 2: Data Gathering
Query the user's database (`[DATABASE_QUERY_TOOL]`) to gather the required entities (Tenant, Property, Manager/Landlord details).

### Step 3: Gap-Filling (Interview)
Legal forms often require specific circumstantial data not stored in a database (e.g., "What time will the repair person enter?", "What are the details of the noise complaint?").
You MUST ask the manager for any missing information before attempting to generate the form. Do not invent circumstantial details.

### Step 4: Draft Generation
Generate the text of the form. Use the official structure required by the jurisdiction.
See `references/jurisdiction-template.md` for a worked example of how a jurisdiction's forms are structured.

### Step 5: Manager Approval
Send the completed draft to the manager via `[MANAGER_CHANNEL]`.
**You must receive explicit approval before proceeding.** (See `property-db` HITL rules).

### Step 6: Delivery & Audit
Once approved:
1. Deliver the final form to the tenant via their legally recognized `[TENANT_CONTACT_METHOD]` (note: some jurisdictions require physical mailing or posting on the door; advise the manager if electronic delivery is insufficient).
2. Log the delivery in the **Interaction Log**.