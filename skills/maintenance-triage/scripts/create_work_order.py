#!/usr/bin/env python3
"""
Generate a structured work order for a maintenance request.
Used by the maintenance-triage skill to format data for manager review.

Usage:
    python create_work_order.py \
        --address "123 Main St, Toronto" \
        --tenant-name "Jane Doe" \
        --tenant-phone "+16471234567" \
        --tenant-email "jane@example.com" \
        --issue-type "appliance" \
        --description "Washer not spinning" \
        --appliance-model "Samsung WF45T6000AW" \
        --vendors '{"plumber": [{"name": "Bob Fix", "phone": "4161234567", "notes": "Available Mon-Fri"}]}'
"""

import argparse
import json
import sys
from datetime import date

WORK_ORDER_TEMPLATE = """\
===========================================
MAINTENANCE WORK ORDER DRAFT
===========================================
Date:          {date}
Property:      {address}

TENANT
  Name:        {tenant_name}
  Phone:       {tenant_phone}
  Email:       {tenant_email}

ISSUE
  Type:        {issue_type}
  Description: {description}
  {appliance_line}

VENDOR OPTIONS
{vendor_list}

STATUS: Awaiting manager approval (APPROVE to dispatch Vendor 1)
===========================================
"""

APPLIANCE_LINE_TEMPLATE = "Appliance:   {model}"
VENDOR_LINE_TEMPLATE = "  {num}. {name}\n     Phone: {phone}\n     Notes: {notes}"


def format_vendors(vendors_json: str) -> str:
    try:
        vendors = json.loads(vendors_json)
    except json.JSONDecodeError:
        return "  No vendors found — manual lookup required."

    lines = []
    num = 1
    if isinstance(vendors, list):
        vendor_list = vendors
    elif isinstance(vendors, dict):
        vendor_list = []
        for items in vendors.values():
            vendor_list.extend(items)
    else:
        return "  Invalid vendor data format."

    for vendor in vendor_list[:3]:
        lines.append(VENDOR_LINE_TEMPLATE.format(
            num=num,
            name=vendor.get("name", "Unknown"),
            phone=vendor.get("phone", "N/A"),
            notes=vendor.get("notes", "—"),
        ))
        num += 1

    return "\n".join(lines) if lines else "  No vendors found — manual lookup required."


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a maintenance work order.")
    parser.add_argument("--address", required=True)
    parser.add_argument("--tenant-name", required=True)
    parser.add_argument("--tenant-phone", default="N/A")
    parser.add_argument("--tenant-email", default="N/A")
    parser.add_argument("--issue-type", required=True)
    parser.add_argument("--description", required=True)
    parser.add_argument("--appliance-model", default="")
    parser.add_argument("--vendors", default="[]", help="JSON array or object of vendor records")

    args = parser.parse_args()

    appliance_line = (
        APPLIANCE_LINE_TEMPLATE.format(model=args.appliance_model)
        if args.appliance_model
        else ""
    )

    output = WORK_ORDER_TEMPLATE.format(
        date=date.today().strftime("%d/%m/%Y"),
        address=args.address,
        tenant_name=args.tenant_name,
        tenant_phone=args.tenant_phone,
        tenant_email=args.tenant_email,
        issue_type=args.issue_type,
        description=args.description,
        appliance_line=appliance_line,
        vendor_list=format_vendors(args.vendors),
    )

    sys.stdout.write(output)


if __name__ == "__main__":
    main()
