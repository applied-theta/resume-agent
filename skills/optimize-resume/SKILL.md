---
name: optimize-resume
description: >
  Resume optimization -- generates improved resume content based on prior
  analysis, with optional interactive interview, conservative or full-rewrite
  modes, change tracking with confidence levels, and granular approval workflow.
argument-hint: "[--notes \"free-form text\"]"
disable-model-invocation: true
allowed-tools: Agent, Read, Write, Bash, Glob, AskUserQuestion
---

# Optimize Resume

Generate optimized resume content based on a prior analysis run. This command collects optional user notes for career context, then delegates to the resume-rewriter subagent to produce before/after change pairs with explanations (conservative mode, the default) or a complete rewrite (full mode, on request), along with a fully rewritten resume file and a structured change manifest with confidence indicators. An optional interactive interview captures additional career context before the rewriter runs, enriching optimization quality. After the rewriter produces output, a granular approval workflow gives the user control over individual changes before finalizing the resume. A before/after score comparison validates optimization improvement through full re-analysis. High-scoring resumes receive special handling to prevent over-optimization.

## Prerequisites

- Read `${CLAUDE_PLUGIN_ROOT}/skills/shared/workspace-resolution.md` for workspace layout and path conventions
- This command requires a prior analysis run. At minimum, the session directory must contain:
  - `parsed-resume.json` -- structured resume data from the resume-parser
  - At least one analysis file (`ats-analysis.json`, `content-analysis.json`, `keyword-analysis.json`, or `strategy-analysis.json`)

If these files do not exist, the user must run `/analyze-resume` first (resume can be provided via direct path, e.g., `/analyze-resume /path/to/resume.pdf`).


## Procedure

### Step 1: Locate the Session Directory

Find the most recent session directory that contains analysis results. Resolve the workspace root first by reading `${CLAUDE_PLUGIN_ROOT}/.env-config` for `WORKSPACE_ROOT` (fallback: `${CLAUDE_PLUGIN_ROOT}/workspace/`).

1. Use `Glob` to search for `{workspace}/{slug}/sessions/*/parsed-resume.json` (if a resume slug is known from this conversation) or `{workspace}/*/sessions/*/parsed-resume.json` (if no slug context). Also check the legacy path `{workspace}/output/*/parsed-resume.json` as a fallback.
2. If multiple session directories exist, use the most recent one (by timestamp in the directory name).
3. If a session directory was already established in this conversation, prefer that one.

**If no session directory with `parsed-resume.json` is found:**

Display to the user:
> No prior analysis run found. The resume optimizer needs parsed resume data and analysis results to work with.
>
> Please run `/analyze-resume` first to generate the analysis, then run `/optimize-resume` to get optimized content.

Stop execution.

### Step 2: Verify Analysis Files Exist

Check the session directory for the required analysis files.

**Required:**
- `parsed-resume.json` -- must exist and must not contain `"error": true`

**Expected (at least one must exist):**
- `ats-analysis.json`
- `content-analysis.json`
- `keyword-analysis.json`
- `strategy-analysis.json`

1. If `parsed-resume.json` is missing or contains `"error": true`:
   > No valid parsed resume found in the session directory. Please run `/analyze-resume` first.

   Stop execution.

2. If none of the four analysis files exist:
   > No analysis results found in the session directory. The optimizer needs at least one analysis (ATS, content, keyword, or strategy) to inform its rewrites.
   >
   > Please run `/analyze-resume` first to generate analysis results, then run `/optimize-resume`.

   Stop execution.

3. If some analysis files are missing, note which ones are available. The resume-rewriter handles missing files gracefully and adjusts its approach accordingly.

Tell the user which analysis files were found:
> Found analysis results in `{workspace}/{slug}/sessions/{session}/`:
> - Parsed resume: Yes
> - ATS analysis: {Yes/No}
> - Content analysis: {Yes/No}
> - Keyword analysis: {Yes/No}
> - Strategy analysis: {Yes/No}

### Step 2.5: High-Score Check

Before proceeding with optimization, check whether the resume already scores well enough that a full optimization is unnecessary or should be reduced in scope. This step reads `scores-summary.json` and applies score thresholds to prevent over-optimization of already-strong resumes.

#### 2.5.1: Read Score Data

Read `scores-summary.json` from the session directory.

- **If `scores-summary.json` does not exist**: Skip the high-score check entirely. Set `polish_mode = false` and proceed to Step 3 with standard optimization flow.
- **If `scores-summary.json` is malformed** (invalid JSON or missing `overall_score` field): Display a warning and skip the check:
  > **Note:** Could not read scoring data from `scores-summary.json`. Proceeding with standard optimization.

  Set `polish_mode = false` and proceed to Step 3 with standard optimization flow.
- **If `scores-summary.json` has `fallback: true` on multiple dimensions** (2 or more dimension entries with `"fallback": true` in `dimension_scores`): Note that the score is an estimate and proceed with standard optimization regardless of the score value:
  > **Note:** Overall score ({score}/100) is based on estimated data for multiple dimensions. Proceeding with standard optimization.

  Set `polish_mode = false` and proceed to Step 3 with standard optimization flow.

#### 2.5.2: Apply Score Thresholds

Extract the `overall_score` and `grade` fields from `scores-summary.json`. Apply the following thresholds:

**Score >= 90 (Confirmation Gate):**

Present a confirmation gate via `AskUserQuestion`:

> Your resume scored {score}/100 ({grade}). This is an excellent score. Only minor polish is recommended. Would you like to proceed?

Options:
- "Yes, proceed with polish"
- "No, my resume is great as-is"

**If the user selects "No, my resume is great as-is":** End the workflow with a congratulatory message:

> Congratulations! Your resume is already in excellent shape with a score of {score}/100 ({grade}). No changes have been made. You can always re-run `/optimize-resume` later if you'd like minor polish.

Stop execution. No output files are produced.

**If the user selects "Yes, proceed with polish":** Set `polish_mode = true` and proceed to Step 3.

**Score >= 85 and < 90 (Polish Mode):**

Acknowledge the resume quality and set the polish mode flag:

> Your resume scored {score}/100 ({grade}) -- a strong result. The optimizer will focus on refinements only: formatting fixes, minor rewording, and keyword optimization. No structural changes will be made.

Set `polish_mode = true`. Proceed to Step 3.

**Score < 85 (Standard Flow):**

No special handling. Set `polish_mode = false`. Proceed to Step 3.

#### 2.5.3: Polish Mode Effects

When `polish_mode` is `true`, the following downstream steps are affected:

