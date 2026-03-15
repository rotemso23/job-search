---
name: cv-tailoring-strategy
description: "Teaches the cv-tailoring-agent how to adapt a CV to a specific job description — rewriting bullets, placing ATS keywords, reordering sections, and flagging honest gaps — without fabricating experience. Also handles direct CV edits when no JD is involved."
---

# CV Tailoring Strategy Playbook

You handle two modes of CV work. Identify which applies before doing anything else:

| Mode | When to use |
|------|------------|
| **JD Tailoring** (Phases 1–8) | User wants the CV adapted to a specific job posting |
| **Direct Edit** (Phase 0) | User wants to update, correct, or improve the CV without a JD |

---

## Phase 0 — Direct CV Edit Mode (no JD)

Use this mode when the user asks to update, add, remove, or correct something in their CV directly — not in response to a JD.

**Step 1 — Get the CV**
Load from memory if available. If not, ask the user to paste or upload it.

**Step 2 — Apply the requested changes**
Make only the changes explicitly requested. Do not rewrite unrelated sections.

Show a before/after for every change:
```
Before: [original text]
After:  [updated text]
Reason: [what changed]
```

**Step 3 — Save the updated CV**
Write the full updated CV to:
`C:\Users\משתמש\Desktop\job search\CV\Rotem Solomon CV.md`

If the `CV` folder doesn't exist, create the file anyway — Claude Code will create the directory.

Also update the CV in memory:
- `C:\Users\משתמש\.claude\projects\c--Users-------Desktop-job-search\memory\user_cv.md`
- `C:\Users\משתמש\Desktop\job search\.claude\agent-memory\cv-tailoring-agent\cv.md`
- `C:\Users\משתמש\Desktop\job search\.claude\agent-memory\job-search-agent\cv.md`
- `C:\Users\משתמש\Desktop\job search\.claude\agent-memory\jd-analyzer-agent\cv.md`

**Step 4 — Confirm**
Tell the user what was changed and where the file was saved.

---

## Phase 1 — Inputs Checklist (JD Tailoring mode)

Follow this sequence in order — do not skip ahead:

**Step 1 — Get the CV**
Load from memory if available. If not, ask: "Please share your CV — paste the text or upload the file."

**Step 2 — Check for existing JD analysis**
If the company name is known, look for `C:\Users\משתמש\Desktop\job search\CV\[Company Name]\jd-analysis.md`.
- If the file **exists** → load it and skip to Phase 2. Do not re-fetch or re-analyze.
- If the file **does not exist** → continue to Step 3.

**Step 3 — Verify the full JD is available**
Before running any analysis, confirm you have the complete job description text:
- If the JD appears truncated, cut off, ends with "…", or is missing sections — **stop immediately**:
  > "The job description appears incomplete. Please paste the full JD before I continue."
- If no JD has been provided at all — ask: "Please share the JD — paste the text or give me the URL."
- Only proceed once the full JD is confirmed complete.

**Step 4 — Run JD analysis**
Run the `jd-analyzer-strategy` playbook to extract must-haves, hidden priorities, tech stack, and ATS keywords. The analyzer saves the result to `CV\[Company Name]\jd-analysis.md` automatically.

---

## Phase 2 — CV Parsing

Extract from the CV:

| Element | Why it matters |
|---------|---------------|
| Current/target job title | Match or bridge to JD title |
| Skills and technologies | Map against JD must-haves and nice-to-haves |
| Work experience bullets | Primary rewrite targets |
| Achievements with metrics | Highest-value content — preserve and surface |
| Education and certifications | Check against JD credentials |
| Summary / objective (if present) | First rewrite target — highest recruiter visibility |

Flag any CV sections that are missing but expected for the role (e.g., no summary for a senior role, no metrics in any bullet).

---

## Phase 3 — Gap Analysis

Before rewriting, map CV content against JD requirements:

| JD requirement | In CV? | Action |
|---------------|--------|--------|
| Must-have [M] skill | Yes | Ensure exact-match keyword is present |
| Must-have [M] skill | Partial | Rewrite bullet to make it explicit |
| Must-have [M] skill | No | Flag as honest gap — do not fabricate |
| Nice-to-have [N] skill | Yes | Include if space allows |
| Nice-to-have [N] skill | No | Skip — not worth forcing |

**Honest gap rule:** If the user genuinely lacks a must-have skill, flag it clearly:
> ⚠️ **Gap:** JD requires [skill] — not found in CV. Do not add this unless the user confirms they have it.

Never invent experience. Never upgrade "familiar with" to "expert in" unless the user confirms it.

---

## Phase 4 — Summary Rewrite

The summary is the first thing a recruiter reads and the highest-leverage rewrite.

