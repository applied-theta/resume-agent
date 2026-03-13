"""Validate JSON and markdown output files against their JSON Schemas.

Usage:
    uv run scripts/validate-output.py <file-path>

Determines which schema to use based on filename. Validates JSON files against
the corresponding schema in schemas/. For markdown report files, checks for
required sections. Files with no matching schema are passed through (exit 0).

Exit codes:
    0 - valid (or no matching schema)
    1 - validation error, file not found, or other error
"""

import json
import sys
from pathlib import Path

import jsonschema

# Map output filenames to their schema files
SCHEMA_MAP: dict[str, str] = {
    "parsed-resume.json": "parsed-resume.schema.json",
    "ats-analysis.json": "ats-analysis.schema.json",
    "content-analysis.json": "content-analysis.schema.json",
    "keyword-analysis.json": "keyword-analysis.schema.json",
    "strategy-analysis.json": "strategy-analysis.schema.json",
    "scores-summary.json": "scores-summary.schema.json",
    "skills-research.json": "skills-research.schema.json",
    "change-manifest.json": "change-manifest.schema.json",
    "interview-findings.json": "interview-findings.schema.json",
}

# Required sections for markdown report files
REPORT_REQUIRED_SECTIONS: dict[str, list[str]] = {
    "analysis-report.md": [
        "Executive Summary",
        "Scorecard",
        "Action Plan",
    ],
    "optimization-report.md": [
        "Overview",
        "Experience Section",
        "Approval Summary",
    ],
}

SCHEMAS_DIR = Path(__file__).resolve().parent.parent / "schemas"


def validate_json_file(file_path: Path, schema_name: str) -> int:
    """Validate a JSON file against a schema. Returns exit code."""
    schema_path = SCHEMAS_DIR / schema_name
    if not schema_path.exists():
        print(f"ERROR: Schema file not found: {schema_path}", file=sys.stderr)
        return 1

    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"ERROR: Invalid schema JSON in {schema_path}: {exc}", file=sys.stderr)
        return 1

    try:
        data = json.loads(file_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(
            f"ERROR: Invalid JSON syntax in {file_path.name}: {exc}",
            file=sys.stderr,
        )
        return 1

    try:
        jsonschema.validate(instance=data, schema=schema)
    except jsonschema.ValidationError as exc:
        print(
            f"ERROR: Validation failed for {file_path.name}: {exc.message}",
            file=sys.stderr,
        )
        return 1

    return 0


def validate_markdown_report(file_path: Path, required_sections: list[str]) -> int:
    """Validate a markdown report has required sections. Returns exit code."""
    content = file_path.read_text(encoding="utf-8")
    missing = []
    for section in required_sections:
        if section.lower() not in content.lower():
            missing.append(section)

    if missing:
        print(
            f"ERROR: {file_path.name} missing required sections: "
            + ", ".join(missing),
            file=sys.stderr,
        )
        return 1

    return 0


def main() -> int:
    if len(sys.argv) != 2:
        print(
            "Usage: uv run scripts/validate-output.py <file-path>",
            file=sys.stderr,
        )
        return 1

    file_path = Path(sys.argv[1])
    basename = file_path.name

    # Check if this file has a matching JSON schema
    schema_name = SCHEMA_MAP.get(basename)
    if schema_name is not None:
        if not file_path.exists():
            print(f"ERROR: File not found: {file_path}", file=sys.stderr)
            return 1
        return validate_json_file(file_path, schema_name)

    # Check if this is a markdown report with required sections
    required_sections = REPORT_REQUIRED_SECTIONS.get(basename)
    if required_sections is not None:
        if not file_path.exists():
            print(f"ERROR: File not found: {file_path}", file=sys.stderr)
            return 1
        return validate_markdown_report(file_path, required_sections)

    # No matching schema — pass through
    return 0


if __name__ == "__main__":
    sys.exit(main())
