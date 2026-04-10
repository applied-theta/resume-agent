# Workspace Resolution

How to resolve the workspace root, determine per-resume directory structure, and maintain session context across skills.

## Workspace Root

The workspace root is the base directory for all resume data (inputs, sessions, exports).

### Resolution Order (highest priority first)

1. **Explicit argument**: `--workspace /path/to/dir` provided by the user on the skill invocation
2. **Config file**: Read `${CLAUDE_PLUGIN_ROOT}/.env-config` and extract the `WORKSPACE_ROOT` value
3. **Fallback**: `${CLAUDE_PLUGIN_ROOT}/workspace/`

### How to Read the Workspace Root

```bash
# Read WORKSPACE_ROOT from .env-config
cat ${CLAUDE_PLUGIN_ROOT}/.env-config
# Look for the WORKSPACE_ROOT=... line
```

If the file does not exist or `WORKSPACE_ROOT` is not set, use: `${CLAUDE_PLUGIN_ROOT}/workspace/`

Store the resolved path as `{workspace}` for use throughout the skill.


## Per-Resume Directory Structure

Each resume is stored under a slug-named directory within the workspace root:

```
{workspace}/
├── <resume-slug>/
│   ├── input/
│   │   ├── <resume-file>        (PDF or Markdown)
│   │   └── <jd-file>            (optional job description)
│   └── sessions/
│       └── YYYY-MM-DD-HHMMSS/
│           ├── parsed-resume.json
│           ├── ats-analysis.json
│           ├── content-analysis.json
│           ├── keyword-analysis.json
│           ├── strategy-analysis.json
│           ├── skills-research.json
│           ├── scores-summary.json
│           ├── analysis-report.md
│           ├── optimized-resume.md
│           ├── change-manifest.json
│           ├── optimization-report.md
│           ├── *-optimized.pdf
│           ├── *-optimized.docx
│           └── post-opt/
│               └── (re-analysis files)
```


## Resume Slug Derivation

Derive the slug from the resume filename:

1. Remove the file extension (`.pdf`, `.md`, `.markdown`)
2. Convert to lowercase
3. Replace spaces, underscores, and special characters with hyphens
4. Collapse consecutive hyphens to a single hyphen
5. Remove leading/trailing hyphens
6. Truncate to 50 characters

**Examples:**
- `John_Doe_Resume.pdf` -> `john-doe-resume`
- `resume (3).pdf` -> `resume-3`
- `My Resume - Senior Engineer.md` -> `my-resume-senior-engineer`

### Collision Handling

If a slug directory already exists and its `input/` contains a **different** resume file (different name or content), append a numeric suffix: `resume-2`, `resume-3`, etc.

If the same resume file is being re-analyzed, reuse the existing slug directory.

### Rename Option

After deriving the slug, briefly mention it to the user:

> Resume project: `{slug}/`

If the user wants a different name, they can say so. Otherwise proceed with the auto-derived slug.


## Active Resume Context

Within a conversation, once a resume slug and session directory are established:

- **Remember** both the resume slug and session path for the rest of the conversation
- **Reuse** them for all subsequent skills (optimize-resume, export-resume, individual analyses)
- A new slug/session is only created if the user explicitly provides a **different** resume file

This context is maintained naturally through conversation memory. The first skill that runs (usually `analyze-resume`) establishes the context, and subsequent skills inherit it.


## Session Discovery

### Finding Sessions for the Active Resume (slug is known)

```
Glob {workspace}/{slug}/sessions/*/parsed-resume.json
```

If multiple sessions exist, use the most recent one (by timestamp in the directory name), unless a session was already established in the conversation.

### Finding Sessions Across All Resumes (slug is not known)

```
Glob {workspace}/*/sessions/*/parsed-resume.json
```

Use the most recent session across all resume slugs. Tell the user which resume was selected.

### Finding Optimized Resumes

```
Glob {workspace}/{slug}/sessions/*/optimized-resume.md       (slug known)
Glob {workspace}/*/sessions/*/optimized-resume.md             (slug unknown)
```


## Backwards Compatibility (Legacy Layout)

If the workspace contains a legacy `output/` directory (from the old flat structure):

```
{workspace}/output/*/parsed-resume.json
```

Skills should check for sessions in this location as a **fallback** after checking the new per-resume structure. When a legacy session is found, tell the user:

> Found sessions in the legacy workspace layout. New sessions will use the per-resume directory structure under `{workspace}/{slug}/`.

New sessions are always created under the new `{slug}/sessions/` structure.


## Common Paths Reference

| Purpose | Pattern |
|---------|---------|
| Resume input directory | `{workspace}/{slug}/input/` |
| Create new session | `{workspace}/{slug}/sessions/YYYY-MM-DD-HHMMSS/` |
| Find parsed resumes (active) | `{workspace}/{slug}/sessions/*/parsed-resume.json` |
| Find parsed resumes (all) | `{workspace}/*/sessions/*/parsed-resume.json` |
| Find optimized resumes | `{workspace}/*/sessions/*/optimized-resume.md` |
| Legacy sessions (fallback) | `{workspace}/output/*/parsed-resume.json` |
| Post-optimization re-analysis | `{workspace}/{slug}/sessions/{session}/post-opt/` |
