# Codebase Changes Report

## Metadata

| Field | Value |
|-------|-------|
| **Date** | 2026-04-10 |
| **Time** | 10:17 EDT |
| **Branch** | main |
| **Author** | Stephen Sequenzia |
| **Base Commit** | `cadc59e` (v0.3.2) |
| **Latest Commit** | uncommitted |
| **Repository** | git@github.com:applied-theta/resume-agent.git |

**Scope**: Workspace management restructuring for Cowork compatibility and multi-resume support

**Summary**: Restructured the plugin's workspace from a flat `workspace/output/` layout to a per-resume directory structure (`{workspace}/{slug}/sessions/`) with a configurable `WORKSPACE_ROOT`. Decoupled `.env-config` from the workspace directory, moving it to the plugin root, and added a shared workspace resolution reference used by all 9 skills.

## Overview

This change addresses two active Cowork pain points: output files ending up in the plugin cache directory (inaccessible to users) and session discovery glob patterns failing in the VM. The restructuring also adds multi-resume support with independent session histories per resume.

- **Files affected**: 26
- **Lines added**: +257
- **Lines removed**: -157
- **Commits**: 0 (all changes uncommitted)

## Files Changed

| File | Status | Lines | Description |
|------|--------|-------|-------------|
| `skills/shared/workspace-resolution.md` | Added | +119 | Shared reference for workspace layout, slug derivation, session discovery |
| `skills/analyze-resume/SKILL.md` | Modified | +55 / -28 | Added Step 0 workspace setup, per-resume slug derivation, updated all paths |
| `skills/optimize-resume/SKILL.md` | Modified | +20 / -17 | Updated session discovery and all output path references |
| `skills/keyword-align/SKILL.md` | Modified | +19 / -13 | Updated input/output paths and session discovery |
| `hooks/setup-deps.sh` | Modified | +19 / -7 | Moved config to plugin root, added WORKSPACE_ROOT resolution |
| `scripts/env_config.py` | Modified | +15 / -4 | Updated config path, added workspace_root() helper |
| `skills/parse-resume/SKILL.md` | Modified | +15 / -11 | Updated input copy and session creation paths |
| `CLAUDE.md` | Modified | +17 / -9 | Updated workspace convention, hooks, and pipeline flow docs |
| `skills/content-review/SKILL.md` | Modified | +11 / -9 | Updated session discovery and output paths |
| `skills/ats-check/SKILL.md` | Modified | +11 / -9 | Updated session discovery and output paths |
| `skills/skills-research/SKILL.md` | Modified | +14 / -10 | Updated input/output paths and session discovery |
| `skills/strategy-review/SKILL.md` | Modified | +13 / -9 | Updated input/output paths and session discovery |
| `skills/export-resume/SKILL.md` | Modified | +7 / -3 | Updated session discovery glob for optimized-resume.md |
| `README.md` | Modified | +5 / -5 | Updated quick start guide with path-based workflow |
| `agents/resume-parser.md` | Modified | +5 / -5 | Updated workspace/input/ and workspace/output/ references |
| `agents/keyword-optimizer.md` | Modified | +4 / -4 | Updated input lookup and write path references |
| `agents/resume-rewriter.md` | Modified | +3 / -3 | Updated session read and input reference paths |
| `agents/skills-research.md` | Modified | +3 / -3 | Updated JD lookup and write path references |
| `agents/content-analyst.md` | Modified | +2 / -2 | Updated read/write path references |
| `agents/strategy-advisor.md` | Modified | +2 / -2 | Updated JD lookup and write path references |
| `skills/analyze-resume/references/architecture.md` | Modified | +3 / -3 | Updated architecture diagram paths |
| `scripts/md_to_pdf_router.py` | Modified | +3 / -3 | Updated config file path references and docstrings |
| `scripts/run-python.sh` | Modified | +2 / -2 | Updated config path from workspace/.env-config to .env-config |
| `hooks/hooks.json` | Modified | +1 / -1 | Updated Stop hook to read WORKSPACE_ROOT from config |
| `agents/ats-analyzer.md` | Modified | +1 / -1 | Updated write path reference |
| `.gitignore` | Modified | +1 / -0 | Added .env-config to gitignore |

## Change Details

### Added

- **`skills/shared/workspace-resolution.md`** — New shared reference file that serves as the single source of truth for workspace layout. Documents the resolution order (--workspace arg > RESUME_WORKSPACE env var > .env-config > fallback), per-resume directory structure, slug derivation rules, active resume context management, session discovery glob patterns, and backwards compatibility with legacy `workspace/output/` layout. Referenced by all 9 skills.

### Modified

#### Infrastructure (5 files)

- **`hooks/setup-deps.sh`** — Moved `.env-config` from `${PLUGIN_ROOT}/workspace/` to `${PLUGIN_ROOT}/`. Added `WORKSPACE_ROOT` resolution that checks the `RESUME_WORKSPACE` env var and defaults to `${PLUGIN_ROOT}/workspace`. Writes `WORKSPACE_ROOT` to the config output. Cleans up legacy config file at old location if found.

