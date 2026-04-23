---
name: job-search-strategy
description: "Strategic playbook for the job-search-agent — teaches how to search job boards effectively, formulate queries, iterate on results, and avoid common pitfalls."
---

# Job Search Strategy Playbook

You are executing a structured job search. Follow this playbook in order. Do not skip phases or reorder them.

---

## Phase 1 — Profile Extraction (Before You Search)

Before opening any job board, read the CV from `Rotem Solomon CV.md` (in the repo root) and extract:

| Signal | Where to find it | Why it matters |
|--------|-----------------|----------------|
| Core job titles | CV headline, most recent roles | Drives primary search terms |
| Tech stack | Skills section, project bullets | Keyword filters |
| Seniority level | Years of experience, titles held | Prevents mismatched results |
| Location constraints | User request | Filters geographically |
| Must-haves / deal-breakers | User request or memory | Eliminates waste upfront |

If running interactively and anything is ambiguous, ask before searching. In automated mode, proceed with the profile from the CV and memory — do not pause.

---

## Phase 2 — Query Construction

### Target Job Titles for Rotem Solomon

There are **3 fixed groups**. Fetch all 3 every session — **1 WebFetch per group** on LinkedIn's own search UI.

**Group 1 — AI/ML (core):**
- Algorithm Engineer / Algorithm Developer
- Machine Learning Engineer / ML Engineer
- AI Engineer / AI/ML Engineer
- Research Engineer / Deep Learning Engineer
- Data Scientist

**Group 2 — Signal Processing & Biomedical:**
- Biomedical Algorithm Engineer
- Signal Processing Engineer
- Medical AI Engineer / Healthcare AI Engineer
- Medical Imaging Engineer

**Group 3 — LLM / Agents:**
- LLM Engineer / AI Agent Developer / GenAI Engineer

### Query Strategy
Use title-only (broad) queries. Do not add skill keywords; filtering by skill happens in Phase 7 scoring after reading the JD.

---

## Phase 3 — Search LinkedIn

**Use LinkedIn's own job search UI via WebFetch** — this applies LinkedIn's own "Past month" date filter, giving genuinely fresh results instead of Google's stale index.

For each of the 3 groups, WebFetch the following URL (replace the `keywords` value per group):

**Group 1:**
```
https://www.linkedin.com/jobs/search/?keywords=%22algorithm+engineer%22+OR+%22machine+learning+engineer%22+OR+%22AI+engineer%22+OR+%22deep+learning+engineer%22+OR+%22data+scientist%22&location=Israel&f_TPR=r2592000
```

**Group 2:**
```
https://www.linkedin.com/jobs/search/?keywords=%22signal+processing+engineer%22+OR+%22biomedical+algorithm%22+OR+%22medical+AI+engineer%22+OR+%22medical+imaging+engineer%22&location=Israel&f_TPR=r2592000
```

**Group 3:**
```
https://www.linkedin.com/jobs/search/?keywords=%22LLM+engineer%22+OR+%22AI+agent+developer%22+OR+%22generative+AI+engineer%22+OR+%22GenAI+engineer%22&location=Israel&f_TPR=r2592000
```

