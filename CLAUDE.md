# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Claude Code plugin for AI-powered resume analysis and optimization. Analyzes resumes across 6 dimensions (ATS compatibility, content quality, keyword alignment, strategic positioning, structure/format, market intelligence) and produces optimized resumes with change tracking and export to PDF and DOCX formats. Works in both Claude Code and Claude Cowork environments.

## Dependencies & Setup

- **Python >= 3.12** with `uv` for package management (falls back to `pip` in Cowork VMs)
- Dependencies: `pymupdf`, `jsonschema`, `typst`, `python-docx`, `fpdf2` (auto-installed via SessionStart hook)
- Dev dependencies: `pytest` (in `[dependency-groups] dev`)
- Run scripts with: `scripts/run-python.sh scripts/<script>.py` (auto-detects `uv` vs `python3`)
- Run tests with: `uv run pytest` (local dev with `uv`; not available on Cowork)

## Architecture

### Plugin Structure

This is a Claude Code plugin (`.claude-plugin/plugin.json`), not a standalone application. It has no build step or entry point — it's invoked through Claude Code's skill/agent system.

### Skills (user-facing commands)

Skills live in `skills/<name>/SKILL.md` and are the user-facing entry points. Each skill has YAML frontmatter (name, description, allowed-tools) and a markdown body with detailed procedural instructions.

| Skill | Role |
|-------|------|
| `analyze-resume` | **Orchestrator** — runs the full 7-step analysis pipeline |
| `optimize-resume` | **Orchestrator** — interview + rewrite + approval workflow |
| `parse-resume` | Delegates to resume-parser agent |
| `ats-check` | Delegates to ats-analyzer agent |
| `content-review` | Delegates to content-analyst agent |
| `keyword-align` | Delegates to keyword-optimizer agent (requires JD) |
| `strategy-review` | Delegates to strategy-advisor agent |
| `skills-research` | Delegates to skills-research agent |
| `export-resume` | Unified export to PDF or DOCX with environment-aware backend selection |

### Agents (subagents)

Agent definitions live in `agents/<name>.md` with YAML frontmatter (name, model, tools, description). They are dispatched by skills, not invoked directly by users.

- **resume-parser** — Extracts structured JSON from PDF/Markdown resumes
- **ats-analyzer** — ATS compatibility scoring with platform simulation (has WebSearch)
- **content-analyst** — Per-bullet scoring and content quality assessment
- **keyword-optimizer** — JD decomposition and keyword gap analysis
- **strategy-advisor** — Career archetype detection and positioning
- **skills-research** — Market demand analysis with web research (has WebSearch, WebFetch)
- **interview-researcher** — Background research during optimization interview (has WebSearch, WebFetch)
- **resume-rewriter** — Produces optimized resume content (pinned to `opus` model)

### Export Architecture

The export system uses a shared parser with dual renderer pattern:

1. **Shared parser** (`scripts/parse_resume.py`) — Parses resume markdown into a structured intermediate representation (sections, headings, bullets, contact info). Consumed by all renderers.
2. **PDF rendering** — Two backends, auto-selected by environment:
   - **Typst** (`scripts/md-to-pdf.py`) — Primary backend in Claude Code; uses Typst templates for high-quality PDF output
   - **Python fallback** (`scripts/md_to_pdf_fallback.py`) — Fallback in Cowork VMs where Typst is unavailable; uses fpdf2 with 4 presets (classic, modern, compact, harvard)
   - **Router** (`scripts/md_to_pdf_router.py`) — Auto-detects the available backend via `workspace/.env-config` and dispatches accordingly
3. **DOCX rendering** (`scripts/md-to-docx.py`) — Produces Word documents via python-docx with 4 bundled preset templates and support for user-provided custom templates
4. **ATS validation** — Automatic post-export validation for both formats:
   - `scripts/validate_pdf.py` — Checks PDF text extraction fidelity, heading preservation, and garbled text detection
   - `scripts/validate_docx.py` — Checks DOCX content completeness across paragraphs and tables

### Pipeline Flow

`analyze-resume` orchestrates:
1. Session setup → `workspace/output/YYYY-MM-DD-HHMMSS/`
2. Input detection + JD collection
3. Parse (sequential, foreground — resume-parser agent)
4. Parallel analysis (4-5 agents as background tasks)
5. Score computation (`scripts/compute-scores.py`)
6. Report generation (`analysis-report.md`)
7. Chat summary

