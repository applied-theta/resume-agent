"""Convert resume markdown to PDF using Typst.

Usage:
    uv run scripts/md-to-pdf.py <input-md> [output-pdf] [options]

Options:
    --preset PRESET          Style preset: classic, modern, compact (default: modern)
    --font FONT              Font family override (e.g., "Inter", "EB Garamond", "Lato")
    --color COLOR            Accent color as hex (e.g., "#2B547E") or named preset
    --margin MARGIN          Margin size: narrow, standard, wide (default: from preset)
    --page-size SIZE         Page size: letter, a4 (default: letter)
    --line-spacing SPACING   Line spacing: tight, standard, relaxed (default: from preset)
    --section-spacing SPACE  Section spacing: compact, standard, generous (default: from preset)
    --pdf-a                  Enable PDF/A-2b compliance output

Exits with code 0 on success, 1 on error. Errors are written to stderr.
"""

import json
import re
import sys
from pathlib import Path

import typst

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
TEMPLATES_DIR = PROJECT_ROOT / "templates" / "pdf"
FONTS_DIR = PROJECT_ROOT / "fonts"

NAMED_COLORS: dict[str, str] = {
    "navy": "#2B547E",
    "teal": "#008080",
    "charcoal": "#36454F",
    "black": "#000000",
    "burgundy": "#800020",
}

MARGIN_VALUES: dict[str, str] = {
    "narrow": "0.5in",
    "standard": "0.75in",
    "wide": "1in",
}

LINE_SPACING_VALUES: dict[str, str] = {
    "tight": "0.55em",
    "standard": "0.65em",
    "relaxed": "0.78em",
}

SECTION_SPACING_VALUES: dict[str, str] = {
    "compact": "0.6em",
    "standard": "0.9em",
    "generous": "1.2em",
}

PRESET_DEFAULTS: dict[str, dict[str, str]] = {
    "classic": {
        "font": "EB Garamond",
        "color": "#2B547E",
        "margin": "standard",
        "line_spacing": "standard",
        "section_spacing": "standard",
        "font_size": "11pt",
    },
    "modern": {
        "font": "Inter",
        "color": "#2B547E",
        "margin": "standard",
        "line_spacing": "standard",
        "section_spacing": "standard",
        "font_size": "10pt",
    },
    "compact": {
        "font": "Source Sans 3",
        "color": "#36454F",
        "margin": "narrow",
        "line_spacing": "tight",
        "section_spacing": "compact",
        "font_size": "9.5pt",
    },
    "harvard": {
        "font": "EB Garamond",
        "color": "#000000",
        "margin": "wide",
        "line_spacing": "tight",
        "section_spacing": "compact",
        "font_size": "11pt",
    },
}

VALID_PRESETS = list(PRESET_DEFAULTS.keys())


# ---------------------------------------------------------------------------
# Markdown parser: resume markdown -> structured data
# ---------------------------------------------------------------------------


def parse_resume_markdown(text: str) -> dict:
    """Parse resume markdown into a structured dict.

    Returns a dict with keys:
        name: str
        contact_lines: list[str]
        sections: list[dict] with keys:
            heading: str
            level: int (2 or 3)
            meta_line: str | None  (bold company/date line for H3)
            content: list[str]  (lines of content)
    """
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


# ---------------------------------------------------------------------------
# Typst content generator
# ---------------------------------------------------------------------------


def escape_typst(text: str) -> str:
    """Escape characters that have special meaning in Typst markup."""
    # Escape: # @ $ \ ~ ` ^ < >
    # But preserve our deliberate Typst markup
    result = text
    for char in ["\\", "#", "@", "$"]:
        result = result.replace(char, "\\" + char)
    return result


def md_bold_to_typst(text: str) -> str:
    """Convert markdown **bold** to Typst *bold* (strong)."""
    return re.sub(r"\*\*(.+?)\*\*", r"*\1*", text)


