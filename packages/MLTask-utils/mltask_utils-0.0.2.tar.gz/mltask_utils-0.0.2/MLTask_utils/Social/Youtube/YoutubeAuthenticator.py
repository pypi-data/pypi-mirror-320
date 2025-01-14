import os
import google_auth_oauthlib.flow
from datetime import datetime
from pprint import pprint

# DTask-Dev KEYS
SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtubepartner",
    "https://www.googleapis.com/auth/youtube",
    "https://www.googleapis.com/auth/userinfo.email",
    "openid",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/youtube.force-ssl",
]


def get_creds(user_oauth_token, user_oauth_refresh_token):
    google_client_id = os.environ.get("GOOGLE_CLIENT_ID")
    google_client_secret = os.environ.get("GOOGLE_CLIENT_SECRET")

    cred_json = {
        "token": user_oauth_token,
        "refresh_token": user_oauth_refresh_token,
        "token_uri": "https://oauth2.googleapis.com/token",
        "client_id": google_client_id,
        "client_secret": google_client_secret,
        "scopes": SCOPES,
        "expiry": "2024-01-09T03:06:03.230066Z",
    }

    # cred_json = json.dumps(cred_json)
    # credentials = google.oauth2.credentials.Credentials(
    #     json.loads(cred_json))

    expiry_datetime = datetime.strptime(cred_json["expiry"], "%Y-%m-%dT%H:%M:%S.%fZ")
    cred_json["expiry"] = expiry_datetime
    return cred_json


CLIENT_SECRETS_CONFIG = {
    "web": {
        "client_id": os.environ.get("GOOGLE_CLIENT_ID"),
        "project_id": os.environ.get("GOOGLE_CLIENT_PROJECT_ID"),
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_secret": os.environ.get("GOOGLE_CLIENT_SECRET"),
        "redirect_uris": [os.environ.get("GOOGLE_REDIRECT_URIS")],
        "javascript_origins": [os.environ.get("GOOGLE_JAVASCRIPT_ORIGINS")],
    }
}


def authorize():
    flow = google_auth_oauthlib.flow.Flow.from_client_config(
        CLIENT_SECRETS_CONFIG, SCOPES
    )

    flow.redirect_uri = os.environ.get("GOOGLE_REDIRECT_URIS")

    authorization_url, state = flow.authorization_url(
        # Enable offline access so that you can refresh an access token without
        # re-prompting the user for permission. Recommended for web server apps.
        access_type="offline",
        prompt="consent",
        # Enable incremental authorization. Recommended as a best practice.
        # include_granted_scopes='true'
    )

    return authorization_url

    # return flask.redirect(authorization_url)


def oauth2callback(authorization_response):
    flow = google_auth_oauthlib.flow.Flow.from_client_config(
        CLIENT_SECRETS_CONFIG, SCOPES
    )  # , state=state)

    flow.redirect_uri = os.environ["GOOGLE_REDIRECT_URIS"]
    flow.fetch_token(authorization_response=authorization_response)

    token = flow.credentials.token
    refresh_token = flow.credentials.refresh_token
    # token_uri = flow.credentials.token_uri
    # expiry = flow.credentials.expired

    return (token, refresh_token)
