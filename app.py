import os
import uuid
import shutil
from flask import Flask, render_template, session, request

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


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)
