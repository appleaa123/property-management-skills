---
name: manager-persona
description: Extracts the manager's communication style, urgency signals, and approval preferences to create a persona guide. Use this skill to ensure all AI-generated communications match the manager's unique voice and decision-making style.
---

# Manager Persona Extraction Skill

This skill builds a "Manager Persona" profile to ensure all AI communications align with the manager's voice and priorities.

## Data Concepts Required

This workflow relies on the **Interaction (Audit) Log** entity.
See: `property-db/references/data-concepts.md`.

## Linear Workflow Steps

### Step 1: Identify Data Source (Conversational Onboarding)
Determine if you should analyze existing logs or conduct an interview.
*   **Example Dialogue**: "To make sure I sound just like you when I talk to tenants, I'd like to build a communication profile. Should I look through your past sent messages in the log, or would you prefer a quick 5-minute interview?"

### Step 2: Extraction (Data-Driven or Interview)
*   **Method A (Logs)**: Analyze the last 50 messages for tone, brevity, and formatting.
*   **Method B (Interview)**: Use the structured script in `references/extraction-guide.md`. **Ask only 1-2 questions at a time.**

### Step 3: Synthesis of Dimensions
Compile the finding into a profile. You must understand the **Meaning** of each dimension:
1.  **Tone**: Does the manager prioritize "Legal Precision" (Formal) or "Community Building" (Casual)?
2.  **Urgency**: What specific keywords trigger a "Drop Everything" response from the manager?
3.  **Approval Style**: Is the manager a "Details First" reviewer or a "Big Picture" delegator?

### Step 4: Draft Persona Profile
Draft the document using `references/persona-template.md`.
*   **Meaning**: Include a "Golden Set" of examples that other AI agents can use as few-shot prompts.

### Step 5: Fiduciary Review & HITL Approval
Present the drafted persona to the manager via `[MANAGER_CHANNEL]`.
**Wait for explicit approval**. The manager must confirm: "This sounds like me."

## Reference Files
- `references/persona-template.md` — The standardized profile format.
- `references/extraction-guide.md` — Analysis methodology and interview script.