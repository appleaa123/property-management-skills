# Data Concepts: Client Care Route

To execute the route planning workflow, you must understand how the user stores the following core entities (defined in the `property-db` skill):

## 1. Property Record
*   **What you need**: The ability to query properties by their "Current Status" to find those that need attention (e.g., pending repairs, arrears). You must also be able to retrieve the address and the "Geographic Identifier" (postal/zip code) for routing.

## 2. Tenant Record
*   **What you need**: The ability to link the flagged property to the current tenant and retrieve their name and contact details (`[TENANT_CONTACT_METHOD]`).

## 3. Interaction Log
*   **What you need**: The ability to write records when you send confirmation requests and when you receive tenant replies, ensuring an audit trail.