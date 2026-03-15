# Codebase Changes Report

## Metadata

| Field | Value |
|-------|-------|
| **Date** | 2026-03-14 |
| **Time** | 22:48 EDT |
| **Branch** | main |
| **Author** | Stephen Sequenzia |
| **Base Commit** | 481f973 |
| **Latest Commit** | uncommitted |
| **Repository** | git@github.com:applied-theta/resume-agent.git |

**Scope**: Cowork Exports — Dual-format resume export with environment-aware backends

**Summary**: Implemented the complete cowork-exports feature adding dual-format export (PDF + DOCX) with environment-aware backend selection, ATS validation, 8 presets across formats, custom template support, and comprehensive edge case handling. The plugin now works in both Claude Code (Typst) and Claude Cowork VM (fpdf2 fallback) environments.

## Overview

This session executed 17 spec-generated tasks across 6 dependency-ordered waves, producing the entire export pipeline from shared parser through rendering, validation, and integration. All tasks passed on first attempt with no retries needed.

- **Files affected**: 28
- **Lines added**: +9,103
- **Lines removed**: -671
- **Commits**: 0 (all changes uncommitted)

## Files Changed

| File | Status | Lines | Description |
|------|--------|-------|-------------|
| `scripts/parse_resume.py` | Added | +228 | Shared resume markdown parser module (importable + CLI) |
| `scripts/md-to-docx.py` | Added | +724 | DOCX renderer with preset and custom template support |
| `scripts/md_to_pdf_fallback.py` | Added | +893 | Python PDF fallback renderer using fpdf2 with 4 presets |
| `scripts/md_to_pdf_router.py` | Added | +444 | Environment-aware PDF backend auto-routing |
| `scripts/validate_pdf.py` | Added | +361 | Post-export PDF ATS validation with garbled text detection |
| `scripts/validate_docx.py` | Added | +325 | Post-export DOCX ATS validation |
| `scripts/export_edge_cases.py` | Added | +417 | Centralized edge case handling utilities |
| `scripts/env_config.py` | Added | +111 | Environment config helper for reading detection results |
| `scripts/build-word-templates.py` | Added | +370 | Generates 4 bundled Word preset template files |
| `skills/export-resume/SKILL.md` | Added | +400 | Unified export skill replacing export-pdf |
| `templates/word/professional.docx` | Added | binary | Calibri, Navy (#2B547E), corporate roles preset |
| `templates/word/simple.docx` | Added | binary | Arial, Black (#000000), ATS-compatible preset |
| `templates/word/creative.docx` | Added | binary | Georgia, Teal (#008080), creative roles preset |
| `templates/word/academic.docx` | Added | binary | Times New Roman, Dark Gray (#333333), academic preset |
| `tests/__init__.py` | Added | +0 | Test package init |
| `tests/test_parse_resume.py` | Added | +439 | 32 unit tests for shared parser |
| `tests/test_md_to_docx.py` | Added | +963 | 127 tests for DOCX renderer |
| `tests/test_md_to_pdf_fallback.py` | Added | +841 | 90 tests for PDF fallback renderer |
| `tests/test_md_to_pdf_router.py` | Added | +416 | 27 tests for PDF routing logic |
| `tests/test_validate_pdf.py` | Added | +545 | 35 tests for PDF ATS validation |
| `tests/test_validate_docx.py` | Added | +491 | 29 tests for DOCX ATS validation |
| `tests/test_export_edge_cases.py` | Added | +614 | 45 tests for edge case handling |
| `CLAUDE.md` | Modified | +48 / -3 | Updated with new export architecture documentation |
| `hooks/setup-deps.sh` | Modified | +228 / -1 | Added environment detection, dependency fallback, config generation |
| `pyproject.toml` | Modified | +7 / -0 | Added python-docx, fpdf2, pytest dependencies |
| `scripts/md-to-pdf.py` | Modified | +1 / -121 | Refactored to import from shared parser module |
| `skills/export-pdf/SKILL.md` | Deleted | -169 | Replaced by unified export-resume skill |
| `uv.lock` | Modified | +377 / -242 | Updated lockfile for new dependencies |

## Change Details

### Added

- **`scripts/parse_resume.py`** — Shared resume markdown parser extracted from md-to-pdf.py. Produces structured data (sections, headings, contact info, bullets) consumed by all renderers. Importable module with CLI entry point.

- **`scripts/md-to-docx.py`** — DOCX renderer consuming shared parser output. Maps markdown to Word elements (H1→name, H2→sections, H3→subsections, bullets, tables). Supports 4 bundled presets and user-provided custom templates with validation and fallback.

- **`scripts/md_to_pdf_fallback.py`** — Pure Python PDF renderer using fpdf2 for Cowork VM environments where Typst is unavailable. Supports 4 presets (modern, classic, compact, harvard) with full customization (fonts, accent colors, margins, page size, spacing). TTF font embedding from bundled fonts directory.

- **`scripts/md_to_pdf_router.py`** — Environment-aware router that auto-selects between Typst and fpdf2 backends based on `workspace/.env-config` detection results. Handles runtime Typst failures with automatic fallback.

- **`scripts/validate_pdf.py`** — Post-export PDF ATS validation. Extracts text via pymupdf, verifies heading preservation, checks for dropped content, and detects garbled text (font embedding issues) using multiple heuristics.

- **`scripts/validate_docx.py`** — Post-export DOCX ATS validation. Extracts text from both paragraphs and tables, verifies section headings, checks for dropped content with normalized comparison.

- **`scripts/export_edge_cases.py`** — Centralized edge case utilities providing consistent error messaging across the export pipeline: source file validation, output size checks (25MB warn, 30MB limit), page count warnings, dependency availability checks, and template validation.

- **`scripts/env_config.py`** — Python helper for reading environment detection config (`workspace/.env-config`). Provides `has_typst()`, `pdf_backend()`, `has_uv()`, `has_python_docx()`, `has_pdf_fallback()`, `fonts_dir()`, `fonts_accessible()`.

- **`scripts/build-word-templates.py`** — Build script that programmatically generates the 4 Word preset templates using python-docx. Configures heading styles, body text, list styles, table styles, and page margins per preset spec.

- **`skills/export-resume/SKILL.md`** — Unified export skill replacing export-pdf. Supports format selection (PDF/DOCX), preset selection, custom templates, environment-aware backend routing, automatic ATS validation, and comprehensive error handling.

- **`templates/word/*.docx`** — Four bundled Word preset templates (Professional, Simple, Creative, Academic) with correctly configured heading styles, body text, list styles, and table styles.

- **`tests/`** — Complete test suite with 385 tests across 7 test files covering parser, DOCX renderer, PDF fallback, PDF routing, PDF validation, DOCX validation, and edge case handling.

### Modified

- **`CLAUDE.md`** — Updated project overview, dependencies, architecture documentation with new Export Architecture section, expanded scripts table (9 new entries), updated hooks description, added templates/word to reference data, added environment awareness design principle.

- **`hooks/setup-deps.sh`** — Transformed from simple `uv sync` to comprehensive environment detection: checks for uv/pip/typst availability, installs dependencies via detected package manager, validates font directory, writes detection results to `workspace/.env-config`. Bash 3.2 compatible.

- **`pyproject.toml`** — Added `python-docx` and `fpdf2` to main dependencies, added `pytest` to dev dependency group.

- **`scripts/md-to-pdf.py`** — Refactored to import `parse_resume_markdown` from shared `parse_resume` module instead of inline parsing. Removed 120 lines of duplicated parser code.

- **`uv.lock`** — Updated lockfile reflecting new python-docx, fpdf2, and pytest dependencies with all transitive dependencies (lxml, typing-extensions, fonttools, pillow, defusedxml).

### Deleted

- **`skills/export-pdf/SKILL.md`** — Replaced by the unified `export-resume` skill that supports both PDF and DOCX formats.

## Git Status

### Unstaged Changes

| File | Status |
|------|--------|
| `CLAUDE.md` | Modified |
| `hooks/setup-deps.sh` | Modified |
| `pyproject.toml` | Modified |
| `scripts/md-to-pdf.py` | Modified |
| `skills/export-pdf/SKILL.md` | Deleted |
| `uv.lock` | Modified |

### Untracked Files

| File | Description |
|------|-------------|
| `scripts/build-word-templates.py` | Word template generator |
| `scripts/env_config.py` | Environment config helper |
| `scripts/export_edge_cases.py` | Edge case utilities |
| `scripts/md-to-docx.py` | DOCX renderer |
| `scripts/md_to_pdf_fallback.py` | PDF fallback renderer |
| `scripts/md_to_pdf_router.py` | PDF routing module |
| `scripts/parse_resume.py` | Shared parser |
| `scripts/validate_docx.py` | DOCX validator |
| `scripts/validate_pdf.py` | PDF validator |
| `skills/export-resume/` | Unified export skill |
| `templates/word/` | Word preset templates |
| `tests/` | Test suite |

## Session Commits

No commits in this session. All changes are uncommitted.
