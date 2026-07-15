import os
import io
import zipfile
from flask import Blueprint, render_template, request, send_file, jsonify
from modules.split_pdf import (
    get_page_count,
    split_by_ranges,
    split_all_pages,
    parse_range_string,
)

split_pdf_bp = Blueprint("split_pdf", __name__)


def get_session_folder():
    from app import get_session_folder as _gsf
    return _gsf()


@split_pdf_bp.route("/split-pdf")
def split_pdf_page():
    return render_template("split_pdf.html")


@split_pdf_bp.route("/split-pdf/upload", methods=["POST"])
def split_pdf_upload():
    if "file" not in request.files:
        return jsonify({"error": "No file provided."}), 400
    f = request.files["file"]
    if not f.filename.lower().endswith(".pdf"):
        return jsonify({"error": "Only PDF files are supported."}), 400

    folder = get_session_folder()
    dest = os.path.join(folder, f.filename)
    f.save(dest)
    count = get_page_count(dest)
    return jsonify({"filename": f.filename, "page_count": count})


@split_pdf_bp.route("/split-pdf/split", methods=["POST"])
def split_pdf_split():
    data = request.get_json()
    filename = data.get("filename")
    mode = data.get("mode", "all")
    range_str = data.get("ranges", "")

    folder = get_session_folder()
    pdf_path = os.path.join(folder, filename)
    if not os.path.isfile(pdf_path):
        return jsonify({"error": "File not found in session."}), 400

    output_dir = os.path.join(folder, "split_output")
    os.makedirs(output_dir, exist_ok=True)

    # Clear previous split output
    for old in os.listdir(output_dir):
        os.remove(os.path.join(output_dir, old))

    try:
        if mode == "range":
            ranges = parse_range_string(range_str)
            if not ranges:
                return jsonify({"error": "No valid ranges provided."}), 400
            page_count = get_page_count(pdf_path)
            for (s, e) in ranges:
                if s < 1 or e > page_count or s > e:
                    return jsonify({"error": f"Range {s}-{e} is out of bounds (1-{page_count})."}), 400
            output_files = split_by_ranges(pdf_path, ranges, output_dir)
        else:
            output_files = split_all_pages(pdf_path, output_dir)
    except Exception as ex:
        return jsonify({"error": f"Split failed: {str(ex)}"}), 500

    # Zip all output files in-memory
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for fpath in output_files:
            zf.write(fpath, os.path.basename(fpath))
    zip_buffer.seek(0)

    base = os.path.splitext(filename)[0]
    return send_file(zip_buffer, as_attachment=True,
                     download_name=f"{base}_split.zip",
                     mimetype="application/zip")
