---
name: ltb-forms
description: "Auto-populate jurisdiction-appropriate rental notice forms (N1/N4/N9/N12 for Ontario, or any registered jurisdiction) using tenant/property data. Supports batch mode, manager approval, and form delivery via email or messaging."
---

# LTB Forms Skill

Fills rental notice forms for any jurisdiction using pypdf and your property database. Ontario (CA-ON) is fully configured out of the box. Other jurisdictions can be added via the Form Onboarding workflow at the bottom of this skill.

## Tool Requirements

- **Database client** — read tenant and property data (see `property-db` skill)
- **Python + pypdf** — fill PDF forms (`pip install pypdf>=4.0.0`)
- **Email client** — send completed forms as attachments (reference: `himalaya`)
- **Messaging** — send form summaries and approval requests to operator
- **File system** — read blank form PDFs, write completed PDFs to `{OUTPUT_DIR}` (set env var, default `./forms/`)

## References

- `skills/ltb-forms/scripts/fill_ltb_form.py` — pypdf field mapping and PDF generation
- `skills/ltb-forms/form-registry.yaml` — jurisdiction → form code → blank PDF path and field map
- Blank forms: `skills/ltb-forms/assets/CA-ON/N1-blank.pdf`, `N4-blank.pdf`, `N9-blank.pdf`, `N12-blank.pdf`

## Ontario Form Types (CA-ON)

| Form | Purpose                                     | Trigger Phrase              |
| ---- | ------------------------------------------- | --------------------------- |
| N1   | Notice of Rent Increase                     | "generate N1 for [tenant]"  |
| N4   | Notice to End Tenancy — Non-Payment of Rent | "generate N4 for [tenant]"  |
| N9   | Tenant's Notice to Terminate Tenancy        | "generate N9 for [tenant]"  |
| N12  | Notice to End Tenancy — Landlord's Own Use  | "generate N12 for [tenant]" |

Other jurisdictions: check `form-registry.yaml` for registered forms. If the needed jurisdiction has no forms registered yet, use the Form Onboarding workflow.

## Workflow

### Step 0: Detect Jurisdiction

Read `province`, `state`, and `country` from the queried property record (Step 2 populates this).

- Canadian property → jurisdiction = `CA-[PROVINCE_CODE]` (e.g., `CA-ON` for Ontario, `CA-BC` for BC)
- US property → jurisdiction = `US-[STATE_CODE]` (e.g., `US-CA` for California)
- International → ask operator for jurisdiction code if unclear

Look up the jurisdiction in `form-registry.yaml`. If the jurisdiction has no registered forms:

> "This property is in [region]. I don't have forms registered for that jurisdiction yet. Would you like to add them? I can walk you through the form onboarding process."

If yes, jump to the **Form Onboarding** section.

### Step 1: Identify Form and Tenant

Parse trigger phrase to identify form type (N1/N4/N9/N12) and tenant name or address.

**Batch mode:** If the request names 2 or more tenants or asks for multiple forms, activate batch mode. In batch mode: run Steps 2–4 for every form first (fill all PDFs), then run a single Step 5b batch HITL, then a single Step 6a grouping step. Steps 5 and 6 are skipped in batch mode. Track each generated form in a **manifest**: `[N]. [FORM_TYPE] — [tenant name] — [address], [city] → [tenant_id]_[FORM_TYPE].pdf`.

**N1 batch mode:** If any N1 forms are in the batch, run Step 3b ONCE before the Step 2–4 loop to collect all rent amounts and effective dates upfront.

### Step 2: Query Property Database

Query your database for tenant and property data. Example (PostgREST/Supabase reference):

```bash
# Match by tenant name
curl -s "$DB_URL/rest/v1/tenant?select=tenant_id,name,email,phone,lease_start,rent_amount,property_id,properties(address,city,province,postalcode,landlord_name,landlord_phone)&name=ilike.*[name]*" \
  -H "apikey: $DB_KEY" -H "Authorization: Bearer $DB_KEY"

# OR match by property address
curl -s "$DB_URL/rest/v1/tenant?select=tenant_id,name,email,phone,lease_start,rent_amount,property_id,properties(address,city,province,postalcode,landlord_name,landlord_phone)&properties.address=ilike.*[address]*" \
  -H "apikey: $DB_KEY" -H "Authorization: Bearer $DB_KEY"
```

**Join rule:** Query the `tenant` table first. Use the returned `property_id` to resolve all landlord information from the `properties` table. Never guess the landlord from names or addresses — always join via `property_id`.

**Name splitting rule:** For `RFirstName[0]` and `RLastName[0]`, split the full name on the first space. Example: `"Bob Landlord"` → `RFirstName="Bob"`, `RLastName="Landlord"`. If only one word exists, use it as last name and leave first name blank.

