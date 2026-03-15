"""Pure-Python PDF fallback renderer using fpdf2.

Used when Typst is unavailable (e.g., in Cowork VM). Consumes the shared
parser output from ``parse_resume.py`` and generates an ATS-compatible PDF
with embedded fonts.

Supports 4 presets (modern, classic, compact, harvard), each with
preset-specific visual styling that matches the Typst templates.  All
customisation options (font, accent colour, margins, page size, line
spacing, section spacing) are supported.

Usage as module:
    from md_to_pdf_fallback import generate_pdf_fallback

    from parse_resume import parse_resume_markdown
    parsed = parse_resume_markdown(markdown_text)
    generate_pdf_fallback(parsed, "output.pdf")

Usage as CLI:
    uv run scripts/md_to_pdf_fallback.py <input.md> [output.pdf] [--preset PRESET]
"""

import re
import sys
import warnings
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
FONTS_DIR = PROJECT_ROOT / "fonts"

# Minimum margin in mm to prevent layout breakage
_MIN_MARGIN_MM = 5.0

# ---------------------------------------------------------------------------
# Font mapping: family name -> {style: filename}
# Variable-weight fonts are used for both regular and bold via the same file.
# ---------------------------------------------------------------------------

_FONT_MAP: dict[str, dict[str, str]] = {
    "Inter": {
        "": "Inter[opsz,wght].ttf",
        "B": "Inter[opsz,wght].ttf",
        "I": "Inter-Italic[opsz,wght].ttf",
        "BI": "Inter-Italic[opsz,wght].ttf",
    },
    "EB Garamond": {
        "": "EBGaramond[wght].ttf",
        "B": "EBGaramond[wght].ttf",
        "I": "EBGaramond-Italic[wght].ttf",
        "BI": "EBGaramond-Italic[wght].ttf",
    },
    "Lato": {
        "": "Lato[wght].ttf",
        "B": "Lato[wght].ttf",
        "I": "Lato-Italic[wght].ttf",
        "BI": "Lato-Italic[wght].ttf",
    },
    "Source Sans 3": {
        "": "SourceSans3[wght].ttf",
        "B": "SourceSans3[wght].ttf",
        "I": "SourceSans3-Italic[wght].ttf",
        "BI": "SourceSans3-Italic[wght].ttf",
    },
}

# ---------------------------------------------------------------------------
# Preset definitions (mirrors md-to-pdf.py PRESET_DEFAULTS)
# ---------------------------------------------------------------------------

NAMED_COLORS: dict[str, str] = {
    "navy": "#2B547E",
    "teal": "#008080",
    "charcoal": "#36454F",
    "black": "#000000",
    "burgundy": "#800020",
}

MARGIN_PRESETS: dict[str, float] = {
    "narrow": 12.7,     # 0.5 in -> mm
    "standard": 19.05,  # 0.75 in -> mm
    "wide": 25.4,       # 1.0 in -> mm
}

LINE_SPACING_PRESETS: dict[str, float] = {
    "tight": 4.0,
    "standard": 5.0,
    "relaxed": 6.0,
}

SECTION_SPACING_PRESETS: dict[str, float] = {
    "compact": 3.0,
    "standard": 5.0,
    "generous": 7.0,
}

# Per-preset visual style overrides that mirror the Typst templates.
# Keys: h2_uppercase, h2_underline_uses_accent, h2_underline_stroke_pt,
#        bullet_char, name_size_pt, h2_size_offset, h3_size_offset
_PRESET_STYLES: dict[str, dict] = {
    "modern": {
        "h2_uppercase": True,
        "h2_underline_uses_accent": True,
        "h2_underline_stroke_pt": 0.7,
        "bullet_char": "\u2022",       # filled circle (small)
        "name_size_pt": 20,
        "h2_size_offset": 2.0,
        "h3_size_offset": 1.0,
        "body_text_luma": 30,          # luma(30) in Typst
    },
    "classic": {
        "h2_uppercase": False,
        "h2_underline_uses_accent": False,
        "h2_underline_stroke_pt": 0.5,
        "h2_underline_luma": 120,      # gray underline
        "bullet_char": "\u25C6",       # filled diamond
        "name_size_pt": 22,
        "h2_size_offset": 1.5,
        "h3_size_offset": 0.5,
        "body_text_luma": 20,
    },
    "compact": {
        "h2_uppercase": True,
        "h2_underline_uses_accent": True,
        "h2_underline_stroke_pt": 0.5,
        "bullet_char": "\u2022",       # filled circle
        "name_size_pt": 17,
        "h2_size_offset": 1.5,
        "h3_size_offset": 0.5,
        "body_text_luma": 30,
    },
    "harvard": {
        "h2_uppercase": True,
        "h2_underline_uses_accent": False,
        "h2_underline_stroke_pt": 0.5,
        "h2_underline_luma": 0,        # black underline
        "h2_text_luma": 0,             # black text on heading
        "bullet_char": "\u2022",       # filled circle
        "name_size_pt": 20,
        "h2_size_offset": 1.0,
        "h3_size_offset": 0.5,
        "body_text_luma": 10,
    },
}

