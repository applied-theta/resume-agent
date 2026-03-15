"""Tests for the DOCX ATS validation script (validate_docx.py)."""

import sys
import tempfile
from pathlib import Path

import pytest

# Add scripts/ to path so we can import the modules
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from parse_resume import parse_resume_markdown
from validate_docx import extract_docx_text, validate_docx

# Import the renderer via importlib for hyphenated filename
import importlib.util

_spec = importlib.util.spec_from_file_location(
    "md_to_docx",
    str(Path(__file__).resolve().parent.parent / "scripts" / "md-to-docx.py"),
)
md_to_docx = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(md_to_docx)

render_docx = md_to_docx.render_docx

from docx import Document

# ---------------------------------------------------------------------------
# Fixtures and helpers
# ---------------------------------------------------------------------------

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates" / "word"

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

TABLE_RESUME_MD = """\
# Test Person

test@email.com

## Summary

Summary text here.

## Experience

## Education

## Skills

| Category | Skills | Level |
|----------|--------|-------|
| Languages | Python, Go | Expert |
| Cloud | AWS, GCP | Advanced |
| Tools | Docker, K8s | Intermediate |
"""

SHORT_RESUME_MD = """\
# Alex

alex@test.com

## Summary

Short summary.

## Experience

## Education

## Skills
"""


def _generate_docx(markdown: str, preset: str = "professional",
                    template_path: str | None = None) -> str:
    """Generate a DOCX from markdown and return the temp file path."""
    parsed = parse_resume_markdown(markdown)
    doc = render_docx(parsed, preset=preset, template_path=template_path)
    tmp = tempfile.NamedTemporaryFile(suffix=".docx", delete=False)
    doc.save(tmp.name)
    tmp.close()
    return tmp.name


# ---------------------------------------------------------------------------
# Unit Tests: Text Extraction
# ---------------------------------------------------------------------------


class TestExtractDocxText:
    """Test DOCX text extraction."""

    def test_extracts_paragraphs(self) -> None:
        docx_path = _generate_docx(FULL_RESUME_MD)
        try:
            result = extract_docx_text(docx_path)
            assert len(result["paragraphs"]) > 0
            assert "Jane Doe" in result["paragraphs"]
        finally:
            Path(docx_path).unlink()

    def test_extracts_headings(self) -> None:
        docx_path = _generate_docx(FULL_RESUME_MD)
        try:
            result = extract_docx_text(docx_path)
            assert "Summary" in result["headings"]
            assert "Experience" in result["headings"]
            assert "Education" in result["headings"]
            assert "Skills" in result["headings"]
        finally:
            Path(docx_path).unlink()

    def test_extracts_table_texts(self) -> None:
        docx_path = _generate_docx(TABLE_RESUME_MD)
        try:
            result = extract_docx_text(docx_path)
            assert len(result["table_texts"]) > 0
            assert "Python, Go" in result["table_texts"]
            assert "AWS, GCP" in result["table_texts"]
        finally:
            Path(docx_path).unlink()

    def test_full_text_includes_everything(self) -> None:
        docx_path = _generate_docx(FULL_RESUME_MD)
        try:
            result = extract_docx_text(docx_path)
            assert "Jane Doe" in result["full_text"]
            assert "Senior Software Engineer" in result["full_text"]
            assert "Led a team of 5 engineers" in result["full_text"]
        finally:
            Path(docx_path).unlink()

    def test_file_not_found_raises(self) -> None:
        with pytest.raises(FileNotFoundError, match="DOCX file not found"):
            extract_docx_text("/nonexistent/file.docx")

    def test_corrupted_file_raises(self) -> None:
        tmp = tempfile.NamedTemporaryFile(suffix=".docx", delete=False)
        tmp.write(b"not a valid docx file content")
        tmp.close()
        try:
            with pytest.raises(ValueError, match="Cannot open DOCX file"):
                extract_docx_text(tmp.name)
        finally:
            Path(tmp.name).unlink()


# ---------------------------------------------------------------------------
# Unit Tests: Validation - Pass Cases
# ---------------------------------------------------------------------------


