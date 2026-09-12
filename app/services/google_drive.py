"""Optional Google Drive sync using a user's OAuth client secret.

Place a Google OAuth desktop client file at data/google_client_secret.json and
complete the browser consent flow from the Settings panel. Tokens are stored
locally in data/google_token.json and are never committed by the app.
"""

from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
CLIENT_SECRET_PATH = DATA_DIR / "google_client_secret.json"
TOKEN_PATH = DATA_DIR / "google_token.json"
SCOPES = ["https://www.googleapis.com/auth/drive.file"]


def integration_status():
    return {
        "configured": CLIENT_SECRET_PATH.exists(),
        "connected": TOKEN_PATH.exists(),
        "client_secret": str(CLIENT_SECRET_PATH),
        "token_path": str(TOKEN_PATH),
    }


def authorization_url():
    if not CLIENT_SECRET_PATH.exists():
        raise RuntimeError("Add data/google_client_secret.json from a Google Cloud OAuth Desktop client first.")
    from google_auth_oauthlib.flow import InstalledAppFlow

    flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRET_PATH), SCOPES)
    credentials = flow.run_local_server(host="127.0.0.1", port=0, open_browser=False, access_type="offline", prompt="consent")
    TOKEN_PATH.write_text(credentials.to_json(), encoding="utf-8")
    return integration_status()


def upload_text(filename, content, folder_id=None):
    if not TOKEN_PATH.exists():
        raise RuntimeError("Connect Google Drive from Settings before uploading.")
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaInMemoryUpload

    credentials = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
    service = build("drive", "v3", credentials=credentials, cache_discovery=False)
    metadata = {"name": filename, "mimeType": "text/plain"}
    if folder_id:
        metadata["parents"] = [folder_id]
    result = service.files().create(body=metadata, media_body=MediaInMemoryUpload(content.encode("utf-8"), mimetype="text/plain"), fields="id,name,webViewLink").execute()
    return result
