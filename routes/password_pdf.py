import os
from flask import Blueprint, render_template, request, send_file, jsonify
from modules.password_pdf import protect as _protect, unlock as _unlock

password_pdf_bp = Blueprint("password_pdf", __name__)


def get_session_folder():
    from app import get_session_folder as _gsf
    return _gsf()


@password_pdf_bp.route("/password-pdf")
def password_pdf_page():
    return render_template("password_pdf.html")


@password_pdf_bp.route("/password-pdf/protect", methods=["POST"])
def password_pdf_protect():
    if "file" not in request.files:
        return jsonify({"error": "No file provided."}), 400
    f = request.files["file"]
    if not f.filename.lower().endswith(".pdf"):
        return jsonify({"error": "Only PDF files are supported."}), 400
    password = request.form.get("password", "").strip()
    if not password:
        return jsonify({"error": "Password cannot be empty."}), 400

    folder = get_session_folder()
    pdf_path = os.path.join(folder, f.filename)
    f.save(pdf_path)
    try:
        out_path = _protect(pdf_path, password, folder)
    except Exception as e:
        return jsonify({"error": f"Failed to protect: {str(e)}"}), 500
    return send_file(out_path, as_attachment=True,
                     download_name=os.path.basename(out_path))


@password_pdf_bp.route("/password-pdf/unlock", methods=["POST"])
def password_pdf_unlock():
    if "file" not in request.files:
        return jsonify({"error": "No file provided."}), 400
    f = request.files["file"]
    if not f.filename.lower().endswith(".pdf"):
        return jsonify({"error": "Only PDF files are supported."}), 400
    password = request.form.get("password", "").strip()
    if not password:
        return jsonify({"error": "Password cannot be empty."}), 400

    folder = get_session_folder()
    pdf_path = os.path.join(folder, f.filename)
    f.save(pdf_path)
    try:
        out_path = _unlock(pdf_path, password, folder)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to unlock: {str(e)}"}), 500
    return send_file(out_path, as_attachment=True,
                     download_name=os.path.basename(out_path))