def md_italic_to_typst(text: str) -> str:
    """Convert markdown *italic* (single asterisk) to Typst _italic_ (emphasis)."""
    return re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"_\1_", text)


def md_link_to_typst(text: str) -> str:
    """Convert markdown [text](url) links to Typst #link() calls."""
    return re.sub(
        r"\[([^\]]+)\]\(([^)]+)\)",
        r'#link("\2")[\1]',
        text,
    )


def convert_inline(text: str) -> str:
    """Convert markdown inline formatting to Typst."""
    result = escape_typst(text)
    result = md_bold_to_typst(result)
    result = md_italic_to_typst(result)
    result = md_link_to_typst(result)
    return result


def format_contact_line(contact_line: str) -> str:
    """Convert pipe-delimited contact line to Typst formatted contact block."""
    parts = [p.strip() for p in contact_line.split("|") if p.strip()]
    typst_parts = []
    for part in parts:
        # Check if it's an email
        if "@" in part and "." in part:
            escaped = escape_typst(part)
            typst_parts.append(f'#link("mailto:{part}")[{escaped}]')
        # Check if it looks like a URL
        elif any(domain in part.lower() for domain in ["linkedin.com", "github.com", "http"]):
            url = part if part.startswith("http") else f"https://{part}"
            escaped = escape_typst(part)
            typst_parts.append(f'#link("{url}")[{escaped}]')
        else:
            typst_parts.append(escape_typst(part))

    return " #h(1fr) ".join(typst_parts) + "\n"


def format_meta_line(meta_line: str) -> str:
    """Convert a bold company/date meta line to Typst.

    Handles patterns like:
        **Company Name**, City, State | Month YYYY - Present
        **Company Name**, City, State — Month YYYY - Month YYYY
    """
    text = meta_line
    # Remove leading ** and handle the bold part
    text = re.sub(r"\*\*(.+?)\*\*", r"*\1*", text)
    # Replace em-dash or pipe separators with Typst h(1fr) for right-alignment
    if " | " in text:
        parts = text.split(" | ", 1)
        return f"{parts[0].strip()} #h(1fr) {parts[1].strip()}\n"
    elif " — " in text:
        parts = text.split(" — ", 1)
        return f"{parts[0].strip()} #h(1fr) {parts[1].strip()}\n"
    elif " -- " in text:
        parts = text.split(" -- ", 1)
        return f"{parts[0].strip()} #h(1fr) {parts[1].strip()}\n"
    return text + "\n"


def format_bullet(line: str) -> str:
    """Convert a markdown bullet point to Typst list item."""
    stripped = line.strip()
    if stripped.startswith("- "):
        content = convert_inline(stripped[2:])
        return f"- {content}\n"
    elif stripped.startswith("* "):
        content = convert_inline(stripped[2:])
        return f"- {content}\n"
    return ""


def format_skill_line(line: str) -> str:
    """Format a skill category line.

    Handles patterns like:
        **Category:** Skill 1, Skill 2, Skill 3
        - Languages: Go, Python, Java
        - **Category:** Skill 1, Skill 2
    """
    stripped = line.strip()
    # Remove leading bullet if present
    if stripped.startswith("- "):
        stripped = stripped[2:]

    # Check for bold category
    match = re.match(r"\*\*(.+?)\*\*[:\s]+(.+)", stripped)
    if match:
        category = escape_typst(match.group(1).rstrip(":"))
        skills = escape_typst(match.group(2))
        return f"*{category}:* {skills}\n\n"

    # Check for plain category: value
    match = re.match(r"([A-Za-z &/]+):\s+(.+)", stripped)
    if match:
        category = escape_typst(match.group(1))
        skills = escape_typst(match.group(2))
        return f"*{category}:* {skills}\n\n"

    return convert_inline(stripped) + "\n\n"


def is_table_line(line: str) -> bool:
    """Check if a line is a markdown table row."""
    stripped = line.strip()
    return stripped.startswith("|") and stripped.endswith("|")