1. **Step 3.5 (Interview):** Reduced interview scope -- select only 2-3 categories and limit to 1 question each. Focus on emphasis preferences and any targeted improvements.
2. **Step 4 (Rewriter Delegation):** Pass the `polish_mode` flag to the resume-rewriter, which triggers its "polish only" mode -- limiting changes to formatting fixes, minor rewording, and keyword optimization. No structural changes, no section reordering, no major content additions.

### Step 2.7: Notes Collection

Collect optional user notes that provide career context for the optimization. Notes inform the interview question selection (Step 3.5) and flow through to the rewriter via `interview-findings.json`. Notes are session-scoped only and are never persisted between sessions.

#### Check for `--notes` argument

If the user provided a `--notes` argument with the `/optimize-resume` command:
1. Extract the free-form text value from the argument.
2. If the value is an empty string (e.g., `--notes ""`), treat this as no notes provided and fall through to the interactive prompt below.
3. If the value is non-empty, use it as the user's notes.

#### Interactive prompt (when `--notes` not provided or empty)

If no notes were provided via `--notes` (or the value was empty), prompt the user via `AskUserQuestion`:

> Do you have any context to share about your career goals, specific concerns, or areas you'd like the optimization to focus on?

Provide these options:
- "Yes, I'd like to add notes"
- "No, continue without notes"

**If user selects "No, continue without notes":** Proceed to Step 3 without notes. No `user-notes.txt` is written.

**If user selects "Yes, I'd like to add notes":** Collect the free-form text from the user.
- If the user provides empty text (blank or whitespace only): re-prompt once with "It looks like no notes were entered. Would you like to try again or continue without notes?" with options "Try again" / "Continue without notes". If empty again or user selects continue, proceed without notes.
- If the user provides non-empty text: use it as the user's notes.

#### Write notes to session directory

When notes are available (non-empty text from either `--notes` argument or interactive prompt):

1. Write the notes to `{workspace}/{slug}/sessions/{session}/user-notes.txt`.
2. If the file write fails, log the error but do not crash the pipeline. Continue without persisted notes. The notes text is still available in memory for passing to Step 3.5 and Step 4.

Tell the user:
> User notes saved to session directory.

**If no notes:** Tell the user:
> No user notes provided. Continuing with standard optimization.

### Step 3: Determine Rewriting Mode

The default mode is **conservative** -- producing before/after pairs for each change with explanations.

- If the user explicitly requested a "full rewrite" or "complete rewrite", use **full rewrite mode**.
- Otherwise, use **conservative mode** (the default).

Tell the user:
> Running resume optimization in {conservative/full rewrite} mode...

### Step 3.5: Interactive Interview (Conditional)

An optional, adaptive, multi-turn interview that captures career context to improve optimization quality. The interview is positioned between mode determination (Step 3) and rewriter delegation (Step 4). When the user skips the interview, the rewriter runs with analysis data only and all changes default to `source: analysis`.

#### 3.5.1: Offer Interview

Present the interview offer via `AskUserQuestion`:

> Would you like to do a brief interview to help tailor the optimization? (Recommended)
>
> The interview takes 3-7 questions and helps the optimizer understand your career goals, undersold accomplishments, and emphasis preferences.

Options:
- "Yes, interview me"
- "Skip -- optimize with analysis data only"

**If the user selects "Skip":**

- **If user notes were provided (Step 2.7):** Generate a minimal `interview-findings.json` to pass notes context to the rewriter. Write the file to the session directory with:
  - `status`: `"partial"`
  - `career_direction`: Extract career direction from the notes if present, otherwise empty string
  - `emphasis_preferences`: Extract any emphasis preferences from the notes as an array of strings
  - `optimization_directives`: Synthesize actionable optimization directives from the notes (e.g., "User wants to emphasize leadership experience", "User is targeting PM roles")
  - `new_accomplishments`: empty array
  - `gap_context`: empty array
  - `section_priorities`: empty object
  - `target_role_insights`: Extract target role details from notes if mentioned
  - `research_results`: empty array
  - `interview_metadata`: `{ "questions_asked": 0, "categories_covered": [], "duration_estimate": "0 minutes" }`

  Proceed to Step 4 with `interview-findings.json` available. Changes informed by notes will have `source: interview` in the manifest.

- **If no user notes were provided:** Proceed directly to Step 4. No `interview-findings.json` is produced. The rewriter runs with analysis data only, and all changes in the manifest will have `source: analysis`.

#### 3.5.2: Load Context for Question Selection

Read the following files from the session directory to inform question selection:

1. **`scores-summary.json`** -- dimension scores and overall score for category relevance scoring
2. **`ats-analysis.json`** (if available) -- ATS issues and structure quality findings
3. **`content-analysis.json`** (if available) -- bullet-level scores, quantification gaps, weak patterns
4. **`keyword-analysis.json`** (if available) -- keyword gaps and alignment data
5. **`strategy-analysis.json`** (if available) -- career archetype, strategic positioning, value proposition assessment
6. **`skills-research.json`** (if available) -- market demand data and skills intelligence
7. **`user-notes.txt`** (if available) -- free-form user context collected in Step 2.7; used to avoid re-asking topics the user already covered

If `scores-summary.json` is missing, proceed with the interview using available analysis files, but skip category scoring that depends on dimension scores. If no analysis files are available at all, skip the interview and proceed to Step 4 with a note:
> Interview skipped -- insufficient analysis data for targeted questions.

#### 3.5.3: Score Question Categories

Score 6 question categories for relevance (0-10) based on the analysis findings. Higher scores indicate greater relevance and priority for the interview.

**Category 1: Career Aspirations**
- Triggered by: weak strategic positioning score (<70), no job description provided, career transitions detected in `strategy-analysis.json`, user notes mentioning career change or uncertainty
- Score higher (7-10) when: strategy score is low, no JD present, career transition signals detected
- Score lower (0-3) when: strategy score is strong (>85), clear career trajectory visible, JD provides sufficient direction context

**Category 2: Undersold Accomplishments**
- Triggered by: low content score (<70), quantification gaps identified in `content-analysis.json`, weak bullet patterns detected (score 1-2 bullets)
- Score higher (7-10) when: content score is low, many bullets lack metrics, quantification gaps flagged
- Score lower (0-3) when: content score is strong (>85), bullets are well-quantified

**Category 3: Emphasis Preferences**
- Always relevant -- universally valuable for tailoring optimization
- Base score: 5 (always included in consideration)
- Score higher (7-8) when: multiple career directions possible, diverse skill set, user notes don't already cover emphasis
- Score lower (4-5) when: user notes already clearly specify emphasis preferences

**Category 4: Gap Explanations**
- Triggered by: employment gaps detected in `parsed-resume.json` timeline or `strategy-analysis.json`, career transitions visible, unexplained short tenures
- Score higher (7-10) when: gaps detected, career transitions present, short tenures flagged
- Score lower (0-2) when: no gaps detected, linear career progression