- **`scripts/env_config.py`** — Updated `_CONFIG_PATH` to read from plugin root instead of `workspace/`. Added `WORKSPACE_ROOT` to defaults dict. Added new `workspace_root()` helper function that returns the resolved workspace root as a `Path`.

- **`scripts/run-python.sh`** — Updated config path from `$PLUGIN_ROOT/workspace/.env-config` to `$PLUGIN_ROOT/.env-config`.

- **`scripts/md_to_pdf_router.py`** — Updated config file path references and docstrings from `workspace/.env-config` to `.env-config`.

- **`hooks/hooks.json`** — Updated Stop hook to dynamically read `WORKSPACE_ROOT` from `.env-config` and display the actual workspace location.

#### Skills (10 files)

- **`skills/analyze-resume/SKILL.md`** — Added Step 0 (Workspace Setup) for resolving workspace root and determining resume slug. Updated Step 1 to create sessions at `{workspace}/{slug}/sessions/YYYY-MM-DD-HHMMSS/`. Updated all input/output path references across Steps 2-7 and error handling. Added rename option for auto-derived slugs.

- **`skills/optimize-resume/SKILL.md`** — Updated Step 1 session discovery to use new glob patterns with legacy fallback. Updated all path references in Steps 4, 8, 9, and 10 including score computation, optimization report, and PDF export paths.

- **`skills/parse-resume/SKILL.md`** — Updated input scanning, copy commands, session creation, and output paths.

- **`skills/ats-check/SKILL.md`** — Updated session discovery globs and output paths with legacy fallback.

- **`skills/content-review/SKILL.md`** — Updated session discovery globs and output paths with legacy fallback.

- **`skills/keyword-align/SKILL.md`** — Updated JD file copy paths, session discovery, and output paths with legacy fallback.

- **`skills/strategy-review/SKILL.md`** — Updated JD lookup, session discovery, and output paths with legacy fallback.

- **`skills/skills-research/SKILL.md`** — Updated JD lookup, session discovery, and output paths with legacy fallback.

- **`skills/export-resume/SKILL.md`** — Updated session discovery glob for `optimized-resume.md` with legacy fallback. Updated output directory detection for new session path structure.

- **`skills/analyze-resume/references/architecture.md`** — Updated architecture diagram paths from `workspace/input/` and `workspace/output/` to `{workspace}/{slug}/` equivalents.

#### Agents (7 files)

- **`agents/resume-parser.md`** — Updated error messages referencing `workspace/input/` and extraction/output paths referencing `workspace/output/{session}/`.

- **`agents/content-analyst.md`** — Updated read path for parsed-resume.json and write path for content-analysis.json.

- **`agents/strategy-advisor.md`** — Updated JD lookup path and write path for strategy-analysis.json.

- **`agents/skills-research.md`** — Updated JD lookup path, write path, and code example for skills-research.json.

- **`agents/ats-analyzer.md`** — Updated write path for ats-analysis.json.

- **`agents/keyword-optimizer.md`** — Updated parsed resume lookup, JD lookup, write path, and code example for keyword-analysis.json.

- **`agents/resume-rewriter.md`** — Updated session read docs, original resume reference, and output write docs.

#### Documentation (3 files)

- **`CLAUDE.md`** — Updated Workspace Convention section with new per-resume structure, updated Pipeline Flow, Hooks, and Export Architecture sections. Added documentation for WORKSPACE_ROOT and RESUME_WORKSPACE env var.

- **`README.md`** — Updated Quick Start guide to use direct path argument instead of manual workspace/input/ placement.

- **`.gitignore`** — Added `.env-config` entry to ignore the config file at plugin root.

## Git Status

### Unstaged Changes

| Status | File |
|--------|------|
| M | .gitignore |
| M | CLAUDE.md |
| M | README.md |
| M | agents/ats-analyzer.md |
| M | agents/content-analyst.md |
| M | agents/keyword-optimizer.md |
| M | agents/resume-parser.md |
| M | agents/resume-rewriter.md |
| M | agents/skills-research.md |
| M | agents/strategy-advisor.md |
| M | hooks/hooks.json |
| M | hooks/setup-deps.sh |
| M | scripts/env_config.py |
| M | scripts/md_to_pdf_router.py |
| M | scripts/run-python.sh |
| M | skills/analyze-resume/SKILL.md |
| M | skills/analyze-resume/references/architecture.md |
| M | skills/ats-check/SKILL.md |
| M | skills/content-review/SKILL.md |
| M | skills/export-resume/SKILL.md |
| M | skills/keyword-align/SKILL.md |
| M | skills/optimize-resume/SKILL.md |
| M | skills/parse-resume/SKILL.md |
| M | skills/skills-research/SKILL.md |
| M | skills/strategy-review/SKILL.md |

### Untracked Files

| File |
|------|
| skills/shared/ |

## Session Commits

No commits in this session. All changes are uncommitted.