def is_table_separator(line: str) -> bool:
    """Check if a line is a markdown table separator (e.g., |---|---|---|)."""
    return bool(re.match(r"^\|[\s\-:|]+\|$", line.strip()))


def parse_table_cells(line: str) -> list[str]:
    """Extract cell contents from a markdown table row."""
    return [c.strip() for c in line.strip().strip("|").split("|") if c.strip()]


def format_table(table_lines: list[str]) -> str:
    """Convert markdown table lines to a Typst grid."""
    data_rows: list[list[str]] = []
    for line in table_lines:
        if is_table_separator(line):
            continue
        cells = parse_table_cells(line)
        if cells:
            data_rows.append(cells)

    if not data_rows:
        return ""

    num_cols = max(len(row) for row in data_rows)
    cols_spec = ", ".join(["1fr"] * num_cols)

    parts = [f"#grid(\n  columns: ({cols_spec}),\n  gutter: 0.5em,\n"]
    for row in data_rows:
        for cell in row:
            escaped = escape_typst(cell)
            parts.append(f"  [{escaped}],\n")
        for _ in range(num_cols - len(row)):
            parts.append("  [],\n")
    parts.append(")\n")
    return "".join(parts)


def is_skills_section(heading: str) -> bool:
    """Check if a section heading indicates a skills/expertise section."""
    lower = heading.lower()
    return any(
        kw in lower
        for kw in ["skill", "expertise", "competenc", "technologies", "tech stack"]
    )


def is_education_section(heading: str) -> bool:
    """Check if a section heading indicates an education section."""
    return "education" in heading.lower()


def generate_typst_content(parsed: dict) -> str:
    """Generate Typst content string from parsed resume data.

    This produces the resume content that will be injected into the template
    via sys_inputs. The template handles page setup, fonts, and styling.
    """
    parts: list[str] = []

    # Name
    if parsed["name"]:
        name = escape_typst(parsed["name"])
        parts.append(f'#align(center)[#text(size: 20pt, weight: "bold")[{name}]]\n')

    # Contact lines
    for cl in parsed["contact_lines"]:
        parts.append(
            f"#align(center)[#text(size: 9pt)[\n  {format_contact_line(cl)}"
            "]]\n"
        )

    parts.append("#v(0.3em)\n")
    parts.append('#line(length: 100%, stroke: 0.5pt + luma(180))\n')

    # Sections
    for section in parsed["sections"]:
        heading = section["heading"]
        level = section["level"]

        if level == 2:
            escaped_heading = escape_typst(heading)
            parts.append(f"\n== {escaped_heading}\n")
        elif level == 3:
            escaped_heading = escape_typst(heading)
            parts.append(f"\n=== {escaped_heading}\n")

        # Meta line (company/date for job entries)
        if section.get("meta_line"):
            parts.append(format_meta_line(section["meta_line"]))

        # Content lines
        is_skills = level == 2 and is_skills_section(heading)
        is_edu = level == 2 and is_education_section(heading)
        content_lines = section.get("content", [])

        # Collect and render content, detecting table blocks
        idx = 0
        while idx < len(content_lines):
            line = content_lines[idx]
            stripped = line.strip()

            if not stripped:
                idx += 1
                continue

            # Detect markdown table block (consecutive |...| lines)
            if is_table_line(stripped):
                table_block: list[str] = []
                while idx < len(content_lines) and is_table_line(
                    content_lines[idx].strip()
                ):
                    table_block.append(content_lines[idx])
                    idx += 1
                parts.append(format_table(table_block))
                continue

            if stripped.startswith("- ") or stripped.startswith("* "):
                if is_skills:
                    parts.append(format_skill_line(stripped))
                else:
                    parts.append(format_bullet(line))
            elif stripped.startswith("**") and is_skills:
                parts.append(format_skill_line(stripped))
            elif stripped.startswith("**") and "**" in stripped[2:]:
                # Bold line (e.g., degree line in education, career entry title)
                converted = convert_inline(stripped)
                parts.append(converted + "\n\n")
            else:
                # Regular paragraph text
                converted = convert_inline(stripped)
                parts.append(converted + "\n")
            idx += 1

    return "".join(parts)


