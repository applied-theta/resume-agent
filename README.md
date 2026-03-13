# Resume Agent Plugin

AI-powered Resume Analysis & Optimization plugin for Claude Code and Claude Cowork.

Analyzes resumes across 6 dimensions (ATS compatibility, content quality, keyword alignment, strategic positioning, structure/format, market intelligence) and produces optimized resumes with change tracking.

## Installation

```bash
claude plugin install --git https://github.com/sequenzia/resume-agent-plugin
```

Or install from a local directory:

```bash
claude plugin install --dir /path/to/resume-agent-plugin
```

## Requirements

- [uv](https://docs.astral.sh/uv/) — Python package manager (auto-installs dependencies on first session)
- Python >= 3.12

Dependencies (`pymupdf`, `jsonschema`, `typst`) are installed automatically via the SessionStart hook.

## Commands

| Command | Description |
|---------|-------------|
| `/resume-agent:analyze-resume` | Full 6-dimension analysis pipeline |
| `/resume-agent:parse-resume` | Parse resume into structured JSON |
| `/resume-agent:ats-check` | ATS compatibility analysis |
| `/resume-agent:content-review` | Content quality analysis |
| `/resume-agent:keyword-align` | Keyword alignment (requires JD) |
| `/resume-agent:strategy-review` | Strategic positioning analysis |
| `/resume-agent:skills-research` | Market intelligence and skills demand |
| `/resume-agent:optimize-resume` | Resume rewriting with change tracking |
| `/resume-agent:export-pdf` | Export resume markdown to styled PDF |

## Quick Start

1. Install the plugin
2. Place your resume (PDF or Markdown) in `workspace/input/`
3. Run `/resume-agent:analyze-resume`
4. Optionally provide a job description for keyword alignment
5. Review the analysis report in `workspace/output/{session}/`
6. Run `/resume-agent:optimize-resume` for rewritten content

## Architecture

The plugin orchestrates 8 specialized subagents:

- **resume-parser** — Extracts structured data from PDF/Markdown
- **ats-analyzer** — Evaluates ATS compatibility with platform simulation
- **content-analyst** — Scores bullet points and content quality
- **keyword-optimizer** — Analyzes keyword alignment against job descriptions
- **strategy-advisor** — Detects career archetype and strategic positioning
- **skills-research** — Market demand analysis and terminology verification
- **interview-researcher** — Background research during optimization interview
- **resume-rewriter** — Produces optimized resume content (Opus model)

## Scoring

Scores are computed across 6 dimensions with configurable weights (see `skills/analyze-resume/scoring-rubric.json`).

### With Job Description

| Dimension | Weight |
|-----------|--------|
| ATS Compatibility | 18% |
| Keyword Alignment | 22% |
| Content Quality | 22% |
| Strategic Positioning | 13% |
| Structure & Format | 12% |
| Market Intelligence | 13% |

### Without Job Description

| Dimension | Weight |
|-----------|--------|
| ATS Compatibility | 22% |
| Content Quality | 26% |
| Strategic Positioning | 22% |
| Structure & Format | 17% |
| Market Intelligence | 13% |

## Safety

- Never fabricates metrics or achievements — uses `[X]` placeholders
- All resume data stays in the local `workspace/` directory
- Honest scoring — scores reflect genuine assessment
- Missing data is acknowledged, not guessed

## Known Issues

- **Pyright type errors**: 13 errors (PyMuPDF return types, importlib patterns). All tests pass.
- **Empty golden-file directories**: Integration/snapshot tests are planned but not implemented.

## License

Fonts in `fonts/` are licensed under the SIL Open Font License.
