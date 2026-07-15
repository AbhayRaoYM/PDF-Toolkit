import os
import io
import zipfile
from flask import Blueprint, render_template, request, send_file, jsonify
from modules.pdf_to_images import convert as _convert

pdf_to_images_bp = Blueprint("pdf_to_images", __name__)


def get_session_folder():
    from app import get_session_folder as _gsf
    return _gsf()


@pdf_to_images_bp.route("/pdf-to-images")
def pdf_to_images_page():
    return render_template("pdf_to_images.html")


@pdf_to_images_bp.route("/pdf-to-images/convert", methods=["POST"])
def pdf_to_images_run():
    if "file" not in request.files:
        return jsonify({"error": "No file provided."}), 400
    f = request.files["file"]
    if not f.filename.lower().endswith(".pdf"):
        return jsonify({"error": "Only PDF files are supported."}), 400

    fmt = request.form.get("format", "png").lower()
    if fmt not in ("png", "jpg"):
        fmt = "png"
    try:
        dpi = int(request.form.get("dpi", 150))
        dpi = max(72, min(dpi, 300))
    except ValueError:
        dpi = 150

    folder = get_session_folder()
    out_dir = os.path.join(folder, "images_output")
    os.makedirs(out_dir, exist_ok=True)
    for old in os.listdir(out_dir):
        os.remove(os.path.join(out_dir, old))

    pdf_path = os.path.join(folder, f.filename)
    f.save(pdf_path)

    try:
        image_files = _convert(pdf_path, out_dir, fmt=fmt, dpi=dpi)
    except Exception as e:
        return jsonify({"error": f"Conversion failed: {str(e)}"}), 500

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for fpath in image_files:
            zf.write(fpath, os.path.basename(fpath))
    zip_buffer.seek(0)
    base = os.path.splitext(f.filename)[0]
    return send_file(zip_buffer, as_attachment=True,
                     download_name=f"{base}_images.zip",
                     mimetype="application/zip")
