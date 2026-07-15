import os
from flask import Blueprint, render_template, request, send_file, jsonify
from modules.pdf_to_word import convert as _do_convert

pdf_to_word_bp = Blueprint("pdf_to_word", __name__)


def get_session_folder():
    from app import get_session_folder as _gsf
    return _gsf()


@pdf_to_word_bp.route("/pdf-to-word")
def pdf_to_word_page():
    return render_template("pdf_to_word.html")


@pdf_to_word_bp.route("/pdf-to-word/convert", methods=["POST"])
def pdf_to_word_convert():
    if "file" not in request.files:
        return jsonify({"error": "No file provided."}), 400
    f = request.files["file"]
    if not f.filename.lower().endswith(".pdf"):
        return jsonify({"error": "Only PDF files are supported."}), 400

    folder = get_session_folder()
    pdf_path = os.path.join(folder, f.filename)
    f.save(pdf_path)

    try:
        docx_path = _do_convert(pdf_path, folder)
    except Exception as e:
        return jsonify({"error": f"Conversion failed: {str(e)}"}), 500

    return send_file(docx_path, as_attachment=True,
                     download_name=os.path.basename(docx_path))
