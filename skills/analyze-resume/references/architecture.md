# Resume Analysis Pipeline — Architecture Reference

This document provides architecture context and scoring references for the resume analysis pipeline.

## System Architecture

```
User Layer:  Slash commands, conversational input, file-based input (workspace/input/)
    |
    v
Orchestration: /analyze-resume skill - pipeline coordination
    |
    v
Subagents:   8 specialized agents
    |
    v
Support:     Scripts (extract-pdf-text, compute-scores, validate-output, md-to-pdf),
             Skills (ats-check, content-review, keyword-align, strategy-review, optimize-resume)
    |
    v
File System: workspace/input/ (user files), workspace/output/{session}/ (results)
```

## Subagents

| Agent | Model | Tools | Purpose |
|-------|-------|-------|---------|
| resume-parser | sonnet | Read, Bash, Glob | Extract structured data from PDF/Markdown resumes |
| ats-analyzer | sonnet | Read, Bash, WebSearch | Evaluate ATS compatibility across 4 sub-dimensions with platform simulation |
| content-analyst | sonnet | Read | Score bullet points and assess content quality |
| keyword-optimizer | sonnet | Read, Bash | Analyze keyword alignment against job descriptions |
| strategy-advisor | sonnet | Read, WebFetch | Detect career archetype and evaluate strategic positioning |
| skills-research | sonnet | Read, WebSearch, WebFetch, Context7 | Market demand analysis, terminology verification, and trending skills |
| interview-researcher | sonnet | Read, WebSearch, WebFetch, Context7 | Background research during optimization interview |
| resume-rewriter | opus | Read, Write, Bash | Produce optimized resume content (highest writing quality) |

## Scoring Weights

Scoring weights, grade boundaries, and dimension metadata are defined in `scoring-rubric.json` (the single source of truth).

### With Job Description (6 dimensions)

| Dimension | Weight |
|-----------|--------|
| ATS Compatibility | 18% |
| Keyword Alignment | 22% |
| Content Quality | 22% |
| Strategic Positioning | 13% |
| Structure & Format | 12% |
| Market Intelligence | 13% |

### Without Job Description (5 dimensions)

| Dimension | Weight |
|-----------|--------|
| ATS Compatibility | 22% |
| Content Quality | 26% |
| Strategic Positioning | 22% |
| Structure & Format | 17% |
| Market Intelligence | 13% |

## File-Based Inter-Agent Contracts

All agents communicate exclusively through JSON files in timestamped session directories. There is no shared memory or message passing. `parsed-resume.json` is the universal data bus — every downstream agent reads it.

## Graceful Degradation

The pipeline continues when individual agents fail. `compute-scores.py` redistributes scoring weights proportionally across available dimensions rather than zeroing missing ones.

## Structure/Format Coupling

The `structure_format` scoring dimension is primarily extracted from `ats-analysis.json > dimensions.structure_quality.score`. When ATS analysis fails, `compute-scores.py` falls back to estimating a structure score from `parsed-resume.json` metadata.

## Safety Rules

- **Never fabricate metrics or achievements.** Use bracketed placeholders `[X]` for unknown data.
- **PII stays local.** All resume data remains in the `workspace/` directory.
- **Honest scoring.** Scores must reflect genuine assessment.
- **Missing data acknowledged.** Note absent data rather than guessing.