**Data source per form type — who sends to whom:**

| PDF Field              | N1 (Landlord → Tenant)                           | N4 (Landlord → Tenant)                           | N9 (Tenant → Landlord)                                    | N12 (Landlord → Tenant)                          |
| ---------------------- | ------------------------------------------------ | ------------------------------------------------ | --------------------------------------------------------- | ------------------------------------------------ |
| `To_TenantName[0]`     | `tenant.name` — tenant **receives** notice       | —                                                | —                                                         | —                                                |
| `TO_TenameName[0]`     | —                                                | `tenant.name` — tenant **receives** notice       | `properties.landlord_name` — landlord **receives** notice | `tenant.name` — tenant **receives** notice       |
| `From_LandlordName[0]` | `properties.landlord_name` — landlord **sends**  | `properties.landlord_name` — landlord **sends**  | `tenant.name` — tenant **sends**                          | `properties.landlord_name` — landlord **sends**  |
| `RentUnitAddress[0]`   | `properties.address` — N1 only                   | —                                                | —                                                         | —                                                |
| `RentalUnitAddress[0]` | —                                                | `properties.address`                             | `properties.address`                                      | `properties.address`                             |
| `SignName[0]`          | `properties.landlord_name` (full name — N1 only) | —                                                | —                                                         | —                                                |
| `RFirstName[0]`        | —                                                | landlord first name (split from `landlord_name`) | tenant first name (split from `tenant.name`)              | landlord first name (split from `landlord_name`) |
| `RLastName[0]`         | —                                                | landlord last name (split from `landlord_name`)  | tenant last name (split from `tenant.name`)               | landlord last name (split from `landlord_name`)  |
| `SignPhoneNum[0]`      | `properties.landlord_phone` — N1 only            | —                                                | —                                                         | —                                                |
| `RDayPhone[0]`         | —                                                | `properties.landlord_phone`                      | `tenant.phone`                                            | `properties.landlord_phone`                      |

> **N1 field name differences:** N1 uses `To_TenantName[0]` (not `TO_TenameName`), `RentUnitAddress[0]` (not `RentalUnitAddress`), and `SignName[0]`/`SignPhoneNum[0]` instead of split `RFirstName`/`RLastName`/`RDayPhone`. Use the exact names above — do not substitute.

### Step 2b: Handle Missing landlord_phone

If `landlord_phone` is NULL in the query result, ask the operator:

> "The landlord phone is not on file for [address]. What is the day phone number for [landlord_name]?"

Use the provided number to fill `RDayPhone[0]`. After the form is approved (Step 5), ask:

> "Save [phone] as the landlord phone for [address] in the database for future use? Reply YES to confirm."

Only update the database if the operator replies YES.

### Step 2c: Value Format Rules

Apply these formats before passing values to `--fields`:

| Field                                 | Format                                                           | Example                           | Why                                                                                                                                                                                    |
| ------------------------------------- | ---------------------------------------------------------------- | --------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `StartDate` (N1)                      | `DD MM YYYY`                                                     | `01 07 2026`                      | N1 only — form pre-prints `/` separators                                                                                                                                               |
| `PayDate`, `ArrearFrom*`, `ArrearTo*` | `DD MM YYYY`                                                     | `03 04 2026`                      | N4 only — form pre-prints `/` separators                                                                                                                                               |
| `TerminationDate`                     | `DD MM YYYY`                                                     | `30 04 2026`                      | N9/N12 — form pre-prints `/` separators                                                                                                                                                |
| `SignDate` (all forms)                | `DD/MM/YYYY`                                                     | `20/03/2026`                      | No pre-printed separators; explicit slashes required                                                                                                                                   |
| `RDayPhone` (all forms)               | `[space]NXX NXX XXXX`                                            | ` 416 555 0001`                   | Form pre-prints `(`, `)`, `-`; leading space offsets the first `(`                                                                                                                     |
| `SignPhoneNum` (N1)                   | `[space]NXX NXX XXXX`                                            | ` 416 555 0001`                   | Same format as `RDayPhone` — leading space offsets the first `(`                                                                                                                       |
| `RentIncAmount1[0]` (N1)              | Integer portion right-padded to 6 chars + `.` + 2 decimal digits | `"    20.00"` for $20.00 increase | Form pre-prints `$` and `.`; digits must right-align with the decimal point. Calculate as `new_rent − tenant.rent_amount`. Format: `f"{int(delta):>6}.{round((delta % 1) * 100):02d}"` |

### Step 3: Check for Missing Required Fields

Before filling, verify all **Required** fields (marked in the Field Reference tables below) are available or can be calculated.

