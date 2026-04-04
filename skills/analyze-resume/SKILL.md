---
name: analyze-resume
description: >
  Full resume analysis pipeline -- analyzes, reviews, evaluates, and provides
  feedback on a resume across six dimensions (ATS compatibility, content quality,
  keyword alignment, career strategy, skills intelligence, strategic positioning).
  Use this skill whenever the user wants to analyze a resume, review a resume,
  get feedback on a resume, evaluate a resume, check resume quality, assess a
  resume for job applications, or run any kind of comprehensive resume review --
  even if they don't say "analyze resume" explicitly.
argument-hint: "[resume-path] [--jd path|url]"
allowed-tools: Agent, Read, Write, Bash, Glob, WebFetch, AskUserQuestion
---

# Analyze Resume

Run the full resume analysis pipeline. This skill orchestrates the complete analysis workflow: parsing the resume, detecting career strategy, running parallel analysis agents, computing weighted scores, generating a comprehensive report, and presenting a conversational summary.

## Usage

```
/analyze-resume                                          → scans workspace/input/
/analyze-resume /path/to/resume.pdf                      → copies resume, then analyzes
/analyze-resume /path/to/resume.pdf --jd /path/to/jd.txt → copies both, then analyzes
/analyze-resume /path/to/resume.pdf --jd https://...     → copies resume, fetches JD URL
```

## Prerequisites

- A resume file provided as a direct path argument, or placed in `workspace/input/`
- Optionally, a job description (file path via `--jd`, file in `workspace/input/`, pasted inline, provided as a URL, or provided interactively when prompted)


## Pipeline Overview

The pipeline executes in this order:

```
1.   Session Setup      Create timestamped output directory
2a.  Input Detection    Copy files if path args provided; find resume in workspace/input/; auto-detect JD
2b.  JD Collection      Interactive JD prompt if no JD auto-detected; URL/path handling; fallback logic
3.   Parse              Delegate to resume-parser subagent
4.   Parallel Analysis  strategy-advisor + ats-analyzer + content-analyst + keyword-optimizer (if JD) + skills-research
5.   Score Computation  Run compute-scores.py
6.   Report Generation  Write analysis-report.md (template: ${CLAUDE_PLUGIN_ROOT}/skills/analyze-resume/references/report-template.md)
7.   Chat Summary       Present conversational summary with highlights
```

Step 3 runs in foreground (all subsequent agents depend on it). Step 4 launches up to 5 analysis agents (or 4 without JD) as background tasks in parallel. Steps 5-7 run sequentially after all agents complete.

The pipeline dispatches 7 agents total: 1 parser (sequential) + up to 5 analysis agents in parallel (strategy-advisor, ats-analyzer, content-analyst, skills-research always; keyword-optimizer only with JD). The resume-rewriter is invoked separately via `/optimize-resume`.


## Step 1: Session Setup

Create a timestamped session directory for this analysis run:

```
workspace/output/YYYY-MM-DD-HHMMSS/
```

Use the current date and time. This directory will hold all output files from the pipeline.

Tell the user:
> Starting resume analysis... Session directory: `workspace/output/{session}/`


## Step 2a: Input Detection

### Copy Input Files (if path arguments provided)

If the user provided a resume file path as an argument:
1. Ensure the input directory exists: `mkdir -p workspace/input`
2. Copy the file: `cp <provided-path> workspace/input/`
3. If the copy fails (file not found, permission denied), report the error and stop.

If the user provided a JD file path via `--jd`:
1. Copy the file: `cp <provided-path> workspace/input/`
2. If the copy fails, report the error and stop.

After copying (or if no path arguments were provided), proceed with the normal workspace/input/ scan below.

### Find the Resume

Scan `workspace/input/` for resume files. Look for files with `.pdf`, `.md`, or `.markdown` extensions.

