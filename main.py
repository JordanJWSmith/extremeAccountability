import os
import requests
import datetime
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

STRAVA_CLIENT_ID = os.getenv('STRAVA_CLIENT_ID')
STRAVA_CLIENT_SECRET = os.getenv('STRAVA_CLIENT_SECRET')
STRAVA_REFRESH_TOKEN = os.getenv('STRAVA_REFRESH_TOKEN')

FROM_EMAIL = os.getenv('FROM_EMAIL')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
TO_EMAIL = os.getenv('TO_EMAIL')

def get_access_token():
    response = requests.post(
        'https://www.strava.com/oauth/token',
        data={
            'client_id': STRAVA_CLIENT_ID,
            'client_secret': STRAVA_CLIENT_SECRET,
            'grant_type': 'refresh_token',
            'refresh_token': STRAVA_REFRESH_TOKEN
        }
    )
    response.raise_for_status()
    return response.json()['access_token']

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
    msg = MIMEText("Jordan didn't work out today. Shame! 😔")
    msg['Subject'] = "Workout Failure Alert"
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

if __name__ == "__main__":
    main()
