import os
import json
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request


SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]
CREDENTIALS_FILE = "client_secrets.json"
TOKEN_FILE = "token.json"


if not os.path.exists(CREDENTIALS_FILE):
    creds = st.secrets["google_oauth"]
    credentials_data = {
        "installed": {
            "client_id": creds["client_id"],
            "project_id": creds["project_id"],
            "auth_uri": creds["auth_uri"],
            "token_uri": creds["token_uri"],
            "auth_provider_x509_cert_url": creds["auth_provider_x509_cert_url"],
            "client_secret": creds["client_secret"],
            "redirect_uris": creds["redirect_uris"]
        }
    }
    with open(CREDENTIALS_FILE, "w") as f:
        json.dump(credentials_data, f, indent=2)


def get_authenticated_service():
    """Mengembalikan kredensial yang telah diautentikasi."""
    credentials = None

    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as token:
            credentials_data = json.load(token)
            credentials = Credentials.from_authorized_user_info(credentials_data, SCOPES)

    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            credentials = flow.run_local_server(port=0)
            print("TOKEN:", credentials.token)
            print("SCOPES:", credentials.scopes)

        with open(TOKEN_FILE, "w") as token:
            token.write(credentials.to_json())

    return credentials