**Category 5: Section-Specific Concerns**
- Triggered by: any dimension scoring below 70, specific sections flagged as weak in analysis files, formatting issues concentrated in specific sections
- Score higher (7-10) when: multiple dimensions score low, specific section weaknesses identified
- Score lower (0-3) when: all dimensions score well, no section-specific issues flagged

**Category 6: Target Role Context**
- Triggered by: job description provided with significant alignment gaps, missing or weak JD alignment in `keyword-analysis.json`, user mentions specific companies or roles in notes
- Score higher (7-10) when: JD present with alignment gaps, keyword analysis shows significant missing terms
- Score lower (0-3) when: no JD provided (unless career aspirations category already covers direction), strong JD alignment

**Adjustments based on user notes:** If `user-notes.txt` covers topics that a category would ask about, reduce that category's score by 3-4 points to avoid redundancy. The interview should complement, not repeat, previously collected context.

#### 3.5.4: Select Questions

1. **Rank categories** by relevance score (highest first).
2. **Select top 3-5 categories** for the interview.
3. **Generate 1-2 personalized seed questions per selected category**, incorporating specifics from the resume and analysis findings (company names, section names, score references, specific findings).
4. **When `polish_mode` is `true` (overall score >= 85):** Reduced interview -- select only 2-3 categories and limit to 1 question each. Focus on emphasis preferences and any targeted improvements.
5. **Order questions** for natural conversational flow: start with broader context (career aspirations, emphasis preferences), then drill into specifics (accomplishments, gaps, section concerns, target role).
6. **Initialize tracking state:** Set `questions_asked = 0`, `consecutive_short_responses = 0`, `research_tasks = []`, `categories_covered = []`, `findings = {}`.

#### 3.5.5: Conduct Multi-Turn Interview

Present an opening message to the user:

> Based on your analysis results, I have a few targeted questions to help strengthen the optimization. This typically takes 3-7 questions. You can type **done** at any time to skip ahead.

Then execute the question loop:

**For each question round:**

1. **Present the question** via `AskUserQuestion`. Use bidirectional communication -- explain relevant analysis findings to the user while asking for their input. For example:
   > "Your content score was 68/100, primarily because several bullets lack quantified impact. Can you tell me about specific metrics or achievements from your role at {company}? Revenue impact, team size, efficiency gains, user growth -- any numbers help."

2. **Process the response:**
   - **Extract new information**: Identify accomplishments, skills, preferences, context, or career direction not present in the original resume or notes. Record these in the findings.
   - **Check for follow-up threads**: If the response opens a promising thread (e.g., mentions a major project without details), generate a targeted follow-up question before moving to the next category.
   - **Check for research triggers**: If the response mentions a specific company, industry, unfamiliar technology, or specialized skill, dispatch a background research task (see Step 3.5.6).
   - **Track coverage**: Mark categories as adequately covered when responses provide sufficient context for optimization.

3. **Update tracking state:**
   - Increment `questions_asked`.
   - **Disengagement detection**: If the response is under 10 words, increment `consecutive_short_responses`. If the response is 10 words or more, reset `consecutive_short_responses` to 0.

4. **Check exit conditions** (evaluate in this order):
   - **User says "done" or "skip"**: Respect immediately. Proceed to Step 3.5.7 with `status: partial`.
   - **7-question hard cap**: If `questions_asked >= 7`, end the interview. Proceed to Step 3.5.7 with `status: complete`.
   - **Disengagement detected**: If `consecutive_short_responses >= 2`, offer a graceful wrap-up via `AskUserQuestion`:
     > "I notice the responses are brief -- would you like to wrap up the interview and proceed to optimization with what we have?"
     If the user confirms, proceed to Step 3.5.7 with `status: partial`. If the user wants to continue, reset `consecutive_short_responses` to 0 and continue the interview.
   - **All selected categories covered**: If all selected categories have sufficient context, end the interview. Proceed to Step 3.5.7 with `status: complete`.

5. **Generate the next question**: Either a follow-up to deepen the current thread, or the next planned seed question from the queue. Adapt based on information gathered so far.

**Closing message** when the interview concludes:

> Thanks for the additional context. These insights will directly inform the optimization -- particularly around {top 2-3 areas the interview enriched}.

#### 3.5.6: Background Research Dispatch

During the interview, dispatch background research when the user's responses mention:
- **Specific companies** they are targeting or interested in
- **New industries or roles** not reflected in the resume or job description
- **Unfamiliar skills or technologies** mentioned for the first time
- **Accomplishments that could benefit from benchmarking**

**Dispatch process:**

1. Identify the research trigger from the user's response.
2. Determine the appropriate query type: `company_research`, `industry_trends`, `skills_demand`, or `role_requirements`.
3. Dispatch the `interview-researcher` agent via the `Task` tool with `run_in_background: true`, providing:
   - The query type
   - A specific research query based on the trigger
   - The path to `parsed-resume.json` (for candidate context)
   - The session directory path
4. Record the dispatched task in `research_tasks` for collection later.
5. **Do not block the interview** on research results. Continue asking questions while research runs in the background.
6. **Track dispatched queries** to avoid duplicate dispatches for the same topic.

**If research dispatch fails** (Task tool error, agent unavailable): Log the failure and continue the interview without research. The interview is not blocked by research failures.

#### 3.5.7: Collect Research and Compile Findings

After the interview closes:

1. **Collect background research results**: Wait up to 30 seconds for pending research tasks to complete. For each dispatched research task:
   - If the task completed: Extract the structured research brief (query_type, query, findings, sources, relevance_to_resume) and add `status: complete`.
   - If the task is still running after 30 seconds: Include it with `status: partial` and a note that research was in progress.
   - If the task failed or returned no results: Include it with `status: inconclusive` and findings set to "Research inconclusive -- {explanation of what was searched}".
   - If no research tasks were dispatched: The `research_results` array is empty.

2. **Fold in user notes**: If `user-notes.txt` exists in the session directory (from Step 2.7), incorporate the notes content into the interview findings. Notes context supplements interview responses -- when both sources provide information for the same field (e.g., career_direction), synthesize them together. Notes-derived content should be clearly attributable by including it alongside interview-gathered data, not replacing it.

