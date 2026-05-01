# Data Concepts: Rent Adjustment

To execute the rent adjustment workflow, you must understand how the user stores the following core entities (defined in the `property-db` skill):

## 1. Tenant (Lease) Record
*   **What you need**: The ability to query tenants by their "Lease Start Date" to find upcoming anniversaries. You must also be able to retrieve the "Current Rent Amount" and the "Last Rent Adjustment Date" (to ensure an increase hasn't already happened in the last 12 months).

## 2. Property Record
*   **What you need**: The full address and jurisdiction (City, State/Province) to accurately research local rent control laws. You also need bedroom/bathroom counts if available for market research.