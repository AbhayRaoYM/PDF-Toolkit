import os
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]


def build_service(credentials_dict: dict):
    """Build a Gmail API service from credentials stored in Flask session."""
    creds = Credentials(
        token=credentials_dict["token"],
        refresh_token=credentials_dict.get("refresh_token"),
        token_uri=credentials_dict["token_uri"],
        client_id=credentials_dict["client_id"],
        client_secret=credentials_dict["client_secret"],
        scopes=credentials_dict["scopes"],
    )
    return build("gmail", "v1", credentials=creds)


def send_email(credentials_dict: dict, to: str, subject: str,
               body: str, attachment_path: str) -> str:
    """
    Send an email with a single file attachment via Gmail API.
    Returns the sent message ID.
    """
    service = build_service(credentials_dict)

    msg = MIMEMultipart()
    msg["to"] = to
    msg["subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    filename = os.path.basename(attachment_path)
    with open(attachment_path, "rb") as f:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(f.read())
    encoders.encode_base64(part)
    part.add_header("Content-Disposition", f'attachment; filename="{filename}"')
    msg.attach(part)

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    result = service.users().messages().send(
        userId="me", body={"raw": raw}
    ).execute()
    return result.get("id", "")
