#!/usr/bin/env python3
"""
Fill jurisdiction-specific rental notice forms using pypdf.
Supports field inspection and field filling from JSON data.

Form path resolution (two modes — use whichever is convenient):

  Mode A — explicit path (original behaviour, always works):
    python fill_ltb_form.py --form assets/CA-ON/N4-blank.pdf --inspect
    python fill_ltb_form.py --form assets/CA-ON/N4-blank.pdf \\
        --output /data/workspace-legal/forms/tenant123_N4.pdf \\
        --fields '{"TO_TenameName[0]": "Jane Doe", ...}'

  Mode B — registry lookup (--jurisdiction + --form-code):
    python fill_ltb_form.py --jurisdiction CA-ON --form-code N4 --inspect
    python fill_ltb_form.py --jurisdiction CA-ON --form-code N4 \\
        --output /data/workspace-legal/forms/tenant123_N4.pdf \\
        --fields '{"TO_TenameName[0]": "Jane Doe", ...}'

  Registry path: assets/[JURISDICTION]/[FORM_CODE]-blank.pdf
  (relative to the 'assets/' directory next to this script's parent)
"""

import argparse
import json
import re
import sys
from pathlib import Path

try:
    from pypdf import PdfReader, PdfWriter
    from pypdf.generic import BooleanObject, NameObject
except ImportError:
    print("ERROR: pypdf not installed. Run: pip install pypdf", file=sys.stderr)
    sys.exit(1)


def inspect_fields(form_path: Path) -> None:
    """Print all fillable field names in the PDF form, including checkboxes."""
    reader = PdfReader(str(form_path))
    if reader.is_encrypted:
        reader.decrypt("")  # LTB blank forms use empty owner password

    all_fields = reader.get_fields() or {}
    text_fields = reader.get_form_text_fields() or {}

    if not all_fields:
        print("No fillable fields found in this PDF.")
        return

    print(f"Fillable fields in {form_path.name}:")
    print("=" * 60)
    for name, field in all_fields.items():
        ft = field.get("/FT", "")
        # Only show leaf fields (text and button), skip container groups
        if ft not in ("/Tx", "/Btn"):
            continue
        short_name = name.split(".")[-1]  # last segment is the field name used by pypdf
        field_type = "text   " if ft == "/Tx" else "checkbox"
        value = text_fields.get(short_name, "")
        current = f' (current: "{value}")' if value else ""
        print(f"  [{field_type}] {short_name!r}{current}")

    print(f"\nTotal text fields: {len(text_fields)}")
    btn_count = sum(1 for f in all_fields.values() if f.get("/FT") == "/Btn")
    print(f"Total checkboxes:  {btn_count}")


