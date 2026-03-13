---
description: Content quality scoring rubric and methodology for resume bullet point analysis
auto-loaded: true
---

# Content Quality Analysis Rules

This skill provides the domain knowledge and scoring methodology for evaluating resume content quality. It is auto-loaded by the content-analyst agent when performing analysis. The primary focus is bullet point scoring, weak pattern detection, quantification auditing, action verb assessment, and narrative coherence evaluation.

## Bullet Point Scoring Rubric (1-5 Scale)

Each bullet point in the resume's experience section is scored on a 1-5 scale based on the presence and quality of four components: **action verb**, **specific action**, **result/impact**, and **quantification/context**.

### Score 5 - Exceptional

Strong action verb + specific action + quantified result + context. The bullet demonstrates clear impact with measurable outcomes.

**Criteria:**
- Opens with a strong, domain-appropriate action verb
- Describes a specific, clearly-scoped action (not a vague duty)
- Includes a quantified result (number, percentage, dollar amount, time saved)
- Provides context (scale, team size, timeframe, business impact)

**Examples:**
- "Architected a microservices migration for the payments platform, reducing p99 latency by 40% and saving $120K/year in infrastructure costs across 15 services"
- "Led a 12-person cross-functional team to deliver a compliance automation system 3 weeks ahead of deadline, eliminating 200 hours/month of manual audit work"
- "Redesigned the onboarding flow using A/B testing, increasing trial-to-paid conversion by 18% and generating $2.1M in incremental annual revenue"

### Score 4 - Strong

Strong action verb + specific action + result (may lack precise metrics or full context). The bullet clearly communicates impact but could be more specific.

**Criteria:**
- Opens with a strong action verb
- Describes a specific action with clear scope
- Includes a result or impact statement
- May lack exact numbers or full business context

**Examples:**
- "Spearheaded migration from monolithic architecture to microservices, significantly improving system reliability and deployment speed"
- "Developed automated testing framework that reduced regression testing time from days to hours"
- "Mentored junior engineers on distributed systems design, improving team velocity and code quality"

### Score 3 - Adequate

Describes duties adequately but lacks impact. The bullet explains what was done but not why it mattered. Acceptable but improvable.

**Criteria:**
- Uses a reasonable verb (may not be the strongest choice)
- Describes a real task or responsibility
- Missing a clear result or impact statement
- No quantification

**Examples:**
- "Developed RESTful APIs for the customer portal using Python and Flask"
- "Participated in code reviews and provided feedback to team members"
- "Managed database migrations during quarterly releases"

### Score 2 - Weak

Vague, passive, or duty-focused. The bullet reads like a job description rather than an accomplishment. Uses weak language or lacks specificity.

**Criteria:**
- Uses weak or passive verb ("Responsible for", "Helped with", "Assisted in")
- Describes duties rather than accomplishments
- Vague scope ("various", "multiple", "several" without specifics)
- No result, impact, or quantification

**Examples:**
- "Responsible for maintaining the company's web applications"
- "Helped with various customer support tasks and ticket resolution"
- "Assisted in the development of new features for the platform"

### Score 1 - Poor

No discernible value or extremely vague. The bullet provides almost no useful information about what the candidate did or achieved.

**Criteria:**
- Extremely vague or generic
- Could apply to almost anyone in any role
- No specific action, tool, technology, or outcome mentioned
- May be a sentence fragment or a single buzzword

**Examples:**
- "Team player"
- "Worked on projects"
- "Handled tasks as needed"
- "Various responsibilities"
- "Etc."

### Scoring Very Short Bullets (< 5 words)

Bullets with fewer than 5 words are almost always scored 1 or 2. A very short bullet cannot contain a specific action, result, and context. The only exception is if the short phrase is exceptionally precise and impactful (rare).

**Guideline:** If a bullet has fewer than 5 words, cap the maximum score at 2 unless it is a genuinely concise accomplishment with an implied strong result (e.g., "Promoted to VP within 18 months" - though even this benefits from expansion).

---

## Weak Pattern Detection

Weak patterns indicate that a bullet is duty-focused, passive, or vague. The content-analyst agent should flag bullets matching these patterns and suggest rewrites.

### Pattern Categories

Refer to `weak-patterns.json` for the complete set of regex-compatible patterns organized by category.

#### 1. Responsibility Prefixes

Phrases that signal a duty description rather than an accomplishment. These turn accomplishments into passive job descriptions.

**Detection:** Bullets starting with phrases like "Responsible for", "In charge of", "Tasked with", "Duties included".

**Fix:** Replace with a strong action verb that describes what was actually accomplished. "Responsible for managing a team of 5 engineers" becomes "Led a team of 5 engineers to deliver..."

#### 2. Weak Action Verbs

Verbs that dilute impact: "Helped", "Assisted", "Supported", "Contributed to", "Participated in", "Worked on", "Was involved in". These verbs obscure the candidate's actual role and contribution.

