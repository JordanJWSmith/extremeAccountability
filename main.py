import os
import smtplib
import requests
import datetime
from dotenv import load_dotenv
from email.mime.text import MIMEText
from pymongo import MongoClient

from generate_message import generate_shame_message

MONGODB_URI = os.getenv('MONGODB_URI')
client = MongoClient(MONGODB_URI)
db = client['extremeAccountability']  # or whatever database name you want
config_collection = db['creds']

# Load environment variables
load_dotenv()

STRAVA_CLIENT_ID = os.getenv('STRAVA_CLIENT_ID')
STRAVA_CLIENT_SECRET = os.getenv('STRAVA_CLIENT_SECRET')
STRAVA_REFRESH_TOKEN = os.getenv('STRAVA_REFRESH_TOKEN')

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


def get_access_token():
    refresh_token = get_refresh_token_from_db()

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

    access_token = token_data['access_token']
    new_refresh_token = token_data.get('refresh_token')

    if new_refresh_token and new_refresh_token != refresh_token:
        print("🔄 New refresh token received. Updating MongoDB...")
        save_refresh_token_to_db(new_refresh_token)

    return access_token


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
    response_obj = generate_shame_message()
    msg_text = response_obj['body']       # HTML body
    msg_subject = response_obj['subject'] # Plaintext subject

    msg = MIMEText(msg_text, 'html')  # Tell MIMEText this is HTML
    msg['Subject'] = msg_subject
    msg['From'] = FROM_EMAIL
    msg['To'] = TO_EMAIL

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(FROM_EMAIL, EMAIL_PASSWORD)
        server.send_message(msg)

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
