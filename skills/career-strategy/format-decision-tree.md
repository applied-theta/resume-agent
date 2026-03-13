# Format Decision Tree

This document provides a decision tree for recommending resume format, section order, and sections to add or remove based on the detected career archetype and career context.

## Input

- **Detected archetype** (primary, optional secondary)
- **Career context**: years of experience, target role, job description availability, career gaps, industry

## Output

- **Recommended format**: reverse-chronological, hybrid, or skills-based
- **Section order**: prioritized list of resume sections
- **Sections to add**: sections the candidate should include but currently lacks
- **Sections to remove**: sections that are unnecessary or harmful for this archetype

---

## Decision Tree

### Step 1: Determine Base Format from Primary Archetype

```
Is the primary archetype executive?
  YES -> reverse-chronological (executive variant)
  NO  -> continue

Is the primary archetype linear_progression?
  YES -> reverse-chronological (standard)
  NO  -> continue

Is the primary archetype entry_level?
  YES -> Does the candidate have any professional experience (internships, part-time)?
    YES -> reverse-chronological (education-forward)
    NO  -> skills-based (project-forward)
  NO  -> continue

Is the primary archetype career_changer?
  YES -> hybrid (skills-forward)
  NO  -> continue

Is the primary archetype return_to_work?
  YES -> hybrid (activity-forward)
  NO  -> continue

Is the primary archetype military_transitioner?
  YES -> hybrid (skills-forward, civilian translation)
  NO  -> continue

Is the primary archetype international_candidate?
  YES -> Is the candidate applying in the same country they currently work in?
    YES -> reverse-chronological (standard)
    NO  -> reverse-chronological (with localization adjustments)
```

### Step 2: Adjust for Secondary Archetype

If a secondary archetype is detected, apply modifications on top of the base format:

| Secondary Archetype | Modification |
|---------------------|-------------|
| `career_changer` | Add a "Relevant Skills" section near the top; consider splitting experience into "Relevant" and "Additional" |
| `return_to_work` | Add a "Recent Activity" section if gap-filling activities exist; address gap in summary |
| `executive` | Expand summary into "Executive Summary"; add "Core Competencies" section; consider adding "Board & Advisory" section |
| `entry_level` | Move Education higher; add Projects section if not present |
| `military_transitioner` | Add a skill translation note; ensure all military jargon is translated |
| `international_candidate` | Add work authorization line; add language skills section; note credential equivalencies |
| `linear_progression` | No modification needed; reinforce chronological ordering |

### Step 3: Determine Section Order

Refer to the archetype-specific section orders below. Adjust further based on the candidate's strongest content.

**General rule**: Lead with the section that best positions the candidate. For most candidates, this is Experience. For entry-level, it is Education. For career changers and military transitioners, it is Skills.

---

## Per-Archetype Recommendations

### linear_progression

**Format**: Reverse-Chronological

**Section Order**:
1. Contact Information
2. Professional Summary
3. Experience
4. Skills
5. Education
6. Certifications (if applicable)

**Sections to Add**:
- Professional Summary (if missing) -- highlight trajectory and domain depth
- Certifications (if relevant industry certs exist)

**Sections to Remove**:
- Objective statement (replace with Professional Summary)
- References or "References available upon request"
- Hobbies / Interests (unless directly relevant to the target role)

**Key Guidance**:
- Highlight promotions and title progression prominently
- Show increasing scope at each level (bigger teams, budgets, projects)
- Condense early-career roles to 1-2 bullets; expand recent roles

---

### career_changer

**Format**: Hybrid

**Section Order**:
1. Contact Information
2. Professional Summary (frame the transition narrative)
3. Relevant Skills (transferable + new-field skills)
4. Relevant Experience (highlight transferable work)
5. Additional Experience (prior career, condensed)
6. Education (especially if includes retraining)
7. Certifications (especially in the new field)
8. Projects (if showcasing new-field capability)

**Sections to Add**:
- Relevant Skills section (transferable skills front and center)
- Projects section (if recent projects demonstrate target-field skills)
- Certifications (in the target field)

**Sections to Remove**:
- Objective statement (replace with a transition-focused Summary)
- Detailed bullet points from unrelated prior career roles
- Skills section items that only apply to the old career

**Key Guidance**:
- Summary must address the transition directly and frame it positively
- Split experience into "Relevant" and "Additional" if prior career is lengthy
- Emphasize transferable skills: leadership, project management, communication, analytical thinking
- Highlight any projects, freelance work, or coursework in the new field

---

### return_to_work

**Format**: Hybrid

**Section Order**:
1. Contact Information
2. Professional Summary (address the gap proactively)
3. Skills (demonstrate currency)
4. Recent Activity (freelance, volunteer, courses -- if applicable)
5. Experience
6. Education
7. Certifications

**Sections to Add**:
- Recent Activity section (volunteer work, freelance, training during the gap)
- Skills section with recently refreshed or newly acquired skills
- Professional Development section (courses, workshops, certifications taken during the gap)

**Sections to Remove**:
- Objective statement (replace with Summary that addresses the gap)
- Outdated skills or technologies that are no longer relevant
- Excessive detail on roles from before the gap

**Key Guidance**:
- Summary should briefly acknowledge the break and emphasize readiness to return
- Never hide the gap; explain it through a positive lens
- Showcase any activity during the gap: freelance, volunteer, open source, courses
- Focus on skills that remain current and relevant

---

### entry_level

