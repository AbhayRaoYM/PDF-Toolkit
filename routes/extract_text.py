import os
from flask import Blueprint, render_template, request, send_file, jsonify
from modules.extract_text import extract_text as _extract

extract_text_bp = Blueprint("extract_text", __name__)


def get_session_folder():
    from app import get_session_folder as _gsf
    return _gsf()


@extract_text_bp.route("/extract-text")
def extract_text_page():
    return render_template("extract_text.html")


@extract_text_bp.route("/extract-text/extract", methods=["POST"])
def extract_text_run():
    if "file" not in request.files:
        return jsonify({"error": "No file provided."}), 400
    f = request.files["file"]
    if not f.filename.lower().endswith(".pdf"):
        return jsonify({"error": "Only PDF files are supported."}), 400
    folder = get_session_folder()
    pdf_path = os.path.join(folder, f.filename)
    f.save(pdf_path)
    try:
        txt_path = _extract(pdf_path, folder)
    except Exception as e:
        return jsonify({"error": f"Extraction failed: {str(e)}"}), 500
    return send_file(txt_path, as_attachment=True,
                     download_name=os.path.basename(txt_path))