PRESET_DEFAULTS: dict[str, dict[str, str]] = {
    "classic": {
        "font": "EB Garamond",
        "color": "#2B547E",
        "margin": "standard",
        "line_spacing": "standard",
        "section_spacing": "standard",
        "font_size": "11",
    },
    "modern": {
        "font": "Inter",
        "color": "#2B547E",
        "margin": "standard",
        "line_spacing": "standard",
        "section_spacing": "standard",
        "font_size": "10",
    },
    "compact": {
        "font": "Source Sans 3",
        "color": "#36454F",
        "margin": "narrow",
        "line_spacing": "tight",
        "section_spacing": "compact",
        "font_size": "9.5",
    },
    "harvard": {
        "font": "EB Garamond",
        "color": "#000000",
        "margin": "wide",
        "line_spacing": "tight",
        "section_spacing": "compact",
        "font_size": "11",
    },
}

VALID_PRESETS = list(PRESET_DEFAULTS.keys())

PAGE_SIZES: dict[str, tuple[float, float]] = {
    "letter": (215.9, 279.4),
    "a4": (210.0, 297.0),
}


def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    """Convert ``#RRGGBB`` to an ``(r, g, b)`` tuple."""
    h = hex_color.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def _is_skills_section(heading: str) -> bool:
    """Check if a section heading indicates a skills/expertise section."""
    lower = heading.lower()
    return any(
        kw in lower
        for kw in ["skill", "expertise", "competenc", "technologies", "tech stack"]
    )


# ---------------------------------------------------------------------------
# Inline markdown processing
# ---------------------------------------------------------------------------


def _strip_inline_md(text: str) -> str:
    """Remove markdown inline formatting, returning plain text."""
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    return text


def _render_inline_md(pdf: "FPDF", text: str, base_style: str = "") -> None:
    """Write *text* to *pdf* with markdown bold/italic interpreted.

    Uses ``pdf.write()`` to emit inline runs with style changes.  The caller
    must have already set the desired font family and size before calling.

    Only ``**bold**``, ``*italic*``, and ``[text](url)`` are supported.
    Other markdown is passed through as literal text.
    """
    # Tokenise into segments: bold, italic, link, plain
    pattern = re.compile(
        r"(\*\*(.+?)\*\*)"                  # bold
        r"|(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)"  # italic
        r"|(\[([^\]]+)\]\(([^)]+)\))"        # link
    )
    last = 0
    family = pdf.font_family
    size = pdf.font_size_pt

    for m in pattern.finditer(text):
        # Plain text before this match
        if m.start() > last:
            pdf.set_font(family, base_style, size)
            pdf.write(h=pdf.font_size * 1.4, text=text[last:m.start()])

        if m.group(2) is not None:
            # Bold
            style = "B" + base_style.replace("B", "")
            pdf.set_font(family, style, size)
            pdf.write(h=pdf.font_size * 1.4, text=m.group(2))
        elif m.group(3) is not None:
            # Italic
            style = base_style + ("I" if "I" not in base_style else "")
            pdf.set_font(family, style, size)
            pdf.write(h=pdf.font_size * 1.4, text=m.group(3))
        elif m.group(5) is not None:
            # Link
            pdf.set_font(family, base_style, size)
            pdf.write(h=pdf.font_size * 1.4, text=m.group(5), link=m.group(6))

        last = m.end()

    # Trailing plain text
    if last < len(text):
        pdf.set_font(family, base_style, size)
        pdf.write(h=pdf.font_size * 1.4, text=text[last:])


