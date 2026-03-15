"""Centralized edge case handling for the export pipeline.

Provides utility functions for detecting and reporting edge cases across
both PDF and DOCX export paths. All functions produce user-friendly
messages (no raw tracebacks) and classify issues as warnings (non-fatal)
or errors (fatal with actionable guidance).

Usage:
    from export_edge_cases import (
        check_source_file,
        check_output_size,
        check_page_count_pdf,
        check_dependency_available,
        format_garbled_text_warning,
        format_missing_sections_report,
    )
"""

import sys
from pathlib import Path

# Cowork VM file size limit: 30MB. Warn at 25MB.
_COWORK_LIMIT_BYTES = 30 * 1024 * 1024
_WARN_THRESHOLD_BYTES = 25 * 1024 * 1024

# Typical resume page count range
_EXPECTED_MAX_PAGES = 2

# Install instructions per package and environment
_INSTALL_INSTRUCTIONS: dict[str, dict[str, str]] = {
    "python-docx": {
        "uv": "uv add python-docx",
        "pip": "pip install python-docx",
        "pip3": "pip3 install python-docx",
    },
    "fpdf2": {
        "uv": "uv add fpdf2",
        "pip": "pip install fpdf2",
        "pip3": "pip3 install fpdf2",
    },
    "pymupdf": {
        "uv": "uv add pymupdf",
        "pip": "pip install pymupdf",
        "pip3": "pip3 install pymupdf",
    },
    "typst": {
        "uv": "uv add typst",
        "pip": "pip install typst",
        "pip3": "pip3 install typst",
    },
}


def check_source_file(path: str | Path) -> str | None:
    """Validate that a source markdown file exists and is readable.

    Args:
        path: Path to the source markdown file.

    Returns:
        None if the file is valid, or an actionable error message string.
    """
    p = Path(path)
    if not p.exists():
        return (
            f"Source file not found: {p}\n"
            f"Please verify the file path is correct. "
            f"If you haven't optimized a resume yet, run /optimize-resume first."
        )
    if not p.is_file():
        return (
            f"Path is not a file: {p}\n"
            f"Please provide a path to a markdown (.md) file."
        )
    if p.stat().st_size == 0:
        return (
            f"Source file is empty: {p}\n"
            f"The file contains no content to export."
        )
    return None


def check_output_size(path: str | Path) -> list[str]:
    """Check if an output file approaches or exceeds the Cowork 30MB limit.

    Args:
        path: Path to the generated output file.

    Returns:
        A list of warning strings (empty if size is within limits).
    """
    warnings: list[str] = []
    p = Path(path)
    if not p.exists():
        return warnings

    size = p.stat().st_size

    if size > _COWORK_LIMIT_BYTES:
        size_mb = size / (1024 * 1024)
        warnings.append(
            f"Output file is {size_mb:.1f} MB, which exceeds the "
            f"Cowork 30 MB file size limit. The file may not be "
            f"accessible in Cowork environments. Consider reducing "
            f"content or using a more compact preset."
        )
    elif size > _WARN_THRESHOLD_BYTES:
        size_mb = size / (1024 * 1024)
        warnings.append(
            f"Output file is {size_mb:.1f} MB, approaching the "
            f"Cowork 30 MB file size limit. If you plan to use this "
            f"file in Cowork, consider reducing content or using "
            f"a more compact preset to stay within the limit."
        )

    return warnings


def check_page_count_pdf(pdf_path: str | Path, expected_max: int = _EXPECTED_MAX_PAGES) -> list[str]:
    """Check if a PDF exceeds the expected page count.

    Produces an informational warning if the resume overflows beyond
    the typical expected page count. This is non-fatal.

    Args:
        pdf_path: Path to the generated PDF file.
        expected_max: Maximum expected page count (default: 2).

    Returns:
        A list of warning strings (empty if page count is within expectations).
    """
    warnings: list[str] = []
    p = Path(pdf_path)
    if not p.exists():
        return warnings

    try:
        import fitz
    except ImportError:
        # Can't check page count without pymupdf; skip silently
        return warnings

    try:
        doc = fitz.open(str(p))
        page_count = len(doc)
        doc.close()
    except Exception:
        # PDF can't be opened; other validators will catch this
        return warnings

    if page_count > expected_max:
        warnings.append(
            f"Resume PDF is {page_count} page(s), which exceeds the "
            f"typical {expected_max}-page limit for resumes. "
            f"Consider using the 'compact' preset, reducing content, "
            f"or using narrower margins to fit within {expected_max} pages."
        )

    return warnings


