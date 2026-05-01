# Data Concepts: Maintenance Triage

To execute the maintenance triage workflow, you must understand how the user stores the following core entities (defined in the `property-db` skill):

## 1. Maintenance (Work Order) Record
*   **What you need**: The ability to create a new record or update an existing one's status to "Assigned". You need to know the fields for description, date, urgency, and status.

## 2. Vendor Record
*   **What you need**: The ability to search the vendor list by "Trade/Specialty" (e.g., who does plumbing?) and "Service Area" (e.g., do they cover this zip code?). You also need their dispatch contact info.

## 3. Property & Tenant Records
*   **What you need**: To link the incoming request to a specific property and tenant, and to retrieve the property's geographic identifier to find the right vendor.

## 4. Interaction Log
*   **What you need**: The ability to append a record stating that the tenant was notified and the vendor was dispatched.