import os
import sys
import shutil
import subprocess


def _find_soffice():
    """Find the LibreOffice binary — tries common names and paths."""
    for name in ("soffice", "libreoffice"):
        path = shutil.which(name)
        if path:
            return path
    # Fallback: known Debian/Ubuntu install path
    fallback = "/usr/lib/libreoffice/program/soffice"
    if os.path.isfile(fallback):
        return fallback
    return None


def convert(docx_path: str, output_dir: str) -> str:
    """Convert a .docx file to PDF. Returns the path of the output PDF."""
    base = os.path.splitext(os.path.basename(docx_path))[0]
    pdf_path = os.path.join(output_dir, base + ".pdf")

    if sys.platform == "win32" or sys.platform == "darwin":
        # Windows / macOS — use docx2pdf (requires Microsoft Word)
        from docx2pdf import convert as _convert
        _convert(docx_path, pdf_path)
    else:
        # Linux — use LibreOffice headless
        soffice = _find_soffice()
        if not soffice:
            raise RuntimeError(
                "LibreOffice is not installed on this server. "
                "Cannot convert Word to PDF."
            )
        result = subprocess.run(
            [
                soffice, "--headless", "--convert-to", "pdf",
                "--outdir", output_dir,
                docx_path,
            ],
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode != 0:
            raise RuntimeError(result.stderr or result.stdout)

    return pdf_path
