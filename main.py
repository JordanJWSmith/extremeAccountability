from dotenv import load_dotenv
load_dotenv()

import os
import time
import smtplib
import requests
import datetime
from email.mime.text import MIMEText
from pymongo import MongoClient

from generate_message import generate_shame_message

MONGODB_URI = os.getenv('MONGODB_URI')
client = MongoClient(MONGODB_URI)
db = client['extremeAccountability']  
config_collection = db['creds']

STRAVA_CLIENT_ID = os.getenv('STRAVA_CLIENT_ID')
STRAVA_CLIENT_SECRET = os.getenv('STRAVA_CLIENT_SECRET')

FROM_EMAIL = os.getenv('FROM_EMAIL')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
TO_EMAIL = os.getenv('TO_EMAIL')


def get_refresh_token_from_db():
    doc = config_collection.find_one({"user": "jordan"})
    if doc and 'refresh_token' in doc:
        return doc['refresh_token']
    raise Exception("No refresh token found in MongoDB.")


def save_refresh_token_to_db(new_token):
    config_collection.update_one(
        {"user": "jordan"},
        {"$set": {"refresh_token": new_token}},
        upsert=True
    )


def get_email_recipients_from_db():
    doc = config_collection.find_one({"user": "jordan"})
    if doc and 'recipients' in doc and isinstance(doc['recipients'], list):
        return doc['recipients']
    raise Exception("No email recipients found in MongoDB.")


def get_access_token():
    doc = config_collection.find_one({"user": "jordan"})
    if not doc:
        raise Exception("Strava credentials not found in DB.")

    access_token = doc.get("access_token")
    expires_at = doc.get("access_token_expires_at", 0)
    refresh_token = doc.get("refresh_token")

    current_time = int(time.time())

    # If access token exists and hasn't expired, use it
    if access_token and current_time < expires_at:
        print("✅ Using cached access token.")
        return access_token

    # Otherwise, refresh the token
    print("🔄 Access token missing or expired. Refreshing...")

    response = requests.post(
        'https://www.strava.com/oauth/token',
        data={
            'client_id': STRAVA_CLIENT_ID,
            'client_secret': STRAVA_CLIENT_SECRET,
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token
        }
    )
    response.raise_for_status()
    token_data = response.json()

    new_access_token = token_data['access_token']
    new_refresh_token = token_data.get('refresh_token', refresh_token)
    expires_at = token_data['expires_at']  # UNIX timestamp

    # Save tokens back to DB
    config_collection.update_one(
        {"user": "jordan"},
        {"$set": {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "access_token_expires_at": expires_at
        }},
        upsert=True
    )

    print("✅ New access token saved to DB.")
    return new_access_token


def get_today_activities(access_token):
    today = datetime.datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    after_epoch = int(today.timestamp())
    response = requests.get(
        'https://www.strava.com/api/v3/athlete/activities',
        headers={'Authorization': f'Bearer {access_token}'},
        params={'after': after_epoch}
    )
    response.raise_for_status()
    return response.json()


def send_shame_email():
    recipients = get_email_recipients_from_db()
    response_obj = generate_shame_message()
    msg_text = response_obj['body']
    msg_subject = response_obj['subject']

    for email in recipients:
        msg = MIMEText(msg_text, 'html')
        msg['Subject'] = msg_subject
        msg['From'] = FROM_EMAIL
        msg['To'] = email

        try:
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(FROM_EMAIL, EMAIL_PASSWORD)
                server.send_message(msg)
            print(f"✅ Email sent to {email}")
        except Exception as e:
            print(f"❌ Failed to send email to {email}: {e}")


def main():
    token = get_access_token()
    activities = get_today_activities(token)
    if not activities:
        send_shame_email()
    else:
        print("Workout complete. No shame needed!")
        print(activities)

if __name__ == "__main__":
    main()