def _update_xfa_datasets(pdf_root: object, field_data: dict) -> None:
    """Update XFA datasets XML stream with field values.

    LTB forms are XFA hybrid PDFs. Checkbox fields (CheckList1-7, SelectSign)
    exist only in the XFA layer and cannot be set via the AcroForm API.
    Text fields are also duplicated in XFA — updating both layers ensures
    consistency across all PDF readers.

    Must be called AFTER clone_reader_document_root on writer._root_object,
    so we mutate the writer-owned in-memory stream objects.

    For each field this function first attempts regex substitution on existing
    elements. Fields not found in the stream (e.g. checkboxes absent from a
    blank form's datasets) are collected and inserted before the closing tag
    of the XFA data root element.

    Args:
        pdf_root: The /Root dictionary of the writer (writer._root_object).
        field_data: Dict of {acroform_field_name: value} to write.
    """
    try:
        acroform = pdf_root.get("/AcroForm")
        if not acroform:
            return
        if hasattr(acroform, "get_object"):
            acroform = acroform.get_object()
        xfa = acroform.get("/XFA")
        if not xfa:
            return

        xfa_items = list(xfa)
        for i in range(0, len(xfa_items) - 1, 2):
            if str(xfa_items[i]) != "datasets":
                continue

            stream_ref = xfa_items[i + 1]
            stream_obj = (
                stream_ref.get_object()
                if hasattr(stream_ref, "get_object")
                else stream_ref
            )
            if not hasattr(stream_obj, "get_data"):
                break

            xml_str = stream_obj.get_data().decode("utf-8", errors="replace")

            # Track fields that are absent from the datasets stream.
            missing: dict[str, str] = {}

            for acroform_name, value in field_data.items():
                # Strip [0] suffix: "CheckList1[0]" → "CheckList1"
                xfa_name = acroform_name.split("[")[0]
                escaped = re.escape(xfa_name)

                # Replace existing open/close element: <FieldName>old</FieldName>
                # Use \s* before > to tolerate newlines inside tags (e.g. <FieldName\n>).
                new_xml, n = re.subn(
                    rf"<{escaped}(?:\s[^>]*)?\s*>.*?</{escaped}\s*>",
                    f"<{xfa_name}>{value}</{xfa_name}>",
                    xml_str,
                    flags=re.DOTALL,
                )
                if n:
                    xml_str = new_xml
                    continue

                # Replace self-closing element: <FieldName/> or <FieldName\n/>
                new_xml, n = re.subn(
                    rf"<{escaped}(?:\s[^>]*)?\s*/>",
                    f"<{xfa_name}>{value}</{xfa_name}>",
                    xml_str,
                    flags=re.DOTALL,
                )
                if n:
                    xml_str = new_xml
                    continue

                # Element not present — queue for insertion.
                missing[xfa_name] = value

            # Insert missing fields before the closing tag of the XFA data root.
            # The data root is the first child element under <xfa:data ...>.
            if missing:
                m = re.search(r"<xfa:data[^>]*>\s*<([\w]+)", xml_str)
                if m:
                    root_tag = m.group(1)
                    close_tag = f"</{root_tag}>"
                    pos = xml_str.rfind(close_tag)
                    if pos >= 0:
                        insert = "".join(
                            f"<{k}>{v}</{k}>" for k, v in missing.items()
                        )
                        xml_str = xml_str[:pos] + insert + xml_str[pos:]

            # Remove compression so we can write raw bytes directly.
            new_data = xml_str.encode("utf-8")
            if NameObject("/Filter") in stream_obj:
                del stream_obj[NameObject("/Filter")]
            if NameObject("/DecodeParms") in stream_obj:
                del stream_obj[NameObject("/DecodeParms")]
            stream_obj._data = new_data
            # Clear any cached decoded bytes so get_data() returns the new value.
            if hasattr(stream_obj, "_decodedSelf"):
                stream_obj._decodedSelf = None
            break

    except Exception as e:
        print(f"WARNING: XFA datasets update failed: {e}", file=sys.stderr)


def fill_form(form_path: Path, output_path: Path, field_data: dict) -> None:
    """Fill form fields and write to output path."""
    reader = PdfReader(str(form_path))
    if reader.is_encrypted:
        reader.decrypt("")  # LTB blank forms use empty owner password
    writer = PdfWriter()

    # clone_reader_document_root copies full document structure including
    # AcroForm field widget references (unlike add_page which copies only
    # page content streams).
    writer.clone_reader_document_root(reader)

    # Update XFA datasets AFTER cloning on writer._root_object so we mutate
    # writer-owned in-memory stream objects. Modifying the reader before clone
    # does not work because the blank form's datasets stream contains no
    # checkbox elements — the insert logic requires a live, mutable stream.
    _update_xfa_datasets(writer._root_object, field_data)

    available_fields = reader.get_form_text_fields() or {}

    # Identify AcroForm button fields (checkboxes, radio buttons) by short name.
    # Short name = last dotted segment, e.g. "form1[0].#subform[0].CheckList1[0]" → "CheckList1[0]"
    btn_field_names = {
        name.split(".")[-1]
        for name, field in (reader.get_fields() or {}).items()
        if field.get("/FT") == "/Btn"
    }

    # For button fields, AcroForm appearance state names are NameObjects with a '/' prefix:
    # e.g. string "1" → NameObject("/1") which matches the "/1" appearance state (checked).
    # Text field values are left as plain strings.
    acroform_field_data = {
        k: (NameObject(f"/{v}") if k in btn_field_names else v)
        for k, v in field_data.items()
    }

    for page in writer.pages:
        writer.update_page_form_field_values(
            page, acroform_field_data, auto_regenerate=True
        )

    # Set NeedAppearances so PDF readers regenerate field visuals on open.
    if "/AcroForm" in writer._root_object:
        writer._root_object["/AcroForm"][NameObject("/NeedAppearances")] = BooleanObject(True)

    unmatched = [k for k in field_data if k not in available_fields]

    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(output_path, "wb") as f:
            writer.write(f)
    except Exception as e:
        print(f"ERROR: Failed to write filled PDF: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Form filled: {output_path}")

    if unmatched:
        print(f"\nWARNING: {len(unmatched)} field(s) not found in AcroForm layer:")
        for field in unmatched:
            print(f"  - {field!r}")
        print("Checkbox fields (CheckList*, SelectSign) are XFA-only — this is expected.")


ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"


