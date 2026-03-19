---
name: job-search-strategy
description: "Strategic playbook for the job-search-agent — teaches how to search job boards effectively, formulate queries, iterate on results, and avoid common pitfalls."
---

# Job Search Strategy Playbook

You are executing a structured job search. Follow this playbook to maximize result quality and coverage.

---

## Phase 1 — Profile Extraction (Before You Search)

Before opening any job board, read the CV from `Rotem Solomon CV.md` (in the repo root) and extract from it and the user's request:

| Signal | Where to find it | Why it matters |
|--------|-----------------|----------------|
| Core job titles | CV headline, most recent roles | Drives primary search terms |
| Tech stack | Skills section, project bullets | Keyword filters |
| Seniority level | Years of experience, titles held | Prevents mismatched results |
| Location constraints | User request | Filters geographically |
| Must-haves / deal-breakers | User request or memory | Eliminates waste upfront |

If **any** of these are missing or ambiguous, **ask before searching**.

---

## Phase 2 — Query Construction

### Title Variants
Never search a single title. Generate 3–5 equivalent titles:
- Example: "Data Engineer" → also search "Analytics Engineer", "ETL Developer", "Data Platform Engineer", "Big Data Engineer"
- Use the user's exact title from CV as one variant — it likely appears in JDs verbatim

### Boolean Operators (use when the platform supports them)
```
"data engineer" AND (Python OR Spark) NOT intern
"product manager" AND ("B2B" OR "SaaS") AND remote
```

### Keyword Layering Strategy
- **Layer 1 (broad):** title only → captures volume
- **Layer 2 (medium):** title + primary skill → improves precision
- **Layer 3 (narrow):** title + primary skill + secondary skill → highest precision, lowest volume

Run at least Layer 1 and Layer 2. Use Layer 3 only if Layer 2 returns 50+ results.

---

## Phase 3 — Platform Coverage

Search platforms in this priority order:

| Priority | Platform | Best for |
|----------|----------|---------|
| 1 | LinkedIn Jobs | Broadest corporate coverage; supports Boolean |
| 2 | Indeed | High volume, good for SMBs; use `"exact phrase"` |
| 3 | Glassdoor | Adds salary data context |
| 4 | Wellfound (AngelList) | Startups, early-stage companies |
| 5 | company career pages | Roles not posted on aggregators |
| 6 | Stack Overflow Jobs / Dice | Developer-specific roles |

**Minimum coverage:** hit at least 2 platforms per search session. Never rely on one source alone.

### Platform-Specific Tips
- **LinkedIn:** Use "Date posted: Past month" filter. Filter by "Easy Apply" only if volume is low.
- **Indeed:** Append `posted:14` to URL or use "Date posted" filter. Avoid "Sponsored" spam at top.
- **Wellfound:** Filter by "Job type: Full-time" and funding stage if relevant.
- **Company pages:** Check companies from user's target list or industry leaders first.

---

## Phase 4 — Freshness & Deduplication

- **Default window:** last 30 days. Flag anything older if included.
- **Deduplication rule:** if the same role appears on 2+ platforms, list it once (prefer LinkedIn link if available, else the source with most detail).
- **Cross-session deduplication (MANDATORY — do this before scoring):**
  1. Read **every** file in `job-results/` using the Read tool.
  2. Build a seen-jobs list: extract every `### [Job Title] at [Company]` heading from those files.
  3. For each candidate job you found today, check it against the seen-jobs list. Match on company name + job title (case-insensitive, ignore minor wording differences like "—" vs "-" or word order shifts).
  4. **Discard any match.** Do not include it in results, scoring, or the email. Do not show the user a job they have already been shown.
  5. If discarding a job leaves you with fewer than 5 results, run an additional search pass before finalizing.
- **Expired postings:** if a link 404s or shows "no longer accepting applications", discard it — never include it.

---

## Phase 4.5 — Deep JD Fetch (Before Scoring)

LinkedIn blocks unauthenticated access — search results only return short snippets, not the full JD. Before scoring any job, attempt to get the full job description:

**For each candidate job found via search:**
1. Try `WebFetch` on the LinkedIn URL — if it returns content (some public listings work), use it.
2. If LinkedIn blocks: search `"[Job Title] [Company] site:[company].com careers"` to find the same role on the company's career page.
3. Try `WebFetch` on the company career page URL.
4. If both fail: try other job boards — search `"[Job Title] [Company] site:glassdoor.com OR site:comeet.com OR site:greenhouse.io OR site:lever.co"`.

**Scoring rule:** Only score a job ⭐⭐⭐ if you successfully fetched real JD content. If you only have a search snippet, cap the score at ⭐⭐ and note "JD not fully read" in the output.