3. **Compile `interview-findings.json`**: Write the interview findings to the session directory, conforming to `${CLAUDE_PLUGIN_ROOT}/schemas/interview-findings.schema.json`. The file contains:

   - **`status`** (required): `"complete"` if all selected categories were covered and the interview ended naturally, `"partial"` if the user said "done"/"skip" early, disengagement was detected, or the interview was interrupted.
   - **`career_direction`** (string): Summary of career aspirations and trajectory preferences gathered during the interview and/or user notes. Empty string if not discussed.
   - **`new_accomplishments`** (array): Accomplishments, metrics, or experiences shared during the interview that are not in the original resume. Each entry includes:
     - `content`: Description of the accomplishment
     - `confidence`: Always `"low"` (interview-sourced, not verified against original resume)
     - `verification_required`: Always `true` (user-reported, needs verification)
   - **`emphasis_preferences`** (array of strings): What the user wants highlighted, de-emphasized, or reframed.
   - **`gap_context`** (array of objects): Explanations for employment gaps, career transitions, or short tenures. Each entry has `gap_type` and `explanation`.
   - **`section_priorities`** (object): Maps section names to priority levels (`"high"`, `"medium"`, `"low"`).
   - **`target_role_insights`** (object): Additional context about target role, company, or application strategy. Fields: `target_title`, `target_company`, `target_industry`.
   - **`research_results`** (array): Compiled results from interview-researcher agent tasks. Each entry conforms to the `research_result` definition in the schema, with fields: `query_type`, `query`, `findings`, `sources`, `relevance_to_resume`, `status`.
   - **`optimization_directives`** (required, array of strings): Prioritized list of specific optimization actions synthesized from all interview data. These are actionable instructions for the rewriter (e.g., "Emphasize leadership experience over technical skills", "Add quantified metrics for the role at {company}", "Frame the career transition from {field A} to {field B} as intentional progression").
   - **`interview_metadata`** (object): Tracking data including `questions_asked` (integer), `categories_covered` (array of category name strings), and `duration_estimate` (string, e.g., "3-5 minutes").

4. **Handle contradictory information**: If the user provided contradictory information during the interview or between notes and interview responses (e.g., expressed interest in both management and IC roles), record both statements in the relevant fields and add a note in `optimization_directives` for the rewriter to handle (e.g., "User indicated interest in both management and IC roles -- default to resume's existing emphasis unless further clarification is available").

5. **Validate the output**: The `interview-findings.json` file is validated against `${CLAUDE_PLUGIN_ROOT}/schemas/interview-findings.schema.json` by the PreToolUse hook when written.

#### 3.5.8: Edge Cases

- **User skips interview (Step 3.5.1)**: If user notes were provided (Step 2.7), a minimal `interview-findings.json` is produced with notes-derived context. If no notes were provided, no `interview-findings.json` is produced and all changes default to `source: analysis`.
- **Partial interview (user says "done" early)**: Findings are written with `status: partial`. Whatever was gathered is passed to the rewriter. Incomplete categories are omitted from findings rather than filled with placeholder data.
- **Research agent returns no results**: The `research_results` array entry for that query notes `status: inconclusive` with findings set to "Research inconclusive".
- **User provides contradictory information**: Recorded in findings and noted in `optimization_directives` for the rewriter to handle.
- **When `polish_mode` is `true` (score >= 85)**: Reduced interview -- 2-3 categories, 1 question each. Focus on emphasis preferences and targeted improvements.
- **Disengagement detection**: 2+ consecutive short responses (under 10 words each) triggers a graceful wrap-up offer via `AskUserQuestion`. If the user wants to continue, the counter resets.
- **Research dispatch fails**: Interview continues without research data. The failure is logged but does not block the interview.
- **Research incomplete at interview close**: Results are included with `status: partial` after the 30-second collection timeout.
- **Analysis files missing**: Interview uses whatever analysis data is available. Categories that depend on missing analysis files are scored 0 and excluded from selection.
- **All analysis files missing**: Interview is skipped entirely with a note to the user (see Step 3.5.2).

### Step 4: Delegate to Resume Rewriter

Delegate to the **resume-rewriter** subagent, providing:
- The session directory path (where all analysis files are located)
- The rewriting mode (conservative or full rewrite)
- The path to the original resume file in `{workspace}/{slug}/input/` (for reference)
- The path to `interview-findings.json` in the session directory (if the interview was conducted in Step 3.5 and the file was produced)
- The `polish_mode` flag (if `true`, the rewriter operates in "polish only" mode -- limiting changes to formatting fixes, minor rewording, and keyword optimization; no structural changes, no section reordering, no major content additions)

The resume-rewriter subagent will:
1. Read all available analysis files from the session directory
2. If `interview-findings.json` is present, integrate interview context via Step 1.5 of the rewriter's procedure (career direction, new accomplishments, emphasis preferences, gap context, section priorities, target role insights, research results, and optimization directives)
3. If `polish_mode` is `true`, activate "polish only" mode (limiting scope to formatting, minor rewording, and keywords)
4. Load the resume writing skill and transformation rules
5. Select a template based on the detected career archetype
6. Transform bullets, rewrite the summary, reorganize skills, adjust section order
7. Write three output files to the session directory:
   - `optimization-report.md` -- before/after pairs with explanations
   - `optimized-resume.md` -- the complete optimized resume
   - `change-manifest.json` -- structured manifest of all changes with confidence levels, source attribution, and verification flags

### Step 5: Verify Output

After the resume-rewriter completes, verify that the output files were created:

1. Check for `optimization-report.md` in the session directory.
2. Check for `optimized-resume.md` in the session directory.
3. Check for `change-manifest.json` in the session directory (non-blocking -- see Step 6 for handling).

**If `optimization-report.md` is missing:**
> The resume-rewriter did not produce an optimization report. Please try running `/optimize-resume` again.

Stop execution.

### Step 6: Present Change Manifest

Read `change-manifest.json` from the session directory and present a transparency summary of all proposed changes to the user.

#### 6.1: Read and Validate the Manifest

1. Read `change-manifest.json` from the session directory.
2. If the file does not exist (rewriter failed to produce it), log a warning and skip to Step 8:
   > **Note:** Change manifest was not generated. Falling back to optimization report for change details.
3. If the file exists but cannot be parsed as valid JSON, log a warning and skip to Step 8:
   > **Note:** Change manifest could not be read (malformed data). Falling back to optimization report for change details.

#### 6.2: Handle Empty Manifest

If `change-manifest.json` exists and is valid but the `changes` array is empty (no changes recommended):

Display to the user:
> **No changes recommended.** The rewriter determined that no optimization changes are warranted for this resume.

If the manifest `metadata.summary` field is present, display it as the explanation:
> Reason: {metadata.summary}

Skip the rest of Step 6, skip Step 7 (approval workflow), and proceed to Step 8.

#### 6.3: Display Changes Grouped by Section

Group the changes by their `section` field and display them organized by resume section. Use the following section display order: Summary, Experience, Skills, Education, Certifications, Structure.

