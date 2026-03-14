# ATS Compatibility Rules

This document provides the domain knowledge and scoring methodology for evaluating resume compatibility with Applicant Tracking Systems (ATS). It is loaded by the ats-analyzer agent when performing analysis.

## Scoring Overview

The ATS compatibility score is a weighted composite of four sub-dimensions, producing an overall score from 0 to 100:

| Dimension | Weight | What It Measures |
|-----------|--------|-----------------|
| Parsability | 30% | Can the ATS extract structured data from the resume? |
| Format Compliance | 25% | Does the resume avoid formatting that breaks ATS parsing? |
| Keyword Readiness | 25% | Is the resume structured for optimal keyword extraction? |
| Structure Quality | 20% | Does the resume follow ATS-preferred organizational patterns? |

**Overall ATS Score** = (Parsability x 0.30) + (Format Compliance x 0.25) + (Keyword Readiness x 0.25) + (Structure Quality x 0.20)


## Dimension 1: Parsability (30% Weight)

Parsability measures whether an ATS can successfully extract structured data fields from the resume. This is the highest-weighted dimension because a resume that cannot be parsed is effectively invisible to the system.

### Evaluation Criteria

#### Contact Information Extractability
- **Name**: Appears at the top of the document, clearly separated from other content. Not embedded in a header/footer.
- **Email**: Standard email format present and extractable (not an image or embedded in a graphic).
- **Phone**: Standard phone format (with or without country code). Not hidden in a footer.
- **Location**: City and state/country present. Full street address is unnecessary and a privacy risk.
- **LinkedIn URL**: If present, uses standard URL format (linkedin.com/in/...).

#### Section Header Recognizability
- Uses standard section headers that ATS systems recognize: "Experience", "Work Experience", "Education", "Skills", "Summary", "Professional Summary", "Certifications", "Projects".
- Avoids creative or non-standard headers like "My Journey", "What I Bring", "Toolbox", "Adventures".
- Headers are formatted consistently (all bold, all caps, or all using the same heading level in Markdown).

#### Date Format Parsability
- Uses standard date formats: "Month YYYY", "MM/YYYY", "YYYY-MM", or "Month YYYY - Present".
- Date ranges use consistent delimiters: dash (-), en-dash, or "to".
- Avoid formats like "Q3 2023", "Summer 2022", or seasons without years.
- "Present" or "Current" is used for ongoing roles (not "Now" or "Ongoing").

#### File Format
- **PDF**: Text-based PDF (not scanned image). Text must be selectable/copyable.
- **Markdown**: Well-structured with proper heading hierarchy.
- DOCX is generally preferred by ATS systems but is outside the scope of this tool.

### Scoring Rubric

| Score Range | Description |
|-------------|-------------|
| 90-100 | All contact fields extractable, standard headers, consistent dates, text-based format |
| 70-89 | Minor issues: one non-standard header, slight date inconsistency |
| 50-69 | Moderate issues: multiple non-standard headers, some contact info not extractable |
| 30-49 | Significant issues: contact info buried in headers/footers, creative section names throughout |
| 0-29 | Critical failures: image-based PDF, no recognizable structure, contact info not parseable |


## Dimension 2: Format Compliance (25% Weight)

Format compliance checks whether the resume uses formatting elements that are known to cause ATS parsing failures. Even modern ATS systems struggle with certain visual formatting techniques.

### Elements to Check

Refer to `format-checklist.json` for the complete checklist with severity ratings.

#### Critical Issues (immediate score reduction)
- **Tables**: ATS systems often read tables left-to-right across rows, jumbling content that is meant to be read in columns. Two-column layouts using tables are a common failure mode.
- **Text boxes**: Content inside text boxes is frequently skipped entirely by ATS parsers.
- **Headers/Footers with critical info**: Many ATS systems ignore document headers and footers. Name, contact info, or page numbers in headers/footers may be lost.
- **Images/graphics**: Logos, icons, skill bars, infographics, and photos are invisible to ATS. Any text embedded in images is lost.

#### Warning Issues (score penalty)
- **Multi-column layouts**: Even without tables, columnar layouts (via CSS or column breaks) can confuse reading order.
- **Non-standard fonts**: Unusual or decorative fonts may not render correctly. Stick to Arial, Calibri, Times New Roman, Garamond, or similar widely-supported fonts.
- **Excessive formatting**: Heavy use of bold, italic, underline, colors, or font size variation can interfere with parsing.
- **Special characters**: Unicode symbols, emojis, or decorative bullets may be stripped or replaced with garbage characters.

#### Info Issues (minor or no impact)
- **Hyperlinks**: Generally safe but some older ATS strip them. Ensure URLs are also written as plain text.
- **Bullet point style**: Standard round bullets are safest. Custom bullet characters may render incorrectly.
- **Page breaks**: Should fall between sections, not mid-entry.

