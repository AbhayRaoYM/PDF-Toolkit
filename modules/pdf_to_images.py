import os
import fitz  # pymupdf


def convert(pdf_path: str, output_dir: str, fmt: str = "png", dpi: int = 150) -> list:
    """Render each PDF page as an image. Returns list of output file paths."""
    doc = fitz.open(pdf_path)
    base = os.path.splitext(os.path.basename(pdf_path))[0]
    mat = fitz.Matrix(dpi / 72, dpi / 72)
    output_files = []
    for i, page in enumerate(doc, start=1):
        pix = page.get_pixmap(matrix=mat)
        out_name = f"{base}_page{i}.{fmt}"
        out_path = os.path.join(output_dir, out_name)
        if fmt == "jpg":
            pix.save(out_path, "jpeg")
        else:
            pix.save(out_path)
        output_files.append(out_path)
    doc.close()
    return output_files