**N1 — additional pre-fill questions (ask before generating, single-form mode only):**

**Q1 — New rent amount:**

> "What is the new monthly rent amount for [tenant name] at [address]?
> Current rent: $[tenant.rent_amount]. Ontario 2026 guideline max (2.1%): $[rent_amount × 1.021 rounded to 2dp]."

**Q2 — Effective date:**

> "What is the effective date of the rent increase? (Must be at least 90 days from today — earliest: [today + 90 days formatted DD/MM/YYYY])"

**N1 validation warnings** (show before proceeding — do not block):

- If `tenant.last_rent_adjustment_date` is less than 12 months before the effective date: "⚠️ Last increase was [last_rent_adjustment_date] — less than 12 months before the proposed effective date. Verify eligibility before issuing."
- If proposed increase > 2.1%: "⚠️ Proposed increase ([X]%) exceeds the Ontario 2026 guideline (2.1%). Above-guideline increases require a separate LTB application (AGI)."

Calculate `RentIncPercent[0]` as: `((new_rent / current_rent) - 1) × 100`, rounded to 2 decimal places.

**Agent fields:** Ask operator if they are using a legal representative. If yes, collect: name, company, LSUC#, address, phone, fax, municipality, province, postal code. If no → leave all agent fields blank.

### Step 3b: N1 Batch Pre-fill Questions (batch mode, N1 forms only)

Run this step ONCE before the Step 2–4 loop. Send ONE message collecting all N1 inputs upfront:

```
📋 N1 BATCH INPUT REQUIRED — [N] forms

Minimum effective date: [today + 90 days as DD/MM/YYYY]

| # | Tenant        | Current Rent | New Rent | Effective Date (DD/MM/YYYY) |
|---|---------------|-------------|----------|----------------------------|
| 1 | [tenant name] | $[amount]   |          |                            |
| 2 | [tenant name] | $[amount]   |          |                            |

Legal agent/representative? (yes / no)
If yes, provide: name, company, LSUC#, address, phone, fax, municipality, province, postal code.

Reply with one line per row, e.g.:
1 | $2,100 | 01/10/2026
2 | $1,850 | 01/10/2026
```

On receipt: validate each effective date ≥ today + 90 days. Show non-blocking validation warnings. Cache as `batch_n1_inputs[tenant_id] = { new_rent, effective_date }`.

### Step 4: Fill Form

Use the exact PDF field names from the Field Reference tables below.

**N1 example (Ontario / CA-ON):**

```bash
python3 skills/ltb-forms/scripts/fill_ltb_form.py \
    --jurisdiction CA-ON --form-code N1 \
    --output ${OUTPUT_DIR:-./forms}/[tenant_id]_N1.pdf \
    --fields '{
      "To_TenantName[0]": "Jane Doe",
      "From_LandlordName[0]": "Bob Landlord",
      "RentUnitAddress[0]": "123 Main St, Toronto ON M5V 1A1",
      "StartDate[0]": "01 07 2026",
      "RentIncAmount1[0]": "    42.00",
      "PaymentPeriodM[0]": "1",
      "RentIncPercent[0]": "2.10",
      "SignName[0]": "Bob Landlord",
      "SignPhoneNum[0]": " 416 555 0001",
      "SignDate[0]": "01/04/2026",
      "Check1[0]": "1",
      "Check2[0]": "1",
      "Check_2_1[0]": "1",
      "Check_2_2[0]": "1",
      "SelectSign[0]": "0"
    }'
```

**N4 example (Ontario / CA-ON):**

```bash
python3 skills/ltb-forms/scripts/fill_ltb_form.py \
    --jurisdiction CA-ON --form-code N4 \
    --output ${OUTPUT_DIR:-./forms}/[tenant_id]_N4.pdf \
    --fields '{
      "TO_TenameName[0]": "Jane Doe",
      "From_LandlordName[0]": "Bob Landlord",
      "RentalUnitAddress[0]": "123 Main St, Toronto ON M5V 1A1",
      "OweMeAmount[0]": "1200.00",
      "PayDate[0]": "17 04 2026",
      "ArrearFrom1[0]": "01 03 2026",
      "ArrearTo1[0]": "31 03 2026",
      "RentCharge1[0]": "1200.00",
      "RentPaid1[0]": "0.00",
      "RentOwe1[0]": "1200.00",
      "TotalRentOwe[0]": "1200.00",
      "RFirstName[0]": "Bob",
      "RLastName[0]": "Landlord",
      "RDayPhone[0]": " 416 555 0001",
      "SignDate[0]": "20/03/2026",
      "CheckList1[0]": "1",
      "CheckList2[0]": "1",
      "CheckList3[0]": "1",
      "CheckList4[0]": "1",
      "CheckList5[0]": "1",
      "CheckList6[0]": "1",
      "CheckList7[0]": "1",
      "SelectSign[0]": "0"
    }'
```

