"""
convert_cv.py
Converts your CV PDF to Markdown so the job-search agents can read it.
Run once after updating your CV PDF:

    python convert_cv.py

Reads cv_file from config.ini, expects a PDF with the same base name in the
same directory, and writes the Markdown file ready for use by the agents.
"""

import configparser
import pathlib
import sys

import pymupdf

WORK_DIR = pathlib.Path(__file__).parent
CONFIG   = WORK_DIR / "config.ini"

if not CONFIG.exists():
    sys.exit("config.ini not found — copy config.example.ini and fill in your details.")

cfg = configparser.ConfigParser()
cfg.read(CONFIG)

cv_md  = WORK_DIR / cfg["user"]["cv_file"]
cv_pdf = cv_md.with_suffix(".pdf")

if not cv_pdf.exists():
    sys.exit(f"PDF not found: {cv_pdf}\nSave your CV as '{cv_pdf.name}' in the repo root.")

print(f"Converting {cv_pdf.name} -> {cv_md.name} ...")
doc = pymupdf.open(str(cv_pdf))
pages = []
for page in doc:
    pages.append(page.get_text())
cv_md.write_text("\n\n".join(pages), encoding="utf-8")
print(f"Done. {cv_md.name} is ready.")
