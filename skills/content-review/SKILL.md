---
name: content-review
description: >
  Content quality analysis -- scores every bullet point on a 1-5 scale,
  detects weak patterns, audits quantification, evaluates action verbs,
  and assesses narrative coherence across the resume.
argument-hint: "[resume-path]"
disable-model-invocation: true
allowed-tools: Agent, Read, Bash, Glob
---

# Content Review

Run a content quality analysis on a resume. This command evaluates bullet point effectiveness, action verb strength, quantification coverage, and narrative coherence, producing a comprehensive content quality assessment with per-bullet scoring.

## Prerequisites

- Read `${CLAUDE_PLUGIN_ROOT}/skills/shared/workspace-resolution.md` for workspace layout and path conventions

## Usage

```
/content-review                        → scans {workspace}/{slug}/input/
/content-review /path/to/resume.pdf    → copies resume, then analyzes
```

## Procedure

### Step 1: Determine the Session Directory

Identify the current session directory under `{workspace}/{slug}/sessions/`. If a session directory already exists from a previous command in this conversation, reuse it. Otherwise, create a new timestamped session directory: `{workspace}/{slug}/sessions/YYYY-MM-DD-HHMMSS/`.

### Step 2: Check for Parsed Resume

Check whether `parsed-resume.json` exists in the session directory.

- Use `Glob` to look for `{workspace}/{slug}/sessions/*/parsed-resume.json` if no session is established, or check the specific session directory. Also check `{workspace}/output/*/parsed-resume.json` as a legacy fallback.
- If `parsed-resume.json` exists and does not contain an `"error": true` field, proceed to Step 4.
- If `parsed-resume.json` does not exist, proceed to Step 3.

### Step 3: Parse the Resume First

A parsed resume is required before content analysis can run. Delegate to the **resume-parser** subagent to parse the resume.

**Copy input file (if path argument provided):**
If the user provided a resume file path as an argument:
1. Ensure the input directory exists: `mkdir -p {workspace}/{slug}/input`
2. Copy the file: `cp <provided-path> {workspace}/{slug}/input/`
3. If the copy fails (file not found, permission denied), report the error and stop.

1. Look for a resume file in `{workspace}/{slug}/input/` (PDF or Markdown).
2. If no resume file is found in `{workspace}/{slug}/input/`:
   - Display a clear message to the user:
     > No resume found. Please provide a resume in one of two ways:
     > 1. **Direct path**: `/content-review /path/to/resume.pdf`
     > 2. **Workspace**: Place a PDF or Markdown file in `{workspace}/{slug}/input/` and run `/content-review`
   - Stop execution.
3. If a resume file is found, delegate to the **resume-parser** agent, providing the file path and session directory.
4. After parsing completes, verify that `parsed-resume.json` was created in the session directory.
5. If parsing failed (file contains `"error": true` or was not created):
   - Display the error message from `parsed-resume.json` if available.
   - Otherwise display: "Resume parsing failed. Please check that your resume file is a valid PDF or Markdown document."
   - Stop execution.

### Step 4: Run Content Analysis

Delegate to the **content-analyst** subagent to perform the content quality analysis.

Provide the content-analyst with:
- The session directory path (where `parsed-resume.json` is located)
- The content-analyst will read `parsed-resume.json` for structured resume data including experience entries with bullet points, summary, skills, and education sections

The content-analyst will write its output to `content-analysis.json` in the session directory.

### Step 5: Present Results Summary

After the content-analyst completes, read `content-analysis.json` from the session directory and present a conversational summary to the user.

**Summary format:**

1. **Overall Content Quality Score** with letter grade (use the grade mapping from CLAUDE.md)
2. **Bullet Score Distribution** -- summarize the spread of bullet scores across the 1-5 scale (e.g., how many scored 5, 4, 3, 2, 1) and the average score
3. **Narrative Coherence** -- report the coherence score and whether career progression is clear and professional identity is defined
4. **Key Content Issues** -- highlight the most common patterns found:
   - Weak action verbs flagged
   - Bullets lacking quantification
   - Passive voice or filler phrases detected
5. **Top Recommendations** -- list the 3-5 highest-impact improvements from the `top_improvements` array, prioritized by potential score improvement
6. **Session output path** -- tell the user where the full analysis was saved

Keep the summary concise and actionable. Highlight what is working well alongside what needs improvement.
