import os
from pdf2docx import Converter


def convert(pdf_path: str, output_dir: str) -> str:
    """Convert a PDF file to .docx. Returns the path of the output .docx file."""
    base = os.path.splitext(os.path.basename(pdf_path))[0]
    docx_path = os.path.join(output_dir, base + ".docx")
    cv = Converter(pdf_path)
    cv.convert(docx_path, start=0, end=None)
    cv.close()
    return docx_path