### Scoring Rubric

| Score Range | Description |
|-------------|-------------|
| 90-100 | No tables, no text boxes, no images, standard fonts, clean formatting |
| 70-89 | Minor formatting concerns: hyperlinks only, slight font variation |
| 50-69 | One critical issue present (e.g., a skills table) or multiple warnings |
| 30-49 | Multiple critical issues: tables + images, or text boxes with key content |
| 0-29 | Heavily designed resume: multi-column table layout, graphics throughout, text boxes for sections |


## Dimension 3: Keyword Readiness (25% Weight)

Keyword readiness evaluates whether the resume is structured to maximize keyword extraction by ATS systems. ATS systems weight keywords differently based on placement, and certain structural patterns improve match rates.

### Evaluation Criteria

#### Dedicated Skills Section
- A clearly labeled "Skills" or "Technical Skills" section exists.
- Skills are listed as discrete items (comma-separated, bulleted, or in a simple list), not buried only in prose.
- Skills section appears before or immediately after the experience section for optimal weighting.

#### Acronym and Full-Term Pairs
- Industry acronyms are paired with their full terms at least once: "Search Engine Optimization (SEO)", "Amazon Web Services (AWS)".
- This ensures matching regardless of whether the job description uses the acronym or the full term.
- After first use, either form is acceptable.

#### Keyword Placement in High-Weight Locations
ATS systems typically assign higher weight to keywords found in:
1. **Job titles** (highest weight)
2. **Skills section** (high weight)
3. **Summary/objective** (high weight)
4. **First bullet point of each role** (medium-high weight)
5. **Other bullet points** (medium weight)
6. **Education and certifications** (standard weight)

#### Keyword Density and Natural Integration
- Keywords should appear naturally in context, not keyword-stuffed.
- Critical skills should appear in multiple locations (skills section + experience bullets).
- Avoid invisible keyword stuffing (white text, tiny font, hidden sections).

### Scoring Rubric

| Score Range | Description |
|-------------|-------------|
| 90-100 | Dedicated skills section, acronym pairs used, keywords in high-weight locations, natural integration |
| 70-89 | Skills section present but could be better organized; most acronyms paired; good placement |
| 50-69 | Skills scattered in prose only, or skills section is poorly structured; some acronym pairs missing |
| 30-49 | No dedicated skills section; keywords only in bullet points; no acronym pairing |
| 0-29 | Very few extractable keywords; skills not identifiable by ATS |


## Dimension 4: Structure Quality (20% Weight)

Structure quality assesses whether the resume follows organizational patterns that ATS systems expect and that optimize for both automated parsing and recruiter review.

### Evaluation Criteria

#### Reverse-Chronological Order
- Experience entries are listed most recent first.
- Education entries are listed most recent first.
- Dates are present for all entries and support chronological ordering.
- Employment gaps are not hidden through creative date formatting (this raises flags).

#### Consistent Formatting
- All experience entries follow the same pattern: Title, Company, Location, Dates, Bullets.
- Bullet points use the same style throughout (not mixing dashes, dots, and arrows).
- Indentation is consistent.
- Font sizes and styles are uniform within each section type.

#### Appropriate Length
- **Entry-level (0-2 years)**: 1 page strongly preferred.
- **Mid-career (3-10 years)**: 1-2 pages.
- **Senior/Executive (10+ years)**: 2 pages acceptable, 3 pages only for academic CVs or extensive publication lists.
- Each page should be substantially filled (no half-empty pages except the last).

#### File Size
- PDF file size should be under 5 MB (most ATS have upload limits).
- Ideal range: 50 KB - 2 MB for a standard 1-2 page resume.
- Oversized files often indicate embedded images or complex formatting.

### Scoring Rubric

| Score Range | Description |
|-------------|-------------|
| 90-100 | Reverse-chronological, consistent formatting, appropriate length, reasonable file size |
| 70-89 | Minor inconsistencies in formatting; length slightly off for experience level |
| 50-69 | Mixed chronological order or significant formatting inconsistencies; length clearly inappropriate |
| 30-49 | No clear chronological order; inconsistent formatting throughout; major length issues |
| 0-29 | Functional/skills-based format with no chronology; chaotic formatting; extreme length |


## Common ATS Failure Patterns

### Pattern 1: The Invisible Resume
**Symptoms**: Resume is submitted but never surfaces in ATS search results.
**Causes**:
- Image-based PDF (scanned document without OCR text layer)
- Critical content in text boxes that the parser skips
- Name and contact info in document headers that are ignored
**Detection**: Check if text is selectable in PDF; verify contact info is in the document body.

