#!/usr/bin/env python3
"""Validate the structure of a technical SBAR Markdown/plain-text message.

Reads the selected template from ../templates/ and checks for all four SBAR
sections, non-placeholder content, and (by default) every required field
declared as a bullet in the chosen template. This is a structural check,
NOT verification of facts, evidence quality, risk, or technical correctness.
Requires Python 3.9+ and no third-party packages.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = ROOT / "templates"
SECTIONS = ("Situation", "Background", "Assessment", "Recommendation")
ALIASES = {"s": "Situation", "b": "Background", "a": "Assessment", "r": "Recommendation"}
HEADING = re.compile(
    r"^(Situation|Background|Assessment|Recommendation|S|B|A|R)"
    r"(?:\s*[:\u2013\u2014-]\s*(.*))?$", re.IGNORECASE
)
BULLET_FIELD = re.compile(r"^\s*[-*+]\s+(.+?)\s*:\s*(.*)$")
INLINE_FIELD = re.compile(r"^\s*(.+?)\s*:\s*(.*)$")
FENCE = re.compile(r"^\s*(`{3,}|~{3,})")
PLACEHOLDERS = {"", "...", "…", "-", "todo", "tbd", "tbc", "fill in", "placeholder"}
OPTIONAL_CUE = re.compile(r"\b(optional|only if|if known|when known|if applicable)\b", re.I)


def unmark(text: str) -> str:
    """Remove lightweight Markdown delimiters used in template headings/labels."""
    return text.replace("**", "").replace("__", "").replace("`", "").strip()


def filled(value: str) -> bool:
    """Detect unfilled blanks and placeholders; 'unknown' is an explicit answer."""
    value = unmark(value).strip()
    if value.casefold() in PLACEHOLDERS:
        return False
    if (value.startswith("[") and value.endswith("]")) or (
        value.startswith("<") and value.endswith(">")
    ):
        return False
    return bool(re.search(r"\w", value, flags=re.UNICODE))


def sections_from(text: str) -> tuple[dict[str, list[str]], list[str], list[str]]:
    """Parse explicit SBAR headings; ignore fenced code and quoted examples."""
    sections: dict[str, list[str]] = {}
    seen: list[str] = []
    duplicates: list[str] = []
    current = None
    fence_char = None
    fence_length = 0

    for line in text.splitlines():
        fence = FENCE.match(line)
        if fence:
            sequence = fence.group(1)
            if fence_char is None:
                fence_char, fence_length = sequence[0], len(sequence)
            elif sequence[0] == fence_char and len(sequence) >= fence_length:
                fence_char = None
            continue
        if fence_char is not None or line.lstrip().startswith(">"):
            continue

        clean = unmark(re.sub(r"^\s*#{1,6}\s+", "", line.strip()))
        heading = HEADING.fullmatch(clean)
        if heading:
            key = ALIASES.get(heading.group(1).lower(), heading.group(1).capitalize())
            if key in sections:
                duplicates.append(key)
            else:
                sections[key] = []
                seen.append(key)
            current = key
            if heading.group(2):
                sections[key].append(heading.group(2))
        elif current is not None:
            sections[current].append(line)
    return sections, seen, duplicates


def field_label_and_value(line: str, *, allow_inline: bool = False) -> tuple[str, str] | None:
    clean = unmark(line.strip())
    match = BULLET_FIELD.match(clean)
    if match is None and allow_inline:
        match = INLINE_FIELD.match(clean)
    if not match:
        return None
    label, value = match.groups()
    return " ".join(label.casefold().split()), value.strip()


def template_fields(section_lines: list[str]) -> list[tuple[str, bool]]:
    fields = []
    for line in section_lines:
        # Ordinary template fields are bullets. Also support explicit inline
        # fill-in fields, such as the incident template's "Status honesty".
        is_inline_placeholder = bool(re.search(r":\s*\[[^]]*\]\s*$", unmark(line)))
        parsed = field_label_and_value(line, allow_inline=is_inline_placeholder)
        if parsed:
            label, instruction = parsed
            optional = bool(OPTIONAL_CUE.search(label) or OPTIONAL_CUE.search(instruction))
            fields.append((label, optional))
    return fields


def document_field_values(section_lines: list[str], expected: set[str]) -> dict[str, str]:
    """Capture values from labeled bullets, including multiline continuation text."""
    values: dict[str, str] = {}
    active = None
    for line in section_lines:
        pair = field_label_and_value(line, allow_inline=True)
        if pair and pair[0] in expected:
            active = pair[0]
            values[active] = (values.get(active, "") + "\n" + pair[1]).strip()
        elif re.match(r"^\s*[-*+]\s+", line):
            active = None
        elif active is not None and line.strip():
            values[active] += "\n" + line.strip()
    return values


def has_section_content(lines: list[str], template_lines: list[str]) -> bool:
    # Template boilerplate (including review guidance) is not a filled answer.
    boilerplate = {line.strip() for line in template_lines}
    for line in lines:
        if line.strip() in boilerplate:
            continue
        candidate = unmark(line.strip())
        if not candidate:
            continue
        parsed = field_label_and_value(line, allow_inline=True)
        if parsed:
            if filled(parsed[1]):
                return True
        elif not candidate.lower().startswith(("review integrity:", "status honesty:")):
            if filled(candidate):
                return True
    return False


def validate(message: str, template: str, sections_only: bool) -> dict[str, object]:
    wanted, template_order, template_duplicates = sections_from(template)
    if template_duplicates or template_order != list(SECTIONS):
        raise ValueError("Template must have exactly four distinct S/B/A/R headings in order")
    actual, order, duplicates = sections_from(message)
    errors: list[str] = []
    warnings: list[str] = []
    for section in SECTIONS:
        if section not in actual:
            errors.append(f"Missing section: {section}")
        elif not has_section_content(actual[section], wanted[section]):
            errors.append(f"Empty or placeholder-only section: {section}")
    if duplicates:
        errors.append("Duplicate sections: " + ", ".join(sorted(set(duplicates))))
    if order != [section for section in SECTIONS if section in actual]:
        errors.append("Sections are out of SBAR order")

    checked_fields = 0
    optional_fields = 0
    if not sections_only:
        for section in SECTIONS:
            expected = template_fields(wanted[section])
            checked_fields += sum(not optional for _, optional in expected)
            optional_fields += sum(optional for _, optional in expected)
            if section not in actual:
                continue
            values = document_field_values(actual[section], {name for name, _ in expected})
            for name, optional in expected:
                value = values.get(name)
                if value is None:
                    if not optional:
                        errors.append(f"Missing field in {section}: {name}")
                elif not filled(value):
                    if not optional:
                        errors.append(f"Unfilled field in {section}: {name}")
                    else:
                        warnings.append(f"Optional field left blank in {section}: {name}")

    return {
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
        "sections_found": order,
        "required_fields_checked": checked_fields,
        "optional_fields": optional_fields,
        "mode": "sections-only" if sections_only else "template-fields",
    }


def choose_template(argument: str) -> Path:
    """Allow template name/stem or an explicit template path."""
    supplied = Path(argument)
    if supplied.is_file():
        return supplied
    filename = supplied.name
    if argument == filename:
        candidate = TEMPLATE_DIR / (filename if filename.endswith(".md") else filename + ".md")
        if candidate.is_file():
            return candidate
    raise ValueError(
        f"Template not found: {argument}. Choose one of: "
        + ", ".join(p.stem for p in sorted(TEMPLATE_DIR.glob("*.md")))
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", type=Path, help="SBAR .md or .txt communication file to validate")
    parser.add_argument(
        "--template", default="quick-update",
        help="Built-in template name/path, or a path to a compatible template file",
    )
    parser.add_argument(
        "--sections-only", action="store_true",
        help="Check the four nonempty SBAR sections without detailed template field labels",
    )
    parser.add_argument("--json", action="store_true", help="Print machine-readable results")
    args = parser.parse_args()
    try:
        template_path = choose_template(args.template)
        message = args.file.read_text(encoding="utf-8-sig")
        template = template_path.read_text(encoding="utf-8-sig")
        result = validate(message, template, args.sections_only)
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps({"file": str(args.file), "template": str(template_path), **result}, indent=2))
    else:
        print(f"{'PASS' if result['valid'] else 'FAIL'}: {args.file} against {template_path.name}")
        print(f"Sections: {', '.join(result['sections_found']) or 'none'}")
        print(f"Required fields checked: {result['required_fields_checked']}")
        for issue in result["errors"]:
            print(f"  ERROR: {issue}")
        for issue in result["warnings"]:
            print(f"  WARNING: {issue}")
        if result["valid"]:
            print("Structural checks passed; factual and technical correctness were not assessed.")
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