For each section that has changes, display a section header and list each change with:
- **Change ID** -- the sequential identifier (e.g., `#1`, `#2`)
- **Confidence level** -- High, Medium, or Low
- **Source attribution** -- analysis, interview, or both
- **Verification flag** -- if `verification_required` is `true`, prefix with a `[!]` indicator
- **Brief description** -- the `rationale` field (truncated if very long)

**Display format per section:**

> **{Section Name}** ({N} changes)
>
> - `#{change_id}` [{confidence}] (source: {source}) -- {rationale}
> - `[!] #{change_id}` [{confidence}] (source: {source}) -- {rationale}  *(verification required)*

Changes with `verification_required: true` or `confidence: Low` are visually flagged:
- Prefix `[!]` before the change ID for verification-required changes
- Append `*(verification required)*` after the rationale for verification-required changes
- Low-confidence changes always display their confidence level prominently as `[Low]`

#### 6.4: Display Overall Statistics

After the per-section breakdown, present aggregate statistics from the manifest metadata:

> **Change Summary:**
> - Total changes: {metadata.total_changes}
> - Confidence breakdown: {metadata.confidence_breakdown.high} high, {metadata.confidence_breakdown.medium} medium, {metadata.confidence_breakdown.low} low
> - Verification required: {count of changes where verification_required is true}

If there are any low-confidence or verification-required changes, add a note:

> **Attention:** {N} change(s) are flagged for review. These include low-confidence rewrites or changes requiring user verification. Review these carefully in the optimization report.

### Step 7: Change Approval Workflow

After presenting the change manifest (Step 6), give the user granular control over which changes to accept or reject. This step uses `AskUserQuestion` for interactive approval.

#### 7.1: Present Detailed Changes for Review

Read `change-manifest.json` and present each change grouped by resume section with full detail for the user's review. For each change, display:

- **Change number** -- the `change_id` (e.g., `CHG-001`)
- **Confidence level** -- High, Medium, or Low
- **Verification flag** -- `[!]` indicator if `verification_required` is `true`
- **Source attribution** -- analysis, interview, or both
- **Before/after text diff** -- the `original_text` and `optimized_text` fields displayed as a diff
- **Rationale** -- the full `rationale` field explaining why the change was made

**Display format per change:**

> **Change #{change_id}** [{confidence}] (source: {source})
> {`[!] Verification required` if verification_required is true}
>
> **Before:**
> > {original_text}
>
> **After:**
> > {optimized_text}
>
> **Rationale:** {rationale}

Visually flag changes that need extra attention:
- Changes with `confidence: Low` are prefixed with a `[Low confidence]` warning indicator
- Changes with `verification_required: true` are prefixed with a `[!] Verification required` warning indicator
- These warning indicators ensure Low-confidence and verification-required changes stand out during review

#### 7.2: Present Three-Way Approval Prompt

After presenting all changes, use `AskUserQuestion` to present three approval options:

> **How would you like to proceed with these changes?**
>
> 1. **Accept All** -- Apply all {N} changes to your resume
> 2. **Reject All** -- Keep your original resume unchanged
> 3. **Selective** -- Choose specific changes to accept or reject (provide change numbers)

The user responds with their choice via `AskUserQuestion`.

#### 7.3: Handle "Accept All"

When the user selects "Accept All":

1. Update all changes in `change-manifest.json` to `status: accepted`
2. The existing `optimized-resume.md` (produced in Step 4) is used as the final output -- no rewriter re-invocation needed
3. Write the updated `change-manifest.json` back to the session directory with all statuses set to `accepted`
4. **Finalize the optimization report**: Update `optimization-report.md` to reflect the final approval status of all changes:
   - Add `**Status:** Accepted` to each change block's metadata (after `**Confidence:**` and `**Source:**` lines)
   - Append an `## Approval Summary` section at the end of the report with:
     - **Total Accepted:** {N} (all changes)
     - **Total Rejected:** 0
     - **Approval Mode:** Accept All
5. Proceed to Step 8

#### 7.4: Handle "Reject All"

When the user selects "Reject All":

1. Update all changes in `change-manifest.json` to `status: rejected`
2. The original resume is preserved -- `optimized-resume.md` is not used as the final output
3. Write the updated `change-manifest.json` back to the session directory with all statuses set to `rejected`
4. **Finalize the optimization report**: Update `optimization-report.md` to reflect the final rejection status of all changes:
   - Add `**Status:** Rejected` to each change block's metadata (after `**Confidence:**` and `**Source:**` lines)
   - Wrap each rejected change title in strikethrough with a `[REJECTED]` suffix (e.g., `### ~~Change #N: [title]~~ [REJECTED]`)
   - Wrap the Before/After lines of each rejected change in strikethrough to visually distinguish them
   - Append an `## Approval Summary` section at the end of the report with:
     - **Total Accepted:** 0
     - **Total Rejected:** {N} (all changes)
     - **Approval Mode:** Reject All
5. Display a message to the user:
   > All changes have been rejected. Your original resume has been preserved unchanged.
   > You can re-run `/optimize-resume` at any time to generate new optimization suggestions.
6. Skip Step 8 (results summary is not applicable when all changes are rejected). Proceed to Step 9 (Before/After Score Comparison) -- re-analysis runs on the original resume to show zero delta as an honest baseline.

#### 7.5: Handle "Selective" Approval

When the user selects "Selective":

1. **Parse user's selections**: The user provides change numbers (e.g., "1, 3, 5" or "CHG-001, CHG-003, CHG-005") indicating which changes to accept. All other changes are rejected.
2. **Validate change numbers**: Verify each provided number corresponds to a valid change in the manifest. If any change numbers are invalid, re-prompt the user via `AskUserQuestion` with the valid range:
   > Some change numbers were not recognized. Valid change numbers are: {list of valid change_ids}. Please provide the change numbers you want to accept.
3. **Update manifest statuses**: Mark selected changes as `status: accepted` and all others as `status: rejected` in `change-manifest.json`.
4. **Prepare filtered manifest**: Create a filtered version of the manifest containing only the accepted changes (changes with `status: accepted`).
5. **Re-invoke the resume-rewriter**: Delegate to the resume-rewriter subagent in **constrained mode**, providing:
   - The original `parsed-resume.json` from the session directory
   - The filtered `change-manifest.json` (accepted changes only)
   - `interview-findings.json` (if present in the session directory)
   - Instructions to produce a cohesive final document incorporating only the accepted changes
6. The re-invoked rewriter produces:
   - An updated `optimized-resume.md` -- the final resume with only accepted changes applied, reading as a cohesive document
   - An updated `optimization-report.md` -- reflecting all changes with their final status (accepted changes in normal format, rejected changes visually distinguished with strikethrough and `[REJECTED]` suffix), a "Constrained Mode Summary" section, and an "Approval Summary" section
   - An updated `change-manifest.json` -- with final accepted/rejected statuses and updated metadata counts
