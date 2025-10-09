import json
import os

import google.auth.transport.requests
import requests
from django.conf import settings
from google.oauth2 import service_account

SCOPES = ["https://www.googleapis.com/auth/firebase.messaging"]

# Load credentials once
# credentials = service_account.Credentials.from_service_account_file(
#     settings.SERVICE_ACCOUNT_FILE, scopes=SCOPES
# )
# 

# Load credentials once using the path from .env
# credentials = service_account.Credentials.from_service_account_file(
#     os.getenv("GOOGLE_APPLICATION_CREDENTIALS"), scopes=SCOPES
# )


credentials = service_account.Credentials.from_service_account_info(
    os.getenv("GOOGLE_APPLICATION_CREDENTIALS"), scopes=SCOPES
)

def send_fcm_notification(device_token, role, title, body):
    """Send push notification via Firebase Cloud Messaging"""
    try:
        request = google.auth.transport.requests.Request()
        credentials.refresh(request)
        access_token = credentials.token

        url = f"https://fcm.googleapis.com/v1/projects/{settings.FIREBASE_PROJECT_ID}/messages:send"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json; UTF-8",
        }

        message = {
            "message": {
                "token": device_token,
                "notification": {"title": title, "body": body},
                "data": {"role": role},
            }
        }

        response = requests.post(url, headers=headers, data=json.dumps(message))
        return response.status_code, response.text
    except Exception as e:
        return 500, str(e)
