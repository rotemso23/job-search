# AI-Assisted Job Search Workspace

A Claude Code agent workspace that automates and streamlines the job search process — from finding relevant job postings to analyzing job descriptions and tailoring a CV for each application.

---

## What this repo is

This is not an application — it's a set of AI agent definitions and strategy playbooks that run inside [Claude Code](https://claude.ai/code). Each agent handles a specific part of the job search workflow, guided by a strategy skill that defines exactly how the work is done.

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

## How to use

### Prerequisites
- [Claude Code](https://claude.ai/code) installed and configured
- Your CV saved locally
- A LinkedIn / job board account for sourcing postings

### Workflow

1. **Search for jobs** — launch the `job-search-agent` to find relevant job postings based on your profile and preferences. Results are saved to `job-results/`.

2. **Analyze a job description** — paste a JD and launch the `jd-analyzer-agent` to extract required skills, ATS keywords, and real role priorities.

3. **Tailor your CV** — launch the `cv-tailoring-agent` with a JD to get `jd-analysis.md` and `recommendations.md` — a structured tailoring guide you apply to your own CV file.

---

## Automation Pipeline

In addition to manual use, the workspace includes a fully autonomous daily loop driven by Windows Task Scheduler.

### Scripts

| File | Role |
|------|------|
| `setup-scheduler.ps1` | Run once (as Administrator) to register the scheduled tasks |
| `run-job-search.ps1` | Runs daily at 08:15 — executes `job-search-agent` and emails results with a numbered quick-apply list |
| `check-reply.py` | Runs hourly from 09:00 — checks Gmail for your reply, parses selected job numbers, runs `cv-tailoring-agent` per job, sends a completion email |

### Flow

```
scheduler
  → run-job-search.ps1 → email to user
  → user replies with job numbers
  → check-reply.py → cv-tailoring-agent per selection → completion email
```

### Debug Logging

`run-job-search.ps1` streams Claude's output in real time using `--output-format stream-json --verbose`. The log at `job-results/YYYY-MM-DD_debug.log` fills incrementally during the run — tail it to monitor progress. Tool calls appear as `[TOOL] ToolName: {input}` lines.

### Setup

1. Store your Gmail app password in `.credentials/gmail.secret` (plain text).
2. Run `setup-scheduler.ps1` as Administrator once to register the tasks.
3. The pipeline runs automatically from that point on.

> `.credentials/` is excluded from version control — never commit credentials.