**Detection:** Bullet begins with or prominently features a weak verb.

**Fix:** Replace with a stronger verb that conveys ownership: "Helped redesign" becomes "Redesigned" or "Co-designed". "Worked on" becomes the specific action: "Built", "Developed", "Implemented".

#### 3. Passive Voice Constructions

Passive constructions remove the candidate as the agent of the action, weakening the statement. "Was selected to" is weaker than "Selected to lead" which is weaker than "Led".

**Detection:** Patterns like "was/were + past participle", "has been", "being + past participle".

**Fix:** Restructure to active voice with the candidate as the subject performing the action.

#### 4. Vague Scope Words

Words that indicate undefined scale: "various", "multiple", "several", "many", "numerous", "some", "a number of", "a lot of". These suggest the candidate cannot or did not quantify their work.

**Detection:** Presence of vague quantifiers without accompanying specific numbers.

**Fix:** Replace with specific numbers or ranges. "Managed various projects" becomes "Managed 8 concurrent projects" or "Managed 5-10 projects per quarter".

#### 5. Filler and Fluff Phrases

Empty phrases that add words but no meaning: "in order to", "on a daily basis", "successfully" (if the result is already stated), "effectively" (without evidence), "in a timely manner", "utilized" (use "used"), "leveraged" (overused buzzword).

**Detection:** Presence of known filler phrases.

**Fix:** Remove the filler and let the specifics speak for themselves.

#### 6. Job Description Language

Language that reads like it was copied from a job posting rather than describing personal accomplishments: "Ensure compliance with...", "Maintain standards for...", "Provide support for...", "Perform duties as assigned".

**Detection:** Bullet reads as a generic duty that could apply to any holder of the role.

**Fix:** Describe a specific instance where the candidate performed this duty with a measurable outcome.

---

## Quantification Audit

The quantification audit identifies bullets that lack metrics and suggests specific metric types the candidate could add. Not every bullet needs numbers, but high-impact accomplishments should be quantified whenever possible.

### Methodology

1. **Scan each bullet** for the presence of numbers, percentages, dollar amounts, or time references
2. **If no quantification found**, determine which metric type would be most appropriate based on the action described
3. **Suggest the metric type** and provide an example of how to add it
4. **Prioritize** bullets where quantification would have the highest impact (typically Score 3-4 bullets that are otherwise well-written)

### Metric Types

Refer to `quantification-guide.md` for the complete guide with examples for each metric type.

| Metric Type | What It Measures | Signal Words |
|-------------|-----------------|--------------|
| Financial | Revenue, cost savings, budget, ROI | "saved", "generated", "reduced costs", "budget" |
| Scale | Volume, users, transactions, team size | "managed", "served", "processed", "supported" |
| Efficiency | Time saved, speed improvement, automation | "reduced time", "accelerated", "automated", "streamlined" |
| Quality | Error rates, satisfaction scores, uptime | "improved", "reduced errors", "increased satisfaction" |

### Quantification Priority

Not all bullets benefit equally from quantification. Prioritize adding metrics to:

1. **Leadership accomplishments** - Team size, budget managed, people mentored
2. **Project outcomes** - Timeline, scope, business impact
3. **Process improvements** - Before/after comparison with specific numbers
4. **Revenue/growth contributions** - Dollar amounts or percentage growth

Lower priority (metrics optional):
- Routine technical tasks (writing code, fixing bugs) - unless the scale is impressive
- Collaborative activities - unless the candidate's specific contribution is quantifiable
- Learning and growth activities - unless certifications or measurable skill gains

---

## Action Verb Assessment

Strong action verbs convey ownership, initiative, and impact. The assessment evaluates verb choice, variety, and domain appropriateness.

### Assessment Criteria

#### Verb Strength

Rate each verb on a strength scale:

| Strength | Description | Examples |
|----------|-------------|---------|
| Strong | Conveys leadership, ownership, or significant impact | Architected, Spearheaded, Orchestrated, Pioneered |
| Moderate | Conveys action but not ownership | Developed, Implemented, Created, Managed |
| Weak | Passive, vague, or diluting | Helped, Assisted, Supported, Worked on |

#### Verb Variety

Flag repetition when the same verb appears in more than 2 bullets within the same experience entry, or more than 3 times across the entire resume. Repetition suggests either limited vocabulary or copy-pasting from a job description.

**Common offenders:** "Managed" (overused for any leadership task), "Developed" (overused for any creation task), "Implemented" (overused for any technical task).

#### Domain Appropriateness

Verbs should match the candidate's role and level. Refer to `action-verbs.json` for categorized verb lists by domain.

- **Individual contributors** should use execution-oriented verbs: Built, Developed, Implemented, Designed, Optimized
- **Managers and leads** should use leadership verbs: Led, Directed, Mentored, Orchestrated, Championed
- **Executives** should use strategic verbs: Defined, Established, Transformed, Drove, Shaped