# ---------------------------------------------------------------------------
# Resolved configuration
# ---------------------------------------------------------------------------


class RenderConfig:
    """Resolved rendering configuration for a single PDF generation."""

    def __init__(
        self,
        preset: str = "modern",
        *,
        font: str | None = None,
        color: str | None = None,
        margin: str | float | None = None,
        page_size: str = "letter",
        line_spacing: str | None = None,
        section_spacing: str | None = None,
        pdf_a: bool = False,
    ) -> None:
        if preset not in PRESET_DEFAULTS:
            raise ValueError(
                f"Invalid preset: {preset}. Valid presets: {', '.join(VALID_PRESETS)}"
            )

        self.preset_name: str = preset
        defaults = PRESET_DEFAULTS[preset]
        self.font_family: str = font or defaults["font"]
        self.font_size: float = float(defaults["font_size"])
        self.page_size_name: str = page_size

        # Font fallback: if a custom font is specified that isn't in the
        # bundled set, fall back to the preset default and emit a warning.
        self.font_warnings: list[str] = []
        if font and font not in _FONT_MAP:
            self.font_warnings.append(
                f"Font '{font}' not found in bundled fonts. "
                f"Falling back to preset default '{defaults['font']}'. "
                f"Available fonts: {', '.join(sorted(_FONT_MAP))}"
            )
            self.font_family = defaults["font"]

        # Resolve colour
        raw_color = color or defaults["color"]
        if raw_color.lower() in NAMED_COLORS:
            raw_color = NAMED_COLORS[raw_color.lower()]
        if not re.match(r"^#[0-9A-Fa-f]{6}$", raw_color):
            raise ValueError(f"Invalid color: {raw_color}. Use hex (#RRGGBB) or named preset.")
        self.accent_color: str = raw_color
        self.accent_rgb: tuple[int, int, int] = _hex_to_rgb(raw_color)

        # Resolve margin - accepts named presets or numeric mm values
        if margin is None:
            margin_key = defaults["margin"]
            self.margin_mm = MARGIN_PRESETS[margin_key]
        elif isinstance(margin, (int, float)):
            self.margin_mm = max(float(margin), _MIN_MARGIN_MM)
        elif isinstance(margin, str):
            if margin in MARGIN_PRESETS:
                self.margin_mm = MARGIN_PRESETS[margin]
            else:
                # Try parsing as a numeric string
                try:
                    self.margin_mm = max(float(margin), _MIN_MARGIN_MM)
                except ValueError:
                    raise ValueError(
                        f"Invalid margin: {margin}. "
                        f"Use a named preset ({', '.join(MARGIN_PRESETS)}) "
                        f"or a numeric value in mm."
                    )
        else:
            raise ValueError(f"Invalid margin type: {type(margin)}")

        # Resolve line spacing
        ls_key = line_spacing or defaults["line_spacing"]
        if ls_key not in LINE_SPACING_PRESETS:
            raise ValueError(f"Invalid line_spacing: {ls_key}. Use: {', '.join(LINE_SPACING_PRESETS)}")

        # Resolve section spacing
        ss_key = section_spacing or defaults["section_spacing"]
        if ss_key not in SECTION_SPACING_PRESETS:
            raise ValueError(f"Invalid section_spacing: {ss_key}. Use: {', '.join(SECTION_SPACING_PRESETS)}")

        self.line_spacing_mm: float = LINE_SPACING_PRESETS[ls_key]
        self.section_spacing_mm: float = SECTION_SPACING_PRESETS[ss_key]

        if page_size not in PAGE_SIZES:
            raise ValueError(f"Invalid page_size: {page_size}. Use: letter, a4")
        self.page_w_mm, self.page_h_mm = PAGE_SIZES[page_size]

        # PDF/A compliance: fpdf2 does not natively produce PDF/A output.
        # The flag is accepted and stored, but the output will not be
        # PDF/A compliant.  A warning is emitted when the flag is set.
        self.pdf_a: bool = pdf_a
        if pdf_a:
            self.font_warnings.append(
                "PDF/A compliance requested but fpdf2 does not support PDF/A output. "
                "The generated PDF will be a standard PDF.  Use the Typst renderer "
                "for PDF/A-2b compliance."
            )

        # Preset-specific visual style (matches Typst template differences)
        style = _PRESET_STYLES[preset]
        self.h2_uppercase: bool = style["h2_uppercase"]
        self.h2_underline_uses_accent: bool = style["h2_underline_uses_accent"]
        self.h2_underline_stroke_pt: float = style["h2_underline_stroke_pt"]
        self.h2_underline_luma: int | None = style.get("h2_underline_luma")
        self.h2_text_luma: int | None = style.get("h2_text_luma")
        self.bullet_char: str = style["bullet_char"]
        self.name_size_pt: float = style["name_size_pt"]
        self.h2_size_offset: float = style["h2_size_offset"]
        self.h3_size_offset: float = style["h3_size_offset"]
        self.body_text_luma: int = style["body_text_luma"]


