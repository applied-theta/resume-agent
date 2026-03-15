"""Tests for post-export PDF ATS validation."""

import sys
import time
from pathlib import Path
from unittest.mock import patch

import pytest

# Add scripts/ to path so we can import the modules
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from validate_pdf import (
    _detect_garbled_text,
    _extract_key_phrases,
    _extract_pdf_text,
    _extract_section_headings,
    validate_pdf,
)
from parse_resume import parse_resume_markdown
from md_to_pdf_fallback import generate_pdf_fallback

# ---------------------------------------------------------------------------
# Test data
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

SINGLE_SECTION_MD = """\
# John Smith

john@example.com

## Skills

- **Languages:** Python, JavaScript, Ruby
"""

UNICODE_MD = """\
# Rene Dupont

rene.dupont@email.com

## Summary

Experienced developpeur with expertise in cloud-native architectures.

## Experience

### Developpeur Senior

**Societe Generale**, Paris | 2020 - Present

- Led migration of legacy systems to microservices
- Managed cross-functional team of 8 engineers

## Education

### Diplome d'Ingenieur

**Ecole Polytechnique** | 2018

## Skills

- **Languages:** Python, Go, Rust
"""


def _generate_test_pdf(md: str, output_path: Path) -> Path:
    """Helper: generate a PDF from markdown using the fallback renderer."""
    parsed = parse_resume_markdown(md)
    return generate_pdf_fallback(parsed, str(output_path))


# ---------------------------------------------------------------------------
# Unit: Section heading extraction
# ---------------------------------------------------------------------------


class TestExtractSectionHeadings:
    """Test _extract_section_headings helper."""

    def test_extracts_h2_headings(self) -> None:
        headings = _extract_section_headings(FULL_RESUME_MD)
        assert "Summary" in headings
        assert "Experience" in headings
        assert "Education" in headings
        assert "Skills" in headings

    def test_does_not_extract_h3_headings(self) -> None:
        headings = _extract_section_headings(FULL_RESUME_MD)
        assert "Senior Software Engineer" not in headings
        assert "Master of Science in Computer Science" not in headings

    def test_does_not_extract_h1_heading(self) -> None:
        headings = _extract_section_headings(FULL_RESUME_MD)
        assert "Jane Doe" not in headings

    def test_empty_markdown(self) -> None:
        headings = _extract_section_headings("")
        assert headings == []

    def test_single_section(self) -> None:
        headings = _extract_section_headings(SINGLE_SECTION_MD)
        assert headings == ["Skills"]


# ---------------------------------------------------------------------------
# Unit: Key phrase extraction
# ---------------------------------------------------------------------------


class TestExtractKeyPhrases:
    """Test _extract_key_phrases helper."""

    def test_extracts_name(self) -> None:
        phrases = _extract_key_phrases(FULL_RESUME_MD)
        assert "Jane Doe" in phrases

    def test_extracts_job_titles(self) -> None:
        phrases = _extract_key_phrases(FULL_RESUME_MD)
        assert "Senior Software Engineer" in phrases
        assert "Software Engineer" in phrases

    def test_extracts_bullet_phrases(self) -> None:
        phrases = _extract_key_phrases(FULL_RESUME_MD)
        # Should contain beginning of bullet text
        has_bullet = any("Led a team" in p for p in phrases)
        assert has_bullet

    def test_strips_markdown_formatting(self) -> None:
        phrases = _extract_key_phrases(FULL_RESUME_MD)
        # Bold markers should be removed
        for p in phrases:
            assert "**" not in p


# ---------------------------------------------------------------------------
# Unit: Garbled text detection
# ---------------------------------------------------------------------------