**If no resume file is found:**
> No resume file found. Please provide a resume in one of two ways:
>
> 1. **Direct path**: `/analyze-resume /path/to/resume.pdf`
> 2. **Workspace**: Place a PDF or Markdown file in `workspace/input/` and run `/analyze-resume`
>
> Supported formats: PDF (`.pdf`), Markdown (`.md`)

Stop the pipeline. Do not proceed.

**If multiple resume files are found:** Use the most recently modified file. Inform the user which file was selected.

### Auto-Detect Job Description

Check for a job description in `workspace/input/`. Look for files with names containing "jd", "job", or "description" (case-insensitive), or `.txt` files that are not the resume.

Also check if the user provided a JD inline in the conversation, as a URL, or via the `--jd` argument (already copied above).

**If a JD URL is provided (via `--jd` or inline):** Use `WebFetch` to retrieve the content before proceeding.


## Step 2b: JD Collection

### Prompt for Job Description (if none found)

If no JD was found from any automatic source (no `--jd` argument, no JD file detected in `workspace/input/`, no inline content or URL), prompt the user via `AskUserQuestion`:

> **Would you like to include a job description?**
> Adding a job description enables keyword alignment analysis and uses a 6-dimension scoring model for more targeted results.

Options (2):
- **"Yes, I have a job description"** — "I can provide a file path or URL"
- **"No, analyze without a job description"** — "Skips keyword alignment; uses 5-dimension scoring"

**If user selects "No, analyze without a job description":** Record JD as unavailable and proceed to the status message below.

**If user selects "Yes, I have a job description":** Collect the JD location via a follow-up prompt:
> Please provide the file path or URL for the job description.

Then process the provided input:
- **URL** (starts with `http://` or `https://`): Use `WebFetch` to retrieve the content. If the fetch fails or the content does not look like a job posting, inform the user and fall back to without-JD mode.
- **File path**: Copy to `workspace/input/`. If the copy fails (file not found, permission denied), inform the user and fall back to without-JD mode.
- **Empty or unrecognizable input**: Treat JD as unavailable, inform the user, and continue in without-JD mode.

All error cases fall back to without-JD mode with an informative message — never crash the pipeline. See the "JD Prompt Follow-Up Failure" error handling subsection for details.

### Record JD availability

Record whether a JD is available. This determines:
- Whether keyword-optimizer runs in Step 4
- Which scoring weights are used in Step 5

Tell the user:
> Found resume: `{filename}`
> Job description: `{found/not found}`
> Mode: `{with JD / without JD}`


## Step 3: Parse Resume

Delegate to the **resume-parser** subagent to extract structured data from the resume.

**Input to provide the subagent:**
- The resume file path
- The session directory path for output

**Expected output:** `workspace/output/{session}/parsed-resume.json`

Tell the user:
> Parsing resume...

**On success:**
> Resume parsed successfully. Identified {N} experience entries, {N} education entries, {N} skills.

**On failure:**
Record the failure. Report the error to the user but continue the pipeline if possible. If parsing fails completely (no structured data), stop the pipeline:
> Resume parsing failed: {error message}. Cannot continue analysis without parsed data.


## Step 4: Parallel Analysis

Run all analysis agents in parallel as background tasks. Use the Task tool or subagent delegation to dispatch them concurrently.

### Agents to Dispatch

**Always run (no notes needed):**
1. **ats-analyzer** -- ATS compatibility analysis and platform simulation

**Always run:**
2. **strategy-advisor** -- Career archetype detection and strategic positioning
3. **content-analyst** -- Content quality analysis
4. **skills-research** -- Market demand analysis, terminology verification, and trending skills

**Run only if JD is available:**
5. **keyword-optimizer** -- Keyword alignment analysis

### Input to Provide Each Subagent

All agents receive:
- The session directory path (subagents read `parsed-resume.json` and other needed files from this directory)

Additionally:
- **keyword-optimizer**: JD content or file path
- **skills-research**: JD content or file path (if available) + target role context
- **ats-analyzer**: (no additional inputs beyond session directory)

### Expected Outputs

