"""
check-reply.py
Runs every hour via Task Scheduler.
Checks Gmail for a reply to today's job search email, runs the CV tailor
agent for each selected job, then sends a completion email.
Stops processing after 07:15 the next day (1 hour before the next search runs).
"""

import imaplib
import email
import email.header
import json
import os
import re
import subprocess
import datetime
import pathlib
import smtplib
import ssl
from email.mime.text import MIMEText

WORK_DIR     = pathlib.Path(__file__).parent
USER_HOME    = r"C:\Users\משתמש"
EMAIL_ADDR   = "rotemso23@gmail.com"
APP_PASSWORD = (WORK_DIR / ".credentials" / "gmail.secret").read_text(encoding="utf-8").strip()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def get_search_date():
    """Return the date of the most recent results file, or None."""
    results_dir = WORK_DIR / "job-results"
    files = sorted(results_dir.glob("????-??-??_search.md"), reverse=True)
    if not files:
        return None
    return files[0].stem.split("_")[0]   # e.g. "2026-03-17"


def done_flag_path(date):
    return WORK_DIR / ".credentials" / f"{date}_tailoring_done.flag"


def past_stop_time(date):
    """True if it's past 07:15 the next day (1 hour before the next search runs)."""
    next_day = datetime.date.fromisoformat(date) + datetime.timedelta(days=1)
    stop_dt  = datetime.datetime.combine(next_day, datetime.time(7, 15))
    return datetime.datetime.now() >= stop_dt


def parse_jobs(date):
    """Return list of (title, full_section_text) from the results file."""
    f = WORK_DIR / "job-results" / f"{date}_search.md"
    if not f.exists():
        return []
    content = f.read_text(encoding="utf-8")
    # Split on ### headings (keep the heading in the section)
    sections = re.split(r'\n(?=### )', content)
    jobs = []
    for s in sections:
        m = re.match(r'^### (.+)', s)
        if m:
            title = m.group(1).strip()
            # Skip "Job X of Y" header lines — they are section counters, not job listings
            if re.match(r'^Job \d+ of \d+$', title):
                continue
            jobs.append((title, s))
    return jobs


def check_gmail_for_reply(date):
    """Return the plain-text body of a reply to today's email, or None."""
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(EMAIL_ADDR, APP_PASSWORD)
    mail.select("inbox")

    imap_date = datetime.date.fromisoformat(date).strftime("%d-%b-%Y")
    # Search for any email with the subject containing the date, from today
    status, ids = mail.search(None, f'(SUBJECT "Daily Job Search Results" SINCE "{imap_date}")')

    reply_body = None
    if status == "OK":
        for mid in ids[0].split():
            _, data = mail.fetch(mid, "(RFC822)")
            msg = email.message_from_bytes(data[0][1])

            raw_subject = email.header.decode_header(msg["Subject"])[0][0]
            subject = raw_subject.decode() if isinstance(raw_subject, bytes) else raw_subject

            if not subject.lower().startswith("re:"):
                continue

            # Extract plain text body
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        reply_body = part.get_payload(decode=True).decode("utf-8", errors="ignore")
                        break
            else:
                reply_body = msg.get_payload(decode=True).decode("utf-8", errors="ignore")

            if reply_body:
                break   # use first reply found

    mail.logout()
    return reply_body


def parse_numbers(text):
    """Extract all integers from the reply, ignoring quoted original email."""
    lines = []
    for line in text.splitlines():
        # Stop at quoted reply block (>, On ... wrote:, or -----Original Message-----)
        if line.startswith(">") or re.search(r"<[^>]+@[^>]+>", line) or line.startswith("-----"):
            break
        lines.append(line)
    return [int(n) for n in re.findall(r'\b(\d+)\b', "\n".join(lines))]


def run_cv_tailor(title, section):
    """Invoke the cv-tailoring-agent for one job."""
    prompt = (
        f"Run the cv-tailoring-agent for this job.\n\n"
        f"Job: {title}\n\n"
        f"Full job details from today's search results:\n{section}\n\n"
        "Fetch the full JD from the link in the details above and run the "
        "complete CV tailoring workflow. Save output to the appropriate "
        "subfolder under CV/ (jd-analysis.md and recommendations.md only)."
    )
    env = os.environ.copy()
    env["USERPROFILE"]  = USER_HOME
    env["APPDATA"]      = USER_HOME + r"\AppData\Roaming"
    env["LOCALAPPDATA"] = USER_HOME + r"\AppData\Local"
    env["PATH"]         = USER_HOME + r"\.local\bin;" + env.get("PATH", "")

    result = subprocess.run(
        ["claude", "--dangerously-skip-permissions", "-p", prompt],
        cwd=str(WORK_DIR),
        capture_output=True,
        text=True,
        creationflags=subprocess.CREATE_NO_WINDOW,
        env=env,
    )
    if result.returncode != 0:
        output = (result.stdout or result.stderr or "no output").strip()
        # Keep last 300 chars to avoid huge emails
        raise RuntimeError(output[-300:])


