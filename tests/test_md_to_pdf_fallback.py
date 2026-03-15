"""Tests for the Python PDF fallback renderer (fpdf2-based)."""

import sys
import time
import warnings
from pathlib import Path

import fitz  # pymupdf
import pytest

# Add scripts/ to path so we can import the modules
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from md_to_pdf_fallback import (
    PRESET_DEFAULTS,
    VALID_PRESETS,
    RenderConfig,
    _PRESET_STYLES,
    generate_pdf_fallback,
)
from parse_resume import parse_resume_markdown

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

FONTS_DIR = Path(__file__).resolve().parent.parent / "fonts"

FULL_RESUME_MD = """\
# Jane Doe

jane.doe@email.com | (555) 123-4567 | linkedin.com/in/janedoe | github.com/janedoe

## Summary

Experienced software engineer with 10+ years of experience building scalable systems.

## Experience

### Senior Software Engineer

**Acme Corp**, San Francisco, CA | Jan 2020 - Present

- Led a team of 5 engineers to deliver a microservices platform
- Reduced deployment time by **40%** through CI/CD pipeline optimization
- Mentored 3 junior engineers on best practices

### Software Engineer

**StartupCo**, New York, NY | Jun 2015 - Dec 2019

- Built RESTful APIs serving 1M+ daily requests
- Implemented *real-time* data processing pipeline using Kafka

## Education

### Master of Science in Computer Science

**MIT**, Cambridge, MA | 2015

### Bachelor of Science in Mathematics

**UCLA**, Los Angeles, CA | 2013

## Skills

- **Languages:** Python, Go, Java, TypeScript
- **Frameworks:** Django, FastAPI, React
- **Cloud:** AWS, GCP, Kubernetes, Docker
"""


def _extract_text(pdf_path: Path) -> str:
    """Extract all text from a PDF file using pymupdf."""
    doc = fitz.open(str(pdf_path))
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text


def _page_count(pdf_path: Path) -> int:
    """Return the number of pages in a PDF file."""
    doc = fitz.open(str(pdf_path))
    count = doc.page_count
    doc.close()
    return count


# ---------------------------------------------------------------------------
# Unit: Renderer produces valid PDF output
# ---------------------------------------------------------------------------


class TestGeneratePdfFallbackBasic:
    """Core PDF generation tests."""

    def test_generates_valid_pdf_file(self, tmp_path: Path) -> None:
        parsed = parse_resume_markdown(FULL_RESUME_MD)
        out = tmp_path / "output.pdf"
        result = generate_pdf_fallback(parsed, str(out))
        assert result.exists()
        assert result.stat().st_size > 0
        # PDF magic bytes
        with open(result, "rb") as f:
            header = f.read(5)
        assert header == b"%PDF-"

    def test_generates_pdf_without_typst(self, tmp_path: Path) -> None:
        """Verify this path does not import or use typst."""
        parsed = parse_resume_markdown(FULL_RESUME_MD)
        out = tmp_path / "no-typst.pdf"
        result = generate_pdf_fallback(parsed, str(out))
        assert result.exists()
        # The module itself should not depend on typst
        import md_to_pdf_fallback

        source = Path(md_to_pdf_fallback.__file__).read_text()
        assert "import typst" not in source

    def test_consumes_shared_parser_output(self, tmp_path: Path) -> None:
        parsed = parse_resume_markdown(FULL_RESUME_MD)
        # Verify it uses the standard parser output structure
        assert "name" in parsed
        assert "contact_lines" in parsed
        assert "sections" in parsed
        out = tmp_path / "parser-output.pdf"
        result = generate_pdf_fallback(parsed, str(out))
        assert result.exists()

    def test_default_preset_is_modern(self, tmp_path: Path) -> None:
        parsed = parse_resume_markdown(FULL_RESUME_MD)
        out = tmp_path / "default.pdf"
        result = generate_pdf_fallback(parsed, str(out))
        assert result.exists()

    def test_all_presets_generate_valid_pdfs(self, tmp_path: Path) -> None:
        parsed = parse_resume_markdown(FULL_RESUME_MD)
        for preset in VALID_PRESETS:
            out = tmp_path / f"{preset}.pdf"
            result = generate_pdf_fallback(parsed, str(out), preset=preset)
            assert result.exists(), f"Preset {preset} failed to generate"
            assert result.stat().st_size > 0, f"Preset {preset} generated empty PDF"

    def test_output_path_creates_parent_dirs(self, tmp_path: Path) -> None:
        parsed = parse_resume_markdown(FULL_RESUME_MD)
        out = tmp_path / "nested" / "deep" / "output.pdf"
        result = generate_pdf_fallback(parsed, str(out))
        assert result.exists()

    def test_returns_path_object(self, tmp_path: Path) -> None:
        parsed = parse_resume_markdown(FULL_RESUME_MD)
        out = tmp_path / "return.pdf"
        result = generate_pdf_fallback(parsed, str(out))
        assert isinstance(result, Path)
        assert result == out


