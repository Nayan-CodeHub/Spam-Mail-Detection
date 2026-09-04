import base64
import os
import re
from html import unescape

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLIENT_SECRETS_PATH = os.path.join(BASE_DIR, "credentials.json")
TOKEN_PATH = os.path.join(BASE_DIR, "models", "gmail_token.json")
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def create_oauth_flow(redirect_uri, state=None):
    if not os.path.exists(CLIENT_SECRETS_PATH):
        raise FileNotFoundError("credentials.json is missing")
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_PATH,
        scopes=SCOPES,
        state=state,
    )
    flow.redirect_uri = redirect_uri
    return flow


def save_credentials(credentials):
    os.makedirs(os.path.dirname(TOKEN_PATH), exist_ok=True)
    with open(TOKEN_PATH, "w", encoding="utf-8") as token_file:
        token_file.write(credentials.to_json())


def load_credentials():
    if not os.path.exists(TOKEN_PATH):
        return None
    credentials = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    if credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())
        save_credentials(credentials)
    return credentials if credentials.valid else None


def _decode_body(data):
    if not data:
        return ""
    decoded = base64.urlsafe_b64decode(data + "=" * (-len(data) % 4))
    return decoded.decode("utf-8", errors="replace")


def _extract_text(payload):
    body = payload.get("body", {})
    if body.get("data"):
        return _decode_body(body["data"])
    for part in payload.get("parts", []):
        if part.get("mimeType") == "text/plain":
            text = _extract_text(part)
            if text:
                return text
    for part in payload.get("parts", []):
        text = _extract_text(part)
        if text:
            return text
    return ""


def _clean_text(text):
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", unescape(text)).strip()


def fetch_latest_messages(limit=10):
    credentials = load_credentials()
    if credentials is None:
        raise RuntimeError("Gmail is not connected")

    service = build("gmail", "v1", credentials=credentials, cache_discovery=False)
    response = service.users().messages().list(
        userId="me",
        labelIds=["INBOX"],
        maxResults=limit,
    ).execute()

    messages = []
    for item in response.get("messages", []):
        raw_message = service.users().messages().get(
            userId="me",
            id=item["id"],
            format="full",
        ).execute()
        headers = {
            header["name"].lower(): header["value"]
            for header in raw_message.get("payload", {}).get("headers", [])
        }
        body = _clean_text(_extract_text(raw_message.get("payload", {})))
        messages.append({
            "id": raw_message["id"],
            "subject": headers.get("subject", "(No subject)"),
            "sender": headers.get("from", "Unknown sender"),
            "date": headers.get("date", ""),
            "body": body or raw_message.get("snippet", ""),
        })
    return messages
