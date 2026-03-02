# Parse Resume

Read and display the structured content of the resume.

Run:
```bash
uv run python src/docx_utils.py read resume.docx
```

From the JSON output, extract and display:

**Summary / Objective**
(the candidate's profile or objective statement)

**Experience**
(each role: company, title, dates, bullet points)

**Skills**
(all listed technologies, tools, languages, frameworks)

**Education**
(degrees, institutions, graduation years)

If a section appears to be missing, say so clearly.