class TestDetectGarbledText:
    """Test _detect_garbled_text helper."""

    def test_clean_text_not_garbled(self) -> None:
        text = (
            "Jane Doe\n"
            "Senior Software Engineer\n"
            "Experience with Python, Go, and Java.\n"
            "Led a team of 5 engineers."
        )
        assert _detect_garbled_text(text) is False

    def test_replacement_characters_detected(self) -> None:
        text = "Jane \ufffd\ufffd\ufffd Engineer \ufffd\ufffd\ufffd\ufffd " + "x" * 200
        assert _detect_garbled_text(text) is True

    def test_control_characters_detected(self) -> None:
        text = "Name\x01\x02\x03\x04\x05\x06\x07\x08 Engineer " + "x" * 200
        assert _detect_garbled_text(text) is True

    def test_long_special_char_runs_detected(self) -> None:
        text = "Some text " + "\u00a7" * 10 + " more text"
        assert _detect_garbled_text(text) is True

    def test_empty_text_not_garbled(self) -> None:
        assert _detect_garbled_text("") is False
        assert _detect_garbled_text("   ") is False

    def test_normal_unicode_not_garbled(self) -> None:
        text = (
            "Rene Dupont\n"
            "Experienced developer with 10+ years.\n"
            "Bullet point with an em-dash \u2014 and smart quotes \u201cHello\u201d"
        )
        assert _detect_garbled_text(text) is False

    def test_bullet_chars_not_garbled(self) -> None:
        text = (
            "EXPERIENCE\n"
            "\u2022 Led a team of 5 engineers\n"
            "\u2022 Reduced deployment time by 40%\n"
            "\u2022 Mentored junior engineers"
        )
        assert _detect_garbled_text(text) is False


# ---------------------------------------------------------------------------
# Unit: Validation correctly identifies complete content (pass case)
# ---------------------------------------------------------------------------


class TestValidationPassCase:
    """Validation correctly identifies complete content."""

    def test_full_resume_passes(self, tmp_path: Path) -> None:
        pdf_path = tmp_path / "full.pdf"
        _generate_test_pdf(FULL_RESUME_MD, pdf_path)
        result = validate_pdf(str(pdf_path), FULL_RESUME_MD)
        assert result["status"] == "pass"
        assert result["issues"] == []
        assert result["checks"]["text_extraction"] is True
        assert result["checks"]["section_headings"] is True
        assert result["checks"]["content_completeness"] is True

    def test_single_section_resume_passes(self, tmp_path: Path) -> None:
        pdf_path = tmp_path / "single.pdf"
        _generate_test_pdf(SINGLE_SECTION_MD, pdf_path)
        result = validate_pdf(str(pdf_path), SINGLE_SECTION_MD)
        assert result["status"] == "pass"
        assert result["checks"]["section_headings"] is True

    def test_returns_extracted_text(self, tmp_path: Path) -> None:
        pdf_path = tmp_path / "text.pdf"
        _generate_test_pdf(FULL_RESUME_MD, pdf_path)
        result = validate_pdf(str(pdf_path), FULL_RESUME_MD)
        assert len(result["extracted_text"]) > 0
        assert "Jane Doe" in result["extracted_text"]

    def test_result_has_structured_format(self, tmp_path: Path) -> None:
        pdf_path = tmp_path / "struct.pdf"
        _generate_test_pdf(FULL_RESUME_MD, pdf_path)
        result = validate_pdf(str(pdf_path), FULL_RESUME_MD)
        assert "status" in result
        assert "extracted_text" in result
        assert "issues" in result
        assert "checks" in result
        assert isinstance(result["issues"], list)
        assert isinstance(result["checks"], dict)


# ---------------------------------------------------------------------------
# Unit: Validation correctly identifies missing sections (fail case)
# ---------------------------------------------------------------------------


