---
name: jd-analyzer-strategy
description: "Teaches the jd-analyzer how to ingest a job posting — from URL or pasted text — extract clean JD content, separate must-haves from nice-to-haves, detect hidden priorities, identify the technical stack, and extract ATS keywords."
---

# Job Description Reading Playbook

Before analyzing any JD, you must first obtain clean, complete job description text. Follow this playbook.

---

## Phase 1 — Identify Input Type

The user will provide one of:

| Input type | What to do |
|------------|-----------|
| Job number reference (e.g. "job #3", "job number 5") | Look up the job in the most recent results file — see Phase 1a |
| URL only | Fetch and extract — see Phase 2 |
| Pasted text | Skip to Phase 3 (clean it) |
| URL + pasted text | Use pasted text as primary; fetch URL only to fill gaps |
| Neither | Ask: "Please share the job posting — paste the text or give me the URL." |

### Phase 1a — Resolving a job number reference

1. List files in `job-results/` and identify the most recent `YYYY-MM-DD_search.md` file (sort by date descending).
2. Read that file and find the job entry matching the requested number (jobs are numbered sequentially in the results file).
3. Extract the job's **URL** and any **pasted/cached description** from the results entry.
4. If a URL is present, proceed to Phase 2 to fetch the full JD.
5. If the results file contains the full JD text already, use it directly and skip to Phase 3.
6. If the job number doesn't exist in the file, tell the user and ask them to provide the URL or paste the JD.

---

## Phase 2 — Fetching from a URL

Use `WebFetch` to retrieve the page. Then apply the platform-specific extraction rules below.

### Platform extraction rules

**LinkedIn** (`linkedin.com/jobs/view/...`)
- The full JD is in the "About the job" section.
- If the page shows a login wall or truncated text ("…show more"), the fetch will be partial. In that case: extract what's available and note `[TRUNCATED — login required for full text]`. Ask the user to paste the full description.
- Ignore: "Easy Apply" button, sidebar company stats, "People also viewed" section.

**Indeed** (`indeed.com/viewjob` or `indeed.com/jobs/...`)
- JD content is in `#jobDescriptionText` or the main article block.
- Sponsored/promoted labels at the top are noise — discard them.
- If redirected to the company's own site, treat it as a direct company page (see below).

**Glassdoor** (`glassdoor.com/job-listing/...`)
- JD is behind a soft login wall. Fetch will often return only a snippet.
- Extract what's available; flag as `[PARTIAL — Glassdoor login wall]` and ask user to paste.

**Wellfound / AngelList** (`wellfound.com/jobs/...`)
- Usually fully accessible. Extract the role description and compensation/equity fields if present — they are useful context for analysis.

**Company career pages (direct)**
- Content is usually fully accessible.
- Isolate the job description block — discard: nav menus, footer, cookie banners, "Apply now" CTAs, unrelated job listings, company boilerplate ("We are a fast-growing...") that appears before or after the actual role requirements.

**Dice / Stack Overflow / other boards**
- Extract the job description section. Discard recruiter contact info, site navigation, and ads.

### Fetch failure handling

| Failure | Action |
|---------|--------|
| 403 / login wall | Note it, ask user to paste the JD text |
| 404 / expired | Tell the user: "This posting appears to be expired or removed." Do not proceed. |
| JS-rendered (blank page) | Tell the user the page requires JavaScript and ask them to paste the text |
| Timeout | Retry once; if it fails again, ask user to paste |

---

## Phase 3 — Cleaning Raw Text

Once you have raw text (fetched or pasted), clean it before analysis:

1. **Strip noise** — remove: "Apply Now", "Save job", cookie notices, navigation links, "Share this job", recruiter signatures, social media links, legal boilerplate unrelated to the role.

2. **Preserve structure** — keep: section headers (Requirements, Responsibilities, Nice to Have, About the Role, etc.), bullet points, any mentioned tools/technologies, compensation/benefits info.

3. **Detect truncation** — if the text ends mid-sentence, mid-list, or with "..." **stop immediately**:
   > ⚠️ **JD appears truncated.** Please paste the full job description before I continue — I will not analyze a partial JD.

4. **Detect boilerplate-only posts** — if the posting contains no specific requirements (only generic phrases like "strong communication skills", "team player", "competitive salary") flag it:
   > ⚠️ **Low-signal JD.** This posting is mostly boilerplate with few specific requirements. Analysis will have limited precision.

---

## Phase 4 — Pre-Analysis Checklist

Before handing the cleaned text to the analysis framework, confirm:

- [ ] JD contains at least one identifiable job title
- [ ] JD contains at least a responsibilities or requirements section
- [ ] Text is not from a different job than the one requested (check title + company match if URL was provided)
- [ ] No obvious truncation or critical missing section

If any check fails, flag it to the user before proceeding with analysis.

---

## Phase 5 — Must-Have vs. Nice-to-Have Separation

The single most important classification step. Misclassifying a must-have as optional causes resume mismatches.

### Signal hierarchy (strongest → weakest)

| Signal | Classification |
|--------|---------------|
| "Required", "Must have", "You must", listed under "Minimum Qualifications" | **Must-have** |
| Minimum years threshold ("5+ years of X") | **Must-have** |
| Listed first in a requirements section | Likely **must-have** |
| "Preferred", "Nice to have", "Bonus", "A plus", "Ideally", "Desired" | **Nice-to-have** |
| Listed under "Additional Qualifications" or a second requirements block | **Nice-to-have** |
| Mentioned once in passing in the responsibilities section | **Nice-to-have** |
| Mentioned 2+ times across sections | Escalate to **must-have** regardless of label |

