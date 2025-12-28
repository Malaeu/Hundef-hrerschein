#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path
from urllib.request import urlopen
from io import BytesIO

PDF_URL = (
    "https://www.tieraerztekammer-nordrhein.de/wp-content/uploads/2024/11/"
    "Sachkundefragen-Loesungen-neu-ab-01.01.2025.pdf"
)


def _load_questions_data(html_path: Path) -> dict[int, list[str]]:
    html = html_path.read_text(encoding="utf-8")
    start = html.find("const QUESTIONS_DATA")
    if start == -1:
        raise RuntimeError("QUESTIONS_DATA not found in index.html")
    brace_start = html.find("{", start)
    if brace_start == -1:
        raise RuntimeError("QUESTIONS_DATA JSON start not found")
    level = 0
    end = None
    for i in range(brace_start, len(html)):
        ch = html[i]
        if ch == "{":
            level += 1
        elif ch == "}":
            level -= 1
            if level == 0:
                end = i
                break
    if end is None:
        raise RuntimeError("QUESTIONS_DATA JSON end not found")
    data = json.loads(html[brace_start : end + 1])
    return {int(k): v.get("correct", []) for k, v in data.items()}


def _extract_pdf_solutions(pdf_bytes: bytes) -> dict[int, list[str]]:
    try:
        from pypdf import PdfReader
    except Exception as exc:
        raise RuntimeError("pypdf is required. Install it in a venv: pip install pypdf") from exc

    reader = PdfReader(BytesIO(pdf_bytes))
    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    lines = [ln.strip() for ln in text.splitlines()]

    solutions: dict[int, list[str]] = {}
    for ln in lines:
        m = re.match(r"^\s*(\d{1,3})\s+(.*)$", ln)
        if not m:
            continue
        q = int(m.group(1))
        letters = re.findall(r"[A-D]", m.group(2))
        if letters:
            solutions[q] = letters
    return solutions


def main() -> int:
    repo = Path(__file__).resolve().parents[1]
    html_path = repo / "index.html"
    reports_dir = repo / "reports"
    report_path = reports_dir / "answers_report.csv"
    local_pdf = reports_dir / "loesungen_2025.pdf"

    if not html_path.exists():
        print("index.html not found", file=sys.stderr)
        return 1

    if local_pdf.exists():
        pdf_bytes = local_pdf.read_bytes()
    else:
        try:
            pdf_bytes = urlopen(PDF_URL).read()
        except Exception as exc:
            print(f"Failed to download PDF: {exc}", file=sys.stderr)
            return 1

    pdf_solutions = _extract_pdf_solutions(pdf_bytes)
    local_solutions = _load_questions_data(html_path)

    all_q = sorted(set(pdf_solutions) | set(local_solutions))

    mismatches = []
    for q in all_q:
        a = sorted(local_solutions.get(q, []))
        b = sorted(pdf_solutions.get(q, []))
        if a != b:
            mismatches.append((q, a, b))

    report_lines = ["question,pdf_answers,local_answers,match"]
    for q in all_q:
        pdf_ans = "".join(sorted(pdf_solutions.get(q, [])))
        local_ans = "".join(sorted(local_solutions.get(q, [])))
        match = "yes" if pdf_ans == local_ans and pdf_ans != "" else "no"
        report_lines.append(f"{q},{pdf_ans},{local_ans},{match}")

    report_path.write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    print(f"Report written: {report_path}")
    if mismatches:
        print(f"Mismatches: {len(mismatches)}")
        for q, a, b in mismatches[:20]:
            print(f"- {q}: local={a} pdf={b}")
        return 2

    print("All answers match.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