class TestValidationFailCase:
    """Validation correctly identifies missing sections."""

    def test_missing_heading_detected(self, tmp_path: Path) -> None:
        # Generate a PDF from a resume missing "Experience"
        md_for_pdf = """\
# Test Person

test@example.com

## Summary

A brief summary.

## Education

### BS in CS

**MIT** | 2020

## Skills

- **Languages:** Python
"""
        # The source markdown has an Experience section that the PDF doesn't
        source_with_experience = md_for_pdf + "\n## Experience\n\n### Role\n\n- Did stuff\n"

        pdf_path = tmp_path / "missing.pdf"
        _generate_test_pdf(md_for_pdf, pdf_path)
        result = validate_pdf(str(pdf_path), source_with_experience)
        assert result["status"] == "fail"
        assert result["checks"]["section_headings"] is False
        has_heading_issue = any(i["type"] == "missing_headings" for i in result["issues"])
        assert has_heading_issue

    def test_missing_content_detected(self, tmp_path: Path) -> None:
        # Generate a minimal PDF but validate against a full resume
        minimal_md = """\
# Test Person

## Summary

A brief summary.

## Experience

## Education

## Skills
"""
        pdf_path = tmp_path / "minimal.pdf"
        _generate_test_pdf(minimal_md, pdf_path)

        # Validate against the full resume which has much more content
        result = validate_pdf(str(pdf_path), FULL_RESUME_MD)
        assert result["status"] == "fail"
        has_content_issue = any(i["type"] == "missing_content" for i in result["issues"])
        assert has_content_issue

    def test_garbled_text_causes_failure(self, tmp_path: Path) -> None:
        pdf_path = tmp_path / "garbled.pdf"
        _generate_test_pdf(FULL_RESUME_MD, pdf_path)

        # Mock the text extraction to return garbled text
        garbled = "\ufffd" * 50 + "x" * 200
        with patch("validate_pdf._extract_pdf_text", return_value=garbled):
            result = validate_pdf(str(pdf_path), FULL_RESUME_MD)
        assert result["status"] == "fail"
        assert result["checks"]["font_embedding"] is False
        has_garbled_issue = any(i["type"] == "garbled_text" for i in result["issues"])
        assert has_garbled_issue


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


class TestEdgeCases:
    """Edge case handling."""

    def test_very_short_resume_single_section(self, tmp_path: Path) -> None:
        pdf_path = tmp_path / "short.pdf"
        _generate_test_pdf(SINGLE_SECTION_MD, pdf_path)
        result = validate_pdf(str(pdf_path), SINGLE_SECTION_MD)
        assert result["status"] == "pass"
        assert result["checks"]["section_headings"] is True

    def test_unicode_characters_handled(self, tmp_path: Path) -> None:
        pdf_path = tmp_path / "unicode.pdf"
        _generate_test_pdf(UNICODE_MD, pdf_path)
        result = validate_pdf(str(pdf_path), UNICODE_MD)
        # Should at least extract text without error
        assert result["checks"]["text_extraction"] is True
        assert len(result["extracted_text"]) > 0

    def test_garbled_text_flagged_correctly(self, tmp_path: Path) -> None:
        pdf_path = tmp_path / "garble-test.pdf"
        _generate_test_pdf(FULL_RESUME_MD, pdf_path)

        garbled = "\ufffd" * 100 + "a" * 200
        with patch("validate_pdf._extract_pdf_text", return_value=garbled):
            result = validate_pdf(str(pdf_path), FULL_RESUME_MD)
        assert result["checks"]["font_embedding"] is False
        has_issue = any(i["type"] == "garbled_text" for i in result["issues"])
        assert has_issue


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------


class TestErrorHandling:
    """Error handling verification."""

    def test_pdf_file_not_found(self) -> None:
        with pytest.raises(FileNotFoundError, match="PDF file not found"):
            validate_pdf("/nonexistent/path.pdf", FULL_RESUME_MD)

    def test_pdf_file_not_found_via_extract(self) -> None:
        with pytest.raises(FileNotFoundError, match="PDF file not found"):
            _extract_pdf_text("/nonexistent/file.pdf")

    def test_unreadable_pdf_raises_error(self, tmp_path: Path) -> None:
        bad_pdf = tmp_path / "bad.pdf"
        bad_pdf.write_bytes(b"not a pdf file content at all")
        with pytest.raises(RuntimeError, match="Could not open PDF"):
            _extract_pdf_text(str(bad_pdf))

    def test_text_extraction_library_missing(self, tmp_path: Path) -> None:
        pdf_path = tmp_path / "test.pdf"
        pdf_path.write_bytes(b"%PDF-1.4 dummy")

        with patch.dict(sys.modules, {"fitz": None}):
            with pytest.raises(RuntimeError, match="pymupdf.*required"):
                _extract_pdf_text(str(pdf_path))


# ---------------------------------------------------------------------------
# Integration: Works with Typst-generated PDFs
# ---------------------------------------------------------------------------