def update_excel_for_job(work_dir, heading_title, after_timestamp):
    """After tailoring, find the new recommendations.md and update the Excel row color."""
    cv_dir = work_dir / "CV"
    if not cv_dir.exists():
        return

    # Find the recommendations.md written after tailoring started
    latest_file = None
    latest_mtime = after_timestamp
    for f in cv_dir.glob("*/recommendations.md"):
        mtime = f.stat().st_mtime
        if mtime > latest_mtime:
            latest_mtime = mtime
            latest_file = f
    if not latest_file:
        return

    # Parse EXCEL_MATCH line
    text = latest_file.read_text(encoding="utf-8")
    m = re.search(r'^EXCEL_MATCH:\s*(strong|good|potential)', text, re.MULTILINE | re.IGNORECASE)
    if not m:
        return
    match_level = m.group(1).lower()

    # Parse "Job Title at Company" from the section heading
    parts = heading_title.rsplit(" at ", 1)
    if len(parts) != 2:
        return
    job_title, company = parts[0].strip(), parts[1].strip()
    search_str = f"{job_title} — {company}"

    subprocess.run(
        ["python", str(work_dir / "excel_helper.py"),
         "update", json.dumps({"search": search_str, "match": match_level})],
        cwd=str(work_dir),
        capture_output=True,
    )


def collect_jd_warnings(work_dir):
    """Return warning lines from any CV/*/jd-analysis.md files modified today."""
    today = datetime.date.today()
    warnings = []
    cv_dir = work_dir / "CV"
    if not cv_dir.exists():
        return warnings
    for analysis_file in cv_dir.glob("*/jd-analysis.md"):
        mtime = datetime.date.fromtimestamp(analysis_file.stat().st_mtime)
        if mtime != today:
            continue
        text = analysis_file.read_text(encoding="utf-8")
        for line in text.splitlines():
            if line.startswith("⚠️ WARNING: JD not fully read"):
                warnings.append(f"  - {analysis_file.parent.name}: {line.strip()}")
                break
    return warnings


def send_email(subject, body):
    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"]    = EMAIL_ADDR
    msg["To"]      = EMAIL_ADDR

    ctx = ssl.create_default_context()
    with smtplib.SMTP("smtp.gmail.com", 587) as s:
        s.ehlo()
        s.starttls(context=ctx)
        s.login(EMAIL_ADDR, APP_PASSWORD)
        s.sendmail(EMAIL_ADDR, EMAIL_ADDR, msg.as_string())


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    date = get_search_date()
    if not date:
        print("No results file found. Nothing to do.")
        return

    flag = done_flag_path(date)
    if flag.exists():
        print(f"Already processed replies for {date}. Exiting.")
        return

    if past_stop_time(date):
        print(f"Past stop time for {date} (07:15 next day). Exiting.")
        return

    print(f"Checking Gmail for reply to {date} job search email...")
    reply = check_gmail_for_reply(date)
    if not reply:
        print("No reply found yet.")
        return

    print("Reply found. Parsing job numbers...")
    numbers = parse_numbers(reply)
    if not numbers:
        print("No numbers found in reply. Exiting.")
        return

    jobs = parse_jobs(date)
    selected = []
    for n in numbers:
        if 1 <= n <= len(jobs):
            selected.append(jobs[n - 1])
        else:
            print(f"  Job #{n} is out of range (max {len(jobs)}). Skipping.")

    if not selected:
        print("No valid jobs selected. Exiting.")
        return

    # Mark done immediately to prevent double-processing
    flag.touch()

    print(f"Running CV tailor agent for {len(selected)} job(s)...")
    completed, failed = [], []
    for title, section in selected:
        try:
            print(f"  -> {title}")
            start_ts = datetime.datetime.now().timestamp()
            run_cv_tailor(title, section)
            completed.append(title)
            update_excel_for_job(WORK_DIR, title, start_ts)
        except Exception as e:
            print(f"  FAILED: {title} — {e}")
            failed.append((title, str(e)))

    # Build completion email
    cv_dir = str(WORK_DIR / "CV")
    lines = [f"CV tailoring is done for your {date} job selections.\n"]

    if completed:
        lines.append("Completed:")
        for t in completed:
            lines.append(f"  - {t}")
        lines.append(f"\nYou can find the results here:\n{cv_dir}")
        lines.append("Each job folder contains: jd-analysis.md and recommendations.md")

    if failed:
        lines.append("\nFailed (run manually):")
        for t, reason in failed:
            lines.append(f"  - {t}")
            lines.append(f"    Reason: {reason}")

    jd_warnings = collect_jd_warnings(WORK_DIR)
    if jd_warnings:
        lines.append("\n⚠️ JD Read Warnings — these analyses used partial content:")
        lines.extend(jd_warnings)
        lines.append("Consider pasting the full JD manually and re-running tailoring for these jobs.")

    send_email(
        subject=f"CV Tailoring Done - {date}",
        body="\n".join(lines),
    )
    print("Completion email sent.")


if __name__ == "__main__":
    main()