# ---------------------------------------------------------------------------
# CLI argument parsing
# ---------------------------------------------------------------------------


def parse_args(argv: list[str]) -> dict:
    """Parse CLI arguments into a config dict."""
    if len(argv) < 2:
        return {"error": "Missing input file argument"}

    config: dict = {
        "input": argv[1],
        "output": None,
        "preset": "modern",
        "font": None,
        "color": None,
        "margin": None,
        "page_size": "letter",
        "line_spacing": None,
        "section_spacing": None,
        "pdf_a": False,
    }

    i = 2
    while i < len(argv):
        arg = argv[i]
        if arg == "--preset" and i + 1 < len(argv):
            config["preset"] = argv[i + 1].lower()
            i += 2
        elif arg == "--font" and i + 1 < len(argv):
            config["font"] = argv[i + 1]
            i += 2
        elif arg == "--color" and i + 1 < len(argv):
            config["color"] = argv[i + 1]
            i += 2
        elif arg == "--margin" and i + 1 < len(argv):
            config["margin"] = argv[i + 1].lower()
            i += 2
        elif arg == "--page-size" and i + 1 < len(argv):
            config["page_size"] = argv[i + 1].lower()
            i += 2
        elif arg == "--line-spacing" and i + 1 < len(argv):
            config["line_spacing"] = argv[i + 1].lower()
            i += 2
        elif arg == "--section-spacing" and i + 1 < len(argv):
            config["section_spacing"] = argv[i + 1].lower()
            i += 2
        elif arg == "--pdf-a":
            config["pdf_a"] = True
            i += 1
        elif not arg.startswith("--") and config["output"] is None:
            config["output"] = arg
            i += 1
        else:
            return {"error": f"Unknown argument: {arg}"}

    return config


def resolve_config(config: dict) -> dict:
    """Resolve config with preset defaults and validate values."""
    preset = config["preset"]
    if preset not in VALID_PRESETS:
        return {"error": f"Invalid preset: {preset}. Valid presets: {', '.join(VALID_PRESETS)}"}

    defaults = PRESET_DEFAULTS[preset]

    # Apply defaults where not overridden
    config["font"] = config["font"] or defaults["font"]
    config["margin"] = config["margin"] or defaults["margin"]
    config["line_spacing"] = config["line_spacing"] or defaults["line_spacing"]
    config["section_spacing"] = config["section_spacing"] or defaults["section_spacing"]
    config["font_size"] = defaults["font_size"]

    # Resolve color
    if config["color"] is None:
        config["color"] = defaults["color"]
    elif config["color"].lower() in NAMED_COLORS:
        config["color"] = NAMED_COLORS[config["color"].lower()]

    # Validate hex color
    if config["color"] and not re.match(r"^#[0-9A-Fa-f]{6}$", config["color"]):
        return {"error": f"Invalid color: {config['color']}. Use hex (#RRGGBB) or named preset."}

    # Validate margin
    if config["margin"] not in MARGIN_VALUES:
        return {"error": f"Invalid margin: {config['margin']}. Use: {', '.join(MARGIN_VALUES)}"}

    # Validate line spacing
    if config["line_spacing"] not in LINE_SPACING_VALUES:
        return {
            "error": f"Invalid line-spacing: {config['line_spacing']}. "
            f"Use: {', '.join(LINE_SPACING_VALUES)}"
        }

    # Validate section spacing
    if config["section_spacing"] not in SECTION_SPACING_VALUES:
        return {
            "error": f"Invalid section-spacing: {config['section_spacing']}. "
            f"Use: {', '.join(SECTION_SPACING_VALUES)}"
        }

    # Validate page size
    if config["page_size"] not in ("letter", "a4"):
        return {"error": f"Invalid page-size: {config['page_size']}. Use: letter, a4"}

    # Resolve output path
    if config["output"] is None:
        input_path = Path(config["input"])
        config["output"] = str(input_path.with_name(f"{input_path.stem}-optimized.pdf"))

    return config