### Pattern 2: The Scrambled Resume
**Symptoms**: Resume appears in ATS but information is jumbled or fields are misassigned.
**Causes**:
- Table-based layout causing left-to-right reading instead of column-by-column
- Multi-column layout confusing the reading order
- Non-standard section headers preventing correct field mapping
**Detection**: Look for tables, columns, or creative headers in the source document.

### Pattern 3: The Keyword Desert
**Symptoms**: Resume parses correctly but never matches job searches.
**Causes**:
- No dedicated skills section for keyword extraction
- Using only acronyms (or only full terms) without pairing
- Skills mentioned only in prose within bullet points, not as discrete extractable items
- Keywords placed only in low-weight locations
**Detection**: Check for a skills section; verify acronym/full-term pairs; check keyword placement.

### Pattern 4: The Date Confusion
**Symptoms**: ATS calculates incorrect years of experience or cannot sort chronologically.
**Causes**:
- Inconsistent date formats across entries
- Missing dates on some entries
- Non-standard date expressions ("Summer 2022", "Q3 2023")
- Date ranges without clear start/end delimiters
**Detection**: Validate all dates against standard formats; check for consistency.

### Pattern 5: The Overdesigned Resume
**Symptoms**: Resume looks great as a PDF but loses most content when parsed.
**Causes**:
- Skill bars, progress circles, or rating graphics for skill levels
- Icons used for section headers or contact methods
- Infographic-style layout with complex visual elements
- Background colors or patterns that interfere with text extraction
**Detection**: Check for any visual elements that would be empty if all images were removed.


## Input Format Considerations

### PDF Input
When analyzing a PDF resume:
- Verify that text is extractable (not image-only)
- Check for embedded fonts that may cause character encoding issues
- Note any visual elements that suggest tables, columns, or graphics
- File size can indicate embedded images or complex formatting
- Metadata (author, creation tool) can hint at potential formatting issues

### Markdown Input
When analyzing a Markdown resume:
- Section headers should use Markdown heading syntax (`#`, `##`, `###`)
- Lists should use standard Markdown bullet syntax (`-`, `*`, or `1.`)
- No HTML tables or complex HTML embedded in the Markdown
- Links should use standard Markdown link syntax
- Markdown is inherently ATS-friendly for parsability since it is plain text
- Focus analysis on keyword readiness and structure quality, as format compliance issues are minimal in Markdown


## Platform-Specific Considerations

Different ATS platforms have varying parsing capabilities and quirks. Refer to `platform-quirks.json` for detailed platform-specific behaviors.

Key platforms to consider:
- **Workday**: Dominant in enterprise hiring. Strict parsing requirements.
- **Greenhouse**: Popular in tech industry. Generally more tolerant of formatting.
- **Lever**: Used by startups and mid-size companies. Good parsing capabilities.
- **Taleo** (Oracle): Legacy system still widely used. Most restrictive parser.
- **iCIMS**: Large enterprise platform. Moderate parsing capabilities.
- **BrassRing (Kenexa/IBM)**: Government and large enterprise. Very strict parsing.

When providing recommendations, note which platforms are most affected by specific issues and prioritize fixes that improve compatibility across the broadest set of platforms.


## Scoring Aggregation

To compute the overall ATS score:

1. Score each dimension independently (0-100).
2. Apply weights: Parsability (0.30), Format Compliance (0.25), Keyword Readiness (0.25), Structure Quality (0.20).
3. Sum weighted scores for the overall score.
4. Identify any critical issues (issues that would cause complete parsing failure on any major platform).
5. Report per-dimension scores, issues found, and actionable recommendations.

### Grade Mapping

| Score | Grade | Interpretation |
|-------|-------|----------------|
| 95-100 | A+ | Exceptional ATS compatibility |
| 90-94 | A | Excellent - minor polish only |
| 85-89 | A- | Very good - small improvements possible |
| 80-84 | B+ | Good - a few items to address |
| 75-79 | B | Above average - several improvements recommended |
| 70-74 | B- | Acceptable - notable issues to fix |
| 65-69 | C+ | Below average - significant work needed |
| 60-64 | C | Poor - multiple compatibility problems |
| 50-59 | D | Very poor - major overhaul needed |
| 0-49 | F | Critical failures - resume likely not parseable |


## Output Requirements

The ats-analyzer agent should produce output conforming to the `ats-analysis` JSON Schema, including:

- `overall_score`: Weighted composite score (0-100)
- `dimensions`: Object with `parsability`, `format_compliance`, `keyword_readiness`, `structure_quality`, each containing:
  - `score`: Dimension score (0-100)
  - `issues`: Array of specific issues found
  - `recommendations`: Array of actionable fixes
- `critical_issues`: Array of issues that cause complete parsing failure
- `platform_specific_notes`: Object with platform-specific observations
