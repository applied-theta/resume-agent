"""Tests for the shared resume markdown parser module."""

import sys
from pathlib import Path

import pytest

# Add scripts/ to path so we can import parse_resume
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from parse_resume import parse_resume_markdown


# ---------------------------------------------------------------------------
# Sample resume markdown fixtures
# ---------------------------------------------------------------------------

FULL_RESUME = """\
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

MINIMAL_RESUME = """\
# John Smith

john@example.com

## Experience

### Developer

**SomeCo** | 2020 - Present

- Wrote code
"""

NO_H1_RESUME = """\
## Summary

A summary without a name heading.

## Experience

### Role

**Company** | 2020 - Present

- Did things
"""

EMPTY_SECTIONS_RESUME = """\
# Test Person

## Summary

## Experience

## Education

## Skills
"""


class TestParseResumeMarkdownBasic:
    """Basic parsing of well-formed resume markdown."""

    def test_parses_name_from_h1(self) -> None:
        result = parse_resume_markdown(FULL_RESUME)
        assert result["name"] == "Jane Doe"

    def test_parses_contact_lines(self) -> None:
        result = parse_resume_markdown(FULL_RESUME)
        assert len(result["contact_lines"]) == 1
        assert "jane.doe@email.com" in result["contact_lines"][0]
        assert "linkedin.com/in/janedoe" in result["contact_lines"][0]

    def test_parses_h2_sections(self) -> None:
        result = parse_resume_markdown(FULL_RESUME)
        h2_sections = [s for s in result["sections"] if s["level"] == 2]
        headings = [s["heading"] for s in h2_sections]
        assert "Summary" in headings
        assert "Experience" in headings
        assert "Education" in headings
        assert "Skills" in headings

    def test_parses_h3_subsections(self) -> None:
        result = parse_resume_markdown(FULL_RESUME)
        h3_sections = [s for s in result["sections"] if s["level"] == 3]
        headings = [s["heading"] for s in h3_sections]
        assert "Senior Software Engineer" in headings
        assert "Software Engineer" in headings
        assert "Master of Science in Computer Science" in headings
        assert "Bachelor of Science in Mathematics" in headings

    def test_parses_meta_lines(self) -> None:
        result = parse_resume_markdown(FULL_RESUME)
        senior_section = next(
            s for s in result["sections"] if s["heading"] == "Senior Software Engineer"
        )
        assert senior_section["meta_line"] is not None
        assert "Acme Corp" in senior_section["meta_line"]
        assert "Jan 2020 - Present" in senior_section["meta_line"]

    def test_parses_bullet_content(self) -> None:
        result = parse_resume_markdown(FULL_RESUME)
        senior_section = next(
            s for s in result["sections"] if s["heading"] == "Senior Software Engineer"
        )
        content_text = "\n".join(senior_section["content"])
        assert "Led a team" in content_text
        assert "Reduced deployment time" in content_text
        assert "Mentored 3 junior engineers" in content_text

    def test_preserves_bold_in_bullets(self) -> None:
        result = parse_resume_markdown(FULL_RESUME)
        senior_section = next(
            s for s in result["sections"] if s["heading"] == "Senior Software Engineer"
        )
        content_text = "\n".join(senior_section["content"])
        assert "**40%**" in content_text

    def test_preserves_italic_in_bullets(self) -> None:
        result = parse_resume_markdown(FULL_RESUME)
        eng_section = next(
            s for s in result["sections"] if s["heading"] == "Software Engineer"
        )
        content_text = "\n".join(eng_section["content"])
        assert "*real-time*" in content_text

    def test_skills_section_has_content(self) -> None:
        result = parse_resume_markdown(FULL_RESUME)
        skills_section = next(
            s for s in result["sections"] if s["heading"] == "Skills"
        )
        content_lines = [l for l in skills_section["content"] if l.strip()]
        assert len(content_lines) >= 3

    def test_no_warnings_for_complete_resume(self) -> None:
        result = parse_resume_markdown(FULL_RESUME)
        assert result["warnings"] == []

    def test_returns_all_expected_keys(self) -> None:
        result = parse_resume_markdown(FULL_RESUME)
        assert "name" in result
        assert "contact_lines" in result
        assert "sections" in result
        assert "warnings" in result

    def test_section_dict_structure(self) -> None:
        result = parse_resume_markdown(FULL_RESUME)
        for section in result["sections"]:
            assert "heading" in section
            assert "level" in section
            assert "meta_line" in section
            assert "content" in section
            assert section["level"] in (2, 3)


class TestParseResumeMarkdownEdgeCases:
    """Edge case handling in the parser."""

    def test_no_h1_heading(self) -> None:
        result = parse_resume_markdown(NO_H1_RESUME)
        assert result["name"] == ""
        assert any("Missing H1" in w for w in result["warnings"])

    def test_no_h1_still_parses_sections(self) -> None:
        result = parse_resume_markdown(NO_H1_RESUME)
        h2_headings = [s["heading"] for s in result["sections"] if s["level"] == 2]
        assert "Summary" in h2_headings
        assert "Experience" in h2_headings

    def test_empty_sections(self) -> None:
        result = parse_resume_markdown(EMPTY_SECTIONS_RESUME)
        assert result["name"] == "Test Person"
        for section in result["sections"]:
            # Empty sections should have no non-blank content
            non_blank = [l for l in section["content"] if l.strip()]
            assert len(non_blank) == 0

    def test_minimal_resume(self) -> None:
        result = parse_resume_markdown(MINIMAL_RESUME)
        assert result["name"] == "John Smith"
        assert len(result["contact_lines"]) == 1
        assert "john@example.com" in result["contact_lines"][0]

    def test_preserves_whitespace_in_content(self) -> None:
        md = """\
