import base64
import hashlib
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
TOKEN_DIR = os.path.join(BASE_DIR, "models", "gmail_tokens")
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/userinfo.email",
    "openid",
]


def _client_secrets_path():
    configured_path = os.environ.get("GOOGLE_CREDENTIALS_PATH")
    return configured_path or CLIENT_SECRETS_PATH


def _token_path(user_id):
    token_name = hashlib.sha256(user_id.encode("utf-8")).hexdigest()
    return os.path.join(TOKEN_DIR, f"{token_name}.json")


def create_oauth_flow(redirect_uri, state=None):
    client_secrets_path = _client_secrets_path()
    if not os.path.exists(client_secrets_path):
        raise FileNotFoundError("Google OAuth credentials are missing")
    if redirect_uri.startswith("http://127.0.0.1:"):
        os.environ.setdefault("OAUTHLIB_INSECURE_TRANSPORT", "1")
    flow = Flow.from_client_secrets_file(
        client_secrets_path,
        scopes=SCOPES,
        state=state,
    )
    flow.redirect_uri = redirect_uri
    return flow


def save_credentials(credentials, user_id):
    token_path = _token_path(user_id)
    os.makedirs(os.path.dirname(token_path), exist_ok=True)
    with open(token_path, "w", encoding="utf-8") as token_file:
        token_file.write(credentials.to_json())


def clear_credentials(user_id):
    if user_id:
        token_path = _token_path(user_id)
        if os.path.exists(token_path):
            os.remove(token_path)
    if os.path.exists(TOKEN_PATH):
        os.remove(TOKEN_PATH)


def load_credentials(user_id):
    if not user_id:
        return None
    token_path = _token_path(user_id)
    if not os.path.exists(token_path):
        return None
    credentials = Credentials.from_authorized_user_file(token_path, SCOPES)
    if credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())
        save_credentials(credentials, user_id)
    return credentials if credentials.valid else None


def get_user_identity(credentials):
    service = build("oauth2", "v2", credentials=credentials, cache_discovery=False)
    user_info = service.userinfo().get().execute()
    return user_info["id"], user_info.get("email", "")


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


def fetch_latest_messages(user_id, limit=10):
    credentials = load_credentials(user_id)
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