**Efficiency:** Do this for the top 15–20 candidates. Skip deep fetch for roles already eliminated by hard filters.

---

## Phase 5 — Filtering & Scoring

Apply filters in this order to avoid discarding too early:

1. **Hard eliminators** (remove immediately):
   - Wrong seniority (e.g., intern/junior when user is senior)
   - Wrong location with no remote option
   - Requires visa sponsorship the user can't fulfill


2. **Soft filters** (flag, don't remove):
   - Missing 1–2 preferred skills → keep, note as gap
   - Slightly off industry → keep if transferable

3. **Scoring** (based on actual JD content from Phase 4.5):

   Before scoring, split the JD requirements into two lists:
   - **Must-haves:** anything the JD marks as required, mandatory, or lists without qualification
   - **Nice-to-haves:** anything marked as "advantage", "bonus", "preferred", or "plus"

   Count how many must-haves are genuinely present in the CV (not inferred, not adjacent — actually present).

   | Rating | Rule |
   |--------|------|
   | ⭐⭐⭐ Strong Match | ≥80% of must-haves covered AND ≤1 must-have tool/skill absent AND full JD read |
   | ⭐⭐ Good Match | 60–79% of must-haves covered OR exactly 2 must-have tools absent OR JD only partially read |
   | ⭐ Potential Match | 40–59% of must-haves covered OR 3+ must-have tools absent |

   **Hard cap rules (cannot be overridden by keyword overlap):**
   - If 3 or more explicit must-have tools or domain skills are absent from the CV → cap at ⭐ regardless of overall keyword match
   - If the JD requires a specific domain (e.g. NLP, computer vision, embedded) and the CV has no project or work experience in that domain → cap at ⭐⭐ maximum
   - If the full JD was not read → cap at ⭐⭐ maximum

**Target output:** 10–20 results. If under 10, widen the query.

---

## Phase 6 — Iteration Rules

If initial results are poor:

| Problem | Fix |
|---------|-----|
| Too few results | Broaden title variants, drop secondary keyword layer, extend date window to 60 days |
| Too many irrelevant | Add a must-have keyword, narrow to specific industry |
| Duplicates dominate | Switch to a new platform or company career pages |
| All roles too senior/junior | Adjust seniority filter; try "mid-level" vs. "senior" keyword swap |

Never return fewer than 5 results without explaining why and asking the user to loosen constraints.

---

## Phase 7 — Output Assembly

For each job include:
```
### [Job Title] at [Company]
- **Match**: ⭐⭐⭐ / ⭐⭐ / ⭐
- **JD Source**: [LinkedIn snippet only | Company career page | Glassdoor/other board]
- **Location**: [City | Remote | Hybrid]
- **Seniority**: [Level]
- **Posted**: [date or "~X days ago"]
- **Link**: [URL]
- **Key Requirements**: [3–5 bullets from the JD]
- **Why It Matches**: [1–2 sentences tied to user's CV]
- **Gaps**: [specific missing skills, or "None identified"]
```

End with a **Search Summary**:
- Platforms searched
- Total found before filtering
- Total after filtering
- Breakdown by match level (⭐⭐⭐ / ⭐⭐ / ⭐)
- Most common filter-out reasons
- Suggested next search iteration (if results were thin)

---

## Phase 8 — Save Results

After presenting results to the user, complete both steps:

### Step 1 — Markdown session log
Save the full output to:
`job-results/YYYY-MM-DD_search.md`

Include: all job listings (same format as Phase 7), plus the Search Summary (platforms, queries, match breakdown).

### Step 2 — Excel tracker
Use the helper script at `job-results/excel_helper.py`. Do NOT write inline openpyxl code.

**Command:**
```bash
python "job-results/excel_helper.py" '<json>'
```

**JSON format** — pass a JSON array of job objects:
```json
[
  {"title": "Algorithm Engineer", "company": "Taboola", "location": "Tel Aviv (Hybrid)", "match": "good", "url": "https://..."},
  {"title": "Data Scientist", "company": "Wix", "location": "Tel Aviv", "match": "strong", "url": "https://..."}
]
```

**`match` values:** `"strong"` (⭐⭐⭐), `"good"` (⭐⭐), `"potential"` (⭐)

The script handles all formatting, colors, borders, hyperlinks, and freeze panes automatically. It appends to existing data and creates the file if it doesn't exist.

---

## Rules (Non-Negotiable)

- Never fabricate a job posting or URL
- Never include a posting you haven't verified exists at the link
- Never skip Phase 1 — ambiguous profiles produce useless results
- If the user's request is vague (e.g., "find me jobs"), ask for role and location before proceeding
- Always note your search queries used, so the user can replicate or refine them
