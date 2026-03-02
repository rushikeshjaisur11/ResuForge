# Tailor Resume

Tailor the resume for a specific job. Pass the job_id as an argument: `/tailor-resume <job_id>`

## Step 1 — Load data

Run:
```bash
uv run python src/docx_utils.py read resume.docx
```

Read `jobs.json` and find the job with `job_id` matching `$ARGUMENTS`.

## Step 2 — Build rewrite mapping

Rewrite the resume's bullet points and sentences to better match that job's description:
- **Do NOT** add any skill, tool, or technology not already in the resume
- Only reword existing content to use keywords from the job description
- Keep identical bullet count per role
- Do not modify contact info, company names, education dates, or section headings

Build a JSON mapping: `{"original line": "rewritten line"}` — only changed lines.

## Step 3 — Save mapping

Sanitize the company name (spaces → `_`, remove special chars).

Write the mapping to:
```
resumes/{CompanyName}/{job_id}/mapping.json
```

## Step 4 — Apply and save

Run:
```bash
uv run python src/docx_utils.py write resume.docx "resumes/{CompanyName}/{job_id}/resume.docx" "resumes/{CompanyName}/{job_id}/mapping.json"
```

Confirm the saved path.
