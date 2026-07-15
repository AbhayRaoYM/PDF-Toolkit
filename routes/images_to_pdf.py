import os
import time
from flask import Blueprint, render_template, request, send_file, jsonify
from modules.images_to_pdf import convert as _convert

images_to_pdf_bp = Blueprint("images_to_pdf", __name__)

ALLOWED_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif", ".webp"}


def get_session_folder():
    from app import get_session_folder as _gsf
    return _gsf()


@images_to_pdf_bp.route("/images-to-pdf")
def images_to_pdf_page():
    return render_template("images_to_pdf.html")


@images_to_pdf_bp.route("/images-to-pdf/upload", methods=["POST"])
def images_to_pdf_upload():
    folder = get_session_folder()
    img_dir = os.path.join(folder, "img_upload")
    os.makedirs(img_dir, exist_ok=True)
    saved = []
    for f in request.files.getlist("files"):
        ext = os.path.splitext(f.filename)[1].lower()
        if ext in ALLOWED_EXTS:
            dest = os.path.join(img_dir, f.filename)
            f.save(dest)
            saved.append(f.filename)
    return jsonify({"files": saved})


@images_to_pdf_bp.route("/images-to-pdf/convert", methods=["POST"])
def images_to_pdf_run():
    data = request.get_json()
    filenames = data.get("files", [])
    if not filenames:
        return jsonify({"error": "No images provided."}), 400

    folder = get_session_folder()
    img_dir = os.path.join(folder, "img_upload")
    image_paths = []
    for name in filenames:
        path = os.path.join(img_dir, name)
        if not os.path.isfile(path):
            return jsonify({"error": f"File not found: {name}"}), 400
        image_paths.append(path)

    out_name = f"images_combined_{int(time.time())}.pdf"
    out_path = os.path.join(folder, out_name)
    try:
        _convert(image_paths, out_path)
    except Exception as e:
        return jsonify({"error": f"Conversion failed: {str(e)}"}), 500

    return send_file(out_path, as_attachment=True, download_name=out_name)