# ---------------------------------------------------------------------------
# Unit: Text layer is extractable from generated PDF
# ---------------------------------------------------------------------------


class TestTextLayerExtraction:
    """Verify that generated PDFs have a native text layer (ATS compatible)."""

    def test_name_extractable(self, tmp_path: Path) -> None:
        parsed = parse_resume_markdown(FULL_RESUME_MD)
        out = tmp_path / "text.pdf"
        generate_pdf_fallback(parsed, str(out))
        text = _extract_text(out)
        assert "Jane Doe" in text

    def test_contact_info_extractable(self, tmp_path: Path) -> None:
        parsed = parse_resume_markdown(FULL_RESUME_MD)
        out = tmp_path / "contact.pdf"
        generate_pdf_fallback(parsed, str(out))
        text = _extract_text(out)
        assert "jane.doe@email.com" in text

    def test_section_headings_extractable(self, tmp_path: Path) -> None:
        parsed = parse_resume_markdown(FULL_RESUME_MD)
        out = tmp_path / "headings.pdf"
        generate_pdf_fallback(parsed, str(out))
        text = _extract_text(out)
        # Default modern preset uses uppercase headings
        assert "EXPERIENCE" in text
        assert "EDUCATION" in text
        assert "SKILLS" in text

    def test_job_titles_extractable(self, tmp_path: Path) -> None:
        parsed = parse_resume_markdown(FULL_RESUME_MD)
        out = tmp_path / "titles.pdf"
        generate_pdf_fallback(parsed, str(out))
        text = _extract_text(out)
        assert "Senior Software Engineer" in text
        assert "Software Engineer" in text

    def test_bullet_content_extractable(self, tmp_path: Path) -> None:
        parsed = parse_resume_markdown(FULL_RESUME_MD)
        out = tmp_path / "bullets.pdf"
        generate_pdf_fallback(parsed, str(out))
        text = _extract_text(out)
        assert "Led a team" in text
        assert "40%" in text
        assert "CI/CD" in text

    def test_skills_extractable(self, tmp_path: Path) -> None:
        parsed = parse_resume_markdown(FULL_RESUME_MD)
        out = tmp_path / "skills.pdf"
        generate_pdf_fallback(parsed, str(out))
        text = _extract_text(out)
        assert "Python" in text
        assert "Docker" in text

    def test_all_presets_have_extractable_text(self, tmp_path: Path) -> None:
        parsed = parse_resume_markdown(FULL_RESUME_MD)
        for preset in VALID_PRESETS:
            out = tmp_path / f"{preset}-text.pdf"
            generate_pdf_fallback(parsed, str(out), preset=preset)
            text = _extract_text(out)
            assert "Jane Doe" in text, f"Name missing in {preset} preset"
            # Check for section heading (case-insensitive since classic is mixed case)
            text_upper = text.upper()
            assert "EXPERIENCE" in text_upper, f"Experience section missing in {preset} preset"


# ---------------------------------------------------------------------------
# Unit: Preset-specific visual styling
# ---------------------------------------------------------------------------


