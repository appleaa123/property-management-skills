---
name: manager-persona
description: Extracts the manager's communication style, urgency signals, and approval preferences to create a persona guide. Use this skill to ensure all AI-generated communications match the manager's unique voice and decision-making style.
---

# Manager Persona Extraction Skill

This skill analyzes historical data (or conducts an interview) to build a "Manager Persona" profile. Other agents and skills will use this profile to sound like the manager and understand their priorities.

## Data Concepts Required

This workflow relies on understanding the **Interaction (Audit) Log** entity.
See: `references/data-concepts.md` (from the `property-db` skill).

## Extraction Workflow

### Step 1: Identify Data Source
Determine how the manager wants to build their persona:
*   **Path A (Data-Driven)**: Does the user have a substantial Interaction Log or history of sent emails/messages they can provide via `[DATABASE_QUERY_TOOL]`?
*   **Path B (Interview)**: If no history is available, or if the manager prefers, conduct a direct interview.

### Step 2: Extract or Interview
*   **If Path A (Data-Driven)**:
    Query the Interaction Log for the last 50-100 outbound messages sent by the manager to tenants or vendors. Analyze these messages using the methodology in `references/extraction-guide.md`.
*   **If Path B (Interview)**:
    Conduct a Q&A session with the manager via `[MANAGER_CHANNEL]`. Ask the questions outlined in the Interview Script section of `references/extraction-guide.md`. **Ask a maximum of 2 questions at a time** to avoid overwhelming the user.

### Step 3: Synthesize
Compile the findings from the data analysis or the interview.
Identify key patterns in:
1.  **Tone & Formality** (e.g., strict and legal vs. warm and casual).
2.  **Urgency Signals** (e.g., what specific issues make the manager act immediately).
3.  **Approval Style** (e.g., micro-manager who wants to see every detail vs. macro-manager who only wants financial summaries).

### Step 4: Draft Persona Profile
Draft the final persona document.
Format strictly according to `references/persona-template.md`.

### Step 5: Review and Save
Present the drafted persona to the manager via `[MANAGER_CHANNEL]` for review.
Once approved, ask the manager where they would like this persona document saved so that other AI agents can access it during future workflows.