**N9 example:**

> Note: `FileNumber`, `FilingLocation`, and `DeliveryMethod` are office-use only — do not fill.
> Ask operator: "Who is filling the N9 form?" → Tenant = `"0"`, Tenant's Representative = `"1"`.

```bash
python3 skills/ltb-forms/scripts/fill_ltb_form.py \
    --jurisdiction CA-ON --form-code N9 \
    --output ${OUTPUT_DIR:-./forms}/[tenant_id]_N9.pdf \
    --fields '{
      "TO_TenameName[0]": "Bob Landlord",
      "From_LandlordName[0]": "Jane Doe",
      "RentalUnitAddress[0]": "123 Main St, Toronto ON M5V 1A1",
      "TerminationDate[0]": "30 04 2026",
      "RFirstName[0]": "Jane",
      "RLastName[0]": "Doe",
      "RDayPhone[0]": " 416 555 0001",
      "SignDate[0]": "20/03/2026",
      "SelectSign[0]": "0"
    }'
```

**N12 — Step before filling: Ask operator for Reason selection**

**Question 1:**

> "Who intends to move into or provide care services to the rental unit and occupy it for at least one year?"

| Answer                         | Fields to set                         |
| ------------------------------ | ------------------------------------- |
| Landlord themselves            | `Reason1[0]="1"`, `Reason1_A1[0]="1"` |
| Landlord's spouse/partner      | `Reason1[0]="1"`, `Reason1_A2[0]="1"` |
| Child of landlord or spouse    | `Reason1[0]="1"`, `Reason1_A3[0]="1"` |
| Parent of landlord or spouse   | `Reason1[0]="1"`, `Reason1_A4[0]="1"` |
| Caregiver for the above person | `Reason1[0]="1"`, `Reason1_A5[0]="1"` |
| Other qualifying person        | `Reason1[0]="1"`, `Reason1_A6[0]="1"` |

**Question 2:**

> "Who signed an Agreement of Purchase and Sale of the rental unit, and the following person intends to move into the rental unit?"

| Answer                         | Fields to set                         |
| ------------------------------ | ------------------------------------- |
| Purchaser themselves           | `Reason2[0]="1"`, `Reason2_A1[0]="1"` |
| Purchaser's spouse/partner     | `Reason2[0]="1"`, `Reason2_A2[0]="1"` |
| Child of purchaser or spouse   | `Reason2[0]="1"`, `Reason2_A3[0]="1"` |
| Parent of purchaser or spouse  | `Reason2[0]="1"`, `Reason2_A4[0]="1"` |
| Caregiver for the above person | `Reason2[0]="1"`, `Reason2_A5[0]="1"` |
| Other qualifying person        | `Reason2[0]="1"`, `Reason2_A6[0]="1"` |

Include only the Reason group(s) that apply. Leave `Reason1_B*` and `Reason2_B*` fields at default `"0"`.

**N12 example** (Reason 1: Landlord themselves):

```bash
python3 skills/ltb-forms/scripts/fill_ltb_form.py \
    --jurisdiction CA-ON --form-code N12 \
    --output ${OUTPUT_DIR:-./forms}/[tenant_id]_N12.pdf \
    --fields '{
      "TO_TenameName[0]": "Jane Doe",
      "From_LandlordName[0]": "Bob Landlord",
      "RentalUnitAddress[0]": "123 Main St, Toronto ON M5V 1A1",
      "TerminationDate[0]": "30 06 2026",
      "RFirstName[0]": "Bob",
      "RLastName[0]": "Landlord",
      "RDayPhone[0]": " 416 555 0001",
      "SignDate[0]": "20/03/2026",
      "SelectSign[0]": "0",
      "Reason1[0]": "1",
      "Reason1_A1[0]": "1"
    }'
```

If the output contains `WARNING: field(s) not found`, the field names are wrong. Check the Field Reference tables below — do not guess field names.

### Step 5: Operator Approval (single-form mode only)

Send via your messaging channel with a human-readable form summary:

**N1:**
```
📋 FORM READY — N1 for [tenant name]
Property: [address]

FORM SUMMARY:
• To (tenant):       [tenant.name]
• From (landlord):   [properties.landlord_name]
• Rental address:    [properties.address]
• Current rent:      $[tenant.rent_amount]
• New rent:          $[RentIncAmount1] / month
• Increase:          [RentIncPercent]%
• Effective date:    [StartDate formatted DD/MM/YYYY]
• Notice given:      [days from today to StartDate] days
• Signed by:         Landlord / Agent
• Sign date:         [SignDate]

Saved to: [OUTPUT_DIR]/[tenant_id]_N1.pdf
Reply APPROVE to confirm this form is final.
```

