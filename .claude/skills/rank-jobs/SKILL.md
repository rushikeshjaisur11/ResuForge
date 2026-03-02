# Rank Jobs

Rank the scraped jobs by relevance to the resume.

## Step 1 — Load data

Run:
```bash
uv run python src/docx_utils.py read resume.docx
```

Then read `jobs.json` (run `uv run python src/linkedin_scraper.py` first if it doesn't exist).

## Step 2 — Rank

Read `config.json` for `top_jobs_count`.

Using the resume content and the job descriptions, select the top `top_jobs_count` most relevant jobs. Consider only skills and experience **explicitly present** in the resume.

## Step 3 — Display results

Print a ranked list:

**#1 — {Job Title} @ {Company}**
Reason: {one sentence explaining relevance}

**#2 — ...**
...