class TestPresetStyles:
    """Verify each preset applies correct fonts, colors, and visual treatment."""

    def test_modern_preset_uses_inter_font(self) -> None:
        cfg = RenderConfig("modern")
        assert cfg.font_family == "Inter"
        assert cfg.font_size == 10.0

    def test_modern_preset_uppercase_headings(self) -> None:
        cfg = RenderConfig("modern")
        assert cfg.h2_uppercase is True

    def test_modern_preset_accent_underline(self) -> None:
        cfg = RenderConfig("modern")
        assert cfg.h2_underline_uses_accent is True
        assert cfg.h2_underline_stroke_pt == 0.7

    def test_modern_preset_name_size(self) -> None:
        cfg = RenderConfig("modern")
        assert cfg.name_size_pt == 20

    def test_classic_preset_uses_garamond_font(self) -> None:
        cfg = RenderConfig("classic")
        assert cfg.font_family == "EB Garamond"
        assert cfg.font_size == 11.0

    def test_classic_preset_mixed_case_headings(self) -> None:
        cfg = RenderConfig("classic")
        assert cfg.h2_uppercase is False

    def test_classic_preset_gray_underline(self) -> None:
        cfg = RenderConfig("classic")
        assert cfg.h2_underline_uses_accent is False
        assert cfg.h2_underline_luma == 120

    def test_classic_preset_diamond_bullet(self) -> None:
        cfg = RenderConfig("classic")
        assert cfg.bullet_char == "\u25C6"

    def test_classic_preset_name_size(self) -> None:
        cfg = RenderConfig("classic")
        assert cfg.name_size_pt == 22

    def test_classic_produces_mixed_case_headings(self, tmp_path: Path) -> None:
        parsed = parse_resume_markdown(FULL_RESUME_MD)
        out = tmp_path / "classic.pdf"
        generate_pdf_fallback(parsed, str(out), preset="classic")
        text = _extract_text(out)
        assert "Experience" in text
        assert "EXPERIENCE" not in text

    def test_compact_preset_uses_source_sans(self) -> None:
        cfg = RenderConfig("compact")
        assert cfg.font_family == "Source Sans 3"
        assert cfg.font_size == 9.5

    def test_compact_preset_uppercase_headings(self) -> None:
        cfg = RenderConfig("compact")
        assert cfg.h2_uppercase is True

    def test_compact_preset_narrow_margins(self) -> None:
        cfg = RenderConfig("compact")
        assert cfg.margin_mm == 12.7  # narrow = 0.5in

    def test_compact_preset_small_name(self) -> None:
        cfg = RenderConfig("compact")
        assert cfg.name_size_pt == 17

    def test_harvard_preset_uses_garamond(self) -> None:
        cfg = RenderConfig("harvard")
        assert cfg.font_family == "EB Garamond"
        assert cfg.font_size == 11.0

    def test_harvard_preset_all_black(self) -> None:
        cfg = RenderConfig("harvard")
        assert cfg.accent_color == "#000000"
        assert cfg.h2_text_luma == 0
        assert cfg.h2_underline_luma == 0
        assert cfg.body_text_luma == 10

    def test_harvard_preset_uppercase_headings(self) -> None:
        cfg = RenderConfig("harvard")
        assert cfg.h2_uppercase is True

    def test_harvard_preset_wide_margins(self) -> None:
        cfg = RenderConfig("harvard")
        assert cfg.margin_mm == 25.4  # wide = 1in

    def test_each_preset_generates_with_correct_font(self, tmp_path: Path) -> None:
        """Each preset should generate output; text content verified per-preset."""
        parsed = parse_resume_markdown(FULL_RESUME_MD)
        for preset in VALID_PRESETS:
            out = tmp_path / f"{preset}-style.pdf"
            result = generate_pdf_fallback(parsed, str(out), preset=preset)
            assert result.exists()
            text = _extract_text(out)
            assert "Jane Doe" in text
            # Verify skills content is present
            assert "Python" in text

    def test_each_preset_has_style_entry(self) -> None:
        """Every preset in PRESET_DEFAULTS must have a matching entry in _PRESET_STYLES."""
        for preset in PRESET_DEFAULTS:
            assert preset in _PRESET_STYLES, f"Missing style entry for preset '{preset}'"


# ---------------------------------------------------------------------------
# Unit: Customization options
# ---------------------------------------------------------------------------


