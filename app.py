import os
import uuid
import shutil
import subprocess
from flask import Flask, render_template, session, request, jsonify

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")

UPLOAD_BASE = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_BASE, exist_ok=True)


def get_session_folder():
    """Return (and create) the upload folder scoped to this browser session."""
    if "session_id" not in session:
        session["session_id"] = uuid.uuid4().hex
    folder = os.path.join(UPLOAD_BASE, session["session_id"])
    os.makedirs(folder, exist_ok=True)
    return folder


@app.before_request
def ensure_session_folder():
    # Only create the folder for non-static requests
    if not request.path.startswith("/static"):
        get_session_folder()


@app.route("/clear-session", methods=["POST"])
def clear_session():
    folder = os.path.join(UPLOAD_BASE, session.get("session_id", ""))
    if os.path.isdir(folder):
        shutil.rmtree(folder)
    session.clear()
    return {"status": "cleared"}, 200


# ── Module routes (imported below to avoid circular imports) ──────────────────
from routes.word_to_pdf import word_to_pdf_bp   # noqa: E402
from routes.merge_pdf import merge_pdf_bp         # noqa: E402
from routes.split_pdf import split_pdf_bp         # noqa: E402
from routes.pdf_to_word import pdf_to_word_bp     # noqa: E402

app.register_blueprint(word_to_pdf_bp)
app.register_blueprint(merge_pdf_bp)
app.register_blueprint(split_pdf_bp)
app.register_blueprint(pdf_to_word_bp)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/debug/soffice")
def debug_soffice():
    """Temporary debug route — remove after confirming soffice path."""
    import shutil as sh
    results = {}
    for name in ("soffice", "libreoffice"):
        results[name] = sh.which(name)
    known = [
        "/usr/bin/soffice",
        "/usr/lib/libreoffice/program/soffice",
        "/usr/local/bin/soffice",
        "/opt/libreoffice/program/soffice",
    ]
    results["known_paths"] = {p: os.path.isfile(p) for p in known}
    try:
        find = subprocess.run(["find", "/usr", "-name", "soffice", "-type", "f"],
                              capture_output=True, text=True, timeout=10)
        results["find_output"] = find.stdout.strip()
    except Exception as e:
        results["find_error"] = str(e)
    results["PATH"] = os.environ.get("PATH", "")
    return jsonify(results)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)
