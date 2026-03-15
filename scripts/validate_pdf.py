"""Post-export ATS validation for PDF files.

Extracts text from a generated PDF and verifies content completeness
against the source markdown. Detects silently dropped content, missing
section headings, and garbled text from font embedding issues.

Usage as module:
    from validate_pdf import validate_pdf

    result = validate_pdf("output.pdf", source_markdown)
    # result["status"] -> "pass" or "fail"
    # result["issues"] -> list of issue dicts

Usage as CLI:
    uv run scripts/validate_pdf.py <pdf-path> <source-markdown-path>
"""

import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent


def _extract_pdf_text(pdf_path: str) -> str:
    """Extract all text from a PDF file using pymupdf.

    Args:
        pdf_path: Path to the PDF file.

    Returns:
        Concatenated text from all pages.

    Raises:
        FileNotFoundError: If the PDF file does not exist.
        RuntimeError: If pymupdf is not available or PDF cannot be read.
    """
    path = Path(pdf_path)
    if not path.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    if not path.is_file():
        raise FileNotFoundError(f"Not a file: {pdf_path}")

    try:
        import fitz
    except ImportError:
        raise RuntimeError(
            "pymupdf (fitz) is required for PDF text extraction. "
            "Install it with: uv add pymupdf  (or: pip install pymupdf)"
        )

    try:
        doc = fitz.open(str(path))
    except Exception as exc:
        raise RuntimeError(f"Could not open PDF file: {exc}")

    try:
        pages_text: list[str] = []
        for page in doc:
            text = page.get_text("text")
            if text.strip():
                pages_text.append(text.strip())
        return "\n".join(pages_text)
    except Exception as exc:
        raise RuntimeError(f"Could not extract text from PDF: {exc}")
    finally:
        doc.close()


def _extract_section_headings(markdown: str) -> list[str]:
    """Extract H2 section headings from markdown.

    Looks for lines starting with ``## `` (but not ``### ``).

    Args:
        markdown: Source markdown text.

    Returns:
        List of heading strings (without the ``## `` prefix).
    """
    headings: list[str] = []
    for line in markdown.split("\n"):
        stripped = line.strip()
        if stripped.startswith("## ") and not stripped.startswith("### "):
            heading = stripped[3:].strip()
            if heading:
                headings.append(heading)
    return headings


def _extract_key_phrases(markdown: str) -> list[str]:
    """Extract key content phrases from markdown for completeness checking.

    Extracts:
    - The candidate name (H1 heading)
    - H3 subsection headings (job titles, degrees)
    - First significant word cluster from each bullet point

    Args:
        markdown: Source markdown text.

    Returns:
        List of key phrases expected in the PDF text.
    """
    phrases: list[str] = []

    for line in markdown.split("\n"):
        stripped = line.strip()

        # H1 heading (candidate name)
        if stripped.startswith("# ") and not stripped.startswith("## "):
            name = stripped[2:].strip()
            if name:
                phrases.append(name)

        # H3 headings (job titles, degree names)
        elif stripped.startswith("### "):
            heading = stripped[4:].strip()
            if heading:
                phrases.append(heading)

        # Bullet points - extract the first meaningful phrase
        elif stripped.startswith("- ") or stripped.startswith("* "):
            bullet_text = stripped[2:].strip()
            # Remove markdown formatting
            clean = re.sub(r"\*\*(.+?)\*\*", r"\1", bullet_text)
            clean = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"\1", clean)
            clean = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", clean)
            # Take first 5-8 words as a key phrase
            words = clean.split()
            if len(words) >= 3:
                phrase = " ".join(words[:6])
                phrases.append(phrase)

    return phrases


def _detect_garbled_text(extracted_text: str) -> bool:
    """Detect garbled text that indicates font embedding issues.

    Looks for patterns common in PDF text extraction when fonts are
    not properly embedded:
    - High ratio of replacement characters (U+FFFD)
    - Sequences of non-printable control characters
    - Unusually high ratio of non-ASCII characters for English text
    - Long runs of the same special character

    Args:
        extracted_text: Text extracted from the PDF.

    Returns:
        True if garbled text is detected, False otherwise.
    """
    if not extracted_text.strip():
        return False

    text = extracted_text.strip()
    total_chars = len(text)
    if total_chars == 0:
        return False

    # Count replacement characters
    replacement_count = text.count("\ufffd")
    if replacement_count > 0 and replacement_count / total_chars > 0.01:
        return True

    # Count non-printable control characters (excluding whitespace)
    control_chars = sum(
        1 for c in text
        if ord(c) < 32 and c not in ("\n", "\r", "\t", " ")
    )
    if control_chars > 0 and control_chars / total_chars > 0.02:
        return True

    # Look for long runs of the same non-alphanumeric character (font mapping issues)
    if re.search(r"[^\w\s]{5,}", text):
        return True

    # High ratio of characters outside basic Latin + common punctuation
    # (indicates wrong character mapping)
    non_basic = sum(
        1 for c in text
        if ord(c) > 127 and c not in ("\u2022", "\u2013", "\u2014", "\u2018",
                                       "\u2019", "\u201c", "\u201d", "\u00e9",
                                       "\u00e8", "\u00f1", "\u00fc")
    )
    if total_chars > 100 and non_basic / total_chars > 0.15:
        return True

    return False