def build_sys_inputs(config: dict) -> dict[str, str]:
    """Build the sys_inputs dict for the Typst template."""
    page_size = "us-letter" if config["page_size"] == "letter" else "a4"
    return {
        "font_family": config["font"],
        "font_size": config["font_size"],
        "accent_color": config["color"],
        "margin": MARGIN_VALUES[config["margin"]],
        "page_size": page_size,
        "line_spacing": LINE_SPACING_VALUES[config["line_spacing"]],
        "section_spacing": SECTION_SPACING_VALUES[config["section_spacing"]],
    }


# ---------------------------------------------------------------------------
# PDF generation
# ---------------------------------------------------------------------------


def generate_pdf(
    content: str,
    template_path: Path,
    sys_inputs: dict[str, str],
    output_path: str,
    *,
    pdf_a: bool = False,
    name: str = "",
) -> None:
    """Compile Typst content to PDF using the specified template.

    The template is the main file. Resume content is passed via sys_inputs
    as a JSON string that the template reads and renders.
    """
    # Pass the resume content as a sys_input
    all_inputs = {**sys_inputs, "resume_content": content}

    # Build font paths
    font_paths: list[str] = []
    if FONTS_DIR.is_dir():
        font_paths.append(str(FONTS_DIR))

    # PDF standards
    pdf_standards: list[str] = []
    if pdf_a:
        pdf_standards.append("a-2b")

    compiled = typst.compile(
        input=str(template_path),
        font_paths=font_paths,
        sys_inputs=all_inputs,
        pdf_standards=pdf_standards,
    )

    Path(output_path).write_bytes(compiled)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    config = parse_args(sys.argv)
    if "error" in config:
        print(f"Error: {config['error']}", file=sys.stderr)
        print(
            f"Usage: {sys.argv[0]} <input-md> [output-pdf] [--preset PRESET] "
            "[--font FONT] [--color COLOR] [--margin MARGIN] "
            "[--page-size SIZE] [--line-spacing SPACING] "
            "[--section-spacing SPACE] [--pdf-a]",
            file=sys.stderr,
        )
        return 1

    config = resolve_config(config)
    if "error" in config:
        print(f"Error: {config['error']}", file=sys.stderr)
        return 1

    # Read input markdown
    input_path = Path(config["input"])
    if not input_path.exists():
        print(f"Error: File not found: {input_path}", file=sys.stderr)
        return 1

    md_text = input_path.read_text(encoding="utf-8")
    if not md_text.strip():
        print("Error: Input file is empty", file=sys.stderr)
        return 1

    # Parse markdown
    parsed = parse_resume_markdown(md_text)

    # Print warnings to stderr
    for warning in parsed.get("warnings", []):
        print(f"WARNING: {warning}", file=sys.stderr)

    # Generate Typst content
    typst_content = generate_typst_content(parsed)

    # Resolve template
    preset = config["preset"]
    template_path = TEMPLATES_DIR / f"{preset}.typ"
    if not template_path.exists():
        print(f"Error: Template not found: {template_path}", file=sys.stderr)
        return 1

    # Build sys_inputs
    sys_inputs = build_sys_inputs(config)

    # Generate PDF
    output_path = config["output"]
    generate_pdf(
        typst_content,
        template_path,
        sys_inputs,
        output_path,
        pdf_a=config["pdf_a"],
        name=parsed.get("name", ""),
    )

    file_size = Path(output_path).stat().st_size
    size_str = f"{file_size / 1024:.1f} KB" if file_size < 1024 * 1024 else f"{file_size / (1024 * 1024):.1f} MB"
    print(f"PDF generated: {output_path} ({size_str})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
