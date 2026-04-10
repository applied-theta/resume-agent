---
name: export-resume
description: >
  Resume export -- converts an optimized resume markdown file to a professionally
  formatted PDF or Word document. Supports PDF presets (Modern, Classic, Compact,
  Harvard) with Typst or Python fallback, and Word presets (Professional, Simple,
  Creative, Academic) with custom template support. Use this skill whenever the
  user wants to export, download, convert, or save their resume as PDF or DOCX.
argument-hint: "[resume-path]"
allowed-tools: Read, Bash, Glob, AskUserQuestion
---

# Export Resume

Convert a resume markdown file to a professionally formatted PDF or Word (DOCX) document. Replaces the former `/export-pdf` skill with unified format selection.

## Prerequisites

- Read `${CLAUDE_PLUGIN_ROOT}/skills/shared/workspace-resolution.md` for workspace layout and path conventions

## Usage

```
/export-resume                           -> auto-detects most recent session's optimized-resume.md
/export-resume /path/to/resume.md        -> converts the specified markdown file
```

## Steps

### Step 1: Locate the Resume Markdown

#### If a path argument was provided:

1. Verify the file exists. If not, report:
   > **Error:** File not found: `{path}`
   >
   > Please check the path and try again.
   Stop processing.
2. Use the provided path as the input file.
3. Determine the output directory:
   - If the file is inside a session directory (`{workspace}/{slug}/sessions/*/` or legacy `{workspace}/output/*/`), write the export to that same session directory.
   - Otherwise, write the export alongside the source file (same directory).

#### If no path argument was provided:

1. Use `Glob` to search for `{workspace}/*/sessions/*/optimized-resume.md`. Also check `{workspace}/output/*/optimized-resume.md` as a legacy fallback.
2. If multiple sessions exist, use the most recent one (by timestamp in the directory name).
3. If a session directory was already established in this conversation, prefer that one.
4. Use the found `optimized-resume.md` as the input file. The export will be written to the same session directory.

**If no file is found:**

Display to the user:

> No optimized resume found. Please provide a file path:
>
> `/export-resume /path/to/resume.md`
>
> Or run `/optimize-resume` first to generate an optimized resume.

Stop processing.

### Step 2: Select Export Format

Prompt the user for format selection via `AskUserQuestion`:

> **Which format would you like to export?**
>
> 1. **PDF** -- Professional PDF with native text layer for ATS compatibility
> 2. **DOCX** -- Word document, ideal for ATS submission and further editing

If the user does not specify, default to **PDF**.

Based on the user's selection, proceed to the appropriate format pipeline:
- **PDF** -> Step 3A (PDF Pipeline)
- **DOCX** -> Step 3B (DOCX Pipeline)

---

### Step 3A: PDF Pipeline

#### Step 3A.1: Select PDF Style Preset

Present the style preset selection to the user via `AskUserQuestion`:

> **Which style preset would you like for your PDF?**
>
> 1. **Modern** (Recommended) -- Clean, contemporary sans-serif design with subtle accent color and balanced whitespace
> 2. **Classic** -- Traditional serif design with conservative colors and generous margins
> 3. **Compact** -- Dense, space-efficient design that maximizes content per page
> 4. **Harvard** -- Traditional academic format with serif font, monochrome black-only color, and generous margins

Default to "Modern" if the user doesn't specify.

#### Step 3A.2: Offer PDF Customization

After preset selection, ask the user if they want to customize the styling via `AskUserQuestion`:

> **Would you like to customize the styling?**
>
> 1. **Use preset defaults** (Recommended) -- Apply the selected preset as-is
> 2. **Customize** -- Fine-tune font, color, margins, page size, and spacing

#### If the user chooses "Customize":

Present customization options one at a time via `AskUserQuestion`:

**Font family:**
> **Which font family?**
>
> 1. **Inter** -- Modern sans-serif (default for Modern preset)
> 2. **EB Garamond** -- Elegant serif (default for Classic preset)
> 3. **Source Sans 3** -- Clean sans-serif (default for Compact preset)
> 4. **Lato** -- Friendly modern sans-serif

