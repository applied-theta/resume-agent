---
description: Runs keyword alignment analysis against a job description. Accepts optional file paths for resume and JD.
argument-hint: "[resume-path] [--jd path|url]"
allowed-tools: Agent, Read, Bash, Glob, WebFetch
---

# Keyword Align

Run a keyword alignment analysis between a resume and a target job description. This command evaluates how well the resume matches the JD by decomposing requirements, classifying keyword matches by confidence level, identifying critical gaps, and generating prioritized optimization actions with specific placement guidance.

A job description is **required** for this command. The JD can be provided as a file in `workspace/input/`, pasted inline in the conversation, as a URL, or via the `--jd` argument.

## Usage

```
/keyword-align                                              → scans workspace/input/ for resume and JD
/keyword-align /path/to/resume.pdf                          → copies resume, scans for JD
/keyword-align /path/to/resume.pdf --jd /path/to/jd.txt     → copies both, then analyzes
/keyword-align --jd https://example.com/job/12345            → scans for resume, fetches JD URL
```

## Procedure

### Step 1: Determine the Session Directory

Identify the current session directory under `workspace/output/`. If a session directory already exists from a previous command in this conversation, reuse it. Otherwise, create a new timestamped session directory: `workspace/output/YYYY-MM-DD-HHMMSS/`.

### Step 2: Locate the Job Description

A job description is required for keyword alignment analysis. Check for a JD from these sources, in order:

1. **`--jd` file path**: The user provided a file path via `--jd`. Copy it to `workspace/input/`: `mkdir -p workspace/input && cp <provided-path> workspace/input/`. If the copy fails, report the error and stop.
2. **Inline**: The user pasted or typed the JD directly in the conversation.
3. **`--jd` URL**: The user provided a URL via `--jd` or inline. Use `WebFetch` to retrieve the content.
   - After fetching, verify that the content looks like a job description (contains job-related terms such as responsibilities, requirements, qualifications, experience, skills, etc.).
   - If the fetched content does not appear to be a job description (e.g., login page, error page, unrelated content), display:
     > Could not extract a job description from the provided URL. The page content does not appear to contain a job posting. Please provide the job description as a file or paste it directly.
   - Stop execution.
4. **File**: Look for a JD file in `workspace/input/`. Search for files with names containing "jd", "job", or "description" (case-insensitive), or `.txt` files that are not the resume.

**If no JD is found from any source:**

Display a clear message to the user:
> No job description provided. Keyword alignment analysis requires a job description to compare against your resume.
>
> You can provide a JD in one of three ways:
> 1. **File**: Place a job description file in `workspace/input/` (name it with "jd", "job", or "description" in the filename)
> 2. **Inline**: Paste the job description text directly in the chat, then run `/keyword-align` again
> 3. **URL**: Provide a URL to the job posting (e.g., `/keyword-align https://example.com/job/12345`)

Stop execution.

### Step 3: Check for Parsed Resume

Check whether `parsed-resume.json` exists in the session directory.

- Use `Glob` to look for `workspace/output/*/parsed-resume.json` if no session is established, or check the specific session directory.
- If `parsed-resume.json` exists and does not contain an `"error": true` field, proceed to Step 5.
- If `parsed-resume.json` does not exist, proceed to Step 4.

### Step 4: Parse the Resume First

A parsed resume is required before keyword alignment analysis can run. Delegate to the **resume-parser** subagent to parse the resume.

**Copy input file (if resume path argument provided):**
If the user provided a resume file path as an argument (not a `--jd` path):
1. Ensure the input directory exists: `mkdir -p workspace/input`
2. Copy the file: `cp <provided-path> workspace/input/`
3. If the copy fails (file not found, permission denied), report the error and stop.

1. Look for a resume file in `workspace/input/` (PDF or Markdown).
2. If no resume file is found in `workspace/input/`:
   - Display a clear message to the user:
     > No resume found. Please provide a resume in one of two ways:
     > 1. **Direct path**: `/keyword-align /path/to/resume.pdf --jd /path/to/jd.txt`
     > 2. **Workspace**: Place a PDF or Markdown file in `workspace/input/` and run `/keyword-align`
   - Stop execution.
3. If a resume file is found, delegate to the **resume-parser** agent, providing the file path and session directory.
4. After parsing completes, verify that `parsed-resume.json` was created in the session directory.
5. If parsing failed (file contains `"error": true` or was not created):
   - Display the error message from `parsed-resume.json` if available.
   - Otherwise display: "Resume parsing failed. Please check that your resume file is a valid PDF or Markdown document."
   - Stop execution.

### Step 5: Run Keyword Alignment Analysis

Delegate to the **keyword-optimizer** subagent to perform the keyword alignment analysis.

Provide the keyword-optimizer with:
- The session directory path (where `parsed-resume.json` is located)
- The job description content (inline text, fetched URL content, or the file path in `workspace/input/`)

The keyword-optimizer will:
- Load the keyword alignment methodology from `${CLAUDE_PLUGIN_ROOT}/skills/keyword-alignment/SKILL.md`
- Load industry cluster data from `${CLAUDE_PLUGIN_ROOT}/skills/keyword-alignment/industry-clusters/`
- Decompose the JD into requirement categories
- Build a keyword inventory from the parsed resume
- Classify matches by confidence tier
- Compute the overall match rate
- Identify critical gaps
- Generate prioritized optimization actions
- Write output to `keyword-analysis.json` in the session directory

### Step 6: Present Results Summary

After the keyword-optimizer completes, read `keyword-analysis.json` from the session directory and present a conversational summary to the user.

**Summary format:**

1. **Match Rate** with assessment level -- display the overall match rate percentage and the assessment (Excellent/Good/Moderate/Weak/Poor based on the ranges below):
   - 85-100%: Excellent
   - 70-84%: Good
   - 50-69%: Moderate
   - 30-49%: Weak
   - 0-29%: Poor
2. **Match Breakdown** -- summarize how many exact matches, high-confidence semantic matches, and medium-confidence semantic matches were found
3. **Critical Gaps** -- list the critical and high-priority gaps (required skills missing from the resume), ordered by priority
4. **Top Optimization Actions** -- list the 3-5 highest-priority optimization actions with their recommended placement locations
5. **Session output path** -- tell the user where the full analysis was saved

Keep the summary concise and actionable. Highlight what is matching well alongside what needs attention.

**If the keyword-optimizer fails or does not produce output:**
> Keyword alignment analysis encountered an issue. Please check the session directory for details: `workspace/output/{session}/`