**Format**: Reverse-Chronological (education-forward) or Skills-Based (if no professional experience)

**Section Order**:
1. Contact Information
2. Professional Summary or Objective
3. Education (strongest credential for new grads)
4. Projects (demonstrate capability in lieu of extensive experience)
5. Skills (technical + soft skills)
6. Experience (internships, part-time, relevant work)
7. Activities / Volunteer Work
8. Awards / Honors (if notable)

**Sections to Add**:
- Projects section (academic, personal, or open-source projects)
- Skills section (comprehensive technical skills list)
- Activities section (leadership roles, clubs, hackathons)

**Sections to Remove**:
- References or "References available upon request"
- Unrelated part-time work (e.g., retail) unless demonstrating key soft skills
- High school information (if the candidate has a college degree)
- GPA (if below 3.3 and not required by the employer)

**Key Guidance**:
- Keep to 1 page strictly
- Education goes high since it is the strongest credential
- Projects section is critical for demonstrating hands-on skills
- Frame internships and part-time roles with measurable achievements
- Include relevant coursework only if directly applicable to the target role

---

### executive

**Format**: Reverse-Chronological (executive variant)

**Section Order**:
1. Contact Information
2. Executive Summary (leadership brand statement)
3. Core Competencies (strategic skills in 3-4 columns or a grid)
4. Experience (achievement-focused, scope emphasized)
5. Board Memberships / Advisory Roles (if applicable)
6. Education
7. Certifications / Professional Development
8. Speaking / Publications (if applicable)

**Sections to Add**:
- Executive Summary (not just a regular summary -- a leadership brand)
- Core Competencies section (strategic capabilities)
- Board / Advisory section (if applicable)
- Speaking / Publications (for thought leadership positioning)

**Sections to Remove**:
- Objective statement
- Detailed technical skills lists (unless applying for a technical executive role)
- Early-career roles older than 15 years (condense to a one-line "Earlier Career" section)
- References

**Key Guidance**:
- Summary should read like a leadership brand: scope, impact, and vision
- Quantify everything: revenue, team size, budget, market share, growth
- Condense early career aggressively; focus on the last 10-15 years
- Each role should emphasize outcomes, not activities
- Consider a 2-page format; 3 pages only if scope truly warrants it

---

### military_transitioner

**Format**: Hybrid (skills-forward, civilian translation)

**Section Order**:
1. Contact Information
2. Professional Summary (translated to civilian language)
3. Core Competencies (civilian-equivalent skills)
4. Experience (military roles translated, acronyms expanded)
5. Education / Training
6. Certifications / Clearances
7. Awards (translated to civilian equivalents)

**Sections to Add**:
- Core Competencies section (leadership, operations, logistics, technical skills -- in civilian terms)
- Clearances section (if applicable and relevant to target role)
- Training section (translate military training to civilian equivalents)

**Sections to Remove**:
- Military jargon, acronyms, and codes that are not translated
- Detailed unit designations and organizational structure
- Awards and decorations without civilian-equivalent descriptions

**Key Guidance**:
- Translate ALL military terminology: "platoon leader" becomes "team leader of 40 personnel"
- Expand all acronyms on first use (MOS, AFSC, NCO, etc.)
- Quantify leadership scope: personnel managed, budget controlled, equipment value
- Emphasize transferable skills: leadership, project management, logistics, training, operations
- Security clearances are valuable -- keep them prominent if relevant to the target industry
- Map military rank to approximate civilian equivalent in the summary

---

### international_candidate

**Format**: Reverse-Chronological (with localization adjustments)

**Section Order**:
1. Contact Information (include work authorization status)
2. Professional Summary (mention global experience and authorization)
3. Experience (emphasize global scope and transferable achievements)
4. Skills (include language proficiencies)
5. Education (note equivalencies where needed)
6. Certifications (note international recognition)

**Sections to Add**:
- Work authorization line near the top (e.g., "Authorized to work in the US" or "Visa status: H-1B")
- Language Skills section or subsection
- Education equivalency notes (e.g., "Equivalent to US Bachelor's degree per WES evaluation")

**Sections to Remove**:
- Personal information not standard in the target country (date of birth, nationality, marital status, national ID for US/UK/Canada/Australia applications)
- Candidate photo (for US/UK/Canada/Australia applications)
- References from foreign companies without context

**Key Guidance**:
- Adapt resume conventions to the target country's norms
- Proactively address work authorization to reduce employer uncertainty
- Translate company names, job titles, and achievements to be understandable in the target market
- Add context for unfamiliar companies ("Infosys, a 300,000-employee global IT services company")
- Include education equivalency assessments if available (WES, NACES)
- Highlight multinational experience as a strength, not a complication

---

## Quick Reference Table

| Archetype | Format | Lead Section | Critical Add | Critical Remove |
|-----------|--------|-------------|-------------|-----------------|
| linear_progression | Reverse-Chron | Experience | Summary with trajectory | Objective statement |
| career_changer | Hybrid | Skills | Relevant Skills; Projects | Unrelated experience detail |
| return_to_work | Hybrid | Skills | Recent Activity | Outdated skills |
| entry_level | Reverse-Chron | Education | Projects; Activities | High school; low GPA |
| executive | Reverse-Chron | Executive Summary | Core Competencies; Board | Early career detail |
| military_transitioner | Hybrid | Skills | Civilian skill translations | Untranslated jargon |
| international_candidate | Reverse-Chron | Experience | Work authorization; Languages | Personal info (DOB, photo) |