7. **Verify re-invocation output**: Check that the rewriter produced valid output files. If the re-invocation fails, fall back to the original `optimized-resume.md` with a warning:
   > **Warning:** The rewriter re-invocation did not complete successfully. Falling back to the original optimized resume (which contains all changes). You may want to manually remove the rejected changes.
8. **Write final manifest**: Write the updated `change-manifest.json` with final statuses back to the session directory. Ensure `metadata.total_changes` and `metadata.confidence_breakdown` reflect only accepted changes.
9. **Finalize the optimization report**: Ensure `optimization-report.md` reflects the accepted/rejected status of each change:
   - Accepted changes show `**Status:** Accepted` and retain their full before/after detail in normal format
   - Rejected changes show `**Status:** Rejected` with their title wrapped in strikethrough and `[REJECTED]` suffix, and Before/After lines in strikethrough
   - An `## Approval Summary` section is appended at the end with:
     - **Total Accepted:** {N}
     - **Total Rejected:** {M}
     - **Approval Mode:** Selective
10. Proceed to Step 8

#### 7.6: Edge Cases

- **User accepts all but one change**: Always re-invoke the rewriter in constrained mode. Do not attempt to manually patch text -- the rewriter ensures document coherence across all accepted changes.
- **User rejects all changes via selective (accepts none)**: Treat identically to "Reject All" (Step 7.4). Skip re-invocation, preserve original resume, proceed to Step 9 for scoring with zero delta.
- **Empty manifest (no changes)**: This case is handled in Step 6.2 -- the approval workflow (Step 7) is skipped entirely when the manifest has no changes. An explanatory message is displayed to the user.
- **Single change in manifest**: Still present all three approval options (Accept All, Reject All, Selective). The user may want to reject even a single change.
- **Rewriter re-invocation fails**: Fall back to the original `optimized-resume.md` with a warning message (see Step 7.5.7). The manifest is still updated with the user's approval decisions.
- **Invalid change numbers from user**: Re-prompt via `AskUserQuestion` with the valid range of change numbers (see Step 7.5.2). Do not proceed until valid selections are provided.

### Step 8: Present Results Summary

Read `optimization-report.md` from the session directory and present a conversational summary to the user.

**Summary format:**

1. **Optimization Overview** -- brief statement of the approach taken and career archetype used
2. **Key Changes** -- highlight the 5-7 most impactful changes with before/after snippets:
   - Summary section changes (if any)
   - Top 3-4 bullet transformations showing the strongest improvements
   - Skills section reorganization highlights
   - Section order changes (if any)
3. **Change Statistics** -- total number of changes made, broken down by section (summary, experience, skills, structure)
4. **Approval Summary** -- if the approval workflow was used, note how many changes were accepted vs rejected and the approval mode used (Accept All, Reject All, or Selective)
5. **Interview Context Note** -- if the interview was conducted (Step 3.5), note which categories were covered and how interview insights informed the optimization
6. **Missing Analysis Note** -- if any analysis files were unavailable, note which optimizations were limited as a result
7. **Output Files** -- tell the user where the files are saved:
   > Full optimization report: `{workspace}/{slug}/sessions/{session}/optimization-report.md`
   > Optimized resume: `{workspace}/{slug}/sessions/{session}/optimized-resume.md`
   > Change manifest: `{workspace}/{slug}/sessions/{session}/change-manifest.json`
   > Interview findings: `{workspace}/{slug}/sessions/{session}/interview-findings.json` (if interview was conducted)
8. **Next Steps** -- suggest the user:
   - Review the optimization report to understand each change
   - Review any flagged changes (verification-required or low-confidence) with extra attention
   - Check any `[X]` placeholders in the optimized resume and fill in real metrics
   - Compare the optimized resume against the original

Keep the summary concise but informative. Show enough before/after pairs to demonstrate the quality of the improvements without overwhelming the user.

### Step 9: Before/After Score Comparison

After the approval workflow and results summary (or directly after Reject All), run a full re-analysis pipeline on the optimized resume to validate optimization improvement through score comparison. This step uses the same analysis agents and scoring rubric as the original analysis to ensure a fair comparison.

#### 9.1: Determine Re-Analysis Target

Select the resume file to re-analyze based on the approval outcome:

- **Accept All or Selective (with accepted changes):** Re-analyze `optimized-resume.md` from the session directory.
- **Reject All:** Re-analyze the original resume file from `{workspace}/{slug}/input/` to produce an honest zero-delta baseline. This confirms the scoring is consistent and shows no artificial improvement.

#### 9.2: Create Post-Optimization Directory

Create a `post-opt/` subdirectory within the session directory:

```
{workspace}/{slug}/sessions/{session}/post-opt/
```

**If directory creation fails:** Display a warning and skip the comparison:
> **Warning:** Could not create post-optimization directory. Score comparison skipped.

Proceed to end of workflow without comparison.

#### 9.3: Run Re-Analysis Pipeline

Dispatch the re-analysis agents in parallel using the `Task` tool, following the same parallel dispatch pattern as the analyze-resume skill's Step 4. The re-analysis target (from Step 9.1) is analyzed as if it were a fresh resume.

**Sequential first:**
1. **resume-parser** on the re-analysis target resume -> `post-opt/parsed-resume.json`

**If resume parsing fails:** Display a warning and skip the comparison:
> **Warning:** Could not parse the optimized resume for re-scoring. Score comparison skipped.

Append a note to `optimization-report.md`:
> ## Score Comparison
>
> Score comparison was not possible -- the optimized resume could not be parsed for re-analysis.

Proceed to end of workflow without comparison.

**Then dispatch in parallel (using Task tool with `run_in_background: true`):**
2. **content-analyst** -> `post-opt/content-analysis.json`
3. **ats-analyzer** -> `post-opt/ats-analysis.json`
4. **strategy-advisor** -> `post-opt/strategy-analysis.json`
5. **skills-research** (only if `skills-research.json` exists in the original session) -> `post-opt/skills-research.json`
6. **keyword-optimizer** (only if `keyword-analysis.json` exists in the original session, indicating a JD was provided) -> `post-opt/keyword-analysis.json`

All agents receive the `post-opt/` directory as their session directory, reading `post-opt/parsed-resume.json` as their input.

Tell the user:
> Running re-analysis on the optimized resume to measure improvement...

**As each agent completes**, note progress. **On individual agent failure:** Record the failure and continue with remaining agents. The dimension will show "N/A" in the comparison table.

#### 9.4: Compute Post-Optimization Scores

Run the scoring script on the `post-opt/` directory:

```bash
${CLAUDE_PLUGIN_ROOT}/scripts/run-python.sh ${CLAUDE_PLUGIN_ROOT}/scripts/compute-scores.py {workspace}/{slug}/sessions/{session}/post-opt/
```

