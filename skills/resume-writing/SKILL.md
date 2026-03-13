---
description: Resume rewriting methodology and optimization rules for the resume-rewriter agent
auto-loaded: true
---

# Resume Writing Methodology

This skill provides the domain knowledge and methodology for rewriting and optimizing resumes. It is auto-loaded by the resume-rewriter agent when producing optimized content.

**Critical Rule: Never fabricate metrics, achievements, or experiences. If a specific number is unknown, use a bracketed placeholder `[X]` with a coaching note explaining what data the candidate should provide.**

---

## Rewriting Modes

### Conservative Mode (Default)

Produces before/after pairs for each recommended change with an explanation of why the change improves the resume. This is the default mode because it respects the candidate's ownership of their resume and teaches them the principles behind each improvement.

**Output format per change:**

```
### Change #N: [Brief title]

**Before:**
> Original bullet or section text

**After:**
> Improved bullet or section text

**Why:** Explanation of what was improved and why it matters.
```

Conservative mode is best when:
- The candidate wants to understand and learn from improvements
- The resume is generally well-structured but needs content polish
- The candidate may want to selectively adopt changes

### Full Rewrite Mode (On Request)

Generates a complete optimized resume as markdown, incorporating all recommended improvements from the analysis outputs. The full rewrite applies the correct template based on the detected career archetype.

Full rewrite mode is best when:
- The resume needs substantial restructuring
- The candidate wants a ready-to-use optimized version
- Multiple sections need reordering or reformatting

**Both modes produce two output files:**
1. `optimization-report.md` -- before/after pairs with explanations (always produced)
2. `optimized-resume.md` -- complete rewritten resume (always produced in full rewrite mode; in conservative mode, produced by applying all recommended changes)

---

## Bullet Transformation Pattern

Every experience bullet should follow the **[Action Verb] + [Activity] + [Result]** pattern. This transforms duty-based descriptions into impact-driven statements.

### The Pattern

```
[Strong Action Verb] + [What You Did / What You Built / What You Led] + [Measurable Outcome / Business Impact]
```

### Transformation Examples

| Before (Duty-Based) | After (Impact-Driven) |
|---------------------|-----------------------|
| Responsible for managing the database | Optimized PostgreSQL database queries, reducing average response time from 800ms to 120ms |
| Helped with onboarding new team members | Designed and implemented structured onboarding program that reduced new hire ramp-up time from 12 weeks to 6 weeks |
| Worked on the frontend redesign project | Led frontend redesign of checkout flow, increasing conversion rate by [X]% |
| Fixed bugs in the codebase | Resolved [X] critical production bugs in payment processing pipeline, eliminating $[X]K in monthly revenue loss |

### When Metrics Are Unknown

Use bracketed placeholders with coaching notes:

```
**After:** Streamlined deployment pipeline, reducing release cycle from [X days/weeks] to [X days/weeks]

> Coaching note: Check your team's release frequency before and after the change.
> Common metrics to look for: deployment frequency, lead time, number of
> manual steps eliminated, time saved per release.
```

See `transformation-rules.md` for the complete step-by-step transformation process and additional examples.

---

## Bracketed Placeholder Rules

When exact metrics or data points are unknown, use bracketed placeholders rather than fabricating numbers.

### Format

- Use `[X]` for a single unknown number: `"Reduced costs by [X]%"`
- Use `[X unit]` when the unit helps: `"Processed [X requests/day]"`
- Use `[specific description]` for non-numeric unknowns: `"Led team of [team size] engineers"`
- Use `[X-Y]` for unknown ranges: `"Improved performance by [X-Y]%"`

### Coaching Note Format

Every placeholder must be accompanied by a coaching note that helps the candidate find the real number:

```
> Coaching note: [Where to find this number]. [What to measure].
> [Alternative metrics if the exact number is unavailable].
```

### Examples

```markdown
Managed cloud infrastructure budget of $[annual budget], achieving [X]% cost reduction through resource optimization

> Coaching note: Check your cloud provider billing dashboard for annual spend.
> Look at month-over-month cost trends after you implemented changes.
> If exact savings are unknown, estimate based on the percentage reduction
> in instance count or resource usage.
```

```markdown
Mentored [X] junior developers, with [X]% receiving promotions within [timeframe]

> Coaching note: Count the people you mentored directly (1:1s, code reviews,
> pair programming). Check with your manager or HR for promotion data.
> If promotion data is unavailable, note other outcomes: successful project
> deliveries, skill certifications earned, or positive feedback received.
```

### Rules

1. Never invent specific numbers -- always use `[X]` when unsure
2. Every `[X]` placeholder requires a coaching note
3. Coaching notes should suggest 2-3 ways to find the real data
4. Provide fallback metrics if the primary metric is unavailable
5. Group coaching notes at the end of each experience entry, not inline

---

## Summary Rewriting

### With a Target Job Description

When a JD is provided, rewrite the summary to:
1. Lead with a professional identity aligned to the target role
2. Include years of experience relevant to the target role
3. Mention 2-3 key skills that match the JD's top requirements
4. State a value proposition that addresses the employer's core need
5. Keep to 2-4 sentences maximum