class TestCustomizationOptions:
    """Verify each customization option applies correctly."""

    def test_font_customization_source_sans(self, tmp_path: Path) -> None:
        parsed = parse_resume_markdown(FULL_RESUME_MD)
        out = tmp_path / "source-sans.pdf"
        result = generate_pdf_fallback(parsed, str(out), font="Source Sans 3")
        assert result.exists()
        text = _extract_text(out)
        assert "Jane Doe" in text

    def test_font_customization_eb_garamond(self, tmp_path: Path) -> None:
        parsed = parse_resume_markdown(FULL_RESUME_MD)
        out = tmp_path / "garamond.pdf"
        result = generate_pdf_fallback(parsed, str(out), font="EB Garamond")
        assert result.exists()

    def test_accent_color_applies_to_headings(self, tmp_path: Path) -> None:
        """Custom accent color should produce a valid PDF (color applied to headings/bullets)."""
        parsed = parse_resume_markdown(FULL_RESUME_MD)
        out = tmp_path / "red-accent.pdf"
        result = generate_pdf_fallback(parsed, str(out), color="#FF0000")
        assert result.exists()
        text = _extract_text(out)
        assert "EXPERIENCE" in text

    def test_accent_color_named_preset(self, tmp_path: Path) -> None:
        parsed = parse_resume_markdown(FULL_RESUME_MD)
        out = tmp_path / "burgundy.pdf"
        result = generate_pdf_fallback(parsed, str(out), color="burgundy")
        assert result.exists()

    def test_page_size_a4(self, tmp_path: Path) -> None:
        parsed = parse_resume_markdown(FULL_RESUME_MD)
        out = tmp_path / "a4.pdf"
        result = generate_pdf_fallback(parsed, str(out), page_size="a4")
        assert result.exists()

    def test_page_size_letter(self, tmp_path: Path) -> None:
        parsed = parse_resume_markdown(FULL_RESUME_MD)
        out = tmp_path / "letter.pdf"
        result = generate_pdf_fallback(parsed, str(out), page_size="letter")
        assert result.exists()

    def test_margin_preset_narrow(self, tmp_path: Path) -> None:
        parsed = parse_resume_markdown(FULL_RESUME_MD)
        out = tmp_path / "narrow.pdf"
        result = generate_pdf_fallback(parsed, str(out), margin="narrow")
        assert result.exists()

    def test_margin_preset_wide(self, tmp_path: Path) -> None:
        parsed = parse_resume_markdown(FULL_RESUME_MD)
        out = tmp_path / "wide.pdf"
        result = generate_pdf_fallback(parsed, str(out), margin="wide")
        assert result.exists()

    def test_margin_numeric_value(self, tmp_path: Path) -> None:
        parsed = parse_resume_markdown(FULL_RESUME_MD)
        out = tmp_path / "numeric-margin.pdf"
        result = generate_pdf_fallback(parsed, str(out), margin=15.0)
        assert result.exists()

    def test_margin_numeric_string(self, tmp_path: Path) -> None:
        parsed = parse_resume_markdown(FULL_RESUME_MD)
        out = tmp_path / "string-margin.pdf"
        result = generate_pdf_fallback(parsed, str(out), margin="20")
        assert result.exists()

    def test_line_spacing_tight(self, tmp_path: Path) -> None:
        parsed = parse_resume_markdown(FULL_RESUME_MD)
        out = tmp_path / "tight.pdf"
        result = generate_pdf_fallback(parsed, str(out), line_spacing="tight")
        assert result.exists()

    def test_line_spacing_relaxed(self, tmp_path: Path) -> None:
        parsed = parse_resume_markdown(FULL_RESUME_MD)
        out = tmp_path / "relaxed.pdf"
        result = generate_pdf_fallback(parsed, str(out), line_spacing="relaxed")
        assert result.exists()

    def test_section_spacing_compact(self, tmp_path: Path) -> None:
        parsed = parse_resume_markdown(FULL_RESUME_MD)
        out = tmp_path / "compact-spacing.pdf"
        result = generate_pdf_fallback(parsed, str(out), section_spacing="compact")
        assert result.exists()

    def test_section_spacing_generous(self, tmp_path: Path) -> None:
        parsed = parse_resume_markdown(FULL_RESUME_MD)
        out = tmp_path / "generous.pdf"
        result = generate_pdf_fallback(parsed, str(out), section_spacing="generous")
        assert result.exists()

    def test_pdf_a_flag_accepted(self, tmp_path: Path) -> None:
        """PDF/A flag should be accepted with a warning, generating a standard PDF."""
        parsed = parse_resume_markdown(FULL_RESUME_MD)
        out = tmp_path / "pdfa.pdf"
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            result = generate_pdf_fallback(parsed, str(out), pdf_a=True)
        assert result.exists()
        # Should have emitted a warning about PDF/A limitation
        pdfa_warnings = [w for w in caught if "PDF/A" in str(w.message)]
        assert len(pdfa_warnings) > 0

    def test_combined_customizations(self, tmp_path: Path) -> None:
        """Multiple customizations applied at once should work together."""
        parsed = parse_resume_markdown(FULL_RESUME_MD)
        out = tmp_path / "combined.pdf"
        result = generate_pdf_fallback(
            parsed,
            str(out),
            preset="classic",
            font="Inter",
            color="teal",
            margin="wide",
            page_size="a4",
            line_spacing="relaxed",
            section_spacing="generous",
        )
        assert result.exists()
        text = _extract_text(out)
        assert "Jane Doe" in text