This produces `post-opt/scores-summary.json` using the same rubric and weights as the original scoring.

**If `compute-scores.py` fails:** Display a warning and skip the comparison:
> **Warning:** Score computation failed for the optimized resume. Score comparison skipped.

Append a note to `optimization-report.md`:
> ## Score Comparison
>
> Score comparison was not possible -- score computation failed for the optimized resume.

Proceed to end of workflow without comparison.

#### 9.5: Compute Score Deltas

Read both score files:
- **Original scores:** `scores-summary.json` from the session root
- **Post-optimization scores:** `post-opt/scores-summary.json`

For each dimension present in both score sets, compute:
- `before`: original dimension score
- `after`: post-optimization dimension score
- `delta`: after - before (positive = improvement, negative = regression)

For dimensions present in only one score set (due to agent failure in either run), show "N/A" for the missing value and no delta.

Compute overall:
- `overall_before`: original `overall_score`
- `overall_after`: post-optimization `overall_score`
- `overall_delta`: overall_after - overall_before

#### 9.6: Present Score Comparison

Display the comparison as a formatted table in chat:

```
| Dimension              | Before | After | Change |
|------------------------|--------|-------|--------|
| ATS Compatibility      | {score} | {score} | {+/-delta} |
| Content Quality        | {score} | {score} | {+/-delta} |
| Strategic Positioning  | {score} | {score} | {+/-delta} |
| Structure & Format     | {score} | {score} | {+/-delta} |
| Market Intelligence    | {score} | {score} | {+/-delta} |
| Keyword Alignment      | {score} | {score} | {+/-delta} |
| **Overall**            | **{score}** | **{score}** | **{+/-delta}** |
```

Use `+` prefix for positive deltas, `-` prefix for negative deltas, and `0` for no change.

**Dimension display names** mapping from internal keys:
- `ats_compatibility` -> "ATS Compatibility"
- `content_quality` -> "Content Quality"
- `strategic_positioning` -> "Strategic Positioning"
- `structure_format` -> "Structure & Format"
- `market_intelligence` -> "Market Intelligence"
- `keyword_alignment` -> "Keyword Alignment"

**For dimensions where re-analysis failed** (agent failure in Step 9.3): Show "N/A" in the After column and "--" in the Change column. The overall score is computed from available dimensions using the existing weight redistribution logic in `compute-scores.py`.

**Highlight the largest improvement dimension:**
> **Largest improvement:** {Dimension Name} (+{delta} points)

**If overall score decreased (optimization made things worse):**
> **Warning:** The overall score decreased by {delta} points after optimization. Review the changes to identify which may have contributed to the regression.

**If overall improvement is trivial (<2 points):**
> Minor improvement -- the original resume was already strong in most areas.

**If a specific dimension decreased:** Show the negative delta honestly. Do not hide regressions. For example: `| Content Quality | 78 | 75 | -3 |`

#### 9.7: Append Score Comparison to Report

Append a `## Score Comparison` section to `optimization-report.md` with:

1. The full comparison table (same format as the chat display)
2. The largest improvement dimension highlight
3. Any warnings (overall decrease, trivial improvement)
4. A note on which dimensions were compared (and which showed "N/A")

**Format:**

```markdown
## Score Comparison

Re-analysis of the optimized resume produced the following score comparison:

| Dimension | Before | After | Change |
|-----------|--------|-------|--------|
| ... | ... | ... | ... |
| **Overall** | **{score}** | **{score}** | **{+/-delta}** |

**Largest improvement:** {Dimension Name} (+{delta} points)

{Any warnings or notes}
```

#### 9.8: Edge Cases

- **Re-analysis agent fails for a dimension**: Show "N/A" for that dimension in the comparison table. Compute overall from available dimensions using the existing weight redistribution logic in `compute-scores.py`. Note which dimensions were unavailable.
- **Optimized resume can't be parsed**: Score comparison is skipped entirely with a warning (see Step 9.3). The `optimization-report.md` notes that re-scoring was not possible.
- **Trivial improvement (<2 points overall)**: Display the comparison table as normal but add a note: "Minor improvement -- the original resume was already strong in most areas."
- **Score decreased for a dimension**: Show the negative delta. Do not hide regressions. The comparison is presented honestly.
- **User rejected all changes**: Re-analysis runs on the original resume (Step 9.1). This produces a zero (or near-zero) delta, serving as an honest baseline that confirms scoring consistency.
- **Original `scores-summary.json` missing**: If the original session does not have `scores-summary.json` (e.g., `compute-scores.py` failed during the original analysis), skip the comparison with a warning:
  > **Warning:** Original scores are not available for comparison. Run `/analyze-resume` first for a complete analysis with scoring.
- **Post-opt directory already exists**: Overwrite any existing `post-opt/` contents from a previous optimization run in the same session.


## Error Handling

### No Prior Analysis Found
If no session directory contains `parsed-resume.json` and at least one analysis file:
> No prior analysis run found. Please run `/analyze-resume` first to analyze your resume, then run `/optimize-resume` to generate optimized content.

### Parsed Resume Has Errors
If `parsed-resume.json` exists but contains `"error": true`:
> The parsed resume contains errors from a previous run. Please run `/analyze-resume` again to re-parse your resume.

### Scores Summary Missing or Malformed
If `scores-summary.json` does not exist or contains invalid JSON during the high-score check (Step 2.5):
> **Note:** Could not read scoring data from `scores-summary.json`. Proceeding with standard optimization.

The high-score check is skipped and the standard optimization flow proceeds. This is a non-blocking condition.

### Rewriter Fails to Produce Output
If the resume-rewriter subagent completes but does not produce the expected output files:
> Resume optimization did not complete successfully. Please try again. If the problem persists, try running `/analyze-resume` first to refresh the analysis data.

### Change Manifest Missing
If `change-manifest.json` is not found in the session directory after the rewriter completes:
> **Note:** Change manifest was not generated. Falling back to optimization report for change details.

The skill continues to Step 8 without the manifest. This is a non-blocking warning. The approval workflow (Step 7) is skipped.

### Change Manifest Malformed
If `change-manifest.json` exists but contains invalid JSON or does not match the expected structure:
> **Note:** Change manifest could not be read (malformed data). Falling back to optimization report for change details.

The skill continues to Step 8 without the manifest. This is a non-blocking warning. The approval workflow (Step 7) is skipped.

### Rewriter Re-invocation Fails
If the resume-rewriter re-invocation during selective approval (Step 7.5) fails to produce output:
> **Warning:** The rewriter re-invocation did not complete successfully. Falling back to the original optimized resume (which contains all changes). You may want to manually remove the rejected changes.