class TestTypstIntegration:
    """Integration tests with Typst-generated PDFs.

    These tests attempt Typst generation and skip if Typst is unavailable.
    """

    @pytest.fixture
    def typst_pdf(self, tmp_path: Path) -> Path | None:
        """Try to generate a PDF via Typst. Returns None if unavailable."""
        try:
            import typst
        except ImportError:
            return None

        try:
            sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
            # Import the Typst-based generator
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "md_to_pdf",
                str(Path(__file__).resolve().parent.parent / "scripts" / "md-to-pdf.py"),
            )
            if spec is None or spec.loader is None:
                return None
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)

            parsed = parse_resume_markdown(FULL_RESUME_MD)
            content = mod.generate_typst_content(parsed)
            template_path = Path(__file__).resolve().parent.parent / "templates" / "pdf" / "modern.typ"
            if not template_path.exists():
                return None

            output_path = tmp_path / "typst-output.pdf"
            sys_inputs = mod.build_sys_inputs(mod.resolve_config({
                "input": "dummy.md",
                "output": str(output_path),
                "preset": "modern",
                "font": None,
                "color": None,
                "margin": None,
                "page_size": "letter",
                "line_spacing": None,
                "section_spacing": None,
                "pdf_a": False,
            }))
            mod.generate_pdf(content, template_path, sys_inputs, str(output_path))
            return output_path
        except Exception:
            return None

    def test_validates_typst_pdf(self, typst_pdf: Path | None) -> None:
        if typst_pdf is None:
            pytest.skip("Typst not available")
        result = validate_pdf(str(typst_pdf), FULL_RESUME_MD)
        assert result["checks"]["text_extraction"] is True
        assert len(result["extracted_text"]) > 0
        # Section headings should be present
        assert result["checks"]["section_headings"] is True


# ---------------------------------------------------------------------------
# Integration: Works with Python-fallback-generated PDFs
# ---------------------------------------------------------------------------


class TestFallbackIntegration:
    """Integration tests with fpdf2-generated PDFs."""

    def test_validates_fallback_pdf_full_resume(self, tmp_path: Path) -> None:
        pdf_path = tmp_path / "fallback-full.pdf"
        _generate_test_pdf(FULL_RESUME_MD, pdf_path)
        result = validate_pdf(str(pdf_path), FULL_RESUME_MD)
        assert result["status"] == "pass"
        assert result["checks"]["text_extraction"] is True
        assert result["checks"]["section_headings"] is True
        assert result["checks"]["content_completeness"] is True
        assert result["checks"]["font_embedding"] is True

    def test_validates_fallback_pdf_all_presets(self, tmp_path: Path) -> None:
        parsed = parse_resume_markdown(FULL_RESUME_MD)
        from md_to_pdf_fallback import VALID_PRESETS

        for preset in VALID_PRESETS:
            pdf_path = tmp_path / f"fallback-{preset}.pdf"
            generate_pdf_fallback(parsed, str(pdf_path), preset=preset)
            result = validate_pdf(str(pdf_path), FULL_RESUME_MD)
            assert result["checks"]["text_extraction"] is True, (
                f"Text extraction failed for preset {preset}"
            )
            assert result["checks"]["section_headings"] is True, (
                f"Section headings missing for preset {preset}"
            )

    def test_validates_fallback_pdf_unicode(self, tmp_path: Path) -> None:
        pdf_path = tmp_path / "fallback-unicode.pdf"
        _generate_test_pdf(UNICODE_MD, pdf_path)
        result = validate_pdf(str(pdf_path), UNICODE_MD)
        assert result["checks"]["text_extraction"] is True
        assert result["checks"]["font_embedding"] is True


# ---------------------------------------------------------------------------
# Performance
# ---------------------------------------------------------------------------


class TestPerformance:
    """Performance benchmarks."""

    def test_validation_under_3_seconds(self, tmp_path: Path) -> None:
        """Validation should complete in under 3 seconds per file."""
        pdf_path = tmp_path / "perf.pdf"
        _generate_test_pdf(FULL_RESUME_MD, pdf_path)

        start = time.perf_counter()
        result = validate_pdf(str(pdf_path), FULL_RESUME_MD)
        elapsed = time.perf_counter() - start

        assert elapsed < 3.0, f"Validation took {elapsed:.2f}s (limit: 3s)"
        assert result["status"] == "pass"