- `workspace/output/{session}/strategy-analysis.json`
- `workspace/output/{session}/ats-analysis.json` (includes `platform_simulation` section)
- `workspace/output/{session}/content-analysis.json`
- `workspace/output/{session}/skills-research.json`
- `workspace/output/{session}/keyword-analysis.json` (only if JD provided)

Tell the user:
> Running all analysis agents in parallel...
> - Career strategy and positioning
> - ATS compatibility analysis (with platform simulation)
> - Content quality analysis
> - Skills and market intelligence research
> {- Keyword alignment analysis (if JD)}

**As each agent completes**, report progress:
> Strategy analysis complete. Archetype: {archetype}
> ATS analysis complete. Score: {score}/100
> Content analysis complete. Score: {score}/100
> Skills research complete. Market alignment: {score}/100
> Keyword analysis complete. Match rate: {rate}% (if applicable)

**On individual agent failure:**
Record the failure. Note it for the report but continue with remaining agents:
> {Agent name} encountered an issue: {error}. Continuing with available analyses.

The pipeline follows graceful degradation: any individual agent can fail without crashing the pipeline. Missing outputs are handled downstream by `compute-scores.py` (weight redistribution) and the report (section omission with explanation).


## Step 5: Score Computation

Run the scoring script to compute weighted overall scores:

```bash
${CLAUDE_PLUGIN_ROOT}/scripts/run-python.sh ${CLAUDE_PLUGIN_ROOT}/scripts/compute-scores.py workspace/output/{session}/
```

This script:
- Reads all available analysis JSON files from the session directory
- Automatically selects with-JD or without-JD weights based on presence of `keyword-analysis.json`
- Reads `skills-research.json` for the Market Intelligence dimension
- Redistributes weights proportionally if any dimension is missing (due to agent failure)
- Writes `scores-summary.json` to the session directory

**Scoring dimensions and weights** are defined in `scoring-rubric.json` (the single source of truth). The script reads weights from this file at runtime. Six dimensions are scored when a JD is present (ats_compatibility, keyword_alignment, content_quality, strategic_positioning, structure_format, market_intelligence); five without a JD (keyword_alignment is omitted and weights are redistributed). See `scoring-rubric.json` for exact values.

Tell the user:
> Computing weighted scores...

**On success:**
> Overall score: {score}/100 ({grade})

**On failure:**
> Score computation failed: {error}. Generating report with available data.


## Step 6: Report Generation

Write a comprehensive analysis report to `workspace/output/{session}/analysis-report.md`.

### Report Template

Read the report template from `${CLAUDE_PLUGIN_ROOT}/skills/analyze-resume/references/report-template.md` and populate it with data from the analysis JSON files in the session directory.

The template defines:
- The full section structure (header, Executive Summary, User Context, Scorecard, Detailed Analysis, Skills Intelligence, ATS Platform Simulation, Priority Action Plan, Dimension Details)
- Inline placeholder syntax for all variable fields
- Content rules governing what to include, what to omit, and how to handle missing data

Tell the user:
> Generating analysis report...


## Step 7: Chat Summary

After writing the report, present a conversational summary in the chat. This should be a concise, friendly overview -- not a copy of the report.

### Summary Format

Present the results conversationally:

> **Resume Analysis Complete**
>
> Your resume scored **{score}/100 ({grade})** overall. Here is a quick look at how you did across each dimension:
>
> | Dimension | Score | Grade |
> |-----------|-------|-------|
> | {dimension} | {score}/100 | {grade} |
> | ... | ... | ... |
>
> **Strongest area:** {highest scoring dimension and brief note on why}
>
> **Biggest opportunity:** {lowest scoring dimension and brief note on the top fix}
>
> **Skills snapshot:** {1-2 sentence highlight from skills-research -- e.g., "Your Python and AWS skills are in high demand. Consider adding Kubernetes, which appears in 72% of similar job postings."}
>
> **ATS platform highlight:** {1-sentence highlight from platform simulation -- e.g., "Your resume scores highest on Greenhouse (92/100) but may need formatting adjustments for Workday (71/100)."}
>
> **Top 3 actions to take:**
> 1. {Most impactful action}
> 2. {Second most impactful}
> 3. {Third most impactful}
>
> The full report is saved at `workspace/output/{session}/analysis-report.md`.
>
> Want to optimize your resume? Run `/optimize-resume` to get rewritten bullet points and a restructured resume.


