import os
import time
from flask import Blueprint, render_template, request, session, send_file, jsonify
from modules.merge_pdf import merge as merge_pdfs

merge_pdf_bp = Blueprint("merge_pdf", __name__)


def get_session_folder():
    from app import get_session_folder as _gsf
    return _gsf()


@merge_pdf_bp.route("/merge-pdf")
def merge_pdf_page():
    folder = get_session_folder()
    existing = [f for f in os.listdir(folder) if f.lower().endswith(".pdf")]
    return render_template("merge_pdf.html", existing_files=existing)


@merge_pdf_bp.route("/merge-pdf/upload", methods=["POST"])
def merge_pdf_upload():
    folder = get_session_folder()
    saved = []
    for f in request.files.getlist("files"):
        if f.filename.lower().endswith(".pdf"):
            dest = os.path.join(folder, f.filename)
            f.save(dest)
            saved.append(f.filename)
    return jsonify({"files": saved})


@merge_pdf_bp.route("/merge-pdf/merge", methods=["POST"])
def merge_pdf_merge():
    data = request.get_json()
    filenames = data.get("files", [])
    if len(filenames) < 2:
        return jsonify({"error": "Please provide at least 2 PDF files to merge."}), 400

    folder = get_session_folder()
    pdf_paths = []
    for name in filenames:
        path = os.path.join(folder, name)
        if not os.path.isfile(path):
            return jsonify({"error": f"File not found in session: {name}"}), 400
        pdf_paths.append(path)

    output_name = f"merged_{int(time.time())}.pdf"
    output_path = os.path.join(folder, output_name)

    try:
        merge_pdfs(pdf_paths, output_path)
    except Exception as e:
        return jsonify({"error": f"Merge failed: {str(e)}"}), 500

    return send_file(output_path, as_attachment=True, download_name=output_name)
