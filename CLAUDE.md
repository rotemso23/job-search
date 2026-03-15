# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

A Claude Code agent workspace for an AI-assisted job search pipeline. There is no application code — the repo consists entirely of agent definitions and strategy playbooks.

## Architecture

The system follows a strict two-layer pattern:

**Agents** (`.claude/agents/`) — define *who* does the work: identity, tools, memory directory, and a pointer to the relevant skill(s). Agents contain no logic.

**Skills** (`.claude/skills/`) — define *how* the work is done: phased playbooks with rules, classification logic, output formats. Skills are the single source of truth for all task logic.

### Agent → Skill mapping

| Agent | Skills loaded (in order) |
|-------|--------------------------|
| `job-search-agent` | `job-search-strategy` |
| `jd-analyzer-agent` | `jd-analyzer-strategy` |
| `cv-tailoring-agent` | `jd-analyzer-strategy` → `cv-tailoring-strategy` |

The `jd-analyzer-strategy` skill is intentionally shared — the cv-tailoring-agent uses it to read and extract the JD before tailoring the CV.

## Conventions

- Agent files are named `[name]-agent.md`, skill files are named `[name]-strategy.md`.
- When logic changes (scoring, output format, filtering rules), edit the **skill** — never the agent.
- Each agent has its own memory directory under `.claude/agent-memory/[agent-name]/` with a `MEMORY.md` index.

## Local-Only (not in repo)

The following directories exist locally but are excluded from version control:

- `CV/` — tailored CV files per application
- `job-results/` — job search session logs and tracker

## Workflow Rules

- **Always read the strategy skill before launching an agent.** For example, before launching `job-search-agent`, read `job-search-strategy.md` and complete all required pre-flight steps (e.g. Phase 1 profile extraction) before invoking the agent.
- **After every job search session, save results to a file** at `job-results/YYYY-MM-DD_search.md`. Include all job listings and the search summary.