**N4:**
```
📋 FORM READY — N4 for [tenant name]
Property: [address]

FORM SUMMARY:
• To (tenant):       [tenant.name]
• From (landlord):   [properties.landlord_name]
• Rental address:    [properties.address]
• Rent owing:        $[OweMeAmount]
• Payment due:       [PayDate formatted DD/MM/YYYY]
• Arrear period(s):  [ArrearFrom1]–[ArrearTo1]
• Signed by:         Landlord / Agent
• Sign date:         [SignDate]

Saved to: [OUTPUT_DIR]/[tenant_id]_N4.pdf
Reply APPROVE to confirm this form is final.
```

**N9:**
```
📋 FORM READY — N9 for [tenant name]
Property: [address]

FORM SUMMARY:
• To (landlord):     [properties.landlord_name]
• From (tenant):     [tenant.name]
• Rental address:    [properties.address]
• Termination date:  [TerminationDate formatted DD/MM/YYYY]
• Signed by:         Tenant / Tenant's Representative
• Sign date:         [SignDate]

Saved to: [OUTPUT_DIR]/[tenant_id]_N9.pdf
Reply APPROVE to confirm this form is final.
```

**N12:**
```
📋 FORM READY — N12 for [tenant name]
Property: [address]

FORM SUMMARY:
• To (tenant):       [tenant.name]
• From (landlord):   [properties.landlord_name]
• Rental address:    [properties.address]
• Termination date:  [TerminationDate formatted DD/MM/YYYY]
• Reason:            [human-readable description]
• Signed by:         Landlord / Landlord's Agent
• Sign date:         [SignDate]

Saved to: [OUTPUT_DIR]/[tenant_id]_N12.pdf
Reply APPROVE to confirm this form is final.
```

### Step 6: PDF Delivery (single-form mode only)

After operator sends `APPROVE` in Step 5, display full form contents in chat and ask for delivery preference:

```
✅ FORM APPROVED — [FORM_TYPE] for [tenant name]

FORM CONTENTS:
To (recipient):        [value]
From (sender):         [value]
Rental address:        [value]
[N4 only] Rent owing:  $[value]
[N4 only] Pay by:      [value]
[N4 only] Arrear(s):   [period(s) and amounts]
[N9/N12] Termination:  [value]
[N12 only] Reason:     [human-readable description]
Signed by:             [role]
Sign date:             [value]

How would you like to receive this form?
1️⃣  Email — send to an email address
2️⃣  Message — send a notification with the file path
3️⃣  Make changes — tell me what to correct

Reply 1, 2, or 3.
```

**Option 1 — Email:**

Ask: `"Send to which email? (Default: [tenant.email])"`. Send via your email tool with the PDF attached. Log delivery to interactions table (HITL-exempt).

**Option 2 — Messaging:**

Ask: `"Send to which phone/contact? (Default: [tenant.phone])"`. Send a message with the form summary and file path. Log delivery to interactions table.

**Option 3 — Make Changes:**

Ask: `"What would you like to change?"`. Return to Step 3 to update the field(s), re-run Step 4 to regenerate, re-run Step 5 for new approval.

**N1 only — post-delivery DB update:**

After delivery, ask:

> "Update the database with the new rent details?
> • `tenant.rent_amount` → $[new_rent]
> • `tenant.last_rent_adjustment_date` → [StartDate as YYYY-MM-DD]
> Reply YES to save."

On YES: run a PATCH to update the tenant record (APPROVE already granted).

---

### Step 5b: Batch Approval (batch mode only)

After all forms are filled, send ONE summary via your messaging channel:

```
📋 BATCH FORMS READY — [N] forms generated

[1]. N4 — Alice Brown — 44 Addison St, Toronto → tenant_001_N4.pdf
[2]. N4 — Bob Chen — 12 Elm St, Richmond Hill → tenant_002_N4.pdf
[3]. N1 — Dave Evans — 8 Maple Ave, Richmond Hill → tenant_004_N1.pdf
[4]. N12 — Eve Foster — 55 King St, Toronto → tenant_005_N12.pdf

Reply:
• APPROVE ALL — approve all forms
• APPROVE 1 3 — approve specific forms by number
• REJECT 2 — discard form 2 (delete PDF, do not deliver)
```

On REJECT: Delete the PDF and log to interactions (rejected forms — HITL-exempt logging). Approved forms proceed to Step 6a.

---

### Step 6a: Batch Grouping & Delivery (batch mode only)

