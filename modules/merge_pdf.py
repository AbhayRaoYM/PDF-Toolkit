import os
from pypdf import PdfWriter, PdfReader


def merge(pdf_paths: list, output_path: str) -> str:
    """Merge a list of PDF files into a single PDF. Returns the output path."""
    writer = PdfWriter()
    for path in pdf_paths:
        reader = PdfReader(path)
        for page in reader.pages:
            writer.add_page(page)
    with open(output_path, "wb") as f:
        writer.write(f)
    return output_path
