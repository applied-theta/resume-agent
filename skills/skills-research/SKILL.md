---
name: skills-research
description: >
  Skills and market intelligence analysis -- researches current demand for
  skills on a resume, verifies terminology accuracy, identifies trending
  skills, and provides market-aware optimization recommendations.
argument-hint: "[resume-path]"
disable-model-invocation: true
allowed-tools: Agent, Read, Bash, Glob
---

# Skills Research

Run a market intelligence analysis on a resume. This command evaluates market demand for the candidate's skills, verifies technology terminology accuracy, identifies trending skills for the target role, and produces prioritized recommendations backed by source citations.

## Usage

```
/skills-research                        → scans workspace/input/
/skills-research /path/to/resume.pdf    → copies resume, then analyzes
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

A parsed resume is required before skills research can run. Delegate to the **resume-parser** subagent to parse the resume.

**Copy input file (if path argument provided):**
If the user provided a resume file path as an argument:
1. Ensure the input directory exists: `mkdir -p workspace/input`
2. Copy the file: `cp <provided-path> workspace/input/`
3. If the copy fails (file not found, permission denied), report the error and stop.

1. Look for a resume file in `workspace/input/` (PDF or Markdown).
2. If no resume file is found in `workspace/input/`:
   - Display a clear message to the user:
     > No resume found. Please provide a resume in one of two ways:
     > 1. **Direct path**: `/skills-research /path/to/resume.pdf`
     > 2. **Workspace**: Place a PDF or Markdown file in `workspace/input/` and run `/skills-research`
   - Stop execution.
3. If a resume file is found, delegate to the **resume-parser** agent, providing the file path and session directory.
4. After parsing completes, verify that `parsed-resume.json` was created in the session directory.
5. If parsing failed (file contains `"error": true` or was not created):
   - Display the error message from `parsed-resume.json` if available.
   - Otherwise display: "Resume parsing failed. Please check that your resume file is a valid PDF or Markdown document."
   - Stop execution.

### Step 4: Run Skills Research

Delegate to the **skills-research** subagent to perform the market intelligence analysis.

Provide the skills-research agent with:
- The session directory path (where `parsed-resume.json` is located)
- The skills-research agent will read `parsed-resume.json` for structured resume data and optionally check for a job description in `workspace/input/` for target role context

The skills-research agent will write its output to `skills-research.json` in the session directory.

**If the skills-research agent fails or does not produce output:**
> Skills research analysis encountered an issue. Please check the session directory for details: `workspace/output/{session}/`

### Step 5: Present Results Summary

After the skills-research agent completes, read `skills-research.json` from the session directory and present a conversational summary to the user.

**Summary format:**

1. **Overall Market Intelligence Score** with letter grade (use the grade mapping from CLAUDE.md)
2. **Target Role** -- report the detected target role and how it was determined (from JD or inferred from resume)
3. **Market Demand Overview** -- summarize the skill assessments: how many skills are High/Moderate/Low/Emerging demand, and highlight the top high-demand skills. Note any skills with Declining trends.
4. **Terminology Issues** -- list any skills with incorrect terminology from the `terminology_verification` array where `is_correct` is false, showing the original term and the correct form
5. **Trending Skills** -- list the trending skills identified for the target role that are not on the resume, with relevance context
6. **Top Recommendations** -- list the 3-5 highest-priority recommendations from the `recommendations.high` array, followed by notable medium-priority items
7. **Session output path** -- tell the user where the full analysis was saved

Keep the summary concise and actionable. Highlight what is strong in the candidate's skill profile alongside what needs improvement.