### When it's ambiguous

- If a skill appears in both sections, classify as **must-have** and note the conflict.
- If the entire JD has no section headers at all, use frequency: skills mentioned 2+ times → must-have, once → nice-to-have.
- Always note your reasoning when the call is close.

---

## Phase 6 — Hidden Priority Detection

Employers often bury their real priorities. Surface them with these signals:

**Frequency count** — tally every mention of each skill/topic across the entire JD (title, summary, responsibilities, requirements, about us). Skills mentioned 3+ times are top priorities regardless of where they appear.

**Positioning** — the first 3 bullets in any list carry more weight than later items. The first requirement listed is usually the most critical.

**Verb intensity** — grade the language:
- "Expert in", "deep knowledge of", "mastery of" → senior/critical requirement
- "Proficient in", "experience with", "strong background in" → standard requirement
- "Familiar with", "exposure to", "understanding of" → junior/optional signal

**Title vs. responsibilities mismatch** — flag explicitly if:
- Title says "Junior" but responsibilities list system design or team leadership
- Title says "Senior" but duties are mostly execution with no ownership
- Role has a generic title ("Engineer") but requirements are highly specialized

**Implicit culture signals** — extract from language patterns:
- "Move fast", "wear many hats", "startup environment" → high ambiguity, broad scope expected
- "Cross-functional alignment", "stakeholder management" → heavy meeting/politics load
- "Own the roadmap", "build from scratch" → high autonomy, likely under-resourced
- "Support the team", "work closely with" → supporting role, not leading

Summarize top 3–5 hidden priorities as plain-language findings.

---

## Phase 7 — Technical Stack Identification

Extract and categorize every technology mentioned — explicit or implied:

| Category | Examples to look for |
|----------|---------------------|
| **Languages** | Python, Java, TypeScript, Go, SQL, Bash… |
| **Frameworks & libraries** | React, FastAPI, Spring Boot, dbt, Airflow… |
| **Data & databases** | PostgreSQL, Snowflake, BigQuery, Redis, Kafka… |
| **Cloud & infra** | AWS, GCP, Azure, Kubernetes, Terraform, Docker… |
| **Tools & platforms** | Jira, GitHub, Databricks, Salesforce, Tableau… |
| **Methodologies** | Agile, Scrum, CI/CD, TDD, REST, microservices… |

For each technology:
- Mark **[M]** if must-have, **[N]** if nice-to-have (using Phase 5 rules)
- Note version or depth qualifier if mentioned (e.g., "Python 3", "5+ years AWS")
- Flag technologies that appear only in the "About Us" section — these describe the company stack, not necessarily what the role needs day-to-day

---

## Phase 8 — ATS Keyword Extraction

ATS systems match resumes against JD text using exact or near-exact string matching. Extract keywords in these priority tiers:

**Tier 1 — Exact match critical** (must appear verbatim in resume):
- Job title and close variants used in the JD
- Technologies marked must-have [M]
- Certifications or credentials named explicitly (e.g., "AWS Certified", "PMP", "CPA")
- Any phrase in quotes in the JD (e.g., "machine learning", "data pipeline")

**Tier 2 — High value** (strong signal, include if applicable):
- All technologies marked nice-to-have [N]
- Methodology/process terms (Agile, CI/CD, REST API)
- Industry-specific jargon used repeatedly
- Action verbs from responsibilities ("architect", "optimize", "lead", "scale")

**Tier 3 — Supporting context** (use to round out resume language):
- Soft skill phrases used verbatim ("cross-functional collaboration", "stakeholder communication")
- Domain terms ("B2B SaaS", "fintech", "healthcare data")
- Team/org terms ("distributed team", "fast-paced environment")

**Output format for keywords:**
```
Tier 1 (exact match): `term` `term` `term`
Tier 2 (high value):  `term` `term` `term`
Tier 3 (context):     `term` `term` `term`
```

**Rules:**
- Extract the exact string as it appears in the JD — do not paraphrase
- If the JD uses both "ML" and "machine learning", list both
- Do not include terms that appear only in boilerplate company descriptions (unless also in requirements)

---

## Phase 9 — Save Analysis Results

After completing Phases 5–8, save the full analysis to a file:

1. **Create a company folder** (if it doesn't already exist):
   `C:\Users\משתמש\Desktop\job search\CV\[Company Name]\`
   Use the exact company name from the JD. If unknown, use the job title.

2. **Save the analysis as:**
   `C:\Users\משתמש\Desktop\job search\CV\[Company Name]\jd-analysis.md`

3. **File format:**
```markdown
# JD Analysis — [Company Name] / [Job Title]

**Source:** [URL or "user-provided text"]

## Must-Have Requirements
- [requirement] [M]

## Nice-to-Have Requirements
- [requirement] [N]

## Hidden Priorities
1. [finding]
2. [finding]

## Technical Stack
| Technology | Category | Must/Nice |
|------------|----------|-----------|
| [tech] | [category] | [M/N] |

## ATS Keywords
Tier 1 (exact match): `term` `term`
Tier 2 (high value):  `term` `term`
Tier 3 (context):     `term` `term`
```

4. **Confirm to the user:**
   > Analysis saved to `CV\[Company Name]\jd-analysis.md`

---

## Rules

- Never analyze a blank, near-blank, or truncated JD — stop and ask the user to paste the full text before proceeding
- Never guess at missing requirements — only extract what's explicitly present
- If the URL and pasted text conflict (e.g., different roles), ask the user which is correct
- Always note the source of the JD text in your output (URL fetched / user-provided text / partial fetch)
- Complete Phases 5–8 for every JD — do not skip even if the JD seems simple
