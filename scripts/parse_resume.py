"""Shared resume markdown parser module.

Parses resume-formatted markdown into structured data that can be consumed
by multiple renderers (PDF via Typst, DOCX via python-docx, etc.).

Usage as module:
    from parse_resume import parse_resume_markdown

    parsed = parse_resume_markdown(markdown_text)
    # parsed["name"] -> str
    # parsed["contact_lines"] -> list[str]
    # parsed["sections"] -> list[dict]
    # parsed["warnings"] -> list[str]

Usage as CLI (for testing/debugging):
    uv run scripts/parse_resume.py <input.md> [--json]
"""

import json
import logging
import sys
from pathlib import Path

logger = logging.getLogger(__name__)


def parse_resume_markdown(text: str) -> dict:
    """Parse resume markdown into a structured dict.

    Heading hierarchy:
        H1 (# ) -> candidate name
        H2 (## ) -> top-level section (e.g., Experience, Education, Skills)
        H3 (### ) -> subsection (e.g., job title, degree)

    Returns a dict with keys:
        name: str
            The candidate's name extracted from the H1 heading.
        contact_lines: list[str]
            Raw contact info lines (pipe-delimited, emails, URLs).
        sections: list[dict]
            Each section dict has:
                heading: str - section title text
                level: int - 2 (H2) or 3 (H3)
                meta_line: str | None - bold company/date line for H3 entries
                content: list[str] - raw content lines (preserving whitespace)
        warnings: list[str]
            Non-fatal warnings about the parsed content (missing headings,
            missing expected sections, unrecognized elements).

    Args:
        text: Resume content in markdown format.

    Returns:
        Structured resume data dict.

    Raises:
        ValueError: If the input is not a string or is empty/whitespace-only.
    """
    if not isinstance(text, str):
        raise ValueError(
            f"Expected markdown string, got {type(text).__name__}. "
            "Provide the resume content as a string."
        )

    if not text.strip():
        raise ValueError(
            "Input markdown is empty or contains only whitespace. "
            "Provide valid resume markdown content."
        )

    lines = text.strip().split("\n")
    warnings: list[str] = []

    name: str = ""
    contact_lines: list[str] = []
    sections: list[dict] = []
    current_section: dict | None = None

    i = 0
    # Parse H1 name
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith("# ") and not line.startswith("## "):
            name = line[2:].strip()
            i += 1
            break
        elif line:
            warnings.append("Missing H1 heading (candidate name)")
            break
        i += 1

    if not name:
        warnings.append("Missing H1 heading (candidate name)")

    # Look for contact lines (pipe-delimited, right after H1 + blank line)
    while i < len(lines) and not lines[i].strip():
        i += 1

    while i < len(lines):
        candidate = lines[i].strip()
        if not candidate or candidate.startswith("#"):
            break
        if "|" in candidate or "@" in candidate or any(
            d in candidate.lower() for d in ["linkedin.com", "github.com", "http"]
        ):
            contact_lines.append(candidate)
            i += 1
        else:
            break

    # Parse remaining sections
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if stripped.startswith("### "):
            heading = stripped[4:].strip()
            current_section = {
                "heading": heading,
                "level": 3,
                "meta_line": None,
                "content": [],
            }
            sections.append(current_section)
            i += 1
            # Check for bold meta line (company/date)
            while i < len(lines) and not lines[i].strip():
                i += 1
            if i < len(lines):
                meta_candidate = lines[i].strip()
                if meta_candidate.startswith("**") or (
                    meta_candidate.startswith("*") and not meta_candidate.startswith("* ")
                ):
                    current_section["meta_line"] = meta_candidate
                    i += 1
                    continue
            continue

        elif stripped.startswith("## "):
            heading = stripped[3:].strip()
            current_section = {
                "heading": heading,
                "level": 2,
                "meta_line": None,
                "content": [],
            }
            sections.append(current_section)
            i += 1
            continue

        elif current_section is not None:
            current_section["content"].append(line)
            i += 1
        else:
            i += 1

    # Validate expected resume structure
    h2_headings = [s["heading"].lower() for s in sections if s["level"] == 2]
    expected_sections = ["summary", "experience", "education", "skills"]
    for expected in expected_sections:
        if not any(expected in h for h in h2_headings):
            warnings.append(f"Missing expected section: {expected}")

    return {
        "name": name,
        "contact_lines": contact_lines,
        "sections": sections,
        "warnings": warnings,
    }


def main() -> int:
    """CLI entry point for testing/debugging the parser."""
    if len(sys.argv) < 2:
        print(
            f"Usage: {sys.argv[0]} <input.md> [--json]",
            file=sys.stderr,
        )
        return 1

    input_path = Path(sys.argv[1])
    output_json = "--json" in sys.argv

    if not input_path.exists():
        print(f"Error: File not found: {input_path}", file=sys.stderr)
        return 1

    try:
        text = input_path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        print(
            f"Error: File is not valid text/markdown: {exc}",
            file=sys.stderr,
        )
        return 1

    try:
        parsed = parse_resume_markdown(text)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    # Print warnings to stderr
    for warning in parsed.get("warnings", []):
        print(f"WARNING: {warning}", file=sys.stderr)

    if output_json:
        print(json.dumps(parsed, indent=2))
    else:
        print(f"Name: {parsed['name']}")
        print(f"Contact lines: {len(parsed['contact_lines'])}")
        print(f"Sections: {len(parsed['sections'])}")
        for section in parsed["sections"]:
            prefix = "  " if section["level"] == 2 else "    "
            meta = f" (meta: {section['meta_line'][:40]}...)" if section.get("meta_line") else ""
            content_count = len([l for l in section["content"] if l.strip()])
            print(
                f"{prefix}H{section['level']}: {section['heading']}"
                f" [{content_count} lines]{meta}"
            )
        if parsed["warnings"]:
            print(f"Warnings: {len(parsed['warnings'])}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