def check_dependency_available(
    package_name: str,
    import_name: str | None = None,
) -> str | None:
    """Check if a Python package is importable and return install instructions if not.

    Args:
        package_name: The pip/uv package name (e.g., "python-docx").
        import_name: The Python import name if different from package_name
                     (e.g., "docx" for python-docx). If None, uses package_name.

    Returns:
        None if the package is importable, or an error message with
        environment-specific install instructions.
    """
    name = import_name or package_name
    try:
        __import__(name)
        return None
    except ImportError:
        pass

    # Build install instructions
    instructions = _INSTALL_INSTRUCTIONS.get(package_name, {})
    if not instructions:
        instructions = {
            "uv": f"uv add {package_name}",
            "pip": f"pip install {package_name}",
        }

    # Detect available package manager
    from pathlib import Path as _Path
    script_dir = _Path(__file__).resolve().parent
    project_root = script_dir.parent

    try:
        from env_config import load_env_config
        config = load_env_config()
        pkg_mgr = config.get("PKG_MANAGER", "none")
    except Exception:
        pkg_mgr = "none"

    lines = [
        f"{package_name} is not installed and is required for this operation.",
        "",
        "Install it with one of the following commands:",
    ]

    if pkg_mgr != "none" and pkg_mgr in instructions:
        lines.append(f"  {instructions[pkg_mgr]}")
    else:
        for mgr, cmd in instructions.items():
            lines.append(f"  {cmd}  ({mgr})")

    lines.extend([
        "",
        "After installing, re-run the export command.",
    ])

    return "\n".join(lines)


def format_garbled_text_warning(extracted_text: str) -> str:
    """Produce a specific warning about font embedding issues in PDF text.

    Called when garbled text is detected during PDF validation. Returns
    a user-friendly warning with actionable guidance.

    Args:
        extracted_text: The raw text extracted from the PDF.

    Returns:
        A formatted warning message string.
    """
    # Analyze what kind of garbling is present
    details: list[str] = []
    total = len(extracted_text.strip())

    if total == 0:
        return (
            "No text could be extracted from the PDF. The file appears to be "
            "image-based or the fonts are not embedded correctly. ATS systems "
            "will not be able to parse this document.\n\n"
            "Suggestions:\n"
            "  - Re-export using a different preset\n"
            "  - Ensure the font files in fonts/ are not corrupted\n"
            "  - Try using the Python fallback renderer (fpdf2)"
        )

    replacement_count = extracted_text.count("\ufffd")
    if replacement_count > 0:
        pct = replacement_count / total * 100
        details.append(
            f"  - {replacement_count} replacement character(s) detected "
            f"({pct:.1f}% of text), indicating missing font glyphs"
        )

    import re
    non_basic = sum(
        1 for c in extracted_text
        if ord(c) > 127 and c not in (
            "\u2022", "\u2013", "\u2014", "\u2018",
            "\u2019", "\u201c", "\u201d", "\u00e9",
            "\u00e8", "\u00f1", "\u00fc", "\u25c6",
        )
    )
    if total > 100 and non_basic / total > 0.05:
        details.append(
            f"  - High proportion of unexpected special characters "
            f"({non_basic} out of {total} chars), suggesting incorrect "
            f"font character mapping"
        )

    if re.search(r"[^\w\s]{5,}", extracted_text):
        details.append(
            "  - Long runs of special characters detected, "
            "indicating font glyph substitution failures"
        )

    detail_str = "\n".join(details) if details else "  - Text appears garbled or incorrectly encoded"

    return (
        "Font embedding issue detected in the generated PDF. "
        "Extracted text appears garbled, which means ATS systems "
        "may not be able to parse your resume correctly.\n\n"
        "Details:\n"
        f"{detail_str}\n\n"
        "Suggestions:\n"
        "  - Re-export using a different font (e.g., Inter or EB Garamond)\n"
        "  - Check that font files in fonts/ are valid TTF files (not corrupted)\n"
        "  - Try using the Python fallback renderer which embeds fonts directly\n"
        "  - If using Typst, ensure font paths are configured correctly"
    )