(`f_TPR=r2592000` = Past 30 days. `location=Israel` applies LinkedIn's location filter.)

- From each WebFetch response, extract: job title, company, location, posting date, and `linkedin.com/jobs/view/...` URL.
- Do **not** fetch company career pages.
- Do **not** try other platforms at this stage.
- **Hard limit: 1 WebFetch per group = 3 WebFetch calls total in this phase.**
- **If a LinkedIn WebFetch returns a login wall or no job listings** (LinkedIn may block unauthenticated access), note the failure and fall back to WebSearch for that group: `"<titles>" Israel site:linkedin.com/jobs/view 2026`. A WebSearch fallback counts toward the Phase 5 budget.

---

## Phase 4 — Freshness & Deduplication

1. **Freshness:** default window is last 30 days. Flag anything older.
2. **Same-session dedup:** if the same role appears in multiple search results, keep it once.
3. **Cross-session dedup (MANDATORY):**
   - Read `job-results/seen-jobs.md` — the cumulative list of all previously shown jobs.
   - Each entry is in format `Job Title | Company` or `Job Title | Company | YYYY-MM-DD`.
   - **Ignore entries older than 60 days** (entries with a date more than 60 days ago are treated as fresh — they may be re-shown). Entries with no date are always treated as seen.
   - Discard any job that matches a non-expired entry on company name + job title (case-insensitive).
   - Do not include, score, or show any non-expired previously seen job.
4. **Expired postings:** if a listing is marked closed or 404s, discard it.

---

## Phase 5 — Iteration (if results are thin)

**This phase MUST complete before Phase 6 begins. Never start fetching individual JDs until all searching and deduplication is fully done.**

Check: how many new (non-deduped) jobs survived Phase 4?

- **5 or more:** proceed to Phase 6.
- **Fewer than 5 and LinkedIn WebFetch worked:** repeat all 3 LinkedIn WebFetch calls with a 60-day window (`f_TPR=r5184000` instead of `r2592000`). Apply Phase 4 dedup, merge survivors. Proceed to Phase 6.
- **Fewer than 5 and LinkedIn WebFetch was blocked for all groups:** fall back to WebSearch for all 3 groups using `site:linkedin.com/jobs/view`: one WebSearch per group, same title variants, add `2026` for freshness bias. Apply Phase 4 dedup, merge survivors. Proceed to Phase 6.
- Do not run more searches after the iteration step regardless of final count.
- **Never return to Phase 5 after Phase 6 has started.** If results are still thin after Phase 6 begins, proceed anyway — do not go back and search more.

---

## Phase 6 — JD Fetch (targeted WebFetch only)

**HARD LIMIT: Exactly 10 WebFetch calls in this entire phase. Count every fetch. Stop immediately when you reach 10, even if more jobs remain.**

1. **Snippet-rank the survivors** from Phase 4 without fetching anything. Score each job 1–3 on the LinkedIn snippet alone using these signals:
   - Title closely matches Rotem's target titles → +1
   - Snippet mentions junior / entry-level / fresh graduate → +1
   - Location is Tel Aviv center → +1 (Haifa or periphery → -1)

2. **WebFetch the top 10 only** by snippet score, using their direct `linkedin.com/jobs/view/...` URLs. Fetch them one-by-one and track your count: after fetch #10, move to Phase 7 — no exceptions.

3. **All other jobs** (ranked below top 10, or beyond the 10-fetch limit) are not fetched. They proceed to Phase 7 with snippet only and are capped at ⭐⭐.

4. **Rules:**
   - **Never use WebSearch to look up a company or job** — queries like `"company name" "job title" requirements` are forbidden.
   - If a URL 404s or returns no content, skip it — it still counts toward the 10-fetch limit.
   - **Do not fetch more than 10 JDs total across Phase 6, including any retries or replacements.**

---

## Phase 7 — Filtering & Scoring

Apply to all surviving jobs (using full JD where fetched, snippet otherwise):

1. **Hard eliminators** (remove immediately):
   - Requires 3+ years industry experience with no junior track
   - Wrong location with no remote option

2. **Soft filters** (flag, don't remove):
   - Missing 1–2 preferred skills → keep, note as gap
   - Slightly off industry → keep if transferable

3. **Scoring:**

   Split JD requirements into must-haves and nice-to-haves. Count how many must-haves are genuinely present in the CV.

   | Rating | Rule |
   |--------|------|
   | ⭐⭐⭐ Strong Match | ≥80% of must-haves covered AND ≤1 must-have absent AND full JD read |
   | ⭐⭐ Good Match | 60–79% of must-haves covered OR exactly 2 must-haves absent OR JD only partially read |
   | ⭐ Potential Match | 40–59% of must-haves covered OR 3+ must-haves absent |

   **Hard cap rules:**
   - 3+ explicit must-have tools/skills absent → cap at ⭐ regardless of keyword overlap
   - JD requires a specific domain the CV has no experience in → cap at ⭐⭐ max
   - Full JD not read → cap at ⭐⭐ max

**Target output:** 4–8 results. If under 4, include what was found, note the shortage in the summary, and suggest expanding the search scope for the next session.

---

## Phase 8 — Output Assembly

For each job:
```
### [Job Title] at [Company]
- **Match**: ⭐⭐⭐ / ⭐⭐ / ⭐
- **JD Source**: [Full JD read | LinkedIn snippet only]
- **Location**: [City | Remote | Hybrid]
- **Seniority**: [Level]
- **Posted**: [date or "~X days ago"]
- **Link**: [URL]
- **Key Requirements**: [3–5 bullets from the JD]
- **Why It Matches**: [1–2 sentences tied to CV]
- **Gaps**: [specific missing skills, or "None identified"]
```

End with a **Search Summary** using `####` (not `###`) for all subsection headers inside it:
```
## Search Summary

#### Queries Used
...

#### Counts
...

#### Filter-Out Reasons
...

#### Suggested Adjustments for Next Session
...
```

**Important:** Use `####` for Search Summary subsections. Only actual job entries use `###`. This keeps the email quick-apply list clean.

---

## Phase 9 — Save Results

### Step 1 — Markdown session log
Save the full output to `job-results/YYYY-MM-DD_search.md`.

### Step 2 — Update seen-jobs
Append all new jobs shown today to `job-results/seen-jobs.md` in format `[Job Title] | [Company] | YYYY-MM-DD` (one per line, using today's date).

### Step 3 — Excel tracker
```bash
python "job-results/excel_helper.py" '<json>'
```

JSON array with fields: `title`, `company`, `location`, `match` (`strong`/`good`/`potential`), `url`.

---

## Rules (Non-Negotiable)

- **You are the job-search-agent. Execute all work directly — never spawn another agent or sub-agent.**
- Never fabricate a job posting or URL
- Never include a posting you haven't verified exists at the link
- Never skip Phase 1 — ambiguous profiles produce useless results
- Always note your search queries used, so the user can replicate or refine them
- **Never use WebSearch to look up an individual company or job.** Broad LinkedIn searches only. JD details come from WebFetch on direct LinkedIn URLs — nothing else.
- **Never WebFetch before Phase 4 dedup is complete.** Fetch JDs only for jobs that survived the seen-jobs filter.
- **Never WebFetch a LinkedIn category or listing page** (e.g. `il.linkedin.com/jobs/algorithm-engineer-jobs`). Only `linkedin.com/jobs/view/...` URLs are permitted. The WebSearch snippets already contain the direct job URLs — use those.
