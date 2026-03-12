import anyio
from pathlib import Path
from datetime import datetime
from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage, AssistantMessage, TextBlock

CV_PATH = Path(__file__).parent.parent / ".claude" / "agent-memory" / "cv-tailoring-agent" / "cv.md"
OUTPUT_DIR = Path(__file__).parent / "outputs"

PROMPT = """You are a job search assistant helping a junior candidate find AI/ML/Data roles in Israel.

## Step 1 — Read the CV
Read the candidate's CV from: {cv_path}

## Step 2 — Search for jobs
Run multiple Google searches to find junior job postings on LinkedIn in Israel. Use searches like:
- site:linkedin.com/jobs "machine learning" junior Israel
- site:linkedin.com/jobs "data scientist" junior "Tel Aviv"
- site:linkedin.com/jobs "AI engineer" entry level Israel
- site:linkedin.com/jobs "data engineer" junior Israel
- site:linkedin.com/jobs "research engineer" Israel junior

Prefer jobs in the center of Israel (Tel Aviv, Herzliya, Ra'anana, Petah Tikva, Ramat Gan, etc.).
Collect up to 10 unique job postings. For each one, fetch the full job page to get the description.

## Step 3 — Analyze each job
For each job, provide:

### [Job Title] — [Company]
**URL:** [url]
**Location:** [location]

**Match Score:** X/100
*One sentence verdict*

**Strengths**
- What in the CV fits this role

**Gaps**
- What is missing or weak

**CV Tailoring**
- Specific changes to make the CV stronger for this exact role

---

## Step 4 — Save the report
Save the full report (all 10 jobs) to: {output_path}

Start with a summary table at the top of the report:
| # | Job Title | Company | Match Score |
|---|-----------|---------|-------------|
"""


async def main():
    if not CV_PATH.exists():
        print(f"Error: CV not found at {CV_PATH}")
        return

    OUTPUT_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = OUTPUT_DIR / f"job_search_{timestamp}.md"

    prompt = PROMPT.format(cv_path=CV_PATH, output_path=output_path)

    print("Starting job search pipeline...")
    print(f"Searching for junior AI/ML/Data jobs in Israel...\n")

    async for message in query(
        prompt=prompt,
        options=ClaudeAgentOptions(
            cwd=str(Path(__file__).parent.parent),
            allowed_tools=["WebSearch", "WebFetch", "Read", "Write"],
            permission_mode="acceptEdits",
            max_turns=50,
        )
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock) and block.text.strip():
                    print(f"[agent] {block.text.strip()}")
        elif isinstance(message, ResultMessage):
            print("\nDone!")
            print(f"Results saved to: {output_path}")


anyio.run(main)
