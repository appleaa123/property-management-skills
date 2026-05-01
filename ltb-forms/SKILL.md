---
name: ltb-forms
description: Legal notice form workflow. Detects the required form based on jurisdiction and situation, gathers required data, drafts the form, and manages the approval/delivery process.
---

# Legal Notice Form Workflow

This skill teaches the 6-step workflow for preparing legally binding property notices.

## Linear Workflow Steps

### Step 1: Research-First Jurisdiction Detection
**Mandatory**: Do not assume the laws of one region apply to another.
1.  Identify the property's City/State/Province.
2.  **Execute Web Search**: Search for "landlord tenant legal forms [Jurisdiction]" and "notice requirements [Jurisdiction]".
3.  Identify the specific form needed (e.g., "Notice to Quit", "N4", "Form 3").

### Step 2: Data Gathering
Query Property, Tenant, and Landlord records via `[DATABASE_QUERY_TOOL]`.
*   **Meaning**: Use exact legal names and addresses. "Apt 2" is not the same as "Unit 2" legally.

### Step 3: The Gap-Filling Interview (Conversational)
Ask the manager for circumstantial facts not in the database.
*   **Example Dialogue**: "I have the tenant's lease data, but for this 'Notice of Entry', I need to know: what is the specific 4-hour window you plan to enter, and what is the reason for the visit?"

### Step 4: Draft Generation
Use `references/jurisdiction-template.md` as a structural guide (using Ontario as a worked example) to write the text of the form for the current jurisdiction.

### Step 5: Fiduciary Approval
Present the full text to the manager via `[MANAGER_CHANNEL]`.
**You must receive explicit "Approved" before serving the notice.**

### Step 6: Serve & Audit
Advise the manager on legal service methods (e.g. Registered Mail vs. Email). Log the service event in the Interaction Log.

## Reference Files
- `references/form-workflow.md` — The 6-step legal logic.
- `references/jurisdiction-template.md` — Ontario worked example for form structure.
- `references/data-concepts.md` — Legal entity requirements.