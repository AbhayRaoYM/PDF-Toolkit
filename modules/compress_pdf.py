import os
import fitz  # pymupdf


# Quality presets: (image_dpi, jpeg_quality)
QUALITY_PRESETS = {
    "high":   (150, 85),
    "medium": (96,  65),
    "low":    (72,  45),
}


def compress(pdf_path: str, quality: str, output_dir: str) -> str:
    """
    Compress a PDF by re-rendering pages at a lower DPI and JPEG quality.
    quality: 'high' | 'medium' | 'low'
    Returns the output file path.
    """
    dpi, jpeg_quality = QUALITY_PRESETS.get(quality, QUALITY_PRESETS["medium"])
    doc = fitz.open(pdf_path)
    out_doc = fitz.open()

    for page in doc:
        mat = fitz.Matrix(dpi / 72, dpi / 72)
        pix = page.get_pixmap(matrix=mat)
        # Re-encode as JPEG at target quality
        jpeg_bytes = pix.tobytes("jpeg", jpg_quality=jpeg_quality)
        img_pdf = fitz.open("pdf", fitz.open("jpg", jpeg_bytes).convert_to_pdf())
        out_doc.insert_pdf(img_pdf)

    base = os.path.splitext(os.path.basename(pdf_path))[0]
    out_path = os.path.join(output_dir, f"{base}_compressed_{quality}.pdf")
    out_doc.save(out_path, garbage=4, deflate=True)
    doc.close()
    out_doc.close()
    return out_path