class TestValidationPassCases:
    """Test that validation correctly identifies complete content (pass case)."""

    def test_full_resume_passes(self) -> None:
        docx_path = _generate_docx(FULL_RESUME_MD)
        try:
            result = validate_docx(docx_path, FULL_RESUME_MD)
            assert result["passed"] is True
            assert len(result["issues"]) == 0
            assert len(result["missing_sections"]) == 0
            assert len(result["dropped_content"]) == 0
            assert "passed" in result["summary"].lower()
        finally:
            Path(docx_path).unlink()

    def test_table_resume_passes(self) -> None:
        docx_path = _generate_docx(TABLE_RESUME_MD)
        try:
            result = validate_docx(docx_path, TABLE_RESUME_MD)
            assert result["passed"] is True
            assert len(result["missing_sections"]) == 0
        finally:
            Path(docx_path).unlink()

    def test_short_resume_passes(self) -> None:
        docx_path = _generate_docx(SHORT_RESUME_MD)
        try:
            result = validate_docx(docx_path, SHORT_RESUME_MD)
            assert result["passed"] is True
        finally:
            Path(docx_path).unlink()

    def test_returns_structured_result(self) -> None:
        docx_path = _generate_docx(FULL_RESUME_MD)
        try:
            result = validate_docx(docx_path, FULL_RESUME_MD)
            assert "passed" in result
            assert "issues" in result
            assert "missing_sections" in result
            assert "dropped_content" in result
            assert "summary" in result
            assert isinstance(result["passed"], bool)
            assert isinstance(result["issues"], list)
            assert isinstance(result["missing_sections"], list)
            assert isinstance(result["dropped_content"], list)
            assert isinstance(result["summary"], str)
        finally:
            Path(docx_path).unlink()


# ---------------------------------------------------------------------------
# Unit Tests: Validation - Fail Cases
# ---------------------------------------------------------------------------


class TestValidationFailCases:
    """Test that validation correctly identifies missing sections (fail case)."""

    def test_missing_section_detected(self) -> None:
        # Create a DOCX from a subset of content, but validate against full markdown
        partial_md = """\
# Jane Doe

## Summary

A summary.

## Experience

## Education

## Skills
"""
        docx_path = _generate_docx(partial_md)
        try:
            # Validate against the full resume (which has more sections)
            result = validate_docx(docx_path, FULL_RESUME_MD)
            assert result["passed"] is False
            assert len(result["missing_sections"]) > 0 or len(result["dropped_content"]) > 0
            assert len(result["issues"]) > 0
        finally:
            Path(docx_path).unlink()

    def test_reports_specific_missing_sections(self) -> None:
        # Create minimal DOCX without subheadings
        minimal_md = """\
# Jane Doe

## Summary

A summary.

## Experience

## Education

## Skills
"""
        docx_path = _generate_docx(minimal_md)
        try:
            result = validate_docx(docx_path, FULL_RESUME_MD)
            assert result["passed"] is False
            # Should report specific missing H3 headings
            missing = result["missing_sections"]
            missing_lower = [m.lower() for m in missing]
            assert any("senior software engineer" in m for m in missing_lower)
        finally:
            Path(docx_path).unlink()

    def test_reports_dropped_content(self) -> None:
        # Create DOCX from minimal version, validate against full
        minimal_md = """\
# Jane Doe

## Summary

A summary.

## Experience

### Senior Software Engineer

**Acme Corp**, San Francisco, CA | Jan 2020 - Present

## Education

## Skills
"""
        docx_path = _generate_docx(minimal_md)
        try:
            result = validate_docx(docx_path, FULL_RESUME_MD)
            assert result["passed"] is False
            # Should detect dropped bullet content from Experience section
            assert len(result["dropped_content"]) > 0 or len(result["missing_sections"]) > 0
        finally:
            Path(docx_path).unlink()

    def test_fail_summary_includes_counts(self) -> None:
        minimal_md = """\
# Jane Doe

## Summary

A summary.

## Experience

## Education

## Skills
"""
        docx_path = _generate_docx(minimal_md)
        try:
            result = validate_docx(docx_path, FULL_RESUME_MD)
            assert result["passed"] is False
            assert "failed" in result["summary"].lower()
            assert "issue" in result["summary"].lower()
        finally:
            Path(docx_path).unlink()


# ---------------------------------------------------------------------------
# Unit Tests: Error Handling
# ---------------------------------------------------------------------------