`optimize-resume` collects optional user notes → interview → rewrite → approval → re-score.

`export-resume` handles post-optimization export:
1. Format selection (PDF or DOCX)
2. Preset/template selection
3. Rendering via appropriate backend (Typst, fpdf2, or python-docx)
4. ATS validation of the exported file
5. Delivery to user

### Python Scripts

All scripts are CLI tools run via `scripts/run-python.sh` (auto-selects `uv run` or `python3`):

| Script | Purpose |
|--------|---------|
| `scripts/run-python.sh` | Environment-aware Python runner (routes through `uv run` or `python3`) |
| `scripts/extract-pdf-text.py` | PDF text extraction via PyMuPDF |
| `scripts/compute-scores.py` | Weighted score computation from analysis JSONs |
| `scripts/validate-output.py` | JSON Schema validation for output files |
| `scripts/md-to-pdf.py` | Markdown-to-PDF conversion via Typst templates |
| `scripts/parse_resume.py` | Shared resume markdown parser (importable module + CLI) |
| `scripts/md_to_pdf_fallback.py` | Python PDF fallback renderer via fpdf2 (4 presets) |
| `scripts/md_to_pdf_router.py` | Environment-aware PDF backend router |
| `scripts/md-to-docx.py` | Markdown-to-DOCX conversion via python-docx |
| `scripts/validate_pdf.py` | Post-export PDF ATS validation |
| `scripts/validate_docx.py` | Post-export DOCX ATS validation |
| `scripts/export_edge_cases.py` | Centralized edge case handling utilities for export |
| `scripts/build-word-templates.py` | Generates the 4 bundled Word preset templates |
| `scripts/env_config.py` | Environment config helper (load config, detect backends) |

### JSON Schemas

`schemas/` contains JSON Schema definitions for all structured outputs. The `validate-output.py` script maps output filenames to schemas (e.g., `parsed-resume.json` → `parsed-resume.schema.json`). The PreToolUse hook on `Write` auto-validates JSON outputs against these schemas.

### Scoring System

Scoring weights and grade boundaries are defined in `skills/analyze-resume/scoring-rubric.json` (single source of truth). Two weight profiles exist: `with_jd` (6 dimensions) and `without_jd` (5 dimensions, keyword alignment excluded). Missing dimensions get their weights redistributed proportionally.

### Hooks

Defined in `hooks/hooks.json`:
- **SessionStart** — `setup-deps.sh` detects the runtime environment (package manager, Typst availability, font access), installs dependencies via `uv sync` or `pip`, and writes `workspace/.env-config` with detected capabilities. Re-runs on every session start to handle environment changes.
- **PreToolUse (Write)** — `validate-output.sh` validates JSON output files against schemas
- **Stop** — Echoes session completion message

### Reference Data

- `skills/*/references/` — Per-skill reference files (rubrics, templates, rules, industry data)
- `reference/resume-conventions-by-country.md` — Country-specific resume conventions
- `fonts/` — Bundled fonts (EB Garamond, Inter, Lato, Source Sans 3) under SIL OFL
- `templates/pdf/` — Typst templates for PDF presets (classic, modern, compact, harvard)
- `templates/word/` — Bundled Word preset templates (professional, simple, academic, creative) generated by `build-word-templates.py`

### Workspace Convention

All user data flows through `workspace/` (gitignored):
- `workspace/input/` — User's resume and optional job description
- `workspace/output/YYYY-MM-DD-HHMMSS/` — Timestamped session directories with all outputs
- `workspace/.env-config` — Auto-generated environment detection config (created by `setup-deps.sh`)

## Key Design Principles

- **Graceful degradation**: Any individual analysis agent can fail without crashing the pipeline. Missing outputs trigger weight redistribution in scoring and section omission in reports. Export backends fall back automatically (Typst → fpdf2 for PDF).
- **Never fabricate data**: Use `[X]` placeholders for missing metrics. Scores reflect genuine assessment.
- **Schema validation on write**: The PreToolUse hook validates all structured JSON outputs before they're written.
- **Single source of truth for scoring**: All weights, grade mappings, and dimension definitions come from `scoring-rubric.json`.
- **Environment awareness**: The plugin auto-detects available tools and adapts its behavior for both Claude Code and Claude Cowork environments via `workspace/.env-config`.
