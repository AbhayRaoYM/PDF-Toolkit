import os
from flask import Blueprint, render_template, request, session, send_file, jsonify
from modules.word_to_pdf import convert as _do_convert

word_to_pdf_bp = Blueprint("word_to_pdf", __name__)


def get_session_folder():
    from app import get_session_folder as _gsf
    return _gsf()


@word_to_pdf_bp.route("/word-to-pdf")
def word_to_pdf_page():
    return render_template("word_to_pdf.html")


@word_to_pdf_bp.route("/word-to-pdf/convert", methods=["POST"])
def word_to_pdf_convert():
    if "file" not in request.files:
        return jsonify({"error": "No file provided."}), 400
    f = request.files["file"]
    if not f.filename.lower().endswith(".docx"):
        return jsonify({"error": "Only .docx files are supported."}), 400

    folder = get_session_folder()
    docx_path = os.path.join(folder, f.filename)
    f.save(docx_path)

    try:
        pdf_path = _do_convert(docx_path, folder)
    except Exception as e:
        return jsonify({"error": f"Conversion failed: {str(e)}"}), 500

    return send_file(pdf_path, as_attachment=True,
                     download_name=os.path.basename(pdf_path))
