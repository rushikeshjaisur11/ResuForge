# Resume Pipeline

Run the full resume tailoring pipeline end-to-end. Use your tools to execute each step below.

---

## Step 1 — Load configuration

Read `config.json` and `.env`. Note the values for:
- `job_title`, `location`, `top_jobs_count`
- `LINKEDIN_EMAIL`, `LINKEDIN_PASSWORD`

---

## Step 2 — Read the resume

Run:
```bash
uv run python src/docx_utils.py read resume.docx
```

Parse the JSON output. Extract the full resume text and identify the candidate's:
- Skills and technologies
- Job titles and companies held
- Years of experience per domain
- Education background

---

## Step 3 — Scrape LinkedIn jobs

Run:
```bash
uv run python src/linkedin_scraper.py
```

Wait for it to complete (it opens a browser window — the user may need to solve a CAPTCHA).
Then read `jobs.json`.

---

## Step 4 — Rank top jobs

Using your understanding of the resume from Step 2 and the jobs from `jobs.json`:

- Select the top `top_jobs_count` jobs most relevant to the candidate
- Only consider skills and experience **explicitly present** in the resume — do not infer
- For each selected job note: job_id, company, title, and a one-sentence reason

---

## Step 5 — Tailor resumes in parallel using subagents

Launch **one subagent per top job at the same time** using the Agent tool. Do not wait for one to finish before starting the next — fire all of them in a single parallel batch.

Each subagent receives:
- The full resume JSON (from Step 2)
- The job's details: `job_id`, `company`, `title`, `full_jd_text`

Each subagent must independently perform these steps:

### 5a. Build a rewrite mapping

Rewrite the resume's bullet points and summary sentences to better match the job description:
- **Do NOT** introduce any skill, tool, or technology not already in the resume
- Only reword existing content to incorporate keywords from the job description
- Keep the exact same number of bullets per role
- Do not change contact info, company names, education dates, or section headings

Build a JSON object:
```json
{"original bullet or sentence": "rewritten version"}
```
Include only lines you actually changed.

### 5b. Save the mapping

Sanitize the company name (spaces → `_`, remove special chars).

Write the mapping JSON to:
```
resumes/{CompanyName}/{job_id}/mapping.json
```

### 5c. Apply the mapping

Run:
```bash
uv run python src/docx_utils.py write resume.docx "resumes/{CompanyName}/{job_id}/resume.docx" "resumes/{CompanyName}/{job_id}/mapping.json"
```

Each subagent should return the saved path on success, or an error message on failure.

---

## Step 6 — Summary

Collect results from all subagents, then print a table:

| Rank | Company | Job Title | Saved Path |
|------|---------|-----------|------------|
| ...  | ...     | ...       | ...        |

Note any subagents that failed alongside their error.
