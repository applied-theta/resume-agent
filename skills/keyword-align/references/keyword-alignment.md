# Keyword Alignment Methodology

This document provides the domain knowledge and methodology for analyzing keyword alignment between a resume and a target job description. It is loaded by the keyword-optimizer agent when performing analysis.

## Overview

Keyword alignment analysis answers the question: "How well does this resume match the target job description?" It decomposes the JD into structured requirement categories, builds a keyword inventory from the resume, classifies matches by confidence level, identifies critical gaps, and generates prioritized optimization actions with specific placement guidance.


## Step 1: JD Decomposition

Decompose the job description into six requirement categories:

| Category | Description | Examples |
|----------|-------------|---------|
| **Required Hard Skills** | Technical skills explicitly listed as required or must-have | "Python", "React", "AWS", "SQL" |
| **Preferred Hard Skills** | Technical skills listed as nice-to-have or preferred | "Kubernetes experience a plus", "Familiarity with GraphQL" |
| **Required Soft Skills** | Non-technical competencies stated as requirements | "Strong communication skills", "Team leadership" |
| **Experience Level** | Years of experience, seniority signals, scope indicators | "5+ years", "Senior-level", "Led teams of 10+" |
| **Industry Terms** | Domain-specific vocabulary and concepts | "CI/CD", "microservices architecture", "HIPAA compliance" |
| **Tools** | Specific products, platforms, or software mentioned | "Jira", "Figma", "Terraform", "Snowflake" |

### Decomposition Guidelines

- A single JD phrase may map to multiple categories (e.g., "5+ years of Python development" yields both an experience level and a required hard skill).
- Distinguish between explicit requirements ("must have", "required") and implicit ones (skills listed without qualification often mean required).
- Phrases like "experience with" or "proficiency in" signal hard skills. Phrases like "ability to" often signal soft skills.
- When the JD lists a technology stack, each technology is a separate required or preferred hard skill.
- Industry terms are domain concepts rather than specific tools (e.g., "event-driven architecture" is an industry term, "Kafka" is a tool).


## Step 2: Resume Keyword Inventory

Build a complete keyword inventory from the resume, noting where each keyword appears. Placement location affects the match weight assigned by ATS systems.

### Placement Locations (by ATS weight)

| Location | ATS Weight | Description |
|----------|-----------|-------------|
| **Job titles** | Highest | Keywords appearing in role titles |
| **Skills section** | High | Dedicated skills/technical skills section |
| **Summary/objective** | High | Professional summary or objective statement |
| **First bullet of each role** | Medium-high | The leading bullet point under each experience entry |
| **Other bullet points** | Medium | Remaining experience bullet points |
| **Education/certifications** | Standard | Degrees, certifications, coursework |
| **Projects section** | Standard | Personal or professional project descriptions |

### Inventory Guidelines

- Extract both explicit keyword mentions and contextual skill demonstrations (e.g., "built a React dashboard" demonstrates React even if not listed in a skills section).
- Note acronym vs. full-term usage: record whether the resume uses "JS", "JavaScript", or both.
- Record the number of times a keyword appears and all locations where it is found.
- Load industry keyword clusters from `industry-clusters/` to expand the matching vocabulary with known synonyms and related terms.


## Step 3: Match Classification

Classify each JD requirement against the resume keyword inventory using four confidence tiers:

### Confidence Tiers

| Tier | Confidence | Description | Examples |
|------|-----------|-------------|---------|
| **Exact Match** | 1.0 | Identical term found in resume (case-insensitive) | JD: "Python" / Resume: "Python" |
| **High-Confidence Semantic** | > 0.8 | Strong synonym, abbreviation, or closely related term | JD: "JavaScript" / Resume: "JS"; JD: "AWS" / Resume: "Amazon Web Services" |
| **Medium-Confidence Semantic** | 0.5 - 0.8 | Related skill or partial overlap | JD: "React" / Resume: "Vue.js" (both frontend frameworks); JD: "CI/CD" / Resume: "Jenkins pipelines" |
| **Low-Confidence** | < 0.5 | Weak or tangential relationship; flagged for review only | JD: "Machine Learning" / Resume: "data analysis" |

### Classification Rules

1. **Exact matches** require the identical term (case-insensitive) or a known abbreviation pair from the industry clusters data. "JavaScript" matching "JS" is an exact match because they are direct abbreviation pairs, not a semantic inference.

2. **High-confidence semantic matches** (> 0.8) include:
   - Direct synonyms: "Software Engineer" / "Software Developer"
   - Version variants: "Python 3" / "Python"
   - Platform variants: "AWS Lambda" / "Lambda functions"
   - Recognized equivalent tools: "PostgreSQL" / "Postgres"
   - Superset skills: resume shows "React Native" and JD asks for "React" (the candidate demonstrably knows the superset)

3. **Medium-confidence semantic matches** (0.5 - 0.8) include:
   - Same technology family: "Vue.js" for "React" (both frontend frameworks but different tools)
   - Implied skills: "built REST APIs" implies knowledge of "HTTP", "JSON", "API design"
   - Related tooling: "Jenkins" for "CI/CD" (tool that implements the concept)
   - Transferable experience: "team leadership" for "people management"

4. **Low-confidence matches** (< 0.5) include:
   - Broad category overlap: "data analysis" for "machine learning"
   - Adjacent domains: "frontend development" for "UI/UX design"
   - These are flagged for the user's awareness but do not count toward the match rate

### Using Industry Clusters

Load the appropriate industry cluster files from `industry-clusters/` based on the detected industry. Always load `general.json` as the baseline. Layer industry-specific clusters on top.

