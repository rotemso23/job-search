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
- When adding a new agent that reads JDs, load `jd-analyzer-strategy` first — do not duplicate its logic.
- Each agent has its own memory directory under `.claude/agent-memory/[agent-name]/` with a `MEMORY.md` index.
