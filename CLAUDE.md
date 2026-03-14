# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Claude Code plugin for AI-powered resume analysis and optimization. Analyzes resumes across 6 dimensions (ATS compatibility, content quality, keyword alignment, strategic positioning, structure/format, market intelligence) and produces optimized resumes with change tracking and PDF export.

## Dependencies & Setup

- **Python >= 3.12** with `uv` for package management
- Dependencies: `pymupdf`, `jsonschema`, `typst` (auto-installed via SessionStart hook on `uv sync`)
- Run scripts with: `uv run scripts/<script>.py`
- No test suite currently exists (integration/snapshot tests are planned)

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
| `export-pdf` | Converts resume markdown to PDF via Typst |

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

### Pipeline Flow

`analyze-resume` orchestrates:
1. Session setup → `workspace/output/YYYY-MM-DD-HHMMSS/`
2. Input detection + JD collection
3. Parse (sequential, foreground — resume-parser agent)
4. Parallel analysis (4-5 agents as background tasks)
5. Score computation (`scripts/compute-scores.py`)
6. Report generation (`analysis-report.md`)
7. Chat summary

`optimize-resume` follows analysis with interview → rewrite → approval → re-score.

### Python Scripts

All scripts are CLI tools run via `uv run`:

| Script | Purpose |
|--------|---------|
| `scripts/extract-pdf-text.py` | PDF text extraction via PyMuPDF |
| `scripts/compute-scores.py` | Weighted score computation from analysis JSONs |
| `scripts/validate-output.py` | JSON Schema validation for output files |
| `scripts/md-to-pdf.py` | Markdown-to-PDF conversion via Typst templates |

### JSON Schemas

`schemas/` contains JSON Schema definitions for all structured outputs. The `validate-output.py` script maps output filenames to schemas (e.g., `parsed-resume.json` → `parsed-resume.schema.json`). The PreToolUse hook on `Write` auto-validates JSON outputs against these schemas.

### Scoring System

Scoring weights and grade boundaries are defined in `skills/analyze-resume/scoring-rubric.json` (single source of truth). Two weight profiles exist: `with_jd` (6 dimensions) and `without_jd` (5 dimensions, keyword alignment excluded). Missing dimensions get their weights redistributed proportionally.

### Hooks

Defined in `hooks/hooks.json`:
- **SessionStart** — `setup-deps.sh` runs `uv sync` to install Python dependencies
- **PreToolUse (Write)** — `validate-output.sh` validates JSON output files against schemas
- **Stop** — Echoes session completion message

### Reference Data

- `skills/*/references/` — Per-skill reference files (rubrics, templates, rules, industry data)
- `reference/resume-conventions-by-country.md` — Country-specific resume conventions
- `fonts/` — Bundled fonts (EB Garamond, Inter, Lato, Source Sans 3) under SIL OFL
- `templates/pdf/` — Typst templates for PDF presets (classic, modern, compact, harvard)

### Workspace Convention

All user data flows through `workspace/` (gitignored):
- `workspace/input/` — User's resume and optional job description
- `workspace/output/YYYY-MM-DD-HHMMSS/` — Timestamped session directories with all outputs

## Key Design Principles

- **Graceful degradation**: Any individual analysis agent can fail without crashing the pipeline. Missing outputs trigger weight redistribution in scoring and section omission in reports.
- **Never fabricate data**: Use `[X]` placeholders for missing metrics. Scores reflect genuine assessment.
- **Schema validation on write**: The PreToolUse hook validates all structured JSON outputs before they're written.
- **Single source of truth for scoring**: All weights, grade mappings, and dimension definitions come from `scoring-rubric.json`.
