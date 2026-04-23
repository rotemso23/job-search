# Plan: Make Repo Public-Ready for LinkedIn / Others

## Context
The user wants to push this job-search pipeline to GitHub and share it on LinkedIn — both as a portfolio project and as a reusable tool for others. Currently several files contain personal details (email, CV filename, name references) that must be abstracted before the repo is public-safe.

---

## What needs to change

### 1. Add a `config.ini` + `config.example.ini`
Create `config.example.ini` (committed) and add `config.ini` to `.gitignore` (the actual local config, never committed).

```ini
# config.example.ini
[user]
email = your@gmail.com
cv_file = MY_CV.md
```

This becomes the single place users set their identity.

### 2. `check-reply.py` — read email from config
- **Line 23**: replace hardcoded `EMAIL_ADDR = "rotemso23@gmail.com"` with a `configparser` read from `config.ini`.

### 3. `run-job-search.ps1` — read email from config
- **Lines 12–13**: replace hardcoded `$from`/`$to` with lines that read `email` from `config.ini`.

### 4. `.claude/skills/job-search-strategy.md` — generalize CV reference
- **Line 14**: change `Rotem Solomon CV.md` → `MY_CV.md` (or read cv_file from config).
- **Lines 30, 119**: remove name-specific section header "Target Job Titles for Rotem Solomon" → "Target Job Titles" and remove "Rotem's" pronoun → "your".

### 5. `.gitignore` — add personal planning docs
These three untracked files (shown as `??` in git status) are personal notes, not part of the framework. Add them to `.gitignore`:
- `CLAUDE_finetune_project.md`
- `CLAUDE_rag_project.md`
- `portfolio-projects.md`
Also add `config.ini` to `.gitignore`.

### 6. `README.md` — add a Configuration section
Insert a "Configuration" step before the existing Setup steps:
- Copy `config.example.ini` → `config.ini`
- Fill in your email and CV filename
- Name your CV file `MY_CV.md` (or whatever you set in config)

---

## Files to modify

| File | Change |
|------|--------|
| `.gitignore` | Add `config.ini`, `CLAUDE_*.md`, `portfolio-projects.md` |
| `config.example.ini` | **New file** — template for user config |
| `check-reply.py` | Read email from `config.ini` via `configparser` |
| `run-job-search.ps1` | Read email from `config.ini` |
| `.claude/skills/job-search-strategy.md` | Replace "Rotem Solomon CV.md" → `MY_CV.md`, remove name references |
| `README.md` | Add Configuration section |

---

## Verification
1. Run `check-reply.py` after setting up `config.ini` — should read email correctly without hardcoded value.
2. Confirm `git status` shows `CLAUDE_*.md` and `portfolio-projects.md` as ignored.
3. Confirm `config.ini` does not appear in `git status` after creation.
4. Confirm `Rotem Solomon CV.md` still gitignored (already is).