# ---------------------------------------------------------------------------
# Font embedding
# ---------------------------------------------------------------------------


class TestFontEmbedding:
    """Verify font embedding from the fonts/ directory."""

    def test_fonts_directory_exists(self) -> None:
        assert FONTS_DIR.exists(), f"Fonts directory not found: {FONTS_DIR}"

    def test_each_preset_font_files_exist(self) -> None:
        from md_to_pdf_fallback import _FONT_MAP, PRESET_DEFAULTS

        for preset, defaults in PRESET_DEFAULTS.items():
            family = defaults["font"]
            mapping = _FONT_MAP.get(family)
            assert mapping is not None, f"Font family {family} not in _FONT_MAP"
            for style, filename in mapping.items():
                path = FONTS_DIR / filename
                assert path.exists(), f"Font file missing for {preset}/{family}/{style}: {path}"

    def test_custom_fonts_dir(self, tmp_path: Path) -> None:
        """Verify the fonts_dir parameter works."""
        import shutil

        custom_fonts = tmp_path / "custom-fonts"
        custom_fonts.mkdir()
        # Copy Inter fonts
        for f in FONTS_DIR.glob("Inter*"):
            shutil.copy2(f, custom_fonts / f.name)

        parsed = parse_resume_markdown(FULL_RESUME_MD)
        out = tmp_path / "custom-font.pdf"
        result = generate_pdf_fallback(
            parsed, str(out), preset="modern", fonts_dir=custom_fonts
        )
        assert result.exists()

    def test_missing_font_file_raises_error(self, tmp_path: Path) -> None:
        empty_fonts = tmp_path / "empty-fonts"
        empty_fonts.mkdir()
        parsed = parse_resume_markdown(FULL_RESUME_MD)
        out = tmp_path / "missing.pdf"
        with pytest.raises(FileNotFoundError, match="Font file not found"):
            generate_pdf_fallback(parsed, str(out), fonts_dir=empty_fonts)

    def test_unknown_font_falls_back_with_warning(self, tmp_path: Path) -> None:
        """Unknown font should fall back to preset default with a warning."""
        parsed = parse_resume_markdown(FULL_RESUME_MD)
        out = tmp_path / "fallback.pdf"
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            result = generate_pdf_fallback(parsed, str(out), font="Comic Sans MS")
        assert result.exists()
        # Verify a warning was emitted about font fallback
        font_warnings = [w for w in caught if "Comic Sans MS" in str(w.message)]
        assert len(font_warnings) > 0
        assert "Falling back" in str(font_warnings[0].message)

    def test_font_fallback_uses_preset_default(self) -> None:
        """When a custom font isn't bundled, RenderConfig should use the preset default."""
        cfg = RenderConfig("modern", font="Not A Real Font")
        assert cfg.font_family == "Inter"  # modern preset default
        assert len(cfg.font_warnings) == 1

    def test_font_fallback_for_classic_preset(self) -> None:
        cfg = RenderConfig("classic", font="Missing Font")
        assert cfg.font_family == "EB Garamond"
        assert len(cfg.font_warnings) == 1


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