After approval (Step 5b), send ONE grouping question in chat:

```
✅ [N] forms approved. How would you like to group the emails?

Default — reply "default":
  • One email per form type: N4 (×[count]), N1 (×[count]), N12 (×[count])

Or describe custom grouping, e.g.:
  • "Split N4s by city"
  • "One email per tenant"
  • "Everything in one email"
  • "Alice and Bob together, rest separately"
```

**Grouping logic:**

| Instruction | Logic |
| ----------- | ----- |
| "by form type" / "default" | Group by `FORM_TYPE` |
| "by city" | Group by `city` in manifest |
| "per tenant" / "one per tenant" | One email per `tenant_id` |
| "everything" / "one email" | Single group, all PDFs |
| Named tenants | Merge into one group |
| Custom recipient | Override recipient for that group |

For each group, send one email via your email tool with all applicable PDFs attached. Confirm each group in chat after sending. Log one interactions record per tenant per group (HITL-exempt).

**N1 DB updates (batch):** After all groups are sent, if any N1 forms were in the batch, ask once for confirmation to update rent records, then run one PATCH per confirmed N1.

---

## Field Reference

### N1 — Notice of Rent Increase

| PDF field name         | Source                                                                                           | Required?                   |
| ---------------------- | ------------------------------------------------------------------------------------------------ | --------------------------- |
| `To_TenantName[0]`     | `tenant.name`                                                                                    | Required                    |
| `From_LandlordName[0]` | `properties.landlord_name`                                                                       | Required                    |
| `RentUnitAddress[0]`   | `properties.address`                                                                             | Required                    |
| `StartDate[0]`         | Effective date — ask operator (min 90 days from today), format `DD MM YYYY`                      | Required                    |
| `RentIncAmount1[0]`    | Rent increase delta — `new_rent − tenant.rent_amount`, right-justified (see Step 2c format rule) | Required                    |
| `PaymentPeriodM[0]`    | Always `"1"` — checks the Per Month checkbox                                                     | Required (checkbox)         |
| `RentIncPercent[0]`    | `((new_rent / current_rent) - 1) × 100`, 2 decimal places                                        | Required                    |
| `SignName[0]`          | `properties.landlord_name` (full name — no split needed)                                         | Required                    |
| `SignPhoneNum[0]`      | `properties.landlord_phone` (ask operator if NULL)                                               | Required                    |
| `SignDate[0]`          | Today's date (`DD/MM/YYYY`)                                                                      | Required                    |
| `Signature[0]`         | —                                                                                                | Leave blank (wet signature) |
| `SelectSign[0]`        | `"0"` = Landlord signs, `"1"` = Agent signs                                                      | Required (XFA checkbox)     |
| `Check1[0]`            | Always `"1"`                                                                                     | Required (XFA checkbox)     |
| `Check2[0]`            | Always `"1"`                                                                                     | Required (XFA checkbox)     |
| `Check_2_1[0]`         | Always `"1"`                                                                                     | Required (XFA checkbox)     |
| `Check_2_2[0]`         | Always `"1"`                                                                                     | Required (XFA checkbox)     |
| `RentIncAmount2[0]`    | New rent for secondary payment period (e.g. parking)                                             | Optional                    |
| `OtherSpecify[0]`      | Description of secondary payment period                                                          | Optional (if row 2 used)    |
| `AgentName[0]`         | Legal agent name                                                                                 | Ask operator if using agent |
| `AgentLSUC[0]`         | Legal agent LSUC#                                                                                | Ask operator if using agent |
| `AgentCompany[0]`      | Legal agent company                                                                              | Ask operator if using agent |
| `AgentAddress[0]`      | Legal agent address                                                                              | Ask operator if using agent |
| `AgentPhoneNum[0]`     | Legal agent phone                                                                                | Ask operator if using agent |
| `AgentMunicipality[0]` | Legal agent municipality                                                                         | Ask operator if using agent |
| `AgentProvince[0]`     | Legal agent province                                                                             | Ask operator if using agent |
| `AgentPostCode[0]`     | Legal agent postal code                                                                          | Ask operator if using agent |
| `AgentFaxNum[0]`       | Legal agent fax                                                                                  | Ask operator if using agent |

### N4 — Non-Payment of Rent

