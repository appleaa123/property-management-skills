# Core Property Management Entities

This document defines the 5 core conceptual entities in a property management system. Users will store this data differently; your job is to map these concepts to their specific schema.

## 1. Property Record
Represents the physical asset being managed.

*   **Purpose**: The central node that all other entities connect to.
*   **Required Conceptual Fields**:
    *   **Unique Identifier**: To distinguish this unit from others.
    *   **Address**: The physical location (Street, City, Region).
    *   **Geographic Identifier**: Postal code, zip code, or neighborhood (used for routing/clustering).
    *   **Current Status**: Flags indicating condition (e.g., "vacant", "occupied", "fix_needed", "late_payment").
*   **Questions to ask the user**: "What field do you use to track if a property needs attention?" "How do you group properties geographically?"

## 2. Tenant (or Resident) Record
Represents the person(s) occupying a property.

*   **Purpose**: For communication, lease enforcement, and rent collection.
*   **Relationships**: Must link to a specific Property Record.
*   **Required Conceptual Fields**:
    *   **Unique Identifier**.
    *   **Name**: Primary contact.
    *   **Contact Methods**: Email, phone number, or preferred messaging handle (`[TENANT_CONTACT_METHOD]`).
*   **Optional Fields (Lease Details)**:
    *   Lease start/end dates.
    *   Current rent amount.
    *   Last rent adjustment date.
*   **Questions to ask the user**: "Where do you store lease terms and rent amounts?" "Do you have a preferred channel for contacting tenants?"

## 3. Vendor (or Contractor) Record
Represents a third-party service provider.

*   **Purpose**: For dispatching maintenance and repairs.
*   **Required Conceptual Fields**:
    *   **Company/Contact Name**.
    *   **Contact Methods**: Phone, email, dispatch portal.
    *   **Trade/Specialty**: What they fix (e.g., Plumbing, Electrical, HVAC, General Handyman).
    *   **Service Area**: Which geographic identifiers they cover.
*   **Questions to ask the user**: "How do you categorize what type of work a vendor does?"

## 4. Maintenance (or Work Order) Record
Represents an issue that needs fixing.

*   **Purpose**: Tracking repairs from report to resolution.
*   **Relationships**: Must link to a Property, usually links to a reporting Tenant, and eventually links to an assigned Vendor.
*   **Required Conceptual Fields**:
    *   **Description of Issue**: What is broken.
    *   **Reported Date**.
    *   **Urgency/Classification**: Emergency vs. Routine.
    *   **Current Status**: Open, Assigned, In Progress, Completed.
*   **Questions to ask the user**: "How do you currently receive and log maintenance requests?"

## 5. Interaction (or Audit) Log
Represents a historical record of actions taken or messages sent.

*   **Purpose**: Maintaining a verifiable history of communication and decisions.
*   **Relationships**: Can link to a Property, Tenant, or Maintenance record.
*   **Required Conceptual Fields**:
    *   **Timestamp**: When it happened.
    *   **Summary**: A concise description of the event (e.g., "Sent visit confirmation request for [date]").
    *   **Channel**: How it happened (e.g., Email, SMS, System Status Change).
*   **Questions to ask the user**: "Where should I write audit logs when I take actions autonomously?"