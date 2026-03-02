"""
CLI utility for reading and writing .docx files.
Called by Claude skills — no AI logic here, purely mechanical.

Usage:
  python src/docx_utils.py read <resume.docx>
      Prints JSON: {"full_text": "...", "paragraphs": [{"index": int, "text": str, "style": str}]}

  python src/docx_utils.py write <src.docx> <out.docx> <mapping.json>
      Applies text mapping to src.docx and saves to out.docx.
      mapping.json: {"original line": "rewritten line", ...}
"""

import json
import os
import sys

from docx import Document


def cmd_read(path: str) -> None:
    doc = Document(path)
    paragraphs = []
    for i, para in enumerate(doc.paragraphs):
        if para.text.strip():
            paragraphs.append({
                "index": i,
                "text": para.text,
                "style": para.style.name,
            })
    full_text = "\n".join(p["text"] for p in paragraphs)
    print(json.dumps({"full_text": full_text, "paragraphs": paragraphs}, ensure_ascii=False, indent=2))


def cmd_write(src_path: str, out_path: str, mapping_path: str) -> None:
    with open(mapping_path, encoding="utf-8") as f:
        mapping = json.load(f)

    doc = Document(src_path)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    for para in doc.paragraphs:
        if para.text in mapping:
            _replace_para(para, mapping[para.text])
        else:
            for run in para.runs:
                if run.text and run.text in mapping:
                    run.text = mapping[run.text]

    doc.save(out_path)
    print(f"Saved: {out_path}")


def _replace_para(para, new_text: str) -> None:
    """Put new_text in the first run, clear the rest (preserves formatting)."""
    if not para.runs:
        return
    para.runs[0].text = new_text
    for run in para.runs[1:]:
        run.text = ""


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1]
    if command == "read":
        cmd_read(sys.argv[2])
    elif command == "write":
        if len(sys.argv) < 5:
            print("Usage: python src/docx_utils.py write <src.docx> <out.docx> <mapping.json>")
            sys.exit(1)
        cmd_write(sys.argv[2], sys.argv[3], sys.argv[4])
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