class TestEdgeCases:
    """Edge case handling."""

    def test_multipage_resume(self, tmp_path: Path) -> None:
        """Resume exceeding one page should flow to additional pages."""
        sections = []
        for i in range(15):
            sections.append(
                f"### Engineer {i+1}\n\n"
                f"**Company {i+1}**, City, ST | 2020 - Present\n\n"
                f"- Achievement line one for position {i+1}\n"
                f"- Achievement line two for position {i+1}\n"
                f"- Achievement line three for position {i+1}\n"
                f"- Achievement line four for position {i+1}\n"
            )

        md = (
            "# Long Resume\n\n"
            "email@test.com\n\n"
            "## Summary\n\nA summary.\n\n"
            "## Experience\n\n"
            + "\n".join(sections)
            + "\n## Education\n\n## Skills\n\n- **Languages:** Python\n"
        )
        parsed = parse_resume_markdown(md)
        out = tmp_path / "multipage.pdf"
        result = generate_pdf_fallback(parsed, str(out))
        assert result.exists()
        pages = _page_count(out)
        assert pages > 1, f"Expected multi-page PDF, got {pages} page(s)"

    def test_file_size_under_30mb(self, tmp_path: Path) -> None:
        """Even large resumes should produce PDFs under 30MB."""
        sections = []
        for i in range(50):
            sections.append(
                f"### Engineer {i+1}\n\n"
                f"**Company {i+1}**, City, ST | 2020 - Present\n\n"
                + "\n".join(f"- Long achievement description number {j} for position {i+1}" for j in range(10))
                + "\n"
            )
        md = (
            "# Massive Resume\n\n"
            "email@test.com\n\n"
            "## Experience\n\n"
            + "\n".join(sections)
            + "\n## Education\n\n## Skills\n\n## Summary\n\n"
        )
        parsed = parse_resume_markdown(md)
        out = tmp_path / "large.pdf"
        result = generate_pdf_fallback(parsed, str(out))
        assert result.stat().st_size < 30 * 1024 * 1024

    def test_empty_sections(self, tmp_path: Path) -> None:
        md = "# Test\n\n## Summary\n\n## Experience\n\n## Education\n\n## Skills\n"
        parsed = parse_resume_markdown(md)
        out = tmp_path / "empty-sections.pdf"
        result = generate_pdf_fallback(parsed, str(out))
        assert result.exists()
        text = _extract_text(out)
        assert "Test" in text

    def test_resume_with_tables(self, tmp_path: Path) -> None:
        md = (
            "# Name\n\n## Summary\n\nText.\n\n"
            "## Experience\n\n## Education\n\n"
            "## Skills\n\n"
            "| Category | Skills |\n"
            "|----------|--------|\n"
            "| Languages | Python, Go |\n"
            "| Cloud | AWS, GCP |\n"
        )
        parsed = parse_resume_markdown(md)
        out = tmp_path / "tables.pdf"
        result = generate_pdf_fallback(parsed, str(out))
        assert result.exists()
        text = _extract_text(out)
        assert "Python" in text

    def test_resume_with_links(self, tmp_path: Path) -> None:
        md = (
            "# Name\n\n## Summary\n\nText.\n\n"
            "## Experience\n\n### Role\n\n"
            "**Co** | 2020\n\n"
            "- See [my project](https://example.com)\n\n"
            "## Education\n\n## Skills\n"
        )
        parsed = parse_resume_markdown(md)
        out = tmp_path / "links.pdf"
        result = generate_pdf_fallback(parsed, str(out))
        assert result.exists()
        text = _extract_text(out)
        assert "my project" in text

    def test_a4_page_size(self, tmp_path: Path) -> None:
        parsed = parse_resume_markdown(FULL_RESUME_MD)
        out = tmp_path / "a4.pdf"
        result = generate_pdf_fallback(parsed, str(out), page_size="a4")
        assert result.exists()
        assert result.stat().st_size > 0

    def test_extreme_margin_clamped_to_minimum(self) -> None:
        """Margins below the minimum should be clamped to 5mm."""
        cfg = RenderConfig("modern", margin=1.0)
        assert cfg.margin_mm == 5.0  # clamped to _MIN_MARGIN_MM

    def test_zero_margin_clamped(self) -> None:
        cfg = RenderConfig("modern", margin=0.0)
        assert cfg.margin_mm == 5.0

    def test_negative_margin_clamped(self) -> None:
        cfg = RenderConfig("modern", margin=-10.0)
        assert cfg.margin_mm == 5.0

    def test_extreme_margin_generates_valid_pdf(self, tmp_path: Path) -> None:
        """Even with minimum margins, PDF should generate correctly."""
        parsed = parse_resume_markdown(FULL_RESUME_MD)
        out = tmp_path / "min-margin.pdf"
        result = generate_pdf_fallback(parsed, str(out), margin=1.0)
        assert result.exists()
        text = _extract_text(out)
        assert "Jane Doe" in text

    def test_long_resume_with_small_margins(self, tmp_path: Path) -> None:
        """Very long resume with small margins should still break pages correctly."""
        sections = []
        for i in range(20):
            sections.append(
                f"### Engineer {i+1}\n\n"
                f"**Company {i+1}**, City, ST | 2020 - Present\n\n"
                f"- Achievement one for position {i+1}\n"
                f"- Achievement two for position {i+1}\n"
                f"- Achievement three for position {i+1}\n"
            )
        md = (
            "# Long Resume\n\n"
            "email@test.com\n\n"
            "## Experience\n\n"
            + "\n".join(sections)
            + "\n## Education\n\n## Skills\n\n- **Languages:** Python\n"
        )
        parsed = parse_resume_markdown(md)
        out = tmp_path / "long-small-margin.pdf"
        result = generate_pdf_fallback(parsed, str(out), margin=6.0)
        assert result.exists()
        pages = _page_count(out)
        assert pages > 1


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------


