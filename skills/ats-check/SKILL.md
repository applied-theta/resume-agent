---
name: ats-check
description: >
  ATS compatibility analysis -- evaluates how a resume performs in applicant
  tracking systems across parsability, format compliance, keyword readiness,
  and structure quality. Scores each dimension and provides specific fixes.
argument-hint: "[resume-path]"
disable-model-invocation: true
allowed-tools: Agent, Read, Bash, Glob
---

# ATS Check

Run an ATS (Applicant Tracking System) compatibility analysis on a resume. This command evaluates how well the resume will perform when processed by automated applicant tracking systems, scoring across four dimensions: parsability, format compliance, keyword readiness, and structure quality.

## Usage

```
/ats-check                        → scans workspace/input/
/ats-check /path/to/resume.pdf    → copies resume, then analyzes
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

A parsed resume is required before ATS analysis can run. Delegate to the **resume-parser** subagent to parse the resume.

**Copy input file (if path argument provided):**
If the user provided a resume file path as an argument:
1. Ensure the input directory exists: `mkdir -p workspace/input`
2. Copy the file: `cp <provided-path> workspace/input/`
3. If the copy fails (file not found, permission denied), report the error and stop.

1. Look for a resume file in `workspace/input/` (PDF or Markdown).
2. If no resume file is found in `workspace/input/`:
   - Display a clear message to the user:
     > No resume found. Please provide a resume in one of two ways:
     > 1. **Direct path**: `/ats-check /path/to/resume.pdf`
     > 2. **Workspace**: Place a PDF or Markdown file in `workspace/input/` and run `/ats-check`
   - Stop execution.
3. If a resume file is found, delegate to the **resume-parser** agent, providing the file path and session directory.
4. After parsing completes, verify that `parsed-resume.json` was created in the session directory.
5. If parsing failed (file contains `"error": true` or was not created):
   - Display the error message from `parsed-resume.json` if available.
   - Otherwise display: "Resume parsing failed. Please check that your resume file is a valid PDF or Markdown document."
   - Stop execution.

### Step 4: Run ATS Analysis

Delegate to the **ats-analyzer** subagent to perform the ATS compatibility analysis.

Provide the ats-analyzer with:
- The session directory path (where `parsed-resume.json` and the original resume file are located)
- The ats-analyzer will read `parsed-resume.json` for structured data and the original file for format-level analysis

The ats-analyzer will write its output to `ats-analysis.json` in the session directory.

### Step 5: Present Results Summary

After the ats-analyzer completes, read `ats-analysis.json` from the session directory and present a conversational summary to the user.

**Summary format:**

1. **Overall ATS Score** with letter grade (use the grade mapping from CLAUDE.md)
2. **Dimension Breakdown** -- show each of the four dimension scores:
   - Parsability (30% weight)
   - Format Compliance (25% weight)
   - Keyword Readiness (25% weight)
   - Structure Quality (20% weight)
3. **Critical Issues** -- if any critical issues were found, highlight them prominently as they require immediate attention
4. **Top Recommendations** -- list the 3-5 highest-impact recommendations across all dimensions
5. **Session output path** -- tell the user where the full analysis was saved

Keep the summary concise and actionable. Highlight what is working well alongside what needs improvement.