The manifest is still updated with the user's approval decisions. The workflow continues to Step 8.

### Invalid Change Numbers
If the user provides invalid change numbers during selective approval:
> Some change numbers were not recognized. Valid change numbers are: {list of valid change_ids}. Please provide the change numbers you want to accept.

The user is re-prompted via `AskUserQuestion` until valid selections are provided.

### Interview Research Dispatch Fails
If the interview-researcher agent cannot be dispatched during the interview (Task tool error or agent unavailable):
> Research dispatch failed. Continuing interview without background research.

The interview continues without research data. This is a non-blocking failure.

### Interview Research Incomplete at Close
If research tasks have not completed when the interview ends and the 30-second collection timeout expires:

Research results are included in `interview-findings.json` with `status: partial` and a note that research was still in progress. The rewriter proceeds with whatever research data is available.

### Analysis Files Missing During Interview
If analysis files needed for interview question scoring are unavailable:

The interview proceeds with available data. Categories that depend on missing analysis files are scored 0 and excluded from question selection. If no analysis data is available at all, the interview is skipped.

### Re-Analysis Agent Failure
If one or more re-analysis agents fail during Step 9.3:

The failed dimension shows "N/A" in the score comparison table. The overall post-optimization score is computed from available dimensions using the existing weight redistribution logic in `compute-scores.py`. The comparison proceeds with available data. This follows the same graceful degradation pattern as the original analysis pipeline.

### Post-Optimization Score Computation Failure
If `compute-scores.py` fails on the `post-opt/` directory during Step 9.4:
> **Warning:** Score computation failed for the optimized resume. Score comparison skipped.

A note is appended to `optimization-report.md` explaining that re-scoring was not possible. The workflow completes without the comparison.

### Post-Optimization Directory Creation Failure
If the `post-opt/` subdirectory cannot be created during Step 9.2:
> **Warning:** Could not create post-optimization directory. Score comparison skipped.

The workflow completes without the comparison. This is a non-blocking failure.

### Step 10: PDF Export Prompt

After the score comparison (or after Step 8 if score comparison was skipped), offer the user the option to export the optimized resume as a professionally formatted PDF.

**Skip this step if:** The user rejected all changes in Step 7 (Reject All). There is no optimized resume to export.

#### 10.1: Present Export Prompt

Ask the user via `AskUserQuestion`:

> **Would you like to export the optimized resume as a PDF?**
>
> 1. **Yes** (Recommended) -- Export as a professionally formatted, ATS-compatible PDF
> 2. **No** -- Skip PDF export

#### 10.2: If "Yes" — Run Export Flow

Follow the same flow as the `/export-pdf` skill:

1. **Preset selection** via `AskUserQuestion`:
   > Which style preset?
   > 1. **Modern** (Recommended) — Clean, contemporary sans-serif design
   > 2. **Classic** — Traditional serif design with conservative colors
   > 3. **Compact** — Dense, space-efficient design for maximum content

2. **Customization offer** via `AskUserQuestion`:
   > Customize styling, or use preset defaults?
   > 1. **Use preset defaults** (Recommended)
   > 2. **Customize** — Fine-tune font, color, margins, page size, spacing

   If the user chooses "Customize", present the same customization prompts as `/export-pdf` Step 3.

3. **Generate PDF** by running:
   ```bash
   ${CLAUDE_PLUGIN_ROOT}/scripts/run-python.sh ${CLAUDE_PLUGIN_ROOT}/scripts/md-to-pdf.py {workspace}/{slug}/sessions/{session}/optimized-resume.md {workspace}/{slug}/sessions/{session}/optimized-resume.pdf --preset <preset> [customization flags]
   ```

4. **Report result** to the user:
   > **PDF exported:** `{workspace}/{slug}/sessions/{session}/optimized-resume.pdf` ({file size})
   > The PDF uses embedded fonts and has a native text layer for ATS compatibility.

#### 10.3: If "No" — Skip

Continue to end of workflow. Inform the user they can run `/export-pdf` later to generate the PDF.

#### 10.4: Error Handling

If PDF generation fails:
> **Warning:** PDF export failed. You can retry with `/export-pdf` after resolving the issue.

This is a non-blocking failure. The optimization workflow is already complete.


## Example Usage

### Default (conservative mode)
```
/optimize-resume
```

Produces before/after pairs for each recommended change with explanations of why each change improves the resume. After review, the user can accept all, reject all, or selectively approve individual changes.

### Full rewrite mode
```
/optimize-resume (user requests "full rewrite" in conversation)
```

Generates a complete optimized resume applying all improvements at once. The approval workflow still applies -- the user can selectively accept or reject changes even in full rewrite mode.

### High-score flow
```
User: /optimize-resume
System: Your resume scored 92/100 (A-). This is an excellent score. Only minor polish is recommended. Would you like to proceed?
User: Yes, proceed with polish
System: [runs reduced interview -- 2-3 categories, 1 question each]
System: [runs rewriter in polish mode -- formatting, minor rewording, keywords only]
System: [presents changes for approval]
```

### With interview
```
User: /optimize-resume
System: Would you like to do a brief interview? (Recommended)
User: Yes, interview me
System: [asks 3-7 adaptive questions based on analysis findings]
System: [dispatches background research for mentioned companies/skills]
System: Thanks for the context. These insights will inform the optimization.
System: [runs rewriter with analysis + interview findings]
System: [presents changes with confidence levels and source attribution]
```

### Selective approval flow
```
User: /optimize-resume
System: [presents changes with confidence levels]
System: How would you like to proceed? (Accept All / Reject All / Selective)
User: Selective - accept 1, 3, 5, 7
System: [re-invokes rewriter with accepted changes only]
System: [presents final optimized resume with only accepted changes]
```

### Score comparison flow
```
User: /optimize-resume
System: [runs optimization, approval workflow completes]
System: Running re-analysis on the optimized resume to measure improvement...
System: [re-analysis agents run in parallel]
System:
| Dimension              | Before | After | Change |
|------------------------|--------|-------|--------|
| ATS Compatibility      | 72     | 81    | +9     |
| Content Quality        | 65     | 78    | +13    |
| Strategic Positioning  | 70     | 74    | +4     |
| Structure & Format     | 68     | 75    | +7     |
| Market Intelligence    | 71     | 73    | +2     |
| **Overall**            | **70** | **79**| **+9** |

Largest improvement: Content Quality (+13 points)

System: Would you like to export as a PDF?
User: Yes
System: Which style preset? (Modern / Classic / Compact)
User: Modern
System: Customize or use defaults?
User: Defaults
System: PDF exported: {workspace}/{slug}/sessions/2026-02-27-143000/optimized-resume.pdf (42.3 KB)
```