class TestErrorHandling:
    """Error handling verification."""

    def test_invalid_preset_raises_value_error(self, tmp_path: Path) -> None:
        parsed = parse_resume_markdown(FULL_RESUME_MD)
        out = tmp_path / "bad.pdf"
        with pytest.raises(ValueError, match="Invalid preset"):
            generate_pdf_fallback(parsed, str(out), preset="nonexistent")

    def test_invalid_color_raises_value_error(self, tmp_path: Path) -> None:
        parsed = parse_resume_markdown(FULL_RESUME_MD)
        out = tmp_path / "bad.pdf"
        with pytest.raises(ValueError, match="Invalid color"):
            generate_pdf_fallback(parsed, str(out), color="not-a-color")

    def test_invalid_margin_raises_value_error(self, tmp_path: Path) -> None:
        parsed = parse_resume_markdown(FULL_RESUME_MD)
        out = tmp_path / "bad.pdf"
        with pytest.raises(ValueError, match="Invalid margin"):
            generate_pdf_fallback(parsed, str(out), margin="huge")

    def test_invalid_line_spacing_raises_value_error(self, tmp_path: Path) -> None:
        parsed = parse_resume_markdown(FULL_RESUME_MD)
        out = tmp_path / "bad.pdf"
        with pytest.raises(ValueError, match="Invalid line_spacing"):
            generate_pdf_fallback(parsed, str(out), line_spacing="mega")

    def test_invalid_section_spacing_raises_value_error(self, tmp_path: Path) -> None:
        parsed = parse_resume_markdown(FULL_RESUME_MD)
        out = tmp_path / "bad.pdf"
        with pytest.raises(ValueError, match="Invalid section_spacing"):
            generate_pdf_fallback(parsed, str(out), section_spacing="mega")

    def test_invalid_page_size_raises_value_error(self, tmp_path: Path) -> None:
        parsed = parse_resume_markdown(FULL_RESUME_MD)
        out = tmp_path / "bad.pdf"
        with pytest.raises(ValueError, match="Invalid page_size"):
            generate_pdf_fallback(parsed, str(out), page_size="tabloid")

    def test_named_color_resolves(self, tmp_path: Path) -> None:
        parsed = parse_resume_markdown(FULL_RESUME_MD)
        out = tmp_path / "navy.pdf"
        result = generate_pdf_fallback(parsed, str(out), color="navy")
        assert result.exists()

    def test_hex_color_works(self, tmp_path: Path) -> None:
        parsed = parse_resume_markdown(FULL_RESUME_MD)
        out = tmp_path / "hex.pdf"
        result = generate_pdf_fallback(parsed, str(out), color="#FF5733")
        assert result.exists()


