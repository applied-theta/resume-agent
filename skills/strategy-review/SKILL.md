---
name: strategy-review
description: >
  Strategic positioning analysis -- detects career archetype, evaluates
  value proposition strength, assesses resume format appropriateness,
  and recommends section ordering and length optimizations.
argument-hint: "[resume-path]"
disable-model-invocation: true
allowed-tools: Agent, Read, Bash, Glob
---

# Strategy Review

Run a strategic positioning analysis on a resume. This command evaluates career archetype classification, value proposition effectiveness, format appropriateness, section ordering, and overall strategic positioning, producing actionable recommendations for improving how the resume markets the candidate.

## Usage

```
/strategy-review                        → scans workspace/input/
/strategy-review /path/to/resume.pdf    → copies resume, then analyzes
```

## Procedure

### Step 1: Determine the Session Directory

Identify the current session directory under `workspace/output/`. If a session directory already exists from a previous command in this conversation, reuse it. Otherwise, create a new timestamped session directory: `workspace/output/YYYY-MM-DD-HHMMSS/`.

### Step 2: Check for Parsed Resume

Check whether `parsed-resume.json` exists in the session directory.

- Use `Glob` to look for `workspace/output/*/parsed-resume.json` if no session is established, or check the specific session directory.
- If `parsed-resume.json` exists and does not contain an `"error": true` field, proceed to Step 4.
- If `parsed-resume.json` does not exist, proceed to Step 3.

### Step 3: Parse the Resume First

A parsed resume is required before strategy analysis can run. Delegate to the **resume-parser** subagent to parse the resume.

**Copy input file (if path argument provided):**
If the user provided a resume file path as an argument:
1. Ensure the input directory exists: `mkdir -p workspace/input`
2. Copy the file: `cp <provided-path> workspace/input/`
3. If the copy fails (file not found, permission denied), report the error and stop.

1. Look for a resume file in `workspace/input/` (PDF or Markdown).
2. If no resume file is found in `workspace/input/`:
   - Display a clear message to the user:
     > No resume found. Please provide a resume in one of two ways:
     > 1. **Direct path**: `/strategy-review /path/to/resume.pdf`
     > 2. **Workspace**: Place a PDF or Markdown file in `workspace/input/` and run `/strategy-review`
   - Stop execution.
3. If a resume file is found, delegate to the **resume-parser** agent, providing the file path and session directory.
4. After parsing completes, verify that `parsed-resume.json` was created in the session directory.
5. If parsing failed (file contains `"error": true` or was not created):
   - Display the error message from `parsed-resume.json` if available.
   - Otherwise display: "Resume parsing failed. Please check that your resume file is a valid PDF or Markdown document."
   - Stop execution.

### Step 4: Run Strategy Analysis

Delegate to the **strategy-advisor** subagent to perform the strategic positioning analysis.

Provide the strategy-advisor with:
- The session directory path (where `parsed-resume.json` is located)
- The strategy-advisor will read `parsed-resume.json` for structured resume data, load career strategy reference data from `${CLAUDE_PLUGIN_ROOT}/skills/strategy-review/references/`, and optionally check for a job description in `workspace/input/` for target role alignment

The strategy-advisor will write its output to `strategy-analysis.json` in the session directory.

### Step 5: Present Results Summary

After the strategy-advisor completes, read `strategy-analysis.json` from the session directory and present a conversational summary to the user.

**Summary format:**

1. **Overall Strategic Positioning Score** with letter grade (use the grade mapping from CLAUDE.md)
2. **Career Archetype** -- report the detected primary archetype (and secondary if present) with the confidence score. Briefly explain what the archetype means for the candidate's resume strategy.
3. **Value Proposition** -- report the summary effectiveness score, whether the candidate is differentiated, and the key selling points identified
4. **Format Recommendation** -- show the current format versus the recommended format, and highlight any sections to add or remove
5. **Top Strategic Recommendations** -- list the 3-5 highest-impact recommendations from the `strategic_recommendations` array
6. **Competitive Insights** -- briefly mention undersold strengths and weaknesses to mitigate from the `competitive_analysis` section
7. **Session output path** -- tell the user where the full analysis was saved

Keep the summary concise and actionable. Highlight what is working well alongside what needs improvement.