| PDF field name                   | Source                                                              | Required?                            |
| -------------------------------- | ------------------------------------------------------------------- | ------------------------------------ |
| `TO_TenameName[0]`               | `tenant.name`                                                       | Required                             |
| `From_LandlordName[0]`           | `properties.landlord_name`                                          | Required                             |
| `RentalUnitAddress[0]`           | `properties.address`                                                | Required                             |
| `OweMeAmount[0]`                 | Calculated total arrears                                            | Required                             |
| `PayDate[0]`                     | 14 days from today                                                  | Required                             |
| `ArrearFrom1[0]`                 | Arrear row 1 — period start                                         | Required                             |
| `ArrearTo1[0]`                   | Arrear row 1 — period end                                           | Required                             |
| `RentCharge1[0]`                 | Rent charged row 1                                                  | Required                             |
| `RentPaid1[0]`                   | Rent paid row 1                                                     | Required                             |
| `RentOwe1[0]`                    | Rent owing row 1                                                    | Required                             |
| `ArrearFrom2[0]` … `RentOwe3[0]` | Arrear rows 2–3                                                     | Optional (leave blank if only 1 row) |
| `TotalRentOwe[0]`                | Sum of all RentOwe rows                                             | Required                             |
| `RFirstName[0]`                  | Landlord first name                                                 | Required                             |
| `RLastName[0]`                   | Landlord last name                                                  | Required                             |
| `RDayPhone[0]`                   | `properties.landlord_phone` (ask operator only if NULL)             | Required                             |
| `SignDate[0]`                    | Today's date                                                        | Required                             |
| `Signature[0]`                   | —                                                                   | Leave blank (wet signature)          |
| `AgentName[0]` … `AgentFaxNum[0]`| Legal agent details                                                 | Ask operator if using agent          |
| `CheckList1[0]`                  | Always `"1"` — waited until day after rent due?                     | Required (XFA checkbox)              |
| `CheckList2[0]`                  | Always `"1"` — correct termination date filled?                     | Required (XFA checkbox)              |
| `CheckList3[0]`                  | Always `"1"` — all tenants in possession named?                     | Required (XFA checkbox)              |
| `CheckList4[0]`                  | Always `"1"` — complete rental unit address filled?                 | Required (XFA checkbox)              |
| `CheckList5[0]`                  | Always `"1"` — math checked?                                        | Required (XFA checkbox)              |
| `CheckList6[0]`                  | Always `"1"` — only rent amounts included?                          | Required (XFA checkbox)              |
| `CheckList7[0]`                  | Always `"1"` — notice signed and dated?                             | Required (XFA checkbox)              |
| `SelectSign[0]`                  | `"0"` = Landlord signs, `"1"` = Agent signs                         | Required (XFA checkbox)              |

### N9 — Tenant's Notice to Terminate

| PDF field name         | Source                                                                                      | Required?                     |
| ---------------------- | ------------------------------------------------------------------------------------------- | ----------------------------- |
| `TO_TenameName[0]`     | `properties.landlord_name` (recipient — the landlord)                                       | Required                      |
| `From_LandlordName[0]` | `tenant.name` (sender — the tenant)                                                         | Required                      |
| `RentalUnitAddress[0]` | `properties.address`                                                                        | Required                      |
| `TerminationDate[0]`   | Termination date (`DD MM YYYY`)                                                             | Required                      |
| `RFirstName[0]`        | Tenant first name (or representative if SelectSign=1)                                       | Required                      |
| `RLastName[0]`         | Tenant last name (or representative if SelectSign=1)                                        | Required                      |
| `RDayPhone[0]`         | Tenant's day phone (ask operator if unknown)                                                | Required                      |
| `SignDate[0]`          | Today's date (`DD/MM/YYYY`)                                                                 | Required                      |
| `SelectSign[0]`        | `"0"` = Tenant signs, `"1"` = Tenant's Representative signs — ask: "Who is filling the N9?" | Required (XFA checkbox)       |
| `Signature[0]`         | —                                                                                           | Leave blank (wet signature)   |
| `FileNumber[0]`        | —                                                                                           | Office use only — leave blank |
| `FilingLocation[0]`    | —                                                                                           | Office use only — leave blank |

### N12 — Landlord's Own Use

