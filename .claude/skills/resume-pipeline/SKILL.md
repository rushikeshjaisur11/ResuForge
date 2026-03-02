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

## Step 5 — Tailor resume for each top job

For each selected job, do the following:

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

Write the mapping JSON to:
```
resumes/{CompanyName}/{job_id}/mapping.json
```
Sanitize the company name for use as a directory (replace spaces with `_`, remove special chars).

### 5c. Apply the mapping

Run:
```bash
uv run python src/docx_utils.py write resume.docx "resumes/{CompanyName}/{job_id}/resume.docx" "resumes/{CompanyName}/{job_id}/mapping.json"
```

---

## Step 6 — Summary

Print a table:

| Rank | Company | Job Title | Saved Path |
|------|---------|-----------|------------|
| ...  | ...     | ...       | ...        |