def resolve_form_path(form: Path | None, jurisdiction: str | None, form_code: str | None) -> Path:
    """Resolve the blank form PDF path from either explicit --form or registry lookup.

    Registry convention: assets/[JURISDICTION]/[FORM_CODE]-blank.pdf
    Example: CA-ON + N4 → assets/CA-ON/N4-blank.pdf
    """
    if form is not None:
        return form
    if jurisdiction and form_code:
        return ASSETS_DIR / jurisdiction.upper() / f"{form_code.upper()}-blank.pdf"
    print(
        "ERROR: Provide either --form <path> OR both --jurisdiction and --form-code.",
        file=sys.stderr,
    )
    sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fill jurisdiction-specific rental notice PDF forms."
    )
    # Form path — two mutually exclusive modes
    path_group = parser.add_mutually_exclusive_group(required=True)
    path_group.add_argument("--form", type=Path, help="Explicit path to blank PDF form")
    path_group.add_argument(
        "--jurisdiction",
        type=str,
        help="Jurisdiction code (e.g. CA-ON, US-CA). Use with --form-code.",
    )
    parser.add_argument(
        "--form-code",
        type=str,
        help="Form code within the jurisdiction (e.g. N1, N4). Required with --jurisdiction.",
    )
    parser.add_argument("--output", type=Path, help="Output path for filled PDF")
    parser.add_argument("--fields", type=str, help="JSON object of field_name: value pairs")
    parser.add_argument(
        "--inspect",
        action="store_true",
        help="List all fillable fields instead of filling",
    )

    args = parser.parse_args()

    if args.jurisdiction and not args.form_code:
        parser.error("--form-code is required when using --jurisdiction")

    form_path = resolve_form_path(args.form, args.jurisdiction, args.form_code)

    ALLOWED_OUTPUT_DIR = Path("/data").resolve()

    if args.output:
        resolved_output = args.output.resolve()
        if not str(resolved_output).startswith(str(ALLOWED_OUTPUT_DIR)):
            print(
                f"ERROR: Output path must be within {ALLOWED_OUTPUT_DIR}",
                file=sys.stderr,
            )
            sys.exit(1)

    if not form_path.exists():
        print(f"ERROR: Form not found: {form_path}", file=sys.stderr)
        if args.jurisdiction:
            print(
                f"       Place the blank PDF at: {form_path}",
                file=sys.stderr,
            )
        sys.exit(1)

    if args.inspect:
        inspect_fields(form_path)
        return

    if not args.output:
        print("ERROR: --output required when filling a form.", file=sys.stderr)
        sys.exit(1)

    if not args.fields:
        print("ERROR: --fields required when filling a form.", file=sys.stderr)
        sys.exit(1)

    try:
        field_data = json.loads(args.fields)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in --fields: {e}", file=sys.stderr)
        sys.exit(1)

    fill_form(form_path, args.output, field_data)


if __name__ == "__main__":
    main()
