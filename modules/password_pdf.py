import os
from pypdf import PdfReader, PdfWriter


def protect(pdf_path: str, password: str, output_dir: str) -> str:
    """Encrypt a PDF with a user password. Returns output path."""
    reader = PdfReader(pdf_path)
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    writer.encrypt(password)
    base = os.path.splitext(os.path.basename(pdf_path))[0]
    out_path = os.path.join(output_dir, base + "_protected.pdf")
    with open(out_path, "wb") as f:
        writer.write(f)
    return out_path


def unlock(pdf_path: str, password: str, output_dir: str) -> str:
    """Remove password protection from a PDF. Returns output path."""
    reader = PdfReader(pdf_path)
    if reader.is_encrypted:
        if not reader.decrypt(password):
            raise ValueError("Incorrect password.")
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    base = os.path.splitext(os.path.basename(pdf_path))[0]
    # Strip _protected suffix if present
    base = base.replace("_protected", "")
    out_path = os.path.join(output_dir, base + "_unlocked.pdf")
    with open(out_path, "wb") as f:
        writer.write(f)
    return out_path
