# Tailor Resume

Tailor the resume for a specific job. Pass the job_id as an argument: `/tailor-resume <job_id>`

## Step 1 — Load data

Run:
```bash
uv run python src/docx_utils.py read resume.docx
```

Read `jobs.json` and find the job with `job_id` matching `$ARGUMENTS`.

## Step 2 — Build sections JSON

Rewrite the professional summary and every professional experience role's bullets to better match the job description.

### Rules
- **Do NOT** add any skill, tool, or technology not already in the resume
- Only reword existing content to use keywords from the job description
- Do not modify contact info, company names, job titles, dates, education, or section headings
- Formatting (bold/italic/font/size) is preserved automatically by the writer

### What to rewrite

1. **Professional Summary** — rewrite to lead with the job's most important keywords and requirements.

2. **Professional Experience bullets** — for each role, produce a revised, ordered bullet list:
   - You MAY reorder bullets (put the most relevant ones first)
   - You MAY remove bullets that are irrelevant to this job
   - You MAY add new bullets, but only by synthesizing/expanding content already implied by the resume (no fabrication of skills or tools)
   - Prioritize action verbs and metrics that match the job description

### Output format

Build a `sections.json`:

```json
{
  "sections": [
    {
      "type": "text_replace",
      "original": "<exact original summary paragraph text from parsed output>",
      "replacement": "<rewritten summary>"
    },
    {
      "type": "role_bullets",
      "original_bullets": [
        "<exact text of bullet 1 from parsed output>",
        "<exact text of bullet 2 from parsed output>"
      ],
      "bullets": [
        "<most relevant bullet — may be new, reworded, or reordered>",
        "<second bullet>",
        "..."
      ]
    }
  ]
}
```

- Include a `role_bullets` entry for **every role** in the experience section.
- `original_bullets` must contain the **exact paragraph text** from the parsed output for each existing bullet under that role — this is how the writer locates them in the document.
- `bullets` is the **complete new list** for that role; it fully replaces the originals. Fewer items = bullets removed; more items = bullets added.

## Step 3 — Save sections JSON

Sanitize the company name (spaces → `_`, remove special chars).

Write the sections to:
```
resumes/{CompanyName}/{job_id}/sections.json
```

## Step 4 — Apply and save

Run:
```bash
uv run python src/docx_utils.py write-sections resume.docx "resumes/{CompanyName}/{job_id}/resume.docx" "resumes/{CompanyName}/{job_id}/sections.json"
```

Confirm the saved path.