**Pattern:**
```
[Professional identity] with [X] years of experience in [relevant domain].
[Key achievement or capability aligned to JD].
[Value proposition addressing employer's core need].
```

**Example:**
```
Before: "Experienced software engineer looking for new opportunities.
I have worked with many technologies and am a fast learner."

After: "Senior Backend Engineer with 6 years of experience building
high-throughput distributed systems in Python and Go. Scaled payment
processing infrastructure from 10K to 500K daily transactions at
[Company]. Proven track record of reducing system latency and improving
reliability in fintech environments."
```

### Without a Job Description

When no JD is provided, rewrite the summary to:
1. Lead with the candidate's strongest professional identity
2. Highlight their most impressive quantified achievement
3. State their core technical or domain expertise
4. Present a general value proposition

---

## Skills Section Optimization

### Reorganization Rules

1. **Group by relevance**: Place the most relevant skill category first based on the target role or archetype
2. **Include both acronyms and full terms**: "Amazon Web Services (AWS)", "Continuous Integration/Continuous Deployment (CI/CD)"
3. **Remove outdated skills**: Drop technologies that are obsolete or no longer relevant to the candidate's target roles
4. **Add implied skills**: If experience bullets demonstrate a skill not listed, recommend adding it
5. **Limit to relevant skills**: 15-25 skills maximum; quality over quantity
6. **Use standard terminology**: Match the terms employers and ATS systems expect

### Category Order by Archetype

| Archetype | Recommended Category Order |
|-----------|---------------------------|
| Technical / Linear Progression | Programming Languages, Frameworks, Cloud/Infrastructure, Tools, Methodologies |
| Executive | Strategic Leadership, Domain Expertise, Technology Platforms, Methodologies |
| Career Changer | Transferable Technical Skills, Domain Knowledge, Tools, Soft Skills |
| Entry-Level | Programming Languages, Frameworks, Tools, Coursework Topics |

---

## Section Reordering Rules

Section order should follow the strategy advisor's recommendations. When no specific recommendation is available, use these defaults by archetype:

### Standard / Linear Progression
1. Contact Information
2. Professional Summary
3. Technical Skills
4. Professional Experience
5. Education
6. Certifications (if applicable)
7. Projects (if applicable)

### Executive
1. Contact Information
2. Executive Summary
3. Core Competencies / Areas of Expertise
4. Professional Experience
5. Board Memberships / Advisory Roles (if applicable)
6. Education
7. Publications / Speaking Engagements (if applicable)

### Technical
1. Contact Information
2. Professional Summary
3. Technical Skills (prominent, detailed)
4. Professional Experience
5. Projects / Open Source Contributions
6. Education
7. Certifications

### Career Changer
1. Contact Information
2. Professional Summary (emphasize transferable value)
3. Relevant Skills (transferable + new skills)
4. Relevant Experience (reframed for target industry)
5. Education / Training / Bootcamp
6. Projects (demonstrating new skills)
7. Previous Experience (condensed)

### Entry-Level
1. Contact Information
2. Summary / Objective
3. Education
4. Projects
5. Experience (internships, part-time)
6. Skills
7. Activities / Volunteer Work (if applicable)

### Return-to-Work
1. Contact Information
2. Professional Summary (address gap positively)
3. Skills (updated, current)
4. Recent Experience / Contract Work / Volunteer Work
5. Previous Professional Experience
6. Education
7. Certifications / Recent Training

---

## Template Selection

Select the appropriate template from `${CLAUDE_PLUGIN_ROOT}/skills/resume-writing/templates/` based on the career archetype detected by the strategy advisor:

| Archetype | Template |
|-----------|----------|
| `linear_progression` | `standard.md` |
| `entry_level` | `standard.md` (with entry-level section order) |
| `executive` | `executive.md` |
| `career_changer` | `career-change.md` |
| `return_to_work` | `standard.md` (with return-to-work section order) |
| `military_transitioner` | `career-change.md` |
| `international_candidate` | `standard.md` |

For technical roles (detected from JD or resume content), prefer `technical.md` regardless of archetype, unless the archetype is executive or career-changer.

---

## Quality Guardrails

### Must Do
- Preserve all factual information from the original resume
- Maintain the candidate's authentic voice and professional identity
- Use action verbs appropriate to the candidate's seniority level
- Ensure every bullet follows the [Action Verb] + [Activity] + [Result] pattern
- Use bracketed placeholders for any unknown metrics
- Include coaching notes for every placeholder

### Must Not Do
- Fabricate metrics, percentages, dollar amounts, or team sizes
- Invent achievements or responsibilities not in the original
- Add skills or technologies not evidenced in the resume
- Change job titles, company names, or dates
- Exaggerate scope or impact beyond what is supported by the original text
- Remove information without explanation

### Writing Style
- Use present tense for current roles, past tense for previous roles
- Avoid first person ("I", "my") in bullet points
- Keep bullets to 1-2 lines maximum
- Start every bullet with a strong action verb (no gerunds like "Managing" or "Leading")
- Vary action verbs across bullets within the same role
- Use industry-specific terminology appropriate to the candidate's field

