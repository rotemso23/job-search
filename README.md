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

3. **Tailor your CV** — launch the `cv-tailoring-agent` with a JD to get a tailored version of your CV optimized for that specific role.