## Error Handling

### No Resume Found
If no resume file is found in `workspace/input/` (and no path argument was provided), stop the pipeline immediately with clear instructions (see Step 2).

### Individual Agent Failure
If a single analysis agent fails:
1. Log the failure and the error message
2. Continue the pipeline with remaining agents
3. The scoring script automatically redistributes weights for missing dimensions
4. Note the missing dimension in the report with an explanation
5. Include a note in the chat summary

This applies equally to all agents including skills-research. If skills-research fails:
- The "Skills Intelligence" section shows a fallback message
- `compute-scores.py` redistributes the Market Intelligence weight across remaining dimensions
- The pipeline continues normally with available data

### Scoring Script Failure
If `compute-scores.py` fails:
1. Report the error to the user
2. Attempt to generate the report using the individual analysis scores directly
3. Omit the overall score and grade from the report, or compute them manually from available data

### Complete Pipeline Failure
If the resume parser fails completely (no `parsed-resume.json`):
1. Stop the pipeline -- downstream agents cannot run without parsed data
2. Report the specific error to the user with guidance on how to fix the input

### JD Prompt Follow-Up Failure
If the user selects "Yes" at the JD prompt but the follow-up fails (bad file path, unreachable URL, unrecognizable input):
1. Report the specific issue to the user (e.g., "File not found: /path/to/jd.txt" or "Could not fetch URL: connection timed out")
2. Set JD as unavailable and continue in without-JD mode
3. Inform the user: "Continuing without a job description. You can re-run with `--jd <path>` to include one."

### Missing skills-research.json
If `skills-research.json` is not present after Step 4 (agent failure or timeout):
1. The "Skills Intelligence" report section shows a fallback message directing users to `/skills-research`
2. `compute-scores.py` redistributes the Market Intelligence weight proportionally
3. The chat summary omits the "Skills snapshot" highlight
4. The pipeline continues without interruption

### Agent Timeout
If a background analysis agent (from Step 4) times out before completing:
1. Treat the timeout as an agent failure -- apply the same graceful degradation as "Individual Agent Failure" above
2. The scoring script redistributes the missing dimension's weight proportionally across remaining dimensions
3. The report omits the timed-out dimension's section and notes it was unavailable
4. The chat summary omits highlights sourced from that dimension
5. Do not block the pipeline waiting for a timed-out agent -- proceed to Step 5 with available outputs


## Pipeline Without Job Description

When no JD is provided:
- Skip the keyword-optimizer agent entirely in Step 4
- The skills-research agent still runs (infers target role from resume)
- The scoring script automatically uses without-JD weights (5 dimensions)
- The report omits the Keyword Alignment section
- The chat summary notes that keyword analysis was skipped
- Recommend providing a JD for a more complete analysis


## Progress Updates

Display progress at each pipeline stage to keep the user informed:

| Stage | Message |
|-------|---------|
| Start | "Starting resume analysis..." |
| Input found | "Found resume: {file}. Mode: {with/without JD}" |
| Parsing | "Parsing resume..." |
| Parse complete | "Resume parsed. {N} experience entries found." |
| Parallel start | "Running all analysis agents in parallel..." (list all agents being dispatched) |
| Each agent done | "{Agent} complete. Score: {score}/100" |
| Scoring | "Computing weighted scores..." |
| Score complete | "Overall: {score}/100 ({grade})" |
| Report | "Generating analysis report..." |
| Done | Full chat summary (see Step 7) |