def format_missing_sections_report(
    missing_sections: list[str],
    total_sections: int,
) -> str:
    """Produce a report identifying which sections were lost during DOCX export.

    Args:
        missing_sections: List of section heading names not found in the DOCX.
        total_sections: Total number of sections in the source markdown.

    Returns:
        A formatted report string.
    """
    if not missing_sections:
        return f"All {total_sections} section(s) verified in the DOCX output."

    found = total_sections - len(missing_sections)
    lines = [
        f"DOCX export is missing {len(missing_sections)} of "
        f"{total_sections} section(s):",
        "",
    ]
    for section in missing_sections:
        lines.append(f"  - {section}")

    lines.extend([
        "",
        f"{found} section(s) were exported correctly.",
        "",
        "This may indicate:",
        "  - The section heading format was not recognized during conversion",
        "  - Content was lost due to unsupported markdown elements",
        "  - The custom template may not support the required heading styles",
        "",
        "Suggestions:",
        "  - Re-export using a bundled preset instead of a custom template",
        "  - Check that section headings use standard ## format",
        "  - Review the exported DOCX to confirm which content is missing",
    ])

    return "\n".join(lines)


def validate_custom_template(template_path: str | Path) -> tuple[bool, str]:
    """Validate a custom Word template file with clear error messages.

    Checks if the template file exists, is a valid .docx, and contains
    the required styles. Returns whether the template is valid and a
    message describing any issues.

    Args:
        template_path: Path to the custom .docx template file.

    Returns:
        A tuple of (is_valid, message). If invalid, the message explains
        what's wrong and that fallback to a preset will be used.
    """
    p = Path(template_path)

    if not p.exists():
        return False, (
            f"Custom template not found: {template_path}\n"
            f"The file does not exist at the specified path. "
            f"A bundled preset will be used instead.\n"
            f"Available presets: professional, simple, creative, academic"
        )

    if not p.suffix.lower() == ".docx":
        return False, (
            f"Custom template is not a .docx file: {template_path}\n"
            f"Expected a Word document (.docx) file. "
            f"A bundled preset will be used instead."
        )

    try:
        from docx import Document
        doc = Document(str(p))
    except ImportError:
        return False, (
            "Cannot validate custom template: python-docx is not installed.\n"
            "Install it with: uv add python-docx (or: pip install python-docx)"
        )
    except Exception as exc:
        return False, (
            f"Custom template is corrupted or not a valid Word document: "
            f"{template_path}\n"
            f"The file could not be opened as a .docx file. "
            f"A bundled preset will be used instead.\n"
            f"(Error: {exc})"
        )

    # Check required styles
    required_styles = ["Heading 1", "Heading 2", "Normal"]
    available = {style.name for style in doc.styles}
    missing = [s for s in required_styles if s not in available]

    if missing:
        return False, (
            f"Custom template is missing required styles: "
            f"{', '.join(missing)}\n"
            f"The template must define at minimum: "
            f"{', '.join(required_styles)}.\n"
            f"A bundled preset will be used as a fallback."
        )

    return True, f"Custom template validated successfully: {template_path}"


def emit_warnings(warnings: list[str], prefix: str = "WARNING") -> None:
    """Print a list of warning messages to stderr with consistent formatting.

    Args:
        warnings: List of warning message strings.
        prefix: Prefix for each warning line (default: "WARNING").
    """
    for w in warnings:
        # For multi-line warnings, prefix only the first line
        lines = w.split("\n")
        print(f"{prefix}: {lines[0]}", file=sys.stderr)
        for line in lines[1:]:
            print(f"  {line}", file=sys.stderr)
