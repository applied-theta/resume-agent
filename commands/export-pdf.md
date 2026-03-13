---
argument-hint: "[resume-path]"
description: Export an optimized resume markdown file to a professionally formatted, ATS-compatible PDF with style presets and customization options.
allowed-tools: Read, Bash, Glob, AskUserQuestion
---

# Export PDF

Convert a resume markdown file to a professionally formatted PDF using Typst. Provides 4 style presets (Classic, Modern, Compact, Harvard) with full customization of fonts, colors, margins, page size, and spacing.

## Usage

```
/export-pdf                           → auto-detects most recent session's optimized-resume.md
/export-pdf /path/to/resume.md        → converts the specified markdown file
```

## Steps

### Step 1: Locate the Resume Markdown

#### If a path argument was provided:

1. Verify the file exists. If not, report the error and stop.
2. Use the provided path as the input file.
3. Determine the output directory:
   - If the file is inside a session directory (`workspace/output/*/`), write the PDF to that same session directory.
   - Otherwise, write the PDF alongside the source file (same directory).

#### If no path argument was provided:

1. Use `Glob` to search for `workspace/output/*/optimized-resume.md`.
2. If multiple sessions exist, use the most recent one (by timestamp in the directory name).
3. If a session directory was already established in this conversation, prefer that one.
4. Use the found `optimized-resume.md` as the input file. The PDF will be written to the same session directory.

**If no file is found:**

Display to the user:
> No optimized resume found. Please provide a file path:
>
> `/export-pdf /path/to/resume.md`
>
> Or run `/optimize-resume` first to generate an optimized resume.

Stop processing.

### Step 2: Select Style Preset

Present the style preset selection to the user via `AskUserQuestion`:

> **Which style preset would you like for your PDF?**
>
> 1. **Modern** (Recommended) — Clean, contemporary sans-serif design with subtle accent color and balanced whitespace
> 2. **Classic** — Traditional serif design with conservative colors and generous margins
> 3. **Compact** — Dense, space-efficient design that maximizes content per page
> 4. **Harvard** — Traditional academic format with serif font, monochrome black-only color, and generous margins

Default to "Modern" if the user doesn't specify.

### Step 3: Offer Customization

After preset selection, ask the user if they want to customize the styling via `AskUserQuestion`:

> **Would you like to customize the styling?**
>
> 1. **Use preset defaults** (Recommended) — Apply the selected preset as-is
> 2. **Customize** — Fine-tune font, color, margins, page size, and spacing

#### If the user chooses "Customize":

Present customization options one at a time via `AskUserQuestion`:

**Font family:**
> **Which font family?**
>
> 1. **Inter** — Modern sans-serif (default for Modern preset)
> 2. **EB Garamond** — Elegant serif (default for Classic preset)
> 3. **Source Sans 3** — Clean sans-serif (default for Compact preset)
> 4. **Lato** — Friendly modern sans-serif

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
> 2. **Narrow** (0.5") — More content space
> 3. **Wide** (1") — More whitespace

**Line spacing:**
> **Which line spacing?**
>
> 1. **Standard** (1.15) (Recommended)
> 2. **Tight** (1.0) — More compact
> 3. **Relaxed** (1.3) — More breathing room

**Section spacing:**
> **Which section spacing?**
>
> 1. **Standard** (Recommended)
> 2. **Compact** — Tighter sections
> 3. **Generous** — More space between sections

**PDF/A compliance (advanced):**
> **Enable PDF/A-2b compliance?**
>
> 1. **No** (Recommended) — Standard PDF output
> 2. **Yes** — PDF/A-2b archival format (for enterprise/government submissions)

### Step 4: Generate PDF

Assemble the CLI arguments based on the user's selections and run the conversion script:

```bash
uv run --directory ${CLAUDE_PLUGIN_ROOT} ${CLAUDE_PLUGIN_ROOT}/scripts/md-to-pdf.py <input-path> <output-path> --preset <preset> [--font <font>] [--color <color>] [--margin <margin>] [--page-size <size>] [--line-spacing <spacing>] [--section-spacing <spacing>] [--pdf-a]
```

Where `<output-path>` follows the pattern `{original-stem}-optimized.pdf` in the appropriate directory.

**If the script fails (exit code 1):** Report the error from stderr to the user.

### Step 5: Report Results

On success, report to the user:

> **PDF exported successfully!**
>
> - **File:** `{output-path}`
> - **Size:** {file-size}
> - **Preset:** {preset name}
> - **Customizations:** {list any overrides, or "None (preset defaults)"}
>
> The PDF has a native text layer for ATS compatibility and uses embedded fonts for consistent rendering.

## Edge Cases

- **No session found and no path provided:** Prompt user to provide a file path or run `/optimize-resume` first.
- **Multiple sessions exist:** Use the most recent session with `optimized-resume.md`.
- **Explicit path to non-session markdown:** Write PDF alongside the source file.
- **Script outputs warnings to stderr:** Relay warnings to the user (e.g., "Missing expected section: skills").
- **User provides hex color in customization:** Pass directly to `--color` flag.

## Example Usage

```
/export-pdf
/export-pdf ~/Documents/my-resume.md
/export-pdf workspace/output/2026-02-27-143000/optimized-resume.md
```
