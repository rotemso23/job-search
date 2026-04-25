# AI-Assisted Job Search Workspace

A Claude Code agent workspace that automates and streamlines the job search process — from finding relevant job postings to analyzing job descriptions and tailoring a CV for each application.

---

## What this repo is

A set of AI agent definitions and strategy playbooks that run inside [Claude Code](https://claude.ai/code). Each agent handles a specific part of the job search workflow, guided by a strategy skill that defines exactly how the work is done.

---

## Getting started

### Prerequisites
- [Claude Code](https://claude.ai/code) installed and configured ([installation guide](https://docs.anthropic.com/en/docs/claude-code/getting-started))
- Python 3.8+ with pip
- Your CV saved as a PDF

### 1. Clone the repo and open it in Claude Code

```bash
git clone https://github.com/rotemso23/job-search.git
```

Then open the folder in Claude Code.

### 2. Configure your profile

Copy `config.example.ini` → `config.ini` in the repo root and fill in your details:

```ini
[user]
email = your@gmail.com
cv_file = MY_CV.md        # the Markdown CV the agents will read

[search]
location = City, Country      # used as the LinkedIn location filter
seniority = junior            # junior / mid / senior — used to score search results
job_titles =                  # replace with your target titles, one per line, indented with spaces
    Software Engineer
    Data Engineer
    ML Engineer
```

> `config.ini` and your CV files are excluded from version control — they never get committed.

### 3. Add your CV

1. Save your CV as a PDF in the repo root — name it whatever you like (e.g. `John_Doe_CV.pdf`).
2. In `config.ini`, set `cv_file` to the same name but with `.md` — e.g. `cv_file = John_Doe_CV.md`.
3. Install dependencies and run the converter:

```bash
pip install -r requirements.txt
python convert_cv.py
```

This reads your PDF and creates the Markdown file automatically. Re-run it any time you update your CV.

> **Important:** open `.gitignore`, find the `# MY_CV.md` line at the bottom, uncomment it and replace `MY_CV.md` with your actual filename so it never gets committed.

---

## How to use

### Launching an agent

Open Claude Code in this folder and describe what you want in natural language:

```
Run the job-search-agent
```

Replace `job-search-agent` with whichever agent you want to run.

### Workflow

1. **Search for jobs** — launch `job-search-agent` to find relevant postings based on your profile and preferences. Results are saved to:
   - `job-results/YYYY-MM-DD_search.md` — full session log
   - `job-results/job_tracker.xlsx` — running Excel tracker with all jobs across sessions, color coded by match quality:
     - 🟢 Green — strong match
     - 🟡 Yellow — good match
     - 🔴 Red — potential match (some gaps)

2. **Analyze a job description** — launch `jd-analyzer-agent` with a job posting URL or paste the JD text directly. It produces a `jd-analysis.md` file with required skills, ATS keywords, and real role priorities.

   > If the analysis output notes that the job description couldn't be fully fetched, copy the full JD text from the job posting and paste it into the chat to get a complete result.

3. **Tailor your CV** — paste a job description and launch `cv-tailoring-agent` to get `jd-analysis.md` and `recommendations.md` — a structured tailoring guide you apply to your own CV file.

---

## Structure

The system uses a two-layer pattern:

**Agents** (`.claude/agents/`) — define *who* does the work: the agent's identity, tools, and which skill(s) to load. Agents contain no logic.

**Skills** (`.claude/skills/`) — define *how* the work is done: phased playbooks with rules, scoring logic, and output formats. Skills are the single source of truth for all task logic.

### Agent → Skill mapping

| Agent | Skills loaded (in order) |
|-------|--------------------------|
| `job-search-agent` | `job-search-strategy` |
| `jd-analyzer-agent` | `jd-analyzer-strategy` |
| `cv-tailoring-agent` | `jd-analyzer-strategy` → `cv-tailoring-strategy` |

---

## Automation Pipeline (Windows only)

In addition to manual use, the workspace includes a fully autonomous daily loop driven by Windows Task Scheduler.

**How it works:** Every morning the pipeline searches for jobs and emails you a numbered list. You reply to that email with the numbers of the jobs you want to apply to (e.g. `1, 3, 5`). The pipeline picks up your reply and for each selected job runs the CV tailoring agent — which analyzes the job description and produces a tailored recommendations file telling you exactly how to adapt your CV for that role. A completion email is sent when done. That's the only action required from you each day.

### Setup

1. Create a `.credentials/` folder in the repo root and save your Gmail app password inside it as `gmail.secret` (plain text, nothing else in the file).

   > **What is a Gmail app password?** It's a 16-character code that lets an app send email on your behalf — it is NOT your regular Gmail password. To generate one:
   > 1. Go to [myaccount.google.com](https://myaccount.google.com) → **Security**
   > 2. Under "How you sign in to Google", enable **2-Step Verification** if not already on
   > 3. Search for **App passwords** (or go to Security → 2-Step Verification → scroll to the bottom)
   > 4. Create a new app password — name it anything (e.g. "Job Search")
   > 5. Copy the 16-character code into `.credentials/gmail.secret` (no spaces, no quotes)

2. Run `setup-scheduler.ps1` as Administrator once to register the scheduled tasks. Open a command prompt as Administrator and run:
   ```
   powershell.exe -ExecutionPolicy Bypass -File ".\setup-scheduler.ps1"
   ```
3. The pipeline runs automatically from that point on — job search at 08:15, reply checks every hour from 09:00.

> `.credentials/` is excluded from version control — never commit credentials.

### Scripts

You only need to run `setup-scheduler.ps1` once — the other scripts are triggered automatically by the scheduler.

| File | Role |
|------|------|
| `setup-scheduler.ps1` | **Run this once** (as Administrator) to register the scheduled tasks |
| `run-job-search.ps1` | Triggered automatically at 08:15 — executes `job-search-agent` and emails results with a numbered quick-apply list |
| `check-reply.py` | Triggered automatically every hour from 09:00 — checks Gmail for your reply, parses selected job numbers, runs `cv-tailoring-agent` per job, sends a completion email |

### Flow

```
scheduler
  → run-job-search.ps1 → email to user
  → user replies with job numbers
  → check-reply.py → cv-tailoring-agent per selection → completion email
```

### Debug Logging

`run-job-search.ps1` streams Claude's output in real time using `--output-format stream-json --verbose`. The log at `job-results/YYYY-MM-DD_debug.log` fills incrementally during the run — tail it to monitor progress. Tool calls appear as `[TOOL] ToolName: {input}` lines.
