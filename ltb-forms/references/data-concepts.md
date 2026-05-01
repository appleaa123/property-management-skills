# Data Concepts: Legal Forms

To draft legal notices, you must understand how the user stores the following core entities (defined in the `property-db` skill):

## 1. Property Record
*   **What you need**: The full, exact legal address of the rental unit. Abbreviations or nicknames are often invalid on legal forms. You need the jurisdiction (City, State/Province/Region) to determine which laws apply.

## 2. Tenant (Lease) Record
*   **What you need**: The exact legal names of all leaseholders. You also need their contact information (`[TENANT_CONTACT_METHOD]`) for delivery, and often specific lease terms (start date, rent amount, deposit held).

## 3. Landlord/Manager Information
*   **What you need**: Legal forms require the sender's full legal name (often a corporate entity, not just the manager's first name), mailing address, and signature line. If this is not in the database, you must ask the manager for it during the Gap-Filling phase.

## 4. Interaction Log
*   **What you need**: To record exactly when and how the notice was served. This log may be required as evidence in a tribunal or court.