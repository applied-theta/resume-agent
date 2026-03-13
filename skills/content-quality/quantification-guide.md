# Quantification Guide

This guide provides methodology and examples for auditing resume bullet points for quantification opportunities. The content-analyst agent uses this to identify bullets lacking metrics and suggest specific, appropriate metric types.

## Principles

1. **Not every bullet needs numbers** -- but high-impact accomplishments should always be quantified
2. **Approximate numbers are better than no numbers** -- "~50 users" is stronger than "users"
3. **Context makes numbers meaningful** -- "$500K" means different things at a startup vs. a Fortune 500
4. **Use brackets for unknowns** -- When suggesting metrics the candidate should add, use `[X]` placeholders: "Reduced latency by [X]%"

---

## Metric Type 1: Financial

Financial metrics demonstrate business impact in terms of revenue, cost savings, budget management, or return on investment.

### When to Suggest

Suggest financial metrics when the bullet describes:
- Cost reduction or optimization efforts
- Revenue-generating activities (sales, product launches, feature releases)
- Budget management or resource allocation
- Process improvements that have cost implications
- Vendor negotiations or procurement

### Metric Formats

| Format | Example | Best For |
|--------|---------|----------|
| Dollar amount | $1.2M, $50K | Revenue generated, costs saved, budget managed |
| Percentage of revenue | 15% revenue increase | Growth contributions |
| ROI | 300% ROI within 6 months | Investment justification |
| Cost per unit | Reduced cost-per-acquisition from $45 to $12 | Efficiency improvements |
| Budget size | Managed $3.5M annual budget | Scope of responsibility |

### Examples by Role

**Engineering:**
- Before: "Optimized cloud infrastructure costs"
- After: "Optimized cloud infrastructure, reducing AWS spend by $120K/year (18% reduction) through right-sizing instances and implementing reserved capacity"

**Sales:**
- Before: "Exceeded sales targets consistently"
- After: "Exceeded annual sales quota by 135%, generating $2.8M in new business revenue across 22 enterprise accounts"

**Operations:**
- Before: "Negotiated better vendor contracts"
- After: "Renegotiated 5 vendor contracts, saving $340K annually while improving SLA terms from 99.5% to 99.9% uptime"

**Product:**
- Before: "Launched a successful new feature"
- After: "Launched premium tier feature generating $800K ARR within 6 months, contributing to 12% overall revenue growth"

### Prompts for Candidates

When a bullet lacks financial metrics, ask:
- "How much money did this save or generate?"
- "What was the budget you managed?"
- "Can you estimate the dollar impact of this improvement?"
- "What was the before/after cost comparison?"

---

## Metric Type 2: Scale

Scale metrics demonstrate the scope and magnitude of the candidate's work -- how many users, systems, transactions, or team members were involved.

### When to Suggest

Suggest scale metrics when the bullet describes:
- Managing teams, people, or cross-functional groups
- Building or maintaining systems that serve users
- Processing transactions, requests, or data volumes
- Supporting customers, clients, or stakeholders
- Working across multiple projects, products, or regions

### Metric Formats

| Format | Example | Best For |
|--------|---------|----------|
| User count | 500K monthly active users | Product/platform scale |
| Team size | 12-person engineering team | Leadership scope |
| Transaction volume | 10M transactions/day | System scale |
| Customer count | 85 enterprise clients | Relationship management |
| Geographic scope | 6 countries, 3 time zones | Operational breadth |
| Project count | 8 concurrent projects | Workload management |
| Data volume | 50TB data warehouse | Technical scale |

### Examples by Role

**Engineering:**
- Before: "Built and maintained microservices"
- After: "Built and maintained 12 microservices handling 2M API requests/day with 99.99% uptime serving 300K users"

**Management:**
- Before: "Managed a team of engineers"
- After: "Managed a team of 8 engineers across 3 time zones, delivering 4 major product releases per quarter"

**Customer Success:**
- Before: "Managed enterprise client relationships"
- After: "Managed a portfolio of 45 enterprise accounts representing $12M in ARR, maintaining a 97% retention rate"

**Data Engineering:**
- Before: "Built data pipelines for analytics"
- After: "Built 15 data pipelines processing 2TB/day from 8 source systems, enabling real-time dashboards for 200 analysts"

### Prompts for Candidates

When a bullet lacks scale metrics, ask:
- "How many users/customers did this serve?"
- "How many people were on the team you managed?"
- "What was the volume of data/transactions/requests?"
- "How many systems, services, or projects were involved?"

---

## Metric Type 3: Efficiency

Efficiency metrics demonstrate improvements in speed, time savings, automation gains, or process optimization.

### When to Suggest

Suggest efficiency metrics when the bullet describes:
- Automating manual processes
- Reducing cycle times or turnaround times
- Streamlining workflows or eliminating bottlenecks
- Improving deployment frequency or release cadence
- Reducing error rates or rework

### Metric Formats

| Format | Example | Best For |
|--------|---------|----------|
| Time reduction | Reduced from 4 hours to 15 minutes | Process automation |
| Percentage improvement | 60% faster deployments | Speed improvements |
| Hours saved | Saved 200 hours/month | Automation impact |
| Frequency improvement | From monthly to daily releases | Cadence improvements |
| Before/after comparison | Reduced build time from 45 min to 8 min | Clear improvement story |
| Elimination | Eliminated 3 manual steps | Process simplification |

