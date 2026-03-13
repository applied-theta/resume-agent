# Report Template

This file defines the structure and content rules for `analysis-report.md`. It is
read by the analyze-resume skill during Step 6 (Report Generation).

---

## Report Structure

```markdown
# Resume Analysis Report

**Date:** {YYYY-MM-DD}
**Resume:** {filename}
**Job Description:** {filename or "Not provided"}
**Overall Score:** {score}/100 ({grade})

---

## Executive Summary

{2-3 paragraph overview of the resume's strengths and weaknesses. Highlight the most
impactful findings. Note the career archetype detected and how it influences the analysis.
If a JD was provided, note the alignment level. If user notes were provided, briefly
acknowledge how they shaped the analysis focus.}

---

## User Context

{INCLUDE THIS SECTION ONLY WHEN USER NOTES WERE PROVIDED.}

{Summarize the user's stated goals, concerns, and focus areas from user-notes.txt.
Explain how these notes influenced the analysis across dimensions. For example:
- "You mentioned transitioning from IC to management — the Strategy and Content analyses
  weighted leadership indicators more heavily."
- "Your concern about ATS compatibility for Workday was addressed in the Platform Simulation."

If notes were not provided, omit this entire section (do not include a placeholder).}

---

## Scorecard

| Dimension | Score | Grade | Weight |
|-----------|-------|-------|--------|
| ATS Compatibility | {score}/100 | {grade} | {weight}% |
| Content Quality | {score}/100 | {grade} | {weight}% |
| Strategic Positioning | {score}/100 | {grade} | {weight}% |
| Structure & Format | {score}/100 | {grade} | {weight}% |
| Market Intelligence | {score}/100 | {grade} | {weight}% |
{| Keyword Alignment | {score}/100 | {grade} | {weight}% | (if JD)}
| **Overall** | **{score}/100** | **{grade}** | |

---

## Detailed Analysis

### ATS Compatibility

{Summary of ATS findings from ats-analysis.json. Include:
- Sub-dimension scores (parsability, format compliance, keyword readiness, structure quality)
- Critical issues found
- Top recommendations}

### Content Quality

{Summary of content findings from content-analysis.json. Include:
- Bullet score distribution (how many at each level 1-5)
- Top weak patterns found
- Quantification gaps
- Narrative coherence assessment}

### Strategic Positioning

{Summary of strategy findings from strategy-analysis.json. Include:
- Career archetype detected
- Value proposition assessment
- Format recommendation
- Key strategic recommendations}

### Keyword Alignment (if JD provided)

{Summary of keyword findings from keyword-analysis.json. Include:
- Overall match rate
- Critical gaps (required skills not found)
- Top optimization actions}

{If no JD: "No job description was provided. Provide a JD for keyword alignment analysis."}

---

## Skills Intelligence

{Summary of market intelligence from skills-research.json. Include:

### Market Demand Analysis
- Table of top skills with their demand classification (High/Moderate/Low/Emerging)
  and trend direction (Rising/Stable/Declining)
- Highlight skills that are high-demand and well-represented on the resume
- Flag skills that are low-demand or declining that may need de-emphasis

### Terminology Issues
- List any technology names that need correction (e.g., "NextJS" → "Next.js")
- Note verified terms that are correctly used

### Trending Skills
- 3-5 trending skills for the target role not currently on the resume
- Relevance and demand level for each
- How each complements the existing skill set

### Key Recommendations
- Top high-priority actions from skills-research recommendations
- Market data supporting each recommendation (with source citations where available)

If skills-research.json is unavailable (agent failure), display:
"Skills intelligence was not available for this analysis. Run `/skills-research` separately
for market demand analysis and terminology verification."}

---

## ATS Platform Simulation

{Summary of platform-specific ATS analysis from ats-analysis.json platform_simulation section.

For each simulated platform (Workday, Greenhouse, Lever):

### {Platform Name}
- **Estimated Score:** {score}/100
- **Key Issues:** {list of platform-specific parsing issues}
- **Optimization Tips:** {platform-specific recommendations}

Include a comparison table:
| Platform | Score | Key Issue |
|----------|-------|-----------|
| Workday | {score}/100 | {primary issue} |
| Greenhouse | {score}/100 | {primary issue} |
| Lever | {score}/100 | {primary issue} |

Note: Platform simulation scores are estimates based on known platform behaviors
and current research. They are provided for guidance and do not affect the overall
ATS Compatibility score.

If platform_simulation is unavailable in ats-analysis.json, display:
"ATS platform simulation was not available for this analysis. The overall ATS
compatibility score above reflects general ATS best practices."}

---

## Priority Action Plan

{Ordered list of the top 5-10 most impactful improvements the candidate should make,
synthesized across all dimensions including skills intelligence and platform simulation.
Each action should be specific and actionable. Prioritize by impact on overall score.}

1. **{Action title}** -- {Specific description of what to do and why}
2. ...

---

## Dimension Details

{If any dimension was unavailable due to agent failure, note it here:
"Note: {dimension} analysis was not available due to: {reason}"}
```

---

## Report Content Rules

- Use data directly from the analysis JSON files. Do not fabricate scores or findings.
- The executive summary should synthesize across dimensions, not repeat dimension-by-dimension details.
- The action plan should be a prioritized, deduplicated synthesis of the top recommendations from all agents, including skills-research recommendations.
- If a dimension is missing due to agent failure, note it clearly and adjust the report accordingly.
- Use the grade mapping from `scoring-rubric.json` to assign grades to individual dimension scores.
- The "User Context" section is only included when notes were provided. Do not include an empty placeholder.
- The "Skills Intelligence" section is always included (with a fallback message if data is unavailable).
- The "ATS Platform Simulation" section is always included (with a fallback message if data is unavailable).