# ---------------------------------------------------------------------------
# Core renderer
# ---------------------------------------------------------------------------


def _register_fonts(pdf: "FPDF", family: str, fonts_dir: Path) -> None:
    """Register a bundled font family (regular, bold, italic, bold-italic)."""
    mapping = _FONT_MAP.get(family)
    if mapping is None:
        raise FileNotFoundError(
            f"Font family '{family}' is not bundled. "
            f"Available: {', '.join(sorted(_FONT_MAP))}. "
            f"Check the fonts/ directory."
        )

    for style, filename in mapping.items():
        font_path = fonts_dir / filename
        if not font_path.exists():
            raise FileNotFoundError(
                f"Font file not found: {font_path}. "
                f"Ensure the fonts/ directory contains {filename}."
            )
        pdf.add_font(family, style, str(font_path))


def _render_contact_line(pdf: "FPDF", contact_line: str, cfg: RenderConfig) -> None:
    """Render a pipe-delimited contact line centred on the page."""
    parts = [p.strip() for p in contact_line.split("|") if p.strip()]
    combined = "  |  ".join(parts)
    pdf.set_font(cfg.font_family, "", 9)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(w=0, h=4.5, text=combined, align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(0, 0, 0)


def _render_section_heading(pdf: "FPDF", heading: str, cfg: RenderConfig) -> None:
    """Render a top-level (H2) section heading with preset-specific styling.

    Preset differences:
    - modern:  UPPERCASE, accent-coloured text + accent-coloured underline (0.7pt)
    - classic: Mixed case, accent-coloured text + gray underline (0.5pt)
    - compact: UPPERCASE, accent-coloured text + accent-coloured underline (0.5pt)
    - harvard: UPPERCASE, black text + black underline (0.5pt)
    """
    pdf.ln(cfg.section_spacing_mm)
    pdf.set_font(cfg.font_family, "B", cfg.font_size + cfg.h2_size_offset)

    # Heading text colour
    if cfg.h2_text_luma is not None:
        # Fixed luminance (e.g. harvard uses pure black)
        pdf.set_text_color(cfg.h2_text_luma, cfg.h2_text_luma, cfg.h2_text_luma)
    else:
        r, g, b = cfg.accent_rgb
        pdf.set_text_color(r, g, b)

    display_text = heading.upper() if cfg.h2_uppercase else heading
    pdf.cell(w=0, h=6, text=display_text, new_x="LMARGIN", new_y="NEXT")

    # Underline
    y = pdf.get_y()
    if cfg.h2_underline_uses_accent:
        r, g, b = cfg.accent_rgb
        pdf.set_draw_color(r, g, b)
    elif cfg.h2_underline_luma is not None:
        luma = cfg.h2_underline_luma
        pdf.set_draw_color(luma, luma, luma)
    else:
        pdf.set_draw_color(0, 0, 0)

    # Stroke weight varies by preset
    x1 = pdf.l_margin
    x2 = pdf.w - pdf.r_margin
    # fpdf2 line() uses set_line_width for thickness
    old_lw = pdf.line_width
    pdf.set_line_width(cfg.h2_underline_stroke_pt * 0.3528)  # pt -> mm
    pdf.line(x1, y, x2, y)
    pdf.set_line_width(old_lw)

    pdf.ln(1.5)
    luma_val = cfg.body_text_luma
    pdf.set_text_color(luma_val, luma_val, luma_val)
    pdf.set_draw_color(0, 0, 0)


def _render_subsection_heading(pdf: "FPDF", heading: str, cfg: RenderConfig) -> None:
    """Render a subsection (H3) heading."""
    pdf.ln(cfg.line_spacing_mm * 0.6)
    pdf.set_font(cfg.font_family, "B", cfg.font_size + cfg.h3_size_offset)
    pdf.cell(w=0, h=5.5, text=heading, new_x="LMARGIN", new_y="NEXT")


def _render_meta_line(pdf: "FPDF", meta_line: str, cfg: RenderConfig) -> None:
    """Render a bold company/date meta line with right-aligned date."""
    text = _strip_inline_md(meta_line)

    sep = None
    for candidate in [" | ", " \u2014 ", " -- "]:
        if candidate in text:
            sep = candidate
            break

    pdf.set_font(cfg.font_family, "", cfg.font_size - 0.5)
    if sep:
        left, right = text.split(sep, 1)
        # Left part (company + location)
        left_w = pdf.get_string_width(left)
        right_w = pdf.get_string_width(right)
        available = pdf.w - pdf.l_margin - pdf.r_margin

        pdf.set_font(cfg.font_family, "B", cfg.font_size - 0.5)
        pdf.cell(w=available - right_w - 2, h=5, text=left)
        pdf.set_font(cfg.font_family, "", cfg.font_size - 0.5)
        pdf.cell(w=right_w + 2, h=5, text=right, align="R", new_x="LMARGIN", new_y="NEXT")
    else:
        pdf.set_font(cfg.font_family, "B", cfg.font_size - 0.5)
        pdf.cell(w=0, h=5, text=text, new_x="LMARGIN", new_y="NEXT")


def _render_bullet(pdf: "FPDF", text: str, cfg: RenderConfig) -> None:
    """Render a bullet point with hanging indent and preset-specific marker."""
    stripped = text.strip()
    if stripped.startswith("- "):
        stripped = stripped[2:]
    elif stripped.startswith("* "):
        stripped = stripped[2:]

    pdf.set_font(cfg.font_family, "", cfg.font_size)
    bullet_indent = 5

    # Use preset-specific bullet character and colour
    r, g, b = cfg.accent_rgb
    pdf.set_text_color(r, g, b)
    pdf.cell(w=bullet_indent, h=cfg.line_spacing_mm, text=f"  {cfg.bullet_char} ")
    luma_val = cfg.body_text_luma
    pdf.set_text_color(luma_val, luma_val, luma_val)

    # Use multi_cell for text that may wrap
    available_w = pdf.w - pdf.r_margin - pdf.get_x()
    _render_inline_md(pdf, stripped)
    pdf.ln(cfg.line_spacing_mm)


def _render_skill_line(pdf: "FPDF", text: str, cfg: RenderConfig) -> None:
    """Render a skill category line: **Category:** Value."""
    stripped = text.strip()
    if stripped.startswith("- "):
        stripped = stripped[2:]

    # Check for **Category:** value pattern
    match = re.match(r"\*\*(.+?)\*\*[:\s]+(.+)", stripped)
    if not match:
        match = re.match(r"([A-Za-z &/]+):\s+(.+)", stripped)

    if match:
        category = match.group(1).rstrip(":")
        skills = match.group(2)
        pdf.set_font(cfg.font_family, "B", cfg.font_size)
        cat_w = pdf.get_string_width(category + ": ")
        pdf.cell(w=cat_w, h=cfg.line_spacing_mm, text=f"{category}: ")
        pdf.set_font(cfg.font_family, "", cfg.font_size)
        available_w = pdf.w - pdf.r_margin - pdf.get_x()
        pdf.multi_cell(w=available_w, h=cfg.line_spacing_mm, text=skills, new_x="LMARGIN", new_y="NEXT")
    else:
        pdf.set_font(cfg.font_family, "", cfg.font_size)
        pdf.multi_cell(w=0, h=cfg.line_spacing_mm, text=_strip_inline_md(stripped), new_x="LMARGIN", new_y="NEXT")


def _render_table(pdf: "FPDF", table_lines: list[str], cfg: RenderConfig) -> None:
    """Render a simple markdown table as a grid."""
    rows: list[list[str]] = []
    for line in table_lines:
        stripped = line.strip()
        if re.match(r"^\|[\s\-:|]+\|$", stripped):
            continue
        cells = [c.strip() for c in stripped.strip("|").split("|") if c.strip()]
        if cells:
            rows.append(cells)

    if not rows:
        return

    num_cols = max(len(row) for row in rows)
    available_w = pdf.w - pdf.l_margin - pdf.r_margin
    col_w = available_w / num_cols

    pdf.set_font(cfg.font_family, "", cfg.font_size - 1)
    for i, row in enumerate(rows):
        style = "B" if i == 0 else ""
        pdf.set_font(cfg.font_family, style, cfg.font_size - 1)
        for j, cell in enumerate(row):
            pdf.cell(w=col_w, h=cfg.line_spacing_mm, text=cell)
        pdf.ln(cfg.line_spacing_mm)


def generate_pdf_fallback(
    parsed: dict,
    output_path: str,
    *,
    preset: str = "modern",
    font: str | None = None,
    color: str | None = None,
    margin: str | float | None = None,
    page_size: str = "letter",
    line_spacing: str | None = None,
    section_spacing: str | None = None,
    fonts_dir: Path | None = None,
    pdf_a: bool = False,
) -> Path:
    """Generate a PDF from parsed resume data using fpdf2.

    Parameters
    ----------
    parsed:
        Output of ``parse_resume_markdown()``.
    output_path:
        Destination file path for the PDF.
    preset:
        Preset name (modern, classic, compact, harvard).
    font:
        Font family override.  If the font is not in the bundled set,
        falls back to the preset default with a warning.
    color:
        Accent colour (#RRGGBB or named preset).
    margin:
        Margin preset name (narrow, standard, wide) or numeric value in mm.
        Values below 5mm are clamped to the minimum.
    page_size:
        Page size (letter, a4).
    line_spacing:
        Line spacing preset (tight, standard, relaxed).
    section_spacing:
        Section spacing preset (compact, standard, generous).
    fonts_dir:
        Override path to the fonts directory (defaults to ``PROJECT_ROOT/fonts``).
    pdf_a:
        Request PDF/A compliance. Not supported by fpdf2; a warning is
        emitted and a standard PDF is generated instead.

    Returns
    -------
    Path
        The path to the generated PDF file.

    Raises
    ------
    ImportError
        If fpdf2 is not installed.
    FileNotFoundError
        If font files are missing.
    ValueError
        If invalid preset or option values are provided.
    """
    try:
        from fpdf import FPDF
    except ImportError:
        raise ImportError(
            "fpdf2 is required for Python PDF fallback rendering. "
            "Install it with: uv add fpdf2  (or: pip install fpdf2)"
        )

    cfg = RenderConfig(
        preset,
        font=font,
        color=color,
        margin=margin,
        page_size=page_size,
        line_spacing=line_spacing,
        section_spacing=section_spacing,
        pdf_a=pdf_a,
    )

    # Emit any warnings from config resolution
    for w in cfg.font_warnings:
        warnings.warn(w, UserWarning, stacklevel=2)

    _fonts_dir = fonts_dir or FONTS_DIR

    # Create PDF
    pdf = FPDF(unit="mm", format=(cfg.page_w_mm, cfg.page_h_mm))
    pdf.set_auto_page_break(auto=True, margin=cfg.margin_mm)
    pdf.set_margins(cfg.margin_mm, cfg.margin_mm, cfg.margin_mm)

    # Register fonts
    _register_fonts(pdf, cfg.font_family, _fonts_dir)

    pdf.add_page()

    # Set base text colour from preset
    luma_val = cfg.body_text_luma
    pdf.set_text_color(luma_val, luma_val, luma_val)

    # --- Name (centred, large) ---
    if parsed.get("name"):
        pdf.set_font(cfg.font_family, "B", cfg.name_size_pt)
        pdf.cell(w=0, h=9, text=parsed["name"], align="C", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(1)

    # --- Contact lines ---
    for cl in parsed.get("contact_lines", []):
        _render_contact_line(pdf, cl, cfg)

    # Divider
    pdf.ln(2)
    pdf.set_draw_color(180, 180, 180)
    pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
    pdf.ln(2)

    # --- Sections ---
    for section in parsed.get("sections", []):
        heading = section["heading"]
        level = section["level"]

        if level == 2:
            _render_section_heading(pdf, heading, cfg)
        elif level == 3:
            _render_subsection_heading(pdf, heading, cfg)

        # Meta line
        if section.get("meta_line"):
            _render_meta_line(pdf, section["meta_line"], cfg)

        # Content
        is_skills = level == 2 and _is_skills_section(heading)
        content_lines = section.get("content", [])

        idx = 0
        while idx < len(content_lines):
            line = content_lines[idx]
            stripped = line.strip()

            if not stripped:
                idx += 1
                continue

            # Table detection
            if stripped.startswith("|") and stripped.endswith("|"):
                table_block: list[str] = []
                while idx < len(content_lines):
                    s = content_lines[idx].strip()
                    if s.startswith("|") and s.endswith("|"):
                        table_block.append(content_lines[idx])
                        idx += 1
                    else:
                        break
                _render_table(pdf, table_block, cfg)
                continue

            if stripped.startswith("- ") or stripped.startswith("* "):
                if is_skills:
                    _render_skill_line(pdf, stripped, cfg)
                else:
                    _render_bullet(pdf, stripped, cfg)
            elif stripped.startswith("**") and is_skills:
                _render_skill_line(pdf, stripped, cfg)
            elif stripped.startswith("**") and "**" in stripped[2:]:
                # Bold paragraph (e.g., degree line in education)
                plain = _strip_inline_md(stripped)
                pdf.set_font(cfg.font_family, "B", cfg.font_size)
                pdf.multi_cell(w=0, h=cfg.line_spacing_mm, text=plain, new_x="LMARGIN", new_y="NEXT")
            else:
                # Regular paragraph
                pdf.set_font(cfg.font_family, "", cfg.font_size)
                _render_inline_md(pdf, stripped)
                pdf.ln(cfg.line_spacing_mm)

            idx += 1

    # Write output
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(out))

    # Post-generation edge case checks
    from export_edge_cases import check_output_size, check_page_count_pdf, emit_warnings
    size_warnings = check_output_size(out)
    page_warnings = check_page_count_pdf(out)
    all_warnings = size_warnings + page_warnings
    if all_warnings:
        emit_warnings(all_warnings)

    return out


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def parse_cli_args(argv: list[str]) -> dict:
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


def main() -> int:
    config = parse_cli_args(sys.argv)
    if "error" in config:
        print(f"Error: {config['error']}", file=sys.stderr)
        print(
            f"Usage: {sys.argv[0]} <input.md> [output.pdf] [--preset PRESET] "
            "[--font FONT] [--color COLOR] [--margin MARGIN] "
            "[--page-size SIZE] [--line-spacing SPACING] "
            "[--section-spacing SPACE] [--pdf-a]",
            file=sys.stderr,
        )
        return 1

    input_path = Path(config["input"])
    if not input_path.exists():
        print(f"Error: File not found: {input_path}", file=sys.stderr)
        return 1

    try:
        md_text = input_path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        print(f"Error: File is not valid text/markdown: {exc}", file=sys.stderr)
        return 1

    if not md_text.strip():
        print("Error: Input file is empty", file=sys.stderr)
        return 1

    from parse_resume import parse_resume_markdown

    try:
        parsed = parse_resume_markdown(md_text)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    for warning in parsed.get("warnings", []):
        print(f"WARNING: {warning}", file=sys.stderr)

    output_path = config.pop("output", None) or str(
        input_path.with_name(f"{input_path.stem}-optimized.pdf")
    )
    input_arg = config.pop("input")

    try:
        result_path = generate_pdf_fallback(
            parsed,
            output_path,
            preset=config["preset"],
            font=config.get("font"),
            color=config.get("color"),
            margin=config.get("margin"),
            page_size=config.get("page_size", "letter"),
            line_spacing=config.get("line_spacing"),
            section_spacing=config.get("section_spacing"),
            pdf_a=config.get("pdf_a", False),
        )
    except (ImportError, FileNotFoundError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    file_size = result_path.stat().st_size
    if file_size < 1024 * 1024:
        size_str = f"{file_size / 1024:.1f} KB"
    else:
        size_str = f"{file_size / (1024 * 1024):.1f} MB"
    print(f"PDF generated: {result_path} ({size_str})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