### Examples by Role

**DevOps/SRE:**
- Before: "Automated the deployment process"
- After: "Automated CI/CD pipeline, reducing deployment time from 4 hours to 12 minutes and enabling 15 deployments/day (up from 2/week)"

**Engineering:**
- Before: "Improved the testing process"
- After: "Built automated test suite covering 85% of codebase, reducing QA cycle from 3 days to 4 hours per release"

**Operations:**
- Before: "Streamlined the onboarding process"
- After: "Redesigned employee onboarding workflow, reducing time-to-productivity from 6 weeks to 2 weeks and eliminating 12 manual handoff steps"

**Finance:**
- Before: "Improved the monthly close process"
- After: "Automated 70% of month-end reconciliation tasks, reducing close cycle from 15 business days to 5"

### Prompts for Candidates

When a bullet lacks efficiency metrics, ask:
- "How long did this take before vs. after your improvement?"
- "How many hours per week/month does this save?"
- "What was the old process and how much faster is the new one?"
- "How many manual steps were eliminated?"

---

## Metric Type 4: Quality

Quality metrics demonstrate improvements in reliability, accuracy, satisfaction, or defect reduction.

### When to Suggest

Suggest quality metrics when the bullet describes:
- Improving system reliability or uptime
- Reducing bugs, errors, or defects
- Increasing customer satisfaction or NPS scores
- Improving accuracy of predictions, reports, or processes
- Implementing quality assurance practices
- Reducing incident frequency or severity

### Metric Formats

| Format | Example | Best For |
|--------|---------|----------|
| Uptime/availability | 99.99% uptime | System reliability |
| Error/defect reduction | Reduced bugs by 40% | Code quality |
| Satisfaction score | NPS improved from 32 to 67 | Customer impact |
| Accuracy rate | 98.5% prediction accuracy | Model/process precision |
| Incident reduction | Reduced P1 incidents by 75% | Operational stability |
| Test coverage | Increased coverage from 45% to 92% | Code quality practices |
| Compliance rate | 100% audit pass rate | Regulatory adherence |

### Examples by Role

**Engineering:**
- Before: "Improved system reliability"
- After: "Improved system reliability from 99.5% to 99.99% uptime (reducing downtime from 43 hours/year to 52 minutes/year)"

**QA:**
- Before: "Improved testing practices"
- After: "Increased automated test coverage from 30% to 85%, reducing production defects by 65% and customer-reported bugs by 40%"

**Customer Service:**
- Before: "Improved customer satisfaction"
- After: "Raised customer satisfaction score from 3.2 to 4.6 (out of 5) by implementing a tiered support model and reducing average resolution time to under 2 hours"

**Data Science:**
- Before: "Built a machine learning model for fraud detection"
- After: "Built ML fraud detection model achieving 98.5% precision and 94% recall, reducing false positives by 60% and catching $2.3M in fraudulent transactions quarterly"

### Prompts for Candidates

When a bullet lacks quality metrics, ask:
- "What was the uptime or reliability before and after?"
- "By how much did errors or defects decrease?"
- "What was the customer satisfaction score improvement?"
- "What accuracy or precision did the system achieve?"

---

## Quantification Audit Methodology

When auditing a resume for quantification gaps, follow this process:

### Step 1: Identify High-Impact Bullets

Focus quantification suggestions on bullets that:
- Describe leadership or team management (always quantify team size)
- Describe project outcomes (always quantify timeline and results)
- Describe process improvements (always quantify before/after)
- Describe revenue or cost impacts (always quantify dollar amounts)

### Step 2: Categorize the Appropriate Metric Type

For each unquantified high-impact bullet:
1. Read the action described
2. Determine which metric type (Financial, Scale, Efficiency, Quality) is most natural
3. Some bullets may benefit from multiple metric types

### Step 3: Suggest Specific Metrics

For each gap identified:
- Name the metric type
- Provide a rewritten example with `[X]` placeholders where the candidate needs to fill in actual numbers
- Explain why this metric type strengthens the bullet

### Step 4: Prioritize Suggestions

Rank quantification suggestions by impact:
1. **Critical** -- Leadership bullets without team size, project bullets without outcomes
2. **High** -- Process improvements without before/after, technical work without scale
3. **Medium** -- Supporting bullets that could be enhanced with numbers
4. **Low** -- Routine tasks where quantification adds modest value

---

## Common Quantification Mistakes to Avoid

| Mistake | Why It's Bad | Better Approach |
|---------|-------------|-----------------|
| Fabricating numbers | Dishonest and can be caught in interviews | Use brackets: "Reduced costs by [X]%" |
| Overly precise numbers | "Improved efficiency by 23.7%" feels made up | Round to clean numbers: "~25% improvement" |
| Numbers without context | "$500K" means nothing without reference frame | Add context: "$500K (15% of annual budget)" |
| Too many numbers in one bullet | Overwhelming and hard to parse | Lead with the most impressive metric, mention 1-2 supporting ones |
| Percentage without base | "200% increase" could mean going from 1 to 3 | Include the base or absolute numbers where possible |