class TestValidationErrorHandling:
    """Test error handling in validation."""

    def test_docx_not_found(self) -> None:
        with pytest.raises(FileNotFoundError, match="DOCX file not found"):
            validate_docx("/nonexistent/resume.docx", FULL_RESUME_MD)

    def test_corrupted_docx(self) -> None:
        tmp = tempfile.NamedTemporaryFile(suffix=".docx", delete=False)
        tmp.write(b"corrupted data here")
        tmp.close()
        try:
            with pytest.raises(ValueError, match="Cannot open DOCX file"):
                validate_docx(tmp.name, FULL_RESUME_MD)
        finally:
            Path(tmp.name).unlink()


# ---------------------------------------------------------------------------
# Integration Tests: Preset-Generated DOCX
# ---------------------------------------------------------------------------


class TestPresetIntegration:
    """Integration: Validation works with preset-generated DOCX."""

    @pytest.mark.parametrize("preset", ["professional", "simple", "creative", "academic"])
    def test_all_presets_pass_validation(self, preset: str) -> None:
        docx_path = _generate_docx(FULL_RESUME_MD, preset=preset)
        try:
            result = validate_docx(docx_path, FULL_RESUME_MD)
            assert result["passed"] is True, (
                f"Preset '{preset}' failed validation: {result['issues']}"
            )
        finally:
            Path(docx_path).unlink()

    @pytest.mark.parametrize("preset", ["professional", "simple", "creative", "academic"])
    def test_table_resume_all_presets(self, preset: str) -> None:
        docx_path = _generate_docx(TABLE_RESUME_MD, preset=preset)
        try:
            result = validate_docx(docx_path, TABLE_RESUME_MD)
            assert result["passed"] is True, (
                f"Preset '{preset}' with tables failed: {result['issues']}"
            )
        finally:
            Path(docx_path).unlink()


# ---------------------------------------------------------------------------
# Integration Tests: Custom-Template-Generated DOCX
# ---------------------------------------------------------------------------


class TestCustomTemplateIntegration:
    """Integration: Validation works with custom-template-generated DOCX."""

    def test_custom_template_passes_validation(self) -> None:
        template_path = str(TEMPLATES_DIR / "simple.docx")
        if not Path(template_path).exists():
            pytest.skip("Simple template not found")

        docx_path = _generate_docx(
            FULL_RESUME_MD, template_path=template_path
        )
        try:
            result = validate_docx(docx_path, FULL_RESUME_MD)
            assert result["passed"] is True, (
                f"Custom template validation failed: {result['issues']}"
            )
        finally:
            Path(docx_path).unlink()

    def test_custom_template_table_content(self) -> None:
        template_path = str(TEMPLATES_DIR / "academic.docx")
        if not Path(template_path).exists():
            pytest.skip("Academic template not found")

        docx_path = _generate_docx(
            TABLE_RESUME_MD, template_path=template_path
        )
        try:
            result = validate_docx(docx_path, TABLE_RESUME_MD)
            assert result["passed"] is True, (
                f"Custom template with tables failed: {result['issues']}"
            )
        finally:
            Path(docx_path).unlink()


# ---------------------------------------------------------------------------
# Edge Cases
# ---------------------------------------------------------------------------


class TestEdgeCases:
    """Test validation edge cases."""

    def test_very_short_resume_validates(self) -> None:
        docx_path = _generate_docx(SHORT_RESUME_MD)
        try:
            result = validate_docx(docx_path, SHORT_RESUME_MD)
            assert result["passed"] is True
        finally:
            Path(docx_path).unlink()

    def test_resume_with_tables_validates_table_content(self) -> None:
        docx_path = _generate_docx(TABLE_RESUME_MD)
        try:
            result = validate_docx(docx_path, TABLE_RESUME_MD)
            assert result["passed"] is True
            # Verify table content was included in extraction
            extracted = extract_docx_text(docx_path)
            assert "Python, Go" in extracted["table_texts"]
        finally:
            Path(docx_path).unlink()

    def test_custom_template_validation_still_works(self) -> None:
        template_path = str(TEMPLATES_DIR / "creative.docx")
        if not Path(template_path).exists():
            pytest.skip("Creative template not found")

        docx_path = _generate_docx(
            FULL_RESUME_MD, template_path=template_path
        )
        try:
            result = validate_docx(docx_path, FULL_RESUME_MD)
            assert result["passed"] is True
        finally:
            Path(docx_path).unlink()