def validate_pdf(
    pdf_path: str,
    source_markdown: str,
) -> dict:
    """Validate a PDF against its source markdown for ATS compatibility.

    Extracts text from the PDF and checks:
    1. All H2 section headings from source are present
    2. Key content phrases (name, job titles, bullet snippets) are present
    3. No garbled text from font embedding issues

    Args:
        pdf_path: Path to the generated PDF file.
        source_markdown: The original markdown source text.

    Returns:
        A dict with:
            status: "pass" or "fail"
            extracted_text: The raw text extracted from the PDF
            issues: list of dicts, each with "type" and "detail" keys
            checks: dict of check names to pass/fail booleans
    """
    issues: list[dict[str, str]] = []
    checks: dict[str, bool] = {}

    # Step 1: Extract text from PDF
    extracted_text = _extract_pdf_text(pdf_path)

    if not extracted_text.strip():
        issues.append({
            "type": "extraction_failed",
            "detail": "No text could be extracted from the PDF. "
                      "The file may be image-based or corrupted.",
        })
        return {
            "status": "fail",
            "extracted_text": "",
            "issues": issues,
            "checks": {"text_extraction": False},
        }

    checks["text_extraction"] = True

    # Step 2: Check for garbled text (font embedding issues)
    garbled = _detect_garbled_text(extracted_text)
    checks["font_embedding"] = not garbled
    if garbled:
        from export_edge_cases import format_garbled_text_warning
        detailed_warning = format_garbled_text_warning(extracted_text)
        issues.append({
            "type": "garbled_text",
            "detail": detailed_warning,
        })

    # Step 3: Check section headings
    expected_headings = _extract_section_headings(source_markdown)
    # PDF renderers may uppercase headings, so normalize
    normalized_pdf = extracted_text.upper()
    missing_headings: list[str] = []
    for heading in expected_headings:
        if heading.upper() not in normalized_pdf:
            missing_headings.append(heading)

    checks["section_headings"] = len(missing_headings) == 0
    if missing_headings:
        issues.append({
            "type": "missing_headings",
            "detail": f"Missing section headings in PDF: {', '.join(missing_headings)}",
        })

    # Step 4: Check key phrases (content completeness)
    key_phrases = _extract_key_phrases(source_markdown)
    missing_phrases: list[str] = []
    for phrase in key_phrases:
        # Check case-insensitive and allow some flexibility for line breaks
        normalized_phrase = " ".join(phrase.split())
        # Try exact match first, then word-by-word
        if normalized_phrase.lower() not in extracted_text.lower():
            # Try checking if all words appear nearby in the text
            words = normalized_phrase.split()
            all_found = all(
                w.lower() in extracted_text.lower() for w in words
            )
            if not all_found:
                missing_phrases.append(phrase)

    checks["content_completeness"] = len(missing_phrases) == 0
    if missing_phrases:
        issues.append({
            "type": "missing_content",
            "detail": (
                f"Content appears to have been dropped during conversion. "
                f"Missing phrases: {'; '.join(missing_phrases[:5])}"
                + (f" (and {len(missing_phrases) - 5} more)"
                   if len(missing_phrases) > 5 else "")
            ),
        })

    # Determine overall status
    # Fail if headings are missing or content is substantially missing
    # Garbled text alone is a fail since it means ATS can't parse
    status = "pass"
    if not checks.get("text_extraction", False):
        status = "fail"
    elif not checks.get("font_embedding", True):
        status = "fail"
    elif not checks.get("section_headings", True):
        status = "fail"
    elif not checks.get("content_completeness", True):
        status = "fail"

    return {
        "status": status,
        "extracted_text": extracted_text,
        "issues": issues,
        "checks": checks,
    }


def main() -> int:
    """CLI entry point for PDF validation."""
    if len(sys.argv) < 3:
        print(
            f"Usage: {sys.argv[0]} <pdf-path> <source-markdown-path>",
            file=sys.stderr,
        )
        return 1

    pdf_path = sys.argv[1]
    md_path = sys.argv[2]

    if not Path(md_path).exists():
        print(f"Error: Markdown file not found: {md_path}", file=sys.stderr)
        return 1

    try:
        source_md = Path(md_path).read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        print(f"Error: Could not read markdown file: {exc}", file=sys.stderr)
        return 1

    try:
        result = validate_pdf(pdf_path, source_md)
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except RuntimeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    # Print results
    status = result["status"].upper()
    print(f"Validation: {status}")

    if result["issues"]:
        print("\nIssues found:")
        for issue in result["issues"]:
            print(f"  [{issue['type']}] {issue['detail']}")

    print("\nChecks:")
    for check_name, passed in result["checks"].items():
        mark = "PASS" if passed else "FAIL"
        print(f"  {check_name}: {mark}")

    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
