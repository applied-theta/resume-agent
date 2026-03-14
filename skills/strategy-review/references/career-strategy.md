# Career Strategy

This document provides the domain knowledge and methodology for strategic positioning analysis of resumes. It is loaded by the strategy-advisor agent when performing analysis.

## Career Archetype Classification

Every resume is classified into a primary career archetype (and optionally a secondary archetype) to guide format recommendations, section ordering, and strategic advice. There are 7 defined archetypes:

| Archetype | Key Characteristic |
|-----------|-------------------|
| `linear_progression` | Steady upward career growth within one industry or domain |
| `career_changer` | Transitioning from one field or industry to another |
| `return_to_work` | Re-entering the workforce after a gap of 1+ years |
| `entry_level` | Under 2 years of professional experience |
| `executive` | Director-level or above with 15+ years of experience |
| `military_transitioner` | Transitioning from military service to civilian roles |
| `international_candidate` | Applying from or relocating to a different country |

### Archetype Detection

Refer to `archetypes.json` for the full set of detection signals per archetype. The detection process follows these steps:

1. **Scan structural indicators**: Total years of experience, number of roles, industry consistency, presence of career gaps, education patterns.
2. **Scan keywords and patterns**: Look for archetype-specific language, titles, certifications, and organizational cues.
3. **Score each archetype**: Assign a confidence score (0 to 1) based on the number and strength of matching signals.
4. **Select primary**: The highest-scoring archetype becomes the primary classification.
5. **Select secondary (optional)**: If a second archetype scores above 0.4 confidence, assign it as the secondary.

### Multi-Archetype Candidates

Some candidates match multiple archetypes. Common combinations:

| Primary | Secondary | Example |
|---------|-----------|---------|
| `career_changer` | `executive` | A VP of Marketing moving into product management |
| `return_to_work` | `career_changer` | Someone re-entering the workforce in a different field |
| `military_transitioner` | `career_changer` | Military personnel moving to civilian tech roles |
| `international_candidate` | `linear_progression` | An experienced engineer relocating to a new country |
| `entry_level` | `career_changer` | A bootcamp grad who previously worked in a non-tech field |

When a secondary archetype is detected, apply the primary archetype's format recommendation but incorporate mitigation strategies from the secondary archetype.


## Value Proposition Evaluation

Assess the resume's value proposition across three dimensions:

### 1. Summary Effectiveness (0-100)

Evaluate the professional summary or objective statement:

| Score Range | Description |
|-------------|-------------|
| 90-100 | Compelling, specific, differentiating; clearly communicates unique value and target alignment |
| 70-89 | Solid summary with relevant positioning; minor improvements possible |
| 50-69 | Generic summary that could apply to many candidates; lacks specificity |
| 30-49 | Vague or unfocused; does not convey value proposition |
| 0-29 | Missing, single sentence, or purely objective-based ("seeking a role in...") |

**Evaluation Criteria:**
- Does it state what the candidate does (not just what they want)?
- Does it include quantifiable impact or scope (team size, revenue, scale)?
- Does it mention the target role type or industry?
- Is it differentiated from a generic professional in the same field?

### 2. Differentiation Assessment

Determine whether the resume makes the candidate stand out:

- **Unique combinations**: Skills or experience pairings that are rare (e.g., engineering + design, data science + domain expertise)
- **Scale indicators**: Large teams managed, high revenue impact, enterprise-scale systems
- **Domain expertise**: Deep specialization signals (publications, patents, speaking, certifications)
- **Career narrative**: A coherent story that connects roles and shows intentional growth

### 3. Target Role Alignment

When a job description is provided, evaluate alignment:

- Does the summary speak to the target role?
- Are the most relevant experiences and skills prominent?
- Is the resume length appropriate for the target role's seniority level?
- Does the section order emphasize what matters most for this role?


## Resume Format Recommendations

Refer to `format-decision-tree.md` for the complete decision tree. The three format types are:

### Reverse-Chronological
- **Best for**: `linear_progression`, `executive`
- **Structure**: Lists experience in reverse time order, emphasizing career trajectory
- **Strengths**: Familiar to recruiters and ATS, highlights promotions and growth
- **Weaknesses**: Exposes gaps and lack of progression

### Hybrid (Combination)
- **Best for**: `career_changer`, `military_transitioner`, `return_to_work`
- **Structure**: Leads with a skills or qualifications summary, followed by chronological experience
- **Strengths**: Highlights transferable skills before potentially mismatched job titles
- **Weaknesses**: Less familiar to some recruiters, can feel like hiding something if not done well

### Skills-Based (Functional)
- **Best for**: `entry_level` (limited experience), extreme career changers
- **Structure**: Organized by skill categories rather than job history
- **Strengths**: Downplays limited or irrelevant experience, highlights capabilities
- **Weaknesses**: ATS systems strongly prefer chronological data; many recruiters dislike this format
- **Caution**: Use sparingly; reverse-chronological or hybrid is almost always preferable


## Section Ordering Optimization

Section order should be optimized based on the candidate's archetype and the content that best serves their positioning. The default order and archetype-specific adjustments:

### Default Order (Reverse-Chronological)
1. Contact Information
2. Professional Summary
3. Experience
4. Skills
5. Education
6. Certifications (if applicable)
7. Projects (if applicable)

