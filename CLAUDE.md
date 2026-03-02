# CLAUDE.md

## Project: ResuForge

Claude skills orchestrate the full pipeline. Python is used only for mechanical I/O (reading/writing .docx files and running the Playwright browser scraper). All intelligence — parsing, ranking, tailoring — is done by Claude inline.

## Setup

```bash
pip install -r requirements.txt
playwright install chromium
cp .env.example .env   # fill in LinkedIn credentials
# Place your resume as resume.docx in the project root
```

## Usage (Claude skills)

| Skill | What it does |
|-------|-------------|
| `/resume-pipeline` | Full end-to-end: scrape → rank → tailor → save |
| `/parse-resume` | Display structured sections of resume.docx |
| `/rank-jobs` | Rank jobs in jobs.json against the resume |
| `/tailor-resume <job_id>` | Tailor resume.docx for one specific job |

## Architecture

```
.claude/commands/
  resume-pipeline.md   # Full pipeline skill (main entry point)
  parse-resume.md      # Display resume sections
  rank-jobs.md         # Rank scraped jobs
  tailor-resume.md     # Tailor for one job by job_id

src/
  docx_utils.py        # CLI: read .docx to JSON / write tailored .docx
  linkedin_scraper.py  # Playwright scraper — saves jobs.json

config.json            # job_title, location, top_jobs_count, max_jobs_to_scrape, targeted_companies
.env                   # LINKEDIN_EMAIL, LINKEDIN_PASSWORD
resume.docx            # Master resume (placed manually)
resumes/               # Output — auto-created per job
jobs.json              # Scraper output (intermediate, gitignored)
```

## Key Design Decisions

- **No API key, no subprocess** — Claude skills run in-session; Claude uses its own intelligence directly (no `claude -p` subprocess).
- **Python = plumbing only** — `docx_utils.py` and `linkedin_scraper.py` have zero AI logic; they are thin CLI wrappers called via Bash tool.
- **Playwright headless=False** — browser is visible so the user can solve CAPTCHA if needed.
- **ATS constraint** — skills explicitly instruct Claude never to add skills not in the original resume.
- **Run-level formatting preserved** — `docx_utils.py write` only mutates `.text` on runs; bold/italic/font/size stay intact.

## Non-obvious Conventions

- `docx_utils.py read` outputs JSON to stdout; Claude reads it via Bash tool.
- `docx_utils.py write <src> <out> <mapping.json>` applies the mapping and creates parent dirs automatically.
- Output path: `resumes/{Company}/{job_id}/resume.docx`; company name sanitized (spaces → `_`).
- `targeted_companies` in config.json is an **optional** list of company name strings. When non-empty, the scraper
  will only keep jobs whose scraped company name contains (or is contained by) one of the listed names —
  case-insensitive substring match. Set to `[]` to scrape all companies (default, no filter).
  Example: `"targeted_companies": ["Google", "Microsoft", "Thoughtworks"]`
