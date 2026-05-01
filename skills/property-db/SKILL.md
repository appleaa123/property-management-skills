---
name: property-db
description: Defines the conceptual data model for property management and the rules for accessing the user's database. Use this skill when you need to understand how properties, tenants, vendors, maintenance requests, and interaction histories relate to each other, and the safety rules (HITL) for reading or modifying this data.
---

# Property Database Access Skill

This skill teaches you the conceptual data models (entities) that make up a property management system and the safety rules for interacting with that data. Because every user stores their data differently (e.g., SQL databases, spreadsheets, custom APIs, or CRM software), your primary goal is to map these universal concepts to the user's specific system.

## Data Source Onboarding (First Invocation)

If you have not yet learned how the user stores their data, you must ask them before attempting any database operations:
1. "Where is your property management data stored?"
2. "What tool should I use to query or update this data?" (e.g., `[DATABASE_QUERY_TOOL]`, an API integration, or a spreadsheet reader).
3. "What do your records look like for Properties, Tenants, Vendors, Maintenance, and Interactions?"

Once you understand their schema, map their fields to the conceptual entities defined below.

## Conceptual Data Models

Before executing any workflow, review the universal data entities and their relationships.
See: `references/core-entities.md`

## Safety Rules (Human-in-the-Loop)

You are operating as a fiduciary agent on behalf of the property manager. Strict rules apply to how data is accessed and modified.
See: `references/hitl-rules.md`

## Workflow: Interacting with Data

1. **Understand the Goal**: Identify which entities you need to query or update based on the task (e.g., finding a tenant's email requires querying the Tenant entity, which relates to a Property entity).
2. **Consult HITL Rules**: Check `references/hitl-rules.md` to determine if the operation requires explicit manager approval.
3. **Execute the Operation**: Use the user's specified `[DATABASE_QUERY_TOOL]` or integration to read or write the data, translating the conceptual fields from `references/core-entities.md` into the user's specific schema.
4. **Audit**: If you perform any action (sending an email, creating a work order, updating a status), you MUST log an Interaction record. Audit logs are always exempt from approval requirements.