# Name

## Summary

   Indented text here
   More indented text

## Experience

## Education

## Skills
"""
        result = parse_resume_markdown(md)
        summary = next(s for s in result["sections"] if s["heading"] == "Summary")
        # Content lines should preserve original line text (including indentation)
        indented_lines = [l for l in summary["content"] if "Indented" in l]
        assert len(indented_lines) > 0
        assert indented_lines[0].startswith("   ")

    def test_missing_expected_sections_generates_warnings(self) -> None:
        md = """\
# Name

## Random Section

Some content
"""
        result = parse_resume_markdown(md)
        assert any("Missing expected section: summary" in w for w in result["warnings"])
        assert any("Missing expected section: experience" in w for w in result["warnings"])
        assert any("Missing expected section: education" in w for w in result["warnings"])
        assert any("Missing expected section: skills" in w for w in result["warnings"])

    def test_multiple_contact_lines(self) -> None:
        md = """\
# Name

email@test.com | phone
linkedin.com/in/user

## Summary

Text

## Experience

## Education

## Skills
"""
        result = parse_resume_markdown(md)
        assert len(result["contact_lines"]) == 2

    def test_resume_with_links_in_bullets(self) -> None:
        md = """\
# Name

## Summary

Intro text.

## Experience

### Role

**Company** | 2020 - Present

- Check out [my project](https://example.com) for details

## Education

## Skills
"""
        result = parse_resume_markdown(md)
        role_section = next(s for s in result["sections"] if s["heading"] == "Role")
        content_text = "\n".join(role_section["content"])
        assert "[my project](https://example.com)" in content_text

    def test_resume_with_table(self) -> None:
        md = """\
# Name

## Summary

Summary text.

## Experience

## Education

## Skills

| Category | Skills |
|----------|--------|
| Languages | Python, Go |
| Cloud | AWS, GCP |
"""
        result = parse_resume_markdown(md)
        skills_section = next(s for s in result["sections"] if s["heading"] == "Skills")
        content_text = "\n".join(skills_section["content"])
        assert "Languages" in content_text
        assert "Python, Go" in content_text

    def test_h3_with_no_meta_line(self) -> None:
        md = """\
# Name

## Experience

### Some Role

- Just bullets, no meta line

## Summary

## Education

## Skills
"""
        result = parse_resume_markdown(md)
        role = next(s for s in result["sections"] if s["heading"] == "Some Role")
        assert role["meta_line"] is None

    def test_only_whitespace_lines_between_sections(self) -> None:
        md = """\
# Name



## Summary



Some text



## Experience

## Education

## Skills
"""
        result = parse_resume_markdown(md)
        assert result["name"] == "Name"
        summary = next(s for s in result["sections"] if s["heading"] == "Summary")
        non_blank = [l for l in summary["content"] if l.strip()]
        assert any("Some text" in l for l in non_blank)


class TestParseResumeMarkdownErrorHandling:
    """Error handling for invalid inputs."""

    def test_empty_string_raises_value_error(self) -> None:
        with pytest.raises(ValueError, match="empty"):
            parse_resume_markdown("")

    def test_whitespace_only_raises_value_error(self) -> None:
        with pytest.raises(ValueError, match="empty"):
            parse_resume_markdown("   \n\n  \t  ")

    def test_non_string_raises_value_error(self) -> None:
        with pytest.raises(ValueError, match="Expected markdown string"):
            parse_resume_markdown(123)  # type: ignore[arg-type]

    def test_none_raises_value_error(self) -> None:
        with pytest.raises(ValueError, match="Expected markdown string"):
            parse_resume_markdown(None)  # type: ignore[arg-type]

    def test_plain_text_without_headings(self) -> None:
        result = parse_resume_markdown("Just some plain text without any markdown headings.")
        assert result["name"] == ""
        assert len(result["warnings"]) > 0

    def test_binary_looking_content_parsed_as_text(self) -> None:
        # Non-markdown text should still parse without crashing
        result = parse_resume_markdown("0x00 0xFF binary-like content\nmore stuff\n")
        assert result["name"] == ""
        assert len(result["warnings"]) > 0


class TestParseResumeMarkdownIntegration:
    """Integration tests ensuring md-to-pdf.py can use the shared parser."""

    def test_import_from_parse_resume(self) -> None:
        """Verify the shared module is importable."""
        from parse_resume import parse_resume_markdown as imported_fn
        assert callable(imported_fn)

    def test_parsed_output_usable_by_typst_generator(self) -> None:
        """Verify parsed output has the structure expected by generate_typst_content."""
        result = parse_resume_markdown(FULL_RESUME)

        # Check the dict keys that generate_typst_content accesses
        assert isinstance(result["name"], str)
        assert isinstance(result["contact_lines"], list)
        assert isinstance(result["sections"], list)

        for section in result["sections"]:
            assert isinstance(section["heading"], str)
            assert isinstance(section["level"], int)
            assert isinstance(section["content"], list)
            # meta_line can be str or None
            assert section["meta_line"] is None or isinstance(section["meta_line"], str)

    def test_md_to_pdf_imports_shared_parser(self) -> None:
        """Verify md-to-pdf.py actually imports from parse_resume module."""
        md_to_pdf_path = Path(__file__).resolve().parent.parent / "scripts" / "md-to-pdf.py"
        source = md_to_pdf_path.read_text()
        assert "from parse_resume import parse_resume_markdown" in source
        # The inline definition should no longer be present
        assert "def parse_resume_markdown" not in source
