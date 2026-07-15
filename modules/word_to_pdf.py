import os
from docx2pdf import convert as _convert


def convert(docx_path: str, output_dir: str) -> str:
    """Convert a .docx file to PDF. Returns the path of the output PDF."""
    base = os.path.splitext(os.path.basename(docx_path))[0]
    pdf_path = os.path.join(output_dir, base + ".pdf")
    _convert(docx_path, pdf_path)
    return pdf_path
