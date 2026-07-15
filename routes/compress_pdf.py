import os
from flask import Blueprint, render_template, request, send_file, jsonify
from modules.compress_pdf import compress as _compress

compress_pdf_bp = Blueprint("compress_pdf", __name__)


def get_session_folder():
    from app import get_session_folder as _gsf
    return _gsf()


@compress_pdf_bp.route("/compress-pdf")
def compress_pdf_page():
    return render_template("compress_pdf.html")


@compress_pdf_bp.route("/compress-pdf/compress", methods=["POST"])
def compress_pdf_run():
    if "file" not in request.files:
        return jsonify({"error": "No file provided."}), 400
    f = request.files["file"]
    if not f.filename.lower().endswith(".pdf"):
        return jsonify({"error": "Only PDF files are supported."}), 400
    quality = request.form.get("quality", "medium").lower()
    if quality not in ("high", "medium", "low"):
        quality = "medium"

    folder = get_session_folder()
    pdf_path = os.path.join(folder, f.filename)
    f.save(pdf_path)
    try:
        out_path = _compress(pdf_path, quality, folder)
    except Exception as e:
        return jsonify({"error": f"Compression failed: {str(e)}"}), 500

    original_size = os.path.getsize(pdf_path)
    compressed_size = os.path.getsize(out_path)
    return send_file(out_path, as_attachment=True,
                     download_name=os.path.basename(out_path),
                     headers={
                         "X-Original-Size": str(original_size),
                         "X-Compressed-Size": str(compressed_size),
                     })
