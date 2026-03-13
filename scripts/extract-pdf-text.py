"""Extract text content from PDF files using PyMuPDF with layout awareness.

Usage:
    uv run scripts/extract-pdf-text.py <input-pdf-path> <output-text-path>

Exits with code 0 on success, non-zero on failure.
Error details are written to stderr.
"""

import os
import sys

import fitz


def extract_text(input_path: str) -> str:
    """Extract text from all pages of a PDF, separated by '---' page breaks.

    Args:
        input_path: Path to the input PDF file.

    Returns:
        Extracted text with page breaks indicated by '---'.

    Raises:
        FileNotFoundError: If the input file does not exist.
        ValueError: If the file is empty or contains no extractable text.
        RuntimeError: If the PDF cannot be opened or parsed.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"File not found: {input_path}")

    if os.path.getsize(input_path) == 0:
        raise ValueError("The provided file is empty")

    try:
        doc = fitz.open(input_path)
    except Exception:
        raise RuntimeError("Could not extract text from PDF")

    try:
        total_pages = len(doc)
        pages: list[str] = []
        for page in doc:
            text = page.get_text("text")
            if text.strip():
                pages.append(text.strip())

        if not pages:
            raise ValueError("PDF contains no extractable text")

        return f"[PAGES:{total_pages}]\n" + "\n---\n".join(pages)
    except ValueError:
        raise
    except Exception:
        raise RuntimeError("Could not extract text from PDF")
    finally:
        doc.close()


def main() -> int:
    if len(sys.argv) != 3:
        print(
            f"Usage: {sys.argv[0]} <input-pdf-path> <output-text-path>",
            file=sys.stderr,
        )
        return 1

    input_path = sys.argv[1]
    output_path = sys.argv[2]

    try:
        text = extract_text(input_path)
    except FileNotFoundError as e:
        print(str(e), file=sys.stderr)
        return 1
    except ValueError as e:
        print(str(e), file=sys.stderr)
        return 1
    except RuntimeError as e:
        print(str(e), file=sys.stderr)
        return 1

    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(text)
            f.write("\n")
    except OSError as e:
        print(f"Could not write output file: {e}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
