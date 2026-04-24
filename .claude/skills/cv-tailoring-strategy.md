---
name: cv-tailoring-strategy
description: "Teaches the cv-tailoring-agent how to adapt a CV to a specific job description — rewriting bullets, placing ATS keywords, reordering sections, and flagging honest gaps — without fabricating experience. Also handles direct CV edits when no JD is involved."
---

# CV Tailoring Strategy Playbook

This playbook covers JD-driven CV tailoring only. Follow phases 1–7 in order.

---

## Automated Mode Rules

When running as part of the automated pipeline (triggered by `check-reply.py`, not by a live user), **never block or wait for input.** These rules override **every** "ask the user", "stop", and "stop and ask" instruction anywhere in this playbook. Flagging issues in the output file (warnings, banners) is always allowed and encouraged.

---


## Phase 1 — Inputs Checklist (JD Tailoring mode)

Follow this sequence in order — do not skip ahead:

**Step 1 — Get the CV**
Load from memory if available. If not, ask: "Please share your CV — paste the text or upload the file."

**Step 2 — Check for existing JD analysis**
If the company name is known, look for an existing analysis. Check in this order (most specific first):
1. `CV\[Company Name] - [Job Title]\jd-analysis.md` — exact match for this company + role
2. `CV\[Company Name]\jd-analysis.md` — only if step 1 does not exist

Use the first one found. If both exist, always use #1 (the specific one). Note the folder path — it will be reused in Phase 7.

- If a file is found → load it and skip to Phase 2. Do not re-fetch or re-analyze.
  - Check if the file starts with a `⚠️ WARNING: JD not fully read` banner. If it does, carry that warning forward — it must appear at the top of `recommendations.md` as well.
- If neither exists → continue to Step 3.

**Step 3 — Verify the full JD is available**
Before running any analysis, confirm you have the complete job description text:
- If the JD appears truncated, cut off, ends with "…", or is missing sections — **stop immediately**:
  > "The job description appears incomplete. Please paste the full JD before I continue."
- If no JD has been provided at all — ask: "Please share the JD — paste the text or give me the URL."
- Only proceed once the full JD is confirmed complete.

**Step 4 — Run JD analysis**
Run the `jd-analyzer-strategy` playbook to extract must-haves, hidden priorities, tech stack, and ATS keywords. The analyzer determines and creates the folder automatically — note the folder path it uses for Phase 7.

After the analyzer completes, check the saved `jd-analysis.md` for a `⚠️ WARNING: JD not fully read` banner. If present, carry it forward — it must appear at the top of `recommendations.md` as well.

---

## Phase 2 — CV Parsing

Extract from the CV:

| Element | Why it matters |
|---------|---------------|
| Current/target job title | Match or bridge to JD title |
| Skills and technologies | Map against JD must-haves and nice-to-haves |
| Work experience, thesis, and project bullets | Primary rewrite targets |
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

Never invent experience. Never upgrade "familiar with" to "expert in" unless the user confirms it. Never infer skills from context — if a skill is not explicitly named in the CV, do not add it, even if the project or thesis work implies it (e.g., do not add "CNN" because the thesis involved deep learning).

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

Work through each experience, thesis, and project section. For each bullet:

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

## Phase 7 — Output Format

**Do NOT modify or save the base CV.** Instead, produce a recommendations file that tells the user exactly what to change.

### Saving the Recommendations

1. **Use the folder established in Phase 1** (either found in Step 2 or created by the jd-analyzer in Step 4). Do not create a new folder.

2. **Save a recommendations file:**
   `C:\Users\משתמש\Desktop\job search\CV\[folder from Phase 1]\recommendations.md`

3. **Confirm to the user:**
   > Recommendations saved to `CV\[folder from Phase 1]\recommendations.md`

### Recommendations File Format

Choose the correct value based on must-have coverage: `strong` (≥80% met), `good` (60–79%), `potential` (<60% or 3+ gaps). Hard cap: if the JD was not fully read (⚠️ WARNING banner is present in jd-analysis.md), use `good` at most — never `strong`.

```markdown
EXCEL_MATCH: strong

# CV Tailoring Recommendations — [Company Name] / [Job Title]

⚠️ WARNING: JD not fully read — [reason]. Analysis is based on partial content and may be incomplete.
(Include this line only if the warning was present in jd-analysis.md. Omit otherwise.)

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
- **Promote:** [skill / technology already in CV] — [where to move it for better visibility]
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

- Never fabricate or infer experience, skills, titles, dates, or metrics — only use what is explicitly stated in the CV
- Never upgrade a skill level without user confirmation
- Always show before/after for every rewrite — never silently change content
- If the user's CV is a poor match for the role (< 40% must-haves met), say so directly before tailoring — don't paper over a bad fit
- Preserve the user's voice — don't make all bullets sound identical