Rules:
- 3–4 lines maximum
- Open with the exact job title from the JD (or close variant) — this is an ATS signal
- Include 2–3 Tier 1 ATS keywords naturally in the first 2 lines
- Mirror the seniority language from the JD ("senior", "lead", "principal")
- End with a value statement tied to the role's top hidden priority

**Before / After format:**
```
Before: [original summary text]
After:  [rewritten summary]
Reason: [what changed and why]
```

---

## Phase 5 — Bullet Rewriting

Work through each experience section. For each bullet:

**Step 1 — Relevance score**
- High: directly matches a JD must-have → rewrite to maximize keyword match
- Medium: adjacent to JD requirements → rewrite to draw the connection explicitly
- Low: unrelated to this role → candidate for removal or deprioritization

**Step 2 — Rewrite rules**
- Lead with a strong action verb that mirrors JD language (if the JD says "architected", use "architected" not "built")
- Include the exact technology name as it appears in the JD (e.g., if JD says "Apache Kafka", don't write "Kafka" alone)
- Add or preserve quantified outcomes: numbers, percentages, scale, time saved, revenue impact
- Keep bullets to 1–2 lines — remove filler words ("responsible for", "helped with", "worked on")

**Step 3 — Keyword insertion**
- Insert Tier 1 ATS keywords into bullets where the experience genuinely supports it
- Never repeat the same keyword more than 3 times across the entire CV — diminishing returns and spam flags
- Tier 2 keywords go into bullets or skills section; Tier 3 keywords go into summary or can be omitted

**Before / After format for each rewritten bullet:**
```
Before: [original bullet]
After:  [rewritten bullet]
Keywords added: [list]
```

---

## Phase 6 — Skills Section

- List must-have [M] technologies first, in the order they appear in the JD
- Group by category matching the JD's tech stack categories (Languages, Frameworks, Cloud, etc.)
- Remove skills with no JD relevance if the skills section is crowded
- Do not add skills the user doesn't have

---

## Phase 7 — Section Order

Reorder CV sections to match what this specific role prioritizes:

| Role type | Recommended order |
|-----------|------------------|
| Technical/engineering | Summary → Skills → Experience → Projects → Education |
| Management/leadership | Summary → Experience → Skills → Education |
| Career change / stretch role | Summary → Skills → Relevant Projects → Experience → Education |
| Early career (< 3 years) | Summary → Education → Skills → Experience |

If the JD emphasizes certifications or specific credentials, elevate Education/Certifications above Experience.

---

## Phase 8 — Output Format

**Do NOT modify or save the base CV.** Instead, produce a recommendations file that tells the user exactly what to change.

### Saving the Recommendations

1. **Create a company folder** inside the CV directory:
   `C:\Users\משתמש\Desktop\job search\CV\[Company Name]\`
   Use the exact company name from the JD. If the company name is unknown, use the job title instead.

2. **Save a recommendations file:**
   `C:\Users\משתמש\Desktop\job search\CV\[Company Name]\recommendations.md`

3. **Confirm to the user:**
   > Recommendations saved to `CV\[Company Name]\recommendations.md`

### Recommendations File Format

```markdown
# CV Tailoring Recommendations — [Company Name] / [Job Title]

**Job Link:** [URL to the job posting]

## Summary Section
- **Rewrite to:**
  [full rewritten summary text]
- **Reason:** [what changed and why]

## Experience Bullets

### [Role Title] @ [Company]
- **Change:** "[original bullet]"
  **To:** "[rewritten bullet]"
  **Keywords added:** [list]

- **Remove:** "[low-relevance bullet]"
  **Reason:** [why it hurts more than helps for this role]

## Skills Section
- **Add:** [skill / technology] — [where to place it]
- **Remove:** [skill] — [reason]
- **Reorder:** [new priority order for this role]

## Section Order
- **Change from:** [original order]
- **Change to:** [new order]
- **Reason:** [why]

## Honest Gaps
- ⚠️ [skill]: required by JD but not in CV — address in cover letter or before applying

## ATS Keyword Coverage
Tier 1 (must appear): [term ✓/✗] [term ✓/✗] ...
Tier 2 (high value):  [term ✓/✗] [term ✓/✗] ...
```

---

## Rules

- Never fabricate experience, skills, titles, dates, or metrics
- Never upgrade a skill level without user confirmation
- Always show before/after for every rewrite — never silently change content
- If the user's CV is a poor match for the role (< 40% must-haves met), say so directly before tailoring — don't paper over a bad fit
- Preserve the user's voice — don't make all bullets sound identical
- If the user asks to add a skill they don't have, refuse and explain why it backfires at interview
