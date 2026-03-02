# ResuForge

A Claude-powered resume tailoring tool. It scrapes recent LinkedIn job postings, ranks the most relevant ones against your resume, and rewrites your resume for each — optimized for ATS keyword matching.

All AI logic runs through Claude Code skills. Python handles only the mechanical parts: reading/writing `.docx` files and browser automation.

---

## Requirements

- [Claude Code](https://claude.ai/code) (authenticated)
- [uv](https://docs.astral.sh/uv/) (Python package manager)
- A LinkedIn account
- Your resume as `resume.docx` in the project root

---

## Setup

**1. Clone / open the project in Claude Code**

**2. Install dependencies**
```bash
uv sync
uv run playwright install chromium
```

**3. Configure credentials**
```bash
cp .env.example .env
```
Edit `.env`:
```
LINKEDIN_EMAIL=you@email.com
LINKEDIN_PASSWORD=yourpassword
```

**4. Configure your job search**

Edit `config.json`:
```json
{
  "job_titles": ["Data Engineer", "AI Engineer"],
  "location": "Pune",
  "keywords": ["Python", "AWS", "Gen AI", "LLM", "BigQuery"],
  "max_jobs_to_scrape": 20,
  "top_jobs_count": 5
}
```

**5. Add your resume**

Place your resume in the project root as `resume.docx`.

---

## Usage

All commands are run as Claude Code skills inside the project.

### Run the full pipeline

```
/resume-pipeline
```

Scrapes LinkedIn → ranks top jobs → tailors and saves a resume for each. Tailored resumes are saved to:
```
resumes/{CompanyName}/{job_id}/resume.docx
```

### Individual skills

| Skill | Description |
|-------|-------------|
| `/parse-resume` | Display the sections Claude extracts from your resume |
| `/rank-jobs` | Rank jobs in `jobs.json` against your resume |
| `/tailor-resume <job_id>` | Tailor your resume for one specific job |

> **Note:** `/rank-jobs` and `/tailor-resume` require `jobs.json` to exist. Run `/resume-pipeline` or `uv run python src/linkedin_scraper.py` first.

---

## How it works

1. **Read resume** — `src/docx_utils.py` extracts text from `resume.docx` as JSON
2. **Scrape jobs** — `src/linkedin_scraper.py` opens a Chromium browser, logs into LinkedIn, and collects up to `max_jobs_to_scrape` recent job postings across all configured `job_titles` into `jobs.json`
3. **Rank jobs** — Claude reads your resume and all job descriptions, then selects the top `top_jobs_count` matches based only on skills explicitly present in your resume
4. **Tailor resumes** — Claude rewrites bullet points and summary sentences to incorporate keywords from each job description, without adding any skills not already in your resume
5. **Save** — `src/docx_utils.py` applies the rewrites to your original `.docx`, preserving all formatting (bold, italic, font sizes)

---

## Notes

- **CAPTCHA**: The LinkedIn scraper runs with a visible browser window. If LinkedIn shows a CAPTCHA, solve it manually and the scraper will continue.
- **ATS safety**: Claude is explicitly instructed never to add skills, tools, or technologies not present in your original resume — only existing content is reworded.
- **Formatting preserved**: Only the text of each line is changed; bold, italic, font, and size are untouched.
- **`jobs.json`** is an intermediate file and is gitignored. Re-run the scraper to refresh it.
- **Multiple job titles**: The scraper searches each title in `job_titles` sequentially, sharing the `max_jobs_to_scrape` budget across all searches.

---

## Project structure

```
ResuForge/
├── resume.docx                  # Your master resume (add manually, gitignored)
├── config.json                  # Job search configuration
├── pyproject.toml               # uv project and dependencies
├── uv.lock                      # Lockfile (auto-generated)
├── .env                         # LinkedIn credentials (gitignored)
├── .env.example                 # Credentials template
├── src/
│   ├── docx_utils.py            # CLI: read/write .docx files
│   └── linkedin_scraper.py      # Playwright LinkedIn scraper
├── .claude/skills/
│   ├── resume-pipeline/         # /resume-pipeline
│   ├── parse-resume/            # /parse-resume
│   ├── rank-jobs/               # /rank-jobs
│   └── tailor-resume/           # /tailor-resume <job_id>
└── resumes/                     # Output directory (gitignored)
    └── {CompanyName}/
        └── {job_id}/
            └── resume.docx
```