| PDF field name         | Source                                                                                  | Required?                     |
| ---------------------- | --------------------------------------------------------------------------------------- | ----------------------------- |
| `TO_TenameName[0]`     | `tenant.name`                                                                           | Required                      |
| `From_LandlordName[0]` | `properties.landlord_name`                                                              | Required                      |
| `RentalUnitAddress[0]` | `properties.address`                                                                    | Required                      |
| `TerminationDate[0]`   | Termination date (`DD MM YYYY`)                                                         | Required                      |
| `RFirstName[0]`        | Landlord first name                                                                     | Required                      |
| `RLastName[0]`         | Landlord last name                                                                      | Required                      |
| `RDayPhone[0]`         | `properties.landlord_phone` (ask operator only if NULL)                                 | Required                      |
| `SignDate[0]`          | Today's date (`DD/MM/YYYY`)                                                             | Required                      |
| `SelectSign[0]`        | `"0"` = Landlord signs, `"1"` = Landlord's Agent signs — ask: "Who is signing the N12?" | Required (XFA checkbox)       |
| `Reason1[0]`           | `"1"` if landlord/family moving in                                                      | Conditional                   |
| `Reason1_A1[0]`        | `"1"` = Landlord themselves                                                             | Set per Q1 answer             |
| `Reason1_A2[0]`        | `"1"` = Landlord's spouse/partner                                                       | Set per Q1 answer             |
| `Reason1_A3[0]`        | `"1"` = Child of landlord or spouse                                                     | Set per Q1 answer             |
| `Reason1_A4[0]`        | `"1"` = Parent of landlord or spouse                                                    | Set per Q1 answer             |
| `Reason1_A5[0]`        | `"1"` = Caregiver for above person                                                      | Set per Q1 answer             |
| `Reason1_A6[0]`        | `"1"` = Other qualifying person                                                         | Set per Q1 answer             |
| `Reason2[0]`           | `"1"` if purchaser moving in                                                            | Conditional                   |
| `Reason2_A1[0]` … `Reason2_A6[0]` | Purchaser-side sub-reasons (same pattern as Reason1)                         | Set per Q2 answer             |
| `Signature[0]`         | —                                                                                       | Leave blank (wet signature)   |
| `FileNumber[0]`        | —                                                                                       | Office use only — leave blank |
| `FilingLocation[0]`    | —                                                                                       | Office use only — leave blank |
| `AgentName[0]` … `AgentFaxNum[0]` | Legal agent details                                                          | Ask operator if using agent   |

---

## Expense Reports

When operator says "generate expense report for [address]":

Query your database for all maintenance records with non-null `expense_amount` for that address, ordered by date. Format as:

```
EXPENSE REPORT — [address]
Generated: [date]

DATE        ISSUE TYPE     VENDOR              COST
[date]      [type]         [worker]            $[amount]
─────────────────────────────────────────────────────
TOTAL:                                         $[total]
(Prices include applicable tax)
```

Save to `{OUTPUT_DIR}/[property_address]_expenses.txt` and send summary via your messaging channel.

---

## Form Onboarding — Adding a New Jurisdiction

Use this workflow when an operator wants to add forms for a jurisdiction not yet in `form-registry.yaml`.

**What you need from the operator (choose one path):**

- **Path A**: A blank PDF form
- **Path B**: A blank PDF form + a hand-filled sample (to infer field mapping automatically)
- **Path C**: A blank PDF form + plain-English descriptions of each field

### Onboarding Step 1: Receive the Blank Form

Operator places the blank PDF in `skills/ltb-forms/assets/[JURISDICTION]/[FORM_CODE]-blank.pdf`.

### Onboarding Step 2: Inspect Fields

```bash
python3 skills/ltb-forms/scripts/fill_ltb_form.py \
    --jurisdiction [JURISDICTION] --form-code [FORM_CODE] --inspect
```

Present the field list to operator with all text fields and checkboxes.

### Onboarding Step 3: Build Field Mapping (HITL)

**Path A:** Ask operator to identify recipient name, sender name, rental address, key date(s), and signer name/phone.

**Path B:** Inspect the sample PDF, infer mapping from field values, present to operator for correction.

**Path C:** Parse operator's plain-English description directly.

In all paths, present proposed mapping and wait for APPROVE before proceeding.

### Onboarding Step 4: Test Fill (HITL)

Generate a test PDF with dummy data:

```bash
python3 skills/ltb-forms/scripts/fill_ltb_form.py \
    --jurisdiction [JURISDICTION] --form-code [FORM_CODE] \
    --output ${OUTPUT_DIR:-./forms}/TEST_[JURISDICTION]_[FORM_CODE].pdf \
    --fields '{ "<field_name>": "<dummy_value>", ... }'
```

Ask operator to review. Reply APPROVE to proceed, or describe corrections.

### Onboarding Step 5: Register in form-registry.yaml (HITL)

After approval, propose the registry addition:

```
📋 REGISTRY UPDATE PROPOSAL

  [JURISDICTION]:
    name: "[full jurisdiction name]"
    authority: "[tribunal or authority name]"
    governing_law: "[legislation name]"
    forms:
      [FORM_CODE]:
        file: "[JURISDICTION]/[FORM_CODE]-blank.pdf"
        purpose: "[one-line purpose]"
        field_map:
          recipient_name: "[field_name]"
          sender_name:    "[field_name]"
          address:        "[field_name]"
          ...

Reply APPROVE to write this to form-registry.yaml.
```

On APPROVE, append to `skills/ltb-forms/form-registry.yaml` under `jurisdictions:`.
