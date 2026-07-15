import os
from pypdf import PdfReader


def extract_text(pdf_path: str, output_dir: str) -> str:
    """Extract all text from a PDF and write to a .txt file."""
    reader = PdfReader(pdf_path)
    lines = []
    for i, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        lines.append(f"--- Page {i} ---\n{text}\n")
    base = os.path.splitext(os.path.basename(pdf_path))[0]
    txt_path = os.path.join(output_dir, base + ".txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return txt_path
