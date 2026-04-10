---
name: parse-resume
description: >
  Resume parsing -- extracts contact info, experience, education, skills,
  projects, and metadata from a PDF or Markdown resume into structured JSON.
argument-hint: "[resume-path]"
disable-model-invocation: true
allowed-tools: Agent, Read, Bash, Glob
---

# Parse Resume

Parse a resume file into structured JSON. This command runs the resume-parser subagent to extract contact information, experience, education, skills, projects, and metadata into a `parsed-resume.json` file.

## Prerequisites

- Read `${CLAUDE_PLUGIN_ROOT}/skills/shared/workspace-resolution.md` for workspace layout and path conventions

## Usage

```
/parse-resume                    → scans {workspace}/{slug}/input/
/parse-resume /path/to/resume.pdf → copies resume, then parses
```

## Steps

### Step 1: Copy Input File and Locate the Resume

#### Copy Input File (if path argument provided)

If the user provided a resume file path as an argument:
1. Ensure the input directory exists: `mkdir -p {workspace}/{slug}/input`
2. Copy the file: `cp <provided-path> {workspace}/{slug}/input/`
3. If the copy fails (file not found, permission denied), report the error and stop.

#### Locate the Resume

Look in `{workspace}/{slug}/input/` for a resume file. Supported formats are PDF (`.pdf`) and Markdown (`.md` or `.markdown`).

Use `Glob` to search for files:
- `{workspace}/{slug}/input/*.pdf`
- `{workspace}/{slug}/input/*.md`
- `{workspace}/{slug}/input/*.markdown`

**If no resume file is found:**
Report to the user:
> No resume file found. Please provide a resume in one of two ways:
>
> 1. **Direct path**: `/parse-resume /path/to/resume.pdf`
> 2. **Workspace**: Place a PDF or Markdown file in `{workspace}/{slug}/input/` and run `/parse-resume`

Stop processing.

**If multiple resume files are found:**
List the files and ask the user which one to parse. If only one file is found, use it automatically.

### Step 2: Validate File Format

Check the file extension of the located resume file:
- `.pdf` -- supported, proceed
- `.md` or `.markdown` -- supported, proceed
- Any other extension -- report to the user:
  > Unsupported file format: `{filename}`. Please provide a resume in PDF (`.pdf`) or Markdown (`.md`) format.

  Stop processing.

### Step 3: Create Session Directory

Generate a timestamped session directory for output:

1. Get the current timestamp in the format `YYYY-MM-DD-HHMMSS`.
2. Create the directory `{workspace}/{slug}/sessions/{timestamp}/`.
3. If a session directory was already created in this conversation, reuse it instead of creating a new one.

### Step 4: Delegate to Resume Parser

Invoke the `resume-parser` subagent with:
- The path to the resume file found in Step 1
- The session directory name from Step 3

The subagent will:
- Extract text from PDF (using `${CLAUDE_PLUGIN_ROOT}/scripts/extract-pdf-text.py`) or read Markdown directly
- Identify and classify resume sections
- Extract contact information, experience, education, skills, projects, and additional sections
- Write structured JSON output to `{workspace}/{slug}/sessions/{session}/parsed-resume.json`

### Step 5: Report Results

After the resume-parser subagent completes, report the results to the user.

**On success**, provide a summary including:
- The file that was parsed
- The session directory where output was written
- A summary of extracted sections:
  - Contact information found (name, and which optional fields were detected)
  - Number of experience entries
  - Number of education entries
  - Skills categories populated
  - Number of projects (if any)
  - Any additional sections detected
  - Metadata highlights (format, page count, structure quality)

**On error** (subagent reports an error in `parsed-resume.json`), relay the error message to the user with guidance on how to fix it.

## Example Usage

```
/parse-resume
/parse-resume ~/Documents/resume.pdf
```

The user either provides a direct file path or places their resume in `{workspace}/{slug}/input/` and runs this command. The system parses the resume and reports what was extracted.