---

## Confidence Classification Rubric

Every optimization change produced by the resume-rewriter must be classified into one of three confidence tiers. This rubric is the single source of truth for classification decisions. When producing `change-manifest.json`, assign a `confidence` value and `source` attribution to each change entry based on the rules below.

### High Confidence

Changes that do not alter the meaning or substance of the content. These are mechanical improvements that any reasonable reviewer would accept.

**Criteria -- all of the following must be true:**
- No change to the semantic meaning of the text
- No new information introduced
- No subjective judgment involved in the transformation

**Examples:**
- Formatting fixes: correcting spacing, alignment, bullet style consistency, or whitespace
- Keyword repositioning: moving an existing keyword from a less prominent position to a more prominent one (e.g., from mid-bullet to bullet start) without changing wording
- Standard header renames: "Work History" to "Professional Experience", "Schooling" to "Education"
- Punctuation normalization: adding or removing trailing periods for consistency across bullets
- Date format standardization: "Jan 2020 - Dec 2022" to "January 2020 -- December 2022"

### Medium Confidence

Changes that preserve the original meaning but express it differently, or reorganize content for better presentation. These changes require the rewriter's judgment but should not introduce new claims.

**Criteria -- all of the following must be true:**
- The original meaning is preserved (a reader would extract the same facts from both versions)
- No new achievements, metrics, or responsibilities are introduced
- The change improves clarity, impact, or ATS compatibility

**Examples:**
- Rephrasing passive bullets into active voice: "Was responsible for managing deployments" to "Managed deployment pipeline for 12 microservices"
- Adding action verbs to passive or noun-based bullets: "Database administration" to "Administered PostgreSQL databases"
- Restructuring bullet points to follow the [Action Verb] + [Activity] + [Result] pattern while keeping the same information
- Section reordering for better flow or archetype alignment (e.g., moving Skills above Experience for a technical role)
- Condensing or splitting bullets while retaining all original information
- Removing redundant information that appears in multiple bullets

### Low Confidence

Changes that could alter what the reader understands about the candidate's experience, scope, or expertise. These require careful review by the candidate.

**Criteria -- any of the following is true:**
- New information or context is introduced that was not in the original resume
- The scope or impact of an achievement could be interpreted differently after the change
- The change relies on assumed context not explicitly stated in the resume
- Interview-sourced content is incorporated

**Examples:**
- Reframing a bullet in a way that could change the perceived scope: "Helped with database migration" to "Led cross-team database migration initiative" (elevated scope)
- Adding content sourced from an interview that was not on the original resume
- Significant expansion of thin bullets with assumed context: "Built API" to "Architected and built RESTful API serving [X] requests/day" (assumed scale)
- Changes that could alter the candidate's presented expertise level: adding specificity about technologies or methodologies not explicitly mentioned
- Suggesting new resume sections or content blocks not present in the original
- Any change incorporating interview-sourced content (automatic Low confidence + `verification_required: true`)

### Borderline and Mixed Changes

When a single change spans multiple tiers, classify at the **highest risk tier** involved:

| Combination | Classification | Rationale |
|-------------|---------------|-----------|
| Formatting + rephrasing | Medium | The rephrasing component requires judgment |
| Rephrasing + scope expansion | Low | The scope change could alter meaning |
| Formatting + new content | Low | Any new content triggers Low |
| Keyword repositioning + active voice rewrite | Medium | The rewrite component goes beyond mechanical formatting |

**Rule**: When in doubt, classify one tier lower (more conservative). It is better to flag a Medium change as Low than to miss a change that needs review.

### Source Attribution

Every change must include a `source` field indicating what informed the change:

| Source Value | Meaning | When to Use |
|--------------|---------|-------------|
| `analysis` | Change driven by analysis findings only | Default for all changes when no interview was conducted. Also used when the change is based solely on analysis outputs (ATS issues, content scores, keyword gaps, strategy recommendations) |
| `interview` | Change driven by interview data only | The change incorporates information from `interview-findings.json` that was not present in analysis outputs |
| `both` | Change informed by both analysis and interview | The change addresses an analysis finding but uses interview-sourced context to inform the specific improvement |

**Default rule**: When no interview was conducted (no `interview-findings.json` in the session directory), all changes must have `source: analysis`. The `interview` and `both` values are only valid when interview findings exist.

**Interview-sourced content rule**: Any change with `source: interview` or `source: both` is automatically classified as **Low confidence** with `verification_required: true`, regardless of how minor the textual change appears. Interview content has not been verified against the candidate's written record and must be reviewed.

---

## Input Dependencies

The resume-rewriter agent reads these files from the session directory:
- `parsed-resume.json` -- structured resume data
- `ats-analysis.json` -- ATS compatibility findings (if available)
- `content-analysis.json` -- bullet-level scoring and suggestions (if available)
- `keyword-analysis.json` -- keyword gaps and optimization actions (if available)
- `strategy-analysis.json` -- archetype, section order, and strategic recommendations (if available)

All available analysis outputs should inform the rewrite. Missing analyses should not block the rewrite; the agent should proceed with whatever information is available.