### Archetype-Specific Adjustments

**linear_progression:**
1. Contact Information
2. Professional Summary
3. Experience (strongest section -- leads the resume)
4. Skills
5. Education
6. Certifications

**career_changer:**
1. Contact Information
2. Professional Summary (reframe career narrative)
3. Skills (transferable skills prominent)
4. Relevant Experience (highlight transferable work)
5. Additional Experience (prior career, condensed)
6. Education (especially if recent retraining)
7. Certifications

**return_to_work:**
1. Contact Information
2. Professional Summary (address the gap proactively)
3. Skills (show currency)
4. Recent Activity (freelance, volunteer, courses -- if applicable)
5. Experience
6. Education
7. Certifications

**entry_level:**
1. Contact Information
2. Professional Summary / Objective
3. Education (strongest credential for entry-level)
4. Projects (demonstrate capability)
5. Skills
6. Experience (internships, part-time, relevant work)
7. Activities / Volunteer Work

**executive:**
1. Contact Information
2. Executive Summary (leadership brand)
3. Core Competencies (strategic skills)
4. Experience (achievement-focused, scope emphasized)
5. Board Memberships / Advisory Roles (if applicable)
6. Education
7. Certifications / Professional Development

**military_transitioner:**
1. Contact Information
2. Professional Summary (translated to civilian language)
3. Skills (civilian-equivalent competencies)
4. Experience (military roles translated, acronyms expanded)
5. Education / Training
6. Certifications / Clearances
7. Awards (translated to civilian equivalents)

**international_candidate:**
1. Contact Information (include work authorization status)
2. Professional Summary (mention international context)
3. Experience (emphasize global scope and transferable achievements)
4. Skills (include language proficiencies)
5. Education (note equivalencies if needed)
6. Certifications (note international recognition)


## Length Appropriateness Guidelines

Resume length should match the candidate's experience level and target role:

| Experience Level | Recommended Length | Notes |
|-----------------|-------------------|-------|
| Entry-level (0-2 years) | 1 page | Strongly preferred; exceeding 1 page signals poor editing |
| Early career (3-5 years) | 1 page | 1 page preferred; 2 pages acceptable only if densely relevant |
| Mid-career (5-10 years) | 1-2 pages | 2 pages becoming appropriate as experience accumulates |
| Senior (10-15 years) | 2 pages | Standard length; condense early career roles |
| Executive (15+ years) | 2-3 pages | 2 pages preferred; 3 acceptable for extensive scope |
| Academic / CV | 3+ pages | CVs follow different conventions; no strict limit |

### Length Assessment Rules

- **Too short**: Resume is significantly under the recommended length for experience level, suggesting underselling or missing content.
- **Too long**: Resume exceeds the maximum for experience level, suggesting poor editing, irrelevant content, or role-by-role exhaustive detail that should be condensed.
- **Just right**: Resume fills the recommended page count with relevant, well-curated content.

### Condensing Guidance

When a resume is too long:
- Condense roles older than 10 years to 1-2 bullets each
- Remove roles older than 15 years unless they demonstrate unique expertise
- Merge short-tenure roles at the same company into a single entry
- Remove skills that are assumed at the candidate's level (e.g., "Microsoft Office" for a senior engineer)
- Trim non-essential sections (hobbies, references, "References available upon request")


## Scoring Methodology

The overall strategic positioning score (0-100) is a composite of:

| Component | Weight | What It Measures |
|-----------|--------|-----------------|
| Value Proposition | 30% | Summary effectiveness, differentiation, alignment |
| Format Appropriateness | 20% | Is the chosen format optimal for this archetype? |
| Section Ordering | 20% | Does the section order maximize strengths? |
| Length Appropriateness | 15% | Is the resume the right length for this experience level? |
| Strength Utilization | 15% | Are strengths prominently featured and weaknesses mitigated? |

### Grade Mapping

| Score | Grade | Interpretation |
|-------|-------|----------------|
| 95-100 | A+ | Exceptional strategic positioning |
| 90-94 | A | Excellent -- minor refinements only |
| 85-89 | A- | Very good -- small adjustments possible |
| 80-84 | B+ | Good -- a few strategic improvements available |
| 75-79 | B | Above average -- several enhancements recommended |
| 70-74 | B- | Acceptable -- notable strategic gaps |
| 65-69 | C+ | Below average -- significant repositioning needed |
| 60-64 | C | Poor -- multiple strategic issues |
| 50-59 | D | Very poor -- major strategic overhaul needed |
| 0-49 | F | Critical -- resume does not effectively position the candidate |


## Output Requirements

The strategy-advisor agent should produce output conforming to the `strategy-analysis` JSON Schema, including:

- `overall_score`: Weighted composite score (0-100)
- `archetype`: Object with `primary`, optional `secondary`, and `confidence`
- `value_proposition`: Object with `current_effectiveness`, `is_differentiated`, `suggested_summary`, `key_selling_points`
- `format_recommendation`: Object with `current_format`, `recommended_format`, `section_order`, `sections_to_add`, `sections_to_remove`
- `competitive_analysis`: Object with `strengths_undersold`, `weaknesses_to_mitigate`, `differentiators`
- `strategic_recommendations`: Array of actionable recommendation strings
