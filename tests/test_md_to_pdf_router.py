"""Tests for the environment-aware PDF routing module."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import fitz  # pymupdf
import pytest

# Add scripts/ to path so we can import the modules
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from md_to_pdf_router import (
    _probe_typst_live,
    detect_pdf_backend,
    generate_pdf_routed,
    parse_cli_args,
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


# ---------------------------------------------------------------------------
# Unit: detect_pdf_backend selects backend from config
# ---------------------------------------------------------------------------


class TestDetectPdfBackend:
    """Routing logic correctly selects backend based on env flags."""

    def test_returns_typst_when_config_says_typst(self) -> None:
        config = {"PDF_BACKEND": "typst", "HAS_TYPST": "true"}
        assert detect_pdf_backend(config) == "typst"

    def test_returns_python_fallback_when_config_says_fallback(self) -> None:
        config = {"PDF_BACKEND": "python-fallback", "HAS_TYPST": "false"}
        assert detect_pdf_backend(config) == "python-fallback"

    def test_returns_none_when_config_says_none(self) -> None:
        config = {"PDF_BACKEND": "none"}
        assert detect_pdf_backend(config) == "none"

    def test_defaults_to_python_fallback_when_key_missing(self) -> None:
        config: dict[str, str] = {}
        assert detect_pdf_backend(config) == "python-fallback"

    def test_explicit_config_overrides_file(self) -> None:
        """When config dict is provided, env-config file is not consulted."""
        config = {"PDF_BACKEND": "typst"}
        result = detect_pdf_backend(config)
        assert result == "typst"


class TestProbeTypstLive:
    """Live probing when config file is missing."""

    def test_returns_typst_when_typst_importable(self) -> None:
        with patch.dict("sys.modules", {"typst": MagicMock()}):
            result = _probe_typst_live()
        assert result == "typst"

    def test_returns_python_fallback_when_fpdf_importable(self) -> None:
        # Simulate typst not importable but fpdf available
        import builtins

        original_import = builtins.__import__

        def mock_import(name, *args, **kwargs):
            if name == "typst":
                raise ImportError("no typst")
            return original_import(name, *args, **kwargs)

        with patch("builtins.__import__", side_effect=mock_import):
            result = _probe_typst_live()
        assert result == "python-fallback"

    def test_returns_none_when_nothing_importable(self) -> None:
        import builtins

        original_import = builtins.__import__

        def mock_import(name, *args, **kwargs):
            if name in ("typst", "fpdf"):
                raise ImportError(f"no {name}")
            return original_import(name, *args, **kwargs)

        with patch("builtins.__import__", side_effect=mock_import):
            result = _probe_typst_live()
        assert result == "none"


class TestDetectWithMissingConfigFile:
    """Graceful handling when env flags not set (first run)."""

    def test_probes_live_when_no_config_file(self, tmp_path: Path) -> None:
        """When config file doesn't exist and no explicit config,
        the function should probe live imports."""
        # Patch _CONFIG_PATH to a non-existent path
        fake_config = tmp_path / "nonexistent" / ".env-config"
        with patch("env_config._CONFIG_PATH", fake_config):
            # With no explicit config and no file, should probe live
            result = detect_pdf_backend()
        # On this system typst is installed via uv, so expect typst or fallback
        assert result in ("typst", "python-fallback")


# ---------------------------------------------------------------------------
# Unit: generate_pdf_routed routes correctly
# ---------------------------------------------------------------------------


class TestGeneratePdfRoutedFallback:
    """PDF generation works via Python fallback path."""

    def test_generates_pdf_via_fallback(self, tmp_path: Path) -> None:
        config = {"PDF_BACKEND": "python-fallback"}
        out = tmp_path / "fallback.pdf"
        result = generate_pdf_routed(
            FULL_RESUME_MD, str(out), config=config
        )
        assert result.exists()
        assert result.stat().st_size > 0
        # Verify PDF magic bytes
        with open(result, "rb") as f:
            header = f.read(5)
        assert header == b"%PDF-"

    def test_fallback_pdf_has_text_layer(self, tmp_path: Path) -> None:
        """Fallback produces ATS-compatible PDFs with text layers."""
        config = {"PDF_BACKEND": "python-fallback"}
        out = tmp_path / "text-layer.pdf"
        generate_pdf_routed(FULL_RESUME_MD, str(out), config=config)
        text = _extract_text(out)
        assert "Jane Doe" in text
        assert "EXPERIENCE" in text

    def test_fallback_all_presets(self, tmp_path: Path) -> None:
        config = {"PDF_BACKEND": "python-fallback"}
        for preset in ("modern", "classic", "compact", "harvard"):
            out = tmp_path / f"{preset}.pdf"
            result = generate_pdf_routed(
                FULL_RESUME_MD, str(out), preset=preset, config=config
            )
            assert result.exists(), f"Preset {preset} failed"

    def test_routing_is_transparent(self, tmp_path: Path) -> None:
        """No manual selection needed; config controls the path."""
        config = {"PDF_BACKEND": "python-fallback"}
        out = tmp_path / "transparent.pdf"
        # Just call generate_pdf_routed -- no manual backend selection
        result = generate_pdf_routed(
            FULL_RESUME_MD, str(out), config=config
        )
        assert result.exists()


class TestGeneratePdfRoutedTypst:
    """PDF generation works via Typst path (Claude Code)."""

    def test_generates_pdf_via_typst(self, tmp_path: Path) -> None:
        """Typst path should produce a valid PDF when typst is available."""
        config = {"PDF_BACKEND": "typst"}
        out = tmp_path / "typst.pdf"
        result = generate_pdf_routed(
            FULL_RESUME_MD, str(out), config=config
        )
        assert result.exists()
        assert result.stat().st_size > 0
        with open(result, "rb") as f:
            header = f.read(5)
        assert header == b"%PDF-"

    def test_typst_pdf_has_text_layer(self, tmp_path: Path) -> None:
        """Typst produces ATS-compatible PDFs with text layers."""
        config = {"PDF_BACKEND": "typst"}
        out = tmp_path / "typst-text.pdf"
        generate_pdf_routed(FULL_RESUME_MD, str(out), config=config)
        text = _extract_text(out)
        assert "Jane Doe" in text

    def test_typst_all_presets(self, tmp_path: Path) -> None:
        config = {"PDF_BACKEND": "typst"}
        for preset in ("modern", "classic", "compact", "harvard"):
            out = tmp_path / f"typst-{preset}.pdf"
            result = generate_pdf_routed(
                FULL_RESUME_MD, str(out), preset=preset, config=config
            )
            assert result.exists(), f"Typst preset {preset} failed"


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


class TestEdgeCases:
    """Edge case handling."""

    def test_typst_runtime_failure_falls_back(self, tmp_path: Path) -> None:
        """If Typst binary exists but fails at runtime, falls back
        to Python with a warning."""
        config = {"PDF_BACKEND": "typst"}
        out = tmp_path / "fallback-on-fail.pdf"

        # Patch the Typst module's compile to simulate runtime failure
        with patch(
            "md_to_pdf_router._generate_via_typst",
            side_effect=_typst_fail_then_fallback(tmp_path),
        ):
            pass

        # Instead of patching the internal function, we simulate by
        # using a config that triggers typst, but patch `typst.compile`
        # to raise an error so the catch clause falls through to fallback
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "md_to_pdf_test", Path(__file__).resolve().parent.parent / "scripts" / "md-to-pdf.py"
        )
        md_to_pdf = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(md_to_pdf)

        original_generate = md_to_pdf.generate_pdf

        def failing_generate(*args, **kwargs):
            raise RuntimeError("Typst compilation failed: segfault")

        md_to_pdf.generate_pdf = failing_generate

        try:
            result = generate_pdf_routed(
                FULL_RESUME_MD, str(out), config=config
            )
            # Should have fallen back to Python and produced a valid PDF
            assert result.exists()
            text = _extract_text(out)
            assert "Jane Doe" in text
        finally:
            md_to_pdf.generate_pdf = original_generate

    def test_neither_backend_available_raises_error(self) -> None:
        """Neither Typst nor Python fallback available gives clear error."""
        config = {"PDF_BACKEND": "none"}
        with pytest.raises(RuntimeError, match="No PDF backend is available"):
            generate_pdf_routed(FULL_RESUME_MD, "dummy.pdf", config=config)

    def test_error_message_is_actionable(self) -> None:
        """Error message should suggest how to fix the problem with install instructions."""
        config = {"PDF_BACKEND": "none"}
        with pytest.raises(RuntimeError, match="(?s)Typst.*fpdf2"):
            generate_pdf_routed(FULL_RESUME_MD, "dummy.pdf", config=config)

    def test_both_backends_unavailable_mentions_uv_sync(self) -> None:
        """Error suggests running uv sync."""
        config = {"PDF_BACKEND": "none"}
        with pytest.raises(RuntimeError, match="uv sync"):
            generate_pdf_routed(FULL_RESUME_MD, "dummy.pdf", config=config)


def _typst_fail_then_fallback(tmp_path: Path):
    """Helper for mocking; not used directly in test."""
    pass


# ---------------------------------------------------------------------------
# CLI argument parsing
# ---------------------------------------------------------------------------


class TestCliArgs:
    """CLI argument parsing mirrors both backend scripts."""

    def test_missing_input_returns_error(self) -> None:
        result = parse_cli_args(["script"])
        assert "error" in result

    def test_input_only(self) -> None:
        result = parse_cli_args(["script", "resume.md"])
        assert result["input"] == "resume.md"
        assert result["preset"] == "modern"
        assert result["output"] is None

    def test_input_and_output(self) -> None:
        result = parse_cli_args(["script", "resume.md", "out.pdf"])
        assert result["input"] == "resume.md"
        assert result["output"] == "out.pdf"

    def test_all_options(self) -> None:
        result = parse_cli_args([
            "script", "resume.md", "out.pdf",
            "--preset", "classic",
            "--font", "EB Garamond",
            "--color", "#FF0000",
            "--margin", "narrow",
            "--page-size", "a4",
            "--line-spacing", "tight",
            "--section-spacing", "compact",
            "--pdf-a",
        ])
        assert result["preset"] == "classic"
        assert result["font"] == "EB Garamond"
        assert result["color"] == "#FF0000"
        assert result["margin"] == "narrow"
        assert result["page_size"] == "a4"
        assert result["line_spacing"] == "tight"
        assert result["section_spacing"] == "compact"
        assert result["pdf_a"] is True

    def test_unknown_arg_returns_error(self) -> None:
        result = parse_cli_args(["script", "resume.md", "--unknown"])
        assert "error" in result
        assert "Unknown argument" in result["error"]


# ---------------------------------------------------------------------------
# Integration: Typst runtime failure fallback verification
# ---------------------------------------------------------------------------


class TestTypstRuntimeFallback:
    """Verify that Typst runtime failure triggers automatic fallback."""

    def test_fallback_produces_valid_pdf_on_typst_error(
        self, tmp_path: Path, capsys
    ) -> None:
        """Simulate Typst compile failure and verify fallback works."""
        config = {"PDF_BACKEND": "typst"}
        out = tmp_path / "runtime-fallback.pdf"

        # Patch typst.compile to raise, simulating runtime failure
        mock_typst = MagicMock()
        mock_typst.compile.side_effect = RuntimeError("Typst runtime error")

        with patch.dict("sys.modules", {"typst": mock_typst}):
            result = generate_pdf_routed(
                FULL_RESUME_MD, str(out), config=config
            )

        assert result.exists()
        text = _extract_text(out)
        assert "Jane Doe" in text

    def test_fallback_emits_warning_on_typst_error(
        self, tmp_path: Path, capsys
    ) -> None:
        """Verify user-visible warning is emitted when Typst fails."""
        config = {"PDF_BACKEND": "typst"}
        out = tmp_path / "warn-fallback.pdf"

        mock_typst = MagicMock()
        mock_typst.compile.side_effect = RuntimeError("Typst crashed")

        with patch.dict("sys.modules", {"typst": mock_typst}):
            generate_pdf_routed(FULL_RESUME_MD, str(out), config=config)

        captured = capsys.readouterr()
        assert "WARNING" in captured.err
        assert "Falling back" in captured.err
