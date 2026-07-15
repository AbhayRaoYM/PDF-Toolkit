import os
from flask import (Blueprint, redirect, request, session,
                   url_for, jsonify, render_template)
from modules.gmail_send import SCOPES, send_email

gmail_bp = Blueprint("gmail", __name__)

CLIENT_SECRET_FILE = os.path.join(os.path.dirname(__file__), "..", "client_secret.json")

# Allow HTTP on localhost during development
os.environ.setdefault("OAUTHLIB_INSECURE_TRANSPORT", "1")


def _has_client_secret():
    return os.path.isfile(CLIENT_SECRET_FILE)


def _flow():
    from google_auth_oauthlib.flow import Flow
    return Flow.from_client_secrets_file(
        CLIENT_SECRET_FILE,
        scopes=SCOPES,
        redirect_uri=request.host_url.rstrip("/") + "/gmail/callback",
    )


# ── OAuth ──────────────────────────────────────────────────────────────────────

@gmail_bp.route("/gmail/authorize")
def gmail_authorize():
    """Start Google OAuth flow."""
    if not _has_client_secret():
        return jsonify({"error": "Gmail not configured on this server."}), 503

    session["gmail_next_file"] = request.args.get("file", "")
    session["gmail_next_to"]   = request.args.get("to", "")

    flow = _flow()
    auth_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
    )
    session["gmail_oauth_state"] = state
    return redirect(auth_url)


@gmail_bp.route("/gmail/callback")
def gmail_callback():
    """Handle OAuth redirect from Google — store credentials in session."""
    flow = _flow()
    flow.fetch_token(authorization_response=request.url)
    creds = flow.credentials
    session["gmail_credentials"] = {
        "token":         creds.token,
        "refresh_token": creds.refresh_token,
        "token_uri":     creds.token_uri,
        "client_id":     creds.client_id,
        "client_secret": creds.client_secret,
        "scopes":        list(creds.scopes),
    }
    return redirect(url_for(
        "gmail.gmail_send_page",
        file=session.pop("gmail_next_file", ""),
        to=session.pop("gmail_next_to", ""),
    ))


# ── Send page ──────────────────────────────────────────────────────────────────

@gmail_bp.route("/gmail/send", methods=["GET"])
def gmail_send_page():
    filename   = request.args.get("file", "")
    prefill_to = request.args.get("to", "")
    authed     = "gmail_credentials" in session
    configured = _has_client_secret()
    return render_template("gmail_send.html",
                           filename=filename,
                           prefill_to=prefill_to,
                           authed=authed,
                           configured=configured)


@gmail_bp.route("/gmail/send", methods=["POST"])
def gmail_send_run():
    """Send a session file via Gmail."""
    data     = request.get_json()
    filename = (data.get("filename") or "").strip()
    to       = (data.get("to") or "").strip()
    subject  = (data.get("subject") or "").strip() or f"Your file: {filename}"
    body     = (data.get("body") or "").strip() or "Please find the attached file from PDF Toolkit."

    if not filename or not to:
        return jsonify({"error": "Recipient email and filename are required."}), 400

    if "gmail_credentials" not in session:
        return jsonify({"error": "Not authenticated with Gmail.", "auth_required": True}), 401

    from app import get_session_folder
    file_path = os.path.join(get_session_folder(), filename)
    if not os.path.isfile(file_path):
        return jsonify({"error": f"File '{filename}' not found in your session."}), 400

    try:
        msg_id = send_email(session["gmail_credentials"], to, subject, body, file_path)
        return jsonify({"success": True, "message_id": msg_id})
    except Exception as e:
        return jsonify({"error": f"Send failed: {str(e)}"}), 500


@gmail_bp.route("/gmail/logout", methods=["POST"])
def gmail_logout():
    """Remove Gmail credentials from session."""
    session.pop("gmail_credentials", None)
    return jsonify({"status": "logged out"})


@gmail_bp.route("/gmail/status")
def gmail_status():
    """Return auth status — polled by the send widget."""
    return jsonify({
        "authed":     "gmail_credentials" in session,
        "configured": _has_client_secret(),
    })