### Suggestion Logic

When flagging a weak verb, suggest 2-3 stronger alternatives that:
1. Match the domain/role level of the position
2. Accurately convey the nature of the action
3. Are not already overused elsewhere in the resume

---

## Narrative Coherence Evaluation

Narrative coherence assesses whether the resume tells a clear, logical career story. This is evaluated at the resume level, not the individual bullet level.

### Evaluation Dimensions

#### Career Progression Logic

Does the resume show a logical progression in responsibility, scope, or specialization?

**Positive signals:**
- Titles show increasing seniority (Junior -> Mid -> Senior -> Lead -> Principal)
- Scope of responsibilities grows over time
- Skills deepen or broaden appropriately
- Company trajectory is logical (small to large, or increasing prestige, or deepening in a domain)

**Red flags:**
- Unexplained title demotions without context
- Scope appears to decrease without explanation
- Random jumps between unrelated domains without a narrative bridge

#### Professional Identity Clarity

Does the resume communicate a clear professional identity?

**Positive signals:**
- Summary/objective clearly states who the candidate is and what they offer
- Experience entries reinforce a consistent theme or expertise area
- Skills section aligns with the professional identity

**Red flags:**
- No summary or a generic one-size-fits-all summary
- Experience entries span unrelated industries with no connecting thread
- Skills section includes contradictory or unfocused skill sets

#### Unexplained Gaps and Jumps

Are there gaps or sudden transitions that need context?

**Items to flag:**
- Employment gaps longer than 6 months without explanation
- Sudden industry changes without a career pivot narrative
- Short tenures (< 1 year) at multiple positions in succession
- Geographic relocations that may signal instability without context

**Note:** Gaps are not inherently negative. The issue is when they are unexplained and leave the reader guessing. Recommendations should suggest adding brief context, not hiding or minimizing gaps.

### Coherence Scoring

The narrative coherence score (0-100) is a component of the overall content quality assessment:

| Score Range | Description |
|-------------|-------------|
| 90-100 | Clear progression, strong identity, no unexplained gaps, compelling career story |
| 70-89 | Generally coherent with minor issues (one short gap, slight role overlap) |
| 50-69 | Some coherence issues: unclear identity, a few unexplained transitions |
| 30-49 | Significant coherence problems: no clear direction, multiple unexplained gaps |
| 0-29 | No discernible career narrative: random positions, no progression, no identity |

---

## Overall Content Quality Score

The overall content quality score (0-100) is a weighted composite of the component scores:

| Component | Weight | Source |
|-----------|--------|--------|
| Average Bullet Score (normalized to 0-100) | 50% | Mean of all bullet scores, mapped from 1-5 to 0-100 |
| Quantification Coverage | 15% | Percentage of high-impact bullets that include metrics |
| Action Verb Quality | 15% | Verb strength average + variety score |
| Narrative Coherence | 20% | Career progression + identity + gap handling |

**Bullet score normalization:** A mean bullet score of 1.0 maps to 0, a score of 5.0 maps to 100. Formula: `(mean_score - 1) / 4 * 100`.

### Grade Mapping

| Score | Grade | Interpretation |
|-------|-------|----------------|
| 95-100 | A+ | Exceptional content quality |
| 90-94 | A | Excellent - minor polish only |
| 85-89 | A- | Very good - small improvements possible |
| 80-84 | B+ | Good - a few bullets to strengthen |
| 75-79 | B | Above average - several improvements recommended |
| 70-74 | B- | Acceptable - notable content issues |
| 65-69 | C+ | Below average - significant rewriting needed |
| 60-64 | C | Poor - most bullets need improvement |
| 50-59 | D | Very poor - major content overhaul needed |
| 0-49 | F | Critical issues - resume content is not effective |

---

## Output Requirements

The content-analyst agent should produce output conforming to the `content-analysis` JSON Schema, including:

- `overall_score`: Weighted composite score (0-100)
- `bullet_analysis`: Array of per-bullet assessments, each containing:
  - `experience_index`: Which experience entry (0-based)
  - `bullet_index`: Which bullet within the entry (0-based)
  - `original_text`: The bullet text as written
  - `score`: Integer score (1-5)
  - `issues`: Array of specific issues found
  - `suggestion`: Rewritten bullet or improvement suggestion
- `quantification_gaps`: Array of bullets lacking metrics with suggested metric types
- `language_issues`: Array of language problems (weak verbs, passive voice, filler)
- `narrative_assessment`: Object with coherence evaluation
  - `coherence_score`: 0-100
  - `progression_clear`: Boolean
  - `identity_defined`: Boolean
  - `gaps_or_jumps`: Array of identified gaps or unexplained transitions
- `top_improvements`: Prioritized list of the highest-impact improvement recommendations