**Accent color:**
> **Which accent color for section headings?**
>
> 1. **Navy** (#2B547E) (Recommended)
> 2. **Teal** (#008080)
> 3. **Charcoal** (#36454F)
> 4. **Burgundy** (#800020)

The user may also type a custom hex color.

**Page size:**
> **Which page size?**
>
> 1. **US Letter** (8.5" x 11") (Recommended)
> 2. **A4** (210mm x 297mm)

**Margins:**
> **Which margin size?**
>
> 1. **Standard** (0.75") (Recommended)
> 2. **Narrow** (0.5") -- More content space
> 3. **Wide** (1") -- More whitespace

**Line spacing:**
> **Which line spacing?**
>
> 1. **Standard** (1.15) (Recommended)
> 2. **Tight** (1.0) -- More compact
> 3. **Relaxed** (1.3) -- More breathing room

**Section spacing:**
> **Which section spacing?**
>
> 1. **Standard** (Recommended)
> 2. **Compact** -- Tighter sections
> 3. **Generous** -- More space between sections

**PDF/A compliance (advanced):**
> **Enable PDF/A-2b compliance?**
>
> 1. **No** (Recommended) -- Standard PDF output
> 2. **Yes** -- PDF/A-2b archival format (for enterprise/government submissions)

#### Step 3A.3: Generate PDF

Assemble the CLI arguments based on the user's selections and run the **environment-aware PDF router** script. The router automatically selects the best available PDF backend (Typst when available in Claude Code, Python fallback in Cowork VM). No manual backend selection is needed.

```bash
${CLAUDE_PLUGIN_ROOT}/scripts/run-python.sh ${CLAUDE_PLUGIN_ROOT}/scripts/md_to_pdf_router.py <input-path> <output-path> --preset <preset> [--font <font>] [--color <color>] [--margin <margin>] [--page-size <size>] [--line-spacing <spacing>] [--section-spacing <spacing>] [--pdf-a]
```

Where `<output-path>` follows the pattern `{original-stem}-optimized.pdf` in the appropriate directory.

The router handles all backend selection transparently:
- If Typst is available, uses the high-quality Typst rendering pipeline
- If Typst is unavailable, uses the Python (fpdf2) fallback renderer
- If Typst exists but fails at runtime, automatically falls back to Python with a warning in stderr

**If the script fails (non-zero exit code):** Report the error from stderr to the user:

> **Export failed:** {error message from stderr}
>
> Please check that the markdown file is valid and try again.

Stop processing.

#### Step 3A.4: ATS Validation

After a successful PDF export, automatically run ATS validation to verify the generated file is parseable by applicant tracking systems. This step must not block file delivery — if validation fails or errors out, the export is still considered successful.

Run the validation script with a timeout of 30 seconds:

```bash
timeout 30 ${CLAUDE_PLUGIN_ROOT}/scripts/run-python.sh ${CLAUDE_PLUGIN_ROOT}/scripts/validate_pdf.py <output-path> <input-path>
```

Where `<output-path>` is the generated PDF and `<input-path>` is the source markdown file.

**Interpreting results:**

- **Exit code 0 (validation passed):** The PDF passed all ATS checks. Record the result for the success report.
- **Exit code 1 (validation failed):** The PDF was exported but validation found issues. Parse the script's stdout for specific issues. Record them for the report.
- **Script error (non-zero exit other than 1, or stderr with no stdout):** The validation script itself failed. Warn the user that validation could not be completed, but do not treat this as an export failure.
- **Timeout (command killed after 30s):** Warn the user that validation timed out, but do not treat this as an export failure.

Proceed to Step 3A.5 regardless of the validation outcome.

#### Step 3A.5: Report PDF Results

On success, report to the user. Include the ATS validation result in the report.

**If validation passed:**

> **PDF exported successfully!**
>
> - **File:** `{output-path}`
> - **Size:** {file-size}
> - **Preset:** {preset name}
> - **Customizations:** {list any overrides, or "None (preset defaults)"}
>
> **ATS Validation: Passed** -- All section headings, content, and text layer verified. The PDF is ATS-compatible.

**If validation failed (issues found):**

> **PDF exported successfully!**
>
> - **File:** `{output-path}`
> - **Size:** {file-size}
> - **Preset:** {preset name}
> - **Customizations:** {list any overrides, or "None (preset defaults)"}
>
> **ATS Validation: Issues Found**
> The file was exported successfully, but validation detected potential ATS compatibility issues:
> {list each issue from the validation output}
>
> Please review the exported file to confirm it displays correctly. You may want to open it and verify the content before submitting to an ATS.

**If validation could not run (script error or timeout):**

> **PDF exported successfully!**
>
> - **File:** `{output-path}`
> - **Size:** {file-size}
> - **Preset:** {preset name}
> - **Customizations:** {list any overrides, or "None (preset defaults)"}
>
> **ATS Validation: Could not complete** -- {reason: script error or timeout}. The file was exported successfully. You may want to open it and verify the content displays correctly before submitting to an ATS.

---

### Step 3B: DOCX Pipeline

#### Step 3B.1: Select DOCX Preset or Template

Present the Word preset selection to the user via `AskUserQuestion`:

> **Which Word preset would you like?**
>
> 1. **Professional** (Recommended) -- Clean business formatting with balanced typography
> 2. **Simple** -- Minimal styling for maximum ATS compatibility
> 3. **Creative** -- More visual design elements with color accents
> 4. **Academic** -- CV-style format for research and education roles
> 5. **Custom template** -- Provide your own .docx template file

Default to "Professional" if the user doesn't specify.

#### If the user chooses "Custom template":

Ask for the template path via `AskUserQuestion`:

> **Please provide the path to your .docx template file:**

Verify the template file exists. If not, report:
> **Template not found:** `{path}`
>
> Would you like to select a preset instead?

Then re-present the preset selection (options 1-4 only).

#### Step 3B.2: Generate DOCX

Assemble the CLI arguments and run the conversion script:

```bash
${CLAUDE_PLUGIN_ROOT}/scripts/run-python.sh ${CLAUDE_PLUGIN_ROOT}/scripts/md-to-docx.py <input-path> <output-path> --preset <preset> [--template <template-path>]
```

Where `<output-path>` follows the pattern `{original-stem}-optimized.docx` in the appropriate directory.

**If the script fails (non-zero exit code):** Report the error from stderr to the user:

> **Export failed:** {error message from stderr}
>
> Please check that the markdown file is valid and try again.

Stop processing.

#### Step 3B.3: ATS Validation

After a successful DOCX export, automatically run ATS validation to verify the generated file preserves all content from the source markdown. This step must not block file delivery — if validation fails or errors out, the export is still considered successful.

Run the validation script with a timeout of 30 seconds:

```bash
timeout 30 ${CLAUDE_PLUGIN_ROOT}/scripts/run-python.sh ${CLAUDE_PLUGIN_ROOT}/scripts/validate_docx.py <output-path> <input-path>
```

Where `<output-path>` is the generated DOCX and `<input-path>` is the source markdown file.

**Interpreting results:**

- **Exit code 0 (validation passed):** The DOCX passed all checks. Record the result for the success report.
- **Exit code 1 (validation failed):** The DOCX was exported but validation found issues. Parse the script's stdout for specific issues (lines starting with `  - `). Record them for the report.
- **Script error (non-zero exit other than 1, or stderr with no stdout):** The validation script itself failed. Warn the user that validation could not be completed, but do not treat this as an export failure.
- **Timeout (command killed after 30s):** Warn the user that validation timed out, but do not treat this as an export failure.

Proceed to Step 3B.4 regardless of the validation outcome.

#### Step 3B.4: Report DOCX Results

On success, report to the user. Include the ATS validation result in the report.

**If a preset was used and validation passed:**

> **Word document exported successfully!**
>
> - **File:** `{output-path}`
> - **Size:** {file-size}
> - **Preset:** {preset name}
>
> **ATS Validation: Passed** -- All sections and content verified. The document is ATS-compatible.

**If a preset was used and validation failed (issues found):**

> **Word document exported successfully!**
>
> - **File:** `{output-path}`
> - **Size:** {file-size}
> - **Preset:** {preset name}
>
> **ATS Validation: Issues Found**
> The file was exported successfully, but validation detected potential issues:
> {list each issue from the validation output}
>
> Please review the exported file to confirm it displays correctly. You may want to open it and verify the content before submitting to an ATS.

**If a preset was used and validation could not run:**

> **Word document exported successfully!**
>
> - **File:** `{output-path}`
> - **Size:** {file-size}
> - **Preset:** {preset name}
>
> **ATS Validation: Could not complete** -- {reason: script error or timeout}. The file was exported successfully. You may want to open it and verify the content displays correctly before submitting to an ATS.

**If a custom template was used and validation passed:**

> **Word document exported successfully!**
>
> - **File:** `{output-path}`
> - **Size:** {file-size}
> - **Template:** `{template-path}`
>
> **ATS Validation: Passed** -- All sections and content verified. The document is ATS-compatible.

**If a custom template was used and validation failed (issues found):**

> **Word document exported successfully!**
>
> - **File:** `{output-path}`
> - **Size:** {file-size}
> - **Template:** `{template-path}`
>
> **ATS Validation: Issues Found**
> The file was exported successfully, but validation detected potential issues:
> {list each issue from the validation output}
>
> Please review the exported file to confirm it displays correctly. You may want to open it and verify the content before submitting to an ATS.

**If a custom template was used and validation could not run:**

> **Word document exported successfully!**
>
> - **File:** `{output-path}`
> - **Size:** {file-size}
> - **Template:** `{template-path}`
>
> **ATS Validation: Could not complete** -- {reason: script error or timeout}. The file was exported successfully. You may want to open it and verify the content displays correctly before submitting to an ATS.

---

## Edge Cases

- **No session found and no path provided:** Prompt user to provide a file path or run `/optimize-resume` first.
- **Multiple sessions exist:** Use the most recent session with `optimized-resume.md` (by timestamp in directory name).
- **Explicit path to non-session markdown:** Write export alongside the source file.
- **Invalid markdown structure:** Report warnings from stderr but still attempt export.
- **Script outputs warnings to stderr but exits 0:** Relay warnings to the user before the success report.
- **User provides hex color in PDF customization:** Pass directly to `--color` flag.
- **Custom DOCX template has incompatible styles:** Fall back to preset styling with a warning.

## Example Usage

```
/export-resume
/export-resume ~/Documents/my-resume.md
/export-resume {workspace}/{slug}/sessions/2026-02-27-143000/optimized-resume.md
```
