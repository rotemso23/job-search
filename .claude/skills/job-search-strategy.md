---
name: job-search-strategy
description: "Strategic playbook for the job-search-agent — teaches how to search job boards effectively, formulate queries, iterate on results, and avoid common pitfalls."
---

# Job Search Strategy Playbook

You are executing a structured job search. Follow this playbook in order. Do not skip phases or reorder them.

---

## Automated Mode Rules

When running as part of the automated pipeline (triggered by `run-job-search.ps1`, not by a live user), **never block or wait for input.** These rules override **every** "ask the user", "stop", and "stop and ask" instruction anywhere in this playbook. If something is ambiguous, make a reasonable assumption and proceed. Flagging issues in the output file (warnings, notes) is always allowed and encouraged.

---

## Phase 1 — Profile Extraction (Before You Search)

Before opening any job board:

1. **Read `config.ini`** from the repo root. Extract:
   - `[user] cv_file` — the CV filename
   - `[search] location` — the target location for LinkedIn searches
   - `[search] seniority` — the user's seniority level (e.g. junior, mid, senior)
   - `[search] job_titles` — the list of target job titles (one per line)

2. **Read the CV** (filename from step 1) and extract:

| Signal | Where to find it | Why it matters |
|--------|-----------------|----------------|
| Tech stack | Skills section, project bullets | Keyword filters |
| Seniority level | Years of experience, titles held | Prevents mismatched results |
| Must-haves / deal-breakers | User request or memory | Eliminates waste upfront |

The `job_titles`, `location`, and `seniority` from `config.ini` take precedence — do not infer them from the CV.

If running interactively and anything is ambiguous, ask before searching. In automated mode, proceed with the profile from config.ini and the CV — do not pause.

---

## Phase 2 — Query Construction

### Target Job Titles

Take the `job_titles` list from `config.ini` and split it into groups of **up to 5 titles each**. Each group becomes one LinkedIn WebFetch call.

Example: 13 titles → 3 groups (5 + 5 + 3).

### Query Strategy
Use title-only (broad) queries. Do not add skill keywords; filtering by skill happens in Phase 7 scoring after reading the JD.

---

## Phase 3 — Search LinkedIn

**Use LinkedIn's own job search UI via WebFetch** — this applies LinkedIn's own "Past month" date filter, giving genuinely fresh results instead of Google's stale index.

For each group of titles (from Phase 2), construct and WebFetch a LinkedIn URL using this template:

```
https://www.linkedin.com/jobs/search/?keywords=KEYWORDS&location=LOCATION&f_TPR=r2592000
```

Where:
- `LOCATION` = the `location` value from `config.ini`, URL-encoded (spaces → `+`)
- `KEYWORDS` = each title in the group, quoted and joined with `+OR+`, URL-encoded (spaces → `+`, `"` → `%22`)

Example for titles ["ML Engineer", "AI Engineer"] with location "Tel Aviv, Israel":
```
https://www.linkedin.com/jobs/search/?keywords=%22ML+engineer%22+OR+%22AI+engineer%22&location=Tel+Aviv%2C+Israel&f_TPR=r2592000
```

(`f_TPR=r2592000` = Past 30 days. `location` applies LinkedIn's location filter.)

- From each WebFetch response, extract: job title, company, location, posting date, and `linkedin.com/jobs/view/...` URL.
- Do **not** fetch company career pages.
- Do **not** try other platforms at this stage.
- **Hard limit: 1 WebFetch per group.**
- **If a LinkedIn WebFetch returns a login wall or no job listings** (LinkedIn may block unauthenticated access), note the failure and fall back to WebSearch for that group: `"<titles>" <location> site:linkedin.com/jobs/view [current year]` (use the `location` from `config.ini`). A WebSearch fallback counts toward the Phase 5 budget.

---

## Phase 4 — Freshness & Deduplication

1. **Freshness:** default window is last 30 days. Flag anything older.
2. **Same-session dedup:** if the same role appears in multiple search results, keep it once.
3. **Cross-session dedup (MANDATORY):**
   - Read `job-results/seen-jobs.md` — the cumulative list of all previously shown jobs. If the file does not exist yet (first run), treat it as empty and skip deduplication.
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
- **Fewer than 5 and LinkedIn WebFetch worked:** repeat all LinkedIn WebFetch calls (one per group) with a 60-day window (`f_TPR=r5184000` instead of `r2592000`). Apply Phase 4 dedup, merge survivors. Proceed to Phase 6.
- **Fewer than 5 and LinkedIn WebFetch was blocked for all groups:** fall back to WebSearch for all groups using `site:linkedin.com/jobs/view`: one WebSearch per group, same title variants, add the current year for freshness bias. Apply Phase 4 dedup, merge survivors. Proceed to Phase 6.
- Do not run more searches after the iteration step regardless of final count.
- **Never return to Phase 5 after Phase 6 has started.** If results are still thin after Phase 6 begins, proceed anyway — do not go back and search more.

---

## Phase 6 — JD Fetch (targeted WebFetch only)

**HARD LIMIT: Exactly 10 WebFetch calls in this entire phase. Count every fetch. Stop immediately when you reach 10, even if more jobs remain.**

1. **Snippet-rank the survivors** from Phase 4 without fetching anything. Score each job 1–3 on the LinkedIn snippet alone using these signals:
   - Title closely matches your target titles → +1
   - Snippet mentions seniority level that matches `seniority` from `config.ini` → +1
   - Location matches the user's preferred location (from `config.ini` `location`) → +1 (far periphery or mismatched city → -1)

2. **WebFetch the top 10 only** by snippet score, using their direct `linkedin.com/jobs/view/...` URLs. Fetch them one-by-one and track your count: after fetch #10, move to Phase 7 — no exceptions.

3. **All other jobs** (ranked below top 10, or beyond the 10-fetch limit) are not fetched. They proceed to Phase 7 with snippet only and are capped at ⭐⭐.

4. **Rules:**
   - **Never use WebSearch to look up a company or job** — queries like `"company name" "job title" requirements` are forbidden.
   - If a URL 404s, returns no content, returns an error, or times out — skip it immediately and move to the next URL. Do not retry. It still counts toward the 10-fetch limit.
   - **Do not fetch more than 10 JDs total across Phase 6, including any retries or replacements.**

---

## Phase 7 — Filtering & Scoring

Apply to all surviving jobs (using full JD where fetched, snippet otherwise):

1. **Hard eliminators** (remove immediately):
   - Experience requirement clearly exceeds the user's seniority level (from `config.ini`) with no junior/entry track mentioned
   - Location does not match `config.ini` `location` and no remote option offered

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
Append all new jobs shown today to `job-results/seen-jobs.md` in format `[Job Title] | [Company] | YYYY-MM-DD` (one per line, using today's date). Create the `job-results/` directory and the file if they do not exist yet.

### Step 3 — Excel tracker
```bash
python "excel_helper.py" '<json>'
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