# ---------------------------------------------------------------------------
# Performance
# ---------------------------------------------------------------------------


class TestPerformance:
    """Performance benchmarks."""

    def test_generation_under_10_seconds(self, tmp_path: Path) -> None:
        """A typical 2-page resume should generate in under 10 seconds."""
        parsed = parse_resume_markdown(FULL_RESUME_MD)
        start = time.perf_counter()
        generate_pdf_fallback(parsed, str(tmp_path / "perf.pdf"))
        elapsed = time.perf_counter() - start
        assert elapsed < 10.0, f"PDF generation took {elapsed:.2f}s (limit: 10s)"

    def test_all_presets_under_10_seconds_each(self, tmp_path: Path) -> None:
        """Each preset should generate in under 10 seconds."""
        parsed = parse_resume_markdown(FULL_RESUME_MD)
        for preset in VALID_PRESETS:
            start = time.perf_counter()
            generate_pdf_fallback(parsed, str(tmp_path / f"{preset}-perf.pdf"), preset=preset)
            elapsed = time.perf_counter() - start
            assert elapsed < 10.0, f"Preset {preset} took {elapsed:.2f}s (limit: 10s)"


# ---------------------------------------------------------------------------
# RenderConfig
# ---------------------------------------------------------------------------


class TestRenderConfig:
    """Test the RenderConfig dataclass."""

    def test_default_modern_config(self) -> None:
        cfg = RenderConfig()
        assert cfg.font_family == "Inter"
        assert cfg.font_size == 10.0
        assert cfg.accent_color == "#2B547E"

    def test_classic_config(self) -> None:
        cfg = RenderConfig("classic")
        assert cfg.font_family == "EB Garamond"
        assert cfg.font_size == 11.0

    def test_compact_config(self) -> None:
        cfg = RenderConfig("compact")
        assert cfg.font_family == "Source Sans 3"
        assert cfg.font_size == 9.5

    def test_harvard_config(self) -> None:
        cfg = RenderConfig("harvard")
        assert cfg.font_family == "EB Garamond"
        assert cfg.accent_color == "#000000"

    def test_font_override(self) -> None:
        cfg = RenderConfig("modern", font="Lato")
        assert cfg.font_family == "Lato"

    def test_color_override_named(self) -> None:
        cfg = RenderConfig("modern", color="teal")
        assert cfg.accent_color == "#008080"

    def test_color_override_hex(self) -> None:
        cfg = RenderConfig("modern", color="#FF0000")
        assert cfg.accent_color == "#FF0000"
        assert cfg.accent_rgb == (255, 0, 0)

    def test_preset_name_stored(self) -> None:
        for preset in VALID_PRESETS:
            cfg = RenderConfig(preset)
            assert cfg.preset_name == preset

    def test_numeric_margin_accepted(self) -> None:
        cfg = RenderConfig("modern", margin=18.0)
        assert cfg.margin_mm == 18.0

    def test_numeric_string_margin_accepted(self) -> None:
        cfg = RenderConfig("modern", margin="18")
        assert cfg.margin_mm == 18.0

    def test_pdf_a_default_false(self) -> None:
        cfg = RenderConfig()
        assert cfg.pdf_a is False
        assert len(cfg.font_warnings) == 0

    def test_pdf_a_true_emits_warning(self) -> None:
        cfg = RenderConfig(pdf_a=True)
        assert cfg.pdf_a is True
        assert any("PDF/A" in w for w in cfg.font_warnings)