Industry clusters provide:
- **Synonyms**: Known equivalent terms (e.g., "k8s" = "Kubernetes")
- **Abbreviations**: Acronym-to-full-term mappings (e.g., "ML" = "Machine Learning")
- **Related terms**: Terms in the same skill cluster for medium-confidence matching


## Step 4: Match Rate Computation

Compute the overall match rate as a percentage representing how well the resume covers the JD requirements.

### Formula

```
match_rate = (weighted_matches / total_weighted_requirements) * 100
```

### Requirement Weights

| Category | Weight per Item | Rationale |
|----------|---------------|-----------|
| Required hard skills | 3.0 | Most critical for ATS filtering and recruiter screening |
| Required soft skills | 1.5 | Important but harder to verify from a resume |
| Preferred hard skills | 1.5 | Differentiators but not dealbreakers |
| Tools | 2.0 | Often used as ATS filter criteria |
| Industry terms | 1.0 | Contextual knowledge indicators |
| Experience level | 2.5 | Key qualification gate |

### Match Value by Confidence Tier

| Tier | Match Value | Rationale |
|------|------------|-----------|
| Exact match | 1.0 | Full credit |
| High-confidence semantic | 0.85 | Near-certain match, slight discount for not being verbatim |
| Medium-confidence semantic | 0.5 | Partial credit; demonstrates related knowledge |
| Low-confidence | 0.0 | Not counted toward match rate |

### Calculation Example

For a JD with 5 required hard skills (weight 3.0 each) and 3 tools (weight 2.0 each):
- Total weighted requirements = (5 * 3.0) + (3 * 2.0) = 21.0
- If 3 hard skills are exact matches (3 * 3.0 * 1.0 = 9.0), 1 is high-confidence (1 * 3.0 * 0.85 = 2.55), 2 tools are exact (2 * 2.0 * 1.0 = 4.0), 1 tool is medium (1 * 2.0 * 0.5 = 1.0)
- Weighted matches = 9.0 + 2.55 + 4.0 + 1.0 = 16.55
- Match rate = (16.55 / 21.0) * 100 = 78.8%

### Target Ranges

| Match Rate | Assessment | Recommendation |
|-----------|------------|----------------|
| 85-100% | Excellent | Strong match; minor keyword optimization may help |
| 70-84% | Good | Solid match; address a few specific gaps |
| 50-69% | Moderate | Notable gaps; targeted optimization needed |
| 30-49% | Weak | Significant misalignment; consider whether this is the right role |
| 0-29% | Poor | Major misalignment; role may not be a fit |


## Step 5: Critical Gap Identification

Critical gaps are required skills from the JD that have no match (not even low-confidence) in the resume. These represent the most impactful optimization opportunities.

### Gap Prioritization

Rank gaps by their impact on the application:

| Priority | Criteria |
|----------|----------|
| **Critical** | Required hard skill or tool with no match at any confidence level |
| **High** | Required hard skill with only a low-confidence match |
| **Medium** | Preferred hard skill with no match; required soft skill with no match |
| **Low** | Industry term with no match; preferred skill with a medium-confidence match |

### Gap Analysis Output

For each gap, provide:
- **Term**: The JD requirement that is unmatched
- **Priority**: Critical / High / Medium / Low
- **Suggestion**: Specific action to address the gap (add to skills section, incorporate into a bullet point, mention in summary, or acknowledge the gap is genuine and suggest how to address it in a cover letter)


## Step 6: Optimization Action Generation

Generate prioritized, actionable optimization recommendations with specific placement guidance.

### Action Types

| Action | Description | When to Recommend |
|--------|-------------|-------------------|
| **Add to skills section** | Add a missing keyword to the dedicated skills section | Candidate has the skill but did not list it |
| **Add acronym pair** | Include both the acronym and full term | Only one form is present (e.g., has "JS" but not "JavaScript") |
| **Incorporate into bullet** | Weave the keyword naturally into an experience bullet point | Skill is demonstrated in experience but not explicitly named |
| **Add to summary** | Include the keyword in the professional summary | High-priority skill that should appear in a high-weight location |
| **Reorder skills section** | Move the most relevant skills to the top of the skills list | Skills section exists but priority skills are buried |
| **Create a skills section** | Add a dedicated skills section | Resume lacks one entirely |
| **Address in cover letter** | Acknowledge a genuine gap and explain transferable experience | Candidate does not have the skill and cannot honestly claim it |

### Placement Guidance Rules

1. **High-priority required skills** should appear in at least two high-weight locations (skills section + summary or first bullet).
2. **Tools and platforms** should appear in the skills section and in the experience bullets where they were used.
3. **Soft skills** are best demonstrated through bullet point achievements rather than listed in a skills section.
4. **Acronym-full term pairs** should appear together at first mention, with either form used subsequently.
5. Never recommend keyword stuffing or dishonest skill claims. Every recommended keyword addition must reflect the candidate's genuine experience.

### Action Priority

Number optimization actions in priority order based on:
1. Impact on match rate (how much the match rate would increase)
2. Ease of implementation (adding to skills section is easier than rewriting bullets)
3. ATS weight of the target placement location


## Output Requirements

The keyword-optimizer agent should produce output conforming to the `keyword-analysis` JSON Schema, including:

- `match_rate`: Overall match rate percentage (0-100)
- `jd_requirements`: Decomposed JD with `required_hard`, `preferred_hard`, `required_soft`, `experience_level`, `industry_terms`, `tools`
- `exact_matches`: Array of exact match objects with `term` and `locations`
- `semantic_matches`: Array of semantic match objects with `resume_term`, `jd_term`, and `confidence`
- `critical_gaps`: Array of gap objects with `term`, `priority`, and `suggestion`
- `optimization_actions`: Array of action objects with `priority` (integer rank), `action`, `impact`, and `placement`
